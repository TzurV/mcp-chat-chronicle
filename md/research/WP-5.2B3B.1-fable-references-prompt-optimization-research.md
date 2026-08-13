# FABLE References In Prompt Optimization: Research Brief

**Status:** Research complete; article not drafted

**Date:** 2026-08-13
**Purpose:** Source material for a future LinkedIn post or article about how a
small, reusable teacher-created reference set can reduce repeated prompt-tuning
work, latency, and remote-model cost.

## 1. Executive Summary

"FABLE references" is a **Chat Chronicle project term**, not an established
term found in the prompt-optimization, distillation, weak-supervision, or LLM
evaluation literature reviewed for this brief. A targeted search found unrelated
uses of "Fable" but no recognized methodology called "FABLE references."
Public writing must therefore introduce the phrase as local shorthand and link
it to established concepts:

- strong-model or teacher-generated reference answers;
- synthetic or pseudo-labels;
- silver-standard development labels;
- labeled demonstrations;
- reference-based evaluation targets.

In Chronicle, FABLE directly created 120 structured reference outputs for 30
frozen real conversations across four AI tasks. The references were generated
once, mechanically validated, kept private, and reused to assess outputs from
smaller candidate models. They are **silver development references**: useful
and consistent, but neither human-adjudicated ground truth nor a final holdout.

The central economic idea is straightforward:

> Pay the strongest teacher once to establish reusable task targets, then use
> inexpensive deterministic and reference-based checks across many prompt
> candidates. Reserve costly remote judging or human review for a small frozen
> shortlist and the untouched holdout.

This can reduce marginal evaluation cost as the number of prompt candidates
grows. The claim is conditional, not automatic. Savings depend on teacher cost,
judge cost, candidate count, caching, local inference cost, and how much of the
task can be scored reliably without another LLM call. Chronicle has not yet
measured a counterfactual "judge every candidate" bill, so this brief provides
formulas and fictional examples rather than a claimed project saving.

The approach has a corresponding risk: reuse makes teacher mistakes cheap to
repeat too. A frozen reference set can encode one teacher's biases, omit valid
alternative answers, become stale after schema changes, and encourage prompt
overfitting. A sealed holdout, explicit versioning, privacy controls, and a
separate post-hoc evaluator remain necessary.

## 2. Terminology And Evidence Labels

This brief uses three evidence labels throughout:

- **Sourced fact:** supported by an external primary paper or official
  documentation linked in section 14.
- **Chronicle fact:** supported by the tracked, privacy-safe project documents
  listed in section 13.
- **Inference:** a reasoned implication or proposed editorial framing. It must
  not be published as a measured result without additional evidence.

### 2.1 Is "FABLE references" an industry term?

**Finding:** No evidence was found that it is an established technical term.
The exact phrase did not resolve to a recognized method in targeted searches of
academic and official prompt-optimization sources. "FABLE" is the project alias
for the teacher used to create Chronicle's references.

Recommended public definition:

> In Chat Chronicle, I call them **FABLE references**: structured reference
> answers created once by a strong teacher model, frozen with their task inputs,
> and reused as silver labels while testing prompts on smaller models.

Do not capitalize the name as though it were an acronym unless the project later
defines one. Do not imply that DSPy, GEPA, Anthropic, or the wider research
community uses this term.

### 2.2 Related established concepts

| Term | Established meaning | Relationship to Chronicle |
| --- | --- | --- |
| Teacher-generated output | An output from a stronger or designated model used to supervise, compare, or train another system | Closest general description of each FABLE output |
| Pseudo-label / synthetic label | A machine-produced target used instead of a human label | Applicable, but the outputs are structured records rather than only class labels |
| Silver-standard label | A useful but imperfect label not treated as expert-adjudicated ground truth | Chronicle's preferred quality designation |
| Gold reference | A carefully adjudicated authoritative target, commonly human-created or otherwise strongly validated | **Not** an accurate description of the FABLE set |
| Demonstration | An input/output example placed in a prompt to guide inference | Some reference cases can serve as labeled demonstrations, subject to privacy and context limits |
| Distillation target | Teacher behavior used to train a student's parameters or outputs | Conceptually related, but Chronicle's current work changes prompts, not model weights |
| Evaluation reference | A target against which candidate output is scored | The primary role of FABLE references in Chronicle's optimization loop |

### 2.3 Prompt optimization is not fine-tuning

Knowledge distillation classically transfers knowledge from an ensemble or
larger teacher into an easier-to-deploy student model. Modern LLM work also uses
teacher-generated labels and rationales to fine-tune smaller models. Chronicle's
current experiment is narrower: it keeps the candidate model weights fixed and
optimizes external instructions or demonstrations.

Calling the Chronicle work "fine-tuning" would therefore be inaccurate. A safe
description is **teacher-supervised prompt optimization** or **reference-backed
prompt search**. The same reference corpus could support a future fine-tuning
experiment, but that would require a separate data, privacy, model, and
evaluation design.

## 3. Chronicle's Reference Corpus

### 3.1 What was created

**Chronicle facts:**

- A frozen private development corpus contains 30 conversations.
- Each conversation contributes four task cases, producing 120 references.
- The tasks cover conversation summary, work-mode classification, last
  activity, and title assessment.
- Selection was deterministic and frozen before content inspection.
- The teacher used only the same task-selected input available to candidate
  models, preventing a privileged-information advantage.
- FABLE directly created every semantic reference in the execution chat.
- All 120 references passed JSON/schema, evidence-membership, and deterministic
  date validation.
- No second teacher reconciled the answers and no human semantically
  adjudicated them.
- Mechanical validation could reject malformed records but could not rewrite
  their meaning; the teacher rewrote invalid drafts from the same frozen input.
- The references and selected inputs remain private and outside Git.

### 3.2 What a reference contains

Every reference is bound to a frozen case and an application-owned output
contract. Depending on the task, the output contains:

- a bounded summary and exact application-provided dates;
- a classification label, concise reason, and uncalibrated confidence;
- a recent-activity status, blockers, and next-action fields;
- a title-fit decision and optional suggested replacement;
- evidence-message identifiers constrained to the task-selected input.

The important design property is not the prose itself. It is the combination of
**semantic target + strict structure + evidence authority + versioned task
identity**. This makes many failures mechanically diagnosable before a semantic
judge is considered.

### 3.3 Development split

The prompt-optimization work uses only a bounded subset of the corpus:

- six conversations for optimizer training;
- four conversations for optimizer validation;
- twenty conversations reserved as an unopened one-shot holdout.

This division is critical. The training and validation references can guide
candidate selection. The holdout must not guide prompt creation, proposal,
shortlisting, or debugging. Otherwise it stops measuring generalization.

### 3.4 Data-flow summary

```text
Frozen selected input
        |
        +--> FABLE creates one structured silver reference (one-time)
        |
        +--> Candidate model runs with prompt P0, P1, ... PK
                         |
                         v
             schema / evidence / contract checks
                         |
                         v
              comparison with frozen reference
                         |
                         v
          structured score and diagnostic feedback
                         |
                         v
            prompt optimizer proposes next candidate

After search stops:
shortlisted candidates --> separate fixed judge --> sealed holdout
```

## 4. How References Enter Prompt Optimization

### 4.1 Layered scoring

Chronicle evaluates each candidate output in layers:

1. **Runtime reliability:** Did the model return a terminal response?
2. **Syntax:** Is it parseable JSON?
3. **Schema and cross-field validity:** Are required fields, labels, null rules,
   and lengths valid?
4. **Evidence authority:** Do cited messages and dates come from the permitted
   selected input?
5. **Reference agreement:** Does the valid result agree with the frozen FABLE
   target on task-relevant fields and semantics?
6. **Deployment eligibility:** Does the complete prompt fit the context budget
   and pass privacy/leakage checks?

This design avoids spending semantic effort on an output that is already
unusable. A fluent but invalid result is still a failed application result.

### 4.2 BootstrapFewShot

DSPy's official `BootstrapFewShot` documentation describes an optimizer that
constructs prompt demonstrations from labeled training examples and accepted
bootstrapped demonstrations. A metric compares expected and predicted values
and decides whether a generated example is acceptable.

In Chronicle, references have two possible roles here:

- provide the labeled output for a demonstration;
- provide the expected target used by the strict acceptance metric.

Chronicle's bounded experiment allowed very few demonstrations and required a
near-perfect acceptance boundary. The completed Bootstrap candidate did not
improve aggregate reliability and was not deployable because the private
demonstrations exceeded context/privacy boundaries. That negative result is
project-specific; it does not refute BootstrapFewShot generally.

### 4.3 GEPA

GEPA (Genetic-Pareto) is a reflective prompt optimizer. The paper and official
DSPy documentation describe three key mechanisms:

1. execution trajectories are collected;
2. a strong reflection model receives scores and textual feedback, diagnoses
   failures, and proposes prompt mutations;
3. Pareto-based candidate selection preserves complementary candidates instead
   of evolving only a single global winner.

Official DSPy documentation explicitly supports metrics that return both a
scalar score and textual feedback. That is where Chronicle's references become
especially useful. A candidate can receive bounded facts such as:

- invalid schema or enum;
- incorrect evidence membership;
- date disagreement;
- reference label disagreement;
- missing or inconsistent action fields;
- context or timeout failure.

The proposer can learn from these diagnostics without asking the original
teacher to regenerate an answer for every prompt candidate. In Chronicle, only
instruction text may mutate; selectors, schemas, evidence rules, generation
settings, and holdout cases remain fixed.

### 4.4 The fixed judge is outside the loop

Chronicle intentionally keeps its fixed remote semantic judge outside
Bootstrap and GEPA feedback. The optimizer uses deterministic checks and
FABLE-reference-derived feedback. The judge is called only after a candidate is
frozen, and only for eligible outputs.

Reasons:

- **Cost:** judging every output of every prompt candidate multiplies remote
  calls by candidate count.
- **Latency:** remote judge calls add another serial or parallel service stage.
- **Reproducibility:** frozen references and deterministic contracts are easier
  to cache and replay.
- **Bias control:** optimizing directly against judge rationales risks learning
  that judge's preferences rather than the task.
- **Separation of roles:** references guide search; the judge provides a
  post-hoc semantic lens.

This separation is a Chronicle design choice, not a universal GEPA
requirement. GEPA can use any compatible feedback metric, including one backed
by an LLM, but Chronicle deliberately does not do so in this experiment.

## 5. Reference Scoring, LLM-As-Judge, And Human Review

| Method | Primary input | Marginal cost | Strength | Main limitation |
| --- | --- | ---: | --- | --- |
| Deterministic contract checks | Candidate output plus schema/rules | Very low | Exact, reproducible, fast | Cannot resolve open-ended semantic quality |
| Reference-based checks | Candidate plus frozen expected output | Low after reference creation | Cacheable target; supports exact and structured semantic comparisons | Inherits reference errors and may penalize valid alternatives |
| Embedding/reference metric | Candidate plus reference | Low local compute | Captures paraphrase better than lexical equality | Similarity is not factual or task correctness |
| LLM-as-judge | Task, candidate, rubric, optionally reference | Remote/local model cost per judgment | Flexible assessment of open-ended quality | Position, verbosity, self-enhancement, reasoning, and provider drift risks |
| Human review | Task, source, candidate, rubric | Highest time/cost | Domain judgment and adjudication | Slow, variable, difficult to scale |

### 5.1 What research says

- BERTScore demonstrates that contextual embedding similarity to a reference
  can correlate better with human judgment than earlier lexical metrics on its
  evaluated generation tasks. This supports semantic reference comparison, but
  not the claim that similarity equals application correctness.
- Deutsch, Dror, and Roth show that reference-free generation metrics can be
  biased toward outputs resembling the evaluator and can even disfavor
  higher-quality human text. This supports retaining independent references,
  while also warning that no single metric should be treated as truth.
- Zheng et al. show that strong LLM judges can approximate human preferences at
  scale, but document position, verbosity, self-enhancement, and reasoning
  limitations. This supports using a judge as a useful external lens, not an
  unquestioned oracle.
- Mohta et al. found that models trained on human labels consistently
  outperformed models trained on LLM-generated labels in their study. This is a
  direct warning against renaming machine-created silver labels as gold.

### 5.2 Why not use only one method?

**Inference:** A practical evaluation stack is hierarchical:

1. reject mechanically invalid output cheaply;
2. compare valid output with a frozen reference;
3. use a separate judge for shortlisted, open-ended cases;
4. use human adjudication for high-stakes disagreements or publication claims.

Chronicle currently omits step 4 by owner decision, so its conclusions must
remain development conclusions rather than human-validated quality claims.

## 6. Relationship To Distillation And Weak Supervision

### 6.1 Distillation

Hinton, Vinyals, and Dean formalized knowledge distillation as compressing the
knowledge of an ensemble into a model that is easier to deploy. Later LLM work
uses teacher-generated labels or rationales as supervision for smaller models.
Hsieh et al.'s Distilling Step-by-Step shows that teacher rationales can provide
additional supervision and reduce the data required in their evaluated setup.

Chronicle resembles distillation in **teacher/student economics** but not in
mechanism:

- the teacher produces reusable task targets;
- smaller models are evaluated against those targets;
- deployment is intended to use the smaller models;
- model weights are not changed in the current experiment.

The economic analogy is valid; calling the current artifact a distilled model
is not.

### 6.2 Synthetic instruction data

Self-Instruct demonstrates that a model can generate, filter, and reuse
instruction/input/output samples to reduce reliance on human-authored
instruction data. It also retains expert-written evaluation and human
evaluation for novel tasks. The relevant principle is **generate once, filter,
then reuse**. Chronicle differs because its real inputs were frozen first and a
separate teacher produced task outputs; the teacher did not invent the corpus.

### 6.3 Weak supervision and silver labels

Snorkel demonstrates the broader value of weak supervision: imperfect sources
can produce useful training labels much faster than exhaustive hand labeling,
provided their lineage, error, and correlation are modeled. Chronicle uses a
single teacher rather than multiple labeling functions, so it cannot estimate
source agreement or correlation. The relevant lesson is to preserve provenance
and avoid confusing scalable weak supervision with ground truth.

## 7. Cost And Time Framework

The formulas below are **inferences and planning tools**, not measured
Chronicle savings.

### 7.1 Variables

Let:

- `N` = number of development cases;
- `K` = number of unique prompt candidates evaluated;
- `M` = number of shortlisted candidates judged after search, where `M < K`;
- `C_T` = one-time teacher cost per reference case;
- `C_C` = candidate-model generation cost per case;
- `C_R` = local deterministic/reference-scoring cost per case;
- `C_J` = remote judge cost per candidate case;
- `H` = one-time corpus preparation, validation, and engineering cost;
- `p_cache` = fraction of attempted evaluations served from a valid cache;
- `K_u = K(1 - p_cache)` = effective unique candidate evaluations.

Use fully loaded cost where possible: API charges, compute, operator time,
artifact transfer, and engineering time. A teacher used interactively under a
subscription may have no itemized per-call invoice, but it still consumes time
and capacity.

### 7.2 Strategy A: judge every candidate

Ignoring shared setup:

```text
Cost_all_judged = K_u * N * (C_C + C_J)
```

### 7.3 Strategy B: frozen references during search, judge shortlist

```text
Cost_reference_search = H
                      + N * C_T
                      + K_u * N * (C_C + C_R)
                      + M * N * C_J
```

Candidate generation appears in both strategies and cancels when comparing the
evaluation architecture. The estimated savings are therefore:

```text
Savings = (K_u - M) * N * C_J
        - H
        - N * C_T
        - K_u * N * C_R
```

The architecture breaks even when:

```text
(K_u - M) * C_J > (H / N) + C_T + K_u * C_R
```

If there is no final shortlist judge (`M = 0`) and setup cost is excluded, a
simplified per-case break-even is:

```text
K_u > C_T / (C_J - C_R)
```

provided `C_J > C_R`.

### 7.4 Time model

For serial execution, substitute latency for cost:

- `T_T`: teacher latency per case;
- `T_R`: reference-scoring latency per case;
- `T_J`: judge latency per case.

```text
Time_saved_serial = (K_u - M) * N * T_J
                  - N * T_T
                  - K_u * N * T_R
                  - H_time
```

Wall-clock time under parallelism is not the serial sum. It is constrained by
batch size, concurrency, rate limits, retries, queueing, model load time, and
the slowest stage. Report both total model-seconds and observed wall time when
publishing actual results.

### 7.5 Fictional cost example

Assume, purely for illustration:

- 40 development cases;
- 20 unique prompt candidates;
- 3 shortlisted candidates;
- one-time teacher generation: `$0.04` per case;
- remote judge: `$0.025` per case;
- local reference scoring: `$0.0002` per case;
- setup cost excluded because it is treated as reusable infrastructure;
- candidate inference excluded because both strategies use it.

Judge-every-candidate evaluation cost:

```text
20 * 40 * $0.025 = $20.00
```

Reference-search plus shortlist judging:

```text
Teacher references: 40 * $0.04          = $1.60
Reference scoring:   20 * 40 * $0.0002 = $0.16
Shortlist judging:    3 * 40 * $0.025  = $3.00
Total                                       $4.76
```

Illustrative saving: `$15.24`, or 76.2%. This is **not a Chronicle result**.
Changing candidate count, token length, teacher price, judge model, cache hit
rate, or required human review can materially change it.

### 7.6 Fictional latency example

Using the same case/candidate counts, suppose:

- teacher generation averages 4 seconds per case;
- reference scoring averages 0.02 seconds per candidate case;
- remote judging averages 4 seconds per candidate case;
- all figures are serial model time.

```text
Judge every candidate: 20 * 40 * 4s = 3,200s

Reference architecture:
  Teacher once:       40 * 4s        = 160s
  Reference scoring:  20 * 40 * .02 =  16s
  Judge shortlist:     3 * 40 * 4s   = 480s
  Total                                 656s
```

The fictional serial saving is 2,544 seconds (42.4 minutes). Real wall time
could be much lower under parallel execution, or higher under rate limits and
retries.

### 7.7 When references do not save money

The reference architecture may cost more when:

- only one prompt is tested;
- a cheap deterministic gold label already exists;
- reference creation requires expensive expert adjudication;
- every output still requires a judge call;
- the schema changes before the references are reused;
- prompt candidates are mostly cache hits;
- the teacher must be recalled frequently because targets are unstable;
- local reference scoring is itself an expensive model call;
- setup and privacy engineering exceed the avoided judge cost.

## 8. Limitations And Failure Modes

### 8.1 Teacher bias and error

A single teacher can systematically misclassify ambiguous cases, prefer its own
writing style, overlook minority patterns, or express unjustified confidence.
Mechanical schema validation catches malformed structure, not incorrect
meaning. Reuse amortizes both good supervision and bad supervision.

Mitigations:

- retain teacher/model/task provenance;
- mark the data silver rather than gold;
- sample disagreements for later human review;
- consider a second independent teacher or consensus only when justified;
- preserve an external evaluator that did not generate the references;
- report uncertainty and disagreement, not only aggregate means.

### 8.2 One reference under-specifies valid output space

Open-ended summaries may have many correct forms. Exact match against one
reference can punish a valid alternative. Use deterministic equality only for
fields with one authoritative answer, such as an application-provided date or
enum. Use bounded semantic comparison or rubric-based review for open text.

### 8.3 Correlated evaluation

Candidate, teacher, proposer, and judge can share model families, training data,
or stylistic preferences. Zheng et al. call out self-enhancement bias in LLM
judging; Deutsch et al. show that reference-free evaluators can favor similar
generators. A different model name does not guarantee independence.

Mitigations:

- document every role and model family;
- keep teacher, proposer, and judge signals separate;
- blind the judge to candidate identity;
- avoid optimizing on judge rationales used later for final claims;
- use human adjudication for important disagreements.

### 8.4 Development overfitting

Every time a prompt is selected using the same finite development references,
the process can overfit the selection criterion. Cawley and Talbot show that
model-selection criteria themselves can be overfit and produce selection bias.
This applies directly to repeated prompt search.

Mitigations:

- freeze train/validation/holdout roles before search;
- keep the holdout physically and procedurally unopened;
- set candidate and call budgets before seeing results;
- evaluate the chosen prompt on the holdout once;
- do not tune again based on the holdout without declaring a new experiment.

### 8.5 Reference leakage

An optimizer may copy source or reference text into a prompt, especially when
few-shot examples or rich textual feedback are available. This can expose
private data, inflate development scores, and make deployment invalid.

Mitigations:

- pass bounded diagnostics rather than raw reference prose when possible;
- scan proposed prompts for exact sensitive values and source/reference
  n-grams;
- prohibit private demonstrations in deployable defaults unless separately
  authorized;
- treat a leakage finding as promotion failure, not something to redact after
  selection;
- never publish private prompts, reference content, paths, IDs, or hashes.

### 8.6 Privacy and provider disclosure

Reference generation and remote prompt proposal can disclose selected private
text to providers. This is separate from Git privacy. A file can remain
untracked yet still leave the machine through an API call.

Mitigations:

- obtain explicit purpose- and provider-specific authorization;
- send only the selected development subset needed for the task;
- exclude holdout and unrelated conversations;
- use short-lived credentials and least privilege;
- keep private artifacts in ignored storage;
- publish only aggregate denominators, costs, and privacy-safe findings.

### 8.7 Task, schema, and selector versioning

A reference is valid only for the exact task definition that created it. Changes
to system instruction, selected input, output schema, evidence policy,
finalizer, or label taxonomy may make the old target incomparable.

Mitigations:

- bind each reference to task, schema, selector, and corpus versions;
- include all effective invalidators in cache identity;
- fail closed on mismatched versions;
- regenerate only under a declared new corpus version;
- never silently normalize old references into a new contract.

### 8.8 Staleness and distribution shift

Reference quality can decay as user workflows, source providers, model
behavior, or the task definition changes. A frozen development set improves
reproducibility but does not guarantee current representativeness.

Mitigations:

- record creation date and corpus coverage;
- monitor production-like failure categories;
- create a new versioned corpus rather than mutating the old one;
- compare old and new corpora before replacing a benchmark.

### 8.9 Silver labels are not human truth

No human semantic review occurred in Chronicle's reference creation. This makes
the data useful for engineering iteration but insufficient for statements such
as "human-quality," "ground truth," or "proven accuracy." Human review is not
mandatory for every internal experiment, but its absence must remain explicit.

## 9. Article-Ready Findings And Careful Claims

### 9.1 Strong observations

1. **A reference set is an asset, not a one-off answer.** The same frozen target
   can evaluate many models and prompt candidates without regenerating the
   teacher response.
2. **Structure multiplies reuse value.** A reference with schema, evidence, and
   provenance supports more cheap checks than unstructured prose alone.
3. **Reliability should precede elegance.** A semantic judge cannot make invalid
   JSON or unauthorized evidence deployable.
4. **The optimizer does not need the final judge in every loop.** Rich
   reference-backed diagnostics can guide prompt search; the judge can remain a
   separate shortlist check.
5. **Cheap reuse increases overfitting risk.** The easier it becomes to score
   thousands of variants, the more important the sealed holdout becomes.
6. **Teacher supervision is reusable but not automatically true.** The correct
   label is silver until independently adjudicated.
7. **Few-shot reuse has a privacy/context cost.** Reference outputs can be
   useful as demonstrations while still being unsuitable for deployment.

### 9.2 Claims supportable now

- "Chronicle created a private set of 120 structured silver references once and
  reused them across model and prompt experiments."
- "The architecture can reduce repeated remote evaluation calls as the number
  of prompt candidates grows."
- "FABLE references are a Chronicle-specific name for teacher-created silver
  development references."
- "Deterministic checks and frozen references guide optimization; a separate
  fixed judge is kept outside the optimization loop."
- "Whether the approach saves money depends on candidate count, teacher cost,
  judge cost, caching, and setup cost."
- "A holdout is still required because reusable development references can be
  overfit."

### 9.3 Claims to avoid

- "FABLE references" is a standard industry technique.
- The references are gold labels or ground truth.
- FABLE references replace human review in high-stakes evaluation.
- Chronicle has already proved a specific percentage or dollar saving.
- Prompt optimization is fine-tuning or weight distillation.
- Reference similarity proves factual correctness.
- GEPA uses the fixed Gemini judge as its optimization teacher.
- The teacher's hidden reasoning or chain of thought was transferred.
- One teacher is unbiased because it is stronger than the candidate.
- Development-set gains guarantee holdout or production gains.

## 10. Suggested Article Directions

### 10.1 Possible titles

1. **What Are FABLE References? Paying the Strong Model Once for Prompt Tuning**
2. **Build the Answer Key Once: A Practical Shortcut for Prompt Optimization**
3. **Silver Labels, Smaller Models: Reusing a Strong LLM During Prompt Search**
4. **Why I Kept the LLM Judge Out of the Prompt-Optimization Loop**
5. **From One Strong Teacher to Many Cheap Prompt Experiments**
6. **The Prompt-Tuning Flywheel: Frozen References, Local Models, and a Holdout**

The first title needs an immediate subtitle or opening sentence explaining that
the term is project-specific.

### 10.2 Recommended narrative structure

1. **The problem:** Trying 20 prompts across many real cases creates a hidden
   multiplication of model and judge calls.
2. **The project term:** Define FABLE references honestly as Chronicle-specific
   silver references.
3. **The one-time step:** A strong teacher creates structured targets from
   frozen task inputs.
4. **The reuse loop:** Small/local models run repeatedly; deterministic and
   reference-backed checks score them cheaply.
5. **Where DSPy fits:** BootstrapFewShot can turn references into examples;
   GEPA can turn reference-derived diagnostics into instruction proposals.
6. **Where the judge fits:** Outside the loop, evaluating only frozen
   shortlisted candidates.
7. **The economic model:** Show cost curves and a clearly fictional break-even
   scenario.
8. **The catch:** Silver labels encode teacher bias; privacy leakage and
   development overfitting are real.
9. **The safeguard:** Versioned contracts, privacy scanning, and an unopened
   holdout.
10. **The open question:** Can reflective prompt optimization turn the reusable
    reference asset into gains that survive the holdout?

### 10.3 Alternative narrative: an answer key, not an oracle

Use the analogy of creating a reusable answer key:

- writing the key is expensive;
- marking repeated practice papers is cheap;
- a flawed key scales its flaw;
- students can overfit the practice set;
- the final exam must stay sealed.

The analogy is accessible but should say "silver answer key" or "working answer
key," not "official answer key."

## 11. Visual And Chart Ideas

### 11.1 Pay once, reuse many

A simple flow diagram:

```text
Strong teacher (one pass)
          |
          v
  Frozen silver references
     /       |       \
Prompt A  Prompt B  Prompt ... K
     \       |       /
  cheap checks + comparison
          |
          v
  small shortlist --> external judge
```

### 11.2 Cost crossover chart

- X-axis: number of unique prompt candidates.
- Y-axis: cumulative evaluation cost.
- Line 1: judge every candidate; starts low, rises steeply.
- Line 2: one-time teacher references + cheap scoring + shortlist judge;
  starts higher, rises slowly.
- Mark the break-even point using the formula in section 7.
- Label all plotted values fictional unless replaced by reconciled project
  accounting.

### 11.3 Evaluation stack

A funnel with complete denominators:

```text
all candidate outputs
  -> terminal responses
  -> parseable JSON
  -> schema/evidence valid
  -> reference agreement
  -> privacy/context eligible
  -> fixed-judge shortlist
  -> sealed holdout
```

This communicates why one semantic score cannot summarize the whole system.

### 11.4 Three supervision roles

A three-column visual:

| Teacher reference | Prompt proposer | Fixed judge |
| --- | --- | --- |
| Creates reusable target once | Suggests new instructions | Reviews frozen shortlist |
| Inside development scoring | Inside optimization | Outside optimization |
| Silver, not truth | Learns from diagnostics | Consistent but biased lens |

### 11.5 Risk/reward matrix

| Benefit | Matching risk |
| --- | --- |
| Reusable scoring | Reusable teacher error |
| Lower marginal cost | Upfront corpus cost |
| Fast candidate search | Development overfitting |
| Rich structured feedback | Reference leakage |
| Reproducibility | Staleness after task changes |

## 12. Questions For The Later Article Writer

Before drafting the final article, resolve:

1. Is the article primarily an educational explainer or a Chronicle experiment
   report?
2. Will actual reconciled teacher, compute, and judge costs be available, or
   should the article retain fictional economics only?
3. Has GEPA completed, and did any improvement survive the sealed holdout?
4. Is FABLE's public product/model name appropriate to mention, or should the
   article say only "a strong teacher model"?
5. Will the article disclose the absence of human adjudication near the first
   use of "silver"?
6. Which project results are publication-safe and supported by complete
   denominators?
7. Should the article include the negative Bootstrap result as evidence that
   reference reuse is not automatically deployable?
8. Is there an owner-reviewed calculation of engineering time, not only API and
   GPU cost?

## 13. Chronicle Sources Consulted

These are tracked, privacy-safe project documents. No private corpus content,
reference output, identifier, path, hash, credential, or cloud resource was
used in this brief.

1. **WP-5.1.2B: Direct FABLE Development References** (project handoff). Defines
   the single-teacher reference-creation protocol, fairness boundary, task
   schemas, provenance, privacy, and silver-label status.
2. **WP-5.1.2B Completion Report** (project report). Confirms 30 conversations,
   four tasks, 120 validated references, no second teacher, no human semantic
   adjudication, and no tracked private artifacts.
3. **WP-5.2B3B.1 Prompt Optimization Activity Log** (project research log).
   Records the development split, layered metric, Bootstrap result, planned
   GEPA role, fixed-judge separation, failures, and privacy controls.
4. **Development Optimization Guide** (project operations guide). Documents
   optimizer lifecycle, authority, request envelope, budgets, privacy scanning,
   transfer boundary, and official DSPy compatibility sources.
5. **WP-5.2B3B.1C: GEPA Pilot And Bounded Search** (project handoff). Defines
   instruction-only mutation, P0 parentage, FABLE-reference-derived feedback,
   proposer/judge separation, zero holdout access, and bounded search.

## 14. External Primary And Official Sources

Dates below are publication or initial-release dates stated by the source.
Relevance notes distinguish the external result from Chronicle-specific
inferences.

### 14.1 Prompt optimization and DSPy

1. **Omar Khattab et al., "DSPy: Compiling Declarative Language Model Calls
   into Self-Improving Pipelines" (5 October 2023).**
   https://arxiv.org/abs/2310.03714

   Introduces DSPy as a programming and compilation model for optimizing LM
   pipelines against a metric, including creating and collecting
   demonstrations. Relevant as the framework behind Chronicle's
   BootstrapFewShot and GEPA integration. Reported benchmark gains belong to
   the paper's tasks and must not be transferred to Chronicle.

2. **DSPy project, "BootstrapFewShot" API documentation (accessed 13 August
   2026).**
   https://dspy.ai/api/optimizers/BootstrapFewShot/

   Officially describes combining labeled and bootstrapped demonstrations and
   using a metric/threshold to accept generated examples. Relevant to how
   frozen references can supply labels and acceptance targets.

3. **Lakshya A. Agrawal et al., "GEPA: Reflective Prompt Evolution Can
   Outperform Reinforcement Learning" (submitted 25 July 2025; revised 14
   February 2026; accepted ICLR 2026 Oral).**
   https://arxiv.org/abs/2507.19457

   Introduces Genetic-Pareto reflective prompt evolution: trajectory
   reflection, natural-language feedback, prompt mutation, and Pareto search.
   Reports sample-efficiency results on six tasks. Relevant to the hypothesis
   that rich reference-backed diagnostics can be more informative than a scalar
   failure score.

4. **DSPy project, "GEPA: Reflective Prompt Optimizer" API documentation
   (accessed 13 August 2026).**
   https://dspy.ai/api/optimizers/GEPA/overview/

   Officially documents metrics returning score plus textual feedback,
   reflection-model use, Pareto candidate selection, budgets, seeds, and
   checkpoint logging. It supports Chronicle's architecture but does not
   prescribe Chronicle's choice to exclude its fixed judge from feedback.

### 14.2 Teacher-generated data, distillation, and weak supervision

5. **Geoffrey Hinton, Oriol Vinyals, and Jeff Dean, "Distilling the Knowledge
   in a Neural Network" (9 March 2015).**
   https://arxiv.org/abs/1503.02531

   Foundational knowledge-distillation paper: compresses knowledge from a
   cumbersome ensemble into an easier-to-deploy model. Relevant to the economic
   teacher/student analogy; Chronicle currently optimizes prompts rather than
   weights.

6. **Alexander Ratner et al., "Snorkel: Rapid Training Data Creation with Weak
   Supervision" (PVLDB 2017).**
   https://www.vldb.org/pvldb/vol11/p269-ratner.pdf

   Demonstrates creating useful training labels from imperfect supervision
   sources and emphasizes source accuracies, correlations, and lineage.
   Relevant to treating machine-created labels as scalable but imperfect.

7. **Yizhong Wang et al., "Self-Instruct: Aligning Language Models with
   Self-Generated Instructions" (ACL, July 2023).**
   https://aclanthology.org/2023.acl-long.754/

   Generates instruction/input/output samples, filters invalid or similar
   examples, and reuses them for instruction tuning. Relevant to the
   generate-filter-reuse pattern. Chronicle does not use self-generated inputs
   or fine-tune weights.

8. **Cheng-Yu Hsieh et al., "Distilling Step-by-Step! Outperforming Larger
   Language Models with Less Training Data and Smaller Model Sizes" (Findings
   of ACL, July 2023).**
   https://aclanthology.org/2023.findings-acl.507/

   Uses LLM-generated labels and rationales as additional supervision for
   smaller models and reports data-efficiency improvements on four NLP
   benchmarks. Relevant evidence that strong-model supervision can reduce data
   requirements in some settings; Chronicle does not store or transfer hidden
   chain-of-thought rationales.

9. **Jay Mohta, Kenan Ak, Yan Xu, and Mingwei Shen, "Are large language models
   good annotators?" (NeurIPS 2023 Workshop / PMLR 239, December 2023).**
   https://proceedings.mlr.press/v239/mohta23a.html

   Finds that models trained with human labels consistently outperformed those
   trained with LLM-generated labels in the studied tasks and identifies
   multilingual limitations. Relevant counterweight to claims that a strong
   teacher removes the need for human labels.

### 14.3 Reference-based evaluation and judging

10. **Tianyi Zhang et al., "BERTScore: Evaluating Text Generation with BERT"
    (submitted 21 April 2019; ICLR 2020).**
    https://arxiv.org/abs/1904.09675

    Compares candidate and reference tokens using contextual embeddings and
    reports stronger correlation/model selection than prior metrics on its
    evaluated tasks. Relevant to semantic reference comparison, with the caveat
    that similarity is not application correctness.

11. **Daniel Deutsch, Rotem Dror, and Dan Roth, "On the Limitations of
    Reference-Free Evaluations of Generated Text" (EMNLP, December 2022).**
    https://aclanthology.org/2022.emnlp-main.753/

    Shows limitations and generator-similarity bias in reference-free metrics.
    Relevant to keeping references and using reference-free methods as
    diagnostics rather than sole progress measures.

12. **Lianmin Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot
    Arena" (NeurIPS 2023).**
    https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html

    Reports strong agreement between a capable LLM judge and human preferences
    while documenting position, verbosity, self-enhancement, and reasoning
    biases. Relevant to Chronicle's decision to use a fixed judge as a separate
    scalable lens rather than optimization ground truth.

### 14.4 Holdout and selection bias

13. **Gavin C. Cawley and Nicola L. C. Talbot, "On Over-fitting in Model
    Selection and Subsequent Selection Bias in Performance Evaluation" (JMLR,
    2010).**
    https://jmlr.org/papers/v11/cawley10a.html

    Shows that optimizing a model-selection criterion over finite data can
    overfit the criterion and bias later performance estimates. This is not an
    LLM-specific paper; its general result directly motivates Chronicle's
    sealed holdout and bounded prompt search.

## 15. Bottom Line For The Future Article

The defensible story is not "a strong model gives you ground truth cheaply."
It is:

> A strong teacher can create a versioned silver reference set once. If the
> task has strict contracts and evidence rules, that set becomes a reusable
> development asset: cheap checks can reject broken outputs and provide useful
> prompt-optimization feedback, while expensive judging is reserved for a
> shortlist. The marginal economics improve with each additional prompt
> candidate, but the teacher's errors, privacy risk, and development overfitting
> scale just as efficiently. That is why provenance, leakage checks, and a
> sealed holdout are part of the method, not administrative overhead.

This framing is useful whether GEPA eventually improves the prompts or produces
a negative result. The reusable-reference architecture can save repeated work;
the holdout determines whether the optimized prompt learned the task rather
than merely learning the answer key.
