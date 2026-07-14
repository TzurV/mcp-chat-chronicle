# Snippet for CLAUDE.md (Claude Code) — add to repo-root CLAUDE.md or ~/.claude/CLAUDE.md

## Trail log

When the user says "Add to trail log" (or "/trail"):

1. Identify this session forensically: find the newest `.jsonl` under `~/.claude/projects/<encoded-cwd>/` whose mtime matches current activity; read `sessionId` from any record and the `ai-title` record's title if present. If ambiguous (concurrent sessions), set `session_id` to null and note the ambiguity — never guess.
2. Generate a 4-char random hex `<hex>`.
3. Write `.worktrail/trail/<UTC yyyyMMdd-HHmmss>-claude_code-<hex>.json` in the workspace root (create the directory; ensure `.worktrail/` is in `.gitignore`):

```json
{
  "trail_version": 1,
  "logged_at": "<ISO datetime with timezone>",
  "engine": "claude_code",
  "app": "Claude Code <version from transcript>",
  "session_id": "<sessionId or null>",
  "session_hint": { "transcript_path": "<path>", "git_branch": "<branch>" },
  "conversation_url": null,
  "title": "<ai-title if found, else null>",
  "workspace": "<cwd>",
  "model": "<model if known, else null>",
  "note": "<one sentence: what this session worked on / where it left off>",
  "marker": "<hex>"
}
```

4. Confirm with the file path only. Fill only verifiable fields; null otherwise; never invent IDs.

Note: the shell command that writes this file is recorded in this session's own transcript — that write-echo guarantees the trail entry can be joined to the correct session at ingest even if step 1 was ambiguous.
