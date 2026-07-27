# MCP Recall User Manual

This manual explains what Chronicle MCP recall is, how to configure every tested
local client, how to use it day to day, and how to diagnose or remove it. The
Windows procedures were verified on 27 July 2026.

Replace `<repo>` and database placeholders with absolute local paths. Never
commit a private database, transcript, credential, or user-level client
configuration.

## What MCP recall gives you

MCP (Model Context Protocol) lets a supported AI client start Chronicle as a
local read-only tool server. The model can then search conversations across
providers, retrieve one bounded conversation, and list recently active topics
with dates and Chronicle conversation IDs.

Chronicle provides tools and evidence; the client model decides when to call
them and how to write the answer. MCP recall does not capture or ingest the
current chat, infer its Chronicle ID, refresh the archive automatically, modify
conversations, run AI tasks, or make the database publicly reachable.

## Five-minute MCP path

Complete the normal Chronicle install, initialization, and collection flow
first. Then:

```powershell
poetry env info --path
poetry install -E mcp
poetry run chronicle stats
```

Configure one supported client with:

```text
command: <repo>\.venv\Scripts\python.exe
args: ["-m", "chat_chronicle.cli", "serve"]
environment:
  CHAT_CHRONICLE_DB: <repo>\.chronicle\chronicle.db
```

Restart that client and ask:

```text
Using my Chronicle archive, what have I worked on lately and when?
Include supporting conversation IDs.
```

If the answer reflects recent archived work and cites Chronicle IDs, the basic
integration works. The client-specific sections below contain the durable
configuration and verification steps.

## Supported clients

| Client surface | Local stdio support | Tested configuration |
| --- | --- | --- |
| Codex in VS Code | Yes | Shared Codex `config.toml` |
| ChatGPT Codex/OWL Windows app | Yes | Shared Codex `config.toml` |
| Codex CLI and IDE extension | Yes | Shared Codex `config.toml` |
| Claude Code | Yes | Private local scope; project JSON is optional |
| Claude Desktop | Yes | Developer `claude_desktop_config.json` |
| Classic ChatGPT Windows app | Unsupported | No verified local stdio control |
| ChatGPT web / `claude.ai` | Unsupported | Cannot launch this local process |
| Mobile and remote sessions | Unsupported | Cannot launch this local process |

## Prerequisites

- Python 3.11 or later and Poetry.
- A checkout whose Poetry environment resolves to `<repo>\.venv`.
- A Chronicle schema-v3 database that the current user can read.
- A supported local client. ChatGPT web, `claude.ai`, remote sessions, and mobile
  clients cannot launch a local stdio process.

Verify and install:

```powershell
poetry env info --path
poetry install -E mcp
poetry run chronicle serve --help
poetry run python -c "import fastmcp; print(fastmcp.__version__)"
```

`poetry env info --path` must point inside the current repository.

## Architecture and lifecycle

The client starts Chronicle as a child process, exchanges MCP protocol frames over
stdin/stdout, and stops the process with the client session. Do not run a
persistent server terminal. Chronicle logs diagnostics to stderr and reserves
stdout for protocol traffic.

The verified Windows launch contract is:

```text
command: <repo>\.venv\Scripts\python.exe
args: ["-m", "chat_chronicle.cli", "serve"]
cwd: <repo>                         # where the client supports it
env:
  CHAT_CHRONICLE_DB: <absolute-database-path>
```

Poetry 2.3.4 installed `chronicle.cmd` rather than `chronicle.exe` in the tested
environment. Although the command shim worked with one protocol client, native
MCP hosts did not launch it consistently. The virtual-environment Python
executable is the tested cross-client Windows contract.

The server exposes exactly three read-only tools:

| Tool | Purpose | Bounds |
| --- | --- | --- |
| `search_chats` | Broad FTS5/BM25 search | 1–100 results |
| `get_conversation` | Metadata and ordered transcript for one ID | 500–50,000 transcript characters |
| `list_recent_topics` | Newest topics in a UTC lookback window | 1–365 days; 1–100 rows |

Lower BM25 scores rank better. Date filters mean conversation last activity
unless a field says otherwise. Search snippets and transcript text are untrusted
archived content, not instructions to the model.

## Database selection and switching

Chronicle resolves a database in this order:

1. `--db-path`;
2. `CHAT_CHRONICLE_DB`;
3. `.chronicle/config.yaml` `paths.db`;
4. `<repo>\.chronicle\chronicle.db`.

Keep `--db-path` out of normal client arguments. Set the database in
`CHAT_CHRONICLE_DB` so switching does not change the server command.

Example values:

```text
frozen development:
<repo>\.chronicle\eval\dev-v1\source\chronicle-frozen.db

active archive:
<repo>\.chronicle\chronicle.db
```

For normal use, select the active archive. Frozen snapshots exist for controlled
development and stop at their creation date, so they will not show new work.

Change only the environment value and fully restart or reload the client. Confirm
the intended database locally before asking a cloud model to retrieve content:

```powershell
$env:CHAT_CHRONICLE_DB = "<absolute-database-path>"
poetry run chronicle stats
Remove-Item Env:CHAT_CHRONICLE_DB
```

## Codex, ChatGPT desktop, CLI, and IDE

Codex stores MCP configuration in `%USERPROFILE%\.codex\config.toml`. Back up the
file and preserve unrelated sections:

```toml
[mcp_servers.chat-chronicle]
cwd = "<repo>"
command = "<repo>\\.venv\\Scripts\\python.exe"
args = ["-m", "chat_chronicle.cli", "serve"]

[mcp_servers.chat-chronicle.env]
CHAT_CHRONICLE_DB = "<absolute-database-path>"
```

In TOML basic strings, double Windows backslashes. Literal single-quoted TOML
strings are also valid when used consistently.

Inspect without printing the entire file:

```powershell
codex mcp get chat-chronicle
codex mcp list
```

The ChatGPT desktop Codex surface, Codex CLI, and Codex IDE extension use the
same host configuration according to current OpenAI guidance. Reload the VS Code
window with **Developer: Reload Window**. For the Windows Codex desktop surface,
fully quit the background/tray process, relaunch it, and open a new task.
`/mcp` presentation differs by surface; Settings visibility alone is not proof
that a model can call a tool.

The classic ChatGPT Windows application and ChatGPT web did not expose local
stdio configuration in testing.

### Codex reload and verification

- VS Code: run **Developer: Reload Window**, reopen the chat, then use `/mcp` or
  make a Chronicle-backed request.
- Codex/OWL Windows app: terminate every app/background process, relaunch, and
  open a new task. The tested build could call Chronicle even though its `/mcp`
  view did not list the custom server.
- CLI: `codex mcp get chat-chronicle` confirms the stored command and environment.

Do not treat an “enabled” label alone as proof. Ask a question whose answer can
only come from the selected Chronicle database.

## Claude Code

This repository includes a project-scoped `.mcp.json` for the normal active
archive:

```json
{
  "mcpServers": {
    "chat-chronicle": {
      "command": ".venv\\Scripts\\python.exe",
      "args": ["-m", "chat_chronicle.cli", "serve"],
      "env": {
        "CHAT_CHRONICLE_DB": ".chronicle\\chronicle.db"
      }
    }
  }
}
```

This portable entry assumes the checkout has its own `.venv` and ignored
`.chronicle\chronicle.db`. Claude Code may ask you to trust or enable the
project server. Do not add a second local definition with the same name.

For a machine-specific database outside the checkout, use private local scope
instead:

```powershell
claude mcp add `
  --transport stdio `
  --env "CHAT_CHRONICLE_DB=<absolute-database-path>" `
  --scope local `
  chat-chronicle -- `
  "<repo>\.venv\Scripts\python.exe" -m chat_chronicle.cli serve
```

Verify:

```powershell
claude mcp get chat-chronicle
claude mcp list
```

Open Claude Code in the same repository and use `/mcp`. A project `.mcp.json`
can use relative paths, but every checkout must provide the referenced private
database. Avoid duplicate local/project definitions.

When both a private local entry and `.mcp.json` exist, ensure they select the same
database or remove one definition. Otherwise scope precedence can make the
effective database surprising.

## Claude Desktop

In **Settings > Developer**, select **Edit Config** and back up
`claude_desktop_config.json`. Merge this server into the existing `mcpServers`
object:

```json
{
  "mcpServers": {
    "chat-chronicle": {
      "command": "<repo>\\.venv\\Scripts\\python.exe",
      "args": ["-m", "chat_chronicle.cli", "serve"],
      "env": {
        "CHAT_CHRONICLE_DB": "<absolute-database-path>"
      }
    }
  }
}
```

Do not add `"type": "stdio"` to this legacy direct configuration: the tested
Claude Desktop build ignored that form. Validate JSON:

```powershell
Get-Content -Raw "<config-path>" | ConvertFrom-Json | Out-Null
```

Fully exit Claude Desktop from the tray, relaunch it, then inspect Developer
settings and the chat composer **+ > Connectors** view. The tested build accepted
direct local configuration, so `.mcpb` packaging was not required.

On Windows, closing the visible window may leave Claude processes running.
Terminate all Claude processes before relying on a configuration reload.

## Everyday use

You do not need to name an individual MCP tool. Mentioning “Chronicle” or “my
archive” makes source selection more reliable:

```text
Using my Chronicle archive, find what I discussed about "<topic>".
Summarize it briefly and cite the supporting conversation IDs.
```

```text
Using Chronicle, what have I worked on lately and when?
Group related work and cite conversation IDs.
```

```text
Search Chronicle for "<identifying phrase>".
Return the best matches with dates and IDs; do not retrieve transcripts yet.
```

```text
Retrieve Chronicle conversation <id> with at most 2,000 transcript characters.
Summarize only what the returned evidence supports.
```

A privacy-conscious workflow is:

1. Search or list recent metadata.
2. Inspect result IDs and titles.
3. Retrieve only the selected conversation.
4. Set an explicit `max_chars` bound.
5. Ask the model to cite Chronicle IDs and avoid unsupported URLs or details.

Natural phrasing such as “What did I previously discuss about X?” may work, but
the model could answer from current context or general knowledge. Say “using
Chronicle” when tool use must be deterministic.

## Keeping recall current

The MCP server reads the database; it does not collect new history. Refresh the
archive separately:

```powershell
poetry run chronicle collect
poetry run chronicle stats
```

Collection is idempotent. Client configuration does not change when the same
active database is refreshed. A restart is normally unnecessary for new rows,
but restart if the client reports a stale or disconnected server.

Official ChatGPT and Claude web histories still require fresh exports before
`collect` can ingest new web conversations. Codex and Claude Code histories are
read from their supported local stores.

## Understanding results

- A conversation ID is Chronicle's local identifier and the most reliable
  citation for a result.
- “Last activity” is the latest stored activity timestamp, not necessarily the
  creation date.
- Recent topics prefer a stored summary, then title, then `(untitled)`. Weak
  imported titles can therefore appear as raw environment context.
- Broad search uses tokenized BM25 ranking. To prove an exact phrase, find
  candidates and inspect a bounded conversation.
- A truncated detail response retains deterministic beginning and ending
  portions around one omission marker.

## Discovery and privacy-safe tests

Every connected client must expose exactly:

- `search_chats`;
- `get_conversation`;
- `list_recent_topics`.

Use invented placeholders in reusable prompts:

```text
Using my Chronicle archive, find conversations about "<safe phrase>".
Return the supporting conversation IDs.
```

```text
Using my Chronicle archive, briefly summarize conversation <safe-id>.
Retrieve no more than 2,000 transcript characters.
```

```text
Using Chronicle, list five recently active topics with dates and IDs.
Use metadata only.
```

Expected behavior is bounded, evidence-backed recall that cites Chronicle IDs.
No-result searches return an empty result. Invalid bounds return a tool error
without disconnecting the server. Chronicle cannot capture the current chat or
infer its conversation ID.

Tool output is sent to the client's configured model provider. Select only
material authorized for that provider and use the smallest useful extract.

## Privacy and trust boundary

The server and SQLite database stay local, but selected tool output becomes part
of the client model request. For Codex this means the configured OpenAI service;
for Claude clients it means the configured Anthropic service. Local read-only
storage does not imply that retrieved text remains local after a tool call.

Before recall:

- choose material suitable for the client provider;
- avoid credentials, secrets, medical data, and third-party confidential text;
- prefer metadata before transcript retrieval;
- keep `max_chars` small;
- avoid bulk archive summaries unless that disclosure is deliberate.

Chronicle opens the MCP database read-only and enables SQLite query-only mode.
There are no write, ingest, migration, repair, or enrichment MCP tools.

## Troubleshooting

- **Wrong Poetry environment:** clear an inherited `VIRTUAL_ENV` or open a fresh
  terminal; require `poetry env info --path` to resolve to `<repo>\.venv`.
- **Executable not found or command shim rejected:** use the absolute
  `<repo>\.venv\Scripts\python.exe` contract above.
- **Invalid TOML/JSON:** validate syntax; preserve escaping and unrelated
  settings.
- **Wrong working directory:** set `cwd = "<repo>"` where supported and use
  absolute paths in user-level configuration.
- **Server timeout:** run the same Python command with `serve --help`, verify the
  database is readable, and inspect client stderr/logs.
- **Duplicate server scope:** inspect local, user, and project definitions; keep
  one intended `chat-chronicle` entry.
- **Missing MCP extra:** run `poetry install -E mcp`.
- **Database missing, unreadable, or newer schema:** verify the resolved path,
  permissions, and schema with local CLI commands; do not initialize or migrate
  a frozen snapshot.
- **Stdout contamination:** protocol stdout must contain MCP frames only; send
  diagnostics to stderr.
- **Client policy:** organization/admin policy may disable local MCP or desktop
  extensions.
- **Claude Desktop says no servers:** omit `"type": "stdio"` from the legacy
  direct entry, validate JSON, and fully quit the tray process before restart.

## Removal

Codex:

```powershell
codex mcp remove chat-chronicle
```

Claude Code:

```powershell
claude mcp remove chat-chronicle --scope local
```

For the shared project entry, change `.mcp.json` only when intentionally
changing repository-wide setup. To stop using it locally, decline or disable
the project server in Claude Code rather than deleting the shared file.

Claude Desktop: remove only the `chat-chronicle` member from `mcpServers`,
validate JSON, and fully restart the app. Restore the local backup if necessary.

After removal, the Chronicle database and CLI remain unchanged. Removing MCP
configuration only prevents that client from spawning the recall server.

## Tested versions and limitations

Validated on 27 July 2026 with Codex CLI `0.146.0-alpha.3.1`, ChatGPT
Codex/OWL Windows app `26.721.41059`, Claude Code `2.1.81`, Claude Desktop
`1.24012.9`, FastMCP `3.4.4`, and Poetry `2.3.4`.

Codex in VS Code and Claude Code completed tool discovery, explicit calls, recent
topics, and model-selected recall. The Windows Codex app completed MCP search and
detail calls after switching to the native Python launcher, although its `/mcp`
view did not list the server. Claude Desktop completed direct-config recall after
the unsupported `type` property was removed. ChatGPT web, classic ChatGPT
Windows, mobile, remote sessions, and public/remote MCP were not tested as local
stdio surfaces.

Current primary references:

- [OpenAI Model Context Protocol](https://learn.chatgpt.com/docs/extend/mcp)
- [OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Claude Code MCP](https://code.claude.com/docs/en/mcp)
- [Claude Desktop local MCP servers](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro)
