# WP-1.4 Handoff: CLI Ingest + Stats

## Objective
Wire the accepted Class A importers into the public CLI so a user can ingest one official export file and inspect basic archive statistics.

This work package makes `chronicle ingest <path> --provider auto` and `chronicle stats` functional using the WP-1.1 DB layer and the concrete WP-1.2/WP-1.3 importers after the WP-1.3.1 Claude real-export correction is accepted.

## Dependency Gate
Do not start implementation until all of these are accepted:

- WP-1.2 ChatGPT export importer
- WP-1.3 Claude export importer
- WP-1.3.1 Claude real export content-block correction

If WP-1.3.1 is not accepted yet, return `blocked` and state that the Claude real-export parser correction dependency is missing.

## Source Of Truth
Use `md/master-plan.md`, especially:

- Section 2: Core Design Rules
- Section 4: CLI surface
- Section 5: Data Model
- Section 6: M1 / WP-1.4 CLI ingest + stats

Also read:

- `md/agent-operating-notes.md`
- `md/handoffs/WP-1.1-normalized-models-db-layer.md`
- `md/handoffs/reports/WP-1.1-validation-review.md`
- `md/handoffs/WP-1.2-chatgpt-export-importer.md`
- `md/handoffs/reports/WP-1.2-validation-review.md`
- `md/handoffs/WP-1.3-claude-export-importer.md`
- `md/handoffs/reports/WP-1.3-validation-review.md` once it exists
- `md/handoffs/WP-1.3.1-claude-real-export-content-blocks.md`
- `md/handoffs/reports/WP-1.3.1-validation-review.md` once it exists

## Required Poetry Preflight
Before running any Poetry command, from the repo root run:

```powershell
poetry env info --path
```

Expected path:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If Poetry reports any path outside this repo, stop and fix the shell before continuing. Do not install or run commands in another project's virtualenv. If this machine has an inherited `VIRTUAL_ENV`, clear it for Poetry commands or use a fresh terminal.

## Scope
Implement:

- Functional `chronicle ingest <path> --provider auto`.
- Functional `chronicle stats`.
- Provider auto-detection for ChatGPT and Claude official exports.
- DB writes using WP-1.1 `upsert_conversation()` and ingest run helpers.
- Source row creation/reuse for single-file official exports.
- Tests proving ingest, idempotency, provider detection, parse-error handling, and stats output.

Do not implement:

- `chronicle ingest-folder`.
- `chronicle collect`.
- `chronicle source add/list/disable`.
- `chronicle search` or `chronicle open`.
- Adapter base/protocol abstraction.
- Gemini or Class B importers.
- Any real chat/export fixtures.

## DB Behavior
Use the WP-1.1 DB layer.

Default DB:

```text
C:\work\Github\mcp-chat-chronicle\.chronicle\chronicle.db
```

Add a `--db-path` option to `chronicle ingest` and `chronicle stats` so tests and users can target a temp/project-local DB explicitly:

```powershell
poetry run chronicle ingest path\to\export.zip --provider auto --db-path .\.chronicle\chronicle.db
poetry run chronicle stats --db-path .\.chronicle\chronicle.db
```

If `--db-path` is omitted, use `CHAT_CHRONICLE_DB` or the project-local default from `db.default_db_path()`.

Do not create DB files during import-time module loading. The DB may be created when the command opens the connection.

## Provider Detection
`chronicle ingest <path> --provider auto` must detect:

- ChatGPT official export:
  - `conversations.json` is a list.
  - At least one conversation object has a `mapping` object or ChatGPT-like `current_node`.
- Claude official export:
  - `conversations.json` is a list.
  - At least one conversation object has Claude-like fields such as `uuid` and `chat_messages`.

Input path can be:

- `.zip` containing `conversations.json`;
- directory containing `conversations.json`;
- direct `conversations.json` path.

Detection rules:

- If provider is explicitly `chatgpt`, call the ChatGPT importer.
- If provider is explicitly `claude`, call the Claude importer.
- If provider is `auto`, inspect only enough data to choose ChatGPT or Claude.
- If detection is ambiguous or unsupported, exit non-zero with a clear message and do not write an ingest run.
- Do not read or parse browser caches.

## Source Row Rules
For `chronicle ingest`, create or reuse one `sources` row per provider + absolute source path.

Use:

- `source_type = "official_export"`
- `provider = "chatgpt"` or `"claude"`
- `path_or_config = resolved absolute source path`
- `enabled = 1`

If the row already exists, reuse it and update `last_seen_at` / `last_ingested_at` as appropriate.

If WP-1.1 did not provide source helper functions, implement the minimal source helpers in `db.py` or a small local function near the CLI, but keep DB SQL centralized where practical. Do not introduce a repository-wide abstraction layer.

## Ingest Run Rules
Every successful parse attempt must create an `ingest_runs` row.

For each importer result:

- `conversations_seen` = number of parsed normalized conversations returned by the importer.
- For each conversation, call `upsert_conversation(conn, source_id, conversation)`.
- Count `added`, `updated`, and `skipped` from `UpsertResult.status`.
- Store importer errors in `errors_json` as a JSON array of serializable dicts.
- `status = "success"` when the command completed even if parse errors were recorded.
- Use `status = "failed"` only when the command cannot complete the ingest attempt.

Important: parse errors are data, not command failure, unless no provider can be detected or the source cannot be read at all.

After ingest, rebuild FTS by calling `rebuild_fts(conn)` so later search work has a current index.

## CLI Output
Use Rich output, but keep it simple and testable.

`chronicle ingest` should print:

- detected/effective provider;
- DB path;
- source path;
- conversations seen;
- added / updated / skipped counts;
- parse error count;
- ingest run id.

`chronicle stats` should print:

- DB path;
- total conversations;
- total messages;
- counts by provider;
- per-source summary including provider, path, enabled, last ingested time;
- most recent ingest runs with run id, provider/source id, status, seen, added, updated, skipped, error count.

If the DB does not exist yet, `chronicle stats` should either initialize an empty DB and show zero counts or open the DB through the standard `connect()` path and show zero counts. It must not crash.

## Tests Required
Add focused tests, likely in `tests/test_cli_ingest_stats.py`.

Use synthetic fixtures only. Reuse accepted synthetic fixtures from:

- `tests/fixtures/chatgpt/`
- `tests/fixtures/claude/` once WP-1.3 and WP-1.3.1 exist

Required scenarios:

- `chronicle ingest <chatgpt-json> --provider auto --db-path <tmp>` detects ChatGPT and inserts conversations/messages.
- `chronicle ingest <claude-json> --provider auto --db-path <tmp>` detects Claude and inserts conversations/messages.
- Explicit `--provider chatgpt` works.
- Explicit `--provider claude` works.
- Running the same ingest twice returns zero added/updated on the second run and increments skipped.
- A fixture with importer parse errors stores them in `ingest_runs.errors_json` without aborting valid conversations.
- Unsupported/ambiguous provider exits non-zero and does not write an ingest run.
- `chronicle stats --db-path <tmp>` shows total conversations/messages and provider counts after ingest.
- `chronicle stats --db-path <tmp-empty>` works on an empty DB.
- Existing WP-0.1, WP-1.1, WP-1.2, WP-1.3, and WP-1.3.1 tests still pass.

## Acceptance Criteria
WP-1.4 is complete only when all of these are true:

- `chronicle ingest` is functional for ChatGPT and Claude official exports.
- `--provider auto` detects ChatGPT and Claude by file signature.
- Explicit `--provider chatgpt` and `--provider claude` work.
- Unsupported/ambiguous inputs fail clearly without writing ingest runs.
- Source rows are created/reused correctly for provider + resolved source path.
- Every successful parse attempt records an `ingest_runs` row.
- Importer parse errors are stored in `ingest_runs.errors_json`.
- Re-ingesting unchanged fixtures adds and updates zero rows.
- FTS is rebuilt after ingest.
- `chronicle stats` reports total counts, provider counts, source summaries, and recent ingest runs.
- `chronicle stats` works on an empty DB.
- No `ingest-folder`, `collect`, source CRUD, search, or open behavior is implemented.
- No adapter base/protocol is introduced.
- Tests use synthetic fixtures only.
- `poetry run pytest` passes.
- `poetry run ruff check .` passes.
- `poetry run chronicle --help` still lists all existing commands.

## Evidence Required
The executor must return a detailed completion report. Missing evidence means the WP is not accepted, even if the implementation appears correct.

The completion report must be written to:

```text
md/handoffs/reports/WP-1.4-completion-report.md
```

The report must include:

- Changed-files summary.
- Dependency confirmation that WP-1.2, WP-1.3, and WP-1.3.1 validation reports exist and are accepted.
- Exact command output or concise pasted result for:
  - `poetry env info --path`
  - `poetry run pytest`
  - `poetry run ruff check .`
  - `poetry run chronicle --help`
  - at least one ChatGPT ingest command against a temp/project-local DB;
  - at least one Claude ingest command against a temp/project-local DB;
  - `chronicle stats` output after ingest.
- Test names covering the required scenarios.
- Confirmation that no real exports, DB files, zip exports, secrets, or local private data were committed.
- Explicit checklist mapping each acceptance criterion to `pass`, `fail`, or `not attempted`.

## Technical Guardrails
- Keep importer modules concrete.
- Do not add `adapters/base.py`, `AdapterProtocol`, or a framework.
- Keep CLI implementation simple; no background collection or source management yet.
- Keep DB writes through WP-1.1 DB helpers where possible.
- Do not add new runtime dependencies unless unavoidable.
- Do not commit generated DB files or real exports.
- Preserve accepted ChatGPT and Claude parser behavior.

## Completion Report Format
The executor must return the report in this structure:

```markdown
# WP-1.4 Completion Report

## Status
One of:

- ready for PM validation
- blocked

## Dependency Check
Confirm WP-1.2, WP-1.3, and WP-1.3.1 are accepted, with validation report paths.

## Summary
Briefly describe what was implemented.

## Changed Files
List every changed or created file with a one-line purpose for each.

## CLI Behavior
Describe the implemented `ingest` and `stats` behavior, including provider detection and DB path handling.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| `chronicle ingest` functional for ChatGPT and Claude | pass/fail/not attempted | Command/test evidence |
| `--provider auto` detects both providers | pass/fail/not attempted | Test evidence |
| Explicit providers work | pass/fail/not attempted | Test evidence |
| Unsupported/ambiguous inputs fail clearly | pass/fail/not attempted | Test evidence |
| Source rows created/reused | pass/fail/not attempted | Test evidence |
| Successful parse attempts record ingest runs | pass/fail/not attempted | Test evidence |
| Parse errors stored in `errors_json` | pass/fail/not attempted | Test evidence |
| Re-ingest unchanged fixtures adds/updates zero | pass/fail/not attempted | Test evidence |
| FTS rebuilt after ingest | pass/fail/not attempted | Test evidence |
| `stats` reports counts/sources/runs | pass/fail/not attempted | Output/test evidence |
| `stats` works on empty DB | pass/fail/not attempted | Test evidence |
| No out-of-scope commands implemented | pass/fail/not attempted | Scope evidence |
| No adapter base/protocol added | pass/fail/not attempted | File/status evidence |
| Synthetic fixtures only | pass/fail/not attempted | Git/status evidence |
| `poetry run pytest` passes | pass/fail/not attempted | Output |
| `poetry run ruff check .` passes | pass/fail/not attempted | Output |
| `poetry run chronicle --help` still lists commands | pass/fail/not attempted | Output |

## Command Evidence
Paste concise output for all required evidence commands.

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement ingest-folder/collect/source CRUD | pass/fail |  |
| Did not implement search/open behavior | pass/fail |  |
| Did not add adapter base/protocol | pass/fail |  |
| Did not add Gemini/Class B importers | pass/fail |  |
| Did not commit real exports/private data or DB files | pass/fail |  |

## Risks Or Follow-Ups
List known issues, assumptions, or recommended follow-up tasks.
```

## Completion Status Expected
Return one of:

- `ready for PM validation`
- `blocked`

If blocked, include:

- the exact blocker
- what was attempted
- what decision or missing information is needed
