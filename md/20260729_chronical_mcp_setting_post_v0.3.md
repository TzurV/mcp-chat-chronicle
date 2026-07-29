# Chronicle MCP — LinkedIn Article + Feed Post, v0.3

**Date:** 2026-07-29
**Change from v0.2:**
- Article: opens with the risk/surprise (shim, silent config drop, lying UI) before the descriptive setup line.
- Article: Quick Reference table moved up, right after the intro/naming note, so a skimmer gets the answer without reading six sections.
- Article: added a short professional closing line (contract/project availability) so the CTA doesn't depend on a reader also seeing the feed post.
- Feed post: opens with "Why is it..." instead of a two-sentence lead-in.
- Feed post: dropped the absolute claim "None of this is documented anywhere" (unverified) for a hedged, defensible line.
- Feed post: closing line rephrased to frame the article as a step-by-step reference worth keeping.
**Tone:** technical, professional, factual.
**Status:** owner-reported published on 2026-07-29 as a LinkedIn article and
supporting feed post. External publication URLs were not supplied for this
repository record.

---

# PART A — LinkedIn Article

**Suggested title:** Configuring one MCP server across four Windows clients
**Suggested subtitle:** The complete working set — launch contract, four config formats, and how to verify it actually works

---

A local MCP server sounds like a five-minute setup: point the client at your script. Wiring the same one into four Windows clients turned up a shim that silently won't launch, a config property that silently drops the whole entry, and a UI that gives two different false readings on whether the connection is actually working.

I connected the same read-only MCP server — one stdio process, three tools — to Codex in VS Code, the Codex Windows app, Claude Code, and Claude Desktop. Each client has its own configuration format and its own reload behavior. Below is the complete working set, verified on Windows on 27 July 2026.

**A note on names:** `chat-chronicle`, `chat_chronicle`, and `CHAT_CHRONICLE_DB` throughout are my own project's server name, Python package, and environment variable. Substitute your own — the structure is what transfers.

**For anyone skimming — the short version:**

| Concern | Answer |
|---|---|
| Launch | `<repo>\.venv\Scripts\python.exe -m <package>.cli serve` |
| Switchable target | Environment variable, never in `args` |
| Codex (all surfaces) | `~\.codex\config.toml`, backslashes doubled |
| Claude Code | `claude mcp add --scope local`, or project `.mcp.json` |
| Claude Desktop | Developer config JSON, no `"type"` property |
| Reload | Reload Window / full process termination |
| Proof of success | A tool call with a verifiable result |

The full detail, including why each of these is the answer, follows below.

---

## 1. Launch with the interpreter, not a console script

Windows packaging may produce a `.cmd` shim rather than a `.exe`. Protocol clients may tolerate a shim; native MCP hosts may not spawn it. The portable contract is the virtual environment's Python executable plus the module:

```
command: <repo>\.venv\Scripts\python.exe
args:    ["-m", "your_package.cli", "serve"]
cwd:     <repo>              # where the client supports it
```

This one command worked in all four clients. Everything below changes around it; this does not.

## 2. Keep the mutable value in the environment

Put anything you expect to switch — the target database, a profile, an endpoint — in an environment variable, never in `args`:

```
env:
  CHAT_CHRONICLE_DB: <absolute-database-path>
```

Switching between database versions then becomes one value change per client, with an identical launch command everywhere. Define the resolution order explicitly and document it: CLI flag → environment → config file → default.

## 3. The four client formats

**Codex — VS Code, CLI, IDE extension, and the Windows app** share `%USERPROFILE%\.codex\config.toml`:

```toml
[mcp_servers.chat-chronicle]
cwd = "<repo>"
command = "<repo>\\.venv\\Scripts\\python.exe"
args = ["-m", "chat_chronicle.cli", "serve"]

[mcp_servers.chat-chronicle.env]
CHAT_CHRONICLE_DB = "<absolute-database-path>"
```

Double the backslashes in TOML basic strings, or use single-quoted literal strings consistently. Inspect with `codex mcp get <name>` rather than opening the whole file.

**Claude Code** takes a private machine-specific entry through the CLI:

```powershell
claude mcp add --transport stdio `
  --env "CHAT_CHRONICLE_DB=<absolute-database-path>" `
  --scope local `
  chat-chronicle -- `
  "<repo>\.venv\Scripts\python.exe" -m chat_chronicle.cli serve
```

A project-scoped `.mcp.json` with repository-relative paths is the shareable alternative — portable only if every checkout provides the referenced local database. If both a local and a project entry exist under the same name, make them select the same target or remove one; otherwise scope precedence decides for you.

**Claude Desktop** uses Developer → Edit Config → `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "chat-chronicle": {
      "command": "<repo>\\.venv\\Scripts\\python.exe",
      "args": ["-m", "chat_chronicle.cli", "serve"],
      "env": { "CHAT_CHRONICLE_DB": "<absolute-database-path>" }
    }
  }
}
```

Note the omission: the build I tested ignored an entry containing `"type": "stdio"`. Without that property, it connected. Merge into the existing `mcpServers` object and validate the JSON before restarting:

```powershell
Get-Content -Raw "<config-path>" | ConvertFrom-Json | Out-Null
```

## 4. Restart properly, per surface

- VS Code: **Developer: Reload Window**, then reopen the chat.
- Desktop apps: closing the window is not enough on Windows. Terminate the tray and background processes, relaunch, and open a new session.
- CLI: `codex mcp get <name>` / `claude mcp list` confirms what is actually stored.

## 5. Verify with a call, not with the UI

Client UI state and tool execution are separate facts. One surface I tested did not list the server in its `/mcp` view while calling its tools successfully; another showed the server in Settings before it was reachable.

The reliable acceptance test is a request only your server can satisfy, returning something you can independently check:

```
Using my archive, what have I worked on lately and when?
Include supporting conversation IDs.
```

Then confirm the returned identifiers resolve against your own data. Also test the failure paths once: a no-result query should return empty, and an out-of-bounds argument should return a tool error without dropping the connection.

## 6. Design the trust boundary before you connect anything

A local server does not mean local data. The process and the database stay on the machine, but whatever a tool returns becomes part of the model request — to OpenAI for Codex surfaces, to Anthropic for Claude surfaces.

What that implies in practice:

- Open the database read-only and enforce it — for SQLite, `mode=ro` plus `PRAGMA query_only = ON`.
- Ship no write, ingest, migration, or repair tools if the job is retrieval.
- Bound every output. Retrieval takes an explicit character limit, so the caller controls how much leaves the machine.
- Return metadata first, then one selected item — not the whole store.
- Treat returned content as untrusted data, not as instructions to the model.

---

## The context

This came out of Chat Chronicle, a project I have been building in the open: a local-first, searchable archive of AI conversations. Histories from ChatGPT, Claude, Codex, and Claude Code get normalized into one SQLite/FTS journal that stays on your machine.

MCP recall is the newest capability. It exposes exactly three read-only tools — search, retrieve one bounded conversation, list recent topics — so the assistant already in front of you can search your own history instead of you pasting it back in. Read-only by construction, bounded by design, and now verified across four Windows clients. 446 tests, MCP suite running on Windows and Ubuntu CI.

Next up: sharper recall quality and packaging.

---

This kind of work — wiring AI tooling together, evaluating it honestly, and writing down what actually happens instead of what the docs claim — is what I take on as contract / project work. If that's a fit for something you're building, let's talk.

---

# PART B — Feed Post

**1,052 characters** as written, hashtags included. Hook is **80** — well inside the ~140 mobile cutoff.
The `[article link]` marker below was replaced in the published feed post. The
external URL was not supplied for this repository record. A full LinkedIn
article URL runs about 100 characters, which put the published post at roughly
**1,138** characters — short and skimmable, well under the 3,000 hard limit.
Counts were verified programmatically, not estimated.

---

> Why is it so hard to do the one thing MCP asks — point the client at the server?
>
> I wired the same read-only MCP server into Codex (VS Code + Windows app), Claude Code, and Claude Desktop. Three findings I didn't expect:
>
> → Windows packaging quietly produced a shim some clients simply won't launch.
>
> → One client dropped a config entry outright — no error, it just never connected — over a single extra property.
>
> → One surface showed "connected" while a tool call would fail. Another surface did the reverse.
>
> I couldn't find any of this spelled out beforehand.
>
> Full walkthrough — config for all four clients, the exact failure modes, and a 2-minute test that proves your server actually works, not just looks connected. Step by step, worth keeping: [article link]
>
> — — —
> 📩 With many years of experience in R&D and solution development, I'm available for contract / project work — building exactly this kind of thing (AI solutions, evaluation, honest measurement). If you have a project that's a fit, let's talk.
>
> #MCP #AIEngineering #DeveloperTools

---

## Notes for posting

- **Publish order:** article first, then the feed post with the link. LinkedIn shows articles a permanent URL, so the post can be reshared later against the same target.
- **Hook:** the first line is 80 characters and survives the mobile cutoff intact. Do not prepend a greeting or an emoji — anything before it pushes the payload past the fold.
- **Length:** this version is shorter than v0.2 by design — the three findings and the CTA carry the post, nothing dropped from the article's content lives here.
- **Placeholders:** `<repo>` and `<absolute-database-path>` are intentional. Never paste real local paths into a public post.
- **Dated claim:** "verified on Windows on 27 July 2026" is the only decaying statement. Keep the date visible rather than letting it read as current.
- **"I couldn't find any of this spelled out beforehand"** is a claim about your own search, not a claim that no documentation exists anywhere — phrased that way deliberately after the v0.2 review flagged the stronger version as unverifiable.
- Client build numbers are omitted deliberately; they date the material quickly. They are in `docs/mcp-client-setup.md` if wanted.
- **Hashtags:** 3, not 5 — 2026 data shows posts with more than 3 hashtags underperform posts with none. `#MCP` is the specific/searchable term, `#AIEngineering` is the broad professional category, `#DeveloperTools` targets the practitioner audience most likely to need this. Dropped `#Windows` and `#LocalFirst` from the v0.2 set as redundant with the post's own content.
- **No bold in the post body.** LinkedIn's feed composer has no rich-text toolbar — bold only exists via Unicode look-alike characters, which read as accessibility-unfriendly and mildly spammy. The arrows and short paragraph breaks already do the visual-hierarchy job; nothing here needs faking bold. (The article, by contrast, has a real Bold button — see the paste guide.)

---

## Why Chronicle stays at the end

The alternative was moving the project context above section 5 so the verification example had somewhere to stand. I recommend against it. A guide gets saved because it is general, and a project introduction in the middle makes a reader stop and re-evaluate whether the rest applies to them.

The actual source of the tension was narrower: the config blocks carry `chat_chronicle` names, which read as project-specific until declared otherwise. The naming note at the top of the article resolves that — every section then reads as substitutable structure. Section 5 was also made generic ("a request only your server can satisfy", "identifiers resolve against your own data") so it no longer depends on Chronicle's conversation IDs to make sense.

Chronicle therefore appears once, at the end, as provenance for the guide — immediately followed by the availability line, so a reader who stops at the end of the article (and never sees the feed post) still gets the CTA.

---

## Sources

All claims trace to these files under `c:\work\Github\mcp-chat-chronicle`:

| Claim | Source | Location |
|---|---|---|
| Launch contract `<repo>\.venv\Scripts\python.exe -m chat_chronicle.cli serve` | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Architecture and lifecycle", lines 93–106 |
| `.cmd` shim vs `.exe`; native hosts would not launch the shim | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-completion-report.md` | §4 and §9, lines 29–34, 79–92 |
| Launch contract accepted by PM | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-validation-review.md` | "Accepted Integration Findings", lines 40–45 |
| Database resolution order (flag → env → config → default) | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Database selection and switching", lines 120–152 |
| Codex TOML block, doubled backslashes, `codex mcp get` | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | lines 154–199 |
| Claude Code local scope, project `.mcp.json`, scope-precedence caution | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | lines 201–249 |
| Project configuration example | `c:\work\Github\mcp-chat-chronicle\.mcp.json` | whole file |
| Claude Desktop JSON; build ignored `"type": "stdio"`; JSON validation command | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | lines 252–283 |
| Same, as recorded integration finding | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-completion-report.md` | §16, §19, lines 142–168 |
| Reload behavior per surface; full tray termination on Windows | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | lines 179–199, 282–283 |
| UI state is not proof of tool execution; `/mcp` omission on the Codex Windows app | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-completion-report.md` | §12, §17, §26, lines 116–121, 149–155, 276–286 |
| Verification prompt with conversation IDs | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Five-minute MCP path" and "Everyday use", lines 43–52, 285–308 |
| No-result and invalid-bound behavior stays nonfatal | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-completion-report.md` | §18, lines 157–162 |
| SQLite `mode=ro` + `PRAGMA query_only = ON`; no write path | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1A-completion-report.md` | §7, lines 51–58 |
| Three read-only tools and their bounds; untrusted archive text | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | lines 108–118 |
| Local server ≠ local data; provider disclosure; metadata-before-detail workflow | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Privacy and trust boundary", lines 386–402, and lines 310–320 |
| Chronicle description (local-first normalized SQLite/FTS archive) | `c:\work\Github\mcp-chat-chronicle\README.md` | lines 1–10 |
| 446 tests passing, 1 skipped | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-completion-report.md` | §22, lines 214–227 |
| MCP suite on Windows + Ubuntu CI matrix | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1A-completion-report.md` | §15, lines 124–128 |
| Verified 27 July 2026 across four client surfaces | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Tested versions and limitations", lines 453–465 |
