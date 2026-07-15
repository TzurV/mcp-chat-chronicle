# WP-5.1.3 Validation Review: Local LM Studio AI Tasks

## Status

**Accepted.**

## PM Summary

WP-5.1.3 satisfies the handoff. Chronicle now routes the local model through
LiteLLM's explicit `lm_studio/` provider prefix, sends strict JSON Schema requests
that Qwen3.5-4B can complete, finalizes provider-compatible structures into the
accepted stored task contracts, and records privacy-safe actionable failures.

All four accepted AI tasks completed against short synthetic data and owner-selected
real conversations through the owner's local LM Studio service. An unchanged summary
rerun used the cache without another model call or appended result.

## Findings

No blocking findings.

One owner-side configuration distinction is intentional: tracked defaults and fresh
`chronicle init` output now use a 180-second timeout, zero retries, and an 8192-token
context window, but `init` does not overwrite an existing private
`.chronicle/ai-models.yaml`. At PM validation time, the owner's existing catalog still
reported `timeout=480`, `retries=1`, and no configured context window. It remains
functional, but the owner should manually align those values when the tracked policy
is desired. This private catalog is not a repository artifact.

## Acceptance Checklist

| Requirement | Result | Evidence |
| --- | --- | --- |
| Concrete real-call failure identified | Pass | Missing LiteLLM provider routing was isolated; the accepted model value is `lm_studio/qwen3.5-4b`. |
| Direct LM Studio and direct LiteLLM probes succeed | Pass | Completion report records privacy-safe successful text and strict JSON Schema probes. |
| Synthetic Chronicle execution succeeds | Pass | All four task schemas pass through the normal Chronicle execution and persistence path. |
| Short real-conversation execution succeeds | Pass | All four tasks completed on conversation 699; summary also completed on conversation 685 after exact evidence binding. |
| Accepted stored task contracts preserved | Pass | Provider-only summary/next-action shapes are finalized into the accepted result schemas; affected finalizer identities advanced to version 2. |
| Evidence IDs are exact selected IDs | Pass | Provider schemas bind `evidence_message_ids` to the selected ID enum and client-side validation remains active. |
| Cache and retry behavior is correct | Pass | Successful unchanged summary rerun cached without a model call; failures remain append-only and retryable. |
| Failures are actionable and privacy-safe | Pass | Route, model, context, timeout, connection, authentication, rate-limit, parameter, and HTTP categories are normalized without provider-controlled detail. |
| Archive content remains unchanged | Pass | Report confirms no normalized conversation/message/FTS content was modified by AI execution. |
| Documentation and diagnostics are sufficient | Pass | README covers LM Studio setup, prefixed model selection, strict schemas, timeout/context policy, `--verbose`, caching, and privacy. |
| Automated validation passes | Pass | Focused AI collection, full suite, Ruff, and `git diff --check` pass independently. |
| Completion report exists | Pass | `md/handoffs/reports/WP-5.1.3-completion-report.md`. |

## Independent Validation

```powershell
poetry env info --path
```

Resolved to the repository-local `.venv`.

```powershell
poetry run pytest tests/test_ai_adapter.py tests/test_ai_config_matrix.py tests/test_ai_execution_matrix.py tests/test_cli_ai_tasks.py tests/test_conversation_intelligence.py -q
poetry run pytest -q
poetry run ruff check .
git diff --check
poetry run chronicle --ai-task list --verbose
```

Results:

- focused AI collection passed;
- full suite passed, matching the reported 371-test collection;
- Ruff reported `All checks passed!`;
- diff whitespace validation passed;
- task discovery listed all four tasks and printed only privacy-safe effective
  configuration metadata.

The PM did not repeat the long real-model calls or reproduce private generated
outputs. The executor's real smoke evidence is retained only as privacy-safe IDs,
statuses, timing ranges, schema validity, and cache behavior in the completion
report.

## Decision

Accept WP-5.1.3.

Next PM action: calibrate the four prompts on a small owner-selected real-chat sample
before revising and releasing WP-5.1.2. The automated dual-teacher corpus remains
paused until that discussion defines the prompt and reference workflow.
