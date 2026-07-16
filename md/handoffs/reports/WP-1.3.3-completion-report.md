# WP-1.3.3 Completion Report

## Status

ready for PM validation

## Files Changed

- `src/chat_chronicle/adapters/claude_export.py` - parses Claude `projects/*.json`, returns project metadata, and emits reliable project hints only for exact project UUID references.
- `src/chat_chronicle/cli.py` - persists parsed project rows and assigns `conversations.project_id` through existing `project_hints`.
- `src/chat_chronicle/db.py` - includes linked project names in FTS metadata during rebuild.
- `src/chat_chronicle/search.py` - includes linked project names in fallback snippets and phrase search.
- `tests/test_claude_export.py` - adds synthetic project metadata, linking, unlinked, and ZIP coverage.
- `tests/test_cli_ingest_stats.py` - adds end-to-end Claude project ingest, persistence, idempotency, and search tests.
- `tests/test_search.py` - adds direct search coverage for linked project names.
- `tests/fixtures/claude/project_linked/` - synthetic linked Claude project export fixture.
- `tests/fixtures/claude/project_unlinked/` - synthetic unlinked Claude project export fixture.

## Implementation Summary

Claude official export ingestion now reads project metadata from `projects/*.json` in ZIP exports, export directories, and sibling `projects/` directories for direct `conversations.json` paths. Valid project records require `uuid` and `name`; malformed/missing project fields become serializable parse errors without blocking valid conversations.

Conversation linking is conservative: a Claude conversation is linked only when a conversation-level `project_uuid`, `project_id`, `projectId`, `projectUUID`, or `project` object/string contains an exact UUID that matches a parsed project record. Project name matches are not used as links.

The CLI persists parsed project rows through the existing `projects` table and assigns `conversations.project_id` through the existing `project_hints` hook. Reingest remains idempotent: unchanged conversation content is skipped while metadata is still refreshed.

Search indexes linked project names as metadata, not fake transcript text. Broad FTS and phrase search both find conversations by linked project name; fallback snippets can show the project name when that is the matching metadata.

## Real Export Structure Findings

Privacy-safe inspection of:

```text
exports\claude\data-7ddb5876-919f-4a35-b090-f405cbbe3260-1783680081-e3a8326b-batch-0000.zip
```

Observed structure:

```text
entry_count=33
top=conversations.json count=1
top=memories.json count=1
top=projects count=30
top=users.json count=1
project_json_count=30
conversation_count=13
conversation_keys=account,chat_messages,created_at,name,summary,updated_at,uuid
conversation_project_key_names=(none)
message_keys=attachments,content,created_at,files,parent_message_uuid,sender,text,updated_at,uuid
project_keys=created_at,creator,description,docs,is_private,is_starter_project,name,prompt_template,updated_at,uuid
all_conversation_project_like_keys=(none)
attachment_keys=extracted_content,file_name,file_size,file_type
file_keys=file_name,file_uuid
```

## Project-Linking Decision

Synthetic exports with exact conversation-to-project UUID references are linked and searchable.

The owner real export has project metadata, including a private project row, but no project-like key anywhere in conversation/message/attachment/file key sets. Therefore reliable project-to-conversation linking is impossible for that export from the available data. The importer does not guess by project name, timestamps, docs, or transcript content.

## Search Behavior

- Linked synthetic project names are indexed in FTS metadata and phrase search.
- Snippets are generated from existing metadata/transcript corpus; no hidden project metadata is inserted as a synthetic message.
- A real-export search for the private project returns no conversations because no real conversations have a reliable project UUID link.

## Validation Commands

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

```text
poetry run pytest tests/test_claude_export.py -q
.......................................                                  [100%]
```

```text
poetry run pytest
........................................................................ [ 39%]
........................................................................ [ 79%]
.....................................                                    [100%]
181 passed in 21.67s
```

```text
poetry run ruff check .
All checks passed!
```

```text
poetry run chronicle --help

 Usage: chronicle [OPTIONS] COMMAND [ARGS]...

 A local-first, searchable archive of your AI conversations.

+- Options -------------------------------------------------------------------+
| --version          Show the version and exit.                               |
| --help             Show this message and exit.                              |
+-----------------------------------------------------------------------------+
+- Commands ------------------------------------------------------------------+
| ingest         Ingest one supported source, or sweep a parent directory for |
|                sources.                                                     |
| ingest-folder  Sweep a drop folder for export archives and ingest each one. |
| collect        Run every enabled source through its adapter.                |
| scan-local     Report, read-only, which AI-tool data stores exist on this   |
|                machine.                                                     |
| stats          Show per-source counts and the most recent ingest runs.      |
| recent         List the most recently active conversations.                 |
| search         Search the archive with FTS5 ranking and snippets.           |
| open           Open a result: deep link for web chats, transcript view      |
|                otherwise.                                                   |
+-----------------------------------------------------------------------------+
```

## Real-Export Smoke

```text
poetry run chronicle ingest .\exports\claude\data-7ddb5876-919f-4a35-b090-f405cbbe3260-1783680081-e3a8326b-batch-0000.zip --provider claude --db-path C:\tmp\wp133_claude_project_smoke.db
provider: claude
db path: C:\tmp\wp133_claude_project_smoke.db
conversations seen: 13
added: 13  updated: 0  skipped: 0
parse errors: 0
ingest run id: 1
```

```text
poetry run chronicle search "<PRIVATE_PROJECT_NAME>" --provider claude --db-path C:\tmp\wp133_claude_project_smoke.db
db path: C:\tmp\wp133_claude_project_smoke.db
No results
```

Sanitized temp-DB counts:

```text
project_rows=30
linked_claude_conversations=0
car_gui_project_rows=1
search_match_rows=0
```

## Git Status Summary

```text
 M src/chat_chronicle/adapters/claude_export.py
 M src/chat_chronicle/cli.py
 M src/chat_chronicle/db.py
 M src/chat_chronicle/search.py
 M tests/test_claude_export.py
 M tests/test_cli_ingest_stats.py
 M tests/test_search.py
?? md/handoffs/reports/WP-1.3.3-completion-report.md
?? tests/fixtures/claude/project_linked/
?? tests/fixtures/claude/project_unlinked/
```

No real export, DB, ZIP, private transcript, or generated metadata dump is tracked. The real smoke DB was written to `C:\tmp\wp133_claude_project_smoke.db`, outside the repo.

## Known Limitations And Follow-Ups

- Real Claude exports may include standalone project metadata without any reliable conversation reference. This implementation stores those project rows but does not make project-name search return conversations unless `conversations.project_id` is linked.
- The existing `projects` table has no provider project UUID column, so Claude project UUIDs are used during ingest for linking but are not persisted. If future requirements need project UUID display or cross-export project identity, schedule a schema change instead of overloading `root_path`.
- If Anthropic later adds a different reliable project reference field, add that key with a synthetic fixture and real-export structural evidence.
