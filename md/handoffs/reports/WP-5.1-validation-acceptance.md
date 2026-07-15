# WP-5.1 Validation Acceptance: YAML AI-Task Runner + LiteLLM

## Decision

**Accepted.**

WP-5.1 satisfies the handoff after two validation/rework cycles. The configurable AI-task infrastructure is accepted; the four production conversation-intelligence tasks remain WP-5.1.1 scope.

## Accepted Scope

- Strict, versioned external task and model YAML catalogs.
- Installed-package-safe AI templates and `chronicle init` behavior.
- Root `--ai-task` discovery and explicitly bounded execution.
- Local-first remote authorization and actionable failure handling.
- Lazy optional LiteLLM adapter behind a Chronicle-owned interface.
- Provider JSON-schema requests plus mandatory local Pydantic validation.
- Deterministic selectors and prompt/input provenance.
- Schema-v3 append-only `ai_task_results` migration and storage.
- Complete request/output-interpretation cache identity.
- Model-profile generation defaults with per-field task overrides.
- Effective generation values used consistently by requests and cache identity.
- Bounded foreground concurrency, failure isolation, resume, and `--force` auditability.
- Base/non-AI command isolation and privacy-safe tracked artifacts.

## Final PM Validation Evidence

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv

focused ten-file WP-5.1 acceptance collection
127 passed

poetry run pytest
313 passed in 50.10s

poetry run ruff check .
All checks passed!

poetry run chronicle --help
passed; all existing commands and AI root options present

git diff --check
passed; poetry.lock line-ending warning only

git ls-files "*.db" "*.sqlite" "*.zip" ".chronicle/*" "exports/*"
no output
```

Packaging/resource evidence retained from revalidation:

- wheel built successfully;
- packaged task and model YAML resources are present;
- outside-checkout initialization regression passed;
- root and packaged templates are byte-identical.

The documented Windows sandbox launcher error recurred on standalone wheel commands and passed when retried through the approved sandbox escalation. It was not a project failure.

## Generation Precedence Revalidation

The final accepted rule is:

1. Model profile supplies concrete temperature and max-token defaults.
2. Task configuration may override either field independently or both.
3. `CompletionRequest` receives the effective values.
4. Resolved model cache identity replaces raw profile generation settings with effective generation values.
5. An effective default change changes the request and invalidates cache.
6. A profile-default change masked by explicit task overrides preserves the request and cache hit.
7. Invalid task overrides and profile defaults fail before an LLM call.

Eleven focused generation precedence/request/cache/bounds tests were added and passed.

## Closed Validation Findings

1. Installed wheel missing AI templates.
2. Stale cache reuse after prompt metadata changes.
3. Non-actionable dependency/selection failures.
4. JSON schema not propagated to LiteLLM.
5. Missing dry-run cache counts and model provenance.
6. Missing configuration/CLI/migration/failure/concurrency/cache acceptance matrix.
7. Model-profile generation defaults ignored while affecting cache identity.

## Residual Boundaries

- The tracked example task remains disabled and documentation-only.
- The four production conversation-intelligence tasks remain WP-5.1.1.
- Real-history teacher references remain WP-5.1.2.
- Local-model comparative execution/reporting remains WP-5.2.
- A real LM Studio/provider call was optional and was not required for acceptance.

## Next Step

Finalize and hand off WP-5.1.1. WP-5.1.2 remains blocked until the four production task contracts, selectors, prompts, and schemas are accepted.

No commit was made during PM validation.

