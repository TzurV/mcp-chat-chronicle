# WP-5.2B2.1 - Three Qualified Candidate 40-Case Checkpoint

## Status

Ready for execution after:

1. the manager commits this handoff and all accepted planning/reporting changes;
2. the tracked checkout is clean;
3. the owner sends the explicit Vertex disclosure authorization in this handoff's authorization
   section to the executor.

## Executor recommendation

Continue in the same executor thread that completed WP-5.2A5.1. That thread already has the
approved model artifacts, license/download decisions, private provenance, LM Studio identifiers,
frozen input identities, and compatibility evidence. Starting a new executor would add setup and
provenance-transfer risk without improving independence.

## Executor role

Act as the implementation/evaluation executor. Do not ask the owner to commit files. Leave all
delivery changes unstaged and uncommitted for manager validation.

Read `md/agent-operating-notes.md` first. Keep Poetry in this repository's `.venv`, avoid piped
PowerShell commands, and run Windows sandbox-sensitive reads sequentially.

## Objective

Run the three newly qualified local candidates over the same frozen first 10 conversations and
four accepted AI tasks:

1. Phi-4 Mini Instruct;
2. Llama 3.2 3B Instruct;
3. Gemma 3 4B IT.

Each arm contains 40 candidate cases. The total candidate workload is 120 terminal positions.

For each arm:

- generate locally through LM Studio/LiteLLM;
- preserve schema-valid outputs and explicit failures;
- create and verify an immutable candidate package;
- compute deterministic metrics;
- judge every schema-valid output with the fixed Gemini 3.1 Pro rubric-v1 judge;
- prove a zero-call cache-only judge replay;
- produce privacy-safe comparable evidence.

Stop after the checkpoint and completion report. Do not automatically begin any 120-case arm.
The PM/owner will decide complete-arm admission from the checkpoint evidence.

## Accepted foundations

Read and preserve:

- `md/master-plan.md`;
- `md/development-ledger.md`;
- `md/agent-operating-notes.md`;
- `docs/development-evaluation.md`;
- `md/handoffs/WP-5.2A5.1-remaining-lm-studio-candidate-qualification.md`;
- `md/handoffs/reports/WP-5.2A5.1-completion-report.md`;
- `md/handoffs/reports/WP-5.2A5.1-validation-review.md`;
- accepted WP-5.2B1 through WP-5.2B1.4 handoffs, reports, and validation reviews;
- private accepted manifests/configurations under `.chronicle/eval/dev-v1/`.

WP-5.2A5.1 accepted:

| Candidate | Qualification | Artifact policy |
|---|---:|---|
| Phi-4 Mini Instruct | 8/8 | pinned LM Studio Community Q4_K_M |
| Llama 3.2 3B Instruct | 8/8 | pinned LM Studio Community Q4_K_M |
| Gemma 3 4B IT | 8/8 | pinned LM Studio Community Q4_K_M |

Gemma 4 E2B IT is excluded. It failed the fixed-runtime structured-output compatibility gate and
must not be retried, substituted, or discussed as a candidate arm in this work package.

## Frozen comparison contract

Use exactly:

- frozen first 10 selected conversations;
- 40 ordered cases per candidate;
- the same ordered case identities used by accepted WP-5.2B1.3 and Qwen-40;
- task order:
  1. `conversation-summary`;
  2. `work-mode-classification`;
  3. `last-activity`;
  4. `title-assessment`;
- accepted selectors, prompts, schemas, finalizers, evidence policy, task versions, FABLE silver
  references, and task-owned output limits;
- configured context 8,192;
- temperature 0;
- retries 0 for candidate model outcomes;
- concurrency/parallelism 1;
- strict structured output;
- local candidate generation only;
- fixed primary judge `vertex_ai/gemini-3.1-pro-preview`;
- judge rubric version 1, temperature 0, maximum 1,000 tokens, reasoning policy `none`;
- deterministic and semantic metrics reported separately.

Do not change prompts, add examples, tune schemas, expand context, alter output limits, repair
responses, or use a different runtime. Advertised 128K model context is provenance only.

The three new arms must reconstruct identical ordered 40-case identities. They must also match the
accepted historical first-40 identity without mutating or repackaging historical runs.

## Candidate identities

Use the exact privately pinned WP-5.2A5.1 artifacts:

### Phi-4 Mini

- official lineage: `microsoft/Phi-4-mini-instruct`;
- accepted Q4_K_M GGUF revision and SHA-256;
- accepted LM Studio identifier;
- configured context 8,192 and parallelism 1.

### Llama 3.2 3B

- official lineage: `meta-llama/Llama-3.2-3B-Instruct`;
- accepted Q4_K_M GGUF revision and SHA-256;
- accepted owner-controlled Llama license/access record;
- accepted LM Studio identifier;
- configured context 8,192 and parallelism 1.

### Gemma 3 4B

- official lineage: `google/gemma-3-4b-it`;
- accepted Q4_K_M GGUF revision and SHA-256;
- accepted owner-controlled Gemma access record;
- accepted LM Studio identifier;
- configured context 8,192 and parallelism 1.

Before each arm, independently recheck artifact size/hash, loaded model identity, runtime/engine,
context, parallelism, and hardware class. Do not expose private paths or hashes in tracked output.

## External disclosure authorization

Candidate generation is local and discloses no private source to a new remote candidate provider.

Fixed-Pro judging sends the selected private source, schema-valid candidate result, and
corresponding FABLE silver reference to Vertex AI. The previous WP-5.2B1.4 authorization did not
name these three new candidate arms, so the owner must explicitly authorize this scope once.

The authorization becomes active only when the owner sends this exact or substantively equivalent
statement to the executor:

> I authorize fixed-Pro judging for WP-5.2B2.1. You may send the selected first 10 private
> conversation inputs, each schema-valid Phi-4 Mini, Llama 3.2 3B, and Gemma 3 4B candidate result,
> and the corresponding FABLE silver reference to Vertex AI
> `gemini-3.1-pro-preview` in `global`, for up to 120 baseline judge cases plus only the configured
> bounded retries. Use ADC and the existing rubric-v1 judge configuration. I approve the ordinary
> Vertex usage cost. Do not ask again unless provider, model, region, source scope, case count,
> disclosure contents, rubric, or authentication route changes.

After receiving that statement, do not ask the owner to reconfirm for normal CLI safety flags,
ADC refresh, resumable continuation, bounded retry, or cache-only replay inside the same boundary.

Never print credentials, tokens, cloud project/account identity, raw source, candidate output,
FABLE reference, judge rationale, private IDs, or private paths in chat or tracked files.

## Out of scope

- no 120-case candidate arm;
- no Gemini 3.5 Flash candidate rerun;
- no historical Llama 1B, Qwen, Gemini, or judge rerun;
- no Gemma 4 retry;
- no prompt/context/rubric tuning;
- no larger-context study;
- no task routing implementation;
- no composite-score implementation;
- no article drafting or graphic generation;
- no secondary judge;
- no remote generation for local models;
- no runtime/model substitution;
- no live/frozen database write;
- no commit or push.

## Stage 0 - Preflight and immutable baselines

1. Require a clean tracked checkout and record full HEAD.
2. Prove `poetry env info --path` resolves to this repository's `.venv`.
3. Validate the frozen snapshot manifest, database hash/integrity/schema, 711 conversations,
   28,370 messages, and absence of required WAL/SHM sidecars.
4. Hash live/frozen databases and all accepted WP-5.2B1.3/B1.4 candidate packages and judge
   attempts.
5. Validate all 30 private inputs, 120 FABLE references, ordered selection, and accepted task
   catalog identities without changing them.
6. Reconstruct the frozen first-10/40-case prefix independently.
7. Prove it matches accepted WP-5.2B1.3 and Qwen-40 case identity.
8. Recheck the three WP-5.2A5.1 artifact/runtime identities.
9. Create unique ignored config, bundle, generation-work, package, scoring, judge-cache, and log
   paths for all three arms.
10. Confirm no new path overlaps any historical or accepted arm.
11. Confirm disk space, AC power, sleep policy, LM Studio readiness, and single-worker execution.
12. Dry-run/no-provider validate every prepared command.

## Stage 1 - Phi-4 Mini 40 cases

1. Load only the accepted Phi artifact.
2. Verify model identifier, context 8,192, parallelism 1, runtime/engine, and artifact identity.
3. Prepare the exact first-10/40-case bundle.
4. Generate all 40 cases locally with retries 0.
5. Require 40 terminal positions and zero unaccounted.
6. Preserve invalid JSON/schema/evidence/cross-field/context/timeout outcomes as failures.
7. Package immutably, verify, and score deterministically.
8. Record wall span, p50/p95 overall/by task, usage, failures, and task validity.

## Stage 2 - Llama 3.2 3B 40 cases

Repeat Stage 1 with the accepted Llama 3B artifact and a separate scope/package identity.

Specifically preserve semantically awkward but schema-valid outputs, including blocker values like
the WP-5.2A5.1 literal `"[]"` observation. Do not repair, reinterpret, or retry them.

## Stage 3 - Gemma 3 4B 40 cases

Repeat Stage 1 with the accepted Gemma 3 artifact and a separate scope/package identity.

Do not load or probe Gemma 4. Do not change thinking/reasoning controls, output limits, runtime, or
context from the accepted Gemma 3 qualification profile.

## Stage 4 - Fixed-Pro judging

After all three candidate packages verify, judge every schema-valid output with the fixed Pro
profile under the owner authorization above.

For each package require:

```text
eligible = schema-valid candidate outputs
completed + failed = eligible
skipped invalid = 40 - eligible
unaccounted = 0
```

Use candidate-blinded requests. Preserve terminal judge failures after the configured bounded
recovery policy. Never retry a valid semantic score because it differs from FABLE.

The historical Gemini/Llama1/Qwen judge evidence was created in a nearby but earlier run window.
Do not rejudge it here. Record judge model/version/rubric and exact run windows, and include preview
drift as a comparison limitation.

## Stage 5 - Cache-only proofs

For each arm run the identical judged configuration with:

```powershell
--with-judge --allow-remote --confirm-private-eval --judge-cache-only
```

Each replay must:

- exit zero;
- make zero provider calls;
- preserve candidate package, attempt, judge-attempt, judge-output, and aggregate hashes;
- retain coherent deterministic/judge reports;
- fail before provider execution if a cache entry is missing.

## Stage 6 - Checkpoint comparison and admission recommendation

Create a privacy-safe comparison for the three new arms and a clearly separated historical
same-prefix context table.

For each new arm include:

- 40 terminal positions and schema-valid rate;
- validity/failure counts by task and boundary;
- evidence/date/cross-field/output-limit validity;
- work-mode, last-activity, and title-fit confusion matrices;
- exact agreement and per-label support/precision/recall;
- fixed-Pro completed/failed/skipped accounting;
- judge dimension means by task with denominators;
- wall span, summed latency, overall/per-task p50/p95;
- exact usage availability and totals;
- artifact/quantization/runtime/context/hardware provenance;
- cache-only proof.

Historical context may include only accepted same-prefix values:

- Gemini 3.5 Flash: 39/40 schema-valid;
- Llama 3.2 1B: 21/40 schema-valid;
- Qwen3.5-4B: 34/40 schema-valid.

Do not combine historical and current Pro scores without noting preview-model run-window drift.
Do not treat the 40-case checkpoint as a complete-arm leaderboard.

Recommend one of:

- `admit to 120-case arm`;
- `do not admit under current contract`;
- `PM decision required`.

Base recommendations on whole-package reliability, failure boundaries, task-level deterministic
and judge evidence, and operational feasibility. Do not use a hidden composite threshold or tune a
candidate to qualify. Final admission remains a PM/owner decision.

## Failure and fix policy

Candidate model-quality outcomes are preserved:

- invalid JSON/schema/evidence/cross-field output;
- context-limit or timeout under fixed settings;
- refusal or empty response;
- awkward but schema-valid content;
- weak FABLE agreement;
- low judge score;
- slow local execution.

For a genuine generic harness, cache, serialization, atomic-write, resume, request-shape, or
diagnostic defect:

1. use at most two focused repair cycles;
2. add a synthetic regression;
3. run focused tests, full suite, Ruff, Poetry, and diff checks;
4. stop for manager review/commit before resuming from a new clean HEAD;
5. preserve honest split provenance;
6. never repeat successful candidate or judge calls unnecessarily.

Ask for PM/owner approval before changing model, artifact, quantization, runtime, context, task
contract, output limit, prompt, reference, judge, rubric, region, case scope, disclosure content,
authentication route, retry semantics, or execution placement.

## Completion report

Write exactly:

`md/handoffs/reports/WP-5.2B2.1-completion-report.md`

Required sections:

1. status and executive summary;
2. clean preflight and immutable baseline evidence;
3. exact 40-case identity reconciliation;
4. authorization boundary;
5. common model/task/settings contract;
6. Phi generation/package/deterministic/judge/cache evidence;
7. Llama 3B evidence;
8. Gemma 3 evidence;
9. 120-position accounting;
10. three-arm checkpoint comparison;
11. historical same-prefix context;
12. deterministic confusion and per-label metrics;
13. judge metrics by task and denominators;
14. latency, usage, runtime, and provenance;
15. preserved failures and semantic observations;
16. cache-only evidence;
17. implementation defects/fixes, if any;
18. privacy, immutability, and tracking evidence;
19. per-candidate 120-case admission recommendation;
20. limitations;
21. line-by-line acceptance checklist.

Do not include private IDs, titles, paths, fingerprints, source, prompts, references, outputs,
rationales, credentials, tokens, project/account identity, artifact hashes, or license-gated data.

## Required validation

When no tracked code changes:

```powershell
poetry env info --path
poetry run pytest tests/test_ai_adapter.py tests/test_bench.py -q
poetry run ruff check .
poetry check
poetry run python -m bench verify --help
poetry run python -m bench score --help
git diff --check
git diff --cached --name-only
git status --short
```

When tracked code changes, also run the complete repository test suite and every check required by
the generic-fix policy.

Also prove:

- all 120 candidate positions terminal;
- all eligible judge positions terminal;
- three zero-call cache-only replays;
- live/frozen/historical artifact immutability;
- no tracked private artifact;
- completion report exists;
- unrelated LP-4.1 files remain untouched.

## Acceptance criteria

Ready for PM validation requires:

1. three arms contain identical ordered 40-case identities;
2. identities match the accepted historical frozen prefix;
3. all 120 candidate positions are terminal and none unaccounted;
4. all packages verify and score deterministically;
5. every schema-valid output has a terminal fixed-Pro outcome;
6. invalid/model-quality outputs remain visible and unrepaired;
7. all cache-only replays exit zero with zero calls;
8. fixed model/runtime/context/task/judge contracts remain unchanged;
9. exact private provenance and privacy-safe aggregate evidence exist;
10. databases, historical packages, and accepted evidence remain unchanged;
11. no private data or credential is tracked;
12. each candidate has an explicit PM-facing admission recommendation;
13. no 120-case run starts automatically;
14. delivery is unstaged and uncommitted.

## Commit ownership

- Executor leaves everything unstaged and uncommitted.
- Executor does not mark the plan/ledger accepted.
- Manager validates the completion report against this handoff.
- Manager commits only after explicit owner instruction.

