# WP-1.4.1 Completion Report

## Status

ready for PM validation

## Summary

Implemented directory sweep mode for `chronicle ingest <directory>` when the directory is not itself a recognized single source. The sweep discovers supported child sources, sorts them by resolved absolute path, avoids duplicate source paths, skips unsupported/cache/private DB paths, filters incompatible sources in explicit-provider mode, records one ingest run per discovered source, and prints aggregate totals.

Single-source directory behavior is preserved: a valid ChatGPT/Claude export directory, OpenAI Codex home/session directory, or Claude Code project/source directory still ingests as one source before sweep mode is considered.

## Changed Files

- `src/chat_chronicle/cli.py`: added directory discovery, aggregate ingest execution/output, source-level failure handling, and non-raising provider candidate detection.
- `tests/test_cli_ingest_stats.py`: added synthetic directory-sweep tests for mixed providers, ordering, unsupported files, no-source failure, explicit-provider filtering, idempotency, and stats coherence.
- `md/handoffs/reports/WP-1.4.1-completion-report.md`: this report.

Note: `md/development-ledger.md` was already modified before this implementation and was not edited by this work. `md/handoffs/WP-1.4.1-directory-ingest-sweep.md` was already untracked before this implementation.

## Directory Detection And Sweep Behavior

- `chronicle ingest <directory> --provider auto` first checks whether the directory itself is a single supported source.
- If not, it scans child paths deterministically and accepts supported ChatGPT, Claude, OpenAI Codex, and Claude Code sources.
- Accepted directories are not descended into, so child files are not double-ingested.
- Explicit provider mode only accepts discovered sources compatible with that provider and summarizes incompatible skips.
- Unsupported files, generated DB files, cache/tooling folders, `.git`, `.venv`, and unrelated hidden folders are ignored with summary counts.
- Per-source ingest still uses existing adapters, `get_or_create_source()`, `begin_ingest_run()`, `upsert_conversation()`, `finish_ingest_run()`, and DB uniqueness.

## Idempotency Evidence

Privacy-safe smoke used copied synthetic fixtures under `C:\tmp\wp141-smoke-20260714-001`.

First run:

```text
discovered supported sources: 3
total conversations seen: 3
total added: 3  updated: 0  skipped: 0
ingest run ids: 1, 2, 3
```

Second run:

```text
discovered supported sources: 3
total conversations seen: 3
total added: 0  updated: 0  skipped: 3
ingest run ids: 4, 5, 6
```

Stats after the second run:

```text
total conversations: 3
total messages: 6
providers: chatgpt=1, claude=1, openai_codex=1
recent ingest runs: 6 total, second-run runs skipped one conversation each
```

## Validation Command Results

```powershell
poetry env info --path
```

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

```powershell
poetry run pytest tests/test_cli_ingest_stats.py -q
```

```text
.......................                                                  [100%]
```

```powershell
poetry run pytest
```

```text
........................................................................ [ 41%]
........................................................................ [ 82%]
..............................                                           [100%]
174 passed in 16.85s
```

```powershell
poetry run ruff check .
```

```text
All checks passed!
```

```powershell
poetry run chronicle --help
```

```text
Usage: chronicle [OPTIONS] COMMAND [ARGS]...
Commands: ingest, ingest-folder, collect, scan-local, stats, recent, search, open
```

```powershell
poetry run chronicle ingest --help
```

```text
Usage: chronicle ingest [OPTIONS] PATH
Ingest one supported source, or sweep a parent directory for sources.
Options: --provider TEXT, --db-path PATH, --help
```

## Manual Smoke Evidence

Setup used only copied synthetic fixtures:

- `tests/fixtures/chatgpt/minimal/conversations.json`
- `tests/fixtures/claude/minimal/conversations.json`
- `tests/fixtures/openai_codex/minimal/rollout-minimal.jsonl`

The setup command first hit the known Windows sandbox launcher issue (`CreateProcessAsUserW failed: 1312`) and was retried with escalation for temp fixture setup only.

```powershell
poetry run chronicle ingest C:\tmp\wp141-smoke-20260714-001\exports --provider auto --db-path C:\tmp\wp141-smoke-20260714-001\chronicle.db
```

```text
db path: C:\tmp\wp141-smoke-20260714-001\chronicle.db
parent source directory: C:\tmp\wp141-smoke-20260714-001\exports
discovered supported sources: 3
source: chatgpt C:\tmp\wp141-smoke-20260714-001\exports\a-chatgpt
source: claude C:\tmp\wp141-smoke-20260714-001\exports\b-claude
source: openai_codex C:\tmp\wp141-smoke-20260714-001\exports\c-codex\rollout-minimal.jsonl
ignored unsupported paths: 0
total conversations seen: 3
total added: 3  updated: 0  skipped: 0
total parse errors: 0
ingest run ids: 1, 2, 3
```

Second run:

```text
total conversations seen: 3
total added: 0  updated: 0  skipped: 3
total parse errors: 0
ingest run ids: 4, 5, 6
```

Stats:

```powershell
poetry run chronicle stats --db-path C:\tmp\wp141-smoke-20260714-001\chronicle.db
```

```text
db path: C:\tmp\wp141-smoke-20260714-001\chronicle.db
total conversations: 3
total messages: 6
Counts by provider: chatgpt 1, claude 1, openai_codex 1
Recent ingest runs include runs 1-6 with run 4-6 showing Added 0 and Skipped 1 each.
```

## Test Coverage Added

- `test_directory_sweep_auto_ingests_multiple_supported_child_sources`
- `test_directory_sweep_preserves_single_source_directory_behavior`
- `test_directory_sweep_orders_discovered_sources_by_resolved_path`
- `test_directory_sweep_ignores_unsupported_files_when_supported_sources_exist`
- `test_directory_sweep_no_supported_sources_exits_nonzero`
- `test_directory_sweep_explicit_provider_ingests_only_compatible_sources`
- `test_directory_sweep_rerun_is_idempotent_without_duplicate_rows`
- `test_stats_remains_coherent_after_directory_sweep`

## Git Status And Privacy

`git status --short` after implementation:

```text
 M md/development-ledger.md
 M src/chat_chronicle/cli.py
 M tests/test_cli_ingest_stats.py
?? md/handoffs/WP-1.4.1-directory-ingest-sweep.md
?? md/handoffs/reports/WP-1.4.1-completion-report.md
```

`git ls-files` shows no tracked `.db`, `.sqlite`, `.sqlite3`, `.zip`, private export, secret, auth, or generated dump artifacts. Tracked JSON/JSONL files are synthetic test fixtures under `tests/fixtures/`.

## Known Limitations And Follow-Ups

- A directory that is itself a valid export remains single-source by design, even if unrelated child files are present.
- Directory sweep uses existing concrete detection/adapters only; no new provider support was added.
- If all discovered sources fail fatally at ingest time, the command records failed ingest runs and exits non-zero. If at least one source succeeds, the command exits zero and reports failures.
