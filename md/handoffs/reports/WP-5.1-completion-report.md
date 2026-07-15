# WP-5.1 Completion Report: YAML AI-Task Runner + LiteLLM

## Status

`ready for PM validation`

All findings in `WP-5.1-validation-review.md` and the narrow generation-default
finding in `WP-5.1-validation-review-2.md` are addressed. WP-5.1 supplies
infrastructure only; the four production conversation-intelligence tasks remain
out of scope for WP-5.1.1.

## Executive summary

Chronicle now supports independently editable, strict YAML task and model
catalogs; root `--ai-task` discovery/execution; deterministic code-owned input
selectors and output schemas; a lazy LiteLLM adapter behind a Chronicle-owned
interface; conservative remote authorization; bounded foreground async work;
schema-v3 append-only result storage; and exact reproducible caching. Normal
archive commands neither import LiteLLM nor call a model.

The validation rework additionally packages both templates inside the wheel,
matches every request/output-interpretation component during cache lookup,
propagates the Pydantic JSON schema to LiteLLM, preserves actual provenance on
validation failures, makes CLI failures actionable without tracebacks, and
reports dry-run cache hits/misses.

## Files changed

- Source: `src/chat_chronicle/ai.py`, `src/chat_chronicle/ai_config.py`,
  `src/chat_chronicle/cli.py`, `src/chat_chronicle/db.py`.
- Installed resources: `src/chat_chronicle/resources/__init__.py`,
  `src/chat_chronicle/resources/ai-tasks.default.yaml`, and
  `src/chat_chronicle/resources/ai-models.default.yaml`.
- Root templates/package: `ai-tasks.default.yaml`, `ai-models.default.yaml`,
  `pyproject.toml`, `poetry.lock`.
- Focused tests: `tests/test_ai_tasks.py`, `tests/test_ai_config_matrix.py`,
  `tests/test_ai_adapter.py`, `tests/test_ai_cache_matrix.py`,
  `tests/test_ai_execution_matrix.py`, `tests/test_cli_ai_tasks.py`, and
  `tests/test_ai_packaging.py`.
- Migration/init regression tests: `tests/test_db.py` and
  `tests/test_cli_config_collect.py`.
- Docs: `README.md`, `md/development-ledger.md`, this report.

## Final CLI contract

- `chronicle --ai-task list` loads the two local catalogs without LiteLLM.
- Execution requires exactly one exact `--conversation-id` or positive bounded
  `--limit`; batch selection accepts provider/since/until filters with accepted
  date-only end-of-day semantics.
- `--model-profile`, `--db-path`, `--force`, `--dry-run`, and invocation-only
  `--allow-remote` are supported.
- List/exact/batch/normal-command option conflicts fail clearly. No selection
  ever defaults to the entire archive.
- Dry-run prints task/version, logical profile, resolved model, local/remote
  classification, selected IDs/count, and exact effective cache hits/misses.
  It makes zero LLM calls and renders no transcript.
- Execution prints completed/cached/failed counts, result/conversation IDs,
  logical and actual provider/model provenance, and a validated single result.
  A single/all-failed run exits nonzero; a mixed batch continues and reports all
  outcomes.

## Task and model YAML

Task schema version 1 contains enabled state, stable task version, description,
logical model alias, code-owned selector/schema, external system/user prompts,
bounded generation, dependency names, and deterministic selector budgets.
Unknown fields, catalog versions, duplicate YAML keys, unsafe tags, selectors,
schemas, placeholders, dependencies, cycles, and task-to-model aliases fail with
file/task/field context. Interpolation is allowlisted and non-evaluating.

Model schema version 1 contains model identifier, optional API base, credential
environment-variable name, declared remote state, timeout, retries, concurrency,
generation defaults, and `structured_output`. Credential values never live in
YAML. `structured_output: true` sends the code-owned JSON schema; an explicitly
false profile requests JSON-object mode while client-side Pydantic validation
remains mandatory.

Generation precedence is resolved per field. A model profile owns concrete,
bounded safe defaults for temperature and maximum tokens. A task's generation
mapping contains optional overrides, so it may inherit both values or override
only one. The resolved effective values are sent in `CompletionRequest` and
included in effective model provenance/cache identity. A changed profile value
invalidates only when it changes the effective request; a profile default masked
by a task override keeps the same request and cache hit. The complete task hash
still distinguishes explicit task policy from inherited policy intentionally.

The tracked and installed templates are byte-identical and privacy-safe. The
default `service-local` example targets loopback LM Studio and resolves the
model from `CHRONICLE_LOCAL_MODEL`. `chronicle init` reads templates through
`importlib.resources`, creates both local catalogs, preserves them by default,
and overwrites only with `--force`. `CHAT_CHRONICLE_AI_CONFIG_DIR` supports
isolated automation while `.chronicle` remains the normal location.

## Local/remote privacy classification

Only explicit localhost/127.0.0.1/`::1` API bases can be local. Declared remote,
known provider routing without loopback, ambiguous profiles, and every
non-loopback endpoint are remote even if YAML claims `remote: false`. Every
remote execution needs `--allow-remote`; the flag mutates no configuration and
a following invocation is blocked again.

## Internal LLM boundary and failure behavior

`LLMClient.complete()` exchanges Chronicle-owned request/response objects.
`LiteLLMClient` imports LiteLLM only inside `complete()`, uses `acompletion`,
passes the actual JSON schema as a strict `json_schema` response format, and
does not expose provider objects or configure fallback models. The optional
extra is `litellm>=1.74,<2.0`; missing installation reports
`poetry install -E enrich`.

Client-side JSON parsing and Pydantic validation always run. Timeout,
connection, authentication, rate-limit, missing dependency, invalid/empty JSON,
schema validation, and unexpected response failures are normalized. Stored and
printed details are bounded and redact credentials and selected transcript
content. If a provider response exists before JSON/schema failure, its actual
provider/model and usage remain stored.

Concurrency is a profile-bounded semaphore (default one). Attempts commit per
conversation. A failure does not abort a batch; interruption leaves completed
rows committed, and rerun resumes from successful cache hits. No process or
task remains after foreground CLI exit.

## Schema-v3 migration and preservation

Schema v3 adds only append-only `ai_task_results` and indexes. Each attempt
stores conversation FK, logical task/version, input/prompt/task hashes, output
schema name/version, logical profile, resolved model hash, actual provider/model,
validated JSON or sanitized error, distinct real start/completion timestamps,
latency, usage, and selection/truncation metadata.

Automated tests cover fresh v3, v1-to-v3, and v2-to-v3. V2 evidence explicitly
preserves conversation/message/source rows plus legacy `enrichments` and
`knowledge_items`, passes `PRAGMA foreign_key_check`, rebuilds FTS, and finds a
pre-migration synthetic message.

## Exact cache identity and invalidation

A hit must be a successful row matching all of:

1. conversation ID;
2. logical task name and task version;
3. canonical selected-input hash (text, selected IDs/roles/order/range,
   truncation, provider, title, start date, and last-active date);
4. rendered system/user prompt hash;
5. canonical complete task-definition hash;
6. output schema name and explicit code-owned version;
7. logical model-profile alias; and
8. canonical resolved effective model-profile hash excluding credential value,
   with generation replaced by the per-field effective values.

Individual tests invalidate body, role, order, title, start/last-active date,
selected messages, prompt, generation, task version/name, selector/budget,
schema name/version, model alias, and model definition. Credential value changes
neither leak nor invalidate. Failed rows retry. `--force` bypasses matching
successes and appends a new auditable attempt.

Generation-specific request/cache tests prove profile inheritance, temperature-
only override, token-only override, full override, effective-default
invalidation, non-effective masked-default cache reuse, and validation bounds.

## Validation evidence

- `poetry env info --path` -> repository-local `.venv` before every Poetry
  command group.
- Focused collection: 127 tests across the ten AI/config/DB/init files; all
  passed.
- `poetry run pytest` -> `313 passed in 44.74s`.
- `poetry run ruff check .` -> `All checks passed!`.
- `poetry run chronicle --help` -> all existing commands and root AI options.
- Temporary `poetry run chronicle --ai-task list` -> disabled example task and
  local service profile; no LiteLLM import/call.
- Temporary `chronicle stats` -> zero synthetic conversations; temporary search
  for `scan-local` -> `No results`.
- Built `chat_chronicle-0.1.0-py3-none-any.whl`, installed it with `--no-deps`
  into a temporary target outside the checkout, imported that installed copy,
  and invoked `init`: exit 0, both AI catalogs created. The automated packaging
  regression repeats wheel-manifest and outside-checkout initialization checks.
- Synthetic mock smoke: first run stored a validated success; unchanged rerun
  was cached with zero calls; prompt/model/task/schema/input changes executed;
  force appended; failed attempts retried; remote was blocked without the flag;
  no transcript was printed or stored in errors.
- No real archive, credential, network provider, or local LM Studio call was
  used. Optional real-provider smoke was not performed and is not an acceptance
  dependency.

## Privacy and working-tree evidence

The final tracked-artifact check is recorded after validation. Only source,
templates, tests, docs, and package metadata are in the WP-5.1 change set.
Existing tracked JSONL files are synthetic fixtures under `tests/fixtures`.
No DB, ZIP, export, generated local AI config, credential, or private transcript
artifact is tracked. The working tree also contains pre-existing owner planning
changes in `md/master-plan.md` and the WP-5.1.2 handoff; this executor preserved
them and they are not part of the WP-5.1 implementation claim.

## Known limitations and follow-ups

- The tracked example task is deliberately disabled and documentation-only.
- The four production tasks, their final schemas/prompts, and real-history
  teacher/reference evaluation remain WP-5.1.1/WP-5.1.2 scope.
- Provider schema capabilities vary; profiles that cannot accept JSON Schema
  must explicitly disable provider enforcement and still pass local Pydantic
  validation.
- A real local-provider smoke remains optional.

## Acceptance checklist

1. YAML task discovery and generic execution: code + CLI tests.
2. Internal LiteLLM boundary: adapter schema/error/dependency tests.
3. Independent external task/model policy: strict catalog tests.
4. Pydantic YAML and output authority: config/execution tests.
5. Base/non-AI isolation: import, wheel `--no-deps`, and full regression tests.
6. Local default/per-run remote gate: classification and repeated-CLI tests.
7. Explicit bounded selection: exact/batch/conflict/filter tests.
8. Safe schema v3 fresh/v1/v2 migration: DB preservation tests.
9. Complete successful cache identity: individual invalidation matrix.
10. Failed retry and append-only force: attempt-history tests.
11. Bounded foreground async/resume/isolation: concurrency/interruption tests.
12. Clear non-destructive failures: adapter, runner, and CLI tests.
13. Existing CLI/ingest/search/FTS behavior: full 313-test suite.
14. Tests and Ruff: green.
15. README: optional install/config/privacy/cache behavior documented.
16. Detailed report: this file.
17. Privacy: synthetic-only tests and final tracked-artifact gate.
