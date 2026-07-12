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
    "projects",
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


def _create_v1_database(db_path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE sources (
                id INTEGER PRIMARY KEY,
                source_type TEXT NOT NULL CHECK(source_type IN
                    ('official_export','local_store','manual_folder','experimental_cache')),
                provider TEXT NOT NULL,
                path_or_config TEXT,
                enabled INTEGER NOT NULL DEFAULT 1,
                last_seen_at TEXT,
                last_ingested_at TEXT
            );

            CREATE TABLE ingest_runs (
                id INTEGER PRIMARY KEY,
                source_id INTEGER REFERENCES sources(id),
                started_at TEXT NOT NULL,
                finished_at TEXT,
                status TEXT,
                conversations_seen INTEGER,
                added INTEGER,
                updated INTEGER,
                skipped INTEGER,
                errors_json TEXT
            );

            CREATE TABLE conversations (
                id INTEGER PRIMARY KEY,
                source_id INTEGER REFERENCES sources(id),
                provider TEXT NOT NULL,
                provider_conv_id TEXT NOT NULL,
                title TEXT,
                url TEXT,
                created_at TEXT,
                updated_at TEXT,
                message_count INTEGER,
                content_hash TEXT NOT NULL,
                UNIQUE(provider, provider_conv_id)
            );

            CREATE TABLE messages (
                id INTEGER PRIMARY KEY,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role TEXT,
                created_at TEXT,
                body TEXT,
                seq INTEGER
            );

            CREATE TABLE enrichments (
                conversation_id INTEGER PRIMARY KEY REFERENCES conversations(id) ON DELETE CASCADE,
                summary TEXT,
                tags_json TEXT,
                language TEXT,
                model_used TEXT,
                enriched_at TEXT
            );

            CREATE TABLE knowledge_items (
                id INTEGER PRIMARY KEY,
                conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
                kind TEXT CHECK(kind IN ('decision','solution','open_question')),
                statement TEXT NOT NULL,
                context TEXT,
                tags_json TEXT,
                model_used TEXT,
                extracted_at TEXT
            );

            CREATE VIRTUAL TABLE chat_fts USING fts5(
                title,
                summary,
                tags,
                body,
                content='',
                tokenize='porter unicode61'
            );

            CREATE INDEX idx_messages_conversation_seq
                ON messages(conversation_id, seq);
            CREATE INDEX idx_conversations_provider_updated
                ON conversations(provider, updated_at);
            CREATE INDEX idx_ingest_runs_source_started
                ON ingest_runs(source_id, started_at);
            PRAGMA user_version = 1;
            """
        )
        conn.commit()
    finally:
        conn.close()


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


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
        assert get_user_version(conn) == 2


def test_fresh_database_creates_v2_schema(tmp_path) -> None:
    db_path = tmp_path / "chronicle.db"

    initialize_database(db_path)

    with connect(db_path) as conn:
        assert get_user_version(conn) == 2
        assert "projects" in {
            row["name"] for row in conn.execute("SELECT name FROM sqlite_master")
        }
        assert {"project_id", "origin_path", "resume_hint"} <= _table_columns(
            conn, "conversations"
        )
        conn.execute(
            """
            INSERT INTO sources (source_type, provider, path_or_config)
            VALUES ('manual_entry', 'manual', NULL)
            """
        )


def test_v1_database_migrates_to_v2_and_preserves_rows(tmp_path) -> None:
    db_path = tmp_path / "chronicle.db"
    _create_v1_database(db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(
            """
            INSERT INTO sources (
                id, source_type, provider, path_or_config, enabled, last_seen_at, last_ingested_at
            )
            VALUES
                (1, 'official_export', 'chatgpt', 'C:/exports/chatgpt.json', 0,
                 '2026-01-01T00:00:00Z', NULL),
                (2, 'official_export', 'chatgpt', 'C:/exports/chatgpt.json', 1,
                 '2026-01-02T00:00:00Z', '2026-01-02T00:05:00Z'),
                (3, 'local_store', 'openai_codex', NULL, 1, NULL, NULL);

            INSERT INTO conversations (
                id, source_id, provider, provider_conv_id, title, url,
                created_at, updated_at, message_count, content_hash
            )
            VALUES (
                10, 2, 'chatgpt', 'conv-1', 'Legacy chat', 'https://chatgpt.com/c/conv-1',
                '2026-01-01T00:00:00Z', '2026-01-01T00:05:00Z', 1, 'legacy-hash'
            );

            INSERT INTO messages (id, conversation_id, role, created_at, body, seq)
            VALUES (20, 10, 'user', '2026-01-01T00:00:00Z', 'legacy body', 0);

            INSERT INTO ingest_runs (
                id, source_id, started_at, finished_at, status,
                conversations_seen, added, updated, skipped, errors_json
            )
            VALUES (
                30, 2, '2026-01-02T00:00:00Z', '2026-01-02T00:06:00Z', 'success',
                1, 1, 0, 0, '[]'
            );
            """
        )
        conn.commit()
    finally:
        conn.close()

    with connect(db_path) as conn:
        assert get_user_version(conn) == 2
        assert {"project_id", "origin_path", "resume_hint"} <= _table_columns(
            conn, "conversations"
        )
        assert conn.execute("SELECT count(*) FROM projects").fetchone()[0] == 0
        assert conn.execute("SELECT count(*) FROM conversations").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM messages").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM ingest_runs").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM sources").fetchone()[0] == 2

        source = conn.execute(
            "SELECT enabled, last_seen_at, last_ingested_at FROM sources WHERE id = 1"
        ).fetchone()
        assert dict(source) == {
            "enabled": 1,
            "last_seen_at": "2026-01-02T00:00:00Z",
            "last_ingested_at": "2026-01-02T00:05:00Z",
        }
        assert conn.execute(
            "SELECT source_id FROM conversations WHERE id = 10"
        ).fetchone()[0] == 1
        assert conn.execute("SELECT source_id FROM ingest_runs WHERE id = 30").fetchone()[0] == 1
        conn.execute(
            """
            INSERT INTO sources (source_type, provider, path_or_config)
            VALUES ('manual_entry', 'manual', 'manual://one')
            """
        )


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


def test_upsert_conversation_persists_and_refreshes_link_back_metadata(tmp_path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        conn.execute(
            """
            INSERT INTO sources (id, source_type, provider, path_or_config)
            VALUES (1, 'local_store', 'openai_codex', 'C:/exports/source.jsonl')
            """
        )
        conn.execute(
            """
            INSERT INTO sources (id, source_type, provider, path_or_config)
            VALUES (2, 'local_store', 'openai_codex', 'C:/exports/renamed.jsonl')
            """
        )
        project_id = conn.execute(
            """
            INSERT INTO projects (name, root_path, created_at)
            VALUES ('Synthetic Project', 'C:/work/synthetic', '2026-01-01T00:00:00Z')
            """
        ).lastrowid
        conversation = _conversation()
        conversation.project_id = int(project_id)
        conversation.origin_path = "C:/exports/source.jsonl"
        conversation.resume_hint = "synthetic resume"

        first = upsert_conversation(conn, 1, conversation)
        row = conn.execute(
            """
            SELECT source_id, project_id, origin_path, resume_hint
            FROM conversations
            WHERE id = ?
            """,
            (first.conversation_id,),
        ).fetchone()
        assert dict(row) == {
            "source_id": 1,
            "project_id": int(project_id),
            "origin_path": "C:/exports/source.jsonl",
            "resume_hint": "synthetic resume",
        }

        refreshed = conversation.model_copy(
            update={
                "title": "Retitled without content change",
                "origin_path": "C:/exports/renamed.jsonl",
                "resume_hint": None,
            }
        )
        second = upsert_conversation(conn, 2, refreshed)

        assert second.status == "skipped"
        row = conn.execute(
            """
            SELECT source_id, title, origin_path, resume_hint
            FROM conversations
            WHERE id = ?
            """,
            (first.conversation_id,),
        ).fetchone()
        assert dict(row) == {
            "source_id": 2,
            "title": "Retitled without content change",
            "origin_path": "C:/exports/renamed.jsonl",
            "resume_hint": None,
        }
        assert conn.execute("SELECT count(*) FROM messages").fetchone()[0] == 2


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


def test_sources_enforce_unique_provider_path_when_path_is_not_null(tmp_path) -> None:
    with connect(tmp_path / "chronicle.db") as conn:
        conn.execute(
            """
            INSERT INTO sources (source_type, provider, path_or_config)
            VALUES ('official_export', 'chatgpt', 'C:/exports/chatgpt.json')
            """
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO sources (source_type, provider, path_or_config)
                VALUES ('official_export', 'chatgpt', 'C:/exports/chatgpt.json')
                """
            )

        conn.execute(
            """
            INSERT INTO sources (source_type, provider, path_or_config)
            VALUES ('manual_entry', 'chatgpt', NULL)
            """
        )
        conn.execute(
            """
            INSERT INTO sources (source_type, provider, path_or_config)
            VALUES ('manual_entry', 'chatgpt', NULL)
            """
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
