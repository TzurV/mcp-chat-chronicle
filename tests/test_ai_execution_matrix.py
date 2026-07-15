from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path

import pytest

from chat_chronicle.ai import CompletionResponse, LLMError, run_task
from chat_chronicle.ai_config import ModelProfile, TaskDefinition
from chat_chronicle.db import connect, upsert_conversation
from chat_chronicle.models import Conversation, Message


def _task() -> TaskDefinition:
    return TaskDefinition.model_validate(
        {
            "version": "1",
            "model_profile": "local",
            "input_selector": "full-conversation",
            "output_schema": "example-result-v1",
            "system_prompt": "Return JSON",
            "user_prompt": "{transcript}",
        }
    )


def _seed(conn, identity: str) -> int:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return upsert_conversation(
        conn,
        None,
        Conversation(
            provider="synthetic",
            provider_conv_id=identity,
            created_at=now,
            updated_at=now,
            messages=[Message(role="user", body=f"synthetic-{identity}", seq=0)],
        ),
    ).conversation_id


class IsolatingClient:
    async def complete(self, request):
        if "bad" in request.messages[1]["content"]:
            raise LLMError("connection", "Local model service is unavailable.")
        return CompletionResponse('{"result":"ok"}', "mock-provider", "mock-model")


def test_batch_continues_after_failure_and_missing_selection_has_no_traceback(
    tmp_path: Path,
) -> None:
    with connect(tmp_path / "batch.db") as conn:
        good = _seed(conn, "good")
        bad = _seed(conn, "bad")
        results = asyncio.run(
            run_task(
                conn,
                task_name="demo",
                task=_task(),
                profile_name="local",
                profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
                conversation_ids=[bad, 999999, good],
                client=IsolatingClient(),
            )
        )
        assert [item["status"] for item in results] == ["failed", "failed", "completed"]
        assert results[1]["error"] == "selection"
        assert "does not exist" in results[1]["detail"]


def test_bounded_concurrency_is_respected(tmp_path: Path) -> None:
    class TrackingClient:
        active = 0
        maximum = 0

        async def complete(self, request):
            self.active += 1
            self.maximum = max(self.maximum, self.active)
            await asyncio.sleep(0.01)
            self.active -= 1
            return CompletionResponse('{"result":"ok"}', "mock", "mock")

    with connect(tmp_path / "concurrency.db") as conn:
        ids = [_seed(conn, str(index)) for index in range(5)]
        client = TrackingClient()
        asyncio.run(
            run_task(
                conn,
                task_name="demo",
                task=_task(),
                profile_name="local",
                profile=ModelProfile(model="mock", api_base="http://localhost/v1", concurrency=2),
                conversation_ids=ids,
                client=client,
            )
        )
        assert client.maximum == 2


def test_interruption_preserves_committed_results_and_rerun_resumes(tmp_path: Path) -> None:
    class InterruptingClient:
        calls = 0

        async def complete(self, request):
            self.calls += 1
            if self.calls == 2:
                raise asyncio.CancelledError
            return CompletionResponse('{"result":"ok"}', "mock", "mock")

    class SuccessClient:
        async def complete(self, request):
            return CompletionResponse('{"result":"ok"}', "mock", "mock")

    with connect(tmp_path / "interrupt.db") as conn:
        ids = [_seed(conn, "first"), _seed(conn, "second")]
        arguments = dict(
            conn=conn,
            task_name="demo",
            task=_task(),
            profile_name="local",
            profile=ModelProfile(model="mock", api_base="http://localhost/v1", concurrency=1),
            conversation_ids=ids,
        )
        with pytest.raises(asyncio.CancelledError):
            asyncio.run(run_task(**arguments, client=InterruptingClient()))
        assert conn.execute("SELECT count(*) FROM ai_task_results").fetchone()[0] == 1
        resumed = asyncio.run(run_task(**arguments, client=SuccessClient()))
        assert [item["status"] for item in resumed] == ["cached", "completed"]


def test_schema_failure_preserves_provider_model_usage_and_real_timestamps(
    tmp_path: Path,
) -> None:
    class SchemaFailingClient:
        async def complete(self, request):
            await asyncio.sleep(0.001)
            return CompletionResponse(
                '{"wrong":"shape"}', "mock-provider", "mock-model", {"total_tokens": 3}
            )

    with connect(tmp_path / "provenance.db") as conn:
        conversation_id = _seed(conn, "schema")
        result = asyncio.run(
            run_task(
                conn,
                task_name="demo",
                task=_task(),
                profile_name="local",
                profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
                conversation_ids=[conversation_id],
                client=SchemaFailingClient(),
            )
        )[0]
        assert result["status"] == "failed"
        assert result["actual_provider"] == "mock-provider"
        row = conn.execute("SELECT * FROM ai_task_results").fetchone()
        assert row["actual_provider"] == "mock-provider"
        assert row["actual_model"] == "mock-model"
        assert row["usage_json"] == '{"total_tokens":3}'
        assert row["started_at"] < row["completed_at"]
        assert "synthetic-schema" not in row["error"]


@pytest.mark.parametrize(
    "kind", ["dependency", "timeout", "connection", "authentication", "rate_limit"]
)
def test_normalized_failure_detail_is_persisted_without_input(tmp_path: Path, kind: str) -> None:
    class FailingClient:
        async def complete(self, request):
            detail = (
                "AI support is not installed; run `poetry install -E enrich`."
                if kind == "dependency"
                else f"Safe {kind} failure."
            )
            raise LLMError(kind, detail)

    with connect(tmp_path / f"{kind}.db") as conn:
        conversation_id = _seed(conn, kind)
        result = asyncio.run(
            run_task(
                conn,
                task_name="demo",
                task=_task(),
                profile_name="local",
                profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
                conversation_ids=[conversation_id],
                client=FailingClient(),
            )
        )[0]
        assert result["error"] == kind
        if kind == "dependency":
            assert "poetry install -E enrich" in result["detail"]
        stored = conn.execute("SELECT error FROM ai_task_results").fetchone()[0]
        assert f"synthetic-{kind}" not in stored


def test_failure_sanitizer_redacts_credential_and_full_selected_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SYNTHETIC_SECRET", "key-private-value")

    class UnsafeClient:
        async def complete(self, request):
            raise LLMError(
                "provider",
                f"unsafe {request.api_key} synthetic-redaction provider payload",
            )

    with connect(tmp_path / "redaction.db") as conn:
        conversation_id = _seed(conn, "redaction")
        asyncio.run(
            run_task(
                conn,
                task_name="demo",
                task=_task(),
                profile_name="local",
                profile=ModelProfile(
                    model="mock",
                    api_base="http://localhost/v1",
                    api_key_env="SYNTHETIC_SECRET",
                ),
                conversation_ids=[conversation_id],
                client=UnsafeClient(),
            )
        )
        stored = conn.execute("SELECT error FROM ai_task_results").fetchone()[0]
        assert "key-private-value" not in stored
        assert "synthetic-redaction" not in stored
        assert "[REDACTED]" in stored


def test_configured_context_preflight_fails_before_call_and_remains_retryable(
    tmp_path: Path,
) -> None:
    class UnexpectedClient:
        calls = 0

        async def complete(self, request):
            self.calls += 1
            raise AssertionError("context preflight must run before the provider call")

    client = UnexpectedClient()
    with connect(tmp_path / "context.db") as conn:
        conversation_id = _seed(conn, "context")
        arguments = dict(
            conn=conn,
            task_name="demo",
            task=_task(),
            profile_name="local",
            profile=ModelProfile(
                model="mock",
                api_base="http://localhost/v1",
                context_window=32,
            ),
            conversation_ids=[conversation_id],
            client=client,
        )
        first = asyncio.run(run_task(**arguments))[0]
        second = asyncio.run(run_task(**arguments))[0]
        assert first["error"] == second["error"] == "context_length"
        assert client.calls == 0
        rows = conn.execute(
            "SELECT status, error FROM ai_task_results ORDER BY id"
        ).fetchall()
        assert len(rows) == 2
        assert all(row["status"] == "failed" for row in rows)
        assert all("context_length" in row["error"] for row in rows)
