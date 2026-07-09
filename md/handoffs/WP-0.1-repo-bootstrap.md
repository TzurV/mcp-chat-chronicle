# WP-0.1 Handoff: Repo Bootstrap

## Objective
Create the initial Python project scaffold for Chat Chronicle so later workers can build adapters, database ingestion, search, enrichment, and MCP recall on a stable foundation.

This work package implements the scaffold only. Stub commands are acceptable where the master plan allows them.

## Source Of Truth
Use `md/master-plan.md`, especially:

- Section 3: Tech Stack
- Section 4: Repository Layout
- Section 6: M0 / WP-0.1 Repo bootstrap

Do not substitute the chosen stack.

## Scope
Implement:

- Poetry-based Python package layout.
- `src/chat_chronicle/` package.
- Typer CLI entrypoint named `chronicle`.
- Stub CLI commands listed in the master plan.
- Basic pytest test suite.
- Ruff and pre-commit configuration.
- GitHub Actions CI for Windows and Ubuntu on Python 3.11 and 3.12.
- MIT license.
- `.gitignore` that excludes local databases and exports while allowing synthetic fixtures.

Do not implement database schema, real importers, search, enrichment, MCP server logic, or adapter abstractions in this WP.

## Required Tech Choices
Use exactly:

- Python 3.11+
- Poetry
- Pydantic v2
- Typer
- Rich
- pytest
- ruff
- pre-commit
- GitHub Actions on Windows + Ubuntu

Project extras required in `pyproject.toml`:

- `enrich = ["openai"]`
- `mcp = ["fastmcp"]`

## CLI Surface
`chronicle --help` must list these subcommands, even if implemented as stubs:

- `ingest`
- `ingest-folder`
- `collect`
- `scan-local`
- `stats`
- `search`
- `open`

Suggested behavior for stubs:

- Print a short Rich message that the command is not implemented yet.
- Exit successfully unless required arguments are malformed.
- Keep command signatures close to the master plan so later workers do not need to rewrite the CLI surface.

## Expected Layout
Create the scaffold aligned with the master plan:

```text
mcp-chat-chronicle/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── .pre-commit-config.yaml
├── .github/workflows/ci.yml
├── src/chat_chronicle/
│   ├── __init__.py
│   ├── cli.py
│   ├── models.py
│   ├── db.py
│   ├── collect.py
│   ├── scan.py
│   ├── search.py
│   └── adapters/
│       └── __init__.py
└── tests/
    └── test_cli.py
```

Important: do not create `src/chat_chronicle/adapters/base.py` yet. The master plan explicitly says adapter abstraction is introduced only in WP-3.3.

## Acceptance Criteria
WP-0.1 is complete only when all of these are true:

- `poetry install` succeeds.
- `poetry run pytest` passes.
- `poetry run chronicle --help` lists all required subcommands.
- CI exists for Python 3.11 and 3.12 on Windows and Ubuntu.
- Ruff configuration exists.
- Pre-commit configuration exists.
- MIT license exists.
- `.gitignore` excludes `*.db`, `exports/`, and other local/private artifacts without blocking committed synthetic fixtures.
- No real chat data, exports, local databases, or secrets are committed.

## Evidence Required
The executor must return a detailed completion report. Missing evidence means the WP is not accepted, even if the implementation appears correct.

The report must include:

- Changed-files summary.
- Exact command output or concise pasted result for:
  - `poetry install`
  - `poetry run pytest`
  - `poetry run chronicle --help`
- CI workflow path and matrix summary.
- Confirmation that no real chat/export data was added.
- Explicit checklist mapping each acceptance criterion to `pass`, `fail`, or `not attempted`.

## Technical Guardrails
- Keep implementation intentionally boring and minimal.
- Do not add unnecessary frameworks.
- Do not implement future work packages early.
- Do not add `AdapterProtocol` or adapter base classes.
- Do not introduce AI dependencies outside the optional Poetry extras.
- Avoid committing generated caches or local environment files.
- Use synthetic test data only.

## Completion Report Format
The executor must return the report in this structure:

```markdown
# WP-0.1 Completion Report

## Status
One of:

- ready for PM validation
- blocked

## Summary
Briefly describe what was implemented.

## Changed Files
List every changed or created file with a one-line purpose for each.

## Acceptance Criteria Checklist

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| `poetry install` succeeds | pass/fail/not attempted | Paste relevant output or explain blocker |
| `poetry run pytest` passes | pass/fail/not attempted | Paste test summary |
| `poetry run chronicle --help` lists all required subcommands | pass/fail/not attempted | Paste help output |
| CI exists for Python 3.11 and 3.12 on Windows and Ubuntu | pass/fail/not attempted | Name workflow file and matrix |
| Ruff configuration exists | pass/fail/not attempted | Name config location |
| Pre-commit configuration exists | pass/fail/not attempted | Name config file |
| MIT license exists | pass/fail/not attempted | Name file |
| `.gitignore` excludes local/private artifacts | pass/fail/not attempted | List relevant ignore rules |
| No real chat/export data was committed | pass/fail/not attempted | Confirm inspection result |

## Command Evidence
Paste concise output for:

```bash
poetry install
poetry run pytest
poetry run chronicle --help
```

If a command was not run, explain exactly why.

## Scope Control

| Guardrail | Status | Notes |
| --- | --- | --- |
| Did not implement DB schema | pass/fail |  |
| Did not implement real importers | pass/fail |  |
| Did not implement search | pass/fail |  |
| Did not add adapter base/protocol | pass/fail |  |
| Did not add real chat data or exports | pass/fail |  |

## Risks Or Follow-Ups
List any known issues, incomplete items, assumptions, or recommended follow-up tasks.
```

## Completion Status Expected
Return one of:

- `ready for PM validation`
- `blocked`

If blocked, include:

- the exact blocker
- what was attempted
- what decision or missing information is needed
