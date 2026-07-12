# WorkTrail Development Ledger

This ledger records PM-level progress against `md/master-plan.md` and the approved amendment `md/change-order-01.md`. The master plan plus change order remain the source of truth for scope and acceptance criteria; this file tracks execution state, handoffs, validation decisions, risks, and next actions.

## Current Status

| Field | Status |
| --- | --- |
| Date | 2026-07-12 |
| Phase | M1 in progress |
| Last accepted work package | WP-1.4 CLI ingest + stats |
| Current milestone state | M0 complete; WP-1.1 through WP-1.4 accepted; Change Order 01 applied to plan; CO-1 schema migration + link-back touch-ups is next |
| Next action | Write and execute the CO-1 schema migration + link-back touch-up handoff before WP-2.1 |
| Current branch | `main` |
| Last known commit | `c3167c3 Add OpenAI Codex local extractor` |

## Work Package Ledger

| WP | Name | State | Handoff | Completion Report | PM Validation | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| WP-0.1 | Repo bootstrap | Accepted | `md/handoffs/WP-0.1-repo-bootstrap.md` | `md/handoffs/reports/WP-0.1-completion-report.md` | `md/handoffs/reports/WP-0.1-validation-review.md` | Scaffold, CLI stubs, tests, CI, lint, license, and PM artifacts completed. |
| WP-1.1 | Normalized models + DB layer | Accepted | `md/handoffs/WP-1.1-normalized-models-db-layer.md` | `md/handoffs/reports/WP-1.1-completion-report.md` | `md/handoffs/reports/WP-1.1-validation-review.md` | Schema, models, idempotent upserts, ingest run logging, FTS rebuild/search, and project-local DB path accepted. |
| WP-1.2 | ChatGPT export importer | Accepted | `md/handoffs/WP-1.2-chatgpt-export-importer.md` | `md/handoffs/reports/WP-1.2-completion-report.md` | `md/handoffs/reports/WP-1.2-validation-review.md` | Concrete importer accepted with synthetic fixtures; no adapter base introduced. |
| WP-1.3 | Claude export importer | Accepted | `md/handoffs/WP-1.3-claude-export-importer.md` | `md/handoffs/reports/WP-1.3-completion-report.md` | `md/handoffs/reports/WP-1.3-validation-review.md` | Concrete importer accepted with synthetic fixtures; no adapter base introduced. Real export verification remains a follow-up. |
| WP-1.3.1 | Claude real export content-block correction | Accepted | `md/handoffs/WP-1.3.1-claude-real-export-content-blocks.md` | `md/handoffs/reports/WP-1.3.1-completion-report.md` | `md/handoffs/reports/WP-1.3.1-validation-review.md` | Known Claude metadata blocks (`thinking`, `tool_use`, `tool_result`) now skip without noisy parse errors. |
| WP-1.3.2 | OpenAI Codex local extractor | Accepted | `md/handoffs/WP-1.3.2-openai-codex-local-extractor.md` | `md/handoffs/reports/WP-1.3.2-completion-report.md` | `md/handoffs/reports/WP-1.3.2-validation-review.md` | Concrete Class B extractor accepted for local Codex JSONL sessions. |
| WP-1.4 | CLI ingest + stats | Accepted | `md/handoffs/WP-1.4-cli-ingest-stats.md` | `md/handoffs/reports/WP-1.4-completion-report.md` | `md/handoffs/reports/WP-1.4-validation-review.md` | `chronicle ingest` and `chronicle stats` accepted for ChatGPT, Claude, and OpenAI Codex sources. |
| CO-1 | Schema migration + link-back touch-ups | Planned | Pending | Pending | Pending | Inserted by `md/change-order-01.md`; must land after WP-1.4 and before WP-2.1. Adds `projects`, `origin_path`, `resume_hint`, `manual_entry`, and title/link-back guarantees. |
| WP-2.1 | FTS5 search + open | Planned | Pending | Pending | Pending | Must use CO-1 link-back behavior: web opens URL; CLI/local shows transcript plus `origin_path` and `resume_hint`. |
| WP-3.1 | Claude Code extractor | Pulled forward | Pending | Pending | Pending | Prototype-critical per CO-01. Research spike must read Agent Sessions, claude-record, and codex-trace before local inspection/fixtures. |
| Prototype | Real-history search demo | Planned | Pending | Pending | Pending | Search real Claude Code history plus at least one ingested export end-to-end. |
| WP-1.6 | collect + folder workflow + scheduling docs | Deferred until after prototype | Pending | Pending | Pending | Depends on source and ingest flow; no daemon. |
| WP-1.5 | scan-local read-only discovery | Not on prototype path | Pending | Pending | Pending | Can be planned independently, but should not import or parse source contents. |

## Accepted Evidence Snapshot

WP-0.1 was accepted based on:

- `poetry run pytest`: `4 passed`.
- `poetry run chronicle --help`: listed `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, and `open`.
- `poetry run ruff check .`: passed.
- CI workflow exists for Windows and Ubuntu on Python 3.11 and 3.12.
- No DB schema, real importers, search implementation, adapter base/protocol, real chat data, or exports were introduced.

## Operating Notes For Future Handoffs

Every future handoff that involves Poetry must reference `md/agent-operating-notes.md` and require this preflight before install/test/lint commands:

```powershell
poetry env info --path
```

The expected path is:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If Poetry reports another project environment, the executor must stop and fix the shell before running any Poetry command.

## Open Risks And Follow-Ups

| Item | Owner | Status | Notes |
| --- | --- | --- | --- |
| First remote CI run | PM / executor after push | Open | Local validation has passed for accepted WPs; GitHub Actions matrix has not yet run remotely. |
| Poetry `VIRTUAL_ENV` hazard | All executor chats | Mitigated procedurally | Documented in `md/agent-operating-notes.md`; add the preflight to each future handoff. |
| Sandbox launcher failures | PM validation chats | Mitigated procedurally | Use direct `rg`/`Get-Content -Raw`; retry key validation commands with escalation only when the sandbox launcher fails. |
| Claude real export metadata blocks | WP-1.3.1 executor | Mitigated | Known `thinking`, `tool_use`, and `tool_result` blocks now skip without noisy parser errors. Future benign block types should be added with evidence and synthetic tests. |
| OpenAI Codex local format drift | WP-1.3.2 executor | Mitigated procedurally | Codex local JSONL is undocumented Class B storage. Accepted extractor is tolerant, synthetic-fixture covered, and fail-visible on malformed/unknown records. |
| CO-1 schema migration risk | CO-1 executor | Open | Existing DBs must migrate forward cleanly; accepted adapters need link-back/title verification without broad refactors. Consider enforcing source uniqueness while the schema is being migrated. |
| Rename to WorkTrail | Release polish / pre-public | Open | Product name is WorkTrail; target repo/PyPI `worktrail-ai`, CLI `worktrail`. Rename before first public push. |

## Source And Export Observations

| Item | Status | Notes |
| --- | --- | --- |
| ChatGPT official export | Pending real-file verification | User requested the export through the web ChatGPT UI and is waiting for the confirmation email. Re-run the direct ChatGPT parser check once the ZIP is available. |
| Claude official export | Observed | Claude export UX allows selecting a date range, which is useful for smaller validation exports. |
| Source listing utility | Already planned | WP-1.4 `stats` must show per-source summaries after ingest. A dedicated source inventory command belongs to WP-1.6 source management (`source add/list/disable`) rather than expanding WP-1.4. |

## Next Action

Write the CO-1 schema migration + link-back touch-up handoff before starting WP-2.1 search/open.

The CO-1 handoff must preserve the accepted WP-1.4 CLI behavior while adding the schema/link-back changes from `md/change-order-01.md`:

- migrate existing DBs forward cleanly;
- add `projects`;
- add `conversations.project_id`, `origin_path`, and `resume_hint`;
- extend `sources.source_type` with `manual_entry`;
- verify all accepted adapters preserve useful titles and link-back fields;
- keep `chronicle ingest` and `chronicle stats` passing for ChatGPT, Claude, and OpenAI Codex.
