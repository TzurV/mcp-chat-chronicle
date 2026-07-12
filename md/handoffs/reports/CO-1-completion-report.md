# CO-1 Completion Report

## Status
ready for PM validation

## Dependency Check
WP-1.1 through WP-1.4 are accepted:

- WP-1.1: `md/handoffs/reports/WP-1.1-validation-review.md`
- WP-1.2: `md/handoffs/reports/WP-1.2-validation-review.md`
- WP-1.3: `md/handoffs/reports/WP-1.3-validation-review.md`
- WP-1.3.1: `md/handoffs/reports/WP-1.3.1-validation-review.md`
- WP-1.3.2: `md/handoffs/reports/WP-1.3.2-validation-review.md`
- WP-1.4: `md/handoffs/reports/WP-1.4-validation-review.md`

## Summary
Implemented schema version 2 with a fresh v2 schema path and explicit v1-to-v2 migration. Added `projects`, nullable conversation link-back columns, `manual_entry` source type support, DB-level partial uniqueness for non-null source paths, duplicate-source migration cleanup, and persistence of link-back metadata. OpenAI Codex conversations now carry the resolved JSONL `origin_path` when parsed from a file or sessions directory.

## Changed Files
- `src/chat_chronicle/db.py`: bumped schema version, added v2 schema/migration, source deduplication, source uniqueness index, and link-back metadata persistence.
- `src/chat_chronicle/models.py`: added optional `project_id`, `origin_path`, and `resume_hint` to `Conversation`.
- `src/chat_chronicle/adapters/openai_codex.py`: populates resolved JSONL `origin_path`; leaves `resume_hint` unset pending verified Codex resume behavior.
- `tests/test_db.py`: added v2 fresh-schema, v1 migration, source uniqueness, `manual_entry`, and link-back persistence tests.
- `tests/test_openai_codex.py`: verifies Codex `origin_path` and nullable `resume_hint`.
- `md/handoffs/reports/CO-1-completion-report.md`: this report.

Pre-existing uncommitted user changes were present before implementation: `md/development-ledger.md` and `md/handoffs/CO-1-schema-link-back-migration.md`.

## Schema And Migration Behavior
Fresh databases now create the v2 schema directly and set `PRAGMA user_version = 2`. Existing v1 databases migrate through `_migrate_v2(conn)`, which creates `projects`, rebuilds `sources` with the expanded CHECK constraint, adds `conversations.project_id`, `origin_path`, and `resume_hint`, and creates `idx_sources_provider_path_unique`.

Before creating the unique index, the migration deduplicates non-null `(provider, path_or_config)` source rows by keeping the lowest source ID, repointing `conversations.source_id` and `ingest_runs.source_id`, preserving best available `enabled`, `last_seen_at`, and `last_ingested_at`, then deleting duplicate source rows.

## Link-Back Behavior
ChatGPT still produces provider `chatgpt`, stable `provider_conv_id`, useful titles, and URLs in the form `https://chatgpt.com/c/{provider_conv_id}`.

Claude still produces provider `claude`, stable `provider_conv_id`, useful titles where present, and URLs in the form `https://claude.ai/chat/{provider_conv_id}`.

OpenAI Codex remains URL-less and now stores `origin_path` as the resolved `.jsonl` session path. `resume_hint` remains `None` because this repo has no verified evidence that `codex resume <session-id>` is supported locally.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| `CURRENT_SCHEMA_VERSION` is 2 | pass | `src/chat_chronicle/db.py`; schema probe reported `user_version: 2`. |
| Fresh DB creates v2 schema | pass | `test_fresh_database_creates_v2_schema`. |
| v1 DB migrates to v2 without data loss | pass | `test_v1_database_migrates_to_v2_and_preserves_rows`. |
| `projects` table exists | pass | Fresh/migration tests and schema probe `projects_table: 1`. |
| New conversation link-back columns exist and persist | pass | `test_upsert_conversation_persists_and_refreshes_link_back_metadata`; schema probe columns. |
| `manual_entry` source type accepted | pass | `test_fresh_database_creates_v2_schema`; migration test inserts `manual_entry`. |
| DB-level source uniqueness enforced | pass | `test_sources_enforce_unique_provider_path_when_path_is_not_null`. |
| ChatGPT and Claude titles/URLs verified | pass | Existing parser tests plus full `poetry run pytest`. |
| OpenAI Codex `origin_path` handled | pass | `test_parse_minimal_session_returns_one_conversation`; schema probe shows persisted path. |
| `chronicle ingest` remains functional | pass | CLI commands succeeded for ChatGPT, Claude, and OpenAI Codex synthetic fixtures. |
| `chronicle stats` remains functional | pass | `chronicle stats --db-path C:\tmp\co1-validation.db` returned totals and provider counts. |
| No out-of-scope commands implemented | pass | `search`/`open` and other deferred commands remain stubs. |
| No adapter base/protocol added | pass | Static scan found no new `AdapterProtocol` or `adapters/base.py`. |
| Synthetic fixtures only | pass | Tests and CLI evidence use `tests/fixtures`; temporary DB was under `C:\tmp`. |
| `poetry run pytest` passes | pass | `109 passed in 5.29s`. |
| `poetry run ruff check .` passes | pass | `All checks passed!`. |
| `poetry run chronicle --help` still lists commands | pass | Help lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, and `open`. |

## Command Evidence
`poetry env info --path`

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

`poetry run pytest`

```text
........................................................................ [ 66%]
.....................................                                    [100%]
109 passed in 5.29s
```

`poetry run ruff check .`

```text
All checks passed!
```

`poetry run chronicle --help`

```text
Commands:
  ingest         Ingest a single official export or supported local session source.
  ingest-folder  Sweep a drop folder for export archives and ingest each one.
  collect        Run every enabled source through its adapter.
  scan-local     Report, read-only, which AI-tool data stores exist on this machine.
  stats          Show per-source counts and the most recent ingest runs.
  search         Search the archive with FTS5 ranking and snippets.
  open           Open a result: deep link for web chats, transcript view otherwise.
```

Temporary v1 validation DB setup:

```text
C:\tmp\co1-validation.db
```

`poetry run chronicle ingest tests\fixtures\chatgpt\minimal\conversations.json --provider chatgpt --db-path C:\tmp\co1-validation.db`

```text
provider: chatgpt
db path: C:\tmp\co1-validation.db
conversations seen: 1
added: 1  updated: 0  skipped: 0
parse errors: 0
ingest run id: 1
```

`poetry run chronicle ingest tests\fixtures\claude\minimal\conversations.json --provider claude --db-path C:\tmp\co1-validation.db`

```text
provider: claude
db path: C:\tmp\co1-validation.db
conversations seen: 1
added: 1  updated: 0  skipped: 0
parse errors: 0
ingest run id: 2
```

`poetry run chronicle ingest tests\fixtures\openai_codex\minimal\rollout-minimal.jsonl --provider openai_codex --db-path C:\tmp\co1-validation.db`

```text
provider: openai_codex
db path: C:\tmp\co1-validation.db
conversations seen: 1
added: 1  updated: 0  skipped: 0
parse errors: 0
ingest run id: 3
```

`poetry run chronicle stats --db-path C:\tmp\co1-validation.db`

```text
db path: C:\tmp\co1-validation.db
total conversations: 3
total messages: 6
Counts by provider: chatgpt=1, claude=1, openai_codex=1
Recent ingest runs: 3 successful runs, 0 errors
```

Schema probe on the migrated validation DB:

```text
user_version: 2
conversation_columns: project_id,origin_path,resume_hint
projects_table: 1
codex_origin_path: C:\work\Github\mcp-chat-chronicle\tests\fixtures\openai_codex\minimal\rollout-minimal.jsonl
```

Note: two local Python validation commands were rerun with sandbox escalation after the known Windows sandbox launcher error `CreateProcessAsUserW failed: 1312`.

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement search/open/note/source management | pass | Deferred commands remain stubs; no source-management command added. |
| Did not add adapter base/protocol | pass | No `adapters/base.py`; no `AdapterProtocol` in implementation. |
| Did not add Gemini/Claude Code/Cursor/new importers | pass | Only accepted OpenAI Codex extractor was touched for link-back metadata. |
| Did not commit real exports/private data or DB files | pass | No generated DB/export/private files added; validation DB stayed in `C:\tmp`. |

## Risks Or Follow-Ups
- `resume_hint` for OpenAI Codex remains unset until local Codex resume behavior is verified.
- The CLI `stats` table remains unchanged and does not surface link-back fields; WP-2.1 `open` is expected to expose local transcript link-back details.
