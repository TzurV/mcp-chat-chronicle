# WP-5.2B1.2 - Gemini Candidate and Pro-Judge Eight-Case Comparison

## Status

Rework required after initial completion report. Continue in the same executor chat and update the
existing completion report. Do not create a new work package.

## PM Rework Addendum - Judge Sensitivity, Documentation, and README

This addendum supersedes the initial delivery boundary where it conflicts with later instructions.
The implementation and both primary arms are retained. Do not regenerate either candidate package.

### Owner decisions

The owner has decided:

- `vertex_ai/gemini-3.1-pro-preview` is the single primary judge for candidate comparisons;
- the current primary judge prompt, task rubrics, provider schema, application validation, and
  scoring anchors remain fixed for this eight-case comparison;
- `vertex_ai/gemini-2.5-flash` will additionally judge Arm B as a diagnostic judge-sensitivity
  exercise;
- the existing Gemini 2.5 Flash results for Arm A may be reused;
- the same eight frozen cases remain the complete scope;
- the owner authorizes disclosure of Arm B's same eight selected source/reference/candidate cases
  to the already configured Vertex Gemini 2.5 Flash judge;
- repository documentation must describe the generic hosted-candidate benchmark path before PM
  acceptance;
- the executor leaves changes unstaged and uncommitted; the manager commits after validation and
  explicit owner instruction.

### Judge prompt decision

Do not modify the judge prompt or rubric in this rework.

The current observations show judge sensitivity, but they do not prove that either judge is
correct. There is no human ground truth in this development set, and six/eight cases are too few to
calibrate a new prompt safely. A prompt change now would make the existing Pro results incomparable.

Keep the current primary judge contract pinned as rubric version `1`. If a later review changes any
judge instruction, rubric dimension, score anchor, provider schema semantics, evidence policy, or
output interpretation:

1. create a new rubric/prompt version;
2. change judge cache identity;
3. rerun every candidate being compared under that same new version;
4. never combine scores from the old and new versions.

Add a planning note to the completion report: before the 120-case run, the owner should decide
whether to retain rubric v1 or schedule a separate judge-calibration package. Do not implement that
future package here.

### Primary judge reproducibility limitation

Record clearly that `gemini-3.1-pro-preview` is a preview alias. A fixed YAML model ID and rubric
do not guarantee immutable provider weights over time. Preserve:

- exact logical model ID;
- LiteLLM version;
- judge profile/config hash;
- rubric/provider/application contract versions;
- UTC run window;
- region;
- generation settings;
- response usage/finish metadata already allowed by the privacy policy.

Do not include project/account identity. Recommend running future candidate comparisons within a
bounded time window or repeating a fixed anchor package if the preview endpoint changes.

### Rework 1 - Correct README preservation

The initial report says the owner-modified `README.md` was preserved, but the worktree diff reverses
the accepted README changes from commit `d0736cc`. This must be corrected.

Restore the README content from the accepted baseline and retain these accepted sections:

- `scan-local` and `stats` in **Start searching in 5 minutes**;
- current post-v0.1.0 project status;
- initial four AI-task descriptions;
- **Development evaluation harness (optional)**;
- cached judge evaluation instructions;
- removal of the stray duplicate `Start searching in 5 minutes` text near **Limitations**.

Do not use a destructive whole-worktree restore. Reconcile only `README.md` against commit
`d0736cc`, then add only the hosted-candidate documentation required below.

Update the completion report's file/change statement so it accurately describes the final README
diff.

### Rework 2 - Document the hosted benchmark path

Update `docs/development-evaluation.md` and, where concise and appropriate, the README evaluation
section. Document:

- local-artifact versus hosted-API candidate provenance;
- that hosted candidates omit GGUF/artifact/quantization/device fields instead of using fake values;
- the model-profile YAML shape for a generic hosted candidate;
- the evaluation candidate YAML shape for `execution: hosted-api`;
- `bench generate --allow-remote --confirm-private-eval`;
- what private data hosted generation discloses;
- that both authorization flags are required before bundle reads/provider calls;
- independent candidate and judge identities/caches;
- unique paths/run IDs for each candidate and judge configuration;
- package verification and deterministic scoring after generation;
- cache-only judge replay and its zero-call guarantee;
- the fact that changing a judge does not require candidate regeneration;
- the fact that changing a candidate does require a new bundle/package identity;
- the preview-model drift limitation and required provenance.

Use provider-generic examples in tracked documentation. Do not include private paths, project IDs,
credentials, corpus IDs tied to private content, real case fingerprints, private package names, or
raw results.

No new standalone experiment script is required. The reusable implementation belongs in `bench/`.
Add a future note that a `bench compare` command should be considered before the 120-case/model
matrix; do not implement it in this rework unless a concrete defect makes it necessary.

### Rework 3 - Judge Arm B with Gemini 2.5 Flash

Reuse the immutable Arm B Gemini 3.5 Flash candidate package. Do not regenerate candidate outputs.

Create a new ignored scoring directory and judge cache for:

```text
candidate: vertex_ai/gemini-3.5-flash
diagnostic judge: vertex_ai/gemini-2.5-flash
scope: frozen-prefix-v1, conversation-limit=2, eight cases
```

Use the same Gemini 2.5 Flash judge contract/profile policy as the accepted earlier Arm A run where
possible. Record any unavoidable settings difference. In particular:

- keep rubric version, dimensions, anchors, evidence rules, provider schema, and application
  validation unchanged;
- keep candidate identity blinded;
- do not change task prompts, FABLE references, candidate results, or selectors;
- retain the existing 500-token policy if all eight diagnostic judge responses complete cleanly;
- if a response ends because of the token cap, stop and report before changing the cap;
- do not silently adopt the Pro judge's 1,000-token cap and call the result equivalent;
- do not retry a semantic score merely because it differs from Pro.

Required accounting:

```text
eligible: 8
completed: 8
failed: 0
skipped invalid: 0
```

After the successful run, repeat with `--judge-cache-only` and prove:

- exit code zero;
- zero provider calls;
- eight attempt files unchanged;
- attempt aggregate identity unchanged;
- reports contain one coherent judge section;
- candidate package and all other scoring directories unchanged.

If provider/config/harness defects prevent completion, apply the original bounded bug policy. Do
not treat score disagreement as a defect.

### Rework 4 - Build a judge-sensitivity comparison

Update the existing completion report with a clearly separate **Judge sensitivity** section. It is
not the primary candidate comparison and must not alter the primary Pro-judged Arm A/Arm B table.

Use this 2 x 2 evidence matrix:

| Candidate | Gemini 2.5 Flash judge | Gemini 3.1 Pro judge |
| --- | --- | --- |
| Llama 3.2 1B | Reuse accepted earlier run | Reuse WP-5.2B1.2 Arm A |
| Gemini 3.5 Flash | New diagnostic run | Reuse WP-5.2B1.2 Arm B |

For each candidate/judge cell report, without private case data:

- eligible/completed/failed/skipped counts;
- judge schema-valid rate;
- finish categories and retry count;
- judge latency p50/p95 and total wall time when available;
- prompt/completion/reasoning/total token usage when available;
- dimension means grouped by task;
- exact per-dimension score agreement between judges;
- mean absolute score difference between judges;
- count of dimensions where 2.5 is higher, equal, or lower than Pro;
- whether candidate ordering changes under the diagnostic judge;
- generation-setting differences, especially 500 versus 1,000 output tokens.

Do not present judge agreement as correctness. Explain:

- deterministic candidate metrics are judge-independent;
- primary candidate conclusions use Gemini 3.1 Pro consistently for both arms;
- Gemini 2.5 Flash is diagnostic sensitivity evidence only;
- without human adjudication, disagreement cannot establish which judge is correct;
- two conversations cannot establish judge stability or statistical significance.

### Rework 5 - Validation and completion report refresh

Run:

```powershell
poetry env info --path
poetry run pytest <focused benchmark/config tests> -q
poetry run pytest
poetry run ruff check .
poetry check
poetry run python -m bench generate --help
poetry run python -m bench score --help
poetry run chronicle --help
git diff --check
git diff --cached --name-only
git status --short
```

Confirm:

- README retains the accepted `d0736cc` content plus intentional hosted-candidate additions;
- tracked docs contain no private values;
- Arm A and Arm B candidate packages are byte-identical to the initial delivery;
- accepted Gemini 2.5 Arm A and Gemini 3.1 Pro Arm A/Arm B attempts remain unchanged;
- the new Gemini 2.5 Arm B cache-only rerun makes zero calls;
- live and frozen databases remain unchanged;
- no `.chronicle`, DB, ZIP, private config, package, attempt, raw output, reference, token,
  credential, project ID, or private path is tracked;
- all changes remain unstaged and uncommitted.

Refresh the existing report only:

```text
md/handoffs/reports/WP-5.2B1.2-completion-report.md
```

Add:

- a rework addendum;
- corrected files-changed section;
- README/documentation evidence;
- new Gemini 2.5 Flash Arm B accounting and cache proof;
- the 2 x 2 judge-sensitivity matrix and interpretation;
- primary-judge/rubric freeze decision;
- preview drift limitation;
- updated validation and privacy evidence;
- updated acceptance checklist.

Status may return to **Ready for PM validation** only when the new diagnostic run is 8/0/0, its
cache-only rerun proves zero calls, README/docs are correct, and all local validation is green.

## Purpose

Use the exact accepted two-conversation, eight-case frozen prefix to answer two questions:

1. How easily can the evaluation harness replace the local Llama 3.2 1B candidate with a hosted
   Vertex Gemini candidate?
2. How do candidate reliability, latency, token use, deterministic agreement, and semantic scores
   compare on the same eight cases?

This is a bounded development smoke, not a publication-grade benchmark. Do not expand to the full
30-conversation/120-case corpus in this work package.

## Requested Models and Mandatory Clarification

The owner requested:

- candidate: `vertex_ai/gemini-3.5-flash`;
- judge: `vertex_ai/gemini-3.5-pro`.

Google's public Vertex documentation identifies `gemini-3.5-flash` as a current model ID. At the
time this handoff was written, no public `gemini-3.5-pro` model ID was found. Google's documented
current Pro endpoint is `gemini-3.1-pro-preview`, available in `global`.

Do not silently replace the requested judge. Start by giving the owner a short model-availability
preflight and wait for the owner's response. The owner must explicitly select one of these:

- a verified account-visible `vertex_ai/gemini-3.5-pro` endpoint; or
- the documented `vertex_ai/gemini-3.1-pro-preview` endpoint.

Record the exact resolved judge model in private run provenance and the privacy-safe completion
report. Do not use a fallback model after a failed call without owner approval.

Official references used by the manager:

- `https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-5-flash`
- `https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-pro`

## Baseline

Repository baseline:

- accepted commit: `d0736cc` or a later owner-approved commit containing it;
- accepted corpus: private `dev-v1` frozen corpus;
- accepted scope: `conversation-limit=2`, frozen-prefix-v1;
- expected case count: eight, four tasks for each of two conversations;
- existing candidate: Llama 3.2 1B `Q4_K_M` through LM Studio;
- existing Llama package: preserve it byte-for-byte;
- existing judge results from Gemini 2.5 Flash: preserve as history, but do not use them as the
  comparison score when the new Pro judge is selected.

The four tasks are:

1. `conversation-summary`;
2. `work-mode-classification`;
3. `last-activity`;
4. `title-assessment`.

The existing Llama package accounts for eight attempts: six schema-valid and two invalid. The two
invalid outputs remain valid evaluation evidence and must not be repaired or removed.

## Required Experiment Arms

### Arm A - Existing Llama Candidate, New Pro Judge

- Reuse the existing immutable Llama candidate package.
- Verify it against the accepted frozen corpus and exact eight-case scope.
- Recompute deterministic metrics locally.
- Judge its six eligible outputs with the newly selected Pro judge.
- Keep the two invalid outputs visibly skipped from semantic judging.
- Write to a new scoring directory. Never overwrite the accepted Gemini 2.5 Flash judge run.
- Rerun with `--judge-cache-only` and prove zero additional provider calls.

Expected accounting unless package verification reveals corruption:

```text
candidate cases: 8
schema-valid / judge-eligible: 6
schema-invalid: 2
Pro judge completed: 6
Pro judge failed: 0
Pro judge skipped invalid: 2
```

### Arm B - Gemini 3.5 Flash Candidate, Same Pro Judge

- Prepare a new bundle from the same accepted frozen corpus with `--conversation-limit 2`.
- Use the same task catalog, selectors, task versions, schemas, finalizers, prompts, generation
  limits, case order, and frozen-prefix selection as Arm A.
- Generate all eight candidate attempts with the exact resolved
  `vertex_ai/gemini-3.5-flash` model.
- Package and verify the results independently.
- Compute deterministic metrics locally.
- Judge every schema-valid output with the exact same Pro judge profile, rubric version, provider
  schema, and judge generation policy used for Arm A.
- Preserve every invalid raw response privately and count it as `no_valid_output`; do not repair or
  silently retry it as a different request.
- Rerun judging with `--judge-cache-only` and prove zero additional provider calls.

Use unique ignored paths for the Gemini bundle, generation work, candidate package, scoring run,
and judge cache. Do not reuse or mutate Arm A paths.

## Meaning of "All Tests Completed"

Success does not mean every model output must pass its task schema or agree with FABLE. Requiring
that would tune away the result being measured.

For this work package, all tests are completed when:

- all eight case positions in Arm A have an explicit terminal candidate status;
- all eight case positions in Arm B have an explicit terminal candidate status;
- every schema-valid output in both arms has a terminal Pro-judge result;
- every schema-invalid output is explicitly counted and skipped from semantic judging;
- no infrastructure/configuration failure leaves a case unaccounted for;
- both arms pass package verification and deterministic scoring;
- both judge runs have successful zero-call cache-only reruns;
- a privacy-safe comparison report is produced.

Report `8/8 schema-valid` separately if Gemini 3.5 Flash achieves it. Do not make it a hidden
acceptance condition.

## Owner/Executor Working Method

This is an operator-assisted handoff. The executor owns diagnosis, configuration changes, code
changes, instructions, validation, and the completion report. The owner runs the explicitly remote
commands when instructed and returns the complete terminal accounting or sanitized failure output.

The executor must:

1. Give one small command block at a time.
2. Explain what the command will disclose, call, create, or verify before asking the owner to run
   it.
3. State the expected success shape and which output the owner should return.
4. Validate the returned output before giving the next command.
5. Reuse variables such as `$CONFIG`, `$PACKAGE`, and `$RUN` to reduce copy/paste errors.
6. Use PowerShell-safe quoting and line continuation.
7. Never ask the owner to paste credentials, access tokens, private transcripts, raw candidate
   outputs, FABLE references, or private absolute paths into the chat.

The owner's request authorizes disclosure of the same two frozen conversations and their FABLE
references to the confirmed Vertex candidate and judge models for this work package. Do not request
repeated approval for the same model/scope after Gate 0. Request new approval if the model, provider,
conversation count, task set, or disclosure content changes.

## Gate 0 - Preflight and Model Agreement

Before editing code or making a private provider call:

1. Confirm `poetry env info --path` resolves to this repository's `.venv`.
2. Read `md/agent-operating-notes.md` and follow its PowerShell and Poetry guidance.
3. Confirm the worktree and current commit; preserve concurrent owner changes.
4. Confirm the accepted Llama package and frozen source exist, but do not print private paths or
   content in the report.
5. Confirm ADC works with `gcloud auth application-default print-access-token` without displaying
   the token.
6. Confirm project/location environment variables are set by printing booleans only.
7. Recommend `global` for both requested Gemini models unless the owner's verified endpoint
   requires another documented shared location.
8. Run or instruct the owner to run privacy-safe, minimal model-availability probes that send only
   synthetic text.
9. Present the exact candidate and judge IDs that actually resolve.
10. Wait for owner confirmation of the judge ID before private calls.

Do not infer success from documentation alone; verify access in the owner's Vertex project.

## Harness Portability Requirement

The accepted harness currently assumes candidate profiles are local and candidate provenance
contains local artifact, quantization, runtime, and device fields. Hosted Vertex candidates must be
supported honestly rather than represented as fake GGUF artifacts.

If the current code rejects the remote candidate, implement the smallest generic hosted-candidate
extension. It must:

- distinguish local-artifact and hosted-API candidates structurally;
- preserve all accepted local Llama behavior and package compatibility;
- allow hosted candidate profiles only with explicit remote/private authorization at generation
  time;
- add generation CLI controls equivalent to `--allow-remote` and
  `--confirm-private-eval`, failing before provider execution unless both are present;
- record provider, resolved model ID, profile identity, task/generation settings, LiteLLM version,
  application commit, request identity, timing, token usage, retry count, and failure state;
- omit or make inapplicable local-only fields such as GGUF hash, quantization, local artifact path,
  LM Studio runtime, and execution device instead of inventing values;
- keep credentials, access tokens, Google project IDs, and private machine paths out of portable
  packages and tracked reports;
- keep candidate and judge cache identities separate;
- ensure changing only the judge model does not regenerate candidate outputs;
- ensure changing the candidate model creates a distinct candidate identity/package;
- remain provider-generic: do not hard-code Gemini branching into benchmark core logic.

Add strict Pydantic validation for mutually exclusive local/hosted provenance. Invalid mixed
configurations must fail with actionable, traceback-free CLI errors.

## Synthetic Compatibility Gate

Before sending private cases:

- add or update focused tests for hosted candidate config, provenance, authorization, package
  identity, remote-call denial, and local-candidate backward compatibility;
- run the four task contracts with synthetic inputs against Gemini 3.5 Flash;
- run the four judge rubrics with synthetic source/reference/candidate data against the selected
  Pro judge;
- determine compatible structured-output and thinking/reasoning settings through configuration;
- do not increase output limits or change prompts only to conceal a model failure;
- rerun the synthetic judge gate from cache and prove zero calls.

If a model requires different provider-compatible schema projection, keep the application-owned
schema and final validation authoritative. Any provider projection must remain generic and tested.

## Bug and Failure Policy

The executor should fix reproducible defects, but only within these boundaries.

### Fix without additional PM approval

- generic harness bugs exposed by hosted candidate profiles;
- cache-identity, resumability, report, newline, path, serialization, authorization, or package
  verification defects;
- provider request-shape compatibility where the application contract remains unchanged;
- actionable CLI diagnostics and missing focused tests;
- documentation/config examples required to operate the accepted workflow.

Use at most three focused diagnose/fix/validate cycles for the same infrastructure defect. Record
the root cause and regression test. If still blocked after three cycles, stop and report the exact
boundary.

### Do not "fix" as a software defect

- schema-invalid model output when the request and provider schema were correct;
- weak FABLE agreement or low judge scores;
- slower latency or higher token use;
- a legitimate safety refusal;
- task ambiguity visible in the frozen source/reference.

These are evaluation results. Preserve and report them.

### Requires PM/owner approval before changing

- task prompt, selector, schema, finalizer, rubric, score anchors, evidence policy, or accepted FABLE
  reference;
- temperature/output limits in only one arm when that would make the comparison materially unfair;
- provider/model fallback;
- retrying semantic failures with a modified prompt;
- expanding beyond two conversations/eight cases.

If a contract change is genuinely required, version it and rerun both arms. Never compare results
produced under different unreported contracts.

## Performance and Quality Comparison

Create one privacy-safe table with Arm A and Arm B columns. Include:

- candidate model and provider;
- judge model and provider;
- case count and case-fingerprint identity match;
- successful, invalid, and failed candidate counts;
- schema-valid rate overall and by task;
- evidence-valid and cross-field-valid counts;
- summary date/length validity;
- work-mode confusion matrix and exact agreement;
- last-activity status agreement;
- title-fit agreement;
- judge eligible/completed/failed/skipped counts;
- judge dimension means grouped by task;
- candidate total wall time;
- candidate latency p50/p95 overall and by task;
- prompt, completion, reasoning (when available), and total token usage;
- provider retries/rate-limit failures;
- cache-only rerun call count;
- any settings difference required by the provider.

Do not combine deterministic and judge scores into a single score. Do not claim statistical
superiority from two conversations. Describe results as an operational smoke and directional
performance observation.

For the model-replacement objective, explicitly report:

- whether replacement was configuration-only;
- which generic code assumptions blocked it, if any;
- files and abstractions changed;
- whether a third hosted provider could now use the same path without a new adapter;
- whether the accepted local Llama path remained unchanged.

## Required Validation

Run and record:

```powershell
poetry env info --path
poetry run pytest <focused hosted-candidate and benchmark tests> -q
poetry run pytest
poetry run ruff check .
poetry check
poetry run python -m bench generate --help
poetry run python -m bench score --help
poetry run chronicle --help
git diff --check
git diff --cached --name-only
git status --short
```

Also prove:

- existing Llama package unchanged;
- existing Gemini 2.5 judge run unchanged;
- live and frozen DB hashes unchanged;
- both new scoring directories are distinct;
- no `.chronicle`, DB, ZIP, candidate output, judge attempt, credential, token, project ID, or raw
  private content is tracked;
- both cache-only judge reruns make zero provider calls;
- all 16 arm/case positions reconcile as specified.

## Completion Report

Write a detailed report at:

```text
md/handoffs/reports/WP-5.2B1.2-completion-report.md
```

Required sections:

1. status: `Ready for PM validation`, `Partial`, or `Blocked`;
2. owner-confirmed model IDs and region, without project/account identifiers;
3. exact scope and case-fingerprint equality evidence;
4. files changed and why;
5. hosted-candidate architecture/provenance summary;
6. synthetic candidate and judge gate results;
7. Arm A accounting and cache proof;
8. Arm B accounting and cache proof;
9. privacy-safe side-by-side performance/quality table;
10. defects found, root causes, fixes, and regression tests;
11. model-output failures intentionally retained as evaluation results;
12. validation commands and results;
13. no-change/privacy/tracking evidence;
14. limitations and recommendation for the later 120-case evaluation;
15. acceptance checklist mapped line by line to this handoff.

Do not include private conversation IDs, titles, excerpts, paths, FABLE outputs, candidate outputs,
judge rationales, Google project/account identity, credentials, or access tokens.

## Delivery and Commit Ownership

- Leave all changes unstaged and uncommitted.
- Do not update the master plan or development ledger to accepted; PM validation owns status.
- Preserve unrelated owner/concurrent changes.
- The manager validates the report and implementation and commits only after explicit owner request.
