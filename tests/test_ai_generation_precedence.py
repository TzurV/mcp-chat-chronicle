from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from chat_chronicle.ai import CompletionResponse, prepare_attempt, run_task
from chat_chronicle.ai_config import GenerationConfig, ModelProfile, TaskDefinition
from chat_chronicle.db import connect, upsert_conversation
from chat_chronicle.models import Conversation, Message


def _task(generation: dict | None = None) -> TaskDefinition:
    payload = {
        "version": "1",
        "model_profile": "local",
        "input_selector": "full-conversation",
        "output_schema": "example-result-v1",
        "system_prompt": "Return JSON.",
        "user_prompt": "{transcript}",
    }
    if generation is not None:
        payload["generation"] = generation
    return TaskDefinition.model_validate(payload)


def _profile(*, temperature: float = 0.25, max_tokens: int = 700) -> ModelProfile:
    return ModelProfile(
        model="mock",
        api_base="http://localhost/v1",
        generation=GenerationConfig(temperature=temperature, max_tokens=max_tokens),
    )


def _seed(conn) -> int:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return upsert_conversation(
        conn,
        None,
        Conversation(
            provider="synthetic",
            provider_conv_id="generation",
            created_at=now,
            updated_at=now,
            messages=[Message(role="user", body="synthetic generation input", seq=0)],
        ),
    ).conversation_id


@pytest.mark.parametrize(
    ("task_generation", "expected_temperature", "expected_max_tokens"),
    [
        (None, 0.25, 700),
        ({"temperature": 0.8}, 0.8, 700),
        ({"max_tokens": 1234}, 0.25, 1234),
        ({"temperature": 1.1, "max_tokens": 2222}, 1.1, 2222),
    ],
)
def test_effective_generation_profile_defaults_and_partial_task_overrides(
    tmp_path: Path,
    task_generation: dict | None,
    expected_temperature: float,
    expected_max_tokens: int,
) -> None:
    with connect(tmp_path / "request.db") as conn:
        conversation_id = _seed(conn)
        prepared = prepare_attempt(
            conn,
            task=_task(task_generation),
            profile=_profile(),
            conversation_id=conversation_id,
        )
        assert prepared.request.temperature == expected_temperature
        assert prepared.request.max_tokens == expected_max_tokens


def test_effective_profile_default_change_updates_request_and_invalidates_cache(
    tmp_path: Path,
) -> None:
    class Client:
        calls = 0

        async def complete(self, request):
            self.calls += 1
            return CompletionResponse('{"result":"ok"}', "mock", "mock")

    with connect(tmp_path / "effective-change.db") as conn:
        conversation_id = _seed(conn)
        client = Client()
        common = dict(
            conn=conn,
            task_name="demo",
            task=_task(),
            profile_name="local",
            conversation_ids=[conversation_id],
            client=client,
        )
        first = asyncio.run(run_task(**common, profile=_profile(temperature=0.2)))[0]
        second = asyncio.run(run_task(**common, profile=_profile(temperature=0.9)))[0]
        assert first["status"] == second["status"] == "completed"
        assert client.calls == 2
        first_request = prepare_attempt(
            conn,
            task=_task(),
            profile=_profile(temperature=0.2),
            conversation_id=conversation_id,
        ).request
        second_request = prepare_attempt(
            conn,
            task=_task(),
            profile=_profile(temperature=0.9),
            conversation_id=conversation_id,
        ).request
        assert first_request.temperature == 0.2
        assert second_request.temperature == 0.9


def test_overridden_profile_default_change_keeps_request_and_cache_identity(
    tmp_path: Path,
) -> None:
    class Client:
        calls = 0

        async def complete(self, request):
            self.calls += 1
            return CompletionResponse('{"result":"ok"}', "mock", "mock")

    task = _task({"temperature": 1.0, "max_tokens": 900})
    with connect(tmp_path / "non-effective-change.db") as conn:
        conversation_id = _seed(conn)
        first = prepare_attempt(
            conn,
            task=task,
            profile=_profile(temperature=0.1, max_tokens=100),
            conversation_id=conversation_id,
        )
        second = prepare_attempt(
            conn,
            task=task,
            profile=_profile(temperature=0.7, max_tokens=800),
            conversation_id=conversation_id,
        )
        assert first.request.temperature == second.request.temperature == 1.0
        assert first.request.max_tokens == second.request.max_tokens == 900
        assert first.model_hash == second.model_hash
        client = Client()
        common = dict(
            conn=conn,
            task_name="demo",
            task=task,
            profile_name="local",
            conversation_ids=[conversation_id],
            client=client,
        )
        executed = asyncio.run(
            run_task(**common, profile=_profile(temperature=0.1, max_tokens=100))
        )[0]
        cached = asyncio.run(run_task(**common, profile=_profile(temperature=0.7, max_tokens=800)))[
            0
        ]
        assert executed["status"] == "completed"
        assert cached["status"] == "cached"
        assert client.calls == 1


@pytest.mark.parametrize(
    "generation",
    [
        {"temperature": -0.1},
        {"temperature": 2.1},
        {"max_tokens": 0},
        {"max_tokens": 100_001},
    ],
)
def test_invalid_task_generation_override_fails_validation(generation: dict) -> None:
    with pytest.raises(ValidationError):
        _task(generation)


def test_invalid_profile_generation_default_fails_validation() -> None:
    with pytest.raises(ValidationError):
        ModelProfile.model_validate(
            {
                "model": "mock",
                "api_base": "http://localhost/v1",
                "generation": {"temperature": 3, "max_tokens": 0},
            }
        )
