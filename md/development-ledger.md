# WorkTrail Development Ledger

This ledger records PM-level progress against `md/master-plan.md` and the approved amendment `md/change-order-01.md`. The master plan plus change order remain the source of truth for scope and acceptance criteria; this file tracks execution state, handoffs, validation decisions, risks, and next actions.

## Current Status

| Field | Status |
| --- | --- |
| Date | 2026-07-14 |
| Phase | M1 in progress |
| Last accepted work package | WP-2.3.2 search FTS special-character escaping |
| Current milestone state | M0 complete; WP-1.1 through WP-3.1.1 plus WP-1.2.1, WP-1.3.3, WP-1.4.1, WP-1.5, WP-1.6, WP-2.2, WP-2.3, WP-2.3.1, and WP-2.3.2 accepted |
| Next action | Resume prototype owner smoke across `init`, `scan-local`, `collect`, `stats`, `recent`, `search`, and `open`; then decide whether to schedule MCP recall, Cursor extractor, source-management polish, or release/rename preparation |
| Current branch | `main` |
| Last known commit | See `git log -1 --oneline` for the current repository head |

## Work Package Ledger

| WP | Name | State | Handoff | Completion Report | PM Validation | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| WP-0.1 | Repo bootstrap | Accepted | `md/handoffs/WP-0.1-repo-bootstrap.md` | `md/handoffs/reports/WP-0.1-completion-report.md` | `md/handoffs/reports/WP-0.1-validation-review.md` | Scaffold, CLI stubs, tests, CI, lint, license, and PM artifacts completed. |
| WP-1.1 | Normalized models + DB layer | Accepted | `md/handoffs/WP-1.1-normalized-models-db-layer.md` | `md/handoffs/reports/WP-1.1-completion-report.md` | `md/handoffs/reports/WP-1.1-validation-review.md` | Schema, models, idempotent upserts, ingest run logging, FTS rebuild/search, and project-local DB path accepted. |
| WP-1.2 | ChatGPT export importer | Accepted | `md/handoffs/WP-1.2-chatgpt-export-importer.md` | `md/handoffs/reports/WP-1.2-completion-report.md` | `md/handoffs/reports/WP-1.2-validation-review.md` | Concrete importer accepted with synthetic fixtures; no adapter base introduced. |
| WP-1.2.1 | OpenAI split export compatibility | Accepted | `md/handoffs/WP-1.2.1-openai-split-export-compatibility.md` | `md/handoffs/reports/WP-1.2.1-completion-report.md` | `md/handoffs/reports/WP-1.2.1-validation-review.md` | Current OpenAI official exports with `conversations-*.json` ingest directly; real owner ZIP smoke accepted with 422 conversations and 5,166 messages. |
| WP-1.3 | Claude export importer | Accepted | `md/handoffs/WP-1.3-claude-export-importer.md` | `md/handoffs/reports/WP-1.3-completion-report.md` | `md/handoffs/reports/WP-1.3-validation-review.md` | Concrete importer accepted with synthetic fixtures; no adapter base introduced. Real export verification remains a follow-up. |
| WP-1.3.1 | Claude real export content-block correction | Accepted | `md/handoffs/WP-1.3.1-claude-real-export-content-blocks.md` | `md/handoffs/reports/WP-1.3.1-completion-report.md` | `md/handoffs/reports/WP-1.3.1-validation-review.md` | Known Claude metadata blocks (`thinking`, `tool_use`, `tool_result`) now skip without noisy parse errors. |
| WP-1.3.2 | OpenAI Codex local extractor | Accepted | `md/handoffs/WP-1.3.2-openai-codex-local-extractor.md` | `md/handoffs/reports/WP-1.3.2-completion-report.md` | `md/handoffs/reports/WP-1.3.2-validation-review.md` | Concrete Class B extractor accepted for local Codex JSONL sessions. |
| WP-1.3.3 | Claude export project metadata linking | Accepted | `md/handoffs/WP-1.3.3-claude-project-metadata-linking.md` | `md/handoffs/reports/WP-1.3.3-completion-report.md` | `md/handoffs/reports/WP-1.3.3-validation-review.md` | Project metadata is parsed and linked/searchable when the export provides exact project UUID references. Owner real export has 30 project rows, including `CAR GUI`, but no reliable conversation project key, so no guessed links are created. |
| WP-1.4 | CLI ingest + stats | Accepted | `md/handoffs/WP-1.4-cli-ingest-stats.md` | `md/handoffs/reports/WP-1.4-completion-report.md` | `md/handoffs/reports/WP-1.4-validation-review.md` | `chronicle ingest` and `chronicle stats` accepted for ChatGPT, Claude, and OpenAI Codex sources. |
| WP-1.4.1 | Directory ingest sweep | Accepted | `md/handoffs/WP-1.4.1-directory-ingest-sweep.md` | `md/handoffs/reports/WP-1.4.1-completion-report.md` | `md/handoffs/reports/WP-1.4.1-validation-review.md` | Adds parent-folder ingestion to `chronicle ingest <directory>` while preserving existing single-source directory behavior for `.codex`, `.claude\projects`, and provider export directories. |
| CO-1 | Schema migration + link-back touch-ups | Accepted | `md/handoffs/CO-1-schema-link-back-migration.md` | `md/handoffs/reports/CO-1-completion-report.md` | `md/handoffs/reports/CO-1-validation-review.md` | Schema v2 accepted with `projects`, `origin_path`, `resume_hint`, `manual_entry`, link-back persistence, and source uniqueness hardening. |
| WP-2.1 | FTS5 search + open | Accepted | `md/handoffs/WP-2.1-fts-search-open.md` | `md/handoffs/reports/WP-2.1-completion-report.md` | `md/handoffs/reports/WP-2.1-validation-review.md` | Search/open accepted with FTS5 ranking, filters, snippets, URL open, and local transcript link-back behavior. |
| WP-2.2 | Recent active chats CLI | Accepted | `md/handoffs/WP-2.2-recent-active-chats-cli.md` | `md/handoffs/reports/WP-2.2-completion-report.md` | `md/handoffs/reports/WP-2.2-validation-review.md` | Adds accepted `chronicle recent -n <N>` sorted by last activity date with provider/date filters and ID-Date-Provider-Title-URL table. Post-acceptance polish removes duplicate plain rows and adds a default-limit hint when `-n/--limit` is omitted. |
| WP-2.3 | Search phrase mode + query guidance | Accepted | `md/handoffs/WP-2.3-search-phrase-query-guidance.md` | `md/handoffs/reports/WP-2.3-completion-report.md` | `md/handoffs/reports/WP-2.3-validation-review.md` | Accepted explicit `--phrase` mode and guidance for noisy multi-word broad-token searches. Private DB smoke returned conversation `673`; copied-DB Codex idempotency check did not duplicate records. |
| WP-2.3.1 | Search result UX polish | Accepted | `md/handoffs/WP-2.3.1-search-result-ux-polish.md` | `md/handoffs/reports/WP-2.3.1-completion-report.md` | `md/handoffs/reports/WP-2.3.1-validation-review.md` | Accepted phrase ordering by title match, newest activity, then id descending; duplicate default `result ...` rows removed while broad BM25 search and query guidance remain intact. |
| WP-2.3.2 | Search FTS special-character escaping | Accepted | `md/handoffs/WP-2.3.2-search-fts-special-character-escaping.md` | `md/handoffs/reports/WP-2.3.2-completion-report.md` | `md/handoffs/reports/WP-2.3.2-validation-review.md` | Default broad search now treats ordinary punctuation as safe user text. Owner smoke command `chronicle search "scan-local"` no longer fails with `Invalid search query: no such column: local`; `--phrase` remains exact. |
| WP-3.1 | Claude Code extractor | Accepted | `md/handoffs/WP-3.1-claude-code-extractor.md` | `md/handoffs/reports/WP-3.1-completion-report.md` | `md/handoffs/reports/WP-3.1-validation-review.md` | Accepted with WP-3.1.1 addendum. Concrete `claude_code` extractor, ingest wiring, project/link-back fields, synthetic fixtures, memo, and CLI smoke complete. |
| WP-3.1.1 | Claude Code RS-2 format hardening | Accepted | `md/handoffs/WP-3.1.1-claude-code-rs2-format-hardening.md` | `md/handoffs/reports/WP-3.1.1-completion-report.md` | `md/handoffs/reports/WP-3.1.1-validation-review.md` | File-scoped Claude Code identity, `ai-title`, seven record types, `uuid`/`parentUuid`, sidechain, and same-session multi-file fixtures accepted. No broader RS-2 backlog scope approved. |
| Prototype | Real-history search demo | Planned | Pending | Pending | Pending | Search real Claude Code history plus at least one ingested export end-to-end. |
| WP-1.5 | scan-local source inventory | Accepted | `md/handoffs/WP-1.5-scan-local-source-inventory.md` | `md/handoffs/reports/WP-1.5-completion-report.md` | `md/handoffs/reports/WP-1.5-validation-review.md` | Read-only inventory accepted for configured/default histories: exports root, OpenAI/Claude export folders, OpenAI Codex local store, Claude Code projects, and planned Cursor/Copilot paths. No DB writes or full transcript parsing. |
| WP-1.6 | config defaults + collect workflow + scheduling docs | Accepted | `md/handoffs/WP-1.6-config-defaults-collect-workflow.md` | `md/handoffs/reports/WP-1.6-completion-report.md` | `md/handoffs/reports/WP-1.6-validation-review.md` | Accepted after rework: config-aware DB precedence applies to all DB-opening commands, `chronicle init`/`collect` are functional, YAML defaults and engine-interest settings are present, and README includes optional Task Scheduler docs. |

## Research Artifact Ledger

| ID | Name | State | Files | Notes |
| --- | --- | --- | --- | --- |
| RS-1 | Chat-history access methods on Windows 11 | Recorded | `md/research/RS-1-chat-history-access-task.md`; `md/research/RS-1-chat-history-access-findings.md` | Captures official exports, Class B local stores, Class C cache caveats, automation ceilings, Claude Code retention status, and owner retrieval checklist. Feeds WP-3.1, scan-local planning, Codex `.jsonl.zst` follow-up, and possible Copilot CSV backlog work. |
| RS-2 | Claude Code/session self-identification research | Recorded | `md/research/RS-2-chat-self-identification-findings.md`; `md/research/RS-2-claude-code-format-memo.md`; `md/research/RS-2-trail-kit/` | Chat self-identification findings are research input only, not a change order. One immediate addendum applies to WP-3.1: `ai-title`, seven record types, `uuid`/`parentUuid`, `isSidechain`, and multi-file resumed/branched session cases must be reflected in fixtures, memo, and validation. |

## Proposed Backlog Candidates

These are not approved scope. They are recorded from RS-2 for future change-order consideration only.

| Candidate | Source | Status | Notes |
| --- | --- | --- | --- |
| Thread linkage across runtime sessions | RS-2 | Proposed only | Group multiple runtime/session files into one logical conversation when reliable join keys exist. No WP-3.1 schema or merger change approved. |
| Trail adapter | RS-2 | Proposed only | Ingest `.worktrail/trail/` and global trail drop-box records after prototype if approved. |
| CO-2 URL parsing clarification | RS-2 | Proposed only | Use parsed ChatGPT `/c/<id>` and Claude `/chat/<uuid>` IDs as join keys if CO-2 is scheduled. |
| scan-local probe additions | RS-2 | Proposed only | Possible future probes for Cowork local stores and Codex app rollout paths. |
| Cowork extractor | RS-2 | Proposed only | Class B candidate pending future approval. |
| LinkedIn post candidate | RS-2 | Proposed only | Possible post on six-engine self-identification survey; no publishing scope approved. |
| OpenAI Codex local app deep-link | Prototype smoke | Proposed only | `chronicle open <id>` renders a local transcript from JSONL, but there is no verified deep-link/resume behavior that opens the original Codex app chat like ChatGPT web URLs. |
| Config-driven collection workflow | Owner discussion | Approved for WP-1.5/WP-1.6 planning | Add YAML defaults, explicit init, source inventory, and one-line collect. This is orchestration over accepted adapters, not new parsing scope. |
| History download helper | Owner discussion | Proposed only | Future tool to help download histories from chat providers when supported by documented/exportable flows or safe provider-specific automation. Config YAML should record which engines the user uses or wants supported, but download automation is not part of WP-1.5/WP-1.6 unless explicitly scheduled. |

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
| Claude standalone project metadata | WP-1.3.3 / future schema follow-up | Known limitation | Real Claude exports may include `projects/*.json` rows with no reliable conversation reference. Project rows are stored, but search only returns conversations linked by exact project UUID references. |
| WP-2.1 real-archive performance | Prototype validation | Open | Synthetic performance smoke passed on 350 conversations; master-plan p95 target on a larger real archive remains to be measured during prototype validation. |
| Default FTS special-character handling | WP-2.3.2 executor | Mitigated | Default broad search now sanitizes user text before FTS5 `MATCH`; `scan-local` returns results instead of parser errors while `--phrase` remains exact. |
| Rename to WorkTrail | Release polish / pre-public | Open | Product name is WorkTrail; target repo/PyPI `worktrail-ai`, CLI `worktrail`. Rename before first public push. |

## Source And Export Observations

| Item | Status | Notes |
| --- | --- | --- |
| ChatGPT/OpenAI official export | Received and compatibility accepted | Owner ZIP is under `exports/openai` and uses the current split layout (`conversations-000.json` ... `conversations-004.json`) with 422 records. WP-1.2.1 accepted direct ingest and auto-detection; PM smoke produced 422 conversations and 5,166 messages with 92 non-text part warnings. |
| Claude official export | Ingested; project metadata limitation characterized | Claude provider has 13 conversations in the repo-local DB. WP-1.3.3 parses 30 project metadata rows, including `CAR GUI`, and links/searches project names only when exact project UUID references exist. The owner real export has no project-like conversation keys, so `CAR GUI` cannot safely return Claude conversations without guessing. |
| Research records | Recorded | `md/research/` now holds research-spike records for history data retrieval methods and current source-access status. |
| Source listing utility | Accepted as WP-1.5 | `scan-local` lists available configured/default histories before ingest using read-only checks. `stats` continues to list already-ingested sources. |
| Config defaults | Accepted as WP-1.6 | YAML config defines `.chronicle/chronicle.db`, `exports`, `exports/openai`, `exports/claude`, `%USERPROFILE%\.codex`, and `%USERPROFILE%\.claude\projects`. Installation does not mutate folders; explicit `chronicle init` creates directories/config. |
| Engine interest settings | Accepted as WP-1.6 | Config YAML records which engines/sources the user uses or wants support for. This drives scan/help/collect defaults, not parser behavior. |
| One-line loader | Accepted as WP-1.6 | `chronicle collect` ingests enabled local stores and supported sources under the configured exports root with idempotent reruns. |

## Next Action

Resume owner smoke:

```powershell
poetry run chronicle init
poetry run chronicle scan-local
poetry run chronicle collect
poetry run chronicle stats
poetry run chronicle recent -n 10
poetry run chronicle search "scan-local"
poetry run chronicle search --phrase "YOU are the MANAGER"
```

After smoke, choose the next planning track: MCP recall, Cursor extractor, source-management polish, or release/rename preparation.
