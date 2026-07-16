# WP-5.1 Validation Review 2: Model Generation Defaults

## Decision

**Narrow rework required. WP-5.1 is not yet accepted.**

The first validation review's six findings are materially resolved. Packaging, cache metadata/task/schema identity, actionable CLI failures, provider JSON-schema propagation, dry-run provenance, migration coverage, failure isolation, and the expanded acceptance matrix passed PM revalidation.

One model-configuration correctness defect remains. Return only this narrow review to the WP-5.1 executor; do not reopen accepted rework or add WP-5.1.1 task scope.

## Finding

### P1 - Model-profile generation defaults are ignored but still invalidate cache

Evidence:

- `src/chat_chronicle/ai_config.py` defines and validates `ModelProfile.generation`.
- Both tracked/packaged model templates expose model-profile `generation` values.
- `resolve_model(profile)` includes those values in the canonical resolved model configuration and therefore `model_hash`.
- `src/chat_chronicle/ai.py:238-239` always builds the request from `task.generation.temperature` and `task.generation.max_tokens`.
- `TaskDefinition.generation` always materializes its own default object, so there is no state in which model-profile defaults are applied.
- No test currently asserts that model-profile generation defaults affect the emitted `CompletionRequest`.

Consequences:

1. A user can change model-profile temperature/max tokens in `.chronicle/ai-models.yaml`, but the model request remains unchanged.
2. The profile change still alters `model_hash`, causing a cache miss and potentially another paid call for an identical request.
3. The report describes model generation defaults as supported even though they have no execution effect.
4. WP-5.2 cannot reliably vary model/runtime defaults through the configurable model-profile layer.

This violates the handoff's model-profile contract for optional safe generation defaults and the requirement that cache identity represent the effective request/configuration.

## Required Correction

Implement and document one effective-generation resolution rule.

Preferred rule:

1. Model profile supplies safe defaults.
2. Task configuration may override temperature and/or max tokens.
3. The resolved effective values are sent in `CompletionRequest`.
4. Cache/provenance identity hashes the effective values and the configuration identity needed to reproduce them.

The configuration schema may make task generation or individual task generation fields optional to distinguish "inherit" from an explicit value. Preserve strict validation and bounded limits.

Do not silently remove model-profile generation defaults. Removing them would require a PM-approved handoff/plan change because WP-5.1 explicitly requires optional model-profile defaults.

## Required Tests

Add focused tests proving:

1. A task with no generation override uses model-profile temperature and max tokens.
2. A task overriding only temperature inherits profile max tokens.
3. A task overriding only max tokens inherits profile temperature.
4. Explicit task values override both profile defaults.
5. Changing an effective profile default changes the emitted request and invalidates cache.
6. A configuration change that does not change the effective request does not create misleading cache behavior, or the report explicitly justifies why complete config identity intentionally invalidates it.
7. Resolved generation values remain bounded and invalid values fail before an LLM call.
8. Tracked and packaged templates remain byte-identical.

Update README/config documentation so precedence is unambiguous.

## PM Revalidation Evidence

Fresh PM results before this finding was issued:

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv

focused nine-file acceptance collection
116 passed

poetry run pytest
302 passed in 50.12s

poetry run ruff check .
All checks passed!

poetry run chronicle --help
passed; all existing commands and AI root options present

git diff --check
passed; poetry.lock line-ending warning only

private artifact scan
no tracked DB/SQLite/ZIP/.chronicle/export artifacts
```

PM rebuilt the wheel and confirmed its manifest now contains:

```text
chat_chronicle/resources/__init__.py
chat_chronicle/resources/ai-models.default.yaml
chat_chronicle/resources/ai-tasks.default.yaml
```

Root and packaged template comparisons returned no differences.

The Windows sandbox launcher error `CreateProcessAsUserW failed: 1312` recurred on the standalone wheel commands; the important checks passed when retried with the documented sandbox escalation. This is not a project failure.

## Rework Delivery Instructions

The executor must:

1. Implement effective generation-default/override precedence.
2. Add the focused tests above.
3. Refresh `md/handoffs/reports/WP-5.1-completion-report.md`, including the final YAML semantics and cache identity.
4. Run the focused collection, full suite, Ruff, help, diff, wheel-resource, and privacy checks.
5. Keep report status `ready for PM validation` only if all new tests and existing acceptance tests pass.
6. Do not implement WP-5.1.1 tasks or WP-5.1.2 evaluation behavior.
7. Do not commit; return the working tree for final PM revalidation.

## Final Revalidation Gate

PM final revalidation will focus on:

- effective profile/task generation precedence;
- request values and cache behavior;
- unchanged first-review acceptance coverage;
- full regression, Ruff, package resources, diff, and privacy evidence.

WP-5.1.1 and WP-5.1.2 remain dependency-gated until WP-5.1 is accepted.
