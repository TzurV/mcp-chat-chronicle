# WP-5.2B3B Global Prompt Development Evidence Brief

## Article boundary

This is a privacy-safe, article-ready evidence brief, not final article copy. It reports only the
frozen ten-conversation development study. The twenty-conversation holdout has not been opened or
run, so no holdout or generalization result exists.

## Problem and research questions

The study asked whether one global four-task prompt package could improve structured-output
reliability for two small local models without losing portability to a hosted model. It compared:

- P0: the accepted baseline;
- P1: concise schema-first contracts;
- P2: the P1 contracts plus bounded fictional examples;
- optional P3: one model-neutral revision only if a repeated shared local failure met every
  predefined trigger condition.

The primary question was reliability, not prose preference: do valid, evidence-valid task objects
increase across Qwen3.5-4B and Phi-4 Mini? Secondary questions covered deterministic agreement,
fixed-judge quality, Gemini portability, latency/token cost, failure movement, and task difficulty.

## Why context stayed at 8K

WP-5.2B3A tested 16K before prompt tuning. It found no recovery of a prior context failure for
either local model; Qwen exchanged context failures for timeouts and Phi reliability regressed.
Common 8,192 context was therefore frozen for B3B so prompt wording was the only experimental
variable. This prevents a larger context window from being mistaken for a prompt improvement.

## Development/holdout method

Thirty accepted conversations were divided once into 10 development and 20 holdout conversations.
Selection used accepted metadata only—provider and length bucket—not candidates, references,
labels, outcomes, failure classes, or judge scores. Development quotas were exactly 3 ChatGPT,
3 OpenAI Codex, 2 Claude, 2 Claude Code and 4 short, 3 medium, 3 long. Holdout provider quotas were
7/7/3/3. The manifests are versioned, disjoint, checksum-bound, and jointly cover the accepted
authority set.

Every development conversation produced four ordered task cases, giving 40 positions per model
and package. Holdout raw inputs, references, and per-case identities/outcomes remained unopened;
holdout candidate and judge calls were zero.

## Prompt hypotheses and controlled differences

Only `system_prompt` and `user_prompt` could differ. Task versions, schemas, selectors,
finalizers, input limits, source inputs, references, context 8,192, temperature 0, output cap,
reasoning policy, timeout, retry policy, concurrency, runtime, model artifact, judge, and rubric
were fixed.

| Package | Hypothesis | Characters | Estimated prompt tokens | Change from P0 |
|---|---|---:|---:|---:|
| P0 | Accepted concise task instructions | 3,109 | 658 | — |
| P1 | Schema-first wording reduces malformed JSON/schema/cross-field failures | 4,202 | 870 | +1,093 chars; +212 tokens |
| P2 | Fictional valid/edge examples reinforce output shapes | 6,849 | 1,516 | +3,740 chars; +858 tokens |

Token counts use `cl100k_base` over normalized system plus user prompt and are estimates, not
provider-native usage. P1/P2 were frozen before their first call, contained no private example,
used no automated optimizer, and were identical across Qwen, Phi, and Gemini.

Normalized package identities:

- P0: `28a421fa980a1c3e20ba22c65b497ee9ee652c8dc67e9a8e815f4016fc6edb8f`;
- P1: `cebb28d8e8a0b38ddf22becf50cb88993ffdd94db5ee4fe79616062c28a9dddd`;
- P2: `132d6524dd5244e089bd157d639bd73b70ab97e4c72dc1cdee50bb1ac407c953`.

## Model, generation, and judge provenance

| Role | Identity and fixed settings |
|---|---|
| Local Qwen | LM Studio Qwen3.5-4B, accepted Q4_K_M GGUF, context 8,192, parallelism 1 |
| Local Phi | LM Studio Phi-4 Mini Instruct, accepted Q4_K_M GGUF, context 8,192, parallelism 1 |
| Portability control | Vertex global `vertex_ai/gemini-3.5-flash` |
| Candidate generation | temperature 0, max tokens 500, reasoning none, timeout 180s, retries 0, concurrency 1 |
| Fixed judge | Vertex global `vertex_ai/gemini-3.1-pro-preview`, rubric v1, temperature 0, max tokens 1,000, reasoning none, concurrency 1, bounded provider retry 1 |
| Application | exact clean `f25505ae3762fae337d3ed0b7a364689f0cc8853` checkout |

The Phi P1 fictional gate repeated the same title schema failure in two unchanged 3/4 runs. A
manager-approved exception authorized one unchanged 40-position development run; its failures were
preserved without rescue retries. Phi P2 still passed its original 4/4 gate. Both Qwen gates and the
fixed-judge gate passed 4/4.

## Scoring formulas

Usable means schema-valid and evidence-valid. Invalid candidates stay in every 40-case denominator.
Deterministic matrices compare categorical output with the accepted FABLE reference and record
`no_valid_output` explicitly.

UTS v1 gives a case zero when the candidate is invalid/absent or judge scoring fails. Otherwise it
averages applicable judge dimensions after normalizing every 1–4 score with `(score - 1) / 3`.
Each task averages its ten expected cases; four task scores are macro-averaged and multiplied by
100. Valid-output quality averages successfully judged valid survivors only and must stay paired
with valid rate. Latency is not part of UTS.

## Reliability, utility, and operating table

| Package | Model | Valid/40 | Summary / work / last / title | Failures | Candidate p50 / p95 | Wall | Prompt / completion / total tokens; usage n | Judge completed / eligible | Macro UTS | Valid-output quality |
|---|---|---:|---|---|---|---:|---|---:|---:|---:|
| P0 | Qwen | 30/40 | 6/7/10/7 | context_length 6, schema_validation 1, timeout 3 | 74.109s / 180.045s | 275.53m | 88,851/4,372/93,223; 31/40 | 30/30 | 69.4 | 0.934 |
| P0 | Phi | 32/40 | 7/8/10/7 | context_length 6, schema_validation 2 | 54.031s / 152.483s | 131.72m | 95,188/4,169/99,357; 34/40 | 32/32 | 56.6 | 0.713 |
| P0 | Gemini | 38/40 | 8/10/10/10 | invalid_json 1, schema_validation 1 | 2.030s / 11.077s | 10.15m | 199,362/6,347/205,709; 40/40 | 37/38 | 89.5 | 0.968 |
| P1 | Qwen | 26/40 | 6/6/8/6 | context_length 6, timeout 8 | 102.812s / 180.188s | 68.42m | 61,454/3,493/64,947; 26/40 | 25/26 | 51.5 | 0.822 |
| P1 | Phi | 32/40 | 8/7/9/8 | context_length 6, schema_validation 2 | 51.344s / 149.765s | 43.09m | 97,074/3,502/100,576; 34/40 | 32/32 | 63.5 | 0.795 |
| P1 | Gemini | 32/40 | 7/7/9/9 | invalid_json 7, provider_response 1 | 2.467s / 8.436s | 2.22m | 197,400/6,662/204,062; 39/40 | 32/32 | 78.6 | 0.982 |
| P2 | Qwen | 26/40 | 6/6/8/6 | context_length 6, timeout 8 | 73.406s / 180.108s | 61.26m | 66,394/2,235/68,629; 26/40 | 25/26 | 54.2 | 0.870 |
| P2 | Phi | 32/40 | 8/7/10/7 | context_length 6, schema_validation 2 | 55.000s / 156.297s | 45.25m | 102,590/3,615/106,205; 34/40 | 32/32 | 58.7 | 0.746 |
| P2 | Gemini | 36/40 | 9/9/10/8 | invalid_json 4 | 2.186s / 7.265s | 2.04m | 209,792/5,860/215,652; 40/40 | 36/36 | 87.3 | 0.971 |

## Local selection table

| Package | Pooled usable/80 | Lower model/40 | Summary / work / last / title pooled usable | Minimum task/20 | Pooled local macro UTS | Eligibility |
|---|---:|---:|---|---:|---:|---|
| P0 | 62/80 | 30/40 | 13/15/20/14 | 13/20 | 63.0 | selected |
| P1 | 58/80 | 26/40 | 14/13/17/14 | 13/20 | 57.5 | ineligible: local and Gemini guardrails |
| P2 | 58/80 | 26/40 | 14/13/18/13 | 13/20 | 56.4 | ineligible: local and Gemini guardrails |

## Deterministic agreement

| Package | Model | Work exact | Last exact | Title exact | Summary date/length valid |
|---|---|---:|---:|---:|---:|
| P0 | Qwen | 60.0% | 70.0% | 70.0% | 6/6 |
| P0 | Phi | 10.0% | 70.0% | 20.0% | 7/7 |
| P0 | Gemini | 70.0% | 70.0% | 100.0% | 8/8 |
| P1 | Qwen | 20.0% | 60.0% | 50.0% | 6/6 |
| P1 | Phi | 50.0% | 40.0% | 20.0% | 8/8 |
| P1 | Gemini | 60.0% | 70.0% | 90.0% | 7/7 |
| P2 | Qwen | 30.0% | 60.0% | 60.0% | 6/6 |
| P2 | Phi | 40.0% | 50.0% | 20.0% | 8/8 |
| P2 | Gemini | 60.0% | 80.0% | 80.0% | 9/9 |

## Full confusion matrices (non-zero cells; expected→predicted:count)

Each matrix has denominator 10 and includes `no_valid_output` predictions.

| Package | Model | Work mode | Last activity | Title fit |
|---|---|---|---|---|
| P0 | Qwen | executor→[executor:3, no_valid_output:2]; mixed→[no_valid_output:1]; one_off→[manager:1, one_off:3] | awaiting_input→[completed:1, in_progress:1]; completed→[completed:7]; in_progress→[completed:1] | false→[false:1, no_valid_output:3]; true→[true:6] |
| P0 | Phi | executor→[executor:1, mixed:3, no_valid_output:1]; mixed→[no_valid_output:1]; one_off→[mixed:3, unknown:1] | awaiting_input→[completed:1, in_progress:1]; completed→[completed:6, unknown:1]; in_progress→[in_progress:1] | false→[false:1, no_valid_output:2, true:1]; true→[false:4, no_valid_output:1, true:1] |
| P0 | Gemini | executor→[executor:4, one_off:1]; mixed→[executor:1]; one_off→[executor:1, one_off:3] | awaiting_input→[awaiting_input:1, completed:1]; completed→[completed:6, in_progress:1]; in_progress→[completed:1] | false→[false:4]; true→[true:6] |
| P1 | Qwen | executor→[executor:2, no_valid_output:3]; mixed→[no_valid_output:1]; one_off→[executor:4] | awaiting_input→[completed:1, in_progress:1]; completed→[completed:6, no_valid_output:1]; in_progress→[no_valid_output:1] | false→[false:1, no_valid_output:3]; true→[false:1, no_valid_output:1, true:4] |
| P1 | Phi | executor→[executor:3, no_valid_output:2]; mixed→[no_valid_output:1]; one_off→[executor:1, mixed:1, one_off:2] | awaiting_input→[completed:1, in_progress:1]; completed→[awaiting_input:1, completed:4, in_progress:1, no_valid_output:1]; in_progress→[awaiting_input:1] | false→[false:1, no_valid_output:2, true:1]; true→[false:5, true:1] |
| P1 | Gemini | executor→[executor:3, no_valid_output:2]; mixed→[manager:1]; one_off→[no_valid_output:1, one_off:3] | awaiting_input→[completed:1, no_valid_output:1]; completed→[completed:7]; in_progress→[completed:1] | false→[false:3, no_valid_output:1]; true→[true:6] |
| P2 | Qwen | executor→[executor:2, no_valid_output:3]; mixed→[no_valid_output:1]; one_off→[executor:3, one_off:1] | awaiting_input→[completed:2]; completed→[completed:6, no_valid_output:1]; in_progress→[no_valid_output:1] | false→[false:1, no_valid_output:3]; true→[no_valid_output:1, true:5] |
| P2 | Phi | executor→[executor:3, no_valid_output:2]; mixed→[no_valid_output:1]; one_off→[executor:2, mixed:1, one_off:1] | awaiting_input→[completed:2]; completed→[awaiting_input:2, completed:5]; in_progress→[awaiting_input:1] | false→[false:1, no_valid_output:3]; true→[false:5, true:1] |
| P2 | Gemini | executor→[executor:3, no_valid_output:1, one_off:1]; mixed→[manager:1]; one_off→[executor:1, one_off:3] | awaiting_input→[awaiting_input:1, completed:1]; completed→[completed:7]; in_progress→[completed:1] | false→[false:3, no_valid_output:1]; true→[no_valid_output:1, true:5] |

## Per-label deterministic statistics

Format is `label precision/recall/support`; `n/a` means the denominator is zero.

| Package | Model | Work mode | Last activity | Title fit |
|---|---|---|---|---|
| P0 | Qwen | executor 1.00/0.60/5; mixed n/a/0.00/1; one_off 1.00/0.75/4 | awaiting_input n/a/0.00/2; completed 0.78/1.00/7; in_progress 0.00/0.00/1 | false 1.00/0.25/4; true 1.00/1.00/6 |
| P0 | Phi | executor 1.00/0.20/5; mixed 0.00/0.00/1; one_off n/a/0.00/4 | awaiting_input n/a/0.00/2; completed 0.86/0.86/7; in_progress 0.50/1.00/1 | false 0.20/0.25/4; true 0.50/0.17/6 |
| P0 | Gemini | executor 0.67/0.80/5; mixed n/a/0.00/1; one_off 0.75/0.75/4 | awaiting_input 1.00/0.50/2; completed 0.75/0.86/7; in_progress 0.00/0.00/1 | false 1.00/1.00/4; true 1.00/1.00/6 |
| P1 | Qwen | executor 0.33/0.40/5; manager n/a/n/a/0; mixed n/a/0.00/1; one_off n/a/0.00/4; unknown n/a/n/a/0 | awaiting_input n/a/0.00/2; blocked n/a/n/a/0; completed 0.86/0.86/7; in_progress 0.00/0.00/1; unknown n/a/n/a/0 | false 0.50/0.25/4; true 1.00/0.67/6 |
| P1 | Phi | executor 0.75/0.60/5; manager n/a/n/a/0; mixed 0.00/0.00/1; one_off 1.00/0.50/4; unknown n/a/n/a/0 | awaiting_input 0.00/0.00/2; blocked n/a/n/a/0; completed 0.80/0.57/7; in_progress 0.00/0.00/1; unknown n/a/n/a/0 | false 0.17/0.25/4; true 0.50/0.17/6 |
| P1 | Gemini | executor 1.00/0.60/5; manager 0.00/n/a/0; mixed n/a/0.00/1; one_off 1.00/0.75/4; unknown n/a/n/a/0 | awaiting_input n/a/0.00/2; blocked n/a/n/a/0; completed 0.78/1.00/7; in_progress n/a/0.00/1; unknown n/a/n/a/0 | false 1.00/0.75/4; true 1.00/1.00/6 |
| P2 | Qwen | executor 0.40/0.40/5; manager n/a/n/a/0; mixed n/a/0.00/1; one_off 1.00/0.25/4; unknown n/a/n/a/0 | awaiting_input n/a/0.00/2; blocked n/a/n/a/0; completed 0.75/0.86/7; in_progress n/a/0.00/1; unknown n/a/n/a/0 | false 1.00/0.25/4; true 1.00/0.83/6 |
| P2 | Phi | executor 0.60/0.60/5; manager n/a/n/a/0; mixed 0.00/0.00/1; one_off 1.00/0.25/4; unknown n/a/n/a/0 | awaiting_input 0.00/0.00/2; blocked n/a/n/a/0; completed 0.71/0.71/7; in_progress n/a/0.00/1; unknown n/a/n/a/0 | false 0.17/0.25/4; true 1.00/0.17/6 |
| P2 | Gemini | executor 0.75/0.60/5; manager 0.00/n/a/0; mixed n/a/0.00/1; one_off 0.75/0.75/4; unknown n/a/n/a/0 | awaiting_input 1.00/0.50/2; blocked n/a/n/a/0; completed 0.78/1.00/7; in_progress n/a/0.00/1; unknown n/a/n/a/0 | false 1.00/0.75/4; true 1.00/0.83/6 |

## UTS and valid-output quality by task

Each UTS denominator is 10 expected cases. Quality uses completed valid outputs only.

| Package | Model | Summary UTS / quality | Work UTS / quality | Last UTS / quality | Title UTS / quality |
|---|---|---:|---:|---:|---:|
| P0 | Qwen | 60.0 / 1.000 | 60.8 / 0.869 | 86.7 / 0.867 | 70.0 / 1.000 |
| P0 | Phi | 60.0 / 0.857 | 27.5 / 0.344 | 78.3 / 0.783 | 60.7 / 0.867 |
| P0 | Gemini | 78.7 / 0.983 | 95.0 / 0.950 | 84.4 / 0.938 | 100.0 / 1.000 |
| P1 | Qwen | 60.0 / 1.000 | 32.5 / 0.542 | 61.7 / 0.881 | 52.0 / 0.867 |
| P1 | Phi | 71.3 / 0.892 | 51.7 / 0.738 | 64.4 / 0.716 | 66.7 / 0.833 |
| P1 | Gemini | 66.7 / 0.952 | 70.0 / 1.000 | 87.8 / 0.975 | 90.0 / 1.000 |
| P2 | Qwen | 48.7 / 0.973 | 37.5 / 0.625 | 70.6 / 0.882 | 60.0 / 1.000 |
| P2 | Phi | 68.0 / 0.850 | 45.8 / 0.655 | 58.3 / 0.583 | 62.7 / 0.895 |
| P2 | Gemini | 88.7 / 0.985 | 85.0 / 0.944 | 95.6 / 0.956 | 80.0 / 1.000 |

## Fixed-judge dimensions by arm and task

Format is `dimension mean (n)`; invalid and judge-failed cases are excluded here but score zero in UTS.

### P0 Qwen — completed 30/30, skipped invalid 10, failed 0

- conversation-summary: concise_usefulness 4.000 (6); conversation_characterization 4.000 (6); factual_consistency 4.000 (6); material_coverage 4.000 (6); unsupported_claim_avoidance 4.000 (6)
- work-mode-classification: label_support 3.429 (7); mode_distinction 3.429 (7); reason_specificity 3.857 (7); unsupported_claim_avoidance 3.714 (7)
- last-activity: blocker_correctness 4.000 (10); final_meaningful_activity 4.000 (10); next_action_support 2.200 (10); not_source_copying 4.000 (10); status_correctness 3.600 (10); unsupported_claim_avoidance 3.800 (10)
- title-assessment: dominant_activity_fit 4.000 (7); suggestion_only_compliance 4.000 (7); suggestion_usefulness 4.000 (7); title_fits_correctness 4.000 (7); unsupported_claim_avoidance 4.000 (7)

### P0 Phi — completed 32/32, skipped invalid 8, failed 0

- conversation-summary: concise_usefulness 3.571 (7); conversation_characterization 3.286 (7); factual_consistency 4.000 (7); material_coverage 3.000 (7); unsupported_claim_avoidance 4.000 (7)
- work-mode-classification: label_support 1.625 (8); mode_distinction 1.625 (8); reason_specificity 2.000 (8); unsupported_claim_avoidance 2.875 (8)
- last-activity: blocker_correctness 4.000 (10); final_meaningful_activity 2.700 (10); next_action_support 2.600 (10); not_source_copying 3.600 (10); status_correctness 3.200 (10); unsupported_claim_avoidance 4.000 (10)
- title-assessment: dominant_activity_fit 3.429 (7); suggestion_only_compliance 4.000 (7); suggestion_usefulness 3.714 (7); title_fits_correctness 2.857 (7); unsupported_claim_avoidance 4.000 (7)

### P0 Gemini — completed 37/38, skipped invalid 2, failed 1

- conversation-summary: concise_usefulness 3.875 (8); conversation_characterization 4.000 (8); factual_consistency 4.000 (8); material_coverage 3.875 (8); unsupported_claim_avoidance 4.000 (8)
- work-mode-classification: label_support 3.800 (10); mode_distinction 3.800 (10); reason_specificity 3.900 (10); unsupported_claim_avoidance 3.900 (10)
- last-activity: blocker_correctness 4.000 (9); final_meaningful_activity 3.778 (9); next_action_support 3.556 (9); not_source_copying 4.000 (9); status_correctness 3.556 (9); unsupported_claim_avoidance 4.000 (9)
- title-assessment: dominant_activity_fit 4.000 (10); suggestion_only_compliance 4.000 (10); suggestion_usefulness 4.000 (10); title_fits_correctness 4.000 (10); unsupported_claim_avoidance 4.000 (10)

### P1 Qwen — completed 25/26, skipped invalid 14, failed 1

- conversation-summary: concise_usefulness 4.000 (6); conversation_characterization 4.000 (6); factual_consistency 4.000 (6); material_coverage 4.000 (6); unsupported_claim_avoidance 4.000 (6)
- work-mode-classification: label_support 1.333 (6); mode_distinction 2.167 (6); reason_specificity 3.000 (6); unsupported_claim_avoidance 4.000 (6)
- last-activity: blocker_correctness 4.000 (7); final_meaningful_activity 4.000 (7); next_action_support 2.429 (7); not_source_copying 4.000 (7); status_correctness 3.429 (7); unsupported_claim_avoidance 4.000 (7)
- title-assessment: dominant_activity_fit 3.333 (6); suggestion_only_compliance 4.000 (6); suggestion_usefulness 3.667 (6); title_fits_correctness 3.667 (6); unsupported_claim_avoidance 3.333 (6)

### P1 Phi — completed 32/32, skipped invalid 8, failed 0

- conversation-summary: concise_usefulness 3.625 (8); conversation_characterization 3.750 (8); factual_consistency 4.000 (8); material_coverage 3.000 (8); unsupported_claim_avoidance 4.000 (8)
- work-mode-classification: label_support 3.143 (7); mode_distinction 3.143 (7); reason_specificity 3.143 (7); unsupported_claim_avoidance 3.429 (7)
- last-activity: blocker_correctness 3.556 (9); final_meaningful_activity 3.333 (9); next_action_support 2.444 (9); not_source_copying 4.000 (9); status_correctness 2.444 (9); unsupported_claim_avoidance 3.111 (9)
- title-assessment: dominant_activity_fit 3.000 (8); suggestion_only_compliance 4.000 (8); suggestion_usefulness 3.500 (8); title_fits_correctness 3.000 (8); unsupported_claim_avoidance 4.000 (8)

### P1 Gemini — completed 32/32, skipped invalid 8, failed 0

- conversation-summary: concise_usefulness 3.857 (7); conversation_characterization 3.714 (7); factual_consistency 4.000 (7); material_coverage 3.714 (7); unsupported_claim_avoidance 4.000 (7)
- work-mode-classification: label_support 4.000 (7); mode_distinction 4.000 (7); reason_specificity 4.000 (7); unsupported_claim_avoidance 4.000 (7)
- last-activity: blocker_correctness 4.000 (9); final_meaningful_activity 3.556 (9); next_action_support 4.000 (9); not_source_copying 4.000 (9); status_correctness 4.000 (9); unsupported_claim_avoidance 4.000 (9)
- title-assessment: dominant_activity_fit 4.000 (9); suggestion_only_compliance 4.000 (9); suggestion_usefulness 4.000 (9); title_fits_correctness 4.000 (9); unsupported_claim_avoidance 4.000 (9)

### P2 Qwen — completed 25/26, skipped invalid 14, failed 1

- conversation-summary: concise_usefulness 4.000 (5); conversation_characterization 4.000 (5); factual_consistency 4.000 (5); material_coverage 3.600 (5); unsupported_claim_avoidance 4.000 (5)
- work-mode-classification: label_support 2.333 (6); mode_distinction 2.333 (6); reason_specificity 3.167 (6); unsupported_claim_avoidance 3.667 (6)
- last-activity: blocker_correctness 4.000 (8); final_meaningful_activity 3.875 (8); next_action_support 2.500 (8); not_source_copying 4.000 (8); status_correctness 3.500 (8); unsupported_claim_avoidance 4.000 (8)
- title-assessment: dominant_activity_fit 4.000 (6); suggestion_only_compliance 4.000 (6); suggestion_usefulness 4.000 (6); title_fits_correctness 4.000 (6); unsupported_claim_avoidance 4.000 (6)

### P2 Phi — completed 32/32, skipped invalid 8, failed 0

- conversation-summary: concise_usefulness 3.375 (8); conversation_characterization 3.375 (8); factual_consistency 4.000 (8); material_coverage 3.000 (8); unsupported_claim_avoidance 4.000 (8)
- work-mode-classification: label_support 2.429 (7); mode_distinction 2.429 (7); reason_specificity 3.143 (7); unsupported_claim_avoidance 3.857 (7)
- last-activity: blocker_correctness 2.400 (10); final_meaningful_activity 2.900 (10); next_action_support 1.500 (10); not_source_copying 4.000 (10); status_correctness 2.800 (10); unsupported_claim_avoidance 2.900 (10)
- title-assessment: dominant_activity_fit 3.714 (7); suggestion_only_compliance 4.000 (7); suggestion_usefulness 3.857 (7); title_fits_correctness 2.857 (7); unsupported_claim_avoidance 4.000 (7)

### P2 Gemini — completed 36/36, skipped invalid 4, failed 0

- conversation-summary: concise_usefulness 4.000 (9); conversation_characterization 4.000 (9); factual_consistency 4.000 (9); material_coverage 3.778 (9); unsupported_claim_avoidance 4.000 (9)
- work-mode-classification: label_support 3.778 (9); mode_distinction 3.778 (9); reason_specificity 3.889 (9); unsupported_claim_avoidance 3.889 (9)
- last-activity: blocker_correctness 4.000 (10); final_meaningful_activity 3.600 (10); next_action_support 3.600 (10); not_source_copying 4.000 (10); status_correctness 4.000 (10); unsupported_claim_avoidance 4.000 (10)
- title-assessment: dominant_activity_fit 4.000 (8); suggestion_only_compliance 4.000 (8); suggestion_usefulness 4.000 (8); title_fits_correctness 4.000 (8); unsupported_claim_avoidance 4.000 (8)

## Per-task failure taxonomy

Each cell lists terminal candidate failures out of ten expected positions. Empty means zero.

| Package/model | Summary | Work | Last | Title |
|---|---|---|---|---|
| P0 Qwen | context 2, schema 1, timeout 1 | context 2, timeout 1 | — | context 2, timeout 1 |
| P0 Phi | context 2, schema 1 | context 2 | — | context 2, schema 1 |
| P0 Gemini | invalid JSON 1, schema 1 | — | — | — |
| P1 Qwen | context 2, timeout 2 | context 2, timeout 2 | timeout 2 | context 2, timeout 2 |
| P1 Phi | context 2 | context 2, schema 1 | schema 1 | context 2 |
| P1 Gemini | invalid JSON 2, provider response 1 | invalid JSON 3 | invalid JSON 1 | invalid JSON 1 |
| P2 Qwen | context 2, timeout 2 | context 2, timeout 2 | timeout 2 | context 2, timeout 2 |
| P2 Phi | context 2 | context 2, schema 1 | — | context 2, schema 1 |
| P2 Gemini | invalid JSON 1 | invalid JSON 1 | — | invalid JSON 2 |

The prompt variants did not remove any of the six local context failures. On Qwen they increased
timeouts from three at P0 to eight in each variant. On Phi total reliability stayed at 32/40 and
schema failures moved between tasks. On Gemini P1 introduced the largest JSON reliability loss.

## Token, latency, and cost interpretation

Observed generation usage availability includes usage attached to terminal schema-invalid responses,
so it can exceed the valid count. Missing usage is explicit in the operating table. P1/P2 candidate
usage totaled:

| Model | P1 prompt/output/total | P2 prompt/output/total | P2 total delta |
|---|---:|---:|---:|
| Qwen | 61,454 / 3,493 / 64,947 | 66,394 / 2,235 / 68,629 | +3,682 |
| Phi | 97,074 / 3,502 / 100,576 | 102,590 / 3,615 / 106,205 | +5,629 |
| Gemini | 197,400 / 6,662 / 204,062 | 209,792 / 5,860 / 215,652 | +11,590 |

Qwen P2 reduced median latency versus P1 but produced no usable-case gain. Phi P2 was slower and
also produced no gain. Gemini P2 was faster at the median and recovered four cases relative to P1,
but remained below P0 and failed the title-task portability guardrail. Local and cloud latency are
not hardware-equivalent measurements.

Hosted accounting covered exactly 80 candidate calls, 184 development judge calls, and four
fictional judge-gate calls. Candidate usage was 407,192 input and 12,522 output tokens. Development
judge usage was 806,078 input and 56,371 output tokens on 182 successful responses; two terminal
judge failures reported no usage. The fictional judge gate used 3,709 input and 1,467 output tokens.
At [current Google global list-price assumptions](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)—Gemini
3.5 Flash $2.70 input/$16.20 output and Gemini 3.1 Pro Preview $3.60 input/$21.60 output per million
tokens—the estimated total is $5.47: $1.30 candidate, $4.12 development judge, and $0.05 gate. This
is a reproducible estimate, not an invoice.

## Global portability comparison

| Package | Qwen | Phi | Gemini | Interpretation |
|---|---:|---:|---:|---|
| P0 | 30/40 | 32/40 | 38/40 | Best pooled local and best cloud reliability |
| P1 | 26/40 | 32/40 | 32/40 | Qwen and Gemini regress; ineligible |
| P2 | 26/40 | 32/40 | 36/40 | Qwen and Gemini title regress; ineligible |

P1's improvement in Phi work-mode exact agreement and survivor quality was model-specific. P2's
strong Gemini UTS did not transfer to local reliability. The evidence does not support different
prompts per model or task, and the study explicitly forbids such cherry-picking.

## Task-difficulty assessment

| Task | P0 local usable/20 | Best variant/20 | Common failures | Semantic evidence | Assessment |
|---|---:|---:|---|---|---|
| Summary | 13 | 14 | context; Gemini JSON | High survivor quality, but one-case reliability gain | Moderate; small non-shared gain |
| Work mode | 15 | 13 | context/timeout/JSON | Phi P1 exact 50% vs P0 10%; Qwen P1 exact 20% vs 60% | Hardest global semantic tradeoff |
| Last activity | 20 | 18 | timeout; Phi P1 schema | High validity; Phi P2 next-action quality weak | Easiest structurally, still semantically sensitive |
| Title | 14 | 14 | context/timeout/JSON/schema | Gemini fell 100%→80% exact under P2 | Sensitive to examples; no global gain |

Difficulty is inferred from this frozen corpus, not intuition. Confidence is moderate within the
ten-conversation development sample and low for population-level claims.

## P3 decision

The mechanical trigger found repeated context-length failures in at least four pooled local cases
for summary, work, and title under both P1 and P2. The final required condition was false: those
same failures already existed in P0, and a reliable fix would need selector, context, or application
changes rather than model-neutral prompt wording. Qwen timeouts and Phi schema failures were not a
shared category. Therefore P3 has no prompt, candidate, score, judge, or cost evidence.

## Package selection and freeze

The predeclared lexicographic rule selected P0 at criterion one: 62/80 pooled local usable cases
versus 58/80 for both variants. Guardrails independently make P1 and P2 ineligible. P1 loses four
Qwen cases and six Gemini cases, including three work-mode cases. P2 loses four Qwen cases and two
Gemini title cases. Semantic tie-breaks are secondary and cannot override those failures.

The selected package is the complete four-task P0 unit. A private immutable manifest binds exact
prompt texts and hashes, trial identities, selection arithmetic, non-prompt contracts, execution
and judge identities, both split identities, context, commit, timestamp, and holdout attestation.
The privacy-safe tracked package at `bench/prompts/wp-5.2b3b/selected-p0.yaml` is byte-identical to
the accepted authority catalog. Production defaults are unchanged.

## Development-set overfitting and limitations

- Ten conversations make small changes highly unstable and do not support significance claims.
- Metadata quotas improve coverage but do not create a random population sample.
- Prompt variants were authored from public contracts and aggregate P0 failure classes, but package
  selection still uses development outcomes and needs a one-shot holdout.
- FABLE references are silver references; deterministic disagreement is not automatically model
  error.
- The fixed judge is a preview-model evaluator and P0 judge evidence came from an earlier run window.
- The Phi P1 3/4 exception is documented experimental policy, not a normal gate pass.
- Token usage is incomplete for failures; hosted cost uses list prices, not billing export.
- No holdout result exists. Do not claim generalization, production readiness, or prompt superiority.

## Supported observations for an article

1. **More explicit prompts reduced reliability in this development study.** P0 achieved 62/80
   pooled local usable cases; both P1 and P2 achieved 58/80. Caveat: ten conversations. Confidence:
   high for this frozen sample, low for broader generalization. Prohibited overclaim: “schema-first
   prompts are generally worse.”
2. **Survivor quality can improve while whole-package utility falls.** Phi P1 valid-output quality
   rose 0.713→0.795 and UTS 56.6→63.5 while total validity stayed 32/40; Qwen P1 quality and UTS
   both fell with validity. Caveat: judge is one preview model. Confidence: moderate. Prohibited
   overclaim: “the judge proves P1 is better.”
3. **Few-shot cost did not buy local reliability.** P2 added an estimated 858 static prompt tokens
   over P0 and used 3,682 more Qwen and 5,629 more Phi total tokens than P1, yet both local arms
   retained P1's usable counts. Confidence: high for observed accounting. Prohibited overclaim:
   “few-shot prompting never helps small models.”
4. **Portability must be a guardrail, not the optimization target.** Gemini P2 reached 36/40 and
   UTS 87.3, but lost two title cases versus P0 and could not rescue Qwen's four-case regression.
   Confidence: high for the rule application. Prohibited overclaim: “Gemini performance predicts
   local performance.”
5. **Prompt wording could not repair a structural context boundary.** Six context failures remained
   in every local package; B3A had already shown that 16K did not recover them. Confidence: high for
   these cases. Prohibited overclaim: “context is irrelevant in all applications.”
6. **Last activity was structurally easiest but not semantically solved.** P0 was 20/20 usable
   locally; Phi P2 was 10/10 valid yet had judge means 1.5 for next-action support and 2.8 for status
   correctness. Confidence: moderate. Prohibited overclaim: “schema validity equals correctness.”

## Chart-ready figure suggestions

1. Grouped usable-rate bars by package, model, and task using the reliability table.
2. Stacked failure bars from the per-task taxonomy.
3. Reliability-versus-valid-output-quality scatter with macro UTS labels.
4. Static prompt-token overhead and observed generation-token delta versus usable-case delta.
5. Local pooled reliability with Gemini portability guardrail markers.
6. Task heatmap combining usable count, deterministic exact agreement, and task UTS.

## Suggested article outline

1. Why context was tested before prompts.
2. The metadata-only 10/20 development/holdout design.
3. P0, schema-first P1, and bounded-few-shot P2.
4. Reliability first: what the nine development arms showed.
5. Why deterministic agreement and judge quality tell different stories.
6. Cost and latency without hiding failures.
7. Applying a frozen selection rule and rejecting attractive survivor metrics.
8. What the untouched holdout must decide next.

## Evidence links and B3C placeholder

- B3A context decision: `md/handoffs/reports/WP-5.2B3A-completion-report.md`
- B3A article evidence: `md/handoffs/reports/WP-5.2B3A-context-comparison-article-brief.md`
- B3B completion: `md/handoffs/reports/WP-5.2B3B-completion-report.md`
- B3B selected package: `bench/prompts/wp-5.2b3b/selected-p0.yaml`
- Future B3C evidence: not yet created; holdout results do not exist.

