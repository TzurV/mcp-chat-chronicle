# WP-5.2B1.4 - Three-Candidate 120-Case Overnight Run

## Status

Ready for execution after the manager commits this handoff and the tracked checkout is clean.

## Objective

Produce complete development results over all 30 frozen conversations and four accepted AI tasks
for these candidates, in this order:

1. hosted `vertex_ai/gemini-3.5-flash` as the quality/reliability baseline;
2. local Llama 3.2 1B Instruct `Q4_K_M` as the evaluation floor;
3. local Qwen3.5-4B as the first additional local control.

Each complete arm contains 120 cases. Qwen first receives a separate same-prefix
10-conversation/40-case operational checkpoint, then a new complete 120-case run. The expected
candidate workload is therefore 400 cases: 120 Gemini, 120 Llama, 40 Qwen pilot, and 120 Qwen
complete.

Run candidate generation, package verification, deterministic scoring, fixed-Pro judging, and
cache-only proofs locally from the owner's Windows machine. Vertex candidate/judge calls are
remote by definition, but orchestration and scoring remain local. Use remote generation for local
models only through a later explicit owner decision if measured runtime becomes impractical.

The goal is complete comparable development evidence, not prompt tuning or publication in this
work package.

## Owner Decisions

- Obtain real 120-case numbers now rather than adding more small-model integrations first.
- Run Gemini baseline first, Llama floor second, and Qwen control third.
- Use the complete 30-conversation/120-case frozen development corpus for all three main arms.
- Run Qwen over 40 cases before its complete run.
- Treat Qwen's 40-case stage as an operational checkpoint, not a schema-quality exclusion gate.
  Explicit model-output failures remain measured evidence. Proceed to 120 when all 40 positions
  are terminal, the package verifies, and no systemic configuration/provenance/transport defect
  remains.
- Run locally and allow longer runtime. Reconsider a remote machine only if measured runtime is
  operationally impractical.
- Keep article metric selection and article writing outside this work package.
- Leave changes unstaged and uncommitted; the manager validates and commits only after explicit
  owner instruction.

## Accepted Foundations

Read and reuse:

- `md/agent-operating-notes.md`;
- `docs/development-evaluation.md`;
- WP-5.2A1 Llama integration evidence;
- WP-5.2B1/B1.1 split harness and Vertex judge evidence;
- WP-5.2B1.2 hosted-candidate evidence;
- WP-5.2B1.3 handoff, completion report, and validation review;
- private accepted manifests/configurations under `.chronicle/eval/dev-v1/`.

WP-5.2B1.3 accepted evidence must remain unchanged:

- Llama: 21/40 schema-valid;
- Gemini: 39/40 schema-valid;
- both same-prefix 40-case packages and judge caches immutable;
- both cache-only replays zero-call;
- candidate generation commit `dcca7b2` and later scoring-fix commit `3580d6d` recorded honestly.

Do not rewrite prior package provenance or reuse prior output paths.

## Frozen Evaluation Contract

Use exactly:

- complete scope: all 30 frozen conversations, 120 cases;
- Qwen checkpoint scope: frozen first 10 conversations, 40 cases;
- task order:
  1. `conversation-summary`;
  2. `work-mode-classification`;
  3. `last-activity`;
  4. `title-assessment`;
- accepted task catalog, prompts, versions, selectors, schemas, finalizers, evidence policy, FABLE
  references, temperature, and task output limits;
- primary judge: `vertex_ai/gemini-3.1-pro-preview`;
- judge rubric version 1;
- judge temperature 0;
- judge maximum output tokens 1,000;
- judge reasoning policy `none`;
- deterministic and semantic metrics reported separately.

The three complete arms must independently reconstruct the same ordered 120 case identities. The
Qwen checkpoint must match the first 40 identities of those complete arms. Exact identities remain
private.

Do not modify the frozen database, selection, inputs, references, or task catalogs.

## Candidate Identities

### Arm A - Hosted Gemini baseline

- candidate: `vertex_ai/gemini-3.5-flash`;
- execution: `hosted-api`;
- accepted ADC authentication and provider location;
- accepted structured-output/reasoning/generation settings from WP-5.2B1.3;
- explicit `--allow-remote --confirm-private-eval` generation flags;
- no fake artifact, quantization, device, or local-runtime fields.

### Arm B - Local Llama floor

- Llama 3.2 1B Instruct;
- accepted Bartowski `Q4_K_M` GGUF and private artifact hash;
- LM Studio/LiteLLM accepted model identifier;
- 8,192-token configured context;
- parallelism 1;
- exact accepted local profile/settings from WP-5.2B1.3.

### Arm C - Local Qwen control

- Qwen3.5-4B already installed in LM Studio;
- execution: `local-artifact`;
- exact GGUF filename/repository/revision, byte size, SHA-256, quantization, LM Studio version,
  loaded identifier, execution device, configured context, parallelism, and advertised context must
  be inspected and pinned privately before generation;
- use the existing application-owned LM Studio/LiteLLM route; do not add a model-specific adapter;
- use the same 8,192 context and parallelism 1 where supported; record any unavoidable difference
  and stop for PM approval if it materially changes comparison fairness.

Qwen model-output failures are evaluation evidence. Do not modify prompts or schemas to qualify it.

## External Disclosure Authorization - Already Granted

The owner explicitly granted the following authorization in the manager thread on 2026-07-22.
This handoff is the durable record. Do not ask the owner to confirm it again.

The executor is authorized to:

1. send all 30 selected private conversation inputs, accepted task prompts, and response schemas to
   Vertex AI `gemini-3.5-flash` in the accepted `global` location for exactly 120 candidate cases;
   FABLE references are not sent during candidate generation;
2. send selected private source, schema-valid candidate output, and the corresponding FABLE silver
   reference to Vertex AI `gemini-3.1-pro-preview` in the accepted `global` location for every
   eligible Gemini-120, Llama-120, Qwen-40, and Qwen-120 case;
3. make up to 120 baseline hosted-candidate requests and up to 400 baseline primary-judge requests,
   plus only the already configured bounded transport retries and accepted append-only recovery of
   judge infrastructure/schema failures;
4. use the accepted ADC authentication route and environment-provided project/location settings
   without printing their values;
5. pass `--allow-remote --confirm-private-eval` on every authorized candidate/judge command;
6. incur the ordinary Vertex usage associated with this bounded work package;
7. run these authorized calls unattended overnight after the interactive preflight passes.

This authorization is limited to the exact provider, models, `global` location, frozen corpus,
task contracts, case counts, disclosure contents, retry policy, and work package above. It does not
authorize another model/provider/region, more cases, changed prompts/references/rubric, a different
authentication route, remote execution of Llama/Qwen, or automatic expansion after a failure.

Request new approval only when one of those authorized boundaries changes. A normal CLI safety
flag, ADC refresh, resumable continuation, cache-only replay, or configured retry inside the same
boundary is not a reason to ask again.

Never print credentials, tokens, project/account IDs, private paths, raw source, FABLE references,
candidate outputs, judge rationales, or case fingerprints in chat or tracked reports.

## Execution Strategy

This is operator-assisted but should be prepared for unattended overnight execution.

Before the overnight block, the executor must complete interactively:

- repository/private-corpus preflight;
- all configuration and output-path preparation;
- Vertex ADC/model availability check with synthetic text only if availability is uncertain;
- LM Studio server, Llama model, and Qwen model availability checks;
- Qwen artifact hash/provenance pinning;
- one synthetic four-task Qwen transport/schema smoke;
- verification that the already granted authorization above matches every prepared remote command;
- dry-run or no-provider validation of every command/config;
- enough disk-space check;
- confirmation that the machine is on AC power and will not sleep;
- confirmation that logs write only to ignored private paths and contain no credentials.

Create a private ignored PowerShell operator script only when useful, under the accepted private
evaluation `tmp/` area. Do not track it. It must:

- use explicit paths resolved before execution;
- set `$ErrorActionPreference = 'Stop'`;
- log stage names, UTC start/end times, exit codes, and privacy-safe aggregate accounting;
- never log environment-variable values, tokens, raw prompts, source, references, outputs, or
  rationales;
- stop an arm on verification/configuration/infrastructure failure;
- preserve successful attempts for resumable rerun;
- never substitute models or alter configuration automatically;
- never retry semantic disagreement;
- use accepted bounded provider retries only;
- leave enough information to resume at the failed stage the next morning.

Do not add a tracked multi-model orchestration feature merely for this run.

## Executor Rights Within This Work Package

Without another owner question, the executor may:

- read the frozen private development database, selected inputs, FABLE references, accepted private
  manifests/configuration, and prior private evaluation artifacts required by this handoff;
- create and update ignored private configurations, bundles, packages, scoring directories, judge
  caches, logs, and temporary operator scripts under `.chronicle/eval/dev-v1/`;
- hash and verify private artifacts and databases;
- start/check the LM Studio server and load/unload the exact accepted Llama and pinned Qwen models;
- run synthetic, 40-case, and 120-case candidate commands defined here;
- run deterministic scoring, authorized Pro judging, configured retries, cache-only proofs, tests,
  lint, package checks, and CLI help checks;
- diagnose and resume recoverable stages under the failure policy;
- retain invalid/private outputs in ignored evaluation storage;
- continue from Qwen-40 to Qwen-120 without asking when all operational checkpoint conditions pass,
  even when Qwen has schema/evidence/model-quality failures.

The executor may not commit, push, change task/judge contracts, substitute models, broaden remote
disclosure, delete accepted historical artifacts, or move local-model generation to another
machine without the separate approvals already described.

## Stage 0 - Preflight and Immutable Baselines

1. Follow `md/agent-operating-notes.md`; prove Poetry uses this repository's `.venv`.
2. Require a clean tracked checkout and record the full application commit.
3. Validate the private snapshot manifest, immutable hash, integrity, schema, 711-conversation and
   28,370-message counts, and absence of required WAL/SHM sidecars.
4. Hash live/frozen databases and all accepted WP-5.2B1.3 candidate packages/judge attempts.
5. Validate all 30 inputs, 120 references, ordered selection, and task-catalog identities.
6. Create unique ignored config, bundle, generation-work, package, scoring, judge-cache, and log
   paths for:
   - Gemini-120;
   - Llama-120;
   - Qwen-40;
   - Qwen-120.
7. Confirm no output path overlaps an accepted historical run.
8. Prepare all bundles and prove:
   - each complete bundle contains exactly 30 conversations and 120 cases;
   - all three complete bundles have the same ordered case identity;
   - Qwen-40 contains exactly 10 conversations/40 cases and matches the complete prefix.

## Stage 1 - Gemini Baseline, 120 Cases

Generate the complete hosted candidate package first using the accepted explicit remote flags.

Require:

- expected 120;
- terminal 120;
- unaccounted 0;
- immutable candidate package;
- local package verification;
- deterministic-only scoring;
- all failure boundaries retained without output repair.

Record candidate wall time, p50/p95 overall and by task, schema/evidence/cross-field validity,
confusion matrices, usage, retries, and provider failure categories.

Do not require 120/120 schema-valid as an acceptance condition.

## Stage 2 - Llama Floor, 120 Cases

Load and verify the exact accepted Llama artifact/profile, then generate all 120 cases locally.

Require the same terminal/package/verification/deterministic accounting as Stage 1. Preserve
context-length, evidence, schema, or other model-output failures as measured results.

Record actual complete-run wall time rather than relying on the earlier linear estimate.

## Stage 3 - Qwen Operational Checkpoint, 40 Cases

Load and verify the pinned Qwen artifact/profile. Run the synthetic four-task transport/schema
smoke first. A synthetic model-output failure is recorded but blocks private execution only when it
demonstrates a systemic request/configuration incompatibility rather than ordinary model quality.

Generate the same-prefix 40-case private checkpoint. Proceed to Qwen-120 when:

- all 40 candidate positions are terminal;
- the package verifies;
- deterministic scoring completes;
- there are zero unaccounted positions;
- no unresolved configuration, provenance, request-shape, runtime, or transport defect remains.

Schema-invalid/evidence-invalid outputs do not block the complete run. Report the checkpoint result
before continuing in the private log; no overnight owner response is required when only model
quality failures occurred.

## Stage 4 - Qwen Complete Run, 120 Cases

Create a new complete-scope bundle/package/run identity. Do not mutate the 40-case package.

The existing harness binds package identity to scope, so the complete Qwen run may regenerate the
first 40 cases. Treat that duplication as intentional unless an already accepted generic cache
mechanism proves safe. Do not implement cross-scope attempt reuse in this work package.

Require 120 terminal outcomes, zero unaccounted cases, immutable package verification, and
deterministic scoring. Preserve every failure as evaluation evidence.

## Stage 5 - Fixed-Pro Semantic Scoring

After all available candidate packages verify, judge every schema-valid output using the same
fixed primary judge profile and rubric v1. Keep candidate identity blinded.

Required accounting per package:

```text
eligible = schema-valid candidate outputs
completed + failed = eligible
skipped invalid = expected cases - eligible
unaccounted = 0
```

Do not use Gemini 2.5 Flash in this package. Do not retry a valid semantic score because it differs
from FABLE. Preserve failed attempts. Recover infrastructure/provider-schema failures using the
accepted bounded append-only policy, without changing judge contract or model.

Keep the judge runs within the shortest practical time window because the Pro endpoint is a
preview alias.

## Stage 6 - Cache-Only Proofs

For Gemini-120, Llama-120, Qwen-40, and Qwen-120, run the identical judged configuration with:

```powershell
--with-judge --allow-remote --confirm-private-eval --judge-cache-only
```

Each replay must exit zero, make zero provider calls, preserve package/attempt/aggregate hashes,
and retain coherent deterministic/judge reports. Cache misses fail before provider execution.

## Stage 7 - Comparison and Reporting

Retain complete private aggregate evidence. The tracked completion report must include a
privacy-safe comparison for the three complete 120-case arms and separately label Qwen-40 as a
checkpoint.

Include at least:

- terminal/schema-valid/failed counts overall and by task;
- failure boundaries;
- evidence/cross-field/date/length/title validity;
- work-mode, last-activity, and title-fit confusion matrices;
- exact agreement and per-label support;
- primary judge accounting and dimension means by task;
- wall time and p50/p95 overall/by task;
- token/usage availability and totals with cross-provider comparability caveats;
- retries, rate limits, timeouts, context failures, and provider errors;
- model/artifact/quantization/runtime/context/hardware provenance;
- cache-only proof;
- exact same-case identity proof;
- whether local overnight execution was operationally practical.

Do not select the final article metric subset, create publication graphics, or make general
leaderboard/statistical claims here.

## Failure and Fix Policy

Fix and resume generic harness, path, serialization, atomic-write, cache, package, resumability,
provider-request, or actionable-diagnostic defects within at most three focused cycles. Add a
regression and request manager review/commit when a tracked fix is required for clean provenance.
Do not instruct the owner to commit directly.

Preserve as model outcomes:

- invalid JSON/schema/evidence/cross-field output;
- context-limit failure from the accepted configuration;
- refusal;
- weak FABLE agreement or low judge score;
- slow generation or high token use.

Require PM/owner approval before changing model, provider, region, scope, task contract, FABLE
reference, judge/rubric, context, temperature, token limit, retry semantics, reasoning policy,
authentication route, or local/remote execution placement.

An unattended stage may stop safely on an infrastructure error. Do not mark the whole package
`Partial` until the executor has resumed recoverable stages during the next working period or
exhausted the bounded fix policy.

## Required Validation

Run once after all tracked implementation changes and completed runs:

```powershell
poetry env info --path
poetry run pytest tests/test_bench.py -q
poetry run pytest
poetry run ruff check .
poetry check
poetry run python -m bench prepare --help
poetry run python -m bench generate --help
poetry run python -m bench verify --help
poetry run python -m bench score --help
poetry run chronicle --help
git diff --check
git diff --cached --name-only
git status --short
```

Also prove live/frozen DB immutability, historical-package immutability, new package/attempt/cache
identity stability, complete 400 candidate-case accounting, complete eligible judge accounting,
and zero tracked private artifacts.

## Acceptance Criteria

Ready for PM validation requires:

1. Gemini-120, Llama-120, and Qwen-120 use the same ordered 120 case identities;
2. Qwen-40 matches the first 40 complete-case identities;
3. all 400 candidate positions are terminal and none are unaccounted;
4. all four packages verify and score deterministically;
5. every eligible output has a terminal Pro-judge result;
6. invalid outputs are visible and skipped from semantic scoring;
7. every cache-only replay exits zero with zero calls;
8. no candidate output is repaired or removed;
9. exact candidate and judge provenance is recorded privately and summarized safely;
10. full metrics and runtime evidence exist;
11. repository validation passes;
12. live/frozen/historical artifacts remain unchanged;
13. no private artifact or credential is tracked;
14. completion report maps evidence to every requirement;
15. delivery changes remain unstaged and uncommitted.

## Completion Report

Write exactly:

```text
md/handoffs/reports/WP-5.2B1.4-completion-report.md
```

Required sections:

1. status and executive summary;
2. exact scope and case identity reconciliation;
3. repository/runtime/private-corpus preflight;
4. consolidated authorization boundary;
5. Gemini-120 generation, verification, deterministic, judge, and cache evidence;
6. Llama-120 evidence;
7. Qwen artifact/profile pin and synthetic smoke;
8. Qwen-40 checkpoint evidence and continue decision;
9. Qwen-120 evidence;
10. three-arm complete-scope comparison plus separately labelled Qwen checkpoint;
11. deterministic confusion/category metrics;
12. semantic judge metrics;
13. performance/usage/provenance comparison;
14. overnight execution timeline and interruptions;
15. model outcomes preserved;
16. infrastructure defects/fixes/regressions;
17. full validation results;
18. immutability/privacy/tracking evidence;
19. limitations and next-model recommendation;
20. line-by-line acceptance checklist.

Do not include private IDs, titles, paths, fingerprints, source, prompts, references, outputs,
rationales, credentials, tokens, or project/account identity.

## Commit Ownership

- Executor leaves everything unstaged and uncommitted.
- Executor does not update plan/ledger to accepted.
- Manager validates and commits only after explicit owner request.
