# WP-3.1 Validation Review — Claude Code Local Extractor

## Decision

**Accepted**, together with WP-3.1.1.

WP-3.1 delivered the concrete Claude Code extractor, CLI ingest wiring, project persistence, CO-1 link-back fields, synthetic fixtures, research memo, and CLI smoke evidence required by the handoff. WP-3.1.1 resolved the later RS-2 addendum before final acceptance.

## Validation Performed

Reviewed:

- `md/handoffs/WP-3.1-claude-code-extractor.md`
- `md/handoffs/WP-3.1.1-claude-code-rs2-format-hardening.md`
- `md/handoffs/reports/WP-3.1-completion-report.md`
- `md/handoffs/reports/WP-3.1.1-completion-report.md`
- `md/research/RS-2-claude-code-format-memo.md`
- `src/chat_chronicle/adapters/claude_code.py`
- `tests/test_claude_code.py`
- `tests/fixtures/claude_code/`

Commands run by PM validation:

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

```text
poetry run pytest tests/test_claude_code.py -q
12 passed
```

```text
poetry run pytest
136 passed
```

```text
poetry run ruff check .
All checks passed!
```

```text
poetry run chronicle --help
```

The CLI help still lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, and `open`.

## Acceptance Notes

- Extractor is concrete and provider-specific; no adapter framework was introduced.
- `chronicle ingest --provider claude_code` is wired.
- `origin_path`, `resume_hint`, and `project_id` behavior is covered.
- The RS-2 addendum is satisfied through WP-3.1.1: `ai-title`, seven live record types, `uuid`/`parentUuid`, `isSidechain`, and multi-file same-session fixtures are covered.
- Same-session multi-file input no longer silently overwrites because Claude Code `provider_conv_id` is file-scoped.
- No private Claude Code transcript content was added; JSONL fixtures are synthetic.

## Residual Risks

- File-scoped `provider_conv_id` means moving or copying a source `.jsonl` can create a new WorkTrail conversation identity. This is acceptable for v1 and documented.
- `parentUuid`, `isSidechain`, and logical thread/branch grouping are not persisted as dedicated schema fields. They remain future backlog candidates, not accepted scope.
- Real private-history performance and usefulness still need prototype smoke validation.

## Follow-Up

Proceed to commit the accepted WP-3.1/WP-3.1.1 work, then run the prototype private smoke against real Claude Code history and at least one ingested official export. Report only counts and path-shape information from private transcripts.
