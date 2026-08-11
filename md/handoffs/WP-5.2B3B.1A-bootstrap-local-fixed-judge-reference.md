# WP-5.2B3B.1A Handoff: Local Fixed-Judge Bootstrap Reference

## Status

Authorized for execution after executor preflight.

This is a bounded learning and evidence task inside the ongoing WP-5.2B3B.1
automatic prompt-optimization work. It does not reopen BootstrapFewShot, select a
prompt, or authorize GEPA.

## Goal

Run the existing fixed Gemini Pro judge from the owner's local Windows machine
against the frozen **validation outputs** for:

1. the accepted automatic-optimization P0 baseline; and
2. the completed BootstrapFewShot attempt `0003` candidate.

The purpose is to learn whether the fixed semantic judge observes any quality
difference that is not visible in the deterministic and FABLE-backed metrics.
This is an out-of-band research comparison. It cannot override the promotion
gates already failed by the Bootstrap candidate.

## Manager Decision And Authorization

The owner explicitly authorizes this task to:

- run orchestration and scoring on the local Windows machine;
- use the existing fixed judge profile
  `vertex_ai/gemini-3.1-pro-preview` in `global` through LiteLLM and Vertex AI;
- authenticate through the owner's existing local Application Default
  Credentials and environment-based project configuration;
- disclose to that judge only the selected four-conversation validation inputs,
  the corresponding immutable P0 or Bootstrap candidate output, the applicable
  task/schema/rubric, and the existing FABLE reference for each eligible case;
- judge at most the 22 expected schema-valid outputs across the two arms, plus
  no more than the already-configured single bounded infrastructure retry per
  failed judge request;
- incur ordinary Vertex AI usage charges up to a hard ceiling of **US$10** for
  this task.

This authorization is complete. Do not ask the owner to repeat the disclosure
or ordinary-cost approval if the execution remains inside this exact boundary.

Stop before provider execution if the pre-call estimate can exceed US$10, if
the eligible count exceeds 22, or if the configured route differs from the
fixed profile above.

## Known Frozen Evidence

The executor must verify these facts from private artifacts rather than trusting
this prose as the authority:

- development split: six train conversations and four validation
  conversations;
- holdout: twenty conversations, still unopened;
- models: Qwen3.5-4B and Phi-4 Mini;
- tasks: four accepted WP-5.1.1 tasks;
- context: 8,192;
- P0 validation result: 11 valid of 32 positions;
- Bootstrap validation result: 11 valid of 32 positions;
- Bootstrap candidate ID:
  `f9322565f67ea32b2e40f782a36080c42d010411794cf3dddf09f8153e6c6ffd`;
- Bootstrap attempt `0003` is complete and append-only;
- no generated bootstrapped demonstration was accepted; the candidate contains
  four labeled demonstrations;
- Bootstrap is already ineligible for promotion because it fails context-fit
  and privacy gates;
- the phase wrapper failed after the durable result because it incorrectly
  compared historical P0 and current Bootstrap application-commit identities.

Do not edit, regenerate, reinterpret, or re-authorize these artifacts while
preparing the judge run.

## Required Comparison Scope

Evaluate exactly two arms:

| Arm | Scope | Candidate positions | Expected judge-eligible outputs |
|---|---|---:|---:|
| P0 | validation only | 32 | 11 |
| Bootstrap attempt `0003` | validation only | 32 | 11 |

The 32 positions per arm are:

- four frozen validation conversations;
- four tasks per conversation;
- two candidate models per task.

Only schema-valid candidate outputs are judge eligible. Preserve invalid outputs
as `no_valid_output` or the existing failure category; do not send them to the
judge. If verified counts differ from 32 positions or 11 eligible outputs in
either arm, stop before any provider call and report the discrepancy.

Do not read or judge:

- the six training conversations or their outputs;
- any of the twenty holdout conversations or their identities;
- unrelated Chronicle conversations;
- P1, P2, GEPA, or historical candidate arms.

## Semantic Boundary

This run is a **reference measurement**, not a promotion decision.

Regardless of judge scores:

- P0 remains the selected starting package for GEPA;
- Bootstrap remains non-deployable and non-promotable;
- the Bootstrap privacy and context failures remain authoritative;
- no judge score or rationale may enter Bootstrap or GEPA optimizer feedback;
- no prompt, demonstration, output, reference, or rubric may be changed;
- no candidate-model inference may be rerun;
- no malformed candidate or judge response may be repaired manually.

## Phase 0: Local Preflight

1. Confirm Poetry resolves to this repository's `.venv`.
2. Record the clean tracked `HEAD` and `git status --short`.
3. Confirm no RunPod resource is required or allocated for this task.
4. Confirm local ADC is valid without printing tokens or credential contents.
5. Resolve the fixed judge effective configuration and record only:
   - provider/model ID;
   - location;
   - rubric version;
   - temperature;
   - token cap;
   - reasoning policy;
   - timeout/retry policy;
   - credential mode, without credential values.
6. Verify that the private frozen inputs, references, P0 evidence, Bootstrap
   candidate, attempt `0003`, and raw terminal candidate outputs are available
   locally.

Search only known ignored evaluation roots, private backups, and the executor's
documented returned-artifact location. Do not scan unrelated user directories.

If the required candidate outputs were not copied back locally, stop and report
the exact missing artifact class. Do not allocate RunPod, rerun P0, rerun
Bootstrap, or reconstruct model outputs. A later retrieval-only operation can be
authorized separately if the retained volume still exists.

## Phase 1: Artifact And Scope Verification

Before constructing any judge prompt:

1. Validate all available manifests and SHA-256 indexes.
2. Verify P0 and Bootstrap candidate/result identities using the accepted
   application models.
3. Verify attempt `0003` is complete and that attempts `0001` and `0002` remain
   unchanged.
4. Verify the ordered validation manifest independently.
5. Verify each candidate output belongs to exactly one tuple of:
   `(arm, validation conversation, task, model)`.
6. Verify 32 terminal positions per arm and 11 schema-valid outputs per arm.
7. Verify every evidence message ID in a valid output belongs to its selected
   input.
8. Verify each FABLE reference belongs to the same validation case and task.
9. Hash and freeze the two local judge-input manifests before provider calls.
10. Record `holdout_files_opened: 0` and `training_files_opened: 0` from the
    access boundary used by this task.

The existing optimizer application-identity mismatch must not be bypassed by
weakening authority checks. This task may read the immutable artifacts directly
for a separate judge comparison, but it must not create the missing canonical
Bootstrap phase checkpoint or mutate optimizer run state.

## Phase 2: Judge-Package Construction

Use structured application models and existing benchmark/judge primitives. Do
not use ad hoc string parsing.

Construct two source-independent, ignored local judge packages or equivalent
immutable manifests that contain only the validation cases required by this
task. Bind each case to:

- arm identity;
- candidate ID and result/attempt identity;
- model ID;
- task and schema version;
- selected-input hash;
- candidate-output hash;
- FABLE-reference hash;
- fixed-judge policy identity.

The original candidate outputs must remain byte-identical. Package conversion
must not normalize or rewrite their JSON.

Prefer the existing `bench score` and `bench.judge` path. If the repository has
no safe way to adapt optimizer response evidence to the existing judge package,
the executor may create a narrowly scoped, ignored operator adapter under the
private run directory. It must use repository Pydantic models and retain its
source and hash in the private evidence bundle.

Do not make production-code changes merely to complete this optional run. If a
generic tracked bridge is genuinely required, stop before provider calls and
return a narrow patch proposal for manager review.

## Phase 3: Local Fixed-Judge Run

Run the two arms sequentially from the local machine using unique ignored judge
cache/output roots.

For every eligible output, send only the authorized material listed above.
Apply the existing rubric-v1 and strict provider/application schemas. Preserve:

- attempt number;
- completion/failure category;
- finish reason when available;
- token usage when available;
- latency;
- provider/model identity;
- schema-validation diagnostics without private text;
- scores and bounded rationale.

Allow only the configured bounded infrastructure retry. Do not perform semantic
retries, response repair, truncation, prompt changes, model substitution,
location substitution, or authentication-route substitution.

If the fixed judge model is unavailable, authentication fails, or the provider
returns an unsupported contract, preserve the first terminal evidence and stop
under the existing retry policy. Do not silently switch to Gemini Flash or a
different Pro preview.

## Phase 4: Cache-Only Proof

After both arms have terminal judge accounting:

1. rerun each arm using the existing `--judge-cache-only` boundary;
2. prove both commands exit zero;
3. prove zero additional provider calls;
4. prove judge-attempt bytes and aggregate hashes remain unchanged;
5. prove candidate, result, P0, Bootstrap attempt, frozen database, and source
   manifests remain unchanged.

If a cache-only replay fails because of an unrelated deterministic artifact,
stop and report it. Do not repeat successful judge calls.

## Required Analysis

Report the following for P0 and Bootstrap separately and side by side:

1. terminal candidate positions;
2. schema-valid and invalid counts;
3. judge eligible, completed, failed, and skipped counts;
4. fixed-judge dimension means overall, by task, and by candidate model, with
   explicit denominators;
5. judge latency and token usage totals plus p50/p95 where supported;
6. provider cost estimate and actual available usage accounting;
7. paired comparison for only the validation cases that are schema-valid in
   both arms;
8. unpaired comparison with denominators clearly disclosed;
9. whether judge evidence agrees with or contradicts the existing observation
   that Bootstrap did not improve P0;
10. caveats from the very small validation sample, invalid-output exclusion,
    same rubric, and any provider failures.

Do not collapse this into one headline score without also presenting reliability
and denominator information. Do not claim statistical significance.

## Deliverables

Write one tracked, privacy-safe completion report:

`md/handoffs/reports/WP-5.2B3B.1A-bootstrap-local-fixed-judge-reference-completion-report.md`

The report must include:

- executive summary in plain language;
- exact scope and authorization used;
- artifact provenance without private IDs or paths;
- preflight and count reconciliation;
- P0-versus-Bootstrap judge tables;
- paired and unpaired observations;
- cost and runtime evidence;
- cache-only proof;
- immutability and holdout/training non-access evidence;
- limitations;
- explicit statement that the result does not affect prompt promotion;
- remaining Bootstrap checkpoint-recovery blocker;
- exact next recommendation before GEPA;
- Git status and privacy/tracking checks.

Keep all raw prompts, selected source text, FABLE references, candidate outputs,
judge rationales, provider payloads, credentials, private paths, conversation
identities, caches, and generated packages under ignored private storage.

## Validation

At minimum:

```powershell
poetry env info --path
poetry run python -m bench score --help
poetry run ruff check .
poetry check
git diff --check
git status --short
git diff --cached --name-only
git ls-files .chronicle
```

Run focused tests only if tracked code is changed. No full suite is required for
a report-only execution with unchanged application code, but record why it was
not run.

## Stop Conditions

Stop without further provider calls if:

- either arm is not exactly 32 terminal validation positions;
- either arm is not exactly 11 judge-eligible outputs;
- required local immutable artifacts are missing;
- artifact hashes or case authority do not verify;
- train or holdout data would need to be opened;
- the judge route differs from the authorized fixed model/location/rubric;
- estimated spend can exceed US$10;
- a production-code change is required;
- a candidate output would need reconstruction or repair;
- the existing optimizer run state would need mutation;
- credentials or private values would be written to tracked or persistent
  repository files.

## Commit Boundary

The executor must leave all changes unstaged and uncommitted. The development
manager validates and commits the completion report after owner review.
