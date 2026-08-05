# Same Small Model. Same 120 Tasks. From 70% to 99% Valid Outputs.

*What Qwen3.5-4B needed was not a better model. It was more room and more power.*

**TL;DR:** Same quantized Qwen3.5-4B, same 120 structured-extraction tasks from my
AI-conversation archive. Laptop: 84 of 120 valid outputs. A stronger machine at the same 8K
context: 89 — only the timeouts fixed. Maximum context on that machine: 119 — ahead of the
hosted control (112) on reliability and speed, with judged quality in the same band.
Compute and context fix different failures. You need both.

**Compute and context fix different failures, and neither was enough alone.** Faster
hardware cured the timeouts and nothing else. A bigger window on weak hardware cured
nothing at all. Together they took a small quantized model from 70% to 99% valid outputs on
the same 120 tasks. This article shows what each change fixed — and why both were needed.

## Where this picks up

In the previous article — [*Local LLMs Can Do the Job — Most of the Time*](https://www.linkedin.com/pulse/local-llms-can-do-job-most-time-tzur-vaich-xpd1e/) —
I benchmarked five small local models and one hosted control on 120 enrichment tasks from
**Chat Chronicle**, my open-source, local-first archive of AI conversations. The best local
model, Qwen3.5-4B (quantized, on an ordinary laptop), returned schema-valid output in 84 of
120 cases (70.0%), against 112 of 120 (93.3%) for Gemini 3.5 Flash. The conclusion was that
reliability, not quality, is the axis that decides a product — and reliability is where local
lost.

That article ended with two deliberately labelled hypotheses: a larger context window might
help, and stronger hardware might help. This is the measurement.

## The experiment

I ran the same evaluation on a much stronger machine — a cloud instance rented from
RunPod, with a single NVIDIA RTX 5090 (32 GB) : the same frozen 30 conversations, the same four tasks, the same model file
byte-for-byte, temperature 0, one request at a time. Two runs at the original 8,192-token
context, to check repeatability. One run at 262,144 tokens — the maximum context this model
advertises.

![Reliability progression across the four arms](figures/lp42-reliability-progression.svg)

*Schema-valid outputs per arm, n=120 each. The step from 84 to 89 is a faster execution
environment; the step from 89 to 119 is context.*

One note on infrastructure: the stronger machine is evaluation hardware, rented because I
own nothing in this class. My conversations were deliberately processed on it for this
evaluation only — the same way the benchmark uses a hosted model as its scoring judge. The
product's local-first design is unchanged.

## Step 1: stronger hardware, same window

At the same 8,192-token context, the stronger machine produced 89 of 120 valid outputs against
the laptop's 84 — twice: the repeat run matched the first on all 120 case outcomes.

The decomposition is more interesting than the total. On the laptop, the failures were 29
context-length rejections, 5 timeouts, and 2 schema failures. On the stronger machine, the 5
timeouts disappeared — those cases simply completed — and **exactly the same 29 context
failures remained**. Speed cannot admit an input the window rejects.

The speed change deserves its own line. **Laptop: 4 hours 43 minutes. Stronger machine:
just over two minutes — roughly 130 times faster.** For reference, the hosted control took
10 minutes 40 seconds on the same 120 cases. Both ends ran LM Studio; the difference was
what the software had to work with. The laptop offered a mobile CPU and integrated Intel
graphics with about 2 GiB of shared memory; the stronger machine offered a dedicated 32 GB
GPU. Two footnotes, once, here: the laptop figure includes a long timeout tail — excluding
it, the comparison is still about 57 times faster — and the two setups also differ in
operating system and LM Studio version, so this is an environment comparison, not a
controlled GPU benchmark.

![Wall time for the full 120-case run](figures/lp42-wall-time.svg)

## Step 2: bigger window, same laptop

I had already tested the other hypothesis in isolation on the laptop and [posted about it recently](https://www.linkedin.com/posts/tzurvaich_localllm-llmevaluation-aiengineering-activity-7488892478016782337-snby): raising the local context window from 8K to 16K recovered
**nothing**. All 29 context-length rejections turned into timeouts instead. The
error label changed; the outcome did not. Valid outputs stayed at 84 of 120, and the median
case time nearly doubled.

Capacity without the compute to process it does not fix anything — it converts a fast
failure into a slow one.

## Step 3: capacity and compute together

On the stronger machine, I then raised the context from 8,192 to 262,144 — the model's maximum
— with everything else unchanged, in the same session.

Valid outputs went from 89 of 120 to **119 of 120**: all 29 context-length failures
recovered, plus one other case. Nothing regressed — every output already valid at 8K came
back **structurally identical** at maximum context. The change was surgical. Its price: 40
additional seconds on the full run, and peak observed GPU memory rising from 4,219 MiB to
11,896 MiB. One schema-validation failure remained — the one
failure a bigger window could not fix.

One boundary, stated once: 262K is the maximum-context reference point, not a proven
minimum. I did not run 16K or 32K on this hardware; an intermediate setting might buy the
same reliability for less memory.

## Against the hosted control

The maximum-context run and the hosted Gemini control were evaluated on the same 120 cases —
same inputs, prompts, schemas, references, judge, and rubric. Three comparisons, kept
separate:

**Reliability.** Qwen: 119 of 120. Gemini: 112 of 120. On the metric my product actually
stores — a schema-valid output — the local model now leads.

**Speed.** 169 seconds versus 639.5 seconds for the same serial workload, about 3.8 times
faster — a dedicated, warmed-up GPU against a managed hosted endpoint, an observed result
for these runs, not a provider throughput claim.

**Quality.** Here the two are close. On the 110 cases where both arms have completed judge
verdicts, the fixed judge scored Gemini 3.892 of 4 and Qwen 3.830 of 4 — the same band on a
0–4 rubric. The clearer separation is in classification agreement, where Gemini led all
three measures, largest on the last-activity task (70.0% versus 53.3%, n=30). The judge and
reference labels are evaluation instruments, not ground truth — but the direction is
consistent: the small remaining edge belongs to Gemini.

The honest summary: **the small local model with the right resources matches the hosted
control where it counts for this product, beats it on speed, and lands in the same quality
band — with the remaining edge to Gemini.**

## The memory envelope

The most useful output of this study is not the score. It is the envelope.

The previous article could only say my laptop was not enough. This study can say what the
workload actually consumed at full context: a peak below 12 GiB of GPU memory, with the full
120-case run finishing in under three minutes. That is a smaller memory footprint than
I expected — and it makes an ordinary 16 GB consumer card a credible candidate to test.

## What this is, and is not

The same discipline as last time. This is development evidence: 30 real conversations from
my own archive, four tasks, 120 cases — not a representative public benchmark. One model
artifact, one quantization, one hardware allocation; a repeated pair at 8K and a single
maximum-context run. Temperature 0 made the runs highly repeatable, not deterministic: the
two 8K runs agreed on all 120 outcomes, but 4 of 89 shared valid outputs differed
structurally, and the judge occasionally re-scored identical outputs differently (details in
the appendix). Generalize accordingly.

## Where this leaves the project

The previous article ended with two hypotheses. Both are now measured, and the answer was
neither of them alone. Hardware fixed the timeouts. Context fixed the capacity. Only
together did they take the same 4B model from 70% to 99% valid outputs on the same work —
with judged quality landing in the same band as the hosted control — the remaining edge
Gemini's, honestly reported.

The open question has changed shape. It is no longer whether this local model can do this
job. It is whether hardware inside that envelope earns a place on my desk — and that is a
purchase decision I intend to make the same way I have made every other decision in this
project: measured first.

---

## Appendix — detail on demand

### A. Arm-by-arm summary

| Arm | Context / environment | Schema-valid | Wall time | p50 / p95 | Semantic score (denominator) |
|---|---|---:|---:|---:|---:|
| Local Qwen 8K | 8,192; Windows laptop, 11th-gen mobile CPU, iGPU | 84/120 (70.0%) | 4 h 43 m (decomposed: ≈2 h 04 m excl. timeout tail) | 62.1 s / 168.4 s | 0.887 quality among valid, 0–1 macro (84 verdicts; previous study's convention) |
| Remote R8 (original / repeat) | 8,192; rented RTX 5090 | 89/120 (74.2%) both | 131 s / 129 s | 916/1,375 ms; 905/1,356 ms | 3.813/4; 3.815/4 (89 verdicts each) |
| Remote R262K | 262,144; same machine and session | 119/120 (99.2%) | 169 s | 1,196 / 2,081 ms | 3.846/4 (118 verdicts) |
| Gemini 3.5 Flash | hosted (Vertex AI) | 112/120 (93.3%) | 639.5 s | 2,156 / 12,562 ms | 3.905/4 (110 verdicts) |

*Aggregation note: the semantic column above uses each arm's own overall completed-verdict
mean. Table C below restricts to the 110 cases completed in both compared arms and uses
case-normalized means — hence Gemini appears as 3.905 here and 3.892 there. Both are
correct; the conventions differ.*

### B. Failure boundaries

| Arm | Context length | Timeout | Schema | Invalid JSON | Provider | Total failed |
|---|---:|---:|---:|---:|---:|---:|
| Local 8K | 29 | 5 | 2 | 0 | 0 | 36 |
| Local 16K | 0 | 35 | 1 | 0 | 0 | 36 |
| Remote 8K (both runs) | 29 | 0 | 1 | 1 | 0 | 31 |
| Remote 262K | 0 | 0 | 1 | 0 | 0 | 1 |
| Gemini | 0 | 0 | 1 | 6 | 1 | 8 |

### C. Matched semantic comparison (110 cases completed in both arms)

| Task | n | Qwen 262K | Gemini |
|---|---:|---:|---:|
| Conversation summary | 22 | 3.955 | 3.982 |
| Last activity | 28 | 3.804 | 3.940 |
| Title assessment | 30 | 3.900 | 3.973 |
| Work-mode classification | 30 | 3.692 | 3.700 |
| **All matched cases** | **110** | **3.830** | **3.892** |

### D. Repeatability at temperature 0

The two remote 8K runs matched on all 120 terminal outcomes and reproduced the identical
failure set. Among the 89 shared valid outputs, 85 were structurally identical and 4 changed
— exactly one in each task. Separately, 4 of the 85 identical outputs received a different
score from fresh judging. High repeatability; not determinism.

### E. Telemetry note

Peak sampled GPU memory: 4,219 MiB at 8K, 11,896 MiB at 262K, on this runtime, sampled every
two seconds during generation. These are cloud-machine samples, not consumer-desktop power,
thermal, or acoustic measurements.

---

*Chat Chronicle repository: link in comments.*
