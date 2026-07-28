# WP-5.2C1 Handoff: Qwen3.5-4B Remote Speed And Context Study

## Status

**Approved for execution after the manager commits this handoff and the tracked
checkout is clean.**

This is an owner-in-the-loop benchmark and operations package. It is not a
production feature package.

For this handoff, "clean tracked checkout" means no staged or unstaged tracked
change. The following owner-owned, untracked LinkedIn drafts may remain and are
not a blocker:

```text
md/20260728_chronical_mcp_setting_post_v0.1.md
md/20260728_chronical_mcp_setting_post_v0.2.md
md/linkedin-mcp-windows-post.md
```

Preserve them untouched. Do not ask the owner to commit, delete, move, or ignore
them. Other unexpected tracked changes remain a stop condition.

## Executor Role

Act as the implementation and benchmark executor. Work interactively with the
owner for Google Cloud VM selection, provisioning, and transfer commands.

The development manager:

- owns scope and acceptance;
- validates the completion report;
- updates plan and ledger acceptance state;
- stages and commits after validation and an explicit owner request.

The executor must not stage or commit repository changes.

Read and follow:

- `md/agent-operating-notes.md`;
- `docs/development-evaluation.md`;
- `md/handoffs/WP-5.2B1-split-generation-local-scoring-gemini-judge.md`;
- `md/handoffs/reports/WP-5.2B1.4-completion-report.md`;
- `md/handoffs/reports/WP-5.2B2.2-completion-report.md`;
- `md/handoffs/reports/LP-4.1-local-model-results-analysis-brief.md`;
- the WP-5.2C section of `md/master-plan.md`.

## Manager Intent

Evaluate Qwen3.5-4B on a newer Google Cloud VM that is a useful proxy for a
home-work desktop purchase.

The study has two controlled questions:

1. How much faster is the accepted Qwen3.5-4B workload on the selected newer
   machine than on the owner's current laptop?
2. What changes when the configured context window increases from the accepted
   8,192-token baseline?

Candidate generation runs on the Google Cloud VM. Returned packages are
verified and evaluated on the owner's local Windows machine only after the
remote 120-case arm has completed.

Do not mix hardware, runtime, context, prompt, or model changes without naming
them. The report must separate:

- hardware/runtime speed;
- candidate reliability;
- context-window effects;
- semantic evaluation.

## Accepted Baseline

Treat the following as immutable comparison evidence:

- model: Qwen3.5-4B;
- artifact class: GGUF `Q4_K_M`;
- local runtime family: LM Studio/llama.cpp;
- configured context: 8,192 tokens;
- concurrency/parallelism: one unless the accepted private provenance says
  otherwise;
- corpus: frozen first 30 conversations;
- tasks: four accepted WP-5.1.1 tasks;
- cases: 120;
- local schema-valid result: 84/120;
- local failure total: 36/120;
- local failure categories: 29 context-length, five timeout, two schema
  validation;
- local observed wall time: 4h 43m 30.782s;
- existing prompts, selectors, schemas, finalizers, task versions, generation
  settings, and case order;
- fixed FABLE development references;
- fixed primary judge policy, if separately authorized at the local evaluation
  stage.

Do not rewrite or replace the accepted local package.

## Explicit Owner Authorization

The owner authorizes, for this work package:

1. Copying the frozen development database
   `.chronicle/eval/dev-v1/source/chronicle-frozen.db` to an owner-controlled
   Google Cloud VM selected for this study.
2. Copying the repository checkout, prepared 120-case input bundle, task
   prompts, response schemas, configuration, and exact Qwen artifact required
   for candidate generation.
3. Processing the private frozen development data on that VM for the approved
   Qwen candidate arms.
4. Returning hashed candidate packages and privacy-safe machine/runtime metrics
   to the owner's local machine.
5. Keeping all private transfer and run artifacts outside Git.

This authorization does **not** include:

- the live `.chronicle/chronicle.db`;
- provider exports or local ChatGPT/Claude/Codex source stores;
- credentials;
- FABLE references on the VM;
- Vertex judge inputs or judge outputs on the VM;
- another model, cloud inference API, or managed model endpoint;
- a public HTTP model endpoint;
- VM snapshots or reusable images containing private data;
- retaining private data after local verification and owner-approved cleanup.

The frozen DB is authorized, but the prepared input bundle remains the preferred
generation input. Do not make candidate generation depend on direct DB reads
unless a concrete tooling limitation requires it and that reason is documented.

## Cost And Provisioning Boundary

Research and recommendation do not create billable resources.

Before creating a VM, present one concise owner checkpoint containing:

- recommended machine type;
- region and zone;
- current availability/quota state;
- current estimated hourly compute price;
- boot-disk type, size, and estimated cost;
- expected setup and benchmark duration;
- estimated cost for required arms;
- estimated incremental cost for the optional 32K arm;
- shutdown/deletion plan;
- any expected network egress charge.

The owner must approve the exact machine/region/cost estimate before creation.
That is the only required VM-cost approval checkpoint. After approval, do not
ask repeatedly for the already-authorized frozen-data transfer or approved
candidate runs unless machine, region, data scope, model, or cost ceiling
changes.

Never leave a billable GPU VM running while waiting for ordinary review. Stop
the VM when an owner response is required and resume only when needed.

## VM Selection

### Required comparison

Compare at least:

| Candidate | Purpose | Initial PM view |
| --- | --- | --- |
| GCP `g2-standard-8` | One NVIDIA L4, 8 vCPU, 32 GB RAM | Recommended default |
| GCP `g2-standard-4` | One NVIDIA L4, 4 vCPU, 16 GB RAM | Lower-cost fallback; CPU/RAM may confound |
| Available G4 shape | RTX PRO 6000 Blackwell, server-class capacity | Document but normally reject as a home-desktop proxy |

Use official Google Cloud documentation and current project-visible pricing.
Do not rely on old blog pricing or generic third-party calculators.

### Default recommendation

Use `g2-standard-8` unless quota, availability, or current pricing makes it
impractical.

Rationale:

- NVIDIA L4 is a recent, efficient inference GPU;
- 24 GB VRAM gives headroom for Qwen3.5-4B Q4_K_M and the context ladder;
- 32 GB system RAM is comparable to a plausible home-work desktop;
- eight vCPUs reduce preprocessing and packaging bottlenecks;
- it is materially closer to a purchasable modern single-GPU desktop than an
  A100/H100/B200-class instance.

The completion report must state that an L4 VM is a proxy, not a benchmark of a
specific consumer GPU or complete desktop. Do not infer exact RTX desktop
performance, thermals, acoustics, purchase price, or power use from this VM.

### Current official references

- Google Cloud GPU machine types:
  `https://docs.cloud.google.com/compute/docs/gpus`
- Creating G2/G4 instances:
  `https://docs.cloud.google.com/compute/docs/gpus/create-gpu-vm-g-series`
- General GPU VM creation and driver guidance:
  `https://docs.cloud.google.com/compute/docs/gpus/create-vm-with-gpus`
- LM Studio headless/`llmster`:
  `https://lmstudio.ai/docs/developer/core/headless`
- Qwen3.5-4B model card:
  `https://huggingface.co/Qwen/Qwen3.5-4B`

Recheck these at execution time.

## Required Software Shape

Prefer LM Studio `llmster` on Linux so the remote arm stays within the accepted
LM Studio runtime family while using a CUDA execution backend.

Pin and record:

- Linux distribution and image identity;
- kernel;
- VM machine type, zone, vCPU, RAM, disk;
- GPU name, architecture, VRAM, driver, and CUDA capability;
- `nvidia-smi` output fields needed for provenance;
- LM Studio/`llmster` version;
- LM Studio inference engine and version;
- exact model repository, revision, filename, byte size, SHA-256, and
  quantization;
- loaded model ID;
- API endpoint identity;
- context, parallelism, GPU offload, flash-attention/KV settings, reasoning
  setting, and all nondefault load parameters;
- repository commit;
- Python and Poetry versions;
- benchmark config and bundle identities.

If `llmster` cannot run the exact artifact and contracts, stop and report the
boundary. Do not silently switch to Ollama, vLLM, SGLang, llama.cpp standalone,
another quantization, or another model. A runtime substitution requires manager
approval because it changes the comparison.

Bind the model server to loopback only. Do not expose port 1234 or any inference
port to the public network.

## Security And Transfer Rules

Use the owner's existing Google Cloud project and authenticated `gcloud`
session.

Preferred controls:

- OS Login or the owner's normal authenticated SSH path;
- no public inference service;
- SSH access restricted to the owner path, or IAP if already configured;
- default Google encryption at rest plus encrypted SSH/SCP transport;
- no public Cloud Storage object;
- no service-account key file copied into the repository or VM;
- no clipboard/paste of private conversation content;
- no startup script containing credentials or private payload;
- no disk snapshot after private transfer;
- private working directory readable only by the VM user;
- transfer hashes verified at both ends.

Record commands in a private operator log with project, zone, instance, IP,
paths, and hashes redacted from the tracked report.

Do not copy FABLE reference files to the VM. Candidate generation does not need
them.

## Controlled Experiment

### Invariants across every arm

Keep these unchanged:

- exact Qwen GGUF bytes and quantization;
- VM machine type and GPU;
- OS, driver, `llmster`, engine, and repository commit;
- 30-conversation order and 120 case identities;
- prompts, task versions, selectors, schemas, and finalizers;
- generation temperature and task token limits;
- reasoning mode;
- concurrency and model parallelism;
- bundle/package code path;
- retry and failure policy.

Only configured context may differ between context arms.

### Arm R8: remote 8K baseline

Required.

- context: 8,192;
- cases: all 120;
- purpose: reproduce the accepted arm on newer hardware and measure speed;
- no model-output repair;
- no retry of semantic/schema/context failures;
- interruption resume may continue missing positions without repeating
  completed positions;
- infrastructure failures must remain distinct from model failures.

Package and hash the arm before starting another context.

### Arm R16: remote 16K context

Required after R8 is complete and packaged.

- context: 16,384;
- cases: the same 120 in the same order;
- every invariant above remains fixed;
- use a distinct run, package, and config identity;
- report which 8K context failures become schema-valid, remain invalid, or
  change failure category;
- do not treat higher schema validity as semantic improvement until local
  scoring is complete.

### Arm R32: remote 32K context

Conditional but planned.

Run all 120 cases at 32,768 only when:

- R16 still has context-length failures or a meaningful unresolved long-input
  group;
- the model loads with adequate VRAM/system-RAM headroom;
- a four-task synthetic gate succeeds;
- one longest-input private case succeeds without OOM or runtime instability;
- its estimated incremental cost remains within the owner's approved VM budget.

If those conditions are not met, record R32 as `not run` with the exact reason.
Do not call the whole WP partial when R8 and R16 pass and R32 correctly stops at
its defined gate.

### No throughput tuning in this WP

Do not change concurrency, speculative decoding, batching, quantization, GPU
layers, prompt caching policy, or parallel slots to chase a faster number.
Those are separate follow-up experiments.

## Required Preflight

### Local machine

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
```

Require:

- repository `.venv`;
- clean tracked checkout;
- frozen snapshot integrity;
- accepted selection/input/reference/catalog identities;
- live and frozen DB baseline fingerprints captured privately;
- existing accepted local Qwen package still verifies;
- no private artifact tracked.

### Remote VM

Before private transfer:

- verify machine identity and attached GPU;
- verify disk space;
- verify driver and CUDA visibility;
- install the pinned application/runtime dependencies;
- check out the exact repository commit;
- confirm clean tracked checkout;
- run CLI/help and a privacy-safe synthetic four-task gate;
- confirm model server is loopback-only;
- capture idle GPU/CPU/RAM state;
- confirm automatic shutdown or an operator shutdown reminder.

Do not transfer the frozen DB before the synthetic gate and security checks pass.

## Preparation And Transfer

Use a new private run root under:

```text
.chronicle/eval/dev-v1/runs/wp-5.2c1-remote-qwen/
```

Prepare fresh, immutable bundles from the accepted corpus and task catalogs.
Do not modify historical candidate packages.

The executor must give the owner exact PowerShell and `gcloud` commands after
the VM selection checkpoint. Commands must cover:

1. VM creation;
2. SSH connectivity;
3. remote working-directory creation and permissions;
4. repository checkout;
5. software/runtime installation;
6. bundle, model, and authorized frozen-DB transfer;
7. source/destination SHA-256 verification;
8. remote generation;
9. candidate-package return;
10. returned-package SHA-256 verification;
11. VM stop;
12. final remote cleanup and VM/disk deletion after local acceptance.

Never write real project IDs, instance names, external IPs, private paths, or
private hashes into tracked files.

## Runtime Measurement

Capture privacy-safe aggregates for each arm:

- end-to-end generation wall time;
- setup/model-load time separately;
- candidate latency p50 and p95 overall and by task;
- prompt/completion/total token totals when available;
- throughput from provider usage or runtime logs when reliable;
- TTFT when reliably available;
- success and failure totals;
- exact failure categories;
- peak GPU memory;
- sampled GPU utilization;
- sampled CPU and system RAM;
- GPU temperature/power only if available from `nvidia-smi`, with a warning
  that VM telemetry does not represent a consumer desktop;
- interruptions and resumed positions;
- cost estimate and observed billable VM duration.

Do not print private outputs, prompts, IDs, titles, URLs, paths, or excerpts.

## Local Return, Verification, And Evaluation

Candidate generation finishes remotely. Evaluation happens on the owner's local
Windows machine.

For every returned package:

1. compare transfer hash;
2. run `bench verify`;
3. run deterministic-only scoring;
4. reconcile all 120 cases;
5. confirm the remote candidate endpoint is not needed;
6. compare with the accepted local 8K Qwen arm;
7. retain all schema-invalid cases in reliability denominators;
8. preserve work-mode, last-activity, and title-fit confusion matrices;
9. report summary/evidence/date contract metrics;
10. keep all private reports ignored.

The executor must provide exact local commands using the owner's resolved
private config paths rather than inventing paths.

### Judge boundary

Do not run the Vertex judge merely because generation completed.

Before semantic judging, present one consolidated confirmation that identifies:

- the exact returned arm(s);
- eligible case counts;
- the unchanged selected source, candidate output, and FABLE reference
  disclosure;
- `vertex_ai/gemini-3.1-pro-preview`;
- `global`;
- ADC;
- rubric v1;
- ordinary Vertex usage cost.

After owner authorization, judge locally and prove cache-only zero-call replay.
Do not send the frozen DB itself to Vertex.

## Required Comparisons

### Speed

Report:

- local laptop 8K vs remote R8;
- total wall-time speedup;
- p50 and p95 latency speedup;
- per-task speedup;
- load/setup time excluded and included;
- resource and runtime differences;
- why the result is not an exact consumer-desktop prediction.

### Context

Report:

- R8 vs R16 and, if run, R32;
- schema-valid count/rate;
- context-length failure count;
- timeout and schema failure count;
- cases recovered from the lower context;
- cases regressed at the higher context;
- wall time and latency cost;
- peak memory change;
- deterministic agreement and fixed-judge metrics after local scoring;
- whether the larger context improves useful output or merely admits more
  input.

### Home-desktop interpretation

Provide a bounded interpretation:

- what the GCP L4 result says about a modern dedicated-GPU machine;
- what it does not say about a specific RTX card;
- minimum VRAM observed for 8K/16K/32K;
- system-RAM and CPU observations;
- whether a 16 GB or 24 GB GPU appears operationally sufficient for this exact
  4B Q4 workload;
- what should be benchmarked on an actual candidate desktop before purchase.

Do not make a purchase recommendation from cloud GPU results alone.

## Stop Rules

Stop and report before further private work when:

- the proposed VM differs from the owner-approved machine/region/cost;
- GPU quota or regional availability requires a materially different machine;
- the exact model artifact cannot be verified;
- runtime substitution is required;
- the model server would be publicly exposed;
- transfer hash mismatches;
- frozen/live DB fingerprint changes;
- the remote checkout or benchmark contracts drift;
- R8 cannot reproduce all 120 terminal positions;
- an OOM, driver reset, or filesystem failure threatens evidence integrity;
- private data appears in Git;
- local package verification fails.

Routine resumable interruption is not a stop condition when the accepted bench
state machine can continue without duplicating completed calls.

If a generic bench defect is found:

- preserve all attempts and packages;
- stop before editing code;
- describe the defect and proposed minimal patch to the manager;
- wait for a patch handoff or explicit manager instruction;
- do not ask the owner to commit executor changes directly.

## Scope Exclusions

Do not:

- modify production Chronicle behavior;
- tune prompts;
- change task schemas or finalizers;
- change quantization;
- benchmark another model;
- add embeddings;
- create an untouched final evaluation set;
- run multiple concurrent candidate slots;
- repair invalid model output;
- overwrite accepted packages;
- publish private cases or raw metrics containing private identity;
- turn this into a general GCP deployment feature;
- add Terraform, a scheduler, or a hosted service unless separately approved;
- create or publish a Docker image containing the model or data.

## Acceptance Criteria

WP-5.2C1 is ready for PM validation only when:

1. The owner approved exact VM, region/zone, and estimated cost.
2. VM choice and rejected alternatives are documented using current official
   sources.
3. The selected VM is described as a proxy rather than an exact home desktop.
4. Frozen DB transfer occurred only within the explicit authorization above.
5. No live DB, exports, references, credentials, or judge artifacts reached the
   VM.
6. Every transferred private artifact has a matching source/destination hash.
7. The exact repository commit and Qwen artifact are pinned.
8. Runtime, engine, driver, GPU, CPU, RAM, disk, context, and load settings are
   recorded privately.
9. The remote synthetic four-task gate passes before private generation.
10. R8 has 120/120 terminal accounted positions.
11. R8 is packaged, hashed, returned, and locally verified.
12. R16 has 120/120 terminal accounted positions.
13. R16 is packaged, hashed, returned, and locally verified.
14. R32 either completes the same requirements or stops at its defined gate
    with a valid reason.
15. No completed candidate position is duplicated on resume.
16. All first-attempt failures remain preserved.
17. Deterministic scoring runs locally with the remote endpoint unavailable.
18. Speed metrics include wall time and p50/p95 overall/by task.
19. Context metrics reconcile every arm and failure category.
20. Resource metrics include peak VRAM and available CPU/RAM/GPU observations.
21. Comparison with the accepted local 8K Qwen arm is exact and caveated.
22. Semantic judging, if performed, occurs locally only after consolidated
    owner authorization.
23. Judge cache-only replay, if judging occurs, makes zero new provider calls.
24. Live and frozen local DB fingerprints remain unchanged.
25. Historical packages remain unchanged.
26. The VM is stopped when not in use.
27. Remote private artifacts are retained only until local verification and
    manager acceptance, then deleted under owner control.
28. No private artifact or credential is tracked.
29. Focused tests required by any approved tooling patch pass.
30. Full tests, Ruff, Poetry, CLI help, and `git diff --check` pass unless the
    manager explicitly waives unchanged-code tests.
31. The completion report exists at the exact required path.
32. Nothing is staged or committed by the executor.

## Required Completion Report

Write:

```text
md/handoffs/reports/WP-5.2C1-completion-report.md
```

The report must include:

1. status: `ready for PM validation`, `partial`, or `blocked`;
2. executive summary;
3. VM selection table and recommendation;
4. owner approval checkpoint outcome;
5. current official source links and date checked;
6. estimated and observed cost;
7. privacy and transfer boundaries;
8. software/model/runtime provenance;
9. exact experiment invariants;
10. R8 accounting and runtime metrics;
11. R16 accounting and runtime metrics;
12. R32 gate/outcome;
13. local verification evidence;
14. deterministic metrics;
15. judge metrics and cache replay, if authorized;
16. speed comparison with the accepted laptop arm;
17. context-window comparison;
18. home-desktop interpretation and limitations;
19. interruption/resume evidence;
20. database and historical-package immutability;
21. remote cleanup status;
22. validation commands and results;
23. Git privacy/tracking evidence;
24. known limitations and follow-ups;
25. requirement-by-requirement acceptance checklist;
26. final `git status --short`;
27. confirmation that nothing was staged or committed.

The tracked report must contain privacy-safe aggregates only. Exclude project
IDs, zones tied to the owner's account, instance names, IPs, private hashes,
case/conversation/message IDs, titles, URLs, private paths, prompts, source
text, candidate outputs, FABLE references, judge rationales, credentials, and
billing-account details.

## Delivery Message

Return a concise manager-facing message containing:

- status;
- selected VM;
- R8/R16/R32 terminal and schema-valid counts;
- wall times and speedup;
- context-failure changes;
- local verification/scoring status;
- judge status;
- cleanup status;
- validation totals;
- completion-report link;
- exact files changed;
- confirmation that nothing was staged or committed.
