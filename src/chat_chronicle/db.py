"""SQLite persistence for Chat Chronicle."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from chat_chronicle.models import Conversation, IngestRunSummary, Message, UpsertResult

CURRENT_SCHEMA_VERSION = 1
DB_ENV_VAR = "CHAT_CHRONICLE_DB"


def default_db_path() -> Path:
    """Return the configured or project-local SQLite database path."""
    env_path = os.environ.get(DB_ENV_VAR)
    if env_path:
        return Path(env_path).expanduser().resolve()

    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / ".chronicle" / "chronicle.db"


def _resolve_db_path(db_path: Path | str | None = None) -> Path:
    if db_path is None:
        return default_db_path()
    path = Path(db_path).expanduser()
    if _is_in_memory_path(path):
        return path
    return path.resolve()


def _is_in_memory_path(path: Path) -> bool:
    return str(path) == ":memory:"


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a SQLite connection, enable FK checks, and run migrations."""
    resolved = _resolve_db_path(db_path)
    if not _is_in_memory_path(resolved):
        resolved.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(resolved))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrate(conn)
    return conn


def initialize_database(db_path: Path | str | None = None) -> Path:
    """Create or migrate a SQLite database and return the resolved path."""
    resolved = _resolve_db_path(db_path)
    with connect(resolved) as conn:
        migrate(conn)
    return resolved


def get_user_version(conn: sqlite3.Connection) -> int:
    row = conn.execute("PRAGMA user_version").fetchone()
    return int(row[0])


def migrate(conn: sqlite3.Connection) -> None:
    """Apply all known migrations to the connection."""
    conn.execute("PRAGMA foreign_keys = ON")
    version = get_user_version(conn)
    if version > CURRENT_SCHEMA_VERSION:
        msg = f"Database schema version {version} is newer than supported {CURRENT_SCHEMA_VERSION}"
        raise RuntimeError(msg)

    if version < 1:
        _migrate_v1(conn)
        conn.execute(f"PRAGMA user_version = {CURRENT_SCHEMA_VERSION}")
        conn.commit()


def _migrate_v1(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY,
            source_type TEXT NOT NULL CHECK(source_type IN
                ('official_export','local_store','manual_folder','experimental_cache')),
            provider TEXT NOT NULL,
            path_or_config TEXT,
            enabled INTEGER NOT NULL DEFAULT 1,
            last_seen_at TEXT,
            last_ingested_at TEXT
        );

        CREATE TABLE IF NOT EXISTS ingest_runs (
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

        CREATE TABLE IF NOT EXISTS conversations (
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

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role TEXT,
            created_at TEXT,
            body TEXT,
            seq INTEGER
        );

        CREATE TABLE IF NOT EXISTS enrichments (
            conversation_id INTEGER PRIMARY KEY REFERENCES conversations(id) ON DELETE CASCADE,
            summary TEXT,
            tags_json TEXT,
            language TEXT,
            model_used TEXT,
            enriched_at TEXT
        );

        CREATE TABLE IF NOT EXISTS knowledge_items (
            id INTEGER PRIMARY KEY,
            conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
            kind TEXT CHECK(kind IN ('decision','solution','open_question')),
            statement TEXT NOT NULL,
            context TEXT,
            tags_json TEXT,
            model_used TEXT,
            extracted_at TEXT
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS chat_fts USING fts5(
            title,
            summary,
            tags,
            body,
            content='',
            tokenize='porter unicode61'
        );

        CREATE INDEX IF NOT EXISTS idx_messages_conversation_seq
            ON messages(conversation_id, seq);
        CREATE INDEX IF NOT EXISTS idx_conversations_provider_updated
            ON conversations(provider, updated_at);
        CREATE INDEX IF NOT EXISTS idx_ingest_runs_source_started
            ON ingest_runs(source_id, started_at);
        """
    )


def _utc_now_iso() -> str:
    return _datetime_to_iso(datetime.now(UTC))


def _datetime_to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    else:
        value = value.astimezone(UTC)
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def upsert_conversation(
    conn: sqlite3.Connection,
    source_id: int | None,
    conversation: Conversation,
) -> UpsertResult:
    """Insert, update, or skip a normalized conversation by provider identity."""
    content_hash = conversation.content_hash_value()
    with conn:
        existing = conn.execute(
            """
            SELECT id, content_hash
            FROM conversations
            WHERE provider = ? AND provider_conv_id = ?
            """,
            (conversation.provider, conversation.provider_conv_id),
        ).fetchone()

        if existing is None:
            cursor = conn.execute(
                """
                INSERT INTO conversations (
                    source_id, provider, provider_conv_id, title, url,
                    created_at, updated_at, message_count, content_hash
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                _conversation_values(source_id, conversation, content_hash),
            )
            conversation_id = int(cursor.lastrowid)
            _insert_messages(conn, conversation_id, conversation.messages)
            return UpsertResult(conversation_id=conversation_id, status="added")

        conversation_id = int(existing["id"])
        if existing["content_hash"] == content_hash:
            return UpsertResult(conversation_id=conversation_id, status="skipped")

        conn.execute(
            """
            UPDATE conversations
            SET source_id = ?,
                provider = ?,
                provider_conv_id = ?,
                title = ?,
                url = ?,
                created_at = ?,
                updated_at = ?,
                message_count = ?,
                content_hash = ?
            WHERE id = ?
            """,
            (*_conversation_values(source_id, conversation, content_hash), conversation_id),
        )
        conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        _insert_messages(conn, conversation_id, conversation.messages)
        return UpsertResult(conversation_id=conversation_id, status="updated")


def _conversation_values(
    source_id: int | None,
    conversation: Conversation,
    content_hash: str,
) -> tuple[int | None, str, str, str | None, str | None, str | None, str | None, int, str]:
    return (
        source_id,
        conversation.provider,
        conversation.provider_conv_id,
        conversation.title,
        conversation.url,
        _datetime_to_iso(conversation.created_at),
        _datetime_to_iso(conversation.updated_at),
        len(conversation.messages),
        content_hash,
    )


def _insert_messages(
    conn: sqlite3.Connection,
    conversation_id: int,
    messages: list[Message],
) -> None:
    conn.executemany(
        """
        INSERT INTO messages (conversation_id, role, created_at, body, seq)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                conversation_id,
                message.role,
                _datetime_to_iso(message.created_at),
                message.body,
                message.seq,
            )
            for message in sorted(messages, key=lambda item: item.seq)
        ],
    )


def begin_ingest_run(conn: sqlite3.Connection, source_id: int | None) -> int:
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO ingest_runs (
                source_id, started_at, status,
                conversations_seen, added, updated, skipped, errors_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (source_id, _utc_now_iso(), "running", 0, 0, 0, 0, _json_dumps([])),
        )
        return int(cursor.lastrowid)


def finish_ingest_run(
    conn: sqlite3.Connection,
    run_id: int,
    summary: IngestRunSummary,
    status: str = "success",
) -> None:
    with conn:
        conn.execute(
            """
            UPDATE ingest_runs
            SET finished_at = ?,
                status = ?,
                conversations_seen = ?,
                added = ?,
                updated = ?,
                skipped = ?,
                errors_json = ?
            WHERE id = ?
            """,
            (
                _utc_now_iso(),
                status,
                summary.conversations_seen,
                summary.added,
                summary.updated,
                summary.skipped,
                _json_dumps(summary.errors),
                run_id,
            ),
        )


def record_ingest_failure(
    conn: sqlite3.Connection,
    run_id: int,
    errors: list[dict[str, Any]],
    status: str = "failed",
) -> None:
    with conn:
        conn.execute(
            """
            UPDATE ingest_runs
            SET finished_at = ?,
                status = ?,
                errors_json = ?
            WHERE id = ?
            """,
            (_utc_now_iso(), status, _json_dumps(errors), run_id),
        )


def rebuild_fts(conn: sqlite3.Connection) -> None:
    """Rebuild the contentless FTS index from current normalized rows."""
    with conn:
        _clear_fts(conn)
        rows = conn.execute(
            """
            SELECT
                c.id AS conversation_id,
                c.title AS title,
                e.summary AS summary,
                e.tags_json AS enrichment_tags,
                (
                    SELECT group_concat(m.body, char(10))
                    FROM messages AS m
                    WHERE m.conversation_id = c.id
                    ORDER BY m.seq
                ) AS message_body,
                (
                    SELECT group_concat(
                        coalesce(k.statement, '') || ' ' || coalesce(k.context, ''),
                        char(10)
                    )
                    FROM knowledge_items AS k
                    WHERE k.conversation_id = c.id
                ) AS knowledge_body,
                (
                    SELECT group_concat(coalesce(k.tags_json, ''), ' ')
                    FROM knowledge_items AS k
                    WHERE k.conversation_id = c.id
                ) AS knowledge_tags
            FROM conversations AS c
            LEFT JOIN enrichments AS e ON e.conversation_id = c.id
            ORDER BY c.id
            """
        ).fetchall()
        conn.executemany(
            """
            INSERT INTO chat_fts(rowid, title, summary, tags, body)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    int(row["conversation_id"]),
                    row["title"] or "",
                    row["summary"] or "",
                    " ".join(
                        part
                        for part in (row["enrichment_tags"], row["knowledge_tags"])
                        if part
                    ),
                    "\n".join(
                        part
                        for part in (row["message_body"], row["knowledge_body"])
                        if part
                    ),
                )
                for row in rows
            ],
        )


def _clear_fts(conn: sqlite3.Connection) -> None:
    try:
        conn.execute("DELETE FROM chat_fts")
    except sqlite3.OperationalError:
        conn.execute("INSERT INTO chat_fts(chat_fts) VALUES ('delete-all')")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m chat_chronicle.db",
        description="Chat Chronicle SQLite database utilities.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("path", help="Print the resolved default database path.")

    init_parser = subparsers.add_parser("init", help="Create or migrate a database.")
    init_parser.add_argument("--db-path", type=Path, default=None, help="SQLite database path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "path":
        print(default_db_path())
        return 0

    if args.command == "init":
        resolved = initialize_database(args.db_path)
        with connect(resolved) as conn:
            version = get_user_version(conn)
        print(f"database: {resolved}")
        print(f"user_version: {version}")
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
