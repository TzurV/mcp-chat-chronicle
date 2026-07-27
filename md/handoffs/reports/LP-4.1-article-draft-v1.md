# LP-4.1 Article — First Draft (v1)

> Draft status: first complete draft per `LP-4.1-article-drafting-brief.md`. Figures are not
> rendered; each figure appears as a bracketed spec with the exact data to plot. Body word
> count ≈ 1,430 (excluding tables, figure specs, and appendix). Unstaged, awaiting owner
> review and critique pass.
>
> Title layers per the settled plan: the article title below is the "proper" title; a separate
> LinkedIn-native short-post title may be chosen later for the distribution post.

---

# I tested 5 local SLMs on 120 real work tasks. The best matched cloud quality — 70% of the time.

I wanted my chat archive to enrich itself — summaries, work modes, activity status, better
titles — without my history ever leaving my laptop. So I ran five small local models and one
hosted cloud model over the same 120 enrichment tasks, drawn from my own real work, under the
same strict output contracts. When the best local model succeeded, I often couldn't tell its
output from the cloud's. Almost a third of the time, it didn't succeed at all. Most write-ups
only show you the first half.

## The takeaways up front

The best local model (Qwen3.5-4B, quantized, on an ordinary laptop) returned schema-valid
output in **84 of 120 cases (70.0%)**, against **112 of 120 (93.3%)** for the hosted cloud
control. Everything I learned follows from taking that gap seriously:

1. **Structured-output reliability is the first-order product metric.** A model that answers
   brilliantly 60% of the time is a 60% model.
2. **Never average only the survivors.** Quality-of-successful-outputs hides failures; score
   failures as zero and they can't disappear.
3. **Local-first with cloud fallback on invalid output** beats picking either side.
4. **Right-size what you send before growing what the model accepts.** Input size, not model
   intelligence, decided the one task local models did well.
5. **Match model class to workload shape.** Laptop-class 4B inference is a batch tool: backfill
   takes days, daily increments take minutes, interactive is out of reach.

## Why I did this

I built [Chat Chronicle](repo link in first comment), an open-source, local-first archive that
ingests my AI chat histories — ChatGPT, Claude, Codex, Claude Code — into SQLite with full-text
search. The next layer enriches each conversation with four AI tasks: a factual summary, a
work-mode classification (manager / executor / one-off / mixed), a last-activity status with
next action, and a title check with a suggested replacement. Each task is bound to a strict
JSON schema — the product only stores schema-valid output. For privacy and cost, enrichment
should run locally by default. The question: **can small local models actually do this, on the
laptop I already own?**

## The setup, briefly

**30 real conversations from my own archive × 4 tasks = 120 identical cases per model.** Five
local models via LM Studio, all Q4_K_M quantized, all at the same fixed 8,192-token context,
single worker, on a 4-core/8-thread 11th-gen Intel mobile CPU with 32 GB RAM and integrated
graphics: Qwen3.5-4B, Phi-4 Mini, Llama 3.2 3B, Gemma 3 4B, and Llama 3.2 1B as the small
floor. Plus **Gemini 3.5 Flash (Vertex AI) as the cloud control** — a practical quality
ceiling to measure against, not an answer key. Every schema-valid output was scored 1–4 on
task-specific dimensions by a fixed hosted judge (Gemini 3.1 Pro Preview, temperature 0),
blinded to which model produced it. Strict schema validation of outputs, temperature 0, zero
retries — the same footing for every model.

What this is / isn't:

- One person's real corpus, 30 conversations: a **bounded development comparison**, not a
  leaderboard, and not statistically generalizable.
- Reference labels are machine-generated **silver development references**, not
  human-adjudicated.
- The fixed 8,192-token context is part of what's being measured, not an accident.

## What happened: reliability

**No local model reached three valid outputs in four.** Qwen3.5-4B managed 70.0%, Phi-4 Mini
64.2%, Llama 3.2 3B 59.2%, Gemma 3 4B 51.7%, Llama 3.2 1B 47.5% — versus 93.3% for the cloud
control (all n=120). And an invalid output isn't a cosmetic defect: the schema is the product
contract, so an invalid case means there is nothing to store. The reliability axis, not the
quality axis, is where local models lose.

> **[FIGURE 1 — primary visual. Scatter plot, one point per model.**
> **X-axis:** schema-valid rate (% of 120 cases). **Y-axis:** quality among successfully
> judged valid outputs (normalized judge mean, 0–1). Label each point.
> Data (x, y): Gemini 3.5 Flash (93.3, 0.966) · Qwen3.5-4B (70.0, 0.887) · Phi-4 Mini
> (64.2, 0.780) · Llama 3.2 3B (59.2, 0.755) · Gemma 3 4B (51.7, 0.797) · Llama 3.2 1B
> (47.5, 0.509).
> **Visual story:** the cloud control sits alone top-right; the local 3–4B cluster sits high
> on quality but spread wide on reliability; Gemma sits *above* Phi on quality yet far left
> of it on reliability — the survivorship trap, visible. The vertical axis flatters
> everyone; the horizontal axis is the product truth.]**

## The survivorship trap

If I showed you only the judged quality of successful outputs, Gemma 3 4B (0.80) would edge
out Phi-4 Mini (0.78). But Gemma delivered a valid output in 52% of cases, Phi in 64%.
**Averaging survivors is how most local-LLM demos mislead — including, until this evaluation,
mine.** Every aggregate number in this article therefore scores a failed case as zero. That
one policy choice is why the results below may look harsher than the local-model posts you're
used to — and why I trust them more.

## Why they failed

The failures decompose, and the decomposition is more useful than the totals. The **common
floor is context**: three of the four tasks feed a full-conversation selection that reaches
roughly 12–14K tokens on long conversations, which cannot fit an 8,192-token window — every
local model lost 21–30 cases to context length alone (the cloud control, with its much larger
window, lost none). The counter-evidence is the fourth task: **last activity** reads only
recent messages (~6–7K tokens), and it became the local sweet spot — Qwen 30/30 valid, Phi
29/30, Gemma 25/30, Llama 3B 23/30.

Above that floor, failure modes are model-specific. Qwen's failures were almost purely
context (29 of its 36). Gemma's title task collapsed structurally — 24 schema rejections, only
6 of 30 valid. Phi's title outputs stayed schema-valid but inverted the yes/no fit judgment —
a semantic failure. **Same task, opposite failure classes** — and you can't fix what you
haven't decomposed.

## The task × model matrix

| Task (each n=30) | Gemini (cloud) | Qwen3.5-4B | Phi-4 Mini | Llama 3.2 3B | Gemma 3 4B | Llama 3.2 1B |
|---|---|---|---|---|---|---|
| Summary | 23/30 · 72.9 | 17/30 · 56.7 | 14/30 · 39.1 | 12/30 · 37.1 | 12/30 · 38.7 | 16/30 · 37.1 |
| Work mode | 30/30 · 90.0 | 19/30 · 41.7 | 18/30 · 37.2 | 19/30 · 28.9 | 19/30 · 30.6 | 20/30 · 20.0 |
| Last activity | 29/30 · 91.5 | 30/30 · 89.1 | 29/30 · 77.8 | 23/30 · 47.4 | 25/30 · 76.3 | 14/30 · 17.2 |
| Title | 30/30 · 99.1 | 18/30 · 60.0 | 16/30 · 45.8 | 17/30 · 54.2 | 6/30 · 16.4 | 7/30 · 15.3 |

Cells: valid outputs / 30 · task score (0–100; whole-package task score where failures count
as zero — formula in the appendix).

Three reads. **One local model leads everywhere:** Qwen has the best local score on all four
tasks — I went looking for a per-task local routing story and found none. **Work mode is the
quality sink for everyone:** it produced the weakest judged quality of any task for all six
models — the only task where even the cloud control dropped meaningfully below its ceiling.
Distinguishing "managing" from "executing" in real, messy conversations is genuinely hard.
**And under these contracts Gemma 3 4B is a weak research comparator rather than a product
candidate** — its valid outputs score well, but 6-of-30 title validity rules it out as shipped
enrichment.

## Speed, honestly

| Model | p50 / case | 120-case wall span |
|---|---:|---:|
| Gemini 3.5 Flash (hosted) | 2.2s | 10m 40s |
| Llama 3.2 1B | 17.3s | 42m 13s |
| Llama 3.2 3B | 51.1s | 2h 21m |
| Phi-4 Mini | 54.6s | 2h 19m |
| Gemma 3 4B | 61.8s | 2h 08m |
| Qwen3.5-4B | 62.1s | 4h 43m* |

Every 3–4B model runs at p50 51–62s per case on this laptop — the speed belongs to the class,
not the model. The 1B floor is ~3× faster and unusable (see matrix). *Qwen's outlier wall
span is a tail story, not a speed story: 29 context failures failed fast (mean 1.8s), 84
successes took ~2h00m (mean 86s), and 5 timeouts consumed 2h39m — 8,857s of that in a single
case during a recorded overnight wrapper interruption. Excluding timeouts it lands at ~2h04m,
in line with its class. **Lesson: wall-clock is about tails and timeout policy, not
averages.** Hosted latency isn't comparable — different hardware, queueing, everything — so I
compare local to local. What it means for the actual workloads: backfilling my full archive
(711 conversations × 4 tasks) ≈ **2.8 days** of continuous laptop compute — impractical;
**incremental daily enrichment** — minutes per day, completely fine; interactive use on a 2s
budget — out of reach by ~30×.

> **[FIGURE 2 — secondary visual (optional if only one survives). Scatter, X = p50 case
> latency in seconds, log scale (2.2 → 62.1); Y = overall usable score (UTS, 0–100, appendix).
> Data (x, y): Gemini (2.2, 88.4) · Llama 1B (17.3, 22.4) · Llama 3B (51.1, 41.9) · Phi
> (54.6, 50.0) · Gemma (61.8, 40.5) · Qwen (62.1, 61.9). Annotate each point with its wall
> span; Qwen's annotated as "4h43m raw → ~2h04m excluding timeout tail".]**

## What I'd build

Not local *or* cloud — **local-first with an explicit cloud fallback on invalid output**. The
detection is free: schema validation is already the gate the product runs on every output. On
this evidence, a Qwen-local deployment would escalate 36 of 120 cases (30%) — by task: 13, 11,
0, and 12 of 30. Privacy framing stays honest: local by default, and the cloud becomes an
opt-in quality escape hatch the user controls per task — nobody is forced to choose between
"private" and "works". Two things I checked and rejected: routing *different local models* to
different tasks (one local model led everywhere), and the fast 1B floor in any role (fast
wrong answers are still wrong). One thing I'd adopt today: a per-task admission threshold —
last activity is the only task a local model passes at ≥80% validity right now, and it could
ship local-only.

## What's next — measured, not promised

Four hypotheses, none claimed until run: **(1)** re-run the best local model(s) at 16K
context as a new arm — context caused the largest share of failures, but I won't claim
expansion fixes anything until it's measured; **(2)** move generation to a stronger machine —
the harness already splits generation from scoring, and laptop results stay laptop-labeled;
**(3)** a versioned prompt study (schema-first, few-shot) on the top one or two locals against
the unchanged cloud control; **(4)** an untouched evaluation set — everything above is
development data, and I'll say so every time.

## Your turn

If you've shipped small local models behind strict output contracts: what reliability rate
did you see, and what did you fall back to? Chat Chronicle is open source — repo link in the
first comment.

---

## Appendix — detail on demand

### A. Full scorecard

| Model | Schema-valid /120 | Quality among valid (0–1) | Usable-output rate* | UTS | p50 | Wall span |
|---|---:|---:|---:|---:|---:|---:|
| Gemini 3.5 Flash (cloud control) | 112 (93.3%) | 0.966 | 88.3% | 88.4 | 2.2s | 10m 40s |
| Qwen3.5-4B | 84 (70.0%) | 0.887 | 60.8% | 61.9 | 62.1s | 4h 43m (decomposed above) |
| Phi-4 Mini | 77 (64.2%) | 0.780 | 47.5% | 50.0 | 54.6s | 2h 19m |
| Llama 3.2 3B | 71 (59.2%) | 0.755 | 39.2% | 41.9 | 51.1s | 2h 21m |
| Gemma 3 4B | 62 (51.7%) | 0.797 | 38.3% | 40.5 | 61.8s | 2h 08m |
| Llama 3.2 1B | 57 (47.5%) | 0.509 | 20.0% | 22.4 | 17.3s | 42m 13s |

*Usable-output rate: % of all 120 cases that produced a schema-valid output whose judged mean
was ≥3 of 4 — a plain pass rate, if you want one intuitive number.

### B. The UTS formula (Usable Task Score)

Per case: invalid output or no completed judge result → 0; otherwise the mean of the
applicable 1–4 rubric dimensions, normalized as (score − 1) / 3. Average the 30 cases within
each task; macro-average the four tasks; ×100. Failures count as zero **by design** — the
survivorship correction. It's a stated policy metric, not a scientific truth. The ranking is
unchanged under six alternative formulas (different normalization, judge-failure handling,
reliability × quality products, geometric/harmonic combinations); one near-tie (Llama 3B vs
Gemma, 1.4 points) is stable in direction but too close to headline. Judge failures (5 across
720 positions) also score zero and stay visible.

### C. Exact agreement with the silver references (n=30 per task)

Categorical tasks only; "no valid output" counts as a non-match. These measure agreement with
machine-generated silver development references — not correctness.

| Model | Work mode | Last-activity status | Title fit |
|---|---:|---:|---:|
| Gemini 3.5 Flash | 63.3% | 70.0% | 83.3% |
| Qwen3.5-4B | 33.3% | 60.0% | 56.7% |
| Phi-4 Mini | 10.0% | 60.0% | 16.7% |
| Llama 3.2 3B | 10.0% | 40.0% | 43.3% |
| Gemma 3 4B | 16.7% | 46.7% | 10.0% |
| Llama 3.2 1B | 3.3% | 20.0% | 6.7% |

### D. Failure taxonomy (counts per model, n=120)

- **Gemini 3.5 Flash (8):** invalid JSON 6, provider response 1, schema validation 1.
- **Qwen3.5-4B (36):** context length 29, timeout 5, schema validation 2.
- **Phi-4 Mini (43):** context length 21, schema validation 12, timeout 10.
- **Llama 3.2 3B (49):** context length 21, evidence validation 15, timeout 10, schema 3.
- **Gemma 3 4B (58):** context length 30, schema validation 24 (concentrated in title:
  24 of 30 title cases rejected), evidence 2, invalid JSON 1, timeout 1.
- **Llama 3.2 1B (63):** context length 21, evidence validation 16, schema 15, provider
  HTTP 10, invalid JSON 1.

Categorical failure shapes worth knowing: one model never predicted `executor` at all
(Llama 3B, reference support 14), one funnels uncertain cases into `mixed` (Phi), one
over-predicts `manager` (Gemma). The reference label set is skewed (executor 14, one-off 12,
manager 3, mixed 1), which caps what agreement numbers can say.

### E. Hardware, artifacts, and settings

4-core/8-thread 11th-gen Intel mobile CPU, ~32 GB RAM, integrated Iris Xe graphics (~2 GB
shared). LM Studio, llama.cpp Vulkan AVX2 engine; all local artifacts Q4_K_M GGUF (the
common mid-quality quantization a laptop user would realistically pick); context 8,192;
parallelism 1; temperature 0; task-owned output caps; zero retries. Cloud control via Vertex
AI. Judge: Gemini 3.1 Pro Preview, rubric v1, temperature 0, 1,000-token cap, blinded
candidate identity.

### F. Method commitments

Bounded development comparison on one person's frozen 30-conversation corpus; silver
development references; judge scores describe quality among successfully judged valid outputs
only; the judge shares a provider family with the cloud-control candidate — the observed
judge/reference disagreement is compatible with same-family preference but does not establish
it; hosted and local latency are not environment-comparable; all failures preserved,
none repaired or retried; development data throughout — an untouched evaluation set comes
later. Full evaluation harness and task contracts are in the open-source repo.
