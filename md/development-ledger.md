# Chat Chronicle Development Ledger

This ledger records PM-level progress against `md/master-plan.md`. The master plan remains the source of truth for scope and acceptance criteria; this file tracks execution state, handoffs, validation decisions, risks, and next actions.

## Current Status

| Field | Status |
| --- | --- |
| Date | 2026-07-10 |
| Phase | M1 in progress |
| Last accepted work package | WP-0.1 Repo bootstrap |
| Current milestone state | M0 complete; WP-1.1, WP-1.2, and WP-1.3 accepted; M1 CLI ingest next |
| Next action | Execute WP-1.4 CLI ingest + stats |
| Current branch | `main` |
| Last known commit | `735613f Bootstrap project scaffold and PM handoff` |

## Work Package Ledger

| WP | Name | State | Handoff | Completion Report | PM Validation | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| WP-0.1 | Repo bootstrap | Accepted | `md/handoffs/WP-0.1-repo-bootstrap.md` | `md/handoffs/reports/WP-0.1-completion-report.md` | `md/handoffs/reports/WP-0.1-validation-review.md` | Scaffold, CLI stubs, tests, CI, lint, license, and PM artifacts completed. |
| WP-1.1 | Normalized models + DB layer | Accepted | `md/handoffs/WP-1.1-normalized-models-db-layer.md` | `md/handoffs/reports/WP-1.1-completion-report.md` | `md/handoffs/reports/WP-1.1-validation-review.md` | Schema, models, idempotent upserts, ingest run logging, FTS rebuild/search, and project-local DB path accepted. |
| WP-1.2 | ChatGPT export importer | Accepted | `md/handoffs/WP-1.2-chatgpt-export-importer.md` | `md/handoffs/reports/WP-1.2-completion-report.md` | `md/handoffs/reports/WP-1.2-validation-review.md` | Concrete importer accepted with synthetic fixtures; no adapter base introduced. |
| WP-1.3 | Claude export importer | Accepted | `md/handoffs/WP-1.3-claude-export-importer.md` | `md/handoffs/reports/WP-1.3-completion-report.md` | `md/handoffs/reports/WP-1.3-validation-review.md` | Concrete importer accepted with synthetic fixtures; no adapter base introduced. Real export verification remains a follow-up. |
| WP-1.4 | CLI ingest + stats | Handoff ready | `md/handoffs/WP-1.4-cli-ingest-stats.md` | `md/handoffs/reports/WP-1.4-completion-report.md` | Pending | Depends on accepted WP-1.2 and WP-1.3 importers. |
| WP-1.5 | scan-local read-only discovery | Not started | Pending | Pending | Pending | Can be planned independently, but should not import or parse source contents. |
| WP-1.6 | collect + folder workflow + scheduling docs | Blocked by dependencies | Pending | Pending | Pending | Depends on source and ingest flow. |

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
| First remote CI run | PM / executor after push | Open | WP-0.1 was validated locally; GitHub Actions matrix has not yet run remotely. |
| Poetry `VIRTUAL_ENV` hazard | All executor chats | Mitigated procedurally | Documented in `md/agent-operating-notes.md`; add the preflight to each future handoff. |
| Sandbox launcher failures | PM validation chats | Mitigated procedurally | Use direct `rg`/`Get-Content -Raw`; retry key validation commands with escalation only when the sandbox launcher fails. |

## Next Action

Send `md/handoffs/WP-1.4-cli-ingest-stats.md` to the executor chat. The completion report location is:

```text
md/handoffs/reports/WP-1.4-completion-report.md
```

The implementation must preserve these constraints:

- wire accepted ChatGPT and Claude importers into `chronicle ingest`;
- record source rows and `ingest_runs`;
- preserve idempotent `upsert_conversation()` behavior;
- store importer parse errors in `errors_json` without aborting valid conversations;
- do not introduce `adapters/base.py` or `AdapterProtocol`;
- use only synthetic fixtures.
