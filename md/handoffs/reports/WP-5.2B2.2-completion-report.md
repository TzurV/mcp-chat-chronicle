# WP-5.2B2.2 Completion Report

## 1. Status and executive summary

Ready for PM validation.

Three fresh independent 120-case arms completed at the accepted frozen 30-conversation scope.
All 360 candidate positions are terminal with zero unaccounted. Phi-4 Mini produced 77/120
schema-valid outputs (64.2%), Llama 3.2 3B produced 71/120 (59.2%), and Gemma 3 4B produced
62/120 (51.7%).

Fixed-Pro judging completed 208/210 eligible outputs. Phi completed 77/77 and Gemma completed
62/62. Llama completed 69/71 and retained two provider-invalid-JSON failures after the single
configured bounded retry. Three cache-only replays exited zero with zero calls and byte-identical
packages, candidate attempts, judge attempts, judge outputs, and aggregate reports.

This is a complete development-corpus comparison against silver FABLE references and an automated
preview judge. It is not an independent, statistically representative, or scientific evaluation.

## 2. Clean preflight and immutable baseline evidence

Execution began from clean HEAD `46fef2f2d66cd8ca7e444a3839a480a4ce48d17b`. Poetry resolved
to this repository's `.venv`. The frozen database passed immutable read-only integrity validation
at schema version 3 with 711 conversations and 28,370 messages and no WAL/SHM sidecars.

Frozen/live database, snapshot-manifest, accepted complete-arm, checkpoint, and judge-attempt
identities were recorded privately. Accepted Gemini-120, Qwen-120, Llama-120, Qwen-40, and
WP-5.2B2.1 packages verified unchanged. Approximately 288 GB disk was free, execution used AC
power with AC sleep disabled, and LM Studio was ready for single-worker execution.

All three accepted artifacts independently matched their pinned exact byte sizes and SHA-256
values before use.

## 3. Complete 120-case identity reconciliation

Each arm independently reconstructed frozen-prefix-v1 over all 30 selected conversations and the
four accepted tasks. The three new ordered 120-case identities matched each other and the accepted
Gemini-120, Qwen-120, and Llama-120 identities. Their first 40 positions matched Qwen-40 and all
three accepted WP-5.2B2.1 checkpoint packages.

Exact identities remain private. No accepted package was modified, extended, copied, or repackaged.

## 4. Owner authorization and disclosure boundary

The owner authorized fixed-Pro judging for these three complete arms: at most 360 baseline cases
plus one configured bounded retry per failed eligible case, using the selected 30 private inputs,
schema-valid candidate output, and corresponding FABLE reference through Vertex AI
`gemini-3.1-pro-preview` in `global`, ADC, and rubric v1.

Before judging, ADC validity and project presence were confirmed without exposing values; both
accepted location aliases were set to `global`; and one synthetic application-owned judge request
passed provider schema, strict application schema, identity, and evidence membership.

## 5. Common model/task/settings contract

All candidates used the accepted LM Studio Community Q4_K_M artifacts, LM Studio CLI commit
`9902c3a`, llama.cpp Vulkan AVX2 engine 2.25.2, context 8,192, parallelism/concurrency 1,
temperature 0, candidate retries 0, strict structured output, and task-owned output limits.

Task order was summary, work mode, last activity, and title assessment. Prompts, selectors,
schemas, finalizers, evidence rules, task versions, references, and output limits were unchanged.
The judge used rubric v1, temperature 0, maximum 1,000 output tokens, and reasoning `none`.
Gemma 4 was neither loaded nor probed.

## 6. Independent full-arm package policy

Each complete arm used a unique ignored bundle, generation-work directory, immutable package,
scoring directory, and judge cache. All 120 candidate calls were newly generated. Checkpoint
attempts were not copied or promoted, and no package-merging code was introduced.

## 7. Phi generation/package/deterministic/judge/cache evidence

- Candidate: 120 terminal; 77 valid; 43 failed; zero unaccounted.
- Failures: context length 21, schema validation 12, timeout 10.
- Per-task validity (summary/mode/activity/title): 14/18/29/16.
- Evidence-valid and cross-field-valid: 77/77.
- Summary date/length valid: 14/14; title suggestion-valid: 15.
- Judge: 77 eligible; 77 completed; 0 failed; 43 skipped.
- Judge attempts: 77 baseline; no retry required.
- Cache-only: exit zero, zero calls, unchanged evidence hashes.

## 8. Llama 3B evidence

- Candidate: 120 terminal; 71 valid; 49 failed; zero unaccounted.
- Failures: context length 21, evidence validation 15, schema validation 3, timeout 10.
- Per-task validity (summary/mode/activity/title): 12/19/23/17.
- Evidence-valid and cross-field-valid: 71/71.
- Summary date/length valid: 12/12; title suggestion-valid: 17.
- Judge: 71 eligible; 69 completed; 2 terminal provider-invalid-JSON failures; 49 skipped.
- Judge attempts: 71 baseline plus two bounded retries.
- Cache-only: exit zero, zero calls, unchanged evidence hashes.

Awkward but schema-valid content was preserved without repair or reinterpretation.

## 9. Gemma 3 evidence

- Candidate: 120 terminal; 62 valid; 58 failed; zero unaccounted.
- Failures: context length 30, schema validation 24, evidence validation 2, invalid JSON 1,
  timeout 1.
- Per-task validity (summary/mode/activity/title): 12/19/25/6.
- Evidence-valid and cross-field-valid: 62/62.
- Summary date/length valid: 12/12; title suggestion-valid: 6.
- Judge: 62 eligible; 62 completed; 0 failed; 58 skipped.
- Judge attempts: 62 baseline plus one successful bounded retry.
- Cache-only: exit zero, zero calls, unchanged evidence hashes.

Gemma remains a weak research comparator rather than a product-quality endorsement.

## 10. 360-position accounting

| Candidate | Expected | Valid | Failed | Terminal | Unaccounted |
|---|---:|---:|---:|---:|---:|
| Phi-4 Mini | 120 | 77 | 43 | 120 | 0 |
| Llama 3.2 3B | 120 | 71 | 49 | 120 | 0 |
| Gemma 3 4B | 120 | 62 | 58 | 120 | 0 |
| **Total** | **360** | **210** | **150** | **360** | **0** |

Judge accounting is 208 completed + 2 failed = 210 eligible; 150 invalid candidates were skipped.

## 11. Per-task reliability and failure boundaries

| Candidate/task | Valid | Failed | Valid rate |
|---|---:|---:|---:|
| Phi summary | 14 | 16 | 46.7% |
| Phi mode | 18 | 12 | 60.0% |
| Phi activity | 29 | 1 | 96.7% |
| Phi title | 16 | 14 | 53.3% |
| Llama summary | 12 | 18 | 40.0% |
| Llama mode | 19 | 11 | 63.3% |
| Llama activity | 23 | 7 | 76.7% |
| Llama title | 17 | 13 | 56.7% |
| Gemma summary | 12 | 18 | 40.0% |
| Gemma mode | 19 | 11 | 63.3% |
| Gemma activity | 25 | 5 | 83.3% |
| Gemma title | 6 | 24 | 20.0% |

Context-limit outcomes affected every arm under the fixed 8,192-token contract. Phi and Llama also
retained ten timeouts each. Gemma's principal additional boundary was 24 schema failures,
concentrated heavily in title assessment.

## 12. Full deterministic confusion and per-label metrics

Rows are FABLE labels; columns are candidate labels. `NVO` means no valid output.

### Phi-4 Mini

| Work mode | executor | manager | mixed | one-off | unknown | NVO |
|---|---:|---:|---:|---:|---:|---:|
| executor | 1 | 0 | 5 | 0 | 0 | 8 |
| manager | 0 | 0 | 1 | 0 | 0 | 2 |
| mixed | 0 | 0 | 0 | 0 | 0 | 1 |
| one-off | 0 | 0 | 7 | 2 | 2 | 1 |

| Last activity | awaiting | blocked | completed | in progress | unknown | NVO |
|---|---:|---:|---:|---:|---:|---:|
| awaiting | 0 | 0 | 3 | 4 | 0 | 0 |
| completed | 0 | 0 | 14 | 0 | 1 | 1 |
| in progress | 0 | 0 | 3 | 4 | 0 | 0 |

| Title fit | false | true | NVO |
|---|---:|---:|---:|
| false | 2 | 1 | 8 |
| true | 10 | 3 | 6 |

### Llama 3.2 3B

| Work mode | executor | manager | mixed | one-off | unknown | NVO |
|---|---:|---:|---:|---:|---:|---:|
| executor | 0 | 0 | 5 | 1 | 0 | 8 |
| manager | 0 | 0 | 1 | 0 | 0 | 2 |
| mixed | 0 | 0 | 0 | 0 | 0 | 1 |
| one-off | 0 | 0 | 8 | 3 | 1 | 0 |

| Last activity | awaiting | blocked | completed | in progress | unknown | NVO |
|---|---:|---:|---:|---:|---:|---:|
| awaiting | 1 | 0 | 2 | 2 | 0 | 2 |
| completed | 0 | 0 | 6 | 6 | 0 | 4 |
| in progress | 0 | 0 | 0 | 5 | 1 | 1 |

| Title fit | false | true | NVO |
|---|---:|---:|---:|
| false | 1 | 4 | 6 |
| true | 0 | 12 | 7 |

### Gemma 3 4B

| Work mode | executor | manager | mixed | one-off | unknown | NVO |
|---|---:|---:|---:|---:|---:|---:|
| executor | 2 | 2 | 3 | 0 | 0 | 7 |
| manager | 0 | 1 | 0 | 0 | 0 | 2 |
| mixed | 0 | 0 | 0 | 0 | 0 | 1 |
| one-off | 0 | 6 | 3 | 2 | 0 | 1 |

| Last activity | awaiting | blocked | completed | in progress | unknown | NVO |
|---|---:|---:|---:|---:|---:|---:|
| awaiting | 1 | 0 | 3 | 1 | 0 | 2 |
| completed | 0 | 0 | 12 | 3 | 0 | 1 |
| in progress | 0 | 0 | 4 | 1 | 0 | 2 |

| Title fit | false | true | NVO |
|---|---:|---:|---:|
| false | 0 | 1 | 10 |
| true | 2 | 3 | 14 |

Exact agreement:

| Candidate | Work mode | Last activity | Title fit |
|---|---:|---:|---:|
| Phi | 10.0% | 60.0% | 16.7% |
| Llama 3B | 10.0% | 40.0% | 43.3% |
| Gemma 3 | 16.7% | 46.7% | 10.0% |

Per-label precision/recall/support:

| Candidate/task/label | Precision | Recall | Support |
|---|---:|---:|---:|
| Phi mode/executor | 1.000 | 0.071 | 14 |
| Phi mode/manager | unavailable | 0.000 | 3 |
| Phi mode/mixed | 0.000 | 0.000 | 1 |
| Phi mode/one-off | 1.000 | 0.167 | 12 |
| Phi activity/awaiting | unavailable | 0.000 | 7 |
| Phi activity/completed | 0.700 | 0.875 | 16 |
| Phi activity/in progress | 0.500 | 0.571 | 7 |
| Phi title/false | 0.167 | 0.182 | 11 |
| Phi title/true | 0.750 | 0.158 | 19 |
| Llama mode/executor | unavailable | 0.000 | 14 |
| Llama mode/manager | unavailable | 0.000 | 3 |
| Llama mode/mixed | 0.000 | 0.000 | 1 |
| Llama mode/one-off | 0.750 | 0.250 | 12 |
| Llama activity/awaiting | 1.000 | 0.143 | 7 |
| Llama activity/completed | 0.750 | 0.375 | 16 |
| Llama activity/in progress | 0.385 | 0.714 | 7 |
| Llama title/false | 1.000 | 0.091 | 11 |
| Llama title/true | 0.750 | 0.632 | 19 |
| Gemma mode/executor | 1.000 | 0.143 | 14 |
| Gemma mode/manager | 0.111 | 0.333 | 3 |
| Gemma mode/mixed | 0.000 | 0.000 | 1 |
| Gemma mode/one-off | 1.000 | 0.167 | 12 |
| Gemma activity/awaiting | 1.000 | 0.143 | 7 |
| Gemma activity/completed | 0.632 | 0.750 | 16 |
| Gemma activity/in progress | 0.200 | 0.143 | 7 |
| Gemma title/false | 0.000 | 0.000 | 11 |
| Gemma title/true | 0.750 | 0.158 | 19 |

Blocked and unknown activity labels and unknown work mode have zero reference support; undefined
precision/recall values are reported as unavailable.

## 13. Fixed-Pro metrics by task and denominator

Each value is `mean (n)` over successfully judged outputs for that task.

| Candidate/task | Dimension means |
|---|---|
| Phi summary | factual consistency 3.929 (14); material coverage 3.000 (14); concise usefulness 3.429 (14); conversation characterization 3.214 (14); unsupported-claim avoidance 4.000 (14) |
| Phi mode | label support 2.611 (18); mode distinction 2.611 (18); reason specificity 2.778 (18); unsupported-claim avoidance 3.444 (18) |
| Phi activity | blocker correctness 4.000 (29); final meaningful activity 3.069 (29); status correctness 3.310 (29); next-action support 2.448 (29); not-source-copying 3.724 (29); unsupported-claim avoidance 3.931 (29) |
| Phi title | dominant-activity fit 3.250 (16); title-fits correctness 2.750 (16); suggestion usefulness 3.875 (16); suggestion-only compliance 4.000 (16); unsupported-claim avoidance 4.000 (16) |
| Llama summary | factual consistency 4.000 (12); material coverage 3.500 (12); concise usefulness 3.917 (12); conversation characterization 3.500 (12); unsupported-claim avoidance 4.000 (12) |
| Llama mode | label support 2.053 (19); mode distinction 2.000 (19); reason specificity 2.421 (19); unsupported-claim avoidance 3.000 (19) |
| Llama activity | blocker correctness 1.810 (21); final meaningful activity 3.762 (21); status correctness 2.476 (21); next-action support 2.857 (21); not-source-copying 3.857 (21); unsupported-claim avoidance 3.429 (21) |
| Llama title | dominant-activity fit 3.588 (17); title-fits correctness 4.000 (17); suggestion usefulness 3.765 (17); suggestion-only compliance 4.000 (17); unsupported-claim avoidance 4.000 (17) |
| Gemma summary | factual consistency 4.000 (12); material coverage 3.750 (12); concise usefulness 4.000 (12); conversation characterization 3.750 (12); unsupported-claim avoidance 4.000 (12) |
| Gemma mode | label support 1.842 (19); mode distinction 1.842 (19); reason specificity 2.579 (19); unsupported-claim avoidance 3.526 (19) |
| Gemma activity | blocker correctness 4.000 (25); final meaningful activity 3.960 (25); status correctness 3.360 (25); next-action support 3.240 (25); not-source-copying 4.000 (25); unsupported-claim avoidance 3.920 (25) |
| Gemma title | dominant-activity fit 3.333 (6); title-fits correctness 2.667 (6); suggestion usefulness 4.000 (6); suggestion-only compliance 3.333 (6); unsupported-claim avoidance 4.000 (6) |

Llama's two terminal failures are last-activity cases. Judge run windows occurred consecutively in
the same execution session; historical preview scores were produced in earlier windows.

## 14. Latency, usage, runtime, artifact, and hardware provenance

| Candidate | Observed wall span | Summed latency | Overall p50/p95 |
|---|---:|---:|---:|
| Phi | 2h18m50.713s | 2h18m47.392s | 54.608/180.031s |
| Llama 3B | 2h21m16.435s | 2h21m11.071s | 51.124/180.061s |
| Gemma 3 | 2h08m12.976s | 2h08m09.243s | 61.834/156.592s |

Per-task p50/p95:

| Candidate | Summary | Mode | Activity | Title |
|---|---|---|---|---|
| Phi | 52.297/180.015s | 45.172/180.062s | 59.000/129.890s | 47.280/180.030s |
| Llama 3B | 49.547/180.061s | 49.719/180.047s | 59.375/143.234s | 45.452/180.047s |
| Gemma 3 | 58.515/161.000s | 49.108/148.047s | 79.030/128.344s | 50.672/141.343s |

Exact per-task usage:

| Candidate/task | Available | Missing | Prompt | Completion | Total |
|---|---:|---:|---:|---:|---:|
| Phi summary | 20 | 10 | 54,266 | 3,092 | 57,358 |
| Phi mode | 19 | 11 | 49,534 | 1,808 | 51,342 |
| Phi activity | 30 | 0 | 77,013 | 4,197 | 81,210 |
| Phi title | 20 | 10 | 54,970 | 2,097 | 57,067 |
| Llama summary | 20 | 10 | 56,694 | 2,749 | 59,443 |
| Llama mode | 20 | 10 | 55,710 | 2,183 | 57,893 |
| Llama activity | 30 | 0 | 78,063 | 3,350 | 81,413 |
| Llama title | 19 | 11 | 50,501 | 1,848 | 52,349 |
| Gemma summary | 20 | 10 | 62,938 | 4,576 | 67,514 |
| Gemma mode | 20 | 10 | 63,438 | 2,843 | 66,281 |
| Gemma activity | 29 | 1 | 83,518 | 5,605 | 89,123 |
| Gemma title | 20 | 10 | 63,659 | 3,183 | 66,842 |

Missing usage was not inferred. Provider token counts are tokenizer-specific and not direct quality
measures.

The privacy-safe hardware class was a 4-core/8-thread 11th-generation Intel mobile CPU,
approximately 32 GiB RAM, and integrated Intel Iris Xe graphics reporting approximately 2 GiB
shared adapter memory. All artifacts were Q4_K_M. Context remained 8,192 and parallelism 1.

## 15. Six-candidate complete-scope comparison

Reliability and terminal judge coverage:

| Candidate | Execution | Valid | Valid rate | Judge completed/eligible |
|---|---|---:|---:|---:|
| Gemini 3.5 Flash | Vertex cloud | 112/120 | 93.3% | 110/112 |
| Qwen3.5 4B | local | 84/120 | 70.0% | 84/84 |
| Phi-4 Mini | local | 77/120 | 64.2% | 77/77 |
| Llama 3.2 3B | local | 71/120 | 59.2% | 69/71 |
| Gemma 3 4B | local | 62/120 | 51.7% | 62/62 |
| Llama 3.2 1B | local | 57/120 | 47.5% | 56/57 |

Deterministic agreement:

| Candidate | Work mode | Last activity | Title fit |
|---|---:|---:|---:|
| Gemini | 63.3% | 70.0% | 83.3% |
| Qwen | 33.3% | 60.0% | 56.7% |
| Phi | 10.0% | 60.0% | 16.7% |
| Llama 3B | 10.0% | 40.0% | 43.3% |
| Gemma 3 | 16.7% | 46.7% | 10.0% |
| Llama 1B | 3.3% | 20.0% | 6.7% |

Candidate latency p50/p95:

| Candidate | p50 | p95 |
|---|---:|---:|
| Gemini | 2.156s | 12.562s |
| Llama 1B | 17.312s | 53.609s |
| Llama 3B | 51.124s | 180.061s |
| Phi | 54.608s | 180.031s |
| Qwen | 62.094s | 168.375s |
| Gemma 3 | 61.834s | 156.592s |

Gemini has the strongest whole-package reliability and deterministic agreement. Qwen is the
strongest local complete-arm reliability result. Phi improves on the Llama 1B floor and has strong
activity validity, but categorical agreement is weak. Llama 3B improves materially over 1B yet
retains weak blocker and mode quality. Gemma valid outputs often score strongly, but its 51.7%
whole-package reliability and 20% title validity sharply limit utility.

Historical and current scores use the same rubric but different preview-model run windows.
No composite score is computed here.

## 16. Preserved failures and task-specific observations

All 150 candidate failures and two terminal judge failures remain private immutable evidence.
Candidate failures were never repaired, truncated, suppressed, or retried. Valid semantic scores
were never retried because they disagreed with FABLE.

Common limitations were fixed-context rejection and timeout at the task contract. Phi was highly
reliable on last activity but weak on title-fit agreement. Llama's valid titles scored well while
last-activity blocker correctness remained poor. Gemma's valid summaries and activity outputs
scored strongly, but title schema reliability was only 6/30.

## 17. Cache-only evidence

All three cache-only commands exited zero and made zero provider calls. Attempt counts remained
Phi 77, Llama 73, and Gemma 63. Pre/post hashes were identical for candidate packages, candidate
attempts, judge attempts, judge outputs, and aggregate reports.

## 18. Implementation defects/fixes

No tracked application or harness defect was found and no tracked code changed. The accepted
Vertex location aliases were set explicitly to `global` as required by the prior routing
diagnosis. No model, provider, project, region, authentication, schema, prompt, rubric, runtime,
context, retry policy, or output limit changed.

## 19. Privacy, immutability, and tracking evidence

Private configs, bundles, candidate packages, outputs, references, judge attempts, rationales,
identities, hashes, and logs remain ignored. No credential, project/account identity, source text,
private path, or model output appears in this report.

Frozen/live databases, snapshot manifest, accepted checkpoint packages, accepted historical
complete arms, and historical judge evidence remained unchanged. Git tracks no private evaluation
artifact. Delivery consists only of this unstaged report.

## 20. LP-4.1 analysis handoff summary

LP-4.1 now has six aligned complete-scope arms with reliability, deterministic, semantic, latency,
usage, runtime, and resource evidence. Analysis should:

- keep candidate validity and semantic quality separate;
- retain no-valid-output in deterministic denominators;
- reproduce any composite score from an explicit published formula;
- perform sensitivity analysis before narrative claims;
- treat Gemma as a weak research comparator;
- note local-versus-cloud runtime and tokenizer differences;
- preserve preview-judge run-window drift;
- avoid claims of statistical representativeness or independent evaluation.

This work package does not choose publication metrics, implement a composite, draft the article, or
generate graphics.

## 21. Limitations

The development corpus is selected, silver-referenced, repeatedly used, and only 30 conversations.
The automated judge is a preview model and two Llama cases remain unscored. Local timings reflect
one laptop class and single-worker execution. Provider token counts are not cross-tokenizer
equivalents. Results measure the fixed 8,192-token/task contract, not advertised maximum context.

## 22. Line-by-line acceptance checklist

1. Clean requested HEAD and repository `.venv`: pass.
2. Frozen integrity/schema/counts/sidecars: pass.
3. Complete 120-case identity matches all accepted complete arms: pass.
4. First 40 matches accepted checkpoints: pass.
5. Three fresh independent packages with no merge/promotion: pass.
6. Artifact size/hash and loaded runtime identity rechecked: pass.
7. 360 candidate positions terminal, zero unaccounted: pass.
8. Packages verify and score deterministically: pass.
9. Every eligible output has a terminal fixed-Pro outcome: pass.
10. Candidate failures visible and unrepaired: pass.
11. One bounded retry only for each failed eligible judge case: pass.
12. Three cache-only zero-call replays with byte-stable evidence: pass.
13. Fixed artifact/runtime/context/task/judge contracts unchanged: pass.
14. Full privacy-safe deterministic, judge, latency, usage, and provenance evidence: pass.
15. Six-candidate comparison provided without composite score: pass.
16. Databases, checkpoints, and historical packages unchanged: pass.
17. No private artifact or credential tracked: pass.
18. No Gemma 4, article drafting, tuning, or independent evaluation: pass.
19. Required repository validation: pass (focused tests, Ruff, Poetry metadata, CLI help,
    package verification, identity checks, diff checks, and Git-boundary checks).
20. Delivery unstaged and uncommitted for PM validation: pass.
