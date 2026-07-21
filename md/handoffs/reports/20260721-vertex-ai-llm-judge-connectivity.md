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
