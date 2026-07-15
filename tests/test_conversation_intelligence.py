from __future__ import annotations

import asyncio
import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from importlib.resources import files
from pathlib import Path

import pytest
from pydantic import ValidationError

import chat_chronicle.ai as ai_module
from chat_chronicle.ai import (
    CompletionResponse,
    ConversationSummaryProviderResult,
    LastActivityResult,
    TitleAssessmentResult,
    WorkModeClassificationResult,
    run_task,
    select_input,
)
from chat_chronicle.ai_config import ModelProfile, TaskDefinition, load_task_catalog
from chat_chronicle.db import connect, upsert_conversation
from chat_chronicle.models import Conversation, Message


def _task(selector: str, schema: str, **changes) -> TaskDefinition:
    data = {
        "version": "1",
        "model_profile": "service-local",
        "input_selector": selector,
        "output_schema": schema,
        "system_prompt": "Return JSON without chain-of-thought.",
        "user_prompt": "Title: {title}\n{transcript}",
        "max_input_chars": 50_000,
        "recent_message_count": 12,
    }
    data.update(changes)
    return TaskDefinition.model_validate(data)


def _seed(conn, identity: str, messages: list[Message], *, title: str = "Synthetic title") -> int:
    start = datetime(2026, 2, 1, 9, tzinfo=UTC)
    return upsert_conversation(
        conn,
        None,
        Conversation(
            provider="synthetic",
            provider_conv_id=identity,
            title=title,
            created_at=start,
            updated_at=start + timedelta(days=2),
            messages=messages,
        ),
    ).conversation_id


def _message(role: str | None, body: str, seq: int) -> Message:
    return Message(
        role=role,
        body=body,
        seq=seq,
        created_at=datetime(2026, 2, 1, 9, tzinfo=UTC) + timedelta(minutes=seq),
    )


def _production_catalog():
    path = Path(__file__).resolve().parents[1] / "ai-tasks.default.yaml"
    return load_task_catalog(path)


def test_production_catalog_and_packaged_template_are_exact() -> None:
    root = Path(__file__).resolve().parents[1] / "ai-tasks.default.yaml"
    packaged = files("chat_chronicle.resources").joinpath("ai-tasks.default.yaml")
    assert root.read_bytes() == packaged.read_bytes()
    catalog = load_task_catalog(root)
    assert set(catalog.tasks) == {
        "conversation-summary",
        "work-mode-classification",
        "last-activity",
        "title-assessment",
    }
    assert all(task.enabled and task.version == "1" for task in catalog.tasks.values())
    assert all(task.model_profile == "service-local" for task in catalog.tasks.values())
    assert all(task.depends_on == [] for task in catalog.tasks.values())
    assert catalog.tasks["last-activity"].recent_message_count == 12


def test_meaningful_filtering_preserves_provider_roles_and_renders_ids(tmp_path: Path) -> None:
    messages = [
        _message("system", "excluded system", 0),
        _message("developer", "excluded developer", 1),
        _message("user", "ChatGPT or Codex user", 2),
        _message("human", "Claude human", 3),
        _message("assistant", "Assistant response", 4),
        _message("tool", "excluded tool result", 5),
        _message("function", "excluded function result", 6),
        _message("reasoning", "excluded reasoning", 7),
        _message("metadata", "excluded importer metadata", 8),
        _message("assistant", "   ", 9),
    ]
    with connect(tmp_path / "roles.db") as conn:
        conversation_id = _seed(conn, "roles", messages)
        selected = select_input(
            conn,
            conversation_id,
            _task("conversation-overview-v1", "conversation-summary-v1"),
        )
        assert "ChatGPT or Codex user" in selected.text
        assert "Claude human" in selected.text
        assert "Assistant response" in selected.text
        assert "excluded" not in selected.text
        assert "message_id=" in selected.text
        assert selected.metadata["meaningful_message_count"] == 3
        assert selected.metadata["message_ids"] == selected.metadata["selected_message_ids"]


def test_overview_is_complete_or_deterministically_samples_beginning_middle_end(
    tmp_path: Path,
) -> None:
    messages = [
        _message("user" if i % 2 == 0 else "assistant", f"marker-{i}-" + "x" * 90, i)
        for i in range(20)
    ]
    with connect(tmp_path / "overview.db") as conn:
        conversation_id = _seed(conn, "overview", messages)
        full = select_input(
            conn,
            conversation_id,
            _task(
                "conversation-overview-v1",
                "conversation-summary-v1",
                max_input_chars=50_000,
            ),
        )
        assert full.metadata["sampling_strategy"] == "complete"
        assert full.metadata["omitted_count"] == 0

        bounded_task = _task(
            "conversation-overview-v1",
            "conversation-summary-v1",
            max_input_chars=900,
        )
        first = select_input(conn, conversation_id, bounded_task)
        second = select_input(conn, conversation_id, bounded_task)
        assert first == second
        assert len(first.text) <= 900
        assert "marker-0-" in first.text
        assert "marker-19-" in first.text
        assert first.metadata["sampling_strategy"] == "beginning-25-middle-25-end-50"
        assert first.metadata["omitted_count"] > 0
        assert first.metadata["seq_start"] == 0
        assert first.metadata["seq_end"] == 19
        assert first.metadata["selected_chars"] == len(first.text)


def test_overview_records_message_truncation_and_empty_selection(tmp_path: Path) -> None:
    with connect(tmp_path / "truncate.db") as conn:
        long_id = _seed(conn, "long", [_message("user", "z" * 2_000, 0)])
        selected = select_input(
            conn,
            long_id,
            _task(
                "conversation-overview-v1",
                "conversation-summary-v1",
                max_input_chars=300,
            ),
        )
        assert selected.metadata["truncation_details"]
        assert selected.metadata["truncation_details"][0]["message_id"] in selected.metadata[
            "message_ids"
        ]

        empty_id = _seed(
            conn,
            "empty",
            [_message("system", "not conversation", 0), _message("assistant", "", 1)],
        )
        empty = select_input(
            conn,
            empty_id,
            _task("conversation-overview-v1", "conversation-summary-v1"),
        )
        assert empty.text == ""
        assert empty.metadata["message_ids"] == []
        assert empty.metadata["seq_start"] is None


def test_overview_ids_are_structural_despite_prefix_and_quoted_body_collisions(
    tmp_path: Path,
) -> None:
    messages = [
        _message(
            "user" if index % 2 == 0 else "assistant",
            (
                f"collision-marker-{index + 1}-" + "x" * 90
                + (" quoted message_id=3" if index == 19 else "")
            ),
            index,
        )
        for index in range(20)
    ]
    with connect(tmp_path / "id-collisions.db") as conn:
        conversation_id = _seed(conn, "id-collisions", messages)
        task = _production_catalog().tasks["work-mode-classification"].model_copy(
            update={"max_input_chars": 900}
        )
        first = select_input(conn, conversation_id, task)
        second = select_input(conn, conversation_id, task)

        assert first == second
        assert len(first.text) <= 900
        assert 20 in first.metadata["selected_message_ids"]
        assert 2 not in first.metadata["selected_message_ids"]
        assert 3 not in first.metadata["selected_message_ids"]
        assert first.metadata["message_ids"] == first.metadata["selected_message_ids"]
        assert "message_id=20" in first.text
        assert "quoted message_id=3" in first.text

        for false_evidence in (2, 3):
            failed = asyncio.run(
                run_task(
                    conn,
                    task_name=f"collision-{false_evidence}",
                    task=task,
                    profile_name="service-local",
                    profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
                    conversation_ids=[conversation_id],
                    client=StaticClient(
                        {
                            "mode": "executor",
                            "confidence": 0.8,
                            "reason": "Synthetic execution activity dominates.",
                            "evidence_message_ids": [false_evidence],
                        }
                    ),
                )
            )[0]
            assert failed["status"] == "failed"
            assert failed["error"] == "evidence_validation"

        valid = asyncio.run(
            run_task(
                conn,
                task_name="collision-valid",
                task=task,
                profile_name="service-local",
                profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
                conversation_ids=[conversation_id],
                client=StaticClient(
                    {
                        "mode": "executor",
                        "confidence": 0.8,
                        "reason": "Synthetic execution activity dominates.",
                        "evidence_message_ids": [20],
                    }
                ),
            )
        )[0]
        assert valid["status"] == "completed"
        rows = conn.execute(
            "SELECT status, result_json FROM ai_task_results ORDER BY id"
        ).fetchall()
        assert [row["status"] for row in rows] == ["failed", "failed", "success"]
        assert rows[0]["result_json"] is None
        assert rows[1]["result_json"] is None


def test_recent_selector_retains_newest_then_returns_chronological_and_stops(
    tmp_path: Path,
) -> None:
    messages = [_message("user", f"recent-{i}-" + "q" * 70, i) for i in range(8)]
    with connect(tmp_path / "recent.db") as conn:
        conversation_id = _seed(conn, "recent", messages)
        candidate_task = _task(
            "recent-meaningful-v1",
            "last-activity-v1",
            recent_message_count=5,
            max_input_chars=360,
        )
        selected = select_input(conn, conversation_id, candidate_task)
        assert selected.metadata["original_candidate_count"] == 5
        assert selected.metadata["message_ids"] == sorted(selected.metadata["message_ids"])
        assert selected.metadata["message_ids"][-1] == 8
        assert "recent-7-" in selected.text
        assert "recent-2-" not in selected.text
        assert len(selected.text) <= 360
        assert selected.metadata["sampling_strategy"] == "newest-complete-first"


SYNTHETIC_SCENARIOS = {
    "manager": [
        ("user", "Plan package Fern, delegate it, and define acceptance checks."),
        ("assistant", "Package Fern is delegated with three acceptance checks."),
        ("user", "Review the report and request rework on the missing check."),
    ],
    "executor": [
        ("user", "Implement the bounded Fern parser from the synthetic handoff."),
        ("assistant", "I inspected the parser, edited it, and ran its tests."),
        ("assistant", "The synthetic implementation and test report are delivered."),
    ],
    "one_off": [
        ("user", "What does a stable sort mean?"),
        ("assistant", "It preserves the order of records with equal keys."),
    ],
    "mixed": [
        ("user", "Define and delegate package Cedar."),
        ("assistant", "I then implemented Cedar and ran its synthetic checks."),
        ("user", "Now validate the delivery and reprioritize the next package."),
    ],
    "completed": [("assistant", "All synthetic checks passed and delivery is complete.")],
    "in_progress": [("assistant", "I am still implementing the second bounded step.")],
    "blocked": [("assistant", "Work is blocked because the synthetic service is unavailable.")],
    "awaiting_input": [("assistant", "I need the owner's synthetic format decision to continue.")],
    "explicit_action": [("assistant", "Next I will run the synthetic packaging check.")],
    "inferred_action": [
        ("assistant", "The implementation is ready; packaging is not yet checked.")
    ],
    "unknown_action": [("user", "A fragment without a supported continuation.")],
    "accurate_title": [("user", "Assess the Fern Parser title for the Fern parser work.")],
    "topic_change": [
        ("user", "Explain sorting."),
        ("assistant", "A short sorting explanation."),
        ("user", "Now implement and test the unrelated Cedar formatter."),
    ],
}


@pytest.mark.parametrize("scenario", sorted(SYNTHETIC_SCENARIOS))
def test_provider_neutral_synthetic_scenarios_are_selectable(
    tmp_path: Path, scenario: str
) -> None:
    messages = [
        _message(role, body, seq)
        for seq, (role, body) in enumerate(SYNTHETIC_SCENARIOS[scenario])
    ]
    with connect(tmp_path / f"scenario-{scenario}.db") as conn:
        conversation_id = _seed(conn, scenario, messages, title=f"Synthetic {scenario}")
        selector = "recent-meaningful-v1" if scenario in {
            "completed",
            "in_progress",
            "blocked",
            "awaiting_input",
            "explicit_action",
            "inferred_action",
            "unknown_action",
        } else "conversation-overview-v1"
        schema = (
            "last-activity-v1"
            if selector == "recent-meaningful-v1"
            else "title-assessment-v1"
        )
        selected = select_input(conn, conversation_id, _task(selector, schema))
        assert selected.text
        assert selected.metadata["message_ids"]


@pytest.mark.parametrize(
    ("model", "valid"),
    [
        (
            ConversationSummaryProviderResult,
            {"summary": "It began safely. It ended clearly.", "evidence_message_ids": [1]},
        ),
        (
            WorkModeClassificationResult,
            {
                "mode": "manager",
                "confidence": 0.8,
                "reason": "Coordination dominates.",
                "evidence_message_ids": [1],
            },
        ),
        (
            LastActivityResult,
            {
                "recent_work": "Synthetic work finished.",
                "status": "completed",
                "blockers": [],
                "next_action": None,
                "next_action_basis": "unknown",
                "evidence_message_ids": [1],
            },
        ),
        (
            TitleAssessmentResult,
            {
                "title_fits": True,
                "confidence": 0.9,
                "reason": "The title is specific.",
                "suggested_title": None,
                "evidence_message_ids": [1],
            },
        ),
    ],
)
def test_schema_json_and_strict_unknown_fields(model, valid) -> None:
    schema = model.model_json_schema()
    assert schema["additionalProperties"] is False
    model.model_validate(valid)
    with pytest.raises(ValidationError):
        model.model_validate({**valid, "unexpected": True})
    with pytest.raises(ValidationError):
        model.model_validate({**valid, "evidence_message_ids": ["1"]})


@pytest.mark.parametrize("mode", ["manager", "executor", "one_off", "mixed", "unknown"])
def test_all_work_modes_are_contract_values(mode: str) -> None:
    WorkModeClassificationResult.model_validate(
        {"mode": mode, "confidence": 0.5, "reason": "Synthetic reason.", "evidence_message_ids": []}
    )


@pytest.mark.parametrize(
    "status", ["in_progress", "completed", "blocked", "awaiting_input", "unknown"]
)
def test_all_activity_statuses_are_contract_values(status: str) -> None:
    LastActivityResult.model_validate(
        {
            "recent_work": "Synthetic recent work.",
            "status": status,
            "blockers": ["Synthetic blocker."] if status == "blocked" else [],
            "next_action": None,
            "next_action_basis": "unknown",
            "evidence_message_ids": [],
        }
    )


@pytest.mark.parametrize(
    ("basis", "action"),
    [
        ("explicit", "Run the synthetic check."),
        ("inferred", "Inspect the next step."),
        ("unknown", None),
    ],
)
def test_all_next_action_bases_are_contract_values(basis: str, action: str | None) -> None:
    LastActivityResult.model_validate(
        {
            "recent_work": "Synthetic recent work.",
            "status": "in_progress" if basis != "unknown" else "unknown",
            "blockers": [],
            "next_action": action,
            "next_action_basis": basis,
            "evidence_message_ids": [],
        }
    )


def test_schema_consistency_and_bounds() -> None:
    with pytest.raises(ValidationError, match="suggested_title"):
        TitleAssessmentResult.model_validate(
            {
                "title_fits": True,
                "confidence": 1,
                "reason": "Fits.",
                "suggested_title": "Must not exist",
                "evidence_message_ids": [],
            }
        )
    with pytest.raises(ValidationError, match="next_action"):
        LastActivityResult.model_validate(
            {
                "recent_work": "Work.",
                "status": "unknown",
                "blockers": [],
                "next_action": "Invented action",
                "next_action_basis": "unknown",
                "evidence_message_ids": [],
            }
        )
    with pytest.raises(ValidationError, match="2-5"):
        ConversationSummaryProviderResult.model_validate(
            {"summary": "Only one sentence.", "evidence_message_ids": []}
        )


class StaticClient:
    def __init__(self, output: dict) -> None:
        self.output = output
        self.requests = []

    async def complete(self, request):
        self.requests.append(request)
        return CompletionResponse(json.dumps(self.output), "mock", request.model)


def test_summary_dates_are_application_owned_and_evidence_is_validated(tmp_path: Path) -> None:
    client = StaticClient(
        {
            "summary": "The synthetic task was requested. A bounded result was returned.",
            "evidence_message_ids": [1],
        }
    )
    task = _production_catalog().tasks["conversation-summary"]
    with connect(tmp_path / "summary.db") as conn:
        conversation_id = _seed(conn, "summary", [_message("user", "Synthetic request", 0)])
        result = asyncio.run(
            run_task(
                conn,
                task_name="conversation-summary",
                task=task,
                profile_name="service-local",
                profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
                conversation_ids=[conversation_id],
                client=client,
            )
        )[0]
        assert result["status"] == "completed"
        assert result["result"]["start_date"] == "2026-02-01T09:00:00.000000Z"
        assert result["result"]["last_active_date"] == "2026-02-03T09:00:00.000000Z"
        assert set(client.requests[0].response_schema["properties"]) == {
            "summary",
            "evidence_message_ids",
        }

        bad = StaticClient(
            {
                "summary": "The synthetic task was requested. An invalid citation was returned.",
                "evidence_message_ids": [999],
            }
        )
        failed = asyncio.run(
            run_task(
                conn,
                task_name="conversation-summary-bad-evidence",
                task=task,
                profile_name="service-local",
                profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
                conversation_ids=[conversation_id],
                client=bad,
            )
        )[0]
        assert failed["status"] == "failed"
        assert failed["error"] == "evidence_validation"
        row = conn.execute("SELECT error FROM ai_task_results ORDER BY id DESC").fetchone()
        assert "999" not in row["error"]


def test_all_tasks_store_independently_and_title_assessment_never_writes_title(
    tmp_path: Path,
) -> None:
    catalog = _production_catalog()
    outputs = {
        "conversation-summary": {
            "summary": "The synthetic request was discussed. The response records a safe result.",
            "evidence_message_ids": [1],
        },
        "work-mode-classification": {
            "mode": "one_off",
            "confidence": 0.8,
            "reason": "A bounded standalone exchange.",
            "evidence_message_ids": [1],
        },
        "last-activity": {
            "recent_work": "A bounded synthetic exchange completed.",
            "status": "completed",
            "blockers": [],
            "next_action": None,
            "next_action_basis": "unknown",
            "evidence_message_ids": [1],
        },
        "title-assessment": {
            "title_fits": False,
            "confidence": 0.9,
            "reason": "The source title is generic.",
            "suggested_title": "Bounded Synthetic Exchange",
            "evidence_message_ids": [1],
        },
    }
    with connect(tmp_path / "independent.db") as conn:
        conversation_id = _seed(
            conn, "independent", [_message("user", "Explain a synthetic concept", 0)], title="Chat"
        )
        fts_before = conn.execute("SELECT * FROM chat_fts ORDER BY rowid").fetchall()
        for task_name, output in outputs.items():
            result = asyncio.run(
                run_task(
                    conn,
                    task_name=task_name,
                    task=catalog.tasks[task_name],
                    profile_name="service-local",
                    profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
                    conversation_ids=[conversation_id],
                    client=StaticClient(output),
                )
            )[0]
            assert result["status"] == "completed"
        rows = conn.execute(
            "SELECT task_name, output_schema_name, output_schema_version FROM ai_task_results"
        ).fetchall()
        assert {row["task_name"] for row in rows} == set(outputs)
        assert len({(row["task_name"], row["output_schema_name"]) for row in rows}) == 4
        assert all("finalizer-1" in row["output_schema_version"] for row in rows)
        assert conn.execute("SELECT title FROM conversations").fetchone()["title"] == "Chat"
        assert conn.execute("SELECT * FROM chat_fts ORDER BY rowid").fetchall() == fts_before


def test_finalizer_version_change_invalidates_only_schema_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    task = _production_catalog().tasks["conversation-summary"]
    client = StaticClient(
        {
            "summary": "The synthetic task began. The synthetic task ended.",
            "evidence_message_ids": [1],
        }
    )
    with connect(tmp_path / "finalizer-cache.db") as conn:
        conversation_id = _seed(conn, "finalizer", [_message("user", "Synthetic task", 0)])
        arguments = dict(
            conn=conn,
            task_name="conversation-summary",
            task=task,
            profile_name="service-local",
            profile=ModelProfile(model="mock", api_base="http://localhost/v1"),
            conversation_ids=[conversation_id],
            client=client,
        )
        assert asyncio.run(run_task(**arguments))[0]["status"] == "completed"
        assert asyncio.run(run_task(**arguments))[0]["status"] == "cached"
        original = ai_module.OUTPUT_SCHEMAS["conversation-summary-v1"]
        assert isinstance(original, ai_module.OutputSchemaSpec)
        monkeypatch.setitem(
            ai_module.OUTPUT_SCHEMAS,
            "conversation-summary-v1",
            replace(original, finalizer_version="2"),
        )
        assert asyncio.run(run_task(**arguments))[0]["status"] == "completed"
        assert len(client.requests) == 2


def test_prompts_capture_approved_semantics_without_chain_of_thought_request() -> None:
    catalog = _production_catalog()
    work_prompt = catalog.tasks["work-mode-classification"].system_prompt
    for label in ("manager", "executor", "one_off", "mixed", "unknown"):
        assert label in work_prompt
    activity_prompt = catalog.tasks["last-activity"].system_prompt
    for status in ("in_progress", "completed", "blocked", "awaiting_input", "unknown"):
        assert status in activity_prompt
    all_prompts = "\n".join(
        task.system_prompt + task.user_prompt for task in catalog.tasks.values()
    ).lower()
    assert "do not provide chain-of-thought" in all_prompts
