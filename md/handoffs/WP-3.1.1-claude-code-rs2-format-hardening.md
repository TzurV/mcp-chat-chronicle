# WP-3.1.1 Handoff: Claude Code RS-2 Format Hardening

## Objective

Harden the already-implemented WP-3.1 Claude Code extractor against the live RS-2 format findings before PM acceptance.

This is a narrow validation-fix work package for the same execution thread that implemented WP-3.1. It does not approve any broader RS-2 backlog scope.

## Starting Point

Start from the existing WP-3.1 working tree and report:

- `src/chat_chronicle/adapters/claude_code.py`
- `tests/test_claude_code.py`
- `tests/fixtures/claude_code/`
- `md/research/RS-2-claude-code-format-memo.md`
- `md/handoffs/reports/WP-3.1-completion-report.md`
- `md/research/RS-2-chat-self-identification-findings.md`
- `md/handoffs/WP-3.1-claude-code-extractor.md`

The WP-3.1 implementation already has core ingestion, project persistence, link-back fields, synthetic fixtures, and CLI smoke evidence. Do not redo that work. Patch only what is needed to satisfy the RS-2 addendum.

## Required Poetry Preflight

Before running any Poetry command:

```powershell
poetry env info --path
```

Expected:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If Poetry resolves to another repository's virtual environment, stop and fix the shell according to `md/agent-operating-notes.md`.

## Scope

Implement or document the RS-2 Claude Code format facts that were added after the initial WP-3.1 implementation:

- `ai-title` records carry the real session title and must win over title synthesis.
- Seven live-observed record types must be handled or explicitly documented:
  - `user`
  - `assistant`
  - `queue-operation`
  - `attachment`
  - `file-history-snapshot`
  - `system`
  - `ai-title`
- records can carry `uuid` / `parentUuid` chains.
- `isSidechain` marks sub-agent/sidechain records.
- resumed or branched Claude Code sessions can span multiple `.jsonl` files.

Keep v1 scope **session-per-file**. Do not implement a cross-file logical conversation merger.

## Explicit Non-Scope

Do not implement:

- trail adapter;
- CO-2 URL parsing;
- scan-local additions;
- Cowork extractor;
- LinkedIn/post artifacts;
- cross-file logical conversation grouping;
- schema redesign for thread linkage;
- source CRUD, collection daemon, scheduler, or MCP recall.

Record broader ideas only as future backlog candidates if needed.

## Required Implementation Decisions

### Multi-file resumed/branched sessions

Add a synthetic fixture where two `.jsonl` files represent the same logical resumed/branched Claude Code session.

For v1, those files must not silently collapse into one stored conversation unless that behavior is explicitly justified and accepted. The preferred v1 behavior is:

- one WorkTrail conversation per source `.jsonl` file;
- `origin_path` identifies the exact file;
- `resume_hint` still uses the raw Claude Code session id when available;
- enough facts are preserved in the format memo for future thread linkage.

If the implementation currently uses `sessionId` alone as `provider_conv_id`, verify whether two files with the same `sessionId` overwrite/merge. If they do, fix the identity strategy for Claude Code so file-scoped v1 conversations remain distinct, for example by deriving a stable provider conversation id from `sessionId` plus file identity while keeping `resume_hint = claude --resume <raw-session-id>`.

Document the final decision in the completion report.

### `ai-title`

Add or verify a focused test proving:

- `ai-title` is parsed;
- `ai-title` wins over synthesized title;
- missing `ai-title` still falls back to existing synthesis.

### Record types

Add or verify fixture coverage for the seven live-observed record types listed above.

Expected behavior:

- `user`, `assistant`, and supported `system` content can contribute visible messages when they contain visible text.
- `queue-operation`, `attachment`, and `file-history-snapshot` skip without noisy false errors.
- `ai-title` sets title metadata and does not create a chat message.

### `uuid` / `parentUuid`

Add fixture coverage where messages contain `uuid` and `parentUuid`.

The current normalized model may not have a dedicated parent field. That is acceptable for WP-3.1.1 if:

- `uuid` remains the message id when available;
- `parentUuid` behavior is described in `md/research/RS-2-claude-code-format-memo.md`;
- the report states whether `parentUuid` is currently persisted, ignored, or only used for future derivation.

Do not invent a schema change unless a minimal change is clearly required to prevent data loss in accepted fields.

### `isSidechain`

Add fixture coverage for sidechain records.

The implementation must either:

- include sidechain visible messages in the per-file transcript with no false errors; or
- skip/flag sidechain records consistently and document why.

The chosen behavior must be explicit in tests, memo, and report.

## Documentation Updates

Update `md/research/RS-2-claude-code-format-memo.md` so it clearly records:

- all seven live-observed record types;
- `ai-title` title precedence;
- `uuid` / `parentUuid`;
- `isSidechain`;
- multi-file resumed/branched sessions;
- v1 session-per-file behavior;
- what facts are preserved now for later logical-thread linkage;
- known limitations and drift risks.

Refresh `md/handoffs/reports/WP-3.1-completion-report.md` or add a short addendum section that points to the WP-3.1.1 report.

## Tests Required

Add focused tests for:

- `ai-title` title precedence;
- all seven live-observed record types;
- `system` record handling;
- `uuid` as message id;
- `parentUuid` fixture handling/documentation;
- `isSidechain` fixture handling;
- two `.jsonl` files representing the same resumed/branched logical session without accidental silent collapse;
- existing WP-3.1 ingest/search/open behavior remains intact.

The multi-file fixture must be synthetic and must not include private transcript content.

## Required Validation Evidence

Include exact command evidence in the completion report:

```powershell
poetry env info --path
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
```

Also include focused evidence for the new tests, for example:

```powershell
poetry run pytest tests/test_claude_code.py -q
```

If CLI smoke commands are re-run, use a temporary DB outside the repo and report only synthetic fixture data.

## Completion Report

Write the completion report here:

```text
md/handoffs/reports/WP-3.1.1-completion-report.md
```

The report must include:

- status: `ready for PM validation`, `partial`, or `blocked`;
- files changed;
- what changed from WP-3.1;
- exact handling for `ai-title`;
- exact handling for all seven record types;
- exact handling for `uuid` / `parentUuid`;
- exact handling for `isSidechain`;
- exact behavior for multi-file resumed/branched session fixtures;
- whether Claude Code `provider_conv_id` changed and why;
- validation evidence;
- git status summary confirming no private data, DBs, zips, or real transcripts are tracked;
- known limitations and follow-ups.

Do not mark ready if the report does not answer the RS-2 addendum points directly.

## Acceptance Criteria

WP-3.1.1 is complete when:

- RS-2 addendum facts are reflected in fixtures, tests, memo, and report;
- no private Claude Code content is committed;
- session-per-file v1 behavior is explicit and tested;
- multi-file same/resumed session input does not silently lose or overwrite a source file's transcript;
- `ai-title` title precedence is tested;
- sidechain behavior is explicit and tested;
- all seven live-observed record types are covered;
- full test suite and Ruff pass;
- existing accepted provider behavior does not regress.
