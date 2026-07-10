# WP-1.1 Handoff: Normalized Models + DB Layer

## Objective
Implement the normalized Pydantic models and SQLite persistence layer for Chat Chronicle.

This work package creates the authoritative schema, migrations, idempotent conversation/message upsert behavior, ingest run logging primitives, and FTS5 table setup. It must also provide a simple way to create an empty `.db` file with all tables before real importers exist.

## Source Of Truth
Use `md/master-plan.md`, especially:

- Section 2: Core Design Rules
- Section 3: Tech Stack
- Section 5: Data Model
- Section 6: M1 / WP-1.1 Normalized models + DB layer

Also read `md/agent-operating-notes.md` before running Poetry commands.

## Required Poetry Preflight
Before running any Poetry command, from the repo root run:

```powershell
poetry env info --path
```

Expected path:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If Poetry reports any path outside this repo, stop and fix the shell before continuing. Do not install or run commands in another project's virtualenv.

## Scope
Implement:

- `src/chat_chronicle/models.py` with Pydantic v2 models for normalized conversations, messages, enrichments, knowledge items, and DB operation results.
- `src/chat_chronicle/db.py` with SQLite connection handling, path resolution, migrations, schema creation, ingest run helpers, idempotent conversation upserts, message replacement on changed conversations, and FTS rebuild/sync support.
- Tests proving schema creation, migrations, idempotency, ingest run error logging, and FTS availability.
- A small module-level DB initialization command so an executor/user can create an empty DB with tables before importers exist.

Do not implement:

- ChatGPT/Claude/Gemini importers.
- `chronicle ingest`, `chronicle stats`, `chronicle search`, or `chronicle open` behavior beyond what is necessary to keep existing CLI tests passing.
- Adapter abstraction, `AdapterProtocol`, or `adapters/base.py`.
- Docker, Postgres, server DBs, or non-SQLite storage.
- Real chat fixtures or real exported data.

## DB Location Decision
The database is a local SQLite `.db` file, not Docker. For this project, the default development DB must live under the repository directory, not under `%LOCALAPPDATA%`.

Use this DB path precedence:

1. Explicit function/command `db_path` argument.
2. Environment variable `CHAT_CHRONICLE_DB`.
3. Project-local default, when run from the repository root:
   - `C:\work\Github\mcp-chat-chronicle\.chronicle\chronicle.db`

Implementation notes:

- Create parent directories only when opening/initializing a DB for writing.
- Do not create a DB file at import time.
- Tests must use temporary DB paths under `tmp_path`, not the real user default.
- The repo `.gitignore` already ignores `*.db`; no DB file should be committed.
- The default `poetry run python -m chat_chronicle.db path` output from the repo root must be the project-local `.chronicle\chronicle.db` path unless `CHAT_CHRONICLE_DB` is set.

## Empty DB Creation Command
Add a minimal executable module command in `src/chat_chronicle/db.py`:

```powershell
poetry run python -m chat_chronicle.db init --db-path .\scratch\chronicle.db
```

Required behavior:

- Creates the parent directory if needed.
- Creates the SQLite DB file if missing.
- Applies all migrations.
- Prints the resolved DB path and schema/user_version.
- Exits successfully when run again against the same DB without changing existing rows.

Also support:

```powershell
poetry run python -m chat_chronicle.db path
```

Required behavior:

- Prints the resolved default DB path using the precedence above.
- Does not create the file.

This module command is an implementation/admin utility. Do not add a public `chronicle db` CLI command in this WP unless needed for tests; the master-plan CLI surface should remain focused on the planned commands.

## Pydantic Models
Define models with explicit, typed fields and simple validation:

- `Message`
  - `provider_message_id: str | None = None`
  - `role: str | None`
  - `created_at: datetime | None`
  - `body: str`
  - `seq: int`
- `Conversation`
  - `provider: str`
  - `provider_conv_id: str`
  - `title: str | None = None`
  - `url: str | None = None`
  - `created_at: datetime | None = None`
  - `updated_at: datetime | None = None`
  - `messages: list[Message]`
  - computed or helper-supported `content_hash`
- `Enrichment`
  - Fields matching the master-plan `enrichments` table.
- `KnowledgeItem`
  - Fields matching the master-plan `knowledge_items` table.
- `UpsertResult`
  - `conversation_id: int`
  - `status: Literal["added", "updated", "skipped"]`
- `IngestRunSummary`
  - Fields needed to update `ingest_runs`: seen, added, updated, skipped, errors.

Model rules:

- Store timestamps in SQLite as ISO8601 UTC text.
- Normalize empty message bodies only enough to support hashing consistently; do not invent importer-specific cleanup here.
- `content_hash` must be stable for identical normalized message sequences.
- Keep provider values open-set strings. Do not create a provider enum yet.

## SQLite Schema
Implement migrations using `PRAGMA user_version`.

Version 1 must create these tables from the master plan:

- `sources`
- `ingest_runs`
- `conversations`
- `messages`
- `enrichments`
- `knowledge_items`
- `chat_fts`

Schema requirements:

- Preserve the master-plan column names and constraints unless there is a concrete sqlite compatibility reason to adjust.
- `conversations` must enforce `UNIQUE(provider, provider_conv_id)`.
- `messages.conversation_id` must reference `conversations(id)`.
- Use ISO8601 text for timestamps.
- Store JSON values as text, including `errors_json` and `tags_json`.
- Enable foreign keys on each connection with `PRAGMA foreign_keys = ON`.
- Set `PRAGMA user_version = 1` after migration.

FTS requirements:

- Create `chat_fts` using FTS5 with columns `title`, `summary`, `tags`, `body`.
- Implement a rebuild helper, for example `rebuild_fts(conn)`, that clears and repopulates the index from current conversations/messages/enrichments/knowledge items.
- Tests must prove a term in an inserted message body can be found through `chat_fts`.

## DB API Requirements
Implement a small DB API in `db.py`:

- `default_db_path() -> Path`
- `connect(db_path: Path | str | None = None) -> sqlite3.Connection`
- `initialize_database(db_path: Path | str | None = None) -> Path`
- `migrate(conn: sqlite3.Connection) -> None`
- `get_user_version(conn: sqlite3.Connection) -> int`
- `upsert_conversation(conn, source_id: int | None, conversation: Conversation) -> UpsertResult`
- `begin_ingest_run(conn, source_id: int | None) -> int`
- `finish_ingest_run(conn, run_id: int, summary: IngestRunSummary, status: str = "success") -> None`
- `record_ingest_failure(conn, run_id: int, errors: list[dict], status: str = "failed") -> None`
- `rebuild_fts(conn) -> None`

Behavior requirements:

- `connect()` must run migrations before returning.
- `upsert_conversation()` must:
  - compute a stable content hash from normalized messages;
  - insert a new conversation and messages when missing;
  - skip unchanged conversations with zero message rewrites;
  - update conversation metadata and replace messages when the content hash changes;
  - return `added`, `updated`, or `skipped`.
- Ingest run helpers must write counts and `errors_json`; parse errors are data, not exceptions that abort an entire run.
- Use transactions for multi-row operations.

## Tests Required
Add focused tests under `tests/`, using synthetic in-memory data only.

Required scenarios:

- `initialize_database(tmp_path / "chronicle.db")` creates a DB file with all expected tables.
- Running initialization twice is safe and leaves `PRAGMA user_version = 1`.
- `default_db_path()` honors `CHAT_CHRONICLE_DB`.
- `upsert_conversation()` inserts a new conversation and messages with status `added`.
- Upserting the same conversation again returns `skipped` and does not duplicate messages.
- Upserting changed message content returns `updated`, replaces messages, and updates `content_hash`.
- `conversations` enforces `UNIQUE(provider, provider_conv_id)`.
- `begin_ingest_run()` / `finish_ingest_run()` records counts and `errors_json`.
- `record_ingest_failure()` records errors without deleting already-created run rows.
- `rebuild_fts()` indexes message body text and supports a simple `MATCH` query.
- Existing WP-0.1 CLI tests still pass.

## Acceptance Criteria
WP-1.1 is complete only when all of these are true:

- Pydantic models exist and cover normalized conversations/messages plus enrichment/knowledge placeholders.
- SQLite migration creates every table from the master-plan schema.
- DB path precedence is implemented and tested.
- Empty DB initialization works via `poetry run python -m chat_chronicle.db init --db-path <path>`.
- `poetry run python -m chat_chronicle.db path` prints the resolved default DB path without creating the DB.
- Idempotent upsert behavior is implemented and tested: added, skipped, updated.
- Ingest run logging records counts and JSON errors.
- FTS5 table exists and can be rebuilt/searched in tests.
- Re-running tests does not create or commit real DB files outside temp paths.
- `poetry run pytest` passes.
- `poetry run ruff check .` passes.
- `poetry run chronicle --help` still lists all required WP-0.1 commands.

## Evidence Required
The executor must return a detailed completion report. Missing evidence means the WP is not accepted, even if the implementation appears correct.

The completion report must be written to:

```text
md/handoffs/reports/WP-1.1-completion-report.md
```

The report must include:

- Changed-files summary.
- Exact command output or concise pasted result for:
  - `poetry env info --path`
  - `poetry run pytest`
  - `poetry run ruff check .`
  - `poetry run chronicle --help`
  - `poetry run python -m chat_chronicle.db path`
  - `poetry run python -m chat_chronicle.db init --db-path <temp-or-scratch-path>`
- Confirmation that any scratch DB created for evidence is git-ignored and not committed.
- Explicit checklist mapping each acceptance criterion to `pass`, `fail`, or `not attempted`.

## Technical Guardrails
- Keep all DB logic in `src/chat_chronicle/db.py`; do not spread raw SQL into future adapter placeholders.
- Use stdlib `sqlite3`; do not add SQLAlchemy, Alembic, DuckDB, Postgres, or Docker.
- Do not add adapter abstractions or real importers.
- Do not commit generated DB files.
- Do not use real chat data.
- Keep tests deterministic and synthetic.
- Preserve existing CLI stub behavior unless a change is strictly necessary for tests.

## Completion Report Format
The executor must return the report in this structure:

```markdown
# WP-1.1 Completion Report

## Status
One of:

- ready for PM validation
- blocked

## Summary
Briefly describe what was implemented.

## Changed Files
List every changed or created file with a one-line purpose for each.

## DB Path Behavior
State the implemented DB path precedence and paste the output of:

```powershell
poetry run python -m chat_chronicle.db path
```

## Empty DB Initialization Evidence
Paste the command and output for:

```powershell
poetry run python -m chat_chronicle.db init --db-path <temp-or-scratch-path>
```

Confirm the created DB was not committed.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| Pydantic models cover required normalized objects | pass/fail/not attempted | Name models/tests |
| Migration creates all required tables | pass/fail/not attempted | Test/output |
| DB path precedence implemented and tested | pass/fail/not attempted | Test/output |
| Empty DB init command works | pass/fail/not attempted | Command output |
| DB path command prints without creating DB | pass/fail/not attempted | Command output |
| Idempotent upsert added/skipped/updated behavior works | pass/fail/not attempted | Test summary |
| Ingest run logging records counts/errors_json | pass/fail/not attempted | Test summary |
| FTS5 table rebuild/search works | pass/fail/not attempted | Test summary |
| No real DB/chat/export files committed | pass/fail/not attempted | Git/status evidence |
| `poetry run pytest` passes | pass/fail/not attempted | Output |
| `poetry run ruff check .` passes | pass/fail/not attempted | Output |
| `poetry run chronicle --help` still lists commands | pass/fail/not attempted | Output |

## Command Evidence
Paste concise output for all required evidence commands.

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement importers | pass/fail |  |
| Did not add adapter base/protocol | pass/fail |  |
| Did not implement search CLI behavior | pass/fail |  |
| Did not add Docker/server DB dependencies | pass/fail |  |
| Did not commit generated DB files or real chat data | pass/fail |  |

## Risks Or Follow-Ups
List known issues, assumptions, or recommended follow-up tasks.
```

## Completion Status Expected
Return one of:

- `ready for PM validation`
- `blocked`

If blocked, include:

- the exact blocker
- what was attempted
- what decision or missing information is needed
