# Your scattered AI chats, one local search

I knew I had worked on it.

I remembered the topic. I remembered roughly when it happened. I even remembered some of the reasoning.

But I could not remember where it was.

Was it in ChatGPT? Claude? Codex? Claude Code? Was it part of a coding session, a planning conversation, or a quick side discussion?

That has become a real problem in my daily work.

AI chats are no longer just casual conversations. For me, they now contain design decisions, debugging history, implementation notes, review comments, rejected options, prompts, experiments, and context that I may need again later.

In other words, AI conversations have become part of the engineering record.

The problem is that this record is scattered.

Each tool has its own history. Each platform has its own search. Some conversations live in web products. Some live in local coding-agent stores. Some can be exported. Some are easier to access than others. And none of them naturally give me a simple cross-tool answer to one basic question:

**Where did I work on this?**

## Last week, I asked the community

Last week, I asked the community how people are solving this.

The response was overwhelming.

People shared local logging scripts, Obsidian workflows, session recorders, scheduled summaries, CLI wrappers, browser-based ledgers, agent orchestration tools, database-backed memory layers, and more.

Some of the ideas were excellent.

But I still did not find a simple solution that fit my own use case.

I was not looking for a full AI memory platform. I was not trying to build another agent framework. I did not want to send my whole archive to a hosted model just to find my own work.

I wanted something much simpler:

A local, searchable work trail across the AI tools I actually use.

## The problem I wanted to solve

The first requirement was very low level.

I wanted to answer questions like:

- I worked on this last week — which chat was it?
- Which tool did I use for that discussion?
- Was it ChatGPT, Claude, Codex, or Claude Code?
- Can I search across all of them from one place?
- Can I get back to the original conversation when a link exists?

That last point matters. Search alone is not enough. I wanted retrieval with provenance: find the conversation locally, then trace back to the original session or transcript.

I also wanted the basic workflow to stay local.

That meant:

- no hosted database required
- no mandatory AI model dependency for basic search
- no browser extension as a first requirement
- no background daemon just to make the first version useful
- no silent upload of private transcripts

The goal was not to build something impressive.

The goal was to build something I would actually use every day.

## So I started building

After a week, I have a working first version.

The project is called **Chat Chronicle**.

It collects supported AI conversation histories into a normalized local archive, then makes them searchable.

At the moment, it supports four sources:

- ChatGPT official exports
- Claude official exports
- OpenAI Codex local sessions
- Claude Code local sessions

Two of those sources are already resident locally if you use the tools: Codex and Claude Code. ChatGPT and Claude web still require official exports in this first version.

The README is intentionally written as the practical cheat sheet: install, locate supported sources, ingest, search, and open results. The article is not meant to replace that. The article is about the problem, the design choices, and the development story.

The core loop is simple:

```powershell
poetry run chronicle collect
poetry run chronicle search "docker network"
poetry run chronicle open <result-id>
```

In practice, the full first-use flow is:

1. install the project
2. initialize the local database and export folders
3. place ChatGPT / Claude exports in the expected folders, if using web history
4. let the tool read local Codex / Claude Code stores where available
5. collect
6. search
7. open the result or local transcript

That is the first useful loop:

**Install. Locate or export. Ingest. Search. Open.**

## What the tool stores

Chat Chronicle normalizes conversations, messages, source identity, timestamps, and link-back metadata into a local SQLite database with FTS5 search.

In plain language, the architecture looks like this:

```text
Official exports                 Local durable stores
ChatGPT / Claude                 Codex / Claude Code
        |                                |
        +---------- source adapters -----+
                         |
                normalized SQLite
                  + FTS5 index
                         |
       stats / recent / search / open / optional AI tasks
```

Each source has its own adapter because each source has a different shape.

ChatGPT and Claude web histories arrive through official exports. Codex and Claude Code have durable local session stores. Those are different inputs, but once imported, they become part of the same searchable archive.

The shared layer is deliberately boring:

- SQLite for storage
- FTS5 for search
- normalized tables for conversations and messages
- source metadata for traceability
- link-back information where available

That boring part is important.

For basic recall, the archive should work with ordinary search first. AI enrichment can come later.

## What already works

The current version is already helping me daily.

It can show recent activity across sources. It can search broadly. It can search for exact phrases. It can open a result.

For web-backed conversations, such as ChatGPT, it keeps the provider URL when available and attempts to open the original thread in the browser.

For local coding-agent sessions, where reliable deep links are not always available, it renders the locally archived transcript with source metadata.

That distinction matters.

Sometimes the best trace-back is a web URL. Sometimes it is a local transcript. The important thing is that the search result points somewhere durable enough to continue the work.

The collection process is also idempotent. Re-running collection updates changed conversations and skips unchanged ones instead of duplicating them. That makes it practical as a repeated workflow rather than a one-off import.

## Privacy and control

Privacy was not an afterthought.

The archive is local. The configuration, database, official exports, ZIP files, and real local-session data are git-ignored.

Normal archive commands do not call an AI model.

That was a deliberate design choice.

I do not want a transcript to be sent to a model just because I searched for a phrase. Search should be local and deterministic.

There is optional AI task scaffolding, but it is explicitly separate from the ordinary archive workflow. The current design allows local loopback profiles by default, while remote model use requires an explicit decision.

That distinction is important to me:

Finding my own work should be local.

Sending transcripts to a model should be intentional.

## The AI layer

The AI-powered layer is not the main claim yet.

The scaffolding is there. The project has optional conversation-intelligence tasks such as conversation summary, work-mode classification, last activity, and title assessment.

The integration path has been tested on short real conversations using a local LM Studio model setup.

But I am being careful not to overstate this part.

A successful local smoke test proves that the path works. It does not prove general summary quality. It does not turn the project into a fully evaluated AI memory system.

For now, the useful part is simpler:

**collect, search, open.**

The AI layer can improve the workflow later, but it is not the centre of this first release.

## How the project was built

There is another reason I wanted to share the repository early.

The tool itself was built using the same AI-assisted development workflow that created the need for it.

I use a working method I call the **Threaded Handoff Method (THM)**.

At a high level, that means separating the work into structured handoffs between planning, implementation, review, and validation. In practice, Claude, ChatGPT, and Codex helped me design, implement, review, and iterate through work packages, completion reports, validation checks, and follow-up fixes.

I also added the manager transcript / development trail, because the project is not only the code. It is also an example of how the code was developed using AI tools.

That makes the repository both the project and a record of how the project was built. I hope this added information helps improve AI-based code development practice.

## What is not finished

This is still a first version.

There are clear limitations.

ChatGPT and Claude web histories are only as fresh as the latest manual export. Coding-agent local formats are not guaranteed stable. Local coding-agent sessions do not always have reliable application deep links. Some sources I would like to support later, such as Gemini, Cursor, MCP-based recall, embeddings, and hybrid search, are not complete first-release features.

The AI enrichment layer is also not the core value yet. It is scaffolded, but the first useful thing is the archive and search workflow.

That is fine.

The point of this first release is not to solve everything.

The point is to solve the basic retrieval problem well enough that it becomes useful immediately.

## Why I am opening it now

I am opening the repository because the problem is real, and because the community responses showed that many people are building their own partial versions of this.

Some people are using Obsidian. Some are using session recorders. Some are using local databases. Some are using scheduled summaries. Some are moving work into one CLI or one self-hosted interface. Some are creating wrappers around coding agents.

All of those approaches make sense.

My version focuses on a narrower question:

**Can I build a local searchable work trail across the AI conversations I already use?**

After one week, the answer is: yes, enough to be useful.

It is not finished.

It is not perfect.

But it is already helping me find my own work again.

And that was the original goal.

## Appendix: Search cheat sheet

The full setup guide is in the README. It includes installation, supported sources, where to find local Codex and Claude Code histories, how to export ChatGPT and Claude web history, how to collect, and how to search/open results.

The short version is:

```powershell
poetry run chronicle recent -n 20
poetry run chronicle search "your remembered phrase"
poetry run chronicle search --phrase "exact sentence you remember"
poetry run chronicle search "release planning" --provider openai_codex
poetry run chronicle open <result-id>
```

For ChatGPT and Claude web conversations, `open` uses the stored provider URL when available.

For Codex and Claude Code, `open` renders the locally archived transcript.

The README is the place to keep this operational detail up to date as source formats and supported tools evolve.
