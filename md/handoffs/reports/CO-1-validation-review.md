# CO-1 Validation Review

## Decision
**Accepted.**

The completion report at `md/handoffs/reports/CO-1-completion-report.md` satisfies the CO-1 handoff. The implementation adds schema version 2, migrates v1 databases forward, persists link-back metadata, accepts `manual_entry` sources, and preserves the accepted WP-1.4 CLI ingest/stats behavior.

## Validation Performed

| Check | Result | Evidence |
| --- | --- | --- |
| Poetry preflight uses repo-local venv | Pass | `poetry env info --path` -> `C:\work\Github\mcp-chat-chronicle\.venv` |
| Full test suite | Pass | `poetry run pytest` -> `109 passed in 14.88s` |
| Ruff lint | Pass | `poetry run ruff check .` -> `All checks passed!` |
| CLI help still lists required commands | Pass | `poetry run chronicle --help` lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, and `open` |
| Manual ChatGPT ingest | Pass | Ingested `tests\fixtures\chatgpt\minimal\conversations.json` into `C:\tmp\co1-pm-validation-efa2c8c.db` |
| Manual Claude ingest | Pass | Ingested `tests\fixtures\claude\minimal\conversations.json` into the same temp DB |
| Manual OpenAI Codex ingest | Pass | Ingested `tests\fixtures\openai_codex\minimal\rollout-minimal.jsonl` into the same temp DB |
| Manual stats | Pass | `chronicle stats` reported 3 conversations, 6 messages, and one row for each provider |
| Schema probe | Pass | Temp DB reports `PRAGMA user_version = 2`; `conversations` includes `project_id`, `origin_path`, and `resume_hint` |

Two read-only schema probe attempts hit the known Windows sandbox launcher error `CreateProcessAsUserW failed: 1312`; the successful rerun used sandbox escalation for validation only.

## Acceptance Criteria Review

| Acceptance Criterion | Result | Notes |
| --- | --- | --- |
| `CURRENT_SCHEMA_VERSION` is 2 | Pass | `src/chat_chronicle/db.py` sets version 2. |
| Fresh DBs create v2 schema | Pass | Covered by `test_fresh_database_creates_v2_schema`. |
| v1 DBs migrate forward without data loss | Pass | Covered by `test_v1_database_migrates_to_v2_and_preserves_rows`. |
| `projects` table exists | Pass | Fresh and migration tests cover the table. |
| New conversation link-back columns exist and persist | Pass | Tests cover persistence and metadata refresh on skipped content. |
| `manual_entry` source type accepted | Pass | Fresh and migrated schema tests insert `manual_entry`. |
| DB-level source uniqueness enforced | Pass | Partial unique index exists and duplicate non-null paths raise `IntegrityError`. |
| Duplicate source cleanup handled | Pass | Migration test repoints `conversations.source_id` and `ingest_runs.source_id` to the kept source row. |
| ChatGPT and Claude titles/URLs verified | Pass | Existing parser tests and full suite remain green. |
| OpenAI Codex `origin_path` handled | Pass | `test_parse_minimal_session_returns_one_conversation` asserts resolved `origin_path`; `resume_hint` remains `None` pending verified local behavior. |
| `chronicle ingest` remains functional | Pass | Manual commands and CLI tests cover ChatGPT, Claude, and OpenAI Codex. |
| `chronicle stats` remains functional | Pass | Manual command and tests pass. |
| No out-of-scope commands implemented | Pass | Search/open/note/source-management remain out of scope. |
| No adapter base/protocol added | Pass | No `adapters/base.py` or `AdapterProtocol` introduced. |
| Synthetic fixtures only | Pass | Validation used `tests/fixtures`; temp DB stayed under `C:\tmp`. |

## Scope Notes

- `chronicle open` behavior is intentionally not implemented here. WP-2.1 will consume `url`, `origin_path`, and `resume_hint`.
- OpenAI Codex `resume_hint` is intentionally unset because local Codex resume behavior has not been verified in this repo. This is acceptable for CO-1 because `origin_path` supplies the local link-back field.
- The source uniqueness concern from WP-1.4 is resolved at the DB level with a partial unique index for non-null `path_or_config`.

## Next Step

CO-1 is accepted. The next handoff should be WP-2.1 FTS5 search + open.
