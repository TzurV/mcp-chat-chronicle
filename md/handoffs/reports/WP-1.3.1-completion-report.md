# WP-1.3.1 Completion Report

## Status
ready for PM validation

## Dependency Check
WP-1.3 is accepted. Validation report: `md/handoffs/reports/WP-1.3-validation-review.md` (Decision: **Accepted.**). The dependency gate is satisfied, so implementation proceeded.

## Summary
Corrected the Claude official-export content parser so that known non-text Claude
metadata blocks (`thinking`, `tool_use`, `tool_result`) are skipped silently instead of
being recorded as `non_text_content_block` parse errors. Text extraction from
`content[]` blocks and the flat `text` fallback are unchanged. Unknown block types
without extractable text, and structurally invalid blocks, still produce serializable
`ClaudeImportError` records. Added a synthetic fixture reproducing the real export block
shape and six focused tests. No roles were normalized, no thinking/tool blocks are
persisted, and no CLI/DB/provider-detection/adapter-abstraction code was added.

## Changed Files
- `src/chat_chronicle/adapters/claude_export.py` — Added `_KNOWN_METADATA_BLOCK_TYPES`
  and a skip branch in `_text_from_content()` so known metadata blocks do not create
  parse errors; unknown/invalid blocks are unchanged.
- `tests/test_claude_export.py` — Added a "real export content blocks (WP-1.3.1)"
  section with per-message error-scoping helper and six tests covering the required
  scenarios.
- `tests/fixtures/claude/real_blocks/conversations.json` — New synthetic fixture whose
  block shapes mirror the real export (text+thinking; text+tool_use+tool_result;
  metadata-only; unknown `image` block; invalid non-dict block). Fully synthetic.

## Parser Behavior
- `text` block with a non-empty string `text`: appended to the message body (multiple
  text blocks joined with a blank line).
- `thinking`: skipped silently as known metadata; no error.
- `tool_use`: skipped silently as known metadata; no error.
- `tool_result`: skipped silently as known metadata; no error.
- Unknown block type (e.g. `image`) with no extractable `text`: still recorded as a
  `non_text_content_block` error; the block contributes no body.
- Invalid block shape (non-dict entry such as an int): still recorded as an
  `invalid_content_block` error.
- Metadata-only message (only known metadata, no text): produces an empty body, so the
  message is skipped as non-searchable, and this skip produces **no** parse error (not
  `non_text_content_block`, not `missing_message_content`). Sequence numbers on the
  surviving messages remain contiguous.
- Flat `text` fallback and plain-string `content` are unchanged from WP-1.3.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| Known metadata blocks skipped without parse errors | pass | `test_text_plus_thinking_extracts_text_without_errors`, `test_text_plus_tool_use_and_tool_result_extracts_text_without_errors` (per-message error set empty) |
| Text extraction from `content[]` preserved | pass | Same two tests assert exact joined bodies; existing `test_minimal_messages_are_ordered_and_mapped` still passes |
| Flat `text` fallback remains supported | pass | Existing `test_missing_optional_fields_degrade_cleanly` and `missing_optional` fixture still pass unchanged |
| Malformed/unknown non-text content still records errors | pass | `test_unknown_block_type_without_text_still_reports_error`, `test_invalid_content_block_shape_still_reports_error` |
| Metadata-only messages skipped without noisy errors | pass | `test_metadata_only_message_is_skipped_without_parse_errors` |
| Synthetic tests cover real export block shape | pass | `tests/fixtures/claude/real_blocks/conversations.json` + `test_real_blocks_only_reports_true_parse_errors` |
| No private export data committed | pass | `git status` shows only source, tests, and synthetic fixture changed; no zip/DB/private files |
| No DB/CLI/provider detection/adapter abstraction added | pass | Change limited to `_text_from_content()` and tests; `cli.py`, DB, no `adapters/base.py` touched |
| `poetry run pytest` passes | pass | `70 passed in 1.27s` |
| `poetry run ruff check .` passes | pass | `All checks passed!` |
| `poetry run chronicle --help` still lists commands | pass | Lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, `open` |

## Command Evidence

```text
$ poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

Note: the machine had an inherited `VIRTUAL_ENV` pointing at another project's venv.
Per the handoff preflight, `VIRTUAL_ENV`/`POETRY_ACTIVE` were cleared before every
Poetry command, after which `poetry env info --path` reports the in-repo `.venv` above.

```text
$ poetry run pytest
......................................................................   [100%]
70 passed in 1.27s
```

```text
$ poetry run ruff check .
All checks passed!
```

```text
$ poetry run chronicle --help
Usage: chronicle [OPTIONS] COMMAND [ARGS]...

  A local-first, searchable archive of your AI conversations.

Commands:
  ingest         Ingest a single official export file.
  ingest-folder  Sweep a drop folder for export archives and ingest each one.
  collect        Run every enabled source through its adapter.
  scan-local     Report, read-only, which AI-tool data stores exist on this machine.
  stats          Show per-source counts and the most recent ingest runs.
  search         Search the archive with FTS5 ranking and snippets.
  open           Open a result: deep link for web chats, transcript view otherwise.
```

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement CLI ingest/stats | pass | `cli.py` untouched; change is only in the content-block parser. |
| Did not add DB writes | pass | No `sqlite3`/`chat_chronicle.db` usage introduced. |
| Did not add provider detection | pass | No detection logic added. |
| Did not add adapter base/protocol | pass | No `adapters/base.py` or `AdapterProtocol`; importer stays concrete. |
| Did not normalize Claude roles | pass | `human`/`assistant` preserved; role handling untouched. |
| Did not commit real exports/private data or DB files | pass | Only a synthetic fixture added; `git status` shows no export/DB artifacts. |

## WP-1.4 Impact
Real Claude exports carry large volumes of `thinking`, `tool_use`, and `tool_result`
blocks (the private-export evidence recorded 105 `thinking`, 155 `tool_use`, and 155
`tool_result` blocks against 415 total `non_text_content_block` errors). Before this fix,
every such block became a `non_text_content_block` error, so a healthy import produced
hundreds of noisy entries in `ingest_runs.errors_json` and would make WP-1.4 ingest/stats
reports look broken. After this fix those known metadata blocks are skipped silently, so
`errors_json` will retain only true parse problems — malformed records, unknown non-text
block types, and invalid block shapes. WP-1.4 should still persist
`[error.model_dump() for error in result.errors]` into `ingest_runs.errors_json`; the
list is now meaningfully smaller and each entry represents a genuine anomaly.

## Risks Or Follow-Ups
- The known-metadata set is `{thinking, tool_use, tool_result}`. If a future/real export
  introduces additional benign non-text block types (e.g. attachments, citations as
  standalone blocks), they will surface as `non_text_content_block` errors until added
  to `_KNOWN_METADATA_BLOCK_TYPES`. This is intentional fail-visible behavior.
- The fix was validated against synthetic fixtures only, matching the documented real
  export shape; no real/private export is committed. Comparing against a real export
  (per the WP-1.3 PM follow-up) remains a recommended pre-M2 check.
- This WP deliberately does not persist thinking/tool content into the normalized model;
  if that content is later wanted (e.g. for tool-call display), it is a separate WP.
