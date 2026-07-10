from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime

import pytest

import chat_chronicle.db as db_module
from chat_chronicle.db import (
    begin_ingest_run,
    connect,
    default_db_path,
    finish_ingest_run,
    get_user_version,
    initialize_database,
    rebuild_fts,
    record_ingest_failure,
    upsert_conversation,
)
from chat_chronicle.models import Conversation, IngestRunSummary, Message

EXPECTED_TABLES = {
    "sources",
    "ingest_runs",
    "conversations",
    "messages",
    "enrichments",
    "knowledge_items",
    "chat_fts",
}


def _conversation(body: str = "hello chronicle", provider_conv_id: str = "conv-1") -> Conversation:
    return Conversation(
        provider="chatgpt",
        provider_conv_id=provider_conv_id,
        title="Synthetic chat",
        url="https://chatgpt.com/c/conv-1",
        created_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, 12, 5, tzinfo=UTC),
        messages=[
            Message(
                role="user",
                created_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
                body=body,
                seq=0,
            ),
            Message(role="assistant", body="synthetic reply", seq=1),
        ],
    )


def test_initialize_database_creates_expected_tables(tmp_path) -> None:
    db_path = tmp_path / "chronicle.db"

    resolved = initialize_database(db_path)

    assert resolved == db_path
    assert db_path.exists()
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'virtual table')"
        ).fetchall()
        table_names = {row["name"] for row in rows}
        assert EXPECTED_TABLES <= table_names


def test_initialize_database_is_idempotent_and_sets_user_version(tmp_path) -> None:
    db_path = tmp_path / "chronicle.db"

    initialize_database(db_path)
    initialize_database(db_path)

    with connect(db_path) as conn:
        assert get_user_version(conn) == 1


def test_default_db_path_honors_environment(monkeypatch, tmp_path) -> None:
    expected = tmp_path / "configured.db"
    monkeypatch.setenv("CHAT_CHRONICLE_DB", str(expected))

    assert default_db_path() == expected
    assert not expected.exists()


def test_default_db_path_uses_project_local_chronicle_dir(monkeypatch) -> None:
    monkeypatch.delenv("CHAT_CHRONICLE_DB", raising=False)
    repo_root = db_module.Path(db_module.__file__).resolve().parents[2]

    assert default_db_path() == repo_root / ".chronicle" / "chronicle.db"


def test_upsert_conversation_adds_new_conversation_and_messages(tmp_path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        result = upsert_conversation(conn, None, _conversation())

        assert result.status == "added"
        assert result.conversation_id > 0
        message_count = conn.execute(
            "SELECT count(*) FROM messages WHERE conversation_id = ?",
            (result.conversation_id,),
        ).fetchone()[0]
        assert message_count == 2


def test_upsert_conversation_skips_unchanged_without_duplicate_messages(tmp_path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        first = upsert_conversation(conn, None, _conversation())
        second = upsert_conversation(conn, None, _conversation())

        assert second.status == "skipped"
        assert second.conversation_id == first.conversation_id
        message_count = conn.execute("SELECT count(*) FROM messages").fetchone()[0]
        assert message_count == 2


def test_upsert_conversation_updates_changed_content_and_replaces_messages(tmp_path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        first = upsert_conversation(conn, None, _conversation("original body"))
        old_hash = conn.execute(
            "SELECT content_hash FROM conversations WHERE id = ?",
            (first.conversation_id,),
        ).fetchone()[0]

        changed = upsert_conversation(conn, None, _conversation("changed body"))

        assert changed.status == "updated"
        assert changed.conversation_id == first.conversation_id
        rows = conn.execute(
            "SELECT body FROM messages WHERE conversation_id = ? ORDER BY seq",
            (first.conversation_id,),
        ).fetchall()
        assert [row["body"] for row in rows] == ["changed body", "synthetic reply"]
        new_hash = conn.execute(
            "SELECT content_hash FROM conversations WHERE id = ?",
            (first.conversation_id,),
        ).fetchone()[0]
        assert new_hash != old_hash


def test_conversations_enforce_unique_provider_identity(tmp_path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        upsert_conversation(conn, None, _conversation())
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO conversations (
                    provider, provider_conv_id, message_count, content_hash
                )
                VALUES (?, ?, ?, ?)
                """,
                ("chatgpt", "conv-1", 0, "manual-hash"),
            )


def test_ingest_run_finish_records_counts_and_errors(tmp_path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        run_id = begin_ingest_run(conn, None)
        summary = IngestRunSummary(
            conversations_seen=3,
            added=1,
            updated=1,
            skipped=1,
            errors=[{"record": "bad-row", "error": "missing id"}],
        )

        finish_ingest_run(conn, run_id, summary)

        row = conn.execute("SELECT * FROM ingest_runs WHERE id = ?", (run_id,)).fetchone()
        assert row["status"] == "success"
        assert row["conversations_seen"] == 3
        assert row["added"] == 1
        assert row["updated"] == 1
        assert row["skipped"] == 1
        assert json.loads(row["errors_json"]) == [{"error": "missing id", "record": "bad-row"}]


def test_record_ingest_failure_keeps_run_row_and_records_errors(tmp_path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        run_id = begin_ingest_run(conn, None)

        record_ingest_failure(conn, run_id, [{"record": "conv-2", "error": "invalid json"}])

        row = conn.execute("SELECT * FROM ingest_runs WHERE id = ?", (run_id,)).fetchone()
        assert row is not None
        assert row["status"] == "failed"
        assert json.loads(row["errors_json"]) == [{"error": "invalid json", "record": "conv-2"}]


def test_rebuild_fts_indexes_message_body(tmp_path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        upsert_conversation(conn, None, _conversation("needleterm lives in this body"))

        rebuild_fts(conn)

        rows = conn.execute(
            "SELECT rowid FROM chat_fts WHERE chat_fts MATCH ?",
            ("needleterm",),
        ).fetchall()
        assert len(rows) == 1
