# WP-5.1.4 Validation Review: Windows CI Rich Output Wrapping

## Status

**Accepted.**

The implementation satisfies the handoff under deterministic local validation. The
PM committed it as `f0ecaf6`, the owner pushed it, and the owner subsequently
confirmed that the hosted GitHub test passed. The remote closure gate is complete.

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

No blocking finding.

The deterministic regressions run on any host OS, including Linux, while the pushed
GitHub workflow supplied the final hosted-runner confirmation for the environment in
which the original failure occurred.

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
| Hosted GitHub Actions validation | Pass | Owner confirmed the pushed `f0ecaf6` test passed. |

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

## Remote Closure Evidence

- Commit: `f0ecaf6 test: harden Rich output assertions in CI`.
- Owner pushed the commit.
- Owner confirmed the hosted GitHub test passed.
- No hosted-runner path or other unnecessary environment detail is retained here.

## Decision

Accept WP-5.1.4. Resume manual prompt calibration planning. WP-5.1.2 remains paused
until the prompt and reference workflow are agreed.
