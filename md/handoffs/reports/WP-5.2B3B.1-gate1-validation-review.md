# WP-5.2B3B.1 Gate 1 PM Validation Review

**Date:** 2026-08-06  
**Decision:** Gate 1 and the Vertex proposer-route amendment accepted; private/paid execution remains separately gated

## Executive decision

The final delivery resolves the original nine findings, the four repeat-review
findings, and the final component-wise continuation defect. The tracked CLI now
reaches a resumable orchestrator; authority, budgets, trials, candidate/result
identity, BootstrapFewShot demonstrations, complete-request context accounting,
timing, verification, pilot continuation, and shortlist selection are connected.

Gate 1 is accepted for manager commit. This acceptance covers the generic,
network-independent optimizer foundation only. It does not authorize private
transfer, credentials/ADC, RunPod allocation, Vertex, Anthropic, or other provider calls, or
spending. Those actions remain gated by the owner's explicit approval of the
recorded disclosure wording and final cost ceilings.

## Repeat Review Findings

### 1. Blocker: BootstrapFewShot demonstrations are not packaged or replayed

`bench/optimization/dspy_bridge.py:49` reconstructs candidates from signature
instructions only. DSPy BootstrapFewShot stores its learned examples as predictor
demonstrations, while `bench/optimization/production.py:248` returns only
`prompts_from_program(compiled)`. The resulting Chronicle package therefore
does not contain or replay the labeled/bootstrapped demonstrations. In practice,
the claimed BootstrapFewShot comparator can become P0 prompt text with different
lineage rather than a compiled few-shot program.

Required rework:

- define a deterministic, safe representation that renders the accepted bounded
  demonstrations into the four candidate prompt texts, or explicitly extend the
  immutable candidate package while retaining the prompt-only mutation contract;
- prove the packaged candidate differs from P0 when DSPy selected demonstrations
  and that `LiteLLMCandidateAdapter` actually sends those demonstrations;
- enforce the one-labeled/one-bootstrapped limit, source/reference authority,
  privacy scan, stable identity, token accounting, and safe serialization;
- add a network-free test through the real DSPy BootstrapFewShot bridge, not only
  `FakeOptimizerAdapter`.

### 2. Blocker: the runner cannot perform an authorized continuation

`bench/optimization/execution.py:179` always constructs the budget ledger with
`pilot=True`, and the loop at line 255 always stops at `pilot_candidates`. A
subsequent `resume` remains at the same limit and immediately returns terminal.
The configured 40-candidate and twelve-hour ceilings are therefore descriptive
only; the handoff's continuation rule cannot be executed from the committed
application.

Required rework:

- make the four-hour pilot a durable state/checkpoint with an explicit computed
  continuation decision using all four declared criteria;
- allow the same authorized run to stop with a valid pilot no-improvement result
  or continue under total ceilings without changing completed evidence;
- enforce the 3,000-invocation ceiling before calls and derive the achievable
  candidate count rather than assuming all 40 can be evaluated;
- test pilot stop, permitted continuation, budget-limited continuation, resume,
  and unchanged attempt authority.

### 3. High: prompt-fit guardrail does not measure the complete request

`bench/optimization/execution.py:541` takes only the maximum system-prompt token
estimate, and line 582 compares that value with the 7,000-token prompt ceiling.
The selected transcript, task user prompt, schema/tool overhead, and output
allowance used by `bench/optimization/production.py:109` are excluded. A
candidate can consequently be marked `prompt_fits_context=True` while its real
request exceeds the fixed 8,192-token context.

Required rework:

- compute a conservative per-case total request envelope from the actual system
  prompt, selected input/user prompt, schema overhead, and output allowance;
- persist the maximum observed/estimated envelope and fail the shortlist
  guardrail when any required case cannot fit 8,192 tokens;
- keep provider context failures as experiment outcomes, but do not label such a
  package context-fit based only on system-prompt size;
- add boundary tests for just-inside and just-outside requests.

### 4. Medium: optimizer/proposer latency is not retained

`bench/optimization/production.py:455` derives calls and token usage from DSPy
history but explicitly adds zero latency. That value is not replaced by a wall
clock around BootstrapFewShot/GEPA compilation, so the required proposer and
optimizer timing evidence cannot be produced later.

Required rework:

- capture monotonic wall time for each BootstrapFewShot and GEPA proposal attempt;
- retain latency in append-only trial/result evidence and aggregate inspection;
- do not invent per-provider latency when the provider does not return it;
- add interrupted/resumed timing-accounting coverage.

### 5. Blocker: pilot continuation comparison is lexicographic

The second repeat delivery implements the continuation checkpoint, but
`bench/optimization/execution.py:558` compares the three reliability values as
tuples using `>=`. Python tuple ordering is lexicographic: a higher total-valid
count can make the expression true even when worst-model validity or
minimum-task validity is lower than P0. The handoff requires one candidate to be
no worse on all three measures independently before paid continuation.

Required narrow rework:

- replace the tuple comparison with explicit component-wise checks requiring
  total validity, worst-model validity, and minimum-task validity each to be at
  least the corresponding P0 value for the same candidate;
- add a regression where total validity improves but worst-model validity falls;
- add a regression where total validity improves but minimum-task validity falls;
- preserve the accepted BootstrapFewShot, continuation, request-envelope,
  timing, authority, budget, and test changes unchanged.

## Repeat Validation Evidence

- The manager independently reran `tests/test_bench_optimization.py` after the
  final correction: 50 passed.
- The executor's final full-suite result is 524 passed and one skipped.
- The original nine findings, four repeat findings, and final component-wise
  continuation finding were checked in the current code and are resolved.
- No private/provider/paid action or holdout access occurred.
- Nothing is staged or committed.

## Original Gate 1 Review (Historical)

The findings below describe the first delivery and are retained as the audit
trail. They are resolved in the repeat delivery and must not be reimplemented or
reverted while addressing the four repeat-review findings above.

The original Gate 1 patch had useful safety foundations and its reported dependency,
split, no-call, and local validation evidence is credible. It is not yet the
complete generic optimizer execution boundary required by the handoff.

The manager must not commit this exact patch because the tracked CLI can only
write an execution-intent file. The actual provider-facing optimization driver
is absent, and several critical controls are therefore not connected to the
execution path. A private untracked driver would make the remote experiment
non-reproducible and could bypass the declared metrics, budgets, privacy gate,
and shortlist rules.

No private transfer, paid compute, proposer call, or model call is authorized by
this review. Rework remains inside Gate 1 and must stay unstaged/uncommitted.

## Original Findings

### 1. Blocker: no tracked end-to-end optimizer execution path

`bench/__main__.py:218` routes both `optimize` and `resume` to
`authorize_execution()`. `bench/optimization/operations.py:128` only writes an
execution-intent JSON file. The BootstrapFewShot, GEPA, proposer, budget,
feedback, privacy, package, and trial primitives are not called by any tracked
execution orchestrator.

This means the committed application would not reproduce the remote experiment.
It also means the four disclosure flags authorize an intent but do not guard the
actual calls.

Required rework:

- add a tracked, testable orchestrator consumed by `optimize` and `resume`, or a
  separately named tracked run command whose relationship to the intent is
  explicit;
- execute BootstrapFewShot and GEPA through injected candidate/proposer adapters;
- evaluate both Qwen and Phi, generate deterministic feedback, persist
  append-only attempts, apply privacy checks, and produce verified packages;
- consume the authorization intent and bind it to the clean application commit,
  configuration hash, split hashes, models, proposer, budgets, and run ID;
- make the remote operator entry point part of the committed source, not an
  ignored helper script;
- add an end-to-end synthetic run and resume test with fake providers and zero
  network access.

### 2. Blocker: shortlist export does not implement the selection contract

`bench/optimization/operations.py:165` collects privacy-eligible packages and
sorts them only by `candidate_id` at line 175. It does not apply the accepted
lexicographic metrics, P0 guardrails, model/task reliability floors, terminal
accounting, 8K fit, lineage diversity, or no-leak provenance. It can also return
fewer than three candidates while reporting success.

Required rework:

- rank complete packages using the declared `MetricVector` ordering;
- apply all P0, worst-model, minimum-task, privacy, terminal-accounting, and
  prompt-fit guardrails;
- include immutable P0 plus three to five eligible GEPA candidates, or produce a
  clear no-improvement result when fewer than three qualify;
- fail on missing/inconsistent metrics or trial authority;
- add deterministic ordering, boundary, no-improvement, and tampering tests.

### 3. Blocker: preflight does not prove split authority or zero holdout access

`bench/optimization/operations.py:22` verifies each supplied split manifest in
isolation, but never reads `paths.development_manifest`, proves the train and
validation manifests share the accepted parent, proves they are disjoint, proves
their union equals the accepted ten conversations, or validates required input
and reference files. The returned `zero_holdout` value at line 56 is a constant.

Required rework:

- bind and hash-verify the accepted ten-conversation development manifest;
- independently reconstruct or validate the deterministic 6/4 split;
- prove train/validation disjointness, union, order, provider quotas, length
  quotas, case counts, and parent identity;
- bind and verify the selected inputs and FABLE references needed by each case;
- derive the zero-holdout assertion from verified authority rather than setting
  it to `True`;
- add overlap, foreign-parent, altered-order, duplicate, missing-file,
  substituted-reference, and holdout-contamination tests.

### 4. High: hard budgets are not enforced before calls

`bench/optimization/budget.py:22` checks a supplied counter only after values
exist. It is not connected to any proposer or candidate call, does not reserve
the next call before execution, and does not persist authoritative cumulative
usage. Token and cost ceilings can therefore be exceeded by the missing driver.

Required rework:

- implement atomic pre-call reservation for candidate, task, proposer, retry,
  elapsed-compute, token, and projected-cost budgets;
- reconcile reservations with actual usage after each attempt;
- persist counters across resume and fail closed on missing/inconsistent usage;
- stop before, not after, a call that would exceed a ceiling;
- test exact-boundary, one-over-boundary, interrupted-call, missing-usage, retry,
  and resumed-run behavior.

### 5. High: current-attempt authority may point to stale history

`bench/optimization/trials.py:72` validates the pointer hash but does not require
`current_attempt` to reference the latest existing attempt. This reintroduces the
stale-attempt ambiguity previously fixed in the accepted benchmark package path.

Required rework:

- require new optimizer authorities to point to the latest attempt;
- retain explicit documented legacy behavior only if a real legacy artifact
  needs it;
- reject missing, dangling, stale, and hash-mismatched pointers with actionable
  diagnostics;
- add regressions for each state.

### 6. High: candidate identity is coupled to mutable result fields

`bench/optimization/package.py:42` derives `candidate_id` from prompts,
contracts, metrics, accounting, and privacy. Adding evaluation metrics or privacy
results therefore changes the identity of the same prompt candidate and can make
lineage, trial references, and cache identity unstable.

Required rework:

- define a stable prompt-candidate identity from immutable prompt/package and
  lineage fields;
- keep evaluation/accounting/privacy evidence in a separately hashed immutable
  result envelope, or define a second artifact identity;
- prove that evaluating, rescoring, or privacy-checking a prompt does not change
  its candidate identity;
- test lineage, cache, package verification, and resume with this separation.

### 7. High: candidate verification is only self-validation

`verify_candidate()` reads a candidate JSON and reports success if its internal
Pydantic/hash checks pass. It does not bind the candidate to the accepted P0
contracts, config, split, model artifacts, metrics, trial authority, or privacy
scanner provenance.

Required rework:

- make optimizer package verification config-aware;
- verify all immutable contracts against accepted P0;
- verify run/split/model/proposer/optimizer identities and result-envelope
  hashes;
- verify terminal accounting and privacy-scanner version/result;
- retain a separate syntax-only inspection command if useful, but do not label
  syntax-only validation as complete package verification.

### 8. Medium: proposer options are not equally operational

`ProposerProfile` and `proposer_lm()` require an API-key environment variable.
That supports the recommended first-party Anthropic route but does not support
the report's Vertex ADC fallback as described. Region and credential mode are
not applied by the bridge itself.

Required rework:

- either remove the Vertex option from this checkpoint, or model credential
  mode explicitly and prove ADC plus region propagation;
- bind proposer request parameters, effort/reasoning policy, timeout,
  concurrency, and response usage to config and cache/run identity;
- predeclare whether BootstrapFewShot uses the candidate model or a separate
  teacher and account for its calls/disclosure accordingly.

### 9. High: tests validate primitives, not the promised lifecycle

The focused suite passes, but it has no synthetic end-to-end optimize/resume
test, no provider-call adapter test, no shortlist-rule test, no authoritative
split tampering matrix, and no proof that budgets are enforced around calls.

Required rework:

- add the focused tests required by findings 1-8;
- test all CLI lifecycle commands through synthetic artifacts;
- prove ordinary installs/imports work without the optimization extra and an
  isolated install with the extra works;
- keep all tests network-independent and privacy-safe.

## Evidence accepted at this checkpoint

- The repository started clean on `main` at `365bb815...`.
- Poetry resolves to the repository-local `.venv`.
- The manager reran the focused optimizer suite: 18 passed.
- The executor-reported full suite, Ruff, Poetry, CLI, tracking, and diff checks
  passed.
- DSPy 3.3.0 and GEPA 0.1.1 are stable published versions and the reported wheel
  hashes match PyPI.
- The proposed accepted P0 hash and reported 6/4 aggregate split match the
  handoff, subject to the preflight-authority rework above.
- No provider call, private transfer, paid compute, or holdout access was made.

## Proposer and cost recommendation

After the implementation rework passes, the manager recommends:

- proposer: Anthropic first-party `claude-sonnet-5` through LiteLLM;
- processing: global;
- hard proposer cap: US$50;
- call cap: 250;
- declared envelope: 12.5 million input and 2 million output tokens;
- credential: temporary `OPTIMIZER_PROPOSER_API_KEY`, supplied only through the
  approved secret/environment mechanism and revoked after teardown.

Anthropic's official documentation confirms the model ID and introductory
US$2/US$10 per-million input/output pricing through 2026-08-31. The proposed
US$45 envelope and US$50 hard cap reconcile at those rates. This recommendation
still requires explicit owner approval before calls.

RunPod's public page currently lists RTX 5090 at US$0.99/hour. Keep the configured
compute ceiling at no more than US$12.05, but the owner must confirm the actual
console GPU and storage rates before allocation.

## Required disclosure wording

Use this clearer wording for owner approval after rework:

> I authorize the bounded WP-5.2B3B.1 pilot to process only the frozen six-train
> and four-validation development conversations. The owner-controlled RunPod Pod
> may receive their selected source chat text, corresponding FABLE reference
> fields, accepted schemas/contracts, current prompt candidates, Qwen/Phi
> candidate outputs, and structured deterministic diagnostics. Anthropic
> `claude-sonnet-5` through the global first-party API may receive only the
> selected development source text, current prompts, candidate outputs, relevant
> FABLE reference fields, schemas/contracts, and bounded diagnostics required by
> BootstrapFewShot or GEPA. No holdout content or identity, unrelated history,
> live database, fixed-judge rationale or credential, raw provider error,
> environment value, or historical package outside the accepted controls is
> authorized. Limits are 250 proposer calls, US$50 proposer cost, four hours for
> the initial RunPod pilot, and no more than the separately confirmed RunPod
> compute cap. One infrastructure retry is allowed; semantic retries and output
> repair are not.

## Rework delivery

The executor should update the existing Gate 1 patch and progress report rather
than create a new work package. Leave all files unstaged and uncommitted. Report:

- exact files changed;
- focused and full validation;
- synthetic end-to-end call/accounting evidence;
- revised preflight and shortlist evidence;
- final `git status --short`;
- confirmation that no private/provider/paid action occurred.

Return status as `Ready for repeat Gate 1 PM validation`.

## Provider-route amendment — 2026-08-06

The owner subsequently selected Google Vertex AI instead of the historical Anthropic recommendation.
This amendment does not reopen the accepted Gate 1 findings or authorize the private pilot. The
tracked selected proposer is `vertex_ai/gemini-3.1-pro-preview`, provider Google Vertex AI, location
`global`, credential mode `vertex-adc`, temperature zero, reasoning `none`, concurrency one, one
infrastructure retry, no semantic retry, and no output repair.

Tracked configuration contains only the environment-variable names `GOOGLE_CLOUD_PROJECT`,
`GOOGLE_CLOUD_LOCATION`, `VERTEXAI_PROJECT`, `VERTEXAI_LOCATION`, and
`GOOGLE_GENAI_USE_VERTEXAI`. The real project value, ADC material, credential values/files, and
private paths are prohibited from configuration and artifacts. Runtime project/location resolution
and ADC availability checks occur only when an explicitly authorized production proposer is built.

The proposer ceilings are 250 calls, 12.5 million input tokens, and 2 million output tokens including
reasoning. At US$2/million input and US$12/million output, the calculated maximum is US$49; the hard
cap remains US$50. Pre-call reservation, retained interruption accounting, and all prior candidate,
continuation, context, timing, privacy, authority, and shortlist controls remain authoritative.

The optimizer proposer and later fixed judge are both Gemini 3.1 Pro. The fixed judge remains outside
the optimization loop, and no fixed-judge rationale or score is supplied to BootstrapFewShot or GEPA.
This same-family evaluation-bias risk must be disclosed in the completion report and any article; it
does not invalidate deterministic schema, evidence, reliability, runtime, or cost measurements.

The provider amendment was independently reviewed after its injected, network-free validation. The
manager reran the focused optimizer suite (`68 passed`), Ruff, Poetry validation, and diff checks; the
executor's complete suite reported `542 passed, 1 skipped`. The amendment is accepted for commit.

This acceptance grants no authority to access ADC, call Vertex or Anthropic, transfer private data,
allocate paid resources, spend money, or access holdout data. Those actions remain subject to the
owner's explicit bounded disclosure and cost authorization.

## Synthetic production-route repair — 2026-08-09

The first authorized synthetic Vertex gate returned a provider response, then failed while adapting
DSPy 3.3 usage history. DSPy stores typed `LMHistoryEntry` values; the application incorrectly used
the legacy mapping-only `.get(...)` contract. The repair accepts both legacy mappings and typed DSPy
history while reading usage metadata only. Privacy-safe boundary diagnostics and regressions were
added without changing provider, model, prompt, schema, retry, budget, or optimization behavior.

The manager independently reran the focused optimizer suite (`69 passed`), Ruff, Poetry validation,
and diff checks. The executor's complete suite reported `543 passed, 1 skipped`. The generic repair
is accepted for commit. The original attempt remains conservatively charged as 2 calls, 100,000 input
tokens, 16,000 output/reasoning tokens, and US$0.392 because the exact provider attempt count cannot
be proven. No private development data, holdout data, RunPod action, or provider rerun occurred.

Only one corrected synthetic production-route gate, plus its configured infrastructure retry, is
authorized after this repair commit. Private-pilot execution remains blocked until that gate passes
and the manager explicitly releases it.

## Generalized typed-usage repair — 2026-08-09

The corrected synthetic gate returned a provider response but exposed a nested DSPy/LiteLLM typed
`CompletionTokensDetailsWrapper` that the first compatibility repair did not normalize. The second
repair replaces field-specific mapping assumptions with one bounded accessor for mappings, typed
attributes, and model-dump-compatible objects. It covers prompt/input and completion/output aliases,
top-level and nested reasoning, missing optional values, and fail-closed unsupported populated
structures. Duplicate reasoning reports are included once through their maximum.

The ignored gate runner's Windows pointer-update failure was separate from production persistence.
Production already uses bounded atomic replacement for Windows sharing violations; the ignored runner
now reuses that implementation. Append-only attempt evidence remains authoritative.

The manager independently reran the focused optimizer suite (`80 passed`), Ruff, Poetry validation,
and diff checks. The executor's complete suite reported `554 passed, 1 skipped`. The generalized
repair is accepted for commit. Cumulative conservative accounting remains 4 calls, 200,000 input
tokens, 32,000 output/reasoning tokens, and US$0.784. No provider call, ADC access, private-data or
holdout access, RunPod action, or pilot activity occurred during this repair.

One post-commit synthetic production-route gate, plus its configured infrastructure retry, remains
authorized. Private-pilot execution remains blocked until the gate passes and the manager releases it.

## Corrected synthetic production-route gate — 2026-08-09

The post-repair synthetic Vertex gate passed at application commit `5b5a946`. It produced one valid
semantic result from one logical provider call, with 23 measured input tokens, 271 measured
output/reasoning tokens, and 9,828 ms latency. The typed adapter did not expose transport retry or
finish-reason metadata, so accounting conservatively charges the full authorized gate envelope rather
than treating unobserved retries as zero.

Cumulative conservative accounting is therefore 6 calls, 250,023 input tokens, 40,271
output/reasoning tokens, and US$0.983298. Remaining proposer authorization is 244 calls, 12,249,977
input tokens, 1,959,729 output/reasoning tokens, and US$49.016702. Environment values were
process-scoped and cleared. No private data, holdout data, RunPod resource, or private-pilot activity
was used by the gate.

The synthetic production-route gate is accepted. The bounded four-hour private development pilot may
proceed under the existing disclosure authorization, RunPod availability waiting rules, US$12.05
compute/storage ceiling, retry policy, continuation criteria, and absolute holdout exclusion.
