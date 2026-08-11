# WP-5.2B3B.1 Prompt Optimization Activity Log

**Status:** Ongoing evidence collection; P0 and BootstrapFewShot complete, GEPA
not started

**Evidence date:** 2026-08-11

**Purpose:** Preserve a detailed, privacy-safe record of the prompt-optimization
work, including negative results, engineering failures, DSPy compatibility
changes, operational costs, and article-ready observations. This is source
material for a future LinkedIn article, not an article draft and not a final
experimental conclusion.

## 1. Executive Snapshot

The project has tested three levels of prompt work so far:

1. manual global prompt variants P1 and P2;
2. DSPy BootstrapFewShot as a low-data automatic few-shot method;
3. infrastructure for GEPA reflective prompt search, which is implemented but
   has not yet run on the private development data.

Neither completed method beat the unchanged P0 prompt package:

- manual P1 and P2 each reduced pooled local usable outputs from 62/80 to 58/80;
- BootstrapFewShot matched P0 at 11/32 schema-valid validation outputs but
  reduced semantic agreement, failed context fit, and copied private material
  closely enough to fail the privacy promotion gate;
- a separate fixed Gemini Pro judge slightly favored P0 over Bootstrap on both
  paired and unpaired valid outputs.

The emerging lesson is not that prompt optimization is ineffective. It is that
small-model prompt optimization is constrained by several interacting systems:

- baseline schema reliability;
- task-specific behavior;
- prompt and demonstration context overhead;
- privacy of learned examples;
- optimizer/library compatibility;
- artifact authority and resumability;
- remote compute and credential operations.

GEPA remains the main unanswered experiment because it changes instructions
instead of depending on private few-shot examples.

## 2. Research Question

Can an established prompt optimizer produce one four-task prompt package that:

- improves Qwen3.5-4B and Phi-4 Mini together;
- does not hide model-specific prompt branches;
- preserves strict structured outputs and evidence authority;
- fits the common 8,192-token deployment context;
- does not copy private source/reference text into a deployable prompt;
- transfers from remote GPU search back to the local Windows target;
- improves on unseen development holdout conversations?

The current evidence answers only the manual-prompt and BootstrapFewShot parts.
GEPA, local transfer, and holdout generalization remain open.

## 3. Frozen Experimental Boundary

| Dimension | Frozen policy |
|---|---|
| Development corpus | 10 private conversations selected before prompt inspection |
| Optimizer train split | 6 conversations |
| Optimizer validation split | 4 conversations |
| Internal holdout | 20 conversations, unopened |
| Tasks | Conversation summary, work-mode classification, last activity, title assessment |
| Candidate models | Qwen3.5-4B Q4_K_M and Phi-4 Mini Instruct Q4_K_M |
| Candidate context | 8,192 tokens |
| Baseline | Accepted P0 four-task package |
| Prompt policy | One globally portable package; no model-specific branches |
| Reliability priority | Total valid, worst model, minimum task, then semantic measures |
| References | Existing FABLE-created private development references |
| Fixed judge | Vertex Gemini 3.1 Pro Preview, rubric v1, outside optimizer feedback |
| Holdout rule | No access until one winner or explicit P0 retention is frozen |

The 8K context was selected before prompt optimization. Earlier 16K testing did
not recover previous context failures and reduced combined validity, so prompt
development did not get a larger context window merely to accommodate a method.

## 4. Methods Investigated

### 4.1 Manual global prompt variants

P1 and P2 were manually designed complete four-task prompt packages. They were
applied unchanged across Qwen, Phi, and Gemini candidate execution. Both were
controlled against P0 on the same ten-conversation development scope.

This stage tested whether clearer global instructions could improve small-model
reliability without model-specific tuning.

### 4.2 DSPy BootstrapFewShot

BootstrapFewShot compiles a program by selecting labeled examples and, when a
candidate model generates an acceptable training answer, optionally selecting a
bootstrapped example. The accepted configuration allowed at most:

- one labeled demonstration per task;
- one bootstrapped demonstration per task;
- one compile round;
- candidate models acting as their own teachers;
- no repair or semantic retry.

The completed candidate contained four labeled demonstrations, one per task.
No generated response passed the strict acceptance boundary, so no generated
bootstrapped demonstration was included.

### 4.3 GEPA

GEPA is the planned primary optimizer. It uses structured execution feedback and
a strong proposer model to reflect on failures and propose revised instructions.
The planned implementation:

- uses P0 as the initial parent;
- mutates instruction text only;
- evaluates Qwen and Phi jointly;
- keeps the fixed Gemini judge outside the optimization loop;
- uses FABLE references and deterministic checks for development feedback;
- returns a bounded shortlist rather than choosing a hidden winner;
- preserves every proposal, failure, call, token, latency, and cost append-only.

GEPA has not yet made a private proposer call. No GEPA result should be implied
from this log.

### 4.4 Why these three methods were selected

This is a three-stage method program, not three completed optimizer results.
Manual global prompting and BootstrapFewShot are complete; GEPA is selected and
implemented but has not run on private development data.

The methods were chosen to increase automation and search power one step at a
time while keeping the experiment interpretable:

1. **Manual global variants** are the transparent control. They test whether a
   human-authored schema-first instruction or a bounded fictional few-shot
   package can improve both local models without introducing model-specific
   branches. They are cheap, inspectable, and establish whether more detailed
   prompting helps before adding an optimizer.
2. **BootstrapFewShot** is the smallest established DSPy compilation step that
   can exploit the existing labeled development cases. It tests a distinct
   mechanism: teaching by examples rather than rewriting the instruction. Its
   one-round, one-labeled/one-bootstrapped limits bound overfitting, context
   growth, privacy exposure, and compute.
3. **GEPA** is the planned instruction-search method. It can consume structured
   failure feedback and ask a stronger proposer to reflect on failure patterns,
   while Chronicle restricts mutation to the four system prompts. It is a good
   fit for this experiment because a deployable result need not contain private
   demonstrations.

This sequence also creates useful negative evidence. Manual elaboration showed
that clearer-looking instructions can reduce reliability. Bootstrap showed that
few-shot examples can exceed the context and privacy boundaries without
improving aggregate validity. GEPA now tests whether instruction-only reflective
search can avoid both failure modes.

### 4.5 Alternatives deliberately deferred

- **MIPROv2** jointly searches instructions and few-shot examples and uses a
  more involved optimization procedure. That is potentially useful, but it
  combines the two mutation types Chronicle first wants to understand
  separately and reintroduces the private-demonstration/context risks already
  exposed by Bootstrap.
- **BootstrapFewShotWithRandomSearch** would search more demonstration sets.
  The first bounded package was already non-promotable on privacy and context,
  so spending more calls on demonstration selection is not the next informative
  experiment.
- **Fine-tuning or reinforcement learning** changes model weights rather than
  only the external task definitions. It would require a different artifact,
  deployment, privacy, and evaluation boundary and is outside this prompt-only
  learning exercise.

The deferred methods remain possible follow-ups. The present choice is about
experimental clarity and bounded cost, not a claim that these are the only or
universally best prompt-optimization techniques.

### 4.6 Development data and FABLE references

#### 4.6.1 Corpus structure

The private development corpus contains 30 frozen conversations with four task
cases per conversation, for 120 reference cases in total. Selection happened
before content inspection. B3B/B3B.1 uses only ten conversations:

- six optimizer-training conversations, or 24 task cases;
- four optimizer-validation conversations, or 16 task cases per candidate
  model and 32 model/task positions across Qwen and Phi;
- twenty unopened holdout conversations, or 80 task cases reserved for a
  one-shot later evaluation.

Each case binds a conversation alias, task name, task-selected input, allowed
message evidence IDs, output schema, and hashes for the frozen source,
selection, task catalog, input, and reference. Conversation summary, work mode,
and title assessment use the conversation-overview selector. Last activity uses
the recent-meaningful-turn selector.

#### 4.6.2 Reference record structure

FABLE directly created one schema-valid reference for every frozen task case:

| Task | Main reference fields |
|---|---|
| Conversation summary | Summary, exact start date, exact last-active date, evidence message IDs |
| Work-mode classification | Manager/executor/one-off/mixed/unknown label, confidence, reason, evidence IDs |
| Last activity | Recent work, status, blockers, next action and basis, evidence IDs |
| Title assessment | Title-fit boolean, confidence, reason, optional replacement title, evidence IDs |

The references use the same application-owned output contracts expected from a
candidate. Evidence IDs must belong to the selected input; dates and cross-field
relationships are checked mechanically. Reference files are private and remain
outside Git.

These are **silver development references**, not human-adjudicated gold labels.
One strong teacher, FABLE, produced the semantic judgments directly from each
frozen selected input. There was no second-teacher consolidation and no human
review. Mechanical validation rejected malformed records, but it did not change
their meaning; FABLE rewrote the few invalid drafts from the same frozen input.

#### 4.6.3 How optimization feedback is produced

Chronicle evaluates a candidate in layers:

1. Did the call terminate and return parseable JSON?
2. Does the result satisfy the strict task schema and cross-field rules?
3. Are evidence IDs, dates, labels, and selected-input authority valid?
4. How does the valid result agree with the frozen FABLE reference?
5. Does the complete prompt fit 8,192 tokens and pass the privacy scanner?

Reliability is lexicographically primary: semantic improvement cannot compensate
for losing valid outputs, weakening the worst model, or weakening the minimum
task. Bootstrap uses a dedicated literal-boolean acceptance boundary derived
from these checks. GEPA is designed to receive structured facts and bounded
reference-backed feedback, such as an invalid enum, evidence mismatch, date
mismatch, label mismatch, timeout, or context failure.

#### 4.6.4 Why the fixed judge is outside optimization

The fixed Gemini judge is a post-hoc evaluator, not the optimizer's teacher.
Keeping it outside Bootstrap and the future GEPA loop provides several benefits:

- avoids tuning prompts directly to one judge's preferences or rationale style;
- keeps the search metric deterministic, reproducible, and cacheable;
- avoids a remote judge call for every candidate position;
- preserves an external comparison after the optimizer has stopped;
- limits same-family bias because the planned GEPA proposer and fixed judge are
  both Gemini 3.1 Pro, even though that risk cannot be removed completely.

For Bootstrap, the acceptance metric only decides whether a generated example
is trustworthy enough to package; the fixed judge is not consulted. For GEPA,
the planned feedback is deterministic and FABLE-reference-backed; no judge score
or rationale will enter proposal generation. Only after a candidate is frozen
may the fixed judge compare eligible outputs as a separate semantic reference.

This does not make the FABLE references independent human truth, nor does it
make the fixed judge authoritative. They serve different roles: FABLE supplies
frozen development targets for search and deterministic comparison; the fixed
judge supplies a consistent post-hoc semantic lens for valid outputs.

## 5. Controlled Manual Prompt Result

| Candidate | Pooled local valid | Qwen | Phi | Gemini portability |
|---|---:|---:|---:|---:|
| P0 | 62/80 | 30/40 | 32/40 | 38/40 |
| P1 | 58/80 | 26/40 | 32/40 | 32/40 |
| P2 | 58/80 | 26/40 | 32/40 | 36/40 |

Observations:

- Both manual variants reduced pooled local reliability by four cases.
- Phi was unchanged while Qwen absorbed the local regression.
- Gemini portability also regressed, so the variants did not merely trade local
  performance for stronger cloud-model behavior.
- P3 was not triggered under the predeclared continuation rule.
- This remains ten-conversation development evidence, not a general claim that
  explicit prompts or few-shot prompting are inferior.

## 6. Automatic P0 Baseline

The automatic-optimization run rebuilt P0 under the frozen 6/4 split and remote
candidate environment.

### Validation result

| Measure | P0 |
|---|---:|
| Total valid | 11/32 |
| Qwen valid | 5/16 |
| Phi valid | 6/16 |
| Conversation summary | 0/8 |
| Work-mode classification | 6/8 |
| Last activity | 0/8 |
| Title assessment | 5/8 |
| Semantic agreement | 0.1266 |

The zero-valid summary and last-activity cells show that the optimization problem
starts from a weak reliability floor. Prompt changes must first produce valid
structured evidence before semantic quality can matter.

The accepted P0 evidence is frozen and must not be rerun or rewritten.

## 7. BootstrapFewShot Result

### Demonstration package

The compiler selected four labeled examples:

- conversation summary taught with a Phi example;
- last activity taught with a Phi example;
- title assessment taught with a Qwen example;
- work-mode classification taught with a Qwen example.

No generated Bootstrap example was accepted. The package therefore tested a
small labeled few-shot strategy, not successful self-generated demonstration
learning.

### Validation result

| Measure | P0 | Bootstrap | Direction |
|---|---:|---:|---|
| Total valid | 11/32 | 11/32 | Equal |
| Qwen valid | 5/16 | 6/16 | Bootstrap +1 |
| Phi valid | 6/16 | 5/16 | Bootstrap -1 |
| Conversation summary | 0/8 | 0/8 | Equal |
| Work-mode classification | 6/8 | 5/8 | Bootstrap -1 |
| Last activity | 0/8 | 0/8 | Equal |
| Title assessment | 5/8 | 6/8 | Bootstrap +1 |
| Semantic agreement | 0.1266 | 0.0922 | Bootstrap lower |

The aggregate reliability did not improve. One valid case moved from Phi to
Qwen and one moved from work-mode classification to title assessment. Semantic
agreement declined.

### Promotion failures

Bootstrap was rejected independently of its aggregate score:

- the complete request did not fit the accepted 8,192-token envelope;
- four exact-sensitive-value findings and four source-ngram-overlap findings
  failed the prompt privacy gate;
- private demonstrations cannot become a deployable default prompt;
- minimum-task validity remained zero.

This is a completed negative comparator, not a candidate for GEPA parentage or
deployment.

### Measured attempt activity

| Measure | Bootstrap attempt |
|---|---:|
| Bootstrap compilation calls | 20 |
| Validation terminal positions | 80 |
| Validation invocations including infrastructure retries | 108 |
| Combined invocations | 128 |
| Infrastructure retries | 28 |
| Input tokens | 306,622 |
| Output tokens | 37,886 |
| Measured phase latency | 170,203 ms |
| Wrapper wall time | 209 seconds |
| Configured compute accounting | approximately US$0.0734 |

These are optimizer/candidate accounting figures, not the full RunPod invoice.

## 8. Fixed-Judge Reference

The fixed judge was intentionally excluded from Bootstrap feedback and is
contractually excluded from any future GEPA feedback. GEPA has not run yet. The
judge was run afterward as an optional local reference against only schema-valid
P0 and Bootstrap validation outputs.

### Scope and result

| Measure | P0 | Bootstrap |
|---|---:|---:|
| Terminal validation positions | 32 | 32 |
| Judge eligible | 11 | 11 |
| Judge completed | 11 | 11 |
| Invalid outputs excluded | 21 | 21 |

| Comparison | P0 | Bootstrap | Bootstrap minus P0 |
|---|---:|---:|---:|
| Paired case mean, 10 shared cases | 3.1600 | 3.1450 | -0.0150 |
| Unpaired case mean, 11 cases per arm | 3.2364 | 3.2227 | -0.0137 |
| Dimension-weighted mean | 3.2857 | 3.2200 | -0.0657 |

Task-level case means moved in opposite directions:

- work-mode classification: 2.8333 to 3.2500;
- title assessment: 3.7200 to 3.2000.

Model-level case means also favored P0:

- Phi: 2.6000 versus 2.3400;
- Qwen: 4.0000 versus 3.9583.

The paired result contained two improved, five equal, and three worse cases.
This is too small and too validity-filtered for statistical claims. It supports
the development decision to retain P0 but does not establish a general
BootstrapFewShot result.

### Judge operation

| Measure | P0 | Bootstrap |
|---|---:|---:|
| Successful calls | 11 | 11 |
| Infrastructure retries | 0 | 0 |
| Latency total | 40,387 ms | 48,872 ms |
| Latency p50 / p95 | 3,532 / 4,984 ms | 3,844 / 11,140 ms |
| Input tokens | 38,868 | 36,684 |
| Output/reasoning tokens | 2,898 | 2,890 |
| Usage-derived cost | US$0.112512 | US$0.108048 |

Including the successful synthetic diagnostic probe, known measured judge usage
was 76,326 input tokens and 5,987 output/reasoning tokens for US$0.224496.
Cache-only replay verified 22 entries and made zero additional provider calls.

## 9. DSPy And Harness Engineering Changes

The experiment required substantial compatibility and evidence work before a
single trustworthy Bootstrap result existed.

### `bench/optimization/dspy_bridge.py`

- Added a task-specific DSPy program bridge using public DSPy 3.3 APIs.
- Bound demonstrations to application-owned task and model authority rather
  than trusting generated fields.
- Captured accepted demonstration provenance from the public metric trace.
- Required exact selected-input and response hashes.
- Failed closed for missing, ambiguous, foreign, or tampered provenance.
- Preserved the one-labeled/one-bootstrapped limit.
- Added a Bootstrap-only boolean metric adapter: scores below 0.999 are false,
  scores at or above 0.999 are true, and nonnumeric/nonfinite values fail closed.
- Retained rich `dspy.Prediction(score, feedback)` results for GEPA.

### `bench/optimization/production.py`

- Added the application-owned LiteLLM/DSPy production adapters.
- Supported both mapping-style and typed DSPy history records.
- Added compatibility for `LMHistoryEntry`, `LMUsage`, and
  `CompletionTokensDetailsWrapper`.
- Collected usage from DSPy's deep-copied teacher programs.
- Counted prompt/input and completion/output aliases without duplication.
- Counted reasoning tokens exactly once.
- Propagated measured usage across post-response adaptation and authority
  failures instead of retaining only a conservative reservation.
- Kept unsupported populated usage structures fail-closed.

### `bench/optimization/execution.py`

- Added append-only, resumable P0, Bootstrap, and GEPA orchestration.
- Added durable authorization consumption and budget reservations.
- Captured optimizer and candidate wall time separately.
- Preserved interrupted attempts and measured usage.
- Required continuation candidates to meet total, worst-model, and
  minimum-task comparisons component by component.
- Prevented ordinary resume from silently rewriting completed evidence.

### `bench/optimization/package.py`

- Added immutable prompt candidate and result models.
- Stored demonstrations separately from prompt text.
- Bound candidate identity to prompts, contracts, demonstrations, lineage, and
  context.
- Restricted demonstrations to Bootstrap candidates.

### `bench/optimization/request_envelope.py`

- Counted system prompt, demonstrations, selected input, schema, wrappers, and
  output allowance in one complete request envelope.
- Added exact 8,192-fit and 8,193-nonfit boundaries.

### Supporting modules

- `authority.py`: frozen train/validation/input/reference authority.
- `budget.py`: hard candidate, call, token, wall-time, and cost ceilings.
- `diagnostics.py`: privacy-safe boundary and exception diagnostics.
- `feedback.py`: structured deterministic/reference-backed optimizer feedback.
- `privacy.py`: exact-value and source n-gram prompt leakage checks.
- `trials.py`: append-only attempt/current-pointer evidence.
- `operations.py`: inspect, shortlist, package, and checkpoint operations.

The unresolved checkpoint defect is in the operations/resume authority boundary:
historical P0 correctly records an earlier accepted application commit, while
the completed Bootstrap result records the later compatibility-fix commit. The
current wrapper incorrectly requires both to equal the latest configuration.
The repair must match each result to its own consumed execution authorization
while proving the experiment contract is otherwise unchanged.

## 10. Failure And Recovery Timeline

| Stage | Failure or stop | Classification | Resolution/status |
|---|---|---|---|
| Gate 1 | Existing harness supported prefixes but not strict ordered non-prefix 6/4 splits | Missing capability | Added frozen manifest support across prepare/generate/verify/score/judge |
| Gate 1 review | Bootstrap demonstrations were not packaged/replayed through the real DSPy path | Test/implementation gap | Added real DSPy compile, demonstration serialization, and replay tests |
| Gate 1 review | Budget, context, timing, and continuation boundaries were incomplete | Safety/reproducibility gap | Added hard ceilings, complete-request accounting, monotonic timing, and component-wise continuation |
| Vertex route | DSPy typed history was treated as a dictionary | DSPy compatibility defect | Added typed/mapping history accessor |
| Vertex route | Typed completion-token details were treated as a dictionary | DSPy compatibility defect | Added bounded typed/model-dump compatibility and reasoning accounting |
| Windows persistence | Atomic replacement encountered sharing violations | Platform reliability defect | Added bounded WinError 5/32 retry in the accepted atomic writer |
| First remote allocation | Compute was deleted too aggressively during diagnosis | Operating-procedure failure | Added no-delete rule, owner-first SSH, persistent-volume retention, and two-hour stop-only policy |
| Bootstrap attempt | DSPy augmented demonstrations omitted generated `task` and `model_id` fields | DSPy authority mismatch | Authority now comes from trusted compile scope and metric provenance, not generated text |
| Bootstrap attempt | `dspy.Prediction(score=0)` was truthy, so malformed output was accepted | DSPy metric adaptation defect | Added literal boolean threshold for Bootstrap while preserving rich GEPA feedback |
| Bootstrap completion | Historical P0 was rechecked against the newer Bootstrap application commit | Checkpoint identity defect | Still pending network-free repair; durable Bootstrap artifacts remain valid |
| Local judge preflight | Required remote candidate/response artifacts had not been returned | Artifact-transfer omission | Performed retrieval-only RunPod operation and verified 130/130 artifacts |
| Local judge auth | Two local ADC stores existed because custom `CLOUDSDK_CONFIG` and explicit ADC path diverged | Credential-source defect | Aligned application ADC with the active gcloud configuration directory |
| Local judge auth | Quota and resource projects differed | Credential configuration defect | Reissued ADC and set the intended quota project |
| Codex execution | Fresh executor processes did not inherit interactive shell variables | Process-boundary defect | Resolve/set ADC and Vertex variables inside each operator process before imports |
| OAuth login | Browser consent omitted the required cloud-platform scope | Authorization-flow defect | Repeated login with explicit cloud-platform consent and verified token scopes |
| Synthetic diagnostics | Recorder conflated provider, empty-response, JSON, schema, and contract failures | Observability defect | Added phase-specific ignored recorder with offline injected boundary tests |
| Final judge | Instrumented synthetic probe and all 22 private eligible outputs completed | Accepted execution | Cache-only replay proved zero new calls |

This separation matters for publication: most intermediate failures were
engineering or operations defects, not evidence about prompt quality.

## 11. Operational Evidence And Cost Boundaries

- Remote candidate execution used a known RTX 5090-class environment at an
  observed rate near US$0.99/hour when available.
- Scarce capacity required waiting cycles and persistent-volume checkpointing.
- The first accepted end-of-day stop preserved model artifacts, source bundle,
  P0 checkpoint, attempts, and restart manifests while reducing GPU spend to
  zero.
- Later retrieval used short-lived compatible compute only to return immutable
  evidence; estimated retrieval compute was approximately US$0.1733.
- Bootstrap configured compute accounting was approximately US$0.0734; this is
  not the provider invoice.
- The fixed-judge reference cost US$0.224496 in measured Vertex usage.
- A final B3B.1 cost reconciliation must separate RunPod billing, persistent
  storage, proposer calls, candidate inference, retrieval, and judge cost.

Do not sum partial figures from different checkpoints until the final billing
ledger proves they are nonoverlapping.

## 12. Article-Ready Observations So Far

### Observation 1: Manual prompt elaboration regressed the weakest model

- **Evidence:** P0 62/80 versus P1/P2 58/80; Qwen lost four valid cases while
  Phi was unchanged.
- **Interpretation:** A globally clearer prompt can still impose parsing or
  instruction-following overhead on the smaller/weaker model.
- **Caveat:** Ten development conversations; two manual variants only.
- **Confidence:** Medium for this controlled set, low for generalization.

### Observation 2: Few-shot prompting changed where failures occurred, not the total

- **Evidence:** P0 and Bootstrap both 11/32 valid; Qwen gained one, Phi lost one;
  title gained one, work mode lost one.
- **Interpretation:** A few-shot package may redistribute task/model behavior
  without improving overall reliability.
- **Caveat:** Four labeled examples and no accepted generated Bootstrap example.
- **Confidence:** Medium for the exact candidate, low beyond it.

### Observation 3: Few-shot examples carry real deployment costs

- **Evidence:** The Bootstrap package exceeded 8K and failed eight privacy
  findings despite using only four examples.
- **Interpretation:** Demonstration selection must be evaluated for context and
  privacy, not only accuracy.
- **Caveat:** The selected examples came from private development conversations.
- **Confidence:** High for this package.

### Observation 4: Semantic judging did not rescue the reliability result

- **Evidence:** Fixed judge slightly favored P0 in paired and unpaired means.
- **Interpretation:** Bootstrap did not hide a clear semantic gain behind equal
  schema-valid counts.
- **Caveat:** Only ten paired valid outputs; invalid outputs are excluded from
  semantic means.
- **Confidence:** Low-to-medium; descriptive only.

### Observation 5: Optimizer integration can cost more engineering time than inference

- **Evidence:** DSPy authority, truthiness, typed usage, copied-teacher history,
  atomic persistence, checkpoint identity, ADC routing, and diagnostics all
  required explicit fixes.
- **Interpretation:** Reproducible prompt optimization is a systems problem, not
  only an LLM prompt problem.
- **Caveat:** Chronicle deliberately enforces stricter authority, privacy, and
  append-only evidence than a quick notebook experiment.
- **Confidence:** High as an engineering observation.

### Observation 6: Negative experiments are useful when boundaries are frozen

- **Evidence:** P0 remained selected after manual prompts, Bootstrap, and fixed
  judging; no holdout was opened to search for a better story.
- **Interpretation:** A no-improvement result can still narrow the next method
  and protect against prompt overfitting.
- **Caveat:** GEPA remains untested.
- **Confidence:** High as a process observation.

## 13. Potential Article Spine

This is planning material only. Do not draft or publish until GEPA and preferably
local transfer/holdout evidence are complete.

1. **Problem:** Small local models are attractive, but strict multi-task output
   reliability is fragile.
2. **Baseline:** Manual prompt improvements made the controlled result worse.
3. **Established method:** BootstrapFewShot automated example selection but did
   not improve aggregate validity.
4. **Unexpected cost:** Four demonstrations failed context and privacy gates.
5. **Engineering reality:** DSPy integration, resumability, remote compute, and
   credentials became part of the experiment.
6. **Independent check:** A fixed cloud judge slightly favored the baseline.
7. **Next experiment:** GEPA instruction search may avoid private example
   deployment, but must prove remote-to-local transfer and holdout behavior.
8. **Takeaway:** Prompt optimization potential should be measured as reliability,
   quality, privacy, context, cost, and reproducibility together.

## 14. Publication Metrics Candidate List

Retain for later selection:

- valid outputs and failure categories by model/task;
- worst-model and minimum-task validity;
- semantic agreement against FABLE references;
- fixed-judge means with denominators;
- paired versus unpaired comparisons;
- context-envelope size and rejected candidates;
- privacy finding counts;
- candidate/proposer call counts and retries;
- input/output/reasoning tokens;
- candidate, optimizer, and judge latency;
- RunPod compute/storage and Vertex costs;
- number of generated, accepted, and rejected prompt candidates;
- remote-to-local performance gap;
- development-to-holdout generalization gap.

No single composite should replace reliability and semantic-quality axes. If a
single summary number is later used, publish its formula, invalid-output policy,
task weighting, sensitivity, and denominators.

## 15. Missing Evidence Before Article Drafting

- Canonical no-call recovery of the completed Bootstrap phase checkpoint.
- GEPA proposer and candidate results.
- Complete GEPA search trace and cost reconciliation.
- Three to five privacy/context-eligible shortlisted candidates, or explicit
  no-improvement closure.
- Local rerun of P0 and shortlist candidates.
- One frozen winner or explicit P0 retention.
- One-shot evaluation on the untouched 20-conversation holdout.
- Final fixed-judge and Gemini portability evidence.
- Human decision on which metrics and operational failures belong in the public
  narrative.

## 16. Prohibited Claims At This Stage

Do not claim:

- BootstrapFewShot is generally ineffective;
- manual prompt engineering generally hurts small models;
- GEPA works or fails for Chronicle;
- remote gains transfer locally;
- the current results generalize beyond the development corpus;
- fixed-judge differences are statistically significant;
- FABLE references are independent human gold labels;
- invalid outputs have equivalent semantic quality to valid outputs;
- the prompt search improved the untouched holdout.

## 17. Evidence Sources

- `md/handoffs/WP-5.2B3B-global-prompt-development.md`
- `md/handoffs/reports/WP-5.2B3B-completion-report.md`
- `md/handoffs/reports/WP-5.2B3B-prompt-development-evidence-brief.md`
- `md/handoffs/WP-5.2B3B.1-automatic-prompt-optimization-remote-search.md`
- `md/handoffs/reports/WP-5.2B3B.1-execution-progress.md`
- `md/handoffs/reports/WP-5.2B3B.1-gate1-validation-review.md`
- `md/handoffs/reports/WP-5.2B3B.1-runpod-teardown-incident-report.md`
- `docs/development-optimization.md`
- `docs/runpod-vertex-adc.md`
- `docs/windows-vertex-adc.md`
- `md/handoffs/WP-5.2B3B.1A-bootstrap-local-fixed-judge-reference.md`
- `md/handoffs/reports/WP-5.2B3B.1A-bootstrap-local-fixed-judge-reference-completion-report.md`
- [DSPy BootstrapFewShot API](https://dspy.ai/api/optimizers/BootstrapFewShot/)
- [DSPy GEPA API](https://dspy.ai/api/optimizers/GEPA/overview/)
- [DSPy MIPROv2 API](https://dspy.ai/api/optimizers/MIPROv2/)

Private raw inputs, FABLE references, candidate responses, prompt packages,
provider payloads, rationales, credentials, resource identifiers, and billing
records remain under ignored local storage and are not publication sources by
themselves.

## 18. Update Protocol

Append future GEPA, transfer, and holdout findings to this log without rewriting
accepted historical observations. Every update should separate:

1. measured fact;
2. interpretation;
3. denominator;
4. limitation;
5. confidence;
6. publication status.
