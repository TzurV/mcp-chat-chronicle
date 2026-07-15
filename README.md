# Chat Chronicle

*A local-first, searchable archive of your AI conversations — populated by source-specific importers and extractors, normalized into one SQLite/FTS journal, with optional YAML-defined AI tasks and MCP recall planned as separate layers.*

> **Status: core real-history prototype accepted; configurable AI-task foundation is next.** The local DB, official ChatGPT and Claude export importers, OpenAI Codex and Claude Code local extractors, single-source and parent-folder ingest, config/init/collect, scan-local inventory, stats, search, phrase search, open, and recent-activity CLI paths are implemented and exercised against the owner's real archive. Claude project metadata is linked only when reliable conversation references exist. See [`md/master-plan.md`](md/master-plan.md) for the full plan and [`md/development-ledger.md`](md/development-ledger.md) for execution status.

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

## One-command workflow: `init` + `collect`

For routine use, two commands set up and refresh the archive:

```powershell
poetry run chronicle init
poetry run chronicle collect
```

`chronicle init` is the explicit setup step. Package install never creates
files or folders; `init` does. It creates, if missing:

```text
.chronicle/
.chronicle/config.yaml        # generated, git-ignored local config
.chronicle/ai-tasks.yaml      # external AI task prompts and policy
.chronicle/ai-models.yaml     # external model/provider profiles
.chronicle/chronicle.db       # DB schema is initialized only if the file is new
exports/
exports/openai/
exports/claude/
```

`init` never overwrites an existing `config.yaml` unless you pass `--force`,
and never deletes or recreates an existing database. Useful flags:

```powershell
poetry run chronicle init --config .\.chronicle\config.yaml
poetry run chronicle init --force
```

`chronicle collect` reads `.chronicle/config.yaml` and ingests every enabled
configured source using the same accepted adapters as `chronicle ingest`:

- official export folders (`exports/openai`, `exports/claude`) are swept for
  all supported child sources;
- local stores (`%USERPROFILE%\.codex`, `%USERPROFILE%\.claude\projects`) are
  each ingested as one source.

Missing configured paths are reported and skipped, never fatal. Reruns are
idempotent — unchanged conversations are skipped, not duplicated. Output shows
each source's provider/path/status plus aggregate seen/added/updated/skipped/
errors counts.

```powershell
poetry run chronicle collect --config .\.chronicle\config.yaml
poetry run chronicle collect --db-path .\.chronicle\chronicle.db
```

### Where config lives and what it stores

The tracked template [`chronicle.default.yaml`](chronicle.default.yaml)
documents the schema (and contains no private absolute paths). `init` copies it
to a git-ignored local `.chronicle/config.yaml`. The config stores:

- `paths.db` — default database path;
- `paths.exports_root` — root under which export folders live;
- `engines.<name>.enabled` / `.interested` — which engines `collect` ingests
  and which you want supported (interest records intent for the future
  download helper; it does not change parsing);
- `sources.<name>` — `provider` / `kind` (`official_export` or `local_store`) /
  `path` entries.

Path values support `${USERPROFILE}`/`$HOME` environment variables, `~` home
expansion, and relative paths resolved from the project root.

### DB path precedence

Every command that opens the database (`ingest`, `collect`, `stats`, `search`,
`recent`, `open`) resolves the database path in this order (highest first):

1. CLI `--db-path`;
2. `CHAT_CHRONICLE_DB` environment variable;
3. config YAML `paths.db` (from `.chronicle/config.yaml` when present);
4. built-in default `.chronicle/chronicle.db`.

Read commands still work without a config file — they fall through to the
built-in default. When a config file is present it must be valid; a malformed
config surfaces a clear error rather than silently using the default.

> Cloud chats (ChatGPT, Claude web) still require a manual export/download into
> `exports/...` before `collect` can ingest them. An automated history-download
> helper is a future backlog item, not yet scheduled.

### Scheduling recurring collection (optional, Windows Task Scheduler)

There is no background daemon by design. To refresh the archive automatically,
register a one-line **Windows Task Scheduler** job that runs `chronicle collect`
on a schedule. This is optional and you run it yourself — Chat Chronicle never
creates or registers a scheduled task for you.

Daily at 20:00, from your project directory:

```powershell
schtasks /Create /SC DAILY /ST 20:00 /TN "ChatChronicleCollect" /TR "powershell -NoProfile -ExecutionPolicy Bypass -Command \"Set-Location 'C:\work\Github\mcp-chat-chronicle'; poetry run chronicle collect\""
```

Adjust the path, time, and frequency (`/SC HOURLY`, `/SC WEEKLY`, ...) to taste.
Inspect, run, or remove it with:

```powershell
schtasks /Query /TN "ChatChronicleCollect"
schtasks /Run   /TN "ChatChronicleCollect"
schtasks /Delete /TN "ChatChronicleCollect" /F
```

Because `chronicle collect` is idempotent, running it on a schedule only adds
new conversations and never duplicates existing rows.

## Local development database

The database is a local SQLite file. For this repo, keep development databases under the project directory and out of git:

```powershell
poetry run python -m chat_chronicle.db init --db-path .\.chronicle\chronicle.db
```

Re-running the same command should be safe and should report the same schema version. The `.db` file is ignored by git.

To point commands at this project-local DB for the current PowerShell session:

```powershell
$env:CHAT_CHRONICLE_DB = "C:\work\Github\mcp-chat-chronicle\.chronicle\chronicle.db"
poetry run python -m chat_chronicle.db path
```

Expected path:

```text
C:\work\Github\mcp-chat-chronicle\.chronicle\chronicle.db
```

## CLI Surface

```bash
chronicle init                                         # create .chronicle/, config, DB, export folders
chronicle collect                                      # ingest all enabled configured sources
chronicle scan-local                                   # read-only source inventory
chronicle ingest path/to/export.zip --provider auto    # ingest one supported source
chronicle ingest path/to/exports --provider auto       # sweep a parent folder for supported sources
chronicle stats                                        # counts per source, last runs
chronicle search "docker network"                      # FTS5, ranked, snippets
chronicle search --phrase "YOU are the MANAGER"        # exact phrase search
chronicle open <result-id>                             # deep link or transcript view
chronicle recent -n 20                                 # recent active chats by last activity date
chronicle --ai-task list                               # discover configured optional AI tasks
```

## Optional YAML-defined AI tasks

Install the optional LiteLLM-backed layer explicitly; the base archive and all
normal commands have no AI dependency and make no model calls:

```powershell
poetry install -E enrich
poetry run chronicle init
poetry run chronicle --ai-task list
poetry run chronicle --ai-task example-task --conversation-id 1 --dry-run
```

`init` copies the tracked privacy-safe templates `ai-tasks.default.yaml` and
`ai-models.default.yaml` to `.chronicle/ai-tasks.yaml` and
`.chronicle/ai-models.yaml`. Existing local catalogs are kept unless `--force`
is explicitly supplied. Prompts/tasks and model profiles are separate,
strictly validated YAML files. The included example task is disabled and the
local LM Studio profile uses a loopback endpoint plus the
`CHRONICLE_LOCAL_MODEL` environment variable.

For isolated automation or testing, `CHAT_CHRONICLE_AI_CONFIG_DIR` may point at
the directory containing `ai-tasks.yaml` and `ai-models.yaml`; normal use keeps
the default `.chronicle` location. Model profiles request strict JSON-schema
output by default. A provider known not to support it must explicitly set
`structured_output: false`, which degrades the provider request to JSON-object
mode while retaining mandatory client-side Pydantic validation.

Generation precedence is per field: the selected model profile supplies safe
`temperature` and `max_tokens` defaults, and a task may override either or both
under its own `generation` mapping. Omitted task fields inherit the profile.
Chronicle sends and caches the resolved effective values. Changing a profile
default that is masked by a task override therefore does not cause an identical
request to be executed again.

Runnable tasks always require one `--conversation-id` or a positive bounded
`--limit`. Loopback profiles run locally by default; cloud or non-loopback
profiles are blocked unless that invocation includes `--allow-remote`.
Successful results resume from a configuration/input-aware cache; `--force`
appends a fresh auditable attempt. In a mixed batch, individual failures are
stored and reported while successful conversations continue; the command exits
nonzero when every selected conversation fails. The four production conversation-
intelligence tasks are intentionally deferred to WP-5.1.1.

`chronicle ingest` accepts either a single supported source or a parent directory. A parent directory is scanned for supported child sources such as ChatGPT/OpenAI exports, Claude exports, OpenAI Codex local JSONL sessions, and Claude Code project JSONL sessions. Directories that are already valid single sources, such as `$env:USERPROFILE\.codex` or `$env:USERPROFILE\.claude\projects`, still ingest as one source rather than being expanded file by file.

Example parent-folder ingest:

```powershell
poetry run chronicle ingest .\exports --provider auto --db-path .\.chronicle\chronicle.db
```

Re-running the same command is expected to be idempotent: existing conversations should be skipped rather than duplicated.

Example Claude export smoke test:

```powershell
poetry run chronicle ingest .\exports\claude --provider claude --db-path .\.chronicle\chronicle.db
poetry run chronicle recent -n 10 --provider claude --db-path .\.chronicle\chronicle.db
```

`chronicle search` uses broad FTS5 token search by default. Ordinary punctuation in broad queries is treated as safe user text, so inputs such as `scan-local`, `provider:openai_codex`, and path-like strings should return results or `No results` rather than SQLite FTS syntax errors. For exact hyphen/phrase matching such as `YOU are the MANAGER`, use:

```powershell
poetry run chronicle search --phrase "YOU are the MANAGER" --provider openai_codex --db-path .\.chronicle\chronicle.db
```

Search is case-insensitive for normal usage. Phrase mode matches the exact word sequence regardless of letter case, and default FTS search also treats case differences as non-significant. For noisy multi-word broad searches with common words such as `you`, `are`, and `the`, the CLI prints a hint suggesting `--phrase`.

`chronicle recent` supports `--provider`, `--since`, `--until`, and `--db-path`. If `-n/--limit` is omitted, it shows up to 10 rows and prints a note explaining how to increase the limit.

`chronicle scan-local` is read-only. It reports configured/default source locations and status without importing data, creating a database, or parsing transcript bodies:

```powershell
poetry run chronicle scan-local
```

## Stack, and what we deliberately did not choose

Python 3.11+ · Poetry · Pydantic v2 · Typer + Rich · stdlib `sqlite3` + FTS5 · pytest · ruff · pre-commit · GitHub Actions (Windows + Ubuntu).

Optional extras: `enrich` (YAML-defined AI tasks through LiteLLM, local service profile by default) and the planned `mcp` layer (FastMCP recall server). The core archive keeps zero mandatory AI dependencies.

Not chosen: **DuckDB** (an analytics engine, wrong fit for text recall) · **Marvin** (native `json_schema` structured output teaches more) · **a browser extension** (fragile; exports and extractors cover the same ground) · **a background daemon** (a one-line Windows Task Scheduler entry suffices).

## Privacy

Everything stays on your machine. Local databases and exports are git-ignored; only synthetic fixtures are ever committed. No real chat data lives in this repository.

## Limitations (honest)

- Web-chat history (ChatGPT, Claude, Gemini) is only as fresh as your last export request. Coding-agent history refreshes automatically because those tools keep durable local transcripts.
- Coding-agent conversations have no URLs — `chronicle open` renders a local transcript for those.
- Local-store formats are undocumented and can change with any tool release; a format change degrades to "source skipped with a warning," never a crash.

## License

MIT — see [LICENSE](LICENSE).
