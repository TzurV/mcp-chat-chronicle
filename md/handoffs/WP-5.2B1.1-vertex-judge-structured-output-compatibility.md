# WP-5.2B1.1 - Vertex Judge Structured-Output Compatibility

## Status

**Ready for executor implementation.**

Continue in the same executor thread that implemented WP-5.2B1 when practical. Read:

- `md/master-plan.md`;
- `md/development-ledger.md`;
- `md/agent-operating-notes.md`;
- `md/handoffs/WP-5.2B1-split-generation-local-scoring-gemini-judge.md`;
- `md/handoffs/reports/WP-5.2B1-completion-report.md`;
- `md/handoffs/reports/WP-5.2B1-validation-review.md`;
- `md/handoffs/reports/20260721-vertex-ai-llm-judge-connectivity.md`;
- `docs/development-evaluation.md`.

This is a narrow compatibility and validation package. Do not redesign the evaluation
program or regenerate candidate outputs.

## Objective

Make the existing WP-5.2B1 Gemini judge path work reliably through
`vertex_ai/gemini-2.5-flash` with Application Default Credentials and strict,
application-consumable structured results.

Success requires all six schema-valid candidate outputs from the existing two-conversation
development smoke to complete Vertex judge evaluation successfully. The two schema-invalid
candidate outputs must remain explicitly skipped.

Expected final private judge accounting:

```text
eligible: 6
completed: 6
failed: 0
skipped_invalid: 2
```

The judge metrics must contain non-empty task-dimension scores. Candidate generation and
deterministic scoring must not be rerun except for the deterministic scoring operation that the
existing composed `bench score --with-judge` command intentionally performs before judging.

## Background

WP-5.2B1 produced a valid local evaluation-floor smoke using two frozen conversations x four
accepted AI tasks:

- eight candidate cases total;
- six schema-valid Llama 3.2 1B outputs;
- two explicit invalid outputs;
- deterministic scoring completed successfully;
- all six consumable outputs passed application evidence/cross-field checks;
- deterministic categorical quality was intentionally weak, as expected from the 1B floor.

The first remote-judge attempt used the direct `gemini/gemini-2.5-flash` route without an API key.
It correctly preserved six `provider_authentication` failures. That route is not accepted.

Vertex AI connectivity was then implemented and independently validated:

- judge profile: `vertex_ai/gemini-2.5-flash`;
- authentication: Google Application Default Credentials;
- project/location: environment variables outside the repository;
- no `GEMINI_API_KEY`;
- synthetic LiteLLM sentinel connectivity passed;
- repository commit `36a794c` records the accepted Vertex dependency/profile change.

The private judge rerun reached Vertex but produced:

```text
eligible: 6
completed: 0
failed: 6
failure_categories:
  output_schema: 5
  provider_invalid_json: 1
skipped_invalid: 2
```

This proves authentication and transport work. It does not produce a semantic evaluation.
Five responses were parseable but failed the application judge schema; one was not parseable
JSON. No dimension means were available.

## Working Diagnosis

`bench/judge.py` currently sends `JudgeResult.model_json_schema()` directly as the provider
response schema. That Pydantic schema is an application contract, not necessarily a safe Vertex
provider contract.

The generated application schema includes or may include constructs such as:

- `const` for `status: Literal["success"]`;
- string `minLength`/`maxLength` constraints;
- defaults;
- an unconstrained/dynamic `scores: dict[str, int]` shape;
- Pydantic-specific schema structure that has not been proven through the actual Vertex route.

Vertex controlled generation supports a restricted JSON Schema subset. The executor must verify
the actual generated schema and LiteLLM payload against current official Google and LiteLLM
documentation. Do not assume the diagnosis is complete merely because connectivity succeeded.

There is a second confirmed design gap: the current judge cache identity covers candidate,
source, reference, rubric, profile/model/config, and generation settings, but does not explicitly
bind the provider response schema, application schema, or judge request-construction version.
A schema-only implementation change can therefore reuse stale judge results or failures unless
the cache identity is corrected.

## Accepted Design Direction

Separate the provider-facing judge schema from the strict application-facing `JudgeResult`
contract, following the provider-schema/application-schema pattern already used by Chronicle AI
tasks.

The recommended provider contract is task-specific:

- fixed top-level properties;
- `status` represented using a supported one-value string enum rather than `const` if needed;
- `scores` represented as an object with exactly the rubric dimensions for the current task;
- every score an integer from 0 through 4;
- all score dimensions required;
- no extra score dimensions;
- `rationale` as a plain required string in the provider schema, with length enforced later;
- `evidence_message_ids` as a required integer array;
- `unsupported_claim_count` as a required non-negative integer;
- no provider-side defaults;
- only Vertex-supported schema keywords.

An alternative representation, such as a list of `{dimension, score}` records, is acceptable only
if it is demonstrably more reliable through Vertex and is deterministically normalized before
strict application validation. Do not weaken exact task-dimension enforcement.

Application-side validation remains authoritative and must still enforce:

- exact case alias, fingerprint, and task;
- `status == "success"`;
- exact task-specific rubric dimension set;
- score bounds 0-4;
- concise non-empty rationale and its accepted maximum length;
- evidence IDs limited to the selected source IDs;
- non-negative unsupported-claim count;
- no unknown fields;
- privacy-safe failure handling.

Do not silently repair materially malformed judge output. Deterministic normalization of an
accepted provider representation is allowed; inventing missing scores, evidence, or verdicts is
not.

## Required Implementation

### 1. Inspect And Record The Exact Boundary

Using synthetic data only:

1. Materialize the current `JudgeResult` JSON schema.
2. Identify unsupported or unreliable Vertex schema constructs.
3. Record the actual LiteLLM/Vertex structured-output request shape without credentials or private
   prompt content.
4. Reproduce the failure using the exact current judge contract and a synthetic prompt when
   practical.
5. Record the root cause in the completion report using privacy-safe schema facts.

Do not enable verbose LiteLLM debugging during a private run. Provider debug output may include
prompts or responses.

### 2. Add An Explicit Provider-Facing Judge Contract

Implement an application-owned provider schema builder keyed by task/rubric dimensions. It must:

- use only the verified Vertex-supported subset;
- produce deterministic canonical output;
- require every field needed by `JudgeResult`;
- define exact task-specific score dimensions;
- remain independent of candidate-model identity;
- be unit-testable without LiteLLM, Vertex, credentials, or private data.

Keep the existing strict `JudgeResult` model, or a strictly equivalent application model, as the
post-response authority.

### 3. Normalize And Validate Responses

After receiving provider output:

1. Parse strict JSON.
2. Normalize only the explicitly accepted provider representation.
3. Validate through `JudgeResult`.
4. Apply case/fingerprint/task/rubric/evidence checks.
5. Persist only accepted structured output or a privacy-safe failure record.

Known provider invalid JSON, application schema failures, and output-contract failures must remain
separate categories. Unexpected programming/filesystem errors must still abort visibly and must
not be cached as provider failures.

### 4. Correct Judge Cache Identity

Add the following to judge cache identity:

- provider judge schema name and version;
- canonical provider schema hash;
- application judge schema name and version;
- canonical application schema hash;
- judge response normalizer/finalizer version;
- judge request-construction version;
- task-specific rubric/dimension identity.

Changing any of these must create a new immutable cache identity. Matching successful results
remain cached; matching failures retry only under the existing explicit retry policy. The two
existing failed judge runs must remain untouched.

### 5. Improve Privacy-Safe Diagnostics

Persist and report enough bounded metadata to distinguish:

- invalid JSON;
- missing required field;
- unknown field;
- wrong primitive type;
- wrong status/task/case identity;
- missing/extra score dimension;
- score outside 0-4;
- rationale length failure;
- evidence membership failure.

Do not persist raw private judge responses for this work package. Do not include values, source
text, FABLE text, candidate text, private paths, IDs, credentials, provider exception text, or
chain-of-thought in tracked output or default terminal diagnostics.

### 6. Synthetic Vertex Gate

Before another private judge attempt:

1. Run one synthetic case for each of the four tasks through the real
   `vertex_ai/gemini-2.5-flash` LiteLLM route.
2. Use synthetic source, reference, candidate output, and evidence IDs only.
3. Require four accepted `JudgeResult` values with exact task dimensions.
4. Rerun and prove cache/resume behavior without another remote call where the harness supports it.
5. Record only aggregate pass/fail, model route, schema versions, and privacy-safe usage/latency.

The owner has authorized these synthetic Vertex calls for compatibility validation. ADC and
project/location remain external environment state. Do not add an API-key fallback.

### 7. Existing Six-Case Private Success Gate

Only after the synthetic Vertex gate passes:

1. Reuse the existing verified candidate package. Do not regenerate Llama outputs.
2. Reuse the complete accepted local inputs and FABLE references read-only.
3. Use a fresh unique scoring run directory dedicated to the corrected judge contract.
4. Run deterministic scoring/verification through the normal command path.
5. Run Vertex judge scoring with all three authorization flags.
6. Do not use the old direct-Gemini or first Vertex scoring directories as writable destinations.
7. Preserve all previous failure attempts and reports unchanged.
8. Verify final accounting is exactly six eligible, six completed, zero failed, two skipped.
9. Verify task-dimension means are non-empty and every accepted result has the exact rubric keys.
10. Rerun the same corrected judge command and prove all six successful results are cached with
    zero additional Vertex calls.
11. Confirm candidate package hash and deterministic metrics are unchanged from the accepted
    smoke.
12. Confirm live and frozen database hashes remain unchanged.
13. Confirm no private artifact is tracked or staged.

The owner explicitly authorizes disclosure of these same six previously authorized cases to the
configured Vertex judge for this corrected success gate. Do not expand beyond this two-conversation
scope.

## Required Tests

Use synthetic fixtures and injected clients for committed tests. At minimum cover:

1. provider schema uses only the accepted Vertex keyword allowlist;
2. deterministic provider schema generation for each task;
3. exact required score properties for every task rubric;
4. provider schema contains no unsupported defaults/constraints;
5. valid response for every task reaches `JudgeResult`;
6. missing score dimension rejected;
7. extra score dimension rejected;
8. score below 0 or above 4 rejected;
9. missing required field rejected;
10. unknown field rejected;
11. wrong field type rejected;
12. wrong status rejected;
13. wrong case/task/fingerprint rejected;
14. out-of-selection evidence rejected;
15. invalid JSON classified separately;
16. application schema failure diagnostics contain field/category only;
17. raw response/private marker never appears in stored failures or CLI output;
18. provider schema change invalidates judge cache;
19. application schema change invalidates judge cache;
20. request-construction/normalizer version change invalidates judge cache;
21. unchanged success resumes without a call;
22. unchanged failure remains cached unless explicitly retried;
23. explicit failure retry remains append-only;
24. unexpected programming error aborts without cache;
25. disabled/unauthorized/missing-ADC boundaries remain fail-closed;
26. deterministic-only scoring makes zero remote calls;
27. the two invalid candidate cases remain skipped and unjudged;
28. existing package verification and scoped matrix accounting remain unchanged;
29. Windows and Linux CI remain network/private-data independent.

Add a synthetic cross-stage regression representing six eligible and two invalid candidate cases,
and assert final judge accounting of six completed, zero failed, and two skipped.

## Required Validation

Before private calls:

```powershell
poetry env info --path
poetry install -E enrich
poetry run pytest tests/test_bench.py -q
poetry run pytest
poetry run ruff check .
poetry check
poetry run python -m bench score --help
poetry run chronicle --help
git diff --check
git status --short
git diff --cached --name-only
git ls-files ".chronicle/*" "*.db" "*.sqlite" "*.zip" "exports/*"
```

Then run the four-task synthetic Vertex gate. Only after it passes may the executor run the
six-eligible-case private success gate.

Do not print tokens, project IDs, account identifiers, private paths, case aliases, conversation or
message IDs, titles, prompts, references, candidates, raw judge responses, or rationales in the
completion report.

## Documentation

Update `docs/development-evaluation.md` to explain:

- Vertex ADC is the accepted judge route;
- no `GEMINI_API_KEY` is required;
- a synthetic exact-schema check precedes private judging;
- provider and application judge schemas are separate;
- judge cache identity includes both schema layers and request/normalizer versions;
- failed historical runs are retained;
- private retries require a fresh approved run identity or explicit append-only retry as applicable.

Update the connectivity report with an addendum describing the structured-output compatibility
finding and its final resolution. Do not overwrite or imply that the earlier sentinel connectivity
test proved judge-contract compatibility.

Do not edit the master plan or development ledger; those remain PM-owned.

## Completion Report

Write a detailed completion report at:

```text
md/handoffs/reports/WP-5.2B1.1-completion-report.md
```

The report must include:

1. status `Ready for PM validation` only if all six private judge cases succeed;
2. executive summary;
3. verified root cause;
4. provider/application schema separation;
5. provider schema/version and cache identity changes;
6. privacy-safe diagnostic design;
7. files changed;
8. synthetic unit/integration coverage;
9. real four-task synthetic Vertex evidence;
10. private success accounting: eligible/completed/failed/skipped only;
11. cache-resume evidence with zero second-run calls;
12. proof existing candidate package/deterministic metrics were unchanged;
13. proof previous failed runs were preserved;
14. live/frozen DB no-write evidence;
15. dependency/full-suite/Ruff/help/diff results;
16. Git privacy/tracking evidence;
17. known limitations;
18. requirement-by-requirement checklist;
19. final `git status --short`;
20. confirmation nothing was staged or committed.

If the synthetic Vertex gate or any private judge case still fails, report status `Partial` with
privacy-safe failure categories and stop. Do not claim completion and do not repeatedly retry.

## Delivery And Commit Ownership

The executor must:

- leave all implementation and report changes unstaged and uncommitted;
- not run `git add`, `git commit`, amend, rebase, or history-rewriting commands;
- preserve PM-owned plan, ledger, handoff, and validation-review changes;
- avoid unrelated refactors;
- provide final `git status --short`;
- return a concise delivery summary pointing to the completion report.

The PM/manager validates the implementation and report. Only the PM may commit, and only after an
explicit owner request.
