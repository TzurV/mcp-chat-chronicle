# RS-2 — Findings: Chat Self-Identification Survey & the Trail-Log Design

**Date:** 2026-07-13 · **Method:** the same question ("provide information on this chat like ID and any other metadata") posed live to six AI surfaces on the owner's Windows 11 machine; answers analyzed for verifiable facts vs confabulation vs capability.
**Companion:** `RS-1-chat-history-access-findings.md` (retrieval) · this memo (live capture / self-identification) · artifacts in `RS-2-trail-kit/`
**Status:** complete except one pending check (§4, Codex app UUID grep — slot marked TODO)

---

## 1. The universal result

**No engine can report its own conversation identity. Six surfaces, three vendors, zero exceptions** — including chat *titles*, which live in the UI layer, invisible to the model that generated them. Conversation IDs exist in every backend (Copilot said so explicitly) and are deliberately unexposed. This empirically confirms master-plan §1.6 across the entire ecosystem.

Corollary discovered en route: **even runtime session IDs don't identify conversations.** One 4-day Cowork chat occupied at least two `local_*` session directories; Claude Code resumed/branched sessions span multiple `.jsonl` files. *Conversation is a derived entity, joined at ingest — never a captured field.*

## 2. Capability matrix

| Surface | Knows/recovers own ID? | Can write files? | Join key to full transcript | Writer tier |
| --- | --- | --- | --- | --- |
| **Claude Code** (CLI/VS Code) | ✅ forensically — read own newest `.jsonl`, confirmed `sessionId`, version, branch, cwd | ✅ shell | Direct: `sessionId` + transcript path; write-echo as backstop | **Agent-writer (best)** |
| **Codex CLI** (VS Code) | ❌ | ✅ shell, *workspace-write only* | Write-echo (trail-write command lands in own rollout) + cwd/time | **Agent-writer** |
| **Codex app** | ❌, but leaks a UUIDv7 in its writable-roots path (`~/.codex/visualizations/.../<uuid>`) | ✅ workspace-write | Write-echo; path-UUID as `session_hint` (TODO §4) | **Agent-writer** |
| **Cowork** (Claude desktop) | ⚠️ runtime-instance ID leaks via env paths; rotates within one chat; no title | ✅ file tools | Runtime IDs as hints; account/profile UUIDs; workspace+time | **Agent-writer** |
| **ChatGPT** (desktop/web) | ❌ (points user to web `/c/<id>` URL) | ❌ | **Human-pasted URL** — parses to the conversation ID used in official exports → clean merge | **Composer** |
| **Windows Copilot** | ❌ (confirms IDs exist internally, unexposed) | ❌ | **None, ever** (no URL, no usable export ID) — trail entries are its *only* good metadata | **Composer** |

Claude web/desktop chat (not separately interviewed): composer tier by pattern, with the `/chat/<uuid>` URL as join key (matches export `uuid`).

## 3. Design rules extracted (for any "log this chat" instruction)

1. **Never ask a model for IDs** — ask for environment facts + a one-sentence note, with hard null-discipline ("use null, never invent"). Composer engines confabulate confidently (one reported a wrong country while its timezone said otherwise; model self-reports are informative, not authoritative).
2. **Capability, not vendor, decides the pattern:** agent-writers write the record themselves; composers emit filled JSON for a human clipboard-catcher; the human carries the one thing no model sees — the address-bar URL.
3. **Identity is established at ingest, not capture.** The *act of writing* the trail file is the best marker: shell-agents' write commands are recorded in their own transcripts (self-fulfilling join). Pasted URLs match export IDs. Leaked path-UUIDs go in `session_hint` as tiebreakers.
4. **One schema, many writers, a dumb folder as the interface** — per-workspace `.worktrail/trail/` for restricted-write agents (auto-associates project), global `C:\work\worktrail\trail\` for workspace-less composers.

## 4. Open item (TODO)

Codex app: grep `~/.codex/sessions/2026/07/**` filenames and content for `019f4778-e308-77b3-bcd7-58fb6340dd1e` (PowerShell commands provided in chat 2026-07-13). Filename hit → Codex app gets forensic self-ID like Claude Code. Content hit → recoverable at ingest. No hit → write-echo join only (already sufficient). Record the result here.

## 5. Trail record schema v1

See `RS-2-trail-kit/trail-record.schema.json`. Fields: `trail_version, logged_at*, engine*, app, session_id` (verified runtime-instance ID only), `session_hint` (unverified environmental leaks), `conversation_url` (human-pasted), `title, workspace, model` (self-reported = informative), `note*`, `marker`. `*` = required. Deliberately excluded: location, preferences, anything profiling-shaped — the trail is for *finding sessions*, and minimal records stay safe to back up.

## 6. Digestion map — where the project consumes this

| Finding | Destination | Action |
| --- | --- | --- |
| `ai-title` record exists in Claude Code JSONL (real titles in-band); 7 record types; `uuid`/`parentUuid` threading; `isSidechain` sub-agent records; **resumed sessions span multiple files** | **WP-3.1** format memo + fixtures | Fold into the memo; add multi-file-session and sidechain fixtures; prefer `ai-title` over title synthesis |
| Conversation = derived entity (multi-runtime-session chats in both Anthropic surfaces) | **Data model** (§5 master plan) + backlog | No v1 schema change (extractor already records session ids/cwd/timestamps); add backlog item: *thread linkage — group runtime sessions into logical conversations* |
| Trail drop-box + this kit | **New backlog/v1.x candidate: `trail` adapter** — sweeps `.worktrail/trail/` (per known workspace) + global folder; trivial JSON reader | Small WP after prototype; merges naturally with CO-2 |
| URL join key (ChatGPT `/c/<id>`, Claude `/chat/<uuid>` = export IDs) | **CO-2 spec** | Confirm: merge by *parsed conversation ID*, not raw URL string |
| Cowork `local-agent-mode-sessions` store discovered; Codex app local rollouts confirmed | **§1.3 Class B candidates** + **WP-1.5 scan-local** probe list | Add both paths to scan-local; Cowork extractor = backlog candidate |
| `cleanupPeriodDays` behavior (RS-1 §8) + null-discipline + tier model | **WP-6.1 README** | Setup recommendations section: raise Claude Code retention; prefer CLI tools for auto-capture; how to install the trail kit |
| The survey itself | **LP plan (§7)** | Strong new post candidate: *"I asked six AI engines to identify themselves. None could. Here's what leaked anyway."* Empirical, reproducible, demonstrates the project's origin constraint live — consider it for the LP-3 forensics slot or as LP-3.5 |
| Write-echo self-fulfilling join | **Appendix A** (marker-join epilogue) | The shelved Version B marker returns in reliable form: for shell-agents the log-write *is* the marker. One-paragraph addendum when plan next consolidates |

## 7. Artifacts (in `RS-2-trail-kit/`)

`README.md` (install/usage per engine) · `trail-record.schema.json` · `trail-save.ps1` (clipboard-catcher for composer engines) · `snippet-CLAUDE.md` (Claude Code instruction) · `snippet-AGENTS.md` (Codex CLI/app instruction) · `composer-instructions.md` (ChatGPT / Copilot / Claude-web saved prompts) · `cowork-skill-SKILL.md` (Cowork skill, install via Settings → Capabilities).

These work **today**, before any WorkTrail code — the trail folder simply accumulates until the `trail` adapter exists to ingest it.
