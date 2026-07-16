# WP-1.3.2 Handoff: OpenAI Codex Local Extractor

## Objective
Implement a concrete OpenAI Codex local-store extractor before WP-1.4 so Codex sessions can be ingested alongside ChatGPT and Claude.

ChatGPT support already exists as WP-1.2 (`chatgpt_export.py`). This work package adds the missing Codex parser/extractor only. WP-1.4 will wire the accepted ChatGPT, Claude, and Codex adapters into `chronicle ingest`.

## Source Classification
OpenAI Codex local sessions are **Class B local durable stores**, not official exports.

Current machine evidence, inspected by keys/types and filenames only:

```text
Codex home: `%USERPROFILE%\.codex`
Session index: `%USERPROFILE%\.codex\session_index.jsonl`
Session files: `%USERPROFILE%\.codex\sessions\<year>\<month>\<day>\rollout-*.jsonl`
Archived sessions: `%USERPROFILE%\.codex\archived_sessions`
```

Observed `session_index.jsonl` keys:

```text
id, thread_name, updated_at
```

Observed session JSONL line shape:

```text
top-level keys: timestamp, type, payload
top-level types: session_meta, turn_context, response_item, event_msg
```

Observed payload shapes:

```text
session_meta keys:
  id, timestamp, cwd, originator, cli_version, instructions, source, model_provider

turn_context keys:
  cwd, approval_policy, sandbox_policy, model, effort, summary

response_item keys:
  type, role, content, summary, encrypted_content, name, arguments, call_id,
  output, status, input, ghost_commit

event_msg keys:
  type, message, text, images, info, rate_limits
```

Observed `response_item.type` values:

```text
message, reasoning, function_call, function_call_output, custom_tool_call,
custom_tool_call_output, ghost_snapshot
```

Observed message content block types:

```text
input_text, output_text
```

Do not commit real Codex session files, copied transcript text, private paths beyond the generic paths above, secrets, auth files, SQLite files, or local cache data.

## Dependency Gate
Do not start implementation until WP-1.1 is accepted.

The implementation should preserve all accepted WP-1.2, WP-1.3, and WP-1.3.1 behavior.

## Source Of Truth
Use:

- `md/master-plan.md`, especially Core Design Rules and Class B ground rules.
- `md/agent-operating-notes.md`.
- `md/handoffs/reports/WP-1.1-validation-review.md`.
- `md/handoffs/reports/WP-1.2-validation-review.md`.
- `md/handoffs/reports/WP-1.3.1-validation-review.md`.
- The local Codex shape evidence above.

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

- A concrete extractor module, likely `src/chat_chronicle/adapters/openai_codex.py`.
- `load_conversations(source: Path | str)` that accepts:
  - one Codex session `.jsonl` file;
  - a directory containing Codex session `.jsonl` files;
  - the Codex home directory containing `session_index.jsonl` and `sessions/`.
- `parse_session_jsonl(raw: str, *, source_name: str | None = None)` or equivalent testable parser function.
- Normalized `Conversation` and `Message` output using WP-1.1 models.
- Per-record/per-line extractor errors as serializable Pydantic models, not raised exceptions.
- Synthetic fixtures only.

Do not implement:

- CLI ingest or stats behavior.
- DB writes.
- Provider detection in the CLI.
- `collect`, `scan-local`, source CRUD, or scheduler behavior.
- Adapter base/protocol abstraction.
- Claude Code, Cursor, Gemini, Copilot, or ChatGPT changes unless needed for test compatibility.
- Real/private Codex data fixtures.

## Parser Rules
Provider:

```text
provider = "openai_codex"
```

Conversation identity:

- Prefer `session_meta.payload.id` when present.
- Else derive a stable ID from the session filename stem.
- `url` must be `None` because local Codex sessions do not have a reliable web deep link.

Conversation title:

- If a `session_index.jsonl` entry is available for the session id, use `thread_name`.
- Else use a conservative fallback from the session filename or first meaningful user message prefix.
- Do not expose local filesystem paths as titles.

Timestamps:

- Use `session_meta.payload.timestamp` or the first valid line timestamp as `created_at`.
- Use the newest valid line timestamp or session index `updated_at` as `updated_at`.
- Convert ISO timestamps to aware UTC datetimes.
- Invalid timestamps should become extractor errors and should not abort the session.

Messages:

- Include only user-visible transcript messages:
  - `response_item` where `payload.type == "message"` and `payload.role` is one of `user`, `assistant`, or `developer`;
  - extract text from `payload.content[]` blocks where block type is `input_text` or `output_text` and `text` is a non-empty string.
- Also support `event_msg` fallback for visible text if needed:
  - `payload.type == "user_message"` should map to role `user`;
  - `payload.type == "agent_message"` should map to role `assistant`;
  - use `payload.text` or `payload.message` when it is a non-empty string.
- Avoid duplicate messages if the same visible message appears as both `response_item` and `event_msg`. Prefer `response_item` as the canonical source.
- Skip non-transcript metadata such as `reasoning`, `function_call`, `function_call_output`, `custom_tool_call`, `custom_tool_call_output`, `ghost_snapshot`, `turn_context`, token counts, rate limits, and encrypted content.
- Skipped known metadata should not produce parse errors.
- Unknown or malformed records should produce serializable extractor errors and parsing should continue.

Sequence:

- Output messages in file order.
- `seq` must be contiguous after skipped metadata.

Privacy:

- Do not include function arguments, tool outputs, encrypted content, local full paths, auth material, or raw environment details in message bodies.
- It is acceptable for a message body to contain user-visible chat text from the synthetic fixture only.

## Tests Required
Add focused tests, likely in `tests/test_openai_codex.py`, with synthetic fixtures under `tests/fixtures/openai_codex/`.

Required scenarios:

- Minimal session with `session_meta` and one user/assistant `response_item` pair parses to one `Conversation`.
- `input_text` and `output_text` content blocks become ordered message bodies.
- Known metadata rows (`turn_context`, `reasoning`, function calls, tool outputs, token counts, rate limits, encrypted content, ghost snapshots) are skipped without errors.
- Event-message fallback handles `user_message` / `agent_message` when response items are absent.
- Duplicate response/event visible messages do not create duplicate normalized messages.
- Invalid JSONL line records an error and does not abort the rest of the file.
- Missing session id falls back to filename-derived identity.
- Directory loading finds nested `sessions/<year>/<month>/<day>/*.jsonl` files.
- Optional `session_index.jsonl` title/updated_at metadata is applied when present.
- Errors are JSON-serializable for later `ingest_runs.errors_json`.
- Existing ChatGPT, Claude, DB, and CLI stub tests still pass.

## Acceptance Criteria
WP-1.3.2 is complete only when all of these are true:

- Concrete OpenAI Codex extractor module exists.
- It accepts one `.jsonl` file and a Codex sessions/home directory.
- It returns WP-1.1 normalized `Conversation` / `Message` models.
- Provider is `openai_codex`.
- URL is `None`.
- Visible user/assistant/developer messages are extracted in order with contiguous `seq`.
- Known Codex metadata/tool/reasoning records are skipped without noisy errors.
- Malformed/unknown records produce serializable extractor errors without aborting valid messages.
- Synthetic fixtures cover the observed local Codex JSONL shape.
- No real/private Codex data, auth files, DB files, SQLite files, or exports are committed.
- No DB writes, CLI ingest behavior, provider detection, collect/scan-local, or adapter abstraction is introduced.
- `poetry run pytest` passes.
- `poetry run ruff check .` passes.
- `poetry run chronicle --help` still lists all existing commands.

## Evidence Required
The executor must return a detailed completion report. Missing evidence means the WP is not accepted, even if the implementation appears correct.

The completion report must be written to:

```text
md/handoffs/reports/WP-1.3.2-completion-report.md
```

The report must include:

- Changed-files summary.
- Exact command output or concise pasted result for:
  - `poetry env info --path`
  - `poetry run pytest`
  - `poetry run ruff check .`
  - `poetry run chronicle --help`
- Test names covering each required parser scenario.
- Confirmation that no real Codex sessions, auth files, DB files, SQLite files, zip exports, secrets, or local private data were committed.
- Explicit checklist mapping each acceptance criterion to `pass`, `fail`, or `not attempted`.
- Short note explaining what WP-1.4 must call to ingest Codex sessions.

## Technical Guardrails

- Keep `openai_codex.py` concrete.
- Do not add `adapters/base.py`, `AdapterProtocol`, or a framework.
- Treat Codex local storage as undocumented and version-sensitive.
- Parse-don't-validate: tolerate unknown rows, record errors only for malformed/unexpected data that affects parsing.
- Do not read from live SQLite databases in this WP.
- Do not persist tool calls or reasoning as separate entities.
- Use synthetic fixtures only.

## Completion Report Format
The executor must return the report in this structure:

```markdown
# WP-1.3.2 Completion Report

## Status
One of:

- ready for PM validation
- blocked

## Dependency Check
Confirm WP-1.1, WP-1.2, WP-1.3, and WP-1.3.1 are accepted, with validation report paths.

## Summary
Briefly describe what was implemented.

## Changed Files
List every changed or created file with a one-line purpose for each.

## Parser Behavior
Describe session discovery, identity/title handling, text extraction, metadata skipping, event fallback, duplicate avoidance, and error handling.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| Concrete OpenAI Codex extractor exists | pass/fail/not attempted | File/test evidence |
| Accepts one `.jsonl` file and sessions/home directory | pass/fail/not attempted | Test evidence |
| Returns normalized models | pass/fail/not attempted | Test evidence |
| Provider is `openai_codex` and URL is `None` | pass/fail/not attempted | Test evidence |
| Visible messages extracted in order with contiguous `seq` | pass/fail/not attempted | Test evidence |
| Known metadata/tool/reasoning records skipped without noisy errors | pass/fail/not attempted | Test evidence |
| Malformed/unknown records produce serializable errors | pass/fail/not attempted | Test evidence |
| Synthetic fixtures cover observed Codex JSONL shape | pass/fail/not attempted | File/test evidence |
| No private Codex data committed | pass/fail/not attempted | Git/status evidence |
| No DB/CLI/provider detection/collect/scan/adapter abstraction added | pass/fail/not attempted | Scope evidence |
| `poetry run pytest` passes | pass/fail/not attempted | Output |
| `poetry run ruff check .` passes | pass/fail/not attempted | Output |
| `poetry run chronicle --help` still lists commands | pass/fail/not attempted | Output |

## Command Evidence
Paste concise output for all required evidence commands.

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement CLI ingest/stats | pass/fail |  |
| Did not add DB writes | pass/fail |  |
| Did not add provider detection | pass/fail |  |
| Did not add collect/scan-local behavior | pass/fail |  |
| Did not add adapter base/protocol | pass/fail |  |
| Did not commit real Codex/private data or DB files | pass/fail |  |

## WP-1.4 Impact
State the public function(s) WP-1.4 should call and the expected provider string.

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
