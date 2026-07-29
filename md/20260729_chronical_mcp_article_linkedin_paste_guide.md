# Publishing the Chronicle MCP article on LinkedIn — paste guide

Source article: `md/20260729_chronical_mcp_setting_post_v0.3.md`, Part A.

**Status:** used for the owner-reported LinkedIn publication on 2026-07-29.
Retained as the publication procedure and formatting record.

## What LinkedIn's article editor actually supports

LinkedIn's article composer ("Write article") is a rich-text editor, not a markdown renderer:

- Toolbar has: Heading 1, Heading 2, Normal, Bold, Italic, Underline, numbered list, bulleted list, blockquote, text link, divider, and image/video/embed insert.
- **No native tables.** The Quick Reference table has no equivalent — it has to become a list.
- **No native code blocks or monospace font.** There's no "code" button.
- **Pasting markdown syntax does nothing.** `##`, `**bold**`, `` `code` ``, and `|table|` characters paste as literal characters, not formatting — the editor doesn't parse them.

Practical consequence: paste plain text with the markdown symbols stripped, then apply formatting manually per line by selecting the text and clicking the toolbar button. There's no way to batch-apply this on paste.

## Conversion map

| Article element | What to do in LinkedIn |
|---|---|
| Title | Paste into the Title field as-is. |
| Subtitle | No separate subtitle field exists. Put it as the first line of the body, italicized. |
| `## 1. Launch...` section headers | Select the line, click **Heading 2**. Drop the `##`. |
| `**A note on names:**` bold labels | Drop the `**`, select the text, click **Bold**. |
| Code blocks (TOML / JSON / PowerShell) | Drop the ` ``` ` fences, select the block, click **Blockquote**. Line breaks survive inside a blockquote, so the config still reads as a block. It won't be monospace, but it will be visually offset from prose. |
| Inline code like `` `args` `` | Drop the backticks. Plain text reads fine inline; there's no inline-code substitute. |
| Quick Reference table | Convert each row to a bullet: bold the left column, then `—`, then the answer. See below. |
| `---` horizontal rules | Use the toolbar's **Divider** insert instead of pasting dashes. |

**Optional upgrade for the code blocks:** if you want the config blocks to look and read like actual code (monospace, syntax highlighting, one-click copy), post each one as a public GitHub Gist and use LinkedIn's **Embed** button with the Gist URL. That's the only way to get real code formatting in a LinkedIn article — worth it if you expect readers to copy-paste the configs directly. Blockquote is the fallback if you'd rather not manage four gists.

---

## Paste-ready body

Everything below is stripped of markdown syntax and ready to paste into the body, section by section. `[Heading 2]` and `[Blockquote]` are instructions for you — delete each tag after applying that toolbar style to the text under it.

---

A local MCP server sounds like a five-minute setup: point the client at your script. Wiring the same one into four Windows clients turned up a shim that silently won't launch, a config property that silently drops the whole entry, and a UI that gives two different false readings on whether the connection is actually working.

I connected the same read-only MCP server — one stdio process, three tools — to Codex in VS Code, the Codex Windows app, Claude Code, and Claude Desktop. Each client has its own configuration format and its own reload behavior. Below is the complete working set, verified on Windows on 27 July 2026.

[Bold] A note on names: chat-chronicle, chat_chronicle, and CHAT_CHRONICLE_DB throughout are my own project's server name, Python package, and environment variable. Substitute your own — the structure is what transfers.

For anyone skimming — the short version:

[Bulleted list — bold each label before the dash]
Launch — repo\.venv\Scripts\python.exe -m package.cli serve
Switchable target — Environment variable, never in args
Codex (all surfaces) — ~\.codex\config.toml, backslashes doubled
Claude Code — claude mcp add --scope local, or project .mcp.json
Claude Desktop — Developer config JSON, no "type" property
Reload — Reload Window / full process termination
Proof of success — A tool call with a verifiable result

The full detail, including why each of these is the answer, follows below.

[Heading 2]
1. Launch with the interpreter, not a console script

Windows packaging may produce a .cmd shim rather than a .exe. Protocol clients may tolerate a shim; native MCP hosts may not spawn it. The portable contract is the virtual environment's Python executable plus the module:

[Blockquote]
command: repo\.venv\Scripts\python.exe
args: ["-m", "your_package.cli", "serve"]
cwd: repo    (where the client supports it)

This one command worked in all four clients. Everything below changes around it; this does not.

[Heading 2]
2. Keep the mutable value in the environment

Put anything you expect to switch — the target database, a profile, an endpoint — in an environment variable, never in args:

[Blockquote]
env:
  CHAT_CHRONICLE_DB: absolute-database-path

Switching between database versions then becomes one value change per client, with an identical launch command everywhere. Define the resolution order explicitly and document it: CLI flag → environment → config file → default.

[Heading 2]
3. The four client formats

[Bold] Codex — VS Code, CLI, IDE extension, and the Windows app share %USERPROFILE%\.codex\config.toml:

[Blockquote]
[mcp_servers.chat-chronicle]
cwd = "repo"
command = "repo\\.venv\\Scripts\\python.exe"
args = ["-m", "chat_chronicle.cli", "serve"]

[mcp_servers.chat-chronicle.env]
CHAT_CHRONICLE_DB = "absolute-database-path"

Double the backslashes in TOML basic strings, or use single-quoted literal strings consistently. Inspect with codex mcp get name rather than opening the whole file.

[Bold] Claude Code takes a private machine-specific entry through the CLI:

[Blockquote]
claude mcp add --transport stdio
  --env "CHAT_CHRONICLE_DB=absolute-database-path"
  --scope local
  chat-chronicle --
  "repo\.venv\Scripts\python.exe" -m chat_chronicle.cli serve

A project-scoped .mcp.json with repository-relative paths is the shareable alternative — portable only if every checkout provides the referenced local database. If both a local and a project entry exist under the same name, make them select the same target or remove one; otherwise scope precedence decides for you.

[Bold] Claude Desktop uses Developer → Edit Config → claude_desktop_config.json:

[Blockquote]
{
  "mcpServers": {
    "chat-chronicle": {
      "command": "repo\\.venv\\Scripts\\python.exe",
      "args": ["-m", "chat_chronicle.cli", "serve"],
      "env": { "CHAT_CHRONICLE_DB": "absolute-database-path" }
    }
  }
}

Note the omission: the build I tested ignored an entry containing "type": "stdio". Without that property, it connected. Merge into the existing mcpServers object and validate the JSON before restarting:

[Blockquote]
Get-Content -Raw "config-path" | ConvertFrom-Json | Out-Null

[Heading 2]
4. Restart properly, per surface

[Bulleted list]
VS Code: Developer: Reload Window, then reopen the chat.
Desktop apps: closing the window is not enough on Windows. Terminate the tray and background processes, relaunch, and open a new session.
CLI: codex mcp get name / claude mcp list confirms what is actually stored.

[Heading 2]
5. Verify with a call, not with the UI

Client UI state and tool execution are separate facts. One surface I tested did not list the server in its /mcp view while calling its tools successfully; another showed the server in Settings before it was reachable.

The reliable acceptance test is a request only your server can satisfy, returning something you can independently check:

[Blockquote]
Using my archive, what have I worked on lately and when?
Include supporting conversation IDs.

Then confirm the returned identifiers resolve against your own data. Also test the failure paths once: a no-result query should return empty, and an out-of-bounds argument should return a tool error without dropping the connection.

[Heading 2]
6. Design the trust boundary before you connect anything

A local server does not mean local data. The process and the database stay on the machine, but whatever a tool returns becomes part of the model request — to OpenAI for Codex surfaces, to Anthropic for Claude surfaces.

What that implies in practice:

[Bulleted list]
Open the database read-only and enforce it — for SQLite, mode=ro plus PRAGMA query_only = ON.
Ship no write, ingest, migration, or repair tools if the job is retrieval.
Bound every output. Retrieval takes an explicit character limit, so the caller controls how much leaves the machine.
Return metadata first, then one selected item — not the whole store.
Treat returned content as untrusted data, not as instructions to the model.

[Divider]

[Heading 2]
The context

This came out of Chat Chronicle, a project I have been building in the open: a local-first, searchable archive of AI conversations. Histories from ChatGPT, Claude, Codex, and Claude Code get normalized into one SQLite/FTS journal that stays on your machine.

MCP recall is the newest capability. It exposes exactly three read-only tools — search, retrieve one bounded conversation, list recent topics — so the assistant already in front of you can search your own history instead of you pasting it back in. Read-only by construction, bounded by design, and now verified across four Windows clients. 446 tests, MCP suite running on Windows and Ubuntu CI.

Next up: sharper recall quality and packaging.

[Divider]

This kind of work — wiring AI tooling together, evaluating it honestly, and writing down what actually happens instead of what the docs claim — is what I take on as contract / project work. If that's a fit for something you're building, let's talk.
