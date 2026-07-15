# WP-5.1 Validation Review: YAML AI-Task Runner + LiteLLM

## Decision

**Rework required. WP-5.1 is not accepted.**

The implementation establishes a credible foundation and the existing test suite remains green, but the completion report correctly declares the delivery `partial`. Independent PM validation found implementation defects in addition to the report's missing acceptance matrix. Return this review to the WP-5.1 executor and keep all WP-5.1.1/WP-5.1.2 execution dependency-gated.

## Findings

### 1. P1 - Installed-package `chronicle init` cannot access the AI YAML templates

Evidence:

- `src/chat_chronicle/cli.py:676` derives a source-tree repository root from `Path(__file__).resolve().parents[2]`.
- `src/chat_chronicle/cli.py:686` copies `ai-tasks.default.yaml` and `ai-models.default.yaml` from that derived root.
- `pyproject.toml:35` packages only `src/chat_chronicle`.
- PM built the wheel and inspected its manifest. Neither root YAML template was present.

This works from the editable repository checkout but fails after wheel/pipx installation because the installed package has no repository root containing those files. That violates the required `chronicle init` behavior and makes the documented installed workflow unusable.

Required correction:

1. Package the templates as package data under `chat_chronicle` or another stable installed resource location.
2. Load/copy them through `importlib.resources` or an equivalent installation-safe resource API.
3. Do not depend on source-tree parent traversal.
4. Add a wheel/package test that installs or imports the built artifact from outside the repository and proves `chronicle init` creates both catalogs.
5. Prove existing files are still preserved unless `--force` is supplied.

### 2. P1 - Cache identity can reuse stale output after prompt metadata changes

Evidence:

- `src/chat_chronicle/ai.py:186` hashes selected text and selection metadata only.
- The selection metadata does not include title, provider, start date, or last-active date.
- Those values are interpolated into prompts at `src/chat_chronicle/ai.py:187-196`.
- `prompt_hash` is calculated at `src/chat_chronicle/ai.py:197` but is not supplied to the cache lookup.
- `src/chat_chronicle/db.py:778-781` does not match on prompt hash, logical task name, or output-schema version.

A title or activity-date change can alter the rendered prompt while producing the same cache lookup identity. The runner can therefore return an earlier success without calling the model. Two differently named tasks with identical definitions can also cross-hit the same stored row, and schema-version identity is stored but not independently matched.

Required correction:

1. Define one documented canonical cache identity containing every value capable of changing the request or output interpretation.
2. Include either the rendered prompt hash or every prompt input value in the lookup identity.
3. Include logical task identity and explicit output-schema version, unless a stronger canonical identity makes cross-task reuse intentionally safe and the handoff/report are amended with PM approval.
4. Keep credential values excluded.
5. Store and query the same identity components; do not compute provenance fields that the cache ignores.
6. Add individual invalidation tests for conversation body/role/order, title, start/last-active date, prompt text, generation setting, task version, selector/budget, schema name/version, model alias, resolved model definition, and selected-message changes.
7. Add a test proving an unrelated credential value change does not leak into or unnecessarily alter the cache identity.

Also correct provenance while touching this path:

- `src/chat_chronicle/db.py:796-810` assigns one completion-time value to both `started_at` and `completed_at`; persist the real start and completion timestamps.
- Preserve actual provider/model and usage when a provider response exists but JSON/Pydantic validation fails, subject to sanitized storage.

### 3. P1 - Required CLI failures are not actionable and some can escape as tracebacks

Evidence:

- `LiteLLMClient` creates an actionable missing-extra message, but `run_task` replaces it with the generic stored error `dependency: structured completion failed`.
- `src/chat_chronicle/cli.py:314-320` prints only result ID, conversation ID, and status; the actionable dependency/provider failure is not shown.
- `select_input()` is called before the per-conversation `try` block at `src/chat_chronicle/ai.py:184`.
- A nonexistent exact conversation ID or another selection exception can escape `asyncio.gather()` at `src/chat_chronicle/ai.py:286` and produce an unhandled traceback.

This does not meet the handoff requirement for clear, sanitized dependency/config/provider failures and isolated batch behavior.

Required correction:

1. Preserve a sanitized actionable message for missing optional dependencies, including `poetry install -E enrich`.
2. Render sanitized failure kind/detail in CLI output without prompts, transcripts, keys, or provider payloads.
3. Validate exact conversation IDs before execution or normalize selection errors inside each work item.
4. Define and test exit behavior. At minimum, an invalid single selection or a single/all-failed invocation must exit non-zero without a traceback. Document mixed-batch behavior.
5. Keep one failed conversation from aborting successful selected conversations.

### 4. P2 - The code-owned JSON schema is never sent to LiteLLM

Evidence:

- `CompletionRequest.response_schema` is defined at `src/chat_chronicle/ai.py:42` and populated at `src/chat_chronicle/ai.py:214`.
- `LiteLLMClient.complete()` ignores that field and always sends only `response_format={"type": "json_object"}` at `src/chat_chronicle/ai.py:75`.

Client-side Pydantic validation is present and must remain, but the handoff also requires Pydantic/JSON-schema response requests where the provider supports them. The current request cannot enforce the actual shape at the provider/local-runtime boundary.

Required correction:

1. Translate the Chronicle-owned schema into the supported LiteLLM structured-output request.
2. Retain client-side JSON parsing and Pydantic validation.
3. Handle providers that do not support schema enforcement explicitly and fail or degrade according to a documented profile capability; do not silently pretend schema enforcement occurred.
4. Add an adapter test that asserts the schema reaches the mocked LiteLLM call without exposing a provider response object to business logic.

### 5. P2 - Dry-run and result output do not meet the approved CLI contract

Evidence:

- `src/chat_chronicle/cli.py:294` reports only that no model call was made.
- The handoff requires selected task/profile/IDs, local/remote state, and cache hit/miss counts.
- Successful result dictionaries do not carry actual provider/model identity to the CLI, so the default output cannot show the required logical and actual model identities.

Required correction:

1. Make dry-run calculate and display cache hit/miss counts using the exact corrected cache identity while making zero model calls.
2. Render logical profile plus actual provider/model for executed successes; identify cached provenance safely.
3. Apply the accepted provider/date-filter semantics, including date-only `--until` behavior.
4. Reject irrelevant/ambiguous option combinations for `list`, exact-ID selection, and normal subcommands rather than silently ignoring options.
5. Add focused CliRunner coverage for all forms.

### 6. P1 - The handoff's mandatory acceptance matrix is absent

Only four focused AI tests were delivered. The completion report identifies this gap accurately, but WP-5.1 cannot enter PM validation or acceptance without the required evidence.

Required committed coverage includes all handoff items, particularly:

- malformed YAML, unknown fields, duplicate YAML aliases/keys, unsupported catalog versions, unknown selectors/schemas/placeholders, missing environment variables, unknown dependencies, and cycles;
- task-to-model alias validation and template privacy;
- `chronicle init` create/preserve/force behavior from an installed package;
- `--ai-task list`, exact ID, bounded filters, no implicit whole archive, dry-run, remote guard, missing extra, and command-option conflicts;
- timeout, connection, authentication, rate-limit, invalid/empty JSON, schema validation, unexpected provider response, and sanitized error behavior;
- batch failure isolation, bounded concurrency, retry behavior, Ctrl+C preservation/resume where practical, and no fallback;
- fresh v3, v1-to-v3, and **v2-to-v3** migration preservation, foreign keys, legacy `enrichments`/`knowledge_items`, and FTS behavior;
- every cache invalidator listed in Finding 2, failed-attempt retry, and `--force` append-only auditability;
- no eager LiteLLM import for base/non-AI commands;
- temporary-config CLI smoke and tracked-artifact privacy checks.

Do not satisfy this item with a checklist in the report alone. Each behavioral claim needs focused automated evidence or, where inherently packaging/CLI integration oriented, a reproducible validation command plus an automated regression test where feasible.

## Validation Evidence

PM validation was run from the repository root after confirming:

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

Fresh results:

```text
poetry run pytest tests\test_ai_tasks.py tests\test_db.py -q
20 passed

poetry run pytest
237 passed in 49.21s

poetry run ruff check .
All checks passed!

poetry run chronicle --help
AI root options and all existing commands rendered successfully

git diff --check
passed; only a poetry.lock CRLF/LF warning was emitted

git ls-files "*.db" "*.sqlite" "*.zip" ".chronicle/*" "exports/*"
no output
```

Packaging probe:

```text
poetry build -f wheel --output C:\tmp\wp51-validation-wheel
wheel built successfully

wheel manifest
ai-tasks.default.yaml: absent
ai-models.default.yaml: absent
```

Two read-only validation commands initially encountered the documented Windows sandbox launcher error `CreateProcessAsUserW failed: 1312`; important wheel validation was retried with sandbox escalation. This is not a project failure.

## What Is Accepted As Progress

The following design direction is sound and should be preserved through rework:

- separate strict YAML task and model catalogs;
- lazy optional LiteLLM import behind a Chronicle-owned interface;
- local-first remote guard;
- explicit bounded conversation selection;
- append-only AI attempt table;
- client-side Pydantic validation;
- successful-result caching and `--force` intent;
- no mandatory AI dependency on normal archive commands;
- privacy-safe tracked templates and no tracked private archive artifacts.

This acknowledgement is not package acceptance.

## Rework Delivery Instructions

Return this validation review to the same executor thread.

The executor must:

1. Fix Findings 1-5.
2. Implement the complete focused acceptance matrix in Finding 6.
3. Run all required handoff validation commands from the verified repo `.venv`.
4. Build and inspect/install a wheel from outside the source checkout and prove `chronicle init` works there.
5. Refresh `md/handoffs/reports/WP-5.1-completion-report.md` with exact new evidence and a requirement-by-requirement mapping.
6. Change report status to `ready for PM validation` only when every WP-5.1 acceptance criterion is met.
7. Keep WP-5.1.1 production tasks and WP-5.1.2 real-data evaluation work out of this rework.
8. Do not commit; return the working tree for PM revalidation.

## Revalidation Gate

PM revalidation will check:

- installed-package resource behavior;
- corrected cache identity with metadata/schema/task invalidation;
- actionable no-traceback CLI failures;
- real schema propagation through the LiteLLM adapter;
- dry-run cache counts and actual-model provenance;
- v2 migration preservation;
- complete automated acceptance coverage;
- full regression, Ruff, diff, and privacy evidence.

WP-5.1.1 and WP-5.1.2 remain blocked until WP-5.1 is accepted.

