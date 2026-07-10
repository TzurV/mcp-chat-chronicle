# WP-1.2 Handoff: ChatGPT Export Importer

## Objective
Implement the concrete ChatGPT official-export importer.

This work package parses `conversations.json` from ChatGPT official exports and converts each parsed conversation into the normalized `Conversation` and `Message` models implemented in WP-1.1.

This is parser/importer work only. Do not wire it into the public `chronicle ingest` CLI yet; that belongs to WP-1.4.

## Source Of Truth
Use `md/master-plan.md`, especially:

- Section 2: Core Design Rules
- Section 5: Data Model
- Section 6: M1 / WP-1.2 ChatGPT export importer

Also read:

- `md/agent-operating-notes.md`
- `md/handoffs/WP-1.1-normalized-models-db-layer.md`
- `md/handoffs/reports/WP-1.1-validation-review.md`

## Required Poetry Preflight
Before running any Poetry command, from the repo root run:

```powershell
poetry env info --path
```

Expected path:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If Poetry reports any path outside this repo, stop and fix the shell before continuing. Do not install or run commands in another project's virtualenv.

## Scope
Implement:

- `src/chat_chronicle/adapters/chatgpt_export.py`
- Synthetic ChatGPT export fixtures under `tests/fixtures/chatgpt/`
- Focused parser tests under `tests/`
- A small concrete result type for parsed conversations and per-record parse errors

Do not implement:

- `chronicle ingest` behavior
- DB writes from the importer
- Claude, Gemini, Cursor, or Claude Code importers
- `AdapterProtocol`, `adapters/base.py`, or a general adapter framework
- Real ChatGPT export data
- Any browser/cache/Class C parsing

## Concrete Importer API
Create a concrete module, not a base class:

```python
# src/chat_chronicle/adapters/chatgpt_export.py

from pathlib import Path
from pydantic import BaseModel, Field

from chat_chronicle.models import Conversation


class ChatGPTImportError(BaseModel):
    record_id: str | None = None
    node_id: str | None = None
    error: str
    detail: str | None = None


class ChatGPTImportResult(BaseModel):
    conversations: list[Conversation] = Field(default_factory=list)
    errors: list[ChatGPTImportError] = Field(default_factory=list)


def load_conversations(source: Path | str) -> ChatGPTImportResult:
    ...


def parse_conversations_json(data: object) -> ChatGPTImportResult:
    ...
```

`load_conversations()` must accept:

- a `.zip` official export containing `conversations.json`;
- a directory containing `conversations.json`;
- a direct path to `conversations.json`.

This keeps WP-1.2 testable before the public ingest CLI exists.

## ChatGPT Export Parsing Rules
Parse the official export `conversations.json`, which is expected to be a list of conversation objects.

For each conversation:

- `provider` must be `"chatgpt"`.
- `provider_conv_id` should use the export conversation `id`.
- `title` should use the export `title`, if present.
- `url` should be `https://chatgpt.com/c/{provider_conv_id}`.
- `created_at` should use `create_time`, converted from Unix seconds to UTC `datetime`.
- `updated_at` should use `update_time`, converted from Unix seconds to UTC `datetime`.
- `messages` should come from the selected linear branch of the `mapping` tree.

Tree linearization:

- Prefer `current_node` when it exists and is present in `mapping`.
- Follow `parent` pointers from `current_node` back to the root, then reverse the chain.
- If `current_node` is missing or invalid, select the deepest valid message-bearing chain in `mapping`.
- Ignore mapping nodes with no `message`.
- Preserve message order with sequential `seq` values starting at `0`.

Message mapping:

- `provider_message_id` should use the ChatGPT message `id` when present; otherwise the mapping node id.
- `role` should use `message.author.role` when present.
- `created_at` should use message `create_time`, converted from Unix seconds to UTC `datetime`.
- `body` should be extracted from `message.content.parts`.
- Include only string parts.
- Join multiple string parts with blank lines: `"\n\n".join(parts)`.
- Skip messages with no text body.

Error handling:

- Malformed conversations or nodes must not abort the whole parse.
- Record per-conversation/per-node errors in `ChatGPTImportResult.errors`.
- Errors must be serializable so later WP-1.4 can store them in `ingest_runs.errors_json`.
- Unknown content types, non-string content parts, missing mappings, invalid timestamps, and broken parent chains should be logged as errors or warnings in the result, then skipped or degraded.

Timestamp handling:

- Unix timestamps may be `int`, `float`, `None`, or missing.
- Convert valid timestamps with `datetime.fromtimestamp(value, UTC)`.
- Invalid timestamps become `None` and produce an error entry.

## Fixtures Required
Use synthetic fixtures only. Do not commit real ChatGPT exports.

Create fixtures under:

```text
tests/fixtures/chatgpt/
```

Required fixture scenarios:

- A minimal valid `conversations.json` with one user message and one assistant message.
- A regenerated/edited branch fixture where `current_node` selects the correct branch.
- A fixture with missing/invalid `current_node` where the deepest valid chain is selected.
- A fixture with non-text content parts that are skipped gracefully.
- A fixture with malformed nodes that produce errors but still parse other conversations.
- A zip fixture generated from synthetic JSON, or a test that creates a synthetic zip at runtime under `tmp_path`.

Prefer runtime-created zips in tests to avoid committing binary fixtures unless a committed zip is genuinely useful.

## Tests Required
Add focused tests, likely in `tests/test_chatgpt_export.py`.

Required scenarios:

- `parse_conversations_json()` parses a minimal synthetic export into one normalized `Conversation`.
- The parsed conversation has provider `"chatgpt"`, a ChatGPT URL, title, UTC timestamps, and ordered messages.
- The regenerated branch fixture follows `current_node` and excludes messages from the abandoned branch.
- Missing/invalid `current_node` falls back to the deepest valid chain.
- Non-text/mixed `content.parts` do not crash parsing; string parts are preserved and non-string parts are reported.
- Malformed nodes produce error entries and do not abort parsing of valid conversations.
- `load_conversations()` works for a direct `conversations.json` path.
- `load_conversations()` works for a directory containing `conversations.json`.
- `load_conversations()` works for a synthetic zip containing `conversations.json`.
- Existing WP-0.1 and WP-1.1 tests still pass.

## Acceptance Criteria
WP-1.2 is complete only when all of these are true:

- `src/chat_chronicle/adapters/chatgpt_export.py` exists.
- The importer is concrete and does not introduce `adapters/base.py` or `AdapterProtocol`.
- Official-export `conversations.json` list shape is parsed.
- Tree-shaped `mapping` is linearized using `current_node` when possible.
- Missing/invalid `current_node` falls back to the deepest valid chain.
- Text message bodies are extracted from `content.parts`.
- Non-text or malformed message content is skipped gracefully and recorded in parse errors.
- Unix timestamps are converted to UTC datetimes.
- ChatGPT conversation URLs are constructed as `https://chatgpt.com/c/{conv_id}`.
- The importer returns normalized WP-1.1 `Conversation` and `Message` models.
- Tests use synthetic fixtures only.
- No DB writes or public CLI ingest behavior are added.
- `poetry run pytest` passes.
- `poetry run ruff check .` passes.
- `poetry run chronicle --help` still lists all existing commands.

## Evidence Required
The executor must return a detailed completion report. Missing evidence means the WP is not accepted, even if the implementation appears correct.

The completion report must be written to:

```text
md/handoffs/reports/WP-1.2-completion-report.md
```

The report must include:

- Changed-files summary.
- Exact command output or concise pasted result for:
  - `poetry env info --path`
  - `poetry run pytest`
  - `poetry run ruff check .`
  - `poetry run chronicle --help`
- Test names covering the required fixture scenarios.
- Confirmation that no real ChatGPT exports, DB files, zip exports, secrets, or local private data were committed.
- Explicit checklist mapping each acceptance criterion to `pass`, `fail`, or `not attempted`.

## Technical Guardrails
- Keep parser logic in `src/chat_chronicle/adapters/chatgpt_export.py`.
- Do not add a base adapter abstraction.
- Do not alter the DB schema for this WP.
- Do not implement CLI ingest or stats behavior.
- Do not add network calls.
- Do not add new runtime dependencies unless unavoidable; prefer stdlib `json`, `zipfile`, and `pathlib`.
- Keep all fixtures synthetic.
- Preserve existing DB/model behavior and tests.

## Completion Report Format
The executor must return the report in this structure:

```markdown
# WP-1.2 Completion Report

## Status
One of:

- ready for PM validation
- blocked

## Summary
Briefly describe what was implemented.

## Changed Files
List every changed or created file with a one-line purpose for each.

## Parser API
Describe the functions/classes added in `chatgpt_export.py`.

## Fixture Coverage
List each synthetic fixture/test scenario and the test that covers it.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| Concrete ChatGPT importer module exists | pass/fail/not attempted | File/test reference |
| No adapter base/protocol added | pass/fail/not attempted | File/status evidence |
| `conversations.json` list shape parsed | pass/fail/not attempted | Test reference |
| `current_node` branch selected | pass/fail/not attempted | Test reference |
| Deepest-chain fallback works | pass/fail/not attempted | Test reference |
| Text bodies extracted from `content.parts` | pass/fail/not attempted | Test reference |
| Non-text/malformed content recorded without crash | pass/fail/not attempted | Test reference |
| Unix timestamps become UTC datetimes | pass/fail/not attempted | Test reference |
| ChatGPT URLs constructed | pass/fail/not attempted | Test reference |
| Returns WP-1.1 normalized models | pass/fail/not attempted | Test reference |
| Synthetic fixtures only | pass/fail/not attempted | Git/status evidence |
| No DB writes or public CLI ingest behavior added | pass/fail/not attempted | Scope evidence |
| `poetry run pytest` passes | pass/fail/not attempted | Output |
| `poetry run ruff check .` passes | pass/fail/not attempted | Output |
| `poetry run chronicle --help` still lists commands | pass/fail/not attempted | Output |

## Command Evidence
Paste concise output for all required evidence commands.

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement DB writes | pass/fail |  |
| Did not implement public CLI ingest behavior | pass/fail |  |
| Did not add adapter base/protocol | pass/fail |  |
| Did not add Claude/Gemini/Class B importers | pass/fail |  |
| Did not commit real exports/private data | pass/fail |  |

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
