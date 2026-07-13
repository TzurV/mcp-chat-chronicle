# WP-2.3.1 Handoff: Search Result UX Polish

## Objective

Polish the accepted WP-2.3 search behavior based on owner testing:

- keep default broad search as FTS5 + BM25;
- change phrase search ordering to title matches first, then newest activity first;
- remove duplicate `result ...` plain-text rows from default human output, or gate them behind a deliberately named option if script output is still needed.

This is a small follow-up to accepted WP-2.3, not a replacement for it.

## Source Of Truth

Read before implementation:

- `md/master-plan.md`
- `md/development-ledger.md`
- `md/agent-operating-notes.md`
- `md/handoffs/WP-2.3-search-phrase-query-guidance.md`
- `md/handoffs/reports/WP-2.3-validation-review.md`
- `src/chat_chronicle/search.py`
- `src/chat_chronicle/cli.py`
- `tests/test_search.py`
- `tests/test_cli_search_open.py`

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

## Current Behavior

Default search:

- uses FTS5 `MATCH`;
- ranks with `bm25(chat_fts)`;
- should remain unchanged.

Phrase search:

- uses exact case-insensitive substring matching against title and message bodies;
- does not use BM25;
- currently sorts by title-match rank first, then `conversation_id ASC`.

CLI output:

- `chronicle search` prints a Rich table;
- when results exist, it also prints duplicate plain rows beginning with `result ...`;
- this duplication is noisy for normal human use and should not be default output.

## Required Behavior

### Default Broad Search

Do not change default broad search ranking or matching semantics.

These commands should continue to use FTS5 + BM25:

```powershell
poetry run chronicle search "docker network" --db-path .\.chronicle\chronicle.db
poetry run chronicle search "YOU are the MANAGER" --provider openai_codex --db-path .\.chronicle\chronicle.db
```

### Phrase Search Ordering

For:

```powershell
poetry run chronicle search --phrase "YOU are the MANAGER" --provider openai_codex --db-path .\.chronicle\chronicle.db
```

Sort phrase results by:

1. title matches before body-only matches;
2. newest last activity date first, using:

```sql
coalesce(conversations.updated_at, conversations.created_at)
```

3. stable tie-breaker by conversation id descending.

Rationale:

- title matches are stronger intent;
- when phrase matches are otherwise equivalent, the user expects recently active conversations first;
- id descending is consistent with "newer row wins" when timestamps tie.

### Duplicate Plain Rows

Remove duplicated `result ...` lines from default `chronicle search` output.

Preferred behavior:

- default `chronicle search` prints the Rich table only, plus any relevant guidance hint;
- no plain `result ...` rows after the table.

Optional only if the executor sees a clean reason:

- add `--plain` to print machine-readable rows instead of the Rich table;
- or add `--debug-output` for the duplicate rows.

Do not add `--plain` unless tests and implementation stay small. The preferred WP-2.3.1 scope is to remove the duplicate rows by default.

## Query Guidance

Preserve WP-2.3 query guidance behavior:

- broad noisy multi-word queries still print:

```text
Hint: this was a broad token search. For exact phrase matching, use --phrase "..."
```

- no hint for `--phrase`;
- no hint for one-word queries;
- no hint for advanced FTS syntax where the hint would be misleading.

## Tests Required

Add or update focused tests for:

- phrase search title matches still sort before body-only matches;
- body-only phrase matches sort by last activity date descending;
- timestamp ties sort by conversation id descending;
- default broad search still uses existing BM25 expectations;
- `chronicle search` no longer prints duplicate `result ...` rows by default;
- query guidance still appears after broad noisy searches;
- query guidance does not appear for `--phrase`;
- existing `chronicle recent` duplicate-line behavior remains unaffected by this WP.

Do not weaken existing phrase exactness tests from WP-2.3.

## Required Validation Evidence

Include exact command output for:

```powershell
poetry env info --path
poetry run pytest tests/test_search.py tests/test_cli_search_open.py -q
poetry run pytest
poetry run ruff check .
poetry run chronicle search --help
```

Also include privacy-safe manual smoke against the repo-local private DB:

```powershell
poetry run chronicle search --phrase "YOU are the MANAGER" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
poetry run chronicle search "YOU are the MANAGER" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
```

Report only:

- whether conversation `673` appears near the top of body-only phrase matches due to recency;
- whether broad search still prints the query guidance hint;
- whether duplicate `result ...` rows are absent by default;
- no private transcript text.

## Completion Report Requirements

Write:

```text
md/handoffs/reports/WP-2.3.1-completion-report.md
```

The report must include:

- status: `ready for PM validation`, `partial`, or `blocked`;
- files changed;
- phrase ordering summary;
- search output summary;
- validation commands and results;
- privacy-safe manual smoke evidence;
- git status summary confirming no private DB/export/JSONL artifacts are tracked;
- known limitations and follow-ups.

## Acceptance Criteria

WP-2.3.1 is complete when:

- default broad search remains FTS5 + BM25;
- phrase search still returns only exact phrase/title matches;
- phrase search sorts title matches first, then newest last activity first, then conversation id descending;
- default search output no longer prints duplicate `result ...` rows;
- query guidance behavior from WP-2.3 remains intact;
- tests and Ruff pass;
- completion report is written at the required path;
- no private transcript, DB, export, JSONL, or generated dump is committed.
