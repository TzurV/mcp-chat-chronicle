# WP-5.1.4 Validation Review: Windows CI Rich Output Wrapping

## Status

**Locally accepted; remote GitHub Actions confirmation pending.**

The implementation satisfies the handoff under deterministic local validation and
is ready for the PM-owned commit. WP-5.1.4 is not finally closed until the committed
patch is pushed and the real GitHub Actions Windows and Ubuntu jobs both pass.

## PM Summary

The reported failure was a test-rendering defect rather than a production CLI
defect. Rich legitimately inserted line breaks after a long GitHub Windows temporary
path, while the test required `unknown model profile` to remain one contiguous raw
substring.

The patch changes tests only. It normalizes presentation whitespace while retaining
strong assertions for exit code, task identity, the exact missing profile, the full
semantic diagnostic, and absence of a traceback. Separate tests construct a long
Windows-runner-shaped path and force a 20-column Rich console.

## Findings

No blocking implementation finding.

The remaining validation dependency is environmental: the deterministic regressions
run on any host OS, including Linux, but only a pushed GitHub workflow can confirm
the exact hosted Windows runner that originally failed. Local green tests are not a
substitute for that final matrix result.

## Scope Review

Implementation changes are confined to:

- `tests/test_cli_ai_tasks.py`;
- `md/handoffs/reports/WP-5.1.4-completion-report.md`.

No production source, model configuration, prompt, schema, cache, database, or CLI
behavior changed. No skip, `xfail`, retry, OS branch, or CI-only bypass was added.

## Acceptance Checklist

| Requirement | Result | Evidence |
| --- | --- | --- |
| Root cause reproduced deterministically | Pass | Long runner-shaped path and forced 20-column Rich console reproduce physical wrapping. |
| Semantic assertion is wrapping-independent | Pass | Focused helper normalizes whitespace only. |
| Strong error contract retained | Pass | Exit 1, task name, exact missing alias, complete normalized diagnostic, and no traceback are mandatory. |
| Lower-level domain contract retained | Pass | Existing `validate_catalog_references()` test remains unchanged and passes. |
| Production behavior unchanged | Pass | Test-only implementation diff. |
| Cross-platform simulation present | Pass | Synthetic path segments and explicit console width do not depend on host OS. |
| Focused validation | Pass | Unknown-profile tests and 32-test AI configuration/CLI matrix pass independently. |
| Full validation | Pass | Full local suite passes with 373 tests reported by the executor. |
| Ruff and diff checks | Pass | Independently clean. |
| Hosted Windows and Ubuntu jobs | Pending | Requires PM commit, owner push, and GitHub Actions completion. |

## Independent Validation

```powershell
poetry env info --path
poetry run pytest tests/test_cli_ai_tasks.py -k unknown_task_model_alias -q
poetry run pytest tests/test_ai_config_matrix.py tests/test_cli_ai_tasks.py -q
poetry run pytest -q
poetry run ruff check .
git diff --check
```

Results:

- Poetry resolved to the repository `.venv`;
- three unknown-profile variants passed;
- the 32-test focused matrix passed;
- the full suite passed;
- Ruff reported `All checks passed!`;
- diff validation passed.

## Remote Closure Gate

After PM commit and owner push:

1. Confirm the GitHub Actions Windows job passes the previously failing test.
2. Confirm the Ubuntu job also passes, proving the normalization is cross-platform.
3. Record workflow URL, commit SHA, job names, and final pass/fail status in the
   ledger without copying runner paths or other unnecessary environment details.
4. Only then change WP-5.1.4 from `Remote CI confirmation pending` to `Accepted`.

If either job fails, do not stack unrelated work on the patch. Return WP-5.1.4 to
rework with the exact failing assertion and hosted-runner evidence.

## Decision

Approve WP-5.1.4 for PM commit. Keep prompt calibration and WP-5.1.2 paused until
the pushed commit has a green Windows and Ubuntu matrix.
