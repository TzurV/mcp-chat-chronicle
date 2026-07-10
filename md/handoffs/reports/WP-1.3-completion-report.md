# WP-1.3 Completion Report

## Status

ready for PM validation

## Summary

Implemented the concrete Claude official-export importer at
`src/chat_chronicle/adapters/claude_export.py`. It parses the flat
`conversations.json` array shape (`uuid`, `name`, `created_at`,
`chat_messages[]`) and converts each record into the WP-1.1 normalized
`Conversation` and `Message` models.

The module mirrors the accepted WP-1.2 importer's public shape
(`load_conversations()` / `parse_conversations_json()` returning a result object
carrying conversations plus per-record errors), but shares no code with it: the
Claude export is a flat array of messages rather than ChatGPT's tree-shaped
`mapping`, so the two parsers have no common traversal logic. Per master-plan
design rule 2, no adapter base class or protocol was introduced.

Parse problems are treated as data, never exceptions. A malformed conversation
or message is recorded in `ClaudeImportResult.errors` and the remaining records
still parse. Errors are Pydantic models that serialize cleanly for WP-1.4 to
store in `ingest_runs.errors_json`.

Scope was held to parser/importer work: no DB writes, no `chronicle ingest`
wiring, no changes to the ChatGPT importer, and no new runtime dependencies
(stdlib `json`, `zipfile`, `pathlib`, `datetime` only).

## Export Shape Verification

**No real Claude export was inspected.** No official Claude export archive was
available anywhere on this machine at implementation time. I checked the user's
`~/Downloads` directory (the conventional landing spot for a requested export)
and the repository tree; neither contained a Claude export archive or a
`conversations.json` of Claude origin.

Because the handoff explicitly permits this path, the parser was implemented
against the master-plan shape and the assumptions are recorded here. **Every
fixture under `tests/fixtures/claude/` is hand-written and synthetic. No real
Claude export data was inspected, sanitized, or committed.**

### Assumptions used

Taken from `md/master-plan.md` §6 WP-1.3 ("Claude's export `conversations.json`
is a flat array (`uuid`, `name`, `created_at`, `chat_messages[]`)") and the
publicly documented structure of Anthropic's account data export:

| Level | Field | Assumption |
| --- | --- | --- |
| Top level | — | A flat JSON array of conversation objects. |
| Conversation | `uuid` | String conversation id. Required; a record without one is skipped with an error. |
| Conversation | `name` | Optional string title. An empty string is treated as absent. |
| Conversation | `created_at` | ISO8601 string, UTC (`Z` suffix), microsecond precision. |
| Conversation | `updated_at` | Optional ISO8601 string. |
| Conversation | `chat_messages` | Array of message objects, already in display order. |
| Message | `uuid` | String message id (falls back to `id`, then `None`). |
| Message | `sender` | `"human"` or `"assistant"` (falls back to `role`). |
| Message | `created_at` | ISO8601 string. |
| Message | `text` | Flat convenience string carrying the message text. |
| Message | `content` | List of typed blocks, e.g. `{"type": "text", "text": "..."}`; non-text block types such as `image` / `tool_use` also occur. |

Defensive choices made where the shape was uncertain:

- **Role key.** The handoff says "`sender` or `role`, whichever exists in the
  verified export shape." Since the shape was not verified, the parser accepts
  `sender` first and falls back to `role`. The role string is passed through
  verbatim (`"human"`, not remapped to `"user"`), because the normalized
  `Message.role` field is a free-form `str | None` and no cross-provider role
  vocabulary has been specified yet. **This is a decision worth PM review** —
  see Risks.
- **Body extraction.** The parser prefers the structured `content[]` blocks and
  falls back to the flat `text` field only when `content` yields no text. Real
  exports carry both and they agree; the assistant message in the `minimal`
  fixture has `"text": ""` alongside populated `content` blocks specifically to
  prove `content` wins and the empty `text` does not blank the body.
- **Timestamps.** Implemented as ISO8601 strings only. The handoff says "Support
  Unix timestamps only if the verified export shape contains them" — the shape
  was not verified to contain them, so numeric timestamps are rejected with an
  `invalid_timestamp` error rather than silently guessing an epoch unit. (This
  is the deliberate opposite of the ChatGPT importer, whose export uses Unix
  seconds.)
- **`updated_at` fallback chain.** Conversation `updated_at`, else the latest
  parsed message `created_at`, else conversation `created_at`, else `None`.
- **String `content`.** Accepted as a plain body, in case a variant emits
  `content` as a bare string rather than a block list.

If a real export later contradicts any row above, only
`src/chat_chronicle/adapters/claude_export.py` and the fixtures need to change;
no other module depends on these assumptions.

## Changed Files

| File | Status | Purpose |
| --- | --- | --- |
| `src/chat_chronicle/adapters/claude_export.py` | created | The concrete Claude official-export importer: `load_conversations()`, `parse_conversations_json()`, `ClaudeImportResult`, `ClaudeImportError`. |
| `tests/test_claude_export.py` | created | 24 focused parser tests covering every required scenario. |
| `tests/fixtures/claude/minimal/conversations.json` | created | One human + one assistant message; the happy path. |
| `tests/fixtures/claude/realistic/conversations.json` | created | Two conversations carrying the full assumed export field set (`account`, `attachments`, `files`, block `start_timestamp`/`stop_timestamp`/`citations`). |
| `tests/fixtures/claude/mixed_content/conversations.json` | created | Text + `image` + `tool_use` blocks, plus a bare-string `content`. |
| `tests/fixtures/claude/malformed/conversations.json` | created | Non-object record, missing `uuid`, non-list `chat_messages`, non-string `name`, unparseable timestamp, offset-aware timestamp, non-object message, unusable `content`, non-string `sender`. |
| `tests/fixtures/claude/missing_optional/conversations.json` | created | Absent `name`, message `uuid`, and `updated_at`; plus a conversation with no message timestamps at all. |
| `md/handoffs/reports/WP-1.3-completion-report.md` | created | This report. |

No existing file was modified. `md/development-ledger.md` and
`md/handoffs/WP-1.4-cli-ingest-stats.md` appear in `git status` but were already
dirty/untracked before this work package began; they are PM artifacts and were
not touched.

## Parser API

```python
PROVIDER = "claude"
CONVERSATIONS_FILENAME = "conversations.json"

class ClaudeImportError(BaseModel):
    record_id: str | None = None    # conversation uuid, or array index when absent
    message_id: str | None = None   # message uuid, or array position when absent
    error: str                      # stable machine-readable code
    detail: str | None = None       # human-readable context

class ClaudeImportResult(BaseModel):
    conversations: list[Conversation]
    errors: list[ClaudeImportError]

def load_conversations(source: Path | str) -> ClaudeImportResult: ...
def parse_conversations_json(data: object) -> ClaudeImportResult: ...
```

`load_conversations()` accepts a `.zip` export (selecting the shallowest
`conversations.json` member), a directory containing `conversations.json`, or a
direct path to `conversations.json`. A missing source, a missing
`conversations.json`, and invalid JSON are all returned as errors rather than
raised.

Mapping performed by `parse_conversations_json()`:

- `provider` → `"claude"`.
- `provider_conv_id` → conversation `uuid`.
- `title` → `name` (empty string normalized to `None`).
- `url` → `https://claude.ai/chat/{uuid}`.
- `created_at` → conversation `created_at`, as an aware UTC `datetime`.
- `updated_at` → `updated_at`, else newest message timestamp, else `created_at`.
- `messages` → `chat_messages[]` in array order, with contiguous `seq` from `0`.
- Message text comes from `content[]` text blocks joined by `"\n\n"`, falling
  back to the flat `text` field. Messages with no text body are skipped.

Error codes emitted: `source_not_found`, `conversations_json_not_found`,
`invalid_json`, `unexpected_export_shape`, `invalid_conversation_record`,
`missing_conversation_uuid`, `invalid_title`, `invalid_timestamp`,
`missing_chat_messages`, `invalid_chat_messages`, `invalid_message_record`,
`invalid_message_content`, `invalid_content_block`, `non_text_content_block`,
`invalid_message_text`, `missing_message_content`, `invalid_role`.

## Fixture Coverage

| Required scenario | Fixture | Covering test(s) |
| --- | --- | --- |
| Minimal valid export, one human + one assistant message | `minimal/` | `test_parse_minimal_export_returns_one_conversation`, `test_minimal_conversation_metadata_is_normalized`, `test_minimal_messages_are_ordered_and_mapped` |
| Verified real export structure, sanitized and hand-written | `realistic/` | `test_realistic_export_parses_flat_conversation_list`, `test_realistic_export_preserves_chat_message_order_with_contiguous_seq`, `test_realistic_export_normalizes_timestamps_to_utc` |
| Mixed content blocks, non-text skipped gracefully | `mixed_content/` | `test_mixed_content_preserves_text_and_reports_non_text_blocks`, `test_message_with_only_non_text_content_is_skipped_and_seq_stays_contiguous`, `test_plain_string_content_is_supported` |
| Malformed records produce errors but valid conversations still parse | `malformed/` | `test_malformed_records_do_not_abort_parsing_of_valid_conversations`, `test_malformed_records_report_expected_error_codes`, `test_conversation_with_invalid_chat_messages_keeps_identity_and_empty_messages`, `test_invalid_role_is_reported_and_message_body_survives`, `test_offset_aware_timestamps_are_converted_to_utc` |
| Missing optional fields (`name`, message id, `updated_at`) degrade correctly | `missing_optional/` | `test_missing_optional_fields_degrade_cleanly`, `test_updated_at_falls_back_to_created_at_when_no_message_timestamps` |
| Zip export, created at runtime under `tmp_path` (no binary fixture committed) | — | `test_load_conversations_from_zip`, `test_load_conversations_reports_zip_without_conversations_json` |
| `load_conversations()` from a direct `conversations.json` path | `minimal/` | `test_load_conversations_from_direct_json_path` |
| `load_conversations()` from a directory | `minimal/` | `test_load_conversations_from_directory` |
| Errors are JSON-serializable for `ingest_runs.errors_json` | `malformed/` | `test_errors_are_json_serializable_for_ingest_runs` |
| Non-list payload reported, not raised | — | `test_non_list_payload_is_reported_not_raised` |
| Provider and URL correct across all fixtures | all | `test_all_parsed_conversations_use_the_claude_provider_and_url` (parametrized) |

Additional `load_conversations()` failure-path tests:
`test_load_conversations_reports_missing_source`,
`test_load_conversations_reports_directory_without_conversations_json`,
`test_load_conversations_reports_invalid_json`.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| Concrete Claude importer module exists | pass | `src/chat_chronicle/adapters/claude_export.py` defines `load_conversations()` and `parse_conversations_json()`. |
| No adapter base/protocol added | pass | `grep -rn "AdapterProtocol" src/ tests/` → no matches; `src/chat_chronicle/adapters/` contains only `__init__.py`, `chatgpt_export.py`, `claude_export.py`. |
| Export shape verification documented | pass | "Export Shape Verification" section above: no real export available, assumptions tabulated. |
| `conversations.json` flat list shape parsed | pass | `test_realistic_export_parses_flat_conversation_list`; non-list payload covered by `test_non_list_payload_is_reported_not_raised`. |
| `uuid`/`name`/timestamps/`chat_messages` mapped | pass | `test_minimal_conversation_metadata_is_normalized`, `test_realistic_export_preserves_chat_message_order_with_contiguous_seq` |
| Claude URLs constructed | pass | `test_all_parsed_conversations_use_the_claude_provider_and_url` asserts `https://claude.ai/chat/{uuid}` for every fixture. |
| Text bodies extracted from Claude message shape | pass | `test_minimal_messages_are_ordered_and_mapped` (blocks joined by `"\n\n"`), `test_plain_string_content_is_supported` |
| Non-text/malformed content recorded without crash | pass | `test_mixed_content_preserves_text_and_reports_non_text_blocks`, `test_message_with_only_non_text_content_is_skipped_and_seq_stays_contiguous`, `test_malformed_records_do_not_abort_parsing_of_valid_conversations` |
| Timestamps become UTC datetimes | pass | `test_realistic_export_normalizes_timestamps_to_utc`, `test_offset_aware_timestamps_are_converted_to_utc` (`+02:00` → UTC) |
| Returns WP-1.1 normalized models | pass | `test_parse_minimal_export_returns_one_conversation` asserts `isinstance(conversation, Conversation)`; `Message` objects come from `chat_chronicle.models`. |
| Synthetic fixtures only | pass | All five fixtures hand-written; `git status` shows only `tests/fixtures/claude/` JSON added, no archives or `.db` files. |
| No DB writes or public CLI ingest behavior added | pass | `grep -n "sqlite3\|from chat_chronicle.db" src/chat_chronicle/adapters/claude_export.py` → no matches; `cli.py` unchanged. |
| ChatGPT importer remains accepted | pass | `git diff --stat -- src/chat_chronicle/adapters/chatgpt_export.py tests/test_chatgpt_export.py` → empty; all prior tests pass in the 64-test run. |
| `poetry run pytest` passes | pass | `64 passed in 1.90s` (40 pre-existing + 24 new). |
| `poetry run ruff check .` passes | pass | `All checks passed!` |
| `poetry run chronicle --help` still lists commands | pass | Lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, `open`. |

## Command Evidence

### `poetry env info --path`

The documented `VIRTUAL_ENV` hazard from `md/agent-operating-notes.md` **fired on
this run.** The first invocation reported another project's environment:

```text
C:\work\Github\Asensus\SurgeryCopilot\GitLabRepo\CopilotLocalMongoDB\.venv
```

Per the operating notes I stopped and cleared the inherited `VIRTUAL_ENV` before
running any Poetry command. After clearing it:

```powershell
PS> $env:VIRTUAL_ENV = $null; poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv

PS> $env:VIRTUAL_ENV = $null; poetry run python -c "import sys; print(sys.prefix)"
C:\work\Github\mcp-chat-chronicle\.venv
```

**No Poetry command was run against the foreign environment.** Every command
below was executed with `VIRTUAL_ENV` cleared, in
`C:\work\Github\mcp-chat-chronicle\.venv`.

### `poetry run pytest`

```text
................................................................         [100%]
64 passed in 1.90s
```

(40 pre-existing WP-0.1 / WP-1.1 / WP-1.2 tests, plus 24 new Claude tests.)

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

All seven commands still listed; none gained behavior in this work package.

### Scope verification

```text
PS> git status --porcelain
 M md/development-ledger.md            # pre-existing, PM artifact, untouched
?? md/handoffs/WP-1.4-cli-ingest-stats.md   # pre-existing, PM artifact, untouched
?? src/chat_chronicle/adapters/claude_export.py
?? tests/fixtures/claude/
?? tests/test_claude_export.py

PS> grep -rn "AdapterProtocol" src/ tests/
none

PS> grep -n "sqlite3|requests|urllib|httpx|from chat_chronicle.db" src/chat_chronicle/adapters/claude_export.py
none

PS> git diff --stat -- src/chat_chronicle/adapters/chatgpt_export.py tests/test_chatgpt_export.py src/chat_chronicle/db.py src/chat_chronicle/cli.py
(empty — untouched)
```

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement DB writes | pass | `claude_export.py` imports only `json`, `zipfile`, `datetime`, `pathlib`, `typing`, `pydantic`, and `chat_chronicle.models`. No `chat_chronicle.db` import, no `sqlite3`. |
| Did not implement public CLI ingest behavior | pass | `cli.py` untouched; `chronicle --help` output unchanged; `ingest` remains a stub for WP-1.4. |
| Did not add adapter base/protocol | pass | No `adapters/base.py`; no `AdapterProtocol`; the module is concrete and shares no code with `chatgpt_export.py`. |
| Did not add Gemini/Class B importers | pass | Only `claude_export.py` added under `adapters/`. |
| Did not commit real exports/private data | pass | All five fixtures hand-written and synthetic. No real export was inspected. No `.db`, `.zip`, secret, or private file added; `scratch/wp-1.1-evidence.db` remains gitignored. |
| Did not add runtime dependencies | pass | `pyproject.toml` untouched; stdlib + existing `pydantic` only. |
| Did not alter the DB schema | pass | `db.py` untouched. |
| Did not add network calls | pass | No HTTP client imported; the Claude URL is built by string formatting only. |

## Risks Or Follow-Ups

1. **Unverified export shape (highest risk).** No real Claude export was
   available, so every field mapping is an assumption from the master plan and
   public documentation. Before WP-1.4 ships, a real export should be obtained
   and diffed against `tests/fixtures/claude/realistic/conversations.json`. The
   blast radius is contained to one module and its fixtures. Recommend the PM
   requests an export and files a short verification task.

2. **Role vocabulary is not normalized across providers.** Claude emits
   `"human"` where ChatGPT emits `"user"`; the parser passes both through
   verbatim. Search and display (M2) will eventually need a canonical role
   vocabulary. This is a cross-provider decision, deliberately not made
   unilaterally inside WP-1.3. Recommend a PM decision before WP-2.1.

3. **Numeric timestamps are rejected, not coerced.** If a real export turns out
   to carry Unix timestamps in any field, those fields will degrade to `None`
   with an `invalid_timestamp` error rather than crash. This is intentional and
   fail-loud, but it means a shape surprise shows up as error volume rather than
   a hard failure. Resolved by risk 1.

4. **`content` vs `text` precedence.** The parser prefers `content[]` blocks. If
   a real export ever puts the full text in `text` and only a truncated preview
   in `content`, bodies would be truncated. The fallback ordering should be
   confirmed against a real export as part of risk 1.

5. **Attachment and tool-use content is discarded.** Non-text blocks (`image`,
   `tool_use`) are skipped with a `non_text_content_block` error, and a message
   whose content is entirely non-text is dropped from the transcript. This
   matches the handoff ("skip messages with no text body"), but it means the
   error list on a tool-heavy export will be noisy. If WP-1.4 surfaces error
   counts to the user, consider classifying `non_text_content_block` as
   informational rather than an error.
