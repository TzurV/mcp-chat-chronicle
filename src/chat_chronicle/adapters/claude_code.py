"""Claude Code local-session extractor.

Parses Claude Code JSONL session files from the local ``.claude/projects``
store and converts visible transcript text into normalized conversations.

Claude Code local storage is a Class B source: useful and durable, but
undocumented and version-sensitive. This module is intentionally concrete and
tolerant. Known metadata/tooling rows are skipped, malformed lines are recorded
as serializable errors, and unknown records are reported without aborting the
rest of the input.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PureWindowsPath
from typing import Any

from pydantic import BaseModel, Field

from chat_chronicle.models import Conversation, Message

PROVIDER = "claude_code"

_VISIBLE_ROLES = frozenset({"user", "assistant", "system", "developer"})
_CHAT_RECORD_TYPES = frozenset({"user", "assistant", "system", "developer"})
_KNOWN_METADATA_RECORD_TYPES = frozenset(
    {
        "summary",
        "file-history-snapshot",
        "attachment",
        "last-prompt",
        "queue-operation",
        "mode",
        "ai-title",
        "custom-title",
        "agent-name",
    }
)
_KNOWN_TOOL_BLOCK_TYPES = frozenset(
    {"tool_use", "tool-use", "tool_call", "tool-call", "tool_result", "tool-result"}
)
_KNOWN_NON_TEXT_BLOCK_TYPES = _KNOWN_TOOL_BLOCK_TYPES | frozenset({"thinking", "image", "document"})


class ClaudeCodeExtractError(BaseModel):
    """A single non-fatal extractor problem, serializable into JSON."""

    record_id: str | None = None
    line_number: int | None = None
    error: str
    detail: str | None = None


class ClaudeCodeProjectHint(BaseModel):
    """Best-effort project identity inferred without DB writes."""

    name: str
    root_path: str | None = None


class ClaudeCodeExtractResult(BaseModel):
    conversations: list[Conversation] = Field(default_factory=list)
    errors: list[ClaudeCodeExtractError] = Field(default_factory=list)
    project_hints: dict[str, ClaudeCodeProjectHint] = Field(default_factory=dict)


class _ErrorSink:
    def __init__(self) -> None:
        self.errors: list[ClaudeCodeExtractError] = []

    def add(
        self,
        error: str,
        *,
        record_id: str | None = None,
        line_number: int | None = None,
        detail: str | None = None,
    ) -> None:
        self.errors.append(
            ClaudeCodeExtractError(
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


def load_conversations(source: Path | str) -> ClaudeCodeExtractResult:
    """Parse one Claude Code JSONL file, one project dir, or a projects root."""
    path = Path(source)
    errors = _ErrorSink()

    if not path.exists():
        errors.add("source_not_found", detail=str(path))
        return ClaudeCodeExtractResult(errors=errors.errors)

    if path.is_file():
        if path.suffix.lower() != ".jsonl":
            errors.add("unsupported_source_file", detail=path.name)
            return ClaudeCodeExtractResult(errors=errors.errors)
        return parse_session_jsonl(
            path.read_text(encoding="utf-8"),
            source_name=str(path.resolve()),
            project_dir_name=path.parent.name,
        )

    session_files = _find_session_files(path)
    if not session_files:
        errors.add("session_files_not_found", detail=str(path))
        return ClaudeCodeExtractResult(errors=errors.errors)

    conversations: list[Conversation] = []
    project_hints: dict[str, ClaudeCodeProjectHint] = {}
    for session_file in session_files:
        partial = parse_session_jsonl(
            session_file.read_text(encoding="utf-8"),
            source_name=str(session_file.resolve()),
            project_dir_name=session_file.parent.name,
        )
        conversations.extend(partial.conversations)
        errors.errors.extend(partial.errors)
        project_hints.update(partial.project_hints)

    return ClaudeCodeExtractResult(
        conversations=conversations,
        errors=errors.errors,
        project_hints=project_hints,
    )


def parse_session_jsonl(
    raw: str,
    *,
    source_name: str | None = None,
    project_dir_name: str | None = None,
) -> ClaudeCodeExtractResult:
    """Parse a single Claude Code session JSONL document."""
    errors = _ErrorSink()
    fallback_id = _fallback_id_from_source(source_name)
    session_id: str | None = None
    title: str | None = None
    cwd: str | None = None
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

        parsed_session_id = _string_value(record.get("sessionId"))
        if session_id is None and parsed_session_id:
            session_id = parsed_session_id
        if cwd is None:
            cwd = _string_value(record.get("cwd")) or _string_value(record.get("project"))

        record_type = record.get("type")
        if not isinstance(record_type, str) or not record_type:
            errors.add(
                "invalid_record_type",
                record_id=record_id,
                line_number=line_number,
                detail=f"expected a non-empty string, got {type(record_type).__name__}",
            )
            continue
        normalized_type = record_type.lower()

        if normalized_type in {"ai-title", "custom-title", "agent-name"}:
            title = title or _title_from_metadata_record(record, normalized_type)
            continue

        if normalized_type in _KNOWN_METADATA_RECORD_TYPES:
            continue

        if normalized_type not in _CHAT_RECORD_TYPES:
            errors.add(
                "unknown_record_type",
                record_id=record_id,
                line_number=line_number,
                detail=f"type={record_type!r}",
            )
            continue

        candidate = _message_from_chat_record(
            record,
            record_type=normalized_type,
            record_id=record_id,
            line_number=line_number,
            line_timestamp=line_timestamp,
            errors=errors,
        )
        if candidate is not None:
            candidates.append(candidate)

    provider_conv_id = _provider_conversation_id(session_id, fallback_id, source_name)
    resume_session_id = session_id or fallback_id
    if session_id is None:
        errors.add(
            "missing_session_id",
            record_id=provider_conv_id,
            detail="sessionId missing; using filename-derived id",
        )

    messages = _build_messages(candidates)
    created_at = min(valid_line_timestamps) if valid_line_timestamps else None
    updated_at = max(valid_line_timestamps) if valid_line_timestamps else None
    resolved_title = _resolve_title(title, messages, fallback_id)
    project_hint = _project_hint(cwd, project_dir_name)

    conversation = Conversation(
        provider=PROVIDER,
        provider_conv_id=provider_conv_id,
        title=resolved_title,
        url=None,
        origin_path=_origin_path_from_source(source_name),
        resume_hint=f"claude --resume {resume_session_id}" if resume_session_id else None,
        created_at=created_at,
        updated_at=updated_at,
        messages=messages,
    )
    project_hints = {provider_conv_id: project_hint} if project_hint is not None else {}
    return ClaudeCodeExtractResult(
        conversations=[conversation],
        errors=errors.errors,
        project_hints=project_hints,
    )


def _find_session_files(path: Path) -> list[Path]:
    return sorted(candidate for candidate in path.rglob("*.jsonl") if candidate.is_file())


def _message_from_chat_record(
    record: dict[str, Any],
    *,
    record_type: str,
    record_id: str,
    line_number: int,
    line_timestamp: datetime | None,
    errors: _ErrorSink,
) -> _MessageCandidate | None:
    message = record.get("message")
    role = record_type
    content_source: dict[str, Any] = record
    if isinstance(message, dict):
        role = _string_value(message.get("role")) or role
        content_source = message
    elif message is not None:
        errors.add(
            "invalid_message",
            record_id=record_id,
            line_number=line_number,
            detail=f"expected an object, got {type(message).__name__}",
        )
        return None

    role = _normalize_role(role)
    if role not in _VISIBLE_ROLES:
        errors.add(
            "invalid_message_role",
            record_id=record_id,
            line_number=line_number,
            detail=f"role={role!r}",
        )
        return None

    body = _text_from_content(content_source, record_id, line_number, errors)
    if body is None:
        return None

    return _MessageCandidate(
        provider_message_id=_string_value(record.get("uuid")) or f"line-{line_number}",
        role=role,
        body=body,
        created_at=line_timestamp,
        line_number=line_number,
    )


def _text_from_content(
    source: dict[str, Any],
    record_id: str,
    line_number: int,
    errors: _ErrorSink,
) -> str | None:
    content = source.get("content")
    if isinstance(content, str):
        body = content.strip()
        return body or None
    if isinstance(content, list):
        parts: list[str] = []
        for position, block in enumerate(content):
            if isinstance(block, str):
                if block.strip():
                    parts.append(block)
                continue
            if not isinstance(block, dict):
                errors.add(
                    "invalid_content_block",
                    record_id=record_id,
                    line_number=line_number,
                    detail=f"content[{position}] is {type(block).__name__}; skipped",
                )
                continue
            block_type = _string_value(block.get("type"))
            normalized_type = block_type.lower() if block_type else None
            if normalized_type == "text":
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text)
                elif text is not None:
                    errors.add(
                        "invalid_content_block_text",
                        record_id=record_id,
                        line_number=line_number,
                        detail=f"content[{position}].text is {type(text).__name__}; skipped",
                    )
                continue
            if normalized_type in _KNOWN_NON_TEXT_BLOCK_TYPES:
                continue
            if block.get("text") is not None:
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text)
                    continue
            errors.add(
                "unknown_content_block_type",
                record_id=record_id,
                line_number=line_number,
                detail=f"content[{position}] type={block_type!r}; skipped",
            )
        body = "\n\n".join(part.strip() for part in parts if part.strip()).strip()
        return body or None

    if content is None:
        return None

    errors.add(
        "invalid_message_content",
        record_id=record_id,
        line_number=line_number,
        detail=f"content: expected string or list, got {type(content).__name__}",
    )
    return None


def _build_messages(candidates: list[_MessageCandidate]) -> list[Message]:
    candidates.sort(key=lambda candidate: candidate.line_number)
    return [
        Message(
            provider_message_id=candidate.provider_message_id,
            role=candidate.role,
            created_at=candidate.created_at,
            body=candidate.body,
            seq=index,
        )
        for index, candidate in enumerate(candidates)
    ]


def _resolve_title(title: str | None, messages: list[Message], fallback_id: str) -> str:
    if title:
        return _prefix(title)
    first_user = next((message.body for message in messages if message.role == "user"), None)
    if first_user:
        return _prefix(first_user)
    return fallback_id


def _title_from_metadata_record(record: dict[str, Any], record_type: str) -> str | None:
    if record_type == "ai-title":
        return _string_value(record.get("aiTitle"))
    if record_type == "custom-title":
        return _string_value(record.get("customTitle"))
    if record_type == "agent-name":
        return _string_value(record.get("agentName"))
    return None


def _project_hint(cwd: str | None, project_dir_name: str | None) -> ClaudeCodeProjectHint | None:
    if cwd:
        root = str(Path(cwd).expanduser())
        # A recorded cwd may be a Windows path parsed on POSIX (backslash
        # separators that PosixPath treats as a filename) or vice-versa. Take
        # the trailing segment regardless of separator style so the project
        # name is derived correctly on any OS.
        name = PureWindowsPath(root).name or Path(root).name or root
        return ClaudeCodeProjectHint(name=name, root_path=root)
    if project_dir_name:
        return ClaudeCodeProjectHint(name=project_dir_name, root_path=None)
    return None


def _record_id(record: dict[str, Any], line_number: int) -> str:
    for key in ("uuid", "sessionId", "requestId"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return f"line-{line_number}"


def _fallback_id_from_source(source_name: str | None) -> str:
    if source_name:
        stem = Path(source_name).stem
        if stem:
            return stem
    return "claude-code-session"


def _provider_conversation_id(
    session_id: str | None,
    fallback_id: str,
    source_name: str | None,
) -> str:
    """Return a file-scoped provider id so same-session files do not overwrite."""
    base_id = session_id or fallback_id
    if source_name is None:
        return base_id
    file_stem = Path(source_name).stem or "session"
    identity = str(Path(source_name).expanduser().resolve(strict=False))
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
    return f"{base_id}::{file_stem}::{digest}"


def _origin_path_from_source(source_name: str | None) -> str | None:
    if not source_name:
        return None
    return str(Path(source_name).expanduser().resolve(strict=False))


def _prefix(text: str, *, limit: int = 80) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 1].rstrip()}..."


def _normalize_role(role: str) -> str:
    lowered = role.strip().lower()
    if lowered == "human":
        return "user"
    if lowered == "model":
        return "assistant"
    return lowered


def _string_value(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


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
