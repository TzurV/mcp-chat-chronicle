# WP-2.3.1 Completion Report: Search Result UX Polish

## Status

ready for PM validation

## Files Changed

- `src/chat_chronicle/search.py`
- `src/chat_chronicle/cli.py`
- `tests/test_search.py`
- `tests/test_cli_search_open.py`
- `md/handoffs/reports/WP-2.3.1-completion-report.md`

## Phrase Ordering Summary

Default broad search remains on the existing FTS5 `MATCH` plus `bm25(chat_fts)` path and keeps its existing `ORDER BY rank ASC, c.id ASC`.

Phrase search remains exact case-insensitive substring matching against conversation titles and message bodies. Its ordering is now:

1. title matches first;
2. `coalesce(conversations.updated_at, conversations.created_at)` descending;
3. conversation id descending.

Focused tests cover title matches outranking newer body-only matches, body-only matches sorting by newest last activity, and timestamp ties sorting by id descending.

## Search Output Summary

`chronicle search` now prints the Rich search-results table only, plus the broad-search guidance hint when applicable. The duplicate plain `result ...` rows were removed from default search output. No `--plain` or debug output mode was added.

Existing `chronicle recent` behavior was left unchanged.

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
....................................                                     [100%]
```

```powershell
poetry run pytest
```

```text
........................................................................ [ 43%]
........................................................................ [ 86%]
......................                                                   [100%]
166 passed in 11.16s
```

```powershell
poetry run ruff check .
```

```text
All checks passed!
```

```powershell
poetry run chronicle search --help
```

```text
Usage: chronicle search [OPTIONS] QUERY

 Search the archive with FTS5 ranking and snippets.

+- Arguments -----------------------------------------------------------------+
| *    query      TEXT  Full-text search query. [required]                    |
+-----------------------------------------------------------------------------+
+- Options -------------------------------------------------------------------+
| --phrase                   Treat QUERY as an exact phrase instead of broad  |
|                            FTS terms.                                       |
| --provider        TEXT     Filter by provider.                              |
| --since           TEXT     Only results on or after this ISO date.          |
| --until           TEXT     Only results on or before this ISO date.         |
| --tag             TEXT     Filter by enrichment tag.                        |
| --limit           INTEGER  Maximum number of results. [default: 10]         |
| --db-path         PATH     SQLite database path. Defaults to                |
|                            CHAT_CHRONICLE_DB or .chronicle.                 |
| --help                     Show this message and exit.                      |
+-----------------------------------------------------------------------------+
```

Note: the privacy-filtered private DB smoke commands initially hit the known Windows sandbox launcher failure `CreateProcessAsUserW failed: 1312`; they were rerun with escalation and did not print private transcript text.

## Privacy-Safe Manual Smoke Evidence

Commands exercised:

```powershell
poetry run chronicle search --phrase "YOU are the MANAGER" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
poetry run chronicle search "YOU are the MANAGER" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
```

Privacy-safe observed facts:

- phrase command exited zero;
- ordered phrase helper IDs started `673,544,482`;
- conversation `673` was position 1 among phrase matches;
- title-hit flags for the top phrase IDs were `673:0,544:0,482:0`, so `673` was first among body-only matches due to recency;
- phrase search duplicate plain rows: `0`;
- broad search printed the query guidance hint;
- broad search duplicate plain rows: `0`.

## Git Status Summary

Final `git status --short` showed only intended source/test changes and this report:

```text
 M src/chat_chronicle/cli.py
 M src/chat_chronicle/search.py
 M tests/test_cli_search_open.py
 M tests/test_search.py
?? md/handoffs/reports/WP-2.3.1-completion-report.md
```

No private DB, export, JSONL, or generated dump artifacts were tracked.

## Known Limitations And Follow-Ups

- Phrase search remains exact lexical matching and does not match across message boundaries.
- No machine-readable `chronicle search --plain` mode was added; add one only if a future scripted-output use case needs it.
- Windows sandbox launcher failures remain an environment issue documented in `md/agent-operating-notes.md`; they did not indicate validation failure.
