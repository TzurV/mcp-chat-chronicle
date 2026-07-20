# WorkTrail — Master Plan

**Repo:** first public source release under `mcp-chat-chronicle`; later rename/PyPI candidate `worktrail-ai` · **One-liner:** *A local-first activity and context ledger across AI tools — populated by source-specific importers and extractors, normalized into one SQLite/FTS journal, optionally enriched by a local SLM and recallable from MCP clients.*

**Status:** Chat Chronicle v0.1.0 source release published · release commit `1f3fbce` and remote tag `v0.1.0` are available from the public GitHub repository/release page · real-history core prototype accepted; ingest/collect/stats/search/phrase/recent/open work across the owner's real ChatGPT, Claude, OpenAI Codex, and Claude Code histories · WP-5.1 configurable AI-task foundation, WP-5.1.1 production task contracts, WP-5.1.3 local LM Studio compatibility/smoke, and WP-5.1.4 Windows CI portability are accepted · AI development has resumed with an approved sequence of frozen private snapshot, 30-conversation x four-task direct FABLE development references, local runtime integration, and a different Gemini model as LiteLLM-configured judge · local model shortlist, remote machine, and later untouched evaluation set remain TBD · **Plan v3.4 ("Plan A+ — Batch-first, Pluggable Collectors", + configurable AI tasks and measured local-model evaluation)**, **amended by `md/change-order-01.md`**. Full reasoning chain in Appendix A. · **Last updated:** 2026-07-20
**This document is the single source of truth when read with the approved amendment `md/change-order-01.md`.** Work packages (WP-x.y) are written to be handed off verbatim to sub-code-agents in VS Code. LinkedIn posts (LP-x) map to milestones.

**Guiding principle:** *Build the boring useful archive first. Clever live capture, marker joins, and cache forensics are optional later experiments.*

---

## 1. Project Charter

### 1.1 Problem
AI tools are multiplying, but the activity trail is missing. Work is scattered across ChatGPT, Claude, Gemini, **and coding agents** (OpenAI Codex, Claude Code, Cursor, Copilot Chat). Each stores history in an isolated, poorly-searchable silo. There is no way to ask "where did I debug that docker networking issue, in which tool, and how do I get back to it?"

### 1.2 Solution
A **source-agnostic core** fed by **pluggable, source-specific adapters**:

```
source-specific collector / importer / extractor
        ↓
normalized Conversation + Message objects (Pydantic)
        ↓
SQLite database (idempotent upsert)
        ↓
FTS5 search index
        ↓
CLI: search / stats / open
        ↓
optional: YAML-defined conversation-intelligence tasks via local LLM (v1.2)
        ↓
optional: MCP recall (v1.3)
```

Each chat engine gets its own collection method; everything downstream — schema, upsert, search, snippets, stats, enrichment, MCP tools, CLI UX, tests — is shared. Adding a new source means adding one adapter, not changing the system.

**Terminology (use consistently):**
- **Importer** — reads official export files (ChatGPT export, Claude export, Gemini Takeout).
- **Extractor** — reads local app/tool storage (Claude Code JSONL, Cursor workspace SQLite).
- **Collector** — `worktrail collect`: discovers configured sources and runs the right importer/extractor.
- **Adapter** — the implementation unit for one source. Its single contract: *given this messy source, produce normalized conversations and messages.*

### 1.3 Source classification (the key architectural insight)

| Class | What | Reliability | Examples | Scheduled for |
| --- | --- | --- | --- | --- |
| **A — Official exports** | User-requested export files | High (implicit provider contract) | ChatGPT export, Claude export, Gemini Takeout | **v1** |
| **B — Local durable stores** | Coding-agent/IDE tool storage on disk | Medium — complete and passive, but **undocumented internals that can change any release** | OpenAI Codex (`~/.codex/sessions` JSONL), Claude Code (`~/.claude/projects` JSONL), Cursor (`%APPDATA%\Cursor\...\workspaceStorage` SQLite), VS Code/Copilot Chat if practical | **v1.1** |
| **C — Local caches / forensic stores** | App/browser IndexedDB, LevelDB, cache | Low — partial, wiped on logout/update, per-product reverse engineering | ChatGPT Desktop cache, Claude Desktop cache, browser storage | **Post-v1 experimental only. Never build the product around Class C.** |

Class B is what makes batch-first viable as a *daily* tool: extractors are **passive** — no export button, no model cooperation — and coding-agent history is most of a developer's valuable history. `worktrail collect` picks up fresh Claude Code/Cursor sessions automatically; only web-chat history waits for export cadence.

### 1.4 Positioning vs prior art (state in README, LP-1, and the article)

| Project | What it does | How we differ |
| --- | --- | --- |
| [OpenMemory MCP (mem0)](https://mem0.ai/blog/introducing-openmemory-mcp) | Stores distilled *facts/preferences* about you, shared across MCP clients | We index *events*: which conversation, when, in which tool, with a way back. An archive, not a memory. |
| [OpenChat](https://github.com/p0u4a/openchat) | Browser extension captures chatgpt.com/claude.ai traffic → local MCP resources | We use official exports + durable local stores (robust, no extension); adapter architecture covers coding agents, which extensions can't reach. |
| [Agent Sessions](https://github.com/jazzyalex/agent-sessions) | Local multi-agent history browser with useful parser prior art | We are Windows-first and unify web-chat exports plus coding agents into one archive, then add knowledge distillation and MCP recall. |
| Provider built-in search | Per-silo only | Cross-provider **and cross-tool** (web chats + coding agents), local, private, scriptable. |

Distinctive angles to lead with: the **adapter/source-class architecture**, the **Windows storage forensics** of what AI tools actually keep on disk (`scan-local`), and the **local-SLM benchmark**. The shelved marker-join design (Appendix A.3/A.6) remains strong *content*, not product.

### 1.5 Goals / Non-goals
**Goals:** learning (export formats, adapter design, SQLite/FTS5, idempotent ingestion, CLI UX, Windows file discovery, local SLMs, MCP) · a tool used daily · a credible GitHub repo · a 5-post LinkedIn series + 1 long-form article.
**v1 goal, deliberately boring:** *a Windows user can import available AI conversation data into a local SQLite archive and search it fast.*
**Non-goals for v1** (post-v1 backlog, §6): live logging / `log_activity` / marker join · Class C cache parsing · browser extension · query rewriting on by default · sqlite-vec hybrid search · OpenTelemetry · local RAG TUI · cross-provider threading · cloud sync · multi-user · UI beyond CLI.

### 1.6 Known constraints (do not re-litigate — verified 2026-07)
- MCP servers only see explicit tool calls; models don't know their own conversation IDs. Hence adapters for capture, MCP for recall only. (The marker-echo workaround exists and is shelved — Appendix A.)
- ChatGPT supports only **remote HTTPS** MCP servers ([OpenAI docs](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)); target Claude Desktop/Cursor for MCP recall, document bridging as experimental.
- **Class B formats are less stable than Class A**, not more: no export contract at all. Mitigate with pinned per-version fixtures, parse-don't-validate with per-record error logging, and copy-before-read for live SQLite files (Cursor's DB is locked while Cursor runs).
- Coding-agent conversations have **no URLs** — `worktrail open` shows a local transcript view for those; deep links exist only for web-chat sources.
- "Scheduled collection" = a documented one-line **Windows Task Scheduler** entry invoking `worktrail collect`. No daemon, no service.
- Phi Silica is WinRT/C#, NPU/Copilot+ gated — stretch spike only; primary local runtime is LM Studio.

### 1.7 Naming (CO-6)
The first public source release remains **Chat Chronicle**, using
`mcp-chat-chronicle` / `chat_chronicle` / `chronicle`. The owner explicitly deferred
the planned **WorkTrail** / `worktrail-ai` / `worktrail` rename beyond v0.1.0 so the
accepted implementation can ship without a release-blocking naming migration. The
future rename remains a naming/packaging change, not an architecture change.

---

## 2. Core Design Rules

1. **One question per adapter.** *Given this messy source, can I produce normalized conversations and messages?* Everything else is shared code.
2. **The abstraction is discovered, not designed** *(amendment to the original A+ proposal)*: write adapters as plain concrete code first; do not add `AdapterProtocol`/`base.py` inside parser/extractor work packages. Re-evaluate the abstraction only in a dedicated refactor WP after multiple accepted adapters make the repeated CLI/collector integration shape obvious. No framework-building inside source-specific parser work.
3. **No configuration state may be broken — only leaner.** No LM Studio → enrichment/`--smart` silently off. No MCP client → CLI fully functional. A source missing → skipped with a note in `ingest_runs`, never a crash.
4. **Read-only before write.** `scan-local` reports what exists without importing; experimental sources are surfaced as "found, not imported" long before any parser is written for them.
5. **Everything idempotent.** Re-running any collect/ingest against unchanged sources changes zero rows (`provider + provider_conv_id` identity, `content_hash` change detection).

---

## 3. Tech Stack (decided — sub-agents must not substitute)

| Concern | Choice | Rationale / source |
| --- | --- | --- |
| Language / pkg | Python 3.11+ · **Poetry** | User's stack |
| Data models | **Pydantic v2** | Validation + shared schema with SLM structured output later |
| CLI | **Typer** + Rich | Fast, typed, pretty tables |
| DB | **SQLite** (stdlib `sqlite3`) + **FTS5** | Zero-install, right tool for text recall |
| LLM task runtime (v1.2) | **LiteLLM Python SDK** behind a small internal client; local service profile uses **LM Studio**, stronger remote profiles are development/evaluation only | Task and model profiles stay external; structured results are validated against code-owned Pydantic schemas |
| MCP (v1.3) | **FastMCP** (`fastmcp` 3.x) over official `mcp` 1.x | De-facto standard; [FastMCP](https://pypi.org/project/fastmcp/) · [mcp SDK](https://pypi.org/project/mcp/) |
| Testing | pytest + **synthetic fixtures only** | Never commit real chat data |
| Lint/CI | ruff + pre-commit + GitHub Actions (Windows + Ubuntu) | Table stakes for a public repo |

**Not chosen, say why in README:** DuckDB (analytics engine, wrong fit for text recall), Marvin (task definitions and schemas remain explicit), a browser extension (fragile; covered by exports + extractors), a background daemon (Task Scheduler suffices), and a mandatory LiteLLM proxy service (unnecessary for the single-user v1 workflow). Use the LiteLLM Python SDK behind a small internal `LLMClient` port so the application is not coupled to one provider or runtime. LM Studio is the default local service runtime; other local or remote providers are selected by external model profiles.

---

## 4. Repository Layout

```
mcp-chat-chronicle/
├── pyproject.toml               # poetry; extras: [enrich], [mcp]
├── ai-tasks.default.yaml        # tracked task catalog; copied/overridden locally
├── ai-models.default.yaml       # tracked model-profile examples; no credentials
├── README.md                    # positioning (§1.4), 60-sec quickstart, honest limitations
├── md/                          # this plan + handoffs + design notes + research + article/post drafts
│   └── research/                # research spikes on source access, local stores, retention, and roadmap inputs
├── src/chat_chronicle/
│   ├── models.py                # Conversation, Message, Enrichment (Pydantic)
│   ├── db.py                    # connection, migrations, idempotent upserts, FTS sync
│   ├── adapters/
│   │   ├── chatgpt_export.py    # v1  — Class A importer (tree-walk mapping)
│   │   ├── claude_export.py     # v1  — Class A importer
│   │   ├── gemini_takeout.py    # v1 optional — Class A importer [experimental]
│   │   ├── openai_codex.py      # v1  — Class B extractor (JSONL)
│   │   ├── claude_code.py       # v1.1 — Class B extractor (JSONL)
│   │   ├── cursor.py            # v1.1 — Class B extractor (workspace SQLite)
│   │   └── base.py              # created only by a dedicated refactor WP, NOT inside parser work
│   ├── collect.py               # collector: reads sources table, runs adapters, logs ingest_runs
│   ├── scan.py                  # scan-local: read-only source discovery on Windows
│   ├── search.py                # FTS5 queries, snippets, ranking
│   ├── enrich/                  # v1.2: LiteLLM adapter, task loader, schemas, worker
│   ├── cli.py                   # typer: ingest, ingest-folder, collect, scan-local, stats, search, open
│   └── mcp_server.py            # v1.3: search_chats, get_conversation, list_recent_topics
├── bench/                       # v1.2 benchmark harness (separate poetry group)
│   ├── tasks/                   # json_adherence, summary_fidelity, needle
│   ├── run.py                   # model × task matrix → results.jsonl
│   └── report.py                # markdown table + chart for LP-4
└── tests/
    ├── fixtures/                # SYNTHETIC exports + per-version Class B fixtures
    └── test_*.py
```

**CLI surface (v1 target; `chronicle` remains the pre-rename implementation until CO-6 lands):**

```bash
worktrail ingest path/to/export.zip --provider auto   # Class A/Class B, one supported source
worktrail ingest-folder path/to/exports               # sweep a drop folder
worktrail collect                                     # run all enabled sources
worktrail scan-local                                  # read-only: what sources exist on this machine?
worktrail stats                                       # counts per source, last runs, unjoined/errors
worktrail search "docker network"                     # FTS5, ranked, snippets, links
worktrail open <result-id>                            # deep link (web) or transcript + origin/resume hints
worktrail --ai-task list                              # names resolved from .chronicle/ai-tasks.yaml
worktrail --ai-task <name> --conversation-id <id>     # run one configured AI task
```

The pre-rename development form is `poetry run chronicle --ai-task <name> ...`. `--ai-task` is intentionally a generic dispatch option rather than one hard-coded command per prompt. Task names, prompts, input-selection policy, model-profile alias, generation parameters, and task version come from `.chronicle/ai-tasks.yaml`. Supported output-schema names remain code-owned and Pydantic-validated. `.chronicle/ai-models.yaml` separately maps logical profiles such as `service-local`, `development-fast`, and `evaluation-strong` to LiteLLM provider/model settings. Secrets are environment-variable references only and must never be written into either YAML file.

Normal `search`, `recent`, `stats`, `collect`, and `open` execution never invokes an LLM. AI tasks run as an explicit, resumable offline workflow. The service default is local-only; a model profile marked remote requires an explicit `--allow-remote` invocation because the archive contains real private data.

`scan-local` example output (read-only, builds trust before any parsing):

```
ChatGPT export folder:   not configured
Claude export folder:    not configured
Claude Code:             found  ~/.claude/projects            (v1.1 extractor)
Cursor:                  found  %APPDATA%\Cursor\User\workspaceStorage  (v1.1 extractor)
VS Code / Copilot Chat:  found  %APPDATA%\Code\User\workspaceStorage    (evaluating)
ChatGPT Desktop cache:   found  — experimental, not imported
Claude Desktop cache:    found  — experimental, not imported
```

---

## 5. Data Model (authoritative schema)

```sql
CREATE TABLE sources (
    id INTEGER PRIMARY KEY,
    source_type TEXT NOT NULL CHECK(source_type IN
        ('official_export','local_store','manual_folder','experimental_cache','manual_entry')),
    provider TEXT NOT NULL,            -- 'chatgpt','claude','gemini','claude_code','cursor',... (open set)
    path_or_config TEXT,
    enabled INTEGER NOT NULL DEFAULT 1,
    last_seen_at TEXT, last_ingested_at TEXT
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    root_path TEXT,
    created_at TEXT
);

CREATE TABLE ingest_runs (                          -- debugging + scheduling visibility
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    started_at TEXT NOT NULL, finished_at TEXT, status TEXT,
    conversations_seen INTEGER, added INTEGER, updated INTEGER, skipped INTEGER,
    errors_json TEXT                                -- per-record parse errors, never fatal
);

CREATE TABLE conversations (
    id            INTEGER PRIMARY KEY,
    source_id     INTEGER REFERENCES sources(id),
    project_id    INTEGER REFERENCES projects(id),
    provider      TEXT NOT NULL,
    provider_conv_id TEXT NOT NULL,
    title         TEXT,                -- required by adapter AC; synthesize when source lacks a name
    url           TEXT,                -- chatgpt.com/c/<id> · claude.ai/chat/<uuid> · NULL for coding agents
    origin_path   TEXT,                -- local source transcript path for CLI-agent sources
    resume_hint   TEXT,                -- best-effort reopen command, e.g. claude --resume <session-id>
    created_at    TEXT, updated_at TEXT,            -- ISO8601 UTC
    message_count INTEGER,
    content_hash  TEXT NOT NULL,                    -- sha256 of normalized messages → idempotent re-ingest
    UNIQUE(provider, provider_conv_id)
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    role TEXT, created_at TEXT, body TEXT, seq INTEGER
);

CREATE TABLE ai_task_results (                       -- populated in v1.2, optional forever
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    task_name TEXT NOT NULL, task_version TEXT NOT NULL,
    input_hash TEXT NOT NULL, prompt_hash TEXT NOT NULL,
    task_config_hash TEXT NOT NULL,
    schema_name TEXT NOT NULL, schema_version TEXT NOT NULL,
    model_profile TEXT NOT NULL, model_config_hash TEXT NOT NULL,
    model_used TEXT,
    result_json TEXT, status TEXT NOT NULL, error TEXT,
    started_at TEXT, completed_at TEXT
);                                                  -- append-only attempts; indexed cache identity
CREATE INDEX idx_ai_task_result_cache ON ai_task_results(
    conversation_id, task_name, input_hash,
    task_config_hash, schema_version, model_config_hash, status
);

CREATE TABLE knowledge_items (                      -- v1.2 "distilled knowledge" (WP-5.5)
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    kind TEXT CHECK(kind IN ('decision','solution','open_question')),
    statement TEXT NOT NULL,                        -- "chose X over Y because Z" / "fixed E by doing F"
    context TEXT,                                   -- short surrounding detail
    tags_json TEXT, model_used TEXT, extracted_at TEXT
);                                                  -- indexed in chat_fts (statement+context)

-- v2: CREATE VIRTUAL TABLE chat_vec USING vec0(embedding float[384]);  -- summaries first

CREATE VIRTUAL TABLE chat_fts USING fts5(
    title, summary, last_activity, body,
    content='', tokenize='porter unicode61'         -- external-content; sync via triggers/rebuild
);
```

Link-back guarantee: every adapter must populate enough information to return to the original session. Web sources use `url`; CLI-agent/local-store sources use `origin_path` and best-effort `resume_hint`; all sources must provide `provider_conv_id` and a usable `title` (source title when present, otherwise synthesize `"<project>: <first user message, truncated>"`).

Deep links: ChatGPT `https://chatgpt.com/c/{conv_id}`, Claude `https://claude.ai/chat/{uuid}` (both IDs in official exports). Gemini and all coding agents: `url` NULL → `worktrail open` renders the stored transcript and prints `origin_path` + `resume_hint`.

---

## 6. Milestones & Work Packages

Each WP = one sub-agent handoff: **Objective · Tasks · Acceptance criteria (AC) · Notes/sources.** Every handoff must explicitly state that the executor leaves changes uncommitted, the PM validates the report and implementation, and only the PM stages and commits after validation plus an explicit owner request. A commit request addressed to the PM is never executor authorization. CO-01 overrides the remaining execution order for prototype speed:

```text
WP-1.4  CLI ingest + stats
CO-1    schema migration + importer/extractor link-back touch-ups
WP-2.1  FTS search + open
WP-3.1  Claude Code extractor
PROTOTYPE: search/open real coding-agent + web-export history end-to-end [ACCEPTED]
WP-1.5  scan-local source inventory
WP-1.6  config defaults + collect + scheduling docs
WP-2.3.2 search FTS special-character escaping
NEXT: WP-5.1 YAML AI-task runner + LiteLLM model configuration
then WP-5.1.1 task details, Gemini when a real Takeout is available, MCP/release later
```

Accepted work is not redone; the schema amendments arrive as a forward migration before WP-2.1.

### M0 — Scaffold (≈1 evening)
**WP-0.1 Repo bootstrap.**
*Objective:* Working skeleton with CI.
*Tasks:* Poetry layout per §4; deps `pydantic^2 typer rich`; dev `pytest ruff pre-commit`; extras `enrich=[openai] mcp=[fastmcp]`. GitHub Actions: lint + test, 3.11/3.12, **Windows + Ubuntu**. MIT license. `.gitignore`: `*.db`, `exports/`, fixtures exempt.
*AC:* `poetry install && poetry run pytest` green in CI on both OS; `chronicle --help` lists all §4 subcommands (stubs OK).

### M1 — v1 core: schema + Class A importers
**WP-1.1 Normalized models + DB layer.**
*Objective:* `models.py` + `db.py` per §5 — including `sources` and `ingest_runs` from day one.
*Tasks:* Pydantic models; migration runner (`PRAGMA user_version`); `upsert_conversation()` skipping unchanged `content_hash`; every ingest wrapped in an `ingest_runs` row with counts + `errors_json`; FTS rebuild command.
*AC:* Re-ingesting an identical fixture → run recorded with added=0/updated=0; per-record parse errors land in `errors_json` without aborting the run; FTS row-sync tested.

**WP-1.2 ChatGPT export importer.** *(depends WP-1.1 — write as plain concrete code, no base class: design rule 2)*
*Objective:* Parse `conversations.json` from the official export.
*Tasks:* Walk the **tree-shaped `mapping`** (nodes: `id/parent/children/message`); linearize the current branch (follow `current_node` back, else deepest chain); title, Unix→ISO timestamps, roles, `content.parts`; skip non-text parts gracefully; construct URL.
*AC:* Fixture with an edited/regenerated branch parses to the correct linear thread; malformed nodes logged to `errors_json`, never crash.
*Sources:* [export structure](https://community.openai.com/t/decoding-exported-data-by-parsing-conversations-json-and-or-chat-html/403144) · [mapping Q&A](https://community.openai.com/t/questions-about-the-json-structures-in-the-exported-conversations-json/954762).

**WP-1.3 Claude export importer.** *(depends WP-1.1)*
Same contract; Claude's export `conversations.json` is a flat array (`uuid`, `name`, `created_at`, `chat_messages[]`). **First task: request a real export, sanitize it into a synthetic fixture** — verify the format before speccing the parser.

**WP-1.3.1 Claude real export content-block correction.** *(depends WP-1.3 — must complete before WP-1.4)*
*Objective:* Align the Claude importer with real export content blocks discovered during manual verification. Real exports contain expected non-text metadata blocks such as `thinking`, `tool_use`, and `tool_result`; these must be skipped without polluting parser errors, while malformed or unknown blocks still produce serializable parse errors.
*AC:* Synthetic fixture covers `text` plus known metadata blocks; metadata-only messages skip without noisy errors; unknown/malformed blocks still log errors; no DB writes, CLI ingest behavior, adapter base/protocol, or real export data introduced.

**WP-1.3.2 OpenAI Codex local extractor.** *(depends WP-1.1 — must complete before WP-1.4)*
*Objective:* Parse local OpenAI Codex JSONL sessions from `~/.codex/sessions` into normalized conversations/messages before CLI ingest wiring. Treat this as Class B storage: undocumented, local, version-sensitive, and covered by synthetic fixtures only.
*AC:* Concrete `openai_codex.py` extractor accepts one session JSONL file and Codex session/home directories; extracts visible user/assistant/developer messages from `response_item`/visible event fallbacks; skips known metadata/tool/reasoning rows without noisy errors; malformed/unknown records log serializable errors; no DB writes, CLI behavior, adapter base/protocol, or real Codex data introduced. CO-3 follow-up: older Codex sessions may be compressed as `.jsonl.zst`; add support before relying on archived Codex history.

**WP-1.4 CLI ingest + stats.** *(accepted under the current pre-rename `chronicle` command)*
*AC:* `chronicle ingest <path> --provider auto` detects ChatGPT/Claude official exports and OpenAI Codex local sessions by file signature; `chronicle stats` shows per-source counts + last `ingest_runs` summary; 1k conversations ingest < 30 s. After CO-6 rename, equivalent commands are exposed as `worktrail`.

**CO-1 Schema migration + link-back touch-ups.** *(inserted by Change Order 01 — must land before WP-2.1)*
*Objective:* Apply the link-back/project schema amendments as one migration after accepted WP-1.1, and patch accepted adapters only where required to satisfy title/link-back guarantees.
*Tasks:* Bump `PRAGMA user_version`; add `projects`; add `conversations.project_id`, `origin_path`, and `resume_hint`; extend `sources.source_type` CHECK with `manual_entry`; verify/patch ChatGPT and Claude importers to always populate a usable title; verify local-store extractors populate `origin_path` and best-effort `resume_hint` where supported; update DB tests and migration tests.
*AC:* Existing DBs migrate forward; all accepted importers/extractors still pass; every conversation has `provider_conv_id` and a useful `title`; web-source rows preserve URL link-back; CLI-agent rows carry `origin_path` and best-effort `resume_hint`; `manual_entry` is accepted by the schema but `worktrail note` is not implemented yet.

**CO-2 `worktrail note` manual web-chat entry.** *(approved, deferred post-M2)*
*Objective:* Let the user create a lightweight manual placeholder for a web chat before an official export is available.
*Future spec:* `worktrail note --url <chat-url> --project X "one-liner"` creates a `manual_entry` source/conversation row; later export ingests merge by URL match.
*Scheduling:* Do not build on the prototype path. CO-1 only prepares the schema.

**WP-1.5 scan-local (read-only discovery).**
*Objective:* Report what AI-tool data exists on this Windows machine — import nothing.
*Tasks:* Probe configured paths plus known defaults (`exports/openai`, `exports/claude`, `~/.codex`, `~/.claude/projects`, `%APPDATA%\Cursor\User\workspaceStorage`, `%APPDATA%\Code\User\workspaceStorage`, desktop-app cache dirs); output a provider/path/status table with status (found / missing / configured / experimental / unsupported); use path-existence, mtime, and shallow signature checks only — no full transcript parsing and no DB writes. Read the config file from WP-1.6 when present, but keep useful defaults when no config exists.
*AC:* Runs in <2 s on normal workstations; never imports or mutates source data; prints a clear inventory of available histories and missing configured paths; missing sources are notes, not failures. Not on the CO-01 prototype critical path.

**WP-1.6 config defaults + collect workflow + scheduling docs.**
*Objective:* Make the recurring usage loop one command.
*Tasks:* Add a YAML config file for project defaults; define default DB path (`.chronicle/chronicle.db`), exports root (`exports`), default export subdirectories (`exports/openai`, `exports/claude`), and local native sources (`%USERPROFILE%\.codex`, `%USERPROFILE%\.claude\projects`) with enable flags. Include an `engines`/`enabled_sources` section so the user can state which chat engines they use or want support for; this drives `scan-local` and future download/help UX, not parser behavior. Add an explicit init command (`chronicle init` or `chronicle config init`) that creates `.chronicle/`, `exports/`, `exports/openai/`, and `exports/claude/` and writes a starter config; package install must not create user folders. `chronicle collect` reads config and ingests all enabled local sources plus all supported sources under the configured exports root using existing ingest/adapters and idempotent DB writes. `scan-local` should show the same configured/default source inventory read-only. Document one-line **Windows Task Scheduler** setup for recurring `chronicle collect` (no daemon — design constraint §1.6).
*AC:* Fresh checkout can run init and get the expected directories/config; `collect` loads configured local stores and all supported exports under the configured root; rerunning `collect` against unchanged data adds 0 conversations; missing configured paths are skipped with a note; CLI `--db-path` still overrides env/config/default; no private export/DB data is committed.

**Future CO: history download helper.** *(backlog candidate, not WP-1.5/WP-1.6 scope)*
*Objective:* Help users obtain cloud-hosted histories for providers that support documented exports or safe automation.
*Notes:* This is distinct from import/parsing. The YAML config should record which engines the user uses or wants supported so `scan-local`/help/download UX can explain missing histories and provider-specific next steps. Download support must be provider-by-provider, respect terms and authentication boundaries, and fall back to documented manual export instructions when automation is unsupported. Gemini chat history should be treated as a Google Takeout/My Activity source: selecting the plain "Gemini" product can export only metadata such as custom Gems, while chat text is exported through **My Activity** filtered to **Gemini Apps** / **Gemini Apps Activity**. The expected downloaded archive path is under `My Activity/Gemini Apps/`, with chat text currently visible in `MyActivity.html`; verify whether JSON is also present before writing a parser.

### M2 — v1 search (first "wow")
**WP-2.1 FTS5 search + open.**
*Tasks:* FTS5 `MATCH` + `bm25()` ranking; filters `--provider --since --until --tag`; Rich table: date · source · title · snippet() · link/id; `worktrail open <id>` → launch URL for web sources, or render stored transcript with Rich paging and print `origin_path` + `resume_hint` for CLI-agent/local-store sources.
*AC:* p95 < 100 ms on 5k conversations; quoting/empty-query edge cases handled; `open` works for URL and local transcript rows; CO-1 link-back fields are exercised in tests.
*Source:* [SQLite FTS5 docs](https://sqlite.org/fts5.html).

### M3 — v1.1: Class B extractors (coding agents)
Class B ground rules (all WPs): pinned per-tool-version fixtures; parse-don't-validate with `errors_json`; **copy-before-read** for any live SQLite file; a format change must degrade to "source skipped + warning," never crash.

**WP-3.1 Claude Code extractor.**
*Objective:* Ingest `~/.claude/projects/**/*.jsonl` transcripts.
*Tasks:* **First task is a research spike** — study the parsers in Agent Sessions, claude-record, and codex-trace as format documentation, then inventory the actual JSONL structure on the developer's machine and freeze it into a fixture + short format memo in `md/` (local inspection remains authoritative; the memo is also LP-3 material). Then: map sessions → conversations (project dir + session id), messages with roles/timestamps; populate `project_id`, `origin_path`, and best-effort `resume_hint` such as `claude --resume <session-id>`; incremental by file mtime + content hash.
*AC:* Fixture round-trips; re-collect with no new sessions → 0 changes; unknown record types logged and skipped; link-back fields satisfy CO-1.

**Prototype milestone.** *(accepted by owner real-history smoke)*
*Demo AC:* `worktrail search "<something real>"` returns ranked hits spanning the owner's actual Claude Code history and at least one ingested web-chat export; `worktrail open <id>` launches a web URL for export sources or shows a local transcript with `origin_path` + `resume_hint` for CLI sources.
*Accepted evidence:* Real ChatGPT, Claude, OpenAI Codex, and Claude Code histories are present in the repo-local private DB; owner CLI smoke exercised stats, recent, broad search, phrase search, web URL open, and local transcript rendering. No private transcript or DB artifact is tracked.

**WP-3.2 Cursor extractor.** *(deferred; owner does not use Cursor)*
*Objective:* Ingest Cursor chat from `workspaceStorage` SQLite.
*Tasks:* Same spike-first approach (inventory `state.vscdb` keys, freeze fixture + memo); copy DB to temp before opening (lock avoidance); map workspace → conversation grouping.
*AC:* Extraction works while Cursor is running (via the copy); fixture-pinned; graceful skip on schema drift.

**CO-3 Codex archived-session support.** *(candidate, build on demand)*
*Objective:* Extend the accepted OpenAI Codex extractor if the owner needs archived Codex sessions that are compressed as `.jsonl.zst`.
*AC:* Reads both `.jsonl` and `.jsonl.zst` with synthetic compressed fixtures; no real Codex data committed; graceful skip if optional decompression support is unavailable.

**WP-3.3 Evaluate/extract the adapter abstraction.** *(dedicated refactor only — design rule 2)*
*Objective:* After multiple concrete adapters and CLI/collector wiring have exposed real repetition, decide whether to factor `adapters/base.py` (`AdapterProtocol`: `discover(source) -> iter[Conversation]`). If the shape is still not obvious, document why no abstraction was extracted. If extracted, refactor only the repeated integration surface and document "how to add a source" in `CONTRIBUTING.md`.
*AC:* All adapters pass the same contract test suite; adding a mock adapter requires touching only `adapters/` + `sources` row.

### M4 — v1.3: MCP recall ⏰ **time-fenced: land within 2 weeks of WP-2.1 acceptance, may run parallel after search**
Small (≈1 evening on FastMCP) but strategically load-bearing — it's the demo, the MCP learning goal, and LP-5. Do not let it slide behind enrichment.

**WP-4.1 FastMCP server.**
*Tasks:* `mcp_server.py`, stdio transport, `worktrail serve`. Tools (docstrings matter — the model reads them):
  - `search_chats(query, provider?, after?, before?, limit=10)` → {title, provider, date, summary?, url?, id, score}
  - `get_conversation(id, max_chars=8000)` → truncated transcript
  - `list_recent_topics(days=7)` → digest from validated AI-task results (or titles until v1.2 exists)
  **No `log_activity` in v1 MCP** (shelved — Appendix A.6).
*AC:* Registered in Claude Desktop; end-to-end: "what was I working on in Cursor last month about X?" → correct answer with transcript access.
*Sources:* [FastMCP docs](https://gofastmcp.com) · [MCP python-sdk](https://github.com/modelcontextprotocol/python-sdk).

**WP-4.2 (experimental, timeboxed 1 evening) ChatGPT bridging docs.** `mcp-remote`/tunnel path per [OpenAI connector docs](https://developers.openai.com/api/docs/guides/tools-connectors-mcp); outcome is a docs page, success optional.

### M5 — v1.2: configurable conversation intelligence + benchmark
**WP-5.1 YAML AI-task runner + LiteLLM model configuration.**
*Objective:* Provide one optional, provider-independent execution path for externally defined LLM tasks without slowing or coupling normal archive operations to an LLM.
*Tasks:* Add the optional LiteLLM SDK behind a small internal `LLMClient`; add tracked privacy-safe defaults plus generated local `.chronicle/ai-tasks.yaml` and `.chronicle/ai-models.yaml`; validate both files with Pydantic; resolve `worktrail --ai-task <name> ...` / pre-rename `poetry run chronicle --ai-task <name> ...` from the task catalog; reserve `--ai-task list` for discoverability; support conversation selection (`--conversation-id`, provider/date filters, and bounded `--limit`), resumable execution, `--force`, timeouts, retries, and per-conversation failure recording. Store hashes of the conversation input, canonical task configuration, prompt, schema version, and resolved model configuration alongside the logical model profile, actual provider/model, timing, usage when available, and validated JSON output in `ai_task_results`. Task YAML owns prompts, task versions, input selectors, generation parameters, dependencies, and model-profile aliases; Python owns the allowed input selectors, Pydantic output schemas, privacy enforcement, and DB writes. API keys come only from environment variables. Local profiles are allowed by default; remote profiles require `--allow-remote`.
*AC:* A new task can be added or its prompt changed in YAML without adding a CLI command; unknown task/schema/input-selector names fail clearly; unchanged task+input+resolved configuration is skipped from cache; changing the conversation, prompt, task settings/version, schema version, model alias, or model definition produces a new result; malformed YAML or invalid structured output is fail-visible and does not corrupt prior results; LM Studio/provider unavailable produces an actionable task failure while `search`, `recent`, `stats`, `collect`, and `open` remain unaffected; tests mock LiteLLM and use synthetic conversations only.
*Sources:* [LiteLLM Python SDK](https://docs.litellm.ai/) · [LiteLLM structured outputs](https://docs.litellm.ai/docs/completion/json_mode) · [LM Studio structured output](https://lmstudio.ai/docs/developer/openai-compat/structured-output).

**WP-5.1.1 Initial conversation-intelligence task catalog.** *(accepted after one evidence-integrity rework; handoff at `md/handoffs/WP-5.1.1-initial-conversation-intelligence-tasks.md`)*
*Objective:* Ship the first four YAML-defined tasks based on the owner's real working pattern.
*Tasks:* Define independently runnable tasks: (1) `conversation-summary`, returning a concise summary accompanied by deterministic DB-derived `start_date` and `last_active_date`; the LLM must not infer those dates; (2) `work-mode-classification`, classifying the conversation as `manager`, `executor`, `one_off`, `mixed`, or `unknown`, with confidence and concise evidence; later design discussion must decide whole-conversation versus current-phase classification; (3) `last-activity`, summarizing the last configurable number of meaningful turns into recent work, status, blockers, and likely next action while excluding system/tool/reasoning noise; and (4) `title-assessment`, determining whether the current title reflects the conversation's activity and suggesting, but never automatically applying, a replacement title. Keep each task independently versioned, cached, selectable, and assignable to its own model profile. Dependencies between tasks may be declared in YAML, but one failed task must not invalidate successful independent results.
*AC:* Each task has a Pydantic output contract, synthetic gold examples, deterministic input-selection evidence, and separate stored results; dates exactly match DB metadata; classification always uses the approved label set; last-activity output cites the message range or IDs used; title assessment preserves the source title and does not rename data; normal archive commands make zero LLM calls.

**WP-5.1.3 Local LM Studio AI-task smoke and compatibility fix.** *(accepted 2026-07-15; handoff at `md/handoffs/WP-5.1.3-local-lm-studio-ai-task-smoke-fix.md`; validation at `md/handoffs/reports/WP-5.1.3-validation-review.md`)*
*Objective:* Make all four accepted AI tasks complete through the owner's local LM Studio Qwen3.5-4B runtime on short conversations before investing in prompt evaluation automation.
*Tasks:* Diagnose direct LM Studio, LiteLLM's `lm_studio/` provider route, structured-output compatibility, Chronicle schema/evidence persistence, context handling, and privacy-safe failure diagnostics. Prove the path with invented direct probes and a temporary synthetic DB before running one owner-selected short real conversation. Keep WP-5.1.2 paused.
*AC:* Real local `conversation-summary`, work-mode, last-activity, and title-assessment calls complete and validate on a short synthetic case and one short real conversation; reruns cache; failures are actionable without leaking prompts/results; archive content/FTS remains unchanged; synthetic/full/Ruff/privacy checks pass; report at `md/handoffs/reports/WP-5.1.3-completion-report.md`.

**WP-5.1.4 Windows CI Rich-output wrapping patch.** *(accepted 2026-07-15 after hosted GitHub confirmation; handoff at `md/handoffs/WP-5.1.4-windows-ci-rich-output-wrapping.md`; validation at `md/handoffs/reports/WP-5.1.4-validation-review.md`)*
*Objective:* Restore a green GitHub Actions matrix after a long Windows pytest temporary path caused Rich to wrap the actionable `unknown model profile` diagnostic across physical lines.
*Tasks:* Reproduce the layout dependency deterministically, preserve the domain error and actionable CLI semantics, and make the CLI regression independent of OS path length and terminal width without skips or weakened generic assertions.
*AC:* Long-path/narrow-width synthetic regression passes cross-platform; exit code, task name, missing profile, semantic diagnostic, and no-traceback behavior remain covered; focused/full/Ruff/help/diff checks pass; report at `md/handoffs/reports/WP-5.1.4-completion-report.md`.

**WP-5.1.2A Frozen private development snapshot.** *(accepted 2026-07-20; handoff at `md/handoffs/WP-5.1.2A-frozen-private-development-snapshot.md`; validation at `md/handoffs/reports/WP-5.1.2A-validation-review.md`)*
*Objective:* Freeze the current real archive as an immutable, local-only basis for development-set creation without changing the live product DB.
*Tasks:* Use SQLite's backup API, not a raw live-file copy, to create `.chronicle/eval/dev-v1/source/chronicle-frozen.db`. Record a local manifest with creation time, schema version, aggregate counts, source identity, integrity-check result, and SHA-256 hash. Mark the snapshot read-only by operating policy and never ingest, migrate, or write AI results into it. Keep the snapshot, manifest, hashes, source paths, and all derived private artifacts git-ignored. This package is an operator/data-preparation activity; it does not add product functionality.
*AC:* The frozen DB passes SQLite integrity checking; its hash is stable across repeat verification; aggregate counts match the source at snapshot time; the live DB hash and counts are unchanged by the operation; no private path, manifest, hash, DB, transcript, title, URL, UUID, or derived private artifact is tracked.

**WP-5.1.2B Direct FABLE development references.** *(accepted 2026-07-20 after narrow permission/provenance rework; 30 frozen conversations and 120/120 product-schema-valid silver development references; handoff at `md/handoffs/WP-5.1.2B-direct-fable-development-references.md`; validation at `md/handoffs/reports/WP-5.1.2B-validation-review.md`; depends accepted WP-5.1.2A; supersedes the unexecuted automated two-teacher corpus design in `md/handoffs/WP-5.1.2-real-data-teacher-reference-corpus.md`)*
*Objective:* Create a useful first development corpus directly in a FABLE chat, without implementing teacher-generation or answer-reconciliation code.
*Tasks:* Deterministically select and freeze 30 eligible conversations from the snapshot, stratified for provider, date, and conversation-length coverage and deduplicated before labeling. FABLE may inspect the complete raw content of every selected conversation; the owner has explicitly accepted remote disclosure without a conversation-level secret quarantine for this development set. Apply the exact current WP-5.1.1 YAML prompts and structured contracts to all four tasks: `conversation-summary`, `work-mode-classification`, `last-activity`, and `title-assessment`. Produce 120 conversation-task cases with source conversation/message IDs, deterministic DB dates, task/prompt/schema versions, FABLE model provenance, structured reference output, evidence IDs, timestamps, and explicit failure state where a reference cannot be produced. Do not request or store chain-of-thought. Store the selected-ID manifest, task inputs, references, and reports only under git-ignored `.chronicle/eval/dev-v1/`. No human review or second-teacher consolidation is planned. These outputs are FABLE-generated silver development references, not ground truth and not a final evaluation set.
*AC:* The 30 selected IDs are frozen before reference generation; all 120 expected cases have a schema-valid reference or explicit failure record; DB-owned dates exactly match the frozen source; cited evidence IDs belong to the selected input; FABLE/task/schema provenance is present; the frozen DB remains unchanged; no teacher-generation code is added; no private inputs, outputs, manifests, paths, IDs, or references are tracked. A privacy-safe completion report may contain aggregate counts only.

**WP-5.2A Small local model and runtime integration.** *(depends WP-5.1.2B; candidate list remains owner-TBD)*
*Objective:* Make selected small local models callable through stable runtime integrations before building comparative evaluation automation.
*Tasks:* Define the candidate model/runtime matrix in a later owner discussion. Reuse the application-owned LLM client and LiteLLM profiles for OpenAI-compatible services such as LM Studio, Foundry Local, Ollama, or llama.cpp where verified. Add a dedicated adapter only when a selected host exposes a materially different API. Treat model artifact, version, quantization, runtime, execution provider, context limit, and generation settings as separate configuration and provenance fields. The current local baseline is an Intel Core i7-1185G7 (4 cores/8 threads), 31.7 GB RAM, Intel Iris Xe integrated graphics, no detected NVIDIA runtime, and an installed Qwen3.5-4B LM Studio model; this records feasibility context but does not approve the benchmark shortlist.
*AC:* Every approved candidate completes the four task contracts on a short synthetic case and at least one development conversation; schema failures and runtime errors are captured without changing archive content; model/runtime provenance and local hardware are recorded; normal archive commands remain independent of AI services.

**WP-5.2B Development evaluation harness with Gemini judge.** *(depends WP-5.1.2B and WP-5.2A)*
*Objective:* Compare local candidates on the 120-case development set using deterministic metrics plus a separate Gemini model as an LLM judge.
*Tasks:* Build a reproducible candidate model-profile x AI-task x prompt-variant runner using the accepted task contracts. Use deterministic scoring for schema validity, evidence-ID validity, DB-owned dates, categorical labels/status/title-fit agreement, latency, token usage, and cost when reported. Use a different Gemini model, called through LiteLLM, for rubric-based scoring of free-text factual coverage, unsupported claims, recent-state capture, and suggested-title quality. Configure the judge by local YAML model/profile alias; API credentials remain environment variables and are never stored in config. Persist judge model identity, prompt/rubric version, generation settings, structured scores, explanations limited to concise verdict rationale, failures, and raw candidate/reference associations locally. FABLE is the teacher and Gemini is the judge; do not use the candidate model to judge itself. This 30-conversation corpus is available for prompt development and model selection, so its results are development metrics only.
*AC:* One command can resume a bounded evaluation run; reruns cache by full candidate/task/prompt/reference/judge identity; deterministic and judge-based metrics are reported separately; all 120 cases are accounted for by score or explicit failure; privacy-safe reports expose only aggregate results; no API key or private case content is tracked; the live and frozen source DBs remain unchanged.

**WP-5.2C Remote execution and later independent evaluation.** *(deferred until hardware and transfer decisions are approved)*
*Objective:* Reproduce selected model runs on a stronger remote machine and later create an untouched evaluation set for defensible final comparisons.
*Tasks:* Define the remote machine, runtime installation, encrypted/private transfer procedure, data-retention boundary, and hardware capture after local integration is understood. Transfer only the explicitly approved frozen development bundle, not the complete archive. Use the 30-conversation corpus for development runs only. Create a separate, newly selected and untouched evaluation set after prompts/models are frozen; its size, teacher process, and release/reporting policy remain TBD.
*AC:* Remote runs record exact hardware/runtime/model/config identity and reproduce the same case fingerprints; transfer and deletion are owner-approved and documented locally; development and later evaluation results are never combined; no final or publication-grade quality claim relies only on the 30-conversation development set.

**WP-5.3 `--smart` query rewriting (optional flag, off by default).**
*Tasks:* `worktrail search --smart` (and an MCP parameter): local model rewrites a vague query into FTS terms + date hints (structured output); hard 2 s timeout → raw-query fallback. **Not on by default** — no LLM call on the default search path.
*AC:* 10 hand-written "vague memory" queries: rewritten beats raw on ≥7; LM Studio down → silent raw fallback.

**WP-5.4 (stretch spike) Phi Silica feasibility memo.** C#/`winrt` interop investigation only; memo in `md/`. [Microsoft Learn](https://learn.microsoft.com/en-us/windows/ai/apis/phi-silica).

**WP-5.5 Distilled knowledge extraction.** *(depends WP-5.1 — same task runner, extra schema)*
*Objective:* Extract *decisions, solutions, and open questions* from conversations into `knowledge_items` — a personal solutions database, arguably more valuable than the chats themselves.
*Tasks:* `KnowledgeItems` Pydantic schema (0–5 items per conversation; kind ∈ decision/solution/open_question; statement ≤ 40 words + short context); define it as a separately versioned YAML task rather than overloading the summary prompt; index statement+context in FTS; `worktrail search --kind solution` filter; `worktrail knowledge` list view.
*AC:* On 30 gold-labeled fixtures, ≥70% of hand-identified decisions/solutions captured, <20% hallucinated items (measure both!); empty result is a valid output (most chit-chat has no knowledge items).

**WP-5.6 Weekly digest.** *(depends WP-5.1)*
*Objective:* "What did I work on, where did I leave off" — generated fully offline.
*Tasks:* `worktrail digest [--days 7]`: gather the window's conversations (all sources) → summaries + knowledge items → one structured local-model pass → markdown digest (themes, per-project activity, open questions carried forward, links/ids); write to stdout + `md/digests/`; document a weekly Task Scheduler line next to the nightly `collect` docs. Mention the daily "mission control" variant (`--days 1`) in docs.
*AC:* Digest over a fixture week groups by topic, cites conversation ids, runs < 2 min on a 3B model; no LM Studio → clear message, no crash.

**WP-5.7 Project brief.** *(depends WP-5.1 and project/link-back schema)*
*Objective:* `worktrail brief --project X` produces forward-looking, paste-able context for the next AI session.
*Tasks:* Reuse summaries + knowledge items + recent activity to generate a compact brief with recent decisions, open threads, next steps, and relevant conversation ids/links. Fully offline; same graceful LM Studio failure behavior as digest.
*AC:* Fixture project produces a useful next-session brief with cited conversation ids; no cloud dependency; no crash when enrichment is unavailable.

### M6 — Release & polish
**First-release checkpoint: complete.** Chat Chronicle v0.1.0 was prepared in a
separate release thread, committed as `1f3fbce`, tagged and pushed as `v0.1.0`, and
made publicly available on GitHub. The source release includes the release-quality
README, AI-task guide, prepared LinkedIn article, and owner-reviewed sanitized
manager-chat artifact. `md/release-1-planning-note.md` records the decisions and
privacy process. This source release deliberately retains the Chat Chronicle name;
WorkTrail rename, PyPI/pipx publication, MCP, and benchmark work remain deferred.

**WP-6.1 — v0.1.0 source release.** Release-quality five-minute README, supported-source/export instructions, honest limitations, separate advanced AI-task guide, LinkedIn article, sanitized manager-chat artifact, full validation, `v0.1.0` tag, and GitHub publication under the current Chat Chronicle name. WorkTrail rename, PyPI/pipx publication, demo GIF, and MCP setup remain later release work.
*AC:* A Windows user can clone the repository, run `poetry install`, initialize, collect supported sources, and perform the first search using the README alone. Core archive commands have zero AI dependency; private exports and raw histories remain untracked; full tests, Ruff, pre-commit, package build, and privacy scans pass before tagging.

### v2 roadmap — AI deepening (committed direction, starts only after v0.1 ships)
The story arc: *v1 proves the boring archive; v2 makes it intelligent — and measures every step.* Sequenced:

**V2-1 Retrieval eval harness (built first, before any upgrade).** 30–50 real questions about the developer's own archive with known correct conversations → recall@k / MRR per search mode. Every subsequent feature must move this number, not vibes. Extend `bench/` — same reporting pattern as WP-5.2.

**V2-2 Embeddings + hybrid search.** Embed *summaries* (not bodies) into sqlite-vec; hybrid = FTS5 top-50 → cosine re-rank ([patterns](https://alexgarcia.xyz/blog/2024/sqlite-vec-hybrid-search/index.html)). Embedding model: **free local open-weights, served via LM Studio `/v1/embeddings`** through the same internal `LLMClient`/LiteLLM boundary where supported (e.g. `bge-small-en-v1.5`, `nomic-embed-text-v1.5`, or `all-MiniLM-L6-v2` — check MTEB at build time; differences are marginal at this corpus size). Fallback runtime: `sentence-transformers` in-process behind a `[vec]` extra. Scale reality: 5k summaries × 384 dims ≈ 8 MB, one-time minutes of CPU — free local is the *correct* tool here, not a compromise. `worktrail search --mode fts|hybrid`; A/B against V2-1 harness.

**V2-2.5 Git correlation.** Link conversations ↔ repo/branch/commits via repo path + time window: git says what changed, chats say why. Do not squeeze into v1.

**V2-3 `worktrail chat` — agentic RAG over the archive, fully offline.** A local model in a tool-calling loop over the **same retrieval API** used by the CLI and MCP server (one retrieval layer, three consumers). Iterative: model decides queries, reads hits, refines (search "CORS" → read snippet → search the error string it found), answers with conversation-id citations. Bench extension: "agentic loop competence" of 3–4B models — which small models can drive a tool loop without derailing (underexplored; strong article material).

### Post-v1 backlog (unscheduled — timeboxed spikes only if pulled forward)
In rough priority order: **Gemini Takeout/My Activity importer** (chat text lives under My Activity filtered to Gemini Apps, not necessarily the plain Gemini product checkbox) · **Codex cross-client workspace-association spike** (RS-3: determine whether VS Code/Codex Desktop visibility is keyed by path, repository identity, local metadata, or service association before changing project grouping) · **VS Code/Copilot Chat extractor** (if practical) · **history download helper for providers that support export automation or documented export flows** · **host-bundled local-model adapters** for Edge Prompt API models (Phi-4-mini and prerelease Aion-1.0-Instruct) and Chrome Gemini Nano, which require browser JavaScript bridges rather than LiteLLM HTTP; Phi Silica remains WP-5.4/Windows App SDK scope · **Markdown/Obsidian export** of digests + knowledge items · **local cross-encoder reranker** (e.g. bge-reranker; precision win, benchmark against V2-1) · **entity extraction** (technologies/repos/error codes → filterable facets) · **cross-provider threading** (local model links continuation chats into storylines) · **temporal/intent query parsing on by default in chat** · **live logging + marker join** (the shelved Version B experiment — revisit only once the archive is proven daily-useful; still excellent article material) · **OpenTelemetry instrumentation** (inward-facing: spans per adapter run/tool call, TTFT/TPS via GenAI semantic conventions) · **Class C cache extractors** (forensic, experimental) · **browser-extension capture** (study OpenChat first).

**Sequencing & calendar** (~6 focused hrs/week): prototype fast path = WP-1.4 → CO-1 → WP-2.1 → WP-3.1 → real-history demo, accepted. Claude project metadata, WP-1.5/WP-1.6 usability polish, WP-2.3.2 search punctuation hardening, WP-5.1 configurable AI-task infrastructure, WP-5.1.1 production task contracts, WP-5.1.3 local LM Studio compatibility/smoke, WP-5.1.4 CI portability, and the public v0.1.0 source release are accepted. The resumed AI-development sequence is WP-5.1.2A frozen snapshot → WP-5.1.2B direct FABLE references → WP-5.2A selected local runtime integrations → WP-5.2B Gemini-judged development evaluation. The local model shortlist and WP-5.2C remote machine remain TBD. A separate untouched evaluation set follows only after prompts and models are frozen. Cursor, Gemini history import, MCP, WorkTrail rename, and PyPI publication remain later work unless explicitly reprioritized.

---

## 7. LinkedIn Series Plan

Rules: post *after* the milestone works (show, don't promise) · one visual per post · name prior art generously · end with a question · repo link in first comment. The series arc is the honest engineering story: **architecture surviving contact with reality.**

**Progress-share checkpoint — Friday, 17 July 2026.** Share the accepted real-history prototype, WP-5.1 YAML/LiteLLM foundation, and the four accepted WP-5.1.1 task contracts. Public evidence may show the multi-source architecture, supported providers, aggregate counts, privacy-safe terminal output for `stats`, `recent`, or search, synthetic/config-only AI-task discovery, and the task names/purposes. Redact local usernames, absolute paths, conversation titles, snippets, URLs, UUIDs, transcript text, prompts/results from real histories, and private model/account configuration. Clearly state that real-model quality evaluation has not yet been completed; do not present WP-5.1.2 references or WP-5.2 benchmark results as available.

**LP-1 (after M2/prototype) — "AI tools are multiplying, but the activity trail is missing."**
Hook: the original AI-generated plan assumed MCP clients passively stream telemetry — they don't, and models don't know their own conversation IDs. Content: the three-stage evolution (impossible telemetry → clever marker workaround, designed then shelved → boring batch-first adapters), why the useful product is an activity/context ledger, and why "the boring architecture is the one that ships." Visual: the A→B→A+ evolution diagram. CTA: "Where does your AI work trail disappear?"

**LP-2 (after M2) — "SQLite FTS5 is criminally underrated."**
The whole search layer is stdlib + one virtual table: bm25, porter tokenizer, snippet(); p95 latency on a real archive. Visual: terminal GIF of `worktrail search`. Code-forward — the post developers save.

**LP-3 (after M3) — "Your AI coding tools keep full transcripts on your disk. Here's where."**
The forensics post. Content: `worktrail scan-local` output; Claude Code's JSONL in `~/.claude/projects`, Cursor's workspaceStorage SQLite; the Class A/B/C source model; copy-before-read and format-drift defenses; privacy implications (it's *your* data — index it). Visual: scan-local screenshot. High curiosity factor.

**LP-4 (after M5) — "I benchmarked 5 local SLMs on my own laptop for real work. Results surprised me."**
The data post — highest expected reach. WP-5.2 results table; the JSON-adherence gap with vs without schema enforcement (that gap is the story); TPS/TTFT on consumer hardware. Visual: one clean chart. Caveat hardware honestly.

**LP-5 (after WP-4.1/M6) — "I asked Claude what I was working on in Cursor last month. It answered." (capper)**
The MCP demo: 30–45 s video, question in Claude Desktop → `search_chats` → transcript. Content: 20 lines of FastMCP, why recall-not-capture is the right MCP boundary, lessons from the whole arc, invitation to contribute + link to the long-form article.

**Long-form article** (dev.to or blog, cross-post Medium): *"Building a cross-tool AI chat archive: exports, local stores, local SLMs, and MCP"* — merge LP-1+3+4 with full depth; the benchmark section alone is HN-submittable. Draft incrementally in `md/article.md`, ~1 hr per milestone while fresh.

**v2 series (post-v0.1, sketch):** the AI-deepening arc yields at least three more posts — "I built an eval harness before adding any AI search" (V2-1, methodology post) · "Hybrid search on a laptop: measured, not vibed" (V2-2 with recall@k deltas) · "Can a 3B model drive an agentic tool loop?" (V2-3 bench results). Plus WP-5.5/5.6 material: "my AI conversations became a solutions database."

---

## 8. Risks & Mitigations

| Risk | Mitigation |
| --- | --- |
| Class B format drift (Claude Code/Cursor internals change any release) | Spike-first format memos; pinned per-version fixtures; parse-don't-validate; degrade to "source skipped + warning" |
| Cursor SQLite locked while running | Copy-before-read pattern (WP-3.2) |
| Adapter framework over-engineering | Design rule 2: abstraction extracted only in a dedicated refactor after repeated integration shape is proven, never inside source-specific parser work |
| Export formats change silently | Fixtures pinned; per-record `errors_json`; `ingest_runs` makes breakage visible |
| MCP recall slips behind "more important" work | Time fence: within 2 weeks of WP-2.1 acceptance (§6 M4) |
| Privacy: chat archives are sensitive | Local-only; `.gitignore` DBs/exports; synthetic fixtures only; README privacy section |
| FABLE references mistaken for ground truth | Name WP-5.1.2B output silver development references; record model/task/schema provenance and failures; do not claim final quality from the 30-conversation development set; create a separate untouched evaluation set after prompt/model selection |
| Teacher or judge calls expose private archive data | Owner explicitly authorizes FABLE to receive all selected raw conversations without conversation-level quarantine and Gemini to judge the derived cases; restrict disclosure to the frozen 30-conversation bundle, keep credentials in environment variables, retain a local disclosure/provenance record, and never track private inputs or outputs |
| LLM-as-judge bias or instability | Use a different Gemini model from the FABLE teacher through a separately configured LiteLLM profile; version the rubric and judge settings; keep deterministic and judge metrics separate; preserve failures and score coverage |
| Development-set overfitting | Freeze all 30 selected IDs before FABLE labeling; treat all 120 cases as development data; create a separate untouched evaluation set only after prompts and candidate models are frozen |
| LM Studio not running | Enrichment/`--smart` optional everywhere; health-check with actionable error |
| Scope creep (live logging nostalgia, Class C, TUI…) | All in post-v1 backlog with explicit re-entry criteria ("archive proven daily-useful") |
| OpenChat/OpenMemory ship overlapping features | Differentiation = coding-agent coverage + adapter architecture + benchmark content; learning/content value survives regardless |
| Benchmark contested ("wrong quant/settings") | Publish exact model files, quant, settings, hardware; frame as "on my machine," invite PRs |

---

## 9. Reference Library

**Research records:** `md/research/RS-1-chat-history-access-task.md` and `md/research/RS-1-chat-history-access-findings.md` record the Windows 11 chat-history access research spike: official export paths, durable local stores, local-cache caveats, automation ceilings, Claude Code retention settings, and owner data-retrieval status. Treat these files as planning inputs for source defaults, `scan-local`, WP-3.1 Claude Code extraction, Codex `.jsonl.zst` follow-up, and possible Copilot CSV backlog work.
**MCP / SDK:** [MCP spec & docs](https://modelcontextprotocol.io) · [python-sdk (mcp 1.x)](https://github.com/modelcontextprotocol/python-sdk) · [FastMCP](https://github.com/PrefectHQ/fastmcp) · [OpenAI MCP connector rules](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)
**Exports:** [ChatGPT conversations.json structure](https://community.openai.com/t/decoding-exported-data-by-parsing-conversations-json-and-or-chat-html/403144) · [mapping-tree Q&A](https://community.openai.com/t/questions-about-the-json-structures-in-the-exported-conversations-json/954762) · [export scripting example](https://gist.github.com/ocombe/1d7604bd29a91ceb716304ef8b5aa4b5)
**Class B stores:** undocumented — WP-3.1/3.2 research spikes produce the authoritative format memos in `md/` (verify paths/format on the dev machine; do not trust third-party blog posts over local inspection). Required parser-prior-art reading before WP-3.1/3.2: [Agent Sessions](https://github.com/jazzyalex/agent-sessions), [claude-record](https://github.com/davidglogan/claude-record), and [codex-trace](https://github.com/PixelPaw-Labs/codex-trace).
**Search:** [SQLite FTS5 official docs](https://sqlite.org/fts5.html) · [sqlite-vec](https://github.com/asg017/sqlite-vec) · [hybrid FTS+vector patterns](https://alexgarcia.xyz/blog/2024/sqlite-vec-hybrid-search/index.html) · [Simon Willison's writeup](https://simonwillison.net/2024/Oct/4/hybrid-full-text-search-and-vector-search-with-sqlite/)
**Local SLMs:** [LiteLLM OpenAI-compatible endpoints](https://docs.litellm.ai/docs/providers/openai_compatible) · [LM Studio structured output](https://lmstudio.ai/docs/developer/openai-compat/structured-output) · [LM Studio dev docs](https://lmstudio.ai/docs/developer) · [Foundry Local](https://learn.microsoft.com/en-us/azure/foundry-local/what-is-foundry-local) · [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) · [Phi-4-mini-instruct](https://huggingface.co/microsoft/Phi-4-mini-instruct) · [Gemma-3-4B-it](https://huggingface.co/google/gemma-3-4b-it) · [Phi Silica API](https://learn.microsoft.com/en-us/windows/ai/apis/phi-silica) · [Edge Prompt API](https://learn.microsoft.com/en-us/microsoft-edge/web-platform/prompt-api) · [Chrome Prompt API (Gemini Nano)](https://developer.chrome.com/docs/ai/prompt-api)
**Prior art:** [OpenMemory MCP](https://mem0.ai/blog/introducing-openmemory-mcp) · [OpenChat](https://github.com/p0u4a/openchat) · [Agent Sessions](https://github.com/jazzyalex/agent-sessions) · [LLMLingua](https://www.llmlingua.com/) · [RouteLLM](https://github.com/lm-sys/RouteLLM)

## 10. Explicitly Rejected

Do not relitigate these unless a future change order explicitly reopens them: Screenpipe-style screen capture (Class C by another name), OpenWebUI consolidation (changes workflow, does not rescue history), Databricks Omnigent / Createst.ai (different problem, not local-first), Compositor (unverified pending a reference link), and live logging / marker join (still shelved per Appendix A.6).

---

## Appendix A — How this plan came to be (critique + evolution record)

Kept as the honest history behind the plan; also the raw material for LP-1 and the article. Sections A.1–A.5 record the first two stages as they were decided at the time; A.6–A.7 record the second reversal that produced the current Plan A+.

### A.1 The original AI-generated plan and what was wrong with it

The project began as an AI-generated proposal: a "Cross-Client Chat Meta-Logger MCP Server" where "any MCP-enabled client logs session telemetry (client name, conversation ID, timestamps) to your database," plus two siblings (a token-compression "Context Janitor" and a local-model capability router). Fact-checking (2026-07-09) found:

**Fatal architecture flaw.** MCP servers are passive — they receive only explicit tool calls, never a telemetry stream. Worse, models don't know their own conversation IDs/URLs, so the plan's killer feature (deep-link back to the thread) was unimplementable as designed. The promised finale demo could not be built.

**Client-support reality.** ChatGPT supports only remote HTTPS MCP servers ([OpenAI docs](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)); the Gemini app only gained MCP-style connected apps in June 2026. Only the Claude ecosystem makes local stdio servers easy.

**The "nothing similar exists" premise was false.** [OpenMemory MCP](https://mem0.ai/blog/introducing-openmemory-mcp) (cross-client local memory) and [OpenChat](https://github.com/p0u4a/openchat) (browser extension capturing chatgpt.com/claude.ai into a local MCP server) are close prior art; idea 2 was largely [LLMLingua](https://www.llmlingua.com/) (Microsoft, 2023); idea 3 was [RouteLLM](https://github.com/lm-sys/RouteLLM), a stale niche.

**Stale/incorrect technical details.** `mcp ^0.1.0` (SDK was at 1.28.x, FastMCP the de-facto standard); `marvin ^2.0.0` (at 3.x, and the wrong tool vs native structured output); `VARCHAR[]` columns in a schema claimed to run on SQLite (no array type); "semantic search" promised with no embeddings anywhere in the design; "RAG = infinite effective context" (marketing, not engineering); reference material pasted twice; an evaluation section disconnected from all three build ideas. Model facts largely checked out (Gemini Nano 9,216-token context per [Chrome docs](https://developer.chrome.com/docs/ai/prompt-api); Phi Silica 3.3B/4K per [Microsoft Learn](https://learn.microsoft.com/en-us/windows/ai/apis/phi-silica)) — with the caveat that Phi Silica needs Copilot+/supported-GPU hardware.

### A.2 The first pivot (plan v1 — "Batch Journal")

The pain point survived the critique — siloed, unsearchable chat history is real, and the author has it personally. The fix was architectural honesty: capture via official data exports (robust, works day one) instead of imaginary MCP telemetry; MCP reserved for what it's actually good at (recall); local SLM for enrichment, doubling as benchmark content; positioning stated openly against OpenMemory ("facts about you") and OpenChat ("extension capture").

### A.3 The discussion that produced plan v2 ("Version B — Live Journal")

Four questions were raised against v1's acknowledged weakness (batch-only = stale data, local LLM sidelined):

1. **"Can skills make each chat keep a local log?"** → Partially: a Claude skill could drive a `log_activity` MCP tool for live journal entries. Cooperative and Claude-only.
2. **"How do we work around the model not knowing its own thread?"** → **The marker join:** the model can't *read* its conversation ID but can *write into the conversation* — echo a returned marker (e.g. `⟦CC-7f3a9⟧`), and the next export ingest joins the live entry to the real conversation retroactively. No existing project was found shipping this.
3. **"Can we use OpenTelemetry?"** → Not for capture (consumer chat apps emit nothing to you); yes inward-facing as post-v1 engineering + article material.
4. **"The local LLM feels sidelined."** → Promoted to query rewriting on every search, plus a post-v1 list (embeddings, digests, offline RAG TUI).

Three scopes were compared (A batch-only / B live journal / C full vision) and **B was chosen** on the argument: batch-only fails the *"will you still use it in month three?"* test because data is always stale, and live logging was the only available fix — with graceful degradation to batch when cooperation fails.

### A.4 Version B in one paragraph (as adopted, later shelved)

Claude ecosystem = live tier (`log_activity` tool + ~15-line skill + marker echo, searchable in seconds, deep links attached at next export via marker scan; fuzzy timestamp/title fallback); all other providers = batch tier via exports; local SLM on the search hot path via query rewriting. Cost estimate: +1.5 weeks over batch-only.

### A.5 What Version B meant in practice

Claude as the live-journal citizen; ChatGPT/Gemini as batch citizens; the user's only unavoidable manual step being periodic export requests; two-tier install (~5 min search-only, ~15 min full) with graceful degradation at every layer.

### A.6 The second reversal: B → A+ (this plan)

A further review (2026-07-09) checked what chat tools actually store **locally on Windows**, and the findings changed the calculus that had justified B:

**The new fact — Class B durable local stores.** Consumer cloud-chat apps keep only fragile, partial caches (IndexedDB/LevelDB, wiped on logout/update — Class C, not buildable-upon). But **coding agents keep durable, complete local transcripts**: Claude Code writes JSONL session logs under `~/.claude/projects`; Cursor stores chat in workspaceStorage SQLite; VS Code/Copilot may have usable workspace state. These are **passive** sources — no export button, no model cooperation, no skill, no marker.

**Why this kills B's justification.** B existed to fix staleness, and live logging was believed to be the only fix. Extractors over Class B stores fix staleness *more reliably than live logging ever could* — for exactly the sources that carry most of a developer's valuable history. The month-three test now passes without B: `chronicle collect` keeps coding-agent history automatically fresh; only web-chat history waits for export cadence, which is acceptable. B's complexity (Claude-specific, cooperative, vulnerable to missed calls/echoes/edits/export mangling) no longer buys anything proportionate.

**The accompanying critique of B** (accepted): live capture was Claude-specific, dependent on model behavior, not generic across ChatGPT/Gemini/Copilot/Cursor, and interesting technically but not necessary for the useful product. The plan itself had admitted batch was the reliable fallback — *if batch is the reliable fallback, batch should be the foundation.*

**The resulting architecture — Plan A+:** batch-first, source-agnostic core, pluggable adapters (importer/extractor/collector vocabulary), three source classes (A official exports = v1; B durable local stores = v1.1; C forensic caches = post-v1 experimental only), manual or Task-Scheduler collection, enrichment and MCP recall as optional later layers. Removed/demoted from v1: Claude skill, `log_activity`, `live_entries`, marker join and echo, fuzzy matching, ChatGPT MCP bridging (docs-only), query rewriting on the default search path.

### A.7 Final decision and the four amendments

Plan A+ was adopted with four amendments from review:

1. **Abstraction discovered, not designed** — write source adapters as concrete code; extract `AdapterProtocol` only in a dedicated refactor once repeated adapter wiring proves the shape. Guard against the adapter framework becoming its own scope creep.
2. **Class B is *less* stable than Class A** — undocumented internals with no export contract. Spike-first format memos, pinned per-version fixtures, parse-don't-validate, copy-before-read for locked SQLite.
3. **Time-fence MCP recall** — it's ~1 evening on FastMCP, a core learning goal, and the demo; land within 2 weeks of CLI search working rather than letting "v1.3" slide.
4. **Scheduling = Windows Task Scheduler + docs** — never a daemon.

Minor accepted notes: coding-agent conversations have no URLs (`open` renders local transcripts); `--smart` query rewriting stays off by default (the "hot path" enthusiasm of v2 added latency + a hard dependency for marginal gain).

**Preserved deliberately:** the marker join stays in the post-v1 backlog and in this appendix — "designed it, then shelved it for good reasons" is itself the strongest content in the series (LP-1).

### A.8 The AI-enrichment review (plan v3.1)

With A+ settled, a follow-up review asked how to deepen the AI side without breaking the "boring core first" principle — the author being an AI engineer, the AI surface *is* part of the learning goal. Candidates considered: embeddings/hybrid search, a local cross-encoder reranker, temporal/intent query parsing, entity extraction, cross-tool threading, distilled knowledge extraction, a weekly digest, an agentic `chronicle chat`, and a retrieval eval harness.

Decisions:
- **Into v1.2** through the generic AI-task runner: the owner's first conversation-intelligence catalog (summary with deterministic dates, work-mode classification, last-activity state, and title assessment), then **distilled knowledge** (WP-5.5 — decisions/solutions/open-questions into `knowledge_items`; a personal solutions database) and **weekly digest** (WP-5.6 — offline "what did I work on, where did I leave off").
- **Committed v2 roadmap** (post-v0.1, in order): **eval harness first** (V2-1 — every retrieval upgrade must move recall@k, not vibes), then **embeddings + hybrid search** (V2-2 — free local open-weights embedding models via LM Studio `/v1/embeddings`; at personal-archive scale, ~8 MB of vectors, local is the correct tool rather than a compromise), then **`chronicle chat`** (V2-3 — agentic RAG: a local model in a tool loop over the same retrieval API serving the CLI and MCP; plus an "agentic loop competence" bench for 3–4B models).
- **Deferred to backlog:** reranker, entity extraction, threading, default-on query parsing.

Clarification recorded during the discussion, worth restating in the README: in v1 the *only* AI inside the product is an explicitly invoked, YAML-defined task runner. Prompts and model profiles are external configuration; validated schemas, privacy gates, provenance, and DB writes remain application-owned. The normal search path stays lexical and makes zero LLM calls. Service use defaults to a local model, while stronger remote models are restricted to explicitly authorized development/evaluation runs. The product's restraint is the feature — v1 ships with zero mandatory AI dependencies and gains intelligence in measured, benchmarked steps.

**Guiding principle, restated:** build the boring useful archive first. The boring architecture is the one that ships — then make it intelligent, and measure every step.
