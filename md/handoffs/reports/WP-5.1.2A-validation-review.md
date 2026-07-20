# WP-5.1.2A PM Validation Review

## Decision

**Accepted.**

WP-5.1.2A created the required frozen private development snapshot without
changing product code or the live Chronicle database. The completion report and
private local evidence satisfy all 18 handoff acceptance criteria.

## Evidence Reviewed

The PM reviewed:

- `md/handoffs/WP-5.1.2A-frozen-private-development-snapshot.md`;
- `md/handoffs/reports/WP-5.1.2A-completion-report.md`;
- the ignored private snapshot manifest;
- the ignored temporary operator script;
- the private snapshot's current file properties;
- independent SQLite integrity, schema, count, and sidecar checks;
- independent manifest structure and frozen-hash verification;
- Git ignore, tracking, status, and whitespace evidence.

Private paths and hash values are deliberately omitted from this tracked review.

## Validation Results

| Check | Result |
| --- | --- |
| Poetry environment resolves to repository `.venv` | pass |
| Source opened read-only | pass |
| SQLite `Connection.backup` used | pass |
| Raw filesystem DB copy absent | pass |
| Snapshot `PRAGMA integrity_check` | `ok` |
| Source/snapshot schema version parity | pass |
| Source/snapshot conversation and message count parity | pass |
| Source before/after no-write evidence | pass |
| Snapshot hash stable against private manifest | pass |
| Snapshot self-contained without WAL/SHM | pass |
| Read-only/query-only validation | pass |
| Windows read-only attribute | set |
| Manifest is valid structured JSON with required fields | pass |
| Private artifacts ignored | pass |
| Private artifacts untracked | pass |
| No application/dependency/schema changes | pass |
| No AI task or remote API/model call | pass |
| `git diff --check` | pass |

The independently observed aggregate counts matched the completion report:
711 conversations and 28,370 messages, with schema version 3.

## Findings

No blocking findings.

### Writer Detection

The preflight writer check was process-based rather than lock-based. This is
acceptable for this one-time snapshot because the source DB SHA-256, size, UTC
mtime, schema version, conversation/message counts, and sidecar state matched
before and after the operation. That combined evidence is stronger than process
name inspection alone.

A future repeatable snapshot utility, if separately approved, should consider a
formal writer/lock protocol. No such utility is required by WP-5.1.2A.

### Freeze Enforcement

The Windows read-only attribute is advisory. The private manifest's SHA-256 and
the required pre-use hash verification are the authoritative freeze evidence.
WP-5.1.2B must open the snapshot read-only and verify that hash before selecting
conversations.

### Temporary Operator Script

The private temporary script is ignored, untracked, and explicitly identified
in the completion report, which satisfies the handoff. It may now be removed
after PM validation to reduce local clutter. Its presence is not a release or
privacy blocker.

## Scope Confirmation

WP-5.1.2B has not started. No conversation IDs were selected, no FABLE
references were created, and no private content was sent remotely.

The superseded automated two-teacher WP-5.1.2 handoff remains historical only
and must not be executed.

## Next Gate

WP-5.1.2B may begin only from a separately approved handoff. That handoff must:

1. verify the frozen snapshot hash before use;
2. select and freeze exactly 30 conversation IDs before labeling;
3. generate four direct FABLE references per conversation;
4. keep all source IDs, inputs, outputs, and provenance local and untracked;
5. produce only privacy-safe aggregate tracked reporting.
