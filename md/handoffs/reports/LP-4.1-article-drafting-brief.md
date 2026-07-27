# LP-4.1 Article — Drafting Brief (Settled Plan)

## What this document is

This is the **settled drafting plan** for the LP-4.1 technical article, produced after a
second-opinion review cycle. It is self-contained: it holds the aim, the audience, the
terminology and prohibited-claims constraints, the complete settled section outline (with word
budgets and the exact data each section uses), the editorial decisions, and the open
verification item.

Roles for the next phase: the **drafting author writes**; the reviewer acts as **critique, not
main author**. Drafting begins only on the author's explicit request. This brief folds in the
two changes agreed in review — the survivorship-trap moment and the constrained-decoding
correction — so the draft starts from the corrected plan, not the original outline.

All evidence here is privacy-safe aggregate. No conversation content, titles, IDs, private
paths, credentials, or per-case data are included or may be requested.

---

## 1. Aim and audience

A **technical LinkedIn long-form article** with two goals, in this order:

1. demonstrate the author's professional engineering skill — evaluation design, measurement
   honesty, structured-output product thinking;
2. give readers **useful, practical information** for putting small local LLMs into real
   products.

Tone: engineering post, **not a scientific publication**. Light, useful, professional. It opens
with an executive summary and ranked takeaways, keeps the body approachable, and pushes heavy
technical detail into an appendix rather than burying the reader.

Length target: **~1,200–1,500 words** in the body, plus appendix. LinkedIn long-form is not
commonly very long, so the discipline is: lead with value, detail on demand.

A more rigorous long-form or scientific version may follow **after the next project phase**
(larger context, stronger hardware, prompt study, untouched eval set). This article is the
**practical baseline story** and must not spend its claims budget on things the next phase will
measure properly.

---

## 2. Project context (for the "why I did this" section)

The author built **Chat Chronicle** (open source, v0.1.0): a local-first, privacy-respecting
archive that ingests the author's own AI chat histories (ChatGPT, Claude, Codex, Claude Code)
into SQLite with full-text search. The next feature layer enriches each conversation with four
AI tasks, each bound to a **strict JSON schema contract** (the product only consumes
schema-valid output):

1. **Conversation summary** (2–5 sentences, evidence message IDs, word cap);
2. **Work-mode classification** (manager / executor / one-off / mixed / unknown);
3. **Last activity** (recent work, status, blockers, supported next action);
4. **Title assessment** (does the stored title fit; suggestion-only replacement).

Enrichment should run **locally by default** for privacy and cost. The question the article
answers: *can small local models do this on a laptop?*

---

## 3. Terminology and prohibited claims (binding — do not relax)

These are evidence-boundary commitments, not style choices. The draft must obey them and the
critique must enforce them.

- Gemini = **cloud control / strong hosted baseline / practical quality ceiling** — never
  "ground truth" (it had 8 invalid outputs itself).
- FABLE = **silver development references**; say "exact agreement with FABLE", never "accuracy".
- This is a **bounded development comparison** on one person's corpus — never "benchmark
  leaderboard", never statistically generalizable.
- Judge scores describe **quality among successfully judged valid outputs**, never whole-model
  quality.
- The judge shares a provider/model family with the Gemini candidate; observed judge/reference
  disagreement is **compatible with same-family preference but does not establish bias**
  (parked).
- **Do not claim "constrained decoding ON" or "despite grammar enforcement."** The evidence
  records intended `structured_output: true` in profiles; it does **not** establish what
  LM Studio actually enforced per model/artifact. Say only what is supported: **"strict schema
  validation of outputs, temperature 0, zero retries."** (See §7, open verification item — if
  verified later, the stronger claim becomes an upgrade, not a loss.)
- Terminology rule extends to prose: prefer "this evaluation" over "this benchmark" in
  first-person lines (e.g., "…including, until this evaluation, mine").

---

## 4. The evidence the article draws on

**Design.** 30 fixed conversations × 4 tasks = **120 identical cases per model**. Six models:
five local (LM Studio, Q4_K_M, context 8,192, single worker, 4-core/8-thread 11th-gen Intel
mobile CPU, ~32 GiB RAM, Iris Xe iGPU) plus **Gemini 3.5 Flash via Vertex AI as cloud control**.
Fixed hosted judge (Gemini 3.1 Pro Preview, rubric v1, temperature 0), blinded to candidate
identity, scoring 1–4; only schema-valid outputs judged, invalid = zero (never dropped). All 720
positions terminal; immutable evidence packages; zero-retry policy applied uniformly (same
footing for every model).

### 4.1 Headline scorecard

| Model | Deployment | Schema-valid /120 | Quality among valid (0–1) | UTS | p50 latency | 120-case wall span |
|---|---|---:|---:|---:|---:|---:|
| Gemini 3.5 Flash | cloud control | 112 (93.3%) | 0.966 | 88.4 | 2.2s | 10m 40s |
| Qwen3.5-4B | local | 84 (70.0%) | 0.887 | 61.9 | 62.1s | 4h 43m (decomposed) |
| Phi-4 Mini | local | 77 (64.2%) | 0.780 | 50.0 | 54.6s | 2h 19m |
| Llama 3.2 3B | local | 71 (59.2%) | 0.755 | 41.9 | 51.1s | 2h 21m |
| Gemma 3 4B | local | 62 (51.7%) | 0.797 | 40.5 | 61.8s | 2h 08m |
| Llama 3.2 1B | local floor | 57 (47.5%) | 0.509 | 22.4 | 17.3s | 42m 13s |

Ranking is identical under six alternative scoring formulas. One near-tie: Llama 3B vs Gemma
differ by 1.4 UTS — direction stable, not headline-worthy.

### 4.2 Task × model matrix (valid /30 · task-level UTS) — the centerpiece table

| Task | Gemini | Qwen | Phi | Llama 3B | Gemma | Llama 1B |
|---|---|---|---|---|---|---|
| Summary | 23/30 · 72.9 | 17/30 · 56.7 | 14/30 · 39.1 | 12/30 · 37.1 | 12/30 · 38.7 | 16/30 · 37.1 |
| Work mode | 30/30 · 90.0 | 19/30 · 41.7 | 18/30 · 37.2 | 19/30 · 28.9 | 19/30 · 30.6 | 20/30 · 20.0 |
| Last activity | 29/30 · 91.5 | 30/30 · 89.1 | 29/30 · 77.8 | 23/30 · 47.4 | 25/30 · 76.3 | 14/30 · 17.2 |
| Title | 30/30 · 99.1 | 18/30 · 60.0 | 16/30 · 45.8 | 17/30 · 54.2 | 6/30 · 16.4 | 7/30 · 15.3 |

Exact agreement with FABLE (n=30; no valid output = non-match) — work mode / last activity /
title: Gemini 63.3/70.0/83.3%; Qwen 33.3/60.0/56.7%; Phi 10.0/60.0/16.7%; Llama 3B
10.0/40.0/43.3%; Gemma 16.7/46.7/10.0%; Llama 1B 3.3/20.0/6.7%.

### 4.3 Failure decomposition (n=120 per model)

- **Common floor: context-length failures, 21–30 per local arm** — the fixed 8,192-token window
  cannot fit the full-conversation input selector (~12–14K tokens) on long conversations. The
  one task with a small selector (last activity, ~6–7K tokens) is the local sweet spot: 30/29/25/23
  of 30 valid for Qwen/Phi/Gemma/Llama-3B.
- Model-specific modes: Qwen 81% context-failure (29/36, +5 timeouts); Gemma **24 schema
  failures concentrated in title assessment** (24 of 30 title cases rejected — structural); Phi
  and Llama 3B +10 timeouts each; Llama 3B +15 evidence failures; **Phi's title failures are
  semantic (inverts title-fit) while Gemma's are structural — same task, opposite failure
  classes.**

### 4.4 Speed (workload-shaped claims only)

- All 3–4B models cluster at **p50 51–62s per case**; the 1B floor runs ~17s but is unusable
  (UTS 22.4).
- Qwen's 4h43m wall span is a **timeout-tail artifact**: 29 context failures fail fast (mean
  1.8s), 84 successes (~2h00m, mean 86s), 5 timeouts summing 2h39m — 8,857s of that in a single
  case consistent with a recorded overnight wrapper interruption. Excluding timeouts, Qwen's
  summed latency (~2h04m) is comparable to the other 4B arms. **Publish only the decomposed
  form.**
- Workload conclusion (author's real archive, 711 conversations): full backfill ≈ **2.8 days**
  continuous laptop compute (impractical); **incremental daily enrichment ≈ minutes/day
  (acceptable)**; interactive use (2s budget) out of reach by ~30×. Hosted and local latency are
  not environment-comparable.

---

## 5. Settled section outline (with word budgets and content)

The two review changes are folded in: **§5b is the new survivorship-trap moment**, and the
constrained-decoding wording is corrected in §4-Setup and §5.

1. **Title + hook** (~60–90 words). Proper article title plus a 2–3 line hook stating the core
   reversal in narrative form: the best local model matched cloud quality, but only 70% of the
   time. Wording must be **distinct** from the takeaway version in §2.

2. **Executive summary & takeaways** (~120–160 words). The five ranked lessons as one-liners so
   a skimmer leaves with everything: (1) structured-output reliability is the first-order
   metric; (2) never average only the survivors; (3) local-first with cloud fallback on invalid
   output; (4) right-size the input before growing the context window; (5) match model class to
   workload shape. The 70% reversal appears here in **metric form with denominator** (distinct
   from the hook).

3. **Why I did this** (~120 words). Chat Chronicle in two sentences (local-first private chat
   archive; four AI enrichment tasks with strict JSON contracts) and the question: can small
   local models do this on a laptop?

4. **The setup, briefly** (~140 words). 30 real conversations × 4 tasks × 6 models (5 local +
   Gemini Flash cloud control), fixed blinded judge, **strict schema validation of outputs,
   temperature 0, zero retries (uniform footing)**. Include the 3-line "what this is / isn't"
   box: one corpus, silver references, development data, 8K context. **Do not** claim grammar
   enforcement.

5. **What happened: reliability** (~160 words). Lead visual = the scatter (reliability x, n=120,
   vs quality-among-valid y). Headline finding: **no local model reached three-in-four valid
   outputs.** Best local (Qwen) = 70.0% valid vs cloud 93.3%. State the reliability gap plainly;
   the schema failures are real product failures, not cosmetics.

5b. **The survivorship trap** (~110 words — short, high-impact, the signature moment). Show the
   trap with the article's own data:
   > "If I showed you only the judged quality of successful outputs, Gemma (0.80) beats Phi
   > (0.78). But Gemma delivered a valid output in 52% of cases, Phi in 64%. Averaging survivors
   > is how most local-LLM demos mislead — including, until this evaluation, mine."
   This is the screenshot-and-share moment: it names a trap the author fell into, serving both
   aims at once (practical lesson + evaluation-design skill). Explain that the composite scores
   failures as zero precisely so they cannot disappear.

6. **Why they failed** (~180 words — **first candidate for trimming to appendix if overflow**).
   The 8K context floor dominates every local arm; the small-input task (last activity) is the
   local sweet spot; and models fail the *same* task in opposite ways — **Phi semantic vs Gemma
   structural**. Keep the taxonomy tight; full counts live in the appendix.

7. **The task × model matrix** (~120 words + table). The 4×6 centerpiece table with a short
   read-through: one local model (Qwen) leads all four tasks yet still delivers only 70% of the
   contract; work-mode is semantically hardest for everyone including the cloud control.

8. **Speed, honestly** (~150 words). Workload-shaped only: backfill = days (impractical), daily
   increments = minutes (fine), interactive = impossible (~30× off). Use the **decomposed** Qwen
   wall span as the "tails and timeout policy, not averages" lesson. Name the workload with every
   speed claim.

9. **What I'd build** (~150 words — **the payoff; never cut**). The practical architecture:
   local-first with **explicit cloud fallback on invalid output** (escalation ≈ 30% of cases;
   detection is free because schema validation already exists). Fold in the privacy/cost framing:
   local by default for privacy and cost; the cloud is an optional, explicit quality escape
   hatch — users shouldn't be forced to choose. Note local-to-local task routing was checked and
   rejected.

10. **What's next** (~110 words). The four planned measurements as **unmeasured hypotheses, not
    promises**: (1) re-run best local model(s) at 16K context as a new measured arm — the context
    hypothesis is *not* claimed as a fix until measured; (2) move generation to stronger hardware
    (harness already splits generation from scoring); (3) versioned prompt-strategy study
    (schema-first, few-shot) on the top one or two locals vs the unchanged cloud control; (4) an
    untouched evaluation set for defensible final comparisons.

11. **CTA + repo link** (~40 words). One question to the audience; open-source repo link (in
    first comment for the short-post variant).

### Appendix (trailing or linked — detail on demand)

- **UTS**: exact per-task values, the formula (per case: invalid or failed judge = 0; else mean
  rubric normalized (score−1)/3; average 30 cases per task; macro-average 4 tasks; ×100), and
  the six-formula stability note. UTS is **secondary/appendix only** — never the headline number
  (a single composite invites the leaderboard reading the terminology bans).
- **Usable-output rate** (optional one-number summary): % of 120 cases producing a valid output
  scoring ≥3/4. Reads like a pass rate, needs no formula — offered as the intuitive single number
  if one is wanted, in place of leading with UTS.
- FABLE silver-reference agreement table (§4.2).
- Full failure taxonomy counts (§4.3), including the distinct categorical failure shapes
  (a model that never predicts `executor`, one that funnels to `mixed`, one that over-predicts
  `manager`).
- Hardware / quantization spec; why Q4_K_M; the five model choices.
- Terminology and prohibited-claims commitments (§3).
- Judge/reference same-family note (compatible with, does not establish).

---

## 6. Editorial decisions (settled)

1. **Narrative:** measured results → survivorship-honest analysis → practical lessons → next
   steps. Failure taxonomy folded into the lessons; task × model matrix is the technical
   centerpiece.
2. **Primary visual:** two-axis scatter (reliability n=120 vs quality-among-valid). **Lead with
   this single visual if only one survives.** Secondary: p50 latency (log) vs UTS with decomposed
   wall-span annotations. Centerpiece table: the 4×6 matrix.
3. **Composite:** UTS retained **secondary/appendix only**. Two-axis view stays primary.
4. **Public metric set (short body):** valid rate + failure decomposition; task matrix;
   quality-among-valid paired with valid rate; separate operational (speed) table. FABLE
   agreement and UTS live in the appendix. "Raw results" = complete aggregate tables + exact
   formula, never per-case data.
5. **Speed:** only workload-shaped claims; only the decomposed Qwen wall span.
6. **Gemma framing:** "weak research comparator" under these contracts — review tone in draft.
7. **Judge-bias wording:** qualified only ("compatible with, does not establish").
8. **Baseline integrity:** context stays 8,192 for all published baseline results;
   context-expansion and prompt-tuning results become **separate follow-up stories**, never edits
   to this one.
9. **Retry policy:** zero retries, applied uniformly — stated in-article as a same-footing
   measurement choice.
10. **Titles/format:**
    - **Format decision:** write and publish the **LinkedIn long-form article first** (not too
      long). A short ~300-word post may follow as a distribution vehicle pointing to it.
    - **Two title layers:** a cliché-friendly **short-post title** (LinkedIn-native, may lean on
      the "surprised me" register) is allowed *and kept distinct from* the **article's proper
      title**, which must not overclaim or use "benchmark leaderboard" framing.
    - Leading headline candidate for the article: *"I tested 5 local SLMs on 120 real work tasks.
      The best matched cloud quality — 70% of the time."* (uses "tested", not "benchmarked", to
      stay consistent with the no-leaderboard rule).

### Overflow rule

If the body exceeds budget, **cut from §6 (failure detail) into the appendix — never from §9
(the architecture payoff)**, which is what makes the article practical.

---

## 7. Open verification item (for the manager thread, not the drafting thread)

Small, legitimate check: **verify what LM Studio actually enforced per model/artifact** — e.g.,
whether `json_schema` requests were accepted or silently downgraded per artifact. The accepted
reports record intended `structured_output: true` in the profiles but do not characterize
runtime enforcement, and the presence of invalid-JSON / schema failures suggests enforcement was
at best partial or bypassed on some paths.

- **Until verified:** the article says only "strict schema validation of outputs, temperature 0,
  zero retries."
- **If verified positive:** "despite schema-constrained generation" becomes an available
  *strengthener* — it makes the reliability finding stronger (failures occurred despite
  enforcement). This is an upgrade path, not a dependency; the article does not wait on it.

---

## 8. Critique checklist (how the reviewer will read the draft)

- No prohibited claim slips in (§3), especially "ground truth", "accuracy", "benchmark
  leaderboard", "constrained decoding ON".
- Each caveat appears **once**, at the claim it bounds — decisive, not repeated or apologetic.
- The survivorship-trap moment (§5b) survives editing intact and reads as a shareable line.
- The 70% reversal is worded **distinctly** in the hook (§1) vs the takeaway (§2).
- Speed claims always name the workload; only the decomposed Qwen span appears.
- §9 payoff is intact; any trimming came from §6.
- Body stays within ~1,200–1,500 words; heavy detail is in the appendix, not the body.

---

## 9. Reference documents (repository paths)

- `md/handoffs/reports/LP-4.1-article-second-opinion-brief.md` — the review pack this brief
  settles.
- `md/handoffs/reports/LP-4.1-local-model-results-analysis-brief.md` — full analysis brief.
- `md/handoffs/reports/WP-5.2B1.4-completion-report.md` — Gemini-120 / Qwen-120 / Llama-1B-120
  complete-arm evidence.
- `md/handoffs/reports/WP-5.2B2.2-completion-report.md` — Phi-120 / Llama-3B-120 / Gemma-120
  complete-arm evidence.
- `md/handoffs/reports/WP-5.2B1.4-validation-review.md`,
  `md/handoffs/reports/WP-5.2B2.2-validation-review.md` — PM validation of the evidence.
- `md/handoffs/reports/LP-4.1-validation-review.md` — PM acceptance of the analysis direction.
- `md/handoffs/LP-4.1-local-model-results-analysis-and-article-planning.md`,
  `md/handoffs/LP-4.1-complete-results-continuation.md` — analysis mandates.
- `docs/ai-tasks.md` — task contracts and intended structured-output configuration (note: intent,
  not verified runtime enforcement — see §7).
- `docs/development-evaluation.md` — evaluation harness runbook.
- `md/master-plan.md` (LP-4 / LP-4.1) — the article's place in the publication series.
