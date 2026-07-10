"""OpenAI Codex local-session extractor.

Parses Codex JSONL session files from the local ``.codex`` store and converts
visible transcript messages into the normalized
:class:`~chat_chronicle.models.Conversation` and
:class:`~chat_chronicle.models.Message` models.

Codex local storage is a Class B source: durable and useful, but undocumented.
This module is deliberately tolerant and concrete. Known metadata rows are
skipped, while malformed or unexpected records are captured as serializable
extractor errors for later ``ingest_runs.errors_json`` storage.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from chat_chronicle.models import Conversation, Message

PROVIDER = "openai_codex"
SESSION_INDEX_FILENAME = "session_index.jsonl"

_VISIBLE_RESPONSE_ROLES = frozenset({"user", "assistant", "developer"})
_VISIBLE_CONTENT_BLOCK_TYPES = frozenset({"input_text", "output_text"})
_KNOWN_TOP_LEVEL_TYPES = frozenset(
    {"session_meta", "turn_context", "response_item", "event_msg"}
)
_KNOWN_RESPONSE_ITEM_METADATA_TYPES = frozenset(
    {
        "reasoning",
        "function_call",
        "function_call_output",
        "custom_tool_call",
        "custom_tool_call_output",
        "ghost_snapshot",
    }
)
_KNOWN_EVENT_METADATA_TYPES = frozenset(
    {
        "agent_reasoning",
        "rate_limits",
        "token_count",
        "info",
        "error",
        "turn_context",
    }
)


class OpenAICodexExtractError(BaseModel):
    """A single non-fatal extractor problem, serializable into JSON."""

    record_id: str | None = None
    line_number: int | None = None
    error: str
    detail: str | None = None


class OpenAICodexExtractResult(BaseModel):
    conversations: list[Conversation] = Field(default_factory=list)
    errors: list[OpenAICodexExtractError] = Field(default_factory=list)


class CodexSessionIndexEntry(BaseModel):
    """Optional metadata from ``session_index.jsonl``."""

    session_id: str
    thread_name: str | None = None
    updated_at: datetime | None = None


class _ErrorSink:
    def __init__(self) -> None:
        self.errors: list[OpenAICodexExtractError] = []

    def add(
        self,
        error: str,
        *,
        record_id: str | None = None,
        line_number: int | None = None,
        detail: str | None = None,
    ) -> None:
        self.errors.append(
            OpenAICodexExtractError(
                record_id=record_id,
                line_number=line_number,
                error=error,
                detail=detail,
            )
        )


@dataclass(frozen=True)
class _MessageCandidate:
    provider_message_id: str | None
    role: str
    body: str
    created_at: datetime | None
    line_number: int
    source_kind: str


def load_conversations(source: Path | str) -> OpenAICodexExtractResult:
    """Parse one Codex session file, a sessions directory, or a Codex home directory."""
    path = Path(source)
    errors = _ErrorSink()

    if not path.exists():
        errors.add("source_not_found", detail=str(path))
        return OpenAICodexExtractResult(errors=errors.errors)

    if path.is_file():
        if path.suffix.lower() != ".jsonl":
            errors.add("unsupported_source_file", detail=path.name)
            return OpenAICodexExtractResult(errors=errors.errors)
        return parse_session_jsonl(path.read_text(encoding="utf-8"), source_name=str(path))

    index_entries, index_errors = _load_session_index(path)
    session_files = _find_session_files(path)
    errors.errors.extend(index_errors)
    if not session_files:
        errors.add("session_files_not_found", detail=str(path))
        return OpenAICodexExtractResult(errors=errors.errors)

    conversations: list[Conversation] = []
    for session_file in session_files:
        partial = parse_session_jsonl(
            session_file.read_text(encoding="utf-8"),
            source_name=str(session_file),
            index_entries=index_entries,
        )
        conversations.extend(partial.conversations)
        errors.errors.extend(partial.errors)

    return OpenAICodexExtractResult(conversations=conversations, errors=errors.errors)


def parse_session_jsonl(
    raw: str,
    *,
    source_name: str | None = None,
    index_entries: dict[str, CodexSessionIndexEntry] | None = None,
) -> OpenAICodexExtractResult:
    """Parse a single Codex session JSONL document."""
    errors = _ErrorSink()
    fallback_id = _fallback_id_from_source(source_name)
    title_fallback = _fallback_title_from_source(source_name)

    session_id: str | None = None
    session_created_at: datetime | None = None
    valid_line_timestamps: list[datetime] = []
    candidates: list[_MessageCandidate] = []

    for line_number, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.add("invalid_jsonl_line", line_number=line_number, detail=str(exc))
            continue

        if not isinstance(record, dict):
            errors.add(
                "invalid_record",
                line_number=line_number,
                detail=f"expected an object, got {type(record).__name__}",
            )
            continue

        record_type = record.get("type")
        payload = record.get("payload")
        record_id = _record_id(record, line_number)
        line_timestamp = _to_utc(
            record.get("timestamp"),
            errors,
            record_id=record_id,
            line_number=line_number,
            field="timestamp",
        )
        if line_timestamp is not None:
            valid_line_timestamps.append(line_timestamp)

        if not isinstance(record_type, str) or not record_type:
            errors.add(
                "invalid_record_type",
                record_id=record_id,
                line_number=line_number,
                detail=f"expected a non-empty string, got {type(record_type).__name__}",
            )
            continue

        if record_type not in _KNOWN_TOP_LEVEL_TYPES:
            errors.add(
                "unknown_record_type",
                record_id=record_id,
                line_number=line_number,
                detail=f"type={record_type!r}",
            )
            continue

        if not isinstance(payload, dict):
            errors.add(
                "invalid_payload",
                record_id=record_id,
                line_number=line_number,
                detail=f"expected an object, got {type(payload).__name__}",
            )
            continue

        if record_type == "session_meta":
            parsed_id = _session_id_from_payload(payload, errors, record_id, line_number)
            if parsed_id is not None and session_id is None:
                session_id = parsed_id
            parsed_created = _to_utc(
                payload.get("timestamp"),
                errors,
                record_id=record_id,
                line_number=line_number,
                field="payload.timestamp",
            )
            if parsed_created is not None and session_created_at is None:
                session_created_at = parsed_created
            continue

        if record_type == "turn_context":
            continue

        if record_type == "response_item":
            candidate = _message_from_response_item(
                payload,
                record_id=record_id,
                line_number=line_number,
                line_timestamp=line_timestamp,
                errors=errors,
            )
            if candidate is not None:
                candidates.append(candidate)
            continue

        candidate = _message_from_event_msg(
            payload,
            record_id=record_id,
            line_number=line_number,
            line_timestamp=line_timestamp,
            errors=errors,
        )
        if candidate is not None:
            candidates.append(candidate)

    provider_conv_id = session_id or fallback_id
    index_entry = index_entries.get(provider_conv_id) if index_entries else None
    if session_id is None:
        errors.add(
            "missing_session_id",
            record_id=provider_conv_id,
            detail="session_meta.payload.id missing; using filename-derived id",
        )

    messages = _dedupe_and_build_messages(candidates)
    created_at = session_created_at
    if created_at is None and valid_line_timestamps:
        created_at = min(valid_line_timestamps)
    updated_at = _resolve_updated_at(valid_line_timestamps, index_entry)
    title = _resolve_title(index_entry, title_fallback, messages)

    conversation = Conversation(
        provider=PROVIDER,
        provider_conv_id=provider_conv_id,
        title=title,
        url=None,
        created_at=created_at,
        updated_at=updated_at,
        messages=messages,
    )
    return OpenAICodexExtractResult(conversations=[conversation], errors=errors.errors)


def _find_session_files(path: Path) -> list[Path]:
    sessions_dir = path / "sessions"
    search_root = sessions_dir if sessions_dir.is_dir() else path
    return sorted(
        candidate
        for candidate in search_root.rglob("*.jsonl")
        if candidate.name != SESSION_INDEX_FILENAME
    )


def _load_session_index(
    path: Path,
) -> tuple[dict[str, CodexSessionIndexEntry], list[OpenAICodexExtractError]]:
    index_path = path / SESSION_INDEX_FILENAME
    if not index_path.is_file():
        return {}, []

    errors = _ErrorSink()
    entries: dict[str, CodexSessionIndexEntry] = {}
    lines = index_path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.add("invalid_session_index_line", line_number=line_number, detail=str(exc))
            continue
        if not isinstance(record, dict):
            errors.add(
                "invalid_session_index_record",
                line_number=line_number,
                detail=f"expected an object, got {type(record).__name__}",
            )
            continue

        session_id = record.get("id")
        if not isinstance(session_id, str) or not session_id:
            errors.add(
                "invalid_session_index_id",
                line_number=line_number,
                detail=f"expected a non-empty string, got {type(session_id).__name__}",
            )
            continue

        thread_name = record.get("thread_name")
        if thread_name is not None and not isinstance(thread_name, str):
            errors.add(
                "invalid_session_index_title",
                record_id=session_id,
                line_number=line_number,
                detail=f"expected a string, got {type(thread_name).__name__}",
            )
            thread_name = None
        if thread_name == "":
            thread_name = None

        updated_at = _to_utc(
            record.get("updated_at"),
            errors,
            record_id=session_id,
            line_number=line_number,
            field="updated_at",
        )
        entries[session_id] = CodexSessionIndexEntry(
            session_id=session_id,
            thread_name=thread_name,
            updated_at=updated_at,
        )

    return entries, errors.errors


def _session_id_from_payload(
    payload: dict[str, Any],
    errors: _ErrorSink,
    record_id: str,
    line_number: int,
) -> str | None:
    session_id = payload.get("id")
    if session_id is None:
        return None
    if isinstance(session_id, str) and session_id:
        return session_id
    errors.add(
        "invalid_session_id",
        record_id=record_id,
        line_number=line_number,
        detail=f"expected a non-empty string, got {type(session_id).__name__}",
    )
    return None


def _message_from_response_item(
    payload: dict[str, Any],
    *,
    record_id: str,
    line_number: int,
    line_timestamp: datetime | None,
    errors: _ErrorSink,
) -> _MessageCandidate | None:
    item_type = payload.get("type")
    if item_type in _KNOWN_RESPONSE_ITEM_METADATA_TYPES:
        return None

    if item_type != "message":
        if isinstance(item_type, str) and item_type:
            errors.add(
                "unknown_response_item_type",
                record_id=record_id,
                line_number=line_number,
                detail=f"type={item_type!r}",
            )
        else:
            errors.add(
                "invalid_response_item_type",
                record_id=record_id,
                line_number=line_number,
                detail=f"expected a string, got {type(item_type).__name__}",
            )
        return None

    role = payload.get("role")
    if role not in _VISIBLE_RESPONSE_ROLES:
        if role is not None:
            errors.add(
                "invalid_message_role",
                record_id=record_id,
                line_number=line_number,
                detail=f"role={role!r}",
            )
        return None

    body = _text_from_response_content(payload, record_id, line_number, errors)
    if body is None:
        return None

    return _MessageCandidate(
        provider_message_id=_provider_message_id(payload, line_number),
        role=role,
        body=body,
        created_at=line_timestamp,
        line_number=line_number,
        source_kind="response_item",
    )


def _text_from_response_content(
    payload: dict[str, Any],
    record_id: str,
    line_number: int,
    errors: _ErrorSink,
) -> str | None:
    content = payload.get("content")
    if content is None and payload.get("encrypted_content") is not None:
        return None
    if not isinstance(content, list):
        errors.add(
            "invalid_message_content",
            record_id=record_id,
            line_number=line_number,
            detail=f"content: expected a list, got {type(content).__name__}",
        )
        return None

    parts: list[str] = []
    for position, block in enumerate(content):
        if not isinstance(block, dict):
            errors.add(
                "invalid_content_block",
                record_id=record_id,
                line_number=line_number,
                detail=f"content[{position}] is {type(block).__name__}; skipped",
            )
            continue
        block_type = block.get("type")
        text = block.get("text")
        if block_type in _VISIBLE_CONTENT_BLOCK_TYPES and isinstance(text, str):
            if text.strip():
                parts.append(text)
            continue
        if block_type in _VISIBLE_CONTENT_BLOCK_TYPES:
            errors.add(
                "invalid_content_block_text",
                record_id=record_id,
                line_number=line_number,
                detail=f"content[{position}].text is {type(text).__name__}; skipped",
            )
            continue
        errors.add(
            "unknown_content_block_type",
            record_id=record_id,
            line_number=line_number,
            detail=f"content[{position}] type={block_type!r}; skipped",
        )

    body = "\n\n".join(parts).strip()
    return body or None


def _message_from_event_msg(
    payload: dict[str, Any],
    *,
    record_id: str,
    line_number: int,
    line_timestamp: datetime | None,
    errors: _ErrorSink,
) -> _MessageCandidate | None:
    event_type = payload.get("type")
    if event_type not in {"user_message", "agent_message"}:
        if event_type in _KNOWN_EVENT_METADATA_TYPES:
            return None
        if isinstance(event_type, str) and event_type:
            errors.add(
                "unknown_event_msg_type",
                record_id=record_id,
                line_number=line_number,
                detail=f"type={event_type!r}",
            )
        else:
            errors.add(
                "invalid_event_msg_type",
                record_id=record_id,
                line_number=line_number,
                detail=f"expected a string, got {type(event_type).__name__}",
            )
        return None

    role = "user" if event_type == "user_message" else "assistant"
    text = payload.get("text")
    if text is None:
        text = payload.get("message")
    if not isinstance(text, str):
        errors.add(
            "invalid_event_msg_text",
            record_id=record_id,
            line_number=line_number,
            detail=f"expected a string, got {type(text).__name__}",
        )
        return None
    body = text.strip()
    if not body:
        return None

    return _MessageCandidate(
        provider_message_id=_provider_message_id(payload, line_number),
        role=role,
        body=body,
        created_at=line_timestamp,
        line_number=line_number,
        source_kind="event_msg",
    )


def _dedupe_and_build_messages(candidates: list[_MessageCandidate]) -> list[Message]:
    response_keys = {
        (_normalize_role_body(candidate.role, candidate.body))
        for candidate in candidates
        if candidate.source_kind == "response_item"
    }
    seen_response_keys: set[tuple[str, str]] = set()
    kept: list[_MessageCandidate] = []

    for candidate in candidates:
        key = _normalize_role_body(candidate.role, candidate.body)
        if candidate.source_kind == "event_msg" and key in response_keys:
            continue
        if candidate.source_kind == "response_item":
            if key in seen_response_keys:
                continue
            seen_response_keys.add(key)
        kept.append(candidate)

    kept.sort(key=lambda candidate: candidate.line_number)
    return [
        Message(
            provider_message_id=candidate.provider_message_id,
            role=candidate.role,
            created_at=candidate.created_at,
            body=candidate.body,
            seq=index,
        )
        for index, candidate in enumerate(kept)
    ]


def _normalize_role_body(role: str, body: str) -> tuple[str, str]:
    return role, "\n".join(line.rstrip() for line in body.strip().splitlines())


def _resolve_title(
    index_entry: CodexSessionIndexEntry | None,
    title_fallback: str,
    messages: list[Message],
) -> str:
    if index_entry is not None and index_entry.thread_name:
        return index_entry.thread_name
    first_user = next((message.body for message in messages if message.role == "user"), None)
    if first_user:
        return _prefix(first_user)
    return title_fallback


def _resolve_updated_at(
    valid_line_timestamps: list[datetime],
    index_entry: CodexSessionIndexEntry | None,
) -> datetime | None:
    candidates = list(valid_line_timestamps)
    if index_entry is not None and index_entry.updated_at is not None:
        candidates.append(index_entry.updated_at)
    if not candidates:
        return None
    return max(candidates)


def _provider_message_id(payload: dict[str, Any], line_number: int) -> str:
    for key in ("id", "call_id"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return f"line-{line_number}"


def _record_id(record: dict[str, Any], line_number: int) -> str:
    payload = record.get("payload")
    if isinstance(payload, dict):
        for key in ("id", "call_id"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
    return f"line-{line_number}"


def _fallback_id_from_source(source_name: str | None) -> str:
    if source_name:
        stem = Path(source_name).stem
        if stem:
            return stem
    return "codex-session"


def _fallback_title_from_source(source_name: str | None) -> str:
    return _fallback_id_from_source(source_name)


def _prefix(text: str, *, limit: int = 80) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 1].rstrip()}..."


def _to_utc(
    value: object,
    errors: _ErrorSink,
    *,
    record_id: str | None,
    line_number: int | None,
    field: str,
) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.add(
            "invalid_timestamp",
            record_id=record_id,
            line_number=line_number,
            detail=f"{field}: expected an ISO8601 string, got {type(value).__name__}",
        )
        return None

    candidate = value.strip()
    if candidate.endswith(("Z", "z")):
        candidate = f"{candidate[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        errors.add(
            "invalid_timestamp",
            record_id=record_id,
            line_number=line_number,
            detail=f"{field}: {value!r} is not ISO8601 ({exc})",
        )
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
