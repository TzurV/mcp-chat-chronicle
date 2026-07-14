# WP-2.3.2 Handoff: Search FTS Special-Character Escaping

## Status

Ready for executor.

## Context

Owner smoke found a default broad-search failure:

```powershell
poetry run chronicle search "scan-local"
```

Current behavior:

```text
Invalid search query: no such column: local
```

This is an FTS5 query parsing bug: ordinary user text containing `-` is being treated as FTS syntax instead of safe plain-text search input.

This work is a focused patch on the accepted WP-2.3/WP-2.3.1 search behavior.

## Required Preflight

Read:

- `md/agent-operating-notes.md`
- `md/handoffs/WP-2.3-search-phrase-query-guidance.md`
- `md/handoffs/WP-2.3.1-search-result-ux-polish.md`
- `md/handoffs/reports/WP-2.3-completion-report.md`
- `md/handoffs/reports/WP-2.3.1-completion-report.md`

Before running Poetry commands:

```powershell
poetry env info --path
```

Expected:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If Poetry resolves to any other environment, stop and fix the shell before running tests or installs.

## Objective

Make default broad search treat user-entered text as safe plain text, so punctuation and FTS5-reserved characters do not crash the CLI.

The command below must return matching rows or `No results`; it must not expose a SQLite/FTS parser error:

```powershell
poetry run chronicle search "scan-local"
```

## Scope

In scope:

- Default `chronicle search <query>` query sanitization/escaping.
- Tests for punctuation and FTS-special-character inputs.
- Clear user-facing behavior for empty or punctuation-only broad queries.
- Completion report.

Out of scope:

- Changing `--phrase` semantics.
- Replacing FTS5/BM25 broad search.
- Adding source CRUD, config changes, or new provider parsing.
- Reintroducing duplicate `result ...` output rows.
- Creating a general advanced FTS query language unless it is tiny, explicit, and separate from default user input.

## Required Behavior

- Default broad search remains FTS5 `MATCH` + `bm25(chat_fts)`.
- User text with hyphens, quotes, colons, parentheses, slashes, backslashes, and other punctuation does not raise SQLite parser errors.
- `scan-local` should be searchable as ordinary text. It is acceptable for broad search to tokenize this as `scan` and `local`; exact hyphen matching remains the job of `--phrase`.
- Existing token searches such as `docker network` must keep working.
- Existing provider, date, and limit filters must keep working.
- Existing broad-search query guidance must remain.
- Existing `--phrase` exact substring mode must remain unchanged.
- `chronicle search --phrase "scan-local"` must still use exact phrase behavior.

## Implementation Guidance

The likely fix is in the search layer that builds the FTS5 `MATCH` expression.

Treat default broad-search input as plain text:

- extract searchable terms from the user query;
- split hyphenated words into safe terms;
- quote or otherwise escape terms before passing them into FTS5 `MATCH`;
- drop pure punctuation/control syntax;
- keep SQL values parameterized;
- do not interpolate raw user input into SQL.

Prefer a small helper with focused unit tests, for example a helper that converts:

| User input | Safe broad-search intent |
| --- | --- |
| `scan-local` | `scan` AND/OR `local`, according to existing broad-search semantics |
| `C:\Users\tzurv\.codex` | searchable path-like terms, no parser crash |
| `"quoted text"` | searchable text terms, no parser crash |
| `provider:openai_codex` | searchable text terms, no parser crash |
| `()` | friendly no-searchable-terms result, no parser crash |

Do not silently swallow real database errors unrelated to FTS query syntax.

## Tests To Add Or Update

Add focused coverage in the existing search/CLI test files.

Required cases:

- `search_conversations(..., "scan-local")` does not raise and can find content containing `scan-local` or equivalent tokenized text.
- `chronicle search "scan-local"` exits zero and does not print `Invalid search query`.
- FTS-special-character inputs do not raise:
  - `provider:openai_codex`
  - `"scan-local"`
  - `(scan-local)`
  - `C:\Users\tzurv\.codex`
  - `scan/local`
- Existing broad token search still works, for example `docker network`.
- `chronicle search --phrase "scan-local"` remains exact phrase search.
- Existing query guidance still appears for broad noisy multi-word search when applicable.
- Punctuation-only or no-searchable-token input returns a friendly message and no SQLite exception.

## Manual Validation

Run:

```powershell
poetry env info --path
poetry run pytest tests/test_search.py tests/test_cli_search_open.py -q
poetry run pytest
poetry run ruff check .
poetry run chronicle search "scan-local"
poetry run chronicle search --phrase "scan-local"
poetry run chronicle --help
```

For private DB smoke, if available:

```powershell
poetry run chronicle search "scan-local" --db-path .\.chronicle\chronicle.db
poetry run chronicle search --phrase "scan-local" --db-path .\.chronicle\chronicle.db
```

Report only privacy-safe evidence: command status, row counts, provider/title summaries if needed. Do not paste private transcript bodies.

## Completion Report Required

Write:

```text
md/handoffs/reports/WP-2.3.2-completion-report.md
```

The report must include:

- status: `ready for PM validation`;
- files changed;
- explanation of the FTS5 failure mode;
- description of the sanitization/escaping approach;
- confirmation that broad search still uses FTS5/BM25;
- confirmation that `--phrase` behavior is unchanged;
- test results;
- manual validation output summary;
- git status summary confirming no private DB/export/JSONL/ZIP artifacts were added.

## Acceptance Criteria

- `chronicle search "scan-local"` no longer crashes.
- FTS punctuation/control-like input is treated as safe user text in default broad search.
- Broad search still uses FTS5/BM25.
- `--phrase` exact matching remains unchanged.
- Search result duplicate plain rows remain absent by default.
- Tests and Ruff pass.
- Completion report exists at the required path.
- No private artifacts are tracked.
