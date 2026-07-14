# WP-1.4.1 Handoff: Directory Ingest Sweep

## Objective

Add support for:

```powershell
poetry run chronicle ingest <directory> --provider auto --db-path .\.chronicle\chronicle.db
```

where `<directory>` is a folder containing multiple ingestible chat-history sources.

This is a focused follow-up to accepted WP-1.4. It extends the existing `chronicle ingest <path>` command so a user can point it at a folder of exports instead of running one ingest command per file.

## Source Of Truth

Read before implementation:

- `md/master-plan.md`
- `md/change-order-01.md`
- `md/development-ledger.md`
- `md/agent-operating-notes.md`
- `md/handoffs/WP-1.4-cli-ingest-stats.md`
- `md/handoffs/reports/WP-1.4-validation-review.md`
- `src/chat_chronicle/cli.py`
- `src/chat_chronicle/db.py`
- existing adapter modules under `src/chat_chronicle/adapters/`
- existing CLI ingest tests

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

## Current Behavior

Accepted behavior already supports ingesting one source at a time, for example:

```powershell
poetry run chronicle ingest .\exports\openai\export.zip --provider chatgpt --db-path .\.chronicle\chronicle.db
poetry run chronicle ingest .\exports\claude\export.zip --provider claude --db-path .\.chronicle\chronicle.db
poetry run chronicle ingest "$env:USERPROFILE\.codex" --provider openai_codex --db-path .\.chronicle\chronicle.db
poetry run chronicle ingest "$env:USERPROFILE\.claude\projects" --provider claude_code --db-path .\.chronicle\chronicle.db
```

Some directories are already valid single sources. Do not break this:

- OpenAI Codex local home/directory source;
- Claude Code projects directory;
- official export directories already accepted by provider adapters;
- direct directories containing a provider's expected export files.

## Required Behavior

### Directory Sweep Mode

When `chronicle ingest <directory>` receives a directory that is not itself a recognized single source, treat it as a parent folder and discover supported sources inside it.

Primary user scenario:

```powershell
poetry run chronicle ingest .\exports --provider auto --db-path .\.chronicle\chronicle.db
```

The command should discover supported child sources such as:

- ChatGPT/OpenAI official export ZIP files;
- OpenAI split-export directories or files containing `conversations-*.json`;
- Claude official export ZIP files;
- Claude official export directories/files supported by the existing adapter;
- OpenAI Codex local JSONL/session sources already supported by the existing adapter, where unambiguous;
- Claude Code project/session sources already supported by the existing adapter, where unambiguous.

Use existing provider adapters and detection logic. Do not create a new adapter abstraction.

### Preserve Single-Source Directory Behavior

Detection order matters:

1. First ask whether the supplied directory is itself a recognized source for the requested provider or for `--provider auto`.
2. If yes, ingest it exactly as today.
3. Only if the directory is not a recognized single source, enter directory sweep mode.

This prevents accidental duplicate ingestion of `.codex`, `.claude\projects`, or an already-valid export directory by walking every internal file separately.

### Discovery Rules

Implement deterministic discovery:

- sort discovered paths by resolved absolute path before ingesting;
- do not ingest the same resolved path twice;
- when a discovered directory is accepted as a source, do not also ingest child files from that accepted source;
- skip private DB files, generated SQLite files, `.git`, `.venv`, cache folders, and hidden/tooling folders that are not supported chat-history sources;
- report unsupported files as skipped/ignored summary counts, not noisy per-file errors.

Use conservative recursion. It is acceptable to scan recursively, but the executor must avoid descending into a directory after it has been selected as a supported source.

### Provider Handling

For `--provider auto`:

- allow mixed-source directories;
- detect the provider per discovered source;
- print/report each source with its detected provider.

For an explicit provider:

- ingest only sources compatible with that provider;
- skip incompatible discovered sources with a concise summary;
- preserve current explicit-provider behavior for a path that is itself one valid source.

### Idempotency And Source Reuse

Directory sweep must preserve accepted WP-1.4/CO-1 idempotency:

- rerunning the same directory ingest must not duplicate `sources`;
- rerunning the same directory ingest must not duplicate `conversations` or `messages`;
- source reuse must continue to use resolved provider/path identity and the DB-level unique index added by CO-1;
- per-source ingest runs should remain understandable in `chronicle stats`.

The implementation must not bypass existing upsert/source helper logic.

### Output

The CLI should print:

- DB path;
- parent source directory path;
- number of discovered supported sources;
- per-source provider/path summary;
- total conversations seen/added/updated/skipped;
- total parse errors;
- ingest run IDs or a clear summary of created ingest runs.

Keep output concise enough for a folder with many exports.

### Failure Semantics

Use these semantics unless there is a clear existing project pattern that conflicts:

- no supported sources found: exit non-zero with a clear message;
- at least one source ingested successfully: exit zero, even if unsupported files were skipped;
- source-level parser warnings: behave like existing ingest and record/report them;
- source-level fatal failures: continue remaining sources when possible, report failures, and exit non-zero only if no source ingested successfully.

## Out Of Scope

Do not implement these in WP-1.4.1:

- scheduling;
- daemon/watch mode;
- `collect` workflow;
- source add/list/disable management commands;
- GUI;
- new providers such as Gemini, Copilot, Cursor, or Cowork;
- renaming `chronicle` to `worktrail`;
- deep-link opening for local Codex chats.

## Tests Required

Add focused tests for:

- `chronicle ingest <directory> --provider auto` ingests multiple supported child sources;
- a mixed folder with at least two providers is handled correctly;
- a directory that is itself a recognized source still uses existing single-source behavior;
- deterministic ordering of discovered sources;
- unsupported files are ignored/skipped without failing the whole command when supported sources exist;
- no supported sources found exits non-zero with a clear message;
- explicit provider mode only ingests compatible sources;
- rerunning the same directory ingest produces no duplicate sources, conversations, or messages;
- `chronicle stats` remains coherent after a directory sweep.

Use synthetic fixtures only. Do not add private exports, private JSONL files, SQLite DBs, or ZIP archives to git.

## Required Validation Evidence

Include exact command output for:

```powershell
poetry env info --path
poetry run pytest tests/test_cli_ingest_stats.py -q
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
poetry run chronicle ingest --help
```

Also include a privacy-safe manual smoke using a temporary folder populated with copies of existing test fixtures or owner-approved export files:

```powershell
poetry run chronicle ingest <temp-parent-folder> --provider auto --db-path <temp-db>
poetry run chronicle ingest <temp-parent-folder> --provider auto --db-path <temp-db>
poetry run chronicle stats --db-path <temp-db>
```

Report only counts, providers, and whether the second run was idempotent. Do not include private transcript text.

## Completion Report Requirements

Write:

```text
md/handoffs/reports/WP-1.4.1-completion-report.md
```

The report must include:

- status: `ready for PM validation`, `partial`, or `blocked`;
- files changed;
- summary of directory detection and sweep behavior;
- explicit statement that single-source directory behavior was preserved;
- idempotency evidence from a second run;
- validation command results;
- privacy-safe manual smoke evidence;
- git status summary confirming no private DB/export/JSONL/ZIP artifacts are tracked;
- known limitations and follow-ups.

## Acceptance Criteria

WP-1.4.1 is complete when:

- `chronicle ingest <directory>` can ingest multiple supported child sources from one parent folder;
- recognized single-source directories still ingest as one source;
- mixed-provider directory ingest works with `--provider auto`;
- explicit-provider directory ingest only uses compatible sources;
- reruns are idempotent and do not duplicate DB rows;
- output clearly summarizes discovered sources and aggregate results;
- tests and Ruff pass;
- completion report is written at the required path;
- no private transcript, DB, export ZIP, JSONL, or generated dump is committed.
