# WP-2.3 Handoff: Search Phrase Mode And Query Guidance

## Objective

Improve `chronicle search` so users can intentionally run exact phrase searches and receive practical query guidance when broad token search is likely to be noisy.

This follow-up was triggered by a real OpenAI Codex search case:

```powershell
poetry run chronicle search "YOU are the MANAGER" --provider openai_codex --db-path .\.chronicle\chronicle.db
```

The current chat was indexed as provider `openai_codex`, conversation `673`, but the query did not appear in the default top results because SQLite FTS tokenized the unquoted query into common terms such as `you`, `are`, `the`, and `manager`. Those terms occur in many tool/system transcripts, so BM25 ranking returned noisier matches first.

## Source Of Truth

Read before implementation:

- `md/master-plan.md`
- `md/development-ledger.md`
- `md/agent-operating-notes.md`
- `md/handoffs/WP-2.1-fts-search-open.md`
- `md/handoffs/reports/WP-2.1-validation-review.md`
- `md/handoffs/WP-2.2-recent-active-chats-cli.md`
- `src/chat_chronicle/search.py`
- `src/chat_chronicle/cli.py`
- `src/chat_chronicle/db.py`
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

## Scope

Implement:

- explicit phrase search mode for `chronicle search`;
- query guidance for multi-word queries that are likely to behave as broad token searches;
- ranking behavior that surfaces exact phrase/title matches above broad BM25-only matches when phrase mode is requested;
- tests for search helper behavior and CLI output;
- completion report at:

```text
md/handoffs/reports/WP-2.3-completion-report.md
```

Do not implement:

- semantic/vector search;
- local SLM enrichment;
- UI beyond CLI text;
- schema redesign unless clearly required and approved;
- local Codex app deep-link/open-in-Codex behavior;
- source management commands;
- changes to importers/extractors.

## Required CLI Behavior

Add an explicit phrase option:

```powershell
poetry run chronicle search --phrase "YOU are the MANAGER" --provider openai_codex --db-path .\.chronicle\chronicle.db
```

Expected semantics:

- `--phrase` treats the query as an exact phrase, not as independent broad terms.
- Phrase search should match message bodies and conversation titles.
- Phrase search should continue to support existing filters:
  - `--provider`
  - `--since`
  - `--until`
  - `--tag`
  - `--limit`
  - `--db-path`
- Phrase search should still produce the existing table shape:
  - `ID`
  - `Date`
  - `Provider`
  - `Title`
  - `Snippet`
  - `Open hint`
- If phrase search has no results, print `No results` and exit zero.

Keep existing search behavior unchanged when `--phrase` is not provided.

## Query Guidance Requirements

Add guidance for non-phrase searches that look likely to be noisy.

At minimum, when all of these are true:

- `--phrase` is not used;
- the query contains multiple words;
- the query contains common short/stop-style terms such as `you`, `are`, `the`, `a`, `an`, `to`, `of`, `in`, `for`;

print a short hint after the results or after `No results`:

```text
Hint: this was a broad token search. For exact phrase matching, use --phrase "..."
```

Do not print the hint for:

- one-word queries;
- queries already using `--phrase`;
- queries where the query string is already valid advanced FTS syntax and the executor determines the hint would be misleading.

The hint must be helpful but not noisy. It should not replace results or turn successful broad search into an error.

## Search Implementation Guidance

Preferred approach:

- Continue using FTS5 for the default search path.
- For `--phrase`, use a safe phrase-specific FTS expression or a constrained exact-text fallback.
- Avoid direct string interpolation into SQL. Use parameters wherever possible.
- If building an FTS phrase expression is necessary, escape embedded quotes correctly and add tests for that behavior.
- Boost exact phrase/title matches above broader body-only matches in phrase mode.

Acceptable behavior:

- Phrase search can use FTS5 phrase syntax if tests prove exact phrase behavior.
- Phrase search can combine FTS candidate filtering with exact substring verification in Python or SQL if that is simpler and safer.

Do not accept:

- phrase search that still returns records matching only one token from the phrase;
- SQL string construction vulnerable to malformed query text;
- regressions in default BM25 search behavior.

## Local Transcript Open Follow-Up

Record, but do not implement in this WP:

- `chronicle open <id>` is the correct way to view local OpenAI Codex rows today.
- The `local: <origin_file>` value shown in `recent` is a local transcript hint, not a web URL.
- There is no current deep-link that reopens the original Codex app chat the way ChatGPT URLs open web chats.
- Add a backlog note for future local app/session navigation if reliable Codex deep-link or resume behavior is verified.

If the executor notices Windows Unicode output failures while validating `chronicle open`, they may document them in the completion report, but fixing transcript rendering is outside WP-2.3 unless the PM explicitly expands scope.

## Tests Required

Add focused tests for:

- default search behavior remains broad token/BM25 search;
- `--phrase` returns a conversation containing the exact phrase;
- `--phrase` does not return conversations containing only some phrase tokens;
- phrase search works with `--provider`;
- phrase search works with `--limit`;
- phrase search works against title matches;
- phrase search handles embedded quotes or rejects them gracefully with a clear error;
- multi-word broad search prints the query guidance hint;
- one-word search does not print the query guidance hint;
- `--phrase` search does not print the broad-search hint;
- empty query validation remains intact;
- `chronicle --help` documents `--phrase`.

Use synthetic fixtures/data only. Do not commit private OpenAI Codex JSONL or DB files.

## Required Validation Evidence

Include exact command output for:

```powershell
poetry env info --path
poetry run pytest tests/test_search.py tests/test_cli_search_open.py -q
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
poetry run chronicle search --help
```

Also include privacy-safe manual smoke against the repo-local private DB:

```powershell
poetry run chronicle search --phrase "YOU are the MANAGER" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
poetry run chronicle search "YOU are the MANAGER" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
poetry run chronicle search "chat_chronicle" --provider openai_codex --limit 20 --db-path .\.chronicle\chronicle.db
```

Report only:

- whether conversation `673` is returned by the phrase search;
- whether broad search prints the query guidance hint;
- whether the distinctive title search still returns the expected row;
- no private transcript text.

## Completion Report Requirements

Write:

```text
md/handoffs/reports/WP-2.3-completion-report.md
```

The report must include:

- status: `ready for PM validation`, `partial`, or `blocked`;
- files changed;
- CLI syntax summary;
- default search behavior;
- phrase search behavior;
- query guidance behavior;
- safety notes for FTS query escaping / malformed input;
- validation commands and results;
- privacy-safe manual smoke evidence;
- git status summary confirming no private DB/export/JSONL artifacts are tracked;
- known limitations and follow-ups.

## Acceptance Criteria

WP-2.3 is complete when:

- `chronicle search --phrase "<text>"` works;
- phrase mode returns only exact phrase/title matches, not partial-token matches;
- default broad search behavior remains compatible with WP-2.1;
- noisy multi-word broad searches show clear query guidance;
- provider/date/tag/limit filters still work;
- tests and Ruff pass;
- completion report is written at the required path;
- no private OpenAI Codex transcript, DB, export, or generated dump is committed.
