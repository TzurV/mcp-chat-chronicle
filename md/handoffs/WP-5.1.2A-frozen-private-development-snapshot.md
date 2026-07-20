# WP-5.1.2A Handoff: Frozen Private Development Snapshot

## Status

Ready for execution.

This is a local data-operations work package. It is not an application-code
implementation task.

## Objective

Create one consistent, immutable, local-only SQLite snapshot of the owner's
current real Chat Chronicle database. This snapshot becomes the fixed source for
WP-5.1.2B selection and FABLE reference creation.

The live product database must not be changed by this activity.

## Plan Position

This work package implements WP-5.1.2A from `md/master-plan.md`.

It precedes:

1. WP-5.1.2B, which freezes 30 conversation IDs and creates four direct FABLE
   references per conversation;
2. WP-5.2A, which integrates selected local models and runtimes;
3. WP-5.2B, which evaluates candidates with deterministic metrics and a
   separately configured Gemini judge.

The old handoff
`md/handoffs/WP-5.1.2-real-data-teacher-reference-corpus.md` is superseded
planning history. Do not execute its 300-case, two-teacher, orchestration, or
reconciliation scope.

## Required Operating Notes

Read and follow `md/agent-operating-notes.md` before doing any work.

In particular:

- verify Poetry resolves to this repository's `.venv`;
- account for the known Windows sandbox launcher failure;
- leave all work uncommitted for PM validation;
- do not stage any file.

## Approved Data Boundary

The source is the owner's real configured Chronicle database. It is expected to
resolve to the repository-local database:

```text
.chronicle/chronicle.db
```

Do not hard-code or report the owner's private absolute path. Resolve and verify
the effective path using the accepted configuration precedence:

1. an explicitly supplied source path, if the owner provides one for this task;
2. `CHAT_CHRONICLE_DB`;
3. `.chronicle/config.yaml` `paths.db`;
4. the built-in repository-local default.

The private development root is:

```text
.chronicle/eval/dev-v1/
```

Required local artifact layout:

```text
.chronicle/eval/dev-v1/
  source/
    chronicle-frozen.db
    snapshot-manifest.json
```

Both artifacts are private and must remain ignored and untracked.

## Scope

Perform all of the following:

1. Verify the source DB exists and is the intended real product database.
2. Verify no Chronicle ingest, collect, AI-task, or other known writer is active.
3. Capture privacy-safe source metadata and aggregate counts.
4. Create a consistent SQLite-native backup.
5. Close all backup connections before hashing or freezing the destination.
6. Validate the snapshot's integrity and parity with the source.
7. Record the private snapshot manifest.
8. mark the snapshot read-only where practical on Windows;
9. prove it can be opened in read-only/query-only mode;
10. prove the source remained unchanged during this task;
11. prove all private artifacts are ignored and untracked;
12. write the required privacy-safe completion report.

## Explicit Non-Scope

Do not:

- modify application source code;
- add a snapshot, corpus, benchmark, or evaluation module;
- add a reusable repository script;
- modify dependencies or lock files;
- change the product schema;
- run a product migration against the source or snapshot;
- add evaluation tables to either database;
- run any AI task;
- select the 30 WP-5.1.2B conversations;
- send any content to FABLE, Gemini, or another remote service;
- create teacher references or candidate predictions;
- modify `md/master-plan.md` or `md/development-ledger.md`;
- modify the superseded WP-5.1.2 handoff;
- commit, stage, amend, rebase, or otherwise change Git history.

Temporary operator commands or private temporary files may be used only below
`.chronicle/eval/dev-v1/`. Do not add them to the repository. Remove or clearly
identify any temporary artifact before delivery.

## Preflight And Stop Conditions

### Poetry Environment

From the repository root:

```powershell
poetry env info --path
```

Expected:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If Poetry resolves outside this repository, stop and report the blocker. Do not
install anything and do not use another project's environment.

### Git State

Record:

```powershell
git status --short
```

The worktree already contains PM-owned planning/research changes. Preserve them
exactly. Do not revert, reformat, stage, or incorporate them into this delivery.

### Source Checks

Before creating the destination:

- verify the effective source DB exists and is non-empty;
- verify it is not the proposed destination path;
- verify `chronicle-frozen.db` does not already exist;
- verify the source schema is readable without migration;
- record the source `PRAGMA user_version`;
- record aggregate row counts for at least `conversations` and `messages`;
- record whether source `-wal` or `-shm` sidecars exist;
- verify no known Chronicle writer is active;
- use a source connection opened in SQLite URI read-only mode.

Stop rather than overwrite an existing `chronicle-frozen.db` or
`snapshot-manifest.json`. A new snapshot version requires a separately approved
directory/version name.

If the source schema is unreadable, the source changes during the operation,
integrity checking fails, or count parity cannot be established, do not declare
the snapshot frozen. Preserve privacy, report the blocker, and do not continue
to WP-5.1.2B.

## Snapshot Creation Requirements

Use Python's standard-library SQLite online backup API, or an equivalently safe
SQLite-native backup mechanism.

Required properties:

- source connection uses SQLite URI read-only mode;
- destination is a newly created SQLite database;
- backup uses SQLite's backup facility, not a filesystem copy;
- source and destination are different resolved files;
- all SQLite connections are closed before hashing the snapshot;
- no `Copy-Item`, `shutil.copyfile`, Explorer copy, or raw byte copy is used;
- no package installation is required.

The source may use WAL mode. The backup mechanism must include the source's
committed logical state without depending on copying `-wal` or `-shm` files.

Do not copy source sidecars into the development snapshot directory.

## Source No-Write Evidence

Capture a source fingerprint immediately before and immediately after snapshot
creation. Keep the detailed fingerprint in the private manifest.

The fingerprint must include, where available:

- resolved source path;
- source file size and UTC modification time;
- SHA-256 of the closed source DB file;
- presence and metadata of source WAL/SHM sidecars;
- `PRAGMA user_version`;
- aggregate `conversations` and `messages` counts;
- additional aggregate counts used by the operator;
- repository Git HEAD;
- fingerprint timestamp in UTC.

Do not treat volatile SHM metadata alone as proof of logical mutation. The
source DB hash, source DB metadata, schema version, and logical aggregate counts
must remain stable. If an external writer changes the source during the
operation, stop and rerun only after the writer is closed and the existing
incomplete destination has been handled safely.

The completion report must state whether before/after source verification
matched, but it must not contain private absolute paths or actual hashes.

## Snapshot Validation

After all backup handles are closed:

1. Run `PRAGMA integrity_check` against the snapshot and require exactly `ok`.
2. Verify the snapshot `PRAGMA user_version` matches the source.
3. Verify snapshot `conversations` and `messages` counts match the source
   snapshot-time counts.
4. Verify any additional recorded aggregate counts match.
5. Verify no snapshot `-wal` or `-shm` sidecar is required.
6. Record the closed snapshot's file size and SHA-256.
7. Reopen the snapshot using SQLite URI `mode=ro`.
8. Set `PRAGMA query_only=ON` for verification reads.
9. Where supported, reopen with `immutable=1` after the snapshot is closed and
   self-contained.
10. Demonstrate that a write attempt is rejected as read-only or query-only.
11. Set the Windows read-only file attribute where practical.
12. Recompute the snapshot SHA-256 after all validation and require it to match
    the manifest's frozen hash.

Do not run product initialization or migration functions against the snapshot.

## Private Snapshot Manifest

Write:

```text
.chronicle/eval/dev-v1/source/snapshot-manifest.json
```

Use valid structured JSON. At minimum record:

- manifest format version;
- corpus/development version: `dev-v1`;
- UTC creation and verification timestamps;
- backup method;
- source logical role;
- private resolved source path;
- repository Git HEAD;
- Python and SQLite library versions;
- source `PRAGMA user_version`;
- source journal mode;
- source aggregate counts;
- before/after source fingerprints and match result;
- destination relative and private resolved path;
- destination file size;
- destination SHA-256;
- snapshot `PRAGMA user_version`;
- snapshot aggregate counts;
- integrity-check result;
- read-only/query-only verification result;
- Windows read-only attribute result;
- snapshot sidecar check;
- freeze status;
- notes or explicit limitations.

Do not put transcript text, message bodies, titles, URLs, or conversation/message
IDs in the manifest.

The manifest itself is private because it contains local paths and hashes. It
must not be copied into the tracked completion report.

## Git Privacy Verification

Verify the private root is ignored:

```powershell
git check-ignore -v .chronicle/eval/dev-v1/source/chronicle-frozen.db
git check-ignore -v .chronicle/eval/dev-v1/source/snapshot-manifest.json
```

Verify no private evaluation artifact is tracked:

```powershell
git ls-files .chronicle
git status --short
```

Expected:

- both private artifacts match an ignore rule;
- `git ls-files .chronicle` returns no private artifact;
- `git status --short` does not show the snapshot, manifest, sidecars, temporary
  scripts, or other private evaluation files.

Do not use `git add -f`.

## Required Completion Report

Create:

```text
md/handoffs/reports/WP-5.1.2A-completion-report.md
```

The report status must be:

```text
Ready for PM validation
```

The report must contain:

1. executive summary;
2. source-resolution method, using only a repository-relative or redacted path;
3. confirmation that SQLite's backup API was used;
4. confirmation that no raw filesystem DB copy was used;
5. local artifact paths expressed relative to the repository;
6. source schema version and privacy-safe aggregate counts;
7. snapshot schema version and matching aggregate counts;
8. integrity-check result;
9. source before/after no-write verification result;
10. snapshot hash verification result, without publishing the hash;
11. read-only/query-only and rejected-write evidence;
12. sidecar/self-contained result;
13. Git ignore/tracking evidence;
14. commands or procedures used, with private absolute paths and hashes redacted;
15. limitations, warnings, or blockers;
16. exact tracked files changed;
17. final `git status --short` summary;
18. an acceptance-criteria checklist;
19. explicit confirmation that WP-5.1.2B has not started;
20. explicit confirmation that no remote model or API call was made.

Do not include:

- actual SHA-256 values;
- private absolute paths or usernames;
- conversation or message IDs;
- titles, snippets, URLs, UUIDs, or transcript content;
- copied manifest JSON;
- credentials, tokens, model responses, or remote disclosure records.

## Acceptance Criteria

WP-5.1.2A is ready for PM validation only when all of the following are true:

1. The effective real source DB was resolved and verified.
2. The snapshot was created with a SQLite-native backup API.
3. No raw filesystem copy of the live database was used.
4. The destination did not pre-exist and was not overwritten.
5. `PRAGMA integrity_check` returned `ok`.
6. Source and snapshot schema versions match.
7. Source and snapshot conversation/message counts match.
8. Source before/after fingerprints and aggregate counts show no source change
   caused by this task.
9. The snapshot is self-contained and does not require WAL/SHM sidecars.
10. The closed snapshot hash is recorded privately and remains stable after
    validation.
11. Read-only/query-only access works and a write attempt is rejected.
12. The private manifest is complete and valid JSON.
13. The snapshot and manifest are ignored and untracked.
14. No product code, tests, dependencies, lock files, plan, or ledger files were
    changed by the executor.
15. No AI task, FABLE reference, Gemini judge, or remote API call was run.
16. No private data appears in tracked output.
17. The detailed completion report exists at the required location.
18. All delivery changes remain unstaged and uncommitted.

## Validation Notes

This work package changes no application code, so a full pytest or Ruff run is
not required solely for WP-5.1.2A. Run:

```powershell
git diff --check
git status --short
```

The executor must still perform all database, hash, read-only, and Git privacy
checks defined above.

If the executor changes any tracked application, test, dependency, or
configuration file despite this scope, stop and report the deviation rather
than expanding validation to legitimize it.

## Delivery And Commit Ownership

Follow `md/agent-operating-notes.md`.

The executor must:

1. perform the snapshot operation and validation;
2. write the detailed completion report;
3. leave all tracked changes unstaged and uncommitted;
4. report `git status --short`;
5. deliver status as `Ready for PM validation`.

The executor must not run `git add`, `git commit`, amend, squash, rebase, or
rewrite history.

The PM/manager validates the private evidence and completion report against this
handoff. Only the PM/manager may commit, and only after successful validation
and an explicit owner request.
