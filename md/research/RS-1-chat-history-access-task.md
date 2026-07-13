# RS-1 — Task Definition: Chat-History Access Methods on Windows 11

**Type:** Research spike (no code) · **Feeds:** adapter roadmap (§1.3 source classes), WP-3.1 spike, CO-2 planning
**Owner:** research executor (AI-assisted) · **Requested by:** Tzur · **Date:** 2026-07-12

## Objective

For each target engine, identify every practical method to (a) **download/export** complete chat history, and/or (b) **force or locate a durable local copy** on a Windows 11 machine — so WorkTrail adapters can ingest it. Prefer **CLI or programmable** methods over manual UI flows.

## Target engines

1. **Claude** (claude.ai web + Claude Desktop) and **Claude Code** (CLI)
2. **ChatGPT** (chatgpt.com web + Windows desktop app) and **Codex** (CLI/desktop)
3. **Windows Copilot** (the Copilot app on Windows 11; consumer, not M365)

## Questions to answer per engine

1. **Official export:** does one exist? Trigger method (UI/API), turnaround time, delivery mechanism, file format(s), completeness (all history? attachments? projects?).
2. **Durable local store (Class B):** does the tool write complete transcripts to disk as a side effect of normal use? Exact Windows paths, format, retention behavior, version sensitivity.
3. **Local cache (Class C):** what partial/fragile local data exists (IndexedDB/LevelDB/WebView2)? Only catalog — never build on it.
4. **Programmatic/CLI access:** official APIs, unofficial-but-stable endpoints, community tools. For unofficial methods: note ToS/stability/auth risks explicitly.
5. **"Force a local copy" options:** settings, flags, env vars, or usage patterns that cause the engine to persist history locally (e.g., using the CLI variant instead of web).
6. **Recommended WorkTrail capture method** + source class (A/B/C) + automation ceiling (fully automatic / semi-automatic / manual-with-reminder).

## Method & rules

- Web research + **local verification on this machine where possible** (path existence only — read-only, no parsing; consistent with design rule 4).
- Distinguish clearly: *verified locally* vs *verified from official docs* vs *community-reported*.
- Flag anything that violates provider ToS or depends on session-token scraping as **use-at-own-risk; not for the shipped product** (may still inform personal use).
- No real chat content leaves the machine; no exports committed to the repo.

## Deliverable

`md/research/RS-1-chat-history-access-findings.md`: per-engine section answering Q1–Q6, a summary matrix (engine × method × class × automation ceiling), implications for the adapter roadmap, and sources.

## Acceptance

- All five engines covered; every claim tagged with verification level.
- Summary matrix usable directly as input to `sources` table defaults and scan-local probe list.
- Explicit recommendation per engine, including "not worth pursuing" where honest.
