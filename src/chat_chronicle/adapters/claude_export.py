"""Claude official-export importer.

Parses ``conversations.json`` from an official Claude data export and converts
each conversation into the normalized :class:`~chat_chronicle.models.Conversation`
and :class:`~chat_chronicle.models.Message` models.

The export is a flat JSON array of conversation objects (``uuid``, ``name``,
``created_at``, ``chat_messages[]``) rather than the tree-shaped ``mapping``
used by the ChatGPT export, so this module shares no code with
:mod:`chat_chronicle.adapters.chatgpt_export`. Like that module it is
deliberately concrete: the shared adapter abstraction is only extracted once
three adapters exist (master plan design rule 2).

Parse problems are data, not exceptions: a malformed conversation or message is
recorded in :class:`ClaudeImportResult.errors` and the remaining records still
parse.
"""

from __future__ import annotations

import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from chat_chronicle.models import Conversation, Message

PROVIDER = "claude"
CONVERSATIONS_FILENAME = "conversations.json"
_URL_TEMPLATE = "https://claude.ai/chat/{conv_id}"


class ClaudeImportError(BaseModel):
    """A single non-fatal parse problem, serializable into ``ingest_runs.errors_json``."""

    record_id: str | None = None
    message_id: str | None = None
    error: str
    detail: str | None = None


class ClaudeImportResult(BaseModel):
    conversations: list[Conversation] = Field(default_factory=list)
    errors: list[ClaudeImportError] = Field(default_factory=list)


class _ErrorSink:
    """Collects parse errors scoped to the conversation currently being parsed."""

    def __init__(self) -> None:
        self.errors: list[ClaudeImportError] = []

    def add(
        self,
        error: str,
        *,
        record_id: str | None = None,
        message_id: str | None = None,
        detail: str | None = None,
    ) -> None:
        self.errors.append(
            ClaudeImportError(
                record_id=record_id, message_id=message_id, error=error, detail=detail
            )
        )


def load_conversations(source: Path | str) -> ClaudeImportResult:
    """Parse a Claude export from a zip, a directory, or a ``conversations.json`` path."""
    path = Path(source)
    errors = _ErrorSink()

    if not path.exists():
        errors.add("source_not_found", detail=str(path))
        return ClaudeImportResult(errors=errors.errors)

    if path.is_dir():
        candidate = path / CONVERSATIONS_FILENAME
        if not candidate.is_file():
            errors.add("conversations_json_not_found", detail=str(candidate))
            return ClaudeImportResult(errors=errors.errors)
        return _parse_json_text(candidate.read_text(encoding="utf-8"), str(candidate))

    if zipfile.is_zipfile(path):
        return _parse_zip(path)

    return _parse_json_text(path.read_text(encoding="utf-8"), str(path))


def _parse_zip(path: Path) -> ClaudeImportResult:
    errors = _ErrorSink()
    with zipfile.ZipFile(path) as archive:
        member = _find_conversations_member(archive)
        if member is None:
            errors.add("conversations_json_not_found", detail=str(path))
            return ClaudeImportResult(errors=errors.errors)
        raw = archive.read(member).decode("utf-8")
    return _parse_json_text(raw, f"{path}::{member}")


def _find_conversations_member(archive: zipfile.ZipFile) -> str | None:
    """Return the shallowest ``conversations.json`` member, if any."""
    candidates = [
        name
        for name in archive.namelist()
        if not name.endswith("/") and Path(name).name == CONVERSATIONS_FILENAME
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda name: (name.count("/"), name))


def _parse_json_text(raw: str, origin: str) -> ClaudeImportResult:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return ClaudeImportResult(
            errors=[ClaudeImportError(error="invalid_json", detail=f"{origin}: {exc}")]
        )
    return parse_conversations_json(data)


def parse_conversations_json(data: object) -> ClaudeImportResult:
    """Parse the decoded ``conversations.json`` payload (a flat list of conversations)."""
    if not isinstance(data, list):
        return ClaudeImportResult(
            errors=[
                ClaudeImportError(
                    error="unexpected_export_shape",
                    detail=f"expected a list of conversations, got {type(data).__name__}",
                )
            ]
        )

    conversations: list[Conversation] = []
    errors: list[ClaudeImportError] = []

    for index, record in enumerate(data):
        sink = _ErrorSink()
        conversation = _parse_conversation(record, index, sink)
        errors.extend(sink.errors)
        if conversation is not None:
            conversations.append(conversation)

    return ClaudeImportResult(conversations=conversations, errors=errors)


def _parse_conversation(record: object, index: int, errors: _ErrorSink) -> Conversation | None:
    if not isinstance(record, dict):
        errors.add(
            "invalid_conversation_record",
            record_id=str(index),
            detail=f"expected an object, got {type(record).__name__}",
        )
        return None

    conv_id = record.get("uuid")
    if not isinstance(conv_id, str) or not conv_id:
        errors.add(
            "missing_conversation_uuid",
            record_id=str(index),
            detail="conversation has no usable string 'uuid'",
        )
        return None

    title = record.get("name")
    if title is not None and not isinstance(title, str):
        errors.add("invalid_title", record_id=conv_id, detail=f"got {type(title).__name__}")
        title = None
    if title == "":
        title = None

    created_at = _to_utc(record.get("created_at"), conv_id, None, "created_at", errors)
    messages = _build_messages(record.get("chat_messages"), conv_id, errors)
    updated_at = _resolve_updated_at(record, messages, created_at, conv_id, errors)

    return Conversation(
        provider=PROVIDER,
        provider_conv_id=conv_id,
        title=title,
        url=_URL_TEMPLATE.format(conv_id=conv_id),
        created_at=created_at,
        updated_at=updated_at,
        messages=messages,
    )


def _resolve_updated_at(
    record: dict[str, Any],
    messages: list[Message],
    created_at: datetime | None,
    conv_id: str,
    errors: _ErrorSink,
) -> datetime | None:
    """Prefer the conversation's own ``updated_at``, else the newest message, else creation."""
    updated_at = _to_utc(record.get("updated_at"), conv_id, None, "updated_at", errors)
    if updated_at is not None:
        return updated_at

    message_times = [message.created_at for message in messages if message.created_at is not None]
    if message_times:
        return max(message_times)

    return created_at


def _build_messages(
    chat_messages: object,
    conv_id: str,
    errors: _ErrorSink,
) -> list[Message]:
    if chat_messages is None:
        errors.add(
            "missing_chat_messages",
            record_id=conv_id,
            detail="conversation has no 'chat_messages'; parsed with an empty message list",
        )
        return []

    if not isinstance(chat_messages, list):
        errors.add(
            "invalid_chat_messages",
            record_id=conv_id,
            detail=(
                f"expected a list, got {type(chat_messages).__name__}; "
                "parsed with an empty message list"
            ),
        )
        return []

    messages: list[Message] = []
    for position, raw_message in enumerate(chat_messages):
        message = _parse_message(raw_message, position, len(messages), conv_id, errors)
        if message is not None:
            messages.append(message)
    return messages


def _parse_message(
    raw_message: object,
    position: int,
    seq: int,
    conv_id: str,
    errors: _ErrorSink,
) -> Message | None:
    if not isinstance(raw_message, dict):
        errors.add(
            "invalid_message_record",
            record_id=conv_id,
            message_id=str(position),
            detail=f"chat_messages[{position}] is {type(raw_message).__name__}; skipped",
        )
        return None

    message_id = _extract_message_id(raw_message)
    # Fall back to the array position so downstream errors stay locatable.
    error_id = message_id or str(position)

    body = _extract_body(raw_message, conv_id, error_id, errors)
    if not body:
        return None

    return Message(
        provider_message_id=message_id,
        role=_extract_role(raw_message, conv_id, error_id, errors),
        created_at=_to_utc(raw_message.get("created_at"), conv_id, error_id, "created_at", errors),
        body=body,
        seq=seq,
    )


def _extract_message_id(message: dict[str, Any]) -> str | None:
    for key in ("uuid", "id"):
        value = message.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _extract_role(
    message: dict[str, Any], conv_id: str, message_id: str, errors: _ErrorSink
) -> str | None:
    for key in ("sender", "role"):
        value = message.get(key)
        if value is None:
            continue
        if isinstance(value, str) and value:
            return value
        errors.add(
            "invalid_role",
            record_id=conv_id,
            message_id=message_id,
            detail=f"{key}: expected a non-empty string, got {type(value).__name__}",
        )
        return None
    return None


def _extract_body(
    message: dict[str, Any], conv_id: str, message_id: str, errors: _ErrorSink
) -> str | None:
    """Collect text from ``content[]`` blocks, falling back to the flat ``text`` field."""
    content = message.get("content")
    if content is not None:
        parts = _text_from_content(content, conv_id, message_id, errors)
        body = "\n\n".join(parts).strip()
        if body:
            return body

    text = message.get("text")
    if isinstance(text, str):
        return text.strip() or None
    if text is not None:
        errors.add(
            "invalid_message_text",
            record_id=conv_id,
            message_id=message_id,
            detail=f"text: expected a string, got {type(text).__name__}",
        )

    if content is None:
        errors.add(
            "missing_message_content",
            record_id=conv_id,
            message_id=message_id,
            detail="message has neither 'content' nor 'text'; skipped",
        )
    return None


def _text_from_content(
    content: object, conv_id: str, message_id: str, errors: _ErrorSink
) -> list[str]:
    if isinstance(content, str):
        return [content] if content.strip() else []

    if not isinstance(content, list):
        errors.add(
            "invalid_message_content",
            record_id=conv_id,
            message_id=message_id,
            detail=f"content: expected a list or string, got {type(content).__name__}",
        )
        return []

    parts: list[str] = []
    for position, block in enumerate(content):
        if isinstance(block, str):
            if block.strip():
                parts.append(block)
            continue
        if not isinstance(block, dict):
            errors.add(
                "invalid_content_block",
                record_id=conv_id,
                message_id=message_id,
                detail=f"content[{position}] is {type(block).__name__}; skipped",
            )
            continue

        block_type = block.get("type")
        text = block.get("text")
        if isinstance(text, str):
            if text.strip():
                parts.append(text)
            continue

        errors.add(
            "non_text_content_block",
            record_id=conv_id,
            message_id=message_id,
            detail=f"content[{position}] type={block_type!r} has no 'text'; skipped",
        )
    return parts


def _to_utc(
    value: object,
    conv_id: str | None,
    message_id: str | None,
    field: str,
    errors: _ErrorSink,
) -> datetime | None:
    """Convert an ISO8601 timestamp to an aware UTC datetime, or ``None``."""
    if value is None:
        return None
    if not isinstance(value, str):
        errors.add(
            "invalid_timestamp",
            record_id=conv_id,
            message_id=message_id,
            detail=f"{field}: expected an ISO8601 string, got {type(value).__name__}",
        )
        return None

    # ``fromisoformat`` accepts offsets but not the trailing ``Z`` before 3.11.
    candidate = value.strip()
    if candidate.endswith(("Z", "z")):
        candidate = f"{candidate[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        errors.add(
            "invalid_timestamp",
            record_id=conv_id,
            message_id=message_id,
            detail=f"{field}: {value!r} is not ISO8601 ({exc})",
        )
        return None

    if parsed.tzinfo is None:
        # Claude exports timestamps in UTC; a naive value is read as such.
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
