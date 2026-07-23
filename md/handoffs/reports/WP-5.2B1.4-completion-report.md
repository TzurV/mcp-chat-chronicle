# WP-5.2B1.4 Completion Report

## 1. Status and executive summary

Ready for PM validation with three retained terminal judge failures. All 400 candidate positions are terminal, all four immutable candidate packages verify, deterministic scoring is complete, and every schema-valid candidate has a terminal fixed-Pro judge outcome. The complete-arm schema-valid rates were Gemini 93.3% (112/120), Qwen 70.0% (84/120), and Llama 47.5% (57/120). Qwen-40 was a checkpoint only, at 85.0% (34/40).

Cache-only replay passed for every arm with zero additional provider calls and byte-stable packages, judge attempts, judge outputs, and aggregate reports. Full repository validation passed. Delivery consists only of this unstaged report; private evidence remains ignored.

## 2. Exact scope and case identity reconciliation

- Gemini-120, Llama-120, and Qwen-120 contain the same ordered 120 aliases over 30 frozen conversations and four tasks.
- Qwen-40 contains exactly the corresponding 40 aliases for the first 10 frozen conversations.
- Candidate accounting is 120 + 120 + 120 + 40 = 400 terminal positions, with zero unaccounted.
- The complete arms share the same frozen-prefix identity. The checkpoint has the accepted first-10 prefix identity.

## 3. Repository/runtime/private-corpus preflight

The application was clean at `ea00f45d3e085cf5aae52fb1163bac17f948e411` for retry-aware packaging/scoring and remaining-arm generation. Gemini candidate requests occurred earlier at `d1b6ca800d7407b84a6693d205841316f42fd49b`; the intervening change affected post-generation attempt selection only, not prompts or provider requests.

The frozen database, live database, and snapshot-manifest hashes still equal their preflight baselines. The frozen snapshot remained the accepted 711-conversation development corpus. No source, selection, input, reference, or task-catalog artifact was modified.

## 4. Consolidated authorization boundary

Execution stayed within the recorded authorization: the accepted private frozen cases, Vertex AI in the `global` location, Gemini 3.5 Flash candidate calls already completed for Gemini-120, and Gemini 3.1 Pro Preview judging under rubric v1. Local Llama and Qwen candidate generation used LM Studio. No provider, model, region, case scope, prompt, schema, context, timeout, or disclosure boundary changed during an arm.

## 5. Gemini-120 evidence

- Candidate generation provenance: `d1b6ca800d7407b84a6693d205841316f42fd49b`.
- Retry-aware packaging/scoring provenance: `ea00f45d3e085cf5aae52fb1163bac17f948e411`.
- Verification: 120 expected; 112 valid; 8 failed; 254 generation attempts.
- Candidate failures: invalid JSON 6, provider response 1, schema validation 1.
- Deterministic: evidence-valid 112, cross-field-valid 112, no-valid-output 8.
- Task validity: summary 23/30, work mode 30/30, last activity 29/30, title 30/30.
- Agreement: work mode 63.3%, last activity 70.0%, title fit 83.3%.
- Judge: 112 eligible; 110 completed; 2 terminal `provider_invalid_json`; 8 skipped invalid; 114 attempts after the bounded recovery pass.
- Representative judge means: factual consistency 4.00, material coverage 3.95, unsupported-claim avoidance 3.96, label support 3.60.
- Cache-only replay: exit zero, zero calls, stable package/attempt/judge/aggregate hashes.

## 6. Llama-120 evidence

- Verification: 120 expected; 57 valid; 63 failed; 120 generation attempts.
- Candidate failures: context length 21, evidence validation 16, schema validation 15, provider HTTP 10, invalid JSON 1.
- Deterministic: evidence-valid 57, cross-field-valid 57, no-valid-output 63.
- Task validity: summary 16/30, work mode 20/30, last activity 14/30, title 7/30.
- Agreement: work mode 3.3%, last activity 20.0%, title fit 6.7%.
- Judge: 57 eligible; 56 completed; 1 terminal `output_schema`; 63 skipped invalid; 59 attempts after bounded recovery.
- Representative judge means: factual consistency 3.56, material coverage 2.69, unsupported-claim avoidance 3.02, label support 1.58.
- Cache-only replay: exit zero, zero calls, stable package/attempt/judge/aggregate hashes.

## 7. Qwen artifact/profile pin and synthetic smoke

The accepted Qwen3.5 4B Q4_K_M GGUF artifact was pinned by repository revision, filename, byte size, and SHA-256 in private evidence. Runtime was LM Studio CLI commit `9902c3a`, with context 8,192 and parallelism 1. The advertised maximum context was recorded separately and was not substituted for the configured context. Synthetic smoke passed all four task schemas before the checkpoint.

Llama used Llama 3.2 1B Instruct, Q4_K_M GGUF, through the same LM Studio runtime, context 8,192, and parallelism 1. Both local arms ran on a privacy-safe machine class of a 4-core/8-thread 11th-generation Intel mobile CPU, approximately 32 GiB physical RAM, and integrated Intel Iris Xe graphics reporting approximately 2 GiB shared adapter memory. LM Studio selected the execution device automatically; no discrete GPU/NPU or dedicated VRAM was reported. These characteristics describe the performance environment without exposing hostname, user, serial number, or private paths.

Gemini used Vertex AI Gemini 3.5 Flash in the `global` location. Its hosted service latency is not directly comparable with single-worker local inference because execution hardware, queueing, transport, and tokenizer/cache behavior differ.

## 8. Qwen-40 checkpoint evidence and continue decision

- Verification: 40 expected; 34 valid; 6 failed; 40 attempts.
- All six failures were context-length outcomes.
- Task validity: summary 8/10, work mode 8/10, last activity 10/10, title 8/10.
- Agreement: work mode 50.0%, last activity 50.0%, title fit 80.0%.
- Judge: 34 eligible and completed; 0 failed; 6 skipped invalid.
- The checkpoint had complete accounting, no infrastructure/configuration defect, and passed deterministic scoring, so proceeding to 120 cases was justified.
- This checkpoint is not treated as an independent complete-arm leaderboard result.

## 9. Qwen-120 evidence

- Verification: 120 expected; 84 valid; 36 failed; 120 attempts; schema-valid rate 70.0%.
- Candidate failures, preserved exactly: context length 29, timeout 5, schema validation 2.
- Deterministic: evidence-valid 84, cross-field-valid 84, no-valid-output 36.
- Task validity: summary 17/30, work mode 19/30, last activity 30/30, title 18/30.
- Agreement: work mode 33.3%, last activity 60.0%, title fit 56.7%.
- Judge: 84 eligible and completed; 0 current failures; 36 skipped invalid; 85 attempts after one successful bounded recovery.
- Representative judge means: factual consistency 4.00, material coverage 4.00, unsupported-claim avoidance 3.87, label support 2.58.
- Cache-only replay: exit zero, zero calls, stable package/attempt/judge/aggregate hashes.

## 10. Complete-scope comparison and Qwen checkpoint

| Arm | Terminal | Valid | Valid rate | Failed | Judge completed/eligible |
|---|---:|---:|---:|---:|---:|
| Gemini-120 | 120 | 112 | 93.3% | 8 | 110/112 |
| Qwen-120 | 120 | 84 | 70.0% | 36 | 84/84 |
| Llama-120 | 120 | 57 | 47.5% | 63 | 56/57 |
| Qwen-40 checkpoint | 40 | 34 | 85.0% | 6 | 34/34 |

Gemini provided the strongest combination of validity, latency, deterministic agreement, and semantic scores. Qwen valid outputs were semantically strong, but overall utility was reduced by context/timeout failures and weaker work-mode classification. Llama was least reliable and least aligned on categorical tasks.

## 11. Deterministic confusion/category metrics

Complete-arm exact agreement:

| Arm | Work mode | Last activity | Title fit |
|---|---:|---:|---:|
| Gemini-120 | 63.3% | 70.0% | 83.3% |
| Qwen-120 | 33.3% | 60.0% | 56.7% |
| Llama-120 | 3.3% | 20.0% | 6.7% |

All exact-agreement denominators are the 30 complete-scope cases for that task; `no output` is included as a predicted outcome but is not a reference label. Rows below are reference labels and columns are predictions.

### Gemini-120 confusion matrices

| Work mode | executor | manager | mixed | one-off | no output | unknown |
|---|---:|---:|---:|---:|---:|---:|
| executor | 8 | 0 | 1 | 5 | 0 | 0 |
| manager | 1 | 2 | 0 | 0 | 0 | 0 |
| mixed | 1 | 0 | 0 | 0 | 0 | 0 |
| one-off | 2 | 0 | 1 | 9 | 0 | 0 |

| Last activity | awaiting input | blocked | completed | in progress | no output | unknown |
|---|---:|---:|---:|---:|---:|---:|
| awaiting input | 3 | 0 | 3 | 1 | 0 | 0 |
| completed | 0 | 0 | 15 | 1 | 0 | 0 |
| in progress | 0 | 0 | 3 | 3 | 1 | 0 |

| Title fit | false | true | no output |
|---|---:|---:|---:|
| false | 11 | 0 | 0 |
| true | 5 | 14 | 0 |

| Task / label | Precision | Recall | Support |
|---|---:|---:|---:|
| Work mode / executor | 0.667 | 0.571 | 14 |
| Work mode / manager | 1.000 | 0.667 | 3 |
| Work mode / mixed | 0.000 | 0.000 | 1 |
| Work mode / one-off | 0.643 | 0.750 | 12 |
| Last activity / awaiting input | 1.000 | 0.429 | 7 |
| Last activity / completed | 0.714 | 0.938 | 16 |
| Last activity / in progress | 0.600 | 0.429 | 7 |
| Title fit / false | 0.688 | 1.000 | 11 |
| Title fit / true | 1.000 | 0.737 | 19 |

### Qwen-120 confusion matrices

| Work mode | executor | manager | mixed | one-off | no output | unknown |
|---|---:|---:|---:|---:|---:|---:|
| executor | 4 | 2 | 0 | 0 | 8 | 0 |
| manager | 0 | 1 | 0 | 0 | 2 | 0 |
| mixed | 0 | 0 | 0 | 0 | 1 | 0 |
| one-off | 1 | 6 | 0 | 5 | 0 | 0 |

| Last activity | awaiting input | blocked | completed | in progress | no output | unknown |
|---|---:|---:|---:|---:|---:|---:|
| awaiting input | 1 | 0 | 1 | 5 | 0 | 0 |
| completed | 0 | 0 | 14 | 2 | 0 | 0 |
| in progress | 0 | 1 | 3 | 3 | 0 | 0 |

| Title fit | false | true | no output |
|---|---:|---:|---:|
| false | 3 | 1 | 7 |
| true | 0 | 14 | 5 |

| Task / label | Precision | Recall | Support |
|---|---:|---:|---:|
| Work mode / executor | 0.800 | 0.286 | 14 |
| Work mode / manager | 0.111 | 0.333 | 3 |
| Work mode / mixed | unavailable | 0.000 | 1 |
| Work mode / one-off | 1.000 | 0.417 | 12 |
| Last activity / awaiting input | 1.000 | 0.143 | 7 |
| Last activity / completed | 0.778 | 0.875 | 16 |
| Last activity / in progress | 0.300 | 0.429 | 7 |
| Title fit / false | 1.000 | 0.273 | 11 |
| Title fit / true | 0.933 | 0.737 | 19 |

### Llama-120 confusion matrices

| Work mode | executor | manager | mixed | one-off | no output | unknown |
|---|---:|---:|---:|---:|---:|---:|
| executor | 1 | 1 | 6 | 0 | 6 | 0 |
| manager | 0 | 0 | 1 | 0 | 1 | 1 |
| mixed | 0 | 0 | 0 | 0 | 1 | 0 |
| one-off | 1 | 1 | 7 | 0 | 2 | 1 |

| Last activity | awaiting input | blocked | completed | in progress | no output | unknown |
|---|---:|---:|---:|---:|---:|---:|
| awaiting input | 0 | 0 | 1 | 3 | 3 | 0 |
| completed | 0 | 0 | 1 | 3 | 11 | 1 |
| in progress | 0 | 0 | 0 | 5 | 2 | 0 |

| Title fit | false | true | no output |
|---|---:|---:|---:|
| false | 2 | 3 | 6 |
| true | 2 | 0 | 17 |

| Task / label | Precision | Recall | Support |
|---|---:|---:|---:|
| Work mode / executor | 0.500 | 0.071 | 14 |
| Work mode / manager | 0.000 | 0.000 | 3 |
| Work mode / mixed | 0.000 | 0.000 | 1 |
| Work mode / one-off | unavailable | 0.000 | 12 |
| Last activity / awaiting input | unavailable | 0.000 | 7 |
| Last activity / completed | 0.500 | 0.063 | 16 |
| Last activity / in progress | 0.455 | 0.714 | 7 |
| Title fit / false | 0.500 | 0.182 | 11 |
| Title fit / true | 0.000 | 0.000 | 19 |

The zero-support reference labels (`blocked` and `unknown` for last activity, and `unknown` for work mode) have undefined recall; precision is also undefined when the model made no prediction for the label. Qwen-40 remains separate: its full checkpoint matrices are retained in private evidence, while its exact agreement was work mode 5/10, last activity 5/10, and title fit 8/10.

## 12. Semantic judge metrics

The fixed judge used Gemini 3.1 Pro Preview, rubric v1, temperature 0, maximum 1,000 tokens, and no reasoning effort. All judge outputs retained blinded candidate identity.

Means below are over successfully judged, schema-valid outputs for the named task—not all 30 corpus positions. Each cell is `mean (n)`.

### Gemini-120: 110 completed, 2 failed, 8 skipped invalid

| Task | Applicable dimension means |
|---|---|
| Summary: 22 completed, 1 failed, 7 skipped | concise usefulness 3.955 (22); conversation characterization 4.000 (22); factual consistency 4.000 (22); material coverage 3.955 (22); unsupported-claim avoidance 4.000 (22) |
| Work mode: 30 completed | label support 3.600 (30); mode distinction 3.600 (30); reason specificity 3.733 (30); unsupported-claim avoidance 3.867 (30) |
| Last activity: 28 completed, 1 failed, 1 skipped | blocker correctness 4.000 (28); final meaningful activity 3.929 (28); next-action support 3.857 (28); not-source-copying 4.000 (28); status correctness 3.857 (28); unsupported-claim avoidance 4.000 (28) |
| Title: 30 completed | dominant-activity fit 3.867 (30); suggestion-only compliance 4.000 (30); suggestion usefulness 4.000 (30); title-fits correctness 4.000 (30); unsupported-claim avoidance 4.000 (30) |

### Qwen-120: 84 completed, 0 failed, 36 skipped invalid

| Task | Applicable dimension means |
|---|---|
| Summary: 17 completed, 13 skipped | concise usefulness 4.000 (17); conversation characterization 4.000 (17); factual consistency 4.000 (17); material coverage 4.000 (17); unsupported-claim avoidance 4.000 (17) |
| Work mode: 19 completed, 11 skipped | label support 2.579 (19); mode distinction 2.579 (19); reason specificity 3.211 (19); unsupported-claim avoidance 3.526 (19) |
| Last activity: 30 completed | blocker correctness 3.867 (30); final meaningful activity 4.000 (30); next-action support 2.900 (30); not-source-copying 4.000 (30); status correctness 3.333 (30); unsupported-claim avoidance 3.933 (30) |
| Title: 18 completed, 12 skipped | dominant-activity fit 4.000 (18); suggestion-only compliance 4.000 (18); suggestion usefulness 4.000 (18); title-fits correctness 4.000 (18); unsupported-claim avoidance 4.000 (18) |

### Llama-120: 56 completed, 1 failed, 63 skipped invalid

| Task | Applicable dimension means |
|---|---|
| Summary: 16 completed, 14 skipped | concise usefulness 3.000 (16); conversation characterization 2.625 (16); factual consistency 3.563 (16); material coverage 2.688 (16); unsupported-claim avoidance 3.563 (16) |
| Work mode: 19 completed, 1 failed, 10 skipped | label support 1.579 (19); mode distinction 1.579 (19); reason specificity 1.895 (19); unsupported-claim avoidance 2.737 (19) |
| Last activity: 14 completed, 16 skipped | blocker correctness 1.500 (14); final meaningful activity 2.500 (14); next-action support 2.000 (14); not-source-copying 2.643 (14); status correctness 1.714 (14); unsupported-claim avoidance 2.286 (14) |
| Title: 7 completed, 23 skipped | dominant-activity fit 2.000 (7); suggestion-only compliance 4.000 (7); suggestion usefulness 2.571 (7); title-fits correctness 2.286 (7); unsupported-claim avoidance 4.000 (7) |

Three eligible results remain terminal judge failures after bounded recovery: two Gemini provider-invalid-JSON failures and one Llama output-schema failure. They are not silently converted to scores.

## 13. Performance, usage, and provenance comparison

Observed wall time is the reproducible span from the earliest authoritative candidate attempt start timestamp to the latest authoritative attempt completion timestamp in each immutable package. It includes local wrapper interruption occurring inside that span, but does not add inferred idle time outside those timestamps. Gemini's observed span reflects authoritative retry attempts only; earlier superseded failed attempts are excluded. Summed case latency is the sum of authoritative per-case durations and is not elapsed wall time.

| Arm | Observed wall span | Summed case latency | Overall p50 / p95 (n) |
|---|---:|---:|---:|
| Gemini-120 | 10m 39.524s | 7m 33.787s | 2.156s / 12.562s (120) |
| Llama-120 | 42m 13.023s | 43m 02.964s | 17.312s / 53.609s (120) |
| Qwen-120 | 4h 43m 30.782s | 4h 43m 27.047s | 62.094s / 168.375s (120) |
| Qwen-40 checkpoint | 44m 30.512s | 44m 29.285s | 59.297s / 164.953s (40) |

Per-task candidate latency p50/p95 (all 30 positions per task for complete arms; 10 per task for the checkpoint):

| Arm | Summary | Work mode | Last activity | Title |
|---|---|---|---|---|
| Gemini-120 | 2.719s / 9.218s | 2.030s / 7.906s | 2.109s / 11.077s | 1.734s / 12.562s |
| Qwen-120 | 61.687s / 180.030s | 49.047s / 162.922s | 81.844s / 134.967s | 48.187s / 150.467s |
| Llama-120 | 18.359s / 58.297s | 14.203s / 50.905s | 22.016s / 48.359s | 14.375s / 52.922s |
| Qwen-40 checkpoint | 50.344s / 112.656s | 38.952s / 111.750s | 71.390s / 162.547s | 37.718s / 102.484s |

Exact candidate usage:

| Arm / task | Available | Missing | Prompt | Completion | Total |
|---|---:|---:|---:|---:|---:|
| Gemini / summary | 30 | 0 | 189,338 | 6,571 | 195,909 |
| Gemini / work mode | 30 | 0 | 192,098 | 3,802 | 195,900 |
| Gemini / last activity | 29 | 1 | 97,200 | 4,991 | 102,191 |
| Gemini / title | 30 | 0 | 193,442 | 3,841 | 197,283 |
| **Gemini total** | **119** | **1** | **672,078** | **19,205** | **691,283** |
| Llama / summary | 21 | 9 | 66,626 | 3,181 | 69,807 |
| Llama / work mode | 21 | 9 | 67,235 | 1,692 | 68,927 |
| Llama / last activity | 27 | 3 | 66,684 | 3,506 | 70,190 |
| Llama / title | 20 | 10 | 63,894 | 1,560 | 65,454 |
| **Llama total** | **89** | **31** | **264,439** | **9,939** | **274,378** |
| Qwen-120 / summary | 18 | 12 | 51,655 | 2,841 | 54,496 |
| Qwen-120 / work mode | 19 | 11 | 54,714 | 2,247 | 56,961 |
| Qwen-120 / last activity | 30 | 0 | 85,357 | 4,244 | 89,601 |
| Qwen-120 / title | 19 | 11 | 54,870 | 1,978 | 56,848 |
| **Qwen-120 total** | **86** | **34** | **246,596** | **11,310** | **257,906** |
| Qwen-40 / summary | 8 | 2 | 17,455 | 1,107 | 18,562 |
| Qwen-40 / work mode | 8 | 2 | 17,663 | 868 | 18,531 |
| Qwen-40 / last activity | 10 | 0 | 27,002 | 1,234 | 28,236 |
| Qwen-40 / title | 8 | 2 | 17,710 | 703 | 18,413 |
| **Qwen-40 total** | **34** | **6** | **79,830** | **3,912** | **83,742** |

Gemini also reported 12,029 cache-read input tokens for summary; that provider-specific counter is not added again to its reported total. Missing usage remains unavailable rather than inferred. Token accounting is not directly cross-provider comparable because hosted and local runtimes expose different tokenizers, cache counters, and failure-path usage.

## 14. Overnight execution timeline and interruptions

Gemini generation completed earlier at the generation commit and was recovered locally without repeating successful calls. A deterministic index migration selected the latest successful attempt while permanently preserving each baseline attempt and leaving attempt/raw files unchanged. Packaging and scoring occurred at the later clean commit.

Llama and Qwen local foreground wrappers exceeded command windows while their child generators continued. Progress was monitored through terminal indexes, running markers, and LM Studio health; duplicate workers were avoided. The authoritative timestamp spans were Llama 42m13s, Qwen-40 44m31s, and Qwen-120 4h43m31s. Qwen-120 completed 120/120. These interruptions demonstrated resumability but also showed that single-worker local overnight execution is operationally slow and needs robust external process supervision.

## 15. Model outcomes preserved

All invalid JSON, schema/evidence/cross-field failures, context-limit outcomes, timeouts, provider errors, low agreement, low judge scores, and slow generations remain in private evidence. No candidate output, attempt JSON, or raw response was repaired, deleted, or rewritten. Invalid candidates were excluded from judging and reported by category.

## 16. Infrastructure defects, fixes, and regressions

The run exposed two generic harness defects before final execution: LM Studio reasoning-effort pass-through and retry-aware authoritative-attempt selection. The accepted implementation preserves legacy missing-pointer baseline semantics while requiring new current pointers to reference the latest attempt. Regression coverage proves retry-aware packaging, verification, deterministic scoring, judge eligibility, legacy readability, invalid-pointer failure, and unchanged WP-5.2B1.3 verification.

The Gemini private migration validated every pointer before packaging, preserved baseline pointers, selected the latest successful attempt where available, and proved attempt/raw tree hashes unchanged. The code change affected selection only, not prompts or provider requests.

## 17. Full validation results

- Poetry environment resolved to the repository virtual environment.
- Focused benchmark tests: passed.
- Full suite: `432 passed, 1 skipped`.
- Ruff: passed.
- `poetry check`: passed.
- Bench prepare/generate/verify/score help: passed.
- Chronicle help: passed.
- `git diff --check`: passed.
- Staged-file check: empty.
- All four new packages verify and score deterministically.

The subsequent validation-review rework changed Markdown only. Per review instruction, model operations and repository tests were not rerun. The report-only post-check used existing immutable evidence, repeated artifact hashes, `git diff --check`, staged/tracked-file inspection, and Git status.

## 18. Immutability, privacy, and tracking evidence

Frozen DB, live DB, and snapshot-manifest hashes match preflight. Accepted WP-5.2B1.3 Llama and Gemini package hashes match their baselines and verify unchanged at 21/40 and 39/40 valid respectively. New candidate-package hashes remained stable.

Across a repeated cache-only proof, all four judge attempt hashes, judge output hashes, and aggregate-report hashes were byte-identical. Attempt counts stayed 114, 59, 34, and 85, proving zero new provider calls. Operational run manifests refresh only their non-evidentiary update timestamp.

No private IDs, titles, paths, fingerprints, prompts, references, outputs, rationales, credentials, tokens, project identity, or account identity are included here. Private configs, outputs, and evidence remain ignored and untracked.

The report-only validation review recomputed hashes with the same baseline algorithm: all four candidate packages and all four judge-attempt aggregates matched their pre-review values exactly. Embedded candidate attempts are covered by the unchanged immutable package bytes. Frozen/live database and both accepted WP-5.2B1.3 package hashes also matched their recorded baselines. No generation, judging, retry, or provider-call command was run.

## 19. Limitations and next-model recommendation

This is a bounded development comparison, not a leaderboard or statistical generalization. The judge is itself a preview model, three judge outputs remained terminal failures, local hardware identity was intentionally not exposed, and provider token counts are not directly comparable.

For the next bounded model study, retain Gemini as the development control. Qwen merits further evaluation only as a separately authorized new arm with an up-front context/timeout policy chosen before generation; do not reinterpret this arm by changing those settings post hoc. Llama 1B is not recommended for the next complete arm under the current contracts.

## 20. Acceptance checklist

1. Same 120 complete-arm identities: pass.
2. Qwen-40 equals the first 40 identities: pass.
3. All 400 candidate positions terminal: pass.
4. Four packages verify and score deterministically: pass.
5. Every eligible output has a terminal Pro-judge outcome: pass (three outcomes are retained failures).
6. Invalid outputs visible and skipped: pass.
7. Four cache-only replays exit zero with zero calls: pass.
8. No candidate repaired or removed: pass.
9. Exact private provenance recorded and safely summarized: pass.
10. Full metrics/runtime evidence exists: pass.
11. Repository validation passes: pass.
12. Live/frozen/historical artifacts unchanged: pass.
13. No private artifact or credential tracked: pass.
14. Report maps evidence to every requirement: pass.
15. Delivery remains unstaged and uncommitted: pass.
