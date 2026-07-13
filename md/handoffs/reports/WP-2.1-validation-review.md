# WP-2.1 Validation Review

## Decision
**Accepted.**

The completion report at `md/handoffs/reports/WP-2.1-completion-report.md` satisfies the WP-2.1 handoff. The implementation makes `chronicle search` and `chronicle open` functional over the accepted SQLite/FTS5 archive and consumes the CO-1 link-back fields for URL-backed web rows and local-store transcript rows.

## Validation Performed

| Check | Result | Evidence |
| --- | --- | --- |
| Poetry preflight uses repo-local venv | Pass | `poetry env info --path` -> `C:\work\Github\mcp-chat-chronicle\.venv` |
| Full test suite | Pass | `poetry run pytest` -> `123 passed in 13.27s` |
| Ruff lint | Pass | `poetry run ruff check .` -> `All checks passed!` |
| CLI help still lists required commands | Pass | `poetry run chronicle --help` lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, and `open` |
| Manual temp DB ingest | Pass | Ingested ChatGPT and OpenAI Codex synthetic fixtures into `C:\tmp\wp21-pm-validation-20260713.db` |
| Search with results | Pass | `chronicle search docker` returned result id `1`, provider `chatgpt`, title, snippet, and `chronicle open` hint |
| Search with no results | Pass | `chronicle search zzznomatch` printed `No results` and exited successfully |
| Web open | Pass | Browser-disabled `chronicle open 1` printed the ChatGPT URL and did not fail browser launch |
| Local open | Pass | `chronicle open 2` printed OpenAI Codex transcript plus `origin_path` |

One browser-disabled web-open smoke command hit the known Windows sandbox launcher error `CreateProcessAsUserW failed: 1312`; the successful rerun used sandbox escalation for validation only.

## Acceptance Criteria Review

| Acceptance Criterion | Result | Notes |
| --- | --- | --- |
| `chronicle search` functional | Pass | CLI and query-layer tests cover all three accepted providers. |
| `search --db-path` works | Pass | Tests and manual smoke use temp DB paths. |
| FTS5 `MATCH` + `bm25` ranking used | Pass | `src/chat_chronicle/search.py` uses `chat_fts MATCH ?` and `bm25(chat_fts)`. |
| Search output includes required fields | Pass | Rich table and stable `result ...` lines include id, date, provider, title, snippet, and open hint. |
| Provider/since/until/tag/limit filters work | Pass | Covered in direct and CLI tests. |
| Empty query and invalid limit fail clearly | Pass | Covered in direct and CLI tests. |
| No results and empty DB handled cleanly | Pass | Covered by tests and manual no-result smoke. |
| `chronicle open` functional | Pass | Web and local paths covered. |
| Web URL rows print and attempt browser launch | Pass | Browser helper is testable and monkeypatched in tests; manual validation used `CHAT_CHRONICLE_NO_BROWSER=1`. |
| Local rows print transcript and link-back fields | Pass | OpenAI Codex row prints transcript and `origin_path`; tests also cover synthetic `resume_hint`. |
| CO-1 link-back fields exercised in tests | Pass | URL, `origin_path`, and `resume_hint` are covered. |
| No out-of-scope behavior implemented | Pass | No new importers, collect/source-management/note, MCP, rename, or enrichment behavior added. |
| No adapter base/protocol added | Pass | No `adapters/base.py` or `AdapterProtocol` found. |
| Synthetic fixtures only | Pass | Tests and manual validation used `tests/fixtures`; temp DB stayed under `C:\tmp`. |

## Scope Notes

- SQLite `snippet()` is attempted, with a Python fallback for contentless FTS rows. Tests prove useful fallback snippets.
- The synthetic performance smoke covers 350 conversations. The master-plan p95 target on a larger real archive remains a prototype validation item.
- `md/research/` is present as an untracked, unrelated directory and was not reviewed or included in this validation.

## Next Step

WP-2.1 is accepted. The next handoff should be WP-3.1 Claude Code extractor, including the required research spike over Agent Sessions, claude-record, and codex-trace before local fixture work.
