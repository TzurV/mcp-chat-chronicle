# WP-2.3.1 Validation Review: Search Result UX Polish

## Decision

**Accepted.**

WP-2.3.1 satisfies the handoff. Phrase search now sorts title matches first, then newest last activity date first, then conversation id descending. Default broad search remains on the existing FTS5 + BM25 path. Default `chronicle search` output no longer prints duplicate `result ...` rows after the Rich table.

## Reviewed Materials

- `md/handoffs/WP-2.3.1-search-result-ux-polish.md`
- `md/handoffs/reports/WP-2.3.1-completion-report.md`
- `src/chat_chronicle/search.py`
- `src/chat_chronicle/cli.py`
- `tests/test_search.py`
- `tests/test_cli_search_open.py`

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
36 passed
```

```powershell
poetry run pytest
```

Result:

```text
166 passed
```

```powershell
poetry run ruff check .
```

Result:

```text
All checks passed!
```

```powershell
poetry run chronicle search --help
```

Result: help still documents `--phrase` and existing search filters.

```powershell
git diff --check
```

Result: no whitespace errors.

## Private DB Smoke

Against the repo-local private DB:

```powershell
poetry run chronicle search --phrase "YOU are the MANAGER" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
poetry run chronicle search "YOU are the MANAGER" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
```

Privacy-safe outcome:

- Phrase search returned conversation `673` first among body-only phrase matches due to recency.
- Broad search still printed the query guidance hint.
- Duplicate plain `result ...` rows were absent by default.
- No private transcript text is included in this review.

## Acceptance Notes

- Default broad search still orders by BM25 rank and conversation id.
- Phrase search remains exact lexical matching and does not use BM25, which is appropriate because all returned rows contain the same phrase.
- No `--plain` mode was added; this keeps the WP small and preserves the requested default human output.
- `chronicle recent` behavior was not changed.

## Residual Risk

- Phrase search still does not match phrases split across message boundaries.
- Script-friendly search output is not available after removing duplicate rows; add a deliberate `--plain` option only if a future automation use case needs it.

## Final Status

WP-2.3.1 is accepted and ready to commit.
