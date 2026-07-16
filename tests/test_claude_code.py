from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from typer.testing import CliRunner

from chat_chronicle.adapters.claude_code import (
    ClaudeCodeExtractResult,
    load_conversations,
    parse_session_jsonl,
)
from chat_chronicle.cli import app
from chat_chronicle.db import connect
from chat_chronicle.models import Conversation

FIXTURES = Path(__file__).parent / "fixtures" / "claude_code"
runner = CliRunner()


def _fixture_path(name: str, filename: str | None = None) -> Path:
    directory = FIXTURES / name
    if filename is not None:
        return directory / filename
    matches = sorted(directory.glob("*.jsonl"))
    assert len(matches) == 1
    return matches[0]


def _parse(name: str) -> ClaudeCodeExtractResult:
    path = _fixture_path(name)
    return parse_session_jsonl(path.read_text(encoding="utf-8"), source_name=str(path))


def _error_codes(result: ClaudeCodeExtractResult) -> set[str]:
    return {error.error for error in result.errors}


def _only(result: ClaudeCodeExtractResult) -> Conversation:
    assert len(result.conversations) == 1
    return result.conversations[0]


def _invoke_ingest(source: Path, db_path: Path, provider: str = "claude_code"):
    return runner.invoke(
        app,
        [
            "ingest",
            str(source),
            "--provider",
            provider,
            "--db-path",
            str(db_path),
        ],
    )


def test_parse_single_synthetic_claude_code_session() -> None:
    result = load_conversations(_fixture_path("project_one", "session-one.jsonl"))

    assert result.errors == []
    conversation = _only(result)
    assert conversation.provider == "claude_code"
    assert conversation.provider_conv_id.startswith("claude-code-session-one::session-one::")
    assert conversation.title == "Synthetic Claude Code fixture"
    expected_origin_path = str(_fixture_path("project_one", "session-one.jsonl").resolve())
    assert conversation.origin_path == expected_origin_path
    assert conversation.resume_hint == "claude --resume claude-code-session-one"
    assert conversation.created_at == datetime(2026, 7, 1, 9, 0, tzinfo=UTC)
    assert conversation.updated_at == datetime(2026, 7, 1, 9, 1, tzinfo=UTC)
    assert [message.role for message in conversation.messages] == ["user", "assistant"]
    assert conversation.messages[1].body == "The alpha fixture term is present in this response."


def test_parse_project_directory_with_multiple_sessions() -> None:
    result = load_conversations(FIXTURES / "project_one")

    assert result.errors == []
    provider_ids = [conversation.provider_conv_id for conversation in result.conversations]
    assert provider_ids[0].startswith("claude-code-session-one::session-one::")
    assert provider_ids[1].startswith("claude-code-session-two::session-two::")


def test_parse_projects_root_with_multiple_project_directories() -> None:
    result = load_conversations(FIXTURES / "projects_root")

    assert result.errors == []
    provider_ids = [conversation.provider_conv_id for conversation in result.conversations]
    assert provider_ids[0].startswith("claude-code-root-one::session-root-one::")
    assert provider_ids[1].startswith("claude-code-root-two::session-root-two::")
    assert sorted(hint.name for hint in result.project_hints.values()) == [
        "project-one",
        "project-two",
    ]


def test_malformed_json_and_unknown_records_are_serializable_errors() -> None:
    result = _parse("malformed")
    conversation = _only(result)

    assert [message.body for message in conversation.messages] == [
        "Healthy malformed fixture text.",
        "Healthy assistant text survives.",
    ]
    assert {
        "invalid_jsonl_line",
        "unknown_record_type",
        "unknown_content_block_type",
        "invalid_timestamp",
    } <= _error_codes(result)
    payload = [error.model_dump() for error in result.errors]
    assert json.loads(json.dumps(payload)) == payload


def test_metadata_and_tool_records_do_not_create_noisy_errors() -> None:
    result = _parse("metadata")
    conversation = _only(result)

    assert result.errors == []
    assert [message.body for message in conversation.messages] == [
        "Metadata fixture visible text.",
        "Metadata fixture answer.",
    ]


def test_cli_ingest_persists_project_id_messages_and_ingest_run(tmp_path: Path) -> None:
    db_path = tmp_path / "chronicle.db"

    result = _invoke_ingest(FIXTURES / "project_one", db_path)

    assert result.exit_code == 0, result.stdout
    assert "provider: claude_code" in result.stdout
    assert "conversations seen: 2" in result.stdout
    with connect(db_path) as conn:
        assert conn.execute("SELECT count(*) FROM conversations").fetchone()[0] == 2
        assert conn.execute("SELECT count(*) FROM messages").fetchone()[0] == 4
        assert conn.execute("SELECT count(*) FROM ingest_runs").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM projects").fetchone()[0] == 1
        row = conn.execute(
            """
            SELECT c.project_id, c.origin_path, c.resume_hint, p.name, p.root_path
            FROM conversations AS c
            JOIN projects AS p ON p.id = c.project_id
            WHERE c.provider_conv_id LIKE 'claude-code-session-one::session-one::%'
            """
        ).fetchone()
    assert row["project_id"] is not None
    assert row["origin_path"].endswith("session-one.jsonl")
    assert row["resume_hint"] == "claude --resume claude-code-session-one"
    assert row["name"] == "project-one"
    assert row["root_path"].endswith("project-one")


def test_cli_ingest_repeated_source_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "chronicle.db"

    first = _invoke_ingest(FIXTURES / "project_one", db_path)
    second = _invoke_ingest(FIXTURES / "project_one", db_path)

    assert first.exit_code == 0, first.stdout
    assert second.exit_code == 0, second.stdout
    assert "added: 0  updated: 0  skipped: 2" in second.stdout
    with connect(db_path) as conn:
        assert conn.execute("SELECT count(*) FROM sources").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM conversations").fetchone()[0] == 2
        assert conn.execute("SELECT count(*) FROM messages").fetchone()[0] == 4
        assert conn.execute("SELECT count(*) FROM ingest_runs").fetchone()[0] == 2


def test_cli_auto_detects_claude_code_and_search_open_work(tmp_path: Path) -> None:
    db_path = tmp_path / "chronicle.db"
    ingest = _invoke_ingest(FIXTURES / "project_one", db_path, provider="auto")

    assert ingest.exit_code == 0, ingest.stdout
    assert "provider: claude_code" in ingest.stdout

    search = runner.invoke(
        app,
        ["search", "alpha", "--provider", "claude_code", "--db-path", str(db_path)],
    )
    assert search.exit_code == 0, search.stdout
    assert "claude_code" in search.stdout
    assert "alpha fixture term" in search.stdout

    with connect(db_path) as conn:
        conversation_id = int(
            conn.execute(
                "SELECT id FROM conversations WHERE provider_conv_id LIKE ?",
                ("claude-code-session-one::session-one::%",),
            ).fetchone()[0]
        )
    opened = runner.invoke(app, ["open", str(conversation_id), "--db-path", str(db_path)])

    assert opened.exit_code == 0, opened.stdout
    assert "provider: claude_code" in opened.stdout
    assert "origin_path:" in opened.stdout
    assert "session-one.jsonl" in opened.stdout
    assert "resume_hint: claude --resume claude-code-session-one" in opened.stdout
    assert "Find the alpha fixture term." in opened.stdout


def test_ai_title_wins_over_synthesized_title() -> None:
    conversation = _only(_parse("ai_title_precedence"))

    assert conversation.title == "AI Title Wins"
    assert conversation.messages[0].body == "This fallback title should not win."


def test_missing_ai_title_still_synthesizes_from_first_user_message() -> None:
    conversation = _only(load_conversations(_fixture_path("project_one", "session-two.jsonl")))

    assert conversation.title == "Second session question with beta term."


def test_rs2_live_observed_record_types_uuid_parent_and_sidechain_behavior() -> None:
    result = _parse("rs2_records")
    conversation = _only(result)

    assert result.errors == []
    assert conversation.title == "RS2 Live Shape Title"
    assert [message.role for message in conversation.messages] == [
        "user",
        "system",
        "assistant",
        "assistant",
    ]
    assert [message.provider_message_id for message in conversation.messages] == [
        "rs2-user-uuid",
        "rs2-system-uuid",
        "rs2-assistant-uuid",
        "rs2-sidechain-uuid",
    ]
    assert [message.body for message in conversation.messages] == [
        "RS2 user visible text.",
        "RS2 system visible text.",
        "RS2 assistant visible text.",
        "RS2 sidechain visible text.",
    ]


def test_same_session_id_in_multiple_files_stays_file_scoped_on_ingest(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "chronicle.db"

    result = _invoke_ingest(FIXTURES / "multi_file_same_session", db_path)

    assert result.exit_code == 0, result.stdout
    assert "conversations seen: 2" in result.stdout
    assert "added: 2  updated: 0  skipped: 0" in result.stdout
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT provider_conv_id, origin_path, resume_hint, title
            FROM conversations
            ORDER BY origin_path
            """
        ).fetchall()
        messages = conn.execute(
            """
            SELECT c.origin_path, m.body
            FROM conversations AS c
            JOIN messages AS m ON m.conversation_id = c.id
            WHERE m.role = 'user'
            ORDER BY c.origin_path, m.seq
            """
        ).fetchall()

    assert len(rows) == 2
    assert rows[0]["provider_conv_id"] != rows[1]["provider_conv_id"]
    assert all(row["provider_conv_id"].startswith("shared-resume-session::branch-") for row in rows)
    assert [Path(row["origin_path"]).name for row in rows] == ["branch-a.jsonl", "branch-b.jsonl"]
    assert [row["resume_hint"] for row in rows] == [
        "claude --resume shared-resume-session",
        "claude --resume shared-resume-session",
    ]
    assert [row["title"] for row in rows] == [
        "Shared Resume Branch A",
        "Shared Resume Branch B",
    ]
    assert [row["body"] for row in messages] == [
        "Branch A unique visible text.",
        "Branch B unique visible text.",
    ]
