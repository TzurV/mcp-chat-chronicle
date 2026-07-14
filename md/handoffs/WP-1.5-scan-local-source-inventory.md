# WP-1.5 Handoff: scan-local Source Inventory

## Objective

Implement a read-only source inventory command:

```powershell
poetry run chronicle scan-local
```

The command should report which supported or planned AI-history sources appear to exist on this Windows machine before ingest. It must not import data, write to the database, parse full transcripts, or create directories.

This is an accessories/usability task. It prepares the ground for WP-1.6 config defaults and `chronicle collect`, but does not implement YAML config or collection.

## Source Of Truth

Read before implementation:

- `md/master-plan.md`
- `md/development-ledger.md`
- `md/agent-operating-notes.md`
- `md/research/RS-1-chat-history-access-findings.md`
- `md/handoffs/WP-1.4.1-directory-ingest-sweep.md`
- `src/chat_chronicle/cli.py`
- current adapter detection behavior in `src/chat_chronicle/adapters/`
- existing CLI tests

## Required Poetry Preflight

Before running Poetry commands:

```powershell
poetry env info --path
```

Expected:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If it points elsewhere, stop and fix the shell according to `md/agent-operating-notes.md`.

## Command Scope

Implement the existing `scan-local` CLI command as a real read-only command.

Expected command:

```powershell
poetry run chronicle scan-local
```

Optional flags may be added if useful and small:

```powershell
poetry run chronicle scan-local --json
poetry run chronicle scan-local --root .\exports
```

Do not add these flags if they create unnecessary complexity. A clear Rich table is enough for this WP.

## Sources To Inventory

Check at least these default locations:

| Provider | Type | Default path | Expected status behavior |
| --- | --- | --- | --- |
| `chatgpt` | official export folder | `exports/openai` | found/missing; shallow check for ZIPs, `conversations.json`, or `conversations-*.json` |
| `claude` | official export folder | `exports/claude` | found/missing; shallow check for ZIPs or `conversations.json` |
| `openai_codex` | local store | `%USERPROFILE%\.codex` | found/missing; shallow check for `session_index.jsonl`, `sessions/`, or rollout JSONL files |
| `claude_code` | local store | `%USERPROFILE%\.claude\projects` | found/missing; shallow check for JSONL files |
| `cursor` | planned local store | `%APPDATA%\Cursor\User\workspaceStorage` | experimental/found/missing; do not parse DB files |
| `copilot_vscode` | planned local store | `%APPDATA%\Code\User\workspaceStorage` | experimental/found/missing; do not parse DB files |

Use Windows environment variables carefully. Tests should avoid depending on the real user profile by monkeypatching environment variables and/or passing temporary paths through helper functions.

## Status Semantics

Use concise statuses. Suggested set:

- `found`: source path exists and shallow signature suggests usable data;
- `missing`: expected path does not exist;
- `empty`: path exists but no shallow source signature found;
- `experimental`: path exists for a planned source that is not ingest-supported yet;
- `unsupported`: path is known but no importer/extractor exists yet;
- `error`: shallow inspection failed due to permissions or filesystem error.

Do not treat missing optional sources as command failure.

Exit code should be zero unless the command itself fails.

## Output Requirements

Render a table with at least:

```text
Provider | Kind | Path | Status | Notes
```

The table should distinguish:

- cloud/export sources that require user downloads into `exports/...`;
- native local histories already stored on the machine;
- planned/experimental sources that are detected but not ingest-supported.

Example notes:

- `ingest: chronicle ingest .\exports\openai --provider chatgpt`
- `ingest: chronicle ingest %USERPROFILE%\.codex --provider openai_codex`
- `planned extractor; not ingested by collect yet`
- `missing; request/export history from provider`

Do not print private transcript content, project descriptions, message text, or raw JSON snippets.

## Relationship To WP-1.6

WP-1.6 will add YAML config and `chronicle collect`. WP-1.5 should keep the design compatible:

- default DB path remains `.chronicle/chronicle.db`;
- default exports root remains `exports`;
- default export folders are `exports/openai` and `exports/claude`;
- local native defaults are `%USERPROFILE%\.codex` and `%USERPROFILE%\.claude\projects`;
- source definitions should be easy to reuse later by config/collect code.

Do not implement YAML config in WP-1.5.

## Backlog Awareness

The plan now includes a future history-download helper for providers that support documented exports or safe automation. WP-1.5 should not download anything. It may print a short note like `download/export required` for missing cloud-export folders, but no network/browser automation is in scope.

The future YAML should record which engines the user uses or wants supported. WP-1.5 can hard-code current defaults for now.

## Out Of Scope

Do not implement:

- YAML config parsing or writing;
- `chronicle init`;
- `chronicle collect`;
- download automation;
- source CRUD;
- parsing full conversations;
- DB writes;
- Cursor/Copilot extraction;
- browser cache forensics;
- package install side effects.

## Tests Required

Add focused tests for:

- `scan-local` lists all expected providers;
- missing default paths are reported as missing and command exits zero;
- export folder with a synthetic ChatGPT/OpenAI export signature reports found;
- export folder with a synthetic Claude export signature reports found;
- synthetic OpenAI Codex local-store shape reports found;
- synthetic Claude Code local-store shape reports found;
- Cursor/Copilot existing paths are marked experimental/unsupported, not imported;
- no DB file is created by `scan-local`;
- no source files are modified;
- optional JSON output if implemented.

Use temporary directories and synthetic fixtures only.

## Required Validation Evidence

Include exact command output for:

```powershell
poetry env info --path
poetry run pytest tests/test_cli_scan_local.py -q
poetry run pytest
poetry run ruff check .
poetry run chronicle scan-local
poetry run chronicle --help
```

If no dedicated `tests/test_cli_scan_local.py` is created, explain where the tests live and run that file explicitly.

For the manual `scan-local` smoke, report only provider/path/status rows. Do not include private transcript content.

## Completion Report Requirements

Write:

```text
md/handoffs/reports/WP-1.5-completion-report.md
```

The report must include:

- status: `ready for PM validation`, `partial`, or `blocked`;
- files changed;
- source inventory behavior summary;
- exact statuses supported;
- validation command results;
- privacy-safe manual `scan-local` output summary;
- git status summary confirming no DB/export/private data was added;
- known limitations and follow-ups for WP-1.6.

## Acceptance Criteria

WP-1.5 is complete when:

- `chronicle scan-local` is functional and read-only;
- it reports configured/default export folders and native local history paths;
- missing sources do not fail the command;
- supported local/export sources are distinguishable from planned/experimental sources;
- no DB writes or directory creation occur;
- tests and Ruff pass;
- completion report is written at the required path;
- no private transcript, DB, export ZIP, JSONL, or generated dump is committed.
