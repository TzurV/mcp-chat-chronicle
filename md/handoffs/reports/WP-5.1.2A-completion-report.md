# WP-5.1.2A Completion Report: Frozen Private Development Snapshot

## Status

Ready for PM validation

## 1. Executive Summary

A single consistent, immutable, local-only SQLite snapshot of the owner's real
Chat Chronicle database was created at
`.chronicle/eval/dev-v1/source/chronicle-frozen.db`, with a private manifest at
`.chronicle/eval/dev-v1/source/snapshot-manifest.json`.

The snapshot was produced with Python's standard-library SQLite online backup
API (`sqlite3.Connection.backup`) from a source connection opened in SQLite URI
read-only mode. No filesystem copy was used at any point.

All required checks passed: `PRAGMA integrity_check` returned `ok`, schema
version and aggregate counts match the source exactly, the source was proven
unchanged by before/after fingerprints, the snapshot is self-contained with no
WAL/SHM sidecars, its hash was stable across validation, read-only and
query-only access work, a write attempt was rejected, and both private
artifacts are ignored and untracked.

No application code, test, dependency, lock, plan, or ledger file was changed.
The only tracked file added by this work package is this report. All changes are
unstaged and uncommitted.

## 2. Source Resolution Method

The effective source was resolved using the accepted configuration precedence:

1. no explicit source path was supplied for this task;
2. `CHAT_CHRONICLE_DB` was checked and found unset;
3. `.chronicle/config.yaml` `paths.db` was found and used;
4. the built-in default was therefore not needed.

Resolved source (repository-relative): `.chronicle/chronicle.db`

The private absolute path was recorded only in the private manifest. It is
redacted here.

Pre-creation checks performed before any destination was created:

- source exists and is non-empty — confirmed;
- source resolved path differs from the destination resolved path — confirmed;
- `chronicle-frozen.db` did not already exist — confirmed;
- `snapshot-manifest.json` did not already exist — confirmed;
- source schema readable without migration — confirmed;
- source `PRAGMA user_version` recorded;
- aggregate `conversations` and `messages` counts recorded;
- source `-wal` and `-shm` sidecars — neither present;
- no known Chronicle writer active — confirmed (see §15);
- source opened with SQLite URI `mode=ro` plus `PRAGMA query_only=ON`.

## 3. SQLite Backup API Confirmation

The snapshot was created with Python's standard-library SQLite online backup
API:

```python
src_conn = sqlite3.connect("file:///<redacted-source>?mode=ro", uri=True)
src_conn.execute("PRAGMA query_only=ON")
dst_conn = sqlite3.connect("<redacted-destination>")
src_conn.backup(dst_conn)
```

The destination was a newly created SQLite database. Both connections were
closed before any hashing or validation was performed.

## 4. No Raw Filesystem Copy

No `Copy-Item`, `shutil.copyfile`, `shutil.copy2`, Explorer copy, `robocopy`, or
raw byte copy was used. The destination's entire content came from SQLite's
backup facility. No source `-wal` or `-shm` sidecar was copied into the
development snapshot directory (none existed, and none would have been copied).

## 5. Local Artifact Paths (repository-relative)

```text
.chronicle/eval/dev-v1/
  source/
    chronicle-frozen.db        (private, ignored, untracked, read-only)
    snapshot-manifest.json     (private, ignored, untracked)
  tmp/
    make_snapshot.py           (private temporary operator script, ignored, untracked)
```

`tmp/make_snapshot.py` is the temporary operator script for this task. It lives
below the private development root, is covered by the `.chronicle/` ignore rule,
and is not part of the repository. It is retained rather than deleted so the PM
can inspect the exact procedure during validation; it may be removed after
validation.

## 6. Source Schema Version And Aggregate Counts

| Metric | Source value |
| --- | --- |
| `PRAGMA user_version` | 3 |
| `conversations` rows | 711 |
| `messages` rows | 28,370 |
| Journal mode | `wal` |
| `-wal` sidecar present | no |
| `-shm` sidecar present | no |

These are aggregate counts only. No conversation or message identifiers, titles,
URLs, or content are reported.

## 7. Snapshot Schema Version And Aggregate Counts

| Metric | Snapshot value | Matches source |
| --- | --- | --- |
| `PRAGMA user_version` | 3 | yes |
| `conversations` rows | 711 | yes |
| `messages` rows | 28,370 | yes |

Both aggregate counts and the schema version match the source snapshot-time
values exactly.

## 8. Integrity Check Result

`PRAGMA integrity_check` against the closed snapshot returned exactly:

```text
ok
```

## 9. Source Before/After No-Write Verification

A full source fingerprint was captured immediately before and immediately after
snapshot creation. The compared fields were: SHA-256 of the closed source file,
file size, UTC modification time, `PRAGMA user_version`, and the aggregate
`conversations`/`messages` counts.

**Result: matched.** All compared fields were identical before and after.

The source file's modification time remained at its pre-task value, which
predates this work package. No source sidecars were created. The live product
database was not changed by this activity.

Detailed fingerprints (including hashes, absolute path, and timestamps) are
recorded only in the private manifest.

## 10. Snapshot Hash Verification

The closed snapshot's SHA-256 was computed after all backup handles were closed
and recorded privately in the manifest as the frozen hash. After the complete
validation sequence — integrity check, count parity, read-only reopen,
`immutable=1` reopen, rejected-write probe, and the Windows read-only attribute
change — the SHA-256 was recomputed.

**Result: the recomputed hash matched the manifest's frozen hash.** The snapshot
was not modified by validation.

The hash value itself is deliberately not published in this report.

Snapshot file size: 81,883,136 bytes.

## 11. Read-Only / Query-Only And Rejected-Write Evidence

| Check | Result |
| --- | --- |
| Reopen with URI `mode=ro` | succeeded |
| `PRAGMA query_only=ON` for verification reads | applied |
| Reopen with `immutable=1` after close | succeeded; counts identical |
| Write attempt (`CREATE TABLE`) against read-only handle | rejected |
| Windows read-only file attribute | set |

The write attempt was rejected with:

```text
sqlite3.OperationalError: attempt to write a readonly database
```

The Windows read-only attribute is set on `chronicle-frozen.db`; the file
reports `IsReadOnly = True`.

## 12. Sidecar / Self-Contained Result

After snapshot creation and all validation, neither
`chronicle-frozen.db-wal` nor `chronicle-frozen.db-shm` exists. The snapshot is
self-contained and requires no sidecar files to be opened and queried. This was
confirmed both immediately after creation and again after read-only and
`immutable=1` reopen.

## 13. Git Ignore And Tracking Evidence

`git check-ignore -v` output (all three private artifacts):

```text
.gitignore:13:.chronicle/   .chronicle/eval/dev-v1/source/chronicle-frozen.db
.gitignore:13:.chronicle/   .chronicle/eval/dev-v1/source/snapshot-manifest.json
.gitignore:13:.chronicle/   .chronicle/eval/dev-v1/tmp/make_snapshot.py
```

`git ls-files .chronicle` returned no output — no private evaluation artifact is
tracked.

`git status --short` does not show the snapshot, the manifest, any sidecar, the
temporary operator script, or any other private evaluation file.

`git add -f` was not used. Nothing was staged.

## 14. Commands And Procedures Used

Preflight:

```powershell
poetry env info --path        # -> c:\work\Github\mcp-chat-chronicle\.venv
git status --short
git rev-parse HEAD
```

Source resolution and writer check:

```powershell
$env:CHAT_CHRONICLE_DB        # unset
Get-Content -Raw .chronicle/config.yaml
Get-ChildItem -Path .chronicle -Filter "chronicle.db*" -Force
Get-Process | Where-Object { $_.ProcessName -match 'chronicle|python' }
Get-CimInstance Win32_Process -Filter "ProcessId=<pid>"
```

Snapshot creation and validation (private operator script):

```powershell
New-Item -ItemType Directory -Force -Path .chronicle/eval/dev-v1/source
poetry run python .chronicle/eval/dev-v1/tmp/make_snapshot.py
```

The script performs, in order: source resolution, pre-existence and
distinct-path guards, before-fingerprint, SQLite online backup,
after-fingerprint and no-write comparison, snapshot hashing, integrity check,
schema-version and count parity, sidecar check, rejected-write probe,
`immutable=1` reopen, Windows read-only attribute, hash-stability recheck, and
manifest write. Any failed check aborts with a blocker before the snapshot can
be declared frozen.

Git privacy and delivery validation:

```powershell
git check-ignore -v .chronicle/eval/dev-v1/source/chronicle-frozen.db
git check-ignore -v .chronicle/eval/dev-v1/source/snapshot-manifest.json
git ls-files .chronicle
git diff --check
git status --short
```

Private absolute paths and hash values are redacted throughout.

## 15. Limitations, Warnings, And Blockers

No blockers. The following are recorded for transparency:

- **Writer check method.** No Chronicle ingest, collect, or AI-task process was
  running. One Python process from this repository's `.venv` was present; its
  command line identified it as the VS Code `autopep8` language server, not a
  Chronicle writer. The check is process-based rather than lock-based, but it is
  corroborated by the strongest available evidence: the source's SHA-256, size,
  mtime, schema version, and both aggregate counts were byte-identical before
  and after the operation, and no `-wal`/`-shm` sidecars appeared.
- **Source journal mode is `wal`** with no sidecars present at snapshot time,
  indicating a cleanly checkpointed database. The SQLite backup API captures the
  committed logical state regardless, without depending on sidecar copying.
- **`sqlite3.version` deprecation warning.** Recording the `sqlite3` module
  version emitted a Python 3.12 `DeprecationWarning`. It is cosmetic, affects
  only a manifest metadata field, and does not touch product code.
- **Windows read-only attribute is advisory.** It prevents casual modification
  but does not make the file cryptographically immutable. The recorded SHA-256
  in the private manifest is the authoritative freeze evidence.
- **Temporary operator script retained.** See §5 — kept for PM inspection,
  private and untracked, removable after validation.

## 16. Exact Tracked Files Changed

One tracked file was added by this work package:

| File | Change |
| --- | --- |
| `md/handoffs/reports/WP-5.1.2A-completion-report.md` | new — this report |

No other tracked file was created, modified, or deleted by the executor. In
particular: no application source, no test, no dependency or lock file, no
schema, no `md/master-plan.md`, no `md/development-ledger.md`, and no
modification to the superseded WP-5.1.2 handoff.

## 17. Final `git status --short`

```text
 M md/development-ledger.md
 M md/master-plan.md
?? md/handoffs/WP-5.1.2A-frozen-private-development-snapshot.md
?? md/handoffs/reports/WP-5.1.2A-completion-report.md
?? md/research/RS-3-codex-cross-client-workspace-visibility.md
```

The pre-existing PM-owned planning and research changes (`md/development-ledger.md`,
`md/master-plan.md`, the WP-5.1.2A handoff, and `md/research/RS-3-...`) were
present before this task and are preserved exactly as found. They were not
reverted, reformatted, staged, or incorporated into this delivery.

`git diff --check` produced no output.

## 18. Acceptance Criteria Checklist

| # | Criterion | Status |
| --- | --- | --- |
| 1 | Effective real source DB resolved and verified | pass |
| 2 | Snapshot created with a SQLite-native backup API | pass |
| 3 | No raw filesystem copy of the live database used | pass |
| 4 | Destination did not pre-exist and was not overwritten | pass |
| 5 | `PRAGMA integrity_check` returned `ok` | pass |
| 6 | Source and snapshot schema versions match | pass |
| 7 | Source and snapshot conversation/message counts match | pass |
| 8 | Source before/after fingerprints show no change from this task | pass |
| 9 | Snapshot self-contained; no WAL/SHM sidecars required | pass |
| 10 | Closed snapshot hash recorded privately and stable after validation | pass |
| 11 | Read-only/query-only access works; write attempt rejected | pass |
| 12 | Private manifest complete and valid JSON | pass |
| 13 | Snapshot and manifest ignored and untracked | pass |
| 14 | No product code, tests, deps, locks, plan, or ledger changed | pass |
| 15 | No AI task, FABLE reference, Gemini judge, or remote API call run | pass |
| 16 | No private data in tracked output | pass |
| 17 | Detailed completion report exists at required location | pass |
| 18 | All delivery changes unstaged and uncommitted | pass |

## 19. WP-5.1.2B Status

WP-5.1.2B has **not** started. No conversations were selected, no 30-ID freeze
list was produced, and no FABLE references were created. The snapshot is the
fixed source that WP-5.1.2B will draw from.

## 20. Remote Call Confirmation

**No remote model or API call was made.** Nothing was sent to FABLE, Gemini, or
any other remote service. No AI task was run. No credentials or tokens were
read, used, or recorded. All work was local, offline, and confined to SQLite and
Git operations on this machine.
