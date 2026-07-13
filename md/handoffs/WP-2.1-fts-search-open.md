# WP-2.1 Handoff: FTS5 Search + Open

## Objective
Implement the first usable search experience over the local archive.

This delivery makes `chronicle search` and `chronicle open` functional using the accepted SQLite/FTS5 database, the accepted WP-1.4 ingest path, and the accepted CO-1 link-back fields.

## Delivery Position
This is the next delivery after accepted CO-1.

Execution order:

```text
WP-1.4 accepted
CO-1 accepted
WP-2.1 FTS5 search + open  <-- this handoff
WP-3.1 Claude Code extractor
prototype
```

## Dependency Gate
Do not start implementation unless these are accepted:

- WP-1.1 Normalized models + DB layer
- WP-1.2 ChatGPT export importer
- WP-1.3 Claude export importer
- WP-1.3.1 Claude real export content-block correction
- WP-1.3.2 OpenAI Codex local extractor
- WP-1.4 CLI ingest + stats
- CO-1 Schema migration + link-back touch-ups

Validation reports expected:

- `md/handoffs/reports/WP-1.1-validation-review.md`
- `md/handoffs/reports/WP-1.2-validation-review.md`
- `md/handoffs/reports/WP-1.3-validation-review.md`
- `md/handoffs/reports/WP-1.3.1-validation-review.md`
- `md/handoffs/reports/WP-1.3.2-validation-review.md`
- `md/handoffs/reports/WP-1.4-validation-review.md`
- `md/handoffs/reports/CO-1-validation-review.md`

If any dependency is missing, return `blocked` and state the exact missing validation report.

## Source Of Truth
Read these before editing:

- `md/master-plan.md`, especially Sections 2, 5, and 6 / WP-2.1
- `md/change-order-01.md`, especially CO-1 link-back behavior
- `md/development-ledger.md`
- `md/agent-operating-notes.md`
- `md/handoffs/reports/CO-1-validation-review.md`

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

- Functional `chronicle search <query>`.
- Functional `chronicle open <conversation-id>`.
- A small `src/chat_chronicle/search.py` query layer for FTS search/open helpers.
- `--db-path` option on `chronicle search` and `chronicle open`.
- Search filters already present in the CLI signature:
  - `--provider`
  - `--since`
  - `--until`
  - `--tag`
  - `--limit`
- Ranked FTS5 search using `chat_fts MATCH` and `bm25(chat_fts)`.
- Rich table output with result id, date, provider/source, title, snippet, and link/open hint.
- `open` behavior:
  - web-source rows with `url`: print the URL and attempt to open it with the standard-library browser helper;
  - local-store rows with no `url`: render the stored transcript and print `origin_path` plus `resume_hint` when present;
  - rows with neither `url` nor `origin_path`: render the stored transcript and clearly state that no source link is available.
- Tests using synthetic fixtures and temporary DBs only.

Do not implement:

- Claude Code extraction.
- Cursor/Gemini/new importers.
- `collect`.
- `ingest-folder`.
- `scan-local`.
- `source add/list/disable`.
- `note`.
- rename to WorkTrail.
- MCP server behavior.
- enrichment, smart search, query rewriting, embeddings, hybrid search, reranking, or local LLM behavior.
- adapter base/protocol abstraction.

## CLI Requirements

### `chronicle search`
Current stub signature already includes:

```text
chronicle search QUERY --provider PROVIDER --since DATE --until DATE --tag TAG --limit N
```

Add:

```text
--db-path PATH
```

Expected behavior:

- Empty or whitespace-only query exits non-zero with a clear message.
- Query uses FTS5 `MATCH`.
- Results are ordered by FTS rank, best first.
- Default limit remains 10.
- Limit must be validated to a reasonable positive value. Recommended: `1 <= limit <= 100`.
- If the DB is empty or no results match, print a clear zero-results message and exit 0.
- If the DB path does not exist, opening through `connect()` may initialize an empty DB; the command should then show zero results, not crash.

Output should include enough information for the user to run `chronicle open <id>`:

```text
id | date | provider | title | snippet | link/open hint
```

Use Rich for display, but keep output testable by including stable strings such as `No results` and visible result IDs.

### `chronicle open`
Current stub signature is:

```text
chronicle open <result-id>
```

Add:

```text
--db-path PATH
```

Interpret `result-id` as `conversations.id`.

Expected behavior:

- Missing conversation ID exits non-zero with a clear message.
- Web-source rows with `url`:
  - print title/provider/date/url;
  - attempt to open `url` using Python standard library `webbrowser.open(url)`;
  - do not fail the command if the browser launch returns false or raises a local OS error; print the URL either way so the user has the link.
- Local-store rows without `url`:
  - print title/provider/date;
  - print `origin_path` if present;
  - print `resume_hint` if present;
  - render messages ordered by `seq`, including role labels and timestamps when available.
- For testability, design the implementation so browser launching can be disabled or monkeypatched. Recommended: keep browser-opening inside a tiny helper function in `cli.py` or `search.py`.

## Search Query Layer Requirements
Implement the reusable logic in `src/chat_chronicle/search.py` rather than burying all SQL in `cli.py`.

Recommended public functions/classes:

```python
@dataclass(frozen=True)
class SearchResult:
    conversation_id: int
    provider: str
    title: str | None
    updated_at: str | None
    url: str | None
    origin_path: str | None
    resume_hint: str | None
    snippet: str
    rank: float

def search_conversations(
    conn: sqlite3.Connection,
    query: str,
    *,
    provider: str | None = None,
    since: str | None = None,
    until: str | None = None,
    tag: str | None = None,
    limit: int = 10,
) -> list[SearchResult]: ...

def get_conversation_detail(
    conn: sqlite3.Connection,
    conversation_id: int,
) -> ConversationDetail | None: ...
```

You may choose a different shape if simpler, but keep the query layer small and directly testable.

## FTS And Snippet Requirements
Use the existing `chat_fts` table populated by `rebuild_fts(conn)`.

Important implementation detail: the current FTS5 table is contentless (`content=''`). Depending on the SQLite build, `snippet(chat_fts, ...)` may not return useful text because contentless FTS stores the index but not retrievable column content.

Required behavior:

- Use FTS5 `MATCH` and `bm25(chat_fts)` for result selection and ranking.
- First try SQLite `snippet()` if it works with the current table.
- If `snippet()` returns empty/NULL/unhelpful text, build a deterministic fallback snippet in Python from title and message bodies for the matched conversation.
- The fallback snippet must be short, stable, and include the matched term when practical.
- Tests must prove the displayed snippet contains useful text from a matched message.

## Filter Requirements

### Provider
`--provider chatgpt` limits results to `conversations.provider = 'chatgpt'`.

Do not restrict provider values to the current three providers. The schema keeps provider open-set; accept any string and return zero results if absent.

### Date Filters
`--since` and `--until` should filter conversation dates.

Recommended field:

```sql
coalesce(conversations.updated_at, conversations.created_at)
```

Input may be:

- `YYYY-MM-DD`
- ISO timestamp accepted by SQLite string comparison if normalized

Keep this simple in WP-2.1. Validate obviously malformed dates enough to avoid confusing SQL behavior, but do not build a full date parser framework.

### Tag Filter
`--tag` should filter against existing enrichment/knowledge tag fields where present:

- `enrichments.tags_json`
- `knowledge_items.tags_json`

No enrichment worker exists yet, so fixture tests may insert synthetic enrichment/tag rows directly.

Keep tag matching simple and documented. A string containment check is acceptable for WP-2.1; no JSON1 dependency is required.

## Link-Back Requirements
Use accepted CO-1 fields:

- Web sources:
  - `url` should be present for ChatGPT and Claude official exports.
  - `chronicle open <id>` prints and attempts to launch the URL.
- Local-store sources:
  - `url` is normally NULL.
  - `origin_path` should be printed.
  - `resume_hint` should be printed only when non-empty.
  - transcript is rendered from normalized `messages`.

Tests must exercise both:

- a web-source row with URL;
- a local-store row with `origin_path` and no URL.

## Performance Requirement
Master plan AC says p95 < 100 ms on 5k conversations.

For this handoff:

- Add a focused synthetic performance smoke test or benchmark-style test that seeds enough rows to catch obviously non-indexed behavior.
- Do not make the test flaky or machine-sensitive.
- Recommended: insert/rebuild a few hundred synthetic conversations and assert search returns quickly under a generous threshold, or document why full p95 validation is deferred to real archive/prototype validation.

The completion report must state what was measured and what remains to validate on a larger archive.

## Tests Required
Add focused tests, likely in `tests/test_search.py` and/or `tests/test_cli_search_open.py`.

Minimum required scenarios:

- Search finds a term from an ingested ChatGPT fixture.
- Search finds a term from an ingested Claude fixture.
- Search finds a term from an ingested OpenAI Codex fixture.
- Results include conversation IDs usable by `chronicle open`.
- Results are ranked using FTS5 and return a useful snippet.
- `--provider` filters results.
- `--since` filters results.
- `--until` filters results.
- `--tag` filters results using synthetic enrichment/tag rows.
- `--limit` limits results and rejects invalid values.
- Empty query exits non-zero with a clear message.
- No-match query exits 0 with a clear zero-results message.
- Search against an empty/new DB does not crash.
- `open` for ChatGPT/Claude web rows prints title/provider/url and calls or can call the browser helper.
- `open` for OpenAI Codex/local rows prints transcript, `origin_path`, and `resume_hint` when present.
- `open` missing ID exits non-zero clearly.
- Existing WP-1.4 ingest/stats behavior still passes.
- Existing CO-1 migration/link-back tests still pass.

Use synthetic fixtures only. Do not use real exports or private history.

## Acceptance Criteria
WP-2.1 is complete only when all of these are true:

- `chronicle search` is functional.
- `chronicle search --db-path <path>` works.
- Search uses FTS5 `MATCH` and `bm25(chat_fts)` ranking.
- Search output includes result IDs, provider, date, title, useful snippet, and link/open hint.
- `--provider`, `--since`, `--until`, `--tag`, and `--limit` work.
- Empty query and invalid limit fail clearly.
- No results and empty DB are handled cleanly.
- `chronicle open <id> --db-path <path>` is functional.
- `open` handles URL rows by printing and attempting to launch the URL.
- `open` handles local-store rows by printing transcript plus `origin_path` and `resume_hint` when present.
- CO-1 link-back fields are exercised in tests.
- No Claude Code/Cursor/Gemini/importer/collect/source-management/note/rename behavior is implemented.
- No adapter base/protocol is introduced.
- Tests use synthetic fixtures only.
- `poetry run pytest` passes.
- `poetry run ruff check .` passes.
- `poetry run chronicle --help` still lists all existing commands.

## Evidence Required
The executor must write a detailed completion report to:

```text
md/handoffs/reports/WP-2.1-completion-report.md
```

The report must include:

- Changed-files summary.
- Dependency confirmation that WP-1.1 through WP-1.4 and CO-1 are accepted.
- Exact command output or concise pasted result for:
  - `poetry env info --path`
  - `poetry run pytest`
  - `poetry run ruff check .`
  - `poetry run chronicle --help`
  - at least one ingest command used to prepare a temp DB;
  - at least one `chronicle search` command that returns results;
  - at least one `chronicle search` command that returns no results;
  - at least one `chronicle open` command for a web-source row;
  - at least one `chronicle open` command for a local-store row.
- Test names covering all required scenarios.
- Statement of how snippets are produced, including whether SQLite `snippet()` or fallback snippets are used.
- Performance evidence or a clear statement of what was deferred to real archive validation.
- Confirmation that no real exports, real Codex sessions, DB files, zip exports, secrets, auth files, or local private data were committed.
- Explicit checklist mapping each acceptance criterion to `pass`, `fail`, or `not attempted`.

## Completion Report Format
Use this exact structure:

```markdown
# WP-2.1 Completion Report

## Status
One of:

- ready for PM validation
- blocked

## Dependency Check
Confirm WP-1.1 through WP-1.4 and CO-1 are accepted, with validation report paths.

## Summary
Briefly describe search/open behavior.

## Changed Files
List every changed or created file with a one-line purpose.

## Search Behavior
Describe FTS query, ranking, filters, snippets, empty/no-result handling, and DB path handling.

## Open Behavior
Describe web URL behavior and local transcript/link-back behavior.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| `chronicle search` functional | pass/fail/not attempted |  |
| `search --db-path` works | pass/fail/not attempted |  |
| FTS5 `MATCH` + `bm25` ranking used | pass/fail/not attempted |  |
| Search output includes required columns | pass/fail/not attempted |  |
| Provider/since/until/tag/limit filters work | pass/fail/not attempted |  |
| Empty query and invalid limit fail clearly | pass/fail/not attempted |  |
| No results and empty DB handled cleanly | pass/fail/not attempted |  |
| `chronicle open` functional | pass/fail/not attempted |  |
| Web URL rows print and launch URL | pass/fail/not attempted |  |
| Local rows print transcript and link-back fields | pass/fail/not attempted |  |
| CO-1 link-back fields exercised in tests | pass/fail/not attempted |  |
| No out-of-scope behavior implemented | pass/fail/not attempted |  |
| No adapter base/protocol added | pass/fail/not attempted |  |
| Synthetic fixtures only | pass/fail/not attempted |  |
| `poetry run pytest` passes | pass/fail/not attempted |  |
| `poetry run ruff check .` passes | pass/fail/not attempted |  |
| `poetry run chronicle --help` still lists commands | pass/fail/not attempted |  |

## Command Evidence
Paste concise output for all required evidence commands.

## Performance Evidence
State what was measured and whether larger real-archive p95 validation remains.

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement Claude Code/Cursor/Gemini/new importers | pass/fail |  |
| Did not implement collect/ingest-folder/source management/note | pass/fail |  |
| Did not implement rename/MCP/enrichment/smart search | pass/fail |  |
| Did not add adapter base/protocol | pass/fail |  |
| Did not commit real exports/private data or DB files | pass/fail |  |

## Risks Or Follow-Ups
List known issues, assumptions, or recommended follow-up tasks.
```

## Technical Guardrails
- Keep `search.py` small and testable.
- Use stdlib SQLite and existing Rich/Typer dependencies only.
- Preserve accepted ingest/stats behavior.
- Do not rename package, command, or docs in this work package.
- Do not add LLM, embedding, MCP, or browser-extension dependencies.
- Do not commit generated DBs, exports, private histories, or secrets.

## Completion Status Expected
Return one of:

- `ready for PM validation`
- `blocked`

If blocked, include:

- exact blocker;
- what was attempted;
- what decision or missing information is needed.
