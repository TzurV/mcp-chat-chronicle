# WP-5.2B2.2 - Three Retained Candidate Complete Arms

## Status

Ready for execution after:

1. the manager commits this handoff and the accepted WP-5.2B2.1 documentation;
2. the tracked checkout is clean;
3. the owner sends the single Vertex disclosure authorization in this handoff to the executor.

## Executor recommendation

Continue in the same executor thread that completed WP-5.2A5.1 and WP-5.2B2.1. That thread already
has the accepted model artifacts, private provenance, LM Studio identifiers, frozen inputs, package
locations, judge configuration, Vertex routing diagnosis, and checkpoint evidence.

Starting a new executor thread would require a detailed private-artifact transfer and would add
setup risk without improving evaluation independence.

## Executor role and commit ownership

Act as the implementation/evaluation executor.

Read `md/agent-operating-notes.md` before starting. In particular:

- verify Poetry resolves to this repository's `.venv`;
- avoid piped and parallel PowerShell reads on this Windows sandbox;
- use the accepted real-data development policy;
- leave every delivery change unstaged and uncommitted.

The executor must not run `git add`, `git commit`, amend, rebase, or otherwise rewrite repository
history. The manager validates the completion report and commits only after an explicit owner
request.

Executor delivery status is `Ready for PM validation`, never `Accepted`.

## Objective

Create complete, independently generated 120-case development arms for:

1. Phi-4 Mini Instruct;
2. Llama 3.2 3B Instruct;
3. Gemma 3 4B IT.

Each arm uses all 30 frozen development conversations and the four accepted AI tasks:

1. `conversation-summary`;
2. `work-mode-classification`;
3. `last-activity`;
4. `title-assessment`.

The total candidate workload is:

```text
3 candidates x 30 conversations x 4 tasks = 360 candidate positions
```

For each arm:

- generate locally through the accepted LM Studio/LiteLLM path;
- preserve every valid output and every explicit failure;
- create and verify a new immutable complete-arm package;
- compute deterministic metrics;
- fixed-Pro judge every schema-valid output;
- prove a zero-call cache-only judge replay;
- report privacy-safe, article-ready aggregate evidence.

This is the final complete-scope development run before LP-4.1 analysis is finalized. It is not an
untouched scientific evaluation set.

## PM admission decision

WP-5.2B2.1 is accepted.

Checkpoint results:

| Candidate | Schema-valid | Fixed-Pro completed | Admission |
|---|---:|---:|---|
| Phi-4 Mini | 26/40 | 26/26 eligible | Complete 120-case arm |
| Llama 3.2 3B | 26/40 | 26/26 eligible | Complete 120-case arm |
| Gemma 3 4B | 23/40 | 22/23 eligible | Complete as weak research comparator |

Gemma's admission is for comparative learning and article completeness. It is not a
product-quality endorsement. Its low reliability and any additional complete-arm failures must
remain visible.

## Accepted foundations

Read and preserve:

- `md/master-plan.md`;
- `md/development-ledger.md`;
- `md/agent-operating-notes.md`;
- `docs/development-evaluation.md`;
- `md/handoffs/WP-5.2A5.1-remaining-lm-studio-candidate-qualification.md`;
- `md/handoffs/reports/WP-5.2A5.1-completion-report.md`;
- `md/handoffs/reports/WP-5.2A5.1-validation-review.md`;
- `md/handoffs/WP-5.2B2.1-three-qualified-candidate-40-case-checkpoint.md`;
- `md/handoffs/reports/WP-5.2B2.1-completion-report.md`;
- `md/handoffs/reports/WP-5.2B2.1-validation-review.md`;
- accepted WP-5.2B1 through WP-5.2B1.4 handoffs, reports, and reviews;
- private accepted manifests/configurations under `.chronicle/eval/dev-v1/`.

Accepted complete-arm historical context:

| Candidate | Scope | Schema-valid |
|---|---:|---:|
| Gemini 3.5 Flash cloud control | 120 | 112/120 |
| Qwen3.5-4B local control | 120 | 84/120 |
| Llama 3.2 1B local floor | 120 | 57/120 |

The separate accepted Qwen checkpoint is 34/40. The three accepted WP-5.2B2.1 checkpoint packages
remain immutable historical evidence.

## Full-arm package policy

Create three new complete-arm scopes and generate all 120 positions independently for each model.

Do not:

- mutate or extend a checkpoint package in place;
- copy checkpoint attempt files into a complete-arm package;
- implement package-merging or promotion code;
- treat checkpoint outputs as the first 40 complete-arm outputs;
- repackage any historical run.

This deliberately repeats the first 40 local candidate calls. The tradeoff is accepted because it:

- keeps checkpoint evidence immutable;
- avoids new merge semantics and harness code;
- produces coherent complete-arm run windows and wall-time measurements;
- matches the independent complete-arm method used for the accepted baseline candidates.

The executor may use the checkpoint only for preflight comparison and expected-runtime planning.

## Frozen comparison contract

Use exactly:

- the accepted frozen 30-conversation selection;
- 120 ordered cases per candidate;
- the same ordered case identities as accepted Gemini-120, Qwen-120, and Llama-120;
- the accepted task order;
- accepted selectors, prompts, schemas, finalizers, evidence policy, task versions, FABLE silver
  references, and task-owned output limits;
- configured context 8,192;
- temperature 0;
- candidate retries 0;
- concurrency/parallelism 1;
- strict structured output;
- local candidate generation only;
- fixed primary judge `vertex_ai/gemini-3.1-pro-preview`;
- judge location `global`;
- ADC authentication;
- judge rubric version 1;
- judge temperature 0;
- judge maximum output tokens 1,000;
- judge reasoning policy `none`;
- deterministic and semantic metrics reported separately.

Do not change prompts, add examples, tune schemas, expand context, alter output limits, repair
responses, use another runtime, or change quantization. Advertised model context is provenance
only.

## Candidate identities

Use the exact privately pinned and accepted WP-5.2A5.1 Q4_K_M artifacts.

### Phi-4 Mini

- official lineage: `microsoft/Phi-4-mini-instruct`;
- accepted LM Studio Community Q4_K_M artifact, revision, size, and SHA-256;
- accepted LM Studio identifier;
- context 8,192 and parallelism 1.

### Llama 3.2 3B

- official lineage: `meta-llama/Llama-3.2-3B-Instruct`;
- accepted LM Studio Community Q4_K_M artifact, revision, size, and SHA-256;
- accepted owner-controlled Llama license/access record;
- accepted LM Studio identifier;
- context 8,192 and parallelism 1.

### Gemma 3 4B

- official lineage: `google/gemma-3-4b-it`;
- accepted LM Studio Community Q4_K_M artifact, revision, size, and SHA-256;
- accepted owner-controlled Gemma license/access record;
- accepted LM Studio identifier;
- context 8,192 and parallelism 1.

Gemma 4 E2B remains excluded. Do not load, probe, retry, or substitute it.

Before each arm, independently verify the accepted artifact size/hash, loaded identifier,
runtime/engine, context, parallelism, and hardware class. Keep exact hashes and private paths in
ignored private provenance only.

## External disclosure authorization

Candidate generation is local.

Fixed-Pro judging sends the selected private source, schema-valid candidate result, and
corresponding FABLE silver reference to Vertex AI. WP-5.2B2.1 authorization does not cover these
three new complete arms.

The owner must send this exact or substantively equivalent statement once before judging:

> I authorize fixed-Pro judging for WP-5.2B2.2. You may send the selected 30 private conversation
> inputs, each schema-valid Phi-4 Mini, Llama 3.2 3B, and Gemma 3 4B complete-arm candidate result,
> and the corresponding FABLE silver reference to Vertex AI
> `gemini-3.1-pro-preview` in `global`, for up to 360 baseline judge cases plus one configured
> bounded retry for each failed eligible case. Use ADC and the existing rubric-v1 judge
> configuration. I approve the ordinary Vertex usage cost. Do not ask again for ADC refresh,
> setting the accepted Vertex location aliases to `global`, resumable continuation, the configured
> bounded retry, or cache-only replay inside this exact scope. Ask again only if provider, model,
> region, project, authentication route, source scope, case count, disclosed fields, rubric, or
> retry policy would change.

This authorization does not permit:

- another provider or Gemini API-key route;
- a different Vertex project;
- a substitute judge;
- another region;
- unbounded retries;
- candidate regeneration through Vertex;
- prompt/rubric/schema changes;
- disclosure of conversations outside the frozen 30.

Never print credentials, tokens, cloud project/account identity, raw source, candidate output,
FABLE reference, judge rationale, private IDs, or private paths in chat or tracked files.

## Vertex route preflight

The accepted WP-5.2B2.1 diagnosis found that absent local location aliases prevented the
application-owned judge route from using `global`.

Before private judging:

1. confirm ADC works without printing token or identity values;
2. confirm project variables are present without printing values;
3. set both accepted location aliases to `global`:

```powershell
$env:GOOGLE_CLOUD_LOCATION = "global"
$env:VERTEXAI_LOCATION = "global"
```

4. run one synthetic application-owned structured judge request;
5. require provider schema, application schema, model identity, and evidence membership to pass;
6. only then start private judge calls.

Do not rely on publisher-model metadata GET alone for this preview alias; the accepted diagnosis
showed that an explicit-global generation request is the meaningful route probe.

If the exact synthetic route fails, use at most one bounded diagnostic cycle within the same
provider/model/region/ADC contract. Do not start private calls until it passes. Do not substitute a
judge.

## Execution order

Run one local model at a time:

1. Phi-4 Mini complete arm;
2. Llama 3.2 3B complete arm;
3. Gemma 3 4B complete arm.

For each arm, finish generation, immutable packaging, verification, and deterministic scoring
before unloading the model and moving to the next arm.

After all three packages verify, run fixed-Pro judging and cache-only replay one package at a time.

The executor may run this as a resumable overnight workflow. Do not run multiple local candidates
concurrently.

## Stage 0 - Preflight and immutable baselines

1. Require a clean tracked checkout and record full HEAD.
2. Prove `poetry env info --path` resolves to this repository's `.venv`.
3. Validate the frozen snapshot manifest, database hash/integrity/schema, 711 conversations,
   28,370 messages, and absence of required WAL/SHM sidecars.
4. Hash live/frozen databases and all accepted complete/checkpoint packages and judge attempts.
5. Validate all 30 inputs, 120 FABLE references, ordered selection, and task-catalog identities.
6. Independently reconstruct the complete ordered 120-case identity.
7. Prove it matches accepted Gemini-120, Qwen-120, and Llama-120.
8. Prove its first 40 match accepted WP-5.2B2.1 and Qwen-40 identities.
9. Recheck all three accepted model artifact/runtime identities.
10. Create unique ignored config, bundle, work, package, score, judge-cache, and log paths.
11. Prove no new path overlaps a checkpoint, baseline, or historical arm.
12. Confirm disk space, AC power, sleep policy, LM Studio readiness, and single-worker execution.
13. Estimate runtime from the accepted checkpoint without presenting it as a measured full-arm
    result.
14. Dry-run/no-provider validate every prepared command.

Stop before generation if any identity, immutability, package-path, artifact, or runtime check
fails.

## Stage 1 - Phi-4 Mini 120

1. Load only the accepted Phi artifact.
2. Verify loaded identifier, artifact identity, runtime, context 8,192, and parallelism 1.
3. Prepare the new complete 120-case bundle.
4. Generate all 120 candidate cases locally with retries 0.
5. Require 120 terminal positions and zero unaccounted.
6. Preserve invalid JSON/schema/evidence/cross-field/context/timeout outcomes as failures.
7. Package immutably.
8. Verify the package.
9. Score deterministically.
10. Record wall span, summed latency, overall/per-task p50/p95, usage, failures, and validity.

## Stage 2 - Llama 3.2 3B 120

Repeat Stage 1 with the accepted Llama 3B artifact and a separate complete-arm identity.

Preserve semantically awkward but schema-valid output exactly. Do not repair or reinterpret it.

## Stage 3 - Gemma 3 4B 120

Repeat Stage 1 with the accepted Gemma 3 artifact and a separate complete-arm identity.

Do not alter thinking/reasoning controls, output limits, context, runtime, or prompt to improve its
checkpoint reliability. Poor reliability is part of the research result.

## Stage 4 - Fixed-Pro judging

After the owner authorization and successful synthetic route probe, judge every schema-valid
output in the three complete packages.

For each package require:

```text
eligible = schema-valid candidate outputs
completed + failed = eligible
skipped invalid = 120 - eligible
unaccounted = 0
```

Use candidate-blinded requests. Preserve terminal judge failures after the one configured bounded
retry. Never retry a valid semantic score because it differs from FABLE.

Do not rejudge Gemini, Qwen, Llama 1B, or any 40-case checkpoint package. Record the exact
judge-model/rubric identity and run window. Treat preview-model run-window drift as a limitation.

## Stage 5 - Cache-only proofs

For each arm run the identical judged configuration using:

```powershell
--with-judge --allow-remote --confirm-private-eval --judge-cache-only
```

Each replay must:

- exit zero;
- make zero provider calls;
- preserve candidate package, candidate attempts, judge attempts, judge outputs, and aggregate
  hashes;
- retain one coherent deterministic and judge report;
- fail before provider execution if an expected cache entry is missing.

## Stage 6 - Complete comparison evidence

For each new complete arm report:

- 120 terminal positions and schema-valid rate;
- validity and failure counts by task and boundary;
- evidence/date/cross-field/output-limit validity;
- full work-mode, last-activity, and title-fit confusion matrices;
- exact agreement and per-label precision/recall/support;
- fixed-Pro completed/failed/skipped accounting;
- judge dimension means by task with denominators;
- observed wall span and summed latency;
- overall and per-task p50/p95 latency;
- exact per-task usage availability and token totals;
- artifact, quantization, runtime, context, parallelism, and privacy-safe hardware provenance;
- cache-only proof.

Create a clearly labeled complete-scope comparison table containing:

- Gemini 3.5 Flash cloud control;
- Qwen3.5-4B local control;
- Llama 3.2 1B local floor;
- Phi-4 Mini;
- Llama 3.2 3B;
- Gemma 3 4B.

Separate:

- candidate reliability;
- deterministic agreement;
- judge quality;
- latency/runtime;
- resource and token evidence.

Do not compute or publish a new composite score in this work package. LP-4.1 owns composite-score
reproduction, sensitivity analysis, narrative, and publication metric selection.

Do not describe the complete development corpus as statistically representative or independent.

## Failure and fix policy

Candidate model-quality outcomes are final evidence:

- invalid JSON/schema/evidence/cross-field output;
- context-length or timeout at the fixed settings;
- refusal or empty response;
- awkward but schema-valid content;
- weak FABLE agreement;
- low judge score;
- slow local execution.

Do not repair, truncate, reinterpret, suppress, or retry candidate quality failures.

For a genuine generic harness, cache, serialization, atomic-write, resume, request-shape, or
diagnostic defect:

1. use at most two focused repair cycles;
2. add a synthetic regression;
3. run focused tests, full suite, Ruff, Poetry, and diff checks;
4. stop for manager review before continuing from changed tracked code;
5. preserve split provenance and all completed provider attempts;
6. never repeat successful candidate or judge calls unnecessarily.

Do not ask the owner to commit. Report the required manager action and wait.

Ask for PM/owner approval before changing model, artifact, quantization, runtime, context, task
contract, output limit, prompt, reference, judge, rubric, region, project, case scope, disclosed
fields, authentication route, retry semantics, or execution placement.

## Out of scope

- no prompt or few-shot tuning;
- no larger-context study;
- no new model qualification;
- no Gemma 4 operation;
- no Chrome Gemini Nano work;
- no remote local-model execution;
- no secondary judge;
- no judge-rubric revision;
- no FABLE reference revision;
- no composite-score implementation;
- no article drafting or graphic generation;
- no independent untouched evaluation set;
- no live/frozen database write;
- no commit or push.

## Completion report

Write exactly:

`md/handoffs/reports/WP-5.2B2.2-completion-report.md`

Required sections:

1. status and executive summary;
2. clean preflight and immutable baseline evidence;
3. complete 120-case identity reconciliation;
4. owner authorization and disclosure boundary;
5. common model/task/settings contract;
6. independent full-arm package policy;
7. Phi generation/package/deterministic/judge/cache evidence;
8. Llama 3B evidence;
9. Gemma 3 evidence;
10. 360-position accounting;
11. per-task reliability and failure boundaries;
12. full deterministic confusion and per-label metrics;
13. fixed-Pro metrics by task and denominator;
14. latency, usage, runtime, artifact, and hardware provenance;
15. six-candidate complete-scope comparison;
16. preserved failures and task-specific observations;
17. cache-only evidence;
18. implementation defects/fixes, if any;
19. privacy, immutability, and tracking evidence;
20. LP-4.1 analysis handoff summary;
21. limitations;
22. line-by-line acceptance checklist.

The report must be detailed enough for PM validation and later LP-4.1 analysis without opening
private candidate outputs.

Do not include private IDs, titles, paths, fingerprints, source, prompts, references, outputs,
rationales, credentials, tokens, project/account identity, artifact hashes, or license-gated data.

## Required validation

When no tracked code changes occur:

```powershell
poetry env info --path
poetry run pytest tests/test_ai_adapter.py tests/test_bench.py -q
poetry run ruff check .
poetry check
poetry run python -m bench prepare --help
poetry run python -m bench generate --help
poetry run python -m bench verify --help
poetry run python -m bench score --help
git diff --check
git diff --cached --name-only
git status --short
```

When tracked code changes occur, also run the complete repository test suite and every check
required by the generic-fix policy.

Also prove:

- all 360 candidate positions are terminal;
- every eligible judge position is terminal;
- all three packages verify and score;
- all three cache-only replays exit zero with zero calls;
- live/frozen/checkpoint/historical artifacts remain unchanged;
- no private artifact or credential is tracked;
- the completion report exists;
- unrelated LP-4.1 files remain untouched;
- delivery is unstaged and uncommitted.

## Acceptance criteria

Ready for PM validation requires:

1. three new complete arms contain identical ordered 120-case identities;
2. identities match the accepted complete baseline arms;
3. all 360 candidate positions are terminal with zero unaccounted;
4. all packages verify and score deterministically;
5. every schema-valid output has a terminal fixed-Pro outcome;
6. invalid/model-quality outputs remain visible and unrepaired;
7. all cache-only replays exit zero with zero provider calls;
8. fixed artifact/runtime/context/task/judge contracts remain unchanged;
9. exact private provenance and privacy-safe aggregate evidence exist;
10. databases, checkpoints, historical packages, and accepted evidence remain unchanged;
11. no private data or credential is tracked;
12. the report provides complete article-analysis inputs without claiming scientific evaluation;
13. no prompt tuning, article drafting, or independent evaluation begins automatically;
14. delivery is unstaged and uncommitted.

## Delivery

Return:

- a concise completion summary;
- exact validation results;
- the completion-report path;
- privacy-safe final Git status;
- any residual limitation or retained failure.

Do not commit. The PM/manager owns validation and commit.
