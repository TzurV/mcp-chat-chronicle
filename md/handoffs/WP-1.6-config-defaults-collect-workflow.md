# WP-1.6 Handoff: Config Defaults + Collect Workflow

## Objective

Make routine use one-command and predictable:

```powershell
poetry run chronicle init
poetry run chronicle collect
```

WP-1.6 adds YAML defaults, explicit local directory setup, default DB configuration, configured source inventory, and a one-line loader that ingests all configured local histories plus all supported exports.

This is an orchestration layer over accepted importers/extractors. Do not add new provider parsers in this work package.

## Preferred Sequencing

Run after WP-1.5 `scan-local` is accepted, or coordinate carefully with the WP-1.5 executor if both are in flight.

WP-1.6 should reuse or align with the same source definitions used by `scan-local`.

## Source Of Truth

Read before implementation:

- `md/master-plan.md`
- `md/development-ledger.md`
- `md/agent-operating-notes.md`
- `md/handoffs/WP-1.5-scan-local-source-inventory.md`
- `md/handoffs/WP-1.4.1-directory-ingest-sweep.md`
- `README.md`
- `src/chat_chronicle/cli.py`
- `src/chat_chronicle/db.py`
- current adapter modules under `src/chat_chronicle/adapters/`
- existing CLI ingest/stats/scan tests

If WP-1.5 is already complete when this starts, also read:

- `md/handoffs/reports/WP-1.5-completion-report.md`
- `md/handoffs/reports/WP-1.5-validation-review.md`, if present

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

## Required User-Facing Behavior

### `chronicle init`

Implement an explicit setup command:

```powershell
poetry run chronicle init
```

It should create, if missing:

```text
.chronicle/
.chronicle/config.yaml
.chronicle/chronicle.db
exports/
exports/openai/
exports/claude/
```

Rules:

- Package install must not create folders or files.
- `chronicle init` is the explicit mutation point.
- Existing config files must not be overwritten unless an explicit `--force` option is provided.
- Existing DB files must not be deleted or recreated.
- DB schema should be initialized if the DB does not exist.
- Print a concise summary of created/existing paths.

Optional flags if small and useful:

```powershell
poetry run chronicle init --config .\.chronicle\config.yaml
poetry run chronicle init --force
```

### YAML Defaults

Add a YAML config file for project/user defaults.

Recommended generated path:

```text
.chronicle/config.yaml
```

Recommended tracked template:

```text
chronicle.default.yaml
```

The tracked template must not contain private absolute paths. The generated local config may resolve to local Windows paths.

Recommended schema:

```yaml
version: 1

paths:
  db: .chronicle/chronicle.db
  exports_root: exports

engines:
  chatgpt:
    enabled: true
    interested: true
  claude:
    enabled: true
    interested: true
  openai_codex:
    enabled: true
    interested: true
  claude_code:
    enabled: true
    interested: true
  cursor:
    enabled: false
    interested: true
  copilot_vscode:
    enabled: false
    interested: false

sources:
  chatgpt:
    provider: chatgpt
    kind: official_export
    path: exports/openai
  claude:
    provider: claude
    kind: official_export
    path: exports/claude
  openai_codex:
    provider: openai_codex
    kind: local_store
    path: ${USERPROFILE}/.codex
  claude_code:
    provider: claude_code
    kind: local_store
    path: ${USERPROFILE}/.claude/projects
```

Schema names may be adjusted if the codebase has a cleaner local convention, but the concepts must remain:

- default DB path;
- exports root;
- per-engine enabled/interested flags;
- provider/kind/path source entries;
- support for environment variables such as `${USERPROFILE}`;
- support for relative paths resolved from the project root/current working directory.

### DB Path Precedence

Use this precedence:

1. CLI `--db-path`
2. `CHAT_CHRONICLE_DB`
3. config YAML `paths.db`
4. built-in default `.chronicle/chronicle.db`

Existing commands that accept `--db-path` must keep working.

### `chronicle collect`

Replace the current stub with a working collection command:

```powershell
poetry run chronicle collect
```

Behavior:

- read `.chronicle/config.yaml` by default;
- accept `--config <path>` if small and useful;
- ingest enabled configured sources;
- for official export folders, ingest all supported sources under the configured path using the accepted directory-sweep behavior;
- for local-store sources, ingest the configured local store as one source;
- missing configured paths should be reported and skipped, not fatal;
- unsupported/experimental enabled sources should be reported and skipped unless a provider is implemented;
- aggregate output should show per-source provider/path/status and total seen/added/updated/skipped/errors;
- rerunning unchanged sources must add zero conversations and must not duplicate rows.

Recommended default configured sources:

- `chatgpt` from `exports/openai`
- `claude` from `exports/claude`
- `openai_codex` from `%USERPROFILE%\.codex`
- `claude_code` from `%USERPROFILE%\.claude\projects`

### `scan-local` Integration

If WP-1.5 has landed, update `chronicle scan-local` so it can read config defaults when present.

Expected behavior:

- still works without a config file;
- uses config paths/engine interest where present;
- stays read-only;
- missing configured paths are visible in output.

Do not let scan-local create config files or directories.

## Dependency Guidance

YAML is not in the Python standard library.

Preferred approach:

- add `PyYAML` as a runtime dependency if no YAML parser already exists;
- load with `yaml.safe_load`;
- validate into small Pydantic or dataclass models;
- keep errors clear and actionable.

Do not hand-roll a fragile YAML parser.

## Future Download Helper Backlog

The plan now includes a future history-download helper for providers that support documented exports or safe automation.

WP-1.6 must not implement download automation.

It should only make room for future UX by recording engine interest in the YAML and by printing helpful missing-source notes such as:

```text
chatgpt exports/openai missing; export/download history into this folder
```

## Out Of Scope

Do not implement:

- history download automation;
- browser automation;
- provider authentication;
- source CRUD commands such as `source add/list/disable`;
- new provider extractors/importers;
- Cursor/Copilot parsing;
- Task Scheduler registration automation;
- rename from `chronicle` to `worktrail`;
- UI beyond CLI.

Task Scheduler docs are in scope; actually creating scheduled tasks is not.

## Tests Required

Add focused tests for:

- `chronicle init` creates `.chronicle/`, config, DB, and export folders;
- `chronicle init` does not overwrite an existing config by default;
- config YAML loads successfully and resolves relative paths/env vars;
- invalid config produces a clear nonzero CLI error;
- DB path precedence: `--db-path` beats env/config/default;
- `chronicle collect` ingests enabled official export folders and local-store sources from synthetic fixtures;
- `chronicle collect` skips missing configured paths with notes and exit zero when at least one source is collected or when all missing sources are optional;
- `chronicle collect` rerun is idempotent;
- `chronicle collect` output includes per-source and aggregate counts;
- `scan-local` remains read-only and, if WP-1.5 has landed, honors config paths;
- no private export, DB, ZIP, or JSONL data is tracked.

Use temp directories and synthetic fixtures only.

## Required Validation Evidence

Include exact command output for:

```powershell
poetry env info --path
poetry run pytest tests/test_cli_config_collect.py -q
poetry run pytest
poetry run ruff check .
poetry run chronicle init --help
poetry run chronicle collect --help
poetry run chronicle --help
```

If tests live in another file, state that clearly and run that file explicitly.

Also include privacy-safe manual smoke using a temp project folder/config:

```powershell
poetry run chronicle init
poetry run chronicle collect
poetry run chronicle collect
poetry run chronicle stats
```

Report only:

- created/existing path summary;
- providers collected;
- first-run totals;
- second-run idempotency totals;
- no transcript text.

## Documentation Requirements

Update `README.md` with:

- how to run `chronicle init`;
- where config lives;
- default DB/export folders;
- how to run `chronicle collect`;
- how `--db-path`/env/config/default precedence works;
- note that cloud chats still require manual export/download until the future download-helper backlog item is scheduled.

Add or update planning docs only if implementation reveals a material scope change.

## Completion Report Requirements

Write:

```text
md/handoffs/reports/WP-1.6-completion-report.md
```

The report must include:

- status: `ready for PM validation`, `partial`, or `blocked`;
- files changed;
- config schema summary;
- init behavior summary;
- collect behavior summary;
- DB path precedence evidence;
- validation command results;
- privacy-safe manual smoke evidence;
- git status summary confirming no private DB/export/JSONL/ZIP artifacts are tracked;
- known limitations and follow-ups.

## Acceptance Criteria

WP-1.6 is complete when:

- `chronicle init` explicitly creates the local config/DB/export folder structure without package-install side effects;
- YAML config stores DB/export/source/engine-interest defaults;
- `chronicle collect` ingests enabled configured sources using accepted adapters/ingest behavior;
- missing optional paths are reported clearly and do not crash routine collection;
- reruns are idempotent;
- DB path precedence is implemented and tested;
- README documents the workflow;
- tests and Ruff pass;
- completion report is written at the required path;
- no private transcript, DB, export ZIP, JSONL, or generated dump is committed.
