# CO-1 Handoff: Schema Migration + Link-Back Touch-Ups

## Objective
Implement the approved Change Order 01 schema amendments as a forward SQLite migration before WP-2.1 search/open.

This delivery prepares the archive for reliable link-back behavior by adding project/link-back fields to the normalized model and DB layer, while preserving the accepted WP-1.4 `chronicle ingest` and `chronicle stats` behavior.

## Delivery Position
This is the next delivery after accepted WP-1.4.

Execution order:

```text
WP-1.4 accepted
CO-1 schema migration + link-back touch-ups  <-- this handoff
WP-2.1 FTS search + open
WP-3.1 Claude Code extractor
prototype
```

## Dependency Gate
Do not start implementation unless all of these are accepted:

- WP-1.1 Normalized models + DB layer
- WP-1.2 ChatGPT export importer
- WP-1.3 Claude export importer
- WP-1.3.1 Claude real export content-block correction
- WP-1.3.2 OpenAI Codex local extractor
- WP-1.4 CLI ingest + stats

Validation reports expected:

- `md/handoffs/reports/WP-1.1-validation-review.md`
- `md/handoffs/reports/WP-1.2-validation-review.md`
- `md/handoffs/reports/WP-1.3-validation-review.md`
- `md/handoffs/reports/WP-1.3.1-validation-review.md`
- `md/handoffs/reports/WP-1.3.2-validation-review.md`
- `md/handoffs/reports/WP-1.4-validation-review.md`

If any dependency is missing, return `blocked` and state the exact missing validation report.

## Source Of Truth
Read these before editing:

- `md/change-order-01.md`, especially CO-1
- `md/master-plan.md`, especially Sections 2, 5, and 6
- `md/development-ledger.md`
- `md/agent-operating-notes.md`
- `md/handoffs/reports/WP-1.4-validation-review.md`

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

- A DB migration from schema version 1 to schema version 2.
- `projects` table.
- Nullable `conversations.project_id`.
- Nullable `conversations.origin_path`.
- Nullable `conversations.resume_hint`.
- `manual_entry` accepted by `sources.source_type`.
- DB/model persistence for the new conversation fields.
- Source uniqueness hardening for `sources(provider, path_or_config)` where `path_or_config` is not null.
- Tests for fresh DB creation and migration from a v1 DB.
- Tests proving accepted importers/extractors still ingest through WP-1.4 CLI after the migration.

Do not implement:

- `chronicle search`.
- `chronicle open`.
- `chronicle note`.
- `chronicle source add/list/disable`.
- `chronicle collect`.
- `chronicle ingest-folder`.
- Claude Code, Cursor, Gemini, or new importer/extractor behavior.
- Rename to WorkTrail.
- Adapter base/protocol abstraction.
- Real export fixtures or private local data.

## Schema Requirements

### Schema Version
Bump:

```python
CURRENT_SCHEMA_VERSION = 2
```

Fresh DB creation must create the v2 schema directly.

Existing v1 DBs must migrate forward through a deterministic `_migrate_v2(conn)` path.

### Projects Table
Add:

```sql
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    root_path TEXT,
    created_at TEXT
);
```

No project inference UI is required in this work package. The table may remain empty after ChatGPT/Claude/Codex ingest.

### Conversation Columns
Add nullable columns:

```sql
ALTER TABLE conversations ADD COLUMN project_id INTEGER REFERENCES projects(id);
ALTER TABLE conversations ADD COLUMN origin_path TEXT;
ALTER TABLE conversations ADD COLUMN resume_hint TEXT;
```

If SQLite/foreign-key limitations require table rebuild instead of simple `ALTER TABLE`, implement a safe rebuild and preserve existing rows.

### Sources `manual_entry`
The current v1 `sources.source_type` CHECK does not include `manual_entry`. SQLite cannot directly alter a CHECK constraint, so this likely requires rebuilding the `sources` table:

```sql
source_type TEXT NOT NULL CHECK(source_type IN
    ('official_export','local_store','manual_folder','experimental_cache','manual_entry'))
```

Preserve existing source IDs so `conversations.source_id` and `ingest_runs.source_id` remain valid.

### Source Uniqueness Follow-Up
WP-1.4 reuses source rows through helper logic but the DB does not enforce uniqueness. CO-1 should harden this while the schema is already migrating.

Add a migration-safe uniqueness guarantee for non-null source paths:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_sources_provider_path_unique
ON sources(provider, path_or_config)
WHERE path_or_config IS NOT NULL;
```

If duplicate source rows already exist in a v1 DB, handle them deterministically before creating the index:

- keep the lowest `sources.id` for each `(provider, path_or_config)`;
- repoint `conversations.source_id` and `ingest_runs.source_id` from duplicate IDs to the kept ID;
- preserve the best available `enabled`, `last_seen_at`, and `last_ingested_at` values;
- delete the duplicate source rows;
- then create the unique index.

Add a focused migration test for this behavior if practical.

## Model Requirements
Update `Conversation` in `src/chat_chronicle/models.py` to include:

```python
project_id: int | None = None
origin_path: str | None = None
resume_hint: str | None = None
```

Keep these fields optional. Existing parser tests should not need broad fixture rewrites.

Update `content_hash_value()` only if needed. Recommended: keep the content hash based on normalized messages only, as it is today, so link-back metadata changes do not force message-content updates.

## DB Persistence Requirements
Update `upsert_conversation()` and related DB value helpers so:

- inserts persist `project_id`, `origin_path`, and `resume_hint`;
- updates persist those fields;
- unchanged message content still returns `skipped` as before;
- when a skipped conversation has changed link-back metadata, choose one explicit behavior and test it.

Recommended behavior for skipped rows:

- keep `status = "skipped"` when message content hash is unchanged;
- still refresh mutable metadata fields such as `source_id`, `title`, `url`, `project_id`, `origin_path`, `resume_hint`, timestamps, and `message_count` if they differ.

If that recommendation would be too invasive, document the tradeoff in the completion report and add a follow-up.

## Adapter Touch-Up Requirements

### ChatGPT
Verify the ChatGPT importer still populates:

- `provider = "chatgpt"`
- stable `provider_conv_id`
- useful `title`
- `url = https://chatgpt.com/c/{provider_conv_id}`

No `origin_path` or `resume_hint` is required for official web exports.

### Claude
Verify the Claude importer still populates:

- `provider = "claude"`
- stable `provider_conv_id`
- useful `title`
- `url = https://claude.ai/chat/{provider_conv_id}`

No `origin_path` or `resume_hint` is required for official web exports.

### OpenAI Codex
OpenAI Codex is a local-store source and has no web URL. Populate best-effort link-back fields on returned `Conversation` objects:

- `origin_path`: resolved path to the source `.jsonl` session file when parsing a file or session directory.
- `resume_hint`: best-effort local command if the session ID is known. Use a conservative value and document it, for example `codex resume <session-id>` only if this is supported by local Codex behavior or existing project evidence. If not verified, leave `None` and state why in the report.

Do not add real Codex sessions to the repo.

## CLI Requirements
`chronicle ingest` and `chronicle stats` from WP-1.4 must continue to work without user-facing regression.

`chronicle stats` may remain simple. It does not need to show `project_id`, `origin_path`, or `resume_hint` in CO-1 unless that falls out naturally. WP-2.1 will expose link-back behavior through `open`.

## Tests Required
Add or update focused tests. Minimum required scenarios:

- Fresh DB initializes directly to schema version 2.
- Existing v1 DB migrates to v2 and preserves existing source/conversation/message/ingest-run rows.
- `projects` table exists.
- `conversations` includes `project_id`, `origin_path`, and `resume_hint`.
- `sources.source_type` accepts `manual_entry`.
- Source uniqueness index prevents duplicate non-null `(provider, path_or_config)` rows.
- If duplicate v1 source rows are handled, migration repoints dependent rows and deduplicates correctly.
- `upsert_conversation()` persists new link-back fields on insert and update.
- Existing ChatGPT, Claude, and OpenAI Codex parser tests still pass.
- WP-1.4 CLI ingest tests still pass.
- `chronicle ingest` works after migration for ChatGPT, Claude, and OpenAI Codex synthetic fixtures.
- `chronicle stats` works after migration.

Use synthetic fixtures only.

## Acceptance Criteria
CO-1 is complete only when all of these are true:

- `CURRENT_SCHEMA_VERSION` is 2.
- Fresh DBs create the v2 schema.
- v1 DBs migrate forward to v2 without data loss.
- `projects` table exists.
- `conversations.project_id`, `conversations.origin_path`, and `conversations.resume_hint` exist and are persisted.
- `sources.source_type` accepts `manual_entry`.
- Source uniqueness for non-null `(provider, path_or_config)` is enforced at the DB level.
- Accepted ChatGPT and Claude importers still provide usable titles and web URLs.
- OpenAI Codex local-store conversations populate `origin_path` where feasible, or the report explains why not.
- `chronicle ingest` remains functional for ChatGPT, Claude, and OpenAI Codex.
- `chronicle stats` remains functional.
- No search/open/note/source-management behavior is implemented.
- No adapter base/protocol is introduced.
- Tests use synthetic fixtures only.
- `poetry run pytest` passes.
- `poetry run ruff check .` passes.
- `poetry run chronicle --help` still lists all existing commands.

## Evidence Required
The executor must write a detailed completion report to:

```text
md/handoffs/reports/CO-1-completion-report.md
```

The report must include:

- Changed-files summary.
- Dependency confirmation that WP-1.1 through WP-1.4 are accepted.
- Exact command output or concise pasted result for:
  - `poetry env info --path`
  - `poetry run pytest`
  - `poetry run ruff check .`
  - `poetry run chronicle --help`
  - at least one `chronicle ingest` command after migration
  - at least one `chronicle stats` command after migration
- Test names covering all required scenarios.
- Schema version evidence.
- Migration evidence from v1 to v2.
- Confirmation that no real exports, real Codex sessions, DB files, zip exports, secrets, auth files, or local private data were committed.
- Explicit checklist mapping each acceptance criterion to `pass`, `fail`, or `not attempted`.

## Completion Report Format
Use this exact structure:

```markdown
# CO-1 Completion Report

## Status
One of:

- ready for PM validation
- blocked

## Dependency Check
Confirm WP-1.1 through WP-1.4 are accepted, with validation report paths.

## Summary
Briefly describe the schema migration and link-back changes.

## Changed Files
List every changed or created file with a one-line purpose.

## Schema And Migration Behavior
Describe fresh DB v2 creation, v1-to-v2 migration, source CHECK migration, source uniqueness handling, and any duplicate-source handling.

## Link-Back Behavior
Describe how ChatGPT, Claude, and OpenAI Codex conversations populate title/url/origin_path/resume_hint.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| `CURRENT_SCHEMA_VERSION` is 2 | pass/fail/not attempted |  |
| Fresh DB creates v2 schema | pass/fail/not attempted |  |
| v1 DB migrates to v2 without data loss | pass/fail/not attempted |  |
| `projects` table exists | pass/fail/not attempted |  |
| New conversation link-back columns exist and persist | pass/fail/not attempted |  |
| `manual_entry` source type accepted | pass/fail/not attempted |  |
| DB-level source uniqueness enforced | pass/fail/not attempted |  |
| ChatGPT and Claude titles/URLs verified | pass/fail/not attempted |  |
| OpenAI Codex `origin_path` handled | pass/fail/not attempted |  |
| `chronicle ingest` remains functional | pass/fail/not attempted |  |
| `chronicle stats` remains functional | pass/fail/not attempted |  |
| No out-of-scope commands implemented | pass/fail/not attempted |  |
| No adapter base/protocol added | pass/fail/not attempted |  |
| Synthetic fixtures only | pass/fail/not attempted |  |
| `poetry run pytest` passes | pass/fail/not attempted |  |
| `poetry run ruff check .` passes | pass/fail/not attempted |  |
| `poetry run chronicle --help` still lists commands | pass/fail/not attempted |  |

## Command Evidence
Paste concise output for all required evidence commands.

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement search/open/note/source management | pass/fail |  |
| Did not add adapter base/protocol | pass/fail |  |
| Did not add Gemini/Claude Code/Cursor/new importers | pass/fail |  |
| Did not commit real exports/private data or DB files | pass/fail |  |

## Risks Or Follow-Ups
List known issues, assumptions, or recommended follow-up tasks.
```

## Technical Guardrails
- Keep the migration small and explicit.
- Prefer SQL migration tests over broad refactors.
- Preserve accepted WP-1.4 CLI behavior.
- Do not rename the package or CLI in this work package.
- Do not add runtime dependencies.
- Do not add adapter abstraction.
- Do not commit generated DBs, exports, private histories, or secrets.

## Completion Status Expected
Return one of:

- `ready for PM validation`
- `blocked`

If blocked, include:

- exact blocker;
- what was attempted;
- what decision or missing information is needed.
