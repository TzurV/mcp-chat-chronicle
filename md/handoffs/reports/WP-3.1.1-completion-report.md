# WP-3.1.1 Completion Report — Claude Code RS-2 Format Hardening

## Status

**ready for PM validation**

WP-3.1.1 hardens the WP-3.1 Claude Code extractor against the RS-2 addendum without expanding scope beyond session-per-file ingestion.

## Files Changed

- `src/chat_chronicle/adapters/claude_code.py`
- `tests/test_claude_code.py`
- `tests/fixtures/claude_code/ai_title_precedence/session-ai-title.jsonl`
- `tests/fixtures/claude_code/rs2_records/session-rs2-records.jsonl`
- `tests/fixtures/claude_code/multi_file_same_session/branch-a.jsonl`
- `tests/fixtures/claude_code/multi_file_same_session/branch-b.jsonl`
- `md/research/RS-2-claude-code-format-memo.md`
- `md/handoffs/reports/WP-3.1-completion-report.md`
- `md/handoffs/reports/WP-3.1.1-completion-report.md`
- `md/development-ledger.md`

This continues from the existing WP-3.1 working tree, which also includes the original `claude_code` extractor, CLI wiring, project helper, and WP-3.1 synthetic fixtures.

## Changes From WP-3.1

- Changed Claude Code `provider_conv_id` from raw `sessionId` to a file-scoped id when a source path is known.
- Added synthetic fixture coverage for same-`sessionId` multi-file resumed/branched sessions.
- Added explicit tests for `ai-title` precedence and fallback title synthesis.
- Added explicit fixture coverage for the seven live-observed record types.
- Added explicit tests for `system` records, `uuid`, `parentUuid`, and `isSidechain`.
- Updated RS-2 memo and WP-3.1 report addendum.

## Identity Decision

V1 behavior is **one WorkTrail conversation per source `.jsonl` file**.

Claude Code raw `sessionId` alone is not safe as `provider_conv_id`, because two files can represent the same resumed/branched logical Claude Code session. Using only `sessionId` would allow the DB uniqueness constraint on `(provider, provider_conv_id)` to skip/update one file using another file's identity.

Final behavior:

- `provider_conv_id`: `<raw-sessionId>::<file-stem>::<12-char-source-path-hash>` when `sessionId` and source path are available.
- Fallback identity: filename-derived id, still file-scoped when a source path is available.
- `origin_path`: exact resolved source `.jsonl` file path.
- `resume_hint`: raw Claude Code session id, for example `claude --resume shared-resume-session`.

The synthetic `multi_file_same_session` fixture verifies two files sharing `sessionId = shared-resume-session` ingest as two distinct conversations with distinct `origin_path` values and no transcript loss.

## `ai-title`

Exact behavior:

- `ai-title` records are metadata, not chat messages.
- `ai-title` sets the conversation title.
- `ai-title` wins over first-user-message title synthesis, even when the user message appears before the title record.
- If `ai-title` is absent, existing title synthesis from the first visible user message still applies.

Covered by:

- `test_ai_title_wins_over_synthesized_title`
- `test_missing_ai_title_still_synthesizes_from_first_user_message`

## Seven Record Types

The WP-3.1.1 synthetic fixture covers all seven live-observed record types:

- `user`: parsed as visible user message when text is present.
- `assistant`: parsed as visible assistant message when text is present.
- `system`: parsed as visible system message when text is present.
- `queue-operation`: skipped as metadata with no parse error.
- `attachment`: skipped as metadata with no parse error.
- `file-history-snapshot`: skipped as metadata with no parse error.
- `ai-title`: parsed as title metadata, not as a message.

Covered by `test_rs2_live_observed_record_types_uuid_parent_and_sidechain_behavior`.

## `uuid` / `parentUuid`

Exact behavior:

- `uuid` is persisted as normalized `Message.provider_message_id` when available.
- `parentUuid` is currently not persisted because the accepted normalized `Message` model has no parent field.
- No schema change was introduced.
- `parentUuid` is documented in the RS-2 memo as a future logical-thread-linkage fact.

The RS-2 fixture includes `uuid` and `parentUuid` chains and verifies no false errors are emitted.

## `isSidechain`

Exact behavior:

- Sidechain records are included in the per-file transcript when they contain visible supported message text.
- `isSidechain` is not persisted as a dedicated field in v1.
- No false parse errors are emitted for sidechain records.
- This behavior is documented in the RS-2 memo.

Covered by the sidechain assistant record in `tests/fixtures/claude_code/rs2_records/session-rs2-records.jsonl`.

## Validation Evidence

### Poetry preflight

```text
> poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

### Focused Tests

```text
> poetry run pytest tests/test_claude_code.py -q
............                                                             [100%]
```

### Full Tests

```text
> poetry run pytest
........................................................................ [ 52%]
................................................................         [100%]
136 passed in 9.97s
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

## Git Status Summary

Final status:

```text
> git status --short
 M md/development-ledger.md
 M src/chat_chronicle/cli.py
 M src/chat_chronicle/db.py
 M tests/test_db.py
?? md/handoffs/WP-3.1-claude-code-extractor.md
?? md/handoffs/WP-3.1.1-claude-code-rs2-format-hardening.md
?? md/handoffs/reports/WP-3.1-completion-report.md
?? md/handoffs/reports/WP-3.1.1-completion-report.md
?? md/research/RS-2-chat-self-identification-findings.md
?? md/research/RS-2-claude-code-format-memo.md
?? md/research/RS-2-trail-kit/
?? src/chat_chronicle/adapters/claude_code.py
?? tests/fixtures/claude_code/
?? tests/test_claude_code.py
```

`rg --files -g "*.db" -g "*.sqlite" -g "*.zip" -g "*.jsonl"` found existing synthetic JSONL fixtures, new synthetic Claude Code JSONL fixtures, and pre-existing ignored `scratch/*.db` files. `git ls-files scratch\wp-1.4-evidence-cli.db scratch\wp-1.1-evidence.db` returned no tracked paths.

No private Claude Code transcript content, `.db`, `.sqlite`, `.zip`, or real transcript files were added or tracked by this work.

## Known Limitations And Follow-Ups

- `parentUuid`, `isSidechain`, and logical thread/branch grouping are documented but not persisted as dedicated schema fields.
- File-scoped `provider_conv_id` protects against silent overwrite but means moving/copying source files can produce new conversation identities.
- Cross-file logical conversation merging remains a future backlog candidate, not v1 scope.
- Sidechain visible text is included in the per-file transcript; future UX may want sidechain labeling if schema/UI scope expands.
