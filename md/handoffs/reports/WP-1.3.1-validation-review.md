# WP-1.3.1 PM Validation Review

## Decision
**Accepted.**

The completion report at `md/handoffs/reports/WP-1.3.1-completion-report.md` satisfies the WP-1.3.1 handoff. The implementation narrowly corrects Claude content-block parsing so expected real-export metadata blocks no longer pollute parse errors, while malformed and unknown blocks remain visible.

## Evidence Checked

| Requirement | Validation Result | Notes |
| --- | --- | --- |
| Known metadata blocks skipped without parse errors | Pass | `_KNOWN_METADATA_BLOCK_TYPES` covers `thinking`, `tool_use`, and `tool_result`; tests assert no per-message errors for text plus metadata. |
| Text extraction from `content[]` preserved | Pass | Existing and new tests assert exact text bodies and joined text blocks. |
| Flat `text` fallback preserved | Pass | Existing missing-optional tests still pass. |
| Unknown/malformed non-text content still records errors | Pass | Tests cover unknown `image` block and invalid non-dict block. |
| Metadata-only messages skipped without noisy errors | Pass | Test asserts metadata-only message is omitted and records no parse errors. |
| Synthetic fixture covers real export block shape | Pass | `tests/fixtures/claude/real_blocks/conversations.json` is synthetic and includes text, thinking, tool use, tool result, unknown, and invalid blocks. |
| No private export data committed | Pass | Status and static scan found no real export archive, DB file, private export path, or private conversation titles in new files. |
| No DB/CLI/provider detection behavior added | Pass | Change is limited to Claude parser and tests; `cli.py` and DB behavior are untouched. |
| No adapter base/protocol added | Pass | No `adapters/base.py` or `AdapterProtocol` introduced. |
| Claude roles not normalized | Pass | Role handling is untouched; provider-native roles remain accepted. |

## Independent Validation

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

```text
poetry run pytest
......................................................................   [100%]
70 passed in 2.26s
```

```text
poetry run ruff check .
All checks passed!
```

```text
poetry run chronicle --help
```

Result: help output still lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, and `open`.

Static checks performed:

- `git status --short` shows only PM docs, Claude parser/tests, the synthetic real-block fixture, and WP-1.3.1 report artifacts changed.
- `git ls-files` shows no tracked export archive or DB file.
- Search found no private real-export filename/path or private conversation titles from the manual Claude export evidence in source/tests/new handoff content.

## Scope Control

| Guardrail | Validation Result | Notes |
| --- | --- | --- |
| Did not implement CLI ingest/stats | Pass | `cli.py` unchanged. |
| Did not add DB writes | Pass | No new DB imports or writes in the Claude importer. |
| Did not add provider detection | Pass | No detection logic added. |
| Did not add adapter base/protocol | Pass | Importer remains concrete. |
| Did not normalize Claude roles | Pass | Existing role extraction is unchanged. |
| Did not commit real exports/private data or DB files | Pass | Synthetic fixture only. |

## PM Decision

WP-1.3.1 is accepted. WP-1.4 CLI ingest + stats is now unblocked from the parser side and should use the corrected Claude importer.

## Follow-Ups

- WP-1.4 should keep persisting importer errors into `ingest_runs.errors_json`; after this fix, those errors should represent true anomalies rather than expected Claude metadata.
- Future benign Claude content block types should be added deliberately only after real-export evidence, with synthetic fixture coverage.
