# WP-2.1 Completion Report

## Status
- ready for PM validation

## Dependency Check
WP-1.1 through WP-1.4 and CO-1 are accepted:

- `md/handoffs/reports/WP-1.1-validation-review.md`
- `md/handoffs/reports/WP-1.2-validation-review.md`
- `md/handoffs/reports/WP-1.3-validation-review.md`
- `md/handoffs/reports/WP-1.3.1-validation-review.md`
- `md/handoffs/reports/WP-1.3.2-validation-review.md`
- `md/handoffs/reports/WP-1.4-validation-review.md`
- `md/handoffs/reports/CO-1-validation-review.md`

## Summary
Implemented usable `chronicle search` and `chronicle open` over the existing SQLite v2 schema and `chat_fts` index. Search uses FTS5 `MATCH`, `bm25(chat_fts)` ordering, provider/date/tag/limit filters, useful snippets, and `--db-path`. Open prints URL-backed web rows and attempts standard-library browser launch; local rows render the stored transcript plus CO-1 link-back fields.

## Changed Files
- `src/chat_chronicle/search.py` - FTS search query layer, date/tag filters, snippets, and conversation detail helpers.
- `src/chat_chronicle/cli.py` - functional `search` and `open` commands, `--db-path`, Rich output, transcript rendering, browser helper.
- `tests/test_search.py` - direct query-layer tests for ranking, snippets, filters, detail lookup, validation, and performance smoke.
- `tests/test_cli_search_open.py` - CLI search/open tests using synthetic ChatGPT, Claude, and OpenAI Codex fixtures.
- `tests/test_cli.py` - removed `search`/`open` from the stub-command expectation.
- `md/handoffs/reports/WP-2.1-completion-report.md` - this report.

## Search Behavior
`search_conversations()` selects rows with `chat_fts MATCH ?`, joins to `conversations` by `rowid`, and orders by `bm25(chat_fts) ASC`. It supports provider, since, until, tag, and limit filters. Date-only `since` starts at `T00:00:00Z`; date-only `until` ends at `T23:59:59.999999Z`. Tag filtering uses simple containment against `enrichments.tags_json` and `knowledge_items.tags_json`.

SQLite `snippet()` is attempted in the query. Because `chat_fts` is contentless, the implementation falls back when SQLite returns empty or unhelpful snippets, building a deterministic short snippet from title, summary/tags, messages, and knowledge-item text. Empty queries and invalid limits fail clearly. New or empty DBs initialize through `connect()` and return `No results`.

## Open Behavior
`chronicle open <id>` loads `conversations.id` and ordered `messages.seq`. Web rows print id/provider/title/date/url and call a small browser helper using `webbrowser.open(url)`. Browser errors or false returns do not fail the command. Local rows print id/provider/title/date, `origin_path`, `resume_hint` when present, and the stored transcript. Rows without URL or origin path state that no source link is available.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| `chronicle search` functional | pass | `test_search_finds_terms_from_ingested_chatgpt_claude_and_codex_fixtures`; manual `chronicle search docker` |
| `search --db-path` works | pass | All CLI search tests and manual commands use temp `--db-path` |
| FTS5 `MATCH` + `bm25` ranking used | pass | `src/chat_chronicle/search.py`; `test_search_uses_fts_ranking_and_fallback_snippet` |
| Search output includes required columns | pass | Rich table includes ID/date/provider/title/snippet/open hint; stable result lines also printed |
| Provider/since/until/tag/limit filters work | pass | `test_provider_since_until_and_tag_filters`; `test_search_cli_filters_and_limit_validation` |
| Empty query and invalid limit fail clearly | pass | `test_search_rejects_empty_query`; `test_search_rejects_invalid_limit`; CLI equivalents |
| No results and empty DB handled cleanly | pass | `test_search_no_results_and_empty_database_exit_zero`; manual no-result command |
| `chronicle open` functional | pass | `test_open_web_row_prints_url_and_calls_browser_helper`; `test_open_local_row_prints_transcript_origin_path_and_resume_hint` |
| Web URL rows print and launch URL | pass | Browser helper called in test; manual command prints URL |
| Local rows print transcript and link-back fields | pass | Codex CLI test covers transcript, `origin_path`, and synthetic `resume_hint`; manual local open covers transcript and origin path |
| CO-1 link-back fields exercised in tests | pass | Web URL and local origin/resume tests |
| No out-of-scope behavior implemented | pass | Only search/open/query helpers changed |
| No adapter base/protocol added | pass | No adapter abstraction files or protocols added |
| Synthetic fixtures only | pass | Tests use `tests/fixtures`; manual evidence uses synthetic fixtures |
| `poetry run pytest` passes | pass | `123 passed in 10.09s` |
| `poetry run ruff check .` passes | pass | `All checks passed!` |
| `poetry run chronicle --help` still lists commands | pass | Help output lists ingest, ingest-folder, collect, scan-local, stats, search, open |

## Command Evidence
Poetry preflight:

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

Full tests:

```text
poetry run pytest
123 passed in 10.09s
```

Lint:

```text
poetry run ruff check .
All checks passed!
```

CLI help:

```text
poetry run chronicle --help
Commands: ingest, ingest-folder, collect, scan-local, stats, search, open
```

Temp DB ingest evidence:

```text
poetry run chronicle ingest tests\fixtures\chatgpt\minimal\conversations.json --db-path C:\tmp\wp21-fts-search-open-evidence-01.db
provider: chatgpt
conversations seen: 1
added: 1  updated: 0  skipped: 0
parse errors: 0
ingest run id: 1

poetry run chronicle ingest tests\fixtures\openai_codex\minimal\rollout-minimal.jsonl --db-path C:\tmp\wp21-fts-search-open-evidence-01.db
provider: openai_codex
conversations seen: 1
added: 1  updated: 0  skipped: 0
parse errors: 0
ingest run id: 2
```

Search with results:

```text
poetry run chronicle search docker --db-path C:\tmp\wp21-fts-search-open-evidence-01.db
Search results
result 1 | 2026-01-01T01:00:00.500000Z | chatgpt | Docker networking notes | Docker networking notes How do I inspect a docker bridge network? Run `docker network inspect bridge`. It prints the sub ... | chronicle open 1 (web URL)
```

Search with no results:

```text
poetry run chronicle search zzznomatch --db-path C:\tmp\wp21-fts-search-open-evidence-01.db
db path: C:\tmp\wp21-fts-search-open-evidence-01.db
No results
```

Open web row:

```text
$env:CHAT_CHRONICLE_NO_BROWSER='1'; poetry run chronicle open 1 --db-path C:\tmp\wp21-fts-search-open-evidence-01.db
id: 1
provider: chatgpt
title: Docker networking notes
date: 2026-01-01T01:00:00.500000Z
url: https://chatgpt.com/c/conv-minimal-1
browser launch: unavailable; use the printed URL
```

The first web-open evidence attempt hit the known Windows sandbox launcher error `CreateProcessAsUserW failed: 1312`; the rerun used sandbox escalation for validation only. Browser launch was disabled by `CHAT_CHRONICLE_NO_BROWSER=1` to avoid opening a real browser. Normal command execution still attempts `webbrowser.open(url)`, covered by `test_open_web_row_prints_url_and_calls_browser_helper`.

Open local row:

```text
poetry run chronicle open 2 --db-path C:\tmp\wp21-fts-search-open-evidence-01.db
id: 2
provider: openai_codex
title: How do I list Codex session files?
date: 2026-06-01T10:02:00.000000Z
origin_path: C:\work\Github\mcp-chat-chronicle\tests\fixtures\openai_codex\minimal\rollout-minimal.jsonl
origin_file: rollout-minimal.jsonl
transcript:
user [2026-06-01T10:01:00.000000Z]:
How do I list Codex session files?
assistant [2026-06-01T10:02:00.000000Z]:
Look under the sessions directory.

Each rollout file is JSONL.
```

Required scenario tests:

```text
test_search_finds_terms_from_ingested_chatgpt_claude_and_codex_fixtures
test_search_uses_fts_ranking_and_fallback_snippet
test_provider_since_until_and_tag_filters
test_search_cli_filters_and_limit_validation
test_search_rejects_invalid_limit
test_search_rejects_empty_query
test_search_no_results_and_empty_database_exit_zero
test_open_web_row_prints_url_and_calls_browser_helper
test_open_local_row_prints_transcript_origin_path_and_resume_hint
test_open_missing_id_and_unknown_id_exit_nonzero
test_search_performance_smoke_uses_indexed_fts_path
test_help_lists_every_required_command
```

## Performance Evidence
`test_search_performance_smoke_uses_indexed_fts_path` seeds 350 synthetic conversations, rebuilds FTS, searches a term present in 7 rows, and asserts the query returns under 2.0 seconds. This catches an obvious table-scan implementation mistake without making CI machine-sensitive. The master-plan p95 target on 5k real conversations remains deferred to prototype/real-archive validation.

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement Claude Code/Cursor/Gemini/new importers | pass | No importer/extractor changes |
| Did not implement collect/ingest-folder/source management/note | pass | Existing stubs unchanged |
| Did not implement rename/MCP/enrichment/smart search | pass | Search remains lexical FTS only |
| Did not add adapter base/protocol | pass | No adapter abstraction introduced |
| Did not commit real exports/private data or DB files | pass | Only synthetic fixtures and temp DB under `C:\tmp` used |

## Risks Or Follow-Ups
- SQLite `snippet()` is attempted but contentless FTS generally needs fallback snippets; this is handled and tested.
- Full p95 validation on a 5k-conversation archive remains for prototype validation.
- Web browser launch is intentionally best-effort; URL is printed regardless.
