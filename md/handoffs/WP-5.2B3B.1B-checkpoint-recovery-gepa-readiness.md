# WP-5.2B3B.1B Handoff: Checkpoint Recovery And GEPA Readiness

## Status

Authorized for execution from the clean manager commit that contains this
handoff.

This is a bounded, network-free recovery task inside WP-5.2B3B.1. It repairs
the historical-result/current-application authority boundary, registers the
already completed BootstrapFewShot result, and proves that GEPA can start from
P0. It does **not** authorize a GEPA proposal, candidate inference, fixed judging,
RunPod allocation, ADC use, or any provider call.

## Goal

Deliver one reproducible application-owned recovery path that:

1. verifies historical P0 and Bootstrap results against the exact consumed
   execution authorization that created each result;
2. permits those results to have different approved application commits without
   weakening any experiment, artifact, task, model, split, budget, or trial
   authority;
3. registers the existing completed Bootstrap result in canonical run state;
4. preserves every accepted package, result, attempt, budget record, provider
   response, and prior authorization byte-for-byte;
5. is idempotent and makes zero model/provider calls; and
6. produces a GEPA-readiness artifact proving that P0, not Bootstrap, is the
   next parent.

Successful completion means the private run is durably and verifiably ready for
a separately authorized GEPA pilot. It does not mean GEPA has started.

## Background

The accepted automatic-optimization run contains:

- one frozen P0 result produced under an earlier clean application commit;
- one completed BootstrapFewShot result from append-only attempt `0003`,
  produced under a later clean application commit containing DSPy compatibility
  repairs;
- a complete Bootstrap candidate package and validation result;
- four labeled demonstrations and no accepted generated demonstration;
- preserved attempts `0001`, `0002`, and `0003`;
- budget, usage, latency, response, and authorization evidence;
- no GEPA result or proposer call.

Bootstrap completed at 11/32 valid, equal to P0 on reliability but lower on
semantic agreement. It failed the 8,192-token context-fit and prompt-privacy
promotion gates. A later local fixed-judge comparison also slightly favored P0.
Bootstrap is therefore a closed, non-promotable comparator. P0 remains the GEPA
parent regardless of this recovery's outcome.

The phase wrapper failed after Bootstrap had already persisted valid evidence.
It rechecked historical P0 as if P0 had been produced by the current Bootstrap
application commit, resulting in `optimizer result application identity
mismatch`. The result's own authority correctly names its creation commit. The
recovery must respect that history rather than rewrite it.

## Manager Decisions

The owner and development manager authorize the executor to:

- inspect the repository implementation, synthetic tests, and ignored private
  optimizer metadata required for this recovery;
- read manifests and artifact bytes only through existing verification paths
  where needed to recompute hashes;
- implement a generic authority/recovery operation and focused tests;
- after the manager commits the generic patch, run exactly one local no-call
  recovery against the existing private run;
- write new ignored recovery/checkpoint/readiness evidence atomically; and
- update the tracked completion report and existing progress/activity documents
  with privacy-safe evidence.

This authorization is complete for the local no-call scope. Do not ask for
permission to inspect the known private optimizer metadata, run local tests, or
execute the no-call recovery after the required manager commit.

No authorization is granted for:

- network access by the optimizer;
- Vertex, Gemini, LiteLLM, DSPy LM, LM Studio, or candidate-model calls;
- RunPod allocation, restart, transfer, or persistent-volume access;
- ADC discovery, refresh, login, or token inspection;
- opening the twenty-conversation holdout;
- semantic inspection of raw train/validation conversation text;
- rerunning P0 or Bootstrap;
- creating a GEPA proposal; or
- altering accepted experiment settings.

## Core Authority Invariant

A historical result is valid when all of the following hold:

1. the result is structurally valid and its own stable hash verifies;
2. its referenced candidate package and terminal trial authority verify;
3. its complete `ResultAuthority` matches exactly one consumed, append-only
   `ExecutionAuthority` retained by the same run;
4. that execution authorization's own stable hash and run membership verify;
5. immutable experiment identity remains compatible with the accepted run:
   run, task contracts, selected P0 catalog, train/validation manifests, model
   artifact hashes, optimizer identity, proposer policy, context, seed, privacy
   policy, and budget policy; and
6. any difference in application commit/config identity is explained by that
   exact consumed authorization rather than inferred from the current checkout.

The current clean application commit governs **new execution**. It must not be
retroactively imposed on accepted historical results.

Do not solve the defect by ignoring `application_commit`, dropping config
identity, accepting any authorization in the directory, comparing only selected
fields ad hoc, mutating historical authority, or substituting the latest
authorization for the one actually consumed.

## Non-Goals

- Do not improve Bootstrap prompts or demonstrations.
- Do not reconsider Bootstrap promotion.
- Do not repair candidate outputs.
- Do not alter FABLE references or deterministic metrics.
- Do not change the frozen 6/4 development split or inspect the 20-conversation
  holdout.
- Do not change Qwen, Phi, context, generation, retry, privacy, or budget policy.
- Do not combine this task with GEPA execution or RunPod setup.
- Do not rewrite historical artifacts merely to make current verification pass.

## Gate 0: Preflight And Frozen Inventory

1. Confirm the branch is `main` and Poetry resolves to this repository's
   `.venv`.
2. Confirm the tracked checkout starts clean at the manager commit containing
   this handoff.
3. Confirm ordinary Chronicle imports do not initialize DSPy, LiteLLM, Google
   credentials, or provider clients.
4. Locate only the known ignored optimizer run and returned immutable evidence.
   Do not scan unrelated user directories.
5. Record privacy-safe hashes and counts for:
   - run state;
   - P0 package and result;
   - Bootstrap package and result;
   - attempts `0001`, `0002`, and `0003`;
   - current trial pointers;
   - consumed execution authorizations;
   - budget/accounting state;
   - existing response evidence; and
   - the frozen train/validation manifests.
6. Confirm no GEPA result, proposal attempt, or proposer usage exists.
7. Confirm holdout files opened is zero.

If the local private recovery set is incomplete, stop and identify the missing
artifact class. Do not restart RunPod or reconstruct evidence under this
handoff.

## Gate 1: Generic Repair And Synthetic Validation

### Required implementation

Implement one application-owned recovery/verification path. It may extend the
existing `bench` CLI or add a narrowly named recovery command, but it must:

- operate without constructing production candidate or optimizer adapters;
- perform no credential or network initialization;
- resolve each result to exactly one consumed execution authorization;
- validate historical P0 and newer Bootstrap authorities independently;
- verify immutable experiment compatibility across those authorizations;
- reconstruct canonical run-state/checkpoint membership from append-only
  evidence;
- identify P0 explicitly as the future GEPA parent;
- reject recovery if any GEPA attempt/result already exists;
- write new state atomically using the accepted Windows sharing-violation retry;
- preserve existing attempts and current pointers;
- produce a stable recovery/readiness hash; and
- be idempotent: a second invocation must be a byte-stable no-op or produce the
  same canonical artifact without modifying accepted evidence.

If the cleanest model requires a schema/version increment for run state or a
new phase/readiness checkpoint model, add an explicit backward-compatible
migration. Do not overload `PilotCheckpoint`, which describes a completed GEPA
pilot and does not yet apply.

### Required regressions

Add focused synthetic tests proving at least:

1. historical P0 and Bootstrap results created by two different clean commits
   are both accepted when each exactly matches its consumed authorization;
2. the same current checkout is not required for historical result validity;
3. new execution still requires the configured current clean commit;
4. missing, dangling, duplicate, stale, foreign-run, or hash-invalid
   authorization references fail closed;
5. changing an immutable experiment field fails even when the application
   commit is valid;
6. changing only an application commit without a matching consumed
   authorization fails;
7. candidate, result, trial, and authorization identity mismatches fail with
   actionable diagnostics;
8. the existing Bootstrap result is registered without calling an adapter;
9. P0 is selected as the GEPA parent and Bootstrap cannot become the parent;
10. an existing GEPA attempt/result blocks recovery;
11. recovery preserves attempts `0001`/`0002`/`0003` and their current pointer;
12. repeated recovery is idempotent and byte-stable;
13. an interrupted atomic replacement on Windows follows the accepted bounded
    retry path; and
14. historical synthetic packages and ordinary optimizer lifecycle tests remain
    compatible.

### Gate 1 validation

Run at minimum:

```powershell
poetry env info --path
poetry run pytest tests/test_bench_optimization.py -q
poetry run pytest
poetry run ruff check .
poetry check
poetry run python -m bench --help
poetry run python -m bench <recovery-command> --help
git diff --check
git status --short
git diff --cached --name-only
git ls-files .chronicle
```

No synthetic test may use network access, real credentials, private source text,
or model inference.

### Mandatory manager checkpoint

Stop after Gate 1 with all changes unstaged and uncommitted. Deliver:

- root-cause confirmation;
- implementation summary;
- focused and full validation evidence;
- exact files changed;
- confirmation that no private recovery or provider call occurred; and
- final Git status.

The development manager validates and commits the generic patch. This is the
single expected implementation checkpoint in the handoff, not a task failure.
Do not execute Gate 2 from a dirty checkout.

## Gate 2: Private No-Call Recovery

Resume only after the manager supplies the new clean commit.

1. Confirm the local checkout is clean at that exact commit.
2. Reverify the Gate 0 private inventory and prove all accepted historical
   hashes remain unchanged.
3. Run the recovery command once against the ignored private optimizer config.
4. Confirm it instantiates no candidate/optimizer/provider adapter and makes no
   network, credential, model, or judge call.
5. Verify the recovered canonical state includes exactly:
   - one accepted P0 result;
   - one accepted Bootstrap result from attempt `0003`;
   - zero GEPA results and zero GEPA attempts;
   - all consumed historical authorization identities;
   - reconciled existing budget/accounting without new reservations;
   - an explicit non-promotable Bootstrap disposition; and
   - P0 as the next GEPA parent.
6. Verify attempts `0001`, `0002`, and `0003`, candidate/result packages,
   provider responses, budget records, fixed-judge evidence, and source
   manifests remain byte-identical.
7. Run the recovery command a second time and prove idempotency and no writes to
   accepted evidence.
8. Run inspect/verify/readiness commands and prove they succeed without network
   access.
9. Record holdout files opened as zero. Do not inspect raw holdout identities or
   content.

If any private artifact fails verification, stop. Do not weaken the repair,
edit the artifact, rerun P0/Bootstrap, or start GEPA.

## Gate 3: GEPA Readiness Evidence

Create one ignored, stable readiness artifact and summarize it in the tracked
completion report. It must establish:

- canonical P0 and Bootstrap result membership;
- exact authorization resolution for each historical result;
- P0 as GEPA parent;
- Bootstrap as completed and non-promotable;
- zero GEPA proposals/results/calls;
- zero new budget reservations or provider usage;
- remaining configured call/token/time/cost capacity without exposing private
  values;
- frozen 6/4 split and zero holdout access;
- required next clean application commit/config transition procedure;
- requirement to use the Windows ADC guide for local Vertex work or the RunPod
  RAM-backed ADC guide for remote GEPA; and
- a clear statement that a new owner authorization is still required before
  allocating compute or making the first GEPA proposer call.

Do not perform an ADC probe merely to declare readiness.

## Deliverables

Create:

`md/handoffs/reports/WP-5.2B3B.1B-checkpoint-recovery-gepa-readiness-completion-report.md`

Update, without rewriting historical observations:

- `md/handoffs/reports/WP-5.2B3B.1-execution-progress.md`;
- `md/research/WP-5.2B3B.1-prompt-optimization-activity-log.md`; and
- `md/development-ledger.md` only to mark the executor delivery ready for PM
  validation, not accepted.

The completion report must include:

- plain-language executive summary;
- exact root cause and authority invariant;
- files changed and migration/compatibility decisions;
- synthetic regression matrix;
- manager checkpoint commit identity;
- privacy-safe private recovery evidence;
- before/after/second-run immutability and idempotency evidence;
- P0-parent and zero-GEPA proof;
- budget/readiness summary;
- tests and checks;
- limitations and exact next authorization boundary; and
- final Git status.

Keep raw private paths, IDs, hashes that identify private content, selected
inputs, FABLE references, candidate outputs, provider responses, credentials,
and generated readiness artifacts under ignored storage. Tracked reports may
include application commit IDs and aggregate counts but not private artifact
identities.

## Stop Conditions

Stop immediately, without recovery writes, if:

- required historical evidence is missing or hash-invalid;
- a result cannot resolve to exactly one consumed authorization;
- immutable experiment identity differs beyond the explicitly modeled
  historical execution boundary;
- any GEPA attempt/result/provider usage already exists;
- recovery would require rerunning P0 or Bootstrap;
- train or holdout semantic content would need manual inspection;
- a credential, network, provider, model, judge, RunPod, or ADC operation would
  occur;
- accepted package/result/trial/budget/provider evidence would need rewriting;
- recovery would make Bootstrap promotable or select it as GEPA parent; or
- the private recovery must run before the manager commits Gate 1.

## Acceptance Criteria

1. Historical P0 and Bootstrap results verify against their own exact consumed
   authorizations.
2. Immutable experiment compatibility remains strict and explicitly modeled.
3. New execution remains pinned to the current clean application commit.
4. Existing P0, Bootstrap, attempts, budget, and response evidence are unchanged.
5. The completed Bootstrap result is registered canonically without rerun.
6. Recovery is atomic, idempotent, and network-free.
7. P0 is the explicit GEPA parent; Bootstrap remains non-promotable.
8. Zero GEPA attempt, proposal, candidate inference, judge, credential, or
   provider call occurs.
9. Holdout access remains zero.
10. Focused and full suites, Ruff, Poetry, CLI, diff, tracking, and privacy
    checks pass.
11. A stable ignored readiness artifact and privacy-safe completion report are
    delivered.
12. The repository is left unstaged and uncommitted for PM validation.

## Commit Boundary

The executor must never stage or commit changes. The development manager owns
both commits:

1. the mandatory Gate 1 generic implementation commit; and
2. the final completion/report commit after Gate 2/3 PM validation.
