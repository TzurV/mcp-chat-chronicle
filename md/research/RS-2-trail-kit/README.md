# WorkTrail Trail Kit — log any AI chat session, today

One schema, many writers, a dumb folder as the interface. Records accumulate in trail folders until WorkTrail's `trail` adapter (backlog) ingests them. Full rationale: `../RS-2-chat-self-identification-findings.md`.

## Locations

- **Agent surfaces** (Claude Code, Codex, Cowork): `<workspace>\.worktrail\trail\*.json` — per-repo, auto-associates the project. Add `.worktrail/` to each repo's `.gitignore`.
- **Composer surfaces** (ChatGPT, Copilot, Claude web): `C:\work\worktrail\trail\*.json` — global, written by `trail-save.ps1` from your clipboard.

## Install (10 minutes, once)

| Surface | What to do |
| --- | --- |
| Claude Code | Append `snippet-CLAUDE.md` content to repo `CLAUDE.md` (or `~/.claude/CLAUDE.md` for all projects) |
| Codex CLI + app | Append `snippet-AGENTS.md` content to repo `AGENTS.md` (or `~/.codex/AGENTS.md`) |
| Cowork | Create a skill from `cowork-skill-SKILL.md` via Claude app Settings → Capabilities |
| ChatGPT | Add the ChatGPT block from `composer-instructions.md` to Custom Instructions |
| Windows Copilot | Tell it once to remember the Copilot block from `composer-instructions.md` |
| Claude web/desktop chat | Add its block to profile personalization |
| Your side | Put `trail-save.ps1` somewhere handy (pin a shortcut); it creates the global folder on first run |

## Use

In any surface: **"Add to trail log."** Agent surfaces write the file themselves and reply with the path. Composer surfaces reply with a JSON block → copy → run `trail-save.ps1` (it prompts for the conversation URL where relevant).

## Ground rules baked into every instruction

- Null-discipline: engines never invent IDs; unverifiable → null.
- `session_id` = runtime instance, not conversation (conversations are joined at ingest).
- No location/preferences in records.
- ChatGPT: use the web `/c/...` address-bar URL, never a Share link.
