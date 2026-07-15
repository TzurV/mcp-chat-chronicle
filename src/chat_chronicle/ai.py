"""Application-owned AI task runner and lazy LiteLLM adapter."""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import re
import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal, Protocol

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    ValidationError,
    field_validator,
    model_validator,
)

from chat_chronicle.ai_config import (
    ModelProfile,
    TaskDefinition,
    interpolate_prompt,
    resolve_generation,
    resolve_model,
)
from chat_chronicle.db import find_ai_cache_hit, record_ai_task_result


class ExampleResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    result: str


class ConversationSummaryProviderResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: list[str] = Field(min_length=2, max_length=5)
    evidence_message_ids: list[StrictInt] = Field(max_length=8)

    @field_validator("summary")
    @classmethod
    def bounded_sentences(cls, value: list[str]) -> list[str]:
        if any(not sentence.strip() for sentence in value):
            raise ValueError("summary sentences must be non-empty")
        if sum(len(sentence.split()) for sentence in value) > 120:
            raise ValueError("summary must contain at most 120 words")
        return value


class ConversationSummaryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(min_length=1, max_length=1_000)
    start_date: str
    last_active_date: str
    evidence_message_ids: list[StrictInt] = Field(max_length=8)

    @field_validator("summary")
    @classmethod
    def bounded_summary(cls, value: str) -> str:
        if len(value.split()) > 120:
            raise ValueError("summary must contain at most 120 words")
        sentences = [item for item in re.split(r"(?<=[.!?])\s+", value.strip()) if item]
        if not 2 <= len(sentences) <= 5:
            raise ValueError("summary must contain 2-5 sentences")
        return value


class WorkModeClassificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: Literal["manager", "executor", "one_off", "mixed", "unknown"]
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1, max_length=500)
    evidence_message_ids: list[StrictInt] = Field(max_length=8)

    @field_validator("reason")
    @classmethod
    def bounded_reason(cls, value: str) -> str:
        if len(value.split()) > 60:
            raise ValueError("reason must contain at most 60 words")
        return value


class LastActivityResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recent_work: str = Field(min_length=1, max_length=800)
    status: Literal["in_progress", "completed", "blocked", "awaiting_input", "unknown"]
    blockers: list[str] = Field(max_length=3)
    next_action: str | None = Field(default=None, max_length=400)
    next_action_basis: Literal["explicit", "inferred", "unknown"]
    evidence_message_ids: list[StrictInt] = Field(max_length=8)

    @field_validator("recent_work")
    @classmethod
    def bounded_recent_work(cls, value: str) -> str:
        if len(value.split()) > 100:
            raise ValueError("recent_work must contain at most 100 words")
        return value

    @field_validator("blockers")
    @classmethod
    def concise_blockers(cls, value: list[str]) -> list[str]:
        if any(not item.strip() or len(item.split()) > 40 for item in value):
            raise ValueError("blockers must be non-empty and at most 40 words each")
        return value

    @field_validator("next_action")
    @classmethod
    def bounded_next_action(cls, value: str | None) -> str | None:
        if value is not None and (not value.strip() or len(value.split()) > 40):
            raise ValueError("next_action must be non-empty and at most 40 words")
        return value

    @model_validator(mode="after")
    def action_consistency(self) -> LastActivityResult:
        if self.next_action_basis == "unknown" and self.next_action is not None:
            raise ValueError("unknown next_action_basis requires next_action=null")
        if self.next_action_basis != "unknown" and self.next_action is None:
            raise ValueError("explicit or inferred next_action_basis requires a next_action")
        return self


class NextActionProviderResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    basis: Literal["explicit", "inferred"]
    action: str = Field(min_length=1, max_length=400)

    @field_validator("action")
    @classmethod
    def bounded_action(cls, value: str) -> str:
        if len(value.split()) > 40:
            raise ValueError("next action must contain at most 40 words")
        return value


class LastActivityProviderResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recent_work: str = Field(min_length=1, max_length=800)
    status: Literal["in_progress", "completed", "blocked", "awaiting_input", "unknown"]
    blockers: list[str] = Field(max_length=3)
    next_action: NextActionProviderResult | None
    evidence_message_ids: list[StrictInt] = Field(max_length=8)

    @field_validator("recent_work")
    @classmethod
    def bounded_recent_work(cls, value: str) -> str:
        if len(value.split()) > 100:
            raise ValueError("recent_work must contain at most 100 words")
        return value

    @field_validator("blockers")
    @classmethod
    def concise_blockers(cls, value: list[str]) -> list[str]:
        if any(not item.strip() or len(item.split()) > 40 for item in value):
            raise ValueError("blockers must be non-empty and at most 40 words each")
        return value


class TitleAssessmentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title_fits: bool
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1, max_length=500)
    suggested_title: str | None = Field(default=None, max_length=80)
    evidence_message_ids: list[StrictInt] = Field(max_length=8)

    @field_validator("reason")
    @classmethod
    def bounded_reason(cls, value: str) -> str:
        if len(value.split()) > 60:
            raise ValueError("reason must contain at most 60 words")
        return value

    @model_validator(mode="after")
    def suggestion_consistency(self) -> TitleAssessmentResult:
        if self.title_fits and self.suggested_title is not None:
            raise ValueError("title_fits=true requires suggested_title=null")
        if not self.title_fits and (
            self.suggested_title is None or not self.suggested_title.strip()
        ):
            raise ValueError("title_fits=false requires a non-empty suggested_title")
        return self


Finalizer = Callable[[BaseModel, "SelectedInput"], dict[str, Any]]


@dataclass(frozen=True)
class OutputSchemaSpec:
    version: str
    provider_model: type[BaseModel]
    final_model: type[BaseModel]
    finalizer_version: str
    finalizer: Finalizer

    @property
    def identity_version(self) -> str:
        return f"{self.version}+finalizer-{self.finalizer_version}"

    def __getitem__(self, index: int) -> str | type[BaseModel]:
        """Retain the accepted WP-5.1 tuple-style registry inspection seam."""
        return (self.version, self.provider_model)[index]


def _identity_finalizer(value: BaseModel, selected: SelectedInput) -> dict[str, Any]:
    return value.model_dump(mode="json")


def _summary_finalizer(value: BaseModel, selected: SelectedInput) -> dict[str, Any]:
    result = value.model_dump(mode="json")
    sentences = []
    for sentence in result["summary"]:
        normalized = sentence.strip()
        if not normalized.endswith((".", "!", "?")):
            normalized += "."
        sentences.append(normalized)
    result["summary"] = " ".join(sentences)
    result["start_date"] = selected.start_date
    result["last_active_date"] = selected.last_active_date
    return result


def _last_activity_finalizer(value: BaseModel, selected: SelectedInput) -> dict[str, Any]:
    result = value.model_dump(mode="json")
    action = result.pop("next_action")
    if action is None:
        result["next_action"] = None
        result["next_action_basis"] = "unknown"
    else:
        result["next_action"] = action["action"]
        result["next_action_basis"] = action["basis"]
    return result


OUTPUT_SCHEMAS: dict[str, OutputSchemaSpec | tuple[str, type[BaseModel]]] = {
    "example-result-v1": OutputSchemaSpec(
        "1", ExampleResult, ExampleResult, "1", _identity_finalizer
    ),
    "conversation-summary-v1": OutputSchemaSpec(
        "1",
        ConversationSummaryProviderResult,
        ConversationSummaryResult,
        "2",
        _summary_finalizer,
    ),
    "work-mode-classification-v1": OutputSchemaSpec(
        "1",
        WorkModeClassificationResult,
        WorkModeClassificationResult,
        "1",
        _identity_finalizer,
    ),
    "last-activity-v1": OutputSchemaSpec(
        "1", LastActivityProviderResult, LastActivityResult, "2", _last_activity_finalizer
    ),
    "title-assessment-v1": OutputSchemaSpec(
        "1", TitleAssessmentResult, TitleAssessmentResult, "1", _identity_finalizer
    ),
}


def _schema_spec(name: str) -> OutputSchemaSpec:
    value = OUTPUT_SCHEMAS[name]
    if isinstance(value, OutputSchemaSpec):
        return value
    version, model = value
    return OutputSchemaSpec(version, model, model, "legacy", _identity_finalizer)


class LLMError(RuntimeError):
    def __init__(self, kind: str, message: str):
        self.kind = kind
        super().__init__(message)


_SAFE_PROVIDER_CODE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")


def _provider_failure(exc: Exception) -> LLMError:
    """Classify provider failures without retaining provider-controlled text."""
    exception_type = type(exc).__name__
    name = exception_type.lower()
    message = str(exc).lower()
    status = getattr(exc, "status_code", None)
    if status is None:
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
    status = status if isinstance(status, int) and 100 <= status <= 599 else None
    raw_code = getattr(exc, "code", None) or getattr(exc, "error_code", None)
    code = str(raw_code) if raw_code is not None else None
    code = code if code and _SAFE_PROVIDER_CODE.fullmatch(code) else None

    if "provider" in message and any(
        marker in message
        for marker in ("not provided", "no provider", "custom_llm_provider")
    ):
        kind = "provider_route"
        detail = (
            "LiteLLM could not resolve the model provider; use a provider-prefixed "
            "model such as 'lm_studio/<model-id>'."
        )
    elif "context" in message and any(
        marker in message for marker in ("length", "window", "maximum", "token")
    ):
        kind = "context_length"
        detail = "The request exceeds the model's configured context window."
    elif "model" in message and any(
        marker in message for marker in ("not found", "not loaded", "does not exist")
    ):
        kind = "model_not_found"
        detail = "The configured model was not found or is not loaded by the provider."
    elif status == 404 and "model" in message:
        kind = "model_not_found"
        detail = "The configured model was not found or is not loaded by the provider."
    elif any(marker in name for marker in ("authentication", "permission")) or status in {
        401,
        403,
    }:
        kind = "authentication"
        detail = "The provider rejected the configured authentication."
    elif any(marker in name for marker in ("ratelimit", "rate_limit")) or status == 429:
        kind = "rate_limit"
        detail = "The provider rate-limited the request."
    elif "timeout" in name or "timed out" in message:
        kind = "timeout"
        detail = (
            "The model request timed out. Increase the selected profile's `timeout` "
            "in the active ai-models.yaml and retry; for local inference, keep "
            "`retries: 0` while calibrating."
        )
    elif "connection" in name or any(
        marker in message
        for marker in ("connection refused", "failed to connect", "unreachable")
    ):
        kind = "connection"
        detail = "Chronicle could not connect to the configured model endpoint."
    elif any(
        marker in message
        for marker in (
            "unsupported parameter",
            "unsupported request",
            "response_format",
            "unrecognized request argument",
            "must be 'json_schema'",
        )
    ):
        kind = "unsupported_parameter"
        detail = "The provider rejected a request parameter or structured-output mode."
    elif status is not None:
        kind = "provider_http"
        detail = f"The provider returned HTTP status {status}."
    else:
        kind = "provider"
        detail = "The model provider rejected the request."

    safe_facts = [f"exception={exception_type[:80]}"]
    if status is not None:
        safe_facts.append(f"status={status}")
    if code is not None:
        safe_facts.append(f"code={code}")
    return LLMError(kind, f"{detail} ({', '.join(safe_facts)})")


@dataclass(frozen=True)
class CompletionRequest:
    model: str
    messages: list[dict[str, str]]
    response_schema: dict[str, Any]
    enforce_schema: bool
    temperature: float
    max_tokens: int
    timeout: float
    retries: int
    api_base: str | None = None
    api_key: str | None = None
    context_window: int | None = None
    estimated_input_tokens: int | None = None


@dataclass(frozen=True)
class CompletionResponse:
    content: str
    provider: str
    model: str
    usage: dict[str, Any] | None = None


class LLMClient(Protocol):
    async def complete(self, request: CompletionRequest) -> CompletionResponse: ...


class LiteLLMClient:
    """Optional adapter. LiteLLM is imported only when an AI call executes."""

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        try:
            import litellm
        except ImportError as exc:
            raise LLMError(
                "dependency",
                "AI support is not installed; run `poetry install -E enrich`.",
            ) from exc

        response_format = (
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "chronicle_response",
                    "strict": True,
                    "schema": request.response_schema,
                },
            }
            if request.enforce_schema
            else {"type": "json_object"}
        )
        try:
            response = await litellm.acompletion(
                model=request.model,
                messages=request.messages,
                response_format=response_format,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                timeout=request.timeout,
                num_retries=request.retries,
                api_base=request.api_base,
                api_key=request.api_key,
            )
            choices = getattr(response, "choices", None)
            if not choices or getattr(choices[0], "message", None) is None:
                raise LLMError("provider_response", "Provider returned no completion choice.")
            content = choices[0].message.content
            if not isinstance(content, str) or not content.strip():
                raise LLMError("invalid_json", "Provider returned an empty structured response.")
            usage_object = getattr(response, "usage", None)
            usage = usage_object.model_dump() if usage_object is not None else None
            provider = str(getattr(response, "provider", "") or "").strip()
            if not provider or provider == "unknown":
                provider = request.model.split("/", 1)[0] if "/" in request.model else "unknown"
            actual_model = str(getattr(response, "model", request.model))
            provider_prefix = f"{provider}/"
            if provider != "unknown" and actual_model.startswith(provider_prefix):
                actual_model = actual_model[len(provider_prefix) :]
            return CompletionResponse(
                content=content,
                provider=provider,
                model=actual_model,
                usage=usage,
            )
        except LLMError:
            raise
        except Exception as exc:
            raise _provider_failure(exc) from exc


@dataclass(frozen=True)
class SelectedInput:
    conversation_id: int
    provider: str
    title: str
    start_date: str
    last_active_date: str
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class PreparedAttempt:
    selected: SelectedInput
    request: CompletionRequest
    input_hash: str
    prompt_hash: str
    task_hash: str
    model_hash: str
    schema_name: str
    schema_version: str


MEANINGFUL_ROLES = frozenset({"user", "human", "assistant"})


def _meaningful_rows(rows: list[sqlite3.Row]) -> list[sqlite3.Row]:
    return [
        row
        for row in rows
        if (row["role"] or "").strip().lower() in MEANINGFUL_ROLES
        and (row["body"] or "").strip()
    ]


def _message_header(row: sqlite3.Row) -> str:
    timestamp = row["created_at"] or "unknown"
    role = (row["role"] or "unknown").strip()
    return (
        f"[message_id={int(row['id'])} seq={int(row['seq'])} "
        f"timestamp={timestamp} role={role}]"
    )


def _render_message(row: sqlite3.Row) -> str:
    return f"{_message_header(row)}\n{(row['body'] or '').strip()}"


def _truncate_message(
    row: sqlite3.Row, budget: int, *, keep_tail: bool
) -> tuple[str, dict[str, Any]]:
    original = _render_message(row)
    header = _message_header(row)
    marker = "\n[…truncated…]\n"
    if budget >= len(original):
        return original, {}
    if budget <= len(header):
        rendered = header[:budget]
    else:
        body_budget = max(0, budget - len(header) - len(marker))
        body = (row["body"] or "").strip()
        fragment = body[-body_budget:] if keep_tail and body_budget else body[:body_budget]
        rendered = f"{header}{marker}{fragment}"[:budget]
    return rendered, {
        "message_id": int(row["id"]),
        "original_chars": len(original),
        "selected_chars": len(rendered),
        "kept": "tail" if keep_tail else "head",
    }


def _append_with_budget(
    selected: list[tuple[sqlite3.Row, str, dict[str, Any]]],
    row: sqlite3.Row,
    budget: int,
    *,
    keep_tail: bool,
) -> bool:
    used = sum(len(item[1]) for item in selected) + max(0, len(selected) - 1) * 2
    separator = 2 if selected else 0
    remaining = budget - used - separator
    if remaining <= 0:
        return False
    rendered = _render_message(row)
    if len(rendered) <= remaining:
        selected.append((row, rendered, {}))
        return True
    if not selected:
        text, detail = _truncate_message(row, remaining, keep_tail=keep_tail)
        selected.append((row, text, detail))
    return False


def _bounded_omitted_ids(ids: list[int]) -> tuple[list[int], bool]:
    return ids[:100], len(ids) > 100


def _overview_selection(
    rows: list[sqlite3.Row], budget: int
) -> tuple[str, list[int], dict[str, Any]]:
    rendered_all = [_render_message(row) for row in rows]
    full_text = "\n\n".join(rendered_all)
    if len(full_text) <= budget:
        return (
            full_text,
            [int(row["id"]) for row in rows],
            {
                "sampling_strategy": "complete",
                "truncation_details": [],
            },
        )

    # Reserve the two separators between the three deterministic allocation groups.
    allocatable = max(1, budget - 4)
    begin_budget = allocatable // 4
    middle_budget = allocatable // 4
    end_budget = allocatable - begin_budget - middle_budget
    begin: list[tuple[sqlite3.Row, str, dict[str, Any]]] = []
    middle: list[tuple[sqlite3.Row, str, dict[str, Any]]] = []
    end: list[tuple[sqlite3.Row, str, dict[str, Any]]] = []

    for row in rows:
        if not _append_with_budget(begin, row, begin_budget, keep_tail=False):
            break
    selected_ids = {int(item[0]["id"]) for item in begin}

    for row in reversed(rows):
        if int(row["id"]) in selected_ids:
            continue
        if not _append_with_budget(end, row, end_budget, keep_tail=True):
            break
    selected_ids.update(int(item[0]["id"]) for item in end)

    candidates = [row for row in rows if int(row["id"]) not in selected_ids]
    # Center-out order provides distributed middle coverage without provider assumptions.
    order: list[sqlite3.Row] = []
    pending = [candidates]
    while pending:
        group = pending.pop(0)
        if not group:
            continue
        midpoint = len(group) // 2
        order.append(group[midpoint])
        pending.extend((group[:midpoint], group[midpoint + 1 :]))
    for row in order:
        if not _append_with_budget(middle, row, middle_budget, keep_tail=False):
            if middle:
                continue
            break

    combined = begin + middle + end
    by_id = {int(item[0]["id"]): item for item in combined}
    chronological = sorted(
        by_id.values(), key=lambda item: (int(item[0]["seq"]), int(item[0]["id"]))
    )
    text = "\n\n".join(item[1] for item in chronological)
    # Allocation math should keep this bounded; this guard handles very small budgets.
    text = text[:budget]
    return (
        text,
        [int(item[0]["id"]) for item in chronological],
        {
            "sampling_strategy": "beginning-25-middle-25-end-50",
            "truncation_details": [item[2] for item in chronological if item[2]],
        },
    )


def _select_meaningful(
    rows: list[sqlite3.Row], task: TaskDefinition
) -> tuple[str, dict[str, Any]]:
    meaningful = _meaningful_rows(rows)
    all_ids = [int(row["id"]) for row in meaningful]
    if task.input_selector == "conversation-overview-v1":
        text, selected_ids, details = _overview_selection(
            meaningful, task.max_input_chars
        )
        original_text = "\n\n".join(_render_message(row) for row in meaningful)
        original_candidate_count = len(meaningful)
    else:
        candidates = meaningful[-task.recent_message_count :]
        picked_reverse: list[tuple[sqlite3.Row, str, dict[str, Any]]] = []
        for row in reversed(candidates):
            if not _append_with_budget(
                picked_reverse, row, task.max_input_chars, keep_tail=True
            ):
                break
        chronological = sorted(
            picked_reverse, key=lambda item: (int(item[0]["seq"]), int(item[0]["id"]))
        )
        text = "\n\n".join(item[1] for item in chronological)
        selected_ids = [int(item[0]["id"]) for item in chronological]
        original_text = "\n\n".join(_render_message(row) for row in candidates)
        original_candidate_count = len(candidates)
        details = {
            "sampling_strategy": "newest-complete-first",
            "truncation_details": [item[2] for item in chronological if item[2]],
        }

    omitted = [item for item in all_ids if item not in set(selected_ids)]
    omitted_ids, omitted_bounded = _bounded_omitted_ids(omitted)
    selected_rows = [row for row in meaningful if int(row["id"]) in set(selected_ids)]
    metadata = {
        "selector": task.input_selector,
        "selector_version": "1",
        "message_ids": selected_ids,
        "selected_message_ids": selected_ids,
        "omitted_count": len(omitted),
        "omitted_message_ids": omitted_ids,
        "omitted_ids_bounded": omitted_bounded,
        "meaningful_message_count": len(meaningful),
        "original_candidate_count": original_candidate_count,
        "seq_start": int(selected_rows[0]["seq"]) if selected_rows else None,
        "seq_end": int(selected_rows[-1]["seq"]) if selected_rows else None,
        "original_chars": len(original_text),
        "selected_chars": len(text),
        "truncated": len(text) < len(original_text),
        **details,
    }
    return text, metadata


def select_input(
    conn: sqlite3.Connection, conversation_id: int, task: TaskDefinition
) -> SelectedInput:
    conversation = conn.execute(
        "SELECT id, provider, title, created_at, updated_at FROM conversations WHERE id = ?",
        (conversation_id,),
    ).fetchone()
    if conversation is None:
        raise ValueError(f"Conversation {conversation_id} does not exist.")
    rows = conn.execute(
        "SELECT id, role, created_at, body, seq FROM messages "
        "WHERE conversation_id = ? ORDER BY seq, id",
        (conversation_id,),
    ).fetchall()
    all_rows = rows
    if task.input_selector in {"conversation-overview-v1", "recent-meaningful-v1"}:
        text, metadata = _select_meaningful(all_rows, task)
    else:
        if task.input_selector in {"recent-messages", "metadata-recent"}:
            rows = rows[-task.recent_message_count :]
        rendered = [f"{row['role'] or 'unknown'}: {row['body']}" for row in rows]
        full_text = "\n\n".join(rendered)
        truncated = len(full_text) > task.max_input_chars
        text = full_text[-task.max_input_chars :] if truncated else full_text
        metadata = {
            "selector": task.input_selector,
            "message_ids": [int(row["id"]) for row in rows],
            "message_roles": [row["role"] for row in rows],
            "message_sequences": [row["seq"] for row in rows],
            "seq_start": int(rows[0]["seq"]) if rows else None,
            "seq_end": int(rows[-1]["seq"]) if rows else None,
            "original_chars": len(full_text),
            "selected_chars": len(text),
            "truncated": truncated,
        }
    dates = [row["created_at"] for row in all_rows if row["created_at"]]
    start = conversation["created_at"] or (dates[0] if dates else "")
    last = conversation["updated_at"] or (dates[-1] if dates else "")
    return SelectedInput(
        int(conversation["id"]),
        conversation["provider"],
        conversation["title"] or "",
        start or "",
        last or "",
        text,
        metadata,
    )


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def _estimate_input_tokens(messages: list[dict[str, str]]) -> int:
    """Return a conservative privacy-safe estimate without adding a tokenizer dependency."""
    characters = sum(len(item.get("role", "")) + len(item.get("content", "")) for item in messages)
    return math.ceil(characters / 4) + (4 * len(messages))


def _provider_response_schema(
    schema_spec: OutputSchemaSpec, selected: SelectedInput
) -> dict[str, Any]:
    """Bind evidence integers to the exact input IDs for provider-side enforcement."""
    schema = schema_spec.provider_model.model_json_schema()
    evidence_schema = schema.get("properties", {}).get("evidence_message_ids")
    if not isinstance(evidence_schema, dict):
        return schema
    selected_ids = list(dict.fromkeys(selected.metadata.get("selected_message_ids", [])))
    if selected_ids:
        items = evidence_schema.setdefault("items", {"type": "integer"})
        if isinstance(items, dict):
            items["enum"] = selected_ids
    else:
        evidence_schema["maxItems"] = 0
    return schema


def prepare_attempt(
    conn: sqlite3.Connection,
    *,
    task: TaskDefinition,
    profile: ModelProfile,
    conversation_id: int,
) -> PreparedAttempt:
    resolved = resolve_model(profile)
    selected = select_input(conn, conversation_id, task)
    prompt_values = {
        "conversation_id": str(selected.conversation_id),
        "provider": selected.provider,
        "title": selected.title,
        "start_date": selected.start_date,
        "last_active_date": selected.last_active_date,
        "transcript": selected.text,
    }
    system = interpolate_prompt(task.system_prompt, prompt_values)
    user = interpolate_prompt(task.user_prompt, prompt_values)
    schema_spec = _schema_spec(task.output_schema)
    effective_generation = resolve_generation(task, profile)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    estimated_input_tokens = _estimate_input_tokens(messages)
    model_for_hash = {key: value for key, value in resolved.items() if key != "api_key"}
    model_for_hash["generation"] = effective_generation.model_dump(mode="json")
    input_payload = {
        "text": selected.text,
        "selection": selected.metadata,
        "provider": selected.provider,
        "title": selected.title,
        "start_date": selected.start_date,
        "last_active_date": selected.last_active_date,
    }
    return PreparedAttempt(
        selected=selected,
        request=CompletionRequest(
            model=resolved["model"],
            messages=messages,
            response_schema=_provider_response_schema(schema_spec, selected),
            enforce_schema=profile.structured_output,
            temperature=effective_generation.temperature,
            max_tokens=effective_generation.max_tokens,
            timeout=profile.timeout,
            retries=profile.retries,
            api_base=profile.api_base,
            api_key=resolved.get("api_key"),
            context_window=profile.context_window,
            estimated_input_tokens=estimated_input_tokens,
        ),
        input_hash=canonical_hash(input_payload),
        prompt_hash=canonical_hash({"system": system, "user": user}),
        task_hash=canonical_hash(task.model_dump(mode="json")),
        model_hash=canonical_hash(model_for_hash),
        schema_name=task.output_schema,
        schema_version=schema_spec.identity_version,
    )


def lookup_cache(
    conn: sqlite3.Connection,
    *,
    task_name: str,
    task: TaskDefinition,
    profile_name: str,
    prepared: PreparedAttempt,
) -> sqlite3.Row | None:
    return find_ai_cache_hit(
        conn,
        prepared.selected.conversation_id,
        task_name,
        task.version,
        prepared.input_hash,
        prepared.prompt_hash,
        prepared.task_hash,
        prepared.schema_name,
        prepared.schema_version,
        profile_name,
        prepared.model_hash,
    )


def inspect_cache(
    conn: sqlite3.Connection,
    *,
    task_name: str,
    task: TaskDefinition,
    profile_name: str,
    profile: ModelProfile,
    conversation_ids: list[int],
) -> list[dict[str, Any]]:
    results = []
    for conversation_id in conversation_ids:
        prepared = prepare_attempt(
            conn, task=task, profile=profile, conversation_id=conversation_id
        )
        hit = lookup_cache(
            conn,
            task_name=task_name,
            task=task,
            profile_name=profile_name,
            prepared=prepared,
        )
        results.append(
            {
                "conversation_id": conversation_id,
                "status": "hit" if hit else "miss",
                "actual_provider": hit["actual_provider"] if hit else None,
                "actual_model": hit["actual_model"] if hit else None,
                "selected_characters": len(prepared.selected.text),
                "estimated_input_tokens": prepared.request.estimated_input_tokens,
                "estimated_request_tokens": (
                    (prepared.request.estimated_input_tokens or 0)
                    + prepared.request.max_tokens
                ),
                "context_window": prepared.request.context_window,
            }
        )
    return results


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _sanitize_error(message: str, prepared: PreparedAttempt) -> str:
    safe = message
    transcript_fragments = [
        line.strip()
        for line in prepared.selected.text.splitlines()
        if line.strip() and not line.lstrip().startswith("[message_id=")
    ]
    transcript_fragments.extend(
        line.split(": ", 1)[1].strip()
        for line in prepared.selected.text.splitlines()
        if ": " in line and line.split(": ", 1)[1].strip()
    )
    for secret in (prepared.request.api_key, prepared.selected.text, *transcript_fragments):
        if secret:
            safe = safe.replace(secret, "[REDACTED]")
    safe = re.sub(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+", "Bearer [REDACTED]", safe)
    safe = re.sub(
        r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*\S+",
        r"\1=[REDACTED]",
        safe,
    )
    safe = re.sub(r"https?://[^\s/@:]+:[^\s/@]+@", "[REDACTED_URL]", safe)
    safe = re.sub(r"(?i)\b[A-Z]:\\[^\r\n]+", "[REDACTED_PATH]", safe)
    return safe[:500]


def _safe_validation_detail(exc: ValidationError) -> str:
    facts = []
    for error in exc.errors(include_url=False, include_context=False, include_input=False)[:3]:
        location = ".".join(str(item) for item in error.get("loc", ())) or "response"
        error_type = str(error.get("type", "invalid"))
        facts.append(f"{location}: {error_type}")
    suffix = f" ({'; '.join(facts)})" if facts else ""
    return f"Response failed output validation{suffix}."[:500]


def _validate_and_finalize(parsed: Any, prepared: PreparedAttempt) -> dict[str, Any]:
    spec = _schema_spec(prepared.schema_name)
    provider_value = spec.provider_model.model_validate(parsed)
    candidate = spec.finalizer(provider_value, prepared.selected)
    final_value = spec.final_model.model_validate(candidate)
    result = final_value.model_dump(mode="json")
    evidence = result.get("evidence_message_ids")
    if evidence is None:
        return result
    selected_ids = set(prepared.selected.metadata.get("selected_message_ids", []))
    invalid = [item for item in evidence if item not in selected_ids]
    if invalid:
        raise LLMError("evidence_validation", "Response cited evidence outside selected input.")
    if evidence:
        return result
    if not selected_ids:
        return result
    schema_name = prepared.schema_name
    unknown_result = (
        schema_name == "work-mode-classification-v1" and result.get("mode") == "unknown"
    ) or (schema_name == "last-activity-v1" and result.get("status") == "unknown")
    if not unknown_result:
        raise LLMError(
            "evidence_validation", "Response omitted required selected-message evidence."
        )
    return result


async def run_task(
    conn: sqlite3.Connection,
    *,
    task_name: str,
    task: TaskDefinition,
    profile_name: str,
    profile: ModelProfile,
    conversation_ids: list[int],
    force: bool = False,
    client: LLMClient | None = None,
) -> list[dict[str, Any]]:
    client = client or LiteLLMClient()
    semaphore = asyncio.Semaphore(profile.concurrency)

    async def one(conversation_id: int) -> dict[str, Any]:
        try:
            prepared = prepare_attempt(
                conn, task=task, profile=profile, conversation_id=conversation_id
            )
        except (ValueError, KeyError) as exc:
            return {
                "status": "failed",
                "id": None,
                "conversation_id": conversation_id,
                "error": "selection",
                "detail": str(exc),
            }
        if not force:
            cached = lookup_cache(
                conn,
                task_name=task_name,
                task=task,
                profile_name=profile_name,
                prepared=prepared,
            )
            if cached is not None:
                return {
                    "status": "cached",
                    "id": int(cached["id"]),
                    "conversation_id": conversation_id,
                    "result": json.loads(cached["result_json"]),
                    "actual_provider": cached["actual_provider"],
                    "actual_model": cached["actual_model"],
                }

        started_at = _utc_now()
        started_clock = time.monotonic()
        response: CompletionResponse | None = None
        try:
            estimated = prepared.request.estimated_input_tokens
            context_window = prepared.request.context_window
            if (
                context_window is not None
                and estimated is not None
                and estimated + prepared.request.max_tokens > context_window
            ):
                raise LLMError(
                    "context_length",
                    "Estimated request tokens exceed the configured model context window "
                    f"({estimated} input + {prepared.request.max_tokens} output > "
                    f"{context_window}).",
                )
            async with semaphore:
                response = await client.complete(prepared.request)
            try:
                parsed = json.loads(response.content)
            except json.JSONDecodeError as exc:
                raise LLMError("invalid_json", "Provider returned invalid JSON.") from exc
            validated = _validate_and_finalize(parsed, prepared)
            completed_at = _utc_now()
            result_id = record_ai_task_result(
                conn,
                conversation_id=conversation_id,
                task_name=task_name,
                task_version=task.version,
                input_hash=prepared.input_hash,
                prompt_hash=prepared.prompt_hash,
                task_hash=prepared.task_hash,
                schema_name=prepared.schema_name,
                schema_version=prepared.schema_version,
                model_profile=profile_name,
                model_hash=prepared.model_hash,
                actual_provider=response.provider,
                actual_model=response.model,
                result=validated,
                status="success",
                error=None,
                latency_ms=int((time.monotonic() - started_clock) * 1000),
                usage=response.usage,
                selection=prepared.selected.metadata,
                started_at=started_at,
                completed_at=completed_at,
            )
            return {
                "status": "completed",
                "id": result_id,
                "conversation_id": conversation_id,
                "result": validated,
                "actual_provider": response.provider,
                "actual_model": response.model,
            }
        except (LLMError, ValidationError) as exc:
            kind = exc.kind if isinstance(exc, LLMError) else "schema_validation"
            detail = (
                _sanitize_error(str(exc), prepared)
                if isinstance(exc, LLMError)
                else _safe_validation_detail(exc)
            )
            completed_at = _utc_now()
            result_id = record_ai_task_result(
                conn,
                conversation_id=conversation_id,
                task_name=task_name,
                task_version=task.version,
                input_hash=prepared.input_hash,
                prompt_hash=prepared.prompt_hash,
                task_hash=prepared.task_hash,
                schema_name=prepared.schema_name,
                schema_version=prepared.schema_version,
                model_profile=profile_name,
                model_hash=prepared.model_hash,
                actual_provider=response.provider if response else None,
                actual_model=response.model if response else None,
                result=None,
                status="failed",
                error=f"{kind}: {detail}",
                latency_ms=int((time.monotonic() - started_clock) * 1000),
                usage=response.usage if response else None,
                selection=prepared.selected.metadata,
                started_at=started_at,
                completed_at=completed_at,
            )
            return {
                "status": "failed",
                "id": result_id,
                "conversation_id": conversation_id,
                "error": kind,
                "detail": detail,
                "actual_provider": response.provider if response else None,
                "actual_model": response.model if response else None,
            }

    return await asyncio.gather(*(one(item) for item in conversation_ids))
