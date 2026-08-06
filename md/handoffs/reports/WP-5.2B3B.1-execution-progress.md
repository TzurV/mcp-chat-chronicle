# WP-5.2B3B.1 execution progress — Vertex proposer route amendment

## Status

**Ready for Vertex proposer route PM validation.** The accepted Gate 1 implementation remains intact.
This unstaged, uncommitted amendment replaces the selected proposer route with Google Vertex AI
`vertex_ai/gemini-3.1-pro-preview`, `global`, authenticated through ADC.
Work remains stopped before private transfer, provider/model calls, credential use, paid allocation,
and holdout access.

The clean starting authority is `main` commit
`97c204ddc6d2dd48b70927888667c91562ffd936`. The manager-created commit containing this patch must
replace that value in the ignored private execution configuration before any future authorized run;
the tracked orchestrator deliberately rejects a dirty tree or a different commit.

## Gate 1 review resolution

1. **Tracked end-to-end execution:** `optimize` and `resume` now invoke the tracked orchestrator in
   `bench/optimization/execution.py`. It consumes a hashed authorization after all four CLI gates,
   runs P0, BootstrapFewShot, and bounded GEPA through injected adapters, evaluates train and
   validation on Qwen and Phi, produces deterministic diagnostics, scans candidate prompts, persists
   candidates/results/state/budgets/attempts, and resumes from durable authority. Production
   LiteLLM/DSPy adapters are tracked in `bench/optimization/production.py`.
2. **Shortlist contract:** export reads only result IDs in terminal run state, validates result and
   latest-attempt authority, ranks with `MetricVector`, applies P0 total-valid and model/task floors,
   privacy, terminal-accounting, 8K-fit, and GEPA-lineage gates, removes identical prompt sets, and
   prefers different parents. It exports immutable P0 plus three to five candidates or writes an
   explicit no-improvement artifact.
3. **Development/split authority:** preflight hash-validates the accepted ten-conversation development
   parent, independently reconstructs the deterministic ordered 6/4 split, proves common parent,
   disjoint union, exact order, quotas, and case counts, then validates exactly ten copied selected
   inputs and forty task references against their canonical hashes and identities. `zero_holdout` is
   derived only after those development-only checks pass; it is not a constant.
4. **Pre-call budgets:** a hashed persistent ledger atomically reserves candidates, task calls,
   proposer calls, retries, tokens, compute time, compute cost, and projected proposer cost before
   each adapter boundary. Reconciliation releases unused reservation, retains interrupted/missing
   usage fail-closed, rejects actual usage beyond reservation, and reloads exact counters on resume.
5. **Latest-attempt authority:** every non-empty trial requires `current.json` to name the latest
   attempt and matching record hash. Missing, dangling, stale, foreign, and hash-mismatched pointers
   fail. A resumed interrupted proposal appends a new complete attempt after its evaluated result is
   durable.
6. **Stable candidate identity:** the candidate ID hashes only prompts, bounded compiled
   demonstrations, immutable contracts, context, and lineage. Metrics, accounting, privacy, and run
   authority live in a separately hashed immutable `CandidateResult`; rescoring or privacy evidence
   changes the result ID without changing the compiled candidate ID.
7. **Config-aware verification:** optimizer verification validates accepted P0 contracts and context,
   run/config/commit, split, model artifact, proposer, optimizer, privacy-scanner, result hash,
   terminal accounting, run-state reference, and complete current trial. Syntax-only package parsing
   remains a separately named internal operation and is not reported as complete verification.
8. **Selected operational proposer:** strict configuration now supports both the selected `vertex-adc`
   mode and the backward-compatible `api-key-environment` mode. The selected profile declares only
   five environment-variable names, resolves paired project/location values transiently, requires
   both locations to be `global`, checks ADC only during authorized adapter construction, and never
   requires an API key. Model, provider, location, credential mode and variable names, generation and
   retry settings, pricing, ceilings, and cache namespace bind configuration/run/cache identity.
9. **Lifecycle tests:** the focused suite now exercises the synthetic optimize/interruption/resume
   lifecycle, real tracked production candidate adapter with an injected fake client, all CLI
   lifecycle commands, split/reference tampering, budget boundaries and interruption, stale attempts,
   stable candidate/result identity, config-aware verification, shortlist guardrails/no-improvement,
   trial/result tampering, and fresh-process ordinary/optimization-extra imports. Tests are synthetic
   and network-independent.

## Repeat review resolution

1. **BootstrapFewShot packaging and replay:** `CandidatePackage` format 3 contains a deterministic
   per-task list of hashed demonstration records. The tracked production bridge compiles each task
   separately through real DSPy BootstrapFewShot, extracts only demonstrations whose selected input
   binds to the frozen optimizer-train examples, validates each response against the accepted task
   schema/evidence/date/reference authority, and enforces at most one labeled and one bootstrapped
   example. `LiteLLMCandidateAdapter` replays the immutable records as user/assistant messages before
   the current request. Demonstrations participate in candidate identity, JSON-only serialization,
   complete-request tokens, and the unchanged privacy scan; schemas/contracts remain immutable.
2. **Pilot and continuation:** run-state format 2 persists a hashed pilot checkpoint after at most the
   configured pilot candidates/four-hour ceiling. It records the exact pilot result IDs, budget hash,
   all four continuation criteria, decision, and achievable additional operations. Failed criteria
   terminate as `pilot-no-improvement`. A passing checkpoint permits `resume` under total ceilings,
   preserving existing candidate/result/trial bytes. Before each GEPA proposal, the runner calculates
   the combined candidate, optimizer, Qwen/Phi train/validation, retry, token, time, and cost
   reservation. It stops `budget-limited` before an unaffordable complete operation; optimizer
   exhaustion or the 40-candidate maximum can stop earlier.
3. **Complete-request context fit:** the canonical request builder is shared by estimation and the
   production adapter. It covers the interpolated system prompt, every packaged demonstration, the
   selected input/user prompt, response schema, conservative wrapper allowance, and configured output
   allowance for every required development case. The maximum case/task/input/output/total envelope
   is immutable result evidence. Promotion requires the complete total to be at most 8,192 tokens.
4. **Optimizer/proposer timing:** the orchestrator measures each BootstrapFewShot and GEPA adapter
   attempt with a monotonic clock. Complete durations are present in both proposal trials and candidate
   results; interrupted durations remain in append-only attempt history. Inspection aggregates all
   optimizer attempts and separates their wall time from candidate-batch wall time. DSPy history is
   still used for calls/tokens only and no per-provider latency is invented.

## Repeat-review synthetic evidence

- **Real BootstrapFewShot bridge:** four real DSPy 3.3.0 BootstrapFewShot compiles ran with `DummyLM`
  candidate teachers and no network. Each task produced one authority-bound labeled demonstration;
  the packaged candidate differed from P0, survived JSON round-trip, rejected a duplicated labeled
  example, and failed the privacy scan when scanned against its demonstration source. The real
  `LiteLLMCandidateAdapter` then issued 16 injected validation requests whose role sequence was
  system, demonstration user, demonstration assistant, current user.
- **Pilot stop:** a two-GEPA synthetic pilot with candidates worse than P0 persisted all criterion
  booleans and terminated `pilot-no-improvement`; resume was a no-op and made no additional attempt.
- **Permitted continuation:** a two-candidate pilot passed all four criteria. Resume retained the
  checkpoint hash and every pre-existing `current.json` byte, added candidates three and four, and
  stopped at the configured four-candidate test maximum.
- **Budget-limited continuation:** with a 500-task test ceiling, the checkpoint calculated exactly two
  achievable additional complete operations. Resume reached 481 task invocations after four GEPA
  candidates, then stopped before the next 80-task operation. The general capacity test proves the
  minimum of candidate, 3,000-task, 250-call, 12.5M/2M-token, 12-hour, and cost limits controls the
  count; a one-hour synthetic operation has capacity 12 under the total defaults.
- **Complete context boundary:** binary boundary construction produced persisted conservative totals
  of exactly 8,192 tokens (eligible for the context guard) and 8,193 tokens (ineligible). The latter
  included a nonzero output allowance, terminated the pilot safely, and was rejected by shortlist
  eligibility using its real result envelope.
- **Timing and resume:** the interruption lifecycle retained two attempts for GEPA proposal 2 and one
  exhaustion attempt. Inspection reported six optimizer attempts / 42 ms total monotonic optimizer
  wall time and 200 ms of separately reported candidate-batch time. Candidate results retained 28 ms
  across the four successful Bootstrap/GEPA proposals; no provider latency was synthesized.

## Final narrow correction — Repeat Review Finding 5

The pilot continuation predicate now evaluates one candidate component by component. A result counts
as no worse than P0 only when its validation `total_valid`, `worst_model_valid`, and
`minimum_task_valid` are each greater than or equal to the corresponding P0 component. No tuple or
lexicographic comparison remains, and all three conditions must hold for the same candidate.

Two end-to-end synthetic pilot regressions exercise the exact false-positive shapes:

- total validity improved from 28 to 29 while worst-model validity fell from 14 to 13; the checkpoint
  set `validation_no_worse_than_p0=false`, chose `stop`, and returned `pilot-no-improvement`;
- total validity improved from 28 to 29 while minimum-task validity fell from 6 to 5; the checkpoint
  made the same reject/stop decision.

The existing positive continuation test remains unchanged and passes when a single candidate is no
worse on all three components.

## Vertex proposer route amendment

- **Strict credential contract:** the selected profile is Google Vertex AI
  `vertex_ai/gemini-3.1-pro-preview`, `vertex-adc`, `global`. Tracked YAML contains the names
  `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `VERTEXAI_PROJECT`, `VERTEXAI_LOCATION`, and
  `GOOGLE_GENAI_USE_VERTEXAI`, but no project value, API key, token, credential file, or private path.
  Literal project-like strings and extra credential fields fail strict validation. Missing runtime
  project/location variables, disagreement, non-global location, a false enable flag, or unavailable
  ADC fail with value-free errors.
- **Injected-client proof:** a network-free fake received the exact LiteLLM model, transient synthetic
  project, `global` location, ADC mode, temperature zero, reasoning `none`, 120-second timeout, one
  infrastructure retry, cache disabled, concurrency one, 8,000-token per-call allowance, pricing,
  and total ceilings. It received no API-key argument. Anthropic API-key-environment compatibility is
  retained in a separate injected-only regression.
- **Identity:** configuration, authorization/result proposer authority, and cache identities bind the
  full non-secret profile. Changing a valid declared location-variable name changes all three. Runtime
  environment values and ADC material are excluded.
- **Budget:** 12.5 million input tokens at US$2/million plus 2 million output tokens at
  US$12/million is exactly US$49 under the US$50 hard cap. Separately reported reasoning tokens are
  conservatively added to output usage. A full-envelope reservation is accepted, and the next
  call/token/cost operation is rejected before invocation; interrupted reservations retain the
  already accepted fail-closed behavior.
- **Methodological limitation:** the optimizer proposer and later fixed judge are both Gemini 3.1
  Pro. The fixed judge remains outside the loop, and neither its score nor rationale is exposed to
  BootstrapFewShot or GEPA. This same-family evaluation-bias risk must appear in the completion report
  and any article; deterministic schema, evidence, reliability, runtime, and cost results remain
  separately valid measurements.

## Synthetic end-to-end lifecycle evidence

The synthetic run uses ten generated conversations and forty generated references. It contains no
private source data and injects fake candidate/proposer adapters, so no network or credential path is
used.

- First `optimize`: evaluated P0, BootstrapFewShot, and GEPA candidate 1; GEPA proposal 2 then raised a
  deliberate interruption after a pre-call reservation. Durable run state retained one GEPA result,
  the interrupted reservation, and attempt 1 of `proposal-gepa-0002`.
- First `resume`: loaded the hashed state and cumulative ledger, appended successful attempt 2 for
  `proposal-gepa-0002`, completed the three-result pilot, evaluated the four continuation criteria,
  and persisted a `pilot-complete` checkpoint. Second `resume` entered the permitted total-budget
  phase and stopped on the injected optimizer-exhaustion response without rewriting completed work.
- Durable results: one P0, one BootstrapFewShot research result, and three GEPA results. Five complete
  candidates were evaluated over train/validation and Qwen/Phi: 20 adapter batches and 400 terminal
  synthetic task cases.
- Budget evidence: five proposer calls are retained—three successful GEPA calls, the deliberately
  interrupted reservation, and the terminal search-exhaustion call. The candidate adapter reported
  exact terminal case usage; combined next-operation projection and reservations preceded calls.
- Verification: each run-referenced candidate/result/trial chain passed config-aware verification.
  A self-consistent contract substitution, a rehashed foreign config authority, and a tampered trial
  pointer were rejected.
- Shortlist: deterministic export produced immutable P0 plus three eligible GEPA candidates. A
  separate two-candidate fixture produced `no-improvement`, not a short successful list. Each
  individual guardrail was tested fail-closed.
- Production-adapter proof: the actual tracked `LiteLLMCandidateAdapter` completed a 16-case synthetic
  Qwen validation batch through an injected async client, accounted 16 calls/192 input/80 output
  tokens, forced per-request retry count zero, and rejected a returned provider mismatch. No socket or
  model was used.

## Aggregate-only private preflight evidence

The strengthened no-call preflight passed against the ignored copied development authority before
this checkpoint:

- accepted development parent: 10 conversations / 40 cases;
- selected authority: exactly 10 input envelopes / 40 task references;
- train: 6 conversations / 24 cases; provider quotas 2 ChatGPT, 2 OpenAI Codex, 1 Claude, 1 Claude
  Code; length quotas 2 short, 2 medium, 2 long;
- validation: 4 conversations / 16 cases; one per provider; length quotas 2 short, 1 medium, 1 long;
- exact disjoint ordered union and deterministic reconstruction: passed;
- copied Qwen/Phi artifacts, accepted task catalog, manifest and canonical input/reference bindings:
  passed;
- DSPy 3.3.0 / GEPA 0.1.1 compatibility and expected result surface: passed;
- derived development-only / zero-holdout assertion: passed.

This operation was local and read-only. It did not open the twenty-conversation holdout, create a
transfer, read a credential, invoke a provider/model, or allocate paid compute.

## Frozen controls and manager recommendation

- Mutable surface: only the four accepted system prompts.
- Context: 8,192; configured prompt ceiling below that boundary.
- Candidate runtime: exact accepted Qwen/Phi artifacts, concurrency one, at most one infrastructure
  retry, zero semantic retries, and no output repair.
- Pilot: at most 12 GEPA candidates and four compute hours; full ceilings remain 40 candidates, 3,000
  task invocations, and 12 compute hours.
- Selected proposer: Google Vertex AI `vertex_ai/gemini-3.1-pro-preview`, `global`, ADC-only, at most
  250 calls, 12.5 million input tokens, 2 million output tokens including reasoning, US$49 calculated
  maximum, and a US$50 hard proposer cap. This selection is not pilot authorization.
- Paid compute: retain no more than the separately confirmed RunPod cap; owner must confirm console
  GPU/storage rates before allocation. No allocation was made here.

## Required disclosure wording for later owner approval

> I authorize the bounded WP-5.2B3B.1 pilot to process only the frozen six-train
> and four-validation development conversations. The owner-controlled RunPod Pod
> may receive their selected source chat text, corresponding FABLE reference
> fields, accepted schemas/contracts, current prompt candidates, Qwen/Phi
> candidate outputs, and structured deterministic diagnostics. Google Vertex AI
> `vertex_ai/gemini-3.1-pro-preview` through the global route and ADC may receive only the
> selected development source text, current prompts, candidate outputs, relevant
> FABLE reference fields, schemas/contracts, and bounded diagnostics required by
> BootstrapFewShot or GEPA. No holdout content or identity, unrelated history,
> live database, fixed-judge rationale or credential, raw provider error,
> environment value, or historical package outside the accepted controls is
> authorized. Limits are 250 proposer calls, US$50 proposer cost, four hours for
> the initial RunPod pilot, and no more than the separately confirmed RunPod
> compute cap. One infrastructure retry is allowed; semantic retries and output
> repair are not.

This wording is recorded for a later explicit owner decision. It grants no authority at this
checkpoint.

## Validation at repeat checkpoint

- `poetry run pytest tests/test_bench_optimization.py -q`: **68 passed**.
- `poetry run pytest`: **542 passed, 1 skipped** in 203.86 seconds. An earlier invocation reached its
  runner timeout without a reported failure; the complete rerun used a sufficient timeout and passed.
- `poetry run pytest tests/test_bench_optimization.py -q -k "cli or lifecycle or
  ordinary_and_optimization_extra_imports"`: **4 passed**.
- `poetry run ruff format --check bench/optimization tests/test_bench_optimization.py`,
  `poetry run ruff check .`, `poetry check`, and `git diff --check`: passed.
- Synthetic CLI coverage exercised `preflight`, `dry-run`, `optimize`, `resume`, `inspect`, `verify`,
  `package`, and `export-shortlist`; both provider-facing commands also reject every missing-gate
  invocation.
- Credential-signature scanning of non-report tracked code/config found no private-key block, Google
  API-key shape, client secret, refresh/access token, or ADC credential path. The diff contains only
  the approved environment-variable names and explicit synthetic markers. No files are staged and no
  untracked run artifact exists.
- No test used private content, network access, provider/model inference, ADC or another credential,
  paid compute, or holdout data.

## Intended unstaged files for this amendment

- `bench/optimization.default.yaml`
- `bench/optimization/dspy_bridge.py`
- `bench/optimization/execution.py`
- `bench/optimization/models.py`
- `bench/optimization/operations.py`
- `bench/optimization/production.py`
- `tests/test_bench_optimization.py`
- `docs/development-optimization.md`
- `md/development-ledger.md`
- `md/handoffs/reports/WP-5.2B3B.1-execution-progress.md`
- `md/handoffs/reports/WP-5.2B3B.1-gate1-validation-review.md`

All remain unstaged and uncommitted for repeat manager validation.
