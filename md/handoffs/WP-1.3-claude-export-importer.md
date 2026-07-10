# WP-1.3 Handoff: Claude Export Importer

## Objective
Implement the concrete Claude official-export importer.

This work package parses Claude official-export `conversations.json` files and converts each parsed conversation into the normalized `Conversation` and `Message` models implemented in WP-1.1.

This is parser/importer work only. Do not wire it into the public `chronicle ingest` CLI yet; that belongs to WP-1.4.

## Source Of Truth
Use `md/master-plan.md`, especially:

- Section 2: Core Design Rules
- Section 5: Data Model
- Section 6: M1 / WP-1.3 Claude export importer

Also read:

- `md/agent-operating-notes.md`
- `md/handoffs/WP-1.1-normalized-models-db-layer.md`
- `md/handoffs/reports/WP-1.1-validation-review.md`
- `md/handoffs/WP-1.2-chatgpt-export-importer.md`
- `md/handoffs/reports/WP-1.2-validation-review.md`

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

- `src/chat_chronicle/adapters/claude_export.py`
- Synthetic Claude export fixtures under `tests/fixtures/claude/`
- Focused parser tests under `tests/`
- A small concrete result type for parsed conversations and per-record parse errors

First task:

- Verify the real Claude official-export shape before finalizing parser assumptions.
- Do not commit the real export.
- If a real export is available, sanitize the observed structure into synthetic fixtures.
- If no real export is available, implement against the master-plan shape (`uuid`, `name`, `created_at`, `chat_messages[]`) and explicitly record the assumption in the completion report.

Do not implement:

- `chronicle ingest` behavior
- DB writes from the importer
- ChatGPT changes, Gemini, Cursor, Claude Code, or other importers
- `AdapterProtocol`, `adapters/base.py`, or a general adapter framework
- Real Claude export data
- Any browser/cache/Class C parsing

## Concrete Importer API
Create a concrete module, not a base class:

```python
# src/chat_chronicle/adapters/claude_export.py

from pathlib import Path
from pydantic import BaseModel, Field

from chat_chronicle.models import Conversation


class ClaudeImportError(BaseModel):
    record_id: str | None = None
    message_id: str | None = None
    error: str
    detail: str | None = None


class ClaudeImportResult(BaseModel):
    conversations: list[Conversation] = Field(default_factory=list)
    errors: list[ClaudeImportError] = Field(default_factory=list)


def load_conversations(source: Path | str) -> ClaudeImportResult:
    ...


def parse_conversations_json(data: object) -> ClaudeImportResult:
    ...
```

`load_conversations()` must accept:

- a `.zip` official export containing `conversations.json`;
- a directory containing `conversations.json`;
- a direct path to `conversations.json`.

This keeps WP-1.3 testable before the public ingest CLI exists and mirrors the accepted WP-1.2 importer shape.

## Claude Export Parsing Rules
Parse the official export `conversations.json`, expected to be a flat list of conversation objects.

For each conversation:

- `provider` must be `"claude"`.
- `provider_conv_id` should use the export conversation `uuid`.
- `title` should use `name`, if present.
- `url` should be `https://claude.ai/chat/{uuid}`.
- `created_at` should use conversation `created_at`, converted to UTC `datetime`.
- `updated_at` should use conversation `updated_at` if present; otherwise use the latest parsed message timestamp; otherwise fall back to `created_at`.
- `messages` should come from `chat_messages[]` in array order.

Message mapping:

- `provider_message_id` should use message `uuid` or `id` if present; otherwise `None`.
- `role` should use message `sender` or `role`, whichever exists in the verified export shape.
- `created_at` should use message `created_at` if present.
- `body` should be extracted from the message text content.
- Preserve message order with sequential `seq` values starting at `0`.
- Skip messages with no text body.

Content extraction:

- Support plain string text fields when present.
- Support list/block content when present, preserving text blocks and skipping non-text blocks.
- Join multiple text fragments with blank lines: `"\n\n".join(parts)`.
- Record non-text or unknown content as parse errors while continuing.

Timestamp handling:

- Support ISO8601 strings with `Z` or explicit offsets.
- Support Unix timestamps only if the verified export shape contains them.
- Invalid timestamps become `None` and produce an error entry.
- Store normalized model timestamps as aware UTC datetimes.

Error handling:

- Malformed conversations or messages must not abort the whole parse.
- Record per-conversation/per-message errors in `ClaudeImportResult.errors`.
- Errors must be serializable so WP-1.4 can store them in `ingest_runs.errors_json`.
- Missing conversation UUID should skip that conversation and record an error.
- Missing or malformed `chat_messages` should record an error and return the conversation with an empty message list only if the conversation identity is valid.

## Fixtures Required
Use synthetic fixtures only. Do not commit real Claude exports.

Create fixtures under:

```text
tests/fixtures/claude/
```

Required fixture scenarios:

- A minimal valid `conversations.json` with one human/user message and one assistant message.
- A fixture reflecting the verified real export structure, sanitized and hand-written.
- A fixture with mixed content blocks, including non-text content skipped gracefully.
- A fixture with malformed conversations/messages that produce errors but still parse valid conversations.
- A fixture with missing optional fields (`name`, message id, `updated_at`) that degrades correctly.
- A zip fixture generated from synthetic JSON, or a test that creates a synthetic zip at runtime under `tmp_path`.

Prefer runtime-created zips in tests to avoid committing binary fixtures.

## Tests Required
Add focused tests, likely in `tests/test_claude_export.py`.

Required scenarios:

- `parse_conversations_json()` parses a minimal synthetic export into one normalized `Conversation`.
- The parsed conversation has provider `"claude"`, a Claude URL, title, UTC timestamps, and ordered messages.
- `chat_messages[]` order is preserved with contiguous `seq`.
- Missing optional fields degrade cleanly.
- Mixed/non-text content does not crash parsing; string/text blocks are preserved and non-text content is reported.
- Malformed records produce error entries and do not abort parsing of valid conversations.
- Errors are JSON-serializable for later `ingest_runs.errors_json`.
- `load_conversations()` works for a direct `conversations.json` path.
- `load_conversations()` works for a directory containing `conversations.json`.
- `load_conversations()` works for a synthetic zip containing `conversations.json`.
- Existing WP-0.1, WP-1.1, and WP-1.2 tests still pass.

## Acceptance Criteria
WP-1.3 is complete only when all of these are true:

- `src/chat_chronicle/adapters/claude_export.py` exists.
- The importer is concrete and does not introduce `adapters/base.py` or `AdapterProtocol`.
- Export shape verification is documented in the completion report.
- Official-export `conversations.json` flat list shape is parsed.
- Conversation `uuid`, `name`, timestamps, and `chat_messages[]` are mapped to normalized models.
- Claude conversation URLs are constructed as `https://claude.ai/chat/{uuid}`.
- Message text bodies are extracted from the verified Claude message shape.
- Non-text or malformed message content is skipped gracefully and recorded in parse errors.
- Timestamps are converted to UTC datetimes.
- The importer returns normalized WP-1.1 `Conversation` and `Message` models.
- Tests use synthetic fixtures only.
- No DB writes or public CLI ingest behavior are added.
- No changes are made to the accepted ChatGPT importer unless a shared test issue makes it unavoidable and is justified.
- `poetry run pytest` passes.
- `poetry run ruff check .` passes.
- `poetry run chronicle --help` still lists all existing commands.

## Evidence Required
The executor must return a detailed completion report. Missing evidence means the WP is not accepted, even if the implementation appears correct.

The completion report must be written to:

```text
md/handoffs/reports/WP-1.3-completion-report.md
```

The report must include:

- Changed-files summary.
- Export shape verification note:
  - whether a real export was inspected;
  - what fields were observed;
  - confirmation that no real export data was committed;
  - if no real export was available, the exact assumptions used.
- Exact command output or concise pasted result for:
  - `poetry env info --path`
  - `poetry run pytest`
  - `poetry run ruff check .`
  - `poetry run chronicle --help`
- Test names covering the required fixture scenarios.
- Confirmation that no real Claude exports, DB files, zip exports, secrets, or local private data were committed.
- Explicit checklist mapping each acceptance criterion to `pass`, `fail`, or `not attempted`.

## Technical Guardrails
- Keep parser logic in `src/chat_chronicle/adapters/claude_export.py`.
- Do not add a base adapter abstraction.
- Do not alter the DB schema for this WP.
- Do not implement CLI ingest or stats behavior.
- Do not add network calls.
- Do not add new runtime dependencies unless unavoidable; prefer stdlib `json`, `zipfile`, `pathlib`, and `datetime`.
- Keep all fixtures synthetic.
- Preserve existing DB/model behavior and all accepted ChatGPT importer tests.

## Completion Report Format
The executor must return the report in this structure:

```markdown
# WP-1.3 Completion Report

## Status
One of:

- ready for PM validation
- blocked

## Summary
Briefly describe what was implemented.

## Export Shape Verification
State whether a real Claude export was inspected. If yes, describe the observed fields and how the sanitized synthetic fixture reflects them. If no, state the assumptions used and why.

## Changed Files
List every changed or created file with a one-line purpose for each.

## Parser API
Describe the functions/classes added in `claude_export.py`.

## Fixture Coverage
List each synthetic fixture/test scenario and the test that covers it.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| Concrete Claude importer module exists | pass/fail/not attempted | File/test reference |
| No adapter base/protocol added | pass/fail/not attempted | File/status evidence |
| Export shape verification documented | pass/fail/not attempted | Report section |
| `conversations.json` flat list shape parsed | pass/fail/not attempted | Test reference |
| `uuid`/`name`/timestamps/`chat_messages` mapped | pass/fail/not attempted | Test reference |
| Claude URLs constructed | pass/fail/not attempted | Test reference |
| Text bodies extracted from Claude message shape | pass/fail/not attempted | Test reference |
| Non-text/malformed content recorded without crash | pass/fail/not attempted | Test reference |
| Timestamps become UTC datetimes | pass/fail/not attempted | Test reference |
| Returns WP-1.1 normalized models | pass/fail/not attempted | Test reference |
| Synthetic fixtures only | pass/fail/not attempted | Git/status evidence |
| No DB writes or public CLI ingest behavior added | pass/fail/not attempted | Scope evidence |
| ChatGPT importer remains accepted | pass/fail/not attempted | Existing tests pass |
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
| Did not add Gemini/Class B importers | pass/fail |  |
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
