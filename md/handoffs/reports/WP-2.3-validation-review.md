# WP-2.3 Validation Review: Search Phrase Mode And Query Guidance

## Decision

**Accepted.**

WP-2.3 satisfies the handoff. `chronicle search --phrase` provides exact lexical phrase matching for titles and message bodies, default FTS/BM25 search remains compatible, and broad multi-word token searches now print query guidance.

## Reviewed Materials

- `md/handoffs/WP-2.3-search-phrase-query-guidance.md`
- `md/handoffs/reports/WP-2.3-completion-report.md`
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
33 passed
```

```powershell
poetry run pytest
```

Result:

```text
163 passed
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

Result: help documents `--phrase` as exact phrase search and preserves existing filters.

## Private DB Smoke

Against the repo-local private DB:

```powershell
poetry run chronicle search --phrase "YOU are the MANAGER" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
poetry run chronicle search "YOU are the MANAGER" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
poetry run chronicle search "chat_chronicle" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
```

Privacy-safe outcome:

- Phrase search returned conversation `673`.
- Broad search printed the guidance hint.
- Distinctive `chat_chronicle` search returned the expected current-chat row.
- Phrase search also returned older exact lexical matches, which is acceptable because phrase mode is exact text matching, not current-conversation filtering.

## Ingest Idempotency Check

Per PM follow-up, OpenAI Codex ingest idempotency was checked against a copied DB:

```powershell
Copy-Item .\.chronicle\chronicle.db C:\tmp\chronicle-wp23-idempotency.db -Force
poetry run chronicle stats --db-path C:\tmp\chronicle-wp23-idempotency.db
poetry run chronicle ingest "$env:USERPROFILE\.codex" --provider openai_codex --db-path C:\tmp\chronicle-wp23-idempotency.db
poetry run chronicle stats --db-path C:\tmp\chronicle-wp23-idempotency.db
```

Before re-ingest:

- `openai_codex`: 238 conversations.

Re-ingest result:

- conversations seen: 239
- added: 1
- updated: 1
- skipped: 237
- source row reused: source ID 4

After re-ingest:

- `openai_codex`: 239 conversations.

Conclusion: records did not duplicate. One new Codex session appeared since the previous ingest, which explains the single added row.

## Acceptance Notes

- Phrase mode is implemented as parameterized exact substring matching rather than generated FTS query strings, which avoids malformed FTS syntax and SQL interpolation risk.
- Existing BM25 search remains the default path.
- Guidance is intentionally advisory; it does not change exit code or suppress broad-search results.
- The local Codex `local: <origin_file>` value remains a transcript hint, not an app deep-link. That gap is already recorded as backlog.

## Residual Risk

- Phrase search does not match across message boundaries.
- `chronicle open <id>` can still hit Windows console encoding issues for some local transcripts unless the shell uses UTF-8. This was not in WP-2.3 scope.
- Broad search still prints script-friendly `result ...` lines after the Rich table; this is existing `search` behavior and was not changed here.

## Final Status

WP-2.3 is accepted and ready to commit.
