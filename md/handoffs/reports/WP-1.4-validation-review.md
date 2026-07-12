# WP-1.4 Validation Review

## Decision
**Accepted.**

The completion report at `md/handoffs/reports/WP-1.4-completion-report.md` satisfies the WP-1.4 handoff. The CLI now wires the accepted ChatGPT, Claude, and OpenAI Codex adapters into `chronicle ingest`, records source rows and ingest runs, rebuilds FTS, and exposes `chronicle stats`.

## Validation Performed

| Check | Result | Evidence |
| --- | --- | --- |
| Poetry preflight uses repo-local venv | Pass | `poetry env info --path` -> `C:\work\Github\mcp-chat-chronicle\.venv` |
| Full test suite | Pass | `poetry run pytest` -> `105 passed in 6.28s` |
| Ruff lint | Pass | `poetry run ruff check .` -> `All checks passed!` |
| CLI help still lists required commands | Pass | `poetry run chronicle --help` lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, and `open` |
| Completion report exists at required path | Pass | `md/handoffs/reports/WP-1.4-completion-report.md` |
| No tracked DB/zip/private export artifacts | Pass | `git ls-files` shows only source, docs, and synthetic JSON/JSONL fixtures; no tracked `.db`, `.zip`, `.sqlite`, export, secret, or auth files observed |

## Acceptance Criteria Review

| Acceptance Criterion | Result | Notes |
| --- | --- | --- |
| `chronicle ingest` functional for ChatGPT, Claude, and OpenAI Codex | Pass | Implemented in `src/chat_chronicle/cli.py`; covered by `tests/test_cli_ingest_stats.py`. |
| `--provider auto` detects all three providers | Pass | Detection covers `conversations.json`, ZIPs, Codex JSONL, Codex sessions folders, and Codex home folders. |
| Explicit providers work for all three providers | Pass | Covered by `test_ingest_explicit_providers_work`. |
| Unsupported/ambiguous inputs fail clearly | Pass | Detection happens before DB connection for auto mode; tests assert no DB file/ingest run is created. |
| Source rows created/reused | Pass | `get_or_create_source()` creates/reuses by provider + resolved path and updates `last_seen_at`. |
| Successful parse attempts record ingest runs | Pass | Ingest wraps parsed adapter results in `begin_ingest_run()` / `finish_ingest_run()`. |
| Parse errors stored in `errors_json` | Pass | Adapter errors are serialized and stored without aborting valid conversations. |
| Re-ingest unchanged fixtures adds/updates zero | Pass | Covered by idempotency test; second run reports skipped. |
| FTS rebuilt after ingest | Pass | `rebuild_fts(conn)` is called after ingest and covered by FTS test. |
| `stats` reports counts/sources/runs | Pass | Implemented with provider, source, and recent ingest-run tables. |
| `stats` works on empty DB | Pass | Covered by `test_stats_works_on_empty_database`. |
| Out-of-scope commands remain stubs | Pass | `ingest-folder`, `collect`, `scan-local`, `search`, and `open` still use `_not_implemented()`. |
| No adapter base/protocol introduced | Pass | No `adapters/base.py` or `AdapterProtocol` found. |
| Synthetic fixtures only | Pass | New tests reuse synthetic fixtures under `tests/fixtures/`; no real data tracked. |

## Scope Notes

- `chronicle source add/list/disable` was not implemented, as required. Dedicated source listing remains a WP-1.6 source-management concern.
- `chronicle search` and `chronicle open` remain WP-2.1 work.
- Gemini, Claude Code, Cursor, and other importers remain out of scope.

## Follow-Ups

- CO-1 should consider adding a DB uniqueness constraint or migration-safe equivalent for `sources(provider, path_or_config)`. WP-1.4 correctly reuses source rows through helper logic, but the schema does not enforce that invariant.
- Continue real-file verification when the ChatGPT export ZIP arrives. Parser-level support exists; this acceptance is based on synthetic fixtures and executor manual fixture commands, per the WP-1.4 scope.

## Next Step

WP-1.4 is accepted. The next handoff should be CO-1 schema migration + link-back touch-ups before WP-2.1 search/open.
