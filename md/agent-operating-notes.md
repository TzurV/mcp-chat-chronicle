# Agent Operating Notes

These notes capture local workflow hazards for agents working on this repository. Future handoffs and validation reviews should reference this file when relevant.

## Commit Ownership And Delivery Workflow

The PM/manager owns staging and commits. Executor agents must not run `git add`,
`git commit`, amend, squash, rebase, or otherwise rewrite repository history.

The required workflow is:

1. The executor implements the handoff and runs all required validation.
2. The executor writes the required detailed completion report.
3. The executor leaves all delivery changes uncommitted and reports
   `git status --short` to the PM.
4. The PM validates the implementation and completion report against the handoff.
5. Rework, when required, is also left uncommitted for repeat PM validation.
6. Only after successful PM validation and an explicit owner request does the
   PM/manager stage and commit the accepted changes.

Every future executor handoff must repeat this rule in its delivery section. A
commit request made to the PM, a commit request for an earlier work package, or a
message adjacent to a handoff is not authorization for the executor to commit.
Executor delivery status is `Ready for PM validation`, never `Accepted`.

## Poetry Virtualenv Preflight

Poetry can accidentally install this project's dependencies into another project's virtualenv if the shell has an active `VIRTUAL_ENV`. This already happened once on this machine when Poetry saw a `VIRTUAL_ENV` from another repo.

Before running any Poetry install, test, lint, or CLI command, executor agents must verify the active environment from the repository root:

```powershell
poetry env info --path
```

The path must be inside this repo:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If the path points anywhere outside `C:\work\Github\mcp-chat-chronicle`, stop before running `poetry install` or `poetry run ...`.

Preferred fix:

1. Open a fresh terminal that has no activated virtualenv.
2. `cd C:\work\Github\mcp-chat-chronicle`
3. Run:

```powershell
poetry env info --path
poetry install
poetry env info --path
```

If a fresh terminal is not available, deactivate the current virtualenv first:

```powershell
deactivate
```

Then verify again:

```powershell
poetry env info --path
```

Do not continue unless the path is this repo's `.venv`.

If Poetry still reports the wrong environment, report the blocker instead of installing dependencies. Do not try to repair another project's virtualenv from this repo.

## Sandbox Execution Notes

On this Windows workspace, the sandbox can intermittently reject process launches with:

```text
CreateProcessAsUserW failed: 1312
```

This is a sandbox launcher issue, not necessarily a project failure.

To reduce wasted retries:

- Prefer `rg` for searching and file discovery.
- Prefer `Get-Content -Raw <file>` for full file reads.
- Avoid PowerShell pipelines for file slicing or filtering when a direct `rg` query will work.
- Avoid parallel PowerShell reads unless the time savings are worth a possible retry.
- If an important `poetry run ...` command fails only with the launcher error, retry the exact command once with sandbox escalation and record that escalation was for sandbox validation only.

## Real-Data Development Policy

This project is also a learning exercise. The owner prefers early testing against the available
real conversation corpus rather than requiring synthetic-only provider development, even when
that accepts a measured reduction in privacy. Synthetic fixtures remain required for committed,
repeatable, network-independent CI coverage, but they are not a prerequisite that must completely
prove an integration before a bounded real-data smoke can begin.

Future plans and executor handoffs should:

1. use a small representative real-data scope early, normally one or two conversations, alongside
   synthetic contract tests;
2. state the remote provider, disclosed fields, conversation scope, maximum calls/retries, and
   expected cost boundary once at the start of the development gate;
3. allow a bounded diagnostic and correction loop inside that approved scope instead of stopping
   after every recoverable provider/schema observation;
4. stop immediately for scope expansion, unexpected sensitive fields, credentials exposure,
   unbounded retries/cost, destructive behavior, or a materially different provider;
5. keep real inputs, model responses, databases, evaluation packages, and diagnostic artifacts
   ignored and untracked unless the owner explicitly approves publication;
6. redact private content from tracked reports while retaining useful aggregate evidence;
7. exercise first-run, rerun, cache, report, and recovery behavior during the same real-data smoke;
8. prefer one completion report with gate addenda over repeated handoffs for narrow issues within
   the same approved objective.

The owner accepting more privacy exposure for development is not blanket authorization to upload
the full corpus or use arbitrary providers. Handoffs must still define a bounded disclosure scope,
but should make that authorization broad enough to complete a practical integration cycle.
