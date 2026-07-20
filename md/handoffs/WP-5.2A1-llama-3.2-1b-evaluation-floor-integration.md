# WP-5.2A1 Handoff: Llama 3.2 1B Evaluation-Floor Integration

## Status

Ready for execution in a separate executor thread.

This is the next work package after accepted WP-5.1.2B. It formalizes the owner's
successful Llama 3.2 1B LM Studio smoke as a pinned, reproducible evaluation-floor
candidate. It must complete before WP-5.2B1 builds the split candidate-generation
and local-scoring harness.

The executor writes code only where the existing implementation cannot meet this
handoff. First inspect and reuse the accepted WP-5.1/WP-5.1.1/WP-5.1.3
infrastructure. Do not add abstractions or model-specific branches merely to make
this package appear larger.

## Objective

Establish `Llama 3.2 1B Instruct` as Chronicle's first formal evaluation-floor
candidate through the existing application-owned LLM client, LiteLLM's LM Studio
provider route, and the accepted four AI-task contracts.

The delivery must:

1. pin the exact local model artifact, quantization, runtime, context, provider
   route, generation settings, and hardware provenance;
2. prove that all four AI tasks reach the local model and terminate as either a
   schema-valid result or an explicit captured model failure;
3. preserve schema-invalid or semantically weak output as a baseline evaluation
   outcome rather than tuning the task prompts to improve this model;
4. prove that synthetic and bounded private-development smokes do not modify the
   live database or frozen WP-5.1.2A snapshot;
5. document a reproducible optional setup without changing the accepted
   Qwen3.5-4B general local-model control;
6. leave a private, machine-readable candidate manifest that WP-5.2B1 can inspect
   when defining its portable generation-package schema.

## Why This Package Is Next

WP-5.2B1 must evaluate a known candidate before it expands into a multi-model
benchmark. Llama 3.2 1B is the approved evaluation floor because it is the smallest
currently downloaded model in the agreed core list and is expected to expose
latency, structured-output, instruction-following, and context limitations clearly.

This package is not expected to prove that a 1B model is good enough for production.
It proves that the evaluation harness will receive honest successes and failures
from a real, fully identified candidate.

## Accepted Preconditions

Treat these as established unless fresh evidence contradicts them:

- WP-5.1 configurable AI-task infrastructure is accepted.
- WP-5.1.1 defines the four production task contracts:
  - `conversation-summary`;
  - `work-mode-classification`;
  - `last-activity`;
  - `title-assessment`.
- WP-5.1.3 established the working LM Studio/LiteLLM boundary, safe diagnostics,
  context checks, schema propagation, and `--verbose` behavior.
- WP-5.1.2A provides a private frozen schema-v3 development snapshot.
- WP-5.1.2B provides 30 frozen conversations and 120 FABLE silver development
  references under git-ignored `.chronicle/eval/dev-v1/`.
- The FABLE references are development labels, not ground truth.
- The owner's current machine is an Intel Core i7-1185G7 system with 31.7 GB RAM,
  Intel Iris Xe integrated graphics, and no NVIDIA runtime.
- LM Studio is installed.
- The owner downloaded:

  ```text
  bartowski/Llama-3.2-1B-Instruct-GGUF
  quantization: Q4_K_M
  reported local size: approximately 807.69 MB
  LM Studio model id: llama-3.2-1b-instruct
  ```

- The intended LiteLLM model route is:

  ```text
  lm_studio/llama-3.2-1b-instruct
  ```

- The intended LM Studio server is loopback-only:

  ```text
  http://127.0.0.1:1234/v1
  ```

- The accepted first baseline uses an 8,192-token configured context, reasoning
  disabled/not applicable, temperature zero, no automatic retry, concurrency one,
  and the task-specific accepted output-token limits.

## Owner Smoke Already Observed

The owner ran the four tasks against one bounded real conversation. The following
is diagnostic context, not acceptance evidence for this handoff:

| Task | Observed outcome |
| --- | --- |
| `conversation-summary` | Schema-valid completion |
| `work-mode-classification` | Schema-valid completion, but semantically questionable and too close to rubric wording |
| `last-activity` | Schema-valid completion, but largely copied a recent source message |
| `title-assessment` | Application-schema failure |

The captured title-assessment response set `title_fits=true` while also returning a
non-null `suggested_title`, and the suggestion exceeded the accepted 3-10 word
limit. This is a useful model-floor result. Do not change the title contract,
finalizer, prompt, or validation to make that output pass.

Do not copy the owner's generated content into tracked files or the completion
report.

## Source Of Truth

Read before changing anything:

- `md/master-plan.md`;
- `md/development-ledger.md`;
- `md/agent-operating-notes.md`;
- `md/handoffs/WP-5.1-yaml-ai-task-runner-litellm.md`;
- `md/handoffs/WP-5.1.1-initial-conversation-intelligence-tasks.md`;
- `md/handoffs/WP-5.1.3-local-lm-studio-ai-task-smoke-fix.md`;
- the corresponding accepted completion reports and validation reviews;
- `md/handoffs/WP-5.1.2A-frozen-private-development-snapshot.md`;
- `md/handoffs/WP-5.1.2B-direct-fable-development-references.md`;
- `ai-models.default.yaml` and its packaged resource;
- `ai-tasks.default.yaml` and its packaged resource;
- `docs/ai-tasks.md`;
- the current AI configuration, client, execution, schema, persistence, and CLI
  modules and tests;
- the private WP-5.1.2A/B manifests and task catalogs under
  `.chronicle/eval/dev-v1/`, without exposing their content in tracked files.

If tracked planning and private manifests disagree, stop and report the exact
privacy-safe discrepancy before running a real-data smoke.

## Worktree And Commit Ownership

The PM worktree may contain pre-existing planning changes, including
`md/master-plan.md`. Preserve them exactly. Do not revert, overwrite, stage, or
commit PM-owned changes.

The PM/manager owns staging and commits. The executor must:

1. implement and validate the handoff;
2. write the detailed completion report;
3. leave every delivery and rework change unstaged and uncommitted;
4. report final `git status --short`;
5. use delivery status `Ready for PM validation`, never `Accepted`.

## Scope

### In Scope

- exact model/runtime/artifact provenance capture;
- a private candidate manifest;
- optional local YAML profile configuration for the Llama candidate;
- direct invented LM Studio and LiteLLM structured-output probes;
- synthetic Chronicle end-to-end smokes for all four tasks;
- one bounded private-development smoke selected without content-based cherry
  picking;
- explicit capture of provider, JSON, application-schema, evidence, and
  cross-field outcomes;
- narrow implementation fixes only if a real integration defect remains;
- focused deterministic tests for any changed behavior;
- an optional Llama evaluation-floor setup section in `docs/ai-tasks.md`;
- privacy-safe completion reporting.

### Out Of Scope

- WP-5.2B1 evaluation runner or scoring code;
- Gemini judge integration;
- confusion-matrix or aggregate benchmark reporting;
- remote candidate execution or transfer packaging;
- running all 120 development cases;
- comparing Llama with Qwen, Phi, Gemma, Gemini Nano, or another candidate;
- prompt tuning, few-shot additions, task-version changes, schema relaxation, or
  finalizer changes;
- auto-correcting invalid model output;
- writing candidate results into the live or frozen source database;
- editing FABLE references;
- creating an untouched final evaluation set;
- downloading another model or changing runtime without owner approval;
- committing model binaries, private configuration, databases, prompts, outputs,
  transcripts, or evaluation artifacts.

## Required Execution Sequence

### 1. Poetry And Worktree Preflight

From the repository root:

```powershell
poetry env info --path
git status --short
git diff --check
```

Poetry must resolve to:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If it resolves elsewhere, stop before every `poetry run` or install command and
follow `md/agent-operating-notes.md`.

Record the starting Git commit and distinguish pre-existing PM changes from this
delivery. Do not clean or reset the worktree.

### 2. Frozen Development Basis Verification

Before using private development data, repeat the non-mutating WP-5.1.2A/B
preflight required by their accepted manifests:

- source snapshot exists and remains ignored;
- recorded snapshot SHA-256 matches a fresh hash;
- no `-wal` or `-shm` sidecar is required;
- `PRAGMA integrity_check` returns `ok`;
- schema version remains 3;
- snapshot counts remain 711 conversations and 28,370 messages;
- frozen selection manifest still resolves to 30 cases;
- all 120 FABLE reference records remain present and unchanged;
- pinned task catalogs still match their recorded hashes;
- no private artifact is tracked.

Do not rewrite the accepted manifests merely to record this run.

### 3. Runtime And Artifact Identification

Verify the existing installation without downloading or replacing anything:

```powershell
lms --version
lms ls
lms server status
(Invoke-RestMethod http://127.0.0.1:1234/v1/models).data.id
```

Start the server or load the already downloaded Llama model if needed using the
installed LM Studio CLI/UI. Keep the bind address at `127.0.0.1`. Do not expose the
server to the LAN.

Identify and record privately:

- exact LM Studio CLI and server version;
- local model id returned by `/v1/models`;
- exact Hugging Face repository/artifact locator;
- GGUF filename;
- GGUF SHA-256;
- byte size;
- architecture and parameter count;
- quantization `Q4_K_M`;
- configured context `8192`;
- runtime execution/device information reported by LM Studio;
- reasoning setting or confirmation that it is not applicable;
- LiteLLM version and route;
- Python version;
- OS and privacy-safe hardware summary.

If the exact artifact file cannot be resolved and hashed, do not invent a hash.
Report the blocker and retain all other provenance. A formal pin requires either
the file hash or a documented, stable LM Studio artifact identifier that resolves
unambiguously to one local file.

### 4. Private Candidate Manifest

Create a machine-readable manifest only under:

```text
.chronicle/eval/dev-v1/candidates/llama-3.2-1b-instruct-q4_k_m/
```

Use JSON or YAML with deterministic UTF-8 serialization. The manifest must include
at least:

- manifest schema/id and creation UTC timestamp;
- logical candidate id;
- display model name;
- LiteLLM provider route;
- LM Studio model id;
- API-base classification (`loopback`) without credentials;
- artifact repository, revision/locator, filename, hash, size, format, and
  quantization;
- runtime name/version and execution provider/device;
- configured and advertised context where known;
- structured-output mode;
- timeout, retries, and concurrency;
- effective temperature and maximum output tokens per task;
- task catalog hash and four task/version/schema/finalizer identities;
- application Git commit;
- Python and LiteLLM versions;
- privacy-safe hardware description;
- pointers to the accepted private snapshot/selection identities by hash, not by
  copied transcript content;
- smoke run ids/statuses and relative artifact locations;
- explicit statement that the candidate is an evaluation floor, not a recommended
  production model.

Absolute paths may exist only in an additional private operator note if required.
Prefer relative paths in the manifest so WP-5.2B1 can later reuse the provenance.
Do not add credentials, prompts, source text, generated text, FABLE outputs, or
chain-of-thought.

This manifest is a private precursor, not the final WP-5.2B1 portable package
schema. Do not add product code that depends on its exact layout unless the handoff
already requires that code for a concrete integration need.

### 5. Dedicated Local Model Profile

Configure a distinct git-ignored local model-profile alias for this candidate.
Do not replace the generic `service-local` profile or the accepted Qwen control.

The effective values must resolve to:

```text
model: lm_studio/llama-3.2-1b-instruct
api_base: http://127.0.0.1:1234/v1
remote: false
api_key_env: null
context_window: 8192
structured_output: true
timeout: 180 seconds, unless measured evidence requires a documented local override
retries: 0
concurrency: 1
temperature: 0
```

Task-level `max_tokens` remains governed by the accepted task catalog. Do not
globally replace those values.

Prefer a private evaluation-specific copy/override of the model/task catalog rather
than repeatedly changing the owner's normal `.chronicle/ai-models.yaml`. Record
which catalog was used and its hash.

If the existing CLI cannot select an alternate configured model profile without
editing the task catalog, use a private copied task catalog that changes only the
four tasks' `model_profile` alias. Do not alter prompt text, selectors, schemas,
versions, finalizers, generation values, or task limits.

### 6. Direct Invented Probes

Before sending private development content, use invented short content to prove:

1. `/v1/models` exposes the intended Llama model;
2. a non-streaming LM Studio chat completion succeeds;
3. a minimal JSON-object response succeeds;
4. a minimal JSON Schema response succeeds or fails with an exact captured
   compatibility category;
5. LiteLLM routes `lm_studio/llama-3.2-1b-instruct` to loopback;
6. LiteLLM passes the exact schema without contacting a remote provider;
7. timeout and provider failures remain privacy-safe and actionable.

Do not treat fluent free text as structured-output success.

### 7. Synthetic Chronicle Smoke

Create a temporary synthetic database with one short invented conversation and
stable message IDs/timestamps. Do not use a committed real transcript.

For each of the four tasks:

1. run `--dry-run --verbose`;
2. record selected character count and estimated request tokens;
3. run the real task through LM Studio;
4. classify the outcome at each boundary:
   - request completed;
   - provider response received;
   - JSON parsed;
   - application schema valid;
   - cross-field constraints valid;
   - evidence IDs valid;
   - deterministic dates valid where applicable;
5. rerun one schema-valid task unchanged to prove cache behavior;
6. run that task once with `--force` to prove append-only attempt behavior.

All four calls must terminate cleanly as a schema-valid success or explicit stored
failure. A model schema failure is acceptable. A traceback, hung request, remote
call, silent correction, or uncategorized provider failure is not acceptable.

### 8. Bounded Private-Development Smoke

Do not run against the live database or the read-only frozen snapshot directly.

Create a disposable writable scratch database under the git-ignored candidate run
directory from the frozen WP-5.1.2A snapshot using SQLite's online backup API.
Record its source snapshot hash and scratch hash privately.

Select exactly one of the already frozen 30 development conversations without
reading content to choose an easy case:

1. use the accepted selection order and selector metadata;
2. choose the case with the smallest accepted input estimate;
3. break ties by frozen selection order;
4. freeze that choice in the private smoke manifest before inspecting output.

Run all four accepted tasks once with `--force` using the dedicated Llama profile.
The generated content remains private. Record only structured status and aggregate
operational evidence in the tracked report.

For every task record privately:

- task/version/schema/finalizer identity;
- selected input fingerprint and counts;
- request/model/runtime identity;
- wall-clock latency;
- token usage if reported;
- JSON/application-schema/evidence/date/cross-field status;
- failure category;
- raw invalid response only when required for diagnosis.

Do not ask the model for chain-of-thought. Do not copy FABLE wording into the
candidate prompt. Do not compare or tune while this baseline run is executing.

### 9. No-Write Verification

After all smokes:

- recompute the frozen snapshot hash and verify it is unchanged;
- verify the live DB fingerprint is unchanged from this package's preflight;
- verify normalized table counts/content fingerprints in the scratch DB match its
  source except for allowed `ai_task_results` and related attempt metadata;
- verify no title, conversation, message, source, project, ingest, or FTS content
  changed;
- verify the synthetic and scratch DBs remain git-ignored;
- verify no model output, private input, or FABLE reference is tracked.

If the live DB changes for any reason during the run, distinguish an external
collector/writer from this work package and report it. Do not overwrite the live DB
to restore a previous state.

## Implementation Rules

### Baseline Integrity

Do not change:

- production task prompts;
- task versions;
- selectors or selection limits;
- output schemas;
- evidence validation;
- DB-owned date finalization;
- title-assessment cross-field rules;
- cache invalidation identity;
- remote-execution guard;
- default search/ingest behavior.

The Llama 1B model is allowed to fail a contract. The product contract is not
allowed to move to accommodate the floor.

### Permitted Narrow Changes

Production changes are permitted only when fresh evidence proves a general
integration defect, for example:

- a provider/runtime provenance field is silently lost;
- a schema-invalid response is mislabeled as provider success;
- a safe error category cannot distinguish transport from schema failure;
- an alternate local YAML profile cannot be selected through the accepted config
  mechanism;
- the CLI crashes instead of persisting an explicit model failure.

Any fix must be provider-general where the defect is general. Do not branch on
`llama-3.2-1b-instruct` in product code.

### Documentation

Update `docs/ai-tasks.md` with a concise optional evaluation-floor subsection that:

- keeps Qwen3.5-4B as the recommended initial functional smoke;
- identifies Llama 3.2 1B `Q4_K_M` as a small evaluation floor;
- gives the verified download locator or command;
- shows how to start/verify LM Studio and select
  `lm_studio/llama-3.2-1b-instruct`;
- states the tested 8,192-token context and local limitations;
- warns that structured validity does not imply semantic quality;
- explains that schema failure is expected benchmark evidence for a floor model;
- does not expose private IDs, paths, outputs, or machine-specific configuration.

Do not expand the main README unless a user-facing setup step cannot be understood
from `docs/ai-tasks.md`.

## Required Automated Tests

No CI test may require LM Studio, a downloaded model, localhost access, or private
data.

If production code or tracked configuration behavior changes, add focused synthetic
tests covering the changed contract. As applicable, cover:

1. alternate local profile selection without prompt/schema mutation;
2. exact `lm_studio/` route and loopback classification;
3. context/timeout/retry/concurrency provenance;
4. structured-output request propagation;
5. schema-invalid output stored as explicit retryable failure;
6. cross-field failure remains distinct from provider/JSON failure;
7. no auto-repair of title-assessment output;
8. cache hit and `--force` append-only behavior;
9. no non-AI command invokes LiteLLM;
10. root/package resource identity if any packaged resource changes;
11. installed-wheel initialization if templates/resources change.

Do not add skips, xfails, OS branches, retries, relaxed assertions, or model mocks
that hide a product regression.

## Acceptance Criteria

WP-5.2A1 is ready for PM validation only when:

1. Poetry resolves to this repository's `.venv`.
2. The frozen WP-5.1.2A snapshot and WP-5.1.2B corpus pass preflight unchanged.
3. The exact Llama GGUF artifact is identified and pinned by hash or an equivalent
   unambiguous local artifact identity.
4. LM Studio runtime, device, context, and model settings are recorded.
5. `lm_studio/llama-3.2-1b-instruct` reaches only the loopback LM Studio endpoint.
6. Direct invented LM Studio and LiteLLM probes establish the structured-output
   behavior.
7. A dedicated private candidate profile resolves the expected model and settings.
8. All four synthetic task calls terminate as schema-valid success or explicit
   captured failure.
9. At least one synthetic task is schema-valid, proving end-to-end integration.
10. One unchanged successful synthetic rerun is a cache hit.
11. One forced successful synthetic rerun appends a new attempt.
12. Exactly one preselected frozen development conversation is run through all four
    tasks on a disposable scratch DB.
13. Every private-development task is accounted for at provider, JSON, schema,
    cross-field, evidence, and date boundaries.
14. The known title-assessment failure is preserved if reproduced; it is not
    auto-corrected or used to weaken the contract.
15. No prompt/task/schema/finalizer version changes are made.
16. No semantic quality claim is made from the smoke.
17. The private candidate manifest contains complete provenance and no credentials.
18. Live and frozen database fingerprints remain unchanged.
19. No private DB, manifest, input, output, reference, model binary, log, path, ID,
    or credential is tracked.
20. Documentation distinguishes the evaluation floor from the Qwen control.
21. Focused tests, full tests, Ruff, help, and `git diff --check` pass.
22. The detailed completion report exists at the exact required path.
23. Nothing is staged or committed.

## Required Validation Commands

Follow `md/agent-operating-notes.md`. Run direct commands rather than fragile
PowerShell pipelines.

```powershell
poetry env info --path
poetry run pytest <focused WP-5.2A1 tests> -q
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
poetry run chronicle --ai-task list
git diff --check
git status --short
git ls-files "*.db" "*.sqlite" "*.zip" "*.jsonl" ".chronicle/*" "exports/*"
```

Also run privacy-safe manual checks for:

- LM Studio model listing;
- direct invented LM Studio structured output;
- direct invented LiteLLM structured output;
- four synthetic Chronicle tasks;
- cache hit and forced append;
- four private-development tasks;
- frozen/live DB no-write;
- private candidate-manifest validation.

Do not paste generated private outputs into the terminal transcript supplied to the
PM. Report statuses and aggregate counts only.

## Required Completion Report

Write the detailed report at exactly:

```text
md/handoffs/reports/WP-5.2A1-completion-report.md
```

The report must include:

1. status: `ready for PM validation`, `partial`, or `blocked`;
2. executive summary;
3. pre-existing owner-smoke evidence versus fresh executor evidence;
4. source-of-truth and frozen-corpus preflight results;
5. files changed and why;
6. exact privacy-safe model artifact identity, hash, size, format, and quantization;
7. runtime/LiteLLM/Python/OS/hardware provenance;
8. effective local profile, context, structured-output, timeout, retry,
   concurrency, and per-task generation settings;
9. direct invented LM Studio and LiteLLM probe outcomes;
10. synthetic four-task outcome matrix with no generated text;
11. cache and append-only evidence;
12. bounded private-development four-task outcome matrix with no private content,
    title, path, URL, UUID, message ID, conversation ID, prompt, reference, or
    generated output;
13. failure-boundary classification for every unsuccessful task;
14. explicit statement that schema-valid output was not treated as semantic
    correctness;
15. explicit statement that the baseline was not prompt-tuned or auto-corrected;
16. private candidate-manifest path stated only relative to `.chronicle`, plus its
    schema/id and validation status;
17. live/frozen/scratch no-write evidence;
18. focused/full/Ruff/help/diff results;
19. Git tracking and privacy evidence;
20. known limitations and precise follow-ups for WP-5.2B1;
21. requirement-by-requirement acceptance checklist;
22. final `git status --short`;
23. confirmation that nothing was staged or committed.

The report may include artifact/model hashes because they are not transcript data.
It must not include private source or generated content.

## Executor Delivery Rules

- Do not stage or commit any file.
- Do not mark the ledger `Accepted`; the PM owns acceptance.
- Do not edit `md/development-ledger.md`; the PM updates status after validation.
- Preserve all pre-existing PM/user worktree changes.
- Keep model binaries and all run artifacts under ignored local storage.
- Do not paste private prompts, transcripts, titles, paths, IDs, FABLE references,
  or model outputs into tracked files or the delivery message.
- Return a concise delivery message pointing to
  `md/handoffs/reports/WP-5.2A1-completion-report.md`.
