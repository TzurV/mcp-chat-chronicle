# WP-1.2.1 Completion Report

## Status

ready for PM validation

## Files Changed

- `src/chat_chronicle/adapters/chatgpt_export.py` - added split `conversations-*.json` discovery/loading and quiet skips for known OpenAI metadata content types.
- `src/chat_chronicle/cli.py` - updated `--provider auto` detection to recognize split ChatGPT/OpenAI exports.
- `tests/test_chatgpt_export.py` - added synthetic split export, malformed split member, canonical precedence, direct split file, and metadata skip coverage.
- `tests/test_cli_ingest_stats.py` - added synthetic split ZIP auto-detection ingest coverage.
- `md/handoffs/reports/WP-1.2.1-completion-report.md` - this report.

Pre-existing worktree state before this implementation already included:

- modified `md/development-ledger.md`;
- untracked `md/handoffs/WP-1.2.1-openai-split-export-compatibility.md`.

Those were not changed by this implementation.

## Implementation Summary

The ChatGPT importer now treats split OpenAI export files as one logical official export source. Existing `conversations.json` behavior is preserved and preferred when present. When the canonical file is absent, split files are decoded in stable lexical order, list payloads are concatenated in memory, and the existing conversation parser handles IDs, branch linearization, URLs, timestamps, and per-record parse errors.

No merged private JSON file is written to disk. No provider name, schema, adapter abstraction, or non-ChatGPT importer behavior was added.

## Split-File Discovery Rules

- ZIP input:
  - prefer the shallowest `conversations.json` member;
  - otherwise load every non-directory member whose basename starts with `conversations-` and ends with `.json`;
  - sort split members lexically by archive member name;
  - malformed JSON, non-list payloads, or invalid UTF-8 in a split member are recorded as serializable parse errors and valid members continue.
- Directory input:
  - prefer direct child `conversations.json`;
  - otherwise recursively discover files matching `conversations-*.json`;
  - sort split paths lexically.
- Direct JSON file input:
  - existing direct `conversations.json` behavior remains;
  - direct `conversations-000.json` style files work because direct file loading still decodes the JSON list through the same parser.
- If both `conversations.json` and split files exist, `conversations.json` wins. This preserves old official-export compatibility and avoids double-importing overlapping records.

## Metadata Handling

Silently skipped known non-visible OpenAI metadata content types:

- `thoughts`
- `reasoning_recap`

Remaining fail-visible parser warnings/errors:

- Unknown unsupported content types without `parts` still produce `unsupported_content_type`.
- Unknown non-string entries in `content.parts`, including opaque dicts, still produce `non_text_content_part`.
- Malformed split members can produce `invalid_json`, `invalid_encoding`, or `unexpected_export_shape`.

Real-export message count did not change from the handoff smoke count: final stats show 5,166 messages. Real-export parse noise dropped to 92 `non_text_content_part` warnings; `thoughts` and `reasoning_recap` no longer create parse errors.

## Synthetic Test Evidence

Covered in `tests/test_chatgpt_export.py`:

- old ZIP with `conversations.json` still works: `test_load_conversations_from_zip`;
- split ZIP works and sorts lexically: `test_load_conversations_from_split_zip`;
- directory split files work: `test_load_conversations_from_split_directory`;
- direct `conversations-000.json` file works: `test_load_conversations_from_direct_split_json_file`;
- `conversations.json` is preferred over split members: `test_conversations_json_is_preferred_over_split_members`;
- malformed split member records a serializable error and valid split files still parse: `test_malformed_split_member_reports_error_and_valid_members_still_parse`;
- `thoughts` and `reasoning_recap` skip without errors: `test_known_openai_metadata_content_types_are_skipped_without_errors`.

Covered in `tests/test_cli_ingest_stats.py`:

- auto-detection identifies split OpenAI export ZIPs as `chatgpt`: `test_ingest_auto_detects_split_chatgpt_zip`.

## Command Evidence

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

```text
poetry run pytest tests/test_chatgpt_export.py -q
...........................                                              [100%]
```

```text
poetry run pytest
........................................................................ [ 50%]
........................................................................ [100%]
144 passed in 16.88s
```

```text
poetry run ruff check .
All checks passed!
```

```text
poetry run chronicle --help
Usage: chronicle [OPTIONS] COMMAND [ARGS]...
Commands: ingest, ingest-folder, collect, scan-local, stats, search, open
```

## Real OpenAI Export Smoke

Input: one owner ZIP under `exports\openai`. Transcript content was not printed or copied.

```text
poetry run chronicle ingest exports\openai\<owner-zip>.zip --provider chatgpt --db-path C:\tmp\wp-1.2.1-openai-smoke-final.db
provider: chatgpt
conversations seen: 422
added: 422  updated: 0  skipped: 0
parse errors: 92
ingest run id: 1
```

```text
poetry run chronicle stats --db-path C:\tmp\wp-1.2.1-openai-smoke-final.db
total conversations: 422
total messages: 5166
provider chatgpt conversations: 422
recent ingest run: seen 422, added 422, updated 0, skipped 0, errors 92
```

Aggregate parser error-code count, queried without transcript content:

```text
{'non_text_content_part': 92}
```

Auto-detection smoke on the same real split ZIP:

```text
poetry run chronicle ingest exports\openai\<owner-zip>.zip --provider auto --db-path C:\tmp\wp-1.2.1-openai-auto-smoke-final.db
provider: chatgpt
conversations seen: 422
added: 422  updated: 0  skipped: 0
parse errors: 92
```

Optional private search/open smoke was not run because no private search term was provided. The DB contains the expected 422 conversations and 5,166 messages.

## Git Status And Artifact Check

```text
git status --short --untracked-files=all
 M md/development-ledger.md
 M src/chat_chronicle/adapters/chatgpt_export.py
 M src/chat_chronicle/cli.py
 M tests/test_chatgpt_export.py
 M tests/test_cli_ingest_stats.py
?? md/handoffs/WP-1.2.1-openai-split-export-compatibility.md
?? md/handoffs/reports/WP-1.2.1-completion-report.md
```

```text
git ls-files exports *.zip *.db
<no output>
```

No real export, `.db`, `.zip`, private transcript, or generated merged JSON file is tracked.

## Known Limitations And Follow-Ups

- Opaque dict entries inside `content.parts` are still recorded as `non_text_content_part`; they are not ingested as text. The real export has 92 such warnings.
- Optional private search/open verification remains available when the owner provides a safe private term to check without printing transcript content.
