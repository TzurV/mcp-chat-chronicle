# WP-1.6 Completion Report: Config Defaults + Collect Workflow

## Status

`ready for PM validation` (rework applied after WP-1.6 validation review)

WP-1.6 is implemented as an orchestration layer over accepted adapters. No new
provider parsers were added. `chronicle init` and `chronicle collect` work
end-to-end with YAML config, DB-path precedence, missing-path tolerance, and
idempotent reruns.

### Rework applied (addresses `WP-1.6-validation-review.md`)

Both rework items from the PM validation review are resolved:

1. **DB path precedence is now coherent across all commands.** The preferred
   fix was applied (not the narrower doc-only fix): a shared CLI helper
   `_resolve_effective_db_path()` loads `.chronicle/config.yaml` when present
   and applies the WP-1.6 precedence, and it is now used by every command that
   opens the DB — `ingest`, `collect`, `stats`, `search`, `recent`, `open`.
   `--db-path` and `CHAT_CHRONICLE_DB` behavior is preserved. Implementation,
   README, template, and tests now agree.
2. **Task Scheduler documentation added to README.** A short, clearly optional
   Windows Task Scheduler (`schtasks`) section documents recurring
   `chronicle collect`. Nothing is created or registered automatically.

### Note on WP-1.5 sequencing

WP-1.5 (`scan-local`) had **not** landed when this work started (`scan.py` was
still a placeholder and the `scan-local` command was still a stub). Per the
handoff, the `scan-local` config integration is therefore treated as
not-applicable for this work package: `scan-local` remains an untouched
read-only stub. The config module was deliberately designed so WP-1.5 can reuse
its source definitions later (`ChronicleConfig`, `SourceConfig`, `resolve_path`).

## Files Changed

| File | Change |
| --- | --- |
| `pyproject.toml` | Added `pyyaml (>=6.0,<7.0)` runtime dependency. |
| `poetry.lock` | Locked PyYAML (already resolvable in env). |
| `src/chat_chronicle/config.py` | **New.** Pydantic config models, `load_config` (via `yaml.safe_load`), env-var/`~`/relative path resolution, DB-path precedence, default config, YAML dump. |
| `chronicle.default.yaml` | **New, tracked template.** Documents the schema; no private absolute paths (`${USERPROFILE}` only). |
| `src/chat_chronicle/collect.py` | Implemented collection orchestration: iterate enabled sources, resolve paths, delegate to injected ingest hooks, aggregate a report. Missing/unsupported sources are reported, not fatal. |
| `src/chat_chronicle/cli.py` | Implemented `chronicle init` and `chronicle collect`. **Rework:** added shared `_resolve_effective_db_path()` and applied config-aware DB precedence to `ingest`, `stats`, `search`, `recent`, `open` (and `collect`); updated `--db-path` help text; updated `ingest-folder` stub to point at `ingest`/`collect`. |
| `tests/test_cli_config_collect.py` | **New.** 31 focused tests (init, config loading, precedence, collect, and — after rework — read commands honoring config `paths.db` with CLI/env overrides and invalid-config handling). |
| `tests/test_cli.py` | Updated stub test: `scan-local` still stub; `ingest-folder` now "superseded"; `collect` covered by the new suite. |
| `README.md` | Documented init/collect workflow, config location/schema, DB-path precedence, cloud-export note, and (**rework**) an optional Windows Task Scheduler section for recurring `collect`. |

## Config Schema Summary

`version: 1`. Validated into `ChronicleConfig` (Pydantic, `extra="forbid"`):

- `paths.db` — default database path (default `.chronicle/chronicle.db`);
- `paths.exports_root` — exports root (default `exports`);
- `engines.<name>.enabled` / `.interested` — per-engine flags. `enabled` gates
  whether `collect` ingests that source; `interested` records intent for the
  future download helper and does not affect parsing;
- `sources.<name>` — `provider`, `kind` (`official_export` | `local_store`),
  `path`.

Path values support `${VAR}`/`$VAR` env vars (`${USERPROFILE}`, `$HOME`), `~`
home expansion, and relative paths resolved from the project root / CWD.
Malformed YAML or schema violations raise `ConfigError`, surfaced by the CLI as
a clear nonzero error.

The generated `.chronicle/config.yaml` matches `chronicle.default.yaml` exactly
(the template is generated from `default_config()`), so the two stay in sync.

## Init Behavior Summary

`chronicle init`:

- creates `.chronicle/`, `.chronicle/config.yaml`, `.chronicle/chronicle.db`,
  `exports/`, `exports/openai/`, `exports/claude/` if missing;
- initializes DB schema **only when the DB file does not already exist**; an
  existing DB is kept (rows preserved), never recreated;
- never overwrites an existing `config.yaml` unless `--force` is passed;
- accepts `--config <path>` to target a non-default config location;
- prints a concise created/existing summary;
- has **no package-install side effects** — folder/file creation happens only
  when `init` runs.

## Collect Behavior Summary

`chronicle collect`:

- reads `.chronicle/config.yaml` by default (or `--config <path>`); errors
  clearly (nonzero) if no config is found;
- ingests only sources whose engine is `enabled`, ordered by name;
- for `official_export` folders, sweeps the configured path for all supported
  child sources (reusing the accepted directory-sweep discovery);
- for `local_store` sources, ingests the configured store as one source;
- reports and **skips** missing paths (`missing`), empty export folders
  (`empty`), and unsupported providers/kinds (`unsupported`) — none are fatal;
- rebuilds FTS once if at least one source was collected;
- prints a per-source table (provider / kind / path / status / seen / added /
  updated / skipped / errors / note) plus aggregate totals;
- reruns are idempotent — unchanged conversations are skipped, no duplicate
  rows.

Per-source hard adapter failures are captured as an `error` status with a note;
they do not crash the whole run.

## DB Path Precedence Evidence

Precedence implemented in `config.resolve_db_path` and the shared CLI helper
`_resolve_effective_db_path`, now applied to **every command that opens the DB**
(`ingest`, `collect`, `stats`, `search`, `recent`, `open`):

1. CLI `--db-path`
2. `CHAT_CHRONICLE_DB`
3. config YAML `paths.db` (from `.chronicle/config.yaml` when present)
4. built-in default `.chronicle/chronicle.db`

Unit-level test evidence (`tests/test_cli_config_collect.py`):

- `test_db_path_precedence_cli_beats_env_and_config` — CLI wins over env+config;
- `test_db_path_precedence_env_beats_config` — env wins over config;
- `test_db_path_precedence_config_used_when_no_cli_or_env` — config used
  otherwise;
- `test_resolve_effective_db_path_uses_config_paths_db` — helper resolves the
  config `paths.db` relative to the project directory;
- `test_resolve_effective_db_path_falls_back_to_default_without_config` — helper
  returns `None` (built-in default) when no config/CLI/env is present.

Read-command end-to-end evidence (rework):

- `test_stats_uses_config_db_when_no_cli_or_env` — `stats` reads config DB;
- `test_search_uses_config_db_when_no_cli_or_env` — `search` reads config DB;
- `test_recent_uses_config_db_when_no_cli_or_env` — `recent` reads config DB;
- `test_read_command_db_path_option_overrides_config` — `--db-path` overrides;
- `test_read_command_env_overrides_config` — `CHAT_CHRONICLE_DB` overrides;
- `test_read_command_invalid_config_surfaces_error` — a malformed config makes a
  read command fail clearly instead of silently using the default;
- `test_collect_db_path_option_overrides_config` — `--db-path` writes to the
  override DB and the config DB is not created.

Read commands still work with no config file present (helper returns `None` →
built-in default applies).

## Validation Command Results

```text
poetry env info --path
c:\work\Github\mcp-chat-chronicle\.venv

poetry run pytest tests/test_cli_config_collect.py -q
............................... (31 passed)

poetry run pytest
213 passed in ~22s

poetry run ruff check .
All checks passed!

poetry run chronicle init --help
Usage: chronicle init [OPTIONS]
  --config PATH   Config file path to create. Defaults to .chronicle/config.yaml.
  --force         Overwrite an existing config file.

poetry run chronicle collect --help
Usage: chronicle collect [OPTIONS]
  --config PATH    Config file path. Defaults to .chronicle/config.yaml.
  --db-path PATH   SQLite database path. Overrides env/config/default.

poetry run chronicle --help
Commands: ingest, ingest-folder, init, collect, scan-local, stats, recent,
          search, open
```

## Privacy-Safe Manual Smoke Evidence

Run in a throwaway temp project directory. The config's local-store sources were
pointed at empty temp folders (not the real `%USERPROFILE%`), and only one
synthetic ChatGPT fixture export was seeded. No transcript text is reproduced.

**Created/existing path summary (`chronicle init`):** created 6, existing 0 —
`.chronicle/`, `.chronicle/config.yaml`, `.chronicle/chronicle.db`
(schema initialized), `exports/`, `exports/openai/`, `exports/claude/`.

**Providers collected (first run):**

| source | provider | kind | status |
| --- | --- | --- | --- |
| chatgpt | chatgpt | official_export | collected |
| claude | claude | official_export | empty (folder present, no export) |
| openai_codex | openai_codex | local_store | missing |
| claude_code | claude_code | local_store | missing |

**First-run totals:** sources collected: 1; total conversations seen: 1;
total added: 1, updated: 0, skipped: 0; total parse errors: 0.

**Second-run idempotency totals:** sources collected: 1; total conversations
seen: 1; total added: 0, updated: 0, skipped: 1.

**`chronicle stats --db-path` (temp DB):** total conversations: 1; total
messages: 2; provider `chatgpt`: 1.

**Read-command config-DB smoke (rework).** In a fresh temp project, after
`init` + `collect` of one synthetic ChatGPT export, with **no** `--db-path` and
**no** `CHAT_CHRONICLE_DB`:

- `chronicle stats` → `db path: ...\tmp...\.chronicle\chronicle.db` (the
  config `paths.db`, resolved into the temp project, not the repo default);
  total conversations: 1, total messages: 2;
- `chronicle search docker` → rendered `Search results` (non-empty), reading the
  same config DB;
- `chronicle stats --db-path fresh.db` → total conversations: 0, confirming the
  CLI `--db-path` override still wins over config.

All smoke temp directories were deleted afterward; the repository's git-ignored
`.chronicle/chronicle.db` was not modified by the test or smoke runs.

## Git Status Summary

No private data tracked. Working-tree additions/modifications are source, tests,
docs, config template, lockfile, and this report only:

```text
 M README.md
 M poetry.lock
 M pyproject.toml
 M src/chat_chronicle/cli.py
 M src/chat_chronicle/collect.py
 M tests/test_cli.py
?? chronicle.default.yaml
?? src/chat_chronicle/config.py
?? tests/test_cli_config_collect.py
?? md/handoffs/reports/WP-1.6-completion-report.md
?? md/handoffs/reports/WP-1.6-validation-review.md
```

(`md/master-plan.md` and `md/development-ledger.md` carried pre-existing
PM-authored edits from before this task; they were not modified by this work.)

Confirmed:

- `chronicle.default.yaml` is **tracked** and contains **no** private absolute
  paths (`${USERPROFILE}` only);
- no `.db`, `.sqlite`, export ZIP, JSONL, or generated dump is tracked;
- generated `.chronicle/config.yaml` and any temp DBs stay git-ignored;
- all smoke temp directories were deleted after use.

## Known Limitations and Follow-Ups

- **`scan-local` not integrated with config.** WP-1.5 has not landed; the
  `scan-local` command remains a read-only stub. When WP-1.5 is implemented it
  should reuse `config.py`'s `ChronicleConfig` / `SourceConfig` / `resolve_path`
  so its inventory honors config paths and engine interest.
- **History download automation** remains out of scope; engine `interested`
  flags and missing-source notes only make room for that future backlog item.
- **Task Scheduler registration remains out of scope.** The README now
  documents an optional `schtasks` one-liner, but Chat Chronicle never creates
  or registers a scheduled task itself.

Both blocking rework items from `WP-1.6-validation-review.md` (config-aware DB
precedence for all commands; Task Scheduler docs) are resolved above.
