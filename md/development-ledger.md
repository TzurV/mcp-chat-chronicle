# WorkTrail Development Ledger

This ledger records PM-level progress against `md/master-plan.md` and the approved amendment `md/change-order-01.md`. The master plan plus change order remain the source of truth for scope and acceptance criteria; this file tracks execution state, handoffs, validation decisions, risks, and next actions.

## Current Status

| Field | Status |
| --- | --- |
| Date | 2026-07-13 |
| Phase | M1 in progress |
| Last accepted work package | WP-2.1 FTS5 search + open |
| Current milestone state | M0 complete; WP-1.1 through WP-2.1 accepted; WP-3.1 Claude Code extractor is next |
| Next action | Write the WP-3.1 Claude Code extractor handoff |
| Current branch | `main` |
| Last known commit | `adaf435 Add schema v2 link-back migration` |

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
| CO-1 | Schema migration + link-back touch-ups | Accepted | `md/handoffs/CO-1-schema-link-back-migration.md` | `md/handoffs/reports/CO-1-completion-report.md` | `md/handoffs/reports/CO-1-validation-review.md` | Schema v2 accepted with `projects`, `origin_path`, `resume_hint`, `manual_entry`, link-back persistence, and source uniqueness hardening. |
| WP-2.1 | FTS5 search + open | Accepted | `md/handoffs/WP-2.1-fts-search-open.md` | `md/handoffs/reports/WP-2.1-completion-report.md` | `md/handoffs/reports/WP-2.1-validation-review.md` | Search/open accepted with FTS5 ranking, filters, snippets, URL open, and local transcript link-back behavior. |
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
| CO-1 schema migration risk | CO-1 executor | Mitigated | Schema v2 migration accepted; source uniqueness now enforced by a DB-level partial unique index. |
| WP-2.1 real-archive performance | Prototype validation | Open | Synthetic performance smoke passed on 350 conversations; master-plan p95 target on a larger real archive remains to be measured during prototype validation. |
| Rename to WorkTrail | Release polish / pre-public | Open | Product name is WorkTrail; target repo/PyPI `worktrail-ai`, CLI `worktrail`. Rename before first public push. |

## Source And Export Observations

| Item | Status | Notes |
| --- | --- | --- |
| ChatGPT official export | Pending real-file verification | User requested the export through the web ChatGPT UI and is waiting for the confirmation email. Re-run the direct ChatGPT parser check once the ZIP is available. |
| Claude official export | Observed | Claude export UX allows selecting a date range, which is useful for smaller validation exports. |
| Source listing utility | Already planned | WP-1.4 `stats` must show per-source summaries after ingest. A dedicated source inventory command belongs to WP-1.6 source management (`source add/list/disable`) rather than expanding WP-1.4. |

## Next Action

Write the WP-3.1 Claude Code extractor handoff.

The WP-3.1 handoff must:

- start with the required research spike over Agent Sessions, claude-record, and codex-trace;
- inspect local Claude Code storage only after the prior-art review;
- use synthetic fixtures only;
- populate CO-1 link-back fields, especially `origin_path` and best-effort `resume_hint`;
- preserve accepted ingest/search/open behavior.
