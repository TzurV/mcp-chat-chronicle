# WP-5.2B3A Completion Report

## 1. Status

**Ready for PM validation.** Both local 16K arms are complete, sealed, verified,
deterministically scored, fixed-Pro judged, cache-only replayed, and reconciled
against the immutable 8K packages. The context-only control passes.

## 2. Executive summary

Increasing context from 8,192 to 16,384 did not improve whole-package
reliability under the frozen contracts:

| Model | 8K valid | 16K valid | Change | 8K context failures | 16K context failures |
|---|---:|---:|---:|---:|---:|
| Qwen3.5-4B Q4_K_M | 84/120 (70.0%) | 84/120 (70.0%) | 0 | 29 | 0 |
| Phi-4 Mini Q4_K_M | 77/120 (64.2%) | 69/120 (57.5%) | -8 | 21 | 11 |
| **Combined** | **161/240 (67.1%)** | **153/240 (63.8%)** | **-8** | **50** | **11** |

No 8K context failure became a valid 16K output. Qwen moved all 29 such
failures to a different failure boundary. Phi retained 11 and moved ten to a
different failure boundary. Qwen had four unrelated invalid-to-valid
transitions offset by four valid-to-invalid regressions; Phi had one unrelated
recovery and nine valid-to-invalid regressions.

The complete evidence supports **common 8K** for WP-5.2B3B. Qwen's valid-output
quality and UTS improved among a different survivor set, but reliability stayed
flat and no context failure recovered. Phi's valid-output quality was nearly
flat while whole-case UTS and reliability regressed.

## 3. Scope and exclusions

Completed:

- reused and reverified the accepted Qwen and Phi 120-case 8K packages;
- generated only two new local 120-case arms at 16K;
- preserved every first-attempt candidate outcome;
- verified both new packages and ran deterministic-only scoring;
- proved the only effective package change was context 8,192 to 16,384;
- reconciled all 240 8K-to-16K case transitions;
- compared reliability, deterministic semantics, latency, tokens, and
  available resource evidence;
- judged all eligible results or preserved an explicit terminal judge failure;
- proved cache-only zero-call, byte-stable replay for both packages;
- produced this report and the companion article evidence brief.

Excluded as required: prompt or selector changes, 32K, model-specific context
selection, remote candidate generation, new teacher references, human
adjudication, production behavior changes, and final article graphics.

## 4. Accepted 8K baseline identities and aggregates

The immutable baselines are the accepted full packages from
[WP-5.2B1.4](WP-5.2B1.4-completion-report.md) and
[WP-5.2B2.2](WP-5.2B2.2-completion-report.md).

| Model | Benchmark revision | Valid | Failure boundaries | Task valid: summary/mode/activity/title | Macro UTS |
|---|---|---:|---|---|---:|
| Qwen | accepted WP-5.2B1.4 revision, package format 0.1.0 | 84 | context 29; timeout 5; schema 2 | 17/19/30/18 | 61.9 |
| Phi | accepted WP-5.2B2.2 revision, package format 0.1.0 | 77 | context 21; timeout 10; schema 12 | 14/18/29/16 | 50.0 |

Both packages reverified at their exact accepted revisions with 120 terminal
positions and their accepted valid/failure totals.

## 5. Runtime-identity comparison

Each arm reproduced its accepted artifact and runtime separately:

- exact accepted Q4_K_M artifact bytes, size, revision, loaded identity, and
  API identity rechecked privately;
- LM Studio CLI identity `9902c3a`;
- accepted llama.cpp Vulkan AVX2 engine 2.25.2;
- automatic device/offload selection, parallelism one;
- same model, quantization, prompts, schemas, selectors, temperature,
  token limits, timeout, retry, reasoning, and structured-output contract;
- configured context was the sole effective change: 8,192 to 16,384.

The machine class was Windows 11 Pro on a 4-core/8-thread 11th-generation Intel
mobile CPU, approximately 32 GiB physical RAM, and integrated Intel Iris Xe
graphics. No discrete/dedicated VRAM was reported. Qwen load/setup took
34.23s; Phi took 11.81s. Load time is separate from candidate wall time.

## 6. Frozen comparison manifest

The private manifest was created and frozen before the first 16K candidate
call. Revalidation passed for the manifest itself, frozen and live databases,
selected inputs, FABLE references, task catalog, selection/snapshot
manifests, and both 8K/16K model/evaluation configs. It was never edited after
generation began.

## 7. Qwen 16K synthetic gate

The exact Qwen artifact was loaded at 16,384 context and parallelism one.
API/runtime identity matched, and the strict synthetic transport/schema gate
passed 4/4 tasks before private generation.

## 8. Qwen 16K 120-case accounting

- terminal positions: 120/120;
- authoritative attempts: 120, with no completed-position duplicates;
- valid: 84;
- failed: 36;
- task validity summary/mode/activity/title: 17/20/28/19;
- failure boundaries: timeout 35; schema validation 1; context 0;
- no invalid output was repaired, hidden, or retried.

The generator sealed a complete package. Non-fatal client-session warnings
appeared only after terminal completion and did not affect accounting or
verification.

## 9. Phi 16K synthetic gate

The exact Phi artifact was loaded at 16,384 context and parallelism one.
API/runtime identity matched, and the strict synthetic transport/schema gate
passed 4/4 tasks before private generation.

## 10. Phi 16K 120-case accounting

- terminal positions: 120/120;
- authoritative attempts: 120, with no completed-position duplicates;
- valid: 69;
- failed: 51;
- task validity summary/mode/activity/title: 14/17/23/15;
- failure boundaries: context 11; provider HTTP 14; schema validation 11;
  timeout 15;
- no invalid output was repaired, hidden, or retried.

The generator sealed a complete package. LiteLLM timeout notices and two
non-fatal client-session warnings appeared after terminal completion; package
accounting and verification passed.

## 11. Package verification

All four packages passed verification from the model-specific accepted
benchmark revisions:

| Package | Expected | Attempts | Valid | Failed | Result |
|---|---:|---:|---:|---:|---|
| Qwen 8K accepted | 120 | 120 | 84 | 36 | pass |
| Qwen 16K new | 120 | 120 | 84 | 36 | pass |
| Phi 8K accepted | 120 | 120 | 77 | 43 | pass |
| Phi 16K new | 120 | 120 | 69 | 51 | pass |

The pair validator confirmed identical ordered cases, artifact/generation
contracts, application provenance, scope, actual/resolved model identities,
providers, API-base class, and all runtime fields other than context. Unique
16K candidate IDs and output locations were non-effective bookkeeping
changes.

## 12. Deterministic scoring

Both 16K packages passed deterministic-only scoring with all invalid positions
retained in denominators.

| Model/context | Evidence/cross-field valid | No valid output | Summary date/length | Title suggestion valid | Mode agreement | Activity agreement | Title-fit agreement |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen 8K | 84/84 | 36 | 17/17 | 18 | 10/30 (33.3%) | 18/30 (60.0%) | 17/30 (56.7%) |
| Qwen 16K | 84/84 | 36 | 17/17 | 19 | 11/30 (36.7%) | 17/30 (56.7%) | 18/30 (60.0%) |
| Phi 8K | 77/77 | 43 | 14/14 | 15 | 3/30 (10.0%) | 18/30 (60.0%) | 5/30 (16.7%) |
| Phi 16K | 69/69 | 51 | 14/14 | 14 | 3/30 (10.0%) | 15/30 (50.0%) | 5/30 (16.7%) |

The matrices below use `reference → prediction=count`; omitted cells are zero.
Every matrix totals 30.

| Arm/task | Non-zero confusion rows |
|---|---|
| Qwen 8K mode | executor→executor 4, manager 2, no-output 8; manager→manager 1, no-output 2; mixed→no-output 1; one-off→executor 1, manager 6, one-off 5 |
| Qwen 16K mode | executor→executor 5, manager 2, no-output 7; manager→manager 1, no-output 2; mixed→no-output 1; one-off→executor 2, manager 5, one-off 5 |
| Qwen 8K activity | awaiting→awaiting 1, completed 1, in-progress 5; completed→completed 14, in-progress 2; in-progress→blocked 1, completed 3, in-progress 3 |
| Qwen 16K activity | awaiting→awaiting 1, completed 1, in-progress 5; completed→completed 14, in-progress 2; in-progress→blocked 1, completed 2, in-progress 2, no-output 2 |
| Qwen 8K title | false→false 3, true 1, no-output 7; true→true 14, no-output 5 |
| Qwen 16K title | false→false 4, true 1, no-output 6; true→true 14, no-output 5 |
| Phi 8K mode | executor→executor 1, mixed 5, no-output 8; manager→mixed 1, no-output 2; mixed→no-output 1; one-off→mixed 7, one-off 2, unknown 2, no-output 1 |
| Phi 16K mode | executor→executor 1, mixed 4, no-output 9; manager→mixed 1, no-output 2; mixed→no-output 1; one-off→mixed 7, one-off 2, unknown 2, no-output 1 |
| Phi 8K activity | awaiting→completed 3, in-progress 4; completed→completed 14, unknown 1, no-output 1; in-progress→completed 3, in-progress 4 |
| Phi 16K activity | awaiting→completed 2, in-progress 4, no-output 1; completed→completed 12, unknown 1, no-output 3; in-progress→completed 1, in-progress 3, no-output 3 |
| Phi 8K title | false→false 2, true 1, no-output 8; true→false 10, true 3, no-output 6 |
| Phi 16K title | false→false 2, no-output 9; true→false 10, true 3, no-output 6 |

Per-label precision/recall/support is unchanged or nearly unchanged except
where no-output regressions reduce recall. Values are listed as
`precision/recall/support`; `NA` means the denominator is zero.

| Arm/task | Per-label values |
|---|---|
| Qwen 8K mode | executor .800/.286/14; manager .111/.333/3; mixed NA/.000/1; one-off 1.000/.417/12 |
| Qwen 16K mode | executor .714/.357/14; manager .125/.333/3; mixed NA/.000/1; one-off 1.000/.417/12 |
| Qwen 8K activity | awaiting 1.000/.143/7; completed .778/.875/16; in-progress .300/.429/7 |
| Qwen 16K activity | awaiting 1.000/.143/7; completed .824/.875/16; in-progress .222/.286/7 |
| Qwen 8K title | false 1.000/.273/11; true .933/.737/19 |
| Qwen 16K title | false 1.000/.364/11; true .933/.737/19 |
| Phi 8K mode | executor 1.000/.071/14; manager NA/.000/3; mixed .000/.000/1; one-off 1.000/.167/12 |
| Phi 16K mode | executor 1.000/.071/14; manager NA/.000/3; mixed .000/.000/1; one-off 1.000/.167/12 |
| Phi 8K activity | awaiting NA/.000/7; completed .700/.875/16; in-progress .500/.571/7 |
| Phi 16K activity | awaiting NA/.000/7; completed .800/.750/16; in-progress .429/.429/7 |
| Phi 8K title | false .167/.182/11; true .750/.158/19 |
| Phi 16K title | false .167/.182/11; true 1.000/.158/19 |

## 13. Judge authorization and synthetic gate

One consolidated authorization was obtained before disclosure for both new
packages, all schema-valid eligible results, disclosure of selected source
input, candidate result, and fixed FABLE reference to
`vertex_ai/gemini-3.1-pro-preview` in `global` via ADC, rubric v1, ordinary
Vertex usage cost, and only the configured bounded retry.

The four-task structured synthetic judge gate then passed 4/4 before package
judging. The earlier generic “continue” instruction was not treated as
authorization; judging began only after the owner explicitly approved the
described disclosure.

## 14. Judge accounting and cache-only replay

| Arm | Eligible | Completed | Terminal failed | Skipped invalid | Judge attempts |
|---|---:|---:|---:|---:|---:|
| Qwen 8K accepted | 84 | 84 | 0 | 36 | accepted immutable evidence |
| Qwen 16K | 84 | 84 | 0 | 36 | 84 |
| Phi 8K accepted | 77 | 77 | 0 | 43 | accepted immutable evidence |
| Phi 16K | 69 | 68 | 1 `output_schema` | 51 | 69 |

Every new eligible result therefore has a successful score or explicit
terminal judge failure. Identical cache-only replays exited zero. Qwen remained
at 84 attempts and Phi at 69; both judge evidence trees, case-score files,
metrics, and aggregate reports were byte-identical before and after replay.
The replay made zero new provider calls.

## 15. Product reliability

| Model/context | Valid | Invalid | Summary | Mode | Activity | Title | Failure boundaries |
|---|---:|---:|---:|---:|---:|---:|---|
| Qwen 8K | 84 (70.0%) | 36 | 17 | 19 | 30 | 18 | context 29; timeout 5; schema 2 |
| Qwen 16K | 84 (70.0%) | 36 | 17 | 20 | 28 | 19 | timeout 35; schema 1 |
| Phi 8K | 77 (64.2%) | 43 | 14 | 18 | 29 | 16 | context 21; timeout 10; schema 12 |
| Phi 16K | 69 (57.5%) | 51 | 14 | 17 | 23 | 15 | context 11; provider HTTP 14; timeout 15; schema 11 |

Qwen's absolute valid gain and relative invalid reduction were both zero.
Phi's absolute valid gain was -8 and invalid count increased 18.6% relative to
its 8K invalid count. Combined invalid count increased from 79 to 87 (10.1%).

## 16. Transition matrices

Each matrix totals exactly 120:

| Model | 8K invalid→16K invalid | Invalid→valid | Valid→invalid | Valid→valid |
|---|---:|---:|---:|---:|
| Qwen | 32 | 4 | 4 | 80 |
| Phi | 42 | 1 | 9 | 68 |

Per-task matrices:

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

Failure-category transitions:

- Qwen: context→timeout 29; schema→schema 1; schema→valid 1;
  timeout→timeout 2; timeout→valid 3; valid→timeout 4; valid→valid 80.
- Phi: context→context 11; context→provider-HTTP 4; context→timeout 6;
  schema→schema 11; schema→timeout 1; timeout→provider-HTTP 4;
  timeout→timeout 5; timeout→valid 1; valid→provider-HTTP 6;
  valid→timeout 3; valid→valid 68.

Recovered-context count is zero for both models. Consequently there is no
recovered-context semantic cohort to judge; quality is `N/A (n=0)`.

## 17. Deterministic semantics

Qwen traded small changes across tasks: mode agreement +3.3 points, activity
-3.3, and title +3.3, with no whole-package reliability gain. Phi mode and
title agreement were unchanged, activity fell ten points, and no-valid-output
increased by eight. These are agreement results against FABLE silver
references, not accuracy or ground truth.

## 18. Fixed-judge semantics

| Model/context | Eligible/completed/failed | Valid-output quality (macro, 0–1) | Task UTS summary/mode/activity/title | Macro UTS | UTS delta |
|---|---:|---:|---|---:|---:|
| Qwen 8K | 84/84/0 | 0.887 | 56.7/41.7/89.1/60.0 | 61.9 | — |
| Qwen 16K | 84/84/0 | 0.935 | 56.7/56.4/85.6/62.0 | 65.2 | +3.3 |
| Phi 8K | 77/77/0 | 0.780 | 39.1/37.2/77.8/45.8 | 50.0 | — |
| Phi 16K | 69/68/1 | 0.791 | 40.7/36.1/64.8/37.8 | 44.8 | -5.1 |

Each value below is a mean over successfully judged outputs for that task:

| Arm/task | Dimension means and denominators |
|---|---|
| Qwen 16K summary | concise usefulness 4.000 (17); conversation characterization 4.000 (17); factual consistency 4.000 (17); material coverage 4.000 (17); unsupported-claim avoidance 4.000 (17) |
| Qwen 16K mode | label support 3.300 (20); mode distinction 3.300 (20); reason specificity 3.650 (20); unsupported-claim avoidance 3.900 (20) |
| Qwen 16K activity | blocker correctness 3.857 (28); final meaningful activity 3.964 (28); next-action support 3.214 (28); not-source-copying 4.000 (28); status correctness 3.500 (28); unsupported-claim avoidance 3.964 (28) |
| Qwen 16K title | dominant-activity fit 3.895 (19); suggestion-only compliance 4.000 (19); suggestion usefulness 3.789 (19); title-fits correctness 4.000 (19); unsupported-claim avoidance 4.000 (19) |
| Phi 16K summary | concise usefulness 3.643 (14); conversation characterization 3.214 (14); factual consistency 4.000 (14); material coverage 3.214 (14); unsupported-claim avoidance 4.000 (14) |
| Phi 16K mode | label support 2.647 (17); mode distinction 2.647 (17); reason specificity 2.941 (17); unsupported-claim avoidance 3.412 (17) |
| Phi 16K activity | blocker correctness 4.000 (23); final meaningful activity 3.261 (23); next-action support 3.043 (23); not-source-copying 3.696 (23); status correctness 3.304 (23); unsupported-claim avoidance 3.913 (23) |
| Phi 16K title | dominant-activity fit 3.143 (14); suggestion-only compliance 4.000 (14); suggestion usefulness 3.571 (14); title-fits correctness 2.429 (14); unsupported-claim avoidance 4.000 (14); one additional eligible title judge failed |

No context-failed case recovered, so recovered-context quality remains
`N/A (n=0)` for both models. Among cases valid at both contexts, Qwen had
80 cases/80 completed with mean normalized quality 0.927 and whole-cohort UTS
92.7. Phi had 68 cases/67 completed/one failed with mean normalized quality
0.797 and whole-cohort UTS 78.5.

UTS formula v1 gives a case zero when candidate output is invalid/absent or
judge scoring does not complete. Otherwise it averages applicable 1–4 rubric
scores normalized by `(score - 1) / 3`; each task averages its 30 cases, the
four tasks are macro-averaged, then multiplied by 100. Valid-output quality is
the macro normalized mean over successfully judged, schema-valid outputs only
and must always be paired with valid rate. Latency is not part of UTS.

## 19. Latency, token, and resource evidence

Overall p50 uses the accepted reports' median convention; p95 and per-task
values use the benchmark's frozen percentile convention.

| Model/context | Candidate wall span | Summed latency | p50/p95 | Timeouts; summed duration |
|---|---:|---:|---:|---:|
| Qwen 8K | 4h43m30.782s | 4h43m27.047s | 62.094/168.375s | 5; 2h39m37.355s |
| Qwen 16K | 3h56m20.700s | 3h56m16.446s | 117.039/180.093s | 35; 1h45m02.344s |
| Phi 8K | 2h18m50.713s | 2h18m47.392s | 54.608/180.031s | 10; 30m00.589s |
| Phi 16K | 2h31m30.816s | 2h31m26.607s | 59.250/180.077s | 15; 45m01.603s |

The accepted raw Qwen 8K span includes one 8,857s interruption/timeout tail and
must not be interpreted alone. Its 29 fast context failures total about 53s,
84 successes about two hours, two schema failures about 172s, and five
timeouts about 2h39m; excluding timeout durations, summed latency is about
2h04m. Qwen 16K excluding timeout durations is about 2h11m.

Per-task p50/p95:

| Arm | Summary | Mode | Activity | Title |
|---|---:|---:|---:|---:|
| Qwen 8K | 61.687/180.030s | 49.047/162.922s | 81.844/134.967s | 48.187/150.467s |
| Qwen 16K | 125.266/180.093s | 113.092/180.093s | 93.343/172.813s | 114.985/180.078s |
| Phi 8K | 52.297/180.015s | 45.172/180.062s | 59.000/129.890s | 47.280/180.030s |
| Phi 16K | 67.202/180.062s | 53.906/180.063s | 64.750/180.046s | 50.281/180.047s |

Observed usage is incomplete on failure paths:

| Arm | Usage available/missing | Prompt | Completion | Total |
|---|---:|---:|---:|---:|
| Qwen 8K | 86/34 | 246,596 | 11,310 | 257,906 |
| Qwen 16K | 85/35 | 238,943 | 11,129 | 250,072 |
| Phi 8K | 89/31 | 235,783 | 11,194 | 246,977 |
| Phi 16K | 80/40 | 200,761 | 9,879 | 210,640 |

Lower observed token totals do not mean lower full-arm consumption because
missing usage increased and failed calls expose no reliable totals.

The 16K resource sampler observed:

| Arm | Window samples | Peak system-used RAM | Peak LM Studio process-group working set | Peak shared/dedicated GPU memory |
|---|---:|---:|---:|---:|
| Qwen 16K | 2,276 | 31.35 GiB | 9.65 GiB | 4.13/0 GiB |
| Phi 16K | 1,426 | 31.71 GiB | 12.87 GiB | 4.50/0 GiB |

Qwen sampling began roughly three minutes after candidate start and continued
past unload; only timestamps inside its candidate window were aggregated. Phi
coverage began within seconds and ended within seconds. System RAM includes
all processes and LM Studio working set includes its process group, so neither
is model-exclusive. The Windows GPU utilization counter exceeded 100% and is
invalid for percentage reporting; memory counters are retained, utilization
is unavailable. Accepted 8K runs did not capture comparable peak telemetry, so
no measured 8K-to-16K RAM delta is claimed.

## 20. Unchanged cloud-reference comparison

| Control | Valid | Macro UTS | Label |
|---|---:|---:|---|
| Gemini 3.5 Flash | 112/120 (93.3%) | 88.4 | unchanged historical cloud control; not regenerated in WP-5.2B3A |

The local/cloud validity gaps remain 23.3 points for Qwen 16K and 35.8 for Phi
16K. Context alone did not close the gap. Local and cloud latency are not
hardware-equivalent measurements.

## 21. Context-policy recommendation

Recommend **common 8K** for WP-5.2B3B.

The 16K gate fails the handoff's decision criteria: combined valid count fell,
Phi materially regressed, no context failure became valid, valid cases
regressed, and long-tail cost increased. Qwen's flat valid count does not
justify its p50 increase from 62.094s to 117.039s. The recommendation is common
rather than model-specific as required.

This is a bounded development decision between tested 8K and 16K settings, not
evidence that 8K is universally optimal.

## 22. Article-brief delivery

The publication-ready companion evidence brief is
[WP-5.2B3A-context-comparison-article-brief.md](WP-5.2B3A-context-comparison-article-brief.md).

## 23. Privacy and data tracking

Candidate generation stayed on loopback LM Studio. Tracked reports contain no
case IDs, conversation/message IDs, titles, URLs, raw inputs, outputs,
references, rationales, private paths, hashes, credentials, or machine-user
identity. Private bundles, packages, scoring outputs, manifests, samples, and
helpers remain ignored.

## 24. Live/frozen database immutability

Private preflight and post-run fingerprints match. Both databases passed
integrity/schema checks and remained unchanged. Selected inputs, references,
task catalog, and selection/snapshot authorities also match the frozen
manifest.

## 25. Historical-package immutability

Both accepted packages reverified unchanged from detached worktrees at their
exact accepted benchmark revisions. No accepted package, accepted scoring
evidence, or WP-5.2C1 artifact was modified.

## 26. Validation

- repository Poetry environment: repository `.venv`;
- full tests: **446 passed, 1 skipped**;
- Ruff: pass;
- `poetry check`: pass;
- benchmark root/generate/verify/score help: pass;
- Chronicle help and AI-task list: pass;
- four package verifications: pass;
- context-only package-pair validation: pass;
- frozen comparison-manifest validation: pass;
- both candidate synthetic gates: 4/4 pass;
- both deterministic scores: pass;
- 240 transitions: pass, 120 per model;
- private tracking scan: no tracked private artifacts;
- fixed-Pro synthetic judge gate: 4/4 pass;
- judge accounting: Qwen 84/84 complete; Phi 68/69 complete with one explicit
  terminal failure;
- both cache-only replays: pass, zero new calls and byte-stable evidence;
- `git diff --check`: pass before report creation; final pass recorded below.

The first piped Chronicle help display produced a Windows Rich broken-pipe
traceback because output was truncated. The required command was rerun
unpiped and passed; this was not a product or benchmark failure.

## 27. Known limitations

- private real-work development corpus;
- 30 conversations and 120 cases per arm;
- FABLE silver references;
- fixed Gemini-family judge, including one terminal Phi judge-schema failure;
- same corpus used to select context;
- one Windows laptop, one GGUF quantization per model, one LM Studio runtime
  contract;
- no untouched context holdout and no 32K arm;
- no statistical or general-population claims;
- no evidence that either tested choice is optimal outside this contract;
- no evidence yet that prompt gains will generalize;
- no comparable historical 8K peak-memory telemetry;
- one Qwen resource-monitor startup gap of roughly three minutes;
- invalid Windows GPU-utilization percentage telemetry;
- an owner docs-only commit advanced repository HEAD during the long run; it
  did not touch benchmark code, authorities, packages, or report targets.

## 28. Acceptance checklist

1. Poetry repository environment: pass.
2. Clean preflight except owner drafts: pass.
3. Database/evidence fingerprints captured privately: pass.
4. Accepted packages unchanged: pass.
5. Artifact/runtime provenance reproduced: pass.
6. Frozen private comparison manifest: pass.
7. Qwen synthetic 4/4: pass.
8. Qwen 120 terminal positions: pass.
9. Qwen verify/deterministic score: pass.
10. Phi synthetic 4/4: pass.
11. Phi 120 terminal positions: pass.
12. Phi verify/deterministic score: pass.
13. No duplicate completed positions: pass.
14. Invalid outputs preserved: pass.
15. Context is sole effective change: pass.
16. All 240 positions reconciled: pass.
17. Transition matrices total 120/model: pass.
18. Failure categories reconcile: pass.
19. Deterministic matrices total 30/task: pass.
20. Fixed-Pro authorization before disclosure: pass.
21. Every eligible result judged/terminal: pass.
22. Cache-only replay zero-call/byte-stable: pass.
23. Speed/resource evidence: pass with stated telemetry limits.
24. Cloud reference labeled unchanged: pass.
25. Common context recommendation: pass, common 8K.
26. Article evidence brief: delivered, publication-ready.
27. Completion report: delivered, ready for PM validation.
28. Databases unchanged: pass.
29. Historical/WP-5.2C1 artifacts unchanged: pass.
30. No private artifact/credential tracked: pass.
31. Full tests and Ruff: pass.
32. Poetry/help/diff validation: pass.
33. Nothing staged or committed by executor: pass.

## 29. Exact files changed

Only the two required untracked reports are intended executor changes:

- `md/handoffs/reports/WP-5.2B3A-completion-report.md`;
- `md/handoffs/reports/WP-5.2B3A-context-comparison-article-brief.md`.

Ignored local evidence and analysis helpers are not tracked.

## 30. Final `git status --short`

Final status is:

```text
?? md/handoffs/reports/WP-5.2B3A-completion-report.md
?? md/handoffs/reports/WP-5.2B3A-context-comparison-article-brief.md
```

## 31. Staging and commit confirmation

The executor staged and committed nothing. The repository advanced during the
long run only through an owner docs/publication commit; its intervening file
list was checked and did not conflict with WP-5.2B3A evidence or report paths.
