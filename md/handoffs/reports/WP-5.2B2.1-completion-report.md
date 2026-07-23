# WP-5.2B2.1 Completion Report

## 1. Status and executive summary

Ready for PM validation.

All three 40-case local candidate packages completed, verify immutably, and score
deterministically. Candidate accounting is 120 terminal positions with zero unaccounted. Phi-4
Mini and Llama 3.2 3B each produced 26/40 schema-valid outputs (65.0%); Gemma 3 4B produced 23/40
(57.5%).

The initial judge wave failed because absent local location aliases routed the application client
away from the required Vertex `global` location. After synthetic diagnosis and separate owner
recovery authorization, the identical fixed route completed 74/75 eligible cases: Phi 26/26,
Llama 26/26, and Gemma 22/23. Gemma retains one terminal provider-invalid-JSON failure after the
single bounded retry. Three cache-only replays exited zero with zero calls and byte-stable
evidence. No substitute judge or 120-case arm was used.

## 2. Clean preflight and immutable baseline evidence

Execution began from clean HEAD `05dfc73f4401ff253f5559fd5058a56aa9a0dc83`. Poetry resolved
to the repository `.venv`. The frozen database passed immutable read-only integrity validation at
schema version 3 with 711 conversations and 28,370 messages and no WAL/SHM sidecars.

Frozen/live database and snapshot-manifest identities were recorded privately. Six accepted
historical/current packages independently matched their checksum identities. Approximately
283.5 GB was free; execution used AC power and AC sleep was disabled.

## 3. Exact 40-case identity reconciliation

Each arm independently reconstructed the same frozen-prefix-v1 scope: 10 conversations, four
tasks in the accepted order, and 40 unique ordered aliases. All three report the same private
frozen-prefix identity as accepted WP-5.2B1.3 and Qwen-40. No historical package was repackaged.

## 4. Authorization boundary

The owner authorized up to 120 baseline fixed-Pro cases plus configured bounded retries, using
ADC, Vertex AI `global`, `gemini-3.1-pro-preview`, and rubric v1. Candidate generation remained
local. Judging stayed within the authorized inputs, candidate outputs, FABLE references, model,
region, authentication route, and disclosure contents.

## 5. Common model/task/settings contract

All candidates used their accepted pinned LM Studio Community Q4_K_M artifacts, LM Studio CLI
commit `9902c3a`, llama.cpp Vulkan AVX2 engine 2.25.2, context 8,192, parallelism/concurrency 1,
temperature 0, retries 0, strict structured output, and task-owned output limits. Independent
pre-load byte-size and SHA-256 checks matched every private pin. Loaded identifiers were Phi-4
Mini Instruct, Llama 3.2 3B Instruct, and Gemma 3 4B IT. Gemma 4 was not loaded or probed.

## 6. Phi generation, package, deterministic, judge, and cache evidence

- Candidate: 40 terminal; 26 valid; 14 failed; zero unaccounted.
- Failures: six context-length and eight schema-validation outcomes.
- Task validity (summary/mode/activity/title): 5/6/9/6.
- Evidence-valid and cross-field-valid: 26/26.
- Deterministic exact agreement (mode/activity/title): 20%/50%/30%.
- Judge: 26 eligible; 26 completed; 0 failed; 14 skipped invalid.
- Attempts: 52 original model-not-found attempts plus 26 authorized recovery attempts.
- Cache-only replay: exit zero, zero calls, unchanged accounting.

## 7. Llama 3B evidence

- Candidate: 40 terminal; 26 valid; 14 failed; zero unaccounted.
- Failures: six context-length and eight evidence-validation outcomes.
- Task validity (summary/mode/activity/title): 4/8/6/8.
- Evidence-valid and cross-field-valid: 26/26.
- Deterministic exact agreement (mode/activity/title): 20%/30%/70%.
- Judge: 26 eligible; 26 completed; 0 failed; 14 skipped invalid.
- Attempts: 52 original model-not-found attempts plus 26 authorized recovery attempts.
- Cache-only replay: exit zero, zero calls, unchanged accounting.

Schema-valid awkward values were preserved without repair or reinterpretation.

## 8. Gemma 3 evidence

- Candidate: 40 terminal; 23 valid; 17 failed; zero unaccounted.
- Failures: six context-length, two evidence-validation, and nine schema-validation outcomes.
- Task validity (summary/mode/activity/title): 5/8/6/4.
- Evidence-valid and cross-field-valid: 23/23.
- Deterministic exact agreement (mode/activity/title): 30%/20%/20%.
- Judge: 23 eligible; 22 completed; 1 terminal provider-invalid-JSON failure; 17 skipped invalid.
- Attempts: 46 original model-not-found attempts, 23 recovery attempts, and one bounded retry.
- Cache-only replay: exit zero, zero calls, unchanged accounting.

## 9. 120-position accounting

| Candidate | Expected | Valid | Failed | Terminal | Unaccounted |
|---|---:|---:|---:|---:|---:|
| Phi-4 Mini | 40 | 26 | 14 | 40 | 0 |
| Llama 3.2 3B | 40 | 26 | 14 | 40 | 0 |
| Gemma 3 4B | 40 | 23 | 17 | 40 | 0 |
| **Total** | **120** | **75** | **45** | **120** | **0** |

## 10. Three-arm checkpoint comparison

| Candidate | Valid rate | Summary | Mode | Activity | Title | Judge completed/eligible |
|---|---:|---:|---:|---:|---:|---:|
| Phi-4 Mini | 65.0% | 5/10 | 6/10 | 9/10 | 6/10 | 26/26 |
| Llama 3.2 3B | 65.0% | 4/10 | 8/10 | 6/10 | 8/10 | 26/26 |
| Gemma 3 4B | 57.5% | 5/10 | 8/10 | 6/10 | 4/10 | 22/23 |

This is a bounded checkpoint, not a complete-arm leaderboard.

## 11. Historical same-prefix context

Accepted same-prefix schema validity was Gemini 3.5 Flash 39/40, Llama 3.2 1B 21/40, and
Qwen3.5 4B 34/40. Historical Pro scores were produced in an earlier preview-model run window.
They provide context only and are not combined with this recovery-window checkpoint.

## 12. Deterministic confusion and per-label metrics

Rows are FABLE labels and columns are candidate outputs including `NVO` (no valid output).

### Phi-4 Mini

| Work mode | executor | manager | mixed | one-off | unknown | NVO |
|---|---:|---:|---:|---:|---:|---:|
| executor | 0 | 0 | 0 | 0 | 0 | 3 |
| manager | 0 | 0 | 1 | 0 | 0 | 0 |
| mixed | 0 | 0 | 0 | 0 | 0 | 0 |
| one-off | 0 | 0 | 2 | 2 | 1 | 1 |

| Last activity | awaiting | blocked | completed | in progress | unknown | NVO |
|---|---:|---:|---:|---:|---:|---:|
| awaiting | 0 | 0 | 0 | 2 | 0 | 0 |
| blocked | 0 | 0 | 0 | 0 | 0 | 0 |
| completed | 0 | 0 | 3 | 0 | 1 | 1 |
| in progress | 0 | 0 | 1 | 2 | 0 | 0 |

| Title fit | false | true | NVO |
|---|---:|---:|---:|
| false | 1 | 0 | 2 |
| true | 3 | 2 | 2 |

### Llama 3.2 3B

| Work mode | executor | manager | mixed | one-off | unknown | NVO |
|---|---:|---:|---:|---:|---:|---:|
| executor | 0 | 0 | 1 | 0 | 0 | 2 |
| manager | 0 | 0 | 1 | 0 | 0 | 0 |
| mixed | 0 | 0 | 0 | 0 | 0 | 0 |
| one-off | 0 | 0 | 4 | 2 | 0 | 0 |

| Last activity | awaiting | blocked | completed | in progress | unknown | NVO |
|---|---:|---:|---:|---:|---:|---:|
| awaiting | 1 | 0 | 0 | 0 | 0 | 1 |
| blocked | 0 | 0 | 0 | 0 | 0 | 0 |
| completed | 0 | 0 | 0 | 3 | 0 | 2 |
| in progress | 0 | 0 | 0 | 2 | 0 | 1 |

| Title fit | false | true | NVO |
|---|---:|---:|---:|
| false | 1 | 1 | 1 |
| true | 0 | 6 | 1 |

### Gemma 3 4B

| Work mode | executor | manager | mixed | one-off | unknown | NVO |
|---|---:|---:|---:|---:|---:|---:|
| executor | 0 | 0 | 1 | 0 | 0 | 2 |
| manager | 0 | 1 | 0 | 0 | 0 | 0 |
| mixed | 0 | 0 | 0 | 0 | 0 | 0 |
| one-off | 0 | 3 | 1 | 2 | 0 | 0 |

| Last activity | awaiting | blocked | completed | in progress | unknown | NVO |
|---|---:|---:|---:|---:|---:|---:|
| awaiting | 1 | 0 | 0 | 0 | 0 | 1 |
| blocked | 0 | 0 | 0 | 0 | 0 | 0 |
| completed | 0 | 0 | 1 | 3 | 0 | 1 |
| in progress | 0 | 0 | 1 | 0 | 0 | 2 |

| Title fit | false | true | NVO |
|---|---:|---:|---:|
| false | 0 | 0 | 3 |
| true | 2 | 2 | 3 |

Exact agreement and per-label precision/recall/support:

| Candidate | Work mode | Last activity | Title fit |
|---|---:|---:|---:|
| Phi-4 Mini | 20% | 50% | 30% |
| Llama 3.2 3B | 20% | 30% | 70% |
| Gemma 3 4B | 30% | 20% | 20% |

| Candidate/task/label | Precision | Recall | Support |
|---|---:|---:|---:|
| Phi mode/executor | unavailable | 0.000 | 3 |
| Phi mode/manager | unavailable | 0.000 | 1 |
| Phi mode/mixed | 0.000 | unavailable | 0 |
| Phi mode/one-off | 1.000 | 0.333 | 6 |
| Phi mode/unknown | 0.000 | unavailable | 0 |
| Phi activity/awaiting | unavailable | 0.000 | 2 |
| Phi activity/completed | 0.750 | 0.600 | 5 |
| Phi activity/in progress | 0.500 | 0.667 | 3 |
| Phi activity/unknown | 0.000 | unavailable | 0 |
| Phi title/false | 0.250 | 0.333 | 3 |
| Phi title/true | 1.000 | 0.286 | 7 |
| Llama mode/executor | unavailable | 0.000 | 3 |
| Llama mode/manager | unavailable | 0.000 | 1 |
| Llama mode/mixed | 0.000 | unavailable | 0 |
| Llama mode/one-off | 1.000 | 0.333 | 6 |
| Llama activity/awaiting | 1.000 | 0.500 | 2 |
| Llama activity/completed | unavailable | 0.000 | 5 |
| Llama activity/in progress | 0.400 | 0.667 | 3 |
| Llama title/false | 1.000 | 0.333 | 3 |
| Llama title/true | 0.857 | 0.857 | 7 |
| Gemma mode/executor | unavailable | 0.000 | 3 |
| Gemma mode/manager | 0.250 | 1.000 | 1 |
| Gemma mode/mixed | 0.000 | unavailable | 0 |
| Gemma mode/one-off | 1.000 | 0.333 | 6 |
| Gemma activity/awaiting | 1.000 | 0.500 | 2 |
| Gemma activity/completed | 0.500 | 0.200 | 5 |
| Gemma activity/in progress | 0.000 | 0.000 | 3 |
| Gemma title/false | 0.000 | 0.000 | 3 |
| Gemma title/true | 1.000 | 0.286 | 7 |

Blocked and unknown activity labels have zero reference support. Zero-support labels have
undefined recall, and labels never predicted have undefined precision.

## 13. Judge metrics by task and denominators

Current accounting is:

| Candidate | Eligible | Completed | Failed | Skipped invalid | Failure category |
|---|---:|---:|---:|---:|---|
| Phi-4 Mini | 26 | 26 | 0 | 14 | none |
| Llama 3.2 3B | 26 | 26 | 0 | 14 | none |
| Gemma 3 4B | 23 | 22 | 1 | 17 | provider invalid JSON |

Each cell below is `mean (n)` over successfully judged, schema-valid outputs for that task.

| Candidate/task | Dimension means |
|---|---|
| Phi summary | factual consistency 4.000 (5); material coverage 3.400 (5); concise usefulness 3.800 (5); conversation characterization 3.200 (5); unsupported-claim avoidance 4.000 (5) |
| Phi mode | label support 2.667 (6); mode distinction 2.667 (6); reason specificity 2.833 (6); unsupported-claim avoidance 3.667 (6) |
| Phi activity | blocker correctness 3.556 (9); final meaningful activity 2.111 (9); status correctness 2.889 (9); next-action support 2.333 (9); not-source-copying 3.111 (9); unsupported-claim avoidance 4.000 (9) |
| Phi title | dominant-activity fit 2.667 (6); title-fits correctness 2.000 (6); suggestion usefulness 4.000 (6); suggestion-only compliance 4.000 (6); unsupported-claim avoidance 4.000 (6) |
| Llama summary | factual consistency 4.000 (4); material coverage 3.500 (4); concise usefulness 3.750 (4); conversation characterization 3.250 (4); unsupported-claim avoidance 4.000 (4) |
| Llama mode | label support 2.625 (8); mode distinction 2.750 (8); reason specificity 3.000 (8); unsupported-claim avoidance 3.500 (8) |
| Llama activity | blocker correctness 0.833 (6); final meaningful activity 3.167 (6); status correctness 2.000 (6); next-action support 2.000 (6); not-source-copying 4.000 (6); unsupported-claim avoidance 3.167 (6) |
| Llama title | dominant-activity fit 3.250 (8); title-fits correctness 3.625 (8); suggestion usefulness 3.500 (8); suggestion-only compliance 4.000 (8); unsupported-claim avoidance 4.000 (8) |
| Gemma summary | factual consistency 4.000 (5); material coverage 3.800 (5); concise usefulness 4.000 (5); conversation characterization 3.800 (5); unsupported-claim avoidance 4.000 (5) |
| Gemma mode | label support 2.375 (8); mode distinction 2.375 (8); reason specificity 3.000 (8); unsupported-claim avoidance 3.375 (8) |
| Gemma activity | blocker correctness 4.000 (5); final meaningful activity 4.000 (5); status correctness 3.200 (5); next-action support 4.000 (5); not-source-copying 4.000 (5); unsupported-claim avoidance 4.000 (5) |
| Gemma title | dominant-activity fit 4.000 (4); title-fits correctness 3.000 (4); suggestion usefulness 4.000 (4); suggestion-only compliance 4.000 (4); unsupported-claim avoidance 4.000 (4) |

The preserved Gemma failure is one eligible last-activity case. Original model-not-found attempts
remain append-only evidence. Recovery occurred later than historical accepted judging, so preview
run-window drift remains a comparison limitation.

## 14. Latency, usage, runtime, and provenance

Per-task p50/p95 candidate latency:

| Candidate | Summary | Mode | Activity | Title |
|---|---|---|---|---|
| Phi | 39.187/87.969s | 29.437/80.375s | 56.718/113.640s | 31.202/79.342s |
| Llama 3B | 31.952/69.233s | 26.233/63.062s | 42.641/95.016s | 25.813/71.094s |
| Gemma 3 | 50.280/92.782s | 36.719/83.609s | 58.984/124.047s | 40.829/85.719s |

| Candidate | Observed wall span | Summed latency | Overall p50/p95 |
|---|---:|---:|---:|
| Phi | 34m04.285s | 34m03.402s | 42.172/141.921s |
| Llama 3B | 29m24.914s | 29m23.592s | 33.757/132.217s |
| Gemma 3 | 37m35.147s | 37m34.179s | 48.382/137.172s |

Exact per-task usage:

| Candidate/task | Available | Missing | Prompt | Completion | Total |
|---|---:|---:|---:|---:|---:|
| Phi summary | 8 | 2 | 16,349 | 1,117 | 17,466 |
| Phi mode | 8 | 2 | 16,581 | 705 | 17,286 |
| Phi activity | 10 | 0 | 25,116 | 1,308 | 26,424 |
| Phi title | 8 | 2 | 16,612 | 759 | 17,371 |
| Llama summary | 8 | 2 | 16,654 | 883 | 17,537 |
| Llama mode | 8 | 2 | 16,886 | 763 | 17,649 |
| Llama activity | 10 | 0 | 25,499 | 898 | 26,397 |
| Llama title | 8 | 2 | 16,917 | 752 | 17,669 |
| Gemma summary | 8 | 2 | 18,847 | 1,567 | 20,414 |
| Gemma mode | 8 | 2 | 19,047 | 1,010 | 20,057 |
| Gemma activity | 10 | 0 | 28,732 | 2,007 | 30,739 |
| Gemma title | 8 | 2 | 19,114 | 1,106 | 20,220 |

Each arm reported usage for 34/40 cases; missing usage was not inferred. The privacy-safe hardware
class was a 4-core/8-thread Intel mobile CPU, approximately 32 GiB RAM, and integrated Intel Iris
Xe graphics reporting approximately 2 GiB shared adapter memory. All three used Q4_K_M GGUF,
LM Studio CLI `9902c3a`, llama.cpp Vulkan AVX2 engine 2.25.2, context 8,192, and parallelism 1.

## 15. Preserved failures and semantic observations

All 45 candidate failures, low agreements, awkward schema-valid values, original judge failures,
and the terminal Gemma invalid-JSON failure remain private immutable evidence. No response was
repaired, retried semantically, removed, or reclassified. Invalid candidates were excluded from
judging.

## 16. Cache-only evidence

All three identical judged configurations replayed with `--judge-cache-only`, exited zero, made
zero provider calls, and retained attempt counts 78, 78, and 70. Pre/post package, judge-attempt,
judge-output, and aggregate hashes were byte-identical.

## 17. Implementation defects and fixes

No tracked code changed. The diagnosis found a local execution-environment routing defect: the
Vertex location aliases required to express `global` were absent. Supplying those aliases restored
the already-approved route; model, region, authentication, prompts, schemas, rubric, retry policy,
and output limits did not change.

## 18. Privacy, immutability, and tracking evidence

Private source, references, candidate outputs, attempts, rationales, identifiers, paths, hashes,
credentials, and cloud identity remain ignored. Frozen/live data and accepted packages were not
mutated. No private artifact is tracked or staged. The only delivery file is this report.

## 19. Per-candidate 120-case admission recommendation

- **Phi-4 Mini: PM decision required.** Reliability is materially below Gemini/Qwen historical
  checkpoints. Valid summaries score well, but title correctness and final-activity usefulness are
  mixed.
- **Llama 3.2 3B: PM decision required.** It has the best title-fit agreement of the new arms but
  only 65% whole-package validity, with particularly weak blocker correctness.
- **Gemma 3 4B: do not admit under the current contract.** It has the lowest validity (57.5%),
  weakest deterministic title/activity agreement, and one terminal judge failure despite strong
  semantic scores among completed outputs.

No hidden composite threshold was used. Final admission remains an owner/PM decision.

## 20. Limitations

Ten conversations are not statistically representative. FABLE is silver development evidence.
The fixed preview alias was initially misrouted locally and recovered later. Preview-model
run-window drift limits direct comparison with historical scores. One Gemma eligible case lacks a
semantic score, and the small checkpoint remains insufficient for statistical generalization.

## 21. Line-by-line acceptance checklist

1. Clean HEAD and repository Poetry environment: pass.
2. Frozen integrity/schema/counts/sidecars: pass.
3. Historical and accepted package immutability: pass.
4. Three identical ordered first-40 scopes: pass.
5. 120 candidate positions terminal, zero unaccounted: pass.
6. Three packages verify and score deterministically: pass.
7. All schema-valid outputs have terminal judge outcomes: pass; 74 completed and one retained
   failure.
8. Invalid/model-quality outputs visible and unrepaired: pass.
9. Bounded judge recovery only: pass.
10. Three cache-only zero-call replays: pass.
11. Fixed model/runtime/context/task/judge contracts unchanged: pass.
12. Privacy-safe aggregate evidence and recommendations: pass.
13. No 120-case arm started: pass.
14. No Gemma 4 operation: pass.
15. No private artifact tracked or staged: pass.
16. Delivery unstaged and uncommitted for PM validation: pass.

## 22. Rework addendum — 2026-07-23

### Report metric completion

The report now publishes all required privacy-safe confusion matrices, per-label
precision/recall/support, wall spans, summed and overall/per-task latency, exact task usage, and
runtime/hardware provenance. Values were read from immutable package attempts and aggregate
reports. Candidate packages were not regenerated, repackaged, or modified.

### Synthetic fixed-route diagnosis

The bounded diagnosis used synthetic content only and retained Vertex AI, model
`gemini-3.1-pro-preview`, `global`, ADC, rubric v1, temperature 0, maximum 1,000 output tokens,
reasoning `none`, and the application-owned schema.

- ADC credentials refreshed successfully and a project resolved; no identity or credential value
  was printed or recorded.
- The configured project variable was present. Both expected Vertex location aliases were absent.
- A publisher-model metadata GET returned 404, but an official Vertex structured generation at the
  exact explicit-global route succeeded. The metadata GET is therefore not a reliable availability
  check for this preview alias.
- An explicit-global LiteLLM structured request succeeded.
- The application-owned request without the location aliases reproduced model-not-found.
- With both location aliases set to the already-required value `global`, the synthetic
  application-owned judge request passed provider schema, strict application schema, identity, and
  evidence-membership checks.

Root-cause classification is **incorrect local Vertex location routing caused by absent location
environment aliases**, with high confidence. ADC, project resolution, exact model availability,
LiteLLM model mapping, and the application judge schema all passed when the required global route
was explicit.

### Route restoration and recovery boundary

The owner separately authorized recovery for exactly the existing 75 eligible cases, using the
same disclosed fields, fixed Vertex model in `global`, ADC, rubric v1, one new recovery attempt,
and only the configured bounded retry. Phi completed 26/26 and Llama completed 26/26 on their
single recovery attempts. Gemma completed 22/23; its one invalid-JSON response remained invalid
after the sole bounded retry. Final accounting is 74 completed, one failed, 45 skipped invalid,
and zero unaccounted.

### Immutability, privacy, validation, and Git status

All diagnosis used synthetic content. Authorized recovery remained inside the separately confirmed
private disclosure boundary. Three cache-only replays exited zero with zero calls; attempt counts
remained 78/78/70 and all package/attempt/output/aggregate hashes were unchanged. No candidate
output, reference, private source, credential, project/account identity, or private path was
disclosed in tracked output. Original candidate packages, candidate attempts, frozen/live
databases, and historical accepted packages remain unchanged. No 120-case arm was started.
Delivery remains unstaged and uncommitted.
