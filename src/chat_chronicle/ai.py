"""Application-owned AI task runner and lazy LiteLLM adapter."""

from __future__ import annotations

import asyncio
import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, ValidationError

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


OUTPUT_SCHEMAS: dict[str, tuple[str, type[BaseModel]]] = {"example-result-v1": ("1", ExampleResult)}


class LLMError(RuntimeError):
    def __init__(self, kind: str, message: str):
        self.kind = kind
        super().__init__(message)


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
            return CompletionResponse(
                content=content,
                provider=str(getattr(response, "provider", "unknown")),
                model=str(getattr(response, "model", request.model)),
                usage=usage,
            )
        except LLMError:
            raise
        except Exception as exc:
            name = type(exc).__name__.lower()
            aliases = {
                "timeout": "timeout",
                "authentication": "authentication",
                "permission": "authentication",
                "ratelimit": "rate_limit",
                "rate_limit": "rate_limit",
                "connection": "connection",
            }
            kind = next((value for key, value in aliases.items() if key in name), "provider")
            raise LLMError(kind, f"{kind.replace('_', ' ')} error from model provider.") from exc


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
    if task.input_selector in {"recent-messages", "metadata-recent"}:
        rows = rows[-task.recent_message_count :]
    rendered = [f"{row['role'] or 'unknown'}: {row['body']}" for row in rows]
    full_text = "\n\n".join(rendered)
    truncated = len(full_text) > task.max_input_chars
    text = full_text[-task.max_input_chars :] if truncated else full_text
    dates = [row["created_at"] for row in rows if row["created_at"]]
    start = conversation["created_at"] or (dates[0] if dates else "")
    last = conversation["updated_at"] or (dates[-1] if dates else "")
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
    schema_version, schema = OUTPUT_SCHEMAS[task.output_schema]
    effective_generation = resolve_generation(task, profile)
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
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_schema=schema.model_json_schema(),
            enforce_schema=profile.structured_output,
            temperature=effective_generation.temperature,
            max_tokens=effective_generation.max_tokens,
            timeout=profile.timeout,
            retries=profile.retries,
            api_base=profile.api_base,
            api_key=resolved.get("api_key"),
        ),
        input_hash=canonical_hash(input_payload),
        prompt_hash=canonical_hash({"system": system, "user": user}),
        task_hash=canonical_hash(task.model_dump(mode="json")),
        model_hash=canonical_hash(model_for_hash),
        schema_name=task.output_schema,
        schema_version=schema_version,
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
            }
        )
    return results


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _sanitize_error(message: str, prepared: PreparedAttempt) -> str:
    safe = message
    transcript_fragments = [
        line.split(": ", 1)[1] for line in prepared.selected.text.splitlines() if ": " in line
    ]
    for secret in (prepared.request.api_key, prepared.selected.text, *transcript_fragments):
        if secret:
            safe = safe.replace(secret, "[REDACTED]")
    return safe[:500]


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
            async with semaphore:
                response = await client.complete(prepared.request)
            try:
                parsed = json.loads(response.content)
            except json.JSONDecodeError as exc:
                raise LLMError("invalid_json", "Provider returned invalid JSON.") from exc
            _, schema = OUTPUT_SCHEMAS[prepared.schema_name]
            validated = schema.model_validate(parsed).model_dump(mode="json")
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
                else "Response failed output validation."
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
