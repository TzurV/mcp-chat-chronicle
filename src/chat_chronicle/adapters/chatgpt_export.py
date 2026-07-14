"""ChatGPT official-export importer.

Parses ``conversations.json`` or split ``conversations-*.json`` files from an
official ChatGPT data export and converts each conversation into the normalized
:class:`~chat_chronicle.models.Conversation` and
:class:`~chat_chronicle.models.Message` models.

This module is deliberately concrete. The shared adapter abstraction is only
extracted once three adapters exist (master plan design rule 2).

Parse problems are data, not exceptions: a malformed conversation or node is
recorded in :class:`ChatGPTImportResult.errors` and the remaining records still
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

PROVIDER = "chatgpt"
CONVERSATIONS_FILENAME = "conversations.json"
SPLIT_CONVERSATIONS_GLOB = "conversations-*.json"
_URL_TEMPLATE = "https://chatgpt.com/c/{conv_id}"
_SILENT_METADATA_CONTENT_TYPES = {"thoughts", "reasoning_recap"}

# Guards against a cyclic or self-referential ``parent`` chain in ``mapping``.
_MAX_CHAIN_DEPTH = 100_000


class ChatGPTImportError(BaseModel):
    """A single non-fatal parse problem, serializable into ``ingest_runs.errors_json``."""

    record_id: str | None = None
    node_id: str | None = None
    error: str
    detail: str | None = None


class ChatGPTImportResult(BaseModel):
    conversations: list[Conversation] = Field(default_factory=list)
    errors: list[ChatGPTImportError] = Field(default_factory=list)


class _ErrorSink:
    """Collects parse errors scoped to the conversation currently being parsed."""

    def __init__(self) -> None:
        self.errors: list[ChatGPTImportError] = []

    def add(
        self,
        error: str,
        *,
        record_id: str | None = None,
        node_id: str | None = None,
        detail: str | None = None,
    ) -> None:
        self.errors.append(
            ChatGPTImportError(record_id=record_id, node_id=node_id, error=error, detail=detail)
        )


def load_conversations(source: Path | str) -> ChatGPTImportResult:
    """Parse a ChatGPT export from a zip, a directory, or a conversations JSON path."""
    path = Path(source)
    errors = _ErrorSink()

    if not path.exists():
        errors.add("source_not_found", detail=str(path))
        return ChatGPTImportResult(errors=errors.errors)

    if path.is_dir():
        candidate = path / CONVERSATIONS_FILENAME
        if candidate.is_file():
            return _parse_json_text(candidate.read_text(encoding="utf-8"), str(candidate))

        split_candidates = _find_split_conversations_paths(path)
        if not split_candidates:
            errors.add("conversations_json_not_found", detail=str(candidate))
            return ChatGPTImportResult(errors=errors.errors)
        return _parse_split_files(split_candidates)

    if zipfile.is_zipfile(path):
        return _parse_zip(path)

    return _parse_json_text(path.read_text(encoding="utf-8"), str(path))


def _parse_zip(path: Path) -> ChatGPTImportResult:
    errors = _ErrorSink()
    with zipfile.ZipFile(path) as archive:
        member = _find_conversations_member(archive)
        if member is not None:
            raw = archive.read(member).decode("utf-8")
            return _parse_json_text(raw, f"{path}::{member}")

        split_members = _find_split_conversations_members(archive)
        if not split_members:
            errors.add("conversations_json_not_found", detail=str(path))
            return ChatGPTImportResult(errors=errors.errors)
        sources: list[tuple[str, str]] = []
        for member in split_members:
            origin = f"{path}::{member}"
            try:
                sources.append((origin, archive.read(member).decode("utf-8")))
            except UnicodeDecodeError as exc:
                errors.add("invalid_encoding", detail=f"{origin}: {exc}")
    parsed = _parse_split_sources(sources)
    return ChatGPTImportResult(
        conversations=parsed.conversations,
        errors=errors.errors + parsed.errors,
    )


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


def _find_split_conversations_members(archive: zipfile.ZipFile) -> list[str]:
    return sorted(
        name
        for name in archive.namelist()
        if not name.endswith("/") and _is_split_conversations_name(Path(name).name)
    )


def _find_split_conversations_paths(path: Path) -> list[Path]:
    return sorted(
        candidate
        for candidate in path.rglob(SPLIT_CONVERSATIONS_GLOB)
        if candidate.is_file() and _is_split_conversations_name(candidate.name)
    )


def _is_split_conversations_name(name: str) -> bool:
    return name.startswith("conversations-") and name.endswith(".json")


def _parse_json_text(raw: str, origin: str) -> ChatGPTImportResult:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return ChatGPTImportResult(
            errors=[ChatGPTImportError(error="invalid_json", detail=f"{origin}: {exc}")]
        )
    return parse_conversations_json(data)


def _parse_split_files(paths: list[Path]) -> ChatGPTImportResult:
    errors = _ErrorSink()
    sources: list[tuple[str, str]] = []
    for path in paths:
        try:
            sources.append((str(path), path.read_text(encoding="utf-8")))
        except UnicodeDecodeError as exc:
            errors.add("invalid_encoding", detail=f"{path}: {exc}")
    parsed = _parse_split_sources(sources)
    return ChatGPTImportResult(
        conversations=parsed.conversations,
        errors=errors.errors + parsed.errors,
    )


def _parse_split_sources(sources: list[tuple[str, str]]) -> ChatGPTImportResult:
    records: list[object] = []
    errors = _ErrorSink()

    for origin, raw in sources:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.add("invalid_json", detail=f"{origin}: {exc}")
            continue
        if not isinstance(data, list):
            errors.add(
                "unexpected_export_shape",
                detail=f"{origin}: expected a list of conversations, got {type(data).__name__}",
            )
            continue
        records.extend(data)

    parsed = parse_conversations_json(records)
    return ChatGPTImportResult(
        conversations=parsed.conversations,
        errors=errors.errors + parsed.errors,
    )


def parse_conversations_json(data: object) -> ChatGPTImportResult:
    """Parse the decoded ``conversations.json`` payload (a list of conversation objects)."""
    if not isinstance(data, list):
        return ChatGPTImportResult(
            errors=[
                ChatGPTImportError(
                    error="unexpected_export_shape",
                    detail=f"expected a list of conversations, got {type(data).__name__}",
                )
            ]
        )

    conversations: list[Conversation] = []
    errors: list[ChatGPTImportError] = []

    for index, record in enumerate(data):
        sink = _ErrorSink()
        conversation = _parse_conversation(record, index, sink)
        errors.extend(sink.errors)
        if conversation is not None:
            conversations.append(conversation)

    return ChatGPTImportResult(conversations=conversations, errors=errors)


def _parse_conversation(record: object, index: int, errors: _ErrorSink) -> Conversation | None:
    if not isinstance(record, dict):
        errors.add(
            "invalid_conversation_record",
            record_id=str(index),
            detail=f"expected an object, got {type(record).__name__}",
        )
        return None

    conv_id = record.get("conversation_id") or record.get("id")
    if not isinstance(conv_id, str) or not conv_id:
        errors.add(
            "missing_conversation_id",
            record_id=str(index),
            detail="conversation has no usable string 'id'",
        )
        return None

    mapping = record.get("mapping")
    if not isinstance(mapping, dict):
        errors.add(
            "missing_mapping",
            record_id=conv_id,
            detail=f"expected an object, got {type(mapping).__name__}",
        )
        return None

    title = record.get("title")
    if title is not None and not isinstance(title, str):
        errors.add("invalid_title", record_id=conv_id, detail=f"got {type(title).__name__}")
        title = None

    created_at = _to_utc(record.get("create_time"), conv_id, None, "create_time", errors)
    updated_at = _to_utc(record.get("update_time"), conv_id, None, "update_time", errors)

    chain = _linearize(mapping, record.get("current_node"), conv_id, errors)
    messages = _build_messages(mapping, chain, conv_id, errors)

    return Conversation(
        provider=PROVIDER,
        provider_conv_id=conv_id,
        title=title,
        url=_URL_TEMPLATE.format(conv_id=conv_id),
        created_at=created_at,
        updated_at=updated_at,
        messages=messages,
    )


def _linearize(
    mapping: dict[str, Any],
    current_node: object,
    conv_id: str,
    errors: _ErrorSink,
) -> list[str]:
    """Return node ids from root to leaf for the selected branch."""
    if isinstance(current_node, str) and current_node in mapping:
        chain = _chain_to_root(mapping, current_node, conv_id, errors)
        if chain:
            return chain
        return []

    if current_node is not None:
        errors.add(
            "invalid_current_node",
            record_id=conv_id,
            detail=f"{current_node!r} is not a key in mapping; falling back to deepest chain",
        )
    else:
        errors.add(
            "missing_current_node",
            record_id=conv_id,
            detail="falling back to deepest chain",
        )

    return _deepest_chain(mapping, conv_id, errors)


def _chain_to_root(
    mapping: dict[str, Any],
    leaf_id: str,
    conv_id: str,
    errors: _ErrorSink,
) -> list[str]:
    """Follow ``parent`` pointers from ``leaf_id`` to the root, then reverse."""
    chain: list[str] = []
    seen: set[str] = set()
    node_id: str | None = leaf_id

    while node_id is not None:
        if node_id in seen:
            errors.add(
                "cyclic_parent_chain",
                record_id=conv_id,
                node_id=node_id,
                detail="parent chain revisits a node; truncating here",
            )
            break
        if len(chain) >= _MAX_CHAIN_DEPTH:
            errors.add(
                "parent_chain_too_deep",
                record_id=conv_id,
                node_id=node_id,
                detail=f"exceeded {_MAX_CHAIN_DEPTH} nodes; truncating here",
            )
            break

        node = mapping.get(node_id)
        if not isinstance(node, dict):
            errors.add(
                "broken_parent_chain",
                record_id=conv_id,
                node_id=node_id,
                detail="parent id is not present in mapping; truncating here",
            )
            break

        seen.add(node_id)
        chain.append(node_id)

        parent = node.get("parent")
        if parent is None:
            break
        if not isinstance(parent, str):
            errors.add(
                "invalid_parent",
                record_id=conv_id,
                node_id=node_id,
                detail=f"expected a string parent id, got {type(parent).__name__}",
            )
            break
        node_id = parent

    chain.reverse()
    return chain


def _deepest_chain(mapping: dict[str, Any], conv_id: str, errors: _ErrorSink) -> list[str]:
    """Select the longest message-bearing root-to-leaf chain in ``mapping``."""
    leaves = [
        node_id
        for node_id, node in mapping.items()
        if isinstance(node, dict) and not _child_ids(node)
    ]
    if not leaves:
        leaves = [node_id for node_id, node in mapping.items() if isinstance(node, dict)]

    best: list[str] = []
    best_score = -1
    for leaf_id in leaves:
        # Probe with a throwaway sink so fallback exploration does not spam errors
        # for the branches we ultimately discard.
        chain = _chain_to_root(mapping, leaf_id, conv_id, _ErrorSink())
        score = sum(1 for node_id in chain if _node_message(mapping[node_id]) is not None)
        if score > best_score or (score == best_score and len(chain) > len(best)):
            best, best_score = chain, score

    if best_score <= 0:
        errors.add(
            "no_message_bearing_chain",
            record_id=conv_id,
            detail="mapping contains no node with a message",
        )
        return []
    return best


def _child_ids(node: dict[str, Any]) -> list[str]:
    children = node.get("children")
    if not isinstance(children, list):
        return []
    return [child for child in children if isinstance(child, str)]


def _node_message(node: object) -> dict[str, Any] | None:
    if not isinstance(node, dict):
        return None
    message = node.get("message")
    return message if isinstance(message, dict) else None


def _build_messages(
    mapping: dict[str, Any],
    chain: list[str],
    conv_id: str,
    errors: _ErrorSink,
) -> list[Message]:
    messages: list[Message] = []
    for node_id in chain:
        message = _node_message(mapping.get(node_id))
        if message is None:
            # A node with no message is structural (e.g. the synthetic root); not an error.
            continue

        body = _extract_body(message, conv_id, node_id, errors)
        if not body:
            continue

        provider_message_id = message.get("id")
        if not isinstance(provider_message_id, str) or not provider_message_id:
            provider_message_id = node_id

        messages.append(
            Message(
                provider_message_id=provider_message_id,
                role=_extract_role(message, conv_id, node_id, errors),
                created_at=_to_utc(
                    message.get("create_time"), conv_id, node_id, "create_time", errors
                ),
                body=body,
                seq=len(messages),
            )
        )
    return messages


def _extract_role(
    message: dict[str, Any], conv_id: str, node_id: str, errors: _ErrorSink
) -> str | None:
    author = message.get("author")
    if not isinstance(author, dict):
        if author is not None:
            errors.add(
                "invalid_author",
                record_id=conv_id,
                node_id=node_id,
                detail=f"expected an object, got {type(author).__name__}",
            )
        return None

    role = author.get("role")
    if role is None:
        return None
    if not isinstance(role, str):
        errors.add(
            "invalid_role",
            record_id=conv_id,
            node_id=node_id,
            detail=f"expected a string, got {type(role).__name__}",
        )
        return None
    return role


def _extract_body(
    message: dict[str, Any], conv_id: str, node_id: str, errors: _ErrorSink
) -> str | None:
    content = message.get("content")
    if not isinstance(content, dict):
        errors.add(
            "invalid_content",
            record_id=conv_id,
            node_id=node_id,
            detail=f"expected an object, got {type(content).__name__}",
        )
        return None

    content_type = content.get("content_type")
    if content_type in _SILENT_METADATA_CONTENT_TYPES:
        return None

    parts = content.get("parts")
    if not isinstance(parts, list):
        errors.add(
            "unsupported_content_type",
            record_id=conv_id,
            node_id=node_id,
            detail=f"content_type={content_type!r} has no 'parts' list",
        )
        return None

    text_parts: list[str] = []
    for position, part in enumerate(parts):
        if isinstance(part, str):
            text_parts.append(part)
            continue
        errors.add(
            "non_text_content_part",
            record_id=conv_id,
            node_id=node_id,
            detail=f"parts[{position}] is {type(part).__name__}; skipped",
        )

    body = "\n\n".join(text_parts).strip()
    return body or None


def _to_utc(
    value: object,
    conv_id: str | None,
    node_id: str | None,
    field: str,
    errors: _ErrorSink,
) -> datetime | None:
    """Convert a Unix-seconds timestamp to an aware UTC datetime, or ``None``."""
    if value is None:
        return None
    # bool is an int subclass but is never a valid timestamp.
    if isinstance(value, bool) or not isinstance(value, int | float):
        errors.add(
            "invalid_timestamp",
            record_id=conv_id,
            node_id=node_id,
            detail=f"{field}: expected a number, got {type(value).__name__}",
        )
        return None
    try:
        return datetime.fromtimestamp(value, UTC)
    except (OverflowError, OSError, ValueError) as exc:
        errors.add(
            "invalid_timestamp",
            record_id=conv_id,
            node_id=node_id,
            detail=f"{field}: {value!r} is out of range ({exc})",
        )
        return None
