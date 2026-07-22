# Chat Chronicle

*A local-first, searchable archive of your AI conversations — populated by source-specific importers and extractors, normalized into one SQLite/FTS journal, with optional YAML-defined AI tasks and MCP recall planned as separate layers.*

## Start searching in 5 minutes

### 1. Install

You need Python 3.11 or later and [Poetry](https://python-poetry.org/).

```powershell
git clone https://github.com/TzurV/mcp-chat-chronicle.git
cd mcp-chat-chronicle
poetry install
```

### 2. Initialize local folders and database

```powershell
poetry run chronicle init
```

This creates the local database, configuration, and export drop folders:

```text
.chronicle/chronicle.db
.chronicle/config.yaml
exports/openai/
exports/claude/
```

These paths are git-ignored. Keep real exports and the local database private.

### 3. Add supported histories

If you already use Codex or Claude Code locally, their histories normally exist in
the default local stores and need no manual export. ChatGPT and Claude web require
official exports; place the downloaded files under:

```text
exports/openai/
exports/claude/
```

Check which local stores and export locations are currently available:

```powershell
poetry run chronicle scan-local
```

See the source-specific instructions below.

### 4. Collect

```powershell
poetry run chronicle collect
poetry run chronicle stats
```

Collection is idempotent: rerunning it updates changed conversations and skips
unchanged ones instead of creating duplicates. `stats` confirms the resulting
conversation/message counts and recent ingest status by provider.

### 5. Search

```powershell
poetry run chronicle recent -n 20
poetry run chronicle search "docker network"
poetry run chronicle search --phrase "YOU are the MANAGER"
poetry run chronicle open <result-id>
```

## Supported sources

| Source | Type | Where history comes from | Manual step required? |
| --- | --- | --- | --- |
| ChatGPT | Official export | Downloaded ChatGPT data export | Yes |
| Claude web | Official export | Downloaded Claude data export | Yes |
| OpenAI Codex | Local store | `%USERPROFILE%\.codex` | No, if Codex has been used locally |
| Claude Code | Local store | `%USERPROFILE%\.claude\projects` | No, if Claude Code has been used locally |

Codex and Claude Code are the easiest starting point because their histories
already live locally. ChatGPT and Claude web require an export first.

## How to export ChatGPT history

OpenAI's current web flow is:

1. Sign in to ChatGPT and open the profile menu.
2. Select **Settings**.
3. Open **Data Controls**.
4. Under **Export Data**, select **Export**, then confirm the request.
5. Wait for the email and download the ZIP file. The download link currently
   expires after 24 hours.
6. Place the ZIP file under:

   ```text
   exports/openai/
   ```

7. Run:

   ```powershell
   poetry run chronicle collect
   ```

Chat Chronicle ingests supported ChatGPT export files from that folder, including
current split exports containing numbered conversation JSON files. Interface labels
and export availability can change by account or workspace, so check
[OpenAI's official export instructions](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data)
if the controls look different.

## How to export Claude history

Anthropic's current flow for individual Claude users is available from the web app
or Claude Desktop, not the mobile apps:

1. Open Claude and select your initials in the lower-left corner.
2. Select **Settings**.
3. Open **Privacy**.
4. Select **Export data**.
5. When the export email arrives, download the file while signed in. The download
   link currently expires after 24 hours.
6. Place the downloaded export under:

   ```text
   exports/claude/
   ```

7. Run:

   ```powershell
   poetry run chronicle collect
   ```

Claude's export structure may change over time. Keep the original export file. If
collection reports warnings, retain the original locally and open an issue with
only sanitized diagnostics—never attach a private export. Claude for Work export
permissions differ by plan and role; see
[Anthropic's official export instructions](https://support.anthropic.com/en/articles/9450526-how-can-i-export-my-claude-data).

## Local sources: Codex and Claude Code

If you use OpenAI Codex locally, Chat Chronicle looks for sessions under:

```text
%USERPROFILE%\.codex
```

If you use Claude Code locally, it looks for project sessions under:

```text
%USERPROFILE%\.claude\projects
```

Check what Chat Chronicle can see without importing anything:

```powershell
poetry run chronicle scan-local
```

`scan-local` is read-only. It reports configured/default source locations and their
availability without creating a database, importing messages, or modifying the
archive.

## Search cheat sheet

Recent activity:

```powershell
poetry run chronicle recent -n 20
```

Broad search:

```powershell
poetry run chronicle search "docker network"
```

Exact phrase search:

```powershell
poetry run chronicle search --phrase "YOU are the MANAGER"
```

Limit results to one provider:

```powershell
poetry run chronicle search "release planning" --provider openai_codex
```

Open a result:

```powershell
poetry run chronicle open <result-id>
```

For ChatGPT and Claude web conversations, `open` uses the stored provider URL when
available and attempts to launch the default browser. For Codex and Claude Code,
`open` renders the locally archived transcript.

## What this is not

Chat Chronicle is not a hosted AI memory service, browser extension, or agent
orchestrator. It is a local archive and search layer for supported AI conversation
histories.

## Project status

> **Status: v0.1.0 is the published source baseline; development continues on `main`.** The local DB, official ChatGPT and Claude export importers, OpenAI Codex and Claude Code local extractors, config/init/collect, scan-local inventory, stats, search, phrase search, open, and recent-activity CLI paths are implemented and exercised against the owner's real archive. YAML-defined AI tasks now run through LiteLLM with strict schemas, caching, and explicit local/remote controls. A private development evaluation harness supports split candidate generation, local deterministic scoring, and optional cached Gemini judging. Claude project metadata is linked only when reliable conversation references exist. See [`md/master-plan.md`](md/master-plan.md) for the full plan and [`md/development-ledger.md`](md/development-ledger.md) for execution status.

## Why

AI work is scattered across ChatGPT, Claude, and coding agents. Each stores history
in an isolated, poorly searchable silo. Chat Chronicle indexes *events*—which
conversation, when, in which tool, and how to get back to it.

A **source-agnostic core** is fed by **pluggable, source-specific adapters**. Adding
a new source means adding one adapter, not changing the storage and search core.

## Positioning

| Project | What it does | How we differ |
| --- | --- | --- |
| [OpenMemory MCP (mem0)](https://mem0.ai/blog/introducing-openmemory-mcp) | Stores distilled facts/preferences about you | We index events, not memories—an archive with a way back to the thread. |
| [OpenChat](https://github.com/p0u4a/openchat) | Browser extension captures chat traffic | We use official exports plus durable local stores; no extension, and we reach coding agents. |
| Provider built-in search | Per-silo only | Cross-provider and cross-tool, local, private, scriptable. |

## Detailed workflow: `init` + `collect`

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

## Advanced: optional local AI tasks

The core archive and search workflow has no AI dependency and makes no model calls.

Optional AI tasks can run YAML-defined conversation-intelligence jobs through
LiteLLM, preferably using a local LM Studio profile. These tasks are separate from
search and must be invoked explicitly.

The initial task catalog provides conversation summaries, work-mode classification,
last-activity descriptions, and title assessment. Prompts and model profiles live in
the git-ignored `.chronicle/ai-tasks.yaml` and `.chronicle/ai-models.yaml`; validated
output contracts and cache/provenance handling remain application-owned.

Quick commands:

```powershell
poetry install -E enrich
poetry run chronicle --ai-task list
poetry run chronicle --ai-task conversation-summary --conversation-id <id> --dry-run
```

For full setup, local-model configuration, privacy gates, caching, schema
validation, and troubleshooting, see [`docs/ai-tasks.md`](docs/ai-tasks.md).

## Development evaluation harness (optional)

The evaluation harness is development tooling, not part of the five-minute archive
workflow. It supports separate preparation, candidate generation, package
verification, deterministic scoring, and optional LLM judging. Private corpora,
candidate outputs, and scoring artifacts stay under git-ignored `.chronicle/eval/`.

Candidates may be local artifacts or hosted APIs. Hosted profiles use explicit
`execution: hosted-api` provenance (with no invented GGUF, quantization, runtime, or
device fields) and generation requires both privacy gates:

```powershell
poetry run python -m bench generate `
  --bundle <candidate-input-bundle> `
  --config $CONFIG `
  --allow-remote `
  --confirm-private-eval
```

This discloses the selected task prompts and conversation content to the configured
candidate provider. Candidate and judge identities and caches are independent, so a
new judge can score an immutable package without regenerating candidates.
The primary semantic default is Gemini 3.1 Pro Preview with rubric v1,
temperature 0, and a 1,000-token cap; Gemini 2.5 Flash results are diagnostic
judge-sensitivity evidence, not a competing default.

After preparing a private evaluation config and generating a candidate package,
verification and deterministic scoring need neither the candidate model runtime nor
a judge:

```powershell
$CONFIG = ".\.chronicle\eval\dev-v1\config\evaluation.yaml"
$PACKAGE = "<path-to-candidate-package.zip>"

poetry run python -m bench verify --package $PACKAGE --config $CONFIG
poetry run python -m bench score --package $PACKAGE --config $CONFIG --deterministic-only
```

To reconstruct reports from already cached judge attempts without permitting a new
provider call:

```powershell
poetry run python -m bench score `
  --package $PACKAGE `
  --config $CONFIG `
  --with-judge `
  --allow-remote `
  --confirm-private-eval `
  --judge-cache-only
```

`--judge-cache-only` fails before provider execution if any required cache entry is
missing. Omitting it from a judge-enabled run can disclose the selected source,
candidate result, and private development reference to the configured remote judge.
See [`docs/development-evaluation.md`](docs/development-evaluation.md) for corpus
preparation, transfer, authorization, and report interpretation.

## Stack, and what we deliberately did not choose

Python 3.11+ · Poetry · Pydantic v2 · Typer + Rich · stdlib `sqlite3` + FTS5 · pytest · ruff · pre-commit · GitHub Actions (Windows + Ubuntu).

Optional extras: `enrich` (YAML-defined AI tasks through LiteLLM, local service profile by default) and the planned `mcp` layer (FastMCP recall server). The core archive keeps zero mandatory AI dependencies.

Not chosen: **DuckDB** (an analytics engine, wrong fit for text recall) · **Marvin** (native `json_schema` structured output teaches more) · **a browser extension** (fragile; exports and extractors cover the same ground) · **a background daemon** (a one-line Windows Task Scheduler entry suffices).

## Privacy

Your archive stays on your machine. Local databases, official exports, and raw local
session records are git-ignored and must never be committed. Test fixtures are
synthetic. The first release includes one deliberate exception: an owner-reviewed,
sanitized manager-chat transcript under `md/release-artifacts/manager-chat/` that
documents the project's development process. It contains no raw source record and
is not loaded into a user's archive automatically. Optional AI tasks are always
explicit; remote model use requires `--allow-remote` and deliberate authorization.

## Limitations (honest)

- ChatGPT and Claude web history is only as fresh as your last export request. Coding-agent history refreshes automatically because those tools keep durable local transcripts.
- Coding-agent conversations have no URLs — `chronicle open` renders a local transcript for those.
- Local-store formats are undocumented and can change with any tool release; a format change degrades to "source skipped with a warning," never a crash.

## License

MIT — see [LICENSE](LICENSE).
