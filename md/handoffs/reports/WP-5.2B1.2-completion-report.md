# WP-5.2B1.2 Completion Report

## 1. Status

**Ready for PM validation.** The bounded two-conversation, eight-case comparison completed for
both arms. This is an operational smoke and directional observation, not evidence of statistical
superiority.

## 2. Owner-confirmed models and region

- Candidate: `vertex_ai/gemini-3.5-flash` in `global`.
- Judge: `vertex_ai/gemini-3.1-pro-preview` in `global`.
- The requested `vertex_ai/gemini-3.5-pro` returned account-level unavailability. The owner
  explicitly selected the documented Pro preview. No fallback occurred.

No project, account, credential, token, or private endpoint identity is recorded here.

## 3. Scope and fingerprint equality

Both arms used `dev-v1`, `frozen-prefix-v1`, `conversation-limit=2`, four tasks per conversation,
and eight cases. Both verified the same privacy-safe frozen-prefix identity:
`407a90c2f38aa5fe66c9c495fdacbe229cf364a8b902cc9d8ca7a935111a46fe`.
Case ordering and all eight case fingerprints matched local authority. The immutable Arm A package
content ID remained `cab0da8d98a4cb7085b255327ee7ad0ea9cca73dec584fe63a4ac6d53934747f`.

## 4. Files changed

- `bench/models.py`: added strict, mutually exclusive `local-artifact` and `hosted-api` candidate
  provenance, plus attempt retry accounting.
- `bench/config.py`: validates candidate execution locality against the selected profile.
- `bench/__main__.py`: added explicit remote/private authorization controls to candidate generation.
- `bench/core.py`: preserves legacy local identity, skips artifact checks only for hosted candidates,
  propagates configured reasoning controls, records hosted-safe LiteLLM/runtime provenance, and
  safely recovers an interrupted post-judge manifest finalization.
- `bench/ai-models.evaluation.default.yaml`: added a provider-generic hosted profile example.
- `bench/ai-models.evaluation.default.yaml`: also pins the primary `gemini-judge` profile to
  `vertex_ai/gemini-3.1-pro-preview`; Gemini 2.5 Flash is not a tracked default.
- `bench/evaluation.default.yaml`: pins rubric v1, temperature 0, and the validated 1,000-token
  primary Pro judge cap.
- `tests/test_bench.py`: added hosted provenance, authorization, package, reasoning propagation,
  opt-in Vertex synthetic-gate, local compatibility, and interrupted-finalization regression tests.
- `README.md`: restored the complete accepted `d0736cc` content, then added a concise hosted
  candidate authorization and identity note to the existing evaluation section.
- `docs/development-evaluation.md`: documented provider-generic hosted provenance/configuration,
  disclosure, generation gates, verification, independent candidate/judge caches, unique paths,
  cache-only replay, preview drift, and the future `bench compare` consideration.
- This completion report.

The supplied updated handoff remains untracked. README reconciliation was intentionally limited to
that file: its erroneous reverse diff was removed before the hosted documentation was added.

## 5. Hosted-candidate architecture and provenance

Candidate execution is structural rather than inferred from fake artifact fields. Existing configs
default to `local-artifact`; their serialized candidate identity deliberately omits the new default,
so accepted local bundles and packages remain verifiable. Hosted configs select `hosted-api` and
must omit artifact hash/file/path, quantization, local runtime, device, and repository fields.
Mixed configurations fail strict Pydantic validation.

Hosted generation requires both `--allow-remote` and `--confirm-private-eval` before bundle reads or
provider execution. Package provenance records profile and resolved provider/model identities,
application commit/diff identity, task generation settings, request/attempt identity, timings,
usage, retry/failure state, and LiteLLM version. Candidate and judge identities/caches remain
separate. The implementation contains no Gemini branch: another hosted LiteLLM profile can use the
same path without a new benchmark adapter.

Replacement required generic code changes because the accepted harness rejected remote candidate
profiles and required GGUF/LM Studio provenance. After those changes, selecting a hosted provider
is configuration-only. The accepted local Llama generation path and package identity are unchanged.

## 6. Synthetic gates

- ADC and environment checks passed without displaying secrets or identifiers.
- Synthetic availability resolved the candidate and selected judge in `global`.
- All four candidate task contracts reached terminal states against Gemini 3.5 Flash. A diagnostic
  run produced two schema-valid outputs and two preserved invalid-JSON outputs; these were treated
  as model evidence, not repaired or retried.
- All four judge rubrics completed against schema-valid synthetic data with the selected Pro judge.
- The synthetic judge cache-only replay completed with zero provider calls.
- A generic defect was found: candidate generation recorded but did not forward
  `reasoning_effort`. The fix is covered by a request-propagation regression test.

## 7. Arm A accounting and cache proof

- Candidate: 8 terminal; 6 schema-valid; 2 schema-invalid; 0 infrastructure-unaccounted.
- Deterministic scoring: 6 evidence-valid and cross-field-valid; 2 `no_valid_output`.
- Judge: 6 eligible, 6 completed, 0 failed, 2 invalid skipped.
- The first 500-token Pro diagnostic ended 2/6 responses at `finish_reason=length` because reasoning
  consumed the shared completion cap. A fresh directory used a 1,000-token judge cap.
- The 1,000-token cache-only rerun returned identical metrics and made zero calls.

## 8. Arm B accounting and cache proof

- Candidate: 8 terminal; **8/8 schema-valid**; 0 invalid; 0 failed.
- Deterministic scoring: 8 evidence-valid and cross-field-valid.
- Judge: 8 eligible, 8 completed, 0 failed, 0 skipped.
- The first CLI finalization was interrupted after all eight attempts and metrics were written. The
  recovery fix verified scope, eligibility, attempt count, and case-score count before repairing the
  manifest/report. Its regression test proves recovery without a provider call.
- The cache-only rerun returned identical metrics and made zero calls.

## 9. Privacy-safe comparison

| Measure | Arm A: Llama 3.2 1B Q4_K_M | Arm B: Gemini 3.5 Flash |
|---|---:|---:|
| Candidate provider | LM Studio/local | Vertex AI/hosted |
| Judge | Vertex `gemini-3.1-pro-preview` | Same |
| Cases / fingerprint match | 8 / yes | 8 / yes |
| Valid / invalid / infrastructure-failed | 6 / 2 / 0 | 8 / 0 / 0 |
| Schema-valid rate | 75% | 100% |
| By task: summary / mode / activity / title | 100% / 100% / 50% / 50% | 100% / 100% / 100% / 100% |
| Evidence-valid / cross-field-valid | 6 / 6 | 8 / 8 |
| Summary date / length valid | 2 / 2 | 2 / 2 |
| Work-mode exact agreement | 0% | 100% |
| Last-activity exact agreement | 0% | 100% |
| Title-fit exact agreement | 0% | 100% |
| Candidate wall time | 50.517 s | 85.103 s |
| Candidate latency p50 / p95 | 5.858 / 6.686 s | 11.000 / 14.172 s |
| Prompt / completion / total tokens | 6,167 / 652 / 6,819 | 8,502 / 765 / 9,267 |
| Reasoning tokens | reported as 0 | not separately reported |
| Provider retries / rate-limit failures | 0 / 0 | 0 / 0 |
| Judge eligible / completed / failed / skipped | 6 / 6 / 0 / 2 | 8 / 8 / 0 / 0 |
| Cache-only provider calls | 0 | 0 |

Per-task candidate latency p50/p95 in milliseconds: Arm A summary 3546/3546, mode 4391/4391,
activity 5858/5858, title 4483/4483; Arm B summary 8202/8202, mode 10641/10641,
activity 1828/1828, title 14172/14172. With two observations per task, these percentiles are
descriptive only.

Judge dimension means were all `4.0` for Arm B. Arm A means were: summary—factual consistency 4.0,
material coverage 2.5, concise usefulness 2.5, conversation characterization 1.0, unsupported-claim
avoidance 4.0; mode—0.0 on all four dimensions; activity—blocker correctness 4.0,
final activity 1.0, status 0.0, next action 0.0, not-copying 0.0, unsupported-claim avoidance 4.0;
title—dominant activity 0.0, title-fit correctness 0.0, suggestion compliance/usefulness 4.0,
unsupported-claim avoidance 4.0.

The work-mode confusion result was two FABLE `one_off` cases mapped to Llama `mixed`, versus two
mapped to Gemini `one_off`. Last activity and title fit similarly had zero exact matches for Arm A
and two of two for Arm B. These are directional observations over two conversations.

The only provider-required policy difference from the older 2.5 Flash history was a shared
1,000-token Pro judge cap; both comparison arms used it. Candidate prompts, task limits, schemas,
finalizers, temperature, selection, and order were unchanged.

## 10. Defects and regression tests

1. Remote candidates were structurally rejected and forced to claim local artifact provenance.
   Fixed with generic execution/provenance variants and locality validation.
2. Candidate `reasoning_effort` was omitted from requests. Fixed by propagating the configured
   value; regression asserts every hosted request receives it.
3. A completed judge run could leave `metrics.json` behind a deterministic-only manifest after an
   interrupted filesystem finalization. Fixed with strictly reconciled, no-call recovery and a
   regression test.
4. The initial Arm B config used an incorrectly inferred full commit SHA. Preflight rejected it
   before provider execution; the exact measured commit was pinned and a new unique bundle used.

## 11. Retained model-output failures

Arm A's original evidence-validation and schema-validation failures remain unchanged and excluded
from judging. Synthetic Gemini invalid JSON remains diagnostic evidence. No output was repaired,
removed, semantically retried, or regenerated with a different request.

## 12. Validation

The tracked-template policy regression passed and resolves the primary profile to Pro Preview with
rubric v1, temperature 0, `reasoning_effort: none`, and a 1,000-token cap. Final validation:

- `poetry env info --path`: repository `.venv`;
- `poetry run pytest`: **429 passed, 1 skipped** in 117.11 seconds under current machine load;
- `poetry run ruff check .`: passed;
- `poetry check`: passed;
- benchmark generate/score and Chronicle help commands: passed and exposed the expected flags;
- `git diff --check`: passed;
- `git diff --cached --name-only`: empty;
- `git diff d0736cc -- README.md` showed only the intentional 16-line hosted-candidate addition;
  the accepted quick start, status, AI-task, evaluation/cache, and Limitations content was restored;
- final status contained the unstaged implementation, templates, documentation, tests, and report,
  plus concurrent PM-owned handoff/validation-review/master-plan/development-ledger changes. The
  executor did not modify PM status records and preserved their `Rework required` state.

## 13. No-change, privacy, and tracking evidence

- Immutable Llama ZIP SHA-256: `dd2d7138df4ed1c3083ecffec5129abe030298ffdc2147af18bd9230d6564716`;
  package verification retained its accepted content ID and 6/2 accounting.
- Frozen DB SHA-256 remained
  `40a33ee09f3f6cbd5bc455c8bfb14989a80c3fa0e0689249d3fd86f962bc2458`, matching both hashes in its
  pre-existing private snapshot manifest.
- Live DB post-run SHA-256 was
  `f9da179524ee8825bf5517cb611bc8437833f5db1bfbd38ce9dbe53bbf658f8f`; benchmark paths never target
  either DB and source/reference verification remained unchanged.
- The accepted Gemini 2.5 Arm A judge run was reused read-only for sensitivity analysis and never
  targeted for writes; new Arm B and Pro runs used distinct scoring paths. Its unchanged hash was
  `bc95ca2938bae6838984d75d0bbb882c177323e69d2508c57f3761410c94e571`.
- Rework pre/post identities matched for the Gemini candidate ZIP
  (`89ad9558b455f8f76f8be61a84614027064c1abe401902e0e4babd418c6d924e`), the Pro Arm A run
  (`f3a6892e587916cd2e4271eba4a108f751ec0322eca0445d1c91ab8910c9a5be`), and the Pro Arm B run
  (`85e8c368e4aca76bda34ef523376cb0852368eefec9cc357ef49be64a2b99a6d`).
- Final database hashes remained identical to the initial delivery evidence: frozen
  `40a33ee09f3f6cbd5bc455c8bfb14989a80c3fa0e0689249d3fd86f962bc2458`; live
  `f9da179524ee8825bf5517cb611bc8437833f5db1bfbd38ce9dbe53bbf658f8f`.
- All configs, bundles, packages, attempts, caches, outputs, and private reports are below ignored
  `.chronicle/`. No credentials, tokens, project IDs, private paths, transcripts, titles, outputs,
  references, or rationales are tracked in this report.

## 14. Limitations and recommendation

Two conversations cannot establish statistical superiority, stable latency, or production cost.
Gemini was slower and used more tokens in this smoke while producing stronger reliability,
deterministic agreement, and Pro scores. Before the 120-case evaluation, retain the generic hosted
path, 1,000-token Pro policy, explicit authorization, immutable packages, and cache-only proof;
then estimate cost and concurrency from a somewhat larger bounded pilot before launching all 120.

The primary judge is the preview alias `gemini-3.1-pro-preview`; a fixed model string does not
guarantee immutable provider weights. The two primary runs used LiteLLM `1.83.0`, `global`, rubric
v1, provider schema v3, application schema v1, request construction v2, response normalizer v1,
temperature 0, and a 1,000-token cap. The privacy-safe combined judge-profile/policy hash is
`cbcc18f856c17e6ee06bb14a6a664be7d5b01ffcb404c26fbdcac401c0638f49`; their UTC manifest windows
were 2026-07-22 11:05–11:07 and 11:12–11:20. Future candidate comparisons should run in a bounded
time window or repeat a fixed anchor package if the preview endpoint changes.

Before the 120-case run, the owner should explicitly decide whether to retain rubric v1 or schedule
a separate judge-calibration package. Any later prompt, rubric, anchor, schema-semantics, evidence,
or interpretation change must receive a new version/cache identity and be rerun across every
candidate; this rework intentionally leaves rubric v1 unchanged.

## Rework addendum: documentation and judge sensitivity

The PM addendum was completed without regenerating either candidate. README now retains the
accepted quick-start `scan-local`/`stats` guidance, post-v0.1.0 status, four AI-task descriptions,
evaluation section, cached-judge instructions, and has no stray duplicate heading near
Limitations. The detailed runbook uses only provider-generic examples and contains no private
corpus values.

Arm B was additionally judged by `vertex_ai/gemini-2.5-flash` in `global`, using the immutable
Gemini candidate package, rubric v1, the same schema/application contracts, temperature 0, and the
accepted 500-token policy. Accounting was 8 eligible, 8 completed, 0 failed, 0 skipped; all eight
responses ended with `stop`, all judge outputs were schema-valid, and there were zero retries. The
cache-only replay completed locally with exit code zero and identical metrics. It retained eight
attempts, attempt aggregate SHA-256
`7079d4e3bdf1a7d7ec12baf25ccb8d4acb43ede2265e8df292e37f12b2eea923`, and exactly one judge section.
The owner-side CLI twice encountered the known transient Windows atomic-file replacement error
after complete cache/metrics writes; the successful cache-only replay could not call a provider.

### Judge sensitivity

This matrix is diagnostic and separate from the primary Pro-judged candidate comparison.

| Candidate | Gemini 2.5 Flash judge | Gemini 3.1 Pro judge |
|---|---:|---:|
| Llama 3.2 1B | 6/6 completed, 0 failed, 2 skipped | 6/6 completed, 0 failed, 2 skipped |
| Gemini 3.5 Flash | 8/8 completed, 0 failed, 0 skipped | 8/8 completed, 0 failed, 0 skipped |

All four cells had 100% judge-schema validity among eligible cases, only `stop` finishes, and zero
retries. Runtime/usage comparison:

| Candidate / judge | p50 / p95 latency | Wall time | Prompt / completion / reasoning / total tokens | Cap |
|---|---:|---:|---:|---:|
| Llama / 2.5 Flash | 2.061 / 2.391 s | 19.708 s | 6,005 / 1,645 / unavailable / 7,650 | 500 |
| Llama / Pro | 3.813 / 5.375 s | 34.608 s | 9,062 / 2,295 / 854 / 11,357 | 1,000 |
| Gemini / 2.5 Flash | 2.031 / 2.405 s | 26.957 s | 9,115 / 2,105 / unavailable / 11,220 | 500 |
| Gemini / Pro | 3.656 / 3.875 s | 34.464 s | 13,263 / 2,001 / unavailable / 15,264 | 1,000 |

Gemini received `4.0` on every task dimension from both judges: exact score agreement 40/40, mean
absolute difference 0.0, with 2.5 higher/equal/lower counts 0/40/0. For Llama, exact agreement was
16/29, mean absolute difference 1.276, and 2.5 was higher/equal/lower on 12/16/1 dimensions. Task
means were:

- Llama summary, 2.5 vs Pro: factual 4/4, coverage 3.5/2.5, concise 3.5/2.5,
  characterization 4/1, unsupported avoidance 4/4.
- Llama work mode: label, distinction, and specificity 0/0; unsupported avoidance 4/0.
- Llama activity: blocker 4/4, final activity 4/1, status 4/0, next action 4/0,
  not-copying 4/0, unsupported avoidance 4/4.
- Llama title: dominant activity 0/0, title fit 0/0, compliance 4/4, usefulness 0/4,
  unsupported avoidance 4/4.
- Gemini: every dimension was 4/4 for every task.

Candidate ordering did not change: Gemini's comparable mean was 4.0 under both judges; Llama's was
2.690 under 2.5 Flash and 1.690 under Pro. Deterministic candidate metrics are judge-independent,
and the primary conclusions continue to use Pro consistently for both candidates. The 2.5 results
show sensitivity only. Without human adjudication, disagreement cannot establish which judge is
correct, and two conversations cannot establish stability or statistical significance.

## 15. Acceptance checklist

- [x] Owner selected exact candidate, judge, and `global` region.
- [x] Accepted commit/corpus/scope and immutable Llama package verified.
- [x] Local and hosted candidates are structurally exclusive and strictly validated.
- [x] Hosted generation requires both authorization flags before provider execution.
- [x] Portable hosted provenance contains no fake local fields or secrets.
- [x] Candidate/judge identities and caches are separate; judge changes do not regenerate candidates.
- [x] Synthetic four-task and four-rubric gates completed; judge cache replay made zero calls.
- [x] Arm A: 8 terminal, 6 valid, 2 invalid, 6 judged, 0 judge failures, 2 skipped.
- [x] Arm B: 8 terminal, 8 valid, 8 judged, 0 judge failures, 0 skipped.
- [x] Both packages verified and deterministic scoring completed on identical fingerprints.
- [x] Both cache-only judge reruns made zero calls.
- [x] All 16 arm/case positions reconcile.
- [x] Comparison keeps deterministic and semantic results separate and makes no significance claim.
- [x] Private artifacts remain ignored; accepted historical artifacts and DBs were not targeted.
- [x] README was restored to the accepted baseline and extended only with hosted-candidate guidance.
- [x] Provider-generic hosted workflow and preview drift are documented in the evaluation runbook.
- [x] Immutable Arm B was judged 8/8 by Gemini 2.5 Flash at the accepted 500-token policy.
- [x] Gemini 2.5 Arm B cache-only replay made zero calls and preserved eight attempt identities.
- [x] The separate 2×2 judge-sensitivity analysis reports agreement without treating it as truth.
- [x] Rubric v1 remains frozen; future calibration is explicitly deferred.
- [x] Both tracked templates default to Pro Preview/rubric-v1/temperature-0/1,000 tokens.
- [x] A regression fails if the primary defaults drift back to the diagnostic judge policy.
- [x] Changes are left unstaged and uncommitted for PM validation.
