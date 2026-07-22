# WP-5.2B1.3 - Ten-Conversation Accepted-Arm Pilot

## Status

Ready for execution.

## Objective

Run the two already accepted candidate arms over the same frozen first 10 development
conversations and all four accepted AI tasks. This produces 40 candidate cases per arm and 80
candidate cases in total.

The two arms are:

1. local Llama 3.2 1B Instruct `Q4_K_M` through LM Studio;
2. hosted `vertex_ai/gemini-3.5-flash` through the accepted generic hosted-candidate path.

Verify and score both immutable candidate packages locally. Judge every schema-valid result with
the same fixed `vertex_ai/gemini-3.1-pro-preview` rubric-v1 primary judge. Measure the local Llama
runtime so the owner can decide later whether the complete 120-case local-model matrix is practical
on this machine or should use remote generation.

This is a development pilot, not a scientific benchmark and not the article publication run. Do
not expand beyond 10 conversations or 40 cases per arm in this work package.

## Planning Context

Accepted foundations:

- WP-5.1.2A: immutable private development database snapshot;
- WP-5.1.2B: 30 frozen conversations and 120 direct FABLE silver references;
- WP-5.2A1: exact Llama 3.2 1B local evaluation-floor integration;
- WP-5.2B1: split prepare/generate/verify/score evaluation harness;
- WP-5.2B1.1: Vertex structured judge and cache-only compatibility;
- WP-5.2B1.2: generic hosted candidates and the accepted two-conversation/eight-case comparison.

The first two-conversation comparison established:

- Llama: 8 terminal cases, 6 schema-valid, 2 schema-invalid;
- Gemini candidate: 8 terminal and 8 schema-valid;
- the Pro judge completed every eligible case;
- cache-only replays made zero provider calls;
- deterministic scores and semantic judge scores remain separate;
- Gemini 2.5 Flash is diagnostic sensitivity only and is not part of this pilot.

Read before starting:

- `md/agent-operating-notes.md`;
- `docs/development-evaluation.md`;
- `md/handoffs/reports/WP-5.2B1.2-completion-report.md`;
- `md/handoffs/reports/WP-5.2B1.2-validation-review.md`;
- the private accepted evaluation configuration and manifests under `.chronicle/eval/dev-v1/`.

Private files under `.chronicle/` are authoritative for exact corpus hashes, model artifacts, run
paths, package identities, and credentials-related environment names. Do not copy their private
values into tracked files or chat messages.

## Frozen Comparison Contract

Use exactly:

- selection: `frozen-prefix-v1`;
- conversation limit: 10;
- conversations: the first 10 positions of the already frozen 30-conversation ordered selection;
- tasks, in accepted order:
  1. `conversation-summary`;
  2. `work-mode-classification`;
  3. `last-activity`;
  4. `title-assessment`;
- expected cases per candidate: 40;
- expected cases across both candidates: 80;
- accepted task catalog, task versions, selectors, prompts, schema identities, finalizers,
  generation settings, and evidence policy from WP-5.1.1/WP-5.2B1;
- accepted FABLE references without edits;
- primary judge: `vertex_ai/gemini-3.1-pro-preview`;
- judge rubric: version 1;
- judge temperature: 0;
- judge maximum output tokens: 1,000;
- judge reasoning policy: `none`.

The two arm manifests must resolve to the same 10-conversation frozen-prefix identity and the same
40 ordered case identities. Candidate model identity is the only intended candidate-contract
difference.

Do not modify or regenerate the 30 frozen inputs, FABLE references, task catalogs, live database,
or frozen database.

## Exact Candidate Arms

### Arm A - Local Llama evaluation floor

Reuse the exact accepted WP-5.2A1 model identity and settings:

- model family: Llama 3.2 1B Instruct;
- accepted artifact: Bartowski `Q4_K_M` GGUF recorded in the private manifest;
- LiteLLM route/model: accepted `lm_studio/llama-3.2-1b-instruct` profile;
- LM Studio configured context: 8,192;
- parallelism: 1 unless the accepted private profile proves otherwise;
- temperature and task token limits: the accepted task/profile effective settings;
- execution: `local-artifact`.

Confirm the loaded LM Studio identifier and artifact correspond to the accepted model before the
first call. Do not assume that a model appearing in `lms ls` is the model currently loaded for the
endpoint.

### Arm B - Hosted Gemini candidate

Reuse the exact accepted WP-5.2B1.2 hosted candidate identity and settings:

- model: `vertex_ai/gemini-3.5-flash`;
- execution: `hosted-api`;
- authentication: the accepted Vertex ADC route;
- provider location and effective reasoning/generation settings: the accepted private profile;
- authorization flags: `--allow-remote --confirm-private-eval`.

Do not substitute another Gemini model, use an API-key fallback, or represent the hosted model with
fake GGUF, quantization, device, or local-runtime fields.

## Owner Authorization and Disclosure Boundary

The owner authorizes this exact 10-conversation scope for:

- hosted candidate generation with `vertex_ai/gemini-3.5-flash`; and
- semantic judging of schema-valid outputs with
  `vertex_ai/gemini-3.1-pro-preview`.

Hosted candidate generation discloses the selected private conversation input, task prompt, and
response schema to the configured Vertex candidate. It does not disclose FABLE references.

Judge scoring discloses the selected private source, schema-valid candidate result, and FABLE
reference to the configured Vertex judge. Candidate model identity remains blinded in the judge
prompt.

Do not repeatedly request approval for the same provider, models, 10-conversation prefix, four
tasks, and disclosure content. The explicit CLI authorization flags remain mandatory. Request new
approval before changing provider, candidate model, judge model, conversation limit, task set, or
disclosure contents.

Never print or paste credentials, access tokens, project/account IDs, raw conversations, FABLE
references, candidate outputs, judge rationales, private paths, or case fingerprints into the
executor chat or tracked report.

## Delivery Style

This is an operator-assisted execution handoff.

The executor owns:

- preflight and contract verification;
- private configuration preparation;
- concise PowerShell instructions for owner-operated runtime/authentication actions;
- candidate generation, package verification, scoring, and cache proof;
- bounded diagnosis and any permitted benchmark fix;
- aggregate interpretation and the completion report.

When owner action is needed, provide one coherent command block at a time. Before each block state:

1. what it calls or reads;
2. what private information leaves the machine, if any;
3. what local artifacts it creates;
4. the expected success shape;
5. exactly which privacy-safe output the owner should return.

Use PowerShell-safe quoting and variables such as `$CONFIG`, `$BUNDLE`, `$PACKAGE`, and `$RUN`.
Validate returned evidence before advancing.

## Phase 0 - Repository and Private-Corpus Preflight

1. Follow `md/agent-operating-notes.md`.
2. Clear inherited `VIRTUAL_ENV`/`POETRY_ACTIVE` when necessary and prove:

   ```powershell
   poetry env info --path
   ```

   resolves to this repository's `.venv`.
3. Record `git rev-parse HEAD` and `git status --short`.
4. Preserve all PM/owner changes. Do not restore, overwrite, or commit them.
5. Candidate generation should use a clean tracked application commit. If PM planning files are
   still modified, ask the owner/PM to commit them before generation. Do not enable dirty-tracked
   execution or pin a tracked-diff hash without explicit PM approval.
6. Validate the frozen snapshot using its private manifest:
   - expected schema version;
   - integrity check;
   - expected 711 conversations and 28,370 messages;
   - expected immutable hash;
   - no required WAL/SHM sidecars.
7. Hash the live and frozen databases before any candidate run. Retain hashes privately.
8. Validate the frozen selection, 30 input files, 120 references, and task-catalog identities using
   the accepted read-only preflight. Do not inspect or print raw content unnecessarily.
9. Confirm that the first 10 frozen positions produce exactly 40 unique ordered task cases.
10. Confirm unique ignored paths/run IDs for each arm's config, bundle, generation work, candidate
    package, scoring directory, and judge cache.
11. Preserve all accepted two-conversation packages, scores, judge attempts, and reports unchanged.

No synthetic provider gate is required merely to repeat accepted models and contracts. Run a
minimal synthetic health probe only if provider/runtime availability has changed or a real call
fails before producing a candidate result.

## Phase 1 - Prepare the Two 40-Case Bundles

Create separate private evaluation configurations for Arm A and Arm B by copying the accepted
private configurations and changing only fields needed for unique run identities and the intended
candidate profile.

For each arm run the accepted preparation command with:

```powershell
--conversation-limit 10
```

Required preparation evidence:

- exactly 10 selected conversations;
- exactly 40 cases;
- frozen-prefix selection identity;
- complete task/catalog/schema/prompt/finalizer identities;
- unique bundle and run identity;
- no private absolute paths or credentials in the portable bundle;
- Arm A and Arm B case identities match exactly and in the same order.

Do not create subset copies of the input/reference authority directories. The harness must derive
the prefix independently from the complete frozen corpus.

## Phase 2 - Generate Arm A Locally

1. Confirm LM Studio server status and list available/loaded models.
2. Load or select the exact accepted Llama model with 8,192 context and parallelism 1.
3. Confirm the OpenAI-compatible endpoint reports the intended model identifier.
4. Record privacy-safe local runtime/model provenance.
5. Start wall-clock measurement immediately before `bench generate` and stop it after package
   finalization.
6. Generate against the Arm A 40-case bundle without remote authorization flags.
7. Resume matching completed attempts if interrupted. Do not regenerate successful attempts.
8. Preserve invalid raw responses only in the ignored private run area.

Required Arm A terminal accounting:

```text
expected cases: 40
terminal cases: 40
unaccounted cases: 0
```

Schema-invalid results, evidence failures, cross-field failures, refusals, and explicit candidate
failures remain visible evaluation outcomes. Do not repair model output or change prompts to make
the result pass.

After generation:

- verify the immutable package against the local frozen corpus;
- run deterministic-only scoring;
- confirm all 40 cases reconcile;
- record total generation wall time, per-task p50/p95 latency, token usage when available, retries,
  and terminal failure categories.

## Phase 3 - Generate Arm B Through Vertex

1. Verify ADC without displaying a token.
2. Verify required Vertex project/location variables by printing booleans only.
3. Confirm the exact accepted hosted candidate profile resolves to
   `vertex_ai/gemini-3.5-flash`.
4. Explain the authorized disclosure once, then run hosted generation with:

   ```powershell
   --allow-remote --confirm-private-eval
   ```
5. Start and stop wall-clock measurement around generation/package finalization.
6. Resume matching completed attempts after an interruption. Do not regenerate successful
   attempts or switch models after a provider failure.

Required Arm B terminal accounting:

```text
expected cases: 40
terminal cases: 40
unaccounted cases: 0
```

After generation:

- verify the immutable package locally;
- run deterministic-only scoring locally;
- confirm all 40 cases reconcile to the same identities as Arm A;
- record total generation wall time, per-task p50/p95 latency, token usage when available, retries,
  and terminal failure categories.

Do not require 40/40 schema validity as an acceptance condition. Report it as a measured result.

## Phase 4 - Primary Pro Judging

Generate both candidate packages before judging so the two primary judge runs can occur in a
reasonably bounded time window against the preview alias.

For each verified immutable package:

1. create a distinct ignored scoring directory and judge cache;
2. use the exact same Pro profile and rubric-v1 contract;
3. run `bench score` with:

   ```powershell
   --with-judge --allow-remote --confirm-private-eval
   ```
4. judge every schema-valid candidate output;
5. explicitly skip every schema-invalid output as `no_valid_output`;
6. require zero unaccounted eligible cases;
7. do not retry a valid semantic score because it differs from FABLE or from the other candidate.

Required judge accounting for each arm:

```text
eligible = schema-valid candidate outputs
completed + failed = eligible
skipped invalid = 40 - eligible
unaccounted = 0
```

The target is zero judge infrastructure/application failures. A recoverable provider or harness
failure should be diagnosed and resumed under the failure policy below.

Do not run Gemini 2.5 Flash judging in this work package.

## Phase 5 - Zero-Call Cache Proof

For each arm, rerun the identical judged package/config with:

```powershell
--with-judge --allow-remote --confirm-private-eval --judge-cache-only
```

Prove:

- command exits zero;
- zero provider calls occur;
- completed/failed/skipped accounting is unchanged;
- judge attempt files are unchanged;
- attempt aggregate identity is unchanged;
- deterministic and judge aggregate reports remain coherent and canonical;
- candidate package remains unchanged.

A cache miss must fail before provider execution. Do not fill it during cache-only verification.

## Phase 6 - Comparison and Runtime Projection

Create a privacy-safe comparison in the completion report. Retain all full aggregate artifacts
privately, but do not decide the later article metric subset here.

At minimum compare:

- candidate/provider identity;
- identical 10-conversation/40-case scope proof;
- candidate terminal/success/schema-invalid/failure counts;
- schema-valid rate overall and by task;
- evidence-valid and cross-field-valid counts;
- summary date and length validity;
- work-mode confusion matrix, exact agreement, and per-label support;
- last-activity status agreement;
- title-fit agreement;
- judge eligible/completed/failed/skipped counts;
- judge dimension means grouped by task;
- candidate total wall time;
- candidate p50/p95 latency overall and by task;
- prompt/completion/reasoning/total token usage when available;
- retry, rate-limit, timeout, and provider failure counts;
- cache-only call count;
- exact settings/provenance differences.

For local Llama, calculate a simple projected duration for 120 cases as three times the measured
40-case generation wall time. Label this as a linear planning estimate, not a benchmark result.
Record observed factors that could make the estimate inaccurate, such as warm-up, context-length
mix, throttling, interruption, or retry behavior.

Make no superiority, statistical significance, general leaderboard, or publication-grade claim
from 10 conversations. FABLE is silver development reference data and Gemini is an automated
judge, not ground truth.

## Failure and Fix Policy

### Fix and resume without another PM approval

The executor may diagnose, implement the smallest generic fix, add a regression, and resume for:

- benchmark filesystem/path/newline/serialization defects;
- package verification or canonical report reconstruction defects;
- cache identity, resumability, or interrupted-finalization defects;
- local/hosted generic provenance handling defects;
- provider request-shape compatibility that does not change the application contract;
- authentication/configuration diagnostics;
- actionable CLI error handling;
- transient provider or runtime interruption after confirming the intended model remains selected.

Use no more than three focused diagnose/fix/validate cycles for the same infrastructure defect.
Do not return `Partial` after the first recoverable failure merely because the initial command did
not complete. Record every cycle and its outcome in the report.

### Preserve as evaluation results

Do not treat these as software defects:

- schema-invalid candidate output from a valid request;
- weak agreement with FABLE;
- low judge scores;
- legitimate refusal;
- slow latency or high token usage;
- task ambiguity visible in the frozen case;
- a different result from the earlier two-conversation smoke when the request is valid and
  provenance is correct.

### Return for PM/owner approval

Do not change without approval:

- candidate or judge model;
- provider or authentication route;
- conversation count or frozen selection order;
- task prompt, task version, selector, schema, finalizer, evidence policy, FABLE reference, judge
  rubric, dimension, or score anchor;
- context, temperature, token limit, retry policy, or reasoning policy in only one arm when it
  affects fairness;
- automatic output correction, truncation, repair, or semantic retry;
- remote-machine execution;
- scope beyond 10 conversations/40 cases per candidate.

`Partial` is appropriate only when a required owner action remains outstanding at report time, the
same infrastructure blocker survives the permitted bounded cycles, or case accounting cannot be
made complete. `Blocked` follows the project's repeated-blocker policy. Model-quality failures do
not make the work package partial when they are explicitly captured and all cases reconcile.

## Required Repository Validation

Run after all permitted implementation changes, or once at the end when this remains run-only:

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

Also confirm:

- live and frozen database hashes are unchanged from Phase 0;
- frozen inputs, selection, FABLE references, and task catalogs are unchanged;
- accepted two-conversation candidate/judge artifacts are unchanged;
- the two new candidate packages are immutable after generation;
- both new cache-only judge replays make zero calls;
- all 80 candidate case positions and every eligible judge case reconcile;
- no `.chronicle`, DB, ZIP, candidate package, raw output, judge attempt, token, credential,
  project/account ID, case fingerprint, private path, or transcript is tracked;
- all executor changes remain unstaged and uncommitted.

## Acceptance Criteria

WP-5.2B1.3 is ready for PM validation when:

1. both arms select the same frozen first 10 conversations;
2. both arms prove the same ordered 40-case identity;
3. Arm A has 40 terminal candidate outcomes and zero unaccounted cases;
4. Arm B has 40 terminal candidate outcomes and zero unaccounted cases;
5. both candidate packages pass local verification;
6. deterministic scoring completes for both packages;
7. every schema-valid output has a terminal Pro-judge result;
8. every schema-invalid output is visibly counted and skipped from semantic judging;
9. no judge case is unaccounted for;
10. both cache-only reruns exit zero with zero provider calls;
11. local Llama wall time and a clearly labelled 120-case planning projection are recorded;
12. complete private metrics and a privacy-safe comparison summary exist;
13. all allowed validation commands pass;
14. live/frozen data and accepted historical run artifacts remain unchanged;
15. no private evaluation or credential artifact is tracked;
16. the completion report maps evidence to every criterion;
17. changes remain unstaged and uncommitted.

## Completion Report

Write the detailed completion report at exactly:

```text
md/handoffs/reports/WP-5.2B1.3-completion-report.md
```

Required sections:

1. status: `Ready for PM validation`, `Partial`, or `Blocked`;
2. executive summary;
3. repository commit/environment preflight;
4. frozen contract and 10-conversation/40-case identity evidence;
5. private configuration/provenance summary without private values;
6. Arm A generation, terminal accounting, verification, and deterministic scoring;
7. Arm B generation, terminal accounting, verification, and deterministic scoring;
8. Pro-judge accounting for both arms;
9. cache-only zero-call proof for both arms;
10. privacy-safe side-by-side metrics table;
11. work-mode confusion matrices and task-level deterministic metrics;
12. semantic judge dimension summary;
13. local Llama measured wall time and 120-case planning projection;
14. observed model-output failures retained as evaluation evidence;
15. infrastructure defects, diagnosis cycles, fixes, regressions, and resumed results;
16. files changed and why, including an explicit statement when no source code changed;
17. repository validation commands/results;
18. database/artifact immutability and privacy/tracking evidence;
19. limitations and recommendation for proceeding to WP-5.2A5 qualification;
20. line-by-line acceptance checklist.

The tracked report may include aggregate counts, rates, timings, token totals, confusion matrices,
and privacy-safe model/configuration identities. It must not include private conversation IDs,
titles, excerpts, paths, fingerprints, prompts, references, candidate outputs, judge rationales,
Google project/account identity, credentials, or access tokens.

## Delivery and Commit Ownership

- Leave every change unstaged and uncommitted.
- Do not mark the master plan or ledger accepted.
- Preserve unrelated PM/owner changes.
- The manager validates the implementation and completion report.
- Only the manager stages and commits after validation and an explicit owner request.
