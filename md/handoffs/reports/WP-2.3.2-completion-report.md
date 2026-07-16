# WP-2.3.2 Completion Report: Search FTS Special-Character Escaping

## Status

ready for PM validation

## Files Changed

- `src/chat_chronicle/search.py` - added `_build_broad_match_query` helper that
  converts raw user text into a safe FTS5 `MATCH` expression, and wired default
  broad search to use it (including a friendly no-results path for
  punctuation-only queries).
- `tests/test_search.py` - added helper-level coverage for hyphenated terms,
  FTS special-character inputs, punctuation-only queries, and continued
  multi-token broad matching.
- `tests/test_cli_search_open.py` - added CLI coverage for `search "scan-local"`,
  FTS-special-character inputs, punctuation-only no-results, and
  `search --phrase "scan-local"` staying exact.
- `md/handoffs/reports/WP-2.3.2-completion-report.md` - this report.

## FTS5 Failure Mode

Default broad search passed the raw, unmodified query string straight into
`chat_fts MATCH ?`. SQLite FTS5 interprets that value as an FTS query
expression, not as plain text, so ordinary punctuation is treated as reserved
syntax:

- `scan-local` -> `-` is a column-filter / `NOT` operator, so FTS5 read
  `local` as a column name: `no such column: local`.
- `provider:openai_codex` -> `:` is a column filter: `no such column: provider`.
- `(scan-local)` -> grouping plus the `-` operator: `no such column: local`.
- `C:\SyntheticUser\.codex` -> `:` column filter: `no such column: C`.
- `scan/local` -> `fts5: syntax error near "/"`.
- `()` -> `fts5: syntax error near ")"`.

Each surfaced to the CLI as `Invalid search query: <sqlite error>` with a
non-zero-feeling failure, which is what the owner smoke hit for
`chronicle search "scan-local"`.

## Sanitization / Escaping Approach

`_build_broad_match_query` treats the query as plain text:

- extract searchable terms with `re.findall(r"[\w]+", query)` (Unicode-aware),
  which drops reserved punctuation and control syntax entirely;
- emit each term as a double-quoted FTS5 string literal (embedded quotes are
  doubled defensively), so a term can never be parsed as an operator, column
  reference, prefix, or grouping token;
- join the quoted terms with spaces, giving FTS5's existing implicit-AND broad
  match;
- return `None` when no searchable terms remain (e.g. `()`, `-.,/`), in which
  case default search returns an empty result list and the CLI prints
  `No results` and exits zero rather than passing syntax to FTS5.

The `MATCH` value remains a bound SQL parameter (`chat_fts MATCH ?`); no user
input is interpolated into SQL. Hyphenated input like `scan-local` splits into
independent `scan` and `local` terms, per the handoff's accepted broad-search
semantics; exact hyphen matching remains the job of `--phrase`.

Real database errors unrelated to FTS query syntax are not swallowed: the CLI
still surfaces `sqlite3.OperationalError` via the existing `Invalid search
query` path, which the sanitized broad query no longer triggers for ordinary
punctuation.

## Broad Search Still Uses FTS5 / BM25

Unchanged. The default path still runs `chat_fts MATCH ?`, ranks with
`bm25(chat_fts)`, uses `snippet(chat_fts, ...)`, and keeps
`ORDER BY rank ASC, c.id ASC` plus all existing provider/date/tag/limit
filters. Only the value bound to `MATCH` is now a sanitized plain-text
expression instead of raw input.

## `--phrase` Behavior Unchanged

`--phrase` continues to use `_search_phrase_conversations` with parameterized
`instr(lower(...), lower(?))` exact substring matching over titles, message
bodies, and linked project names, with the WP-2.3.1 ordering (title matches
first, then last-activity descending, then id descending). No phrase code was
touched. `chronicle search --phrase "scan-local"` still performs exact-phrase
matching, verified by a new CLI test and manual smoke.

## Test Results

```powershell
poetry env info --path
```

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

```powershell
poetry run pytest tests/test_search.py tests/test_cli_search_open.py -q
```

```text
..................................................                       [100%]
```

```powershell
poetry run pytest
```

```text
233 passed in 28.99s
```

```powershell
poetry run ruff check .
```

```text
All checks passed!
```

## Manual Validation Output Summary

`poetry run chronicle --help` exited 0 and lists the `search` command.

Broad and phrase smoke against the repo-local private DB
(`.\.chronicle\chronicle.db`, gitignored) with `CHAT_CHRONICLE_NO_BROWSER=1`:

```powershell
poetry run chronicle search "scan-local" --db-path .\.chronicle\chronicle.db
poetry run chronicle search --phrase "scan-local" --db-path .\.chronicle\chronicle.db
```

Privacy-safe observations:

- both commands exited 0 and rendered a "Search results" table;
- `Invalid search query` did not appear in stdout or stderr (0 occurrences);
- broad `scan-local`: 20 result rows (previously crashed with
  `no such column: local`);
- phrase `scan-local`: 15 result rows (exact substring, unchanged behavior);
- existing broad multi-token search still works: `docker network` returned
  20 result rows.

FTS-special-character inputs were exercised via the new tests and confirmed to
not raise: `provider:openai_codex`, `"scan-local"`, `(scan-local)`,
`C:\SyntheticUser\.codex`, and `scan/local`. Punctuation-only input `()` returns
a friendly `No results` with no SQLite exception.

No private transcript bodies are included in this report.

## Git Status Summary

WP-2.3.2 tracked changes:

```text
 M src/chat_chronicle/search.py
 M tests/test_cli_search_open.py
 M tests/test_search.py
?? md/handoffs/WP-2.3.2-search-fts-special-character-escaping.md
?? md/handoffs/reports/WP-2.3.2-completion-report.md
```

Pre-existing, unrelated workspace state present before this WP and not modified
by it:

```text
 M md/development-ledger.md
 M src/chat_chronicle/cli.py
 M src/chat_chronicle/scan.py
 M tests/test_cli.py
?? md/handoffs/reports/WP-1.5-completion-report.md
?? md/handoffs/reports/WP-1.5-validation-review.md
?? tests/test_cli_scan_local.py
```

The private database `.chronicle/chronicle.db` is gitignored
(`git check-ignore` confirms it) and is not tracked. No private DB, export,
JSONL, ZIP, or generated dump artifacts were added by this WP.

## Known Limitations And Follow-Ups

- Broad search tokenizes hyphenated and path-like input into independent AND
  terms (e.g. `scan-local` -> `scan` AND `local`); it does not preserve the
  original adjacency. Exact-substring intent is served by `--phrase`.
- The FTS index uses the `porter unicode61` tokenizer, so stemmed variants
  still match in broad search (e.g. `network` matches `networking`). This is
  pre-existing behavior and is unchanged by this WP.
- No advanced/explicit FTS query language was added; default input is always
  treated as safe plain text.
