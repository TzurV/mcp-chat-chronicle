# WP-2.2 Handoff: Recent Active Chats CLI

## Objective

Add a simple CLI command that lists the most recently active conversations in a table, sorted by last activity date.

All dates in this work package refer to **last activity date**, defined as:

```sql
coalesce(conversations.updated_at, conversations.created_at)
```

The owner-requested shape is:

```text
ID - Date - Provider - Title - URL
```

## Source Of Truth

Read before implementation:

- `md/master-plan.md`
- `md/development-ledger.md`
- `md/agent-operating-notes.md`
- `src/chat_chronicle/cli.py`
- `src/chat_chronicle/search.py`
- `src/chat_chronicle/db.py`
- `tests/test_cli_search_open.py`
- `tests/test_search.py`

## Required Poetry Preflight

Before running Poetry commands:

```powershell
poetry env info --path
```

Expected:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If it points elsewhere, stop and fix the shell according to `md/agent-operating-notes.md`.

## Proposed CLI

Add a new command:

```powershell
poetry run chronicle recent -n 20 --db-path .\.chronicle\chronicle.db
```

Options:

- `-n`, `--limit`: number of rows to show; default `10`;
- `--provider`: optional provider filter;
- `--since`: optional lower bound on last activity date;
- `--until`: optional upper bound on last activity date;
- `--db-path`: existing DB path option pattern.

Date filters should use the same interpretation as search:

- date-only `--since 2026-07-01` means start of that UTC day;
- date-only `--until 2026-07-13` means end of that UTC day;
- ISO datetime strings should be accepted consistently with existing search behavior if already supported by helper code.

Do not add a root-level `chronicle -n` option. A dedicated `recent` command is clearer and avoids confusing global CLI behavior.

## Output Requirements

Use a Rich table consistent with existing CLI style.

Required columns:

- `ID`
- `Date`
- `Provider`
- `Title`
- `URL`

For local sources without a URL, the `URL` column should show a compact local hint instead of being misleading:

- web-backed rows: actual `url`;
- local rows with `origin_path`: `local: <origin_file>` or similar;
- local rows with `resume_hint`: optional extra hint if it fits cleanly;
- rows with neither: blank or `-`.

Sort:

- newest last activity first;
- stable tie-breaker by conversation id descending.

Empty DB or no matching rows should print `No conversations` and exit zero.

## Scope

Implement:

- query helper for recent conversations;
- CLI command `recent`;
- tests for query helper and CLI behavior;
- completion report at:

```text
md/handoffs/reports/WP-2.2-completion-report.md
```

Do not implement:

- search ranking changes;
- pagination beyond `-n`;
- interactive UI;
- source management;
- semantic sorting;
- browser open behavior changes.

## Tests Required

Add focused tests for:

- default recent list returns 10 max and sorts by last activity descending;
- `-n` / `--limit` works and rejects invalid values such as `0`;
- provider filter works;
- `--since` and `--until` use last activity date;
- rows use `updated_at` over `created_at`;
- rows with only `created_at` still appear;
- URL-backed and local-origin rows display expected URL/local hints;
- empty DB prints `No conversations` and exits zero;
- `chronicle --help` includes the new `recent` command.

## Required Validation Evidence

Include exact command output for:

```powershell
poetry env info --path
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
```

Also include a manual smoke against the repo-local private DB, reporting only table shape/counts, not private titles if sensitive:

```powershell
poetry run chronicle recent -n 10 --db-path .\.chronicle\chronicle.db
poetry run chronicle recent -n 5 --provider chatgpt --db-path .\.chronicle\chronicle.db
poetry run chronicle recent -n 5 --since 2026-01-01 --until 2026-12-31 --db-path .\.chronicle\chronicle.db
```

## Completion Report Requirements

Write:

```text
md/handoffs/reports/WP-2.2-completion-report.md
```

The report must include:

- status: `ready for PM validation`, `partial`, or `blocked`;
- files changed;
- command syntax;
- date semantics;
- sorting semantics;
- test evidence;
- manual smoke evidence;
- git status summary confirming no private DB/export artifacts are tracked;
- known limitations and follow-ups.

## Acceptance Criteria

WP-2.2 is complete when:

- `chronicle recent -n <N>` works;
- output table includes ID, Date, Provider, Title, URL/local hint;
- sorting is by last activity date descending;
- `--since` and `--until` filter on last activity date;
- provider filter works;
- tests and Ruff pass;
- existing `search` and `open` behavior does not regress.
