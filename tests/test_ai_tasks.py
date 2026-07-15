from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from chat_chronicle.ai import CompletionResponse, run_task
from chat_chronicle.ai_config import (
    AIConfigError,
    ModelProfile,
    TaskDefinition,
    is_remote_profile,
    load_model_catalog,
    load_task_catalog,
)
from chat_chronicle.db import CURRENT_SCHEMA_VERSION, connect, upsert_conversation
from chat_chronicle.models import Conversation, Message


def _task() -> TaskDefinition:
    return TaskDefinition.model_validate(
        {
            "version": "1",
            "model_profile": "local",
            "input_selector": "full-conversation",
            "output_schema": "example-result-v1",
            "system_prompt": "Return JSON.",
            "user_prompt": "{transcript}",
            "generation": {"temperature": 0, "max_tokens": 30},
        }
    )


def _conversation() -> Conversation:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return Conversation(
        provider="synthetic",
        provider_conv_id="one",
        title="Synthetic",
        created_at=now,
        updated_at=now,
        messages=[Message(role="user", body="Synthetic input only", seq=0, created_at=now)],
    )


class FakeClient:
    def __init__(self, content: str = '{"result":"ok"}') -> None:
        self.content = content
        self.calls = 0

    async def complete(self, request):
        self.calls += 1
        return CompletionResponse(self.content, "mock", request.model, {"total_tokens": 2})


def test_valid_catalogs_and_remote_classification(tmp_path: Path) -> None:
    task_path = tmp_path / "tasks.yaml"
    task_path.write_text(
        yaml.safe_dump({"version": 1, "tasks": {"demo": _task().model_dump()}}), encoding="utf-8"
    )
    model_path = tmp_path / "models.yaml"
    model_path.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "profiles": {"local": {"model": "mock", "api_base": "http://127.0.0.1:1/v1"}},
            }
        ),
        encoding="utf-8",
    )
    assert "demo" in load_task_catalog(task_path).tasks
    profile = load_model_catalog(model_path).profiles["local"]
    assert not is_remote_profile(profile)
    assert is_remote_profile(profile.model_copy(update={"api_base": "https://example.invalid/v1"}))


def test_unknown_placeholder_and_dependency_cycle_fail(tmp_path: Path) -> None:
    path = tmp_path / "tasks.yaml"
    value = _task().model_dump()
    value["user_prompt"] = "{unknown}"
    path.write_text(yaml.safe_dump({"version": 1, "tasks": {"bad": value}}), encoding="utf-8")
    with pytest.raises(AIConfigError, match="unknown prompt"):
        load_task_catalog(path)
    value["user_prompt"] = "{transcript}"
    value["depends_on"] = ["bad"]
    path.write_text(yaml.safe_dump({"version": 1, "tasks": {"bad": value}}), encoding="utf-8")
    with pytest.raises(AIConfigError, match="cycle"):
        load_task_catalog(path)


def test_success_cache_force_and_schema_failure(tmp_path: Path) -> None:
    db = tmp_path / "chronicle.db"
    with connect(db) as conn:
        conversation_id = upsert_conversation(conn, None, _conversation()).conversation_id
        profile = ModelProfile(model="mock", api_base="http://localhost:1/v1")
        client = FakeClient()
        first = asyncio.run(
            run_task(
                conn,
                task_name="demo",
                task=_task(),
                profile_name="local",
                profile=profile,
                conversation_ids=[conversation_id],
                client=client,
            )
        )
        second = asyncio.run(
            run_task(
                conn,
                task_name="demo",
                task=_task(),
                profile_name="local",
                profile=profile,
                conversation_ids=[conversation_id],
                client=client,
            )
        )
        forced = asyncio.run(
            run_task(
                conn,
                task_name="demo",
                task=_task(),
                profile_name="local",
                profile=profile,
                conversation_ids=[conversation_id],
                client=client,
                force=True,
            )
        )
        assert [first[0]["status"], second[0]["status"], forced[0]["status"]] == [
            "completed",
            "cached",
            "completed",
        ]
        assert client.calls == 2
        bad = FakeClient('{"wrong":"shape"}')
        failed = asyncio.run(
            run_task(
                conn,
                task_name="changed",
                task=_task().model_copy(update={"version": "2"}),
                profile_name="local",
                profile=profile,
                conversation_ids=[conversation_id],
                client=bad,
            )
        )
        assert failed[0]["status"] == "failed"
        rows = conn.execute(
            "SELECT status, result_json, error FROM ai_task_results ORDER BY id"
        ).fetchall()
        assert [row["status"] for row in rows] == ["success", "success", "failed"]
        assert "Synthetic input only" not in json.dumps([dict(row) for row in rows])


def test_fresh_database_is_v3(tmp_path: Path) -> None:
    with connect(tmp_path / "fresh.db") as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_SCHEMA_VERSION == 3
        assert conn.execute("SELECT count(*) FROM ai_task_results").fetchone()[0] == 0
