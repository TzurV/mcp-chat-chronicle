# Agent Operating Notes

These notes capture local workflow hazards for agents working on this repository. Future handoffs and validation reviews should reference this file when relevant.

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

