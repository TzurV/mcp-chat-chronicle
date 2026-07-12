# Change Order 01 — Adaptation Instructions for the Implementation Manager

**Applies to:** `md/master-plan.md` v3.1 (which remains the authoritative plan except as amended here)
**Origin:** LinkedIn community feedback review + prototype-priority decision by the project owner (Tzur), 2026-07-12
**Status:** APPROVED — apply immediately

**Read this as a diff against the master plan.** All design rules (§2) and Class B ground rules (M3) remain in force. Nothing here relaxes the fixtures/idempotency/graceful-degradation requirements.

---

## CO-0. Priority directive: working prototype ASAP, CLI-extraction-first

**Current status acknowledged:** WP-0.1 and WP-1.1 through WP-1.3.2 are accepted (schema, DB layer, ChatGPT + Claude importers done); WP-1.4 is next. This CO adjusts the remaining order — nothing accepted is redone.

The owner's preferred capture path is **CLI-agent extraction (Class B)**, with manual export handling for web chats acceptable for now. Remaining build order:

```
    WP-1.4  CLI ingest + stats           (in flight — finish as planned)
    CO-1    schema migration + importer touch-ups   ← insert here, before search
    WP-2.1  FTS search + open            (with CO-1 link-back behavior)
    WP-3.1  Claude Code extractor        ← PULLED FORWARD (was v1.1)
─── PROTOTYPE: search your real Claude Code + export history end-to-end ───
    WP-1.6  collect + scheduling docs
    ...then per master plan (WP-3.2 Cursor, Codex extractor per CO-3,
       M4 MCP time-fence now counted from WP-2.1 acceptance, M5, M6)
```

Rationale: the owner's daily work lives in CLI agents; extracting `~/.claude/projects` plus the already-built export importers gives a *personally useful* prototype in the shortest path. Design rule 2 still applies — WP-3.1 is plain concrete code; the adapter abstraction is still extracted only at the third adapter.

**WP-3.1 prerequisite (unchanged from CO-3 below):** the research spike studies existing parsers first.

## CO-1. Schema amendments — one migration, land before WP-2.1

WP-1.1 is accepted, so these arrive as a **single migration** (bump `PRAGMA user_version`), plus small touch-ups to the accepted importers where noted.

1. **`projects` table** + nullable `project_id` on `conversations`. Inferred from repo/cwd for coding-agent sources; manually assignable later for web chats.
   ```sql
   CREATE TABLE projects (
       id INTEGER PRIMARY KEY,
       name TEXT UNIQUE NOT NULL,
       root_path TEXT,               -- repo/folder where known
       created_at TEXT
   );
   -- conversations: ADD COLUMN project_id INTEGER REFERENCES projects(id)
   ```
2. **Link-back guarantee (owner requirement — treat as hard AC on every adapter):** every conversation row must carry enough to get back to the original session. Fields:
   - `title` — the chat/session name (already in schema; **adapters MUST populate it** — verify the two accepted importers do, fix if not; if the source has no name, synthesize `"<project>: <first user message, truncated>"`)
   - `url` — deep link for web sources (already in schema)
   - `provider_conv_id` — stable source-side ID (already in schema)
   - `origin_path` TEXT — **NEW column**: local path to the source transcript for CLI-agent sources (e.g. the session `.jsonl` file). This is the link-back for sources with no URL.
   - `resume_hint` TEXT — **NEW column, nullable**: the command that reopens the session where the tool supports it (e.g. `claude --resume <session-id>`; Codex `codex resume`). Populated best-effort.
   - `chronicle open <id>` behavior update: web → launch `url`; CLI-agent → show transcript AND print `origin_path` + `resume_hint`.
3. Add `'manual_entry'` to the `sources.source_type` CHECK now (cheap pre-release; used by the deferred CO-2).

## CO-2. `chronicle note` (manual web-chat entry) — DEFERRED

Approved in principle, **scheduled post-M2** to protect the prototype path. Spec (for later): `note --url <chat-url> --project X "one-liner"` → conversation row with source_type `manual_entry`; later export ingests merge with it by URL match. Do not build now; CO-1.3 already prepared the schema.

## CO-3. v1.1 scope changes

- **Claude Code extractor (WP-3.1) pulled forward** per CO-0. Cursor (WP-3.2) stays in v1.1 position.
- **Codex CLI extractor: candidate, build on demand** — format verified: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`, older sessions compressed to `.jsonl.zst` (support reading both).
- **Mandatory spike inputs before WP-3.1/3.2:** read the parsers of [Agent Sessions](https://github.com/jazzyalex/agent-sessions) (closest prior art — macOS multi-agent history browser), [claude-record](https://github.com/davidglogan/claude-record), [codex-trace](https://github.com/PixelPaw-Labs/codex-trace); they are free format documentation. Local inspection on the owner's machine remains the authority over any blog/repo claim.
- **Positioning table (§1.4): add Agent Sessions row.** Our differentiators: Windows-first · web chats + coding agents unified in one archive · knowledge distillation · MCP recall.

## CO-4. v1.2 additions (M5)

- **New WP: `chronicle brief --project X`** — forward-looking paste-able context for the *next* AI session (recent activity, decisions, open threads, next steps). Sibling of WP-5.6 (digest), same machinery, same offline-only constraint.
- WP-5.6 docs: mention the daily "mission control" variant (`--days 1`) alongside weekly.

## CO-5. v2 / backlog additions

- **v2 (after V2-2): git correlation** — link conversations ↔ repo/branch/commits via repo path + time window ("git says what, chats say why"). Do not squeeze into v1.
- **Backlog: Markdown/Obsidian export** of digests + knowledge items (they are already markdown-shaped).

## CO-6. Rename: **WorkTrail** (owner's choice)

- OpenAI shipped "Chronicle" for Codex (Apr 2026) — the old name is SEO-dead.
- Note: `worktrail` GitHub org + worktrail.net are held by an old time-tracking SaaS. **Recommended concrete naming: repo/PyPI `worktrail-ai`, CLI command `worktrail`** (short alias `wt` if free). Owner has final say on the exact form before the repo goes public; nothing else blocks on this.
- Rename touches: repo, `pyproject.toml` name, package dir, CLI entry point, README, this `md/` folder's references. Zero architecture impact. Do it before first public push.

## CO-7. Framing (docs/posts only)

Lead framing for README + LP-1 becomes: **"AI tools are multiplying, but the activity trail is missing."** Product one-liner: *a local-first activity and context ledger across AI tools.* The §1.2 architecture description is unchanged.

## Explicitly rejected (do not relitigate)

Screenpipe-style screen capture (Class C by another name) · OpenWebUI consolidation (changes workflow, doesn't rescue history) · Databricks Omnigent / Createst.ai (different problem, not local-first) · Compositor (unverified; pending a reference link) · live logging / marker join (still shelved per master plan Appendix A.6).

## Acceptance for this change order

1. CO-1 migration lands before WP-2.1 merges; accepted importers (WP-1.2/1.3) verified/patched for the title + link-back guarantees.
2. Prototype milestone demo: `worktrail search "<something real>"` returns ranked hits spanning the owner's actual Claude Code history AND an ingested export; `worktrail open <id>` launches the URL (web source) or shows the transcript with `origin_path` + `resume_hint` (CLI source).
3. Master plan stays v3.1; this file is the amendment layer. Next consolidation of plan+CO into v3.2 happens after the prototype ships.
