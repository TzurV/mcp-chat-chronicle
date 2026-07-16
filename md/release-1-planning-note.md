# First Release Planning Note

## Status

**Released.** Chat Chronicle v0.1.0 was committed as `1f3fbce`, tagged `v0.1.0`,
pushed to `origin/main`, and published through the public GitHub repository and
release page. Release preparation and owner privacy review are complete.

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

## Owner Discussion And Approval Gate

The detailed release plan, exact working context, deliverables, and order of
activities must be discussed with the owner before execution. Discussion, analysis,
or agreement with a general direction does not authorize the next activity.

For every material stage, the release manager must:

1. present the proposed scope, inputs, outputs, sequence, privacy implications, and
   acceptance criteria;
2. resolve owner questions or requested changes;
3. wait for an explicit owner request and approval to proceed;
4. perform only the approved stage;
5. report results and wait for approval before starting the next stage.

Do not infer authorization from this planning note, earlier project approvals, the
existence of a handoff, or silence. Do not automatically edit the README, create or
publish manager-chat artifacts, draft public posts, rename/package the project,
commit, tag, push, or publish a release without the applicable explicit request and
approval.

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

### Release Artifact Availability

The first release includes the cleaned, human-readable manager transcript at
`md/release-artifacts/manager-chat/chat-chronicle-manager.md`.

### Procedure For Adding Approved Manager-Chat Records

This procedure covers both parts of the manager record: the ChatGPT manager thread
and any OpenAI Codex sessions used to implement or validate its work. It does not
authorize publication. Complete each privacy and owner-approval gate before moving
to the next step.

1. Refresh the private, git-ignored archive from the configured ChatGPT export and
   local Codex store:

   ```powershell
   poetry run chronicle collect --config .\.chronicle\config.yaml
   poetry run chronicle stats --db-path .\.chronicle\chronicle.db
   ```

   A fresh ChatGPT data export must first be placed under the configured
   `exports/openai` source. Codex sessions are collected from the configured local
   store, normally `${USERPROFILE}/.codex`. The export, local JSONL records, and
   `.chronicle/chronicle.db` remain private and git-ignored.

2. Locate the records by stable content and provider rather than documenting a
   private UUID or absolute path. Start with recent activity, then use several
   distinctive phrases from the manager thread and its executor handoffs:

   ```powershell
   poetry run chronicle recent -n 30 --db-path .\.chronicle\chronicle.db
   poetry run chronicle search --phrase "<distinctive manager phrase>" --provider chatgpt --db-path .\.chronicle\chronicle.db
   poetry run chronicle search --phrase "<distinctive implementation phrase>" --provider openai_codex --db-path .\.chronicle\chronicle.db
   poetry run chronicle open <result-id> --db-path .\.chronicle\chronicle.db
   ```

   Record the selected result IDs only in private release-working notes. Confirm
   that the dates and content cover the intended development period and that no
   related executor session has been omitted.

3. Create a working copy outside the repository. Preserve the selected records
   verbatim in that private staging area so redactions are reviewable, but never use
   `git add -f` to bypass the repository's export, database, ZIP, `.chronicle`, or
   local-session ignores.

4. Produce the owner-approved form: full transcript, excerpts, chronology, or case
   study. Remove or replace names, usernames, absolute paths, conversation and
   account IDs, URLs, credentials, private project details, real chat titles and
   snippets, and private AI prompts/results unless the owner explicitly approves a
   specific item. Treat text quoted from executor sessions as private source
   material too. Mark omissions and paraphrases honestly; do not present derived
   prose as a verbatim transcript.

5. Put only the reviewed publication artifact in a dedicated tracked location such
   as `md/release-artifacts/manager-chat-case-study.md`. Include a short provenance
   note stating the source types, covered date range, artifact form, and that private
   identifiers and content were redacted. Do not include the private archive,
   staging copy, raw ChatGPT export, Codex JSONL, or lookup IDs.

6. Before staging, inspect the complete artifact and repository diff, scan for the
   agreed sensitive patterns, and confirm that ignored private files remain
   untracked:

   ```powershell
   git diff -- md/release-artifacts/manager-chat-case-study.md
   git status --short --ignored
   git ls-files "*.db" "*.sqlite" "*.zip" ".chronicle/*" "exports/*"
   ```

   Add a targeted secret/path/identifier scan based on the private values found
   during review. Do not paste those values into a tracked scan script or report.

7. Present the final artifact and privacy-check result to the owner. Only after
   explicit approval may the reviewed artifact be staged and committed. Publication
   or attachment to a release requires a separate explicit approval.

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

## Release Decisions

- release: Chat Chronicle v0.1.0;
- repository/package/CLI remain `mcp-chat-chronicle`, `chat-chronicle`, and
  `chronicle` for this release;
- WorkTrail / `worktrail-ai`, PyPI/pipx, and short CLI aliases are deferred;
- publication target: the existing GitHub repository, installed from source with
  Poetry and Python 3.11+;
- core archive/search has no AI dependency; the `enrich` extra and local AI guide
  are advanced, explicitly invoked work-in-progress functionality;
- public content includes the release-quality README, LinkedIn article, and the
  owner-reviewed sanitized Markdown manager transcript;
- raw exports, databases, local JSONL sessions, private configuration, and raw chat
  transcripts remain excluded;
- release gate: full tests, Ruff, pre-commit, package build, CLI version/help,
  privacy scan, staged diff review, and tag verification must pass.

## Immediate Next Action

The v0.1.0 source-release workstream is complete. The owner controls publication of
the prepared LinkedIn article and any future promotion. Product development resumes
only after the owner selects and explicitly approves the next workstream; WP-5.1.2
and WP-5.2 remain paused.
