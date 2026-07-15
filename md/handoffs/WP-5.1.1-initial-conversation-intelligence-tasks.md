# WP-5.1.1 Handoff: Initial Conversation-Intelligence Task Catalog

## Status

Ready for execution.

WP-5.1 is accepted. This handoff defines the complete executor scope for WP-5.1.1. Do not infer WP-5.1.2 teacher-reference generation, WP-5.2 benchmarking, embeddings, retrieval changes, automatic renaming, or other AI features from the broader roadmap.

## Objective

Ship the first four independently runnable YAML-defined conversation-intelligence tasks on the accepted WP-5.1 runner:

1. `conversation-summary`;
2. `work-mode-classification`;
3. `last-activity`;
4. `title-assessment`.

These tasks reflect the owner's working pattern across manager, executor, and one-off chat threads. Each task must have:

- a stable task version;
- an external YAML prompt and model-profile alias;
- a code-owned deterministic selector;
- a code-owned Pydantic output contract;
- bounded input and output;
- evidence IDs tied to selected messages;
- independent cache/result identity;
- synthetic tests;
- no effect on normal archive commands.

This package establishes production task contracts needed by WP-5.1.2. It does not judge model quality on real conversations.

## Current Accepted Baseline

WP-5.1 is accepted in:

```text
md/handoffs/reports/WP-5.1-validation-acceptance.md
```

Accepted infrastructure includes:

- strict versioned task/model YAML;
- packaged templates and `chronicle init`;
- generic root `--ai-task` dispatch;
- explicit bounded selection and dry-run cache counts;
- local-first LiteLLM profiles and per-invocation remote guard;
- provider JSON-schema requests and local Pydantic validation;
- schema-v3 append-only AI results;
- exact prompt/input/task/schema/model cache identity;
- model-profile generation defaults with optional per-field task overrides;
- bounded foreground concurrency and failure isolation;
- full accepted regression baseline of 313 tests with Ruff clean.

Preserve this behavior. Do not redesign the WP-5.1 runner unless a narrowly scoped extension is required for the four accepted task contracts.

## Source Of Truth

Read before implementation:

- `md/master-plan.md`, M5;
- `md/development-ledger.md`;
- `md/agent-operating-notes.md`;
- `md/handoffs/WP-5.1-yaml-ai-task-runner-litellm.md`;
- `md/handoffs/reports/WP-5.1-completion-report.md`;
- `md/handoffs/reports/WP-5.1-validation-review.md`;
- `md/handoffs/reports/WP-5.1-validation-review-2.md`;
- `md/handoffs/reports/WP-5.1-validation-acceptance.md`;
- accepted WP-5.1 AI source/config/resource/test files;
- current normalized `Conversation`/`Message` models and schema-v3 DB.

## Approved Product Semantics

### Classification Unit

`work-mode-classification` classifies the **conversation as a whole**, not the role of an individual speaker and not only the latest turn.

`last-activity` separately describes the conversation's current/recent phase. Do not overload work-mode classification with current-state reporting.

### Approved Work-Mode Labels

Use exactly:

- `manager`;
- `executor`;
- `one_off`;
- `mixed`;
- `unknown`.

Definitions:

**`manager`**

The thread's primary purpose is project coordination: planning work packages, setting scope/acceptance criteria, delegating to another execution thread, reviewing completion reports, validating delivery, prioritizing, approving, requesting rework, or maintaining project status. Technical discussion may occur, but the thread primarily manages development rather than performing the implementation.

**`executor`**

The thread's primary purpose is carrying out a defined task: inspecting implementation context, editing/building artifacts, running tests, debugging failures, and reporting concrete delivery against a handoff or request. Clarification and planning may occur, but execution dominates.

**`one_off`**

The thread is a bounded question, explanation, recommendation, troubleshooting exchange, or small standalone request without sustained project-management workflow or substantial implementation delivery.

**`mixed`**

The thread contains substantial manager and executor phases, or combines a sustained project workflow with a substantial independent one-off purpose, such that one mode is not a defensible dominant description. Do not use `mixed` merely because every implementation conversation contains some planning.

**`unknown`**

There is insufficient meaningful content, the content is malformed/fragmentary, or the mode cannot be determined reliably. Prefer `unknown` over confident invention.

### Evidence Policy

Every model-generated factual task output must cite selected normalized message IDs. Application validation must reject evidence IDs that were not present in the selected input.

Evidence IDs are local normalized DB message IDs, not provider UUIDs. They are stored for reproducibility and later evaluation. Do not expose private evidence text in default CLI summaries or completion reports.

### Reasoning Policy

Do not request or store chain-of-thought. Require concise conclusions, short reasons, and explicit evidence IDs only.

## Deterministic Input Selectors

Add two code-owned selector versions. Preserve the accepted WP-5.1 selectors for compatibility; do not repurpose their semantics silently.

### `conversation-overview-v1`

Used by:

- `conversation-summary`;
- `work-mode-classification`;
- `title-assessment`.

Requirements:

1. Read normalized messages in deterministic `seq, id` order.
2. Exclude empty messages and non-conversation metadata/system/tool/reasoning records.
3. Preserve visible user/human and assistant content. Handle accepted provider role vocabulary without rewriting stored roles.
4. Render each selected message with normalized message ID, sequence, timestamp when available, role, and body so evidence IDs are visible to the model.
5. Respect the configured character budget at message boundaries where possible.
6. If the complete meaningful conversation fits, include it all.
7. If oversized, include deterministic coverage of the beginning, middle, and end, with at least the first and last meaningful messages when the budget permits.
8. Give the recent/end portion the largest share because outcomes and current state often appear there, while retaining enough beginning context to identify purpose.
9. Keep selected messages in chronological order after sampling.
10. Never duplicate a message.
11. If one message alone exceeds its allocation, truncate deterministically and record that exact message-level truncation.
12. Store selection evidence: selected IDs, omitted count/IDs or bounded omission summary, original/selected character counts, sequence range, sampling strategy/version, and truncation details.

Use a deterministic, documented allocation such as 25% beginning, 25% distributed middle, and 50% end. Minor implementation adjustment is allowed only if it is deterministic, fixture-tested, and documented in the completion report.

Do not add map-reduce summarization. One bounded selector plus one model call remains the WP-5.1.1 architecture.

### `recent-meaningful-v1`

Used by `last-activity`.

Requirements:

1. Apply the same meaningful-message filtering and evidence rendering rules.
2. Select the last configured number of meaningful messages, default 12.
3. Respect the character budget by retaining newest complete messages first, then return them in chronological order.
4. Include no older message merely to fill space after a newer selected message was omitted.
5. Record selected IDs, sequence range, original candidate count, omitted count, character counts, and truncation details.
6. If no meaningful message exists, produce a deterministic empty selection that the task may classify as unknown rather than raising an unhandled error.

### Meaningful-Message Filtering

Filtering must be code-owned and provider-independent.

At minimum exclude normalized roles/types representing:

- system/developer instructions;
- tool/function calls or results;
- reasoning/thinking metadata;
- importer metadata and empty bodies.

Do not accidentally exclude normal Claude `human` messages or accepted user/assistant vocabulary. Add fixtures for all currently supported providers.

## Task 1: `conversation-summary`

### Purpose

Provide a concise factual description of what the conversation is about and what it accomplished, accompanied by deterministic start and last-active dates.

### Selector

`conversation-overview-v1`.

### Provider-Generated Fields

- `summary`: 2-5 concise sentences, maximum 120 words;
- `evidence_message_ids`: 1-8 selected message IDs when meaningful content exists, otherwise empty.

The summary should cover the principal goal/topic, material work or decisions, and outcome/current position when supported. It must not invent success, decisions, blockers, or next steps.

### Application-Owned Final Fields

- `start_date`;
- `last_active_date`.

These dates come directly from accepted DB/selector metadata. The LLM must not infer, normalize, rewrite, or be trusted to echo them.

Implement a small code-owned result finalization contract if needed:

1. provider schema validates only model-owned fields;
2. application injects deterministic dates;
3. final stored result is validated by the full result schema;
4. cache/provenance continues to include date inputs and schema version.

Do not build task-specific DB writes outside the accepted `ai_task_results` path.

### Stored Output Contract

```text
summary: string
start_date: string
last_active_date: string
evidence_message_ids: list[int]
```

Use bounded Pydantic fields. Validate evidence IDs against the selection.

## Task 2: `work-mode-classification`

### Purpose

Classify the whole conversation according to the approved manager/executor/one-off workflow taxonomy.

### Selector

`conversation-overview-v1`.

### Stored Output Contract

```text
mode: manager | executor | one_off | mixed | unknown
confidence: float from 0.0 through 1.0
reason: concise string, maximum 60 words
evidence_message_ids: list[int], maximum 8
```

Requirements:

- classify conversation purpose, not speaker identity;
- use `manager` only when coordination/validation/delegation dominates;
- use `executor` only when concrete implementation/delivery dominates;
- use `one_off` only for bounded standalone work;
- use `mixed` for genuinely substantial multiple modes, not ordinary planning within execution;
- use `unknown` for insufficient evidence;
- confidence is a model self-assessment for comparison, not calibrated truth;
- reason must be concise and evidence-grounded.

## Task 3: `last-activity`

### Purpose

Describe what happened in the most recent meaningful portion of the conversation and where the work was left.

### Selector

`recent-meaningful-v1`, default 12 meaningful messages. Keep this count externally configurable through the task YAML using the accepted bounded selector field.

### Stored Output Contract

```text
recent_work: string, maximum 100 words
status: in_progress | completed | blocked | awaiting_input | unknown
blockers: list[string], maximum 3 items, each concise
next_action: string | null, maximum 40 words
next_action_basis: explicit | inferred | unknown
evidence_message_ids: list[int], maximum 8
```

Status definitions:

- `in_progress`: work is active/incomplete and not clearly blocked;
- `completed`: the selected recent activity reports completion/acceptance with no explicit unfinished follow-up in the selected range;
- `blocked`: progress cannot continue because of a stated technical/external blocker;
- `awaiting_input`: progress specifically waits for owner/user decision, credentials, data, approval, or another report;
- `unknown`: recent state is not reliably inferable.

Requirements:

- blockers must be empty when none are evidenced;
- do not convert a suggestion into an explicit commitment;
- `next_action_basis=explicit` only when the selected messages state the next action;
- use `inferred` only for a conservative, directly supported continuation;
- use `unknown` with `next_action=null` when no defensible next action exists;
- do not use older overview context outside the selector.

## Task 4: `title-assessment`

### Purpose

Assess whether the current conversation title accurately reflects its actual activity and suggest a replacement only when warranted.

### Selector

`conversation-overview-v1`, with the source title supplied as accepted prompt metadata.

### Stored Output Contract

```text
title_fits: boolean
confidence: float from 0.0 through 1.0
reason: concise string, maximum 60 words
suggested_title: string | null, maximum 80 characters
evidence_message_ids: list[int], maximum 8
```

Title-fit rules:

A title fits when it is specific enough to identify the conversation's dominant real activity and is not materially misleading, obsolete, or generic.

A title does not fit when it is:

- empty or a placeholder;
- unrelated to the dominant activity;
- narrowly describes only the opening question after the thread substantially changed;
- so generic that it cannot distinguish the work;
- incorrectly claims a project, outcome, or topic.

Suggested-title rules:

- return `null` when `title_fits=true`;
- return a concrete replacement when `title_fits=false` and evidence is sufficient;
- target approximately 3-10 words and never exceed 80 characters;
- describe the dominant activity, not the provider or date;
- preserve meaningful project/product names and technical acronyms;
- avoid clickbait, judgment, unsupported completion claims, and trailing punctuation unless intrinsic to a name;
- if evidence is insufficient, use a conservative descriptive title or `unknown`-style reasoning rather than invention.

The task only suggests. It must never update `conversations.title`, provider data, source exports, URLs, or origin files.

## Task Catalog And Versions

Add all four tasks to the tracked and packaged default task catalog. Requirements:

- enabled and discoverable after `chronicle init`;
- stable task version `1` unless the repository has adopted a stricter semantic convention;
- independently runnable;
- default model profile `service-local`;
- independent code-owned output schema names:
  - `conversation-summary-v1`;
  - `work-mode-classification-v1`;
  - `last-activity-v1`;
  - `title-assessment-v1`;
- selector names as defined above;
- explicit bounded generation overrides only where needed; otherwise inherit model-profile defaults;
- `depends_on: []` for all four v1 tasks so no task failure blocks another;
- prompts concise, zero-shot, evidence-oriented, and externally editable;
- no private paths, transcript text, account/model IDs, or real examples in tracked YAML.

Keep or remove the disabled WP-5.1 example task according to the cleanest catalog UX. If retained, clearly label it documentation-only and do not let it obscure the four production tasks.

Tracked root and packaged resource YAML must remain byte-identical. Update packaging tests accordingly.

## Schema Registry And Result Finalization

Extend the accepted code-owned schema registry conservatively.

Requirements:

- each schema has an explicit code-owned version;
- provider-facing schema is available to LiteLLM JSON-schema enforcement;
- final stored schema is Pydantic-validated;
- task-specific deterministic finalization is code-owned and allowlisted, not loaded from YAML import paths;
- summary date injection and evidence validation occur before success persistence;
- invalid evidence IDs produce a sanitized schema/evidence failure row, not a successful result;
- schema/finalizer version participates in cache identity;
- no arbitrary functions/classes are resolved from YAML.

Do not create a broad plugin framework. A small schema-spec/finalizer registry matching the accepted WP-5.1 pattern is sufficient.

## Evidence Validation

For every task:

1. Evidence list contains integers only.
2. Every ID belongs to the selected input for that attempt.
3. Remove no invalid IDs silently; reject the result so the failure is visible and retryable.
4. Empty evidence is allowed only when the selector has no meaningful messages or the schema explicitly permits an unknown result.
5. Evidence IDs and selector metadata are stored, but default CLI output must not print transcript bodies.

Add task-specific consistency validation:

- `title_fits=true` requires `suggested_title=null`;
- `title_fits=false` normally requires a non-empty suggestion unless evidence is insufficient and the schema explicitly models that state;
- `next_action_basis=unknown` requires `next_action=null`;
- no blockers means an empty list, not invented placeholder text;
- deterministic summary dates exactly equal selector/DB metadata.

## Cache And Independence

Preserve accepted WP-5.1 cache behavior.

Add proof that:

- each task stores a separate result row;
- same conversation/input under different task/schema identities cannot cross-hit;
- prompt/task/schema/selector changes invalidate only the affected task identity;
- deterministic finalizer/schema version changes invalidate cache;
- unchanged reruns are hits;
- one task failure does not invalidate another task's success;
- `--force` remains append-only.

Do not add cross-task dependency execution in this package. All four v1 tasks are independent.

## CLI Behavior

The accepted generic syntax remains:

```powershell
poetry run chronicle --ai-task list
poetry run chronicle --ai-task conversation-summary --conversation-id <id>
poetry run chronicle --ai-task work-mode-classification --conversation-id <id>
poetry run chronicle --ai-task last-activity --conversation-id <id>
poetry run chronicle --ai-task title-assessment --conversation-id <id>
```

Batch filters, `--dry-run`, `--force`, `--model-profile`, `--db-path`, and `--allow-remote` retain accepted WP-5.1 behavior.

Default CLI output may print validated structured output for a single selected conversation as already accepted. Tests and committed reports use synthetic content only.

No new top-level/subcommand per task. Task names continue to resolve from YAML.

## Privacy And Data Rules

- Use synthetic conversations and temporary DBs for committed tests.
- Do not run remote models against the owner's real archive in this package.
- A local LM Studio smoke is optional and synthetic-only.
- Do not add real summaries/classifications/titles/activity output to fixtures, docs, screenshots, or reports.
- Do not track local `.chronicle` AI YAML, DBs, exports, requests, responses, or credentials.
- No API key in YAML; preserve environment-only credential handling.
- Normal archive commands continue to make zero LLM calls.

Real private teacher generation is exclusively WP-5.1.2 after WP-5.1.1 acceptance.

## Required Synthetic Fixtures

Add small provider-neutral synthetic conversations covering at least:

- clear manager thread with planning, delegation, completion review, and rework;
- clear executor thread with implementation/test/delivery behavior;
- one-off technical explanation;
- genuinely mixed manager/executor phases;
- insufficient/empty conversation yielding unknown;
- completed recent activity;
- in-progress recent activity;
- blocked recent activity;
- awaiting-owner-input recent activity;
- explicit versus inferred versus unknown next action;
- accurate title;
- generic/misleading title requiring suggestion;
- conversation that changes topic after its original title;
- long conversation forcing deterministic overview sampling;
- recent selector exceeding message and character budgets;
- role vocabulary representative of ChatGPT, Claude, OpenAI Codex, and Claude Code;
- excluded system/tool/reasoning/empty records.

Fixtures must be invented and privacy-safe. Do not paraphrase recognizable owner conversations.

## Required Tests

Add focused tests for at least the following.

### Selectors

- meaningful-role filtering across provider vocabulary;
- deterministic ordering and repeated-run identity;
- complete overview when under budget;
- deterministic beginning/middle/end selection when oversized;
- newest-first retention then chronological rendering for recent activity;
- message-level truncation evidence;
- empty meaningful selection;
- rendered message IDs available to the model;
- selection metadata accurately describes included/omitted/truncated data.

### Schemas And Finalization

- all four schemas produce JSON Schema and reject unknown fields;
- all bounds/enums/nullable consistency rules;
- summary dates injected from DB and exact;
- LLM-supplied date fields are neither requested nor trusted;
- valid evidence accepted;
- out-of-selection evidence rejected and stored as sanitized failure;
- title fit/suggestion consistency;
- next action/basis consistency;
- schema/finalizer version cache invalidation.

### Task Semantics

Use deterministic fake outputs to prove the code contracts for every approved label/status. Do not assert that a mock LLM semantically understands text; semantic prompt quality belongs to WP-5.1.2/WP-5.2.

Verify catalog prompts contain the approved label definitions and required fields without requesting chain-of-thought.

### Catalog And CLI

- `chronicle init` creates all four enabled tasks in installed templates;
- `--ai-task list` shows all four task names without LiteLLM;
- each task exact-ID dry-run resolves selector/schema/profile and cache counts;
- each task executes with an injected client and stores its own validated result;
- batch behavior remains bounded and failure-isolated;
- no per-task command was added;
- remote guard and optional dependency behavior remain unchanged;
- tracked root/package templates remain byte-identical and private-data-free.

### Regression

- existing WP-5.1 acceptance matrix remains green;
- fresh/v1/v2 schema-v3 migration remains green;
- normal ingest/collect/scan/stats/recent/search/open behavior remains green;
- no normal command imports/calls LiteLLM;
- title assessment never writes the conversation title;
- failed task attempts remain retryable;
- existing FTS content is unchanged by AI task execution.

## Acceptance Criteria

WP-5.1.1 is complete only when:

1. All four task definitions are enabled in tracked and packaged YAML.
2. Task prompts and policies are externally editable and independently versioned.
3. `conversation-overview-v1` and `recent-meaningful-v1` are deterministic, bounded, evidence-bearing, and tested.
4. Summary output contains application-owned exact start/last-active dates.
5. Work-mode classification uses exactly the approved five labels and whole-conversation semantics.
6. Last activity uses only recent meaningful selected messages and the approved status/action contract.
7. Title assessment suggests only and never renames stored/source data.
8. Every factual output validates evidence IDs against the selected input.
9. Every output is Pydantic/JSON-schema validated with explicit version identity.
10. Each task caches and fails independently.
11. Normal archive commands remain AI-free and regression-clean.
12. No real/private archive content or model call is used in committed evidence.
13. Focused tests and full suite pass.
14. Ruff and `git diff --check` pass.
15. Installed wheel contains updated byte-identical templates.
16. README documents the four available tasks honestly without claiming real-model quality.
17. The detailed completion report exists at the exact required path.
18. Ledger state is only `Ready for PM validation`, not accepted.

## Required Validation Evidence

Before every Poetry command group, follow `md/agent-operating-notes.md`:

```powershell
poetry env info --path
```

It must resolve to:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

Run and report:

```powershell
poetry run pytest <focused WP-5.1.1 test files> -q
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
poetry run chronicle --ai-task list
git diff --check
git status --short
git ls-files
```

Build the wheel and prove:

- both updated YAML resources are present;
- root and packaged templates are byte-identical;
- outside-checkout `chronicle init` creates the four production task definitions;
- no private config is packaged.

Run a synthetic mock smoke for all four tasks and report only synthetic IDs/content or aggregate statuses. Do not use the owner's real DB.

## Documentation Requirements

Update README with:

- the four production task names and concise purposes;
- command examples using `<id>`, not a real conversation ID;
- profile-default/task-override generation precedence;
- deterministic-date statement for summaries;
- whole-conversation work-mode labels;
- last-activity recent-message scope;
- title suggestion-only behavior;
- local default/remote authorization and privacy warning;
- statement that model quality and real-data references are evaluated later in WP-5.1.2/WP-5.2.

Do not publish real outputs.

Update the ledger to `Ready for PM validation` only after implementation and all required evidence are complete. Do not mark accepted.

## Completion Report Requirements

Write the detailed completion report at exactly:

```text
md/handoffs/reports/WP-5.1.1-completion-report.md
```

The report must include:

1. Status: `ready for PM validation`, `partial`, or `blocked`.
2. Executive summary and explicit WP-5.1.2/WP-5.2 exclusion.
3. Files changed grouped by task catalog, selectors, schemas/finalizers, tests, docs.
4. Final YAML definitions and versions.
5. Exact selector algorithms and truncation/evidence metadata.
6. Full Pydantic contracts for all four tasks.
7. Work-mode label definitions and whole-conversation decision.
8. Last-activity status/action semantics.
9. Title-fit/suggestion rules and no-write evidence.
10. Deterministic summary-date implementation/evidence.
11. Evidence-ID validation behavior.
12. Cache/schema/finalizer identity and independent-task behavior.
13. Synthetic fixture/test coverage.
14. Focused/full/Ruff/help/list/diff results.
15. Wheel/template packaging evidence.
16. Privacy and tracked-artifact evidence.
17. Known limitations, especially no real-model quality claim.
18. Requirement-by-requirement acceptance checklist.
19. Final statement that nothing was committed unless the PM explicitly requested it.

## Executor Delivery Rules

- Do not commit unless explicitly instructed by the PM after validation.
- Do not mark WP-5.1.1 accepted.
- Do not use the real owner archive or remote providers.
- Do not start WP-5.1.2 or WP-5.2.
- Preserve unrelated/pre-existing working-tree changes.
- Return a concise delivery message pointing to the exact completion report.

