# WP-5.2B1 Handoff: Split Candidate Generation And Local Scoring With Gemini Judge

## Status

Ready for execution in a separate executor thread.

This is the next work package after accepted WP-5.2A1. It builds the first
reproducible development-evaluation harness and runs the accepted Llama 3.2 1B
evaluation floor over the frozen 30-conversation x four-task corpus.

The central architectural requirement is non-negotiable:

1. prepare a private candidate-input bundle locally;
2. run candidate generation on a remote or local candidate machine;
3. return a portable candidate-output package;
4. verify and score that package on the owner's local machine;
5. keep FABLE references and judge credentials off the candidate machine.

Candidate generation and scoring must be independently runnable. A convenience
same-machine composition is optional, but it cannot be the only workflow.

## Objective

Implement and exercise a development-only evaluation tool that:

- consumes the accepted private WP-5.1.2A/B corpus without modifying it;
- prepares exactly 120 pinned task requests from 30 frozen conversations and the
  four accepted WP-5.1.1 tasks;
- runs `Llama 3.2 1B Instruct Q4_K_M` through the accepted application-owned LLM
  boundary;
- safely resumes interrupted generation;
- emits a portable, path-independent, hashed candidate package;
- verifies the returned package locally against the frozen corpus;
- calculates deterministic product metrics locally;
- reports the required work-mode confusion matrix;
- optionally and resumably invokes a YAML-configured
  `gemini-2.5-flash` judge through LiteLLM;
- keeps deterministic metrics and judge metrics separate;
- records failures instead of excluding them;
- produces private detailed artifacts and a privacy-safe aggregate report.

This is a development-set evaluation. It is not a final model benchmark and must
not produce publication-grade quality claims.

## Approved Execution Model

### Stage A: Local Preparation

The owner's local machine has:

- the immutable WP-5.1.2A snapshot;
- the frozen WP-5.1.2B selection and 30 selector-input files;
- the 120 FABLE silver references;
- accepted task/prompt/schema/finalizer identities;
- the private development manifest.

Preparation creates a private bundle containing only what the candidate machine
needs to generate 120 candidate outputs.

### Stage B: Candidate Generation

The candidate machine has:

- a repository checkout at the pinned application commit;
- Python/Poetry and the accepted optional enrichment dependencies;
- LM Studio or the selected candidate runtime;
- the exact pinned Llama 3.2 1B `Q4_K_M` artifact;
- the private candidate-input bundle;
- no FABLE references;
- no Gemini credential.

It generates candidate outputs and packages them with complete model/runtime/
hardware provenance.

### Stage C: Local Verification And Scoring

The returned candidate package is copied to the owner's local machine. Local
scoring:

- verifies package and case identities;
- rejects mismatches before scoring;
- uses the local frozen source and FABLE references;
- computes deterministic metrics without a model call;
- calls the configured Gemini judge only when explicitly authorized;
- does not load, contact, or require the candidate model/runtime.

`gemini-2.5-flash` is a cloud API called from a process running locally. Therefore
"local scoring" means the scoring orchestration, source/reference lookup,
deterministic metrics, caching, and reports run on this machine. Judge requests are
remote disclosures and require the existing explicit remote authorization.

## Dependencies And Preconditions

Accepted prerequisites:

- WP-5.1: YAML AI-task runner and LiteLLM model configuration.
- WP-5.1.1: four accepted production task contracts.
- WP-5.1.2A: immutable private development snapshot.
- WP-5.1.2B: 30 frozen inputs and 120 FABLE silver references.
- WP-5.1.3: stable LM Studio/LiteLLM compatibility and diagnostics.
- WP-5.2A1: pinned Llama 3.2 1B evaluation-floor candidate.

The accepted Llama candidate identity is:

```text
candidate: llama-3.2-1b-instruct-q4_k_m
provider route: lm_studio/llama-3.2-1b-instruct
format: GGUF
quantization: Q4_K_M
configured context: 8192
temperature: 0
retries: 0
concurrency: 1
```

Read the exact public artifact identity and hash from the accepted WP-5.2A1 report
and private candidate manifest. Do not duplicate or silently replace it.

The initial judge is selected by a local YAML model-profile alias resolving to:

```text
gemini/gemini-2.5-flash
```

Verify the exact LiteLLM route against the installed LiteLLM version before the
first real judge call. Do not hard-code the provider/model in evaluation logic.
Credentials must come from an environment variable such as `GEMINI_API_KEY`;
never write a key into YAML, a package, a report, a cache, or a log.

## Source Of Truth

Read before changing anything:

- `md/master-plan.md`;
- `md/development-ledger.md`;
- `md/agent-operating-notes.md`;
- all accepted WP-5.1, WP-5.1.1, WP-5.1.2A, WP-5.1.2B, WP-5.1.3, and WP-5.2A1
  handoffs, completion reports, and validation reviews;
- `ai-tasks.default.yaml` and packaged copy;
- `ai-models.default.yaml` and packaged copy;
- current AI config/client/request/schema/finalizer/cache code and tests;
- the ignored WP-5.1.2A/B manifests, selection, inputs, references, and task
  catalogs;
- the ignored WP-5.2A1 candidate manifest and run evidence;
- `pyproject.toml`;
- the master-plan `bench/` development-tool layout.

Do not trust a filename alone. Validate every private source artifact against its
accepted recorded hash before deriving a new bundle.

## Worktree And Commit Ownership

The PM/manager exclusively owns staging and commits.

The executor must:

1. inspect and preserve the existing worktree;
2. implement and validate this handoff;
3. write the required completion report;
4. leave all delivery and rework changes unstaged and uncommitted;
5. report final `git status --short`;
6. use `Ready for PM validation`, never `Accepted`.

Do not edit `md/development-ledger.md`; the PM updates project status after
validation.

## Scope

### In Scope

- a development-only `bench` Python package/module;
- strict Pydantic contracts for evaluation config and package formats;
- local private input-bundle preparation;
- candidate generation from a prepared bundle without DB access;
- resumable/atomic per-case generation;
- portable candidate-package creation and verification;
- deterministic task scoring;
- task-specific Gemini judging of schema-valid outputs;
- local judge caching and resume;
- work-mode confusion matrix including invalid candidate output;
- latency/token/retry/failure accounting;
- private detailed JSON/JSONL/CSV/Markdown reports;
- privacy-safe aggregate reporting;
- synthetic fixtures and deterministic CI tests;
- operator documentation for local and remote stages;
- one complete 120-case Llama development run, including local scoring, once the
  owner provides/approves the candidate machine and private transfer.

### Out Of Scope

- changing AI-task prompts, selectors, task versions, schemas, or finalizers;
- tuning prompts from the first run;
- repairing or retrying invalid model output automatically;
- changing the Llama artifact, quantization, context, or generation policy;
- evaluating Qwen, Phi, Gemma, Gemini Nano, or another candidate;
- building Chrome/Edge/WinRT adapters;
- creating a new teacher/reference corpus;
- human review or manual adjudication;
- combining deterministic and judge metrics into one composite score;
- publishing private cases, outputs, references, titles, IDs, paths, or model
  rationales;
- uploading packages automatically;
- implementing a general remote-job scheduler;
- modifying the live or frozen Chronicle databases;
- writing candidate/judge results into `ai_task_results`;
- creating the later untouched final evaluation set.

## Development Tool Surface

Implement the evaluation harness under the plan's development-only `bench/`
surface. Do not add evaluation commands to the normal end-user `chronicle` CLI in
this work package.

The required command shape is:

```powershell
poetry run python -m bench --help
poetry run python -m bench prepare --config <local-eval-config>
poetry run python -m bench generate --bundle <input-bundle> --config <candidate-config>
poetry run python -m bench verify --package <candidate-package> --config <local-eval-config>
poetry run python -m bench score --package <candidate-package> --config <local-eval-config> --deterministic-only
poetry run python -m bench score --package <candidate-package> --config <local-eval-config> --with-judge --allow-remote --confirm-private-eval
```

An optional same-machine composition may be added:

```powershell
poetry run python -m bench run-local --config <local-eval-config>
```

`run-local` must call the same prepare, generate, verify, and score boundaries. It
must not implement a second in-memory path that bypasses package validation.

Commands must:

- return nonzero on invalid configuration/package/identity;
- print privacy-safe progress and aggregate counts only;
- never print prompts, transcript text, references, candidate output, judge
  rationale, credentials, private IDs, or absolute private paths by default;
- support `--verbose` only for allowlisted configuration/provenance fields;
- produce actionable failures without tracebacks for normal operator errors;
- use deterministic case ordering;
- document whether a path is an input bundle, working directory, candidate
  package, or local scoring directory.

If a slightly different command spelling is materially more consistent with the
implemented parser, document and justify it before implementation. The stage
boundaries and independently runnable behavior may not change.

## Configuration

Add a tracked, privacy-safe evaluation configuration template under `bench/`.
Actual evaluation configuration remains under git-ignored
`.chronicle/eval/dev-v1/config/`.

Use strict Pydantic validation. Reject unknown keys and invalid values.

The local configuration must support:

- corpus root and accepted corpus/selection identity;
- candidate id and model-profile alias;
- candidate generation concurrency, timeout, and retry policy;
- expected task names and versions;
- expected case count 120;
- input-bundle, generation-work, candidate-package, scoring-cache, and report
  locations;
- judge enabled/disabled;
- judge model-profile alias;
- judge rubric version;
- judge temperature and maximum output tokens;
- judge concurrency, timeout, and retry policy;
- privacy confirmation requirement;
- deterministic-only mode;
- report format choices.

Reuse the accepted model-profile schema or a narrow shared loader where practical.
Do not create a second general provider abstraction. Candidate and judge model
profiles must remain external configuration.

Tracked templates must contain:

- no credential;
- no private absolute path;
- no private artifact hash;
- no private case/source ID;
- no transcript or generated content;
- clearly fake/synthetic placeholders where a value is required.

## Stage 0: Environment And Corpus Preflight

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

If it resolves elsewhere, stop before running any Poetry command and follow
`md/agent-operating-notes.md`.

Before preparing a real bundle, validate privately:

- frozen database exists and accepted hash matches;
- `PRAGMA integrity_check` is `ok`;
- schema version and accepted counts match;
- no WAL/SHM dependency;
- selection manifest and 30 inputs match accepted hashes;
- 120 references exist and validate;
- root/private task catalogs match accepted hashes;
- WP-5.2A1 candidate manifest validates;
- live/frozen DB fingerprints are recorded for later no-write comparison;
- all private paths are ignored.

Do not repair, normalize, or rewrite accepted corpus files during preflight.

## Stage 1: Prepare The Private Candidate-Input Bundle

### Preparation Rule

Preparation runs only on the owner's local machine because it needs the frozen
private corpus. It must consume accepted frozen inputs and validate them against
the frozen source. Do not select new conversations and do not recompute a different
30-case sample.

Materialize exactly:

```text
30 conversations x 4 task contracts = 120 candidate cases
```

Case ordering must be:

1. frozen conversation selection order;
2. fixed task order:
   - `conversation-summary`;
   - `work-mode-classification`;
   - `last-activity`;
   - `title-assessment`.

### Case Identity

Give every case a non-semantic private alias such as:

```text
c001--conversation-summary
```

The case fingerprint must hash canonical identities for:

- selected input bytes/content;
- selected normalized evidence-message IDs;
- DB-owned deterministic dates where applicable;
- task name and task version;
- input-selector name/version;
- prompt text/hash;
- provider-schema name/version;
- application-schema name/version;
- finalizer name/version;
- effective temperature and maximum output tokens;
- context/request-construction version.

Do not include the candidate model or judge identity in the case fingerprint.
Those belong to candidate/judge attempt identity so the same cases can be reused.

### Bundle Contents

Create a deterministic archive and an inspectable directory form containing:

```text
bundle-manifest.json
checksums.json
cases/<case-alias>.json
contracts/<versioned-contract-files>
README-private.txt
```

Each case must contain only what the remote generator needs:

- case alias and fingerprint;
- task/request identity;
- complete selected prompt/request content;
- allowed evidence-message IDs;
- deterministic finalizer context;
- provider JSON Schema;
- application validation identity;
- generation settings;
- expected candidate-result envelope version.

The input bundle may contain private selected source content and normalized message
IDs because generation requires them. It must not contain:

- the frozen/live SQLite database;
- FABLE references;
- FABLE outputs or provenance beyond a corpus identity that reveals no content;
- Gemini judge config or credentials;
- non-selected archive content;
- provider export/local-store paths;
- original conversation URLs;
- machine-specific absolute paths;
- unrelated private manifests.

### Deterministic Packaging

Use canonical UTF-8 JSON with stable key ordering and normalized line endings.
Archive file order and archive metadata must be deterministic. Rebuilding the same
bundle from unchanged inputs/config/code must produce:

- identical case fingerprints;
- identical content checksums;
- ideally identical archive bytes/hash.

If archive-byte determinism is not practical across ZIP implementations, define a
canonical content-manifest hash as the authoritative identity and test it across
different temporary roots. Do not pretend a nondeterministic ZIP hash is a corpus
identity.

Print a privacy warning when creating the bundle:

```text
This bundle contains private selected conversation content.
Transfer it only to an owner-approved machine using an owner-approved secure method.
```

Do not implement automatic upload, email, Drive, cloud storage, or remote shell
transfer.

### Transfer Gate

After bundle preparation and local synthetic validation, stop before transferring
real private content unless the owner explicitly confirms:

- the target machine;
- the transfer method;
- who controls the machine;
- where temporary private files will be stored;
- when source bundles will be deleted;
- the exact pinned candidate runtime/artifact is ready.

Record this approval only in a private operator log. Do not put remote machine names,
usernames, IP addresses, paths, or transfer details in tracked reports.

## Stage 2: Candidate Generation

### Remote Independence

`bench generate` must run without:

- the frozen DB;
- the live DB;
- FABLE references;
- Gemini configuration;
- Gemini credentials;
- network access other than the candidate's explicitly configured local runtime.

It must accept the prepared bundle as the complete task-input authority.

### Candidate Runtime Preflight

Before generation, verify:

- application commit/version matches bundle requirement;
- bundle manifest and checksums pass;
- exactly 120 unique expected case fingerprints exist;
- candidate config resolves the accepted Llama profile;
- model artifact identity/hash matches WP-5.2A1;
- quantization/context/generation settings match;
- LM Studio is loopback-only and exposes the intended model;
- no remote fallback/provider is configured;
- available disk space is sufficient;
- output directory is private and not tracked.

Reject a mismatch before the first model call.

### Per-Case Execution

For each case:

1. create an immutable attempt identity from case fingerprint, candidate identity,
   artifact/runtime/config identity, and request settings;
2. write an atomic `running` marker;
3. call the accepted application-owned LLM client;
4. capture provider/model identity and timing;
5. parse JSON;
6. validate provider schema;
7. apply accepted deterministic finalizer behavior;
8. validate application schema, cross-field rules, evidence membership, and
   deterministic dates;
9. record success or the exact failure boundary;
10. atomically replace the running marker with a completed attempt record.

Do not auto-correct, reprompt, or alter a schema-invalid response. The accepted
baseline uses no automatic candidate retry. A transport failure must remain
distinguishable from a model contract failure.

For schema-invalid output, retain the bounded raw response privately in the
candidate package. Raw response files are required evaluation evidence and must be
treated as sensitive.

### Resume

Generation must be interruption-safe:

- completed attempt records with matching full identity are skipped;
- interrupted/incomplete atomic markers are detected and can be retried;
- failures remain completed outcomes by default;
- `--retry-failures` is explicit and creates another attempt rather than replacing
  the first;
- `--force` creates a new run identity rather than mutating the accepted run;
- progress reports expected/completed/success/failed/remaining counts;
- repeated resume cannot duplicate or lose cases.

The first baseline run must preserve first-attempt outcomes. Do not silently choose
the best of multiple generations.

## Stage 3: Portable Candidate Package

### Required Structure

Create a path-independent package containing at least:

```text
candidate-manifest.json
checksums.json
case-accounting.json
results/<case-alias>/attempt.json
raw-invalid/<case-alias>.txt
generation-summary.json
README-private.txt
```

`raw-invalid/` contains files only for cases whose response cannot be represented
as a validated application result.

### Candidate Manifest

Record:

- package schema/version and package id;
- source input-bundle content identity;
- expected/attempted/completed/success/failed counts;
- all 120 case aliases/fingerprints and result-file checksums;
- application commit/version;
- candidate logical id;
- LiteLLM route and resolved provider/model;
- exact GGUF repository/file/hash/size/quantization;
- runtime name/version;
- execution provider/device;
- OS and privacy-safe hardware summary;
- configured/advertised context;
- structured-output mode;
- temperature/output-token settings per task;
- timeout/retry/concurrency;
- UTC run start/end;
- per-case latency and usage availability;
- explicit statement that no FABLE reference or judge result is present.

Do not record credentials or machine-specific absolute paths.

### Package Privacy And Transfer

The candidate package contains derived private output and may contain invalid raw
responses. It remains sensitive even though source transcripts and FABLE references
are excluded.

Create:

- the deterministic package/content identity;
- an archive SHA-256 for transfer-integrity checking;
- a privacy-safe one-line summary the owner can compare before/after copying.

The owner transfers the package back manually. No upload implementation is in
scope.

## Stage 4: Local Verification

`bench verify` must run before any score is computed or judge called.

It must reject:

- malformed or unsupported package schema;
- unsafe archive paths, absolute paths, `..` traversal, or symlink entries;
- checksum mismatch;
- archive/content identity mismatch;
- unexpected, missing, or duplicate cases;
- case fingerprints not matching the local frozen corpus;
- task/prompt/schema/finalizer/config mismatch;
- application commit incompatibility;
- candidate identity/artifact/runtime/config mismatch;
- inconsistent success/failure accounting;
- a valid result that fails local application validation;
- evidence IDs outside the case input;
- deterministic dates that disagree with local source metadata;
- source transcripts or FABLE references found inside the candidate package;
- credentials or known secret-shaped fields.

Verification must not load/contact the candidate runtime and must make zero judge
calls.

Successful verification writes a local import/verification record under the
git-ignored scoring directory. Do not unpack into the repository root.

## Stage 5: Deterministic Local Scoring

Deterministic scoring must run with:

```powershell
poetry run python -m bench score ... --deterministic-only
```

It must make zero LiteLLM/model calls.

### Global Metrics

Report:

- 120 expected cases;
- attempted, completed, schema-valid, and failed counts;
- completion rate;
- JSON parse rate;
- provider-schema validity rate;
- application-schema validity rate;
- cross-field validity rate;
- evidence-membership validity rate;
- deterministic-date validity rate;
- failure counts by boundary and task;
- latency p50/p95 and distribution summary globally and per task;
- token/input/output/total usage when reported;
- missing-usage count;
- retries/attempt count;
- full model/artifact/runtime/context/config provenance.

Do not exclude failures from denominators.

### `conversation-summary`

Deterministically report:

- schema-valid count;
- DB-owned start-date exact validity;
- DB-owned last-active-date exact validity;
- evidence-ID membership validity;
- accepted length/word-limit validity;
- `no_valid_output` count.

Free-text factual coverage and unsupported claims belong to judge scoring.

### `work-mode-classification`

Report a confusion matrix with:

- rows: FABLE reference labels;
- columns: candidate labels;
- labels:
  - `manager`;
  - `executor`;
  - `one_off`;
  - `mixed`;
  - `unknown`;
- one additional candidate column:
  - `no_valid_output`.

Also report:

- exact label agreement;
- total support per FABLE class;
- candidate prediction counts;
- schema-valid and no-valid-output counts;
- per-class recall;
- per-predicted-class precision where defined;
- macro metrics only as separate descriptive values, never as a replacement for
  the matrix.

The matrix must total exactly 30 cases. Invalid/runtime-failed cases go to
`no_valid_output`; they are never dropped.

### `last-activity`

Deterministically report:

- schema-valid count;
- exact agreement for status:
  - `completed`;
  - `awaiting_input`;
  - `in_progress`;
  - `unknown` if allowed by the accepted schema;
- a status confusion matrix including `no_valid_output`;
- evidence-ID membership;
- blocker/next-action field structural validity;
- next-action-basis enum validity;
- `no_valid_output` count.

Do not use string similarity as a substitute for source-grounded semantic judging.

### `title-assessment`

Deterministically report:

- schema-valid count;
- exact `title_fits` agreement;
- title-fit confusion matrix including `no_valid_output`;
- cross-field validity;
- suggestion-presence validity;
- 3-10 word suggestion-limit validity;
- evidence-ID membership;
- `no_valid_output` count.

Do not score exact suggested-title string equality as semantic quality.

### Metric Separation

Do not produce one overall quality score. Keep:

- runtime/reliability;
- deterministic contract validity;
- categorical agreement;
- judge semantic scores

as separate sections and machine-readable namespaces.

## Stage 6: Gemini Judge Scoring

### Authorization And Preflight

Judge scoring requires all of:

```text
--with-judge
--allow-remote
--confirm-private-eval
```

Before the first request, print a privacy-safe summary:

- judge profile alias;
- resolved provider/model;
- number of eligible schema-valid cases;
- number already cached;
- number requiring remote calls;
- rubric version;
- timeout/retry/concurrency;
- confirmation that selected source, candidate result, and FABLE silver reference
  will be sent to Gemini.

Missing credential, unknown model alias, invalid profile, or absent authorization
must fail before sending case content and without traceback.

### Judge Inputs

For each schema-valid candidate case, the judge receives:

- the exact selected frozen source input for that task;
- the FABLE silver reference;
- the schema-valid candidate result;
- the task-specific rubric;
- allowed source message IDs for citations.

Do not send:

- candidate model name, artifact, quantization, runtime, or latency;
- other candidate results;
- the full database;
- unselected conversations;
- provider export paths/URLs;
- credentials;
- previous judge rationale.

Blind candidate identity to reduce brand/model bias.

FABLE is context for expected interpretation, not ground truth. The judge must score
the candidate against the source and rubric, not against wording similarity to
FABLE.

### Judge Output Contract

Use strict structured output validated by code. Every judge result must include:

- case alias/fingerprint;
- task;
- judge status;
- task-specific integer dimension scores;
- concise verdict rationale;
- source evidence-message IDs where required;
- unsupported-claim flag/count where applicable;
- judge profile alias and resolved model recorded outside the blinded prompt;
- rubric/schema version;
- started/completed UTC timestamps;
- latency and usage/cost when reported;
- explicit failure category.

Do not request or store chain-of-thought. Rationale must be a short verdict
explanation, not hidden reasoning.

Use an anchored integer scale, recommended `0-4`, where every value is defined in
the rubric. Do not ask the judge for an unanchored percentage.

### Task-Specific Rubrics

#### Conversation Summary

Score separately:

- factual consistency with selected source;
- material work/outcome coverage;
- unsupported-claim avoidance;
- concise usefulness;
- correct characterization of the conversation rather than recent-turn copying.

Dates remain deterministic and are not judged semantically.

#### Work-Mode Classification

Score separately:

- label support from the conversation as a whole;
- manager/executor/one-off/mixed distinction;
- reason specificity and source support;
- unsupported-claim avoidance.

The deterministic confusion matrix remains the primary label-comparison artifact.

#### Last Activity

Score separately:

- focus on the final meaningful activity;
- status correctness;
- blocker correctness;
- next-action support;
- avoidance of merely copying a source turn;
- unsupported-claim avoidance.

#### Title Assessment

Score separately:

- correctness of `title_fits`;
- fit to dominant conversation activity;
- usefulness and specificity of suggestion when required;
- unsupported-claim avoidance;
- compliance with suggestion-only behavior.

### Judge Cache And Resume

Judge cache identity must include:

- candidate case/result hash;
- local source-input fingerprint;
- FABLE reference hash;
- task/rubric/schema version;
- judge profile and resolved provider/model;
- judge model-config hash;
- generation settings.

Changing judge profile, rubric, source, FABLE reference, or candidate output must
invalidate only affected judge entries. It must not require candidate regeneration.

Judge execution must:

- write attempts atomically;
- resume completed matching results;
- retain explicit failures;
- use bounded concurrency;
- support deterministic-only scoring before credentials are available;
- support later judge completion without recomputing deterministic metrics;
- never overwrite earlier attempts.

## Stage 7: Reports

Write all detailed outputs only under:

```text
.chronicle/eval/dev-v1/runs/<run-id>/
```

Required private outputs:

```text
verification.json
deterministic/case-scores.jsonl
deterministic/metrics.json
deterministic/work-mode-confusion.csv
deterministic/last-activity-status-confusion.csv
deterministic/title-fit-confusion.csv
judge/case-scores.jsonl
judge/metrics.json
reports/aggregate.json
reports/aggregate.md
run-manifest.json
```

The private aggregate report may contain case aliases but must not unnecessarily
repeat source text.

The tracked completion report may contain only privacy-safe aggregates:

- expected/completed/valid/failed totals;
- confusion-matrix aggregate cells without case IDs;
- aggregate latency/token/judge metrics;
- model/runtime/judge/rubric provenance;
- failure categories/counts;
- no private titles, source/provider IDs, paths, URLs, prompts, outputs,
  references, rationales, case aliases, source hashes, or private package hashes.

## Remote Operator Runbook

Add a private-safe documentation section that gives exact commands for:

### Local Preparation

```powershell
poetry run python -m bench prepare --config .\.chronicle\eval\dev-v1\config\evaluation.yaml
```

The command must print:

- bundle location;
- expected 120 cases;
- authoritative bundle/content identity;
- archive transfer hash;
- privacy warning.

### Remote Generation

```powershell
poetry env info --path
lms ls --json
lms server status
poetry run python -m bench generate --bundle <copied-input-bundle> --config <remote-candidate-config>
```

The command must support interruption/resume and print the returned package/hash
when all cases are accounted for.

### Local Verification

```powershell
poetry run python -m bench verify --package <returned-candidate-package> --config .\.chronicle\eval\dev-v1\config\evaluation.yaml
```

### Local Deterministic Scoring

```powershell
poetry run python -m bench score --package <returned-candidate-package> --config .\.chronicle\eval\dev-v1\config\evaluation.yaml --deterministic-only
```

### Local Gemini Scoring

```powershell
$env:GEMINI_API_KEY = "<set in this shell; never save in YAML>"
poetry run python -m bench score --package <returned-candidate-package> --config .\.chronicle\eval\dev-v1\config\evaluation.yaml --with-judge --allow-remote --confirm-private-eval
```

Document cleanup of private input/output bundles on the remote machine after the
owner confirms the returned package was verified. Do not automate deletion without
an explicit operator command and confirmation.

## Implementation Design Rules

- Use structured parsers and Pydantic models, not ad hoc string processing.
- Reuse accepted AI request/schema/finalizer code instead of duplicating task
  semantics.
- Keep evaluation persistence file-based and append-only; do not migrate the
  product DB for benchmark state.
- Use atomic file writes and deterministic serialization.
- Keep package schema versions explicit.
- Treat paths and archive entry names as untrusted during import.
- Avoid machine-specific absolute paths in portable packages.
- Use UTC timestamps.
- Never infer missing case results.
- Never exclude failures from aggregate denominators.
- Never auto-select the best retry.
- Keep candidate generation independent of scoring/reference code.
- Keep judge logic independent of candidate-provider logic.
- Do not initialize LiteLLM during deterministic-only scoring.
- Do not contact any model during package verification.
- Do not add a model-specific branch for Llama where a generic candidate contract
  suffices.

## Required Automated Tests

All committed tests use synthetic content and mocked/injected model responses.
CI must not require LM Studio, Gemini, an API key, private data, or network access.

Add focused coverage for:

### Configuration

1. valid strict config;
2. unknown keys rejected;
3. missing candidate/judge profiles actionable;
4. credentials remain environment-only;
5. local candidate versus remote judge classification;
6. effective model/generation provenance;
7. invalid expected case count or task set rejected.

### Input Preparation

8. fixed conversation/task ordering;
9. case fingerprint includes every required task/input contract identity;
10. model/judge identity excluded from case fingerprint;
11. deterministic rebuild across different temporary root paths;
12. exactly expected case accounting;
13. no references/DB/absolute paths in the input bundle;
14. privacy warning;
15. source/catalog/hash mismatch rejected.

### Generation

16. generation runs with no DB/reference/judge access;
17. accepted client/schema/finalizer reuse;
18. atomic success record;
19. atomic explicit provider failure;
20. invalid JSON/provider schema/application schema/cross-field/evidence/date
    boundaries remain distinct;
21. raw invalid response retained privately;
22. no auto-repair or hidden retry;
23. interruption and resume;
24. failure not retried by default;
25. explicit retry creates another attempt;
26. package contains all successes and failures;
27. full candidate provenance.

### Package Security And Verification

28. path-independent package;
29. checksum/content-identity validation;
30. missing/extra/duplicate case rejected;
31. mismatched case fingerprint rejected;
32. mismatched task/prompt/schema/finalizer rejected;
33. mismatched candidate/artifact/config rejected;
34. archive path traversal/absolute path/symlink rejected;
35. source transcript/reference/credential leakage rejected from candidate
    package;
36. verify makes zero model calls.

### Deterministic Scoring

37. all cases remain in denominators;
38. invalid output maps to `no_valid_output`;
39. work-mode confusion matrix axes/order and total;
40. work-mode exact agreement/support/precision/recall;
41. last-activity status matrix and total;
42. title-fit matrix and total;
43. summary date/evidence/length metrics;
44. latency p50/p95;
45. missing usage handled explicitly;
46. deterministic-only makes zero LiteLLM calls;
47. no composite score emitted.

### Judge

48. three authorization flags required;
49. missing credential fails before content transmission;
50. candidate identity absent from judge prompt;
51. source/FABLE/candidate/rubric present only for eligible case;
52. schema-invalid candidate skipped and counted;
53. task-specific structured rubrics;
54. judge output schema/rationale/evidence validation;
55. no chain-of-thought field;
56. cache hit/resume;
57. cache invalidation by candidate/reference/source/rubric/judge identity;
58. changing judge does not invoke candidate generation;
59. judge failures retained and reported;
60. no private text printed by default.

### Regression And Packaging

61. normal `chronicle` commands remain unchanged and zero-LLM;
62. `python -m bench --help` works;
63. full suite and Ruff remain clean;
64. no private fixture/artifact tracked;
65. Windows and Linux path behavior covered.

## Manual Validation Sequence

### Phase 1: Synthetic Implementation Validation

Before private transfer:

- prepare a synthetic 2-conversation x four-task bundle;
- run generation using injected responses;
- interrupt and resume;
- package and copy it between two different temporary roots;
- verify and deterministically score it;
- run mocked judge scoring;
- prove candidate generation and scoring are process-separated;
- prove scoring works when candidate runtime is unavailable.

### Phase 2: One-Case Real Boundary Smoke

Using the private corpus locally:

- prepare the real bundle;
- select one case by frozen order, not content;
- run candidate generation;
- package/copy/verify it through separate directories;
- score deterministic-only;
- run one explicitly authorized Gemini judge case;
- inspect detailed private artifacts;
- confirm no source/reference/output appears in tracked files or default terminal
  output.

Do not proceed to full remote transfer until this smoke and the owner transfer gate
pass.

### Phase 3: Full 120-Case Candidate Run

On the owner-approved candidate machine:

- verify pinned environment/artifact;
- generate all 120 cases;
- preserve first-attempt outcomes;
- resume interruptions;
- create the final candidate package;
- compare transfer hash before/after copy;
- do not delete remote artifacts until local verification succeeds.

### Phase 4: Full Local Scoring

On the owner's local machine:

- verify the returned package;
- score deterministic-only;
- inspect accounting and confusion matrices;
- run/resume Gemini judging for every schema-valid candidate case;
- ensure schema-invalid cases are skipped by judge but retained in all reliability
  denominators;
- write private final reports;
- confirm live/frozen DB fingerprints unchanged.

If the remote machine or Gemini credential is not available, complete
implementation and synthetic validation but report status `partial`, not
`Ready for PM validation`. State the exact owner-controlled gate.

## Acceptance Criteria

WP-5.2B1 is ready for PM validation only when:

1. Poetry resolves to the repository `.venv`.
2. Frozen snapshot, selection, inputs, references, catalogs, and WP-5.2A1
   candidate provenance validate unchanged.
3. The development-only `bench` CLI exposes independently runnable prepare,
   generate, verify, and score commands.
4. A tracked privacy-safe config template and strict loader exist.
5. Preparation produces exactly 120 pinned case fingerprints.
6. The private input bundle contains required selected input but no DB or FABLE
   reference.
7. Real private transfer occurred only after explicit owner approval.
8. Candidate generation runs without DB, FABLE, or Gemini access.
9. The exact accepted Llama artifact/runtime/settings are enforced.
10. Generation is atomic, resumable, and failure-preserving.
11. Every expected case has a success or explicit first-attempt failure.
12. Candidate package contains no source transcript, FABLE reference, credential,
    or machine-specific absolute path.
13. Candidate package has canonical content identity and transfer hash.
14. Local verification rejects every defined mismatch/security case.
15. Local scoring runs with the candidate runtime absent/unreachable.
16. Deterministic-only scoring makes zero model calls.
17. All 120 cases remain in deterministic denominators.
18. Work-mode confusion matrix totals 30 and includes `no_valid_output`.
19. Last-activity and title-fit matrices total 30 each and include invalid output.
20. Summary date/evidence/length and global schema/failure metrics reconcile.
21. Latency p50/p95 and available usage are reported separately by task.
22. No composite quality score is emitted.
23. Judge profile is external YAML and resolves initially to
    `gemini-2.5-flash` through LiteLLM.
24. Gemini credentials remain environment-only.
25. Judge calls require explicit remote/private authorization.
26. Candidate identity is blinded from judge prompts.
27. Every schema-valid case has a schema-valid judge result or explicit judge
    failure; schema-invalid candidates are not semantically judged.
28. Judge cache/resume and identity invalidation work.
29. Changing judge profile/rubric does not regenerate candidate output.
30. Deterministic and judge metrics remain separate.
31. Detailed artifacts remain under ignored `.chronicle/eval/dev-v1/runs/`.
32. Tracked reports contain privacy-safe aggregates only.
33. Live and frozen database fingerprints remain unchanged.
34. No private artifact, model binary, credential, DB, input, output, reference,
    case ID, path, or package is tracked.
35. Focused tests, full tests, Ruff, help, and `git diff --check` pass.
36. Windows and Linux CI-compatible tests require no model/network/private data.
37. Operator documentation covers local preparation, remote generation, return
    transfer, local verification, deterministic scoring, judge scoring, and remote
    cleanup.
38. The detailed completion report exists at the required path.
39. Nothing is staged or committed.

## Required Validation Commands

Follow `md/agent-operating-notes.md`.

```powershell
poetry env info --path
poetry run pytest <focused WP-5.2B1 tests> -q
poetry run pytest
poetry run ruff check .
poetry run python -m bench --help
poetry run python -m bench prepare --help
poetry run python -m bench generate --help
poetry run python -m bench verify --help
poetry run python -m bench score --help
poetry run chronicle --help
poetry run chronicle --ai-task list
git diff --check
git status --short
git ls-files ".chronicle/*" "*.db" "*.sqlite" "*.zip" "exports/*"
```

Also report privacy-safe aggregate evidence for:

- deterministic bundle rebuild;
- synthetic cross-directory/cross-stage run;
- interruption/resume;
- one-case private boundary smoke;
- owner-approved 120-case candidate run;
- transfer hash verification;
- local scoring with candidate runtime unavailable;
- deterministic-only zero-model behavior;
- Gemini authorization/cache/resume;
- confusion-matrix reconciliation;
- frozen/live no-write.

## Required Completion Report

Write the detailed report at exactly:

```text
md/handoffs/reports/WP-5.2B1-completion-report.md
```

The report must include:

1. status: `ready for PM validation`, `partial`, or `blocked`;
2. executive summary;
3. implementation architecture and files changed;
4. exact command surface;
5. config schema and credential boundary;
6. input-bundle schema, content rules, and deterministic identity;
7. candidate-generation state machine and resume behavior;
8. candidate-package schema and privacy boundary;
9. local verification rules;
10. deterministic metrics and denominators;
11. work-mode confusion matrix with aggregate cells only;
12. last-activity status and title-fit aggregate matrices;
13. judge model/profile/rubric/schema provenance;
14. judge authorization, blinding, caching, resume, and failure behavior;
15. candidate-generation aggregate totals and failure categories;
16. local deterministic aggregate results;
17. local judge aggregate results and coverage;
18. latency/token/usage aggregates;
19. proof that no composite score was produced;
20. proof scoring ran without the candidate runtime;
21. private transfer approval and cleanup status without machine/path details;
22. frozen/live no-write evidence without private hashes;
23. focused/full/Ruff/help/diff validation;
24. Git privacy/tracking evidence;
25. known limitations and WP-5.2A5/B2 follow-ups;
26. requirement-by-requirement acceptance checklist;
27. final `git status --short`;
28. confirmation nothing was staged or committed.

Do not include:

- conversation/message/source IDs;
- case aliases;
- private hashes or package IDs;
- titles, URLs, paths, prompts, source excerpts;
- candidate/FABLE/judge outputs or rationales;
- credentials or remote machine details.

## Executor Delivery Rules

- Do not stage or commit anything.
- Do not mark the ledger `Accepted`.
- Do not edit the ledger.
- Preserve all PM/user/pre-existing worktree changes.
- Keep every real input/output/package/cache/report under ignored local storage.
- Do not transfer real private data until the owner explicitly approves the target
  and method.
- Do not run a full Gemini judge batch without the required authorization flags.
- Do not paste private content into the delivery message.
- Return a concise delivery message pointing to
  `md/handoffs/reports/WP-5.2B1-completion-report.md`.
