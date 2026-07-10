# WP-1.1 Completion Report

## Status

ready for PM validation

## Summary

Implemented the normalized Pydantic model layer and local SQLite persistence layer for Chat Chronicle. The DB layer supports project-local path resolution, schema migration via `PRAGMA user_version`, idempotent conversation/message upserts, ingest run logging, FTS5 index rebuild/search support, and a small module-level admin command for path/init operations.

This resubmission addresses `md/handoffs/reports/WP-1.1-validation-review.md`: the default DB path now resolves to `.chronicle/chronicle.db` under the repository root instead of `%LOCALAPPDATA%`.

## Changed Files

- `.gitignore` - includes `.chronicle/` so the project-local development DB directory is ignored.
- `src/chat_chronicle/models.py` - replaces the WP-0.1 placeholder with Pydantic v2 models for `Message`, `Conversation`, `Enrichment`, `KnowledgeItem`, `UpsertResult`, and `IngestRunSummary`; includes UTC timestamp normalization and stable conversation content hashing.
- `src/chat_chronicle/db.py` - replaces the WP-0.1 placeholder with SQLite path resolution, connection handling, migrations, schema creation, ingest run helpers, idempotent upsert behavior, FTS rebuild, and `python -m chat_chronicle.db` admin commands.
- `tests/test_db.py` - adds synthetic deterministic tests for schema creation, migration idempotency, DB path behavior, upsert add/skip/update behavior, uniqueness enforcement, ingest run logging, failure recording, and FTS search.
- `md/handoffs/reports/WP-1.1-completion-report.md` - records this completion/resubmission evidence.

Existing uncommitted documentation changes were present outside the implementation scope: `README.md`, `md/master-plan.md`, `md/development-ledger.md`, `md/handoffs/WP-1.1-normalized-models-db-layer.md`, and `md/handoffs/reports/WP-1.1-validation-review.md`.

## DB Path Behavior

Implemented DB path precedence:

1. Explicit function/module-command `db_path` argument.
2. `CHAT_CHRONICLE_DB` environment variable.
3. Project-local `.chronicle/chronicle.db` under the repository root.

```powershell
poetry run python -m chat_chronicle.db path
C:\work\Github\mcp-chat-chronicle\.chronicle\chronicle.db
```

## Empty DB Initialization Evidence

```powershell
poetry run python -m chat_chronicle.db init --db-path .\.chronicle\chronicle.db
database: C:\work\Github\mcp-chat-chronicle\.chronicle\chronicle.db
user_version: 1
```

The created `.chronicle/chronicle.db` file is ignored by `.gitignore` and does not appear in `git status --short`.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| Pydantic models cover required normalized objects | pass | `src/chat_chronicle/models.py` defines `Message`, `Conversation`, `Enrichment`, `KnowledgeItem`, `UpsertResult`, `IngestRunSummary` |
| Migration creates all required tables | pass | `tests/test_db.py::test_initialize_database_creates_expected_tables`; `poetry run pytest` passed |
| DB path precedence implemented and tested | pass | `test_default_db_path_honors_environment`, `test_default_db_path_uses_project_local_chronicle_dir`; module `path` output pasted above |
| Empty DB init command works | pass | `python -m chat_chronicle.db init --db-path .\.chronicle\chronicle.db` output pasted above |
| DB path command prints without creating DB | pass | `python -m chat_chronicle.db path` output pasted above |
| Idempotent upsert added/skipped/updated behavior works | pass | `test_upsert_conversation_adds_new_conversation_and_messages`, `test_upsert_conversation_skips_unchanged_without_duplicate_messages`, `test_upsert_conversation_updates_changed_content_and_replaces_messages` |
| Ingest run logging records counts/errors_json | pass | `test_ingest_run_finish_records_counts_and_errors`, `test_record_ingest_failure_keeps_run_row_and_records_errors` |
| FTS5 table rebuild/search works | pass | `test_rebuild_fts_indexes_message_body` |
| No real DB/chat/export files committed | pass | `git status --short` shows no DB/export files; `.chronicle/` and `*.db` are ignored |
| `poetry run pytest` passes | pass | `15 passed in 1.48s` |
| `poetry run ruff check .` passes | pass | `All checks passed!` |
| `poetry run chronicle --help` still lists commands | pass | Help output lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, `open` |

## Command Evidence

```powershell
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

```powershell
poetry run python -m chat_chronicle.db path
C:\work\Github\mcp-chat-chronicle\.chronicle\chronicle.db
```

```powershell
poetry run python -m chat_chronicle.db init --db-path .\.chronicle\chronicle.db
database: C:\work\Github\mcp-chat-chronicle\.chronicle\chronicle.db
user_version: 1
```

```powershell
poetry run pytest
...............                                                          [100%]
15 passed in 1.48s
```

```powershell
poetry run ruff check .
All checks passed!
```

```powershell
poetry run chronicle --help

 Usage: chronicle [OPTIONS] COMMAND [ARGS]...

 A local-first, searchable archive of your AI conversations.

+- Options -------------------------------------------------------------------+
| --version          Show the version and exit.                               |
| --help             Show this message and exit.                              |
+-----------------------------------------------------------------------------+
+- Commands ------------------------------------------------------------------+
| ingest         Ingest a single official export file.                        |
| ingest-folder  Sweep a drop folder for export archives and ingest each one. |
| collect        Run every enabled source through its adapter.                |
| scan-local     Report, read-only, which AI-tool data stores exist on this   |
|                machine.                                                     |
| stats          Show per-source counts and the most recent ingest runs.      |
| search         Search the archive with FTS5 ranking and snippets.           |
| open           Open a result: deep link for web chats, transcript view      |
|                otherwise.                                                   |
+-----------------------------------------------------------------------------+
```

```powershell
git status --short
 M .gitignore
 M README.md
 M md/master-plan.md
 M src/chat_chronicle/db.py
 M src/chat_chronicle/models.py
?? md/development-ledger.md
?? md/handoffs/WP-1.1-normalized-models-db-layer.md
?? md/handoffs/reports/WP-1.1-completion-report.md
?? md/handoffs/reports/WP-1.1-validation-review.md
?? tests/test_db.py
```

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement importers | pass | No ChatGPT/Claude/Gemini importer code was added |
| Did not add adapter base/protocol | pass | No adapter abstraction was created |
| Did not implement search CLI behavior | pass | Existing `chronicle search` stub behavior remains unchanged |
| Did not add Docker/server DB dependencies | pass | Uses stdlib `sqlite3`; no SQLAlchemy/Alembic/DuckDB/Postgres/Docker added |
| Did not commit generated DB files or real chat data | pass | `.chronicle/chronicle.db` is ignored; tests use synthetic data only |

## Risks Or Follow-Ups

- FTS synchronization is explicit via `rebuild_fts(conn)`. Later ingest/search WPs should decide where to invoke rebuilds or whether to add trigger-based maintenance.
- `Enrichment` and `KnowledgeItem` models currently mirror DB JSON columns as `tags_json` strings. Later enrichment code may add helper constructors/serializers for list-based ergonomics while preserving DB storage as JSON text.
- Several validation commands had to be rerun outside the sandbox because this Windows workspace intermittently failed process launch with `CreateProcessAsUserW failed: 1312`, matching `md/agent-operating-notes.md`.
