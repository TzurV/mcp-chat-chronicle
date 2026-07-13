# RS-1 — Findings: Chat-History Access Methods on Windows 11

**Date:** 2026-07-12 (§8 added same day after local verification) · **Status:** complete
**Verification tags:** [OFFICIAL] provider docs · [COMMUNITY] third-party tools/reports · [LOCAL-VERIFY] confirm on this machine (read-only path check; `scan-local` will automate this later)

---

## 1. Claude (claude.ai web + Claude Desktop)

**Official export [OFFICIAL]:** Settings → Privacy → **Export data** (web or Claude Desktop; *not* mobile). Email link typically within minutes (up to a few hours for large accounts); **link expires 24 h**. ZIP contains `conversations.json` (+ user/projects files). Complete history. Source: [Claude Help Center](https://support.claude.com/en/articles/9450526-export-your-claude-data).
**Durable local store:** none for web/desktop chats — history is server-side.
**Local cache (Class C):** Claude Desktop keeps app-state/LevelDB caches; community tool [claude_desktop_export_browser](https://github.com/davidteren/claude_desktop_export_browser) reads them. Catalog only — partial, wiped on logout/update.
**Programmatic:** no official consumer-history API. Unofficial claude.ai endpoints with scraped session tokens exist — ToS risk, brittle. **Not for the product.**
**Force-local options:** none. The behavioral fix: do work you want auto-captured in **Claude Code** (or Cowork with the repo mounted) instead of the web chat.
**WorkTrail method:** Class A export importer (**already accepted**, WP-1.3/1.3.1). Automation ceiling: **manual-with-reminder** (export request can't be automated officially). Practical cadence: monthly + before any migration.

## 2. Claude Code (CLI)

**Durable local store [OFFICIAL]:** the gold standard. Full transcripts at
`%USERPROFILE%\.claude\projects\<encoded-project-path>\<session-id>.jsonl` — one folder per project, one JSONL per session. Source: [.claude directory docs](https://code.claude.com/docs/en/claude-directory).
**⚠️ Retention — the "force it to keep history" lever [VERIFIED — see §8]:** Claude Code deletes transcripts older than `cleanupPeriodDays` (default **30**) at startup. Mitigated on the owner's machine 2026-07-12 by setting it to 99999. Full details, the `0`-value trap, and the README recommendation in **§8**. WorkTrail's nightly `collect` remains the structural safety net: ingest before cleanup.
**Programmatic:** just read the files; `claude --resume <session-id>` reopens sessions (our `resume_hint`).
**Privacy note for README:** transcripts are plaintext and can contain secrets echoed by tools; WorkTrail inherits this — local-only stance + `.gitignore` already cover it, but say it explicitly.
**WorkTrail method:** Class B extractor (WP-3.1, prototype-critical). Ceiling: **fully automatic**.

## 3. ChatGPT (web + Windows desktop app)

**Official export [OFFICIAL]:** Settings → Data Controls → **Export data** → email with download link (**expires 24 h** — don't miss it; yours is pending now). ZIP with `conversations.json` (tree-shaped mapping — our accepted importer, WP-1.2), `chat.html`, etc. Usually arrives in minutes; hours on large accounts.
**Durable local store:** none — desktop app is a wrapper; history is server-side. Cache = Class C.
**Programmatic [COMMUNITY — use-at-own-risk, personal use only, NOT for the product]:** the web app's internal `/backend-api/conversations` endpoints work with a browser bearer token. Maintained tools: [chatgpt-exporter (CLI)](https://github.com/FdezRomero/chatgpt-exporter) · [export-chatgpt](https://github.com/brianjlacy/export-chatgpt) (works with Team plans, 2026-03) · [hoya98 extension + console script](https://github.com/hoya98/chatgpt-export) · [ocombe's bash/curl gist](https://gist.github.com/ocombe/1d7604bd29a91ceb716304ef8b5aa4b5). Caveats: tokens expire quickly, endpoints undocumented and change without notice, ToS gray zone. Realistic use: a personal semi-automated refresh between official exports — never shipped as a WorkTrail feature.
**WorkTrail method:** Class A export importer (**accepted**). Ceiling: **manual-with-reminder**; optional personal token-based refresh at your own risk.

## 4. Codex (CLI)

**Durable local store [OFFICIAL/COMMUNITY]:** `%USERPROFILE%\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl` (+ `history.jsonl`); **older sessions compressed to `.jsonl.zst`** — our accepted extractor (WP-1.3.2) reads `.jsonl`; `.zst` support is the on-demand CO-3 follow-up. Viewer prior art: [codex-trace](https://github.com/PixelPaw-Labs/codex-trace).
**Retention [COMMUNITY, LOCAL-VERIFY]:** sessions accumulate (users report multi-GB growth — so deletion is not aggressive); check `config.toml` for any cleanup settings when convenient.
**WorkTrail method:** Class B extractor (**accepted**). Ceiling: **fully automatic**.

## 5. Windows Copilot (consumer app on Windows 11)

The weakest of the five — plan expectations accordingly.
**Official export [OFFICIAL]:** [account.microsoft.com/privacy](https://account.microsoft.com/privacy) → Copilot activity history → **Export** → **CSV** download (no email wait). Columns reported: Conversation / Time / Author (AI or Human) / Message — but **[COMMUNITY] quality complaints are consistent: truncated long responses, formatting jumble**. Retention server-side ~18 months. Sources: [MS Support](https://support.microsoft.com/en-us/privacy/manage-your-copilot-activity-history-in-the-privacy-dashboard) · [export walk-through](https://univik.com/help/export-copilot-chats.html).
**Durable local store:** none found — the app is a WebView2 shell; local data = Class C cache. No official consumer API; users are actively requesting portability ([MS Q&A thread](https://learn.microsoft.com/en-au/answers/questions/4378824/request-for-data-portability-and-chat-history-expo)).
**Force-local options:** none. Per-response manual export (Word/PDF) exists but is useless for bulk.
**WorkTrail method:** optional **Class A-minus CSV importer** — cheap to build (flat CSV → conversations grouped by Conversation column), but mark quality "degraded (truncation)" in `sources`. Ceiling: **manual**. Honest verdict: support it because it's cheap, expect little, revisit if Microsoft ships real portability.

---

## 6. Summary matrix

| Engine | Best method | Class | Format | Automation ceiling | WorkTrail status |
| --- | --- | --- | --- | --- | --- |
| Claude (web/desktop) | Official export (email, 24 h link) | A | JSON (flat array) | Manual + reminder | Importer **accepted** |
| Claude Code | Read `~/.claude/projects` JSONL | B | JSONL/session | **Fully automatic** | WP-3.1 next (prototype) |
| ChatGPT (web/desktop) | Official export (email, 24 h link); unofficial API for personal refresh | A | JSON (tree mapping) | Manual + reminder (semi-auto at own risk) | Importer **accepted** |
| Codex | Read `~/.codex/sessions` JSONL(+zst) | B | JSONL/rollout | **Fully automatic** | Extractor **accepted** (zst pending) |
| Windows Copilot | Privacy-dashboard CSV export | A− (degraded) | CSV, truncation issues | Manual | **New candidate**: cheap CSV importer |

## 7. Actions & adapter implications

1. **Owner, today:** (a) watch for the ChatGPT export email — **link dies in 24 h**; (b) request the Claude export now (same 24 h rule); (c) ~~raise Claude Code's cleanup period~~ **done 2026-07-12, see §8**; (d) optionally pull a Copilot CSV once to judge whether it's worth an importer for your usage.
2. **Plan candidates (no change order yet):** Copilot CSV importer as a low-effort v1.x backlog item; `.jsonl.zst` support (existing CO-3 item); add `%USERPROFILE%\.codex` + Copilot to the `scan-local` probe list.
3. **Docs:** the "prefer CLI tools for auto-capture" behavioral note belongs in the README — it's the practical answer to "force a local copy" for Anthropic/OpenAI ecosystems: **you can't force the web apps; you can choose the CLI variants.**
4. **Do not ship** token-scraping paths (ChatGPT backend-api, claude.ai endpoints, Copilot scraping) in the product under any framing; personal-machine use is the owner's own call.

## 8. Claude Code transcript retention — VERIFIED and applied (2026-07-12)

Follow-up to §2, confirmed by web verification and applied on the owner's machine.

**The facts:**
- Setting: **`cleanupPeriodDays`** in `%USERPROFILE%\.claude\settings.json`. Default **30 days**.
- The cleanup pass runs **at Claude Code startup**: session `.jsonl` files under `~/.claude/projects/` older than the threshold are deleted silently — no warning, no recycle bin ([issue #59248](https://github.com/anthropics/claude-code/issues/59248), [The Register](https://www.theregister.com/ai-and-ml/2026/06/30/claude-code-users-complain-their-chat-records-are-being-mysteriously-wiped-out/5264673)).
- **⚠️ The `0` trap:** schema docs suggest `0` = "disable cleanup," but the actual behavior is **disable transcript persistence entirely** — no `.jsonl` written at all ([issue #23710](https://github.com/anthropics/claude-code/issues/23710)). Never use 0; use a large positive number.
- Settings are read fresh on each `claude` launch; already-running sessions keep the old value until exited. Because cleanup runs at startup *after* reading settings, there is no restart-ordering window where a wipe can slip through.

**Applied on the owner's machine (2026-07-12):**

```json
{
  "effortLevel": "high",
  "autoUpdatesChannel": "latest",
  "model": "opus",
  "cleanupPeriodDays": 99999
}
```

**Consequences for WorkTrail:**
1. Transcripts older than 30 days were likely already purged before this change — the setting protects the future, not the past. The WP-3.1 extractor should expect a ~30-day horizon on first ingest of this machine.
2. **README recommendation (adopt at WP-6.1):** instruct Claude Code users to set `cleanupPeriodDays` high (never 0), and note that WorkTrail's nightly `collect` is the structural protection — history is safe once ingested, regardless of the source tool's retention.
3. `scan-local` (WP-1.5) could optionally read this setting and warn when it's at the default — a nice trust-building touch; backlog note, not scope.

## 9. Owner runbook — data retrieval & settings checklist (as of 2026-07-12)

The operational to-do distilled from §1–§8. Settings work is **complete** (Claude Code was the only engine with a retention lever; fixed in §8 — exit any running `claude` session for it to take effect). Everything below is retrieval.

**Verify the Class B stores (2 min, PowerShell):**

```powershell
dir $env:USERPROFILE\.claude\projects     # expect ~30-day horizon (pre-fix purges)
dir $env:USERPROFILE\.codex\sessions      # check depth; note any .jsonl.zst files
```

Also glance at `$env:USERPROFILE\.codex\config.toml` — no cleanup setting is known to exist (sessions reportedly grow unbounded), 30 seconds confirms it. Many `.jsonl.zst` files → schedule the CO-3 decompression follow-up.

**Retrieval steps:**

| # | Engine | Action | Timing/notes |
| --- | --- | --- | --- |
| 1 | ChatGPT | Download export zip from pending email | **Link expires 24 h**; check spam; re-request freely if missed |
| 2 | Claude web | Request export: claude.ai → initials → Settings → Privacy → Export data | Email in minutes–hours; same 24 h rule |
| 3 | Copilot | [account.microsoft.com/privacy](https://account.microsoft.com/privacy) → Copilot activity → Export CSV | Instant download, no email. Eyeball quality once — this decides whether the Copilot importer ever gets a WP |
| 4 | All | Park all zips/CSVs in one drop folder, e.g. `C:\work\ai-exports\` (outside the repo) | Becomes the `ingest-folder` target + real-data test set for WP-1.4 |

**Settings status per engine:** Claude Code — `cleanupPeriodDays: 99999` applied (§8). Codex — nothing to set (verify config.toml once). Claude web / ChatGPT / Copilot — **no "keep local" or retention settings exist**; export cadence is the only lever, and WorkTrail's nightly `collect` becomes the structural protection once WP-3.1 lands.

**End state:** after steps 1–4, retrieval is fully harvested; everything further waits on code (WP-1.4 ingest makes the exports searchable; WP-3.1 makes Claude Code history automatic).

## Sources

[Claude export](https://support.claude.com/en/articles/9450526-export-your-claude-data) · [.claude directory](https://code.claude.com/docs/en/claude-directory) · [Claude Code history guide](https://kentgigger.com/posts/claude-code-conversation-history) · [claude_desktop_export_browser](https://github.com/davidteren/claude_desktop_export_browser) · [chatgpt-exporter](https://github.com/FdezRomero/chatgpt-exporter) · [export-chatgpt](https://github.com/brianjlacy/export-chatgpt) · [hoya98/chatgpt-export](https://github.com/hoya98/chatgpt-export) · [ocombe gist](https://gist.github.com/ocombe/1d7604bd29a91ceb716304ef8b5aa4b5) · [codex-trace](https://github.com/PixelPaw-Labs/codex-trace) · [Copilot activity history](https://support.microsoft.com/en-us/privacy/manage-your-copilot-activity-history-in-the-privacy-dashboard) · [Copilot export walk-through](https://univik.com/help/export-copilot-chats.html) · [Copilot portability request thread](https://learn.microsoft.com/en-au/answers/questions/4378824/request-for-data-portability-and-chat-history-expo) · [cleanupPeriodDays retention investigation](https://dev.classmethod.jp/en/articles/claude-code-conversation-history-retention/) · [issue #23710 (0-value trap)](https://github.com/anthropics/claude-code/issues/23710) · [issue #59248 (silent cleanup)](https://github.com/anthropics/claude-code/issues/59248)
