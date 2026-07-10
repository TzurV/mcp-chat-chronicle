# WP-1.2 Completion Report

## Status

ready for PM validation

## Summary

Implemented the concrete ChatGPT official-export importer at
`src/chat_chronicle/adapters/chatgpt_export.py`. It parses `conversations.json` from an official
ChatGPT export, linearizes the tree-shaped `mapping` (following `current_node` when valid, else
falling back to the deepest message-bearing chain), extracts text bodies from `content.parts`,
converts Unix timestamps to UTC datetimes, constructs `https://chatgpt.com/c/{id}` URLs, and returns
normalized WP-1.1 `Conversation` / `Message` models.

Parse problems are treated as data, not exceptions. Malformed conversations and nodes are recorded
as serializable `ChatGPTImportError` entries in `ChatGPTImportResult.errors`, and the remaining
records still parse. The result is JSON-serializable so WP-1.4 can store it in
`ingest_runs.errors_json`.

`load_conversations()` accepts a `.zip` export, a directory containing `conversations.json`, or a
direct path to `conversations.json`.

No DB writes, no CLI ingest behavior, no adapter base class, and no new runtime dependencies were
added. The module imports only stdlib (`json`, `zipfile`, `pathlib`, `datetime`), `pydantic`, and
`chat_chronicle.models`.

## Changed Files

| File | Purpose |
| --- | --- |
| `src/chat_chronicle/adapters/chatgpt_export.py` | New. Concrete ChatGPT export parser: `load_conversations`, `parse_conversations_json`, `ChatGPTImportResult`, `ChatGPTImportError`. |
| `tests/test_chatgpt_export.py` | New. 20 focused parser tests covering all required scenarios. |
| `tests/fixtures/chatgpt/minimal/conversations.json` | New. Minimal valid export: one user + one assistant message. |
| `tests/fixtures/chatgpt/branched/conversations.json` | New. Regenerated/edited branch; `current_node` selects the kept branch. |
| `tests/fixtures/chatgpt/deepest_chain/conversations.json` | New. Invalid `current_node`; deepest message-bearing chain must be selected. |
| `tests/fixtures/chatgpt/non_text_parts/conversations.json` | New. Mixed/non-text `content.parts`, image-only message, and a `content_type` with no `parts`. |
| `tests/fixtures/chatgpt/malformed/conversations.json` | New. Malformed records + one healthy conversation that must still parse. |
| `md/handoffs/reports/WP-1.2-completion-report.md` | New. This report. |

No existing files were modified.

## Parser API

Public surface in `chat_chronicle.adapters.chatgpt_export`:

- `PROVIDER = "chatgpt"` — provider constant.
- `class ChatGPTImportError(BaseModel)` — `record_id`, `node_id`, `error`, `detail`. One non-fatal
  parse problem; serializable for `ingest_runs.errors_json`.
- `class ChatGPTImportResult(BaseModel)` — `conversations: list[Conversation]`,
  `errors: list[ChatGPTImportError]`.
- `load_conversations(source: Path | str) -> ChatGPTImportResult` — resolves a zip / directory /
  `conversations.json` path, then delegates to `parse_conversations_json`. Missing sources, zips
  without `conversations.json`, and invalid JSON are reported as errors rather than raised.
- `parse_conversations_json(data: object) -> ChatGPTImportResult` — parses the decoded list payload.

Internal helpers (not part of the contract): `_linearize`, `_chain_to_root`, `_deepest_chain`,
`_build_messages`, `_extract_body`, `_extract_role`, `_to_utc`, `_find_conversations_member`.

Error codes emitted: `source_not_found`, `conversations_json_not_found`, `invalid_json`,
`unexpected_export_shape`, `invalid_conversation_record`, `missing_conversation_id`,
`missing_mapping`, `invalid_title`, `missing_current_node`, `invalid_current_node`,
`broken_parent_chain`, `invalid_parent`, `cyclic_parent_chain`, `parent_chain_too_deep`,
`no_message_bearing_chain`, `invalid_content`, `unsupported_content_type`, `non_text_content_part`,
`invalid_author`, `invalid_role`, `invalid_timestamp`.

### Behavior notes

- Tree linearization prefers `current_node` when it is a string present in `mapping`; it follows
  `parent` pointers to the root and reverses. Cyclic and over-deep chains are truncated and reported.
- When `current_node` is missing or not a key in `mapping`, the deepest message-bearing root-to-leaf
  chain is selected (ties broken by total chain length). Fallback branch exploration uses a
  throwaway error sink so discarded branches do not pollute the reported errors.
- Mapping nodes with no `message` (the synthetic root) are skipped silently — structural, not an error.
- `provider_message_id` uses `message.id` when it is a non-empty string, else the mapping node id.
- Bodies join string parts with `"\n\n"` and are `.strip()`ed. Messages with no text body are skipped.
- Timestamps: `bool` is explicitly rejected (it is an `int` subclass); non-numeric and out-of-range
  values degrade to `None` and emit `invalid_timestamp`.

## Fixture Coverage

| Required fixture scenario | Fixture | Covering test(s) |
| --- | --- | --- |
| Minimal valid export, one user + one assistant message | `minimal/conversations.json` | `test_parse_minimal_export_returns_one_conversation`, `test_minimal_conversation_metadata_is_normalized`, `test_minimal_messages_are_ordered_and_mapped` |
| Regenerated/edited branch, `current_node` selects correct branch | `branched/conversations.json` | `test_current_node_selects_regenerated_branch` |
| Missing/invalid `current_node`, deepest valid chain selected | `deepest_chain/conversations.json` | `test_invalid_current_node_falls_back_to_deepest_chain`, `test_missing_current_node_falls_back_to_deepest_chain` |
| Non-text content parts skipped gracefully | `non_text_parts/conversations.json` | `test_non_text_parts_are_skipped_and_reported` |
| Malformed nodes produce errors but other conversations still parse | `malformed/conversations.json` | `test_malformed_records_do_not_abort_parsing`, `test_malformed_record_timestamps_degrade_to_none`, `test_healthy_message_without_id_falls_back_to_node_id` |
| Synthetic zip | created at runtime under `tmp_path` | `test_load_conversations_from_zip`, `test_load_conversations_from_nested_zip` |

Zips are created at runtime under `tmp_path` as the handoff prefers; no binary fixture is committed.

### Full test list (20 tests, `tests/test_chatgpt_export.py`)

```text
test_parse_minimal_export_returns_one_conversation
test_minimal_conversation_metadata_is_normalized
test_minimal_messages_are_ordered_and_mapped
test_current_node_selects_regenerated_branch
test_invalid_current_node_falls_back_to_deepest_chain
test_missing_current_node_falls_back_to_deepest_chain
test_non_text_parts_are_skipped_and_reported
test_malformed_records_do_not_abort_parsing
test_malformed_record_timestamps_degrade_to_none
test_healthy_message_without_id_falls_back_to_node_id
test_non_list_payload_is_reported_not_raised
test_errors_are_json_serializable_for_ingest_runs
test_load_conversations_from_json_file
test_load_conversations_from_directory
test_load_conversations_from_zip
test_load_conversations_from_nested_zip
test_load_conversations_missing_sources_report_errors[<lambda>-source_not_found]
test_load_conversations_missing_sources_report_errors[<lambda>-conversations_json_not_found]
test_load_conversations_zip_without_conversations_json
test_load_conversations_invalid_json_is_reported
```

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| Concrete ChatGPT importer module exists | pass | `src/chat_chronicle/adapters/chatgpt_export.py` |
| No adapter base/protocol added | pass | `ls src/chat_chronicle/adapters/` → `__init__.py`, `chatgpt_export.py` only; grep for `AdapterProtocol`/`adapters/base` returns nothing |
| `conversations.json` list shape parsed | pass | `test_parse_minimal_export_returns_one_conversation`; non-list rejected by `test_non_list_payload_is_reported_not_raised` |
| `current_node` branch selected | pass | `test_current_node_selects_regenerated_branch` |
| Deepest-chain fallback works | pass | `test_invalid_current_node_falls_back_to_deepest_chain`, `test_missing_current_node_falls_back_to_deepest_chain` |
| Text bodies extracted from `content.parts` | pass | `test_minimal_messages_are_ordered_and_mapped` (asserts `"\n\n"` join) |
| Non-text/malformed content recorded without crash | pass | `test_non_text_parts_are_skipped_and_reported`, `test_malformed_records_do_not_abort_parsing` |
| Unix timestamps become UTC datetimes | pass | `test_minimal_conversation_metadata_is_normalized`; degradation in `test_malformed_record_timestamps_degrade_to_none` |
| ChatGPT URLs constructed | pass | `test_minimal_conversation_metadata_is_normalized` asserts `https://chatgpt.com/c/conv-minimal-1` |
| Returns WP-1.1 normalized models | pass | `test_parse_minimal_export_returns_one_conversation` asserts `isinstance(conversation, Conversation)` |
| Synthetic fixtures only | pass | 5 hand-written JSON fixtures under `tests/fixtures/chatgpt/`; `git ls-files` shows no `.db`/`.zip`/`.sqlite` tracked |
| No DB writes or public CLI ingest behavior added | pass | Importer imports only `json`, `zipfile`, `datetime`, `pathlib`, `typing`, `pydantic`, `chat_chronicle.models`; no `db` or `cli` import; no existing file modified |
| `poetry run pytest` passes | pass | `35 passed in 1.43s` |
| `poetry run ruff check .` passes | pass | `All checks passed!` |
| `poetry run chronicle --help` still lists commands | pass | All 7 commands listed (see below) |

## Command Evidence

> **Poetry preflight note.** A bare `poetry env info --path` initially resolved to
> `C:\work\Github\Asensus\SurgeryCopilot\GitLabRepo\CopilotLocalMongoDB\.venv` — exactly the
> `VIRTUAL_ENV` leak documented in `md/agent-operating-notes.md`. Every Poetry command below was run
> with `VIRTUAL_ENV` cleared for the command's environment, which resolves the repo-local venv. No
> install or command was run against the other project's virtualenv.

### `poetry env info --path`

```text
# bare invocation (leaked VIRTUAL_ENV — NOT used for any command)
C:\work\Github\Asensus\SurgeryCopilot\GitLabRepo\CopilotLocalMongoDB\.venv

# with VIRTUAL_ENV cleared — this is the environment all commands below used
$ VIRTUAL_ENV= poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

### `poetry run pytest`

```text
...................................                                      [100%]
35 passed in 1.43s
```

(20 new ChatGPT importer tests + 15 pre-existing WP-0.1 / WP-1.1 tests, all passing.)

### `poetry run ruff check .`

```text
All checks passed!
```

### `poetry run chronicle --help`

```text
 Usage: chronicle [OPTIONS] COMMAND [ARGS]...

 A local-first, searchable archive of your AI conversations.

+- Options -------------------------------------------------------------------+
| --version          Show the version and exit.                               |
| --help             Show this message and exit.                              |
+-----------------------------------------------------------------------------+
+- Commands ------------------------------------------------------------------+
| ingest         Ingest a single official export file.                        |
| ingest-folder  Sweep a drop folder for export archives and ingest each one. |
| collect        Run every enabled source through its adapter.                |
| scan-local     Report, read-only, which AI-tool data stores exist on this   |
|                machine.                                                     |
| stats          Show per-source counts and the most recent ingest runs.      |
| search         Search the archive with FTS5 ranking and snippets.           |
| open           Open a result: deep link for web chats, transcript view      |
|                otherwise.                                                   |
+-----------------------------------------------------------------------------+
```

### Committed-data verification

```text
$ git status --short
?? .claude/
?? src/chat_chronicle/adapters/chatgpt_export.py
?? tests/fixtures/
?? tests/test_chatgpt_export.py

$ git ls-files | grep -Ei '\.(db|zip|sqlite3?)$'
no db/zip tracked
```

All five fixture files are hand-authored synthetic JSON. No real ChatGPT export, DB file, zip export,
secret, or local private data was created or committed.

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement DB writes | pass | `chatgpt_export.py` does not import `chat_chronicle.db`; no `sqlite3` usage. |
| Did not implement public CLI ingest behavior | pass | `cli.py` untouched; `chronicle ingest` remains the WP-0.1 stub. |
| Did not add adapter base/protocol | pass | No `adapters/base.py`; no `AdapterProtocol`. `adapters/__init__.py` unchanged. |
| Did not add Claude/Gemini/Class B importers | pass | Only `chatgpt_export.py` added under `adapters/`. |
| Did not commit real exports/private data | pass | 5 synthetic JSON fixtures; no `.db`/`.zip` tracked. |
| Did not alter the DB schema | pass | `db.py` and `models.py` untouched. |
| Did not add network calls | pass | No `requests`/`httpx`/`urllib` import. |
| Did not add runtime dependencies | pass | stdlib `json`/`zipfile`/`pathlib`/`datetime` + existing `pydantic`. |

## Risks Or Follow-Ups

1. **`conversation_id` vs `id`.** Real exports carry both `conversation_id` and `id`, usually equal.
   The parser prefers `conversation_id` and falls back to `id`. The handoff only specified `id`;
   this preference is a superset and is safe, but WP-1.4 should confirm against a real export that
   the two never disagree in a way that would split a conversation across ingests.

2. **Deepest-chain tie-breaking.** The fallback scores branches by message-bearing node count, with
   total chain length as tiebreaker. When two branches tie on both, dict iteration order of `mapping`
   decides. This is deterministic for a given JSON file but is not a semantically meaningful choice.
   A real export always has a valid `current_node`, so this path should be rare.

3. **Empty-body messages are dropped entirely.** A message whose parts are all non-text (e.g. an
   image-only assistant turn) produces no `Message` row, only a `non_text_content_part` error. If
   later work wants to preserve image turns as placeholders, this is the place to change.

4. **`seq` is assigned post-filter.** Sequence numbers are `0..n-1` over *retained* messages, so they
   stay contiguous when a message is skipped. They therefore do not index into the original mapping
   chain. This matches WP-1.1's `content_hash` expectations.

5. **Poetry `VIRTUAL_ENV` leak persists on this machine.** The hazard in
   `md/agent-operating-notes.md` reproduced during this WP. Future executors should keep clearing
   `VIRTUAL_ENV` (or use a fresh terminal) before any Poetry command. Worth considering a
   `poetry.toml` with `virtualenvs.in-project = true` plus a preflight assertion in CI.

6. **Not wired into ingest.** Per scope, the importer is unreachable from the CLI. WP-1.4 must call
   `load_conversations()`, feed `result.conversations` to `upsert_conversation()`, and persist
   `[e.model_dump() for e in result.errors]` into `ingest_runs.errors_json`.
