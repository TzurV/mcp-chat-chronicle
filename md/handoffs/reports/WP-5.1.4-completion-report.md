# WP-5.1.4 Completion Report

## Status

Ready for PM validation

## Executive Summary

The Windows CI failure was a rendered-output assertion defect, not a production
AI-task or configuration defect. Rich may insert line breaks inside the semantic
phrase `unknown model profile` when the preceding catalog path changes the line
layout. The CLI regression now normalizes presentation-only whitespace before
asserting the complete task-specific diagnostic. Two additional synthetic tests
cover a long Windows-runner-shaped path and an explicitly constrained 20-column
Rich error console. Production code and domain wording remain unchanged.

## Root-Cause Analysis

`validate_catalog_references()` raises the correct `AIConfigError`, including the
task name, task catalog path, `unknown model profile`, and the missing alias. The
root CLI catches that error and prints it through Rich. The previous CLI test
searched raw rendered output for one contiguous physical-line substring. A long
temporary path changes Rich's wrapping position and can place a newline between
`model` and `profile`; Windows path syntax is valid and was not the defect.

Only the rendered-output test required adjustment. Changing production wording,
globally disabling Rich, or hiding path context would have expanded scope without
improving the actionable error contract.

## Deterministic Local Reproduction

The reproduction used only generated catalogs and a generated database under a
temporary directory. No owner archive, result row, export, private configuration,
local model, or remote service was accessed.

A synthetic path-length sweep reproduced the old assertion failure at controlled
leaf lengths 42 through 49. At the boundary, Rich rendered:

```text
...ai-tasks.yaml references unknown model
profile 'missing-profile'
```

Thus `unknown model profile` was absent from raw output even though the diagnostic
was semantically intact. The failure reproduced from path length interacting with
the effective render width. The added narrow-width regression sets the Rich error
console to 20 columns, which deterministically forces the semantic phrase to wrap;
it asserts that the raw contiguous phrase is absent before validating normalized
semantics. The long-path regression builds a runner-shaped hierarchy containing
`Users/runneradmin/AppData/Local/Temp/pytest-of-runneradmin` and proves that a
catalog path longer than 200 characters is handled correctly on every host OS.

## Selected Fix

The focused `_normalized_rendering()` test helper joins whitespace-separated
rendering tokens with single spaces. It changes only presentation whitespace
inserted by terminal wrapping; it does not remove arbitrary characters, alter
production output, or reduce validation to a generic failure check.

The shared assertion requires all of the following after normalization:

- exact exit code 1;
- task identity `Task 'test-task'`;
- the complete diagnostic `unknown model profile 'missing-profile'`;
- absence of `Traceback` in raw output.

This remains stable wherever Rich inserts spaces or line breaks while rejecting a
generic nonzero failure, a wrong task, a wrong alias, or a different diagnostic.

## Files Changed

- `tests/test_cli_ai_tasks.py` — focused normalization helper, strengthened shared
  semantic assertion, long-path regression, and constrained-width regression.
- `md/handoffs/reports/WP-5.1.4-completion-report.md` — this report.

No production source file was changed. Existing modifications to
`md/development-ledger.md`, `md/master-plan.md`, and the untracked handoff predated
this execution and were not modified by the executor.

## Regression Coverage

- The original normal-width test continues to exercise the unknown-profile path.
- The long runner-shaped path is host-independent and explicitly exceeds 200
  characters.
- The 20-column console deterministically splits the raw semantic phrase.
- All variants require exit code 1, the task name, the missing alias, the complete
  normalized diagnostic, and no traceback.
- `tests/test_ai_config_matrix.py::test_task_to_model_alias_is_validated` remains
  unchanged and passed, preserving the lower-level `AIConfigError` contract.
- Existing valid task/model tests, including list and dry-run success cases, passed
  in both the focused matrix and full suite.

No skip, xfail, retry, OS branch, or CI-only bypass was added.

## Acceptance Checklist

- [x] Documented and deterministically reproduced the Rich wrapping root cause.
- [x] Removed dependence on one physical output line.
- [x] Added deterministic long-path and constrained-width coverage.
- [x] Preserved actionable task name, missing alias, and semantic diagnostic.
- [x] Preserved exact exit code 1 and no-traceback behavior.
- [x] Preserved the lower-level `AIConfigError` contract.
- [x] Did not hide or swallow catalog validation failures.
- [x] Kept strong task-specific assertions.
- [x] Did not change global Rich behavior or unrelated output.
- [x] Added no skip, xfail, retry, conditional bypass, or OS-specific branch.
- [x] Focused tests passed.
- [x] Full suite passed.
- [x] Ruff, CLI help, and diff checks passed.
- [x] Privacy and tracked-artifact review completed.
- [x] Delivery remains unstaged and uncommitted for PM validation.

## Validation Results

- `poetry env info --path` — passed; resolved to this repository's `.venv`.
- `poetry run pytest tests/test_cli_ai_tasks.py -k unknown_task_model_alias -q`
  — passed, 3 tests.
- `poetry run pytest tests/test_cli_ai_tasks.py::test_unknown_task_model_alias_is_actionable -q`
  — passed, 1 test.
- `poetry run pytest tests/test_ai_config_matrix.py tests/test_cli_ai_tasks.py -q`
  — passed, 32 tests.
- `poetry run pytest` — passed, 373 tests in 47.25 seconds.
- `poetry run ruff check .` — passed, all checks passed.
- `poetry run chronicle --help` — passed, exit code 0 with expected help output.
- `git diff --check` — passed with no output.

The Windows sandbox launcher initially returned its documented process-launch
error. Required commands were run individually with sandbox escalation; this was
an execution-environment workaround, not a test retry or product branch.

## Privacy and Tracked-Artifact Check

All new test data is synthetic and created under pytest temporary directories.
`git ls-files` found no tracked database, SQLite, ZIP, or `.chronicle` artifact.
Tracked JSONL files are existing synthetic fixtures under `tests/fixtures`; no new
JSONL file was added. No transcript, generated AI result, credential, private
absolute path, or local configuration content is included in this delivery.

## Known Limitations

None within WP-5.1.4 scope. The test intentionally normalizes whitespace only; it
does not attempt to normalize arbitrary ANSI or other characters because captured
output for this path does not require that broader behavior.

## Final Worktree State

Final `git status --short` at report creation:

```text
 M md/development-ledger.md
 M md/master-plan.md
 M tests/test_cli_ai_tasks.py
?? md/handoffs/WP-5.1.4-windows-ci-rich-output-wrapping.md
?? md/handoffs/reports/WP-5.1.4-completion-report.md
```

No file was staged or committed. PM/manager validation, staging, and commit remain
explicitly reserved for the PM/manager after owner approval.
