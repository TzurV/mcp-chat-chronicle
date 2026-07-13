# WP-2.3 Completion Report

## Status

ready for PM validation

## Files Changed

- `src/chat_chronicle/search.py` - added exact phrase search mode and broad-query hint detection.
- `src/chat_chronicle/cli.py` - added `chronicle search --phrase` and prints broad-search guidance after results or no-results output.
- `tests/test_search.py` - added direct helper coverage for broad default search, phrase exactness, filters, limit, title ranking, embedded quotes, and hint detection.
- `tests/test_cli_search_open.py` - added CLI coverage for phrase mode, broad-query guidance, no-results guidance, one-word suppression, advanced FTS suppression, and `search --help`.
- `md/handoffs/reports/WP-2.3-completion-report.md` - this report.

## CLI Syntax Summary

```powershell
poetry run chronicle search --phrase "YOU are the MANAGER" --provider openai_codex --db-path .\.chronicle\chronicle.db
```

`--phrase` is a boolean option on `chronicle search`. Existing filters remain supported: `--provider`, `--since`, `--until`, `--tag`, `--limit`, and `--db-path`.

## Default Search Behavior

Default search behavior is unchanged: non-phrase searches still use `chat_fts MATCH ?`, `bm25(chat_fts)`, existing filters, and existing fallback snippets. Multi-word non-phrase queries remain broad FTS token searches.

## Phrase Search Behavior

Phrase mode performs parameterized exact-text matching over `conversations.title` and individual `messages.body` values using `instr(lower(...), lower(?))`. It does not return conversations that only contain some phrase tokens. Title matches sort before body-only matches; ties sort by conversation id ascending. If no phrase results match, the CLI prints `No results` and exits zero.

## Query Guidance Behavior

Non-phrase searches print:

```text
Hint: this was a broad token search. For exact phrase matching, use --phrase "..."
```

The hint appears after results or after `No results` when a query has multiple words and includes common stop-style terms such as `you`, `are`, or `the`. It is suppressed for one-word queries, `--phrase`, and queries that look like advanced FTS syntax such as quoted phrases or explicit FTS operators.

## Safety Notes

Phrase search does not build FTS query strings, so embedded quotes and malformed phrase text cannot become unsafe SQL or invalid FTS syntax. All phrase values are passed as SQL parameters. Default FTS search remains unchanged and continues to surface SQLite `OperationalError` as the existing `Invalid search query` CLI error.

## Validation Commands And Results

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
.................................                                        [100%]
```

```powershell
poetry run pytest
```

```text
163 passed in 13.25s
```

```powershell
poetry run ruff check .
```

```text
All checks passed!
```

```powershell
poetry run chronicle --help
```

Result: root help lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `recent`, `search`, and `open`.

```powershell
poetry run chronicle search --help
```

Result: search help includes `--phrase` with the exact phrase description, plus existing filter options.

## Privacy-Safe Manual Smoke Evidence

Commands run against `.\\.chronicle\\chronicle.db`:

```powershell
poetry run chronicle search --phrase "YOU are the MANAGER" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
poetry run chronicle search "YOU are the MANAGER" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
poetry run chronicle search "chat_chronicle" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
```

Results:

- Phrase search returned conversation `673`.
- Broad search printed the query guidance hint.
- Distinctive `chat_chronicle` search returned the expected row, conversation `673`.
- No private transcript text is included in this report.

## Git Status Summary

At report time, tracked code/test changes were limited to:

```text
M src/chat_chronicle/cli.py
M src/chat_chronicle/search.py
M tests/test_cli_search_open.py
M tests/test_search.py
```

Report/handoff files present:

```text
?? md/handoffs/WP-2.3-search-phrase-query-guidance.md
?? md/handoffs/reports/WP-2.3-completion-report.md
```

Pre-existing/unrelated workspace state noted and not modified by this WP:

```text
M md/development-ledger.md
```

No private DB, export, JSONL, ZIP, or generated dump artifacts are tracked.

## Known Limitations And Follow-Ups

- Phrase mode currently matches exact substrings in titles and individual message bodies. It does not match a phrase split across message boundaries.
- Phrase mode is intentionally exact lexical matching, not semantic/vector search.
- `chronicle open <id>` remains the current local OpenAI Codex viewing path. The `local: <origin_file>` value shown by recent/search-related output is a local transcript hint, not a web URL.
- No verified deep-link exists today to reopen the original Codex app chat like ChatGPT web URLs. Future local app/session navigation should wait for reliable Codex deep-link or resume behavior.
