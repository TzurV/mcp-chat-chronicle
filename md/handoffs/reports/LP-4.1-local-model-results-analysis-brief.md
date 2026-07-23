# LP-4.1 Local-Model Results Analysis Brief

## Status

Owner-approved interpretation direction recorded on 2026-07-23 after the required discussion
cycle. This brief is analysis and editorial planning only. It authorizes no publication, no final
article copy, and no publication graphics. It remains unstaged and uncommitted until the
development manager validates and the owner explicitly requests commit.

Evidence basis: the accepted WP-5.2B1.4 completion report and validation review
(complete Gemini-120, Qwen-120, and Llama-120 arms plus the Qwen-40 operational checkpoint),
with WP-5.2B1.2/B1.3 as accepted pilot history. No raw conversations, candidate outputs, FABLE
references, judge rationales, private paths, IDs, or account/project data were inspected.

## 1. Evidence boundary and terminology

- This is a **bounded development comparison** on the owner's real-work frozen corpus
  (30 conversations, 4 tasks, 120 cases per arm). It is not a leaderboard, not statistically
  generalizable, and not a scientific evaluation.
- **Gemini 3.5 Flash (Vertex) is the cloud control / strong hosted baseline / practical quality
  ceiling.** It is never called ground truth: it produced 8 invalid outputs itself, and 2 of its
  eligible outputs have terminal judge failures.
- **FABLE references are silver development references**, not human-adjudicated gold labels.
  "Exact agreement" means agreement with FABLE, not correctness.
- **The judge is Gemini 3.1 Pro Preview** (rubric v1, temperature 0, blinded candidate identity).
  Same-family/provider bias is possible and preliminary observations reinforce previously
  reported same-family judge bias (see section 3, observation 6). Three eligible results retain
  terminal judge failures and are never converted to scores.
- Four measurement layers are kept separate throughout: **product reliability** (schema-valid /
  120), **deterministic agreement** (exact match vs FABLE, /30 per task), **semantic quality**
  (judge means over successfully judged valid outputs only), and **operational performance**
  (latency, wall span, tokens). Every percentage or mean carries its denominator.
- Local arms ran on a privacy-safe machine class: 4-core/8-thread 11th-gen Intel mobile CPU,
  ~32 GiB RAM, integrated Iris Xe graphics, LM Studio, context 8,192, parallelism 1. Hosted
  latency is not directly comparable with single-worker local inference.

## 2. Current model scorecard

Primary evidence: complete 30-conversation / 120-case arms.

| Measure | Gemini 3.5 Flash (cloud control) | Qwen3.5-4B Q4_K_M (local control) | Llama 3.2 1B Q4_K_M (local floor) |
|---|---:|---:|---:|
| Schema-valid | 112/120 (93.3%) | 84/120 (70.0%) | 57/120 (47.5%) |
| Dominant failure modes | invalid JSON 6, provider 1, schema 1 | context length 29, timeout 5, schema 2 | context 21, evidence 16, schema 15, HTTP 10, JSON 1 |
| Exact agreement: work mode / last activity / title fit (n=30 each) | 63.3% / 70.0% / 83.3% | 33.3% / 60.0% / 56.7% | 3.3% / 20.0% / 6.7% |
| Task validity: summary / mode / activity / title (n=30 each) | 23 / 30 / 29 / 30 | 17 / 19 / 30 / 18 | 16 / 20 / 14 / 7 |
| Judge quality of valid outputs (macro, normalized 0-1) | ~0.97 | ~0.89 | ~0.51 |
| **Usable Task Score (estimate, 0-100)** | **~88** | **~62** | **~22** |
| Candidate latency p50 / p95 | 2.156s / 12.562s (n=120) | 62.094s / 168.375s (n=120) | 17.312s / 53.609s (n=120) |
| Observed wall span (120 cases) | 10m 40s | 4h 43m 31s | 42m 13s |

UTS values are estimates computed from the tracked task-level judge-dimension means (section 6);
the exact per-case computation requires the private aggregates and should be reproduced before
any publication use. Qwen-40 remains an operational checkpoint, not a fourth complete arm.

## 3. Main observations

Each with metric, denominator, caveat, and confidence.

1. **Structured-output reliability is the first-order product metric, and it is where local
   models lose.** 93.3% vs 70.0% vs 47.5% schema-valid over the same 120 cases. Caveat: one
   quantization, one runtime, one prompt strategy, one laptop, context 8,192. Confidence: high.

2. **When the mid-size local model succeeds, output quality is roughly at cloud-control level —
   but it succeeds only 70% of the time.** Qwen judged summary and title dimensions were 4.00
   across the board (n=17, n=18); Gemini's were 3.95-4.00 (n=22, n=30). Survivorship warning:
   these means describe surviving cases only and must never be presented as whole-product
   quality; 36/120 Qwen positions produced nothing consumable. Confidence: high on the pattern,
   subject to the same-family judge caveat.

3. **Qwen's failures are dominated by context capacity, not model capability.** 29 of 36 Qwen
   failures were context-length terminations at the configured 8,192-token window. The three
   tasks fed by the full conversation-overview selector (max 50,000 input chars, roughly 12-14K
   tokens) each lost 11-13 cases; the one task with a smaller selector (last-activity, 24,000
   chars / 12 recent messages) went 30/30 valid. The 50K-char budget arithmetically cannot fit
   an 8K window for long conversations. Caveat: the selector contrast is confounded (different
   task, not only different input size), and the accepted arm must not be reinterpreted post
   hoc — the controlled test is the approved follow-up context-expansion arm (section 14).
   Llama is different: beyond 21 context failures, 31 evidence/schema failures are genuine
   capability failures. Confidence: medium-high, framed as strongly supported hypothesis.

4. **Work-mode classification is the semantically hardest task for every model, including the
   cloud control.** Exact agreement 63.3% / 33.3% / 3.3% (n=30 each); it is also every model's
   weakest judge area (label support 3.60 / 2.58 / 1.58 over 30/19/19 judged cases). Mandatory
   caveat: reference support is skewed (executor 14, one-off 12, manager 3, mixed 1) and
   `mixed` was never correctly predicted by any model. Confidence: high that it is hardest;
   the imbalance caveat always travels with the claim.

5. **Task difficulty is model-dependent; there is no universal easiest-to-hardest ranking.**
   Summary was the cloud control's weakest structural task (23/30 valid; 7 of its 8 failures),
   Qwen's weak tasks were the big-context ones (17-19/30), and Llama's was title assessment
   (7/30). The 1B model was ~3.6x faster than Qwen per case but too unreliable for these
   contracts; larger local parameter count bought quality-when-valid, not speed. Confidence:
   high as observation; routing decisions wait for the full candidate set.

6. **Judge-vs-reference disagreement is consistent with same-family judge self-preference.**
   On title fit the Pro judge scored Gemini's title-fits correctness 4.00 (n=30) while FABLE
   exact agreement was 83.3% (5 disagreements, all FABLE=true / Gemini=false); the judge sided
   with the same-family candidate in every disagreement. The current evidence cannot separate
   judge bias from silver-label error; preliminary observations reinforce previously reported
   same-family (Gemini-judging-Gemini) bias. Owner adjudication of disagreement cases is
   recorded as backlog (section 14). Confidence: the discrepancy itself is certain; its cause
   is deliberately left open in public language.

## 4. Task-difficulty analysis

Three separate axes; a single combined "difficulty" number is intentionally not produced.

- **Structural difficulty** (can the model return consumable schema-valid output);
- **Semantic difficulty** (agreement with reference and judge scores);
- **Operational difficulty** (context pressure, output budget, latency).

Task-by-model interpretation (denominator 30 cases per cell; agreement is exact-vs-FABLE;
judge means are over successfully judged valid outputs only):

| Task | Gemini (cloud control) | Qwen3.5-4B | Llama 3.2 1B | Reading |
|---|---|---|---|---|
| Summary | 23/30 valid; judge ~3.98 (n=22) | 17/30 valid; judge 4.00 (n=17) | 16/30 valid; judge ~3.09 (n=16) | Structurally hardest overall: material-selection and context pressure hit every model; the cloud control's only real failure mode (invalid JSON) concentrates here. |
| Work mode | 30/30 valid; 63.3% agree; label support 3.60 (n=30) | 19/30 valid; 33.3% agree; 2.58 (n=19) | 20/30 valid; 3.3% agree; 1.58 (n=19) | Semantically hardest for everyone; manager/executor/mixed/one-off boundaries are fuzzy and reference support is skewed. |
| Last activity | 29/30 valid; 70.0% agree; ~3.94 (n=28) | 30/30 valid; 60.0% agree; ~3.67 (n=30), next-action support 2.90 | 14/30 valid; 20.0% agree; ~2.11 (n=14) | Comparatively suitable for Qwen: the smaller recent-meaningful selector fits the 8K window; its residual weakness is next-action support. |
| Title | 30/30 valid; 83.3% agree; ~3.97 (n=30) | 18/30 valid; 56.7% agree; 4.00 (n=18) | 7/30 valid; 6.7% agree; ~2.97 (n=7) | Easy for the cloud control; for locals it inherits full-overview context pressure; structurally and semantically hardest for the 1B floor. |

## 5. Task-routing options

Assessed for a practical product configuration. The task catalog already assigns
`model_profile` per task, so static routing is a configuration change, not new architecture.

| Option | Expected benefit | Operational complexity | Privacy / cost trade-off | Failure detection needed | Evidence sufficient now? |
|---|---|---|---|---|---|
| One model for all tasks | Simplest ops; one artifact loaded | Lowest | Fully local possible; quality cost on weak tasks | None beyond existing schema validation | Yes for ranking the three tested arms; no for final choice (2 candidates outstanding at qualification, 3 total incoming) |
| Best local model per task (static routing) | Captures model-dependent task fit (e.g. Qwen 30/30 + 60% agreement on last-activity) | Low-moderate: YAML per-task profiles exist; multi-model load/swap on a 32 GiB iGPU laptop favors sequential batch passes | Fully local; more disk/RAM churn | None beyond existing validation | No — wait for the five-candidate matrix |
| Local-first, cloud fallback on invalid output | Recovers most of the reliability gap at low cloud volume (Qwen would have escalated ~30% of cases) | Moderate: routing logic simple because schema validation is already the gate | "Local by default" gains an asterisk; per-case cloud cost on escalations | Already built (schema/evidence/cross-field validation) | Architecture defensible now; escalation-rate numbers per model need full matrix |
| Reliability threshold for task admission (e.g. a model must reach X% valid on a task before enrichment uses it) | Prevents shipping unusable enrichment; principled gate | Low: an offline decision, not runtime machinery | None | None | Yes as policy concept; thresholds set after full matrix |

Recommendation for the article: present routing as design discussion with the task-by-model
matrix as evidence, state that the configuration was built for it, and defer concrete
assignments until WP-5.2A5.1/B2 results are added. Confidence-based routing is future work
only; no calibration evidence exists.

## 6. Composite-score formulas and sensitivity

**Usable Task Score (UTS), 0-100 — evaluated and adopted as a secondary communication metric.**

Definition: per case, score 0 when the candidate output is invalid, absent, or has no completed
judge result; otherwise the mean of the applicable rubric dimensions normalized from the 1-4
judge scale to 0-1 via `(score - 1) / 3`; average cases within each task (denominator always
30); macro-average the four tasks; multiply by 100. Latency is never combined into UTS; speed
stays a separate axis.

Normalization rationale (owner-approved): a judged "1" on this rubric means the output is
wrong; `(s-1)/3` gives it 0 credit, whereas `s/4` would give 0.25 credit for a wrong answer.

Estimated task scores from the tracked task-level dimension means (0-1 before x100):

| Task score | Gemini | Qwen | Llama |
|---|---:|---:|---:|
| Summary | 0.729 (22 judged/30) | 0.567 (17/30) | 0.371 (16/30) |
| Work mode | 0.900 (30/30) | 0.417 (19/30) | 0.200 (19/30) |
| Last activity | 0.915 (28/30) | 0.891 (30/30) | 0.172 (14/30) |
| Title | 0.991 (30/30) | 0.600 (18/30) | 0.153 (7/30) |
| **UTS (macro x100)** | **~88** | **~62** | **~22** |

These use task-level means as a proxy for per-case averaging; reproduce exactly from private
aggregates before publication.

Alternatives compared:

- **Reliability-adjusted judge mean** (valid rate x normalized valid-output judge macro-mean):
  Gemini ~0.90, Qwen ~0.62, Llama ~0.24.
- **Geometric combination** sqrt(reliability x quality): ~0.95 / ~0.79 / ~0.49.
- **No composite** (two-axis reliability-vs-quality chart): retained as the *primary* visual
  regardless of UTS adoption.

Sensitivity results:

- **Ranking never changes** across UTS, the reliability-adjusted mean, geometric/harmonic
  combinations, or the `s/4` normalization variant (which shifts all values up: ~89/~64/~28).
  The gaps are too large to flip.
- **Equal-task vs equal-case weighting are identical by construction** here: all four tasks
  have exactly 30 cases, so the macro and micro averages coincide.
- **Judge-failure treatment:** the three terminal judge failures (2 Gemini, 1 Llama) score 0.
  Excluding them instead would move Gemini by roughly +1.4 UTS points and Llama by well under
  a point; scoring them 0 is conservative against the cloud control, which is the right
  direction given the same-family judge concern.

Decision: **two-axis chart primary, UTS secondary**, always presented with its three-line
definition and the statement that it is a policy choice, not a scientific truth. Its
defensibility rests on the demonstrated formula-insensitivity of the ranking.

## 7. Recommended public metric subset

Owner-approved minimal set for the article:

1. Schema-valid rate per model (n=120 each), with the failure-category decomposition;
2. Task x model validity matrix (12 cells, n=30 each);
3. Exact agreement vs FABLE for the three categorical tasks (n=30 each), labeled as
   agreement with silver references, not correctness;
4. One judged-quality figure for valid outputs (macro normalized judge mean), always paired
   with the valid-rate so survivorship is visible;
5. UTS as the single secondary composite;
6. Operational table kept separate: candidate latency p50 (p95 in appendix), observed wall
   span, and the privacy-safe hardware/runtime description.

Private appendix (not published, retained): full confusion matrices, per-label
precision/recall/support, per-dimension judge means, token accounting, per-task latency,
Qwen-40 checkpoint detail.

Explicitly acceptable to publish (owner-confirmed): the 4h 43m Qwen-120 wall span on the
laptop — treated as a credibility asset, clearly bound to the exact hardware class and
single-worker configuration.

## 8. Article narrative options

Owner decision: **hybrid — narrative A as the spine with narrative B's task-difficulty matrix
as the centerpiece.**

- **Narrative A (spine) — "The reliability gap: demo quality vs product quality."** Hook: the
  best local outputs were indistinguishable from cloud — the problem is the other 30%. Arc:
  four real product tasks with strict output contracts → cloud control sets the bar → every
  case counts, not just the best answers → survivorship correction → scorecard/UTS → why the
  gap is partly an input-budget engineering problem → what's next (more candidates, context
  study, prompt study).
- **Narrative B (centerpiece, absorbed) — "No single winner: which tasks can a small local
  model be trusted with?"** The task x model matrix, three difficulty axes, Qwen's 30/30
  last-activity result as the routing proof-of-concept, local-first-with-fallback as the
  practical architecture. Full routing conclusions deferred to the complete candidate set.

Headline/title options (owner to select at publication time):

1. "I benchmarked local SLMs on 120 real work tasks. The best outputs matched cloud quality —
   70% of the time."
2. "The reliability gap: what happens when local LLMs meet strict output contracts on real
   work."
3. (Existing master-plan candidate) "I benchmarked 5 local SLMs on my own laptop for real
   work. Results surprised me."

**Short post version** (LinkedIn-native, ~300 words): hook → one scorecard visual → three
findings (reliability gap, survivorship, task-dependence) → honest-methodology line → question
CTA → repo link in first comment.

**Longer technical article outline** (dev.to/blog): 1) the product and its four AI tasks;
2) methodology — frozen real-work corpus, silver references, fixed blinded judge, immutable
packages, what this is not; 3) the reliability gap (chart 1); 4) survivorship — why averaging
only successes lies; 5) the task x model matrix (centerpiece); 6) the context-budget finding;
7) speed and operations (chart 2, wall spans, hardware); 8) UTS — one number, three lines,
policy not truth; 9) routing as architecture discussion; 10) limitations incl. judge-bias
observation; 11) what's next: remaining candidates, context expansion, prompt study; 12) CTA.

## 9. Visual concepts

Three candidates, all from privacy-safe aggregate data only; no final graphics before owner
approval:

1. **Reliability x quality two-axis chart (primary).** X = schema-valid rate (n=120); Y =
   normalized judge quality of valid outputs; point size or annotation = number of valid
   outputs. Shows the survivorship story in one frame: Qwen sits high on quality, left on
   reliability.
2. **Latency x UTS operational chart.** X = per-case p50 latency, log scale (2.2s → 62s);
   Y = UTS; each point annotated with observed 120-case wall span (10m40s / 42m13s / 4h43m31s).
   Log scale is mandatory given the ~30x spread.
3. **Task x model matrix (centerpiece).** 4 tasks x N models; each cell shows valid count /30
   and exact agreement where applicable; color by validity band. Designed to absorb the three
   incoming candidates as new columns without redesign.

## 10. Limitations and prohibited claims

Must-state limitations:

- Bounded development comparison on one owner's 30-conversation frozen corpus; not
  generalizable, not a leaderboard.
- FABLE references are silver; exact agreement measures reference agreement, not correctness.
- The judge is a same-provider preview model; three judge results remain terminal failures;
  the title-fit discrepancy is consistent with previously reported same-family judge bias and
  has not yet been human-adjudicated.
- One quantization (Q4_K_M), one runtime (LM Studio), one context policy (8,192), one prompt
  strategy, one laptop class; hosted latency is not comparable with single-worker local
  inference; token counts are not cross-provider comparable.
- Development-set reuse: all 120 cases are development data; nothing here is an untouched
  evaluation set.

Claims the evidence does not support (prohibited):

- Any "ground truth" or "objective accuracy" framing for Gemini or FABLE;
- Statistical significance, generalization to other users/corpora/hardware, or model-family
  superiority claims;
- Presenting valid-output judge means as whole-product quality (survivorship);
- Presenting UTS as anything other than a defined policy metric;
- Concluding that context expansion *will* fix Qwen's reliability (approved follow-up measures
  this; today it is arithmetic-supported hypothesis);
- Attributing the title-fit discrepancy definitively to judge bias (or definitively to label
  error) before adjudication;
- Final routing recommendations before the complete candidate matrix;
- Any per-conversation content, title, ID, or private path.

## 11. Placeholders for incoming models

WP-5.2A5.1 qualifies (in sequence): **Phi-4 Mini Instruct**, **Llama 3.2 3B Instruct**,
**Gemma 4 E2B Instruct** (or approved Gemma 3 4B IT fallback). Baseline policy for all
incoming arms is unchanged: context 8,192, parallelism 1, accepted prompts/schemas/settings,
fixed Pro rubric-v1 judge (owner-confirmed 2026-07-23; the larger-context study is a separate
follow-up arm, section 14).

Every scorecard, matrix, chart, and the UTS table in this brief is designed to add columns
without structural change. Article placeholder slots: scorecard rows, matrix columns, two
chart points each, plus one narrative beat reserved in the spine ("did a 3B-class model close
the reliability gap?"). The article is not drafted, and LP-4 is not published, before every
retained local candidate completes the 120-case run (WP-5.2B2 gate).

## 12. Owner decisions still required

Resolved 2026-07-23: interpretation direction (headline findings 1-6); UTS adopted as
secondary with `(s-1)/3` normalization and judge-failures-score-0; hybrid narrative; public
metric subset (incl. publishing the Qwen wall span); baseline context stays 8,192 for all five
candidates; context study moves to follow-up (optionally remote); judge adjudication to
backlog; framework-now-placeholders-later posture.

Still open (decision needed at or after WP-5.2B2 results):

1. Final headline/title selection (three options in section 8);
2. Publication timing after the WP-5.2B2 gate clears;
3. Final freeze of the public metric subset against the five-model results;
4. Whether the judge-adjudication backlog item runs before the article (strengthens the bias
   discussion) or after;
5. Short post only vs short post + long-form technical article, and their sequencing;
6. Final visual selection and styling (concepts in section 9);
7. Whether Qwen-40 checkpoint data appears anywhere public (default: no).

## 13. Prompt-tuning follow-up proposal (backlog; not part of the baseline)

Proposed design, to run only after all baseline candidate arms complete and with separate
owner approval (maps to WP-5.2B3):

1. Select the best one or two **local** models by task and overall usable reliability from the
   completed five-candidate matrix;
2. Retain Gemini-120 unchanged as the cloud control target;
3. Compare a small number of versioned prompt strategies: the accepted zero-shot baseline, a
   concise schema-first variant, and bounded task-specific few-shot variants;
4. No chain-of-thought is requested or published;
5. Within each prompt study, hold context, model artifact, generation settings, inputs,
   references, and fixed-Pro scoring constant; version every prompt/model identity;
6. Run on the current development set and label all gains as prompt-development results
   (overfitting risk disclosed);
7. Freeze the selected prompt before any later untouched evaluation set;
8. Report separately whether tuning closes reliability gaps, semantic gaps, or task-specific
   gaps — not one blended delta.

This analysis thread proposes the design only and does not execute it.

## 14. Additional follow-ups recorded from the analysis discussion (owner-approved direction)

1. **Context-expansion study (new arm, not a reinterpretation).** Keep 8,192 for all five
   baseline arms for comparability. Afterwards, run the best one or two local models as new,
   separately authorized arms with an up-front larger context policy (16K first; verify each
   pinned artifact's advertised maximum — family-advertised values: Llama 3.2 128K, Qwen3-class
   4B 32K native, Phi-4 Mini 128K, Gemma 3 4B 128K). Directly tests observation 3. Planning
   caveat: the recovered cases are the long ones, so laptop wall time will rise materially.
2. **Remote stronger-machine execution (WP-5.2C shape).** Use the existing split-generation /
   portable-package / local-scoring path. Natural first remote workload: the context-expansion
   arm. Remote performance claims must remain strictly separated from laptop claims. Subset
   selection based on the current findings is the intended scope.
3. **Owner adjudication of judge-vs-FABLE disagreement cases (backlog).** Locally and
   privately adjudicate at minimum the five title-fit disagreements (optionally work-mode
   disagreements) to convert silver to gold exactly where the same-family-bias question sits.
   Until executed, public language stays: "consistent with previously reported same-family
   judge bias; not yet human-adjudicated."
4. **Judge-instruction tightening (rubric v2) — backlog only.** Any rubric change takes a new
   version and requires re-judging every candidate for comparability; do not change rubric v1
   during the baseline program.
