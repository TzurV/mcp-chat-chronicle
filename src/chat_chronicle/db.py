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

CURRENT_SCHEMA_VERSION = 2
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
        _create_schema_v2(conn)
        conn.execute(f"PRAGMA user_version = {CURRENT_SCHEMA_VERSION}")
        conn.commit()
        return

    if version < 2:
        _migrate_v2(conn)


def _create_schema_v2(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY,
            source_type TEXT NOT NULL CHECK(source_type IN
                ('official_export','local_store','manual_folder','experimental_cache','manual_entry')),
            provider TEXT NOT NULL,
            path_or_config TEXT,
            enabled INTEGER NOT NULL DEFAULT 1,
            last_seen_at TEXT,
            last_ingested_at TEXT
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            root_path TEXT,
            created_at TEXT
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
            project_id INTEGER REFERENCES projects(id),
            provider TEXT NOT NULL,
            provider_conv_id TEXT NOT NULL,
            title TEXT,
            url TEXT,
            origin_path TEXT,
            resume_hint TEXT,
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
        CREATE UNIQUE INDEX IF NOT EXISTS idx_sources_provider_path_unique
            ON sources(provider, path_or_config)
            WHERE path_or_config IS NOT NULL;
        """
    )


def _migrate_v2(conn: sqlite3.Connection) -> None:
    """Migrate an existing v1 database to the v2 link-back schema."""
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        conn.execute("BEGIN")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                root_path TEXT,
                created_at TEXT
            )
            """
        )
        _dedupe_sources_for_unique_index(conn)
        _rebuild_sources_for_v2_check(conn)
        _add_column_if_missing(
            conn,
            "conversations",
            "project_id",
            "INTEGER REFERENCES projects(id)",
        )
        _add_column_if_missing(conn, "conversations", "origin_path", "TEXT")
        _add_column_if_missing(conn, "conversations", "resume_hint", "TEXT")
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_sources_provider_path_unique
            ON sources(provider, path_or_config)
            WHERE path_or_config IS NOT NULL
            """
        )
        conn.execute("PRAGMA user_version = 2")
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")

    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        msg = f"v2 migration left foreign key violations: {violations!r}"
        raise RuntimeError(msg)


def _dedupe_sources_for_unique_index(conn: sqlite3.Connection) -> None:
    duplicates = conn.execute(
        """
        SELECT provider, path_or_config, min(id) AS keep_id
        FROM sources
        WHERE path_or_config IS NOT NULL
        GROUP BY provider, path_or_config
        HAVING count(*) > 1
        ORDER BY keep_id
        """
    ).fetchall()
    for duplicate in duplicates:
        provider = duplicate["provider"]
        path_or_config = duplicate["path_or_config"]
        keep_id = int(duplicate["keep_id"])
        ids = [
            int(row["id"])
            for row in conn.execute(
                """
                SELECT id
                FROM sources
                WHERE provider = ? AND path_or_config = ?
                ORDER BY id
                """,
                (provider, path_or_config),
            ).fetchall()
        ]
        duplicate_ids = [source_id for source_id in ids if source_id != keep_id]
        if not duplicate_ids:
            continue

        best = conn.execute(
            """
            SELECT
                max(enabled) AS enabled,
                max(last_seen_at) AS last_seen_at,
                max(last_ingested_at) AS last_ingested_at
            FROM sources
            WHERE id IN ({})
            """.format(",".join("?" for _ in ids)),
            ids,
        ).fetchone()
        conn.execute(
            """
            UPDATE sources
            SET enabled = ?,
                last_seen_at = ?,
                last_ingested_at = ?
            WHERE id = ?
            """,
            (
                int(best["enabled"] or 0),
                best["last_seen_at"],
                best["last_ingested_at"],
                keep_id,
            ),
        )
        conn.executemany(
            "UPDATE conversations SET source_id = ? WHERE source_id = ?",
            [(keep_id, source_id) for source_id in duplicate_ids],
        )
        conn.executemany(
            "UPDATE ingest_runs SET source_id = ? WHERE source_id = ?",
            [(keep_id, source_id) for source_id in duplicate_ids],
        )
        conn.execute(
            "DELETE FROM sources WHERE id IN ({})".format(
                ",".join("?" for _ in duplicate_ids)
            ),
            duplicate_ids,
        )


def _rebuild_sources_for_v2_check(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE sources_v2 (
            id INTEGER PRIMARY KEY,
            source_type TEXT NOT NULL CHECK(source_type IN
                ('official_export','local_store','manual_folder','experimental_cache','manual_entry')),
            provider TEXT NOT NULL,
            path_or_config TEXT,
            enabled INTEGER NOT NULL DEFAULT 1,
            last_seen_at TEXT,
            last_ingested_at TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO sources_v2 (
            id, source_type, provider, path_or_config, enabled, last_seen_at, last_ingested_at
        )
        SELECT id, source_type, provider, path_or_config, enabled, last_seen_at, last_ingested_at
        FROM sources
        ORDER BY id
        """
    )
    conn.execute("DROP TABLE sources")
    conn.execute("ALTER TABLE sources_v2 RENAME TO sources")


def _add_column_if_missing(
    conn: sqlite3.Connection,
    table: str,
    column: str,
    definition: str,
) -> None:
    columns = {
        row["name"]
        for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


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
                    source_id, project_id, provider, provider_conv_id, title, url,
                    origin_path, resume_hint,
                    created_at, updated_at, message_count, content_hash
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                _conversation_values(source_id, conversation, content_hash),
            )
            conversation_id = int(cursor.lastrowid)
            _insert_messages(conn, conversation_id, conversation.messages)
            return UpsertResult(conversation_id=conversation_id, status="added")

        conversation_id = int(existing["id"])
        if existing["content_hash"] == content_hash:
            _update_conversation_metadata(
                conn, conversation_id, source_id, conversation, content_hash
            )
            return UpsertResult(conversation_id=conversation_id, status="skipped")

        _update_conversation_metadata(conn, conversation_id, source_id, conversation, content_hash)
        conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        _insert_messages(conn, conversation_id, conversation.messages)
        return UpsertResult(conversation_id=conversation_id, status="updated")


def _conversation_values(
    source_id: int | None,
    conversation: Conversation,
    content_hash: str,
) -> tuple[
    int | None,
    int | None,
    str,
    str,
    str | None,
    str | None,
    str | None,
    str | None,
    str | None,
    str | None,
    int,
    str,
]:
    return (
        source_id,
        conversation.project_id,
        conversation.provider,
        conversation.provider_conv_id,
        conversation.title,
        conversation.url,
        conversation.origin_path,
        conversation.resume_hint,
        _datetime_to_iso(conversation.created_at),
        _datetime_to_iso(conversation.updated_at),
        len(conversation.messages),
        content_hash,
    )


def _update_conversation_metadata(
    conn: sqlite3.Connection,
    conversation_id: int,
    source_id: int | None,
    conversation: Conversation,
    content_hash: str,
) -> None:
    conn.execute(
        """
        UPDATE conversations
        SET source_id = ?,
            project_id = ?,
            provider = ?,
            provider_conv_id = ?,
            title = ?,
            url = ?,
            origin_path = ?,
            resume_hint = ?,
            created_at = ?,
            updated_at = ?,
            message_count = ?,
            content_hash = ?
        WHERE id = ?
        """,
        (*_conversation_values(source_id, conversation, content_hash), conversation_id),
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


def get_or_create_source(
    conn: sqlite3.Connection,
    *,
    source_type: str,
    provider: str,
    path_or_config: str,
) -> int:
    """Create or reuse a source row for a provider and absolute source path."""
    now = _utc_now_iso()
    with conn:
        existing = conn.execute(
            """
            SELECT id
            FROM sources
            WHERE provider = ? AND path_or_config = ?
            ORDER BY id
            LIMIT 1
            """,
            (provider, path_or_config),
        ).fetchone()
        if existing is not None:
            source_id = int(existing["id"])
            conn.execute(
                """
                UPDATE sources
                SET source_type = ?,
                    enabled = 1,
                    last_seen_at = ?
                WHERE id = ?
                """,
                (source_type, now, source_id),
            )
            return source_id

        cursor = conn.execute(
            """
            INSERT INTO sources (
                source_type, provider, path_or_config, enabled, last_seen_at
            )
            VALUES (?, ?, ?, 1, ?)
            """,
            (source_type, provider, path_or_config, now),
        )
        return int(cursor.lastrowid)


def get_or_create_project(
    conn: sqlite3.Connection,
    *,
    name: str,
    root_path: str | None = None,
) -> int:
    """Create or reuse a project row by stable project name."""
    now = _utc_now_iso()
    with conn:
        existing = conn.execute(
            """
            SELECT id, root_path
            FROM projects
            WHERE name = ?
            """,
            (name,),
        ).fetchone()
        if existing is not None:
            project_id = int(existing["id"])
            if root_path and existing["root_path"] != root_path:
                conn.execute(
                    "UPDATE projects SET root_path = ? WHERE id = ?",
                    (root_path, project_id),
                )
            return project_id

        cursor = conn.execute(
            """
            INSERT INTO projects (name, root_path, created_at)
            VALUES (?, ?, ?)
            """,
            (name, root_path, now),
        )
        return int(cursor.lastrowid)


def mark_source_ingested(conn: sqlite3.Connection, source_id: int) -> None:
    """Record the latest successful ingest attempt time for a source row."""
    now = _utc_now_iso()
    with conn:
        conn.execute(
            "UPDATE sources SET last_seen_at = ?, last_ingested_at = ? WHERE id = ?",
            (now, now, source_id),
        )


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
                ) AS knowledge_tags,
                p.name AS project_name
            FROM conversations AS c
            LEFT JOIN enrichments AS e ON e.conversation_id = c.id
            LEFT JOIN projects AS p ON p.id = c.project_id
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
                        for part in (
                            row["enrichment_tags"],
                            row["knowledge_tags"],
                            row["project_name"],
                        )
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
