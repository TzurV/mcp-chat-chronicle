# WP-4.1A Validation Review

## Decision

**Accepted after rework on 2026-07-27.**

The production implementation was correctly scoped and no production defect
was found during the first PM review. The first review required stronger test
evidence for five acceptance requirements. The executor completed that
test-only rework, and the manager independently revalidated the result.

The original rework instructions remain below as the audit trail.

## PM Validation Performed

The manager independently reviewed:

- `src/chat_chronicle/mcp_server.py`;
- the `chronicle serve` addition in `src/chat_chronicle/cli.py`;
- `.github/workflows/ci.yml`;
- `tests/test_mcp_server.py`;
- `md/handoffs/reports/WP-4.1A-completion-report.md`;
- the complete diff against the accepted WP-4.1A handoff.

Independent commands passed:

```text
poetry env info --path
  -> repository-local .venv

poetry run pytest tests/test_mcp_server.py -q
  -> 13 passed

poetry run pytest
  -> 445 passed, 1 skipped

poetry run ruff check .
  -> All checks passed

poetry check
  -> All set

poetry run chronicle --help
poetry run chronicle serve --help
git diff --check
  -> passed
```

`poetry check` required the documented sandbox-only escalation after two
Windows launcher failures. This was not a project failure.

## Accepted Implementation Findings

These aspects are technically satisfactory and must be preserved:

- FastMCP is imported lazily by `chronicle serve`;
- FastMCP remains an optional extra;
- the server exposes exactly the three requested tools;
- stdio is the only transport;
- database selection is fixed at server startup;
- SQLite opens with `mode=ro` and `PRAGMA query_only = ON`;
- accepted search/detail/recent functions are reused;
- stored summaries are validated without executing an AI task;
- tool outputs are typed and bounded;
- transcript truncation preserves beginning and end with an explicit marker;
- ordinary bad tool arguments do not terminate the server;
- subprocess MCP initialization/list/call/shutdown passes;
- CI installs the MCP extra on Windows and Ubuntu;
- no client registration, remote transport, real archive, or private data was
  introduced.

## Required Rework

### 1. Complete the read-only count evidence

The handoff requires before/after equality for:

- `conversations`;
- `messages`;
- `ai_task_results`;
- schema version;
- database hash;
- modification time;
- absence of WAL/SHM sidecars.

The current `test_read_only_open_and_calls_do_not_mutate` records only the
conversation count. Extend the test to capture and compare all three required
row counts before and after the successful three-tool sequence.

Do not change the read-only implementation unless this stronger test exposes a
real defect.

### 2. Make recent-topic tests independent of wall-clock date

The synthetic archive currently hard-codes July 2026 activity dates while
`list_recent_topics` correctly uses the real current UTC time. The test will
eventually fail merely because time passed.

Make the test durable by either:

- generating active and old fixture dates relative to one captured current UTC
  time; or
- adding a minimal injectable/current-time helper and controlling it in tests.

Do not add a time-freezing dependency. Preserve production semantics: each tool
call captures UTC now once.

Cover at least:

- an active row inside the requested window;
- an old row outside it;
- deterministic ordering/tie behavior;
- the `days` and `limit` bounds.

### 3. Assert the complete discovered input contract

The current discovery test checks the three names, non-empty descriptions, and
only one bound per tool. The completion report states that fields, defaults,
and bounds were all verified.

Assert the discovered MCP input schema for:

- `search_chats`: `query`, `provider`, `after`, `before`, `limit=10`,
  `1 <= limit <= 100`, and required/optional status;
- `get_conversation`: `id`, `max_chars=8000`,
  `500 <= max_chars <= 50_000`, and required/optional status;
- `list_recent_topics`: `days=7`, `limit=20`,
  `1 <= days <= 365`, `1 <= limit <= 100`, and required/optional status.

Keep the exact three-tool assertion so the absence of write/capture/SQL tools
remains explicit.

### 4. Close the remaining search and summary evidence gaps

Add focused tests proving:

- malformed `after` and `before` dates produce actionable failed tool calls;
- provider/date/limit filters remain nonfatal to the server;
- among multiple successful summary attempts, deterministic completion/result
  ordering selects the newest valid result;
- failed summary attempts are ignored;
- a malformed successful summary is skipped according to the implemented
  **newest valid stored summary** policy, falling back to the next valid result
  or `null` when none exists.

Update the completion report wording so it states this exact policy. Avoid the
broader claim that every malformed row necessarily yields `null` when an older
valid result can still be used.

### 5. Prove the exact non-truncation boundary

The existing test covers a short non-truncated transcript and a truncated
500-character transcript, but not the exact boundary required by the handoff.

Add a deterministic assertion that:

- `len(full_transcript) == max_chars` returns the full transcript;
- `truncated` is false;
- `total_chars == returned_chars == max_chars`;
- no omission marker appears.

This may test the helper directly or use a carefully constructed synthetic
conversation, provided the MCP result contract is also already covered.

## Completion Report Update

Refresh the existing report in place:

```text
md/handoffs/reports/WP-4.1A-completion-report.md
```

Add a dated PM-rework addendum containing:

- each gap above and how it was closed;
- names of the new or expanded tests;
- fresh focused/full/Ruff/Poetry/help/diff results;
- the exact newest-valid-summary fallback policy;
- confirmation that no production behavior changed, or a precise explanation
  if a test exposed a necessary fix;
- final unstaged `git status --short`.

Do not create a second completion report.

## Required Validation

Run:

```powershell
poetry env info --path
poetry run pytest tests/test_mcp_server.py -q
poetry run pytest
poetry run ruff check .
poetry check
poetry run chronicle --help
poetry run chronicle serve --help
git diff --check
git diff --cached --name-only
git status --short
```

No external client, network endpoint, model call, private database, or
real-history smoke is required for this rework.

## Delivery Rule

Leave every implementation, test, report, and PM review file unstaged and
uncommitted. The executor must not ask the owner to commit intermediate
changes. Return `ready for PM validation` only after all five rework items and
the refreshed completion report are complete.

## Final PM Acceptance

The rework closed all five requested gaps:

- immutable evidence now compares `conversations`, `messages`, and
  `ai_task_results` before and after the three-tool sequence;
- recent-topic fixture dates are relative to one captured UTC time and retain
  an explicit old-row exclusion;
- discovery asserts complete tool fields, required/optional status, defaults,
  and bounds;
- invalid date filters and newest-valid-summary precedence are covered;
- the exact non-truncation boundary is covered.

No production behavior changed during rework.

Independent final validation:

```text
poetry run pytest tests/test_mcp_server.py -q
  -> 14 passed

poetry run pytest
  -> 446 passed, 1 skipped

poetry run ruff check .
  -> All checks passed

poetry check
  -> All set

git diff --check
git diff --cached --name-only
  -> passed; nothing staged
```

`poetry check` again required sandbox-only escalation after the recurring
Windows launcher failure. This was not a project failure.

**Final PM decision: WP-4.1A accepted. WP-4.1B is unblocked.**
