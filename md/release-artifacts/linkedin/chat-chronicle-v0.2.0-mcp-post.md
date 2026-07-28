# Chat Chronicle v0.2.0 MCP progress post

I work in several AI chats at the same time.

One for planning. Another for implementation. A third for reviewing a problem
from a different angle.

Then, a few days later, I remember that an important decision was made—but not
where it was made, which assistant I was using, or how to find the conversation
again.

That frustration is why I started building **Chat Chronicle**: a local-first,
searchable archive for conversation history from ChatGPT, Claude, Codex, and
Claude Code.

It is still a work in progress. I keep developing it in practical increments
and publishing a new source release when the next piece becomes genuinely
useful.

The next release candidate, **v0.2.0**, adds read-only recall through MCP.
In plain English: while I am working in a supported Codex or Claude client, the
assistant can search my Chronicle archive, list recent topics, and retrieve a
bounded extract from a conversation I choose.

For example (all projects and IDs below are fictional):

- “Where did I discuss the Project Lighthouse migration? Include dates and
  supporting conversation IDs.”
- “Find the conversation where I fixed a Windows terminal-wrapping test. Show
  likely matches before retrieving any transcript.”
- “Retrieve conversation 123 with a 2,000-character limit and summarize the
  decision, blocker, and next action.”

Chronicle exposes only three MCP tools: search, recent topics, and bounded
conversation retrieval. The server is read-only. It cannot modify the archive,
capture the current chat, or magically know which conversation I am currently
in.

There is also an important privacy boundary: the database and MCP server remain
local, but any selected result sent to a cloud-backed client becomes part of
that model provider's request. More relevant evidence can produce a better
grounded answer, but it is a deliberate context-versus-privacy choice—not a
background upload of the archive.

Next, I am continuing the local-AI work: optional cached summaries, work-mode
classification, recent activity and blocker detection, and title assessment.
That work remains separate from normal search and is not automatic.

This project is evolving release by release. If you use multiple AI tools and
have also lost track of where useful work happened, I would be interested in
hearing how you handle it—and in feedback from anyone testing Chronicle with
Codex or Claude.

Repository: https://github.com/tzurv/mcp-chat-chronicle

v0.2.0 release: [OWNER: replace with the verified GitHub release URL after publication]

## Required publication-time edits

After the GitHub release exists and before the owner publishes this post:

1. Replace “The next release candidate, **v0.2.0**” with published-release
   wording such as “The latest release, **v0.2.0**”.
2. Replace both release URL placeholders with the verified public GitHub
   release URL.

## Optional first comment

Source and setup:

- Repository: https://github.com/tzurv/mcp-chat-chronicle
- v0.2.0 release: [OWNER: replace after publication]
- MCP setup guide:
  https://github.com/tzurv/mcp-chat-chronicle/blob/main/docs/mcp-client-setup.md
