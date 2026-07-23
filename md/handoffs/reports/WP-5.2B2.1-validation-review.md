# WP-5.2B2.1 Validation Review

## Final PM decision

**Accepted on 2026-07-23 after fixed-route recovery.**

Final PM validation confirms:

- 120/120 candidate positions are terminal with zero unaccounted;
- Phi completed 26/26 eligible judge cases;
- Llama 3B completed 26/26 eligible judge cases;
- Gemma 3 completed 22/23 eligible judge cases and retained one honest terminal invalid-JSON
  judge failure after the authorized bounded retry;
- final judge accounting is 74 completed, one failed, and 45 skipped invalid;
- the three cache-only replays exited zero with zero provider calls and byte-identical evidence;
- all required confusion, per-label, judge, latency, usage, runtime, and provenance aggregates are
  present in the tracked report;
- candidate, historical, frozen-database, and live-database evidence remained unchanged;
- no 120-case arm started and no private artifact is tracked;
- Poetry resolves to the repository `.venv`, `git diff --check` passes, and nothing is staged.

The fixed judge contract was not changed. Synthetic diagnosis established that absent local Vertex
location aliases prevented the application route from using `global`; setting the required aliases
restored the exact accepted Vertex/model/region/ADC route.

### Complete-arm admission

- **Phi-4 Mini: admit to the 120-case development arm.**
- **Llama 3.2 3B: admit to the 120-case development arm.**
- **Gemma 3 4B: admit as a research comparator, not as a product-quality candidate.**

Gemma's 57.5% checkpoint validity is poor, but its valid outputs contain useful semantic evidence,
the measured additional runtime is manageable, and completing it preserves the planned five-local-
model article dataset. Its complete run must retain every failure and must not be described as an
endorsement.

No repository test suite was rerun during PM validation because the accepted delivery contains
reporting and private evaluation artifacts only; no tracked application or harness code changed.

## Initial review status (superseded)

**Candidate checkpoint complete; rework required before overall PM acceptance.**

The local-generation and deterministic-scoring portions are provisionally accepted:

- all three arms used the accepted frozen first-10 scope;
- all 120 candidate positions are terminal with zero unaccounted;
- the three packages verify and score deterministically;
- model-quality failures remain visible and unrepaired;
- no 120-case arm started;
- live, frozen, and historical artifacts remained unchanged;
- no private artifact is tracked.

The work package is not yet accepted because its fixed-judge semantic gate produced zero successful
scores. A cached `provider_model_not_found` result proves reproducibility of the provider failure;
it does not satisfy the intended semantic comparison.

Do not regenerate any candidate output. Do not begin a 120-case candidate arm.

## Findings

### 1. Blocking: no semantic checkpoint was completed

All 75 schema-valid candidate outputs have terminal judge failures:

| Candidate | Eligible | Judge completed | Judge failed |
|---|---:|---:|---:|
| Phi-4 Mini | 26 | 0 | 26 |
| Llama 3.2 3B | 26 | 0 | 26 |
| Gemma 3 4B | 23 | 0 | 23 |
| **Total** | **75** | **0** | **75** |

Consequences:

- no judge dimension means exist;
- semantic comparison with the accepted historical arms is unavailable;
- Phi and Llama 3B cannot be admitted to complete 120-case runs yet;
- Gemma 3's current negative recommendation may be retained as a reliability observation, but it
  is not a complete semantic admission decision.

The executor correctly did not substitute a model, provider, region, authentication route, or
rubric.

### 2. Required report evidence is incomplete

The handoff required publishable aggregate evidence in the tracked completion report. Section 12
currently says the complete confusion matrices and per-label metrics are retained privately. That
does not satisfy the handoff.

Add the following privacy-safe aggregate evidence directly to the completion report:

- full work-mode confusion matrix for each candidate;
- full last-activity confusion matrix for each candidate;
- full title-fit confusion matrix for each candidate;
- exact agreement and per-label precision, recall, and support;
- `no_valid_output` rows or columns where applicable;
- observed wall span per arm;
- summed candidate latency per arm;
- overall and per-task p50/p95 latency;
- exact per-task usage availability and token totals;
- privacy-safe CPU, RAM, graphics, model, quantization, runtime/engine, context, and parallelism
  provenance.

Do not include private identifiers, paths, hashes, source text, model output, references, or judge
rationales.

## Rework objective

Determine why the accepted fixed judge route returns `provider_model_not_found`, without changing
the comparison contract or disclosing private evaluation content during diagnosis.

If the identical fixed judge route is restored, resume judging only the existing 75 eligible
candidate outputs under a separately confirmed recovery-call authorization. Preserve all failed
attempts and candidate packages.

## Stage 1 - Report-only completion

1. Read the private aggregate artifacts without modifying them.
2. Add every missing aggregate listed in finding 2 to the existing completion report.
3. Recompute nothing that could mutate a candidate package.
4. Record any metric that cannot be reproduced as unavailable, with the exact privacy-safe reason.
5. Do not make any model or provider call in this stage.

## Stage 2 - Synthetic fixed-route diagnosis

Use synthetic, non-private content only.

Preserve exactly:

- provider: Vertex AI;
- model: `gemini-3.1-pro-preview`;
- location: `global`;
- authentication: ADC;
- rubric version: 1;
- temperature: 0;
- maximum output tokens: 1,000;
- reasoning policy: `none`;
- application-owned judge schema.

Run a bounded diagnostic sequence:

1. Verify ADC is usable without printing credentials, tokens, project identity, or account identity.
2. Verify the configured project and location variables are present without printing their values.
3. Check model availability using the official Vertex AI surface available to this environment.
4. Send one minimal synthetic structured-output request through the official Vertex AI
   SDK or REST route.
5. Send the equivalent synthetic request through LiteLLM.
6. Compare only privacy-safe provider/error classifications.
7. If a request succeeds, run one synthetic application-owned judge request.

The goal is to distinguish:

- model unavailable to the configured Vertex project;
- incorrect Vertex model/location routing;
- ADC or project configuration failure mislabeled as model-not-found;
- LiteLLM provider/model mapping failure;
- temporary preview-model availability failure.

Do not use the Gemini Developer API, an API key, a different project, another region, a model alias,
or a substitute judge in this diagnostic.

Limit this stage to the minimum calls above and at most two focused diagnostic/fix cycles. Generic
tracked code fixes require synthetic regression coverage and manager review before private
execution resumes.

## Stage 3 - Decision boundary

### If the exact fixed route remains unavailable

Stop and report the diagnosis. Do not:

- retry private judge cases;
- substitute Gemini 2.5 Flash, Gemini 3.5 Pro, another preview alias, or another judge;
- switch from Vertex AI to the Gemini Developer API;
- change region, authentication route, rubric, schema, or reasoning policy;
- make a 120-case admission recommendation based on absent semantic evidence.

The PM/owner will choose whether to restore access, defer semantic judging, or authorize a
judge-migration work package. A judge migration must rejudge the comparison packages needed for a
common scoring window.

### If the exact fixed route is restored

Stop after synthetic proof and request/confirm one recovery authorization covering:

- the same 75 existing eligible cases only;
- the same selected source, candidate outputs, and FABLE references;
- Vertex AI `gemini-3.1-pro-preview` in `global`;
- ADC and rubric v1;
- one new baseline recovery attempt per eligible case plus only the configured bounded retry;
- ordinary Vertex usage cost.

Do not interpret the original authorization as permitting unlimited retry waves. After the
recovery authorization:

1. append new judge attempts; never overwrite the failed attempts;
2. judge only the existing eligible outputs;
3. require `completed + failed = eligible` for each arm;
4. run a cache-only replay for each arm;
5. prove zero provider calls and unchanged package/attempt identities on replay;
6. add task-level judge dimensions, denominators, failure accounting, and run-window limitation to
   the completion report.

## Validation

When only Markdown changes are made:

```powershell
poetry env info --path
git diff --check
git diff --cached --name-only
git status --short
```

When tracked code changes are required, also run:

```powershell
poetry run pytest tests/test_ai_adapter.py tests/test_bench.py -q
poetry run pytest
poetry run ruff check .
poetry check
```

Also prove:

- all original candidate-package and candidate-attempt hashes are unchanged;
- frozen/live databases and historical accepted packages are unchanged;
- no private artifact or credential is tracked;
- no 120-case arm started;
- all executor delivery remains unstaged and uncommitted.

## Completion-report update

Update the existing file:

`md/handoffs/reports/WP-5.2B2.1-completion-report.md`

Add a dated rework addendum covering:

1. report metric completion;
2. synthetic diagnostic commands and privacy-safe outcomes;
3. root-cause classification and confidence;
4. whether the identical fixed route was restored;
5. private recovery authorization, if used;
6. final judge accounting and semantic metrics, if recovered;
7. cache-only proof, if recovered;
8. immutability, privacy, validation, and Git status.

Do not create a replacement completion report.

## Acceptance after rework

Overall WP-5.2B2.1 may be marked `Ready for PM validation` only when either:

1. the exact fixed judge route is restored and all eligible cases have terminal outcomes with
   successful semantic scores reported where available; or
2. the PM explicitly narrows/changes the work-package acceptance boundary after reviewing a
   conclusive provider-availability diagnosis.

The executor must leave all changes unstaged and uncommitted. Commit ownership remains with the
PM/manager after validation and an explicit owner request.
