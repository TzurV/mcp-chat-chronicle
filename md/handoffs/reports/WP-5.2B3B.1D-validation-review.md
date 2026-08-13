# WP-5.2B3B.1D Validation Review

**Status:** Offline rework accepted; private lifecycle validation pending

## Rework validation addendum

The bounded offline rework resolves the four findings below:

- Chronicle now selects a GEPA component represented by an eligible trace in
  the reflection minibatch, with a regression for the observed `task_0` versus
  tasks `1`, `3`, and `2` mismatch.
- A network-free synthetic proof now enters through tracked `run_optimization`
  orchestration and the production DSPy GEPA adapter. It persists normal
  candidate, result, trial, budget, lineage, privacy, and verification evidence.
- Formatting failures are explicitly excluded from reflection because the
  pinned DSPy behavior would include raw malformed output. They remain terminal
  deterministic failures without repair or semantic retry.
- Callback accounting records exact logical candidate/proposer calls across
  DSPy LM copies. Measured provider usage remains distinct from conservative
  reservations when a provider does not expose complete token data.

Manager validation reran the newly added regression groups: 15 parameterized
cases passed. Ruff and `git diff --check` also passed. The executor's complete
suite evidence remains 626 passed and one expected skip.

The original findings remain below as the historical reason for rework. They
are resolved for the offline gate. WP-5.2B3B.1D is still open because the
handoff requires the authorized private smoke to produce, evaluate, verify, and
zero-call replay one distinct candidate.

## Executive decision

The provider-error repair and hosted route qualification are acceptable, but the work package is not complete. The handoff requires the private smoke to create and evaluate one distinct GEPA candidate. It created none.

The private stop is not evidence that the selected development examples lacked useful reflective feedback. The retained GEPA log shows a deterministic multi-task batching mismatch: the round-robin selector chose `task_0`, while the three sampled examples were tasks `1`, `3`, and `2`. With no `task_0` trace in the minibatch, GEPA could not construct a reflective dataset and never called the proposer.

## Blocking findings

### 1. GEPA component selection is incompatible with the mixed-task minibatch

The current production bridge relies on DSPy/GEPA defaults for component selection and reflection minibatch construction. Chronicle has four task-specific predictors, but the selected component is not guaranteed to occur in the sampled minibatch.

Required rework:

- Add a generic, deterministic component/minibatch policy that guarantees at least one trace for the selected component.
- Prefer a task-aware component selector or task-stratified minibatch implementation over increasing the batch by accident.
- Preserve one-conversation private scope, frozen P0, schemas, selectors, FABLE references, budgets, and append-only evidence.
- Add a regression reproducing the observed mismatch: selected `task_0`, sampled tasks `1`, `3`, `2`, zero matching traces.
- Prove the corrected policy invokes the proposer and produces one distinct candidate without inspecting content to choose the component.

### 2. Synthetic lifecycle evidence bypasses the supported optimizer orchestration

The successful synthetic lifecycle was driven by the ignored `.chronicle/wp-5.2b3b.1d/local_gepa_operator.py`. That script constructs `dspy.GEPA` directly, mutates and writes a package itself, and evaluates it through a custom loop. It does not call the tracked `run_optimization` lifecycle or use its normal budget, trial, result, and append-only persistence boundaries.

Required rework:

- Exercise the corrected synthetic and private lifecycle through the tracked Chronicle optimizer entry point.
- If the existing entry point cannot express this bounded lifecycle, add a generic tracked command or adapter rather than treating an ignored experiment script as production evidence.
- Require normal candidate, result, usage, lineage, authorization, and replay artifacts from the supported path.
- Keep operator-only scripts and private artifacts ignored.

### 3. Structured-output failure feedback policy is implicit

GEPA defaults to excluding formatting failures from reflective feedback. These AI tasks depend on strict JSON schemas, and output-format reliability is a primary optimization objective.

Required rework:

- Make the format-failure feedback policy explicit in Chronicle configuration/code.
- Either provide sanitized, bounded feedback for schema/JSON failures or document and test why those failures are excluded.
- Do not disclose raw malformed outputs unless already authorized and privacy-scanned.
- Add tests proving the selected policy is stable and does not repair or semantically retry candidate output.

### 4. Usage evidence is not complete enough for final acceptance

The completion report labels measured token usage and cost as partial and substitutes a conservative reservation. Conservative accounting is correct for safety, but the handoff also requires complete provider/model/call/retry/token/latency/cost denominators for the lifecycle result.

Required rework:

- Capture exact logical call counts for proposer, surrogate evaluation, and qualification separately.
- Capture measured usage where the provider exposes it and clearly isolate any genuinely unavailable fields.
- Reconcile the conservative reservation without presenting it as measured usage.

## Accepted work

- Primary provider errors are no longer masked by secondary serialization/reconciliation failures.
- `OptimizerOperationError` is serializable across GEPA's process boundary.
- Incomplete usage retains the conservative interrupted reservation.
- Both configured Vertex routes qualified in `global`.
- Existing focused/full-suite, Ruff, Poetry, privacy, and tracking evidence is credible, subject to rerunning after rework.

## Authorized next scope

The executor may implement and validate the generic offline repair without model calls. After manager review and commit, one fresh bounded synthetic lifecycle may run through the supported path. A new private provider run still requires explicit owner authorization because the previous private attempt is retained append-only.

Do not claim P0 improvement, rerun historical P0/Bootstrap work, access holdout data, start fixed judging, allocate RunPod, or broaden the private scope.

## Completion criteria

WP-5.2B3B.1D can be accepted when:

1. The supported tracked lifecycle produces and evaluates one distinct synthetic candidate.
2. The supported tracked lifecycle produces and evaluates one distinct candidate for the authorized one-conversation private smoke.
3. Both artifacts verify in a fresh process and replay with zero provider calls.
4. Component/minibatch alignment and format-failure feedback policy are explicitly tested.
5. Usage and cost accounting are reconciled with clear measured versus reserved values.
6. Full validation, privacy checks, and an updated completion report pass.
