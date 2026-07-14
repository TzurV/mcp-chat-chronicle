# WP-3.1 Handoff: Claude Code Local Extractor

## Objective

Implement a concrete Claude Code local-history extractor so WorkTrail can ingest and search sessions stored under:

```text
%USERPROFILE%\.claude\projects\<encoded-project-path>\<session-id>.jsonl
```

This work package is pulled forward by `md/change-order-01.md` because Claude Code history is prototype-critical. The accepted prototype path is:

1. ingest real Claude Code local history;
2. search it with the accepted WP-2.1 `chronicle search`;
3. inspect a result with `chronicle open`;
4. preserve link-back metadata from CO-1.

## Source Of Truth

Read these before implementation:

- `md/master-plan.md`
- `md/change-order-01.md`
- `md/development-ledger.md`
- `md/research/RS-1-chat-history-access-findings.md`
- `md/research/RS-2-chat-self-identification-findings.md` — research input only, not a change order
- `md/agent-operating-notes.md`
- accepted source code for WP-1.3.2 OpenAI Codex extraction, WP-1.4 ingest, CO-1 schema/link-back, and WP-2.1 search/open

## Required Poetry Preflight

Before running any Poetry command, verify the virtual environment:

```powershell
poetry env info --path
```

Expected:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If it points at another project, stop and clear the inherited shell state before running install/test/lint commands. Follow `md/agent-operating-notes.md`.

## Scope

Implement:

- a concrete Claude Code extractor module, expected path:

```text
src/chat_chronicle/adapters/claude_code.py
```

- provider string:

```text
claude_code
```

- source type:

```text
local_store
```

- support for inputs that are:
  - a single Claude Code session `.jsonl` file;
  - one Claude Code project directory under `.claude\projects`;
  - the `.claude\projects` root containing multiple project directories;
- minimal `chronicle ingest` wiring so `--provider claude_code` works;
- cautious auto-detection for Claude Code paths/fixtures without misclassifying OpenAI Codex JSONL;
- synthetic fixtures and tests only;
- a short format memo in:

```text
md/research/RS-2-claude-code-format-memo.md
```

- a detailed completion report in:

```text
md/handoffs/reports/WP-3.1-completion-report.md
```

Do not implement:

- adapter base classes, protocols, registries, or shared importer abstractions;
- `collect`, scheduling, or source CRUD commands;
- `scan-local`;
- Cursor, Gemini, Copilot, or `.jsonl.zst` support;
- the product/package/CLI rename to WorkTrail;
- MCP recall or local LLM enrichment;
- real transcript fixtures or committed private data.
- logical conversation grouping across multiple Claude Code `.jsonl` files. For v1, keep the extractor session-per-file, but capture enough session ids, cwd, timestamps, `uuid`/`parentUuid`, and sidechain facts in the format memo so cross-file/thread linkage remains derivable later.

## RS-2 Live Format Facts To Act On Now

`md/research/RS-2-chat-self-identification-findings.md` is not a change order. However, the owner approved one immediate WP-3.1 addendum: the Claude Code JSONL format facts from RS-2 section 6 must be reflected in this handoff, the fixtures, the format memo, and PM validation before WP-3.1 acceptance.

The executor must account for these live-verified facts:

- `ai-title` records exist and carry the real session title. Prefer `ai-title` over synthesized titles.
- Seven observed Claude Code record types exist: `user`, `assistant`, `queue-operation`, `attachment`, `file-history-snapshot`, `system`, and `ai-title`.
- Records can carry `uuid` / `parentUuid` chains.
- `isSidechain` marks sub-agent or sidechain records.
- resumed or branched Claude Code sessions can span multiple `.jsonl` files, so one logical conversation is not necessarily one file.

Scope remains session-per-file for v1. Do not design a cross-file logical conversation merger in WP-3.1. The implementation and memo must preserve enough facts for that future linkage work.

## Mandatory Research Spike

Start by studying prior-art parsers before inspecting local data:

- Agent Sessions: `https://github.com/jazzyalex/agent-sessions`
- claude-record: `https://github.com/davidglogan/claude-record`
- codex-trace: `https://github.com/PixelPaw-Labs/codex-trace`

Capture what you learned in `md/research/RS-2-claude-code-format-memo.md`.

The memo must include:

- which files or parser functions were inspected;
- observed Claude Code record shapes and required fields;
- which record types are visible chat content versus metadata/tooling;
- how project/session identity is derived;
- timestamp handling;
- link-back handling;
- `ai-title` handling and title precedence;
- all seven observed record types listed in the RS-2 addendum;
- `uuid` / `parentUuid` threading behavior;
- `isSidechain` behavior and whether sidechain messages are included, skipped, or flagged;
- the known limitation that resumed/branched sessions can span multiple files while WP-3.1 remains session-per-file;
- known unknowns and format-drift risks.

If network access is unavailable, document that blocker in the memo and completion report, then continue from local inspection and existing RS-1 findings.

## Local Inspection And Privacy Rules

After the prior-art review, inspect the local Claude Code store read-only:

```text
%USERPROFILE%\.claude\projects
```

Rules:

- Do not commit real Claude Code transcript files.
- Do not paste private transcript content into tests, docs, reports, or chat.
- It is acceptable to report non-sensitive counts, file extensions, key names, and high-level shapes.
- Build hand-written synthetic fixtures that mimic shape, not copied or lightly sanitized private content.
- Treat these files as plaintext secrets-bearing logs.

RS-1 notes that Claude Code cleanup previously had a default 30-day horizon and was changed to `cleanupPeriodDays: 99999` on 2026-07-12. First real ingest may only see recent history.

## Extractor Requirements

The extractor should expose a concrete public function similar in shape to the accepted importers, but provider-specific where needed. Do not introduce a shared abstraction.

It must:

- parse JSONL line by line;
- tolerate malformed, unknown, or partially written lines by recording serializable errors and continuing;
- extract visible user/assistant/system/developer text where supported by the observed format;
- prefer `ai-title` records for conversation title when present;
- skip known metadata/tool bookkeeping records unless they contain user-visible transcript text;
- preserve enough ordering to reconstruct the session transcript;
- handle multiple sessions from directories;
- return normalized `Conversation` and `Message` models used by the current DB layer;
- keep parse problems as data so ingest can store them in `ingest_runs.errors_json`;
- avoid DB writes inside the extractor.

Unknown record types should be visible in errors, not fatal exceptions, unless the entire input path is unreadable or unsupported.

## Project And Link-Back Requirements

CO-1 link-back fields are part of this work package.

Populate:

- `origin_path`: resolved local `.jsonl` transcript path for each session;
- `resume_hint`: best effort `claude --resume <session-id>` when the session id can be derived from the file name or verified record shape;
- `project_id`: infer and persist project identity when possible.

Expected project behavior:

- derive project root/name from the Claude Code project directory encoding and/or verified record fields;
- add a minimal DB helper such as `get_or_create_project(...)` if needed;
- keep the extractor DB-free by returning provider-specific project hints, then assign `project_id` in the CLI ingest layer before upsert;
- if project inference is not reliable for some records, leave `project_id` null and record the limitation in the report.

`chronicle open` should display the link-back fields naturally through the accepted WP-2.1 behavior.

## CLI Ingest Wiring

Update `chronicle ingest` so these work:

```powershell
poetry run chronicle ingest <path-to-claude-code-jsonl> --provider claude_code --db-path <tmp-db>
poetry run chronicle ingest <path-to-claude-project-dir> --provider claude_code --db-path <tmp-db>
poetry run chronicle ingest <path-to-.claude-projects-root> --provider claude_code --db-path <tmp-db>
```

Auto-detection should recognize Claude Code synthetic fixtures and obvious `.claude\projects` paths. If detection is ambiguous with OpenAI Codex JSONL, fail clearly and ask for `--provider`.

Preserve existing ChatGPT, Claude export, and OpenAI Codex ingest behavior.

## Idempotency And Incremental Behavior

This package does not implement the future `collect` loop. However, repeated ingest of the same Claude Code input must be idempotent through the existing DB upsert behavior:

- no duplicate conversations;
- no duplicate messages;
- source row reuse through the accepted DB uniqueness behavior;
- updated `origin_path` / `resume_hint` should persist on re-ingest.

If content hashing or file mtime is useful inside the extractor tests, keep it local and simple. Do not create a persistent collection cache in this WP.

## Tests Required

Add focused tests for:

- parsing a single synthetic Claude Code JSONL session;
- preferring an `ai-title` record over synthesized titles;
- parsing multiple sessions from a project directory;
- parsing multiple project directories from a `.claude\projects` root fixture;
- parsing a resumed/branched logical session represented by multiple synthetic `.jsonl` files without merging those files into one v1 conversation;
- preserving or documenting `uuid` / `parentUuid` chain information in the format memo;
- handling `isSidechain` records with explicit expected behavior;
- malformed JSONL lines become serializable errors and do not stop healthy sessions;
- known non-chat record types (`queue-operation`, `attachment`, `file-history-snapshot`) are skipped or logged according to the format memo without noisy false errors;
- unknown non-chat record types are skipped or logged according to the format memo;
- metadata/tool records do not create noisy false errors;
- `origin_path` is populated;
- `resume_hint` is populated when a session id is available;
- project hints produce persisted `project_id` through CLI ingest or DB helper coverage;
- `chronicle ingest --provider claude_code` writes conversations/messages/ingest run rows;
- repeated ingest is idempotent;
- `chronicle search` can find ingested Claude Code content;
- `chronicle open` shows the ingested conversation and link-back fields;
- existing provider tests still pass.

Synthetic fixtures should live under a provider-specific test fixture directory, for example:

```text
tests/fixtures/claude_code/
```

## Acceptance Criteria

WP-3.1 is complete when:

- `claude_code.py` exists as a concrete extractor with no new adapter framework;
- the format memo exists at `md/research/RS-2-claude-code-format-memo.md`;
- `chronicle ingest` supports explicit `--provider claude_code`;
- auto-detection handles clear Claude Code paths/fixtures or fails with a clear ambiguity message;
- synthetic Claude Code fixtures round-trip into normalized conversations/messages;
- fixtures cover `ai-title`, sidechain records, and multi-file resumed/branched session cases;
- `ai-title` is preferred over title synthesis;
- repeated ingest of the same fixture creates zero duplicate conversations/messages;
- malformed or unknown records are captured as serializable parse errors, not crashes;
- CO-1 link-back fields are populated where possible;
- existing ChatGPT, Claude export, OpenAI Codex, stats, search, and open behavior does not regress;
- no real transcript, `.db`, `.sqlite`, `.zip`, or private source data is tracked by git.

## Required Validation Evidence

Include exact command output in the completion report for:

```powershell
poetry env info --path
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
```

Also include manual smoke evidence using a temporary DB:

```powershell
poetry run chronicle ingest <synthetic-claude-code-fixture> --provider claude_code --db-path <tmp-db>
poetry run chronicle stats --db-path <tmp-db>
poetry run chronicle search <known-fixture-term> --provider claude_code --db-path <tmp-db>
poetry run chronicle open <result-id> --db-path <tmp-db>
```

If real local Claude Code files are used for a private smoke test, report only counts and non-sensitive path-shape information. Do not include transcript text.

## Completion Report Requirements

Write the completion report here:

```text
md/handoffs/reports/WP-3.1-completion-report.md
```

The report must include:

- status: `ready for PM validation`, `blocked`, or `partial`;
- files changed;
- implementation summary;
- prior-art research summary and memo path;
- explicit statement that RS-2 section 6 format facts were handled;
- local inspection summary with privacy-safe details only;
- how provider/source/project/session identity is derived;
- title precedence, especially `ai-title`;
- handling of `uuid` / `parentUuid`, `isSidechain`, and multi-file resumed/branched sessions;
- link-back field behavior (`origin_path`, `resume_hint`, `project_id`);
- parser error behavior and examples using synthetic data only;
- test and lint evidence;
- manual CLI smoke evidence;
- git status summary confirming no private data, DB files, zips, or real transcripts are tracked;
- known limitations and recommended follow-ups.

Do not mark ready if the report is missing.

## Notes For The Executor

This source is Class B: useful and durable, but undocumented and version-sensitive. Prefer tolerant parsing with fail-visible errors over rigid validation.

Keep changes closely scoped. The goal is to make Claude Code local history searchable through the already accepted ingest/search/open path, not to finish source management or the full collection daemon.
