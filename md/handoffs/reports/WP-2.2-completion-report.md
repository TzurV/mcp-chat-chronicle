# WP-2.2 Completion Report

## Status

ready for PM validation

## Files Changed

- `src/chat_chronicle/search.py` - added `RecentConversation` and `list_recent_conversations()`; aligned date-only lower-bound normalization with stored microsecond UTC timestamps.
- `src/chat_chronicle/cli.py` - added `chronicle recent` with `-n/--limit`, `--provider`, `--since`, `--until`, and `--db-path`.
- `tests/test_search.py` - added query-helper coverage for default limit, sorting, provider/date filters, updated-over-created semantics, created-only rows, tie-breaking, and validation.
- `tests/test_cli_search_open.py` - added CLI coverage for table columns, URL/local hints, provider/date filters, empty DB behavior, invalid limit, and help output.
- `md/handoffs/reports/WP-2.2-completion-report.md` - this report.

Pre-existing worktree state before implementation:

- modified `md/development-ledger.md`;
- untracked `md/handoffs/WP-1.3.3-claude-project-metadata-linking.md`;
- untracked `md/handoffs/WP-2.2-recent-active-chats-cli.md`.

Those files were not changed by this implementation.

## Command Syntax

```powershell
poetry run chronicle recent -n 20 --db-path .\.chronicle\chronicle.db
poetry run chronicle recent --limit 20 --provider chatgpt --since 2026-07-01 --until 2026-07-13 --db-path .\.chronicle\chronicle.db
```

Output columns:

- `ID`
- `Date`
- `Provider`
- `Title`
- `URL`

For URL-backed conversations, `URL` is the stored web URL. For local rows with `origin_path`, it shows `local: <origin_file>`. If no URL or origin path exists, it falls back to `resume_hint`, then `-`.

## Date Semantics

All filters use last activity date:

```sql
coalesce(conversations.updated_at, conversations.created_at)
```

Date-only filters normalize as:

- `--since YYYY-MM-DD` -> `YYYY-MM-DDT00:00:00.000000Z`
- `--until YYYY-MM-DD` -> `YYYY-MM-DDT23:59:59.999999Z`

ISO datetime strings are accepted through the existing shared parser. Invalid date filters return a non-zero CLI result with `Invalid date filter`.

## Sorting Semantics

Rows sort by:

```sql
ORDER BY last_activity_at DESC, conversations.id DESC
```

Rows without either `updated_at` or `created_at` are omitted from `recent`.

## Test Evidence

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

```text
poetry run pytest
........................................................................ [ 47%]
........................................................................ [ 95%]
.......                                                                  [100%]
151 passed in 15.39s
```

```text
poetry run ruff check .
All checks passed!
```

```text
poetry run chronicle --help
Commands include:
recent         List the most recently active conversations.
```

Focused checks also passed:

```text
poetry run pytest tests/test_search.py tests/test_cli_search_open.py -q
.....................                                                    [100%]
```

## Manual Smoke Evidence

The following commands were run against `.chronicle\chronicle.db`. Private titles/URLs are not reproduced here.

```powershell
poetry run chronicle recent -n 10 --db-path .\.chronicle\chronicle.db
```

Result: exited zero; rendered the `Recent conversations` table with columns `ID`, `Date`, `Provider`, `Title`, `URL`; returned 10 rows; newest row was a local `claude_code` row with a `local: <jsonl>` hint, followed by `chatgpt` URL-backed rows.

```powershell
poetry run chronicle recent -n 5 --provider chatgpt --db-path .\.chronicle\chronicle.db
```

Result: exited zero; rendered 5 rows; all rows were provider `chatgpt`; URL column used web URLs.

```powershell
poetry run chronicle recent -n 5 --since 2026-01-01 --until 2026-12-31 --db-path .\.chronicle\chronicle.db
```

Result: exited zero; rendered 5 rows active within the 2026 date window; included both local-origin and web-backed row shapes.

## Git Status And Artifact Check

```text
git status --short --untracked-files=all
 M md/development-ledger.md
 M src/chat_chronicle/cli.py
 M src/chat_chronicle/search.py
 M tests/test_cli_search_open.py
 M tests/test_search.py
?? md/handoffs/WP-1.3.3-claude-project-metadata-linking.md
?? md/handoffs/WP-2.2-recent-active-chats-cli.md
?? md/handoffs/reports/WP-2.2-completion-report.md
```

```text
git ls-files exports *.zip *.db .chronicle
<no output>
```

No private DB, export, ZIP, or generated artifact is tracked.

## Known Limitations And Follow-Ups

- `recent` is intentionally non-interactive and limited to simple `-n` retrieval; no pagination beyond the requested limit was added.
- The table includes full titles by design. For privacy-sensitive demos, use the command output locally but summarize only row counts and providers in reports.
- Date filtering remains string-based over the stored UTC ISO timestamps, matching existing search behavior.
