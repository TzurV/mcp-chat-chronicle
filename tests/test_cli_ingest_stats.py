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


def _copy_fixture(source: Path, destination: Path) -> Path:
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    return destination


def _count_rows(db_path: Path, table: str) -> int:
    with connect(db_path) as conn:
        return int(conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0])


def _single_value(db_path: Path, sql: str):
    with connect(db_path) as conn:
        return conn.execute(sql).fetchone()[0]


def _source_rows(db_path: Path):
    with connect(db_path) as conn:
        return conn.execute(
            "SELECT provider, path_or_config FROM sources ORDER BY id"
        ).fetchall()


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


def test_ingest_claude_project_metadata_links_and_searches_project_name(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    source = FIXTURES / "claude" / "project_linked"

    first = _invoke_ingest(source, db_path)
    second = _invoke_ingest(source, db_path)
    search = runner.invoke(
        app,
        ["search", "CAR GUI", "--provider", "claude", "--db-path", str(db_path)],
    )

    assert first.exit_code == 0, first.stdout
    assert "provider: claude" in first.stdout
    assert "conversations seen: 1" in first.stdout
    assert "parse errors: 1" in first.stdout
    assert second.exit_code == 0, second.stdout
    assert "added: 0  updated: 0  skipped: 1" in second.stdout
    assert _count_rows(db_path, "projects") == 1
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT c.project_id, p.name
            FROM conversations AS c
            LEFT JOIN projects AS p ON p.id = c.project_id
            WHERE c.provider_conv_id = 'conv-project-linked-1'
            """
        ).fetchone()
    assert row["project_id"] is not None
    assert row["name"] == "CAR GUI"
    assert search.exit_code == 0, search.stdout
    assert "CAR GUI" in search.stdout
    assert "Linked Claude project chat" in search.stdout


def test_ingest_claude_project_metadata_without_reference_does_not_guess_link(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    source = FIXTURES / "claude" / "project_unlinked"

    result = _invoke_ingest(source, db_path)
    search = runner.invoke(
        app,
        [
            "search",
            "Standalone Claude Project",
            "--provider",
            "claude",
            "--db-path",
            str(db_path),
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert _count_rows(db_path, "projects") == 1
    with connect(db_path) as conn:
        project_id = conn.execute(
            "SELECT project_id FROM conversations WHERE provider_conv_id = ?",
            ("conv-project-unlinked-1",),
        ).fetchone()[0]
    assert project_id is None
    assert search.exit_code == 0, search.stdout
    assert "No results" in search.stdout


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


def test_directory_sweep_auto_ingests_multiple_supported_child_sources(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    parent = tmp_path / "exports"
    parent.mkdir()
    _copy_fixture(FIXTURES / "chatgpt" / "minimal", parent / "a-chatgpt-export")
    _copy_fixture(FIXTURES / "claude" / "minimal", parent / "b-claude-export")
    _copy_fixture(
        FIXTURES / "openai_codex" / "minimal" / "rollout-minimal.jsonl",
        parent / "c-codex" / "rollout-minimal.jsonl",
    )

    result = _invoke_ingest(parent, db_path)

    assert result.exit_code == 0, result.stdout
    assert "parent source directory:" in result.stdout
    assert "discovered supported sources: 3" in result.stdout
    assert "source: chatgpt" in result.stdout
    assert "source: claude" in result.stdout
    assert "source: openai_codex" in result.stdout
    assert "total conversations seen: 3" in result.stdout
    assert "total added: 3  updated: 0  skipped: 0" in result.stdout
    assert _count_rows(db_path, "sources") == 3
    assert _count_rows(db_path, "conversations") == 3
    assert _count_rows(db_path, "messages") == 6


def test_directory_sweep_preserves_single_source_directory_behavior(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    source = _copy_fixture(FIXTURES / "chatgpt" / "minimal", tmp_path / "chatgpt-export")
    (source / "ignored.txt").write_text("not part of the export", encoding="utf-8")

    result = _invoke_ingest(source, db_path)

    assert result.exit_code == 0, result.stdout
    assert "provider: chatgpt" in result.stdout
    assert "source path:" in result.stdout
    assert "parent source directory:" not in result.stdout
    assert _count_rows(db_path, "sources") == 1
    rows = _source_rows(db_path)
    assert rows[0]["path_or_config"] == str(source.resolve())


def test_directory_sweep_orders_discovered_sources_by_resolved_path(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    parent = tmp_path / "exports"
    parent.mkdir()
    _copy_fixture(FIXTURES / "claude" / "minimal", parent / "z-claude-export")
    _copy_fixture(FIXTURES / "chatgpt" / "minimal", parent / "a-chatgpt-export")

    result = _invoke_ingest(parent, db_path)

    assert result.exit_code == 0, result.stdout
    rows = _source_rows(db_path)
    assert [row["provider"] for row in rows] == ["chatgpt", "claude"]
    assert [row["path_or_config"] for row in rows] == sorted(
        row["path_or_config"] for row in rows
    )


def test_directory_sweep_ignores_unsupported_files_when_supported_sources_exist(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    parent = tmp_path / "exports"
    parent.mkdir()
    _copy_fixture(FIXTURES / "chatgpt" / "minimal", parent / "chatgpt-export")
    (parent / "notes.txt").write_text("not an export", encoding="utf-8")
    (parent / "chronicle.db").write_text("private sqlite placeholder", encoding="utf-8")

    result = _invoke_ingest(parent, db_path)

    assert result.exit_code == 0, result.stdout
    assert "discovered supported sources: 1" in result.stdout
    assert "ignored unsupported paths: 2" in result.stdout
    assert _count_rows(db_path, "conversations") == 1


def test_directory_sweep_no_supported_sources_exits_nonzero(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    parent = tmp_path / "exports"
    parent.mkdir()
    (parent / "notes.txt").write_text("not an export", encoding="utf-8")

    result = _invoke_ingest(parent, db_path)

    assert result.exit_code != 0
    assert "No supported sources found in directory" in result.stderr
    assert not db_path.exists()


def test_directory_sweep_explicit_provider_ingests_only_compatible_sources(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    parent = tmp_path / "exports"
    parent.mkdir()
    _copy_fixture(FIXTURES / "chatgpt" / "minimal", parent / "a-chatgpt-export")
    _copy_fixture(FIXTURES / "claude" / "minimal", parent / "b-claude-export")

    result = _invoke_ingest(parent, db_path, provider="claude")

    assert result.exit_code == 0, result.stdout
    assert "discovered supported sources: 1" in result.stdout
    assert "skipped incompatible sources: 1" in result.stdout
    assert "source: claude" in result.stdout
    assert "source: chatgpt" not in result.stdout
    rows = _source_rows(db_path)
    assert [row["provider"] for row in rows] == ["claude"]
    assert _count_rows(db_path, "conversations") == 1


def test_directory_sweep_rerun_is_idempotent_without_duplicate_rows(
    tmp_path: Path,
) -> None:
    db_path = _db_path(tmp_path)
    parent = tmp_path / "exports"
    parent.mkdir()
    _copy_fixture(FIXTURES / "chatgpt" / "minimal", parent / "a-chatgpt-export")
    _copy_fixture(FIXTURES / "claude" / "minimal", parent / "b-claude-export")

    first = _invoke_ingest(parent, db_path)
    second = _invoke_ingest(parent, db_path)

    assert first.exit_code == 0, first.stdout
    assert second.exit_code == 0, second.stdout
    assert "total added: 0  updated: 0  skipped: 2" in second.stdout
    assert _count_rows(db_path, "sources") == 2
    assert _count_rows(db_path, "conversations") == 2
    assert _count_rows(db_path, "messages") == 4
    assert _count_rows(db_path, "ingest_runs") == 4


def test_stats_remains_coherent_after_directory_sweep(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    parent = tmp_path / "exports"
    parent.mkdir()
    _copy_fixture(FIXTURES / "chatgpt" / "minimal", parent / "a-chatgpt-export")
    _copy_fixture(FIXTURES / "claude" / "minimal", parent / "b-claude-export")
    ingest_result = _invoke_ingest(parent, db_path)
    assert ingest_result.exit_code == 0, ingest_result.stdout

    result = runner.invoke(app, ["stats", "--db-path", str(db_path)])

    assert result.exit_code == 0, result.stdout
    assert "total conversations: 2" in result.stdout
    assert "total messages: 4" in result.stdout
    assert "chatgpt" in result.stdout
    assert "claude" in result.stdout
    assert "Recent ingest runs" in result.stdout


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
