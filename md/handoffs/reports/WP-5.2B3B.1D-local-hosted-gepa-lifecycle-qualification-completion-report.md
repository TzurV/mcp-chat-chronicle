# WP-5.2B3B.1D local hosted GEPA lifecycle qualification completion report

## Outcome

**Bounded offline rework complete; ready for manager validation.**

The generic provider-error boundary is repaired and both authorized Vertex routes qualified.
The earlier hosted synthetic lifecycle produced one distinct GEPA prompt package, completed 8/8
terminal explicit task evaluations, verified from a fresh process, and replayed byte-stably with
zero additional calls. The manager-directed offline rework now also proves a distinct synthetic
candidate through Chronicle's tracked `run_optimization` lifecycle and production DSPy GEPA
adapter, including normal budget, trial, candidate, result, lineage, authorization, privacy, and
fresh-process zero-call verification boundaries.

The bounded private smoke remains incomplete. Its retained log proves that GEPA selected `task_0`
while the sampled tasks were 1, 3, and 2, leaving no matching trace from which to build reflection.
It made no proposer call and produced no proposal or candidate. This was a deterministic
component/minibatch mismatch, not a semantic finding about the selected examples.

No output was repaired or reinterpreted. The private attempt and all prior accounting remain
append-only and were not retried. The work proves the local hosted routes and complete synthetic
persistence/replay lifecycle through both the earlier hosted probe and the supported tracked path,
but it does **not** prove the required private proposal, evaluation, persistence, verification, and
replay lifecycle. It provides no evidence that either candidate improves P0. A fresh private run
requires separate owner authorization after manager review and commit.

## Starting state and required reading

- Branch and commit before changes: clean `main` at
  `99e8fd8eb54f5302404f3e036015066e079b01b2`.
- Every document listed under Required Reading in the handoff was read in full before code
  changes or private development access.
- Poetry environment: this repository's `.venv`.
- DSPy / GEPA / LiteLLM: 3.3.0 / 0.1.1 / 1.83.0.
- Optimizer compatibility and safe state-only Chronicle serialization checks passed.
- A new task-specific ignored run root was used; `git ls-files .chronicle` remained empty.

## Generic provider and serialization repair

The repair has four parts:

1. a DSPy callback side channel records only sanitized failure categories before a later GEPA
   serialization failure can obscure the provider exception;
2. `OptimizerOperationError` is pickle-safe and carries the primary category plus trustworthy
   measured usage when available;
3. missing or incomplete usage marks the budget reservation interrupted without raising a new
   reconciliation exception, so the primary error escapes unchanged while the conservative
   reservation remains charged; and
4. GEPA uses its pinned cloudpickle working-state serializer for DSPy's dynamic signature
   classes. Chronicle candidate and result authority remains state-only JSON and is never loaded
   from that internal checkpoint.

Offline regressions distinguish model-not-found, authentication, permission, quota, rate limit,
timeout, invalid request, invalid JSON, generic provider, and local serialization failures. They
also reproduce a primary model-not-found followed by a secondary `PicklingError`, verify that the
primary category survives, prove exception pickle round-trip, verify successful cloudpickle
configuration, retain measured usage when trustworthy, and preserve append-only attempts and
current pointers.

## Manager-directed offline lifecycle rework

Chronicle now uses a generic deterministic trace-aligned component selector. It begins at GEPA's
per-candidate round-robin cursor, walks components in fixed order, selects the first component with
an eligible captured trace in the current minibatch, and advances the cursor past that component.
It raises an explicit failure if no eligible component trace exists. Selection depends only on
trace/component identity, never input, output, reference, diagnostic, or prompt content.

The exact observed mismatch is covered by a regression: legacy round-robin chooses `task_0` for a
minibatch containing tasks 1, 3, and 2, while the corrected selector chooses represented `task_1`.
The tracked integration regression proves that the proposer is invoked and one distinct candidate
is produced after alignment.

Structured-output policy is explicit: `add_format_failure_as_feedback=False`. Pinned DSPy would
otherwise include the raw malformed completion in the reflection record. Chronicle instead keeps
schema/JSON failures as terminal, scored deterministic diagnostics; it does not repair, semantically
retry, manually reinterpret, or disclose the malformed value through reflection. A regression proves
that failed-prediction traces are ineligible and remain unchanged.

Bounded supported runs can set paired frozen-order train/validation conversation limits and a maximum
candidate-proposal count in tracked configuration authority. GEPA logical calls are counted at the
DSPy callback boundary, including deep-copied candidate LMs. Conservative reservation covers a full
possible end-of-iteration overshoot beyond the nominal metric-call stop.

The network-free proof entered through tracked `run_optimization`, delegated GEPA to the production
DSPy adapter, and stopped after exactly one proposal position. It produced one distinct candidate and
persisted normal Chronicle candidate, result, usage, lineage, authorization, privacy, trial, budget,
and current-pointer artifacts. Accounting was 22 DSPy task calls, one proposer call, 240 terminal
synthetic candidate-evaluation positions across baseline/Bootstrap/GEPA, and a total ledger of 263
task invocations plus one proposer call. Retries, tokens, cost, cache/provider activity, and failures
were all zero. Fresh-process CLI verification returned `provider_calls: 0`; replay did not change any
adapter history. This proof used synthetic data and dummy/injected offline adapters only.

## Hosted route qualification

Both routes used the application-owned LiteLLM adapter, user ADC, `global`, temperature zero,
concurrency one, no semantic retry, no output repair, and disabled cache.

| Role | Configured / actual model | Provider | Finish | Schema | Calls / retries | Input / output tokens | Latency | Measured cost |
|---|---|---|---|---|---:|---:|---:|---:|
| Proposer | `vertex_ai/gemini-3.5-flash` / `gemini-3.5-flash` | `vertex_ai` | stop | valid | 1 / 0 | 77 / 11 | 7,015 ms | US$0.0002145 |
| Surrogate | `vertex_ai/gemini-3.5-flash-lite` / `gemini-3.5-flash-lite` | `vertex_ai` | stop | valid | 1 / 0 | 77 / 6 | 782 ms | US$0.0000381 |

Qualification total: 2 calls, 0 retries, 154 input tokens, 17 output/reasoning tokens,
7,797 ms, US$0.0002526 measured cost, and US$0.1612 conservative reservation. The ignored
record binds configured and actual provider/model identity, role, region, credential mode,
finish state, usage, latency, price, cache state, and its own record hash. Cache-only reading
made zero provider calls.

## Synthetic lifecycle

### Attempt 0001: local serialization interruption

Four Flash-Lite seed-validation calls completed before standard pickle rejected DSPy's dynamic
`StringSignature`. There were 0 proposer calls, 0 proposals, 0 candidates, and no private access.
Measured token usage did not escape; 200,000 input tokens, 8,192 output tokens, and US$0.08048
remain conservatively reserved. The attempt is retained separately and was not overwritten.

### Corrected attempt

- Frozen scope: one synthetic train and one synthetic validation conversation, four tasks each.
- GEPA proposal positions: 1/1; distinct candidate packages: 1/1.
- GEPA internal surrogate metric calls: 10; proposer calls: 1; explicit surrogate calls: 8;
  corrected logical calls: 19.
- Explicit evaluations: 8/8 terminal, 4/8 schema/contract-valid.
- Deterministic/FABLE-like synthetic reference agreement: sum 2.4 across 8 positions.
- Explicit responses: 8/8 provider `vertex_ai`, actual model `gemini-3.5-flash-lite`, finish `stop`.
- Partial measured usage (proposer plus explicit calls whose histories were authoritative):
  4,421 input and 2,769 output/reasoning tokens; US$0.02432.
- DSPy deep-copied the candidate LMs, so internal surrogate token usage was not recoverable from
  the original objects. The original undercounted record is preserved, and a separate
  reconciliation records the authoritative 10 GEPA metric calls and 19 corrected total calls.
- Conservative full-attempt reservation: US$2.793. This is not represented as measured spend.
- Optimizer wall time: 37,453 ms; explicit evaluation latency: 7,718 ms.
- Privacy: 0 findings; complete-request maximum: 1,238/8,192 tokens.
- Fresh-process package/hash verification passed. Cache-only replay was byte-stable and made 0
  provider calls.

GEPA rejected the proposal on its three-example internal subsample. That does not invalidate the
lifecycle proof because improvement was not required; the distinct proposal was captured and
evaluated without editing it.

## Private two-conversation smoke

Selection was metadata-only: the first entry in the frozen six-conversation optimizer-train
manifest and the first entry in the frozen four-conversation optimizer-validation manifest.
Only those two inputs and their eight successful existing FABLE references were opened. All four
accepted tasks used unchanged selectors, schemas, user prompts, P0 parents, generation settings,
and deterministic/FABLE scoring.

The smoke stopped before proposal completion:

| Denominator | Result |
|---|---:|
| Selected conversations | 2/2 |
| Bound FABLE references | 8/8 |
| Seed-validation surrogate calls | 4 |
| Reflective-minibatch surrogate calls | 3 |
| Proposer calls | 0 |
| GEPA proposal positions | 0/1 |
| Distinct candidate packages | 0/1 |
| Required explicit candidate positions | 0/8 |
| Verified/replayed private candidates | 0 |

The retained terminal category is `no-valid-reflective-examples`, but the log establishes its cause:
`task_0` was selected while sampled tasks were 1, 3, and 2, so the minibatch contained zero matching
traces. No provider, authentication, permission, quota, timeout, invalid-request, invalid-JSON, or
serialization exception occurred. Measured token and cost records did not escape the failed GEPA
call. The complete 19-call and US$2.793 reservation is retained; 7 surrogate calls are known observed,
with 0 observed proposer calls and 0 observed retries. Because no candidate exists, private candidate
privacy/context verification and zero-call candidate replay are not applicable and the Gate 4
acceptance criteria do not pass. The corrected policy was tested offline only; no private retry ran.

## Complete accounting

| Activity | Observed logical calls | Conservatively charged calls | Measured tokens (in/out) | Measured cost | Reserved cost |
|---|---:|---:|---:|---:|---:|
| Route qualification | 2 | 2 | 154 / 17 | US$0.0002526 | US$0.1612 |
| Synthetic attempt 0001 | 4 | 4 | unavailable | unavailable | US$0.08048 |
| Synthetic corrected lifecycle | 19 | 19 | 4,421 / 2,769 partial | US$0.02432 partial | US$2.793 |
| Private attempt 0001 | 7 | 19 | unavailable | unavailable | US$2.793 |
| Offline tracked synthetic rework | 0 | 0 | 0 / 0 | US$0 | US$0 |
| **Total** | **32** | **44** | **4,575 / 2,786 partial** | **US$0.0245726 partial** | **US$5.82768** |

The conservative token envelope is at most 2,228,000 input and 320,192 output/reasoning tokens.
No observed infrastructure retry occurred; one infrastructure retry remained configured as the
hard maximum. There were zero semantic retries and zero output repairs. The call ceiling retains
16 calls and the cost ceiling retains US$19.17232. Reservations and measured values are deliberately
not summed as though both were invoices.

## Protected-boundary and privacy evidence

- Fixed-judge calls: 0; the judge was neither constructed nor invoked.
- Holdout calls/files/content: 0; no holdout path was opened or scored.
- RunPod operations: 0; no inventory, SSH, API, lifecycle, or resource action occurred.
- Retained WP-5.2B3B.1C state access/modification: 0.
- Historical P0/Bootstrap execution: 0; P0 supplied prompt parentage only.
- Offline rework provider activity: 0; no hosted route, ADC, private input, or retained attempt was
  accessed. Its tracked synthetic orchestration used 263 network-free task invocations and one
  network-free proposer invocation, accounted separately from provider activity above.
- Private source, references, outputs, generated prompts, project values, ADC details, paths,
  identifiers, and private hashes remain below the ignored B3B.1D root or existing ignored
  development storage.
- Tracked evidence contains aggregate counts and public model/config identities only.
- No file was staged or committed.

## Validation

- Focused provider/optimizer tests: 170/170 passed.
- Full pytest suite: 627 collected, 626 passed, one expected skip.
- Repository-wide Ruff lint: passed. Ruff formatting passed for every intended rework file. The
  repository-wide format check continues to report eight unrelated pre-existing legacy files; none
  was modified.
- `poetry check`: passed.
- CLI help and fresh imports: passed.
- `git diff --check`: passed.
- Supported-path network-free synthetic lifecycle, normal persistence, fresh-process CLI
  verification, and zero-call replay: passed.
- Private verification/replay: not reached because no candidate exists.
- `git ls-files .chronicle`: empty; the B3B.1D root is ignored.
- Targeted pre-commit over all intended delivery files passed trailing-whitespace, EOF, large-file,
  merge-conflict, private-key, Ruff, and Ruff-format hooks.
- Final `git diff --check` passed. All delivery files remain unstaged and uncommitted.
- Tracking/privacy checks found zero staged files, zero tracked files below the ignored private
  root, and zero user-profile paths, Google API key patterns, private-key/client-secret fields, ADC
  filenames, numeric project resources, or email addresses in the delivery diff/report. The 16
  tracked JSONL files are unchanged deliberate synthetic test fixtures.

Final `git status --short`:

```text
 M bench/optimization/budget.py
 M bench/optimization/diagnostics.py
 M bench/optimization/dspy_bridge.py
 M bench/optimization/execution.py
 M bench/optimization/models.py
 M bench/optimization/production.py
 M docs/development-optimization.md
 M md/research/WP-5.2B3B.1-prompt-optimization-activity-log.md
 M src/chat_chronicle/ai.py
 M tests/test_ai_adapter.py
 M tests/test_bench_optimization.py
?? md/handoffs/reports/WP-5.2B3B.1D-local-hosted-gepa-lifecycle-qualification-completion-report.md
?? md/handoffs/reports/WP-5.2B3B.1D-validation-review.md
```

## Decision

The provider-error repair, both hosted route qualifications, component/minibatch repair, explicit
format-failure policy, and complete synthetic lifecycle through the tracked supported path are
successful. The private lifecycle objective remains incomplete because the prior attempt encountered
the now-repaired deterministic alignment defect. Do not characterize this as a GEPA quality result,
a prompt improvement, or evidence against P0. Per owner direction, a fresh private run requires a
separate explicit authorization after this repair is manager-reviewed and committed.
