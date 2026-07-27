# LP-4.1 Article Plan — Second-Opinion Review Pack

## Purpose of this document

The author is planning a technical LinkedIn article based on a completed local-LLM evaluation
and wants an independent second opinion on the article plan **before drafting**. This document
is self-contained: it holds the aim, project context, complete aggregate results, the analysis
conclusions, the editorial decisions already taken, and the specific questions the reviewer is
asked to answer.

Everything here is privacy-safe aggregate evidence. No conversation content, titles, IDs,
private paths, credentials, or per-case data are included, and none may be requested — the
underlying corpus is the author's private chat history.

## 1. Aim of the article

- A **technical article for LinkedIn** with two goals, in this order:
  1. demonstrate the author's professional engineering skills — evaluation design, measurement
     honesty, structured-output product thinking;
  2. give readers **useful, practical information** they can apply when putting small local
     LLMs into real products.
- Tone and depth: engineering post, **not a scientific publication**. It must not overwhelm a
  LinkedIn audience — a compact story with one or two visuals and clearly ranked takeaways.
- A more rigorous long-form or scientific-venue version may follow **after the next project
  phase** (larger-context and stronger-hardware experiments, prompt study, untouched
  evaluation set). This article is explicitly the practical baseline story, and it should not
  spend its claims budget on things the next phase will measure properly.

## 2. Project context

The author built **Chat Chronicle** (open source, published as v0.1.0): a local-first,
privacy-respecting archive that ingests the author's own AI chat histories (ChatGPT, Claude,
Codex, Claude Code) into SQLite with full-text search. The next feature layer enriches each
conversation with four AI tasks, each with a **strict JSON schema contract** (the product
only consumes schema-valid output):

1. **Conversation summary** (2-5 sentences, evidence message IDs, word cap);
2. **Work-mode classification** (manager / executor / one-off / mixed / unknown);
3. **Last activity** (recent work, status, blockers, supported next action);
4. **Title assessment** (does the stored title fit; suggestion-only replacement).

Because the enrichment should run **locally by default** (privacy), the author benchmarked
small local models against a hosted cloud model on real data:

- **Corpus:** a frozen snapshot of the author's real archive; 30 fixed conversations x 4
  tasks = **120 identical cases per model**.
- **References:** machine-generated "FABLE" **silver development references** (not
  human-adjudicated gold labels).
- **Judge:** a fixed hosted judge (Gemini 3.1 Pro Preview, rubric v1, temperature 0), blinded
  to candidate identity, scoring 1-4 on task-specific dimensions. Only schema-valid outputs
  are judged; invalid outputs score zero — they are never silently dropped.
- **Candidates:** five local models (LM Studio, Q4_K_M quantization, context 8,192,
  single-worker, on a 4-core/8-thread 11th-gen Intel mobile CPU laptop, ~32 GiB RAM, Iris Xe
  iGPU) plus **Gemini 3.5 Flash via Vertex AI as the cloud control**.
- All 720 candidate positions terminal and accounted for; immutable evidence packages;
  zero-call cache replays; failures preserved, never repaired.

### Mandatory terminology (the article must follow this; the reviewer should too)

- Gemini = **cloud control / strong hosted baseline / practical quality ceiling** — never
  "ground truth" (it had 8 invalid outputs itself).
- FABLE = **silver development references**; "exact agreement with FABLE", never "accuracy".
- This is a **bounded development comparison** on one person's corpus — never "benchmark
  leaderboard", never statistically generalizable.
- Judge scores describe **quality among successfully judged valid outputs**, never
  whole-model quality.
- The judge shares a provider/model family with the Gemini candidate; observed
  judge/reference disagreement is **compatible with same-family preference but does not
  establish bias** (further work parked).

## 3. Results (complete aggregate evidence)

### 3.1 Headline scorecard

**Usable Task Score (UTS, 0-100)** is the author's composite: per case, invalid output or
failed judge = 0; otherwise mean rubric score normalized (score-1)/3; average 30 cases per
task; macro-average 4 tasks; x100. It deliberately makes failed outputs count as zero — a
survivorship correction, presented as an explicit policy metric, not scientific truth.

| Model | Deployment | Schema-valid /120 | Quality among valid outputs (0-1) | **UTS** | p50 latency | 120-case wall span |
|---|---|---:|---:|---:|---:|---:|
| Gemini 3.5 Flash | cloud control | 112 (93.3%) | 0.966 | **88.4** | 2.2s | 10m 40s |
| Qwen3.5-4B | local | 84 (70.0%) | 0.887 | **61.9** | 62.1s | 4h 43m (see 3.4) |
| Phi-4 Mini | local | 77 (64.2%) | 0.780 | **50.0** | 54.6s | 2h 19m |
| Llama 3.2 3B | local | 71 (59.2%) | 0.755 | **41.9** | 51.1s | 2h 21m |
| Gemma 3 4B | local | 62 (51.7%) | 0.797 | **40.5** | 61.8s | 2h 08m |
| Llama 3.2 1B | local floor | 57 (47.5%) | 0.509 | **22.4** | 17.3s | 42m 13s |

Ranking stability: the order is identical under six alternative scoring formulas (different
normalization, judge-failure handling, reliability x quality products, geometric/harmonic
combinations). One near-tie: Llama 3B vs Gemma differ by only 1.4 UTS points — direction
stable, but not headline-worthy.

### 3.2 Task x model matrix (valid outputs /30; task-level UTS)

| Task | Gemini | Qwen | Phi | Llama 3B | Gemma | Llama 1B |
|---|---|---|---|---|---|---|
| Summary | 23/30 · 72.9 | 17/30 · 56.7 | 14/30 · 39.1 | 12/30 · 37.1 | 12/30 · 38.7 | 16/30 · 37.1 |
| Work mode | 30/30 · 90.0 | 19/30 · 41.7 | 18/30 · 37.2 | 19/30 · 28.9 | 19/30 · 30.6 | 20/30 · 20.0 |
| Last activity | 29/30 · 91.5 | 30/30 · 89.1 | 29/30 · 77.8 | 23/30 · 47.4 | 25/30 · 76.3 | 14/30 · 17.2 |
| Title | 30/30 · 99.1 | 18/30 · 60.0 | 16/30 · 45.8 | 17/30 · 54.2 | 6/30 · 16.4 | 7/30 · 15.3 |

Exact agreement with FABLE (n=30 each; no-valid-output counts as non-matching) — work mode /
last activity / title fit: Gemini 63.3/70.0/83.3%; Qwen 33.3/60.0/56.7%; Phi 10.0/60.0/16.7%;
Llama 3B 10.0/40.0/43.3%; Gemma 16.7/46.7/10.0%; Llama 1B 3.3/20.0/6.7%.

### 3.3 Failure decomposition (the "why", n=120 per model)

- Common floor: **context-length failures, 21-30 per local arm** — the fixed 8,192-token
  window cannot fit the full-conversation input selector (~12-14K tokens) on long
  conversations. The one task with a small selector (last activity, ~6-7K tokens) is the
  local sweet spot: 30/29/25/23 of 30 valid for Qwen/Phi/Gemma/Llama-3B.
- Model-specific modes above the floor: Qwen is 81% context-failure (29/36, plus 5 timeouts);
  Gemma adds **24 schema failures concentrated in title assessment** (24 of 30 title cases
  rejected); Phi and Llama 3B add 10 timeouts each; Llama 3B adds 15 evidence failures; Phi's
  title failures are semantic (inverts title-fit judgments) while Gemma's are structural —
  same task, opposite failure classes.

### 3.4 Speed, honestly

- All 3-4B local models cluster at **p50 51-62s per case** on this laptop; the 1B floor runs
  ~17s but is unusable (UTS 22.4).
- Qwen's headline 4h43m wall span is a **timeout-tail artifact**: per-case evidence shows 29
  context failures failing fast (mean 1.8s), 84 successes (~2h00m total, mean 86s), and 5
  timeouts summing 2h39m — 8,857s of that in a single case consistent with a recorded
  overnight wrapper interruption. Excluding timeouts, Qwen's summed latency (~2h04m) is
  comparable to the other 4B arms. The article will only publish the decomposed form.
- Workload-shaped speed conclusion: on the author's real archive (711 conversations), full
  backfill ≈ 2.8 days of continuous laptop compute (impractical); **incremental daily
  enrichment ≈ minutes per day (acceptable)**; interactive use (2s budget) is out of reach by
  ~30x. Hosted and local latency are not environment-comparable.

## 4. Conclusions

### Main takeaways (the article's core; each has metric + denominator + caveat behind it)

1. **Structured-output reliability is the first-order product metric** — and no local model
   reached three-in-four (70.0% best local vs 93.3% cloud, n=120). "The best local outputs
   matched cloud quality — 70% of the time."
2. **Never average only the survivors.** Quality-among-valid and reliability rank models
   differently (Gemma's valid outputs outscore Phi's despite 12.5 points less reliability);
   the composite scores failures as zero so they cannot disappear.
3. **One local model (Qwen3.5-4B) leads on all four tasks — and still only delivers 70% of
   the contract.** So the practical architecture is local-first with cloud fallback on
   invalid output (escalation would have been 30% of cases; detection is free because schema
   validation already exists). Local-to-local task routing was checked and rejected.
4. **Right-size what you send before you grow what the model accepts.** The input-selector
   size, not model intelligence, decided the one task local models did well.
5. **Match model class to workload shape.** Laptop 4B inference is a batch tool: backfill
   days, daily increments minutes, interactive impossible. Speed claims must name the
   workload.

### Minor / secondary observations (one-liners or appendix; must not crowd the story)

- Parameter count predicts neither reliability nor speed ordering (Gemma 4B < Llama 3B
  reliability; all 3-4B models equally slow per case).
- The fast 1B floor has no credible role for these contracts — fast wrong answers are still
  wrong.
- Wall-clock is about tails and timeout policy, not averages (the 8,857s single-case tail).
- Work-mode classification is semantically hardest for every model including the cloud
  control (63.3% best agreement, n=30) — with a class-imbalance caveat.
- Distinct categorical failure shapes: one model never predicted `executor`, another funnels
  everything into `mixed`, a third over-predicts `manager`.
- Judge/reference disagreement on title fit is compatible with same-family judge preference
  but does not establish it (parked for possible adjudication before publication).

### Next steps (the article's closing section — actually planned work)

1. Re-run the best local model(s) with a larger context window (16K first) as a new measured
   arm — the context hypothesis is deliberately **not** claimed as a fix until measured;
2. Move generation to a stronger machine (the harness already splits generation from
   scoring), keeping remote performance claims separate from laptop claims;
3. A versioned prompt-strategy study (schema-first, few-shot) on the top one or two local
   models against the unchanged cloud control;
4. Later, an untouched evaluation set for defensible final comparisons — the current 120
   cases are development data and are described as such.

## 5. Editorial decisions already taken (intermediate decision log)

1. **Narrative:** practical-lessons structure — measured results → survivorship-honest
   analysis → practical lessons → concrete next steps. The failure-mode taxonomy is folded
   into the lessons; the task x model matrix is the technical centerpiece.
2. **Primary visual:** two-axis chart, reliability (x, n=120) vs quality-among-valid-outputs
   (y); **secondary visual:** p50 latency (log) vs UTS with decomposed wall-span annotations;
   **centerpiece table:** the 4x6 task x model matrix.
3. **Composite:** UTS retained as a **secondary** metric only — exact values reproduced
   per-case, ranking stable across six formulas, three-line limitations. The two-axis view
   stays primary.
4. **Metric subset for the public article:** valid rate + failure decomposition; task matrix;
   exact agreement (labeled as silver-reference agreement); valid-output quality paired with
   valid rate; UTS with formula; separate operational table. "Raw results" means complete
   aggregate tables + exact formula — never per-case data.
5. **Speed presentation:** only workload-shaped claims; only the decomposed Qwen wall span.
6. **Gemma framing:** "weak research comparator" under these contracts (to be reviewed in
   the drafted article for tone).
7. **Judge-bias wording:** qualified only ("compatible with, does not establish");
   strengthening it requires sourcing or the parked local adjudication of the five
   disagreement cases.
8. **Baseline integrity:** context stays 8,192 for all published baseline results;
   context-expansion and prompt-tuning results, when they exist, will be separate follow-up
   stories rather than edits to this one.
9. **Candidate headlines (final choice open):**
   1. "I benchmarked local SLMs on 120 real work tasks. The best matched cloud quality — 70%
      of the time."
   2. "The reliability gap: what happens when local LLMs meet strict output contracts on
      real work."
   3. "I benchmarked 5 local SLMs on my own laptop for real work. Results surprised me."
10. **Formats:** short LinkedIn post (~300 words, one visual, question CTA, repo link in
    first comment) plus a longer technical article; sequencing still open.

## 6. Questions for the second-opinion reviewer

1. **Aim fit:** does the planned structure actually serve both goals — professional
   showcase *and* practical value — or does one crowd the other?
2. **Headline:** which of the three candidates (or what alternative) best fits a LinkedIn
   technical audience without overclaiming?
3. **Overwhelm check:** is the proposed public metric set (section 5, item 4) already too
   much for LinkedIn? What would you cut first? What must survive any cut?
4. **Takeaway ranking:** do you agree with the main-vs-minor split in section 4? Would you
   promote or demote anything?
5. **Credibility:** does the honesty framing (silver references, cloud control not ground
   truth, survivorship correction, decomposed speed) read as rigor — or as hedging that
   weakens the post? Where is the right balance for this audience?
6. **The composite:** does UTS help a LinkedIn reader, or should the article stay with the
   two-axis chart and the matrix only?
7. **Visuals:** which single visual would you lead with if only one survives?
8. **Format:** short post only, or short post + long-form article — and in which order?
9. **Anything missing** that a practitioner audience would ask ("what about X?") that the
   plan should pre-empt?

The reviewer is asked **not** to relax the terminology and prohibited-claims constraints
(sections 2 and 4) — they are evidence-boundary commitments, not style choices.

## 7. Reference documents (repository paths)

Tracked evidence and planning artifacts behind every number in this pack:

- `md/handoffs/reports/LP-4.1-local-model-results-analysis-brief.md` — the full analysis
  brief (six-arm scorecard, exact UTS + sensitivity, task difficulty, routing, limitations,
  prohibited claims, decisions log);
- `md/handoffs/reports/WP-5.2B1.4-completion-report.md` — Gemini-120 / Qwen-120 /
  Llama-1B-120 complete-arm evidence (reliability, confusion matrices, judge means by task,
  latency, tokens, provenance);
- `md/handoffs/reports/WP-5.2B2.2-completion-report.md` — Phi-120 / Llama-3B-120 / Gemma-120
  complete-arm evidence (same structure);
- `md/handoffs/reports/WP-5.2B1.4-validation-review.md` and
  `md/handoffs/reports/WP-5.2B2.2-validation-review.md` — PM validation of the evidence;
- `md/handoffs/reports/LP-4.1-validation-review.md` — PM acceptance of the provisional
  analysis direction;
- `md/handoffs/LP-4.1-local-model-results-analysis-and-article-planning.md` and
  `md/handoffs/LP-4.1-complete-results-continuation.md` — the analysis mandates;
- `md/master-plan.md` (LP-4 / LP-4.1 sections) — the article's place in the publication
  series;
- `docs/development-evaluation.md` — the evaluation harness runbook (methodology detail).

Private per-case evidence (packages, judge attempts, calculation manifest) exists under
ignored repository paths and is intentionally not part of this pack.
