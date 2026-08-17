# WP-5.2B3B.1D.3 Validation Review

**Status:** Accepted after bounded rework

## Findings

### 1. Adapter fallback exception boundary is too broad

`bench/optimization/observability.py` catches every non-`LMError` exception
from `ChatAdapter` and makes a second paid call through `JSONAdapter`. This can
convert an application defect, callback defect, configuration error, or other
unexpected exception into a format fallback. It weakens the stated contract
that only adapter parse/format failure may trigger fallback and can both mask a
bug and spend an unplanned call.

Restrict fallback to DSPy's explicit adapter parse/format exception contract.
Provider errors and every unrelated exception must propagate without a second
transport. Add regressions proving an `AdapterParseError` produces exactly one
JSON fallback, while `ValueError`, `TypeError`, callback errors, and `LMError`
produce none.

### 2. Graded search scoring masks application defects

`bench/optimization/production.py` catches every exception around schema lookup
and Pydantic validation and converts it to the ordinary `schema-invalid` score
of 0.3. A bad schema identity, programming error, or unexpected application
failure would therefore be treated as model output quality and GEPA would keep
searching.

Catch only the expected Pydantic/model-output validation exception. Schema
lookup failures and unrelated exceptions must fail the optimizer operation.
Add regressions proving malformed model output receives 0.3 while an unknown
schema or injected application exception propagates and creates no proposal
decision or additional call.

## Accepted direction

The remaining design is suitable for the intended experiment:

- append-only private proposal envelopes and separate decisions;
- exact transport/fallback evidence;
- versioned GEPA-only graded reliability scores;
- unchanged strict final promotion;
- historical v1 identity compatibility; and
- a complete 6/4 development experiment with three-to-five proposals.

The 540 cumulative-call figure remains planning evidence only and is not
authorized.

## Required validation

After the two bounded corrections, rerun the new observability regressions,
the complete optimizer suite, full repository suite, Ruff, Poetry validation,
CLI/import checks, privacy scans, and `git diff --check`. Leave all changes
unstaged and uncommitted for repeat manager validation. Make no provider or
private-data call.

## Rework acceptance

The bounded rework satisfies both findings:

- only DSPy's `AdapterParseError` triggers one JSON-adapter fallback;
- LM, value, type, callback, configuration, and unexpected exceptions make no
  fallback call and propagate;
- only Pydantic `ValidationError` receives the schema-invalid search score;
  unknown schemas and application defects propagate; and
- regressions prove no proposal decision or extra call is created at either
  unexpected-error boundary.

Manager validation of the final tree passed:

- observability and complete optimizer matrix: 178 passed;
- Ruff: passed;
- Poetry validation: passed;
- `git diff --check`: passed.

The executor's final full-suite result was 658 passed with one expected skip.
No provider, credential, private-data, judge, RunPod, or local-model activity
occurred. D.3 is accepted for commit. The 540-call planning ceiling remains
unauthorized.
