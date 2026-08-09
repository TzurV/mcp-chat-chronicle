"""Privacy-safe failure evidence for provider-facing optimizer operations."""

from __future__ import annotations

import re
import traceback
from pathlib import Path

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
