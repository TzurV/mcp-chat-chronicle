# WP-3.1 Completion Report — Claude Code Local Extractor

## Status

**ready for PM validation**

WP-3.1 is implemented with a concrete `claude_code` extractor, minimal `chronicle ingest --provider claude_code` wiring, CO-1 link-back fields, project persistence, synthetic fixtures, prior-art memo, and end-to-end CLI smoke evidence.

## WP-3.1.1 Addendum

After this report was first written, RS-2 added a narrow hardening requirement before WP-3.1 acceptance. The addendum is tracked in `md/handoffs/WP-3.1.1-claude-code-rs2-format-hardening.md`, with completion evidence in `md/handoffs/reports/WP-3.1.1-completion-report.md`.

The key post-WP-3.1 identity change is that Claude Code `provider_conv_id` is now file-scoped rather than raw `sessionId` only, so two `.jsonl` files sharing a Claude Code `sessionId` cannot silently overwrite one another. `resume_hint` still uses the raw `sessionId`.

## Files Changed

- `src/chat_chronicle/adapters/claude_code.py`
- `src/chat_chronicle/cli.py`
- `src/chat_chronicle/db.py`
- `tests/test_claude_code.py`
- `tests/test_db.py`
- `tests/fixtures/claude_code/**`
- `md/research/RS-2-claude-code-format-memo.md`
- `md/handoffs/reports/WP-3.1-completion-report.md`
- `md/development-ledger.md`

Existing uncommitted handoff docs from the starting tree remain present:

- `md/handoffs/WP-3.1-claude-code-extractor.md`
- pre-existing edits in `md/development-ledger.md`, now updated for completion state

## Implementation Summary

- Added concrete `claude_code` adapter with no shared adapter framework.
- Supports a single `.jsonl`, one Claude Code project directory, or a `.claude/projects`-style root with multiple project directories.
- Parses JSONL line by line and continues through malformed records.
- Extracts visible `user`, `assistant`, `system`, and `developer` text from `message.content` strings or text blocks.
- Skips known metadata/tooling records without noisy errors.
- Captures malformed/unknown records as serializable errors for `ingest_runs.errors_json`.
- Populates `origin_path` and best-effort `resume_hint`.
- Returns DB-free project hints; CLI ingest persists/reuses project rows and assigns `project_id`.
- Adds cautious auto-detection for clear Claude Code JSONL/path signatures while preserving Codex detection.

## Prior-Art Research

Memo: `md/research/RS-2-claude-code-format-memo.md`

Prior art inspected:

- Agent Sessions: `AgentSessions/Services/ClaudeSessionParser.swift`, `AgentSessions/Services/SessionDiscovery.swift`, `docs/claude-code-session-format.md`, `docs/guides/claude-code-jsonl-history.html`.
- claude-record: `src/claude-record`, `docs/ARCHITECTURE.md`.
- codex-trace: `src-tauri/src/parser/entry.rs`, `src-tauri/src/parser/session.rs`, `src-tauri/src/parser/discover.rs`.

Key result: Agent Sessions confirmed the native Claude Code shapes; claude-record is a wrapper/logger rather than a native `.claude/projects` parser; codex-trace reinforced provider-specific JSONL parsing and drift-tolerant detection.

## Local Inspection

Read-only local inspection was performed after prior-art review. Privacy-safe observations only:

- Root: `%USERPROFILE%\.claude\projects`
- Project directories: 4
- `.jsonl` files: 12
- Observed extension: `.jsonl`
- Observed project path shape: encoded Windows paths such as `c--work-Github-...`
- Observed record types in bounded sample: `ai-title`, `assistant`, `attachment`, `file-history-snapshot`, `last-prompt`, `mode`, `queue-operation`, `user`
- Observed key names confirm `message.content`, `message.role`, `sessionId`, `uuid`, `timestamp`, `cwd`, `gitBranch`, `version`

No real transcript text was copied into docs, tests, reports, or chat.

## Identity And Link-Back Behavior

- Provider: `claude_code`
- Source type: `local_store`
- Conversation id: `sessionId`, fallback to filename stem
- Message id: top-level `uuid`, fallback to `line-<line_number>`
- Project hint: prefer `cwd`/`project`; fallback to encoded project directory name
- `origin_path`: resolved transcript `.jsonl` path
- `resume_hint`: `claude --resume <session-id>`
- `project_id`: assigned in CLI ingest via `get_or_create_project(...)`

## Parser Error Behavior

Synthetic malformed fixture coverage verifies:

- invalid JSONL line -> `invalid_jsonl_line`
- unknown top-level type -> `unknown_record_type`
- invalid timestamp -> `invalid_timestamp`
- unknown content block -> `unknown_content_block_type`

Healthy messages in the same file still ingest. Errors serialize through `model_dump()` and are stored in ingest-run JSON.

## Validation Evidence

### Poetry preflight

```text
> poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

### Tests

```text
> poetry run pytest
........................................................................ [ 54%]
............................................................             [100%]
132 passed in 12.20s
```

Focused impacted suite also passed before the full run:

```text
> poetry run pytest tests/test_claude_code.py tests/test_cli_ingest_stats.py tests/test_cli_search_open.py tests/test_db.py -q
.............................................                            [100%]
```

### Ruff

```text
> poetry run ruff check .
All checks passed!
```

### CLI Help

```text
> poetry run chronicle --help
 Usage: chronicle [OPTIONS] COMMAND [ARGS]...

 A local-first, searchable archive of your AI conversations.

 Options:
   --version          Show the version and exit.
   --help             Show this message and exit.

 Commands:
   ingest         Ingest a single official export or supported local session source.
   ingest-folder  Sweep a drop folder for export archives and ingest each one.
   collect        Run every enabled source through its adapter.
   scan-local     Report, read-only, which AI-tool data stores exist on this machine.
   stats          Show per-source counts and the most recent ingest runs.
   search         Search the archive with FTS5 ranking and snippets.
   open           Open a result: deep link for web chats, transcript view otherwise.
```

## Manual CLI Smoke

Temporary DB:

```text
C:\tmp\wp31-claude-code-smoke.db
```

### Ingest

```text
> poetry run chronicle ingest tests\fixtures\claude_code\project_one --provider claude_code --db-path C:\tmp\wp31-claude-code-smoke.db
provider: claude_code
db path: C:\tmp\wp31-claude-code-smoke.db
source path:
C:\work\Github\mcp-chat-chronicle\tests\fixtures\claude_code\project_one
conversations seen: 2
added: 2  updated: 0  skipped: 0
parse errors: 0
ingest run id: 1
```

### Stats

```text
> poetry run chronicle stats --db-path C:\tmp\wp31-claude-code-smoke.db
db path: C:\tmp\wp31-claude-code-smoke.db
total conversations: 2
total messages: 4
Counts by provider: claude_code = 2
Recent ingest runs: run 1, provider claude_code, status success, seen 2, added 2, errors 0
```

### Search

```text
> poetry run chronicle search alpha --provider claude_code --db-path C:\tmp\wp31-claude-code-smoke.db
db path: C:\tmp\wp31-claude-code-smoke.db
result 1 | 2026-07-01T09:01:00.000000Z | claude_code | Synthetic Claude Code fixture | Synthetic Claude Code fixture Find the alpha fixture term. The alpha fixture term is present in this response. | chronicle open 1 (local transcript)
```

### Open

```text
> poetry run chronicle open 1 --db-path C:\tmp\wp31-claude-code-smoke.db
id: 1
provider: claude_code
title: Synthetic Claude Code fixture
date: 2026-07-01T09:01:00.000000Z
origin_path:
C:\work\Github\mcp-chat-chronicle\tests\fixtures\claude_code\project_one\session-one.jsonl
origin_file: session-one.jsonl
resume_hint: claude --resume claude-code-session-one
transcript:
user [2026-07-01T09:00:00.000000Z]:
Find the alpha fixture term.
assistant [2026-07-01T09:01:00.000000Z]:
The alpha fixture term is present in this response.
```

## Git Status Summary

Final status:

```text
> git status --short
 M md/development-ledger.md
 M src/chat_chronicle/cli.py
 M src/chat_chronicle/db.py
 M tests/test_db.py
?? md/handoffs/WP-3.1-claude-code-extractor.md
?? md/handoffs/reports/WP-3.1-completion-report.md
?? md/research/RS-2-claude-code-format-memo.md
?? src/chat_chronicle/adapters/claude_code.py
?? tests/fixtures/claude_code/
?? tests/test_claude_code.py
```

`rg --files -g "*.db" -g "*.sqlite" -g "*.zip" -g "*.jsonl"` found existing synthetic JSONL fixtures, new synthetic `tests/fixtures/claude_code/**` JSONL fixtures, and pre-existing ignored `scratch/*.db` files. `git ls-files` confirmed those scratch DB files are not tracked.

No real transcript files, `.db`, `.sqlite`, `.zip`, or private source data were added or tracked by this work.

The temporary smoke DB is outside the repo at `C:\tmp\wp31-claude-code-smoke.db`.

## Known Limitations And Follow-Ups

- Tool calls/results are skipped as bookkeeping unless they contain future explicitly supported visible text. This keeps WP-3.1 focused on searchable chat transcript text.
- Encoded project directory names are not decoded losslessly; `cwd` is preferred for project root/name when present.
- Claude Desktop/local-agent sidecars, subagent relationships, and `.jsonl.zst` are out of scope.
- Real private Claude Code ingest should be a PM validation smoke only; report counts/path shapes, not transcript text.
