from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from chat_chronicle.ai import CompletionResponse, run_task
from chat_chronicle.ai_config import ModelProfile, TaskDefinition
from chat_chronicle.cli import app
from chat_chronicle.db import connect, upsert_conversation
from chat_chronicle.models import Conversation, Message

runner = CliRunner()


def _catalogs(base: Path, *, remote: bool = False, enabled: bool = True) -> None:
    directory = base / ".chronicle"
    directory.mkdir(parents=True, exist_ok=True)
    task = {
        "enabled": enabled,
        "version": "1",
        "description": "Synthetic test task",
        "model_profile": "test-profile",
        "input_selector": "full-conversation",
        "output_schema": "example-result-v1",
        "system_prompt": "Return JSON.",
        "user_prompt": "{transcript}",
    }
    (directory / "ai-tasks.yaml").write_text(
        yaml.safe_dump({"version": 1, "tasks": {"test-task": task}}), encoding="utf-8"
    )
    api_base = "https://example.invalid/v1" if remote else "http://127.0.0.1:1234/v1"
    (directory / "ai-models.yaml").write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "profiles": {
                    "test-profile": {
                        "model": "synthetic-model",
                        "api_base": api_base,
                        "remote": False,
                    }
                },
            }
        ),
        encoding="utf-8",
    )


def _seed(base: Path, identity: str = "one", *, updated: datetime | None = None) -> int:
    db = base / ".chronicle" / "chronicle.db"
    now = updated or datetime(2026, 1, 1, 12, tzinfo=UTC)
    with connect(db) as conn:
        return upsert_conversation(
            conn,
            None,
            Conversation(
                provider="synthetic",
                provider_conv_id=identity,
                title=f"Title {identity}",
                created_at=now,
                updated_at=now,
                messages=[Message(role="user", body=f"private-{identity}", seq=0)],
            ),
        ).conversation_id


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CHAT_CHRONICLE_DB", str(tmp_path / ".chronicle" / "chronicle.db"))
    _catalogs(tmp_path)
    return tmp_path


def test_list_needs_no_litellm_and_lists_task_and_profile(project: Path) -> None:
    sys.modules.pop("litellm", None)
    result = runner.invoke(app, ["--ai-task", "list"])
    assert result.exit_code == 0, result.output
    assert "test-task" in result.output
    assert "test-profile: local" in result.output
    assert "litellm" not in sys.modules


def test_verbose_list_reports_privacy_safe_catalog_source_and_profile(project: Path) -> None:
    sys.modules.pop("litellm", None)
    result = runner.invoke(app, ["--ai-task", "list", "--verbose"])
    assert result.exit_code == 0, result.output
    assert "AI configuration source: repository-local .chronicle" in result.output
    assert "task catalog: .chronicle/ai-tasks.yaml" in result.output
    assert "model catalog: .chronicle/ai-models.yaml" in result.output
    assert "timeout=60s" in result.output
    assert "retries=1" in result.output
    assert "structured_output=True" in result.output
    assert str(project) not in result.output
    assert "litellm" not in sys.modules


def test_verbose_execution_reports_effective_config_without_private_content(
    project: Path,
) -> None:
    conversation_id = _seed(project)
    result = runner.invoke(
        app,
        [
            "--ai-task",
            "test-task",
            "--conversation-id",
            str(conversation_id),
            "--dry-run",
            "--verbose",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "effective task config:" in result.output
    assert "selector=full-conversation" in result.output
    assert "schema=example-result-v1" in result.output
    assert "temperature=0" in result.output
    assert "effective model config: endpoint=loopback" in result.output
    assert "timeout=60s" in result.output
    assert "private-one" not in result.output
    assert str(project) not in result.output


def test_verbose_labels_environment_config_override_without_printing_path(
    project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    override = project / ".chronicle"
    monkeypatch.setenv("CHAT_CHRONICLE_AI_CONFIG_DIR", str(override))
    result = runner.invoke(app, ["--ai-task", "list", "--verbose"])
    assert result.exit_code == 0, result.output
    assert "AI configuration source: CHAT_CHRONICLE_AI_CONFIG_DIR override" in result.output
    assert "task catalog: [CHAT_CHRONICLE_AI_CONFIG_DIR]/ai-tasks.yaml" in result.output
    assert "model catalog: [CHAT_CHRONICLE_AI_CONFIG_DIR]/ai-models.yaml" in result.output
    assert str(override) not in result.output


@pytest.mark.parametrize(
    "args",
    [
        ["--ai-task", "test-task"],
        ["--ai-task", "test-task", "--conversation-id", "1", "--limit", "1"],
        ["--ai-task", "list", "--dry-run"],
        ["--dry-run", "stats"],
        ["--ai-task", "test-task", "--conversation-id", "1", "--provider", "synthetic"],
        ["--verbose", "stats"],
    ],
)
def test_scope_and_option_conflicts_are_actionable_without_traceback(
    project: Path, args: list[str]
) -> None:
    result = runner.invoke(app, args)
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_nonexistent_exact_selection_is_actionable(project: Path) -> None:
    result = runner.invoke(app, ["--ai-task", "test-task", "--conversation-id", "999", "--dry-run"])
    assert result.exit_code == 1
    assert "does not exist" in result.output
    assert "Traceback" not in result.output


def test_unknown_task_model_alias_is_actionable(project: Path) -> None:
    tasks = project / ".chronicle" / "ai-tasks.yaml"
    data = yaml.safe_load(tasks.read_text("utf-8"))
    data["tasks"]["test-task"]["model_profile"] = "missing-profile"
    tasks.write_text(yaml.safe_dump(data), encoding="utf-8")
    conversation_id = _seed(project)
    result = runner.invoke(
        app,
        ["--ai-task", "test-task", "--conversation-id", str(conversation_id), "--dry-run"],
    )
    assert result.exit_code == 1
    assert "unknown model profile" in result.output
    assert "missing-profile" in result.output
    assert "Traceback" not in result.output


def test_non_loopback_cannot_claim_local_and_allow_remote_is_ephemeral(
    project: Path,
) -> None:
    _catalogs(project, remote=True)
    conversation_id = _seed(project)
    args = ["--ai-task", "test-task", "--conversation-id", str(conversation_id), "--dry-run"]
    blocked = runner.invoke(app, args)
    assert blocked.exit_code == 1
    assert "--allow-remote" in blocked.output
    allowed = runner.invoke(app, [*args, "--allow-remote"])
    assert allowed.exit_code == 0, allowed.output
    blocked_again = runner.invoke(app, args)
    assert blocked_again.exit_code == 1


def test_bounded_filters_use_date_only_until_end_of_day(project: Path) -> None:
    included = _seed(project, "included", updated=datetime(2026, 1, 2, 23, tzinfo=UTC))
    _seed(project, "excluded", updated=datetime(2026, 1, 3, tzinfo=UTC))
    result = runner.invoke(
        app,
        [
            "--ai-task",
            "test-task",
            "--limit",
            "5",
            "--provider",
            "synthetic",
            "--until",
            "2026-01-02",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    assert f"conversation ids: {included}" in result.output
    assert "selected: 1" in result.output


def test_dry_run_reports_exact_cache_counts_and_prints_no_transcript(project: Path) -> None:
    first = _seed(project, "cached")
    second = _seed(project, "miss")

    class Client:
        async def complete(self, request):
            return CompletionResponse('{"result":"ok"}', "mock-provider", "mock-model")

    with connect(project / ".chronicle" / "chronicle.db") as conn:
        asyncio.run(
            run_task(
                conn,
                task_name="test-task",
                task=TaskDefinition.model_validate(
                    yaml.safe_load((project / ".chronicle" / "ai-tasks.yaml").read_text("utf-8"))[
                        "tasks"
                    ]["test-task"]
                ),
                profile_name="test-profile",
                profile=ModelProfile(model="synthetic-model", api_base="http://127.0.0.1:1234/v1"),
                conversation_ids=[first],
                client=Client(),
            )
        )
    result = runner.invoke(app, ["--ai-task", "test-task", "--limit", "2", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "cache hits: 1  cache misses: 1" in result.output
    assert "input estimate:" in result.output
    assert "configured context window: not set" in result.output
    assert "private-cached" not in result.output
    assert "private-miss" not in result.output
    assert str(second) in result.output


def test_success_and_missing_dependency_output_provenance_and_action(
    project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    conversation_id = _seed(project)

    async def successful(*args, **kwargs):
        return [
            {
                "status": "completed",
                "id": 7,
                "conversation_id": conversation_id,
                "result": {"result": "safe"},
                "actual_provider": "mock-provider",
                "actual_model": "mock-model",
            }
        ]

    monkeypatch.setattr("chat_chronicle.cli.run_task", successful)
    args = ["--ai-task", "test-task", "--conversation-id", str(conversation_id)]
    success = runner.invoke(app, args)
    assert success.exit_code == 0, success.output
    assert "mock-provider/mock-model" in success.output

    async def missing(*args, **kwargs):
        return [
            {
                "status": "failed",
                "id": 8,
                "conversation_id": conversation_id,
                "error": "dependency",
                "detail": "AI support is not installed; run `poetry install -E enrich`.",
            }
        ]

    monkeypatch.setattr("chat_chronicle.cli.run_task", missing)
    failure = runner.invoke(app, args)
    assert failure.exit_code == 1
    assert "poetry install -E enrich" in failure.output
    assert "Traceback" not in failure.output
