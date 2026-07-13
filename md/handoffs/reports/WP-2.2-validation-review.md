# WP-2.2 Validation Review — Recent Active Chats CLI

## Decision

**Accepted.**

WP-2.2 satisfies the handoff. `chronicle recent` lists recently active conversations by last activity date and supports limit, provider, date range, and DB path options.

## Validation Performed

Reviewed:

- `md/handoffs/WP-2.2-recent-active-chats-cli.md`
- `md/handoffs/reports/WP-2.2-completion-report.md`
- `src/chat_chronicle/search.py`
- `src/chat_chronicle/cli.py`
- `tests/test_search.py`
- `tests/test_cli_search_open.py`

Commands run by PM validation:

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

```text
poetry run pytest tests/test_search.py tests/test_cli_search_open.py -q
21 passed
```

```text
poetry run pytest
151 passed
```

```text
poetry run ruff check .
All checks passed!
```

```text
poetry run chronicle --help
```

The CLI help includes `recent`.

## Private DB Smoke

Ran these against `.chronicle\chronicle.db`:

```text
poetry run chronicle recent -n 3 --db-path .\.chronicle\chronicle.db
poetry run chronicle recent -n 2 --provider chatgpt --db-path .\.chronicle\chronicle.db
poetry run chronicle recent -n 2 --since 2026-01-01 --until 2026-12-31 --db-path .\.chronicle\chronicle.db
```

All exited zero and rendered the expected table shape. The smoke confirmed:

- newest rows sort by `coalesce(updated_at, created_at) DESC, id DESC`;
- `chatgpt` provider filtering works;
- 2026 date-window filtering works;
- URL-backed rows show URLs;
- local-source rows show `local: <origin_file>` hints.

Private titles and transcript content are intentionally not reproduced in this review.

## Acceptance Notes

- The command is `chronicle recent`, not a global `chronicle -n`, which keeps CLI semantics clean.
- Date-only `--since` and `--until` handling is aligned with stored UTC timestamp strings.
- Rows without activity dates are omitted, which is acceptable for a "recent activity" view.
- Existing `search` and `open` tests still pass.

## Residual Risk

The command prints full titles and URLs by design. For public demos or reports, use row counts/provider summaries rather than pasted command output when titles may be private.

## Follow-Up

Commit WP-2.2. The remaining handoff-ready task is WP-1.3.3 for Claude export project metadata linking.
