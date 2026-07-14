# Composer-tier instructions — ChatGPT, Windows Copilot, Claude web/desktop chat

These engines cannot write files. They compose the record; you save it with `trail-save.ps1` (copy JSON → run script). Add the relevant text as a custom instruction / saved memory in each engine, or keep it as a paste-able prompt.

## ChatGPT (Settings → Personalization → Custom instructions)

> When I say "Add to trail log", respond with ONLY a JSON code block, no commentary:
> `{"trail_version": 1, "logged_at": "<current ISO datetime with timezone>", "engine": "chatgpt", "app": "<web or desktop app>", "session_id": null, "conversation_url": "<PASTE_URL>", "title": "<short topic of this conversation>", "workspace": null, "model": "<your model name>", "note": "<one-sentence summary of what we worked on>", "marker": null}`
> Never invent IDs — use null for anything you cannot verify. After the block, remind me in one line to replace PASTE_URL with the address-bar URL.

**User steps:** copy block → run `trail-save.ps1` (it prompts for the URL). ⚠️ Use the `/c/...` address-bar URL from the **web** version — NOT a Share link (share IDs don't match export conversation IDs). Desktop app hides the URL; reopen the chat in the browser once if needed.

## Windows Copilot (tell it once to remember, or save as a paste-able prompt)

> When I say "Add to trail log", respond with ONLY a JSON code block, no commentary:
> `{"trail_version": 1, "logged_at": "<current ISO datetime with timezone>", "engine": "copilot", "app": "Windows Copilot", "session_id": null, "conversation_url": null, "title": "<short topic of this conversation>", "workspace": null, "model": null, "note": "<one-sentence summary of what we worked on>", "marker": null}`
> Fill only fields you truly know; use null otherwise; never invent IDs. Do not include my location or personal preferences.

**User steps:** copy block → run `trail-save.ps1`. Copilot has no usable URL or export ID — trail entries are its only good metadata, so log Copilot sessions generously.

## Claude web / Claude desktop chat (Settings → Profile personalization, or paste-able)

> When I say "Add to trail log", respond with ONLY a JSON code block, no commentary:
> `{"trail_version": 1, "logged_at": "<current ISO datetime with timezone>", "engine": "claude_web", "app": "<claude.ai web or desktop chat>", "session_id": null, "conversation_url": "<PASTE_URL>", "title": "<short topic of this conversation>", "workspace": null, "model": "<your model name>", "note": "<one-sentence summary of what we worked on>", "marker": null}`
> Never invent IDs — null for anything unverifiable. Remind me in one line to replace PASTE_URL with the address-bar URL.

**User steps:** copy block → run `trail-save.ps1`. The `/chat/<uuid>` in the address bar matches the `uuid` field in Claude's official export — a clean merge key.
