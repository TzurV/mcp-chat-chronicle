# Vertex AI LLM-as-Judge Connectivity Implementation Report

**Date:** 2026-07-21  
**Audience:** Development manager  
**Status:** Connectivity implemented, verified, and accepted for local private-judge use

## Objective

Establish and verify access from the Chat Chronicle development environment to Google Gemini for the WP-5.2B1 LLM-as-judge path, while keeping credentials out of source control and local YAML configuration.

## Outcome

The supported path is Google Vertex AI authenticated with Google Application Default Credentials (ADC). An end-to-end LiteLLM request to `vertex_ai/gemini-2.5-flash` completed successfully and returned the expected sentinel response:

```text
VERTEX_LITELLM_OK
```

This verifies the complete transport chain:

```text
PowerShell environment -> ADC -> Vertex AI -> Gemini 2.5 Flash -> LiteLLM
```

No API key is required for the selected implementation.

## Implementation

The local Google/LLM PowerShell activation profile now supplies both the Google SDK variables and LiteLLM's Vertex aliases:

```text
GOOGLE_CLOUD_PROJECT=<owner-project-id>
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true
VERTEXAI_PROJECT=<owner-project-id>
VERTEXAI_LOCATION=us-central1
```

The repository defaults were updated as follows:

- `bench/ai-models.evaluation.default.yaml` selects `vertex_ai/gemini-2.5-flash` and no longer requires `GEMINI_API_KEY`.
- The `enrich` optional dependency in `pyproject.toml` enables LiteLLM's Google dependencies through `litellm[google]`.
- `poetry.lock` contains the resolved Google authentication and Vertex AI provider dependencies.
- Authentication remains external to the repository through ADC and the isolated personal `gcloud` configuration.

## Verification Evidence

The following checks passed:

1. The active `gcloud` account and project resolved under the isolated personal configuration.
2. `gcloud auth application-default print-access-token` completed successfully (`ADC_OK`).
3. A direct authenticated Vertex AI REST request reached `gemini-2.5-flash` and returned model metadata and usage information.
4. A LiteLLM completion through the project Poetry environment returned `VERTEX_LITELLM_OK`.

The original Gemini Developer API key route reached Google but returned `API_KEY_SERVICE_BLOCKED`. That route was not adopted because the existing Vertex AI and ADC path is operational and avoids storing an additional secret.

## Security and Privacy

- No API key, OAuth access token, or ADC credential was written to the repository.
- The tracked report does not disclose the owner's Google Cloud project identifier.
- No credential value is present in the model profile.
- The connectivity checks used only synthetic sentinel prompts.
- No private conversation, FABLE reference, candidate output, or judge payload was disclosed during verification.

## Repository Validation

The development manager independently reinstalled the resolved `enrich` extra and ran:

```powershell
poetry install -E enrich
poetry run pytest tests/test_ai_config_matrix.py tests/test_bench.py -q
poetry run pytest
poetry run ruff check .
poetry check
```

Results:

- optional dependency installation and lock resolution: passed;
- focused configuration/benchmark tests: 50 passed;
- full suite: 409 passed;
- Ruff: passed;
- Poetry project/lock consistency: passed;
- tracked credential/project-identifier scan: passed;
- the accidental empty shell-redirection artifact `1.74` was removed and not tracked.

This report confirms provider connectivity only. It does not record an authorized private-corpus judge run or replace the explicit `--with-judge --allow-remote --confirm-private-eval` controls required for real evaluation scoring.

## Structured-output compatibility addendum

The sentinel test above proved authentication and transport, not compatibility with Chronicle's
judge output contract. The first judge attempt passed `JudgeResult.model_json_schema()` directly
through LiteLLM. That application schema contained provider-risky constructs, including a
single-value `const`, string-length constraints, defaults, and an open-ended score mapping. Vertex
returned responses, but none reached an accepted application result.

WP-5.2B1.1 implements the boundary separation by generating a small task-specific provider schema containing
only the verified Vertex JSON Schema subset. It requires the exact rubric score properties and
uses a one-value string enum for success. The unchanged strict application model and case-level
checks remain authoritative after JSON parsing. Cache identity now binds both schema layers and
the normalizer/request-construction versions, so the historical failures cannot be reused by the
corrected contract. The first synthetic compatibility-gate call still returned invalid JSON, so
end-to-end judge-contract compatibility is not yet accepted and no private retry was attempted.
This addendum does not revise the narrower claim made by the original connectivity test.

### Reasoning-control rework

The follow-up gate configured LiteLLM `reasoning_effort: none`, which maps Gemini 2.5 Flash to a
zero thinking budget. All four real synthetic task contracts then completed with normalized finish
category `stop` and strict application validation; the identical rerun made zero provider calls.
This supports output-budget exhaustion from automatic thinking as the cause of the earlier invalid
JSON boundary, without changing the provider schema. The subsequent private gate completed five
of six eligible cases; one response finished normally but exceeded the application rationale
length bound. That semantic gate therefore remains incomplete.

### Rationale-contract rework

Provider schema version 3 added the existing 500-character application limit and concise,
no-chain-of-thought guidance to `rationale`. The revised real synthetic gate passed 4/4 and its
identical rerun made zero calls. The fresh private gate then passed 6 completed, 0 failed, and 2
skipped-invalid cases. The local rerun defect was a Windows newline-comparison false positive in
the first confusion-matrix CSV, not a semantic difference. After canonical/idempotent report
rework, the guarded `--judge-cache-only` command exited zero, retained the same six attempts, and
made zero additional Vertex calls.
