from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path

import pytest

import chat_chronicle.ai as ai_module
from chat_chronicle.ai import CompletionResponse, lookup_cache, prepare_attempt, run_task
from chat_chronicle.ai_config import ModelProfile, TaskDefinition
from chat_chronicle.db import connect, upsert_conversation
from chat_chronicle.models import Conversation, Message


def _task(**updates) -> TaskDefinition:
    base = TaskDefinition.model_validate(
        {
            "version": "1",
            "model_profile": "local",
            "input_selector": "full-conversation",
            "output_schema": "example-result-v1",
            "system_prompt": "Title={title}; start={start_date}; last={last_active_date}",
            "user_prompt": "{transcript}",
            "generation": {"temperature": 0, "max_tokens": 30},
        }
    )
    return base.model_copy(update=updates)


def _seed(conn) -> int:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    conversation = Conversation(
        provider="synthetic",
        provider_conv_id="cache-one",
        title="Original title",
        created_at=start,
        updated_at=start,
        messages=[
            Message(role="user", body="first", seq=0, created_at=start),
            Message(role="assistant", body="second", seq=1, created_at=start),
        ],
    )
    return upsert_conversation(conn, None, conversation).conversation_id


class Client:
    calls = 0

    async def complete(self, request):
        self.calls += 1
        return CompletionResponse('{"result":"ok"}', "mock-provider", request.model)


def _execute(conn, conversation_id: int, task=None, profile=None, profile_name="local"):
    return asyncio.run(
        run_task(
            conn,
            task_name="demo",
            task=task or _task(),
            profile_name=profile_name,
            profile=profile or ModelProfile(model="mock", api_base="http://localhost/v1"),
            conversation_ids=[conversation_id],
            client=Client(),
        )
    )[0]


@pytest.mark.parametrize(
    "mutation",
    [
        "body",
        "role",
        "order",
        "title",
        "start_date",
        "last_active",
        "selected_messages",
    ],
)
def test_conversation_and_prompt_metadata_changes_invalidate_cache(
    tmp_path: Path, mutation: str
) -> None:
    with connect(tmp_path / f"{mutation}.db") as conn:
        conversation_id = _seed(conn)
        assert _execute(conn, conversation_id)["status"] == "completed"
        if mutation == "body":
            conn.execute(
                "UPDATE messages SET body = 'changed' WHERE conversation_id = ? AND seq = 0",
                (conversation_id,),
            )
        elif mutation == "role":
            conn.execute(
                "UPDATE messages SET role = 'assistant' WHERE conversation_id = ? AND seq = 0",
                (conversation_id,),
            )
        elif mutation == "order":
            conn.execute(
                "UPDATE messages SET seq = 9 - seq WHERE conversation_id = ?", (conversation_id,)
            )
        elif mutation == "title":
            conn.execute(
                "UPDATE conversations SET title = 'Changed title' WHERE id = ?", (conversation_id,)
            )
        elif mutation == "start_date":
            conn.execute(
                "UPDATE conversations SET created_at = '2026-02-01T00:00:00Z' WHERE id = ?",
                (conversation_id,),
            )
        elif mutation == "last_active":
            conn.execute(
                "UPDATE conversations SET updated_at = '2026-02-02T00:00:00Z' WHERE id = ?",
                (conversation_id,),
            )
        else:
            conn.execute(
                "DELETE FROM messages WHERE conversation_id = ? AND seq = 0", (conversation_id,)
            )
        conn.commit()
        assert _execute(conn, conversation_id)["status"] == "completed"


@pytest.mark.parametrize(
    ("task_update", "profile", "profile_name"),
    [
        ({"system_prompt": "Changed prompt"}, None, "local"),
        ({"generation": _task().generation.model_copy(update={"temperature": 1})}, None, "local"),
        ({"version": "2"}, None, "local"),
        ({"max_input_chars": 5}, None, "local"),
        ({"input_selector": "recent-messages", "recent_message_count": 1}, None, "local"),
        ({}, ModelProfile(model="different", api_base="http://localhost/v1"), "local"),
        ({}, None, "different-alias"),
    ],
)
def test_task_selector_generation_model_and_alias_changes_invalidate_cache(
    tmp_path: Path, task_update: dict, profile: ModelProfile | None, profile_name: str
) -> None:
    with connect(tmp_path / "identity.db") as conn:
        conversation_id = _seed(conn)
        assert _execute(conn, conversation_id)["status"] == "completed"
        changed = _task().model_copy(update=task_update)
        assert (
            _execute(conn, conversation_id, changed, profile, profile_name)["status"] == "completed"
        )


def test_task_name_and_schema_name_version_invalidate_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with connect(tmp_path / "schema.db") as conn:
        conversation_id = _seed(conn)
        task = _task()
        assert _execute(conn, conversation_id, task)["status"] == "completed"
        prepared = prepare_attempt(
            conn,
            task=task,
            profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
            conversation_id=conversation_id,
        )
        assert (
            lookup_cache(
                conn, task_name="other", task=task, profile_name="local", prepared=prepared
            )
            is None
        )
        schema = ai_module.OUTPUT_SCHEMAS["example-result-v1"][1]
        monkeypatch.setitem(ai_module.OUTPUT_SCHEMAS, "example-result-v1", ("2", schema))
        changed_version = prepare_attempt(
            conn,
            task=task,
            profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
            conversation_id=conversation_id,
        )
        assert (
            lookup_cache(
                conn, task_name="demo", task=task, profile_name="local", prepared=changed_version
            )
            is None
        )
        monkeypatch.setitem(ai_module.OUTPUT_SCHEMAS, "example-result-v2", ("1", schema))
        changed_name_task = task.model_copy(update={"output_schema": "example-result-v2"})
        changed_name = prepare_attempt(
            conn,
            task=changed_name_task,
            profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
            conversation_id=conversation_id,
        )
        assert (
            lookup_cache(
                conn,
                task_name="demo",
                task=changed_name_task,
                profile_name="local",
                prepared=changed_name,
            )
            is None
        )


def test_credential_value_is_excluded_from_cache_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profile = ModelProfile(
        model="mock", api_base="http://localhost/v1", api_key_env="SYNTHETIC_AI_KEY"
    )
    with connect(tmp_path / "credential.db") as conn:
        conversation_id = _seed(conn)
        monkeypatch.setenv("SYNTHETIC_AI_KEY", "first-secret")
        first = prepare_attempt(
            conn, task=_task(), profile=profile, conversation_id=conversation_id
        )
        monkeypatch.setenv("SYNTHETIC_AI_KEY", "second-secret")
        second = prepare_attempt(
            conn, task=_task(), profile=profile, conversation_id=conversation_id
        )
        assert first.model_hash == second.model_hash
        assert "first-secret" not in first.model_hash
        assert "second-secret" not in second.model_hash


def test_failed_attempt_is_retryable_and_force_is_append_only(tmp_path: Path) -> None:
    class InvalidClient:
        async def complete(self, request):
            return CompletionResponse("not-json", "mock", "mock")

    with connect(tmp_path / "attempts.db") as conn:
        conversation_id = _seed(conn)
        args = dict(
            conn=conn,
            task_name="demo",
            task=_task(),
            profile_name="local",
            profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
            conversation_ids=[conversation_id],
        )
        assert asyncio.run(run_task(**args, client=InvalidClient()))[0]["status"] == "failed"
        assert asyncio.run(run_task(**args, client=Client()))[0]["status"] == "completed"
        assert (
            asyncio.run(run_task(**args, client=Client(), force=True))[0]["status"] == "completed"
        )
        statuses = [
            row[0] for row in conn.execute("SELECT status FROM ai_task_results ORDER BY id")
        ]
        assert statuses == ["failed", "success", "success"]
