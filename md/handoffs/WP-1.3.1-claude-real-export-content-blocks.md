# WP-1.3.1 Handoff: Claude Real Export Content Blocks

## Objective
Correct the accepted WP-1.3 Claude importer so it handles the real Claude export shape discovered during manual verification.

The importer currently parses conversations, but it misclassifies known Claude metadata blocks (`thinking`, `tool_use`, `tool_result`) as parse errors. This creates noisy `errors_json` output and would make WP-1.4 ingest reports look broken even when the import is mostly healthy.

This work package must be completed and PM-validated before WP-1.4 CLI ingest + stats starts.

## Dependency Gate
Do not start implementation until WP-1.3 is accepted.

If WP-1.3 is not accepted, return `blocked` and state that the Claude importer dependency is missing.

## Source Of Truth
Use:

- `md/master-plan.md`, especially Core Design Rules and M1 / WP-1.3.
- `md/agent-operating-notes.md`.
- `md/handoffs/WP-1.3-claude-export-importer.md`.
- `md/handoffs/reports/WP-1.3-validation-review.md`.
- `src/chat_chronicle/adapters/claude_export.py`.
- `tests/test_claude_export.py`.
- `tests/fixtures/claude/`.

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

## Real Export Evidence To Preserve
Manual verification against a private Claude export produced:

```text
conversations 13
errors 415
errors_by_type Counter({'non_text_content_block': 415})
messages in export 156
messages parsed 145
roles Counter({'human': 78, 'assistant': 78})
content_block_types Counter({'text': 206, 'tool_use': 155, 'tool_result': 155, 'thinking': 105})
```

Sample known metadata block keys:

- `thinking`: `type`, `thinking`, `summaries`, `hidden`, `signature`, timing/flag fields.
- `tool_use`: `type`, `id`, `name`, `input`, display/integration fields.
- `tool_result`: `type`, `tool_use_id`, `content`, `structured_content`, display/integration fields.
- `text`: `type`, `text`, citation/timing/flag fields.

Do not commit the real export, copied records from it, private IDs, private titles, or private message content. Convert the shape above into minimal synthetic fixtures only.

## Scope
Implement:

- Update Claude content parsing so known non-text Claude metadata blocks are skipped without creating parse errors.
- Preserve extraction of text from `content[]` blocks where `type == "text"` and `text` is a non-empty string.
- Preserve fallback to flat message `text` where appropriate.
- Keep malformed or unsupported content blocks visible as parse errors.
- Add synthetic fixture coverage for the real export block shape.
- Update completion report for this corrective WP.

Do not implement:

- CLI ingest or stats behavior.
- DB writes.
- Provider detection.
- Adapter base/protocol abstraction.
- Role normalization from `human` to `user`.
- Tool call persistence, thinking persistence, or structured Claude tool-result storage.
- Any real/private export fixture.

## Parser Rules
Known Claude content block handling must be:

- `text` with non-empty string `text`: append to message body.
- `thinking`: skip silently as known metadata.
- `tool_use`: skip silently as known metadata.
- `tool_result`: skip silently as known metadata.
- Known metadata blocks must not create `non_text_content_block` errors.
- Unknown block type with no extractable text should still produce a parse error.
- Invalid block shapes, such as non-dict entries or invalid `content`, should still produce parse errors.
- A message with only known metadata and no text body may still be skipped as a non-searchable message, but this skip should not be counted as a parse error unless the message shape is malformed.

The goal is to keep `errors_json` useful: errors should mean malformed/unexpected input, not expected Claude metadata.

## Tests Required
Add focused tests in `tests/test_claude_export.py` and synthetic fixtures under `tests/fixtures/claude/` if useful.

Required scenarios:

- A Claude message with `text` plus `thinking` parses the text and records zero errors.
- A Claude message with `text` plus `tool_use` and `tool_result` parses the text and records zero errors.
- A Claude message with only known metadata blocks is skipped without parse errors.
- An unknown block type without text still records a parse error.
- An invalid content block shape still records a parse error.
- Existing WP-1.2 ChatGPT importer tests still pass.
- Existing WP-1.3 Claude importer tests still pass, updated only where the old noisy-error expectation is now intentionally wrong.

## Acceptance Criteria
WP-1.3.1 is complete only when all of these are true:

- Known Claude metadata block types `thinking`, `tool_use`, and `tool_result` are skipped without parse errors.
- Text body extraction from Claude `content[]` blocks is preserved.
- Flat `text` fallback remains supported.
- Malformed/unknown non-text content still produces serializable `ClaudeImportError` records.
- Messages containing only known metadata can be skipped without polluting `errors_json`.
- Synthetic tests cover the real export block shape.
- No real/private export data is committed.
- No DB writes, CLI ingest behavior, provider detection, or adapter abstraction is introduced.
- `poetry run pytest` passes.
- `poetry run ruff check .` passes.
- `poetry run chronicle --help` still lists all existing commands.

## Evidence Required
The executor must return a detailed completion report. Missing evidence means the WP is not accepted, even if the implementation appears correct.

The completion report must be written to:

```text
md/handoffs/reports/WP-1.3.1-completion-report.md
```

The report must include:

- Changed-files summary.
- Exact command output or concise pasted result for:
  - `poetry env info --path`
  - `poetry run pytest`
  - `poetry run ruff check .`
  - `poetry run chronicle --help`
- Test names covering each required parser scenario.
- Confirmation that no real exports, DB files, zip exports, secrets, or local private data were committed.
- Explicit checklist mapping each acceptance criterion to `pass`, `fail`, or `not attempted`.
- Short note explaining how this changes the expected WP-1.4 `errors_json` behavior.

## Technical Guardrails

- Keep `claude_export.py` concrete.
- Do not add `adapters/base.py`, `AdapterProtocol`, or a framework.
- Do not normalize roles yet; preserve Claude provider-native `human` and `assistant`.
- Do not store Claude thinking/tool blocks in the normalized model in this WP.
- Keep the fix narrowly scoped to content block parsing and tests.
- Use synthetic fixtures only.

## Completion Report Format
The executor must return the report in this structure:

```markdown
# WP-1.3.1 Completion Report

## Status
One of:

- ready for PM validation
- blocked

## Dependency Check
Confirm WP-1.3 is accepted, with validation report path.

## Summary
Briefly describe what was changed.

## Changed Files
List every changed or created file with a one-line purpose for each.

## Parser Behavior
Describe how `text`, `thinking`, `tool_use`, `tool_result`, unknown blocks, invalid blocks, and metadata-only messages are handled.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| Known metadata blocks skipped without parse errors | pass/fail/not attempted | Test evidence |
| Text extraction from `content[]` preserved | pass/fail/not attempted | Test evidence |
| Flat `text` fallback remains supported | pass/fail/not attempted | Test evidence |
| Malformed/unknown non-text content still records errors | pass/fail/not attempted | Test evidence |
| Metadata-only messages skipped without noisy errors | pass/fail/not attempted | Test evidence |
| Synthetic tests cover real export block shape | pass/fail/not attempted | File/test evidence |
| No private export data committed | pass/fail/not attempted | Git/status evidence |
| No DB/CLI/provider detection/adapter abstraction added | pass/fail/not attempted | Scope evidence |
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
| Did not add adapter base/protocol | pass/fail |  |
| Did not normalize Claude roles | pass/fail |  |
| Did not commit real exports/private data or DB files | pass/fail |  |

## WP-1.4 Impact
Explain how the fix reduces noisy `errors_json` entries for real Claude exports while preserving true parse errors.

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
