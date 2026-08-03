# WP-5.2B3A Context Comparison: Article Evidence Brief

## Publication status

**Publication-ready evidence brief.** Candidate, deterministic, transition,
performance, resource, authorized fixed-Pro judging, and byte-stable
cache-replay evidence is complete. Article drafting and graphics remain
separate activities.

## 1. Research question

On the same 30-conversation, 120-case private development scope, what changes
when the only effective variable for Qwen3.5-4B and Phi-4 Mini is local context
capacity from 8,192 to 16,384 tokens? Specifically: does 16K recover context
failures into useful outputs without unacceptable reliability, semantic,
latency, token, or memory cost?

## 2. Why context came before prompt optimization

At 8K, context-length rejection accounted for 29/36 Qwen failures and 21/43
Phi failures. Prompt tuning on that unresolved structural floor would mix two
causes: capacity and prompt behavior. Testing context first isolates capacity;
WP-5.2B3B can then optimize one global prompt at one frozen common context.

The later prompt holdout is conditional on this context choice. It is not an
independent validation of the context decision because all 30 conversations
were used here.

## 3. Pre-result hypotheses

Recorded before results:

1. 16K should remove or reduce 8K context failures.
2. Some context-failed cases may become useful, but capacity alone should not
   fix semantic weaknesses.
3. Latency and memory cost should rise when long inputs no longer fail fast.
4. New timeouts or other regressions are possible.
5. Context may explain part, but not all, of the local/cloud gap.

Observed: hypothesis 1 was only partly true at the failure-label level and
false at the useful-output level. Qwen removed the context label but recovered
none of those cases; Phi retained 11 and recovered none. Hypotheses 2–5 remain
consistent with the local evidence.

## 4. Controlled variables

Held constant per model:

- ordered 30 conversations and 120 case identities;
- selected inputs and FABLE references;
- model family, exact GGUF bytes/revision, Q4_K_M quantization;
- LM Studio CLI and accepted inference engine;
- execution device/offload policy and parallelism one;
- task prompts, versions, selectors, schemas, and finalizers;
- temperature, task token caps, timeout, retry, and reasoning policy;
- structured-output request contract;
- model-specific accepted benchmark revision and package format.

Only effective change: `context_window: 8192 -> 16384`. Pair validation passed
for both models.

## 5. Hardware, runtime, and model provenance

| Field | Evidence |
|---|---|
| Host class | Windows 11 Pro laptop; 4-core/8-thread 11th-generation Intel mobile CPU; ~32 GiB RAM; integrated Intel Iris Xe |
| Runtime | LM Studio CLI `9902c3a`; accepted llama.cpp Vulkan AVX2 engine 2.25.2 |
| Execution | local loopback; automatic device/offload; parallelism one; no dedicated VRAM reported |
| Qwen | exact accepted Qwen3.5-4B Q4_K_M artifact; 16K load 34.23s |
| Phi | exact accepted Phi-4 Mini Instruct Q4_K_M artifact; 16K load 11.81s |

Exact hashes, paths, machine identity, and private authorities remain private.

## 6. Accepted 8K baseline table

| Model | Valid/120 | Summary/mode/activity/title | Failures | Overall p50/p95 | Valid-output quality | Macro UTS |
|---|---:|---|---|---:|---:|---:|
| Qwen | 84 (70.0%) | 17/19/30/18 | context 29; timeout 5; schema 2 | 62.094/168.375s | 0.887 (84 judged) | 61.9 |
| Phi | 77 (64.2%) | 14/18/29/16 | context 21; timeout 10; schema 12 | 54.608/180.031s | 0.780 (77 judged) | 50.0 |

## 7. New 16K result table

| Model | Valid/120 | Summary/mode/activity/title | Failures | Overall p50/p95 | New fixed judge | Candidate result |
|---|---:|---|---|---:|---|---|
| Qwen | 84 (70.0%) | 17/20/28/19 | timeout 35; schema 1 | 117.039/180.093s | 84/84 completed | complete/verified |
| Phi | 69 (57.5%) | 14/17/23/15 | context 11; provider HTTP 14; timeout 15; schema 11 | 59.250/180.077s | 68/69 completed; 1 terminal failure | complete/verified |

Combined validity fell from 161/240 (67.1%) to 153/240 (63.8%).

## 8. Chart-ready task validity

Each cell denominator is 30.

| Model | Context | Summary | Work mode | Last activity | Title | Total valid |
|---|---:|---:|---:|---:|---:|---:|
| Qwen | 8K | 17 | 19 | 30 | 18 | 84 |
| Qwen | 16K | 17 | 20 | 28 | 19 | 84 |
| Phi | 8K | 14 | 18 | 29 | 16 | 77 |
| Phi | 16K | 14 | 17 | 23 | 15 | 69 |

## 9. Chart-ready failure decomposition

Each row totals 120 when valid is included.

| Model/context | Valid | Context | Timeout | Schema | Provider HTTP | Other |
|---|---:|---:|---:|---:|---:|---:|
| Qwen 8K | 84 | 29 | 5 | 2 | 0 | 0 |
| Qwen 16K | 84 | 0 | 35 | 1 | 0 | 0 |
| Phi 8K | 77 | 21 | 10 | 12 | 0 | 0 |
| Phi 16K | 69 | 11 | 15 | 11 | 14 | 0 |

Interpretation: removing a context-length label is not the same as recovering a
usable output. Qwen's 29 former context failures all became timeouts.

## 10. Chart-ready 120-case transition matrices

| Model | 8K invalid→16K invalid | Invalid→valid | Valid→invalid | Valid→valid | Total |
|---|---:|---:|---:|---:|---:|
| Qwen | 32 | 4 | 4 | 80 | 120 |
| Phi | 42 | 1 | 9 | 68 | 120 |

Per task:

| Model/task | I→I | I→V | V→I | V→V |
|---|---:|---:|---:|---:|
| Qwen summary | 11 | 2 | 2 | 15 |
| Qwen mode | 10 | 1 | 0 | 19 |
| Qwen activity | 0 | 0 | 2 | 28 |
| Qwen title | 11 | 1 | 0 | 18 |
| Phi summary | 15 | 1 | 1 | 13 |
| Phi mode | 12 | 0 | 1 | 17 |
| Phi activity | 1 | 0 | 6 | 23 |
| Phi title | 14 | 0 | 1 | 15 |

Failure flows:

- Qwen: context→timeout 29; schema→schema 1; schema→valid 1;
  timeout→timeout 2; timeout→valid 3; valid→timeout 4.
- Phi: context→context 11; context→provider-HTTP 4; context→timeout 6;
  schema→schema 11; schema→timeout 1; timeout→provider-HTTP 4;
  timeout→timeout 5; timeout→valid 1; valid→provider-HTTP 6;
  valid→timeout 3.

## 11. Recovered-context-case aggregates

| Model | 8K context failures | Context→valid at 16K | Context→different failure | Context→context | Judge quality |
|---|---:|---:|---:|---:|---|
| Qwen | 29 | 0 | 29 | 0 | N/A, n=0 |
| Phi | 21 | 0 | 10 | 11 | N/A, n=0 |

There is no recovered-context semantic cohort. The four Qwen and one Phi
invalid→valid transitions originated from non-context 8K failures.

## 12. Deterministic semantic metrics

All agreement denominators are 30; `no valid output` remains a prediction
outcome.

| Model/context | Summary date/length valid | Mode agreement | Activity agreement | Title-fit agreement | Title suggestion valid |
|---|---:|---:|---:|---:|---:|
| Qwen 8K | 17/17 | 33.3% | 60.0% | 56.7% | 18 |
| Qwen 16K | 17/17 | 36.7% | 56.7% | 60.0% | 19 |
| Phi 8K | 14/14 | 10.0% | 60.0% | 16.7% | 15 |
| Phi 16K | 14/14 | 10.0% | 50.0% | 16.7% | 14 |

These are agreement with FABLE silver references, not accuracy.

## 13. Fixed-judge semantic metrics

| Model/context | Eligible | Completed | Failed | Skipped invalid | Valid-output quality | Macro UTS |
|---|---:|---:|---:|---:|---:|---:|
| Qwen 8K | 84 | 84 | 0 | 36 | 0.887 | 61.9 |
| Qwen 16K | 84 | 84 | 0 | 36 | 0.935 | 65.2 |
| Phi 8K | 77 | 77 | 0 | 43 | 0.780 | 50.0 |
| Phi 16K | 69 | 68 | 1 | 51 | 0.791 | 44.8 |

Task UTS:

| Model/context | Summary | Mode | Activity | Title | Macro |
|---|---:|---:|---:|---:|---:|
| Qwen 8K | 56.7 | 41.7 | 89.1 | 60.0 | 61.9 |
| Qwen 16K | 56.7 | 56.4 | 85.6 | 62.0 | 65.2 |
| Phi 8K | 39.1 | 37.2 | 77.8 | 45.8 | 50.0 |
| Phi 16K | 40.7 | 36.1 | 64.8 | 37.8 | 44.8 |

Each value below is a mean over successfully judged outputs:

| Arm/task | Dimension means and denominators |
|---|---|
| Qwen 16K summary | concise usefulness 4.000 (17); conversation characterization 4.000 (17); factual consistency 4.000 (17); material coverage 4.000 (17); unsupported-claim avoidance 4.000 (17) |
| Qwen 16K mode | label support 3.300 (20); mode distinction 3.300 (20); reason specificity 3.650 (20); unsupported-claim avoidance 3.900 (20) |
| Qwen 16K activity | blocker correctness 3.857 (28); final meaningful activity 3.964 (28); next-action support 3.214 (28); not-source-copying 4.000 (28); status correctness 3.500 (28); unsupported-claim avoidance 3.964 (28) |
| Qwen 16K title | dominant-activity fit 3.895 (19); suggestion-only compliance 4.000 (19); suggestion usefulness 3.789 (19); title-fits correctness 4.000 (19); unsupported-claim avoidance 4.000 (19) |
| Phi 16K summary | concise usefulness 3.643 (14); conversation characterization 3.214 (14); factual consistency 4.000 (14); material coverage 3.214 (14); unsupported-claim avoidance 4.000 (14) |
| Phi 16K mode | label support 2.647 (17); mode distinction 2.647 (17); reason specificity 2.941 (17); unsupported-claim avoidance 3.412 (17) |
| Phi 16K activity | blocker correctness 4.000 (23); final meaningful activity 3.261 (23); next-action support 3.043 (23); not-source-copying 3.696 (23); status correctness 3.304 (23); unsupported-claim avoidance 3.913 (23) |
| Phi 16K title | dominant-activity fit 3.143 (14); suggestion-only compliance 4.000 (14); suggestion usefulness 3.571 (14); title-fits correctness 2.429 (14); unsupported-claim avoidance 4.000 (14); one additional eligible judge failed |

The fixed contract was Gemini 3.1 Pro Preview, rubric v1, blinded model
identity, temperature zero, selected input plus candidate plus fixed FABLE
reference. The synthetic gate passed 4/4. Qwen completed 84/84; Phi completed
68/69 and preserved one terminal `output_schema` failure. Cache-only replay
made zero new calls and left 84 and 69 attempt trees byte-identical.

## 14. Formulas and denominators

Valid-output quality:

1. For each successfully judged valid output, average applicable rubric
   dimensions after normalizing each 1–4 score with `(score - 1) / 3`.
2. Average within task over judged valid outputs.
3. Macro-average the four task means.
4. Always publish beside valid rate and judged `n`; survivors are not the full
   package.

UTS formula v1:

1. Give a case zero when candidate output is invalid/absent or judge scoring
   does not complete.
2. Otherwise use the normalized applicable-dimension mean above.
3. Average all 30 cases within each task.
4. Macro-average four tasks and multiply by 100.

Latency is never combined into UTS. A judge score of 1 receives zero credit,
which is why normalization is `(s - 1) / 3`, not `s / 4`.

## 15. Latency, wall time, tokens, and memory

| Model/context | Wall span | p50/p95 | Timeouts (duration) | Observed total tokens; availability |
|---|---:|---:|---:|---:|
| Qwen 8K | 4h43m30.782s | 62.094/168.375s | 5 (2h39m37.355s) | 257,906; 86/120 |
| Qwen 16K | 3h56m20.700s | 117.039/180.093s | 35 (1h45m02.344s) | 250,072; 85/120 |
| Phi 8K | 2h18m50.713s | 54.608/180.031s | 10 (30m00.589s) | 246,977; 89/120 |
| Phi 16K | 2h31m30.816s | 59.250/180.077s | 15 (45m01.603s) | 210,640; 80/120 |

Qwen 8K's raw wall span includes an 8,857s interruption/timeout tail. Excluding
timeout durations, its summed latency was about 2h04m versus about 2h11m for
Qwen 16K. Never chart or headline the raw Qwen 8K span without that
decomposition.

Observed token totals are not full-arm totals because usage is absent on many
failure paths. They are comparable only cautiously within the same model and
tokenizer; do not compare them across hosted/local tokenizers.

| 16K arm | Samples | Peak system-used RAM | Peak LM Studio process-group working set | Peak shared/dedicated GPU memory |
|---|---:|---:|---:|---:|
| Qwen | 2,276 | 31.35 GiB | 9.65 GiB | 4.13/0 GiB |
| Phi | 1,426 | 31.71 GiB | 12.87 GiB | 4.50/0 GiB |

System and process-group values are not model-exclusive. Comparable 8K peaks
were not recorded. GPU utilization percentage is unavailable because the
Windows counter produced values above 100%.

## 16. Unchanged Gemini reference

| Control | Valid | Macro UTS | Status |
|---|---:|---:|---|
| Gemini 3.5 Flash | 112/120 (93.3%) | 88.4 | unchanged historical cloud control; not regenerated in WP-5.2B3A |

Context alone did not close the local/cloud reliability gap. Do not compare
local and cloud latency as equivalent hardware measurements.

## 17. Context-policy recommendation

Recommend **common 8K** for WP-5.2B3B.

Reasons:

- combined valid count fell by eight;
- neither model recovered an 8K context failure into a valid 16K result;
- Qwen's reliability stayed flat while p50 nearly doubled;
- Phi materially regressed in reliability and activity agreement;
- 13 previously valid cases became invalid across both models;
- no memory/OOM crash occurred, but long-tail operational cost remained high.

The completed fixed-judge layer does not reverse the policy result: Qwen's UTS
rose 3.3 points while reliability stayed flat and p50 rose sharply; Phi's UTS
fell 5.1 points alongside its reliability regression.

## 18. Claims supported by evidence

- Under this frozen private 120-case contract, 16K did not improve combined
  structured-output reliability.
- A larger configured context can change failure category without producing a
  valid output.
- Qwen removed context-length failures but replaced them with timeouts.
- Phi's 16K reliability was lower than its 8K reliability.
- Context is not the sole explanation for the local/cloud reliability gap.
- Reliability, quality among valid survivors, and runtime cost must be
  reported separately.
- Qwen's quality among valid survivors improved at 16K, but this did not
  represent recovery of any context-failed case.
- Phi's survivor quality was nearly flat while whole-case UTS fell because
  fewer outputs remained usable and one judge result failed.
- Common 8K is the better tested input to the next prompt study.

## 19. Prohibited claims

Do not claim:

- 8K or 16K is universally better or optimal;
- model accuracy or ground truth;
- a schema-valid output is automatically correct;
- context alone closes the cloud gap;
- remote WP-5.2C1 speed is local B3A speed;
- prompt tuning produced a B3A improvement;
- consumer-hardware generalization;
- statistical significance.

## 20. Limitations

- private real-work development corpus;
- 30 conversations/120 cases;
- FABLE silver references;
- fixed Gemini-family judge and one terminal Phi judge-schema failure;
- same corpus used to select context;
- one Windows laptop;
- one Q4_K_M quantization per model;
- one LM Studio runtime contract;
- no untouched context holdout;
- no statistical/general-population claim;
- only 8K and 16K tested;
- no evidence yet that prompt gains will generalize;
- no comparable historical 8K peak-memory sampling;
- Qwen resource sampling missed roughly the first three minutes;
- GPU utilization percentage telemetry was invalid;
- provider-HTTP is retained as observed failure accounting without a broader
  causal claim.

## 21. Chart-ready aggregate tables

### Reliability/quality two-axis

| Arm | Valid rate | Valid-output quality | UTS | Judge status |
|---|---:|---:|---:|---|
| Qwen 8K | 0.700 | 0.887 | 61.9 | accepted |
| Qwen 16K | 0.700 | 0.935 | 65.2 | completed |
| Phi 8K | 0.642 | 0.780 | 50.0 | accepted |
| Phi 16K | 0.575 | 0.791 | 44.8 | 68 completed, 1 terminal failure |

### Runtime cost versus valid-case gain

| Model | Valid gain at 16K | p50 change | p95 change | Wall-span change | Timeout-count change |
|---|---:|---:|---:|---:|---:|
| Qwen | 0 | +54.945s | +11.718s | -47m10.082s, raw tail-sensitive | +30 |
| Phi | -8 | +4.642s | +0.046s | +12m40.103s | +5 |

### Combined policy view

| Context | Valid | Invalid | Valid rate | Context failures |
|---|---:|---:|---:|---:|
| 8K | 161 | 79 | 67.1% | 50 |
| 16K | 153 | 87 | 63.8% | 11 |

## 22. Proposed article observations

1. **Capacity labels can disappear without reliability improving.** Qwen
   changed 29 context errors into 29 timeouts and gained zero valid cases.
2. **Paired transition analysis beats aggregate intuition.** Aggregate Qwen
   validity was flat, but four recoveries and four regressions occurred
   underneath it.
3. **A shared context policy must satisfy the weaker operational arm.** Phi
   lost eight valid cases and six activity outputs at 16K.
4. **Survivorship and whole-package utility can move differently.** Qwen's
   valid-output quality rose 0.887→0.935 and UTS rose 61.9→65.2 despite flat
   reliability; Phi's survivor quality moved only 0.780→0.791 while UTS fell
   50.0→44.8. Valid quality must stay paired with reliability and UTS.
5. **Structural controls should precede prompt tuning.** This study removes
   context as a plausible easy explanation before WP-5.2B3B.

## 23. Headline directions

- “A Bigger Context Window Removed the Error Label, Not the Failure”
- “Why We Tested Context Before Touching the Prompt”
- “From Aggregate Scores to Case Transitions: What 240 Paired Runs Revealed”
- “16K Was More Capacity—and Less Reliability—on One Local Model”

## 24. Suggested article outline

1. Product problem: enrichment must be both valid and useful.
2. Why the 8K context-failure floor was tested first.
3. Experimental contract: two models, paired cases, one effective change.
4. Reliability results and failure-category shifts.
5. Case transitions: recoveries, regressions, and the zero recovered-context
   cohort.
6. Deterministic semantics and the fixed-judge framework.
7. Latency, timeout, token, and memory cost.
8. Why common 8K is the next-study policy.
9. Limitations and what prompt optimization can—and cannot—test next.

## 25. Suggested figures

1. Grouped bars: 8K versus 16K valid cases by model and task.
2. Stacked bars: valid plus failure categories before/after.
3. Two Sankey or 2×2 matrices: paired validity transitions per model.
4. Reliability-versus-valid-output-quality scatter with final UTS labels.
5. Runtime-cost-versus-valid-gain plot using p50, wall decomposition, and
   timeout annotations.

Do not produce final graphics until requested.

## 26. Evidence links

- [WP-5.2B3A completion report](WP-5.2B3A-completion-report.md)
- [Accepted Qwen baseline report](WP-5.2B1.4-completion-report.md)
- [Accepted Phi baseline report](WP-5.2B2.2-completion-report.md)
- [Accepted analysis/UTS brief](LP-4.1-local-model-results-analysis-brief.md)
