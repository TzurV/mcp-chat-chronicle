# WP-1.3.3 Handoff: Claude Export Project Metadata Linking

## Objective

Extend the accepted Claude official-export importer so Claude export project metadata can be ingested, linked to conversations when the export provides a reliable relationship, and used by search.

This follow-up was triggered by the owner finding a Claude export project metadata file:

```json
{"uuid": "11111111-1111-4111-8111-111111111111", "name": "Synthetic Project Alpha", ...}
```

The current archive has provider `claude` ingested successfully, but:

```powershell
poetry run chronicle search "Synthetic Project Alpha" --provider claude --db-path .\.chronicle\chronicle.db
```

returns no results. That is expected with current scope because the importer indexes Claude conversations/messages, not standalone project metadata.

## Source Of Truth

Read before implementation:

- `md/master-plan.md`
- `md/development-ledger.md`
- `md/agent-operating-notes.md`
- `md/handoffs/WP-1.3-claude-export-importer.md`
- `md/handoffs/reports/WP-1.3-validation-review.md`
- `src/chat_chronicle/adapters/claude_export.py`
- `src/chat_chronicle/db.py`
- `src/chat_chronicle/search.py`
- `src/chat_chronicle/cli.py`
- `tests/test_claude_export.py`
- `tests/test_search.py`
- `tests/test_cli_search_open.py`

## Required Poetry Preflight

Before running Poetry commands:

```powershell
poetry env info --path
```

Expected:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If it points elsewhere, stop and fix the shell according to `md/agent-operating-notes.md`.

## Scope

Implement:

- privacy-safe inspection of the real Claude export structure to determine how `projects/*.json` relates to conversations;
- parsing of Claude export project metadata from ZIPs/directories;
- storage/reuse of project rows in the existing `projects` table;
- linking `conversations.project_id` for Claude conversations when the export provides a reliable project UUID/reference;
- search support so linked project names can make conversations discoverable;
- synthetic fixtures and tests only;
- completion report at:

```text
md/handoffs/reports/WP-1.3.3-completion-report.md
```

Do not implement:

- a broad project-management UI;
- schema redesign unless the existing `projects` table is demonstrably insufficient;
- ingestion of private real project descriptions into committed fixtures/docs;
- Claude Code project changes;
- trail adapter, scan-local, collect scheduling, or source CRUD;
- semantic search or enrichment.

## Real Export Inspection Rules

Inspect the owner Claude ZIP only for structural facts:

```text
exports\claude\data-7ddb5876-919f-4a35-b090-f405cbbe3260-1783680081-e3a8326b-batch-0000.zip
```

Allowed to report:

- file names/path patterns;
- counts;
- object key names;
- presence or absence of project UUID references in conversations;
- whether project linking is reliable, partial, or impossible from export data.

Do not print or commit:

- real chat text;
- real project descriptions beyond the already provided project name if avoidable;
- real private metadata values except counts/key names.

## Functional Requirements

Project parsing:

- Find Claude export project metadata files, likely under a `projects/` path in the ZIP/directory.
- Parse project UUID and name at minimum.
- Treat missing/invalid project objects as serializable parse errors, not importer crashes.
- Use the existing `projects` table where possible.

Conversation linking:

- Determine whether Claude conversation records include a project UUID/reference.
- If yes, link conversations to the corresponding project row.
- If no reliable link exists, do not guess. Store/import project rows if useful, but document that conversations cannot be linked.

Search:

- If conversations are linked to projects, searching the project name should return the linked conversations.
- Use last-activity/date sorting behavior consistent with existing search.
- Keep snippets useful without exposing hidden metadata as fake message text.
- If search indexing project names requires FTS rebuild changes, update the relevant DB/search tests.

CLI behavior:

- Existing `chronicle ingest ... --provider claude` should handle projects as part of the same source ingest.
- Existing `chronicle stats` should remain stable.
- Existing `chronicle search` should be able to find linked project names.
- Existing `chronicle open` may show project name if naturally available, but this is optional unless the implementation already has a clean path.

## Tests Required

Add synthetic fixtures/tests for:

- Claude export with `projects/*.json` metadata;
- conversation record linked to a project UUID;
- project row is created/reused in `projects`;
- conversation `project_id` is populated when a link is present;
- search by project name returns linked conversation(s);
- re-ingest is idempotent;
- project metadata with missing/invalid fields records serializable errors without blocking valid conversations;
- Claude export without project links still ingests cleanly and does not guess links;
- existing Claude importer tests still pass.

## Required Validation Evidence

Include exact command output for:

```powershell
poetry env info --path
poetry run pytest tests/test_claude_export.py -q
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
```

Also include a privacy-safe real-export smoke:

```powershell
poetry run chronicle ingest .\exports\claude\data-7ddb5876-919f-4a35-b090-f405cbbe3260-1783680081-e3a8326b-batch-0000.zip --provider claude --db-path <tmp-db>
poetry run chronicle search "Synthetic Project Alpha" --provider claude --db-path <tmp-db>
```

Report only:

- project metadata count;
- conversations seen/added/updated/skipped/errors;
- whether a reliable project-to-conversation link exists;
- whether the synthetic project name returns results after the change;
- no private transcript text.

## Completion Report Requirements

Write:

```text
md/handoffs/reports/WP-1.3.3-completion-report.md
```

The report must include:

- status: `ready for PM validation`, `partial`, or `blocked`;
- files changed;
- implementation summary;
- real export structure findings, privacy-safe only;
- project-linking decision and evidence;
- search/indexing behavior;
- validation commands;
- real-export smoke counts only;
- git status summary confirming no real export, DB, ZIP, private transcript, or generated metadata dump is tracked;
- known limitations and recommended follow-ups.

Do not mark ready if project names are parsed but cannot be linked and the report does not clearly explain that limitation.

## Acceptance Criteria

WP-1.3.3 is complete when:

- Claude export project metadata is parsed from synthetic fixtures;
- existing Claude conversation import remains compatible;
- project rows are persisted/reused;
- conversations are linked to projects when the export provides reliable references;
- search by linked project name works in synthetic tests;
- real-export smoke determines whether a private project can be found through reliable links;
- full tests and Ruff pass;
- no private Claude export data is committed.
