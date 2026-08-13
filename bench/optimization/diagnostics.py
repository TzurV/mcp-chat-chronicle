"""Privacy-safe failure evidence for provider-facing optimizer operations."""

from __future__ import annotations

import json
import re
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_SAFE_ATTRIBUTE_ERROR = re.compile(
    r"^'[A-Za-z_][A-Za-z0-9_.]*' object has no attribute '[A-Za-z_][A-Za-z0-9_]*'$"
)


def sanitized_exception_message(exc: BaseException) -> str:
    """Return only a narrowly allowlisted application-contract error message."""
    message = " ".join(str(exc).split())
    if isinstance(exc, AttributeError) and _SAFE_ATTRIBUTE_ERROR.fullmatch(message):
        return message
    return "external or value-bearing exception details redacted"


def application_stack_frames(
    exc: BaseException,
    application_root: Path,
    *,
    private_prefixes: tuple[str, ...] = (".chronicle",),
) -> list[dict[str, int | str]]:
    """Return path- and value-safe application-owned traceback coordinates."""
    root = application_root.resolve()
    frames: list[dict[str, int | str]] = []
    for frame in traceback.extract_tb(exc.__traceback__):
        path = Path(frame.filename).resolve()
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            continue
        if any(
            relative == prefix or relative.startswith(f"{prefix}/") for prefix in private_prefixes
        ):
            relative = f"<private-artifact>/{path.name}"
        frames.append(
            {
                "file": relative,
                "line": frame.lineno,
                "function": frame.name,
            }
        )
    return frames


def failure_boundary(*, request_started: bool, response_finished: bool) -> str:
    """Classify failure timing without retaining provider request or response bodies."""
    if response_finished:
        return "adapting-provider-response"
    if request_started:
        return "during-provider-call"
    return "before-request-submission"


def optimizer_failure_category(exc: BaseException) -> str:
    """Classify an optimizer failure without retaining provider-controlled text."""
    categories: list[str] = []
    current: BaseException | None = exc
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        categories.append(_single_failure_category(current))
        current = current.__cause__ or current.__context__
    for category in categories:
        if category not in {"provider", "local-serialization"}:
            return category
    if "provider" in categories:
        return "provider"
    return categories[0] if categories else "provider"


def _single_failure_category(exc: BaseException) -> str:
    name = type(exc).__name__.casefold()
    message = " ".join(str(exc).casefold().split())
    status = getattr(exc, "status_code", None)
    if status is None:
        status = getattr(getattr(exc, "response", None), "status_code", None)
    status = status if isinstance(status, int) and 100 <= status <= 599 else None
    kind = str(getattr(exc, "kind", "")).casefold()

    if "pickl" in name or "serializ" in name or "pickle" in message:
        return "local-serialization"
    if (
        "jsondecode" in name
        or kind == "invalid_json"
        or any(marker in message for marker in ("invalid json", "json decode", "valid json"))
    ):
        return "invalid-json"
    if kind == "model_not_found" or (
        "model" in message
        and any(marker in message for marker in ("not found", "does not exist", "not loaded"))
    ):
        return "model-not-found"
    if "permission" in name or "forbidden" in name or status == 403:
        return "permission"
    if "authentication" in name or "unauthenticated" in name or status == 401:
        return "authentication"
    if "quota" in name or "resourceexhausted" in name or "quota" in message:
        return "quota"
    if "ratelimit" in name or "rate_limit" in name or status == 429:
        return "rate-limit"
    if "timeout" in name or kind == "timeout" or "timed out" in message:
        return "timeout"
    if (
        "badrequest" in name
        or "invalidrequest" in name
        or kind in {"unsupported_parameter", "provider_route"}
        or status == 400
    ):
        return "invalid-request"
    return "provider"


@dataclass
class OptimizerFailureRecorder:
    """Keep only sanitized LM/adapter failure categories outside exception objects."""

    categories: list[str] = field(default_factory=list)
    usage_extractor: Callable[[Any], tuple[int, int, int]] | None = field(default=None, repr=False)
    task_calls: int = 0
    proposer_calls: int = 0
    proposer_input_tokens: int = 0
    proposer_output_tokens: int = 0
    _instances: dict[str, Any] = field(default_factory=dict, repr=False)

    def __getattr__(self, name: str):
        if name.startswith("on_"):
            return lambda *args, **kwargs: None
        raise AttributeError(name)

    def on_lm_start(self, call_id: str, instance: Any, inputs: dict[str, Any]) -> None:
        del inputs
        self._instances[call_id] = instance
        if getattr(instance, "_chronicle_optimizer_role", None) == "proposer":
            self.proposer_calls += 1
        else:
            self.task_calls += 1

    def on_lm_end(
        self,
        call_id: str,
        outputs: Any | None,
        exception: Exception | None = None,
    ) -> None:
        del outputs
        instance = self._instances.pop(call_id, None)
        if (
            exception is None
            and instance is not None
            and getattr(instance, "_chronicle_optimizer_role", None) == "proposer"
            and self.usage_extractor is not None
            and getattr(instance, "history", None)
        ):
            prompt, completion, reasoning = self.usage_extractor(instance.history[-1])
            self.proposer_input_tokens += prompt
            self.proposer_output_tokens += completion + reasoning
        self._record(exception)

    def on_adapter_parse_end(
        self,
        call_id: str,
        outputs: Any | None,
        exception: Exception | None = None,
    ) -> None:
        del call_id, outputs
        self._record(exception)

    def _record(self, exception: Exception | None) -> None:
        if exception is not None:
            self.categories.append(optimizer_failure_category(exception))

    @property
    def primary_category(self) -> str | None:
        for category in self.categories:
            if category != "local-serialization":
                return category
        return self.categories[0] if self.categories else None


@dataclass(frozen=True)
class CompleteRequestGuard:
    """Abort a candidate DSPy boundary before submission when its full request exceeds 8K."""

    context_window: int
    output_allowance_tokens: int
    wrapper_allowance_tokens: int = 64

    def __getattr__(self, name: str):
        if name.startswith("on_"):
            return lambda *args, **kwargs: None
        raise AttributeError(name)

    def on_lm_start(self, call_id: str, instance: Any, inputs: dict[str, Any]) -> None:
        del call_id
        if getattr(instance, "_chronicle_optimizer_role", None) != "candidate":
            return
        serialized = json.dumps(
            {"inputs": inputs, "model_kwargs": getattr(instance, "kwargs", {})},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        input_tokens = (len(serialized.encode("utf-8")) + 2) // 3
        total = input_tokens + self.wrapper_allowance_tokens + self.output_allowance_tokens
        if total > self.context_window:
            raise RuntimeError("candidate complete request exceeds the 8K context boundary")
