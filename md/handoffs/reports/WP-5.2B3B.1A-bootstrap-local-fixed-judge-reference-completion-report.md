# WP-5.2B3B.1A Bootstrap local fixed-judge reference — completion report

**Date:** 2026-08-11

**Outcome:** Completed with cache-only replay; fixed-judge evidence does not show a Bootstrap improvement over P0

**Application commit:** `8a4aaf7af3761968a63575fa3b7a2a33925a2930`

## Executive summary

The immutable P0 and Bootstrap attempt `0003` validation evidence was retrieved
from the retained private network volume, verified locally, and judged with the
fixed `vertex_ai/gemini-3.1-pro-preview` profile in `global`.

Both arms had 32 terminal validation positions and exactly 11 schema-valid,
judge-eligible outputs. All 22 eligible outputs now have successful fixed-judge
results. The original authentication-failed private attempt remains append-only;
a fresh successful attempt was added for that case. There were no infrastructure
or semantic retries and no output repair. Cache-only replay verified all 22
terminal entries with zero provider calls and unchanged evidence bytes.

The semantic evidence does not show a Bootstrap improvement:

- paired case mean across the 10 jointly eligible positions: P0 `3.1600`,
  Bootstrap `3.1450`, difference `-0.0150`;
- paired dimension-level mean difference across 45 observations:
  Bootstrap minus P0 `-0.0889`;
- unpaired case mean across all 11 eligible outputs per arm: P0 `3.2364`,
  Bootstrap `3.2227`, difference `-0.0137`;
- unpaired dimension-weighted mean: P0 `3.2857` over 49 scores, Bootstrap
  `3.2200` over 50 scores, difference `-0.0657`.

Bootstrap scored better on work-mode classification but worse on title
assessment. Qwen remained near ceiling in both arms; the Phi subset was lower
for Bootstrap. These are descriptive results from a very small, validity-filtered
sample and are not statistically significant.

This optional reference measurement does not alter promotion. P0 remains the
selected GEPA starting package, and Bootstrap remains non-promotable under its
existing privacy and context-fit failures.

## Authorization and fixed route

The run stayed inside the accepted boundary:

- fixed judge: `vertex_ai/gemini-3.1-pro-preview`;
- Vertex location: `global`;
- local user Application Default Credentials;
- rubric version 1;
- temperature 0;
- maximum output tokens 1,000;
- reasoning policy `none`;
- timeout 180 seconds;
- concurrency 1;
- one bounded infrastructure retry available, none used;
- no semantic retry or output repair;
- US$10 hard Vertex ceiling.

The successful credential route was derived from `CLOUDSDK_CONFIG` and set
before importing Google auth, LiteLLM, or judge modules. The credential path,
account identity, project value, credential contents, and access tokens were
never printed or written to tracked evidence.

## Artifact provenance and retrieval

The returned validation-only archive was verified before judging:

| Evidence | Result |
|---|---:|
| Archive bytes | 1,002,949 |
| Archive SHA-256 | `73e698e8fba47b02a62519dcbf3b62586cd6d5cad3fcd9181e59d6b98f6811d3` |
| Internally indexed artifacts | 130 |
| Internal hash failures | 0 |
| Selected candidate provider records | 82 |
| Frozen validation conversations | 4 |
| Training input/reference files opened | 0 |
| Holdout files opened | 0 |

Retrieval-only RunPod compute cost was approximately US$0.17334. Compute was
stopped after local verification, ongoing GPU spend is US$0/hour, and the
retained private network volume remains intact. Provider resource identifiers
remain only in ignored private operator evidence.

P0, Bootstrap candidate/result identities, attempt `0003`, attempts `0001` and
`0002`, the accepted P0 checkpoint, restart evidence, and optimizer state were
hash-verified. Candidate outputs remained byte-identical and were not normalized,
repaired, truncated, or regenerated.

## Scope reconciliation

| Scope | P0 | Bootstrap attempt `0003` |
|---|---:|---:|
| Terminal positions | 32 | 32 |
| Schema-valid / judge eligible | 11 | 11 |
| Schema-invalid / not disclosed | 21 | 21 |
| Judge completed | 11 | 11 |
| Judge failed at final state | 0 | 0 |
| Judge unattempted | 0 | 0 |
| Candidate models | 2 | 2 |
| Accepted tasks represented among valid outputs | 2 | 2 |

Only valid outputs were disclosed. In both arms the eligible subset contained
title-assessment and work-mode-classification positions; conversation-summary
and last-activity outputs were schema-invalid and remained undisclosed. Ten
positions were valid in both arms; one eligible position per arm was not shared.

Every judged output was rebound to its arm, candidate/result identity, model,
task/schema, selected-input hash, original output hash, FABLE-reference hash,
and fixed-judge contract. Evidence IDs and conversation-summary date authority
were revalidated before request construction.

## Instrumented synthetic gate

The ignored synthetic recorder was repaired without changing tracked production
code or production judge behavior. It records these terminal boundaries
separately:

1. request construction;
2. provider invocation;
3. provider response returned;
4. response-content extraction;
5. empty response;
6. JSON parsing;
7. Pydantic/schema validation;
8. judge-contract validation;
9. successful completion.

The recorder retains only safe phase/error metadata, finish and usage counters,
response presence, byte length and SHA-256, latency, and model/project hashes.
It never retains response text. Eight network-free injected tests passed,
covering provider exception, empty response, malformed JSON, schema-invalid JSON,
contract-invalid JSON, valid success, request-construction failure, and
content-extraction failure.

The one authorized instrumented request passed through
`successful_completion`:

| Probe evidence | Value |
|---|---:|
| Status / terminal phase | Success / `successful_completion` |
| Finish reason | `stop` |
| Provider attempts / retries | 1 / 0 |
| Input tokens | 774 |
| Output tokens | 199 |
| Reasoning tokens | 0 |
| Latency | 10,062 ms |
| Response bytes | 579 |
| Response SHA-256 | `07f7c448f7f821da042da4badd9ba3e4e851e4c78dfb72ac7ae0e159e17047b9` |
| Probe-record SHA-256 | `efd96942cc7771f59ee77e52d7e16309437ed8f68d38bc17ef769cbd7dae86b2` |

The response content remains ignored and private. Earlier authentication and
probe failures remain append-only and unchanged.

## Fixed-judge results

Scores use the accepted 0–4 rubric scale. Each cell shows `mean (n)`.

### Overall dimension means

| Dimension | P0 | Bootstrap |
|---|---:|---:|
| Dominant activity fit | 4.0000 (5) | 2.6667 (6) |
| Label support | 2.6667 (6) | 3.0000 (5) |
| Mode distinction | 2.6667 (6) | 3.0000 (5) |
| Reason specificity | 3.0000 (6) | 3.4000 (5) |
| Suggestion-only compliance | 4.0000 (5) | 4.0000 (6) |
| Suggestion usefulness | 3.4000 (5) | 2.6667 (6) |
| Title-fits correctness | 3.2000 (5) | 2.6667 (6) |
| Unsupported-claim avoidance | 3.4545 (11) | 3.8182 (11) |

### Dimension means by task

| Task / dimension | P0 | Bootstrap |
|---|---:|---:|
| Work mode — label support | 2.6667 (6) | 3.0000 (5) |
| Work mode — mode distinction | 2.6667 (6) | 3.0000 (5) |
| Work mode — reason specificity | 3.0000 (6) | 3.4000 (5) |
| Work mode — unsupported-claim avoidance | 3.0000 (6) | 3.6000 (5) |
| Title — dominant activity fit | 4.0000 (5) | 2.6667 (6) |
| Title — suggestion-only compliance | 4.0000 (5) | 4.0000 (6) |
| Title — suggestion usefulness | 3.4000 (5) | 2.6667 (6) |
| Title — title-fits correctness | 3.2000 (5) | 2.6667 (6) |
| Title — unsupported-claim avoidance | 4.0000 (5) | 4.0000 (6) |

Task-level case means summarize each output's rubric dimensions equally:

| Task | P0 | Bootstrap | Bootstrap − P0 |
|---|---:|---:|---:|
| Work-mode classification | 2.8333 (6) | 3.2500 (5) | +0.4167 |
| Title assessment | 3.7200 (5) | 3.2000 (6) | -0.5200 |

### Dimension means by candidate model

| Dimension | P0 Phi | P0 Qwen | Bootstrap Phi | Bootstrap Qwen |
|---|---:|---:|---:|---:|
| Dominant activity fit | 4.0000 (3) | 4.0000 (2) | 1.3333 (3) | 4.0000 (3) |
| Label support | 1.3333 (3) | 4.0000 (3) | 1.5000 (2) | 4.0000 (3) |
| Mode distinction | 1.3333 (3) | 4.0000 (3) | 1.5000 (2) | 4.0000 (3) |
| Reason specificity | 2.0000 (3) | 4.0000 (3) | 2.5000 (2) | 4.0000 (3) |
| Suggestion-only compliance | 4.0000 (3) | 4.0000 (2) | 4.0000 (3) | 4.0000 (3) |
| Suggestion usefulness | 3.0000 (3) | 4.0000 (2) | 1.3333 (3) | 4.0000 (3) |
| Title-fits correctness | 2.6667 (3) | 4.0000 (2) | 1.3333 (3) | 4.0000 (3) |
| Unsupported-claim avoidance | 3.0000 (6) | 4.0000 (5) | 3.8000 (5) | 3.8333 (6) |

Model-level case means:

| Model | P0 | Bootstrap | Bootstrap − P0 |
|---|---:|---:|---:|
| Phi-4 Mini | 2.6000 (6) | 2.3400 (5) | -0.2600 |
| Qwen3.5-4B | 4.0000 (5) | 3.9583 (6) | -0.0417 |

## Paired and unpaired comparison

### Paired

Ten validation positions were schema-valid in both arms.

| Paired measure | Result |
|---|---:|
| P0 case mean | 3.1600 |
| Bootstrap case mean | 3.1450 |
| Bootstrap − P0 case-mean difference | -0.0150 |
| Improved / equal / worse cases | 2 / 5 / 3 |
| Shared dimension observations | 45 |
| Bootstrap − P0 dimension-mean difference | -0.0889 |
| Improved / equal / worse dimensions | 8 / 31 / 6 |

### Unpaired

| Unpaired measure | P0 | Bootstrap | Difference |
|---|---:|---:|---:|
| Eligible cases | 11 | 11 | 0 |
| Case mean | 3.2364 | 3.2227 | -0.0137 |
| Dimension observations | 49 | 50 | +1 |
| Dimension-weighted mean | 3.2857 | 3.2200 | -0.0657 |
| Dimension-score sum | 161 | 161 | 0 |

The paired and unpaired directions agree: neither shows an aggregate Bootstrap
gain. Equal total dimension points do not imply equality because the eligible
task mixture produced 49 P0 versus 50 Bootstrap dimension observations.

## Calls, latency, tokens, and cost

All 22 fresh private judge attempts finished with reason `stop`. The original
authentication failure is retained as a twelfth historical Bootstrap attempt,
so fixed-judge attempt files total 23.

| Successful arm accounting | P0 | Bootstrap |
|---|---:|---:|
| Successful calls | 11 | 11 |
| Infrastructure retries | 0 | 0 |
| Latency total | 40,387 ms | 48,872 ms |
| Latency p50 / p95 | 3,532 / 4,984 ms | 3,844 / 11,140 ms |
| Input tokens total | 38,868 | 36,684 |
| Input tokens p50 / p95 | 2,818 / 5,348 | 2,872 / 5,378 |
| Output/reasoning tokens total | 2,898 | 2,890 |
| Output/reasoning p50 / p95 | 260 / 281 | 265 / 281 |
| Usage-derived cost | US$0.112512 | US$0.108048 |

Including the successful instrumented probe, known measured usage is 76,326
input tokens and 5,987 output/reasoning tokens, for US$0.224496 at the accepted
standard rates. One earlier failed minimal probe did not retain usage. Even the
pre-call worst-case fixed-run bound of US$1.533132 plus all minimal probe caps
remained below US$1.54, safely inside the US$10 ceiling. Known usage leaves
US$9.775504 of that ceiling.

## Cache-only and immutability proof

Cache-only replay completed successfully:

| Proof | Value |
|---|---:|
| Cache entries verified | 22 |
| Additional provider calls | 0 |
| Judge evidence bytes unchanged | Yes |
| Cache evidence identity | `b55a6eb2e67f93013059c707fe8c0255209d4c29039c23000b7e8d2a7def8dd6` |
| Cache-proof SHA-256 | `71fa4856a4ee2b77f2d84f57c74b18261f4f9d81758cc579a9a38aa5606e3ab7` |
| Final judge-summary SHA-256 | `fc3b738ce8ebe3ca932627e673771f92e816c549f09cc980544dddd71ed575df` |

The returned archive, two frozen judge-input manifests, candidate packages,
candidate results, optimizer state, original provider records, P0 checkpoint,
and Bootstrap attempts remain unchanged. The original failed private judge
attempt remains byte-identical with SHA-256
`af47fdd462c5543fe05f1d3c0b617ac0f1a1e9f1d268579fff797327c4f83802`.

## Privacy and non-access evidence

- Training input files opened: 0.
- Training reference files opened: 0.
- Holdout files opened: 0.
- Candidate inference, P0 rerun, Bootstrap rerun, GEPA, and fixed-judge output
  repair: 0.
- RunPod activity during judging: 0.
- Raw selected text, FABLE references, candidate outputs, prompts, judge
  responses, and bounded rationales remain under ignored private storage.
- No credential, token, account identity, project value, private path,
  conversation identity, or RunPod resource identifier is tracked.
- `git ls-files .chronicle` is empty.

## Interpretation and limitations

The fixed judge agrees with the existing observation that Bootstrap did not
improve P0 at the aggregate level, but the evidence is weak and descriptive:

- only 11 of 32 terminal positions per arm were schema-valid;
- only 10 positions were eligible in both arms;
- invalid outputs were excluded rather than semantically judged;
- eligible task/model composition differs by one position per arm;
- the same rubric and judge model scored both arms;
- no confidence interval or significance claim is warranted;
- Qwen ceiling effects obscure small quality differences;
- this result cannot override deterministic privacy, context, or promotion
  gates.

## Promotion, checkpoint blocker, and next recommendation

This result does not affect prompt promotion. P0 remains the selected starting
package for GEPA. Bootstrap remains non-deployable and non-promotable because
its accepted context-fit and privacy failures remain authoritative. No judge
score or rationale may enter optimizer feedback.

The separate Bootstrap checkpoint-recovery blocker remains: the phase wrapper
compared the historical P0 application identity against the newer Bootstrap
configuration after the Bootstrap result was already durable. This task did not
weaken that authority check or create the missing canonical checkpoint.

The development manager should validate and commit this privacy-safe report
with its manager handoff, plan/ledger closure, and activity-evidence log. Before
GEPA, resolve the existing checkpoint/application-identity
recovery boundary through its own reviewed handoff. GEPA should then begin from
P0, not from Bootstrap, and only under the separate private-pilot proposer and
compute authorization.

## Validation and Git boundary

The ignored recorder received Ruff, formatting, byte-compilation, and eight
network-free injected tests. Final repository validation includes:

- `poetry run python -m bench score --help`;
- repository-wide Ruff;
- explicit Ruff and formatting checks for ignored operator runners;
- `poetry check`;
- `git diff --check` plus report-specific whitespace/privacy checks;
- `git diff --cached --name-only` empty;
- `git ls-files .chronicle` empty.

No focused or full tracked application test suite is required because no tracked
production code changed. `HEAD` remains
`8a4aaf7af3761968a63575fa3b7a2a33925a2930`; the manager handoff and this report
remain untracked, unstaged, and uncommitted.
