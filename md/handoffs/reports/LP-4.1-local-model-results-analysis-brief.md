# LP-4.1 Local-Model Results Analysis Brief

## Status

Ready for PM validation.

Revised on 2026-07-24 with the complete six-arm evidence after the owner approved the updated
interpretation direction in the LP-4.1 continuation discussion. The provisional three-arm
version was accepted by the PM on 2026-07-23; this revision replaces its provisional scorecard,
estimated composite values, and incoming-model placeholders with exact complete-arm results.

This brief is analysis and editorial planning only. It authorizes no publication, no final
article copy, and no publication graphics. It remains unstaged and uncommitted until the
development manager validates and the owner explicitly requests commit.

Evidence basis: the accepted WP-5.2B1.4 and WP-5.2B2.2 completion reports and validation
reviews (complete Gemini-120, Qwen-120, Phi-120, Llama-3B-120, Gemma-120, and Llama-1B-120
arms; the Qwen-40 and WP-5.2B2.1 checkpoints remain operational history). Exact composite
values were reproduced from accepted private per-case aggregates under ignored
`.chronicle/eval/dev-v1/` paths, read-only, with a privacy-safe calculation manifest retained at
`.chronicle/eval/dev-v1/tmp/lp41-uts/uts-calculation-manifest.json`. No raw conversations,
titles, source text, candidate text, FABLE prose, judge rationales, private IDs, credentials,
or cloud account/project data were inspected or quoted.

## 1. Evidence boundary and terminology

- This is a **bounded development comparison** on the owner's real-work frozen corpus
  (30 conversations, 4 tasks, 120 common cases per arm; 720 candidate positions total, all
  terminal). It is not a leaderboard, not statistically representative, and not an independent
  or scientific evaluation.
- The comparison is **five local models plus one cloud control**, not six equivalent
  deployment candidates. **Gemini 3.5 Flash (Vertex) is the cloud control / strong hosted
  baseline / practical quality ceiling.** It is never called ground truth: it produced 8
  invalid outputs itself and 2 of its eligible outputs retain terminal judge failures.
- **FABLE references are silver development references**, not human-adjudicated gold labels.
  "Exact agreement" means agreement with FABLE, not accuracy.
- **The judge is Gemini 3.1 Pro Preview** (rubric v1, temperature 0, blinded candidate
  identity), same provider/model family as the Gemini candidate. Observed judge/reference
  disagreement is **compatible with same-family preference but does not establish bias**
  (see section 3, observation 7). Five eligible results across all arms retain terminal judge
  failures and are never converted to scores.
- Four measurement layers are kept separate throughout: **product reliability** (schema-valid
  /120), **deterministic agreement** (exact match vs FABLE, /30 per task), **semantic quality**
  (quality among successfully judged valid outputs only — never whole-model quality), and
  **operational performance** (latency, wall span, tokens). Every percentage or mean carries
  its denominator.
- All local arms shared one contract: LM Studio (CLI commit `9902c3a`, llama.cpp Vulkan AVX2
  engine 2.25.2 for the WP-5.2B2.2 arms), Q4_K_M artifacts, context 8,192, parallelism 1,
  temperature 0, on a privacy-safe machine class of a 4-core/8-thread 11th-gen Intel mobile
  CPU, ~32 GiB RAM, integrated Iris Xe graphics. Hosted latency is not directly comparable
  with single-worker local inference.

## 2. Current model scorecard (complete six-arm evidence)

| Measure | Gemini 3.5 Flash (cloud control) | Qwen3.5-4B | Phi-4 Mini | Llama 3.2 3B | Gemma 3 4B | Llama 3.2 1B (floor) |
|---|---:|---:|---:|---:|---:|---:|
| Schema-valid /120 | 112 (93.3%) | 84 (70.0%) | 77 (64.2%) | 71 (59.2%) | 62 (51.7%) | 57 (47.5%) |
| Dominant failure modes | invalid JSON 6, provider 1, schema 1 | context 29, timeout 5, schema 2 | context 21, schema 12, timeout 10 | context 21, evidence 15, timeout 10, schema 3 | context 30, schema 24, evidence 2, other 2 | context 21, evidence 16, schema 15, HTTP 10, JSON 1 |
| Task validity: summary/mode/activity/title (n=30 each) | 23/30/29/30 | 17/19/30/18 | 14/18/29/16 | 12/19/23/17 | 12/19/25/6 | 16/20/14/7 |
| Exact agreement: mode / activity / title fit (n=30 each) | 63.3 / 70.0 / 83.3% | 33.3 / 60.0 / 56.7% | 10.0 / 60.0 / 16.7% | 10.0 / 40.0 / 43.3% | 16.7 / 46.7 / 10.0% | 3.3 / 20.0 / 6.7% |
| Quality among judged valid outputs (macro, 0-1) | 0.966 | 0.887 | 0.780 | 0.755 | 0.797 | 0.509 |
| **Usable Task Score (exact, 0-100)** | **88.4** | **61.9** | **50.0** | **41.9** | **40.5** | **22.4** |
| Judge completed / eligible | 110/112 | 84/84 | 77/77 | 69/71 | 62/62 | 56/57 |
| Candidate latency p50 / p95 | 2.156s / 12.562s | 62.094s / 168.375s | 54.608s / 180.031s | 51.124s / 180.061s | 61.834s / 156.592s | 17.312s / 53.609s |
| Observed 120-case wall span | 10m 40s | 4h 43m 31s (see decomposition below) | 2h 18m 51s | 2h 21m 16s | 2h 08m 13s | 42m 13s |

**Qwen wall-span decomposition (from accepted per-case attempt evidence, n=120):** 29 context
failures fail fast (mean 1.8s, 53s total); 84 successes mean 85.8s (~2h 00m); 2 schema
failures 172s; 5 timeouts sum 2h 39m, including a single 8,857s (~2h 28m) case consistent
with the recorded in-window overnight wrapper interruption. Excluding the five timeout cases,
Qwen's summed latency (~2h 04m) is comparable to the other 4B-class arms. The raw 4h 43m
figure must never be published without this decomposition. Per-case speed clusters by class,
not by model: all 3-4B arms sit at p50 51-62s.

Gemma is treated as a weak research comparator under these contracts (WP-5.2B2.2 language),
not a product-quality endorsement; the owner will review this framing in the article draft.

## 3. Main observations

Each with metric, denominator, caveat, confidence, and public/appendix placement.

1. **Structured-output reliability is the first-order product metric, and no local model
   reaches three-in-four.** Cloud control 93.3% vs local 70.0 / 64.2 / 59.2 / 51.7 / 47.5%
   (n=120 each). Caveat: one Q4_K_M quantization, one runtime, fixed 8,192-token contract,
   one prompt strategy, one laptop class. Confidence: high. **Public.**

2. **Quality-among-valid and whole-package reliability rank differently — survivorship is the
   trap.** Gemma's judged valid outputs score better than Phi's (0.797 vs 0.780 macro
   normalized) despite 12.5 points lower reliability; Qwen's valid summaries and titles judged
   at or near ceiling. A quality average over survivors must never be presented as whole-model
   quality; UTS's zero-for-invalid rule is the correction. Caveat: per-task judged n ranges
   6-30; same-provider preview judge. Confidence: high. **Public** (the article's
   methodological core).

3. **Qwen3.5-4B is the best local model on every one of the four tasks.** Task-level UTS:
   summary 56.7 vs next-best-local 39.1; work mode 41.7 vs 37.2; last activity 89.1 vs 77.8;
   title 60.0 vs 54.2 (all n=30). It also leads or ties every deterministic agreement metric.
   Parameter count does not predict this ordering: Gemma 3 4B trails Llama 3.2 3B on
   reliability (51.7% vs 59.2%, n=120). Caveat: bounded development comparison, one prompt
   strategy; some margins modest. Confidence: high within this contract. **Public.**

4. **The fixed 8,192-token contract sets a common failure floor; model-specific failure modes
   differentiate above it.** Context-length failures span 21-30 per local arm (n=120), but
   composition differs sharply: Qwen's failures are 81% context (29/36); Gemma adds 24 schema
   failures concentrated in title assessment (24 of 30 title cases rejected); Phi and Llama 3B
   each add 10 timeouts; Llama 3B adds 15 evidence failures. Two remedies exist and both stay
   hypotheses until measured: growing the window (follow-up arm, section 14) and right-sizing
   inputs (already supported: the small-selector task went 30/30, 29/30, 25/30, 23/30 valid
   for Qwen/Phi/Gemma/Llama-3B). Caveat: never claim context expansion will fix a model.
   Confidence: high on the decomposition. **Public.**

5. **Local wall-clock is dominated by tails and contract interactions, not average speed —
   and speed claims must be workload-shaped.** All 3-4B arms cluster at p50 51-62s (n=120
   each); the Qwen span decomposition (section 2) shows the headline gap was a timeout-tail
   artifact. Product framing on the owner's real 711-conversation archive: full backfill
   ≈ 2,850 cases x ~86s ≈ 2.8 days of continuous laptop compute (impractical); incremental
   daily enrichment ≈ minutes per day (acceptable); interactive use (2s budget) is out of
   reach by ~30x. Caveat: single-worker execution, one laptop class; spans include in-window
   interruption by definition. Confidence: high (reproduced per-case). **Public in decomposed,
   workload-shaped form; raw span alone is prohibited.**

6. **The fast floor model has no credible role for these contracts.** Llama 1B is ~3x faster
   than the 4B class (p50 17.3s, n=120) at UTS 22.4 with 0.509 valid-output quality — fast
   wrong answers are still wrong. Confidence: high. **Public one-liner; detail in appendix.**

7. **Judge/reference disagreement observation (parked).** On title fit the Pro judge scored
   the Gemini candidate's title-fits correctness 4.00 (n=30) while FABLE exact agreement was
   83.3% (all 5 disagreements FABLE=true / candidate=false). This is compatible with
   same-family preference but does not establish bias; it is equally compatible with silver
   reference error. The owner may do further work here (sourcing and/or local adjudication of
   the disagreement cases) before publication; until then the article uses only the qualified
   wording. Confidence: the discrepancy is exact; its cause is undetermined. **Limitations
   section, not a headline.**

## 4. Task-difficulty analysis

Three separate axes; no single combined difficulty number.

- **Structural** (schema-valid output rate and failure boundary);
- **Semantic** (FABLE agreement and fixed-Pro dimensions over judged valid outputs);
- **Operational** (context pressure, timeout, output budget, latency).

Six-model interpretation (denominator 30 cases per cell):

| Task | Cloud control | Qwen | Phi | Llama 3B | Gemma | Llama 1B | Reading |
|---|---|---|---|---|---|---|---|
| Summary (task UTS) | 23/30; 72.9 | 17/30; 56.7 | 14/30; 39.1 | 12/30; 37.1 | 12/30; 38.7 | 16/30; 37.1 | Structurally hardest overall; full-overview selector (~12-14K tokens) cannot fit the 8K local window on long conversations; also the cloud control's only weak spot (7 of its 8 failures). |
| Work mode (task UTS) | 30/30; 63.3% agree; 90.0 | 19/30; 33.3%; 41.7 | 18/30; 10.0%; 37.2 | 19/30; 10.0%; 28.9 | 19/30; 16.7%; 30.6 | 20/30; 3.3%; 20.0 | Semantically hardest for all six arms. Distinct per-model failure shapes: Llama 3B never predicted `executor` (0 predictions, support 14); Phi funnels into `mixed`; Gemma over-predicts `manager`. Reference support is skewed (executor 14, one-off 12, manager 3, mixed 1); `mixed` was never correctly predicted by any model. |
| Last activity (task UTS) | 29/30; 70.0%; 91.5 | 30/30; 60.0%; 89.1 | 29/30; 60.0%; 77.8 | 23/30; 40.0%; 47.4 | 25/30; 46.7%; 76.3 | 14/30; 20.0%; 17.2 | The local sweet spot, generalized across models: the recent-meaningful selector (~6-7K tokens) fits the window. Local semantic weakness concentrates in next-action support (2.4-2.9 means). Llama 1B's collapse here is capability, not context. |
| Title (task UTS) | 30/30; 83.3%; 99.1 | 18/30; 56.7%; 60.0 | 16/30; 16.7%; 45.8 | 17/30; 43.3%; 54.2 | 6/30; 10.0%; 16.4 | 7/30; 6.7%; 15.3 | The great separator, with opposite failure classes on the same task: Gemma's failure is structural (24 schema rejections, 6/30 valid); Phi's is semantic (10 true→false inversions among valid outputs). Easy only for the cloud control. |

Provisional hypotheses from the three-arm brief, tested against six arms: work-mode-hardest
**confirmed**; last-activity suitability for Qwen **confirmed and generalized** (Phi ties its
60% agreement); title separating Qwen/Llama-3B from Phi/Gemma/1B **broadly confirmed** (Phi
lands between the groups); summary as context/material-selection constrained **confirmed**;
model-dependent difficulty **confirmed**; context-explains-some-but-not-all **confirmed**
(finding 4).

## 5. Task-routing options

Revised by the complete evidence. The task catalog already assigns `model_profile` per task,
so any static routing is configuration, not architecture.

| Option | Verdict | Supporting metrics (denominators) | Complexity / privacy / detection | Status |
|---|---|---|---|---|
| One local model for all tasks (Qwen) | **Supported now** as the best single-local configuration | Best local task UTS on 4/4 tasks; best or tied local agreement on 3/3 categorical tasks (n=30 each); 70.0% reliability (n=120) | Config-only; fully local; existing schema validation suffices | Implementable when the owner wants enrichment enabled |
| Best local model per task (local-to-local routing) | **Not supported** — no task where another local model beats Qwen; Phi only ties last-activity agreement (60%, n=30) with lower task UTS (77.8 vs 89.1) | Task UTS table, section 4 | Multi-model swap cost on 32 GiB iGPU laptop | Dropped from recommendations; retained as "checked and rejected" |
| Local-first, cloud fallback on invalid output | **Strongest product configuration** on current evidence | Qwen escalation rates per task: summary 13/30, mode 11/30, activity 0/30, title 12/30 (36/120 = 30% overall) | Detection already built (schema/evidence/cross-field validation); "local by default" gains a disclosed cloud asterisk and per-case cost | Article discussion; implementation is a product decision, not committed here |
| Task admission threshold | Supported as offline policy | E.g. a >=80% task-validity gate admits only Qwen last-activity (30/30) today | None; policy only | Article discussion |
| Faster-but-weaker model role | **No credible role** for the 1B floor under these contracts | UTS 22.4; 0.509 valid-output quality (n=120/57) despite p50 17.3s | — | Public one-liner |

Confidence: high within this bounded contract. Routing conclusions do not extend to other
corpora, prompts, quantizations, or hardware.

## 6. Composite score: exact UTS and sensitivity

**Usable Task Score (UTS), 0-100 — exact, reproduced per-case from private aggregates.**

Definition (formula v1): per case, score 0 when the candidate output is invalid or absent or
the judge result is not completed; otherwise the mean of the applicable rubric dimensions
normalized from the 1-4 judge scale via `(score - 1) / 3`; average the 30 cases within each
task; macro-average the four tasks; multiply by 100. Latency is never combined into UTS.
Normalization rationale: a judged "1" means the output is wrong; `(s-1)/3` gives it zero
credit, where `s/4` would give 0.25 credit for a wrong answer.

Exact values (float64 throughout; reported to 1 decimal):

| Task UTS (x100) | Gemini | Qwen | Phi | Llama 3B | Gemma | Llama 1B |
|---|---:|---:|---:|---:|---:|---:|
| Summary | 72.9 | 56.7 | 39.1 | 37.1 | 38.7 | 37.1 |
| Work mode | 90.0 | 41.7 | 37.2 | 28.9 | 30.6 | 20.0 |
| Last activity | 91.5 | 89.1 | 77.8 | 47.4 | 76.3 | 17.2 |
| Title | 99.1 | 60.0 | 45.8 | 54.2 | 16.4 | 15.3 |
| **UTS (macro)** | **88.4** | **61.9** | **50.0** | **41.9** | **40.5** | **22.4** |
| Zero-scored cases /120 | 10 | 36 | 43 | 51 | 58 | 64 |

Judge-failure policy: terminal judge failures score 0 (Gemini 2, Llama 3B 2, Llama 1B 1) and
remain visible. Equal-task and equal-case weighting were **verified identical** (difference
< 1e-12), as required, because every task has exactly 30 cases.

Sensitivity (all six formulas produce the identical order
Gemini > Qwen > Phi > Llama 3B > Gemma > Llama 1B):

| Formula | Values in rank order |
|---|---|
| UTS, `(s-1)/3` (primary) | 88.4 / 61.9 / 50.0 / 41.9 / 40.5 / 22.4 |
| `s/4` normalization variant | 89.2 / 63.9 / 53.5 / 45.8 / 43.3 / 28.5 |
| Judge failures excluded from denominator | 89.8 / 61.9 / 50.0 / 42.8 / 40.5 / 22.6 |
| Reliability x valid-output quality | 90.2 / 62.1 / 50.1 / 44.6 / 41.2 / 24.2 |
| Geometric sqrt(R x Q) | 95.0 / 78.8 / 70.8 / 66.8 / 64.2 / 49.2 |
| Harmonic 2RQ/(R+Q) | 95.0 / 78.3 / 70.4 / 66.3 / 62.7 / 49.2 |

Near-tie note: the Llama 3B / Gemma gap is 1.4 UTS points (2.5 under `s/4`). The direction is
stable across all variants but the article must not headline a fourth-versus-fifth claim.

Decision (owner-approved): UTS is retained as the **secondary** metric — it reproduces
exactly, the ranking is stable, its limitations fit three lines (policy choice; zero-for-
invalid; same-family judge input), and it adds clarity beyond the primary two-axis chart.
The two-axis reliability-versus-valid-output-quality view remains primary.

Calculation manifest (aliases, formula version, denominators, policies, results, variants):
`.chronicle/eval/dev-v1/tmp/lp41-uts/uts-calculation-manifest.json` (ignored path; source
packages referenced by accepted alias only; nothing was modified).

## 7. Public metric subset (finalized proposal)

1. Schema-valid rate per model (n=120) with failure-category decomposition;
2. Task x model validity matrix (24 cells, n=30 each);
3. Exact agreement vs FABLE for the three categorical tasks (n=30 each), labeled as
   agreement with silver references;
4. Quality among judged valid outputs (macro normalized) always paired with valid rate;
5. UTS with its three-line definition and formula;
6. Operational table kept separate: p50 latency, **decomposed** wall spans (never the raw
   Qwen span alone), and the privacy-safe hardware/runtime description.

"Raw results" in the article means these complete aggregate tables plus the exact scoring
formula — never per-case or per-conversation data, which stay private.

Private appendix (retained, not published): confusion matrices, per-label
precision/recall/support, per-dimension judge means, token accounting, per-task latency,
checkpoint data, calculation manifest.

## 8. Article narrative (owner-approved direction)

**Structure: measured results → survivorship-honest analysis → practical lessons → concrete
next steps.** Narrative A ("the reliability gap") is the spine; the failure-mode taxonomy from
the alternative narrative is absorbed into the lessons; the task x model matrix is the
technical centerpiece. The article is framed as practical lessons from an engineering
comparison on the owner's own frozen real-work corpus.

Practical-lessons candidates (each backed by a section-3 observation):

1. Strict output schemas turn "model quality" into measurable product reliability (obs 1);
2. Never average only the survivors — measure the whole package (obs 2);
3. Right-size what you send before you grow what the model accepts (obs 4);
4. Match model class to workload shape: laptop 4B inference is a batch tool — backfill
   ~2.8 days, daily increments minutes, interactive out of reach ~30x (obs 5);
5. Wall-clock is about tails and timeout policy, not averages (obs 5);
6. One local model can lead on every task and still deliver only 70% of the contract — plan
   the fallback path (obs 3 + routing);
7. Parameter count predicts neither speed nor reliability ordering (obs 3, 6).

Next-steps section (describes actually planned work): stronger machine + 16K-context arm for
the best local model(s) (section 14), prompt-strategy study (section 13), later untouched
evaluation set (WP-5.2C).

Headline options (owner selects at publication time):

1. "I benchmarked local SLMs on 120 real work tasks. The best matched cloud quality — 70% of
   the time."
2. "The reliability gap: what happens when local LLMs meet strict output contracts on real
   work."
3. (Master-plan candidate) "I benchmarked 5 local SLMs on my own laptop for real work.
   Results surprised me."

Formats: short LinkedIn post (~300 words: hook → scorecard visual → three findings →
methodology line → question CTA → repo link in first comment) plus the longer technical
article (results → analysis → lessons → next steps). Sequencing decision remains with the
owner.

## 9. Visual concepts

1. **Reliability x quality two-axis chart (primary).** X = schema-valid rate (n=120); Y =
   quality among judged valid outputs (macro, 0-1); six points. Shows the survivorship story
   (Gemma sits high-quality/low-reliability; the cloud control sits alone top-right).
2. **Latency x UTS operational chart (secondary).** X = per-case p50 (log scale, 2.2s-62s);
   Y = UTS; annotated with decomposed wall spans. Log scale mandatory (~30x spread).
3. **Task x model matrix (centerpiece).** 4 tasks x 6 models; cells show valid/30 (+ exact
   agreement where applicable), color by validity band. Full six-column form now final.

No final graphics before explicit owner request.

## 10. Limitations and prohibited claims

Must-state limitations:

- Bounded development comparison on one owner's selected, repeatedly used 30-conversation
  frozen corpus; silver references; not independent, representative, or scientific.
- Same-provider preview judge; five terminal judge failures scored zero; judge run windows
  differ between the historical and new arms under the same rubric (preview drift possible).
- One quantization, one runtime, one context policy (8,192), one prompt strategy, one laptop
  class; results measure the fixed task contract, not advertised maximum context.
- Hosted and local latency are not environment-comparable; token counts are not
  cross-tokenizer comparable.
- All 120 cases are development data; no untouched evaluation set exists yet.

Prohibited claims (evidence does not support):

- Any ground-truth framing for the cloud control or FABLE; any accuracy language for exact
  agreement;
- Statistical significance, generalization beyond this corpus/hardware/contract, or
  model-family superiority claims;
- Presenting valid-output quality as whole-model quality;
- Presenting UTS as more than a defined policy metric;
- Publishing the raw Qwen wall span without its timeout-tail decomposition;
- Blanket "too slow" claims — speed statements must name the workload (backfill vs
  incremental vs interactive);
- Claiming context expansion will fix any model (unmeasured; separate arm);
- A fourth-versus-fifth headline over the Llama 3B / Gemma near-tie;
- Asserting same-family judge bias as established (say: compatible with preference, does not
  establish it; further owner work parked);
- Local-to-local routing recommendations (checked and rejected on this evidence);
- Any per-conversation content, title, ID, or private path.

## 11. Candidate set status

The comparison set is complete: five local complete arms plus the cloud control, all on the
common 120-case scope. The previously planned incoming-model placeholders are removed. Gemma
ran as the approved Gemma 3 4B IT compatibility fallback (Gemma 4 E2B was neither loaded nor
probed). No further baseline candidates are planned before the article; any new model would be
a separately approved arm added under the unchanged contracts.

## 12. Owner decisions

Resolved 2026-07-23 (three-arm cycle): four-layer separation; UTS secondary with `(s-1)/3`
and judge-failures-score-zero; two-axis chart primary; public metric subset shape; baseline
context stays 8,192; context study and remote execution as follow-ups; adjudication and
rubric v2 to backlog.

Resolved 2026-07-24 (six-arm cycle):

1. Interpretation direction approved, including the two revisions: routing story is "one
   local winner plus cloud fallback" (local-to-local routing dropped), and the softened
   context finding (common floor, not sole cause);
2. Qwen wall span published only in decomposed form (supersedes the earlier raw-figure
   decision);
3. UTS confirmed with exact values and the near-tie handling;
4. Narrative: practical-lessons structure (results → analysis → lessons → next steps) with
   the failure taxonomy folded into lessons;
5. Gemma framed as weak research comparator, to be reviewed in article context;
6. Judge-bias work parked; qualified wording only.

Still open (decision at or after article drafting):

1. Final headline selection (three options, section 8);
2. Short post vs short post + long-form sequencing;
3. Publication timing (after PM validation of this brief and explicit owner request to draft);
4. Final visual selection and styling;
5. Gemma framing check in the drafted article;
6. Parked judge-bias work (sourcing and/or local adjudication) and whether it lands before or
   after publication;
7. Whether checkpoint data (Qwen-40, WP-5.2B2.1) appears anywhere public (default: no).

## 13. Prompt-tuning follow-up proposal (backlog; separate future study)

Maps to WP-5.2B3; runs only after separate owner approval:

1. Candidates: Qwen3.5-4B (clear first pick on complete evidence); optionally Phi-4 Mini as
   second (second-best local UTS and strong last-activity validity);
2. Gemini-120 retained unchanged as the cloud control target;
3. Versioned prompt strategies: accepted zero-shot baseline, concise schema-first variant,
   bounded task-specific few-shot variants;
4. No chain-of-thought requested or published;
5. Context, artifact, generation settings, inputs, references, and fixed-Pro scoring held
   constant within the study; every prompt/model identity versioned;
6. Development-set reuse disclosed; gains labeled prompt-development results;
7. Selected prompt frozen before any later untouched evaluation set;
8. Reliability, semantic, and task-specific gap closure reported separately.

## 14. Additional follow-ups (owner-approved direction; separate future studies)

1. **Context-expansion arm(s).** New, separately authorized arms for the best local model(s)
   with an up-front larger context policy (16K first; verify each pinned artifact's advertised
   maximum before planning). Directly tests observation 4's context hypothesis. Never a
   reinterpretation of accepted arms. Laptop wall time will rise materially because the
   recovered cases are the long ones — hence:
2. **Stronger-machine execution (WP-5.2C shape).** Split generation on the remote machine,
   portable packages, local scoring. Natural first remote workload: the context-expansion
   arm. Remote performance claims stay strictly separated from laptop claims.
3. **Owner adjudication of judge-vs-FABLE disagreement cases (parked with observation 7).**
   Local, private, converts silver to gold exactly where the same-family-preference question
   sits; strengthens but is not required for the article.
4. **Rubric v2 / judge-instruction tightening (backlog).** Any rubric change takes a new
   version and requires re-judging every candidate; rubric v1 stays frozen for the baseline.
5. **Input-cap tuning for local models (new, from the token-length analysis; cheap experiment,
   kept out of the article body per owner).** The `max_input_chars` selector caps in the task
   catalog are per-task: overview (whole conversation, used by summary/work-mode/title) caps at
   50,000 chars ≈ ~12,500 proxy tokens, which is *larger* than the tested 8,192-token local
   window — so that cap does not guarantee fit and rescued only 1 of 30 conversations from
   overflow (8→7 over the window after the cap). The recent selector (last-activity) caps at
   24,000 chars ≈ ~6,000 tokens, *below* the window, so 0 of 30 overflow — which is the real
   reason last-activity was the local sweet spot (input size, not task ease). Proposed
   experiment: lower the overview cap toward the local window for local runs and measure the
   reliability/quality trade-off, as a cheaper complement to buying a larger context window.
   Evidence source: privacy-safe per-conversation size distribution reproduced under
   `.chronicle/eval/dev-v1/tmp/lp41-uts/` (counts and sizes only). Proxy tokens use ~4
   chars/token; true tokenizer counts can be computed later for the final graphic.
