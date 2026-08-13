# WP-5.2B3B.1D.1: Gemini 2.5 Flash-Lite Private GEPA Lifecycle

## Status

Ready for execution by the existing WP-5.2B3B.1D executor after the manager
commits this handoff and the accepted offline repair.

## Executor Working Mode

Continue in the existing executor task because it already holds the relevant
DSPy/GEPA, provider-accounting, and B3B.1D context. Work autonomously inside the
authorization below. Ask the owner only if an authentication action genuinely
requires interactive input or a requested action would cross a stated model,
data, cost, call, or privacy boundary.

Do not stage, commit, amend, merge, rebase, tag, push, or rewrite history. The
manager owns commits. Leave delivery changes unstaged and uncommitted.

## Required Reading

Read before opening private development artifacts or making a provider call:

- `md/agent-operating-notes.md`;
- `docs/public-repository-security.md`;
- `docs/windows-vertex-adc.md`;
- `docs/development-optimization.md`;
- `md/handoffs/WP-5.2B3B.1D-local-hosted-gepa-lifecycle-qualification.md`;
- `md/handoffs/reports/WP-5.2B3B.1D-validation-review.md`;
- `md/handoffs/reports/WP-5.2B3B.1D-local-hosted-gepa-lifecycle-qualification-completion-report.md`;
- `md/research/WP-5.2B3B.1-prompt-optimization-activity-log.md`.

## Background

WP-5.2B3B.1D qualified the hosted Vertex routes and repaired generic provider
failure propagation, DSPy serialization, GEPA component/minibatch alignment,
bounded proposal controls, and call accounting. A network-free synthetic proof
now passes through tracked `run_optimization` orchestration and the production
DSPy GEPA adapter.

The previous private attempt used Gemini 3.5 Flash-Lite as a hosted surrogate,
stopped before proposal because its mixed-task minibatch did not contain the
round-robin-selected component, and remains append-only. It is not a prompt
quality result. The manager accepted the offline repair but kept the private
lifecycle acceptance criterion open.

The owner has now selected Gemini 2.5 Flash-Lite as the single hosted candidate
model replacing the small local LLMs for this bounded learning exercise. This
is a deliberate model change and must use a new ignored run root and new model,
configuration, cache, authorization, and result identities. Do not rewrite or
reinterpret earlier B3B.1D evidence.

## Objective

Prove that Chronicle can optimize a real, private, cloud-hosted candidate model
end to end on the existing two-conversation development smoke:

1. qualify Gemini 2.5 Flash-Lite through the application-owned Vertex/LiteLLM
   route;
2. generate a P0 baseline with that model under an 8,192-token complete-request
   limit;
3. run one local GEPA proposal using Gemini 3.5 Flash as proposer;
4. evaluate the distinct tuned prompt with Gemini 2.5 Flash-Lite;
5. compare P0 and tuned results against the same frozen FABLE references;
6. verify all accepted artifacts from a fresh process and prove zero-call
   replay.

Improvement is not required. Lifecycle completion and honest paired evidence
are the goals.

## Fixed Model Roles

### Candidate model

- LiteLLM model: `vertex_ai/gemini-2.5-flash-lite`
- Route: Vertex AI
- Location: `global`
- Credential mode: local user ADC, following `docs/windows-vertex-adc.md`
- Context policy: application-enforced complete request maximum of 8,192 tokens
- Concurrency: one
- Candidate count: one
- Reasoning/thinking: disabled; fail closed if the route cannot honor the
  accepted no-reasoning setting
- Structured output: required

Gemini 2.5 Flash-Lite is the candidate being measured. Do not label its output
as Qwen or Phi and do not reuse a local-model cache identity.

### GEPA proposer

- LiteLLM model: `vertex_ai/gemini-3.5-flash`
- Route: Vertex AI
- Location: `global`
- Credential mode: the same process-scoped local user ADC
- Concurrency: one
- Exactly one proposal position

The proposer suggests prompt text only. It is not the candidate, reference,
fixed judge, or final scorer.

### References and scoring

The existing FABLE references remain the frozen development answer key. Do not
generate new references from Gemini 2.5 Flash-Lite. The phrase "new baseline"
means new P0 candidate outputs from Gemini 2.5 Flash-Lite, not a new reference
corpus.

Use the unchanged task schemas, selectors, P0 prompts, deterministic contracts,
FABLE reference scoring, privacy rules, and promotion policy. The fixed Gemini
judge is outside this work package and must not be called.

## Frozen Private Scope

Use metadata-only deterministic selection:

- first conversation in the frozen six-conversation optimizer-train manifest;
- first conversation in the frozen four-conversation optimizer-validation
  manifest;
- all four accepted AI tasks;
- one candidate model, Gemini 2.5 Flash-Lite.

This produces eight logical baseline positions and eight logical tuned-candidate
positions. Do not inspect content to choose cases. Do not open, enumerate,
transfer, score, or otherwise access the twenty-conversation holdout.

## Cumulative Authorization And Budget

The owner explicitly authorizes this exact work package:

- disclosure of the selected train and validation inputs, four task prompts and
  schemas, candidate traces/outputs, deterministic diagnostics, and necessary
  FABLE-derived feedback to the two fixed Vertex models above;
- one synthetic Gemini 2.5 Flash-Lite qualification call;
- one bounded private P0 baseline and one GEPA candidate lifecycle;
- ordinary Vertex usage up to a cumulative B3B.1D ceiling of **80 logical
  provider calls** and **US$35**;
- one bounded infrastructure retry per logical operation;
- zero semantic retries and zero output repair;
- refreshing and using existing local user ADC when needed.

Existing B3B.1D accounting is authoritative and must be carried forward:

- observed logical provider calls: 32;
- conservatively charged calls: 44;
- partial measured cost: US$0.0245726;
- conservative reservation: US$5.82768.

Before every provider boundary, calculate capacity against the cumulative
ceilings. Measured values and conservative reservations must remain separate.
Do not make a call that could exceed either ceiling.

This authorization is complete. Do not ask the owner to reconfirm private
disclosure or ordinary cost while remaining inside these exact boundaries.

## Prohibited Activity

- No RunPod allocation, connection, restart, stop, deletion, or retained-volume
  access.
- No access to historical C1 state beyond the tracked privacy-safe reports.
- No fixed-judge call.
- No holdout access.
- No Qwen, Phi, LM Studio, Gemini 3.5 Flash-Lite candidate, fallback model,
  alternate provider, alternate region, or model substitution.
- No new reference generation.
- No task/schema/selector/P0/reference/promotion-policy change.
- No output repair, truncation, manual reinterpretation, or semantic retry.
- No credential, project ID, private path, source text, FABLE content, response,
  generated prompt, or private identifier in tracked files.

## Gate 0: Clean Preflight

1. Confirm `main` is clean at the manager commit containing this handoff and the
   accepted offline repair.
2. Confirm Poetry resolves to the repository `.venv`.
3. Confirm DSPy 3.3.0, GEPA 0.1.1, LiteLLM, and the optimization extra.
4. Confirm all private roots are ignored and `.chronicle` has no tracked files.
5. Create a new ignored D.1 run root. Never modify the prior B3B.1D root.
6. Freeze privacy-safe configuration identity, exact models, region, 8K context
   policy, references, selected scope, cumulative accounting, and clean commit.
7. Confirm no holdout, RunPod, fixed-judge, or historical-run path is configured.

Stop before provider activity if any condition fails.

## Gate 1: Gemini 2.5 Flash-Lite Qualification

Run exactly one synthetic structured-output request through the application-owned
LiteLLM route. Prove:

- resolved and actual model identity;
- `global` route;
- no-reasoning policy;
- schema-valid output;
- finish status when exposed;
- measured calls, retries, tokens, latency, and cost;
- sanitized failure category if unsuccessful.

No unchanged retry is permitted unless the first failure is an explicitly
authorized infrastructure retry. Stop if qualification fails. Do not substitute
a different model.

## Gate 2: Private P0 Baseline

Using the frozen scope and unchanged P0 prompts:

1. Generate all eight logical Gemini 2.5 Flash-Lite baseline positions.
2. Enforce the 8,192-token complete-request limit before each call.
3. Preserve terminal schema, evidence, context, and provider failures exactly.
4. Persist ordinary Chronicle candidate/result/trial/accounting artifacts.
5. Score terminal outputs with deterministic contracts and frozen FABLE
   references.
6. Record reliability by task plus aggregate calls, retries, tokens, latency,
   and cost.

P0 is the parent for Gate 3 regardless of its score. Do not tune or regenerate
references based on its output.

## Gate 3: One GEPA Proposal

Run tracked `run_optimization` locally through the production DSPy GEPA adapter:

- train limit: one frozen train conversation;
- validation limit: one frozen validation conversation;
- proposal limit: one;
- proposer: Gemini 3.5 Flash;
- candidate evaluator: Gemini 2.5 Flash-Lite;
- component selection: accepted trace-aligned policy;
- format-failure feedback: accepted sanitized exclusion policy;
- P0 parent: Gate 2 baseline prompt package.

Require one terminal proposal and one distinct prompt package. Preserve
provider failures and incomplete usage conservatively. Stop without a semantic
retry if GEPA produces no distinct candidate.

## Gate 4: Tuned Candidate Evaluation

Evaluate the distinct prompt package over the same eight logical positions.
Persist terminal outputs and calculate the same deterministic/FABLE metrics as
P0. Produce a paired P0-versus-tuned comparison by task and overall, including:

- schema-valid and usable counts;
- failure categories;
- deterministic contract validity;
- FABLE-reference agreement;
- context eligibility;
- privacy eligibility;
- calls, retries, input/output/reasoning tokens, latency, and cost.

Do not claim statistical significance or general prompt improvement from this
two-conversation smoke. A worse or equal candidate is still a valid lifecycle
result.

## Gate 5: Verification And Replay

1. Verify P0 and tuned packages from a fresh process.
2. Inspect normal run state, lineage, current pointers, trials, results, privacy,
   context, and budget evidence.
3. Replay/cache-check the completed run.
4. Prove zero additional provider calls and byte-stable accepted artifacts.
5. Clear process-scoped Vertex environment values after execution; never delete
   the owner's ADC files.

## Required Deliverables

Create or update:

- `md/handoffs/reports/WP-5.2B3B.1D.1-gemini-2.5-flash-lite-private-lifecycle-completion-report.md`;
- `md/research/WP-5.2B3B.1-prompt-optimization-activity-log.md`;
- `md/development-ledger.md` only to report execution status, without rewriting
  manager decisions;
- focused tests for any additional generic repair required by this exact route.

The completion report must clearly separate:

- qualification, baseline generation, GEPA proposal, and tuned evaluation;
- candidate and proposer models;
- measured usage from conservative reservations;
- lifecycle success from prompt-quality outcome;
- P0 outputs from unchanged FABLE references;
- private development scope from untouched holdout scope.

Do not include private payloads, prompt candidates, FABLE content, credentials,
project identifiers, private paths, private hashes, or source identifiers.

## Acceptance Criteria

1. Gemini 2.5 Flash-Lite qualifies through Vertex/LiteLLM in `global`.
2. Eight P0 baseline positions are terminal and accounted for.
3. GEPA produces one terminal proposal and one distinct candidate.
4. Eight tuned-candidate positions are terminal and accounted for.
5. Both arms use the same frozen inputs, tasks, schemas, and FABLE references.
6. Both packages verify from a fresh process.
7. Replay makes zero provider calls and accepted artifacts remain byte-stable.
8. Complete paired reliability/reference metrics and model/call/retry/token/
   latency/cost evidence are reported.
9. Cumulative activity stays within 80 calls and US$35.
10. No fixed judge, holdout, RunPod, local model, fallback model, or historical
    private run is accessed or changed.
11. Focused/full tests, Ruff, Poetry, CLI, diff, privacy, tracking, and package
    checks pass.
12. Everything remains unstaged and uncommitted for manager validation.

## Mandatory Stop Conditions

Stop, preserve append-only evidence, and report when:

- Gemini 2.5 Flash-Lite cannot qualify exactly as configured;
- the 8K request boundary cannot be enforced;
- frozen scope/reference authority cannot be proven;
- the cumulative call or cost ceiling cannot accommodate the next operation;
- a provider/model/region/credential boundary would change;
- GEPA produces no distinct candidate;
- replay would require a provider call;
- holdout, fixed-judge, RunPod, historical private state, or tracked-private-data
  boundaries would be crossed.

