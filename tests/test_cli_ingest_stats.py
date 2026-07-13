from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from chat_chronicle.cli import app
from chat_chronicle.db import connect

runner = CliRunner()
FIXTURES = Path(__file__).parent / "fixtures"


def _db_path(tmp_path: Path) -> Path:
    return tmp_path / "chronicle.db"


def _invoke_ingest(source: Path, db_path: Path, provider: str = "auto"):
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


def _count_rows(db_path: Path, table: str) -> int:
    with connect(db_path) as conn:
        return int(conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0])


def _single_value(db_path: Path, sql: str):
    with connect(db_path) as conn:
        return conn.execute(sql).fetchone()[0]


def test_ingest_auto_detects_chatgpt_and_inserts_conversations_and_messages(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    source = FIXTURES / "chatgpt" / "minimal" / "conversations.json"

    result = _invoke_ingest(source, db_path)

    assert result.exit_code == 0, result.stdout
    assert "provider: chatgpt" in result.stdout
    assert "conversations seen: 1" in result.stdout
    assert _count_rows(db_path, "conversations") == 1
    assert _count_rows(db_path, "messages") == 2


def test_ingest_auto_detects_split_chatgpt_zip(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    source = tmp_path / "chatgpt-split-export.zip"
    record = json.loads(
        (FIXTURES / "chatgpt" / "minimal" / "conversations.json").read_text(
            encoding="utf-8"
        )
    )[0]
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("export/conversations-000.json", json.dumps([record]))

    result = _invoke_ingest(source, db_path)

    assert result.exit_code == 0, result.stdout
    assert "provider: chatgpt" in result.stdout
    assert "conversations seen: 1" in result.stdout
    assert _count_rows(db_path, "conversations") == 1
    assert _count_rows(db_path, "messages") == 2


def test_ingest_auto_detects_claude_and_inserts_conversations_and_messages(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    source = FIXTURES / "claude" / "minimal" / "conversations.json"

    result = _invoke_ingest(source, db_path)

    assert result.exit_code == 0, result.stdout
    assert "provider: claude" in result.stdout
    assert _count_rows(db_path, "conversations") == 1
    assert _count_rows(db_path, "messages") == 2


def test_ingest_auto_detects_openai_codex_jsonl_and_inserts_conversation(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    source = FIXTURES / "openai_codex" / "minimal" / "rollout-minimal.jsonl"

    result = _invoke_ingest(source, db_path)

    assert result.exit_code == 0, result.stdout
    assert "provider: openai_codex" in result.stdout
    assert _count_rows(db_path, "conversations") == 1
    assert _count_rows(db_path, "messages") == 2


def test_ingest_auto_detects_openai_codex_home_directory(tmp_path: Path) -> None:
    codex_home = tmp_path / "codex-home"
    session_dir = codex_home / "sessions" / "2026" / "06" / "01"
    session_dir.mkdir(parents=True)
    shutil.copyfile(
        FIXTURES / "openai_codex" / "minimal" / "rollout-minimal.jsonl",
        session_dir / "rollout-minimal.jsonl",
    )
    (codex_home / "session_index.jsonl").write_text(
        json.dumps({"id": "codex-minimal-1", "thread_name": "Indexed title"}) + "\n",
        encoding="utf-8",
    )

    result = _invoke_ingest(codex_home, _db_path(tmp_path))

    assert result.exit_code == 0, result.stdout
    assert "provider: openai_codex" in result.stdout


@pytest.mark.parametrize(
    ("provider", "source"),
    [
        ("chatgpt", FIXTURES / "chatgpt" / "minimal" / "conversations.json"),
        ("claude", FIXTURES / "claude" / "minimal" / "conversations.json"),
        ("openai_codex", FIXTURES / "openai_codex" / "minimal" / "rollout-minimal.jsonl"),
    ],
)
def test_ingest_explicit_providers_work(provider: str, source: Path, tmp_path: Path) -> None:
    result = _invoke_ingest(source, _db_path(tmp_path), provider=provider)

    assert result.exit_code == 0, result.stdout
    assert f"provider: {provider}" in result.stdout


def test_reingesting_unchanged_source_reuses_source_and_skips_conversation(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    source = FIXTURES / "chatgpt" / "minimal" / "conversations.json"

    first = _invoke_ingest(source, db_path)
    second = _invoke_ingest(source, db_path)

    assert first.exit_code == 0, first.stdout
    assert second.exit_code == 0, second.stdout
    assert "added: 0  updated: 0  skipped: 1" in second.stdout
    assert _count_rows(db_path, "sources") == 1
    assert _count_rows(db_path, "ingest_runs") == 2


def test_importer_parse_errors_are_stored_without_aborting_valid_conversations(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    source = FIXTURES / "chatgpt" / "malformed" / "conversations.json"

    result = _invoke_ingest(source, db_path)

    assert result.exit_code == 0, result.stdout
    assert "parse errors: " in result.stdout
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT status, conversations_seen, errors_json FROM ingest_runs"
        ).fetchone()
    errors = json.loads(row["errors_json"])
    assert row["status"] == "success"
    assert row["conversations_seen"] > 0
    assert {error["error"] for error in errors} >= {"invalid_conversation_record"}


def test_unsupported_auto_detection_exits_nonzero_without_ingest_run(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    source = tmp_path / "unsupported.txt"
    source.write_text("not a supported export", encoding="utf-8")

    result = _invoke_ingest(source, db_path)

    assert result.exit_code != 0
    assert "Unsupported source format" in result.stderr
    assert not db_path.exists()


def test_ambiguous_auto_detection_exits_nonzero_without_ingest_run(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    source = tmp_path / "conversations.json"
    source.write_text(
        json.dumps(
            [
                {
                    "id": "chatgpt-ish",
                    "mapping": {},
                    "uuid": "claude-ish",
                    "chat_messages": [],
                }
            ]
        ),
        encoding="utf-8",
    )

    result = _invoke_ingest(source, db_path)

    assert result.exit_code != 0
    assert "Ambiguous provider detection" in result.stderr
    assert not db_path.exists()


def test_ingest_rebuilds_fts(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    source = FIXTURES / "chatgpt" / "minimal" / "conversations.json"

    result = _invoke_ingest(source, db_path)

    assert result.exit_code == 0, result.stdout
    assert _single_value(
        db_path,
        "SELECT count(*) FROM chat_fts WHERE chat_fts MATCH 'docker'",
    ) == 1


def test_stats_reports_counts_provider_sources_and_runs_after_ingest(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    ingest_result = _invoke_ingest(
        FIXTURES / "claude" / "minimal" / "conversations.json",
        db_path,
    )
    assert ingest_result.exit_code == 0, ingest_result.stdout

    result = runner.invoke(app, ["stats", "--db-path", str(db_path)])

    assert result.exit_code == 0, result.stdout
    assert "total conversations: 1" in result.stdout
    assert "total messages: 2" in result.stdout
    assert "claude" in result.stdout
    assert "Recent ingest runs" in result.stdout


def test_stats_works_on_empty_database(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)

    result = runner.invoke(app, ["stats", "--db-path", str(db_path)])

    assert result.exit_code == 0, result.stdout
    assert "total conversations: 0" in result.stdout
    assert "total messages: 0" in result.stdout
    assert db_path.exists()
