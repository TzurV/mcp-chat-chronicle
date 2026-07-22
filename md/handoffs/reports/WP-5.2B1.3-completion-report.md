# WP-5.2B1.3 Completion Report

## 1. Status

**Ready for PM validation.** Both accepted candidate arms completed the same frozen
10-conversation, 40-case development pilot. All 80 candidate positions reconcile, all 60
schema-valid outputs have current terminal Pro-judge scores, and both cache-only CLI replays
completed with zero provider calls.

This is a development pilot over silver FABLE references and an automated judge. It is not a
scientific benchmark, publication run, general leaderboard, or statistical superiority claim.

## 2. Executive summary

The local Llama arm produced 21 schema-valid outputs from 40 cases (52.5%); the hosted Gemini arm
produced 39 (97.5%). All invalid outputs and explicit failures remain immutable evaluation
evidence. The Pro judge completed every currently eligible case after one Llama case required two
append-only schema retries. Candidate generation took 257.653 seconds locally and 382.652 seconds
through Vertex.

The simple local 120-case planning projection is 772.959 seconds (12 minutes 52.959 seconds),
calculated as three times the measured final 40-case wall time. This is a linear planning estimate,
not a benchmark result.

## 3. Repository commit and environment preflight

- Candidate generation application commit for both final packages:
  `dcca7b21396eade4397840f5900706c1bc0d8e22`.
- Post-generation scoring/cache-finalization fix commit:
  `3580d6dbcc7e436601e115f8a530303b9e0bb04a`.
- The scoring fix commit is recorded separately and was not written into either candidate package
  or candidate configuration as generation provenance.
- Final candidate package hashes match the identities recorded before the scoring fix.
- Poetry resolved to this repository's `.venv` before benchmark and validation commands.
- The tracked checkout was clean before both final candidate generations.
- PM-owned planning and previously accepted artifacts were preserved.

## 4. Frozen contract and scope identity

Both arms independently selected `frozen-prefix-v1` with `--conversation-limit 10` and the accepted
task order:

1. `conversation-summary`;
2. `work-mode-classification`;
3. `last-activity`;
4. `title-assessment`.

Each bundle contained exactly 10 conversations and 40 unique ordered cases. The ordered case
identities and frozen-prefix identity matched across arms. Exact identities remain private. The
portable bundles contained no absolute workspace path or credential-like value.

## 5. Private configuration and provenance summary

| Property | Arm A | Arm B |
| --- | --- | --- |
| Candidate | Llama 3.2 1B Instruct, Bartowski Q4_K_M | `vertex_ai/gemini-3.5-flash` |
| Execution | LM Studio, local artifact | Vertex AI hosted API |
| Region | local | `global` |
| Context / candidate concurrency | 8,192 / 1 | accepted hosted profile |
| Candidate authorization flags | not applicable | `--allow-remote --confirm-private-eval` |
| Judge | `vertex_ai/gemini-3.1-pro-preview` | same |
| Judge policy | rubric v1, temperature 0, 1,000 tokens, reasoning `none` | same |
| Generation application commit | `dcca7b2` | `dcca7b2` |

LM Studio reported the accepted identifier, Q4_K_M quantization, 8,192-token context, parallelism
1, and the expected endpoint model. The configured artifact filename and SHA-256 matched the loaded
artifact. Vertex used ADC; no API-key fallback occurred. Project/account identity is not recorded.

## 6. Arm A generation, verification, and deterministic scoring

| Measure | Result |
| --- | ---: |
| Expected / terminal / unaccounted | 40 / 40 / 0 |
| Schema-valid | 21 (52.5%) |
| Failed or invalid | 19 |
| Evidence-valid / cross-field-valid | 21 / 21 |
| Summary date-valid / length-valid | 6 / 6 |
| Title suggestion-valid | 3 |
| Total candidate attempts | 40 |
| Wall time | 257.653 s |
| Latency p50 / p95 | 5.516 / 12.405 s |
| Usage availability | 34 of 40 cases |
| Prompt / completion / reasoning / total tokens | 75,956 / 3,181 / 0 / 79,137 |

Failure boundaries were six `context_length`, seven `evidence_validation`, and six
`schema_validation`. Package verification and deterministic-only scoring passed locally.

Per-task candidate results:

| Task | Valid / failed | p50 / p95 latency |
| --- | ---: | ---: |
| Summary | 6 / 4 | 7.250 / 24.313 s |
| Work mode | 8 / 2 | 5.211 / 12.405 s |
| Last activity | 4 / 6 | 6.476 / 9.078 s |
| Title assessment | 3 / 7 | 5.179 / 9.797 s |

## 7. Arm B generation, verification, and deterministic scoring

| Measure | Result |
| --- | ---: |
| Expected / terminal / unaccounted | 40 / 40 / 0 |
| Schema-valid | 39 (97.5%) |
| Failed or invalid | 1 |
| Evidence-valid / cross-field-valid | 39 / 39 |
| Summary date-valid / length-valid | 9 / 9 |
| Title suggestion-valid | 10 |
| Total candidate attempts | 40 |
| Wall time | 382.652 s |
| Latency p50 / p95 | 8.929 / 20.045 s |
| Usage availability | 40 of 40 cases |
| Prompt / completion / reasoning / total tokens | 166,916 / 5,176 / 319 / 172,092 |

The single retained candidate failure was `invalid_json`. Package verification and
deterministic-only scoring passed locally.

Per-task candidate results:

| Task | Valid / failed | p50 / p95 latency |
| --- | ---: | ---: |
| Summary | 9 / 1 | 7.937 / 20.045 s |
| Work mode | 10 / 0 | 3.289 / 20.469 s |
| Last activity | 10 / 0 | 12.483 / 18.797 s |
| Title assessment | 10 / 0 | 10.226 / 21.141 s |

## 8. Pro-judge accounting

| Measure | Arm A | Arm B |
| --- | ---: | ---: |
| Eligible | 21 | 39 |
| Current completed / failed | 21 / 0 | 39 / 0 |
| Invalid candidate skipped | 19 | 1 |
| Unaccounted eligible | 0 | 0 |
| Baseline completed / failed | 20 / 1 | 39 / 0 |
| Total judge attempts | 23 | 39 |
| Current finish reason `stop` | 21 | 39 |

One Arm A Pro response failed application schema validation. Two append-only retries under the
identical contract were required; the first retry was also schema-invalid and the second produced
a valid score. The failed attempts remain preserved. No valid semantic score was retried because
of disagreement with FABLE or the other candidate.

## 9. Cache-only zero-call proof

Both commands used `--with-judge --allow-remote --confirm-private-eval --judge-cache-only` and
exited zero under scoring fix commit `3580d6d`.

| Proof | Arm A | Arm B |
| --- | ---: | ---: |
| Cache-only exit | 0 | 0 |
| Provider calls | 0 | 0 |
| Replay wall time | 10.888 s | 8.503 s |
| Candidate package unchanged | yes | yes |
| Attempt count and aggregate unchanged | yes | yes |
| Judge metrics unchanged | yes | yes |
| Aggregate report coherent | yes | yes |

Cache-only mode is fail-closed: a miss raises before provider execution. Attempt-file hashes,
package hashes, metrics identities, and completed/failed/skipped accounting were unchanged across
both replays.

## 10. Privacy-safe side-by-side metrics

| Measure | Local Llama | Hosted Gemini |
| --- | ---: | ---: |
| Cases / terminal | 40 / 40 | 40 / 40 |
| Schema-valid rate | 52.5% | 97.5% |
| Evidence and cross-field valid | 21 | 39 |
| Candidate wall time | 257.653 s | 382.652 s |
| Candidate latency p50 / p95 | 5.516 / 12.405 s | 8.929 / 20.045 s |
| Prompt tokens | 75,956 (34 cases reported) | 166,916 |
| Completion tokens | 3,181 (34 cases reported) | 5,176 |
| Reasoning tokens | 0 reported | 319 |
| Provider/candidate retries | 0 | 0 |
| Rate-limit / timeout failures | 0 / 0 | 0 / 0 |
| Judge current completed / failed | 21 / 0 | 39 / 0 |
| Cache-only provider calls | 0 | 0 |

Settings were held to the accepted profiles. Intended differences are candidate identity,
local-artifact versus hosted execution/provenance, and provider-required usage metadata. Tasks,
selection, prompts, schemas, finalizers, evidence policy, temperature, task token caps, references,
judge, and rubric were unchanged.

## 11. Confusion matrices and deterministic task metrics

Rows are FABLE labels and columns are candidate labels. `NVO` means `no_valid_output`.

### Work mode

| Arm A | executor | manager | mixed | one_off | unknown | NVO |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| executor | 0 | 0 | 1 | 0 | 0 | 2 |
| manager | 0 | 0 | 1 | 0 | 0 | 0 |
| mixed | 0 | 0 | 0 | 0 | 0 | 0 |
| one_off | 0 | 1 | 5 | 0 | 0 | 0 |
| unknown | 0 | 0 | 0 | 0 | 0 | 0 |

| Arm B | executor | manager | mixed | one_off | unknown | NVO |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| executor | 0 | 0 | 1 | 2 | 0 | 0 |
| manager | 0 | 1 | 0 | 0 | 0 | 0 |
| mixed | 0 | 0 | 0 | 0 | 0 | 0 |
| one_off | 0 | 0 | 0 | 6 | 0 | 0 |
| unknown | 0 | 0 | 0 | 0 | 0 | 0 |

Exact agreement was 0% for Arm A and 70% for Arm B. FABLE support was executor 3, manager 1,
mixed 0, one_off 6, unknown 0.

### Last-activity status

| Arm A | awaiting | blocked | completed | in progress | unknown | NVO |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| awaiting | 0 | 0 | 0 | 2 | 0 | 0 |
| blocked | 0 | 0 | 0 | 0 | 0 | 0 |
| completed | 0 | 0 | 0 | 0 | 1 | 4 |
| in progress | 0 | 0 | 0 | 1 | 0 | 2 |
| unknown | 0 | 0 | 0 | 0 | 0 | 0 |

| Arm B | awaiting | blocked | completed | in progress | unknown | NVO |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| awaiting | 1 | 0 | 1 | 0 | 0 | 0 |
| blocked | 0 | 0 | 0 | 0 | 0 | 0 |
| completed | 0 | 0 | 5 | 0 | 0 | 0 |
| in progress | 0 | 0 | 2 | 1 | 0 | 0 |
| unknown | 0 | 0 | 0 | 0 | 0 | 0 |

Exact agreement was 10% for Arm A and 70% for Arm B. FABLE support was awaiting input 2,
blocked 0, completed 5, in progress 3, unknown 0.

### Title fit

| Arm | false→false | false→true | false→NVO | true→false | true→true | true→NVO | Exact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Arm A | 1 | 1 | 1 | 1 | 0 | 6 | 10% |
| Arm B | 3 | 0 | 0 | 1 | 6 | 0 | 90% |

FABLE title-fit support was false 3 and true 7.

## 12. Semantic judge dimension summary

Means are over schema-valid/current-completed cases for each task.

| Task / dimension | Arm A | Arm B |
| --- | ---: | ---: |
| Summary: factual consistency | 4.000 | 4.000 |
| Summary: material coverage | 2.833 | 3.889 |
| Summary: concise usefulness | 3.167 | 4.000 |
| Summary: conversation characterization | 2.333 | 4.000 |
| Summary: unsupported-claim avoidance | 3.333 | 4.000 |
| Work mode: label support | 1.000 | 3.200 |
| Work mode: mode distinction | 1.000 | 3.200 |
| Work mode: reason specificity | 1.125 | 3.500 |
| Work mode: unsupported-claim avoidance | 2.000 | 3.800 |
| Last activity: blocker correctness | 1.000 | 4.000 |
| Last activity: final meaningful activity | 2.250 | 4.000 |
| Last activity: status correctness | 1.000 | 3.900 |
| Last activity: next-action support | 1.000 | 3.900 |
| Last activity: not source copying | 2.250 | 4.000 |
| Last activity: unsupported-claim avoidance | 2.500 | 4.000 |
| Title: dominant activity fit | 3.000 | 4.000 |
| Title: title-fits correctness | 2.667 | 4.000 |
| Title: suggestion-only compliance | 4.000 | 4.000 |
| Title: suggestion usefulness | 4.000 | 4.000 |
| Title: unsupported-claim avoidance | 4.000 | 4.000 |

## 13. Local runtime projection

Measured final Arm A wall time was 257.653 seconds. Three times that result gives a 120-case linear
planning estimate of 772.959 seconds (12 minutes 52.959 seconds). The estimate may be inaccurate
because warm-up, input/context-length mix, six fast context-limit terminations, machine load,
interruption, and retry behavior need not scale linearly. The earlier superseded local run was
retained privately but is not used for this final-package projection.

## 14. Preserved model-output failures

- Arm A: six context-length failures, seven evidence-validation failures, and six schema-validation
  failures.
- Arm B: one invalid-JSON failure.
- All failures remain in the ignored immutable package/run evidence. No candidate response was
  repaired, truncated, removed, or semantically retried.
- Invalid candidates were scored deterministically as `no_valid_output` and excluded from semantic
  judging.

## 15. Infrastructure defects and recovery cycles

1. The original package leakage scanner treated the ordinary word `credential` in candidate text
   as forbidden provenance. The generic fix checks forbidden field names and secret shapes while
   permitting ordinary language; a regression covers both acceptance and actual forbidden keys.
   The manager reviewed and committed this before final candidate generation.
2. The copied hosted smoke configuration still declared an old dirty-development policy. Clean
   preflight rejected it before a provider call. A fresh unique hosted configuration set
   `allow_dirty_tracked: false` and removed the obsolete diff hash; the 40 ordered cases remained
   identical to Arm A.
3. Windows transient sharing violations interrupted judge/report atomic finalization after complete
   writes. A bounded generic retry for WinError 5/32 and a fail-once regression were manager-reviewed
   and committed as `3580d6d`. Candidate packages and their original generation commit were not
   changed.
4. One Arm A judge result was schema-invalid twice. The baseline and first retry remain immutable;
   the second append-only retry completed. Final current accounting is 21/21 with zero failures.

No defect changed prompts, schemas, references, model profiles, generation policy, judge rubric, or
candidate output.

## 16. Files changed

After the manager committed the generic scoring fix, no source code was changed by the resumed
executor. The only unstaged/uncommitted delivery change is this completion report. All private
configs, bundles, packages, raw outputs, judge attempts, metrics, and diagnostic logs remain ignored.

## 17. Repository validation

- `poetry env info --path`: repository `.venv`.
- `poetry run pytest tests/test_bench.py -q`: passed (real-provider test remains opt-in).
- `poetry run pytest`: **431 passed, 1 skipped** in 92.24 seconds.
- `poetry run ruff check .`: passed.
- `poetry check`: passed.
- `bench prepare/generate/verify/score --help`: passed.
- `chronicle --help`: passed.
- `git diff --check`: passed before report creation.
- `git diff --cached --name-only`: empty.
- Both required cache-only CLI commands: exit zero.

## 18. Immutability, privacy, and tracking evidence

- Live database hash: unchanged from Phase 0.
- Frozen database and private snapshot-manifest hashes: unchanged from Phase 0.
- Frozen snapshot integrity/schema/count contract remained valid; no WAL/SHM sidecars appeared.
- Both final candidate ZIP hashes match the identities recorded before judging and before the
  scoring fix.
- Both accepted historical two-conversation package hashes remain unchanged.
- Package verification and deterministic scoring independently reconstructed the accepted frozen
  inputs, selection, task catalogs, schemas, and references without mismatch.
- Both cache-only replays preserved judge attempt counts and aggregate hashes.
- Git tracks zero private-evaluation, database, SQLite, or ZIP artifacts.
- No credential, token, project/account ID, transcript, private path, case fingerprint, candidate
  output, FABLE output, or judge rationale appears in this report.

## 19. Limitations and WP-5.2A5 recommendation

Ten conversations are insufficient for statistical, leaderboard, stable latency, cost, or
publication claims. FABLE is silver development reference data; the Pro preview is an automated
judge whose alias may drift. The candidates also differ in execution environment, and token totals
are not directly comparable because local usage was unavailable for six context-limit failures.

Proceed to WP-5.2A5 qualification with the same immutable contracts and explicit provider controls.
The local 120-case projection is operationally practical on this observed run, but the qualification
decision should account for the 52.5% local schema-valid rate and six context-limit outcomes, not
wall time alone. Retain rubric v1 for cross-candidate comparability unless a separately versioned
calibration package is approved and rerun for every candidate.

## 20. Acceptance checklist

- [x] Both arms selected the same frozen first 10 conversations.
- [x] Both arms proved the same ordered 40-case identity.
- [x] Arm A has 40 terminal outcomes and zero unaccounted cases.
- [x] Arm B has 40 terminal outcomes and zero unaccounted cases.
- [x] Both immutable packages pass local verification.
- [x] Deterministic scoring completed for both packages.
- [x] Every schema-valid output has a current terminal Pro-judge score.
- [x] Every invalid output is counted and skipped from semantic judging.
- [x] No eligible judge case is unaccounted.
- [x] Both cache-only CLI reruns exit zero with zero provider calls.
- [x] Local wall time and the 120-case linear planning estimate are recorded.
- [x] Complete private metrics and a privacy-safe comparison exist.
- [x] Required focused and full repository validation passed.
- [x] Live/frozen data and accepted historical packages remain unchanged.
- [x] No private evaluation or credential artifact is tracked.
- [x] This report maps evidence to every criterion.
- [x] Delivery changes remain unstaged and uncommitted for PM validation.
