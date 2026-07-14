---
name: trail-log
description: Log the current chat session to the WorkTrail trail folder. Use when the user says "Add to trail log", "trail log", "/trail", or asks to record/log this session for their activity trail.
---

# Trail log — WorkTrail session breadcrumb

When invoked, write one JSON trail record for the current session. This works ahead of any WorkTrail code — records accumulate until the trail adapter ingests them.

## Steps

1. **Gather verifiable metadata from your environment only** (never invent, never ask the model side of you to "remember" an ID):
   - `session_id`: the `local_*` directory name visible in your outputs/uploads paths. This is a **runtime-instance** ID — the same chat may have used others before; if earlier ones are visible in the conversation, put them in `session_hint.earlier_runtime_ids`.
   - `workspace`: the user-selected folder path if one is mounted, else null.
   - `model`, `app` ("Claude desktop app — Cowork mode"), current ISO datetime with timezone.
   - `title`: null (not exposed to you).
2. **Compose the note**: one sentence — what this session worked on and where it left off. Ask the user only if you truly cannot summarize.
3. **Write the record** to `<workspace>\.worktrail\trail\<UTC yyyyMMdd-HHmmss>-cowork-<4-random-hex>.json` if a workspace is mounted (create the dir; ensure `.worktrail/` is gitignored), else to `C:\work\worktrail\trail\`.

```json
{
  "trail_version": 1,
  "logged_at": "<ISO datetime>",
  "engine": "cowork",
  "app": "Claude desktop app (Windows) — Cowork mode",
  "session_id": "<current local_* id>",
  "session_hint": { "earlier_runtime_ids": [], "account_profile_ids": ["<UUIDs from session paths>"] },
  "conversation_url": null,
  "title": null,
  "workspace": "<mounted folder or null>",
  "model": "<model id>",
  "note": "<one sentence>",
  "marker": "<the 4-hex from the filename>"
}
```

4. Confirm with the file path only — no restating the content.

## Rules

- Null-discipline: only environment-verified values; no guessed IDs, no location, no user preferences.
- If the trail directory can't be created, say so plainly and output the JSON in a code block instead so the user can save it via `trail-save.ps1`.
