# WP-5.1.1 Validation Review

## Status

**Rework required.**

WP-5.1.1 is close to acceptance. The committed scope is coherent, the completion
report is detailed, the focused and full regression suites pass, Ruff is clean, and
the four task/catalog/package contracts are present. One evidence-integrity defect
blocks acceptance.

## Blocking Finding

### 1. Overview selected-message IDs are inferred from rendered transcript text

**Location:** `src/chat_chronicle/ai.py`, `_select_meaningful()` overview branch.

The overview selector currently reconstructs `selected_ids` with a substring test:

```python
if f"message_id={int(row['id'])}" in text
```

This is not an exact or trustworthy mapping from selected rows to selected IDs.

- Decimal-prefix collision: `message_id=1` is found inside `message_id=10`,
  `message_id=100`, and similar IDs.
- Transcript-content collision: a selected message body can quote text such as
  `message_id=7`, causing omitted message 7 to be reported as selected.

The incorrect ID then enters `selected_message_ids`, so post-response evidence
validation can accept an evidence ID that was not actually selected for the model.
This violates the handoff requirement that every evidence ID belong to the selected
input and that invalid evidence fail rather than be silently accepted.

## Required Fix

Carry selected rows/IDs structurally through overview selection. Do not parse or
search the rendered transcript to recover identity.

The implementation should preserve the accepted behavior:

- deterministic beginning/middle/end sampling;
- chronological rendered output;
- exact selected and omitted IDs;
- bounded text and omission metadata;
- existing message-level truncation details;
- evidence validation against the exact structurally selected ID set.

Keep the change narrowly scoped. Do not redesign the selector, schema registry,
task catalog, cache model, or persistence path.

## Required Regression Tests

Add focused synthetic tests proving all of the following:

1. An omitted message ID that is a decimal prefix of a selected ID is not present in
   `selected_message_ids` or `message_ids`.
2. A selected message body containing a literal `message_id=<omitted-id>` does not
   add that omitted ID to selection metadata.
3. A provider response citing either falsely implied omitted ID fails with
   `evidence_validation` and writes no successful result.
4. Genuine selected IDs still validate successfully.
5. Overview selection remains deterministic and bounded after the fix.
6. Existing recent-meaningful behavior remains unchanged.

Use synthetic data only. Do not read the owner's real archive and do not call a
local or remote model.

## Validation Evidence Reviewed

- Commit reviewed: `4c15b0c feat: add initial conversation intelligence tasks`.
- Repository environment: `C:\work\Github\mcp-chat-chronicle\.venv`.
- Focused WP-5.1/WP-5.1.1 collection: passed.
- Full suite: passed.
- `poetry run ruff check .`: `All checks passed!`.
- `git diff --check 4c15b0c^ 4c15b0c`: passed.
- Worktree was clean before this PM review.

Green existing tests do not waive the blocker because the collision cases are absent
from the current matrix.

## Completion Report Update

After rework, refresh:

`md/handoffs/reports/WP-5.1.1-completion-report.md`

Add a rework section that states the root cause, structural fix, exact regression
tests, and fresh focused/full/Ruff/diff evidence. Restore the report and ledger to
`Ready for PM validation`; do not mark the work package accepted.

## Process Note

The implementation was committed before PM acceptance. The handoff required the
executor not to commit until explicitly instructed by the PM after validation. Do
not amend, squash, rebase, or otherwise rewrite commit `4c15b0c`. Leave the rework
uncommitted for PM validation unless the PM explicitly authorizes another commit.

WP-5.1.2 remains gated until this rework is accepted.
