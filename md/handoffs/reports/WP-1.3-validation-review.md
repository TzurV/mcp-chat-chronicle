# WP-1.3 PM Validation Review

## Decision
**Accepted.**

The completion report at `md/handoffs/reports/WP-1.3-completion-report.md` satisfies the WP-1.3 handoff. The implementation adds a concrete Claude official-export importer without introducing adapter abstraction, DB writes, public CLI ingest behavior, runtime dependencies, or real/private export data.

## Evidence Checked

| Requirement | Validation Result | Notes |
| --- | --- | --- |
| Concrete Claude importer exists | Pass | `src/chat_chronicle/adapters/claude_export.py` defines `load_conversations()` and `parse_conversations_json()`. |
| No adapter base/protocol added | Pass | Static scan found no `AdapterProtocol` or `adapters/base`; importer remains concrete. |
| Export shape verification documented | Pass | Report states no real export was available and documents assumptions from the master plan. |
| Flat `conversations.json` list parsed | Pass | Covered by synthetic fixture tests. |
| `uuid` / `name` / timestamps / `chat_messages[]` mapped | Pass | Covered by minimal, realistic, missing-optional, and malformed fixture tests. |
| Claude URLs constructed | Pass | Tests assert `https://claude.ai/chat/{uuid}`. |
| Text bodies extracted from Claude message shape | Pass | Supports block lists, plain string content, and flat text fallback. |
| Non-text/malformed content recorded without crash | Pass | Tests cover non-text blocks, malformed messages, and valid conversations surviving bad records. |
| Timestamps become UTC datetimes | Pass | Tests cover UTC `Z`, offset-aware timestamps, and invalid timestamp degradation. |
| Returns WP-1.1 normalized models | Pass | Tests assert `Conversation` output and use WP-1.1 `Message` models. |
| Synthetic fixtures only | Pass | Fixtures are hand-written JSON under `tests/fixtures/claude/`; no real export archive is tracked. |
| No DB writes or public CLI ingest behavior | Pass | Static scan found no `chat_chronicle.db` import or `sqlite3`; `cli.py` is untouched. |
| ChatGPT importer remains accepted | Pass | Full test suite passes, including WP-1.2 tests. |

## Independent Validation

```text
poetry run pytest
................................................................         [100%]
64 passed in 2.69s
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

- Search found no forbidden DB import, adapter protocol/base, network dependency, Gemini importer, Cursor importer, or Claude Code importer references in the Claude importer/tests.
- `rg --files` found no tracked export archives or DB files; an ignored local evidence DB from WP-1.1 still exists at `scratch\wp-1.1-evidence.db`.

## Scope Control

| Guardrail | Validation Result | Notes |
| --- | --- | --- |
| Did not implement DB writes | Pass | No `chat_chronicle.db` or `sqlite3` use in the importer. |
| Did not implement public CLI ingest behavior | Pass | `cli.py` remains unchanged. |
| Did not add adapter base/protocol | Pass | No shared adapter abstraction introduced. |
| Did not add Gemini/Class B importers | Pass | Only Claude importer added. |
| Did not commit real exports/private data | Pass | Synthetic JSON fixtures only. |

## PM Decisions / Follow-Ups

- **Role vocabulary:** accepted for WP-1.3 as provider-native roles. Claude `"human"` is preserved instead of being normalized to ChatGPT `"user"`. A cross-provider role normalization decision should be made before M2 search/display work.
- **Real Claude export verification:** accepted under the handoff's fallback path because no real export was available. Before or during WP-1.4, obtain a real Claude export if possible and compare it against `tests/fixtures/claude/realistic/conversations.json`.
- **Numeric timestamps:** accepted as fail-loud behavior. Numeric timestamps are rejected unless a verified Claude export proves they are used.
- **Content precedence:** accepted for now. The parser prefers structured `content[]` blocks over flat `text`; verify against a real export when available.

## Follow-Ups

- WP-1.4 CLI ingest + stats can proceed.
- WP-1.4 should persist `[error.model_dump() for error in result.errors]` into `ingest_runs.errors_json`.
- WP-1.4 should keep the Claude-shape uncertainty visible in report risks if no real export is available by then.
