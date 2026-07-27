# WP-4.1A Completion Report

## 1. Status

ready for PM validation

## 2. Executive Summary

Implemented a local FastMCP 3.x stdio server named `Chat Chronicle`. It exposes
exactly `search_chats`, `get_conversation`, and `list_recent_topics`, opens only
an existing schema-v3 SQLite archive in read-only/query-only mode, reuses the
accepted retrieval layer, and performs no model calls or archive writes.

## 3. Starting State And Dependency Preflight

- Starting commit: `d0e82c7c68c5d874bdb1715f5ff557ded5283da1`.
- Starting `git status --short`: clean.
- `poetry env info --path`: confirmed the repository-local `.venv`.
- `poetry install -E mcp`: passed using the accepted lock; FastMCP 3.4.4 was
  installed. No dependency metadata or lock changes were required.

## 4. Changed Files

- `.github/workflows/ci.yml`: install the `mcp` extra on the Windows/Ubuntu
  matrix.
- `src/chat_chronicle/cli.py`: add lazy `chronicle serve` command and help/error
  behavior.
- `src/chat_chronicle/mcp_server.py`: implement server, result models,
  read-only connection, tools, summaries, and transcript truncation.
- `tests/test_mcp_server.py`: synthetic unit, discovery, read-only, failure,
  CLI, and real stdio subprocess coverage.
- `md/handoffs/reports/WP-4.1A-completion-report.md`: this report.

## 5. Architecture And Reuse

The CLI resolves the database once using the existing WP-1.6 helper, then
passes the resolved path into one FastMCP server factory. Tools reuse
`search_conversations`, `get_conversation_detail`, and
`list_recent_conversations`. The boundary adds only typed MCP result shaping,
stored-summary lookup, transcript formatting, and read-only connection
management.

## 6. Optional Dependency And CLI Behavior

The CLI imports `chat_chronicle.mcp_server` only inside `serve`. Base CLI help
therefore has no FastMCP import dependency. A simulated missing package exits
without a traceback and prints `poetry install -E mcp`. Serve help documents
stdio, read-only operation, `--db-path`, and CLI/environment/config/default
precedence.

## 7. Read-Only Database Design And Evidence

Connections use an escaped SQLite `file:` URI with `mode=ro`, set
`PRAGMA query_only = ON`, preserve `sqlite3.Row`, require schema version 3 and
required retrieval tables, and close after each call. Tests prove an attempted
delete fails and a successful three-tool sequence preserves SHA-256, nanosecond
mtime, `user_version`, and row counts. No WAL or SHM sidecars appear. A path
containing spaces, `#`, and Windows drive syntax is exercised.

## 8. Server Instructions And Tool Schemas

Discovery identifies `Chat Chronicle` and exactly three tools. Instructions
cover read-only local recall, search-before-detail, last-activity date
semantics, lower-is-better BM25 ranking, untrusted transcript content, and the
inability to capture/infer the current client chat. Discovery tests verify
descriptions, defaults, fields, and bounds.

## 9. `search_chats` Behavior And Evidence

The tool validates nonblank queries and limits, maps `after`/`before` onto
accepted last-activity filters, and preserves accepted broad FTS/BM25 behavior.
Tests cover provider/date/limit filtering, no matches, and safe punctuation
including hyphen, colon, slash, quotes, and parentheses. Results contain all
required structured fields. Successful `conversation-summary` rows are
considered in `completed_at DESC, id DESC` order: malformed rows are skipped,
the newest valid stored summary is returned, and null is returned only when no
valid successful row exists. Failed attempts are ignored.

## 10. `get_conversation` Behavior And Evidence

The tool returns separate nullable metadata plus deterministic ordered message
headers and bodies. Tests cover metadata, ordering, non-truncation, missing ID,
and a 500-character bounded beginning/end transcript with one omission marker.
Reported total/returned character counts and truncation state are verified.

## 11. `list_recent_topics` Behavior And Evidence

The tool captures one UTC time, derives a bounded cutoff, and reuses accepted
last-activity descending/ID descending ordering. Tests verify deterministic
ties, valid stored-summary preference, malformed-summary fallback, and the
visible `(untitled)` title-source fallback. No AI client or provider is used.

## 12. Protocol And Subprocess Evidence

An installed FastMCP client launches the real CLI in a child process over stdio,
initializes, discovers exactly three tools, calls all three, performs a
no-result search and a failed invalid-argument call, then shuts down cleanly.
The protocol client successfully parsed all frames.

## 13. Error, Logging, And Stdout Hygiene

Validation failures and application failures become failed MCP calls with
concise messages. Missing, directory, corrupt, incomplete, older, and newer
archives are rejected without initialization, repair, or migration. FastMCP
banner output is disabled; observed transport diagnostics were emitted on
stderr, not protocol stdout. Errors do not include SQL or transcript bodies.

## 14. Focused And Full Validation Results

- `poetry env info --path`: passed.
- `poetry install -E mcp`: passed.
- `poetry run pytest tests/test_mcp_server.py -q`: 13 passed.
- `poetry run pytest`: 445 passed, 1 skipped.
- `poetry run ruff check .`: passed.
- `poetry check`: passed.
- `poetry run chronicle --help`: passed.
- `poetry run chronicle serve --help`: passed.
- `git diff --check`: passed.
- `git diff --cached --name-only`: empty.

The first full-suite attempt hit the command timeout at approximately two
minutes; the required rerun with a longer allowance completed successfully.

## 15. CI And Cross-Platform Coverage

The existing Ubuntu/Windows and Python 3.11/3.12 matrix now installs
`poetry install -E mcp`, so MCP tests and the real stdio subprocess smoke run
on every matrix entry rather than being skipped.

## 16. Privacy And Tracking Check

All automated and manual-equivalent smoke evidence uses temporary synthetic
databases. No live archive, export, transcript, token, credential, private
evaluation artifact, or user-level client configuration was read or tracked.

## 17. Scope-Control Checklist

- No client registration or user-level configuration.
- No HTTP/SSE/WebSocket/remote hosting.
- No ingestion, initialization, migration, repair, or archive mutation.
- No LLM call, embedding, reranking, capture, logging, SQL tool, or DB-path
  tool argument.
- No WorkTrail rename, README setup work, or MCP packaging.
- No dependency upgrade or unrelated refactor.

## 18. Acceptance-Criteria Matrix

| Criterion | Result | Evidence |
|---|---|---|
| FastMCP 3.x stdio server | pass | FastMCP 3.4.4 real subprocess smoke |
| Exactly three discoverable tools | pass | discovery and subprocess tests |
| Structured contracts and bounds | pass | Pydantic results and discovery schemas |
| Accepted retrieval behavior reused | pass | direct calls to accepted search helpers |
| Newest valid stored summary | pass | deterministic SQL plus validation tests |
| Summary fallbacks | pass | malformed/null and title tests |
| Read-only unchanged database | pass | hash/version/count/mtime/sidecar test |
| Tool-visible nonfatal bad inputs | pass | direct and subprocess invalid calls |
| Protocol-clean stdout | pass | successful installed-client framing |
| Lazy optional dependency | pass | CLI import/help and simulated absence test |
| Real initialize/list/call/shutdown | pass | subprocess protocol test |
| Windows and Ubuntu MCP CI | pass | matrix installs `-E mcp` |
| Focused/full/lint/Poetry/help/diff | pass | validation results above |
| Scope exclusions preserved | pass | scope-control checklist |
| Detailed completion report | pass | this file |
| Unstaged and uncommitted delivery | pass | cached diff empty; status below |

## 19. Known Limitations And WP-4.1B Inputs

This package intentionally supports stdio only. Client registration and
client-specific setup documentation remain WP-4.1B work. FastMCP emits an
informational startup diagnostic to stderr; stdout remains protocol-only.

## 20. Final `git status --short`

```text
 M .github/workflows/ci.yml
 M src/chat_chronicle/cli.py
?? md/handoffs/reports/WP-4.1A-completion-report.md
?? src/chat_chronicle/mcp_server.py
?? tests/test_mcp_server.py
```

## PM Rework Addendum — 2026-07-27

The first PM review found no production defect and requested stronger focused
evidence. No production behavior changed. `tests/test_mcp_server.py` was
expanded as follows:

- `test_read_only_open_and_calls_do_not_mutate` now compares
  `conversations`, `messages`, and `ai_task_results` counts before and after
  the three-tool sequence, in addition to hash, mtime, schema version, and
  WAL/SHM absence.
- `_archive` now generates active and old timestamps relative to one captured
  UTC time. `test_recent_topics_summary_and_fallbacks` proves active inclusion,
  old-row exclusion, deterministic tie ordering, and days/limit bounds without
  fixed wall-clock dates.
- `test_registration_and_discovery_schema` now asserts complete input field
  sets, required/optional status, defaults, and lower/upper bounds for all
  three tools while retaining the exact tool-name assertion.
- `test_search_filters_empty_and_validation` now proves malformed `after` and
  `before` values are actionable failed calls and that a later valid call
  succeeds. Its provider/date/limit checks use relative dates.
- `test_search_uses_newest_valid_stored_summary` proves deterministic
  completion/result ordering, ignores failed attempts, skips a newer malformed
  successful row for the next valid row, and retains null when none is valid.
- `test_conversation_metadata_ordering_and_truncation` now sets `max_chars`
  exactly to the full transcript length and proves unchanged content, false
  truncation, equal total/returned counts, and no omission marker.

The exact summary policy is: consider only successful
`conversation-summary` rows; order by completion timestamp descending and
result ID descending; return the first row that validates against
`ConversationSummaryResult`; skip malformed rows; return null only when no
valid successful row remains. Failed attempts never participate.

Fresh validation:

- `poetry env info --path`: repository-local `.venv`.
- `poetry run pytest tests/test_mcp_server.py -q`: 14 passed.
- `poetry run pytest`: 446 passed, 1 skipped.
- `poetry run ruff check .`: passed.
- `poetry check`: passed after a sandbox-launcher-only escalation.
- `poetry run chronicle --help`: passed.
- `poetry run chronicle serve --help`: passed.
- `git diff --check`: passed.
- `git diff --cached --name-only`: empty.

Final unstaged status:

```text
 M .github/workflows/ci.yml
 M src/chat_chronicle/cli.py
?? md/handoffs/reports/WP-4.1A-completion-report.md
?? md/handoffs/reports/WP-4.1A-validation-review.md
?? src/chat_chronicle/mcp_server.py
?? tests/test_mcp_server.py
```
