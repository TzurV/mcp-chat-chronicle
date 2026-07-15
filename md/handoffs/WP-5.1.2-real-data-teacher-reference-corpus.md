# WP-5.1.2 Handoff: Real-Data Teacher-Reference Corpus

## Status

Planned and dependency gated.

Do not execute this work package until:

1. WP-5.1 has been PM-accepted.
2. WP-5.1.1 has finalized and implemented the four task names, input selectors, prompt versions, and Pydantic output contracts.

This file is the complete executor instruction for WP-5.1.2. Do not infer additional product AI features or local-model benchmark scope from the broader roadmap.

## Objective

Build a private, reproducible evaluation corpus from the owner's real conversations already stored in the repo-local Chronicle database. Generate structured reference outputs for every WP-5.1.1 AI task with two explicitly authorized strong remote teacher models:

- GPT-5.6 Sol;
- Claude Fable 5.

The result is a **teacher-reference corpus** or **silver benchmark**. It is not human-verified ground truth. The owner has decided that there will be no human review or adjudication in this phase.

The corpus will later be consumed by WP-5.2 to compare configurable local models and prompt variants. WP-5.1.2 creates and freezes the corpus and reference provenance; it does not run or rank the local-model matrix.

## Approved Decisions

The following decisions are approved and must not be reopened inside execution:

1. Real private conversation data may be sent to the approved remote teacher APIs for this development/evaluation purpose.
2. Remote transmission remains explicit, bounded, logged locally, and disabled by default in generic tooling.
3. No human review is planned for this phase.
4. Teacher outputs are silver references, not ground truth.
5. Unresolved teacher disagreements remain labeled and are excluded from the primary benchmark score.
6. Run a 30-conversation pilot before expanding to a 300-conversation corpus.
7. The full corpus split is 150 development, 50 validation, and 100 frozen holdout conversations.
8. All four WP-5.1.1 tasks run against the same selected conversation set, yielding up to 1,200 task cases.
9. Canonical evaluation state lives in a separate local SQLite database under `.chronicle/eval/`, not in the product database.
10. Private corpus data, source mappings, teacher requests/responses, candidate predictions, and private reports are never committed.
11. Generic corpus tooling, schemas, privacy-safe templates, synthetic fixtures, tests, and aggregate-only documentation may be committed.
12. WP-5.2 will compare zero-shot and few-shot task variants. Few-shot examples may only come from the development split.

## Dependency Stop Check

Before editing code, read the accepted artifacts for WP-5.1 and WP-5.1.1.

Stop and report `blocked` if either dependency is not accepted or if any of the following is still undefined:

- the exact four task names;
- task versioning rules;
- code-owned selector names;
- code-owned output schema names and versions;
- deterministic date handling;
- evidence/message-range fields;
- model-profile resolution through the WP-5.1 LiteLLM boundary.

Do not create substitute prompts or schemas in the benchmark package to work around an unfinished WP-5.1.1.

## Source Of Truth

Read before implementation:

- `md/master-plan.md`, M5;
- `md/development-ledger.md`;
- `md/agent-operating-notes.md`;
- `md/handoffs/WP-5.1-yaml-ai-task-runner-litellm.md`;
- accepted `md/handoffs/reports/WP-5.1-completion-report.md` and validation review;
- accepted WP-5.1.1 handoff, completion report, and validation review;
- `ai-tasks.default.yaml` and `ai-models.default.yaml` as accepted after WP-5.1/WP-5.1.1;
- the accepted AI runner, task configuration, selector, schema, cache, and LLM-client modules;
- the current product DB module and schema, for read-only access only.

Relevant external references:

- LiteLLM OpenAI-compatible endpoints: <https://docs.litellm.ai/docs/providers/openai_compatible>
- GPT-5.6 Sol: <https://developers.openai.com/api/docs/models/gpt-5.6-sol>
- Claude Fable 5: <https://www.anthropic.com/claude/fable>
- OpenAI API data controls: <https://platform.openai.com/docs/models/default-usage-policies-by-endpoint>
- Anthropic API retention: <https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data>
- Claude Fable covered-model retention: <https://privacy.claude.com/en/articles/15425996-data-retention-practices-for-covered-models>

Provider documentation is temporally unstable. Verify current model IDs, structured-output support, storage controls, and retention rules immediately before the first remote call. Record the verification date and direct documentation links in the local audit record and privacy-safe completion report.

## Data Boundaries

### Product Source Database

The source is the owner's real configured Chronicle database, normally:

```text
.chronicle/chronicle.db
```

Requirements:

- resolve the effective source DB through accepted project configuration rather than hard-coding a private absolute path;
- open the source DB in SQLite read-only/query-only mode;
- never run product schema migration against it from evaluation tooling;
- never add evaluation tables, task results, locks, timestamps, or audit rows to it;
- capture a source fingerprint before and after corpus creation and prove that evaluation tooling did not mutate it;
- tolerate normal WAL/SHM behavior from another application without claiming byte-for-byte identity where SQLite itself changes sidecar state;
- fail clearly if a consistent read-only snapshot cannot be obtained.

### Private Evaluation Root

Default local layout:

```text
.chronicle/eval/
  eval-config.yaml
  eval.db
  artifacts/
    teacher/
      <teacher-run-id>/
        requests.jsonl
        responses.jsonl
    candidate/
      <candidate-run-id>/
        predictions.jsonl
  audit/
    remote-disclosures.jsonl
  reports/
  exports/
```

The exact internal module/file decomposition may follow existing repository patterns, but this data boundary is mandatory.

The whole private root must be ignored by Git. Do not rely only on convention: verify it with `git check-ignore` and prove that no file below it appears in `git ls-files`.

### Tracked Versus Untracked Deliverables

Tracked deliverables may include:

- generic `bench/` corpus, teacher-run, reconciliation, and reporting code;
- a privacy-safe evaluation configuration template with placeholders only;
- independent eval-database schema/migrations;
- synthetic source/evaluation fixtures;
- deterministic unit and CLI tests;
- aggregate-only documentation;
- the required completion report.

Never track:

- `eval.db` or SQLite sidecars;
- real source conversation IDs or mappings;
- real titles, URLs, UUIDs, snippets, prompts, messages, summaries, or suggested titles;
- teacher request or response JSONL;
- candidate predictions derived from real conversations;
- API keys, private model endpoint configuration, account identifiers, or billing data;
- private reports containing case-level content;
- ZIP/JSON/JSONL exports copied from the real sources.

## Canonical Evaluation Database

Use a separately versioned SQLite database at `.chronicle/eval/eval.db`. Use structured columns and JSON serialization through standard parsers; do not encode relational data through ad hoc string formats.

The schema must represent at least the following entities. Names may be adjusted to established repository conventions, but the information and relationships are required.

### `corpora`

- corpus ID and immutable corpus version;
- creation timestamp;
- source DB fingerprint and product schema version;
- deterministic selection seed;
- requested and actual conversation counts;
- selection/split configuration and canonical hash;
- task catalog hash;
- status: draft, pilot, frozen, superseded;
- freeze timestamp.

### `eval_conversations`

- opaque evaluation conversation ID;
- corpus foreign key;
- private source conversation ID mapping;
- provider;
- source content hash;
- normalized metadata snapshot needed by selectors;
- start and last-active dates from the DB;
- message count/input-size bucket;
- selection strata;
- split: development, validation, holdout;
- exclusion/quarantine state and reason.

Do not expose product IDs through report-facing identifiers. Generate opaque stable IDs within the corpus.

### `eval_cases`

- opaque case ID;
- evaluation conversation foreign key;
- task name and task version;
- selector name/version;
- prompt and schema name/version/hash;
- immutable normalized input JSON snapshot;
- input hash;
- selected message IDs or sequence range;
- truncation/omission evidence;
- split and case status.

The frozen input snapshot is the exact payload basis later used for teacher and candidate comparison. Candidate runs must not silently reselect newer source messages.

### `teacher_runs`

- run ID;
- logical model profile;
- provider and requested model ID;
- actual/resolved model ID or provider response metadata when available;
- model snapshot/version when supported;
- task/prompt/schema/config hashes;
- temperature, reasoning-effort, max-token, timeout, and retry settings;
- start/end timestamps;
- storage/retention settings and acknowledgement;
- aggregate input/output tokens, latency, and cost when available;
- status and bounded failure summary.

### `teacher_outputs`

- case and teacher-run foreign keys;
- raw response location/hash;
- parsed validated output JSON;
- schema validity and repair/retry count;
- evidence validation state;
- timing and usage;
- failure category/detail;
- created timestamp.

### `references`

- case foreign key;
- reference status: `teacher_agreement`, `machine_reconciled`, `teacher_disagreement`, or `invalid`;
- canonical structured reference JSON when usable;
- deterministic fields copied from the source DB;
- agreement/reconciliation details;
- confidence/calibration metadata where defined;
- evidence message IDs/range;
- teacher-output provenance;
- eligibility for primary scoring.

### `reconciliation_runs`

- reconciliation run/model/config identity;
- anonymized candidate-order seed;
- input and output hashes;
- reciprocal judge decisions;
- convergence/disagreement state;
- usage, cost, and latency.

### `candidate_runs`, `predictions`, And `scores`

Create the schema needed for WP-5.2, but do not run the local-model matrix here.

Record separately:

- logical model family and exact artifact/version;
- quantization;
- runtime and runtime version;
- execution provider/device;
- endpoint profile;
- hardware snapshot;
- prompt variant;
- generation settings;
- per-case outputs, validity, latency, throughput, and scores.

This separation is mandatory so LM Studio-versus-Foundry comparisons are not mislabeled as model-quality comparisons.

### `remote_disclosures`

- disclosure/run ID;
- owner authorization reference and timestamp;
- allowed providers/models;
- selected case IDs and aggregate count;
- fields sent;
- payload hashes;
- secret-scan outcome and exclusions;
- API mode/storage flags;
- documented retention policy and verification date;
- estimated and actual tokens/cost;
- transmission timestamp and final status.

The disclosure record is private and local.

## Corpus Selection

### Determinism

Selection must be reproducible from:

- source DB fingerprint;
- corpus version;
- canonical selection configuration;
- fixed seed, defaulting to `20260715` unless locally overridden before the corpus is frozen.

Rerunning selection with unchanged inputs must produce the same conversation IDs, split assignment, and case hashes.

Any later selection or prompt/schema/input change creates a new corpus or case version. Never mutate a frozen holdout in place.

### Deduplication

Deduplicate exact normalized conversation content hashes before sampling, including cross-provider copies where the visible message content is identical.

Do not use title alone, provider ID alone, or approximate semantic similarity to delete cases. Record duplicate groups locally and keep one deterministic representative.

### Stratification

Sample across:

- ChatGPT, Claude, OpenAI Codex, and Claude Code when eligible records exist;
- conversation size/message-count buckets;
- recent, middle, and older activity periods;
- titled, untitled, and obvious placeholder-title states;
- full-input versus selector-truncated cases;
- English and other detected languages when enough data exists.

Do not stratify on teacher labels before reference generation. Work-mode and teacher-assessed title quality become reporting strata after labeling.

For minority providers with fewer records than the intended provider allocation, include all eligible unique records before filling remaining slots from larger providers. Do not duplicate minority records to balance counts. Mark provider-level results with fewer than 30 conversations as descriptive/low-N.

### Pilot And Full Corpus

Pilot:

- 30 unique conversations;
- drawn from the future development split;
- all four tasks, up to 120 cases;
- representative provider/length/recency coverage;
- frozen as an identifiable pilot version.

Full corpus:

- 300 unique conversations after deduplication and secret quarantine;
- 150 development;
- 50 validation;
- 100 holdout;
- all four tasks, up to 1,200 cases.

If fewer than 300 eligible unique conversations remain, do not duplicate or weaken privacy controls. Stop expansion, record the actual eligible count, and return `partial` for PM disposition.

## AI Task Coverage

Create a case for each accepted WP-5.1.1 task.

### `conversation-summary`

Reference data must separate:

- deterministic `start_date` and `last_active_date` copied from DB metadata;
- concise summary;
- structured factual units/claims;
- supporting message IDs or sequence ranges;
- unsupported or uncertain claims identified during reconciliation.

Do not score dates through an LLM judge. Later evaluation compares them exactly.

### `work-mode-classification`

Use only the accepted labels:

- `manager`;
- `executor`;
- `one_off`;
- `mixed`;
- `unknown`.

Persist label, confidence if the accepted schema contains it, concise evidence, and supporting message IDs/range. Exact teacher-label agreement is directly measurable. A disagreement that cannot be reconciled remains unresolved.

### `last-activity`

Persist structured fields for:

- recent work/activity;
- current status;
- blockers;
- likely next action;
- evidence message IDs/range;
- selector/truncation metadata.

The reference must be based only on the accepted recent-meaningful-turn selector. It must not use hidden tool/reasoning/system data that the product task excludes.

### `title-assessment`

Persist:

- the source title privately;
- title-fit classification;
- concise reason/evidence;
- one or more acceptable suggested titles when a replacement is warranted;
- no-change state when the title is adequate.

Do not modify the product title. Free-form suggested titles will later be scored by rubric/relevance, not exact string equality.

## Remote Teacher Configuration

Use model profiles resolved through the accepted WP-5.1 LiteLLM/application-owned boundary. Do not add provider SDK calls directly to benchmark code.

Default teacher profiles:

- OpenAI GPT-5.6 Sol, requested API model `gpt-5.6-sol` unless current official documentation requires a pinned snapshot identifier;
- Anthropic Claude Fable 5, requested API model `claude-fable-5` unless current official documentation requires a pinned snapshot identifier.

Requirements:

- configure profiles locally; never track credentials or private endpoint/account data;
- use provider APIs, not consumer chat interfaces;
- prefer immutable model snapshots when available;
- otherwise record requested ID, returned/resolved ID, call date, and configuration hash;
- use structured outputs supported by the accepted WP-5.1 runner;
- make generation parameters explicit and reproducible;
- use low-variance settings appropriate to reference generation;
- cache successful outputs by exact case/task/prompt/schema/resolved-model/settings identity;
- retries must be bounded and recorded;
- reruns must resume without paying for successful unchanged cases again.

Do not use provider Files, Assistants, persistent threads, Batch, or other stateful/storage features unless separately approved. For OpenAI calls, set `store=false` where supported. Record Anthropic's current Fable retention terms before transmission.

## Remote Privacy And Cost Gate

The owner's authorization in this handoff permits the approved bounded teacher runs. It does not authorize arbitrary providers, models, case counts, storage modes, or unlimited spend.

Before any remote transmission, generate a privacy-safe dry-run summary containing only aggregates:

- corpus/pilot version;
- case count by task/provider/split;
- excluded/quarantined count by reason;
- estimated input/output tokens and estimation method;
- estimated cost by provider/model;
- configured maximum cases/tokens/cost;
- provider/model allowlist;
- retention/storage acknowledgement;
- request count including worst-case retries/reconciliation;
- confirmation that no content will print to the terminal or completion report.

Remote execution must require both explicit CLI intent flags, equivalent to:

```text
--allow-remote --confirm-private-eval
```

It must also require local configured ceilings for:

- maximum cases;
- maximum request count;
- maximum input characters/tokens per case;
- maximum output tokens;
- maximum estimated cost in the configured currency;
- timeout/retry count.

Fail before the first remote call if the estimate exceeds any ceiling.

### Secret Quarantine

Run a conservative high-confidence scan before remote transmission for obvious credentials and secrets such as API keys, access tokens, private keys, passwords in credential-like assignments, and known provider token formats.

When a case is flagged:

- do not silently redact and continue, because the teacher and candidate would then see different or semantically damaged inputs;
- quarantine the case locally;
- record only a private reason/category;
- replace it deterministically from the same sampling stratum when possible;
- never print the matched secret or surrounding transcript.

Avoid broad entropy-only rules that would quarantine ordinary UUIDs or code indiscriminately. Tests must cover true positives and common false-positive identifiers.

## Teacher Agreement And Reconciliation

Run both teachers independently from the same frozen case input. Do not expose one teacher's answer to the other during initial generation.

Preserve both original validated outputs even when they agree.

### Direct Agreement

Use deterministic comparisons where valid:

- exact deterministic dates;
- exact classification label;
- exact title-fit/no-change state;
- schema-required status enums;
- normalized evidence ID/range overlap.

For generative fields, do not require exact wording. Compare structured factual units, required-field coverage, evidence support, and contradictions.

### Automated Reconciliation

Only cases that do not meet direct-agreement rules enter reconciliation.

Use bounded, provenance-recorded automated reconciliation. Preferred method:

1. Present anonymized output A/B in randomized order with the frozen source evidence and a task-specific rubric.
2. Ask both configured strong teachers independently to judge or produce a structured merged reference.
3. Validate that proposed factual units are supported by recorded source message IDs/range.
4. Mark `machine_reconciled` only when the reciprocal decisions converge and the merged output validates.
5. Otherwise mark `teacher_disagreement`.

Do not identify which provider produced A or B to the reciprocal judge. Record order randomization and all reconciliation model/config hashes.

No third model or human silently converts an unresolved case into certainty. A future WP may add human gold labels without changing this corpus version.

### Primary Benchmark Eligibility

Eligible:

- `teacher_agreement`;
- `machine_reconciled` with valid evidence.

Not eligible for primary quality scores:

- `teacher_disagreement`;
- invalid or missing teacher output;
- quarantined input;
- evidence validation failure.

WP-5.2 must publish eligible-case coverage and disagreement rates beside every model score.

## Pilot Gate

Do not expand from 30 to 300 conversations unless the pilot demonstrates all of the following:

1. Source DB remained read-only.
2. Selection and case hashes reproduce exactly.
3. All four tasks are represented.
4. Each teacher achieves at least 95% schema-valid outputs after bounded retries.
5. Deterministic date fields are 100% populated and exact.
6. At least 80% of non-quarantined cases are eligible for primary scoring after reconciliation.
7. Classification label agreement is reported; if direct agreement is below 80%, stop for prompt/schema review rather than hiding it through reconciliation.
8. Every teacher call has model/config/usage/latency provenance.
9. Actual and projected full-corpus cost remain inside the locally configured ceiling.
10. No private content appears in tracked files, terminal evidence, Git diff, or completion-report text.
11. Resume/cache behavior prevents duplicate paid calls for unchanged successful cases.
12. Provider retention/storage controls are verified and recorded.

If any gate fails, do not start the 300-conversation run. Return `partial` with privacy-safe aggregate evidence and the exact remediation needed.

No human review is required to pass the pilot. Human review must not be presented as performed.

## Full-Corpus Freeze

After the pilot gates pass and the configured full-run ceiling permits execution:

1. Build the deterministic 300-conversation selection.
2. Freeze inputs and split assignment before any local candidate model is run.
3. Generate/resume both teacher outputs for all cases.
4. Reconcile disagreements under the bounded rules above.
5. Mark the corpus frozen and immutable.
6. Produce a private case-level report under `.chronicle/eval/reports/`.
7. Produce a privacy-safe aggregate readiness summary for the completion report.

Any later task prompt, selector, schema, source selection, or reference-policy change creates a new corpus version. Never rewrite the frozen holdout to improve a model result.

## WP-5.2 Model Registry Preparation

WP-5.1.2 must leave the evaluation schema/configuration ready for arbitrary LiteLLM model profiles. Do not hard-code a three-model limit.

Recommended core same-size cohort for WP-5.2:

1. Qwen3.5-4B;
2. Phi-4-mini-instruct;
3. Gemma-3-4B-it.

Recommended extended candidates:

- Llama 3.2 3B Instruct;
- SmolLM3 3B;
- a currently available pinned Ministral 3B-class instruct artifact;
- Qwen3.5-9B as an optional quality ceiling if local throughput is acceptable.

Model selection is configuration. Record model family separately from artifact, quantization, runtime, execution provider, and endpoint.

Prepare for a same-model runtime comparison where technically valid:

- LM Studio OpenAI-compatible endpoint;
- Microsoft Foundry Local OpenAI-compatible endpoint.

Do not treat Edge Phi-4-mini, Edge Aion-1.0-Instruct, Chrome Gemini Nano, or Phi Silica as ordinary LiteLLM HTTP profiles. They require later browser/WinRT adapters and are outside WP-5.1.2.

## Prompt Variant Preparation

The evaluation structure must support at least:

- `zero_shot`;
- `few_shot`.

Few-shot examples:

- are task-specific and externally configured;
- come only from the development split;
- are versioned and hashed as part of the prompt identity;
- never use validation or holdout examples;
- must not contain exposed private content in tracked defaults;
- may be generated locally into the private eval root for real-data runs.

Do not request or persist exposed chain-of-thought. Use concise rationale and explicit evidence fields defined by the task schema.

WP-5.1.2 only prepares and validates this structure. WP-5.2 executes the zero-shot/few-shot local-model matrix.

## Implementation Constraints

- Reuse accepted WP-5.1 task loading, selector, schema validation, cache identity, and LLM-client boundaries.
- Do not add direct provider SDK coupling around LiteLLM.
- Do not add evaluation behavior to normal `search`, `recent`, `stats`, `collect`, `open`, or ingest paths.
- Prefer development-only `bench` entry points rather than expanding the end-user CLI without an approved product command.
- Use Pydantic/YAML/SQLite structured APIs, not regex/string-built configuration or SQL.
- Parameterize SQL.
- Bound all input sizes, outputs, retries, concurrency, and queues.
- Default concurrency conservatively for expensive remote calls and make it configurable.
- Ctrl+C must leave committed eval rows consistent and rerunnable.
- A failed case must not invalidate successful cases.
- A teacher/config change must invalidate only the affected cache identity.
- Never print real prompts/responses by default, including in exception traces.
- Logs and completion evidence use opaque case/run IDs and aggregate counts.

## Required Tests

Use synthetic conversations and mocked/injected teacher clients for committed tests. No committed test may open the owner's real DB or call a remote API.

Cover at least:

1. Evaluation schema creation and forward migration independent of the product DB.
2. Product source DB opened read-only and unchanged.
3. Deterministic seeded sampling and split assignment.
4. Exact-content deduplication across providers.
5. Minority-provider inclusion without duplicated cases.
6. Stable opaque eval IDs and input hashes.
7. All four task cases created from accepted selectors/schemas.
8. Deterministic dates copied from DB, not generated by teachers.
9. Frozen input snapshot unaffected by later source changes.
10. Secret quarantine true positives and UUID/code false-positive resistance.
11. Dry run makes zero network/LLM calls.
12. Remote calls blocked without both explicit confirmation flags.
13. Provider/model allowlist enforcement.
14. Case/token/request/cost ceilings checked before transmission.
15. `store=false` or equivalent configured where supported.
16. Successful teacher output caching and resumable rerun.
17. Prompt/schema/model/settings changes invalidate the correct cache identity.
18. Malformed teacher output, timeout, retry exhaustion, and partial provider failure.
19. Direct teacher agreement classification.
20. Randomized anonymous reciprocal reconciliation.
21. Reconciled convergence versus unresolved disagreement.
22. Evidence validation and primary-score eligibility rules.
23. Pilot gate pass/fail behavior.
24. Frozen corpus immutability and new-version behavior.
25. Few-shot examples rejected from validation/holdout splits.
26. Model artifact/quantization/runtime stored as separate factors.
27. Privacy-safe aggregate report contains no transcript/title/path/URL/UUID leakage.
28. Git-ignore/privacy checks for all private artifact extensions and paths.

## Acceptance Criteria

WP-5.1.2 is complete only when:

1. Both dependency packages were accepted before execution.
2. Generic tracked tooling and synthetic tests are implemented and documented.
3. `.chronicle/eval/eval.db` is the canonical private evaluation store.
4. The real source DB was read-only and unchanged.
5. A deterministic, representative 30-conversation pilot was built.
6. Both approved teacher profiles ran or resumed through the accepted LiteLLM boundary.
7. Pilot quality/privacy/cost gates passed.
8. A deterministic 300-conversation corpus was created with 150/50/100 splits, or the report is `partial` because fewer than 300 eligible unique records exist.
9. All four task cases have two teacher outputs or explicit bounded failure states.
10. Agreement, reconciliation, disagreement, invalid, and quarantine states are preserved.
11. Unresolved cases are ineligible for primary scoring.
12. The corpus is frozen before any candidate-model testing.
13. Model/prompt/runtime metadata structures are ready for WP-5.2.
14. No human review is claimed or required.
15. No private evaluation artifact is tracked or leaked in the completion report.
16. Full tests and Ruff pass.
17. Existing Chronicle commands and WP-5.1 behavior remain regression-clean.
18. The required detailed completion report exists at the exact path below.

If remote credentials or configured cost authorization prevent teacher generation, implement and validate the generic tooling but report `partial` or `blocked` accurately. Do not claim corpus completion from mocked calls.

## Required Validation Evidence

Before Poetry commands, follow `md/agent-operating-notes.md`:

```powershell
poetry env info --path
```

The result must be the repo-local `.venv`. Stop if Poetry resolves another project's environment.

Run and report:

```powershell
poetry run pytest <focused WP-5.1.2 test files> -q
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
poetry run chronicle --ai-task list
git diff --check
git status --short
git ls-files
```

Also provide privacy-safe aggregate evidence for:

- synthetic end-to-end dry run;
- real 30-conversation pilot selection;
- preflight token/request/cost estimate;
- explicit remote-gate behavior;
- teacher run counts and schema-valid rates;
- agreement/reconciliation/disagreement rates by task;
- pilot-gate decision;
- full corpus counts and split/provider/size strata if expansion runs;
- cache/resume behavior with zero duplicate unchanged successful calls;
- source DB no-write evidence;
- `.chronicle/eval/` ignore/tracking evidence;
- absence of private content in tracked diff/report.

Do not paste model prompts, responses, titles, excerpts, URLs, UUIDs, source IDs, local usernames, or absolute private paths into the completion report.

## Completion Report Requirements

Write the detailed completion report at exactly:

```text
md/handoffs/reports/WP-5.1.2-completion-report.md
```

The report must include:

1. Status: `ready for PM validation`, `partial`, or `blocked`.
2. Dependency acceptance evidence.
3. Executive summary and explicit statement that references are automated silver references with no human review.
4. Files changed, separating tracked generic tooling from untracked private artifacts.
5. Evaluation data layout and eval-database schema/version.
6. Source read-only/no-write mechanism and evidence.
7. Sampling, deduplication, stratification, split, seed, and freeze rules.
8. Pilot aggregate profile without private identifiers/content.
9. Teacher profile/model/config provenance.
10. Current remote retention/storage controls and verification links/date.
11. Secret quarantine method and aggregate exclusions.
12. Preflight estimated versus actual tokens/requests/cost, without billing/account identifiers.
13. Schema-valid, agreement, reconciliation, disagreement, invalid, and usable-reference rates by task.
14. Pilot gate checklist and expansion decision.
15. Full corpus aggregate counts/splits/strata if completed.
16. Cache/resume/retry/failure evidence.
17. Prompt-variant and WP-5.2 model/runtime metadata readiness.
18. Focused and full validation results.
19. Git privacy/tracking evidence.
20. Known limitations, especially lack of human gold labels and low-N provider strata.
21. Requirement-by-requirement acceptance checklist.
22. Final statement that nothing was committed unless the PM explicitly requested a commit.

## Executor Delivery Rules

The PM/manager exclusively owns staging and commits. Do not run `git add`,
`git commit`, amend, squash, rebase, or otherwise rewrite history. Leave all
delivery and rework changes uncommitted with a final `git status --short` for PM
review. Only the PM may commit after successful validation and an explicit owner
request; a commit request addressed to the PM or associated with another work
package is not authorization for the executor.

- Do not commit unless explicitly instructed by the PM after validation.
- Do not update the ledger to `Accepted`; only the PM does that.
- You may set the WP row to `Ready for PM validation` only when every acceptance criterion is satisfied and the full real corpus/reference run is complete.
- Use `partial` when generic tooling is complete but pilot/full remote generation or corpus freeze is incomplete.
- Use `blocked` only for a genuine external dependency that prevents meaningful progress and explain it precisely.
- Preserve all unrelated and pre-existing working-tree changes.
- Return a concise delivery message pointing to the required completion report; the report contains the detailed evidence.
