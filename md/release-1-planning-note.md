# First Release Planning Note

## Status

Recorded for a future dedicated release thread. Do not execute release preparation
from the main development-manager thread.

## Owner Direction

The current accepted product version should be prepared as the first release before
continuing WP-5.1.2 evaluation work.

The release workstream must include:

1. release-readiness review of the current accepted implementation;
2. a release-quality README describing installation, setup, supported sources,
   current CLI capabilities, optional local AI support, privacy boundaries, and
   honest limitations;
3. a LinkedIn post and/or long-form article describing what the first release
   includes and the engineering path that produced it;
4. inclusion of **this current main development-manager chat** as part of the first
   release story or release artifacts;
5. release validation, versioning, packaging, and publication decisions to be
   defined in the dedicated release thread.

## Thread Boundary

All release planning, handoffs, execution reports, README release editing, and
LinkedIn/article drafting must happen in a separate task/thread. This thread remains
the main project development and PM-validation record.

The release thread should begin by reading:

- `md/master-plan.md`;
- `md/development-ledger.md`;
- this note;
- accepted handoffs, completion reports, and validation reviews relevant to the
  first-release scope;
- `md/agent-operating-notes.md` before any Poetry validation.

## Manager Chat Inclusion: Decision Required

The owner explicitly requires this manager chat to be represented in the first
release. The exact form is intentionally unresolved until the release discussion.
Candidates include:

- a privacy-reviewed full transcript;
- a redacted transcript or selected excerpts;
- a generated project chronology derived from the chat;
- a case study explaining manager/executor handoffs and validation loops;
- a private bundled example referenced publicly only through aggregate evidence.

Do not commit or publish the raw chat automatically. Before inclusion, the release
thread must decide:

1. whether the artifact is public or private;
2. full transcript versus excerpts versus derived case study;
3. redaction rules for names, paths, conversation IDs, URLs, credentials, private
   project details, and generated AI results;
4. whether executor-chat material quoted inside this manager chat is included;
5. artifact location and format;
6. explicit owner approval of the final publication-ready artifact.

The latest manager-chat content should be collected into the private archive before
the release artifact is generated so the release does not use a stale partial
transcript. Do not identify the chat through a hard-coded local UUID or private path
in tracked documentation.

## First-Release Scope Boundary

The release should describe accepted behavior only. It may include:

- real-history ingestion support for ChatGPT, Claude, OpenAI Codex, and Claude Code;
- normalized local SQLite storage and idempotent collection;
- source discovery, stats, recent chats, broad/phrase search, and open/link-back;
- YAML configuration and one-line collection;
- optional YAML-defined AI tasks through LiteLLM and LM Studio;
- the four accepted conversation-intelligence task contracts;
- privacy-safe evidence that local Qwen3.5-4B execution works;
- the manager/executor development and validation process.

Do not claim that WP-5.1.2 teacher references, semantic-quality evaluation, model
benchmarks, Gemini import, MCP recall, embeddings, hybrid search, or v2 features are
complete.

## Paused Work

WP-5.1.2 is on owner-directed hold. Preserve its current handoff as planning history,
but do not execute its snapshot, teacher, reconciliation, or benchmark workflow until
the owner resumes that work after the first-release activity.

## Release Decisions Deferred To The Dedicated Thread

- release name and semantic version;
- whether the planned WorkTrail / `worktrail-ai` rename occurs before this release;
- public repository and package publication targets;
- supported Python and Windows versions stated publicly;
- install commands and optional dependency tiers;
- release notes and changelog format;
- screenshot/GIF/architecture-diagram needs;
- LinkedIn post versus article scope and publication order;
- exact manager-chat artifact and redaction policy;
- final release acceptance checklist and rollback criteria.

## Immediate Next Action

Open a separate release task/thread and provide this note as its initial planning
context. Do not create the release implementation handoff in this main thread until
the owner has discussed the deferred decisions in that release thread.
