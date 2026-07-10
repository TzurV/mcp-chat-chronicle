"""Normalized models for Chat Chronicle ingestion and persistence."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


def _utc_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _datetime_for_hash(value: datetime | None) -> str | None:
    if value is None:
        return None
    utc_value = _utc_datetime(value)
    if utc_value is None:
        return None
    return utc_value.isoformat(timespec="microseconds").replace("+00:00", "Z")


class ChronicleModel(BaseModel):
    """Base model with strict-ish defaults suitable for local persistence."""

    model_config = ConfigDict(extra="forbid")


class Message(ChronicleModel):
    provider_message_id: str | None = None
    role: str | None = None
    created_at: datetime | None = None
    body: str
    seq: int

    @field_validator("created_at")
    @classmethod
    def _normalize_created_at(cls, value: datetime | None) -> datetime | None:
        return _utc_datetime(value)


class Conversation(ChronicleModel):
    provider: str
    provider_conv_id: str
    title: str | None = None
    url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    messages: list[Message]

    @field_validator("created_at", "updated_at")
    @classmethod
    def _normalize_timestamps(cls, value: datetime | None) -> datetime | None:
        return _utc_datetime(value)

    def content_hash_value(self) -> str:
        """Return a stable hash for the normalized message sequence."""
        normalized_messages = [
            {
                "provider_message_id": message.provider_message_id,
                "role": message.role,
                "created_at": _datetime_for_hash(message.created_at),
                "body": message.body,
                "seq": message.seq,
            }
            for message in sorted(self.messages, key=lambda item: item.seq)
        ]
        payload = json.dumps(
            normalized_messages,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def content_hash(self) -> str:
        return self.content_hash_value()


class Enrichment(ChronicleModel):
    conversation_id: int
    summary: str | None = None
    tags_json: str | None = None
    language: str | None = None
    model_used: str | None = None
    enriched_at: datetime | None = None

    @field_validator("enriched_at")
    @classmethod
    def _normalize_enriched_at(cls, value: datetime | None) -> datetime | None:
        return _utc_datetime(value)


class KnowledgeItem(ChronicleModel):
    id: int | None = None
    conversation_id: int | None = None
    kind: Literal["decision", "solution", "open_question"]
    statement: str
    context: str | None = None
    tags_json: str | None = None
    model_used: str | None = None
    extracted_at: datetime | None = None

    @field_validator("extracted_at")
    @classmethod
    def _normalize_extracted_at(cls, value: datetime | None) -> datetime | None:
        return _utc_datetime(value)


class UpsertResult(ChronicleModel):
    conversation_id: int
    status: Literal["added", "updated", "skipped"]


class IngestRunSummary(ChronicleModel):
    conversations_seen: int = 0
    added: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[dict[str, Any]] = Field(default_factory=list)
