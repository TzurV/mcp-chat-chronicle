# WP-1.4 Completion Report

## Status
ready for PM validation

## Dependency Check
WP-1.2, WP-1.3, WP-1.3.1, and WP-1.3.2 are accepted:

- WP-1.2 validation report: `md/handoffs/reports/WP-1.2-validation-review.md`
- WP-1.3 validation report: `md/handoffs/reports/WP-1.3-validation-review.md`
- WP-1.3.1 validation report: `md/handoffs/reports/WP-1.3.1-validation-review.md`
- WP-1.3.2 validation report: `md/handoffs/reports/WP-1.3.2-validation-review.md`

## Summary
Implemented public `chronicle ingest` and `chronicle stats` behavior for ChatGPT official exports, Claude official exports, and OpenAI Codex local JSONL/session sources. The CLI now supports `--db-path`, provider auto-detection, source row reuse, ingest run recording, importer error persistence, idempotent upserts, and FTS rebuild after ingest.

## Changed Files
- `src/chat_chronicle/cli.py` - implemented `ingest`/`stats`, provider detection, adapter dispatch, Rich output, and stats queries.
- `src/chat_chronicle/db.py` - added minimal centralized source helpers for source row create/reuse and ingest timestamp updates.
- `tests/test_cli.py` - updated stub-command coverage because `ingest` and `stats` are now implemented.
- `tests/test_cli_ingest_stats.py` - added focused CLI tests for ingest, idempotency, provider detection, parse errors, FTS, and stats.
- `md/handoffs/reports/WP-1.4-completion-report.md` - this completion report.

## CLI Behavior
`chronicle ingest <path> --provider auto --db-path <db>` detects ChatGPT/Claude `conversations.json` signatures and OpenAI Codex JSONL/session signatures, creates or reuses one source row per provider plus resolved source path, calls the accepted concrete importer/extractor, upserts normalized conversations, records an ingest run, stores parse errors in `errors_json`, updates source timestamps, rebuilds FTS, and prints provider/db/source/count/run details.

`chronicle stats --db-path <db>` opens or initializes the DB and prints total conversations/messages, counts by provider, source summaries, and recent ingest runs. Without `--db-path`, both commands use `CHAT_CHRONICLE_DB` or `db.default_db_path()`.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| `chronicle ingest` functional for ChatGPT, Claude, and OpenAI Codex | pass | Manual ingest evidence and `test_ingest_auto_detects_*` tests |
| `--provider auto` detects all three providers | pass | `test_ingest_auto_detects_chatgpt...`, `test_ingest_auto_detects_claude...`, `test_ingest_auto_detects_openai_codex...` |
| Explicit providers work for all three providers | pass | `test_ingest_explicit_providers_work` |
| Unsupported/ambiguous inputs fail clearly | pass | `test_unsupported_auto_detection_exits_nonzero_without_ingest_run`, `test_ambiguous_auto_detection_exits_nonzero_without_ingest_run` |
| Source rows created/reused | pass | `test_reingesting_unchanged_source_reuses_source_and_skips_conversation` |
| Successful parse attempts record ingest runs | pass | `test_reingesting_unchanged_source_reuses_source_and_skips_conversation` |
| Parse errors stored in `errors_json` | pass | `test_importer_parse_errors_are_stored_without_aborting_valid_conversations` |
| Re-ingest unchanged fixtures adds/updates zero | pass | `test_reingesting_unchanged_source_reuses_source_and_skips_conversation` |
| FTS rebuilt after ingest | pass | `test_ingest_rebuilds_fts` |
| `stats` reports counts/sources/runs | pass | `test_stats_reports_counts_provider_sources_and_runs_after_ingest`; manual stats evidence |
| `stats` works on empty DB | pass | `test_stats_works_on_empty_database` |
| No out-of-scope commands implemented | pass | `ingest-folder`, `collect`, `scan-local`, `search`, and `open` remain stubs |
| No adapter base/protocol added | pass | No `adapters/base.py` or protocol added |
| Synthetic fixtures only | pass | Tests use existing synthetic fixtures under `tests/fixtures/` |
| `poetry run pytest` passes | pass | `105 passed in 4.40s` |
| `poetry run ruff check .` passes | pass | `All checks passed!` |
| `poetry run chronicle --help` still lists commands | pass | Help evidence below |

## Command Evidence

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

```text
poetry run pytest
........................................................................ [ 68%]
.................................                                        [100%]
105 passed in 4.40s
```

```text
poetry run ruff check .
All checks passed!
```

```text
poetry run chronicle --help
Usage: chronicle [OPTIONS] COMMAND [ARGS]...

A local-first, searchable archive of your AI conversations.

Commands:
  ingest         Ingest a single official export or supported local session source.
  ingest-folder  Sweep a drop folder for export archives and ingest each one.
  collect        Run every enabled source through its adapter.
  scan-local     Report, read-only, which AI-tool data stores exist on this machine.
  stats          Show per-source counts and the most recent ingest runs.
  search         Search the archive with FTS5 ranking and snippets.
  open           Open a result: deep link for web chats, transcript view otherwise.
```

```text
poetry run chronicle ingest tests\fixtures\chatgpt\minimal\conversations.json --provider auto --db-path scratch\wp-1.4-evidence-cli.db
provider: chatgpt
db path: C:\work\Github\mcp-chat-chronicle\scratch\wp-1.4-evidence-cli.db
source path: C:\work\Github\mcp-chat-chronicle\tests\fixtures\chatgpt\minimal\conversations.json
conversations seen: 1
added: 1  updated: 0  skipped: 0
parse errors: 0
ingest run id: 1
```

```text
poetry run chronicle ingest tests\fixtures\claude\minimal\conversations.json --provider auto --db-path scratch\wp-1.4-evidence-cli.db
provider: claude
db path: C:\work\Github\mcp-chat-chronicle\scratch\wp-1.4-evidence-cli.db
source path: C:\work\Github\mcp-chat-chronicle\tests\fixtures\claude\minimal\conversations.json
conversations seen: 1
added: 1  updated: 0  skipped: 0
parse errors: 0
ingest run id: 2
```

```text
poetry run chronicle ingest tests\fixtures\openai_codex\minimal\rollout-minimal.jsonl --provider auto --db-path scratch\wp-1.4-evidence-cli.db
provider: openai_codex
db path: C:\work\Github\mcp-chat-chronicle\scratch\wp-1.4-evidence-cli.db
source path: C:\work\Github\mcp-chat-chronicle\tests\fixtures\openai_codex\minimal\rollout-minimal.jsonl
conversations seen: 1
added: 1  updated: 0  skipped: 0
parse errors: 0
ingest run id: 3
```

```text
poetry run chronicle stats --db-path scratch\wp-1.4-evidence-cli.db
db path: C:\work\Github\mcp-chat-chronicle\scratch\wp-1.4-evidence-cli.db
total conversations: 3
total messages: 6
Counts by provider: chatgpt=1, claude=1, openai_codex=1
Sources: 3 rows with provider, resolved source path, enabled=1, and last_ingested_at
Recent ingest runs: run ids 3/2/1, status=success, seen=1, added=1, updated=0, skipped=0, errors=0
```

## Test Names Covering Required Scenarios
- `test_ingest_auto_detects_chatgpt_and_inserts_conversations_and_messages`
- `test_ingest_auto_detects_claude_and_inserts_conversations_and_messages`
- `test_ingest_auto_detects_openai_codex_jsonl_and_inserts_conversation`
- `test_ingest_auto_detects_openai_codex_home_directory`
- `test_ingest_explicit_providers_work`
- `test_reingesting_unchanged_source_reuses_source_and_skips_conversation`
- `test_importer_parse_errors_are_stored_without_aborting_valid_conversations`
- `test_unsupported_auto_detection_exits_nonzero_without_ingest_run`
- `test_ambiguous_auto_detection_exits_nonzero_without_ingest_run`
- `test_ingest_rebuilds_fts`
- `test_stats_reports_counts_provider_sources_and_runs_after_ingest`
- `test_stats_works_on_empty_database`

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement ingest-folder/collect/source CRUD | pass | Existing stubs preserved |
| Did not implement search/open behavior | pass | Existing stubs preserved |
| Did not add adapter base/protocol | pass | Concrete adapters reused directly |
| Did not add Gemini/Claude Code/Cursor/other Class B importers | pass | No new importers added |
| Did not commit real exports/private data or DB files | pass | Evidence DB is `scratch\wp-1.4-evidence-cli.db`, ignored by `*.db`; fixtures are synthetic |

## Private Data / Generated Artifact Check
No real exports, real Codex sessions, DB files, zip exports, secrets, auth files, or local private data were committed. `git ls-files *.db *.zip *.sqlite *.sqlite3 exports tests\fixtures` lists only synthetic JSON/JSONL fixtures already under `tests/fixtures/`; no DB or zip files are tracked.

## Risks Or Follow-Ups
- Rich tables are intentionally simple for WP-1.4; later UX work can refine column widths and formatting.
- `stats` uses SQLite JSON functions for run error counts; this passed on the project SQLite build used by tests.
- The existing schema has no unique index on `sources(provider, path_or_config)`, so source reuse is enforced by the helper query rather than a DB constraint.
