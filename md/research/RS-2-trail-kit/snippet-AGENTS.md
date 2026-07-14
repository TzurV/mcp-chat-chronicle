# Snippet for AGENTS.md (Codex CLI and Codex app) — add to repo-root AGENTS.md or ~/.codex/AGENTS.md

## Trail log

When the user says "Add to trail log" (or "/trail"):

1. Generate a 4-char random hex `<hex>`.
2. Write `.worktrail/trail/<UTC yyyyMMdd-HHmmss>-codex-<hex>.json` in the workspace root (create the directory; ensure `.worktrail/` is gitignored):

```json
{
  "trail_version": 1,
  "logged_at": "<ISO datetime with timezone>",
  "engine": "codex",
  "app": "<'Codex CLI' or 'Codex app', whichever you are running in if determinable, else null>",
  "session_id": null,
  "session_hint": { "writable_roots_uuid": "<any UUID visible in your writable roots / env paths, else omit>" },
  "conversation_url": null,
  "title": null,
  "workspace": "<cwd>",
  "model": "<model if known, else null>",
  "note": "<one sentence: what this session worked on / where it left off>",
  "marker": "<hex>"
}
```

3. Confirm with the file path only. Fill only verifiable fields; null otherwise; never invent IDs. Do not attempt to read `~/.codex/sessions` (outside workspace scope) — the join happens at ingest time.

Note: the command that writes this file is recorded in your own rollout transcript under `~/.codex/sessions/`; WorkTrail joins the trail entry to the exact session by finding the filename/marker there (cwd + time window as fallback).
