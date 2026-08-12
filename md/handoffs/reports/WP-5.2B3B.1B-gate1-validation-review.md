# WP-5.2B3B.1B Gate 1 Validation Review

## Status

Resolved; ready for the mandatory manager Gate 1 commit.

## Resolution

The bounded rework was validated on 2026-08-12:

- recovery now checks the exact clean pinned commit before private run-state
  access;
- any partial or complete `proposal-gepa-*` evidence fails closed;
- the readiness contract reports `recovery_provider_calls: 0`, explicitly
  scoped to this no-call operation;
- Bootstrap's non-promotable disposition is bound to the recovered result as
  manager policy rather than recomputed quality evidence;
- both atomic destinations and interruption recovery are regression-tested; and
- fresh-process import isolation excludes production adapters, DSPy, LiteLLM,
  Google authentication, and Vertex clients.

Manager repeat validation passed: 132 focused optimizer tests, Ruff, Poetry,
and `git diff --check`. Gate 2 remained unexecuted.

The historical authorization design is sound in direction, the focused suite
passes, and the patch remains inside the intended no-call scope. Three bounded
safety/meaning issues must be corrected before the command is allowed to mutate
the private canonical run state.

## Finding 1: Recovery Does Not Enforce The Clean Pinned Commit

**Severity:** Blocking

`recover_gepa_readiness()` loads configuration and immediately begins private
state verification. It never measures the tracked implementation identity and
never proves that:

- the checkout is clean; and
- the measured commit equals `config.application_commit`.

The handoff's mandatory manager checkpoint exists specifically so recovery is
performed from the exact committed implementation. At present, the command can
write recovered state and readiness evidence from a dirty checkout or the wrong
commit.

### Required correction

- Reuse `measure_implementation()` and the same clean/pinned rule used by
  `run_optimization()`.
- Permit an injected identity probe for deterministic tests.
- Perform the check before any private state write.
- Add regressions for dirty checkout, wrong commit, and exact clean commit.
- Keep the existing proof that future optimizer execution also remains pinned.

## Finding 2: Existing GEPA Evidence Detection Is Incomplete

**Severity:** Blocking

The recovery rejects GEPA result IDs and counts files under
`proposal-gepa-*/attempts`, and later rejects GEPA candidate/result lineage.
However, a GEPA trial directory or `current.json` pointer without an attempt
file is not detected. Such a partial or interrupted state is still GEPA evidence
and must fail closed under the handoff.

### Required correction

- Reject any `proposal-gepa-*` trial directory or file, including current-only,
  malformed, or partially written evidence.
- Continue rejecting GEPA candidates, results, state membership, and nonzero
  proposer budget usage.
- Add current-only, empty-directory, candidate-only, and malformed-pointer
  regressions.
- Do not delete, normalize, or repair detected GEPA evidence.

## Finding 3: `provider_calls: 0` Is Ambiguous And Potentially False

**Severity:** Required clarity correction

The private inventory already contains retained candidate provider-response
records from P0 and Bootstrap. The readiness model and CLI summary expose the
unqualified field `provider_calls: 0`. The intended statement is that the
**recovery operation made zero new provider calls**, not that the historical run
contains no provider/model activity.

This distinction matters for later cost reconciliation and article evidence.

### Required correction

- Rename the field to `recovery_provider_calls`, `new_provider_calls`, or an
  equally explicit name.
- Keep it structurally fixed at zero.
- Update tests and the Gate 1 report.
- Do not alter historical budget or response accounting.

## Additional Required Evidence

Before returning for repeat review:

1. Confirm the recovery command still imports no production adapter, DSPy LM,
   LiteLLM, Google credential, or provider client.
2. Confirm both recovery writes remain individually atomic and a failure between
   state and readiness writes is recoverable by an idempotent rerun. Add a
   failure-injection regression if this is not already covered.
3. Confirm Bootstrap's `complete-non-promotable` disposition is an explicit
   manager policy bound to this recovered result, and document whether the
   recovery also verifies the retained privacy/context failure evidence. Do not
   present the disposition as a newly computed quality result if it is policy.
4. Refresh the completion report with finding-by-finding resolution.

## Validation Performed By Manager

- Reviewed all seven delivery files and the complete new recovery module.
- Independently ran
  `poetry run pytest tests/test_bench_optimization.py -q`: 123 passed.
- Confirmed no private recovery or provider execution was performed by the
  manager.
- Confirmed changes remain unstaged and uncommitted.

## Rework Boundary

Make only the bounded generic corrections above. Do not execute Gate 2, modify
private optimizer state, rerun P0/Bootstrap, start GEPA, allocate RunPod, access
ADC, or make model/provider/judge calls. Leave all changes unstaged and
uncommitted for repeat manager validation.
