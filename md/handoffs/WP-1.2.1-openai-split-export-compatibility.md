# WP-1.2.1 Handoff: OpenAI Split Export Compatibility

## Objective

Update the accepted ChatGPT/OpenAI official-export importer so it supports the current OpenAI export ZIP layout where conversations are split across files named:

```text
conversations-000.json
conversations-001.json
...
```

This is a narrow compatibility fix discovered during prototype preparation. It does not change the provider model, schema, search behavior, or source-management roadmap.

## Triggering Evidence

The owner received a real OpenAI export under:

```text
C:\work\Github\mcp-chat-chronicle\exports\openai
```

Privacy-safe inspection found:

- one ZIP, approximately 94 MB;
- no `conversations.json`;
- five split files:
  - `conversations-000.json`
  - `conversations-001.json`
  - `conversations-002.json`
  - `conversations-003.json`
  - `conversations-004.json`
- total records across split files: `422`;
- record keys match the existing ChatGPT tree-shaped importer shape, including `conversation_id`, `id`, `mapping`, `current_node`, `create_time`, `update_time`, and `title`;
- in-memory parse through the existing parser produced:
  - parsed conversations: `422`;
  - parsed messages: `5166`;
  - role counts: `user = 2563`, `assistant = 2603`;
  - parse noise: `thoughts = 3571`, `reasoning_recap = 1308`, dict content parts = `92`.

Do not copy real export content into fixtures, docs, reports, or chat. Report counts and structural facts only.

## Source Of Truth

Read before implementation:

- `md/master-plan.md`
- `md/development-ledger.md`
- `md/agent-operating-notes.md`
- `md/handoffs/WP-1.2-chatgpt-export-importer.md`
- `md/handoffs/reports/WP-1.2-validation-review.md`
- `src/chat_chronicle/adapters/chatgpt_export.py`
- `src/chat_chronicle/cli.py`
- `tests/test_chatgpt_export.py`
- `tests/test_cli_ingest_stats.py`

## Required Poetry Preflight

Before running any Poetry command:

```powershell
poetry env info --path
```

Expected:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If Poetry resolves anywhere else, stop and fix the shell according to `md/agent-operating-notes.md`.

## Scope

Implement:

- support for old single-file exports with `conversations.json`;
- support for new split exports with one or more top-level or nested `conversations-*.json` files;
- support for split exports from:
  - ZIP input;
  - directory input;
  - direct JSON file input when the file name is `conversations-000.json` or similar;
- auto-detection updates so `chronicle ingest <openai-export.zip> --provider auto` detects the new split layout as `chatgpt`;
- synthetic fixtures and tests for split exports;
- quieter handling of modern metadata content types observed in the real export:
  - `thoughts`;
  - `reasoning_recap`;
- a required completion report at:

```text
md/handoffs/reports/WP-1.2.1-completion-report.md
```

Do not implement:

- a new provider name;
- a new adapter abstraction;
- schema changes;
- export extraction to disk;
- real export fixtures;
- parsing of hidden chain-of-thought or reasoning metadata into searchable messages;
- changes to Claude, Claude Code, or OpenAI Codex importers except where shared CLI detection requires it.

## Importer Behavior Requirements

The importer should treat the split files as one logical official export source.

Expected behavior:

- If `conversations.json` exists, preserve existing behavior.
- If no `conversations.json` exists but `conversations-*.json` files exist, load them in stable lexical order and concatenate their conversation arrays in memory.
- If both exist, prefer `conversations.json` unless there is a clear reason to do otherwise; document the decision in the report.
- Every split member must decode to a list. If one split member is malformed or not a list, record a parse error with the member name and continue with valid members when possible.
- Existing conversation parsing, branch linearization, ids, URL generation, timestamps, and parse-error-as-data behavior must remain intact.
- The importer must not write merged private JSON files to disk.

## Metadata Noise Requirements

The real export contains many nodes with content types:

- `thoughts`
- `reasoning_recap`

These are not user-visible chat messages and should not create thousands of noisy parse errors. Update `_extract_body` or surrounding logic so these known metadata content types are skipped without error.

For dict entries inside `content.parts`, do not ingest opaque structured objects as text unless there is an explicit, safe, visible text field already supported by synthetic tests. Prefer skip-without-noise for known non-visible structures and fail-visible errors for unknown structures.

The completion report must state:

- which modern content types are skipped silently;
- which still produce parse errors;
- whether message counts changed on the real export smoke.

## Tests Required

Add or update tests for:

- ZIP with old `conversations.json` still works;
- ZIP with split `conversations-000.json` and `conversations-001.json` works;
- directory with split files works;
- direct `conversations-000.json` file works;
- split members are loaded in lexical order;
- malformed split member records a serializable error but valid split files still parse;
- auto-detection identifies split OpenAI export ZIP as `chatgpt`;
- `thoughts` content type is skipped without noisy errors;
- `reasoning_recap` content type is skipped without noisy errors;
- existing ChatGPT fixtures and CLI ingest tests still pass.

Use synthetic fixtures only. Do not include real OpenAI export text or file assets.

## Required Validation Evidence

Include exact command output for:

```powershell
poetry env info --path
poetry run pytest tests/test_chatgpt_export.py -q
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
```

Also run a privacy-safe real-export smoke against the owner ZIP, reporting counts only:

```powershell
poetry run chronicle ingest exports\openai\<zip-name>.zip --provider chatgpt --db-path <tmp-db>
poetry run chronicle stats --db-path <tmp-db>
```

Then optionally confirm search/open on a private search term without pasting transcript content:

```powershell
poetry run chronicle search "<private term>" --provider chatgpt --db-path <tmp-db>
poetry run chronicle open <result-id> --db-path <tmp-db>
```

Report only:

- conversations seen / added / updated / skipped;
- parse error count;
- total conversations/messages;
- whether search finds expected private results;
- whether open shows the expected URL and transcript view;
- no transcript text.

Use a temporary DB outside the repo or an ignored local DB. Do not commit DB files.

## Completion Report Requirements

Write the report here:

```text
md/handoffs/reports/WP-1.2.1-completion-report.md
```

The report must include:

- status: `ready for PM validation`, `partial`, or `blocked`;
- files changed;
- implementation summary;
- exact split-file discovery rules;
- old `conversations.json` compatibility status;
- metadata content types skipped silently;
- remaining parser warnings/errors, if any;
- synthetic test evidence;
- full test and Ruff evidence;
- real OpenAI export smoke counts only;
- git status summary confirming no real export, `.db`, `.zip`, private transcript, or generated merged JSON file is tracked;
- known limitations and recommended follow-ups.

Do not mark ready if the real export still requires a manual merged workaround.

## Acceptance Criteria

WP-1.2.1 is complete when:

- the owner OpenAI ZIP can be ingested directly by `chronicle ingest`;
- `--provider auto` detects split OpenAI export ZIPs as `chatgpt`;
- old `conversations.json` fixtures still pass;
- split-export synthetic fixtures pass;
- `thoughts` and `reasoning_recap` do not create noisy parse errors;
- real-export smoke reports counts only and does not expose private text;
- full tests and Ruff pass;
- no private export files or generated DBs are tracked.
