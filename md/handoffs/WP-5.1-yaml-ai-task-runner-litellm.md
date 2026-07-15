# WP-5.1 Handoff: YAML AI-Task Runner + LiteLLM Model Configuration

## Status

Ready for execution.

This handoff is the complete executor instruction for WP-5.1. Do not infer additional AI features from the broader roadmap.

## Objective

Build the optional foundation that runs externally configured LLM tasks against selected archived conversations:

```powershell
poetry run chronicle --ai-task list
poetry run chronicle --ai-task <name> --conversation-id <id>
```

`<name>` must be resolved from:

```text
.chronicle/ai-tasks.yaml
```

Model/provider details must be resolved independently from:

```text
.chronicle/ai-models.yaml
```

Use the LiteLLM Python SDK behind a small internal application-owned interface. The core archive must continue to install and operate without AI dependencies or a running model service.

WP-5.1 is infrastructure only. Do not finalize or implement the owner's four production conversation-intelligence tasks here; those belong to WP-5.1.1 after their semantics are agreed.

## Current Baseline

The core real-history prototype is accepted. Current supported data includes real ChatGPT, Claude, OpenAI Codex, and Claude Code histories in the owner's git-ignored repo-local database.

Current schema version is 2. Existing schema already contains legacy `enrichments` and `knowledge_items` tables. Preserve them. WP-5.1 adds a forward migration and must not delete, repurpose, or silently migrate their contents.

The current Typer application uses a root callback for `--version` and `no_args_is_help=True`. Implement the requested root `--ai-task` invocation without regressing any existing subcommand or no-argument help behavior.

The last accepted validation baseline was 233 tests passing with Ruff clean. Treat that as historical evidence, not a substitute for fresh validation.

## Source Of Truth

Read before implementation:

- `md/master-plan.md`, especially M5 and the `ai_task_results` schema sketch;
- `md/development-ledger.md`;
- `md/agent-operating-notes.md`;
- `md/handoffs/WP-1.6-config-defaults-collect-workflow.md`;
- `md/handoffs/reports/WP-1.6-completion-report.md`;
- `chronicle.default.yaml`;
- `src/chat_chronicle/config.py`;
- `src/chat_chronicle/cli.py`;
- `src/chat_chronicle/db.py`;
- `src/chat_chronicle/models.py`;
- current CLI/config/DB tests;
- `README.md`.

Do not use real transcript content in fixtures, source files, reports, or terminal evidence.

## Required Poetry Preflight

Before every Poetry install, test, lint, or CLI command group:

```powershell
poetry env info --path
```

Expected:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If Poetry resolves any other environment, stop. Clear the inherited `VIRTUAL_ENV` / `POETRY_ACTIVE` state and follow `md/agent-operating-notes.md`. Do not install LiteLLM or run tests in another project's environment.

## Locked Design Decisions

These decisions are approved and are not optional executor choices:

1. The user-facing syntax is the root option `--ai-task`, not one hard-coded CLI command per prompt.
2. CLI spelling is lowercase kebab case: `--ai-task`, not `--AI_Task` or `--ai_task`.
3. Task definitions and model definitions are separate YAML files.
4. Prompts/query instructions are externally editable YAML.
5. Output schema implementations, input-selector implementations, privacy checks, and DB writes remain code-owned.
6. LiteLLM is behind a small internal port/interface; business logic must not call LiteLLM directly throughout the codebase.
7. Normal `ingest`, `collect`, `scan-local`, `stats`, `recent`, `search`, `open`, and initialization behavior must make zero LLM calls.
8. Local service profiles are the default. Remote execution requires explicit authorization on every invocation.
9. Execution may use LiteLLM's async API internally, but the v1 CLI remains a foreground, resumable command. Do not create a daemon, service, queue server, or scheduled task.
10. Successful results are cacheable and reproducible by input/task/schema/model configuration identity.

## CLI Contract

Implement at least:

```powershell
poetry run chronicle --ai-task list
poetry run chronicle --ai-task <name> --conversation-id <id>
poetry run chronicle --ai-task <name> --limit <n> [--provider <provider>] [--since <date>] [--until <date>]
```

AI invocation options:

- `--ai-task <name>`: required to enter AI-task execution; `list` is a reserved discovery value.
- `--conversation-id <id>`: run against exactly one conversation.
- `--limit <n>`: explicit bounded batch selection, ordered by last activity descending.
- `--provider`, `--since`, `--until`: optional batch filters, with the same provider/date semantics as accepted read commands.
- `--model-profile <alias>`: optional override of the task's configured model profile.
- `--db-path <path>`: retain accepted CLI/env/config/default DB precedence.
- `--force`: ignore a successful matching cache entry and execute again.
- `--dry-run`: show selected task, model profile, conversation IDs/count, local/remote classification, and cache hit/miss counts without rendering transcript bodies or calling an LLM.
- `--allow-remote`: required for every run resolved to a remote model profile.

Selection safety:

- `list` requires no conversation selection and no LiteLLM import/service.
- A runnable task requires either `--conversation-id` or an explicit positive `--limit`.
- Never default to processing the entire archive.
- Reject incompatible combinations clearly, including `--ai-task` together with a normal subcommand.
- Preserve `chronicle --help`, `chronicle --version`, and no-argument help behavior.
- A missing optional AI dependency must produce an actionable message that names the install extra; it must not produce a Python import traceback.

Default result output should be concise and privacy-safe:

- task and task version;
- logical and actual model identity;
- selected/completed/cached/failed counts;
- result ID and conversation ID;
- validated structured result for a single-conversation invocation;
- no raw prompt or transcript unless a future explicit debug feature is approved.

## Configuration Files

Add tracked, privacy-safe templates:

```text
ai-tasks.default.yaml
ai-models.default.yaml
```

`chronicle init` must create missing local copies:

```text
.chronicle/ai-tasks.yaml
.chronicle/ai-models.yaml
```

Rules:

- Do not create these files during package installation.
- Do not overwrite existing local AI YAML files by default.
- Existing `chronicle init --force` behavior may be extended only with explicit, documented overwrite rules; never overwrite silently.
- Templates must contain no real API key, username, private path, transcript, conversation ID, or model-account identifier.
- Environment-variable expansion must reuse the accepted config behavior where practical.
- YAML must use `yaml.safe_load` and Pydantic validation with unknown fields rejected.
- Errors must identify the file and invalid field/task/profile.

### Task Catalog Contract

Use a small versioned schema equivalent to:

```yaml
version: 1
tasks:
  example-task:
    enabled: true
    version: "1"
    description: "Privacy-safe example only"
    model_profile: service-local
    input_selector: full-conversation
    output_schema: example-result-v1
    system_prompt: |
      External task instructions.
    user_prompt: |
      Process the selected conversation input.
    generation:
      temperature: 0
      max_tokens: 500
    depends_on: []
```

The exact field names may follow a cleaner established Pydantic convention, but preserve these concepts:

- stable task name and explicit task version;
- enabled state and description;
- logical model-profile alias;
- code-owned input-selector name;
- code-owned output-schema name/version;
- externally editable system/user prompt text;
- bounded generation parameters;
- optional named dependencies.

Do not execute arbitrary Python, import paths, shell commands, Jinja expressions, or YAML tags from task configuration. Prompt interpolation must use an allowlisted, non-evaluating mechanism. Unknown placeholders must fail before an LLM call.

The tracked default task catalog may be empty or contain disabled/documentation-only examples. Production definitions for `conversation-summary`, `work-mode-classification`, `last-activity`, and `title-assessment` are WP-5.1.1 scope.

### Model Profile Contract

Use a versioned Chronicle-owned model-profile schema translated into LiteLLM call parameters. Each profile must cover:

- logical alias;
- LiteLLM provider/model identifier;
- optional `api_base` for an OpenAI-compatible local endpoint;
- environment-variable name for credentials, never a credential value;
- explicit `remote` declaration;
- timeout;
- conservative retry count;
- optional safe generation defaults.

Provide a privacy-safe `service-local` example for LM Studio at a loopback endpoint. The actual model identifier should be configurable by environment variable or local YAML, not hard-coded as the only supported model.

Do not require the LiteLLM proxy. Use the Python SDK directly for this single-user v1 workflow.

Privacy classification must be conservative:

- loopback endpoints may be local;
- known cloud providers and non-loopback endpoints are remote regardless of a mistaken `remote: false` value;
- ambiguous profiles must fail closed or require `--allow-remote`;
- `--allow-remote` authorizes only the current invocation and must never mutate config into a permanent bypass.

## Internal LLM Boundary

Create a small application-owned interface with one structured completion operation. The worker/task runner depends on this interface, not directly on LiteLLM.

Requirements:

- lazy import of the optional LiteLLM dependency;
- use LiteLLM's async completion path where practical;
- normalized request/response/error objects owned by this project;
- Pydantic/JSON-schema response request where the resolved provider supports it;
- client-side Pydantic validation is mandatory even when provider-side schema enforcement is used;
- clear handling for timeout, authentication, connection, rate-limit, invalid JSON, and schema-validation failures;
- no automatic provider fallback from local to remote;
- dependency injection for deterministic mocked tests.

Do not expose provider-specific response objects outside the adapter.

## Input Selection And Prompt Data

Implement a small code-owned input-selector registry sufficient for future task work. At minimum, provide deterministic selectors for:

- full normalized conversation, with a configurable maximum character/token budget;
- recent normalized messages, with a configured message count and maximum budget;
- metadata plus recent messages.

Selectors must expose deterministic metadata separately from transcript text:

- conversation ID;
- provider;
- source title;
- start date derived from stored message/conversation metadata;
- last-active date derived from stored message/conversation metadata;
- selected message IDs/sequence range;
- normalized selected text.

Do not ask an LLM to infer dates already present in the database. Do not include tool/reasoning/system metadata that accepted importers intentionally excluded from visible messages.

For oversized input, use deterministic truncation with evidence in the stored metadata. Do not build map-reduce summarization in WP-5.1; that belongs to task-specific work if later required.

## Schema V3 Migration And Result Store

Bump the DB schema from v2 to v3 and add `ai_task_results` following the master-plan contract.

The table must persist enough information to explain and reproduce a result:

- conversation foreign key;
- task name/version;
- conversation input hash;
- prompt hash;
- canonical complete task-configuration hash;
- output schema name/version;
- logical model profile;
- canonical resolved model-configuration hash;
- actual provider/model reported by the adapter;
- validated `result_json`;
- status and sanitized error;
- start/completion timestamps;
- latency and token usage when available;
- selected message range/truncation metadata, either as columns or validated JSON metadata.

Database requirements:

- fresh DB creation at v3;
- v1-to-v3 and v2-to-v3 migration coverage;
- no loss/change to existing source, project, conversation, message, ingest, FTS, `enrichments`, or `knowledge_items` data;
- foreign keys remain valid;
- useful indexes for conversation/task/status lookup;
- the indexed successful-cache lookup key includes conversation input, complete task configuration, schema version, and resolved model configuration;
- only successful matching results count as cache hits;
- execution attempts are append-only; `--force` bypasses cache lookup and appends a new auditable attempt without destroying prior output;
- error text must not contain API keys or full transcript/prompt bodies.

Use canonical structured serialization for hashes. Do not use ad hoc concatenated strings whose field ordering can change hashes.

## Optional Dependency And Packaging

Replace the planned direct OpenAI enrichment dependency with LiteLLM in the optional `enrich` extra. Keep the base installation free of AI dependencies.

Requirements:

- use a bounded compatible LiteLLM version range and update the lock file;
- importing or using non-AI commands must not import LiteLLM eagerly;
- standard test execution must still be possible without a live provider;
- CI/development coverage for the optional adapter must be explicit and documented rather than silently skipped;
- do not add the LiteLLM proxy, Redis, Docker, an observability service, or a second orchestration framework.

## Async, Retry, And Failure Behavior

The internal worker may process a bounded batch asynchronously, but default concurrency must be conservative for a local model service.

Requirements:

- no unbounded task creation;
- configurable small concurrency, default 1;
- bounded timeout and retry count from the selected model profile;
- no retry for schema/configuration/authentication failures unless the failure is demonstrably transient;
- one conversation failure does not abort an explicitly selected batch;
- Ctrl+C exits cleanly after preserving already committed results;
- rerunning resumes from successful cache entries;
- no background process remains after CLI exit.

## Friday Progress-Sharing Checkpoint

Friday, 17 July 2026 is a communication checkpoint, not an acceptance shortcut.

The owner can already share the accepted real-history prototype. If WP-5.1 is not PM-accepted by then, describe it only as the next/in-progress YAML-configured AI layer.

Do not place private output into the completion report or a public screenshot. Public-safe evidence must redact:

- usernames and absolute paths;
- conversation titles and snippets;
- URLs and UUIDs;
- transcript/prompt/result text derived from the real archive;
- API keys and account/model identifiers that disclose private configuration.

## Out Of Scope

Do not implement in WP-5.1:

- production prompts or final schemas for the four WP-5.1.1 tasks;
- manager/executor/one-off classification semantics;
- automatic conversation renaming;
- writing suggested titles back to source or normalized conversations;
- embeddings, vector search, reranking, or `--smart` query rewriting;
- knowledge extraction, weekly digest, or project brief;
- MCP server changes;
- Gemini importer/download work;
- Cursor work;
- rename from `chronicle` to `worktrail`;
- LiteLLM proxy deployment;
- remote calls using the owner's real archive during implementation or validation;
- a daemon, job server, GUI, or scheduled-task registration;
- changes to default FTS/BM25 or phrase-search behavior.

## Tests Required

Add focused synthetic tests for all of the following.

### Configuration

- valid task/model YAML loads;
- unknown fields, malformed YAML, duplicate/unknown aliases, unknown schema/selector names, missing environment variables, unknown placeholders, and dependency cycles fail clearly;
- tracked templates contain no private paths or credentials;
- `chronicle init` creates missing local AI YAML and does not overwrite existing files by default.

### CLI

- `--ai-task list` works without importing/calling LiteLLM;
- configured task names and profiles are listed;
- exact-ID and bounded-filter selection work;
- missing explicit scope is rejected;
- invalid task/profile combinations are rejected;
- `--dry-run` calls no LLM and prints no transcript;
- remote profile is blocked without `--allow-remote` and allowed only for that invocation;
- a non-loopback endpoint cannot bypass the remote guard by claiming `remote: false`;
- missing optional dependency produces an install hint, not a traceback;
- normal subcommands and root help/version behavior remain unchanged;
- `--ai-task` cannot be combined ambiguously with a normal subcommand.

### Execution And Validation

- mocked successful structured completion is Pydantic-validated and persisted;
- provider-valid JSON that fails the Pydantic schema is recorded as failure;
- timeout, connection, authentication, rate-limit, invalid JSON, and schema errors are normalized and sanitized;
- batch continues after one conversation failure;
- bounded concurrency is respected;
- no automatic local-to-remote fallback occurs;
- real LiteLLM/provider/network access is not required by tests.

### Cache And Migration

- fresh v3 schema creation;
- v1-to-v3 and v2-to-v3 migrations preserve existing rows/tables;
- unchanged successful task+input+resolved configuration is cached;
- conversation, prompt, generation setting, task version, schema version, model alias definition, or selected-input change invalidates the matching cache;
- failed results are retryable and are not treated as successful cache hits;
- `--force` appends a new attempt and preserves auditable prior success while executing again;
- stored JSON and errors are serializable and secrets/transcript bodies are absent from errors;
- existing FTS/search behavior remains intact after migration.

Use synthetic conversations and temporary databases only.

## Required Validation Evidence

Include exact outputs or concise exact summaries for:

```powershell
poetry env info --path
poetry run pytest <focused WP-5.1 test files> -q
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
poetry run chronicle --ai-task list
poetry run chronicle stats
poetry run chronicle search "scan-local"
git diff --check
git status --short
```

Run AI task smoke against a temporary DB, temporary YAML, synthetic conversation, and injected/mock client. Report:

- first run executed and stored one validated result;
- second unchanged run was a cache hit and made zero model calls;
- changed prompt or model configuration caused a fresh call;
- remote profile was blocked without `--allow-remote`;
- no transcript text was printed.

A real local LM Studio smoke is optional and must not be an acceptance dependency. If performed, use a synthetic conversation only, identify it explicitly as optional, and do not expose private model/account configuration.

## Documentation Requirements

Update `README.md` with:

- optional AI dependency installation;
- `chronicle init` creation of AI YAML files;
- where task and model configuration live;
- `--ai-task list` and one synthetic-form invocation example;
- local-default and explicit `--allow-remote` privacy behavior;
- cache/resume behavior;
- statement that the four production conversation-intelligence tasks arrive in WP-5.1.1.

Do not describe WP-5.1.1 tasks as implemented.

Update the ledger status only to `ready for PM validation` when implementation and the required report are complete. Do not mark the package accepted.

## Completion Report Requirements

Write the detailed completion report at exactly:

```text
md/handoffs/reports/WP-5.1-completion-report.md
```

The report must include:

1. Status: `ready for PM validation`, `partial`, or `blocked`.
2. Executive summary and explicit statement that WP-5.1.1 production tasks remain out of scope.
3. Files changed, grouped by source/config/schema/tests/docs.
4. Final CLI syntax and option behavior.
5. Task YAML schema and a privacy-safe example.
6. Model-profile YAML schema and local/remote classification rules.
7. Internal `LLMClient`/LiteLLM boundary and optional-import behavior.
8. Schema-v3 migration description and preservation evidence for v1/v2 data.
9. Exact cache identity and invalidation rules.
10. Async/concurrency/retry/failure behavior.
11. Remote privacy-gate evidence.
12. Focused and full validation results.
13. Privacy-safe synthetic smoke evidence, including first-run/cache/invalidation behavior.
14. Optional real-local-provider smoke, clearly separated if performed.
15. `git status --short` and `git ls-files` privacy checks proving no DB, export, ZIP, JSONL, local AI config, secret, or private transcript is tracked.
16. Known limitations and follow-ups.
17. Requirement-by-requirement checklist mapping every acceptance criterion below to code/tests/evidence.

Do not paste real prompts, transcripts, conversation titles, URLs, UUIDs, local usernames/paths, API keys, or private model-account details into the report.

Do not commit implementation changes. Leave them in the working tree for PM validation.

## Acceptance Criteria

WP-5.1 is complete only when all of the following are evidenced:

1. `poetry run chronicle --ai-task list` resolves task names from `.chronicle/ai-tasks.yaml` without an LLM call.
2. `poetry run chronicle --ai-task <name> ...` executes a configured task through the internal LiteLLM-backed boundary.
3. Task prompts/policy and model/provider profiles are external and independently configurable.
4. Pydantic owns YAML validation and structured-output validation.
5. Base installation and normal archive commands remain usable without AI dependencies or a provider.
6. Local profiles are default; every remote run requires explicit `--allow-remote`.
7. Explicit selection prevents accidental whole-archive processing.
8. Schema v3 creates `ai_task_results` and safely migrates v1/v2 without changing existing data behavior.
9. Successful results are cached by input plus complete task/schema/resolved-model identity.
10. Cache invalidation and `--force` behavior are tested and auditable.
11. Async execution is bounded, foreground, resumable, and failure-isolated.
12. Missing dependency/provider and malformed config/output failures are clear and non-destructive.
13. Existing CLI, ingest, collection, stats, search, recent, open, and FTS behavior do not regress.
14. Tests and Ruff pass.
15. README documents the optional workflow without claiming WP-5.1.1 features.
16. The detailed completion report exists at the required path.
17. No private archive, local config, DB, credential, or transcript artifact is tracked.
