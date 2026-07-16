# WP-1.5 Completion Report: scan-local Source Inventory

## Status

ready for PM validation

## Files Changed

- `src/chat_chronicle/scan.py` — replaces the placeholder with read-only source inventory definitions and shallow signature checks.
- `src/chat_chronicle/cli.py` — implements `chronicle scan-local` and renders a Rich table.
- `tests/test_cli.py` — updates the old stub assertion.
- `tests/test_cli_scan_local.py` — adds focused temp-only scan-local tests.
- `md/handoffs/reports/WP-1.5-completion-report.md` — this report.

## Behavior Summary

`chronicle scan-local` now reports six default sources:

- `chatgpt` official export folder: default/configured `exports/openai`, or `--root <dir>/openai`.
- `claude` official export folder: default/configured `exports/claude`, or `--root <dir>/claude`.
- `openai_codex` local store: default/configured `%USERPROFILE%\.codex`.
- `claude_code` local store: default/configured `%USERPROFILE%\.claude\projects`.
- `cursor` planned local store: `%APPDATA%\Cursor\User\workspaceStorage`.
- `copilot_vscode` planned local store: `%APPDATA%\Code\User\workspaceStorage`.

The command is read-only. It does not open or initialize the database, create directories, import data, or parse transcript bodies. Export checks are filename-level (`.zip`, `conversations.json`, and OpenAI `conversations-*.json`). Local-store checks are shallow filesystem signatures (`session_index.jsonl`, `sessions/`, `rollout-*.jsonl`, or Claude Code `.jsonl` files). Planned Cursor/Copilot paths are reported as experimental when present and are not ingested.

## Supported Statuses

- `found` — expected path exists and a shallow signature suggests usable data.
- `missing` — expected path does not exist.
- `empty` — path exists but no shallow source signature was found.
- `experimental` — planned source path exists but no extractor is implemented for `collect`.
- `error` — shallow filesystem inspection raised an `OSError`.

`unsupported` is not currently emitted by `scan-local`; planned sources use `experimental` when present and `missing` when absent.

## Validation Command Results

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

```text
poetry run pytest tests/test_cli_scan_local.py -q
.......                                                                  [100%]
```

```text
poetry run pytest
........................................................................ [ 32%]
........................................................................ [ 65%]
........................................................................ [ 98%]
....                                                                     [100%]
220 passed in 17.19s
```

```text
poetry run ruff check .
All checks passed!
```

```text
poetry run chronicle scan-local
Provider         Path                                                        Status
chatgpt          C:\work\Github\mcp-chat-chronicle\exports\openai            found
claude           C:\work\Github\mcp-chat-chronicle\exports\claude            found
openai_codex     %USERPROFILE%\.codex                                      found
claude_code      %USERPROFILE%\.claude\projects                            found
cursor           %USERPROFILE%\AppData\Roaming\Cursor\User\workspaceStorage missing
copilot_vscode   %USERPROFILE%\AppData\Roaming\Code\User\workspaceStorage   experimental
```

The manual scan output included only provider/path/status/notes. No private transcript content, message text, JSON snippets, DB rows, or export contents were printed.

```text
poetry run chronicle --help
Usage: chronicle [OPTIONS] COMMAND [ARGS]...

A local-first, searchable archive of your AI conversations.

Options:
  --version          Show the version and exit.
  --help             Show this message and exit.

Commands:
  ingest         Ingest one supported source, or sweep a parent directory for sources.
  ingest-folder  Sweep a drop folder for export archives and ingest each one.
  init           Create the local .chronicle/, config, DB, and export folder structure.
  collect        Ingest every enabled configured source using accepted adapters.
  scan-local     Report, read-only, which AI-tool data stores exist on this machine.
  stats          Show per-source counts and the most recent ingest runs.
  recent         List the most recently active conversations.
  search         Search the archive with FTS5 ranking and snippets.
  open           Open a result: deep link for web chats, transcript view otherwise.
```

## Test Coverage Added

- `scan-local` lists all expected providers.
- Missing default paths are reported as `missing` and exit zero.
- Synthetic ChatGPT/OpenAI export signatures report `found`.
- Synthetic Claude export signatures report `found`.
- Synthetic OpenAI Codex local-store shape reports `found`.
- Synthetic Claude Code local-store shape reports `found`.
- Synthetic Cursor/Copilot paths report `experimental`, not imported.
- `scan-local` does not create a DB file.
- `scan-local` does not modify source files.

All tests use temporary directories and monkeypatched `USERPROFILE`/`APPDATA`; no test reads the real user profile.

## Git Status Summary

Expected working tree after this WP:

```text
 M src/chat_chronicle/cli.py
 M src/chat_chronicle/scan.py
 M tests/test_cli.py
?? md/handoffs/reports/WP-1.5-completion-report.md
?? tests/test_cli_scan_local.py
```

No DB files, private exports, export ZIPs, JSONL transcripts, source dumps, or generated private artifacts were added.

## Known Limitations And WP-1.6 Follow-Ups

- `scan-local` uses hard-coded planned Cursor/Copilot paths for discovery; no extractor or collection support is added.
- `scan-local --root` overrides only the export root for ChatGPT/Claude. Local-store paths continue to come from config/default environment paths.
- The command does not implement JSON output; the Rich table is the supported WP-1.5 output.
- Existing WP-1.6 config paths for supported sources are reused when `.chronicle/config.yaml` exists. Future config work can reuse `scan_sources()` for source-management or collect previews.
