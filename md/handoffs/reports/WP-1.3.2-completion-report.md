# WP-1.3.2 Completion Report

## Status
ready for PM validation

## Dependency Check
WP-1.1, WP-1.2, WP-1.3, and WP-1.3.1 are accepted:

- WP-1.1 validation report: `md/handoffs/reports/WP-1.1-validation-review.md`
- WP-1.2 validation report: `md/handoffs/reports/WP-1.2-validation-review.md`
- WP-1.3 validation report: `md/handoffs/reports/WP-1.3-validation-review.md`
- WP-1.3.1 validation report: `md/handoffs/reports/WP-1.3.1-validation-review.md`

## Summary
Implemented a concrete OpenAI Codex local-store extractor for JSONL sessions. It parses a single session file, a sessions directory, or a Codex home directory with `session_index.jsonl`, returning WP-1.1 normalized `Conversation` and `Message` models without DB writes or CLI wiring.

Validation rework completed after `md/handoffs/reports/WP-1.3.2-validation-review.md`: `event_msg` rows with `payload.type == "agent_reasoning"` are now treated as known reasoning metadata and skipped without parse errors.

## Changed Files
- `src/chat_chronicle/adapters/openai_codex.py` - concrete Class B OpenAI Codex JSONL extractor.
- `tests/test_openai_codex.py` - focused parser and loader tests for Codex sessions.
- `tests/fixtures/openai_codex/minimal/rollout-minimal.jsonl` - synthetic minimal session fixture.
- `tests/fixtures/openai_codex/metadata/rollout-metadata.jsonl` - synthetic known metadata/tool/reasoning skip fixture.
- `tests/fixtures/openai_codex/event_fallback/rollout-event-fallback.jsonl` - synthetic event-message fallback fixture.
- `tests/fixtures/openai_codex/duplicates/rollout-duplicates.jsonl` - synthetic duplicate event/response fixture.
- `tests/fixtures/openai_codex/malformed/rollout-malformed.jsonl` - synthetic malformed/unknown record fixture.
- `tests/fixtures/openai_codex/missing_id/rollout-no-session-meta-id.jsonl` - synthetic filename-derived identity fixture.
- `md/handoffs/reports/WP-1.3.2-completion-report.md` - this completion report.

## Parser Behavior
`load_conversations(source)` accepts a `.jsonl` file, a directory of JSONL sessions, or a Codex home directory containing `session_index.jsonl` plus `sessions/`. Directory discovery recurses for `*.jsonl` files and excludes `session_index.jsonl`.

`parse_session_jsonl(raw, source_name=..., index_entries=...)` prefers `session_meta.payload.id` for `provider_conv_id`, otherwise uses the source filename stem and records `missing_session_id`. Titles prefer `session_index.jsonl` `thread_name`, then the first user-visible message prefix, then the filename stem. URLs are always `None`.

The parser extracts only visible `response_item` messages where `payload.type == "message"` and role is `user`, `assistant`, or `developer`, using `input_text` / `output_text` blocks. It also supports `event_msg` fallback for `user_message` and `agent_message`. Duplicate event messages are dropped when a matching response item exists.

Known metadata rows (`turn_context`, response-item reasoning, event-message `agent_reasoning`, function calls, tool outputs, token counts, rate limits, encrypted content, ghost snapshots) are skipped without parse errors. Malformed JSONL lines, unknown top-level rows, unknown response/event types, invalid payloads, and invalid timestamps produce serializable `OpenAICodexExtractError` records while valid messages continue parsing. Message `seq` values are contiguous after skipped rows.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| Concrete OpenAI Codex extractor exists | pass | `src/chat_chronicle/adapters/openai_codex.py` |
| Accepts one `.jsonl` file and sessions/home directory | pass | `test_load_conversations_from_jsonl_file`, `test_load_conversations_from_nested_sessions_directory`, `test_session_index_title_and_updated_at_metadata_is_applied` |
| Returns normalized models | pass | `test_parse_minimal_session_returns_one_conversation` asserts `Conversation` |
| Provider is `openai_codex` and URL is `None` | pass | `test_all_parsed_conversations_use_openai_codex_provider_and_no_url` |
| Visible messages extracted in order with contiguous `seq` | pass | `test_input_text_and_output_text_blocks_become_ordered_message_bodies`, `test_event_message_fallback_handles_user_and_agent_messages` |
| Known metadata/tool/reasoning records skipped without noisy errors | pass | `test_known_metadata_rows_are_skipped_without_errors`, `test_agent_reasoning_event_rows_are_skipped_without_errors` |
| Malformed/unknown records produce serializable errors | pass | `test_invalid_jsonl_line_records_error_and_does_not_abort`, `test_errors_are_json_serializable_for_ingest_runs` |
| Synthetic fixtures cover observed Codex JSONL shape | pass | Six synthetic JSONL fixtures under `tests/fixtures/openai_codex/` cover `session_meta`, `turn_context`, `response_item`, and `event_msg` |
| No private Codex data committed | pass | Fixtures are hand-authored synthetic JSONL only; no real sessions, auth files, DBs, SQLite files, zip exports, secrets, or local private data added |
| No DB/CLI/provider detection/collect/scan/adapter abstraction added | pass | Static search over new source/test found no `chat_chronicle.db`, `sqlite3`, `AdapterProtocol`, `adapters/base`, provider detection, or CLI ingest/stats implementation references |
| `poetry run pytest` passes | pass | `91 passed in 3.03s` |
| `poetry run ruff check .` passes | pass | `All checks passed!` |
| `poetry run chronicle --help` still lists commands | pass | Help output lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, and `open` |

## Command Evidence
```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

```text
poetry run pytest
........................................................................ [ 79%]
...................                                                      [100%]
91 passed in 3.03s
```

```text
poetry run ruff check .
All checks passed!
```

```text
poetry run chronicle --help
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

Parser scenario tests:

```text
test_parse_minimal_session_returns_one_conversation
test_minimal_session_metadata_and_timestamps_are_normalized
test_input_text_and_output_text_blocks_become_ordered_message_bodies
test_known_metadata_rows_are_skipped_without_errors
test_agent_reasoning_event_rows_are_skipped_without_errors
test_event_message_fallback_handles_user_and_agent_messages
test_duplicate_event_and_response_messages_prefer_response_items
test_invalid_jsonl_line_records_error_and_does_not_abort
test_missing_session_id_falls_back_to_filename_identity
test_load_conversations_from_jsonl_file
test_load_conversations_from_nested_sessions_directory
test_session_index_title_and_updated_at_metadata_is_applied
test_load_conversations_reports_missing_or_unsupported_sources
test_load_conversations_reports_directory_without_sessions
test_errors_are_json_serializable_for_ingest_runs
test_all_parsed_conversations_use_openai_codex_provider_and_no_url
```

Synthetic fixture evidence:

```text
tests\fixtures\openai_codex\missing_id\rollout-no-session-meta-id.jsonl
tests\fixtures\openai_codex\minimal\rollout-minimal.jsonl
tests\fixtures\openai_codex\metadata\rollout-metadata.jsonl
tests\fixtures\openai_codex\event_fallback\rollout-event-fallback.jsonl
tests\fixtures\openai_codex\malformed\rollout-malformed.jsonl
tests\fixtures\openai_codex\duplicates\rollout-duplicates.jsonl
```

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement CLI ingest/stats | pass | `cli.py` untouched by this WP |
| Did not add DB writes | pass | New extractor does not import DB code or `sqlite3` |
| Did not add provider detection | pass | WP-1.4 remains responsible for detection |
| Did not add collect/scan-local behavior | pass | `collect.py` and `scan.py` untouched |
| Did not add adapter base/protocol | pass | No `adapters/base.py` or `AdapterProtocol` added |
| Did not commit real Codex/private data or DB files | pass | Only synthetic JSONL fixtures were added |

## WP-1.4 Impact
WP-1.4 should call:

```python
from chat_chronicle.adapters.openai_codex import load_conversations

result = load_conversations(source_path)
```

The expected provider string on every returned conversation is `openai_codex`. Persist parser errors with `[error.model_dump() for error in result.errors]`.

## Risks Or Follow-Ups
- Codex local JSONL is undocumented and version-sensitive; future local format changes should be covered with new synthetic fixtures before parser changes.
- The extractor intentionally skips tool calls, tool outputs, reasoning, encrypted content, and local path metadata rather than storing them as transcript messages.
- WP-1.4 still needs to wire this extractor into `chronicle ingest` and provider auto-detection.
