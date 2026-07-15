# WP-5.1.4 Handoff: Windows CI Rich Output Wrapping

## Assignment

Fix the Windows GitHub Actions failure in
`test_unknown_task_model_alias_is_actionable` without weakening the accepted
WP-5.1/WP-5.1.3 CLI error contract.

This is a narrow CI-portability patch. Do not redesign AI configuration, task
selection, Rich output generally, or the AI execution path.

## Required Completion Report

Create the detailed completion report at:

`md/handoffs/reports/WP-5.1.4-completion-report.md`

Set its delivery status to `Ready for PM validation` only after every acceptance
criterion in this handoff passes.

Do not stage or commit any file. The PM/manager owns validation, staging, and the
commit after owner approval.

## Operating Rules

Read and follow `md/agent-operating-notes.md` before running Poetry commands.

Run this preflight first:

```powershell
poetry env info --path
```

Expected repository environment:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

Stop if Poetry resolves to another project's environment. Avoid piped PowerShell
commands and unnecessary parallel shell launches because the Windows sandbox has
previously failed those patterns.

Use synthetic test data only. Do not read the owner's real archive, local AI result
rows, exports, or private `.chronicle` configuration. Do not call LM Studio or any
remote model.

## CI Failure Evidence

GitHub Actions runs the full suite successfully except for one Windows-only
assertion:

```text
FAILED tests/test_cli_ai_tasks.py::test_unknown_task_model_alias_is_actionable
1 failed, 370 passed
```

The test expects this contiguous substring:

```text
unknown model profile
```

The rendered Windows output is semantically correct but Rich wraps the long pytest
temporary path and later wraps the diagnostic between `model` and `profile`:

```text
Task 'test-task' in
C:\Users\runneradmin\...\.chronicle\ai-tasks.yaml references unknown model
profile 'missing-profile'
```

Therefore this assertion fails even though:

- the command exits with code 1;
- the missing alias is identified;
- the error is actionable;
- no traceback is printed.

Local runs pass because their temporary path and effective terminal layout differ
from the GitHub Windows runner. The regression is environmental output wrapping,
not an AI-task execution failure.

## Current Relevant Behavior

`validate_catalog_references()` raises an `AIConfigError` containing:

- the task name;
- the task catalog path;
- `unknown model profile`;
- the missing profile alias.

The root AI-task CLI catches that error and renders it through the existing
Typer/Rich failure path. The current CLI test asserts directly against rendered
terminal text.

There is also a lower-level configuration test that validates the unrendered
`AIConfigError` message. Preserve that test and distinction: the domain error should
remain precise, while CLI rendering tests must account for legitimate terminal
layout.

## Objective

Make the error behavior and test suite deterministic across:

- Windows and Linux;
- short and long temporary paths;
- local terminals and GitHub Actions capture;
- different reasonable terminal widths;
- Rich line wrapping.

The user-facing diagnostic must remain clear and must still identify the task and
missing model profile without a traceback.

## Required Investigation

Before editing, reproduce or deterministically simulate the failure locally. Use a
synthetic long temporary/config path and/or an explicitly constrained terminal width
through the supported Typer/Click test interface.

Record in the completion report:

1. whether the failure reproduces with a long path, a narrow terminal, or both;
2. the exact rendering boundary that breaks the assertion;
3. whether production behavior needed adjustment or only the rendered-output test;
4. why the selected fix remains stable when Rich inserts line breaks.

Do not claim that Windows path syntax itself is invalid. The supplied path is valid;
its length changes Rich's layout.

## Implementation Requirements

Choose the smallest defensible correction after reproduction.

Acceptable approaches include:

- making the CLI test compare a normalized rendering while retaining strong
  semantic assertions;
- rendering the short actionable diagnostic separately from optional long path
  context, accompanied by wrapping-independent tests;
- a similarly narrow approach that proves stable under constrained terminal width.

The fix must satisfy all of the following:

1. Keep exit code 1 for an unknown task model alias.
2. Keep the task name visible.
3. Keep the missing alias visible.
4. Preserve the semantic diagnostic `unknown model profile` after legitimate
   terminal whitespace normalization.
5. Keep `Traceback` absent.
6. Preserve the lower-level `AIConfigError` contract.
7. Do not hide or swallow catalog validation failures.
8. Do not make assertions so weak that any generic failure would pass.
9. Do not globally disable Rich formatting or change unrelated command output.
10. Do not add OS-specific skips, `xfail`, retries, or CI-only branches.

If output normalization is used, normalize presentation-only whitespace or ANSI
formatting in a focused test helper. Do not remove arbitrary characters or collapse
the entire diagnostic into an assertion that only checks the alias.

If production wording/order is changed, preserve actionable information and add
tests for the exact domain-level message plus wrapping-independent CLI semantics.

## Required Regression Coverage

Add or adjust focused synthetic tests proving:

1. the existing normal-width unknown-profile case passes;
2. a long Windows-style temporary/config path cannot break semantic validation;
3. constrained terminal width cannot break semantic validation;
4. exit code remains 1;
5. task name and `missing-profile` remain present;
6. normalized output contains `unknown model profile`;
7. no traceback is rendered;
8. lower-level `validate_catalog_references()` still raises the expected
   `AIConfigError`;
9. a valid task/model reference still succeeds and is not affected by the patch.

The regression must be deterministic on non-Windows developer machines as well as
Windows CI. Do not rely solely on the host's natural pytest temporary path length.

## Scope Boundaries

Expected files are limited to the smallest necessary subset of:

- `tests/test_cli_ai_tasks.py`;
- a focused shared CLI-test helper, only if justified;
- `src/chat_chronicle/ai_config.py` or `src/chat_chronicle/cli.py`, only if a
  production diagnostic adjustment is necessary;
- this WP's completion report;
- `md/development-ledger.md` status only if requested by the PM after delivery.

Do not modify:

- task prompts or output schemas;
- model routing or LiteLLM behavior;
- caching or AI result persistence;
- database schema or archive records;
- tracked AI model defaults;
- WP-5.1.2 evaluation design;
- unrelated tests to make the suite pass.

## Validation Commands

Run, at minimum:

```powershell
poetry env info --path
poetry run pytest tests/test_cli_ai_tasks.py::test_unknown_task_model_alias_is_actionable -q
poetry run pytest tests/test_ai_config_matrix.py tests/test_cli_ai_tasks.py -q
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
git diff --check
git status --short
```

Also run the deterministic long-path/narrow-width regression directly if it is a
separate test.

Expected full-suite result after the fix: all 371 collected tests pass, plus any new
regression test added by this WP.

## Acceptance Criteria

WP-5.1.4 is ready for PM validation only when:

1. The GitHub Windows failure has a documented, reproduced root cause.
2. The relevant CLI test no longer depends on Rich preserving one physical line.
3. Long-path and constrained-width behavior are covered deterministically.
4. The user still receives an actionable unknown-profile diagnostic.
5. Exit code, task name, missing alias, and no-traceback behavior are preserved.
6. No test is skipped, xfailed, conditionally bypassed, or reduced to a generic
   nonzero-exit assertion.
7. Focused tests pass.
8. The full suite passes.
9. Ruff, help, and diff checks pass.
10. No private DB, config, export, transcript, generated AI result, ZIP, or JSONL is
    tracked.
11. The required completion report is complete.
12. Nothing is staged or committed.

## Completion Report Requirements

The report at `md/handoffs/reports/WP-5.1.4-completion-report.md` must contain:

1. Status: `Ready for PM validation`.
2. Executive summary.
3. Root-cause analysis.
4. Local deterministic reproduction method and evidence.
5. Selected fix and why it is wrapping-independent.
6. Files changed.
7. Regression tests added or changed.
8. Requirement-by-requirement acceptance checklist.
9. Focused/full/Ruff/help/diff command results.
10. Privacy/tracked-artifact check.
11. Known limitations, if any.
12. Final `git status --short`.
13. Explicit confirmation that no files were staged or committed.

Do not include private absolute paths, transcripts, AI outputs, credentials, or
local configuration contents in the report.
