# WP-5.2B3A Handoff: Full Local 8K Versus 16K Context Comparison

## Status

**Approved for execution after the development manager commits this handoff and
the tracked checkout is clean.**

WP-5.2C1 remains active in parallel but is externally blocked by Google Cloud
resource availability. WP-5.2B3A is independent and runs entirely on the
owner's local Windows machine.

For this handoff, a clean tracked checkout means no staged or unstaged tracked
changes. The following owner-owned untracked LinkedIn drafts may remain and do
not block execution:

```text
md/20260728_chronical_mcp_setting_post_v0.1.md
md/20260728_chronical_mcp_setting_post_v0.2.md
md/linkedin-mcp-windows-post.md
```

Preserve them untouched. Also preserve every private or tracked WP-5.2C1
artifact produced by its separate executor.

## Executor Role

Act as the benchmark executor. Run the accepted Chronicle evaluation pipeline,
coordinate local LM Studio model loading with the owner, preserve all existing
evidence, and return a completion report plus an article-ready evidence brief.

The development manager:

- owns scope and acceptance;
- reviews the completion report;
- decides the context policy used by WP-5.2B3B;
- stages and commits after validation and an explicit owner request.

The executor must not stage or commit changes and must not mark the ledger
accepted.

## Read First

Read and follow:

- `md/agent-operating-notes.md`;
- `docs/development-evaluation.md`;
- `md/master-plan.md`, especially WP-5.2B1 through WP-5.2B3A;
- `md/handoffs/reports/WP-5.2B1.4-completion-report.md`;
- `md/handoffs/reports/WP-5.2B2.2-completion-report.md`;
- `md/handoffs/reports/LP-4.1-local-model-results-analysis-brief.md`;
- accepted private manifests for the Qwen3.5-4B and Phi-4 Mini 8K arms.

This handoff is self-contained for scope, experiment design, acceptance,
reporting, and stop rules. Older handoffs provide implementation provenance but
cannot broaden this scope.

## Objective

Measure the effect of increasing local context from 8,192 to 16,384 tokens for
the two best accepted local models:

1. Qwen3.5-4B Q4_K_M;
2. Phi-4 Mini Instruct Q4_K_M.

Reuse the accepted full 120-case 8K packages. Generate only the two new 16K
arms, one per model, on the same local machine.

Use the result to recommend one common context policy for the later global
prompt-optimization study:

- WP-5.2B3B prompt development on 10 conversations;
- WP-5.2B3C one-shot prompt evaluation on 20 conversations.

The context study uses all 30 conversations. The later 20-conversation holdout
therefore evaluates prompt changes conditional on the selected context; it is
not an independent validation of the context decision.

## Research Questions

Answer:

1. How many 8K context failures become valid at 16K?
2. Does 16K increase whole-package schema/evidence reliability?
3. Do recovered outputs have acceptable deterministic and judge quality?
4. Does 16K introduce new schema, evidence, timeout, or semantic regressions?
5. What latency, wall-time, token, RAM, and VRAM cost accompanies 16K?
6. Is one common 16K policy operationally suitable for both local models?
7. How much of the local/cloud gap is caused by context rather than prompting
   or model capability?

## Accepted 8K Baselines

Treat these as immutable.

### Qwen3.5-4B

- cases: 120;
- schema-valid: 84/120, 70.0%;
- failures: 36;
- context-length: 29;
- timeout: five;
- schema validation: two;
- task validity summary/mode/activity/title: 17/19/30/18;
- macro UTS: 61.9;
- candidate latency p50/p95: 62.094s/168.375s;
- observed wall span: 4h 43m 30.782s, with the accepted timeout-tail
  decomposition retained.

### Phi-4 Mini

- cases: 120;
- schema-valid: 77/120, 64.2%;
- failures: 43;
- context-length: 21;
- schema validation: 12;
- timeout: ten;
- task validity summary/mode/activity/title: 14/18/29/16;
- macro UTS: 50.0;
- candidate latency p50/p95: 54.608s/180.031s;
- observed wall span: 2h 18m 51s.

### Unchanged Cloud Reference

Gemini 3.5 Flash remains the accepted unchanged cloud reference:

- schema-valid: 112/120, 93.3%;
- macro UTS: 88.4.

Do not generate a new Gemini candidate arm in WP-5.2B3A.

## Scope

### In Scope

- verify accepted 8K package identities;
- reconstruct the exact 120-case scope;
- reproduce each model's accepted artifact/runtime/generation contract;
- load each model at 16,384 context;
- run a four-task synthetic transport/schema gate;
- generate 120 Qwen 16K cases;
- generate 120 Phi 16K cases;
- package and verify both arms;
- deterministic local scoring;
- fixed-Pro local orchestration and remote judging after one consolidated owner
  authorization;
- cache-only zero-call judge replay;
- full 8K/16K transition analysis;
- context-policy recommendation;
- privacy-safe completion report;
- privacy-safe article evidence brief.

### Out Of Scope

- 32K context;
- Google Cloud or any remote candidate runtime;
- prompt edits or prompt optimization;
- input-selector or `max_input_chars` changes;
- model-specific context selection for WP-5.2B3B;
- quantization, artifact, runtime, temperature, token-cap, timeout, retry,
  concurrency, batching, or reasoning-policy changes;
- output repair;
- another local model;
- new teacher references;
- human adjudication;
- final untouched evaluation-set creation;
- final article drafting, publication, or graphics;
- production Chronicle behavior changes;
- embeddings, retrieval, or MCP changes.

## Experimental Invariants

For each model, the only intended change from its accepted 8K arm is:

```text
context_window: 8192 -> 16384
```

Hold constant:

- exact selected 30 conversations and 120 ordered case identities;
- exact selected task inputs;
- FABLE references;
- model family;
- GGUF file bytes, hash, revision, and Q4_K_M quantization;
- LM Studio and inference-engine version used by that model's accepted arm;
- execution backend/device;
- GPU offload and load settings except unavoidable context allocation;
- parallelism and concurrency: one;
- task prompts;
- task versions;
- selectors;
- response schemas;
- finalizers;
- temperature;
- task output-token limits;
- timeout/retry policy;
- reasoning mode;
- structured-output request contract;
- benchmark implementation commit and package format.

Do not claim a context-only comparison if any other effective field changes.

## Runtime-Identity Gate

Before generation, resolve the exact accepted private provenance separately for
Qwen and Phi.

Capture:

- model repository/revision/file/hash/size;
- loaded model identifier;
- LM Studio CLI/daemon version;
- inference engine and version;
- Windows version;
- CPU, RAM, graphics device, and available memory;
- load configuration;
- API model identity;
- context;
- parallelism;
- flash-attention/KV/offload settings;
- benchmark commit and config hashes.

If the exact accepted inference engine is unavailable:

1. stop before private generation;
2. report the precise drift;
3. do not silently compare against the historical package;
4. propose either restoring the accepted runtime or running a separately
   approved paired 8K/16K study under the new runtime.

The executor must not choose the second option without manager approval.

## Data And Privacy Boundary

All candidate generation occurs locally through loopback LM Studio.

Allowed:

- frozen development input bundle;
- private FABLE references during local scoring/judging;
- local candidate packages;
- local fixed-Pro judge calls after explicit authorization.

Not allowed:

- Git tracking of DBs, prompts containing private inputs, candidate outputs,
  references, judge rationales, package hashes tied to private identities, or
  local paths;
- copying data to WP-5.2C1's VM;
- public model-server exposure;
- remote candidate generation;
- pasting private content into chat delivery or tracked reports.

## Local Working Directories

Use distinct ignored run roots:

```text
.chronicle/eval/dev-v1/runs/wp-5.2b3a-qwen-16k/
.chronicle/eval/dev-v1/runs/wp-5.2b3a-phi-16k/
.chronicle/eval/dev-v1/tmp/wp-5.2b3a-analysis/
```

Do not modify:

- accepted 8K packages;
- WP-5.2C1 private roots;
- frozen DB;
- live DB;
- accepted inputs, references, catalogs, or selection manifest.

## Preflight

Follow `md/agent-operating-notes.md`.

```powershell
poetry env info --path
git status --short
git rev-parse HEAD
poetry run python -m bench --help
poetry run python -m bench prepare --help
poetry run python -m bench generate --help
poetry run python -m bench verify --help
poetry run python -m bench score --help
poetry run chronicle --ai-task list
```

Require:

- Poetry resolves to this repository's `.venv`;
- no staged/unstaged tracked change;
- only the explicitly allowed owner drafts or ignored private artifacts are
  untracked;
- frozen DB integrity and expected schema/counts pass;
- live and frozen DB fingerprints are captured privately;
- accepted Qwen/Phi 8K packages verify unchanged;
- task catalogs and FABLE reference identities are unchanged;
- enough local disk space exists;
- no competing LM Studio generation job is running.

## Phase 1: Freeze Comparison Contract

Create a private comparison manifest before loading either 16K arm.

It must bind:

- WP ID and format version;
- Git commit;
- 30-conversation/120-case identity;
- input/reference/task-catalog identities;
- accepted Qwen 8K package identity;
- accepted Phi 8K package identity;
- exact 8K baseline settings and aggregate results;
- exact new 16K settings;
- invariant list;
- failure policy;
- analysis/scoring versions;
- creation time.

Hash and freeze it. Do not edit it after the first 16K candidate call.

## Phase 2: Qwen 16K Arm

1. Stop/unload other local LLMs as needed.
2. Load the exact accepted Qwen artifact at context 16,384, parallelism one.
3. Confirm API identity and effective load settings.
4. Run a synthetic four-task strict-schema gate.
5. Require 4/4 terminal schema-valid synthetic outputs.
6. Prepare a fresh 120-case bundle/config with a unique 16K identity.
7. Generate all 120 candidate positions.
8. Preserve first-attempt success/failure exactly.
9. Resume interruptions without repeating completed positions.
10. Do not retry model/schema/evidence/context failures.
11. Package the current authoritative attempts.
12. Verify the package locally.
13. Run deterministic-only scoring.
14. Stop or unload Qwen before loading Phi.

If context allocation, OOM, engine instability, or identity drift occurs, stop
and report before switching settings.

## Phase 3: Phi 16K Arm

Repeat the same procedure for the exact accepted Phi-4 Mini artifact:

1. load at context 16,384 and parallelism one;
2. verify effective identity/settings;
3. pass the 4/4 synthetic strict-schema gate;
4. generate all 120 candidate positions;
5. preserve failures and resumable state;
6. package;
7. verify;
8. score deterministic-only.

Do not reuse Qwen config identities or result paths.

## Failure And Retry Policy

Every expected candidate position must end as:

- valid success; or
- explicit terminal failure with normalized category.

Allowed:

- resume missing positions after interruption;
- retry an infrastructure write/sharing failure through already accepted
  bounded infrastructure behavior;
- preserve append-only attempts when an explicitly approved recovery is
  required.

Not allowed without manager rework approval:

- retry invalid JSON, schema, evidence, or semantic output;
- increase output tokens;
- alter timeout;
- repair JSON;
- truncate prompts differently;
- lower input caps;
- change runtime;
- change context away from 16,384;
- change concurrency;
- modify benchmark code.

If a generic defect is discovered, preserve evidence, stop, and request a
separate patch handoff. Do not ask the owner to commit executor changes.

## Phase 4: Local Verification And Deterministic Scoring

For each 16K package:

```powershell
poetry run python -m bench verify --package <package> --config <local-eval-config>
poetry run python -m bench score --package <package> --config <local-eval-config> --deterministic-only
```

Require:

- package identity and checksums pass;
- 120/120 cases accounted;
- all invalid outputs remain in denominators;
- work-mode matrix totals 30;
- last-activity matrix totals 30;
- title-fit matrix totals 30;
- summary deterministic checks total 30;
- no candidate or judge model call during deterministic-only scoring;
- live/frozen DBs unchanged.

## Phase 5: Fixed-Pro Judging

Judging executes from the owner's local machine through the accepted evaluation
harness. It is not candidate generation.

Before the first new judge call, present exactly one consolidated owner
confirmation covering:

- both Qwen-16K and Phi-16K packages;
- every schema-valid eligible result;
- selected source input, candidate result, and fixed FABLE reference;
- `vertex_ai/gemini-3.1-pro-preview`;
- `global`;
- ADC;
- rubric v1;
- ordinary Vertex usage cost;
- bounded configured retry only.

Do not ask repeatedly after authorization unless provider, model, region,
rubric, eligible scope, disclosure, or retry policy changes.

After authorization:

1. run the four-task synthetic judge gate;
2. require 4/4 accepted structured judge outputs;
3. judge every eligible Qwen-16K result;
4. judge every eligible Phi-16K result;
5. preserve terminal judge failures;
6. run identical cache-only replay;
7. prove zero new calls and byte-stable attempts.

Do not rejudge accepted 8K packages. Reuse their accepted fixed-Pro evidence.

## Phase 6: Exact 8K/16K Comparison

Compare per model and task.

### Product Reliability

Report:

- valid/120 and percentage;
- invalid/120;
- summary/mode/activity/title valid/30;
- context, timeout, JSON, schema, evidence, provider, and other failures;
- relative invalid-output reduction;
- absolute valid-case gain.

### Case Transition Matrix

For each model, reconcile all 120 case identities into:

| 8K state | 16K state |
| --- | --- |
| valid | valid |
| valid | invalid |
| invalid | valid |
| invalid | invalid |

Subdivide transitions by task and 8K/16K failure category.

Specifically report:

- 8K context failure -> 16K valid;
- 8K context failure -> 16K different failure;
- 8K valid -> 16K invalid regression;
- unchanged semantic/schema failures.

Do not publish case IDs or content.

### Deterministic Semantics

Report:

- work-mode confusion matrix and exact agreement;
- last-activity confusion matrix and exact agreement;
- title-fit confusion matrix and exact agreement;
- summary date/evidence/length validity;
- per-label precision/recall/support;
- all denominators.

### Fixed-Judge Semantics

Report:

- eligible/completed/failed/skipped;
- task-specific dimension means and denominators;
- valid-output quality;
- whole-case UTS with invalid/judge-failed cases scoring zero;
- UTS by task and macro;
- baseline-to-16K delta;
- recovered-case judge quality separately from always-valid cases.

Keep deterministic agreement and judge quality separate.

### Operational Performance

Report:

- candidate wall time;
- model load/setup time separately;
- p50/p95 overall and by task;
- timeout totals and durations;
- prompt/completion/total tokens where available;
- peak process/system RAM;
- graphics memory/utilization when available;
- effective context allocation;
- interruption/resume events;
- difference from 8K.

Do not repeat the historical raw Qwen wall span without its accepted timeout-tail
decomposition.

### Unchanged Cloud Reference

Show the accepted Gemini 3.5 Flash 120-case aggregates as a reference column.
Label it:

```text
unchanged historical cloud control; not regenerated in WP-5.2B3A
```

Do not compare local and cloud latency as equivalent hardware measurements.

## Context-Policy Recommendation

Produce one recommendation for WP-5.2B3B:

- common 8K; or
- common 16K.

Recommend 16K when:

1. both model arms complete without OOM/runtime instability;
2. both have 120 terminal positions;
3. combined Qwen+Phi valid count improves;
4. neither model has a material whole-package reliability regression;
5. recovered context cases show useful, not merely schema-valid, outputs;
6. semantic metrics do not show a material regression;
7. local latency/memory remain operationally acceptable for batch enrichment.

Do not make the final policy decision from valid count alone.

If evidence is mixed, present the trade-off and leave the final decision to the
manager/owner. WP-5.2B3B cannot start until the context policy is accepted and
frozen.

Do not recommend model-specific contexts in this first global-prompt study.

## Article Evidence Requirements

WP-5.2B3A is intended to support a future technical article. Benchmark
acceptance and article drafting remain separate activities so narrative choices
cannot alter the evidence.

Create:

```text
md/handoffs/reports/WP-5.2B3A-context-comparison-article-brief.md
```

The brief must be publication-ready but privacy-safe and include:

1. research question;
2. why context was tested before prompt optimization;
3. hypotheses recorded before results;
4. exact controlled variables;
5. local hardware/runtime/model provenance;
6. 8K baseline table;
7. 16K result table;
8. per-task validity matrix;
9. failure-category decomposition;
10. 120-case transition matrices;
11. recovered-context-case aggregates;
12. deterministic semantic metrics;
13. fixed-judge semantic metrics;
14. UTS and valid-output-quality values with formulas/denominators;
15. latency, wall-time, token, and memory costs;
16. unchanged Gemini reference;
17. context-policy recommendation;
18. claims supported by evidence;
19. prohibited claims;
20. limitations;
21. chart-ready aggregate tables;
22. three to five proposed article observations;
23. two to four headline directions;
24. suggested article outline;
25. suggested figures;
26. links to the tracked completion report and accepted baseline reports.

### Suggested Figures

Provide chart-ready data for:

1. 8K versus 16K validity by model and task;
2. failure-category before/after bars;
3. case transition flow or recovery matrix;
4. quality/reliability two-axis comparison;
5. latency or wall-time cost versus valid-case gain.

Do not create final graphics unless the owner requests them.

### Article Claims Must Distinguish

- context capacity;
- structured-output reliability;
- semantic quality;
- runtime cost;
- prompt optimization, which has not started;
- cloud reference, which was not regenerated.

### Required Limitations

State:

- private real-work development corpus;
- only 30 conversations/120 cases;
- FABLE silver references;
- fixed Gemini-family judge;
- same corpus used to select context;
- one Windows laptop;
- one GGUF quantization per model;
- one LM Studio runtime contract;
- no untouched context holdout;
- no statistical/general population claims;
- no evidence that 16K is optimal beyond the tested 8K/16K choices;
- no evidence yet that prompt gains will generalize.

### Prohibited Claims

Do not claim:

- that 16K is universally better;
- model accuracy or ground truth;
- that recovered schema-valid output is automatically correct;
- that context alone closes the cloud gap;
- that remote WP-5.2C1 speed results are local WP-5.2B3A results;
- that prompt tuning produced any B3A improvement;
- consumer-hardware generalization;
- statistical significance.

## Required Completion Report

Write:

```text
md/handoffs/reports/WP-5.2B3A-completion-report.md
```

The report must include:

1. status: `ready for PM validation`, `partial`, or `blocked`;
2. executive summary;
3. scope and exclusions;
4. accepted 8K baseline identities and aggregates;
5. runtime-identity comparison;
6. frozen comparison manifest result;
7. Qwen 16K synthetic gate;
8. Qwen 16K 120-case accounting;
9. Phi 16K synthetic gate;
10. Phi 16K 120-case accounting;
11. package verification;
12. deterministic scoring;
13. judge authorization and synthetic gate;
14. judge accounting and cache-only replay;
15. 8K/16K product reliability;
16. transition matrices;
17. deterministic semantics;
18. fixed-judge semantics;
19. latency/token/resource evidence;
20. unchanged cloud-reference comparison;
21. context-policy recommendation;
22. article-brief delivery;
23. privacy and data tracking;
24. live/frozen DB immutability;
25. historical-package immutability;
26. focused/full/Ruff/Poetry/help/diff validation;
27. known limitations;
28. acceptance checklist;
29. exact files changed;
30. final `git status --short`;
31. confirmation that nothing was staged or committed.

Do not include private case IDs, conversation/message IDs, titles, URLs, raw
inputs, outputs, references, rationales, paths, hashes, credentials, or
machine-user identity.

## Acceptance Criteria

WP-5.2B3A is ready for PM validation only when:

1. Poetry resolves to the repository `.venv`.
2. The tracked checkout starts clean apart from the explicit untracked-draft
   exception.
3. Frozen/live DB and accepted evidence fingerprints are captured.
4. Qwen and Phi accepted 8K packages verify unchanged.
5. Exact artifact/runtime/generation provenance is reproduced per model.
6. The frozen comparison manifest exists privately.
7. Qwen 16K synthetic gate passes 4/4.
8. Qwen 16K has 120 terminal accounted cases.
9. Qwen package verifies and deterministic scoring completes.
10. Phi 16K synthetic gate passes 4/4.
11. Phi 16K has 120 terminal accounted cases.
12. Phi package verifies and deterministic scoring completes.
13. No completed candidate position is duplicated.
14. No invalid output is repaired or hidden.
15. No prompt, selector, schema, model, quantization, or generation-policy
    change occurs.
16. All 240 new positions are reconciled.
17. Transition matrices total 120 per model.
18. Failure categories reconcile.
19. All deterministic matrices total 30 per applicable task.
20. Fixed-Pro judging is owner-authorized before disclosure.
21. Every eligible result is judged or has an explicit terminal judge failure.
22. Cache-only replay exits zero with zero new calls.
23. Speed/resource metrics are complete and separately interpreted.
24. The unchanged Gemini reference is labeled correctly.
25. One common context recommendation is produced.
26. Article evidence brief exists at the required path.
27. Completion report exists at the required path.
28. Live/frozen DBs remain unchanged.
29. Historical packages and WP-5.2C1 artifacts remain unchanged.
30. No private artifact or credential is tracked.
31. Full tests and Ruff pass unless the manager explicitly approves a
    documentation-only waiver.
32. `poetry check`, CLI help, bench help, and `git diff --check` pass.
33. Nothing is staged or committed by the executor.

## Required Validation Commands

At minimum:

```powershell
poetry env info --path
poetry run pytest
poetry run ruff check .
poetry check
poetry run python -m bench --help
poetry run python -m bench generate --help
poetry run python -m bench verify --help
poetry run python -m bench score --help
poetry run chronicle --help
poetry run chronicle --ai-task list
git diff --check
git status --short
git ls-files ".chronicle/*" "*.db" "*.sqlite" "*.zip" "exports/*"
```

Also run and record privacy-safe results for:

- accepted package re-verification;
- comparison-manifest validation;
- both synthetic 16K gates;
- both 120-case generations;
- both package verifications;
- both deterministic scores;
- judge cache-only replay;
- transition reconciliation;
- DB/package immutability.

## Stop Rules

Stop and report when:

- exact accepted runtime/artifact cannot be reproduced;
- a second effective variable would change;
- model loading requires a different quantization or engine;
- synthetic 16K gate fails;
- OOM/driver reset threatens result integrity;
- package verification fails;
- frozen/live DB changes;
- accepted packages change;
- private data appears in Git;
- WP-5.2C1 concurrent work conflicts with required files;
- a generic code defect requires a patch.

Do not label a correctly stopped runtime-identity or safety boundary as
completed.

## Delivery Message

Return:

- status;
- Qwen 8K/16K valid counts and context-failure change;
- Phi 8K/16K valid counts and context-failure change;
- wall-time and p50/p95 changes;
- judge/cache status;
- common context recommendation;
- article-brief path;
- completion-report path;
- validation totals;
- exact tracked files changed;
- confirmation nothing was staged or committed.
