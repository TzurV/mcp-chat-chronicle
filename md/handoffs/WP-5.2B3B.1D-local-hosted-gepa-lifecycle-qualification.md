# WP-5.2B3B.1D Handoff: Local Hosted GEPA Lifecycle Qualification

## Status

Owner-authorized for execution by a **new executor task** after the manager
commits this handoff and provides a clean checkout.

## Executor Role And Commit Ownership

Act as the implementation and experiment executor. Diagnose and repair the
generic provider-error boundary, qualify the hosted model routes, and prove the
complete GEPA lifecycle locally. Work independently inside the approved scope.
Ask the owner only when interactive Google authentication is genuinely
required or a requested disclosure/model/budget boundary would change.

Do not stage, commit, amend, rebase, merge, tag, push, or rewrite history. Leave
all delivery changes unstaged and uncommitted for manager validation. The
manager owns commits.

## Required Reading

Read before changing code or opening private development artifacts:

- `md/agent-operating-notes.md`;
- `docs/public-repository-security.md`;
- `docs/windows-vertex-adc.md`;
- `docs/development-optimization.md`;
- `md/handoffs/reports/WP-5.2B3B.1C-validation-review.md`;
- `md/handoffs/reports/WP-5.2B3B.1C-gepa-pilot-and-bounded-search-completion-report.md`;
- `md/research/WP-5.2B3B.1-prompt-optimization-activity-log.md`.

## Context And Decision

Manual P1/P2 prompts reduced pooled local validity from 62/80 to 58/80.
BootstrapFewShot tied P0 at 11/32 validation-valid outputs but reduced semantic
agreement, failed context/privacy promotion gates, and was slightly worse under
the fixed judge. P0 therefore remains the only optimizer parent.

The first GEPA attempt is not a method result. Its Gemini 3.1 Pro proposer route
returned HTTP 400/model-not-found and produced zero candidate prompts. A
secondary `PicklingError` obscured the provider failure. The retained RunPod
state is preserved, but another paid remote allocation is not an appropriate
place to diagnose the lifecycle.

This work package proves the application route locally using hosted models:

- proposer: `vertex_ai/gemini-3.5-flash`;
- hosted surrogate candidate: `vertex_ai/gemini-3.5-flash-lite`;
- location: `global`;
- credentials: existing user ADC through environment/configuration, never a
  tracked key;
- optimizer feedback: deterministic contracts plus existing FABLE development
  references;
- fixed judge: excluded from this work package.

Google currently documents model IDs `gemini-3.5-flash` and
`gemini-3.5-flash-lite`; qualification must still prove that the owner's project
and the application-owned LiteLLM route can call them.

## Objective

Prove, end to end, that Chronicle can:

1. call an authorized hosted proposer through LiteLLM;
2. obtain and persist a GEPA prompt candidate;
3. run the four Chronicle tasks through a hosted surrogate candidate model;
4. evaluate outputs using deterministic contracts and FABLE references;
5. preserve provider/model/cost/usage/lineage authority;
6. inspect and resume the run without duplicate provider calls.

Complete this first with synthetic data, then with exactly one frozen optimizer-
train conversation and one frozen optimizer-validation conversation. A better
prompt is **not** required. Success means the lifecycle works and produces a
scorable candidate.

## Non-Goals And Protected Boundaries

- Do not restart, connect to, modify, stop, delete, or inspect RunPod resources.
- Do not open or modify the retained WP-5.2B3B.1C private run state.
- Do not rerun P0 or Bootstrap in their historical run.
- Do not open, enumerate, transfer, score, or inspect the twenty-conversation
  holdout.
- Do not call the fixed Gemini judge.
- Do not run a broad GEPA search or claim prompt improvement.
- Do not change task schemas, selectors, FABLE references, P0 prompts,
  generation settings, reliability metrics, or promotion policy.
- Do not repair, truncate, or manually reinterpret model outputs.
- Do not place credentials, cloud project values, private paths, source text,
  responses, FABLE content, or generated prompt candidates in tracked files.

## Gate 0: Clean Local Preflight

1. Confirm `main` is clean at the manager commit containing this handoff.
2. Run `poetry env info --path`; it must resolve to this repository's `.venv`.
3. Confirm the optimization extra and accepted DSPy/GEPA versions are present.
4. Confirm ignored private evaluation roots remain ignored and untracked.
5. Create a **new** ignored run root for B3B.1D. Never point it at C1 state.
6. Record only privacy-safe commit/config/model identities in tracked evidence.
7. Run all existing optimizer compatibility and no-call preflight checks.

Stop before any provider call if these conditions fail.

## Gate 1: Generic Provider-Failure Repair

Reproduce the escaped-error behavior without network access. Implement the
smallest generic repair so that:

- the primary LiteLLM/provider exception remains the recorded failure;
- GEPA/DSPy serialization cannot replace it with a secondary `PicklingError`;
- measured usage and latency are retained when trustworthy;
- unavailable usage retains a conservative reservation;
- append-only attempts and current pointers remain coherent;
- provider/model-not-found, authentication, permission, quota, timeout,
  invalid-request, invalid-JSON, and local serialization failures remain
  distinguishable;
- diagnostics are sanitized before persistence or display.

Add focused offline regressions for the original boundary and successful
serialization. Preserve historical artifact compatibility.

Run focused tests, full tests, Ruff, Poetry validation, CLI help/import checks,
and `git diff --check`. Do not create a manager commit checkpoint in the middle
of this bounded task unless the repair changes public package contracts or
cannot be validated independently.

## Gate 2: Hosted Route Qualification

Use the application-owned LiteLLM adapters, not direct provider SDK shortcuts.
Use synthetic prompts and schemas only.

1. Qualify `vertex_ai/gemini-3.5-flash` in `global` as proposer.
2. Qualify `vertex_ai/gemini-3.5-flash-lite` in `global` as structured-output
   candidate.
3. Verify actual model identity, finish state, schema-valid output, usage,
   latency, retry count, credential mode, and cache behavior.
4. Verify provider/model identity participates in configuration, candidate,
   result, and cache authority.

Allow at most one configured infrastructure retry per route. Do not repeat an
unchanged semantic failure.

If Gemini 3.5 Flash is unavailable but Flash-Lite qualifies, one synthetic
Flash-Lite-as-proposer probe is authorized. If it passes, use Flash-Lite for
both roles only for this lifecycle qualification and label the limitation. If
Flash-Lite itself is unavailable, stop without trying unlisted models.

## Gate 3: Synthetic GEPA Lifecycle

Using synthetic inputs/references only:

1. Freeze P0-like synthetic parent prompts and a small deterministic task set.
2. Run exactly one GEPA proposal position.
3. Require one distinct candidate prompt package.
4. Run the candidate through the hosted surrogate.
5. Produce terminal deterministic/reference-backed evaluation.
6. Persist proposal, candidate, outputs, result, usage, cost, latency, lineage,
   privacy scan, context check, and current pointers append-only.
7. Verify the package and inspect the run from a fresh process.
8. Resume/cache-check the completed run and prove zero additional provider
   calls and byte-stable accepted evidence.

If this gate fails, stop before private development access. Preserve evidence
and report the exact boundary.

## Gate 4: Two-Conversation Private Development Smoke

After Gate 3 passes, use metadata-only deterministic selection to choose:

- the first conversation in the frozen six-conversation optimizer-train list;
- the first conversation in the frozen four-conversation optimizer-validation
  list.

Do not inspect content to choose cases. Use all four accepted AI tasks, their
unchanged selectors/schemas, P0 prompts, and existing FABLE references.

Run exactly one GEPA proposal position with the hosted proposer, then evaluate
the resulting prompt package with the hosted surrogate over the bounded smoke.
The proposer may receive the selected development inputs, task prompts,
candidate traces, deterministic diagnostics, and FABLE-derived feedback needed
by GEPA. The surrogate may receive the selected inputs, candidate prompts, and
response schemas. No holdout or fixed-judge material may be sent.

Require:

- one terminal proposal;
- one distinct candidate package;
- terminal accounting for all bounded task positions;
- deterministic and FABLE-reference metrics;
- privacy and complete-request context checks;
- append-only provider/candidate evidence;
- fresh-process package verification and inspection;
- a resume/cache-only replay with zero additional calls.

Do not promote the candidate or interpret two conversations as an improvement
result. Stop after the lifecycle proof.

## Budget And Retry Limits

The owner authorizes ordinary Vertex usage for this work package with these hard
limits:

- total measured or conservatively reserved provider cost: US$25;
- total logical provider calls across qualification, synthetic lifecycle, and
  private smoke: 60;
- at most two GEPA proposal positions: one synthetic and one private;
- concurrency one;
- one bounded infrastructure retry per logical operation;
- zero semantic retries and zero output repair.

Run a pre-call capacity calculation before each gate. Stop before a call that
could exceed a limit. Report measured usage separately from conservative
reservations.

## External Disclosure Authorization

The owner authorizes:

- synthetic calls to Vertex AI Gemini 3.5 Flash and Gemini 3.5 Flash-Lite in
  `global` through LiteLLM;
- after the synthetic lifecycle passes, disclosure of exactly the selected one
  optimizer-train and one optimizer-validation conversation, their four task
  inputs/prompts/schemas, candidate traces/outputs, deterministic diagnostics,
  and required FABLE-derived feedback to those same hosted models;
- ordinary Vertex usage cost within the US$25 and call/retry limits above;
- refreshing and using existing local ADC when needed.

This authorization does not include the twenty-conversation holdout, fixed-
judge calls, RunPod activity, other models/providers/regions, credential
publication, or GitHub publication of private material. Do not ask for another
confirmation while remaining inside this exact boundary.

## Required Deliverables

Create:

- `md/handoffs/reports/WP-5.2B3B.1D-local-hosted-gepa-lifecycle-qualification-completion-report.md`;
- a privacy-safe addendum to
  `md/research/WP-5.2B3B.1-prompt-optimization-activity-log.md`;
- focused regression tests for any generic implementation repair;
- updates to `docs/development-optimization.md` only when the accepted operator
  workflow materially changes.

The completion report must distinguish:

- model qualification from GEPA optimization;
- proposer calls from surrogate candidate calls;
- synthetic from private activity;
- deterministic/FABLE scoring from fixed judging;
- measured usage/cost from conservative reservations;
- lifecycle success from prompt-quality improvement.

Include complete denominators, model identities, route/region, calls, retries,
tokens, latency, cost, cache replay, failures, privacy/context results, immutable
artifact evidence, zero holdout/fixed-judge/RunPod activity, and final Git
status. Do not include private payloads, paths, IDs, hashes, credentials, project
values, or generated prompt text.

## Acceptance Criteria

1. Provider failures retain their primary category and are not masked by
   serialization errors.
2. Both hosted routes qualify, or the explicitly allowed Flash-Lite dual-role
   fallback is proven and disclosed.
3. The synthetic GEPA lifecycle creates and evaluates one distinct candidate.
4. The two-conversation private smoke creates and evaluates one distinct
   candidate with terminal accounting.
5. Both runs verify from a fresh process and replay with zero additional calls.
6. Improvement is not required and is not claimed.
7. No RunPod/C1 state, fixed judge, or holdout content is accessed or changed.
8. All provider activity stays within the authorized disclosure, call, retry,
   and US$25 ceilings.
9. Focused/full tests, Ruff, Poetry, CLI, diff, privacy, tracking, and package
   checks pass.
10. Private artifacts remain ignored; delivery changes remain unstaged and
    uncommitted for manager validation.

## Stop Conditions

Stop and preserve evidence when:

- the primary and allowed fallback routes both fail qualification;
- the synthetic lifecycle cannot produce a candidate;
- the primary provider error cannot be retained accurately;
- private selection authority or FABLE binding cannot be proven;
- any holdout/fixed-judge/RunPod path would be touched;
- a budget, call, retry, privacy, context, schema, append-only, or authority
  boundary would be exceeded;
- continuation would require a model, provider, region, task, prompt, scoring,
  or disclosure change not authorized above.
