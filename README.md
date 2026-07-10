# Chat Chronicle

*A local-first, searchable archive of your AI conversations — populated by source-specific importers and extractors, normalized into one SQLite/FTS journal, optionally enriched by a local SLM and recallable from MCP clients.*

> **Status: M1 in progress.** The DB/model layer is implemented; importer and search commands are still stubs. See [`md/master-plan.md`](md/master-plan.md) for the full plan and [`md/development-ledger.md`](md/development-ledger.md) for execution status.

## Why

AI work is scattered across ChatGPT, Claude, Gemini, and coding agents (Claude Code, Cursor, Copilot Chat). Each stores history in an isolated, poorly-searchable silo. Chat Chronicle indexes *events* — which conversation, when, in which tool, and how to get back to it.

A **source-agnostic core** is fed by **pluggable, source-specific adapters**. Adding a new source means adding one adapter, not changing the system.

## Positioning

| Project | What it does | How we differ |
| --- | --- | --- |
| [OpenMemory MCP (mem0)](https://mem0.ai/blog/introducing-openmemory-mcp) | Stores distilled facts/preferences about you | We index events, not memories — an archive with a way back to the thread. |
| [OpenChat](https://github.com/p0u4a/openchat) | Browser extension captures chat traffic | We use official exports plus durable local stores; no extension, and we reach coding agents. |
| Provider built-in search | Per-silo only | Cross-provider and cross-tool, local, private, scriptable. |

## Quickstart

```bash
poetry install
poetry run chronicle --help
```

## Local development database

The database is a local SQLite file. For this repo, keep development databases under the project directory and out of git:

```powershell
poetry run python -m chat_chronicle.db init --db-path .\.chronicle\chronicle.db
poetry run python -m chat_chronicle.db init --db-path .\.chronicle\chronicle.db
```

The second run should be safe and should report the same schema version. The `.db` file is ignored by git.

To point commands at this project-local DB for the current PowerShell session:

```powershell
$env:CHAT_CHRONICLE_DB = "C:\work\Github\mcp-chat-chronicle\.chronicle\chronicle.db"
poetry run python -m chat_chronicle.db path
```

Expected path:

```text
C:\work\Github\mcp-chat-chronicle\.chronicle\chronicle.db
```

## CLI surface (v1 target)

```bash
chronicle ingest path/to/export.zip --provider auto   # one official export file
chronicle ingest-folder path/to/exports               # sweep a drop folder
chronicle collect                                     # run all enabled sources
chronicle scan-local                                  # read-only: what exists on this machine?
chronicle stats                                       # counts per source, last runs
chronicle search "docker network"                     # FTS5, ranked, snippets
chronicle open <result-id>                            # deep link or transcript view
```

## Stack, and what we deliberately did not choose

Python 3.11+ · Poetry · Pydantic v2 · Typer + Rich · stdlib `sqlite3` + FTS5 · pytest · ruff · pre-commit · GitHub Actions (Windows + Ubuntu).

Optional extras: `enrich` (local SLM via LM Studio's OpenAI-compatible server), `mcp` (FastMCP recall server). v1 ships with zero AI dependencies.

Not chosen: **DuckDB** (an analytics engine, wrong fit for text recall) · **Marvin** (native `json_schema` structured output teaches more) · **a browser extension** (fragile; exports and extractors cover the same ground) · **a background daemon** (a one-line Windows Task Scheduler entry suffices).

## Privacy

Everything stays on your machine. Local databases and exports are git-ignored; only synthetic fixtures are ever committed. No real chat data lives in this repository.

## Limitations (honest)

- Web-chat history (ChatGPT, Claude, Gemini) is only as fresh as your last export request. Coding-agent history refreshes automatically because those tools keep durable local transcripts.
- Coding-agent conversations have no URLs — `chronicle open` renders a local transcript for those.
- Local-store formats are undocumented and can change with any tool release; a format change degrades to "source skipped with a warning," never a crash.

## License

MIT — see [LICENSE](LICENSE).
