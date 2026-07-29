# LinkedIn Post Draft — "Four Clients, Four Different MCP Settings"

**Purpose:** visibility post. Show that Chronicle keeps advancing, and share a hard-won,
genuinely useful Windows MCP lesson.
**Audience:** engineers and technical leaders wiring AI clients into local tooling.
**Tone:** provocative opening, informative middle, professional close.
**Status:** superseded by
`md/20260729_chronical_mcp_setting_post_v0.3.md`; retained as an unpublished
editorial alternative.

---

## Primary draft (recommended)

> **MCP is "just a standard." I configured the same server four times, four different ways.**
>
> Chronicle is my local-first archive of AI conversations — ChatGPT, Claude, Codex, Claude Code — normalized into one searchable SQLite journal. Last week I shipped read-only MCP recall, so the assistant I'm already talking to can search that archive instead of me pasting history into a prompt.
>
> Three tools. One stdio process. Read-only. On paper, one config file.
>
> On Windows, it was four.
>
> **Codex in VS Code** wanted TOML in `~/.codex/config.toml`, with doubled backslashes and an explicit `cwd`.
> **The Codex/OWL Windows app** shared that same file — but silently refused to launch until I changed the executable, and then never listed the server in its `/mcp` view *while successfully calling it*.
> **Claude Code** took a private local-scope entry via CLI, plus an optional project-level `.mcp.json` with relative paths — and a scope-precedence trap if you define both.
> **Claude Desktop** needed JSON in the Developer config, and rejected the entry outright when it contained `"type": "stdio"`. Removing a property that every modern example includes is what made it connect.
>
> Same server. Same three tools. Four dialects.
>
> **The three lessons that cost me the most time:**
>
> **1. Don't hand an MCP host a Windows command shim.** Poetry 2.3.4 installed `chronicle.cmd`, not `chronicle.exe`. One protocol client tolerated it; a native host would not spawn it. The contract that worked everywhere was the interpreter itself:
> `<repo>\.venv\Scripts\python.exe -m chat_chronicle.cli serve`
>
> **2. A green light in the UI is not evidence.** One client showed the server in Settings but omitted it from `/mcp`, and called the tools fine anyway. The only acceptance test I trust now: ask a question whose answer can *only* come from the archive, and check that the answer cites a real ID.
>
> **3. Put the mutable part in the environment, not the command.** Database selection lives in `CHAT_CHRONICLE_DB`, never in the args. Switching between a frozen evaluation snapshot and the live archive is one environment value across all four clients — the launch command never changes.
>
> One more thing worth saying out loud: "local server" does not mean "local data." The process and the SQLite file stay on my machine, but whatever a tool returns goes into the model request — to OpenAI for Codex, to Anthropic for Claude. So Chronicle is read-only by construction: SQLite opened `mode=ro` with `query_only` on, three retrieval tools, no write path, and bounded transcript retrieval so you choose *how much* leaves the machine.
>
> 446 tests, MCP suite green on Windows and Ubuntu, docs written from what was actually verified rather than what should have worked.
>
> MCP is a real standard and it does deliver. Just budget for the last mile — on Windows, the last mile is per-client.
>
> Which client gave you the most trouble? I'll compare notes.
>
> #MCP #ModelContextProtocol #AIEngineering #Windows #DeveloperTools #LocalFirst #Python

---

## Shorter variant (higher completion rate, less detail)

> **"MCP is a standard" — so why did I write four different configs for one server?**
>
> Chronicle turns my scattered ChatGPT / Claude / Codex history into one local searchable archive. Last week it got read-only MCP recall: three tools, one stdio process, no writes.
>
> Wiring it into four Windows clients took four dialects. TOML with doubled backslashes for Codex. A CLI-registered local scope for Claude Code. JSON for Claude Desktop — which only connected after I *removed* `"type": "stdio"`, a property most examples tell you to include.
>
> The three things I'd tell anyone starting today:
>
> → Point hosts at `.venv\Scripts\python.exe -m your.module`, not a Poetry-generated `.cmd` shim. Native hosts won't spawn the shim.
> → A server showing "enabled" in the UI proves nothing. One client never listed mine under `/mcp` and called it successfully the whole time. Test with a question only your data can answer.
> → Keep the switchable part (the database path) in an env var, so the launch command is identical everywhere.
>
> And the part people skip: local server ≠ local data. The process stays on your machine; the tool output goes to whichever model provider the client uses. Build read-only, bound your outputs, and decide deliberately what leaves the box.
>
> The standard is real. The last mile is per-client.
>
> #MCP #AIEngineering #DeveloperTools #LocalFirst

---

## Notes for posting

- Best hook line is the first one — it states a contradiction and immediately backs it with a number.
- Keep the Claude Desktop `"type": "stdio"` detail. It is the single most surprising, most quotable, most useful fact in the post.
- The "green light is not evidence" point is the strongest comment-bait; the closing question reinforces it.
- Every version claim is dated. If you post more than a few weeks out, either keep the "verified 27 July 2026" framing or drop version numbers rather than let them read as current.
- Do not include: absolute local paths, conversation IDs, database contents, or anything from `.chronicle/`. The drafts above are already clean of these.

---

## Sources

All claims trace to these files in `c:\work\Github\mcp-chat-chronicle`:

| Claim in the post | Source | Location |
| --- | --- | --- |
| Four clients, four config formats; supported-client matrix | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Supported clients" table, lines 54–65 |
| Codex TOML format, doubled backslashes, `cwd` | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Codex, ChatGPT desktop, CLI, and IDE", lines 154–187 |
| Claude Code local scope + project `.mcp.json` + scope-precedence trap | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Claude Code", lines 201–249 |
| Claude Desktop rejects `"type": "stdio"` | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Claude Desktop", lines 252–283 |
| Same, as an accepted integration finding | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-validation-review.md` | "Accepted Integration Findings", lines 39–56 |
| Same, as a recorded defect/rework item | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-completion-report.md` | §16 and §19, lines 142–168 |
| Poetry 2.3.4 produced `chronicle.cmd`, not `.exe`; native hosts would not launch the shim | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-completion-report.md` | §4 and §9, lines 29–34 and 79–92 |
| Stable Windows launch contract (`.venv\Scripts\python.exe -m chat_chronicle.cli serve`) | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Architecture and lifecycle", lines 93–106 |
| Same, accepted by PM | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-validation-review.md` | "Accepted Integration Findings", lines 40–45 |
| Codex Windows app called tools but did not list the server under `/mcp` | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-completion-report.md` | §12 and §17, lines 116–121 and 149–155 |
| "UI status is not evidence of tool execution" | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-completion-report.md` | §26 Known Limitations, lines 276–286 |
| Database selection stays in `CHAT_CHRONICLE_DB`, not in args; frozen/active switching | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Database selection and switching", lines 120–152 |
| Three read-only tools and their bounds | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | Tool table, lines 108–118 |
| SQLite `mode=ro` + `PRAGMA query_only = ON`; no write path | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1A-completion-report.md` | §7 "Read-Only Database Design And Evidence", lines 51–58 |
| "Local server ≠ local data" — tool output goes to the client's model provider | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Privacy and trust boundary", lines 386–402 |
| 446 tests passing, 1 skipped; Ruff and Poetry checks clean | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1B-completion-report.md` | §22 "Automated Validation Results", lines 214–227 |
| MCP suite runs on the Windows + Ubuntu CI matrix | `c:\work\Github\mcp-chat-chronicle\md\handoffs\reports\WP-4.1A-completion-report.md` | §15 "CI And Cross-Platform Coverage", lines 124–128 |
| Chronicle product description (local-first, normalized SQLite/FTS archive) | `c:\work\Github\mcp-chat-chronicle\README.md` | Header and "Choose your path", lines 1–10 |
| Tested versions, verified 27 July 2026 | `c:\work\Github\mcp-chat-chronicle\docs\mcp-client-setup.md` | "Tested versions and limitations", lines 453–465 |
| Portable project configuration example | `c:\work\Github\mcp-chat-chronicle\.mcp.json` | whole file |
| Feature shipped recently (two commits, this week) | git history | `b459ef8` feat: add FastMCP read-only server; `3b02d34` docs: complete MCP client integration |

### Deliberately excluded

- Frozen-snapshot aggregate counts (711 conversations / 28,370 messages) — accurate, but archive-size disclosure with no upside for this post.
- Exact client build numbers (Codex CLI `0.146.0-alpha.3.1`, Codex/OWL `26.721.41059`, Claude Code `2.1.81`, Claude Desktop `1.24012.9`) — they date the post fast. Available in `docs/mcp-client-setup.md` lines 453–457 if you want them.
- Anything under `.chronicle/`, which is git-ignored private evidence.
