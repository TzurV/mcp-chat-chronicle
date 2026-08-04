# WP-5.2C1 RunPod Qwen Speed/Context Study — Completion Report

Date: 2026-08-04

Status: complete; ready for PM validation

Continuation: WP-5.2C1.1 evidence consolidation and resource closure

Tracked implementation changes: none

## Executive summary

This study tested the same frozen 120 Chronicle tasks with Qwen3.5-4B
Q4_K_M on one RunPod RTX 5090 allocation at two context endpoints. The 8K
endpoint was run twice for repeatability; the 262K endpoint was run once as the
maximum-context endpoint. The accepted Vertex Gemini 3.5 Flash 120-case arm
was reused as a matched hosted control. No candidate or judge request was made
during this report-only continuation.

The central finding is that context capacity, not GPU speed alone, determined
reliability. Both 8K runs produced 89/120 schema-valid results. Raising context
to 262,144 recovered 30 positions without losing an 8K success, producing
119/120 valid results. The cost was 40 additional seconds versus the repeat 8K
run and an increase in peak sampled GPU memory from 4,219 MiB to 11,896 MiB.

The two 8K runs were highly repeatable: all 120 terminal statuses matched,
85/89 shared valid outputs were byte-for-structure identical, and their full
judge aggregates differed by only 0.0022 on a four-point scale. The four
changed valid outputs comprised one result from each task. This is strong
repeatability evidence for reliability and structured output, but it also
shows that temperature zero does not guarantee exact output or judge-score
identity.

Maximum-context Qwen and Gemini were matched on the same ordered cases,
prompts, task contracts, response schemas, references, judge profile, and
rubric. Qwen was more schema-reliable (119/120 versus 112/120) and much faster
for this serial generation run (169 seconds versus 639.524 seconds outer wall
time). Gemini was semantically stronger on the 110 cases with completed
verdicts for both arms: the case-normalized mean was 3.892/4 for Gemini and
3.830/4 for Qwen. Gemini also led deterministic reference agreement for all
three classification tasks.

The final RunPod charge exposed by the billing API was US$6.304635. Successful
Qwen-arm judge verdicts used 1,526,131 input and 85,888 output tokens, an
estimated US$4.083 at the applicable Gemini 3.1 Pro Preview Standard rates.
The conservative WP-5.2C1 total remains below US$10.81 and within the US$22
ceiling.

The complete RunPod evidence tree was archived locally, restored into a
separate directory, and verified file-for-file by SHA-256 before cleanup. The
stopped Pod and its attached 50 GB volume were then deleted. The exact Pod now
returns `not_found`, Pod and network-volume inventories are empty, and account
spend is US$0/hour.

## 1. Protocol and provenance

### 1.1 Frozen evaluation contract

The four candidate packages contain the same ordered 120 case entries: 30
conversations crossed with four tasks in the frozen order conversation
summary, work-mode classification, last activity, and title assessment. Every
ordered alias, task, and case fingerprint matches across the two R8 packages,
R262K, and Gemini.

In the accepted evaluator, a case fingerprint covers the canonical input,
dates, complete task definition, selector, rendered messages, provider schema,
application schema, finalizer, generation settings, and request-construction
version. Equality of all 120 ordered fingerprints therefore proves equality of
the candidate-visible prompts and evaluation contracts even though provider
profiles and package content identities appropriately differ.

All four scoring manifests also bind the same frozen 30-conversation prefix,
120-case scope, `gemini-pro-judge` profile, and rubric version 1. References
were used only in local deterministic scoring and disclosed judge requests;
they were not included in candidate generation packages.

### 1.2 Arm identities

| Arm | Provider/model | Context | Generation application | Profile | Verification status |
|---|---|---:|---|---|---|
| R8 original | LM Studio / Qwen3.5-4B | 8,192 | `7e4dbc4a…` | service-qwen | immutable; waiver-judged, not strict manager-valid |
| R8 repeat | LM Studio / Qwen3.5-4B | 8,192 | `7e4dbc4a…` | service-qwen | immutable; waiver-judged, not strict manager-valid |
| R262K | LM Studio / Qwen3.5-4B | 262,144 | `7e4dbc4a…` | service-qwen-max | strict verification passed |
| Gemini control | Vertex AI / Gemini 3.5 Flash | hosted | `d1b6ca80…` | gemini-candidate | previously accepted strict package/scoring run |

All candidate requests used temperature 0 and a maximum 500 output tokens.
Generation was serial with concurrency 1. The Qwen artifact was the
2,707,513,696-byte Q4_K_M GGUF from public repository
`lmstudio-community/Qwen3.5-4B-GGUF`, filename
`Qwen3.5-4B-Q4_K_M.gguf`. An exact repository revision was not captured and
must not be inferred. The downloaded binary is nevertheless bound by its
exact filename, byte size, quantization, and a privately retained SHA-256 that
was verified against the returned transfer manifests. The artifact, profile,
runtime, and package identities were all verified locally.

The fixed semantic judge was Vertex AI Gemini 3.1 Pro Preview in `global`,
reasoning effort `none`, temperature 0, and maximum 1,000 output tokens.
Requests were blinded and contained only the selected source excerpt,
candidate output, reference, and rubric. Exact private prompts, references,
rationales, case identifiers, hashes, account identifiers, and cloud resource
identifiers are deliberately omitted here.

### 1.3 R8 evidence waiver

Both immutable R8 packages contain the same pre-response `invalid_json`
failure. Exact application commit `7e4dbc4a…` did not retain a raw provider
payload for that boundary, while the strict verifier requires raw-invalid
evidence. Archive and package hashes matched, so this was not transfer
corruption.

The approved detached evaluator waived only that single missing-raw-evidence
gate for the two known immutable package identities and the known failure
shape. It did not change either package or waive any other check. The correct
publication label is therefore **waiver-judged, not strict manager-valid**.
R262K and the accepted Gemini control do not use this waiver.

## 2. Hardware and service evidence

All three Qwen arms ran in one resumed-Pod session, so one hardware/runtime
identity applies to every arm.

| Item | Captured value | Evidence class |
|---|---|---|
| Service | RunPod Secure Cloud, EU-CZ-1 | control plane |
| GPU allocation | 1 × NVIDIA GeForce RTX 5090 | control plane plus `nvidia-smi` |
| Visible GPU memory | 32,607 MiB | `nvidia-smi` |
| GPU architecture | NVIDIA Blackwell | vendor specification |
| CUDA cores | 21,760 | vendor specification; not measured |
| CPU allocation | 32 vCPUs | control plane |
| RAM allocation | 62 GB | control plane |
| Container disk | 50 GB | control plane |
| Persistent volume | 50 GB at `/workspace` | control plane |
| Image | RunPod PyTorch 2.8.0, Python 3.11, CUDA 12.8.1, cuDNN development, Ubuntu 22.04 | pinned control-plane identity |
| Guest/kernel | Ubuntu 22.04, x86-64, Linux 6.8.0-124 | returned runtime evidence |
| NVIDIA driver | 595.71.05 | returned runtime evidence |
| Inference runtime | LM Studio CLI commit `71bd99c`; `llmster 0.0.20-1` | returned runtime evidence |
| Service exposure | loopback only; no public inference listener | listener and API-base checks |

NVIDIA describes the RTX 5090 as a Blackwell GPU with 32 GB GDDR7 and 21,760
CUDA cores ([NVIDIA RTX 5090 specification](https://marketplace.nvidia.com/en-gb/consumer/graphics-cards/nvidia-geforce-rtx-5090/)).
These vendor specifications provide context; the captured allocation and
telemetry, not a consumer-card specification, are authoritative for this run.

The container exposed host totals of 256 processors and about 504 GiB through
`/proc`. Those conflict with the purchased allocation and must not be reported
as Pod specifications. Physical CPU model, cgroup quota files, reliable
process CPU/RAM usage, and time-to-first-token were not captured. They remain
unavailable rather than inferred.

The R262K model-load estimate was 2.52 GiB with low confidence, while the
recorded load completed in 2.34 seconds and the private-free synthetic request
passed in 11.697 seconds. The R8 synthetic gate passed all four tasks; its
first/cold summary request took 18.797 seconds and the three subsequent task
requests took 0.486–0.555 seconds. Synthetic timings are service gates, not
substitutes for benchmark latency.

## 3. Generation results

### 3.1 Complete arm totals

Outer wall time measures the full serial command. Summed latency is the sum of
the 120 recorded terminal attempt latencies and can differ from outer time due
to orchestration overhead and provider waiting behavior.

| Measure | R8 original | R8 repeat | R262K | Gemini control |
|---|---:|---:|---:|---:|
| Expected/terminal positions | 120 | 120 | 120 | 120 |
| Schema-valid | 89 | 89 | 119 | 112 |
| Reliability | 74.17% | 74.17% | 99.17% | 93.33% |
| Failed | 31 | 31 | 1 | 8 |
| Outer wall time | 131 s | 129 s | 169 s | 639.524 s |
| Summed latency | 114.125 s | 112.799 s | 154.701 s | 453.787 s |
| Overall p50 | 916 ms | 905 ms | 1,196 ms | 2,156 ms |
| Overall p95 | 1,375 ms | 1,356 ms | 2,081 ms | 12,562 ms |
| Usage records available | 90 | 90 | 120 | 119 |
| Usage records missing | 30 | 30 | 0 | 1 |
| Prompt tokens | 267,532 | 267,532 | 605,543 | 672,078 |
| Completion tokens | 11,327 | 11,394 | 15,629 | 19,205 |
| Total tokens | 278,859 | 278,926 | 621,172 | 691,283 |

Token totals are provider-reported. Qwen and Gemini use different tokenizers
and failure-path accounting, so cross-provider token counts are descriptive,
not a tokenizer-normalized efficiency comparison. Gemini additionally reported
12,029 cache-read input tokens for summary; they are already represented in
provider accounting and are not added again.

### 3.2 Task timing, reliability, and token evidence

The p50/p95 values below are evaluator-authoritative interpolated percentiles.
`Usage` is the number of 30 terminal positions with a provider usage record;
`Missing` makes the complementary count explicit.

| Arm/task | Valid | Failed | p50/p95 ms | Usage | Missing | Prompt | Completion | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R8 original / summary | 19 | 11 | 933 / 1,545 | 20 | 10 | 60,324 | 3,039 | 63,363 |
| R8 original / work mode | 20 | 10 | 858 / 1,330 | 20 | 10 | 60,844 | 2,511 | 63,355 |
| R8 original / last activity | 30 | 0 | 982 / 1,254 | 30 | 0 | 85,357 | 3,807 | 89,164 |
| R8 original / title | 20 | 10 | 768 / 1,147 | 20 | 10 | 61,007 | 1,970 | 62,977 |
| R8 repeat / summary | 19 | 11 | 918 / 1,523 | 20 | 10 | 60,324 | 3,097 | 63,421 |
| R8 repeat / work mode | 20 | 10 | 891 / 1,350 | 20 | 10 | 60,844 | 2,513 | 63,357 |
| R8 repeat / last activity | 30 | 0 | 1,000 / 1,270 | 30 | 0 | 85,357 | 3,813 | 89,170 |
| R8 repeat / title | 20 | 10 | 768 / 1,114 | 20 | 10 | 61,007 | 1,971 | 62,978 |
| R262K / summary | 29 | 1 | 1,366 / 2,176 | 30 | 0 | 172,779 | 4,821 | 177,600 |
| R262K / work mode | 30 | 0 | 1,181 / 2,081 | 30 | 0 | 173,559 | 3,806 | 177,365 |
| R262K / last activity | 30 | 0 | 1,062 / 1,445 | 30 | 0 | 85,357 | 3,813 | 89,170 |
| R262K / title | 30 | 0 | 1,044 / 1,777 | 30 | 0 | 173,848 | 3,189 | 177,037 |
| Gemini / summary | 23 | 7 | 2,719 / 9,218 | 30 | 0 | 189,338 | 6,571 | 195,909 |
| Gemini / work mode | 30 | 0 | 2,030 / 7,906 | 30 | 0 | 192,098 | 3,802 | 195,900 |
| Gemini / last activity | 29 | 1 | 2,109 / 11,077 | 29 | 1 | 97,200 | 4,991 | 102,191 |
| Gemini / title | 30 | 0 | 1,734 / 12,562 | 30 | 0 | 193,442 | 3,841 | 197,283 |

### 3.3 Failure boundaries

| Arm/task | Context length | Invalid JSON | Schema validation | Provider response | Total |
|---|---:|---:|---:|---:|---:|
| R8 original / summary | 9 | 1 | 1 | 0 | 11 |
| R8 original / work mode | 10 | 0 | 0 | 0 | 10 |
| R8 original / last activity | 0 | 0 | 0 | 0 | 0 |
| R8 original / title | 10 | 0 | 0 | 0 | 10 |
| R8 repeat / summary | 9 | 1 | 1 | 0 | 11 |
| R8 repeat / work mode | 10 | 0 | 0 | 0 | 10 |
| R8 repeat / last activity | 0 | 0 | 0 | 0 | 0 |
| R8 repeat / title | 10 | 0 | 0 | 0 | 10 |
| R262K / summary | 0 | 0 | 1 | 0 | 1 |
| Gemini / summary | 0 | 6 | 1 | 0 | 7 |
| Gemini / last activity | 0 | 0 | 0 | 1 | 1 |

The absent rows are zero. The identical R8 taxonomy—29 context failures, one
schema failure, and one pre-response invalid-JSON failure—reproduced exactly.
R262K removed every context-length failure and retained one properly evidenced
schema failure.

## 4. GPU telemetry

Telemetry covers each complete Qwen generation command. The original R8 arm
was sampled every five seconds; repeat R8 and R262K were sampled every two
seconds. Means therefore describe each arm's own sampled run and should not be
treated as a perfectly cadence-matched energy study.

| Measure | R8 original | R8 repeat | R262K |
|---|---:|---:|---:|
| Samples | 26 | 64 | 83 |
| GPU memory MiB, min / mean / max | 3,708 / 3,710 / 3,712 | 3,712 / 3,720 / 4,219 | 11,872 / 11,894 / 11,896 |
| GPU utilization %, min / mean / max | 0 / 35.0 / 99 | 0 / 41.7 / 99 | 0 / 46.1 / 99 |
| Temperature °C, min / mean / max | 33 / 44.5 / 53 | 33 / 44.9 / 56 | 36 / 47.9 / 58 |
| Power W, min / mean / max | 2.10 / 253.63 / 380.33 | 1.86 / 252.12 / 404.36 | 55.06 / 318.38 / 505.60 |

These are cloud-VM samples, not consumer-desktop thermals, acoustics, energy,
or wall-socket measurements. No reliable process CPU/RAM sample exists. TTFT
is also unavailable.

## 5. Deterministic evaluation

All valid outputs in every arm passed evidence-membership and cross-field
validation: 89/89 for each R8 run, 119/119 for R262K, and 112/112 for Gemini.
Summary date and length checks passed for every valid summary; title suggestion
checks passed for every valid title.

### 5.1 Exact reference agreement

Summary is assessed semantically and has no label-agreement row. Failed
positions count as no valid output in the 30-position task denominator.

| Arm | Title fit | Work mode | Last activity |
|---|---:|---:|---:|
| R8 original | 53.33% | 36.67% | 50.00% |
| R8 repeat | 53.33% | 36.67% | 53.33% |
| R262K | 76.67% | 56.67% | 53.33% |
| Gemini | 83.33% | 63.33% | 70.00% |

### 5.2 Per-label precision and recall

Each cell is `precision / recall (reference support)`. A dash means the metric
is undefined because no reference or predicted example exists.

| Task/label | R8 original | R8 repeat | R262K | Gemini |
|---|---:|---:|---:|---:|
| Title false | 60.0% / 27.3% (11) | 60.0% / 27.3% (11) | 66.7% / 72.7% (11) | 68.8% / 100% (11) |
| Title true | 86.7% / 68.4% (19) | 86.7% / 68.4% (19) | 83.3% / 78.9% (19) | 100% / 73.7% (19) |
| Work executor | 83.3% / 35.7% (14) | 83.3% / 35.7% (14) | 90.0% / 64.3% (14) | 66.7% / 57.1% (14) |
| Work manager | 11.1% / 33.3% (3) | 11.1% / 33.3% (3) | 20.0% / 100% (3) | 100% / 66.7% (3) |
| Work mixed | — / 0% (1) | — / 0% (1) | — / 0% (1) | 0% / 0% (1) |
| Work one-off | 100% / 41.7% (12) | 100% / 41.7% (12) | 100% / 41.7% (12) | 64.3% / 75.0% (12) |
| Last awaiting input | 100% / 28.6% (7) | 100% / 28.6% (7) | 100% / 28.6% (7) | 100% / 42.9% (7) |
| Last completed | 65.0% / 81.3% (16) | 66.7% / 87.5% (16) | 66.7% / 87.5% (16) | 71.4% / 93.8% (16) |
| Last in progress | 0% / 0% (7) | 0% / 0% (7) | 0% / 0% (7) | 60.0% / 42.9% (7) |
| Last blocked | 0% / — (0) | 0% / — (0) | 0% / — (0) | — / — (0) |

No arm predicted or referenced `unknown`; its precision and recall are
undefined. Per-case deterministic records remain in ignored local evaluator
storage.

### 5.3 Full confusion matrices

Rows are frozen reference labels and columns are candidate predictions. `NVO`
means `no_valid_output`. It is a candidate-side prediction column, not a
reference row, because every position has a valid frozen reference. Reference
rows for labels with zero support are retained explicitly. Within each arm,
the row totals for each task sum to the exact 30-position denominator.

#### Title fit

| Arm | Reference | Pred false | Pred true | NVO | Row total |
|---|---|---:|---:|---:|---:|
| R8 original | false | 3 | 2 | 6 | 11 |
| R8 original | true | 2 | 13 | 4 | 19 |
| R8 repeat | false | 3 | 2 | 6 | 11 |
| R8 repeat | true | 2 | 13 | 4 | 19 |
| R262K | false | 8 | 3 | 0 | 11 |
| R262K | true | 4 | 15 | 0 | 19 |
| Gemini | false | 11 | 0 | 0 | 11 |
| Gemini | true | 5 | 14 | 0 | 19 |

#### Work mode

| Arm | Reference | Pred executor | Pred manager | Pred mixed | Pred one-off | Pred unknown | NVO | Row total |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| R8 original | executor | 5 | 2 | 0 | 0 | 0 | 7 | 14 |
| R8 original | manager | 0 | 1 | 0 | 0 | 0 | 2 | 3 |
| R8 original | mixed | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| R8 original | one-off | 1 | 6 | 0 | 5 | 0 | 0 | 12 |
| R8 original | unknown | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| R8 repeat | executor | 5 | 2 | 0 | 0 | 0 | 7 | 14 |
| R8 repeat | manager | 0 | 1 | 0 | 0 | 0 | 2 | 3 |
| R8 repeat | mixed | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| R8 repeat | one-off | 1 | 6 | 0 | 5 | 0 | 0 | 12 |
| R8 repeat | unknown | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| R262K | executor | 9 | 5 | 0 | 0 | 0 | 0 | 14 |
| R262K | manager | 0 | 3 | 0 | 0 | 0 | 0 | 3 |
| R262K | mixed | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| R262K | one-off | 1 | 6 | 0 | 5 | 0 | 0 | 12 |
| R262K | unknown | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Gemini | executor | 8 | 0 | 1 | 5 | 0 | 0 | 14 |
| Gemini | manager | 1 | 2 | 0 | 0 | 0 | 0 | 3 |
| Gemini | mixed | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| Gemini | one-off | 2 | 0 | 1 | 9 | 0 | 0 | 12 |
| Gemini | unknown | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

#### Last activity

| Arm | Reference | Pred awaiting input | Pred blocked | Pred completed | Pred in progress | Pred unknown | NVO | Row total |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| R8 original | awaiting input | 2 | 0 | 1 | 4 | 0 | 0 | 7 |
| R8 original | blocked | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| R8 original | completed | 0 | 0 | 13 | 3 | 0 | 0 | 16 |
| R8 original | in progress | 0 | 1 | 6 | 0 | 0 | 0 | 7 |
| R8 original | unknown | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| R8 repeat | awaiting input | 2 | 0 | 1 | 4 | 0 | 0 | 7 |
| R8 repeat | blocked | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| R8 repeat | completed | 0 | 0 | 14 | 2 | 0 | 0 | 16 |
| R8 repeat | in progress | 0 | 1 | 6 | 0 | 0 | 0 | 7 |
| R8 repeat | unknown | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| R262K | awaiting input | 2 | 0 | 1 | 4 | 0 | 0 | 7 |
| R262K | blocked | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| R262K | completed | 0 | 0 | 14 | 2 | 0 | 0 | 16 |
| R262K | in progress | 0 | 1 | 6 | 0 | 0 | 0 | 7 |
| R262K | unknown | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Gemini | awaiting input | 3 | 0 | 3 | 1 | 0 | 0 | 7 |
| Gemini | blocked | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Gemini | completed | 0 | 0 | 15 | 1 | 0 | 0 | 16 |
| Gemini | in progress | 0 | 0 | 3 | 3 | 0 | 1 | 7 |
| Gemini | unknown | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## 6. Fixed-judge semantic evaluation

### 6.1 Accounting and aggregate scores

The overall mean weights every rubric dimension observation. The task means
first average dimensions within each case and then average cases.

| Measure | R8 original | R8 repeat | R262K | Gemini |
|---|---:|---:|---:|---:|
| Candidate positions | 120 | 120 | 120 | 120 |
| Eligible valid outputs | 89 | 89 | 119 | 112 |
| Completed verdicts | 89 | 89 | 118 | 110 |
| Terminal judge failures | 0 | 0 | 1 | 2 |
| Invalid candidates skipped | 31 | 31 | 1 | 8 |
| Failure category | — | — | 1 provider invalid JSON | 2 provider invalid JSON |
| Overall mean / 4 | 3.8132 | 3.8154 | 3.8458 | 3.9051 |
| Percent of maximum | 95.33% | 95.38% | 96.14% | 97.63% |

| Task | R8 original | R8 repeat | R262K | Gemini |
|---|---:|---:|---:|---:|
| Conversation summary | 3.958 (19) | 3.958 (19) | 3.957 (28) | 3.982 (22) |
| Last activity | 3.772 (30) | 3.789 (30) | 3.817 (30) | 3.940 (28) |
| Title assessment | 3.910 (20) | 3.890 (20) | 3.900 (30) | 3.973 (30) |
| Work-mode classification | 3.613 (20) | 3.613 (20) | 3.692 (30) | 3.700 (30) |

### 6.2 Rubric-dimension means

| Task/dimension | R8 original | R8 repeat | R262K | Gemini |
|---|---:|---:|---:|---:|
| Summary — concise usefulness | 3.947 | 3.947 | 3.964 | 3.955 |
| Summary — conversation characterization | 4.000 | 4.000 | 4.000 | 4.000 |
| Summary — factual consistency | 4.000 | 4.000 | 4.000 | 4.000 |
| Summary — material coverage | 3.842 | 3.842 | 3.821 | 3.955 |
| Summary — unsupported-claim avoidance | 4.000 | 4.000 | 4.000 | 4.000 |
| Last — blocker correctness | 4.000 | 4.000 | 4.000 | 4.000 |
| Last — final meaningful activity | 4.000 | 4.000 | 4.000 | 3.929 |
| Last — next-action support | 3.200 | 3.200 | 3.333 | 3.857 |
| Last — not source copying | 4.000 | 4.000 | 4.000 | 4.000 |
| Last — status correctness | 3.467 | 3.600 | 3.600 | 3.857 |
| Last — unsupported-claim avoidance | 3.967 | 3.933 | 3.967 | 4.000 |
| Title — dominant-activity fit | 3.750 | 3.650 | 3.767 | 3.867 |
| Title — suggestion-only compliance | 4.000 | 4.000 | 4.000 | 4.000 |
| Title — suggestion usefulness | 4.000 | 4.000 | 4.000 | 4.000 |
| Title — title-fits correctness | 3.800 | 3.800 | 3.733 | 4.000 |
| Title — unsupported-claim avoidance | 4.000 | 4.000 | 4.000 | 4.000 |
| Work — label support | 3.500 | 3.500 | 3.600 | 3.600 |
| Work — mode distinction | 3.500 | 3.500 | 3.600 | 3.600 |
| Work — reason specificity | 3.650 | 3.650 | 3.700 | 3.733 |
| Work — unsupported-claim avoidance | 3.800 | 3.800 | 3.867 | 3.867 |

### 6.3 Judge tokens and cache closure

| Arm | Verdicts with usage | Input tokens | Output tokens | Recorded reasoning tokens | Total tokens |
|---|---:|---:|---:|---:|---:|
| R8 original | 89 | 371,945 | 25,171 | 503 | 397,116 |
| R8 repeat | 89 | 372,011 | 25,915 | 1,181 | 397,926 |
| R262K | 118 | 782,175 | 34,802 | 1,743 | 816,977 |
| Gemini control | 110 | 734,312 | 33,841 | 2,623 | 768,153 |

Reasoning tokens are a provider detail within output/total accounting and are
shown separately rather than added again.

Existing cache-only replays passed for both R8 arms, R262K, and the accepted
Gemini control. The R8 attempt trees retained 89 verdicts each; R262K retained
all 119 terminal attempts; Gemini retained its accepted attempt tree. Every
replay was fail-closed and made zero provider calls. WP-5.2C1.1 made no model
or judge calls at all.

## 7. R8 repeatability analysis

| Repeatability measure | Result |
|---|---:|
| Same terminal status | 120/120 (100%) |
| Success → success | 89 |
| Failure → failure | 31 |
| Reliability transitions | 0 |
| Exact structured result among shared successes | 85/89 (95.51%) |
| Changed structured result | 4/89 (4.49%); one per task |
| Identical judge score vectors | 83/89 (93.26%) |
| Identical candidates with identical score vectors | 81/85 (95.29%) |
| Identical candidates with changed score vectors | 4/85 (4.71%) |
| Overall judge-mean difference | 0.0022/4; 0.055 percentage points |

The repeat exactly reproduced the R8 failure surface and prompt-token totals.
Completion tokens differed by only 67 across the run. Outer time differed by
two seconds (1.53%), and p50/p95 differed by 11/19 ms. Peak memory differed by
507 MiB, but most repeat samples remained near 3.7 GiB; the brief maximum and
different sampling cadence make peak equality a weaker repeatability measure
than terminal status or output identity.

Candidate variance and judge variance are separate. Four candidates changed
at temperature zero. Separately, four of the 85 identical candidates received
a different score vector from fresh judging at temperature zero. Therefore the
strong claim is high repeatability, not determinism.

## 8. R8 versus R262K context endpoint

The repeat R8 arm is the primary timing comparator because it immediately
preceded R262K in the same additional-arms session. Original R8 leads to the
same substantive conclusion.

| Measure | R8 repeat | R262K | Change |
|---|---:|---:|---:|
| Schema-valid | 89/120 | 119/120 | +30; +25.0 percentage points |
| Context failures | 29 | 0 | −29 |
| Outer wall time | 129 s | 169 s | +40 s; +31.0% |
| Overall p50 | 905 ms | 1,196 ms | +291 ms; +32.2% |
| Overall p95 | 1,356 ms | 2,081 ms | +725 ms; +53.5% |
| Peak sampled GPU memory | 4,219 MiB | 11,896 MiB | +7,677 MiB; 2.82× |
| Successful judge verdicts | 89 | 118 | +29 |
| Full judge mean | 3.815/4 | 3.846/4 | +0.030/4 |

R262K recovered 30 positions and regressed none. On the 89 positions valid in
both repeat R8 and R262K, all 89 structured results were identical. This is
especially strong evidence that the endpoint changed capacity rather than the
already-fitting outputs. One recovered summary then failed semantic judging
because of judge invalid JSON, accounting for 118 rather than 119 completed
R262K verdicts.

The accepted local Qwen 8K baseline took 4 hours 43 minutes 30.782 seconds.
Remote R8 was about 129.9× faster for the original and 131.9× faster for the
repeat. The 100.7× ratio for R262K is contextual, not like-for-like, because
the context endpoint changed.

The evidence supports 8K and 262K as the useful endpoints. It does not justify
an unrun 16K or 32K breakpoint. Those intermediate contexts might achieve the
same reliability with less memory, but this study did not measure them.

## 9. Matched R262K versus Gemini analysis

### 9.1 Match proof

The comparison is matched on all 120 ordered case fingerprints. This proves
same inputs, dates, task definitions, selectors, rendered system/user prompts,
provider and application schemas, finalizers, generation settings, and request
construction. Scoring uses the same frozen prefix identity, FABLE references,
judge profile, rubric version, and eligibility rules. Different model/provider
profiles and application commits are recorded rather than hidden.

### 9.2 Reliability, speed, and tokens

| Measure | Qwen R262K | Gemini 3.5 Flash | Interpretation |
|---|---:|---:|---|
| Schema-valid | 119/120 | 112/120 | Qwen +7 valid positions |
| Outer wall time | 169 s | 639.524 s | Qwen run 3.78× faster |
| Overall p50 | 1,196 ms | 2,156 ms | Qwen 44.5% lower |
| Overall p95 | 2,081 ms | 12,562 ms | Qwen 83.4% lower |
| Provider-reported total tokens | 621,172 | 691,283 | descriptive; tokenizers differ |
| Peak GPU memory | 11,896 MiB | not applicable/available | dedicated Qwen service only |

The speed comparison reflects these executed serial workflows, not a universal
provider benchmark. Qwen used a dedicated warm local HTTP service on a rented
GPU; Gemini used a hosted global endpoint on a different date and application
commit, with provider-side scheduling and retry behavior. No concurrency or
throughput scaling was tested.

### 9.3 Deterministic and semantic quality

| Measure | Qwen R262K | Gemini | Gemini lead |
|---|---:|---:|---:|
| Title-fit exact agreement | 76.67% | 83.33% | 6.67 pp |
| Work-mode exact agreement | 56.67% | 63.33% | 6.67 pp |
| Last-activity exact agreement | 53.33% | 70.00% | 16.67 pp |
| Full completed-verdict mean | 3.846/4 (118) | 3.905/4 (110) | 0.059/4 |

For a strict matched semantic comparison, 110 cases have successful judge
verdicts in both arms. Each case is weighted equally despite different task
rubric widths:

| Matched task | n | Qwen R262K | Gemini |
|---|---:|---:|---:|
| Conversation summary | 22 | 3.955 | 3.982 |
| Last activity | 28 | 3.804 | 3.940 |
| Title assessment | 30 | 3.900 | 3.973 |
| Work-mode classification | 30 | 3.692 | 3.700 |
| **All matched cases** | **110** | **3.830** | **3.892** |

Gemini leads by 0.0626/4 on this case-normalized matched set. Weighting every
rubric dimension instead gives 3.836 for Qwen and 3.905 for Gemini. Ninety-one
of the 110 matched positions received identical score vectors. The largest
task gap is last activity, consistent with the deterministic 16.67-point
agreement gap. The fixed judge is an evaluator, not ground truth, and Gemini
is a control, not a reference oracle.

## 10. Cost and practicality

### 10.1 RunPod

The captured rate was US$0.99/hour for compute, US$1.004/hour while running
with storage, and US$0.014/hour while stopped with the 50 GB volume retained.
Final billing rows total US$6.304635: US$1.569878 on 2026-08-03 and
US$4.734757 on 2026-08-04. This supersedes the earlier US$6.281557 checkpoint;
the approximately US$0.023 difference is retained-resource billing before
deletion.

RunPod documents per-second Pod/storage billing and a stopped volume-disk rate
of US$0.20/GB/month ([RunPod Pod pricing](https://docs.runpod.io/pods/pricing)).
It also documents that `/workspace` volume-disk data is deleted with the Pod,
whereas a network volume survives independently
([RunPod storage types](https://docs.runpod.io/pods/storage/types)).

The US$6.30 charge covers provisioning, installation, model transfer/load,
synthetic gates, the three benchmark arms, idle/recovery time, and retained
storage. It cannot be honestly assigned to R262K generation alone.

### 10.2 Vertex judge and hosted control estimates

The three Qwen-arm successful judge sets used 1,526,131 input tokens and 85,888
output tokens. At Standard Gemini 3.1 Pro Preview rates below 200K input tokens
of US$2/million input and US$12/million output, the estimate is US$4.083.
Allowing the configured maximum output and a full 200K input for the one failed
request keeps judge usage below US$4.50. Google states these rates and that
response and reasoning tokens are billed as output
([Vertex AI generative AI pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing)).
The billing account remains authoritative.

The reused Gemini 3.5 Flash control's 672,078 input and 19,205 output generation
tokens estimate to US$1.181 at the current global Standard rate of
US$1.50/million input and US$9/million output. Its 110 completed historical
judge verdicts estimate to US$1.875 at the Pro rates above. These are
rate-card estimates for already accepted WP-5.2B1.4 work, not new WP-5.2C1.1
spend and not invoice replacements.

The WP-5.2C1 incremental total is approximately US$10.388 using successful
judge usage, and remains below US$10.805 under the conservative judge bound.
It stayed more than US$11.19 below the US$22 ceiling. This small study supports
short rented-GPU experiments as practical; it does not establish long-run
unit economics, concurrency scaling, or a consumer GPU break-even point.

## 11. Archive, backup, and resource closure

### 11.1 Local evidence verification

Before deletion, the ignored local RunPod evidence root contained 743 files
and 25,534,080 bytes. It includes both returned transfer archives, extracted
copies, candidate packages, transfer/package hashes, telemetry, deterministic
scores, judge attempts, cache evidence, service logs, and operator provenance.
The accepted Gemini package and score/cache tree are also retained locally.

A second ignored local backup archive was created in the evaluator backup area
on the operator workstation. It is 17,385,404 bytes. The archive was extracted
into a separate verification directory: all 743 files and all 25,534,080 bytes
were present, and every restored file matched its source SHA-256. Exact local
paths and hashes are retained in the private closure record. This is a second
local copy on the same workstation, not off-device disaster recovery.

No accepted input, candidate package, score, judge attempt, or transfer archive
was changed during consolidation. The private consolidation JSON and cleanup
record are derived indexes added after the authoritative backup snapshot.

### 11.2 Dated cleanup addendum — 2026-08-04

At the pre-delete gate, the exact target was stopped (`EXITED`), allocated 32
vCPUs and 62 GB RAM, and retained its attached 50 GB `/workspace` volume. There
were no separately created network volumes. Account spend was US$0.014/hour.

After the full restore-and-hash backup passed, the exact Pod was deleted. At
2026-08-04T14:30:03.449Z:

- exact Pod lookup returned `not_found`;
- Pod inventory was empty;
- network-volume inventory was empty;
- the attached volume was therefore deleted with the Pod;
- account spend was US$0/hour; and
- final Pod billing history totalled US$6.304635.

No evidence existed only on RunPod at deletion time. The deleted Pod and its
attached volume are not recoverable from RunPod; the verified local archive
and backup are the recovery sources.

## 12. Article-ready evidence brief

### Compact arm-by-arm publication table

| Arm | Context / execution environment | Schema-valid | Outer wall | Overall p50/p95 | Judge eligible / completed / failed | Semantic score and exact denominator | Verification | Candidate execution cost boundary | Judge cost boundary |
|---|---|---:|---:|---:|---:|---|---|---|---|
| R8 original | 8,192; RunPod RTX 5090; LM Studio | 89/120 (74.17%) | 131 s | 916 / 1,375 ms | 89 / 89 / 0 | 3.8132/4; 455 dimension scores across 89 verdicts | Waiver-judged; not strict manager-valid | Included in shared US$6.304635 three-arm RunPod bill; no per-arm allocation | US$1.046 rate-card estimate for successful verdicts |
| R8 repeat | 8,192; same RunPod/LM Studio session | 89/120 (74.17%) | 129 s | 905 / 1,356 ms | 89 / 89 / 0 | 3.8154/4; 455 dimension scores across 89 verdicts | Waiver-judged; not strict manager-valid | Included in shared US$6.304635 three-arm RunPod bill; no per-arm allocation | US$1.055 rate-card estimate for successful verdicts |
| R262K | 262,144; same RunPod/LM Studio session | 119/120 (99.17%) | 169 s | 1,196 / 2,081 ms | 119 / 118 / 1 | 3.8458/4; 590 dimension scores across 118 verdicts | Strict verification passed | Included in shared US$6.304635 three-arm RunPod bill; no per-arm allocation | US$1.982 rate-card estimate for successful verdicts; failed request excluded |
| Gemini control | Hosted Vertex AI Gemini 3.5 Flash, `global` | 112/120 (93.33%) | 639.524 s | 2,156 / 12,562 ms | 112 / 110 / 2 | 3.9051/4; 548 dimension scores across 110 verdicts | Previously accepted strict package/scoring run | Historical candidate generation estimate US$1.181 | Historical successful-verdict estimate US$1.875 |

The RunPod amount is the final shared invoice for provisioning, setup, all
three Qwen arms, idle/recovery time, and storage; it is not an arm price. The
Qwen-arm judge estimates sum to US$4.083. The Gemini candidate and judge
figures are separate historical rate-card estimates for the reused control,
not WP-5.2C1.1 spend or invoice values.

| Article claim | Evidence | Caveat | Confidence |
|---|---|---|---|
| A rented RTX 5090 changed the accepted Qwen 8K run from hours to minutes. | Local 8K baseline 4:43:30.782; remote R8 129–131 s; about 130–132× faster. | Same benchmark and context, but different runtime/hardware environment. | High |
| Context was the reliability bottleneck at 8K. | Both R8 runs: 29 context failures and 89/120 valid; R262K: zero context failures and 119/120 valid. | Only 8K and 262K endpoints were measured. | High |
| Maximum context recovered 30 cases at modest latency cost. | +30 valid; no R8 success regressed; +40 s versus repeat R8. | “Modest” is workload-relative; memory rose materially. | High |
| Maximum context required about 11.6 GiB peak sampled VRAM. | 11,896 MiB peak versus 4,219 MiB repeat-R8 peak. | Cloud VM sampling, not consumer-card wall power or all intermediate contexts. | High |
| R8 reliability was exactly repeatable. | 120/120 same terminal status; identical 31-case failure taxonomy. | Exact outputs were not fully deterministic. | High |
| Successful R8 structured outputs were highly stable. | 85/89 identical (95.51%); four changes, one per task. | One repeat pair only. | High |
| Judge scores also showed small nondeterminism. | 83/89 identical score vectors; 4/85 identical candidates changed score vector. | One fixed judge/model/configuration; fresh calls at temperature zero. | High |
| R262K Qwen was more schema-reliable and faster than the hosted Gemini control. | 119 vs 112 valid; 169 vs 639.524 s. | Dedicated warm GPU versus hosted API; not a universal provider benchmark. | High for these runs |
| Gemini remained semantically stronger. | Matched 110-case means: Gemini 3.892/4, Qwen 3.830/4; Gemini led all classification agreement measures. | Fixed judge is not ground truth; FABLE references have known limitations. | High for measured evaluation |
| The complete C1 experiment stayed under budget. | Final RunPod US$6.305; successful-judge estimate US$4.083; conservative combined <US$10.805 versus US$22. | Vertex value is estimated; billing account is authoritative. | High for RunPod, medium-high for Vertex estimate |

### Recommended charts

1. Reliability bars: R8 original 74.17%, R8 repeat 74.17%, R262K 99.17%, Gemini 93.33%.
2. Context cost scatter: wall time on the x-axis and peak VRAM on the y-axis for the three Qwen arms, annotated with valid count.
3. Failure waterfall: 29 context + 1 schema + 1 invalid JSON at R8, collapsing to one schema failure at R262K.
4. Matched semantic bars: four task means for R262K and Gemini on the 110 common completed cases.
5. Repeatability strip: 120 status matches, then 89 shared successes split into 85 identical and four changed results.

### Observations and caveats

- Reliability and semantic quality are separate. R262K solved the capacity
  problem, but Gemini still led the matched semantic and classification
  measures.
- Qwen's main remaining deterministic weakness is classification distinction,
  particularly last-activity state and work-mode categories.
- Summary quality was strong for both providers; the largest matched semantic
  gap was last activity.
- Peak VRAM at R262K remained below 12 GiB on this runtime, but the unmeasured
  16K/32K breakpoints could offer a better memory/reliability tradeoff.
- The study has one hardware allocation, one quantization, one model artifact,
  30 conversations, and one repeat pair. Generalization beyond this setup
  requires more runs.
- The accepted FABLE references are comparison aids, not perfect ground truth.
  Exact agreement must not be described as absolute correctness.
- The R8 packages remain waiver-judged, not strict manager-valid.

### Claims not to publish

- Do not describe the host-visible 256-CPU/504-GiB totals as the Pod allocation.
- Do not claim physical CPU, process CPU/RAM, TTFT, desktop power, thermals,
  acoustics, or energy efficiency were measured.
- Do not say all three Qwen packages passed strict verification.
- Do not claim temperature zero made candidate or judge output deterministic.
- Do not claim 262K is the minimum context needed; 16K and 32K were not run.
- Do not claim maximum context made Qwen semantically equivalent to Gemini.
- Do not present Gemini as ground truth or FABLE agreement as absolute accuracy.
- Do not generalize the serial, warm-service latency result to provider-wide
  throughput or concurrency.
- Do not publish private prompts, inputs, references, rationales, aliases,
  hashes, paths, account details, cloud identifiers, or credentials.

## 13. PM-rework addendum — 2026-08-04

The executor applied the four bounded documentation corrections from the PM
validation review:

1. added all 12 accepted categorical confusion matrices, including explicit
   `no_valid_output` treatment and 30-position task denominators;
2. added one compact arm-by-arm publication table with reliability, timing,
   judge accounting, exact semantic denominators, verification, and separated
   candidate/judge cost boundaries;
3. added the public GGUF repository and filename, stated that no exact
   repository revision was captured, and made overall/per-task missing-usage
   counts explicit; and
4. removed the private judge-attempt-tree hash from the tracked supporting
   audit while preserving its unchanged-identity and zero-call cache proof.

The model-binary hash was also redacted from the supporting audit for
consistency with this report's privacy policy; its exact value remains in
ignored provenance storage. Arithmetic and matrix cells were reconstructed
only from the accepted immutable metrics. The accepted candidate packages,
scores, judge attempts, databases, return archives, verified backup, and
cleanup record were not modified. No inference, judging, RunPod, Vertex, or
other provider access occurred, and no full test run was needed because no
code changed.

## 14. Closure checklist

- [x] One canonical article-ready completion report created.
- [x] Frozen 120-case match across Qwen and Gemini proven from ordered fingerprints.
- [x] Hardware, runtime, timing, task, failure, token, telemetry, deterministic, judge, and cost evidence consolidated.
- [x] R8 repeatability analyzed.
- [x] R8 versus R262K endpoint tradeoff analyzed.
- [x] Matched R262K versus Gemini comparison completed.
- [x] R8 waiver status preserved explicitly.
- [x] Existing cache-only replay evidence recorded; zero provider calls.
- [x] Local archive and second-copy restore verified file-for-file.
- [x] Exact stopped RunPod Pod and attached volume deleted after verification.
- [x] Post-delete Pod/volume absence and US$0/hour account spend verified.
- [x] No model or judge calls made in WP-5.2C1.1.
- [x] No benchmark code, accepted inputs, packages, scores, or caches changed.
- [x] Full title-fit, work-mode, and last-activity confusion matrices included for all four arms.
- [x] Compact arm-by-arm publication table included with separated cost boundaries.
- [x] Public model repository/filename and missing revision/usage status made explicit.
- [x] Private judge-tree and model-binary hashes omitted from tracked documentation.
- [x] Delivery changes left unstaged and uncommitted for PM validation.

## End status

WP-5.2C1 is complete from an execution, evidence, publication, backup, and
resource-closure perspective. This documentation-only rework updated the
canonical completion report and the privacy wording in the supporting evidence
audit. Pre-existing manager-owned plan, ledger, handoff, validation-review,
research, and unrelated WP-5.2B3B progress changes remain preserved. The
report is ready for PM validation; nothing has been staged or committed.
