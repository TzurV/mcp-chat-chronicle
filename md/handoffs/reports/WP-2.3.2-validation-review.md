# WP-2.3.2 Validation Review: Search FTS Special-Character Escaping

## Status

Accepted.

## PM Summary

WP-2.3.2 satisfies the handoff. The default broad-search path now treats ordinary user input as plain text before passing it to SQLite FTS5, so punctuation such as hyphens, colons, parentheses, slashes, and path separators no longer causes FTS parser errors.

The implementation is narrowly scoped to broad-search query construction and tests. `--phrase` exact matching remains unchanged.

## Findings

No blocking findings.

One documented behavior remains intentionally unchanged: broad search uses tokenized FTS semantics, so `scan-local` is searched as safe broad terms rather than exact hyphen adjacency. Exact matching remains available through `--phrase`.

## Acceptance Checklist

| Requirement | Result | Evidence |
| --- | --- | --- |
| `chronicle search "scan-local"` no longer crashes | Pass | Manual private DB smoke exited 0 and rendered search results. |
| FTS punctuation/control-like input is treated as safe text | Pass | New tests cover `provider:openai_codex`, `"scan-local"`, `(scan-local)`, `C:\SyntheticUser\.codex`, and `scan/local`. |
| Broad search still uses FTS5/BM25 | Pass | Completion report confirms only the bound `MATCH` value changed; diff keeps FTS5 `MATCH`, `bm25(chat_fts)`, and snippets. |
| `--phrase` exact matching unchanged | Pass | Manual private DB smoke and tests confirm `chronicle search --phrase "scan-local"` still works. |
| Duplicate default `result ...` rows remain absent | Pass | No CLI regression indicated; WP-2.3.1 behavior was not touched. |
| Tests and Ruff pass | Pass | Focused tests, full test suite, and Ruff passed locally. |
| Completion report exists | Pass | `md/handoffs/reports/WP-2.3.2-completion-report.md`. |
| No private artifacts tracked | Pass | Report and `git status --short` show no DB/export/JSONL/ZIP files added. |

## Validation Commands

```powershell
poetry env info --path
```

Result:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

```powershell
poetry run pytest tests/test_search.py tests/test_cli_search_open.py -q
```

Result:

```text
50 passed
```

```powershell
poetry run pytest
```

Result:

```text
233 passed in 20.69s
```

```powershell
poetry run ruff check .
```

Result:

```text
All checks passed!
```

```powershell
poetry run chronicle search "scan-local" --db-path .\.chronicle\chronicle.db
poetry run chronicle search --phrase "scan-local" --db-path .\.chronicle\chronicle.db
poetry run chronicle --help
```

Result:

- broad `scan-local` search exited 0 and rendered a results table;
- phrase `scan-local` search exited 0 and rendered a results table;
- help output lists the expected commands, including `search`.

Private transcript bodies are intentionally not copied into this review.

## Scope Review

Changed files for this WP:

- `src/chat_chronicle/search.py`
- `tests/test_search.py`
- `tests/test_cli_search_open.py`
- `md/handoffs/WP-2.3.2-search-fts-special-character-escaping.md`
- `md/handoffs/reports/WP-2.3.2-completion-report.md`

The remaining dirty files in the workspace belong to already-reviewed WP-1.5/ledger state and are not part of this validation decision.

## Decision

Accept WP-2.3.2.

Next PM action: resume prototype owner smoke, then decide whether to schedule MCP recall, Cursor extractor, source-management polish, or release/rename preparation.
