# WP-5.2B3B.1D.2 Offline GEPA Rejection Analysis

## Executive summary

The single real GEPA mutation was rejected because it did not improve the
three-example reflection minibatch. The persisted trace records selected
examples `[0, 2, 1]`, P0 scores `[0.0, 0.0, 0.0]`, and proposed-program scores
`[0.0, 0.0, 0.0]`. Pinned GEPA 0.1.1 accepts a reflective mutation only when
`new_sum > old_sum`. Both sums were zero, so the strict `0.0 == 0.0` tie was
correctly rejected and GEPA returned its only accepted program, P0.

This is principally expected GEPA behavior on a flat, all-invalid metric
plateau. It is also evidence of an insufficient one-proposal search budget and
a weak, noisy optimization signal. It is not evidence that the proposed text
was semantically worse, that P0 improved, or that Gemini 2.5 Flash-Lite or
Gemini 3.5 Flash is unsuitable.

The rejected instruction was not retained. The selected component is known,
but its proposed text, hash, byte length, and delta from P0 are unavailable and
are not reconstructed or inferred. This is an evidence-retention gap. Exact
per-example feedback text and the four-invocation difference between provider
accounting and persisted scored positions are also not retained at sufficient
resolution. Those gaps must be repaired and validated offline before another
private experiment.

A bounded follow-up is justified after that offline instrumentation work: use
the same candidate and proposer, run three to five failure-focused proposals
with four as the planned target, and use the complete frozen six-conversation
train/four-conversation validation development split. Do not use the fixed
judge until a distinct candidate passes deterministic, context, privacy,
accounting, and full-development promotion gates.

## Evidence inventory and boundaries

The analysis started from clean `main` at accepted commit `3f21363`. The exact
authoritative fresh-run root was resolved from the accepted completion report
and its ignored configuration. No other private run root was accessed.

The private pre-analysis inventory contained 49 files:

| Evidence class | Files |
|---|---:|
| Copied authority | 14 |
| Run configuration | 1 |
| Lifecycle evidence | 8 |
| Ignored operator support | 5 |
| Persisted run state, packages, results, trials, and DSPy/GEPA state | 21 |
| **Total** | **49** |

The inventory records relative names, sizes, and SHA-256 values only in ignored
local storage. A post-analysis inventory found the same 49 files and was
byte-identical to the pre-analysis inventory. The retained run therefore
remained unchanged.

The following boundaries held throughout:

- Provider, candidate-model, proposer, and fixed-judge calls: 0.
- Network calls: 0.
- ADC initialization, probing, or refresh: 0.
- Holdout access, enumeration, or scoring: 0.
- RunPod and LM Studio activity: 0.
- P0, GEPA, evaluation, scoring, verification, or replay reruns: 0.
- Model-output repair, regeneration, or manual reinterpretation: 0.
- Historical private-run access: 0.
- Production-code changes: 0.

Only aggregate and structural evidence appears here. Private prompts,
conversations, references, outputs, identifiers, paths, hashes, credentials,
project values, and provenance remain under ignored local storage.

## Reconstructed lifecycle

### 1. Explicit P0 evaluation

Chronicle evaluated the unchanged P0 package over the authorized two-case
development subset: one frozen train conversation and one frozen validation
conversation, with four tasks per conversation.

- All 8 positions were terminal.
- 4/8 were schema/deterministic-contract valid and usable.
- Four positions were recorded as schema failures.
- Train validity was 2/4; validation validity was 2/4.
- Train FABLE agreement was 0.2750; validation agreement was 0.1125; overall
  agreement was 0.19375.

These are the authoritative explicit P0 metrics. They must not be substituted
for GEPA's later fresh internal rollouts.

### 2. Feedback preparation

Chronicle prepared an aggregate persisted-result diagnostic from P0 failure
counts. The GEPA adapter does not consume that argument: its `gepa` method
explicitly deletes the supplied aggregate feedback and instead obtains fresh
per-example feedback from its internal metric rollouts.

For every internal rollout, Chronicle's metric:

1. parses and validates the response against the task schema;
2. checks evidence membership and the conversation-summary date contract;
3. computes FABLE field agreement only for a valid response; and
4. returns the score
   `(0.999 if valid else 0.0) + semantic_agreement / 1_000_000` together with
   bounded deterministic feedback.

The feedback renderer emits a category and schema path for a violation, or a
short valid-result marker. It never embeds raw private output. DSPy prediction
format failures are deliberately excluded from reflection traces because
`add_format_failure_as_feedback` is false.

### 3. GEPA seed evaluation and component selection

GEPA freshly evaluated P0 on the four-example internal validation set and
recorded a full-validation score of zero over four examples. This differs from
the explicit P0 validation result of 2/4 valid and is direct evidence that a
temperature-zero hosted rollout is not a reproducible cached observation.

The train and validation scopes were each limited to the first conversation.
Within a conversation, examples follow the fixed task order:

| Internal index | Task |
|---:|---|
| 0 | Conversation summary |
| 1 | Work-mode classification |
| 2 | Last activity |
| 3 | Title assessment |

The reflection minibatch selected `[0, 2, 1]`: conversation summary, last
activity, and work-mode classification from the single train conversation,
all using Gemini 2.5 Flash-Lite. Title assessment was not sampled.

The trace-aligned selector starts at the first component and selects the first
sampled component with an eligible trace. The selected component was `task_0`,
conversation summary. Because each sampled example executes only its own
task-specific predictor, the proposer had one sampled conversation-summary
trajectory relevant to the selected component, not three same-component
examples.

### 4. Proposer boundary

Gemini 3.5 Flash completed one proposer call. GEPA constructed a candidate by
copying the current program and replacing only the selected instruction.
Demonstrations were unchanged and remained empty. The other three task
components were copied unchanged.

The proposer therefore crossed the intended real hosted boundary and produced
a real mutation. The missing payload evidence discussed below prevents an
exact content-level characterization of that mutation.

### 5. Internal comparison and rejection

GEPA evaluated P0 and the proposed program on the same three-example
minibatch:

| Example | Task | P0 score | Proposed score | P0 contract-valid | Proposed contract-valid | P0 FABLE | Proposed FABLE |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | Conversation summary | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 |
| 2 | Last activity | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 |
| 1 | Work-mode classification | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 |
| **Sum** |  | **0.0** | **0.0** | **0/3** | **0/3** | **0.0** | **0.0** |

A zero score proves that the composite schema/deterministic contract was not
valid, because every valid response scores at least 0.999. It does not identify
whether the underlying violation category was schema, evidence, or date. Those
per-example categories were not retained. FABLE agreement is zeroed when the
contract is invalid, so this comparison contains no usable semantic ranking
between the two programs.

GEPA's pinned engine computes the two sums and rejects when
`new_sum <= old_sum`. The proposal therefore failed the exact acceptance rule:

```text
required: new_sum > old_sum
observed: 0.0 > 0.0 is false
decision: reject
```

Because the proposal was rejected before full-validation admission, GEPA did
not add it to the accepted candidate pool. Its best accepted program remained
candidate zero, P0, and that unchanged program was returned to Chronicle.

### 6. Unchanged return

The retained run predates the accepted unchanged-prompt detection repair.
Chronicle assigned a different lineage-derived candidate identity to the
returned program and evaluated it a second time even though all four prompt
payload hashes equalled P0. That arm was an unchanged-P0 repeat, not a tuned
candidate. Commit `3f21363` now stops this condition as
`no-distinct-prompt-package`; the retained private run was not rewritten.

## P0 versus proposed-prompt internal metrics

The internal result is a reliability tie, not a semantic quality comparison:

- Composite schema/deterministic validity: 0/3 for P0 and 0/3 for the proposal.
- Per-sampled-task validity: 0/1 for conversation summary, last activity, and
  work mode in both arms.
- Title-assessment evidence: unavailable because it was not sampled.
- FABLE agreement: 0.0 in every sampled position because invalid outcomes are
  assigned zero semantic agreement.
- Context: no context-guard exception or optimizer failure occurred. The exact
  proposed-request token counts were not retained, but context did not cause
  the rejection.
- Privacy: P0 and the unchanged returned package passed Chronicle's privacy
  gate. The rejected proposal never reached package-level privacy scanning, so
  its privacy status is unavailable and was not a rejection input.
- Provider/reliability: the internal provider boundary completed without a
  recorded infrastructure retry or provider failure. Rejection was local and
  metric-driven.
- Failure categories: exact internal categories are unavailable. The explicit
  P0 run's four schema failures cannot be projected onto later stochastic
  internal outputs.

The conversation-summary mutation could only directly affect example 0.
Examples 2 and 1 used unchanged prompt components; their repeated zero scores
do not add evidence about the mutation itself. The proposal's only directly
relevant sampled comparison was therefore one all-zero
conversation-summary pair.

## Rejection root cause

The immediate cause was the strict GEPA acceptance rule applied to a zero-score
tie. The underlying experimental causes are broader:

| Classification | Assessment |
|---|---|
| Expected GEPA behavior | **Yes.** Strict rejection of a non-improving minibatch is correct. |
| Insufficient search budget | **Yes.** One proposal is not enough to assess search effectiveness. |
| Weak/noisy signal | **Yes.** All sampled outcomes collapsed to zero, and only one example exercised the mutated component. |
| Configuration mismatch | **Material limitation.** The run used 1/1 conversations despite a frozen 6/4 development split. |
| Scoring problem | **Plateau, not arithmetic error.** Reliability-first scoring intentionally gives all invalid outputs zero, but cannot rank partial progress. |
| Context or privacy rejection | **No.** Neither was part of the GEPA rejection decision. |
| Orchestration defect | **No defect in the tie decision.** The former unchanged-return handling defect is already repaired. |
| Evidence/diagnostic defect | **Yes.** Rejected proposal content and exact feedback were not durably retained. |

The proposal was not shown to be semantically bad. It was shown only to have
failed to turn the selected rollout into a fully valid response on its single
directly relevant example.

## Feedback-path assessment

Deterministic validation reached GEPA through the fresh internal metric, and a
reflection dataset was successfully built because the proposer was called.
The selected conversation-summary trace therefore carried bounded metric
feedback into the proposer boundary.

The signal was nevertheless sparse:

- The external aggregate P0 feedback was prepared and then discarded by the
  production GEPA adapter.
- Only one sampled trajectory corresponded to the selected task component.
- Invalid results received a zero score and zero semantic agreement.
- FABLE affects the numeric score only after full validity; it is not rendered
  as detailed textual feedback for a valid or invalid output.
- The retained trace does not preserve the exact per-example feedback category
  or text supplied to the proposer.
- DSPy `FailedPrediction` traces are excluded by policy, so native format
  failures cannot become reflective examples. This protects raw malformed
  output but can remove precisely the examples most relevant to a
  format-reliability objective.

The fixed Gemini judge was neither constructed nor invoked. It supplied no
optimization feedback and made zero calls.

For a failure-focused follow-up, retain the reliability-first promotion metric
but improve the private diagnostic signal: persist bounded failure categories,
selected component, example identities local to the run, parent/proposal
scores, and a private pre-decision proposal envelope. Do not disclose raw
malformed output or add output repair.

## Rejected-proposal evidence-retention gap

The retained human-readable GEPA artifacts contain the accepted seed program
and the score trace, but not the rejected candidate. The GEPA engine logs the
new instruction during execution, then applies the strict subsample decision;
only accepted candidates are added to durable state. The retained root has no
separate private proposal event.

Accordingly:

| Required private field | Status |
|---|---|
| Selected component | Available: `task_0`, conversation summary |
| Rejected proposal text | Unavailable; not reconstructed or inferred |
| Proposed component SHA-256 | Unavailable; not reconstructed or inferred |
| Proposed component byte length | Unavailable; not reconstructed or inferred |
| Proposed-minus-P0 length delta | Unavailable; not reconstructed or inferred |
| P0-side prompt metadata | Present privately, but insufficient without the proposal side and intentionally omitted here |
| Other task-component changes | None by the single-component mutation path |
| Demonstration changes | None |
| Returned-program prompt changes | None; all four returned prompts equal P0 |

Future GEPA runs should append a private event **before** the acceptance
decision. It should contain the proposal text in ignored storage, parent and
proposal component hashes, byte lengths, selected component, proposal ordinal,
minibatch-local identities, old/new score vectors, privacy-scan status, and an
event hash. A tracked report should expose only privacy-safe aggregates. This
must be implemented and tested with synthetic data before private calls.

## Implementation assessment

No production code was changed in this work package. Two offline findings need
manager review before another private run:

1. **Rejected-proposal persistence is missing.** The current retained state is
   sufficient to explain the decision but insufficient to audit the exact
   mutation. This is an evidence-contract defect, not a reason to reinterpret
   private output.
2. **Four internal candidate invocations are not attributable from retained
   score evidence.** Provider accounting records 14 internal candidate calls,
   while the durable score topology exposes 10 scored positions: four seed
   validation, three P0 subsample, and three proposal subsample positions.
   Pinned DSPy defaults permit a `ChatAdapter` parse failure to make a second
   call through `JSONAdapter`. That behavior is consistent with the four-call
   difference, but the required LM history was not persisted, so attribution
   is not proven. These calls must not be relabelled as infrastructure retries.
   Before a follow-up, either disable this fallback or persist and budget every
   adapter fallback explicitly as a format retry under the no-repair policy.

The feedback interface also has an avoidable gap: Chronicle computes aggregate
P0 diagnostics, but the production GEPA adapter deletes them. Manager review
should decide whether to incorporate that bounded signal into private
reflection or remove the misleading unused interface. None of these findings
changes the correctness of the observed zero-to-zero rejection.

## Experiment limitations

- The explicit lifecycle covered only two conversations and eight task
  positions. It proved mechanics, not prompt quality.
- Although the frozen development authority contains a 6/4 train/validation
  split, GEPA used only the first conversation from each side.
- The reflection minibatch had three different task components; the selected
  component had only one relevant trajectory.
- Only one proposal was allowed. A single mutation cannot estimate GEPA's
  success rate or distinguish proposer quality from an unlucky mutation.
- Explicit P0 was valid on only 4/8 positions. This creates many zero-score
  plateaus and little semantic signal.
- Fresh internal P0 validation scored 0/4 while explicit P0 validation scored
  2/4. Hosted temperature-zero behavior was therefore operationally
  stochastic at this sample size.
- The proposed instruction was not retained, so no content-level causal
  analysis is possible.
- The exact internal failure categories, proposed-prompt privacy result,
  candidate-model internal tokens/cost, and four extra-call attribution are
  unavailable.

One proposal is not sufficient to assess GEPA. The result supports a bounded
next experiment, not a broad optimization search or a P0-improvement claim.

## Recommended next experiment

Run nothing until a separate handoff authorizes private activity and the
pre-decision persistence/accounting instrumentation passes synthetic review.
Then use this design:

1. Retain Gemini 2.5 Flash-Lite as the sole 8K candidate. Changing it would
   confound the prompt-search question, and one all-zero proposal does not
   disqualify the route.
2. Retain Gemini 3.5 Flash as proposer. It completed the real proposal boundary
   and produced a mutation; the rejection occurred after proposal generation.
3. Generate a fresh explicit P0 baseline across all ten frozen development
   conversations: six train and four validation, four tasks each.
4. Authorize three proposals initially, target four so each task component can
   receive a deterministic proposal opportunity, and permit a fifth only when
   the first four yield a useful but inconclusive validity signal. Five is a
   hard stop.
5. Make proposal selection failure-focused. Prioritize components with P0
   schema/deterministic failures and require multiple eligible same-component
   traces where the frozen train data permits it. Do not manually select or
   alter model outputs.
6. Persist every proposal privately before scoring or acceptance, including
   explicit adapter-fallback accounting and bounded feedback provenance.
7. Retain GEPA's strict `new_sum > old_sum` rule. Do not accept ties.
8. Require a distinct prompt payload before Chronicle package persistence.
9. Evaluate only the selected distinct finalist across all ten development
   conversations. Release the finalist reservation if no distinct proposal is
   accepted.
10. Promote only if the finalist passes schema, evidence, date, terminal,
    context, privacy, lineage, accounting, and byte-verification gates; does not
    regress total validity, minimum task validity, or frozen validation
    validity; and improves at least one declared primary metric. An equality is
    not improvement.
11. Use the fixed judge only after a distinct candidate passes those gates,
    under separate authorization. Do not judge rejected or unchanged programs.
12. Keep the holdout untouched. The ten-conversation development set is
    adequate for bounded candidate selection, but not for a final
    generalization or P0-superiority claim.

The preferred plan is four proposals. Three is the minimum useful search; five
is an authorized-style ceiling, not a target to consume automatically.

## Estimated calls and budget

The estimate applies Chronicle's current conservative reservation formulas to
the complete 6/4 development split, one infrastructure retry allowance per
candidate request, and one proposer retry allowance per proposal.

- Explicit P0: 40 primary candidate positions, 80 reserved attempts.
- GEPA seed validation: 16 primary positions, 32 reserved attempts.
- Each proposal: three parent plus three proposal minibatch positions and up to
  sixteen full-validation positions; 38 reserved candidate attempts.
- Explicit finalist: 40 primary positions, 80 reserved attempts.
- Proposer: one primary call and one retry allowance per proposal.

| Proposal ceiling | Candidate primary-call upper bound | Proposer primary calls | Conservative candidate attempts | Proposer retry capacity | Total conservative new-call charge | Projected cumulative charge from 109 | Retry-priced cost stress |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 162 | 3 | 306 | 3 | 312 | 421 | US$1.47 |
| **4** | **184** | **4** | **344** | **4** | **352** | **461** | **US$1.90** |
| 5 | 206 | 5 | 382 | 5 | 392 | 501 | US$2.33 |

The primary-call upper bound assumes every proposal reaches full validation and
a finalist is evaluated. Rejected proposals and an absent finalist reduce
actual calls. The cost stress uses the same D.1 candidate per-attempt bound and
prices both primary and retry-capable proposer calls at the configured maximum;
it is intentionally more conservative than Chronicle's current proposer-token
reservation.

For a maximum-five-proposal handoff, authorize no more than 400 additional
charged calls and US$3 of incremental conservative provider cost. If historical
cumulative accounting continues from 109 calls, set the cumulative call
ceiling to at least 510. The existing US$35 cumulative cost ceiling is already
ample: adding the US$2.33 stress estimate to the retained US$6.0814776
reservation remains below US$8.42. Recalculate these values if models, prices,
retry policy, minibatch size, evaluation scope, or reservation code changes.

## Article-ready observations

- A successful optimization lifecycle is not the same as an improved prompt:
  GEPA can call a proposer, evaluate a real mutation, reject it correctly, and
  return the seed program.
- Reliability-first metrics create an intentional cliff. When every malformed
  or contract-invalid response scores zero, a mutation must cross the complete
  validity boundary before the optimizer can observe progress.
- Multi-task reflection can look like a three-example experiment while giving
  the selected prompt only one directly relevant example.
- Temperature zero does not make a hosted model a deterministic measurement;
  the same P0 prompt produced materially different validity in explicit and
  internal validation rollouts.
- Rejected proposals are evidence. Persisting them privately before the
  acceptance decision is necessary for reproducible optimization audits.
- Fixed semantic judging belongs after deterministic qualification and
  distinct-candidate selection, not inside a format-reliability search loop.

These observations describe a bounded diagnostic result. They do not establish
that GEPA improves P0 or that any candidate should be promoted.

## Provider, usage, latency, cache, and failure evidence

The retained D.1 lifecycle evidence remains authoritative:

- Candidate route: Gemini 2.5 Flash-Lite through Vertex AI in `global`.
- Proposer route: Gemini 3.5 Flash through Vertex AI in `global`.
- Fresh run: 30 candidate calls and one proposer call; zero recorded
  infrastructure retries, provider failures, or cache hits.
- Explicit P0: 12,113 input tokens, 968 output tokens, zero reasoning tokens,
  13,953 ms candidate latency, and US$0.0015985 measured cost.
- Proposer: 1,314 input tokens, 2,889 output-plus-reasoning tokens, and
  US$0.037296 measured cost.
- Internal candidate calls: 14; portable candidate tokens, cost, and individual
  latency were not retained.
- End-to-end lifecycle wall time: 46,188 ms; optimizer wall time: 24,250 ms.
- Cumulative through D.1: 72 observed calls, 109 conservatively charged calls,
  US$0.06636632 partial measured cost, and US$6.0814776 conservative
  reservation.

WP-5.2B3B.1D.2 added exactly zero calls, tokens, provider cost, retry, cache hit,
or provider latency. Its only limitation was local evidence availability; no
provider or evaluation failure occurred.

## Privacy, validation, and Git evidence

- The private before/after inventories are byte-identical: 49 files before and
  49 after, with no size, path, or SHA-256 change.
- No ignored run evidence was written or repaired.
- No private payload, identifier, path, hash, credential, project value, or
  provenance was added to this tracked report.
- No holdout, fixed-judge, RunPod, LM Studio, ADC, historical-run, or network
  activity occurred.
- No production code or test changed; therefore a full repository test run was
  not required by this handoff.
- A CommonMark parse completed; the file ends with a newline and contains no
  tab characters.
- Targeted pre-commit passed trailing-whitespace, end-of-file, large-file,
  merge-conflict, and private-key checks. Python-only Ruff hooks correctly
  skipped the Markdown-only delivery.
- The report-specific privacy-pattern scan found zero absolute or ignored
  private paths, full SHA-256 values, private case aliases, email addresses,
  Google API key patterns, credential fields, or private-key markers.
- `poetry check`, `git diff --check`, and the untracked-file whitespace check
  passed.
- The only intended tracked delivery is this report, left unstaged and
  uncommitted for manager review.

## Decision

The rejection was correct under the configured metric and acceptance rule, but
one proposal on one relevant failing example is not enough to assess GEPA.
A failure-focused four-proposal experiment, bounded to three through five and
using the full frozen 6/4 development split, is justified after offline repair
of private pre-decision persistence and format-fallback accounting. Keep the
candidate and proposer models unchanged, preserve strict no-tie promotion, and
defer the fixed judge until a distinct deterministic finalist exists.

No provider call occurred during this offline analysis.
