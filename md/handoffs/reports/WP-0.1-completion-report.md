# WP-0.1 Completion Report

## Status

**ready for PM validation**

## Summary

Created the Poetry-based Python scaffold for Chat Chronicle: `src/chat_chronicle/` package, a Typer + Rich CLI entrypoint named `chronicle` exposing all seven required subcommands as stubs, a pytest suite covering the CLI surface, ruff and pre-commit configuration, a GitHub Actions matrix over Windows/Ubuntu × Python 3.11/3.12, MIT license, and a `.gitignore` that blocks local databases and exports while leaving synthetic fixtures committable.

Scope was held to the scaffold. No schema, no importers, no search, no MCP, and — per design rule 2 — no `adapters/base.py`.

One environment issue surfaced and was resolved: Poetry was resolving the virtualenv to an unrelated project (`CopilotLocalMongoDB/.venv`) because that shell had `VIRTUAL_ENV` set, and it had silently installed dependencies there on the first attempt. Per instruction, `virtualenvs.in-project = true` was set (committed as `poetry.toml`), the stray cached env removed, and dependencies reinstalled. The venv is now `C:\work\Github\mcp-chat-chronicle\.venv` on Python 3.12.0.

## Changed Files

| File | Purpose |
| --- | --- |
| `pyproject.toml` | Poetry project: deps `pydantic^2`/`typer`/`rich`, dev group `pytest`/`ruff`/`pre-commit`, extras `enrich`/`mcp`, `chronicle` script, ruff + pytest config |
| `poetry.lock` | Pinned resolution; in sync with `pyproject.toml` (`poetry check --lock` → "All set!") |
| `poetry.toml` | Forces the virtualenv in-project at `.venv` |
| `README.md` | Positioning table, quickstart, CLI surface, stack + "not chosen" rationale, privacy, honest limitations |
| `LICENSE` | MIT |
| `.gitignore` | Ignores `*.db`, `exports/`, `*.zip`, `.env`, caches, `.venv/`; re-includes `tests/fixtures/**` |
| `.pre-commit-config.yaml` | pre-commit-hooks basics + `ruff` (autofix) and `ruff-format` |
| `.github/workflows/ci.yml` | CI: install → lint → test → `chronicle --help` smoke test |
| `src/chat_chronicle/__init__.py` | Package marker, `__version__ = "0.1.0"` |
| `src/chat_chronicle/cli.py` | Typer app; seven stub commands + `--version` |
| `src/chat_chronicle/models.py` | Placeholder for WP-1.1 Pydantic models |
| `src/chat_chronicle/db.py` | Placeholder for WP-1.1 SQLite layer |
| `src/chat_chronicle/collect.py` | Placeholder for WP-1.6 collector |
| `src/chat_chronicle/scan.py` | Placeholder for WP-1.5 discovery |
| `src/chat_chronicle/search.py` | Placeholder for WP-2.1 FTS5 search |
| `src/chat_chronicle/adapters/__init__.py` | Adapters package; notes that `base.py` arrives in WP-3.3 |
| `tests/test_cli.py` | Asserts help lists all seven commands, stubs exit 0, `--version` works, malformed arg fails |

All files are new; nothing pre-existing was modified.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| `poetry install` succeeds | pass | `Installing the current project: chat-chronicle (0.1.0)`, 28 packages installed into `C:\work\Github\mcp-chat-chronicle\.venv` |
| `poetry run pytest` passes | pass | `4 passed in 0.59s` |
| `poetry run chronicle --help` lists all required subcommands | pass | Help output below lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, `open` |
| CI exists for Python 3.11 and 3.12 on Windows and Ubuntu | pass | `.github/workflows/ci.yml`, matrix `os: [ubuntu-latest, windows-latest]` × `python-version: ["3.11", "3.12"]`, `fail-fast: false` — 4 jobs |
| Ruff configuration exists | pass | `[tool.ruff]` / `[tool.ruff.lint]` in `pyproject.toml` (line-length 100, target py311, rules `E,F,I,UP,B,W`). `ruff check .` → "All checks passed!" |
| Pre-commit configuration exists | pass | `.pre-commit-config.yaml` (pre-commit-hooks, `ruff --fix`, `ruff-format`) |
| MIT license exists | pass | `LICENSE`, plus `license = "MIT"` + `license-files` in `pyproject.toml`; `poetry check` → "All set!" |
| `.gitignore` excludes local/private artifacts | pass | Verified empirically, not just by reading — see below |
| No real chat/export data was committed | pass | `git status --untracked-files=all` lists only source/config/test files; a filesystem sweep for `*.db`, `*.zip`, `*.sqlite*`, `.env` outside `.venv` returned nothing |

### `.gitignore` verification (empirical)

Probe files were created and git asked directly, rather than trusting the pattern list:

```
TRACKABLE: tests/fixtures/synthetic_export.json
TRACKABLE: tests/fixtures/synthetic_export.zip
IGNORED  : local.db
IGNORED  : exports/real.json
```

Relevant rules: `*.db`, `*.db-wal`, `*.db-shm`, `*.sqlite`, `*.sqlite3`, `exports/`, `*.zip`, `.env`, `.env.*`, `*.pem`, `*.key`, `.venv/`, plus caches — with `!tests/fixtures/` and `!tests/fixtures/**` re-including synthetic fixtures. Note that a synthetic `.zip` fixture stays trackable despite the blanket `*.zip` rule. All probe files were removed afterwards; the tree is clean.

## Command Evidence

```
$ poetry install
Installing dependencies from lock file
Package operations: 28 installs, 0 updates, 0 removals
  - Installing pydantic (2.13.4)
  - Installing rich (14.3.4)
  - Installing typer (0.26.8)
  - Installing pytest (8.4.2)
  - Installing ruff (0.6.9)
  - Installing pre-commit (3.8.0)
  ... (28 total)
Installing the current project: chat-chronicle (0.1.0)

$ poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
$ poetry run python --version
Python 3.12.0
```

```
$ poetry run pytest
....                                                                     [100%]
4 passed in 0.59s
```

```
$ poetry run chronicle --help
 Usage: chronicle [OPTIONS] COMMAND [ARGS]...

 A local-first, searchable archive of your AI conversations.

+- Options -------------------------------------------------------------------+
| --version          Show the version and exit.                               |
| --help             Show this message and exit.                              |
+-----------------------------------------------------------------------------+
+- Commands ------------------------------------------------------------------+
| ingest         Ingest a single official export file.                        |
| ingest-folder  Sweep a drop folder for export archives and ingest each one. |
| collect        Run every enabled source through its adapter.                |
| scan-local     Report, read-only, which AI-tool data stores exist on this   |
|                machine.                                                     |
| stats          Show per-source counts and the most recent ingest runs.      |
| search         Search the archive with FTS5 ranking and snippets.           |
| open           Open a result: deep link for web chats, transcript view      |
|                otherwise.                                                   |
+-----------------------------------------------------------------------------+
```

Supplementary checks (the two extra steps CI runs):

```
$ poetry run ruff check .
All checks passed!

$ poetry run ruff format --check .
9 files already formatted

$ poetry check
All set!

$ poetry run chronicle scan-local
`chronicle scan-local` is not implemented yet (lands in WP-1.5).
exit=0

$ poetry run chronicle --version
chat-chronicle 0.1.0
```

## CI Workflow

**Path:** `.github/workflows/ci.yml` · **Triggers:** push to `main`, all pull requests.

**Matrix:** `{ubuntu-latest, windows-latest} × {3.11, 3.12}` = 4 jobs, `fail-fast: false` so one OS failing doesn't mask the other.

**Steps per job:** checkout → `setup-python` → `pipx install poetry` → `poetry install` → `poetry run ruff check .` → `poetry run pytest` → `poetry run chronicle --help`.

The `ruff-format` hook in pre-commit and `ruff check` in CI agree on the current tree, so a pre-commit run won't produce a diff that then fails CI.

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement DB schema | pass | `db.py` is a docstring-only placeholder; no SQL, no `sqlite3` import |
| Did not implement real importers | pass | `adapters/` contains only `__init__.py` |
| Did not implement search | pass | `search.py` is a placeholder; `search` command is a stub |
| Did not add adapter base/protocol | pass | `ls src/chat_chronicle/adapters/` → `__init__.py` only. No `base.py`, no `AdapterProtocol` (design rule 2 — deferred to WP-3.3) |
| Did not add real chat data or exports | pass | No fixtures at all yet; no `.db`/`.zip`/export files in the tree |

No AI dependencies were added outside the optional extras: `enrich = ["openai (>=1.30,<2.0)"]` and `mcp = ["fastmcp (>=2.0,<4.0)"]`. Neither is installed by a default `poetry install` — the 28 installed packages contain no `openai` or `fastmcp`.

## Risks Or Follow-Ups

1. **The `VIRTUAL_ENV` hazard is real and will recur.** Poetry 2.x honors an already-activated `VIRTUAL_ENV`, and on this machine a shell had one pointing at an unrelated project. The first `poetry install` therefore wrote dependencies into `CopilotLocalMongoDB/.venv`. `poetry.toml` with `in-project = true` was committed, which fixes fresh shells, but **it does not override an already-active `VIRTUAL_ENV`**. If a later worker sees dependencies "already installed" unexpectedly, run `poetry env info --path` first. Consider noting this in `CONTRIBUTING.md` at WP-3.3. Some packages may be lingering in that other project's venv from the first attempt; that project was not touched to clean them up — flagged rather than acted on outside this repo.

2. **`poetry.toml` is committed.** It's a repo-level preference rather than a personal one, and it makes CI and local behavior match. Easy to drop if it should stay untracked.

3. **Pinned tool versions will drift.** `ruff 0.6.9` is pinned in both `pyproject.toml` (`^0.6`) and `.pre-commit-config.yaml` (`v0.6.9`) so the two agree. These are two places to bump in step; a mismatch shows up as CI passing while pre-commit reformats. Similarly `fastmcp (>=2.0,<4.0)` is a deliberately wide range — the master plan says `fastmcp` 3.x, but 3.x could not be verified as current, so the range admits both. WP-4.1 should pin it precisely once the server is actually written.

4. **CI is untested.** Every CI step was verified locally on Windows/Python 3.12, but the workflow has never run on GitHub — Ubuntu and the 3.11 legs are unexercised, and nothing has been pushed. The first push is the real test. Nothing was committed or pushed, per instruction not to touch the plan or ledger; the 18 files are staged as untracked.

5. **Typer's `open` command shadows the builtin.** The function is named `open_result` with the command name set via `@app.command("open")`, so the CLI surface matches the plan without shadowing. Worth preserving when WP-2.1 fills it in.

6. **`search --limit` is not in the master plan's CLI sketch.** It was added alongside the plan's `--provider/--since/--until/--tag` because WP-2.1's acceptance criteria imply result-count control, and getting the signature right now avoids a rewrite later. Trivial to remove if considered out of scope.
