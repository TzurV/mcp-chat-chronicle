# RS-2 — Claude Code Local JSONL Format Memo

**Date:** 2026-07-13
**Status:** complete for WP-3.1 implementation; updated by WP-3.1.1 hardening
**Scope:** prior-art parser review, privacy-safe local shape inspection, and extractor decisions for `claude_code`.

## Prior Art Inspected

1. **Agent Sessions** — `https://github.com/jazzyalex/agent-sessions`
   - Inspected files:
     - `AgentSessions/Services/ClaudeSessionParser.swift`
     - `AgentSessions/Services/SessionDiscovery.swift`
     - `docs/claude-code-session-format.md`
     - `docs/guides/claude-code-jsonl-history.html`
   - Relevant findings:
     - Primary Claude Code layout is `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`.
     - Chat records use top-level `type` values such as `user` and `assistant`.
     - Visible text is commonly nested under `message.content`; `message.role` carries the source role.
     - `message.content` can be a string or an array of blocks. Text blocks use `{"type":"text","text":"..."}`. Tool/thinking/image blocks require special handling and should not be treated as ordinary chat text by default.
     - Metadata/tooling rows include `summary`, `file-history-snapshot`, `ai-title`, `custom-title`, `agent-name`, and operational records.
     - Session metadata appears redundantly in records: `sessionId`, `uuid`, `parentUuid`, `timestamp`, `cwd`, `gitBranch`, `version`, and sometimes `entrypoint`.
     - Agent Sessions also supports Claude Desktop/local-agent sidecars and richer tool/event rendering; WP-3.1 intentionally does not copy that broader scope.

2. **claude-record** — `https://github.com/davidglogan/claude-record`
   - Inspected files:
     - `src/claude-record`
     - `docs/ARCHITECTURE.md`
   - Relevant findings:
     - This project wraps/records Claude sessions into its own `.log` files and `.claude-record` indexes.
     - It does not provide a parser for Claude Code's native `.claude/projects/*.jsonl` transcript format.
     - Useful design signal: keep session metadata and indexes separate from raw logs, and treat summarization/index failures as non-fatal. WP-3.1 uses existing DB ingest-run errors rather than adding a separate index.

3. **codex-trace** — `https://github.com/PixelPaw-Labs/codex-trace`
   - Inspected files:
     - `src-tauri/src/parser/entry.rs`
     - `src-tauri/src/parser/session.rs`
     - `src-tauri/src/parser/discover.rs`
   - Relevant findings:
     - This is Codex-specific, not Claude-specific, but reinforces the Class B parsing approach: parse JSONL line by line, isolate provider signatures, tolerate format drift, and avoid invoking the source CLI at parse time.
     - Codex records use `payload` and `session_meta` / `response_item` shapes, which are distinct from Claude Code's `message` / `sessionId` shape. WP-3.1 detection keeps these providers separate and asks for explicit `--provider` if signatures ever overlap.

## Local Inspection Summary

Local path inspected read-only after prior-art review:

```text
%USERPROFILE%\.claude\projects
```

Privacy-safe observations only:

- Project directories found: 4.
- `.jsonl` files found: 12.
- Sample project directory names followed the Windows encoded-path shape, for example `c--work-Github-...`.
- File extension observed: `.jsonl`.
- Sample file name shape: UUID `.jsonl`.
- Seven record types targeted by the WP-3.1.1 addendum: `user`, `assistant`, `queue-operation`, `attachment`, `file-history-snapshot`, `system`, `ai-title`.
- Other record types observed in a bounded sample: `last-prompt`, `mode`.
- Sample key names by type confirmed:
  - `user`: `cwd`, `entrypoint`, `gitBranch`, `isSidechain`, `message`, `parentUuid`, `permissionMode`, `promptId`, `promptSource`, `sessionId`, `timestamp`, `type`, `userType`, `uuid`, `version`.
  - `assistant`: `cwd`, `entrypoint`, `gitBranch`, `isSidechain`, `message`, `parentUuid`, `requestId`, `sessionId`, `timestamp`, `type`, `userType`, `uuid`, `version`.
  - `message` keys: `content`, `role`; assistant messages also showed model/usage-related metadata keys.

No real transcript text was copied into tests, docs, reports, or chat.

## Supported Record Shapes

WP-3.1 / WP-3.1.1 supports:

- top-level `type` values: `user`, `assistant`, `system`, `developer`;
- nested `message.role` when present, normalized to `user`, `assistant`, `system`, or `developer`;
- `message.content` as:
  - a string;
  - a list containing strings and/or text blocks with `type: "text"` and `text`;
- top-level `timestamp` ISO 8601 strings;
- `sessionId` for conversation identity;
- `uuid` for message identity;
- `cwd` or `project` for project hints;
- metadata title records: `ai-title`, `custom-title`, `agent-name`;
- `isSidechain` records when they contain visible supported chat text.

`ai-title` behavior:

- `ai-title` records carry the best available Claude Code session title observed so far.
- `ai-title` is parsed as metadata, not as a chat message.
- `ai-title` wins over synthesized titles from first user messages.
- If `ai-title` is absent, the extractor falls back to existing title synthesis from the first visible user message, then the file fallback id.

Known metadata/tooling rows skipped without noisy errors:

- `summary`
- `file-history-snapshot`
- `attachment`
- `last-prompt`
- `queue-operation`
- `mode`
- title metadata rows after title extraction

Known non-chat content blocks skipped without noisy errors:

- `tool_use`, `tool-use`, `tool_call`, `tool-call`
- `tool_result`, `tool-result`
- `thinking`
- `image`
- `document`

Unknown top-level record types and unknown content block types are recorded as serializable parse errors and ingestion continues.

## Identity And Timestamps

Conversation identity:

- v1 intentionally stores one WorkTrail conversation per source `.jsonl` file.
- Claude Code `sessionId` alone is not used as `provider_conv_id`, because resumed or branched logical sessions can span multiple `.jsonl` files that share the same raw `sessionId`.
- File-scoped `provider_conv_id` is derived from the raw `sessionId` plus file identity when a source path is known.
- If `sessionId` is absent, the file fallback id is used and still scoped by file identity when a source path is known.
- `resume_hint` preserves the raw resumable id as `claude --resume <sessionId>` when present.

Message identity:

- Prefer top-level `uuid`.
- Fallback to `line-<line_number>`.
- `parentUuid` is observed as a parent-chain pointer but is not currently persisted in the normalized `Message` model. It is retained as a documented source fact for future logical-thread linkage work.
- `isSidechain` is observed on user/assistant/system records. WP-3.1.1 includes visible sidechain messages in the per-file transcript and does not flag them as errors.

Project identity:

- Prefer `cwd` or `project` fields from records.
- Project hint name is the basename of the inferred root path.
- If no reliable path exists, use the encoded project directory name as a hint with `root_path = null`.
- The extractor stays DB-free. It returns project hints keyed by provider conversation id; CLI ingest creates/reuses project rows and assigns `Conversation.project_id`.

Timestamps:

- Parse ISO 8601 strings and normalize to UTC.
- Conversation `created_at` is the minimum valid record timestamp.
- Conversation `updated_at` is the maximum valid record timestamp.
- Invalid timestamps are non-fatal parse errors.

## Link-Back Handling

WP-3.1 populates:

- `origin_path`: resolved local `.jsonl` transcript path for every parsed session.
- `resume_hint`: `claude --resume <raw-session-id>` when `sessionId` exists, otherwise the file fallback id.
- `project_id`: assigned during CLI ingest from extractor project hints via a DB helper.

`chronicle open` already prints `origin_path`, `origin_file`, `resume_hint`, and the stored transcript for local-source conversations.

## Known Unknowns And Drift Risks

- Claude Code local JSONL is undocumented Class B storage and may add record types or block shapes.
- Tool output may be useful for future search, but WP-3.1 keeps the transcript focused on visible chat text and skips tool bookkeeping unless future requirements expand search scope.
- Encoded project directory names are not a lossless source of Windows paths because hyphens can be both separators and literal path characters. `cwd` is preferred whenever present.
- The current schema does not persist `parentUuid`, branch lineage, or explicit logical thread grouping.
- File-scoped `provider_conv_id` protects v1 ingest from silent overwrite, but a moved/copied source file can appear as a new conversation because file identity is part of the id.
- Cross-file logical conversation grouping is a future backlog candidate, not WP-3.1.1 scope.
- Claude Desktop/local-agent sidecar metadata and subagent relationships are out of WP-3.1 scope.
- `.jsonl.zst` support is explicitly out of scope.
- First real ingest on this machine may only see recent Claude Code history because cleanup was previously at the default horizon before `cleanupPeriodDays` was raised.
