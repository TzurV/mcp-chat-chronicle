# WorkTrail Development Ledger

This ledger records PM-level progress against `md/master-plan.md` and the approved amendment `md/change-order-01.md`. The master plan plus change order remain the source of truth for scope and acceptance criteria; this file tracks execution state, handoffs, validation decisions, risks, and next actions.

## Current Status

| Field | Status |
| --- | --- |
| Date | 2026-07-20 |
| Phase | Post-v0.1.0 AI development corpus and evaluation planning |
| Last accepted delivery | WP-5.2A1 Llama 3.2 1B LM Studio evaluation-floor integration |
| Current milestone state | M0/M1/M2 core and real-history prototype accepted; Chat Chronicle v0.1.0 is public; WP-5.1 through WP-5.1.4 development foundations, the frozen 30-conversation/120-reference private corpus, and WP-5.2A1 evaluation-floor integration are accepted; split candidate generation and local Gemini-judged scoring remain next |
| Next action | Write and execute WP-5.2B1: generate the 120 Llama floor cases, produce a portable hashed candidate package, then score it locally with deterministic metrics and configurable `gemini-2.5-flash`; remote machine and later independent evaluation-set design remain TBD |
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
| WP-1.3.3 | Claude export project metadata linking | Accepted | `md/handoffs/WP-1.3.3-claude-project-metadata-linking.md` | `md/handoffs/reports/WP-1.3.3-completion-report.md` | `md/handoffs/reports/WP-1.3.3-validation-review.md` | Project metadata is parsed and linked/searchable when the export provides exact project UUID references. Owner real export has 30 project rows, including a private project name omitted here, but no reliable conversation project key, so no guessed links are created. |
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
| Prototype | Real-history search demo | Accepted by owner smoke | N/A | Owner CLI evidence in PM thread | N/A | Real ChatGPT, Claude, OpenAI Codex, and Claude Code histories are present in the private repo-local DB. Stats, recent, broad/phrase search, ChatGPT URL open, and local Codex transcript rendering were exercised successfully; no private data is tracked. |
| WP-1.5 | scan-local source inventory | Accepted | `md/handoffs/WP-1.5-scan-local-source-inventory.md` | `md/handoffs/reports/WP-1.5-completion-report.md` | `md/handoffs/reports/WP-1.5-validation-review.md` | Read-only inventory accepted for configured/default histories: exports root, OpenAI/Claude export folders, OpenAI Codex local store, Claude Code projects, and planned Cursor/Copilot paths. No DB writes or full transcript parsing. |
| WP-1.6 | config defaults + collect workflow + scheduling docs | Accepted | `md/handoffs/WP-1.6-config-defaults-collect-workflow.md` | `md/handoffs/reports/WP-1.6-completion-report.md` | `md/handoffs/reports/WP-1.6-validation-review.md` | Accepted after rework: config-aware DB precedence applies to all DB-opening commands, `chronicle init`/`collect` are functional, YAML defaults and engine-interest settings are present, and README includes optional Task Scheduler docs. |
| WP-5.1 | YAML AI-task runner + LiteLLM model configuration | Accepted | `md/handoffs/WP-5.1-yaml-ai-task-runner-litellm.md` | `md/handoffs/reports/WP-5.1-completion-report.md` | `md/handoffs/reports/WP-5.1-validation-acceptance.md` | Accepted after two rework cycles: installed resources, exact cache/provenance identity, actionable failures, provider schema propagation, dry-run provenance/cache counts, full acceptance matrix, and effective model-profile/task generation precedence. Production task semantics remain WP-5.1.1. |
| WP-5.1.1 | Initial conversation-intelligence task catalog | Accepted | `md/handoffs/WP-5.1.1-initial-conversation-intelligence-tasks.md` | `md/handoffs/reports/WP-5.1.1-completion-report.md` | `md/handoffs/reports/WP-5.1.1-validation-acceptance.md` | Accepted after one rework cycle. Overview selected IDs now flow structurally; decimal-prefix and quoted-body collisions are covered and false evidence fails validation. The earlier review remains the rework record. |
| WP-5.1.2 | Automated two-teacher reference corpus | Superseded before execution | `md/handoffs/WP-5.1.2-real-data-teacher-reference-corpus.md` | N/A | N/A | Retained as planning history only. Do not execute: the 300-case, GPT/FABLE orchestration and reconciliation design was replaced by WP-5.1.2A/B. |
| WP-5.1.2A | Frozen private development snapshot | Accepted | `md/handoffs/WP-5.1.2A-frozen-private-development-snapshot.md` | `md/handoffs/reports/WP-5.1.2A-completion-report.md` | `md/handoffs/reports/WP-5.1.2A-validation-review.md` | SQLite-native immutable backup accepted: schema v3, 711 conversations, 28,370 messages, integrity/count/hash/read-only/source-no-write/privacy checks passed. |
| WP-5.1.2B | Direct FABLE development references | Accepted | `md/handoffs/WP-5.1.2B-direct-fable-development-references.md` | `md/handoffs/reports/WP-5.1.2B-completion-report.md` | `md/handoffs/reports/WP-5.1.2B-validation-review.md` | Accepted after narrow rework: 30 frozen conversations, 120/120 Pydantic-valid FABLE references, deterministic selection/evidence/date/privacy checks, broad helper permissions removed, and UTC provenance corrected without changing references. |
| WP-5.2A | Small local model/runtime integration program | In progress | See child packages | See child packages | See child packages | Approved staged candidate/runtime program. Llama 3.2 1B floor is accepted first; additional HTTP candidates and host-managed adapters follow only in their planned sequence. |
| WP-5.2A1 | Llama 3.2 1B LM Studio evaluation floor | Accepted | `md/handoffs/WP-5.2A1-llama-3.2-1b-evaluation-floor-integration.md` | `md/handoffs/reports/WP-5.2A1-completion-report.md` | `md/handoffs/reports/WP-5.2A1-validation-review.md` | Exact Bartowski `Q4_K_M` GGUF and local runtime provenance pinned. Direct probes passed; synthetic and private smokes each produced three schema-valid results and one preserved title-assessment schema failure. Live/frozen DBs remained unchanged. |
| WP-5.2B | Gemini-judged development evaluation program | Planned after WP-5.2A1 | See child packages | See child packages | See child packages | Candidate generation and scoring must be independently runnable. Deterministic scoring stays local; Gemini judge is selected by local YAML through LiteLLM. |
| WP-5.2B1 | Single-model split generation/scoring harness | Handoff next | Pending | Pending | Pending | Evaluate all 120 Llama floor cases. Candidate generation may run remotely and returns a portable hashed package; deterministic and optional `gemini-2.5-flash` scoring run locally without the candidate runtime. |
| WP-5.2C | Remote runs and independent evaluation set | Deferred; details TBD | Pending | Pending | Pending | Stronger remote machine, private transfer, and later untouched evaluation-set size/process require separate owner decisions. |
| WP-5.1.3 | Local LM Studio AI-task smoke and compatibility fix | Accepted | `md/handoffs/WP-5.1.3-local-lm-studio-ai-task-smoke-fix.md` | `md/handoffs/reports/WP-5.1.3-completion-report.md` | `md/handoffs/reports/WP-5.1.3-validation-review.md` | Accepted after direct LM Studio/LiteLLM isolation and real local smoke. Dedicated `lm_studio/` routing, provider-compatible structural schemas, exact evidence binding, safe diagnostics, context estimates, and realistic tracked timeout policy are in place. |
| WP-5.1.4 | Windows CI Rich-output wrapping patch | Accepted | `md/handoffs/WP-5.1.4-windows-ci-rich-output-wrapping.md` | `md/handoffs/reports/WP-5.1.4-completion-report.md` | `md/handoffs/reports/WP-5.1.4-validation-review.md` | Accepted after deterministic long-path and 20-column Rich regressions plus owner-confirmed hosted GitHub pass for `f0ecaf6`. Test-only patch preserves exit code, task/alias identity, full normalized diagnostic, and no-traceback behavior. |

## Release Ledger

| Release | State | Commit | Tag | Public artifacts | Validation |
| --- | --- | --- | --- | --- | --- |
| Chat Chronicle v0.1.0 | Published source release | `1f3fbce` | `v0.1.0` (present locally and on `origin`) | Public GitHub repository/release page; release README; `docs/ai-tasks.md`; prepared LinkedIn article; sanitized manager-chat artifact | Full local suite passed; Ruff passed; `chronicle --version` reports `0.1.0`; branch matches `origin/main`; unauthenticated repository and release-page checks returned HTTP 200 |

## Research Artifact Ledger

| ID | Name | State | Files | Notes |
| --- | --- | --- | --- | --- |
| RS-1 | Chat-history access methods on Windows 11 | Recorded | `md/research/RS-1-chat-history-access-task.md`; `md/research/RS-1-chat-history-access-findings.md` | Captures official exports, Class B local stores, Class C cache caveats, automation ceilings, Claude Code retention status, and owner retrieval checklist. Feeds WP-3.1, scan-local planning, Codex `.jsonl.zst` follow-up, and possible Copilot CSV backlog work. |
| RS-2 | Claude Code/session self-identification research | Recorded | `md/research/RS-2-chat-self-identification-findings.md`; `md/research/RS-2-claude-code-format-memo.md`; `md/research/RS-2-trail-kit/` | Chat self-identification findings are research input only, not a change order. One immediate addendum applies to WP-3.1: `ai-title`, seven record types, `uuid`/`parentUuid`, `isSidechain`, and multi-file resumed/branched session cases must be reflected in fixtures, memo, and validation. |
| RS-3 | Codex cross-client workspace visibility | Recorded | `md/research/RS-3-codex-cross-client-workspace-visibility.md` | Owner observation: VS Code-created Codex conversations became visible in Codex Desktop after the same repository was opened there. Treat account-plus-workspace association as an unverified hypothesis; no extractor, schema, or scan-local change is approved. |

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
| Codex cross-client workspace association | RS-3 | Proposed only | Time-box a read-only investigation into why VS Code-created conversations become visible in Codex Desktop after opening the same repository. Determine whether identity uses path, repository metadata, a local project ID, or a service association before proposing project grouping or scan/import changes. |
| Config-driven collection workflow | Owner discussion | Approved for WP-1.5/WP-1.6 planning | Add YAML defaults, explicit init, source inventory, and one-line collect. This is orchestration over accepted adapters, not new parsing scope. |
| History download helper | Owner discussion | Proposed only | Future tool to help download histories from chat providers when supported by documented/exportable flows or safe provider-specific automation. Config YAML should record which engines the user uses or wants supported, but download automation is not part of WP-1.5/WP-1.6 unless explicitly scheduled. |
| Gemini Takeout/My Activity importer | Owner export note | Proposed only | Gemini chat text should be obtained through Google Takeout by selecting **My Activity**, filtering included activity to **Gemini Apps** / **Gemini Apps Activity**, then inspecting `My Activity/Gemini Apps/MyActivity.html` after ZIP extraction. Selecting the plain "Gemini" product may export only metadata such as custom Gems. Verify real archive shape before parser work. |
| YAML-driven AI task runner | Owner AI-feature discussion | Approved for M5 planning | Use `poetry run chronicle --ai-task <name> ...`; `<name>` resolves from `.chronicle/ai-tasks.yaml`. Prompts/task policy are external, output schemas and safety controls remain code-owned, and models are aliases from `.chronicle/ai-models.yaml` through a thin LiteLLM-backed client. Local service profiles are default; remote development/evaluation profiles require explicit authorization. |
| Initial conversation-intelligence tasks | Owner AI-feature discussion | Accepted as WP-5.1.1 | First catalog: summary with DB-derived start/last-active dates, whole-conversation work-mode classification, last-activity summary from recent meaningful turns, and title assessment with suggestion only. Real-model semantic quality remains unmeasured until WP-5.1.2/WP-5.2. |
| Real-data development references | Owner evaluation redesign | Approved sequence; handoffs pending | Replace the unexecuted automated WP-5.1.2 design with an immutable private snapshot and 30 fixed conversations x four direct FABLE references. Use all 120 cases for development; create an independent evaluation set later. |
| Gemini LLM judge | Owner evaluation redesign | Approved for WP-5.2B planning | Use a different Gemini model from the FABLE teacher, called through LiteLLM and selected by local YAML profile. Keep deterministic and judge metrics separate; exact model remains configuration-time choice. |
| First-release preparation | Owner release direction | Released as v0.1.0 | Public source release committed as `1f3fbce` and tagged `v0.1.0`; release-quality README and AI-task guide, prepared LinkedIn article, and owner-reviewed sanitized manager transcript are included; WorkTrail rename and PyPI remain deferred. |
| Host-bundled local-model benchmark adapters | Owner local-model survey | Proposed only | Edge Phi-4-mini/Aion and Chrome Gemini Nano are browser JavaScript APIs, not LiteLLM HTTP profiles. Evaluate later through dedicated adapters. Phi Silica remains the WP-5.4 Windows App SDK spike. Foundry Local needs no new adapter because it offers an OpenAI-compatible endpoint. |

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
| First remote CI run | PM / owner | Passed | Owner confirmed hosted GitHub validation passed after WP-5.1.4 commit `f0ecaf6`. |
| Poetry `VIRTUAL_ENV` hazard | All executor chats | Mitigated procedurally | Documented in `md/agent-operating-notes.md`; add the preflight to each future handoff. |
| Sandbox launcher failures | PM validation chats | Mitigated procedurally | Use direct `rg`/`Get-Content -Raw`; retry key validation commands with escalation only when the sandbox launcher fails. |
| Claude real export metadata blocks | WP-1.3.1 executor | Mitigated | Known `thinking`, `tool_use`, and `tool_result` blocks now skip without noisy parser errors. Future benign block types should be added with evidence and synthetic tests. |
| OpenAI Codex local format drift | WP-1.3.2 executor | Mitigated procedurally | Codex local JSONL is undocumented Class B storage. Accepted extractor is tolerant, synthetic-fixture covered, and fail-visible on malformed/unknown records. |
| CO-1 schema migration risk | CO-1 executor | Mitigated | Schema v2 migration accepted; source uniqueness now enforced by a DB-level partial unique index. |
| Claude standalone project metadata | WP-1.3.3 / future schema follow-up | Known limitation | Real Claude exports may include `projects/*.json` rows with no reliable conversation reference. Project rows are stored, but search only returns conversations linked by exact project UUID references. |
| WP-2.1 real-archive performance | Prototype validation | Open | Synthetic performance smoke passed on 350 conversations; master-plan p95 target on a larger real archive remains to be measured during prototype validation. |
| Default FTS special-character handling | WP-2.3.2 executor | Mitigated | Default broad search now sanitizes user text before FTS5 `MATCH`; `scan-local` returns results instead of parser errors while `--phrase` remains exact. |
| Rename to WorkTrail | Future release planning | Deferred | v0.1.0 was intentionally published under Chat Chronicle. Any later WorkTrail / `worktrail-ai` rename requires a separately approved migration and release plan; it is no longer a prerequisite for the already-published first source release. |
| FABLE-reference validity | WP-5.1.2B / WP-5.2B | Open by design | No human adjudication or second teacher is planned. References are silver development data, not ground truth; retain FABLE/task/schema provenance and explicit failures. Do not make final quality claims from this set. |
| Private remote disclosure | Owner / WP-5.1.2B / WP-5.2B | Explicitly accepted for bounded development set | Owner authorizes FABLE to inspect every selected raw conversation without conversation-level secret quarantine and Gemini to judge derived cases. Restrict disclosure to the frozen 30-conversation bundle, keep credentials in environment variables, and retain private provenance locally. |
| LLM judge bias | WP-5.2B | Planned mitigation | Use a different Gemini model from the FABLE teacher through LiteLLM/YAML configuration. Version the rubric/settings and report deterministic metrics separately from judge scores. |
| Development-set overfitting | WP-5.2B / WP-5.2C | Open by design | All 120 FABLE-reference cases may be used for development and prompt tuning. Create a separate untouched evaluation set after prompts/models are frozen. |

## Source And Export Observations

| Item | Status | Notes |
| --- | --- | --- |
| ChatGPT/OpenAI official export | Received and compatibility accepted | Owner ZIP is under `exports/openai` and uses the current split layout (`conversations-000.json` ... `conversations-004.json`) with 422 records. WP-1.2.1 accepted direct ingest and auto-detection; PM smoke produced 422 conversations and 5,166 messages with 92 non-text part warnings. |
| Claude official export | Ingested; project metadata limitation characterized | Claude provider has 13 conversations in the repo-local DB. WP-1.3.3 parses 30 project metadata rows and links/searches project names only when exact project UUID references exist. The owner real export has no project-like conversation keys, so its private project names cannot safely return Claude conversations without guessing. |
| Gemini official export | Backlog candidate | Owner note: use Google Takeout -> My Activity -> filter to Gemini Apps / Gemini Apps Activity. Expected extracted location is `My Activity/Gemini Apps/MyActivity.html`; plain "Gemini" product export may contain only metadata/custom Gems. |
| Research records | Recorded | `md/research/` now holds research-spike records for history data retrieval methods and current source-access status. |
| Source listing utility | Accepted as WP-1.5 | `scan-local` lists available configured/default histories before ingest using read-only checks. `stats` continues to list already-ingested sources. |
| Config defaults | Accepted as WP-1.6 | YAML config defines `.chronicle/chronicle.db`, `exports`, `exports/openai`, `exports/claude`, `%USERPROFILE%\.codex`, and `%USERPROFILE%\.claude\projects`. Installation does not mutate folders; explicit `chronicle init` creates directories/config. |
| Engine interest settings | Accepted as WP-1.6 | Config YAML records which engines/sources the user uses or wants support for. This drives scan/help/collect defaults, not parser behavior. |
| One-line loader | Accepted as WP-1.6 | `chronicle collect` ingests enabled local stores and supported sources under the configured exports root with idempotent reruns. |

## Next Action

1. Treat Chat Chronicle v0.1.0 as the published baseline at commit `1f3fbce` / tag `v0.1.0`.
2. The owner decides when and how to publish the prepared LinkedIn article; article publication is not inferred from the tracked draft.
3. Treat WP-5.1.2A as the accepted immutable development basis; the old WP-5.1.2 automation handoff must not be executed.
4. Treat WP-5.1.2B as the accepted private silver development corpus. Do not use it as final evaluation data or publish private cases.
5. Define and approve the local model/runtime shortlist before WP-5.2A implementation; use a different Gemini model through LiteLLM/YAML as the WP-5.2B judge.
6. Defer remote-machine setup and the separate untouched evaluation set to WP-5.2C decisions.
7. Keep this thread as the main development planning and PM-validation record.
