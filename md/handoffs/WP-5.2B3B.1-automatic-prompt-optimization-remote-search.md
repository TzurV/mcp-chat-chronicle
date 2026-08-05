# WP-5.2B3B.1 Handoff: Automatic Prompt Optimization And Remote Search

## Status

**Approved for execution from a clean `main` checkout after the development
manager commits this handoff.**

This work package follows the accepted WP-5.2B3B controlled manual-prompt
experiment. It must use only the frozen ten-conversation development scope. The
twenty-conversation holdout remains unopened until WP-5.2B3B.2 freezes a winner
and WP-5.2B3C is separately authorized.

The work has one mandatory manager checkpoint after the generic optimizer bridge
and preflight are ready, but before private transfer, paid compute, or proposer
calls. After that consolidated checkpoint is approved, the executor should
complete the bounded pilot and permitted continuation without requesting repeated
approval for recoverable errors inside the declared limits.

## Executor Role And Commit Ownership

Act as the benchmark optimization executor. Build the minimum generic integration
needed to run reproducible DSPy BootstrapFewShot and GEPA experiments through the
existing Chronicle benchmark contracts. Prepare and run the bounded remote search,
return an immutable shortlist, and provide article-ready aggregate evidence.

The development manager owns scope, acceptance, staging, commits, merges, tags,
and publication decisions. The executor must not run `git add`, `git commit`,
amend, rebase, merge, tag, or push. Executor delivery status is `Ready for PM
validation`, never `Accepted`.

If a manager checkpoint is required, leave the tracked patch unstaged and
uncommitted, write the checkpoint evidence into the progress report, and stop.
After the manager validates and commits it, resume this same handoff from the new
clean commit. Do not create a replacement handoff for narrow rework inside this
scope.

## Read First

Read and follow:

- `md/agent-operating-notes.md`;
- `md/master-plan.md`, especially WP-5.2B3A through WP-5.2B3C;
- `docs/development-evaluation.md`;
- `md/handoffs/WP-5.2B3B-global-prompt-development.md`;
- `md/handoffs/reports/WP-5.2B3B-completion-report.md`;
- `md/handoffs/reports/WP-5.2B3B-validation-review.md`;
- `md/handoffs/reports/WP-5.2B3B-prompt-development-evidence-brief.md`;
- `md/handoffs/reports/WP-5.2C1-completion-report.md`;
- `md/research/WP-5.2C1-runpod-remote-lm-studio-service.md`;
- `bench/prompts/wp-5.2b3b/selected-p0.yaml`;
- the ignored accepted B3B split, inputs, references, packages, and selected-P0
  manifest;
- the official [DSPy optimizer overview](https://dspy.ai/learn/optimization/optimizers/);
- the official [DSPy GEPA reference](https://dspy.ai/api/optimizers/GEPA/overview/);
- the official [RunPod pricing page](https://www.runpod.io/pricing).

The official APIs and prices may have changed. Verify and pin the exact versions,
artifact revisions, and current console price used by this run. Do not silently
adopt a prerelease DSPy/GEPA build or an incompatible result schema.

## Objective

Determine whether established automatic prompt-optimization methods can produce
a globally portable four-task prompt package that improves on accepted P0 for the
two local target models without opening the holdout.

Use:

1. DSPy BootstrapFewShot as a low-data automatic few-shot baseline;
2. DSPy GEPA as the primary reflective instruction optimizer;
3. Qwen3.5-4B Q4_K_M and Phi-4 Mini Instruct Q4_K_M as joint optimization
   targets;
4. the accepted common 8,192-token context;
5. the existing FABLE references and deterministic validators as development
   feedback;
6. P0, P1, and P2 as immutable historical controls.

Do not optimize model weights. Do not tune model-specific prompts. Do not select
different winning prompt variants per task after viewing results. A candidate is
one complete four-task package.

## Accepted Baseline

The following facts are fixed:

- P0 pooled local validity: 62/80;
- Qwen P0 validity: 30/40;
- Phi P0 validity: 32/40;
- P1 and P2 pooled local validity: 58/80 each;
- common context: 8,192;
- development scope: 10 conversations and 40 task cases per model;
- holdout scope: 20 conversations and 80 task cases per model, unopened;
- selected P0 SHA-256:
  `bd332905a78e74fd26251d85cb9acc417af940279e022c4dd725bb4f1a0cd1c5`.

The selected P0 copy, root task catalog, and packaged task catalog must retain
that exact identity. Existing P0/P1/P2 candidate and judge artifacts are
read-only authorities and must not be rewritten.

## Private Authority And Working Location

The accepted final B3B private run exists under the manager-validated dedicated
checkout at:

`C:\tmp\mcp-chat-chronicle-wp52b3b-f25505a\.chronicle\eval\dev-v1\runs\wp-5.2b3b`

The active repository also has an ignored B3B run directory. Before using either,
compare the accepted manifests and hashes. Treat the dedicated final run as the
authority if the trees differ. Create a new ignored B3B.1 run root in the active
repository and copy only the required accepted development artifacts using a
manifested, hash-verified operation. Never overwrite either B3B source tree.

Record source and destination aggregate identities privately. The tracked report
may state that verification passed but must not expose private hashes, paths below
the approved root, conversation IDs, titles, URLs, or content.

## Non-Negotiable Experiment Boundaries

- The twenty-conversation holdout must not be opened, copied, transferred,
  generated, scored, judged, summarized, or used for optimizer feedback.
- Search uses only the ten accepted development conversations.
- Context remains 8,192 for both candidate models.
- Accepted GGUF bytes, quantization, chat templates, generation settings, and
  concurrency remain unchanged unless a compatibility blocker is returned to the
  manager before search.
- P0/P1/P2 remain immutable controls.
- No output repair, truncation, hidden retry, or manual answer correction is
  allowed.
- Do not optimize against Gemini or the fixed Gemini Pro judge.
- Do not call the fixed judge during the optimizer inner loop.
- Do not promote a prompt containing private examples or copied private text.
- Remote timing is search-infrastructure evidence, not local deployment timing.

## Research Questions

Answer:

1. Can BootstrapFewShot improve reliability with this small development set?
2. Can GEPA improve the complete package using deterministic and reference-backed
   failure feedback?
3. Do improvements hold jointly across Qwen and Phi, or favor one model?
4. Which tasks improve, regress, or remain dominated by context/runtime failures?
5. What search budget, proposer usage, GPU time, and prompt overhead are required?
6. Does the search produce a bounded shortlist worth local transfer testing?
7. Are gains likely to be prompt effects rather than retries, context changes,
   model changes, or selection leakage?

## Gate 0: Local Preflight And Frozen Inputs

From the repository root:

1. Run `poetry env info --path` and require the repository-local `.venv`.
2. Require a clean tracked checkout at the committed handoff identity.
3. Record branch, commit, Python, Poetry, OS, and benchmark versions.
4. Verify the frozen DB integrity, schema version, and accepted counts without
   writing it.
5. Verify the selected P0 hash and accepted B3B manifests.
6. Verify zero holdout access before any implementation or run.
7. Create a fresh ignored run ID for B3B.1. Never reuse a B3B run directory.
8. Capture before-hashes for accepted packages, frozen/live DBs, and source
   manifests.

If the accepted private authority cannot be reconstructed or hash-verified, stop
before implementing optimizer behavior.

## Development Subsplit

Freeze a deterministic metadata-only 6/4 split inside the accepted ten
development conversations before opening per-case outcomes for optimizer design:

- optimizer train: six conversations with provider quotas 2 ChatGPT, 2 OpenAI
  Codex, 1 Claude, and 1 Claude Code;
- optimizer validation: four conversations with one from each provider;
- target length allocation where metadata permits: train 2 short, 2 medium,
  2 long; validation 2 short, 1 medium, 1 long.

Use a documented deterministic selection and tie-break rule. Freeze ordered
manifests and hashes. The two subsets must be disjoint and cover exactly the ten
accepted development conversations. The twenty-conversation holdout is not part
of this operation.

Do not choose the split from P0/P1/P2 outcomes, labels, failure types, titles, or
message content. If the exact length allocation is impossible, record the nearest
deterministic allocation and stop for manager review before reading outcomes.

## Gate 1: Generic Optimizer Bridge

Implement only the generic capability needed for this study. Follow existing
`bench` configuration, package, manifest, atomic-write, resume, cache, and
verification patterns.

Required capabilities:

- a separate optional optimization dependency group; normal Chronicle install,
  search, MCP, AI tasks, and existing bench commands must not require DSPy/GEPA;
- strict Pydantic configuration for optimizer identity, versions, seed, budgets,
  train/validation manifests, candidate models, proposer profile, context,
  concurrency, retries, time and cost ceilings;
- a provider-neutral proposer interface configured externally through LiteLLM;
- adapters between the four Chronicle tasks and DSPy programs without changing
  accepted schemas, selectors, finalizers, or task semantics;
- deterministic aggregate metrics and rich text feedback derived from existing
  schema, evidence, cross-field, date, enum, and reference checks;
- append-only optimizer trials, candidate packages, failure records, usage,
  latency, and search traces;
- atomic, resumable execution with explicit current-attempt authority;
- safe serialization. Do not load untrusted pickle artifacts. Prefer JSON/YAML
  and framework-supported safe formats; if DSPy serialization requires another
  format, document and constrain it;
- commands for preflight, dry-run, optimize, resume, inspect, verify, package,
  and export-shortlist, following the existing `python -m bench` CLI style;
- a privacy-safe tracked configuration template containing no real paths,
  project IDs, credentials, model secrets, or private corpus identities.

Do not modify the normal `chronicle --ai-task` execution path unless a generic
defect makes that unavoidable. Do not introduce DSPy as a runtime dependency for
users who do not install the optimization extra.

## Optimizer Version Compatibility Gate

Before writing the bridge:

1. identify the latest stable DSPy release and its compatible GEPA integration;
2. inspect the stable APIs for `BootstrapFewShot`, `GEPA`, compiled-program
   serialization, detailed results, usage, cache, and error types;
3. pin compatible bounded versions in the optional dependency group;
4. reject prerelease packages unless the manager explicitly approves them;
5. add tests that fail clearly if the pinned result schema or required API is
   incompatible;
6. record official source links, exact versions, hashes where available, and the
   reason for the selected versions.

GEPA result structures have changed between releases. Do not copy assumptions
from an example without testing the exact pinned version.

## Program And Package Model

Represent the four tasks as one optimization program with four prompt-bearing
components. Every optimizer candidate must resolve to one complete package with:

- four task prompt texts;
- immutable task/schema/selector/finalizer identities;
- optimizer and proposer provenance;
- parent candidate and mutation lineage where applicable;
- prompt byte hashes and token estimates;
- deterministic train and validation metrics for both Qwen and Phi;
- failure taxonomy, latency, usage, and terminal accounting.

The optimizer may mutate prompt text only. It must not change schemas, enum sets,
evidence rules, selectors, input limits, context, generation defaults, timeouts,
or model profiles.

## Search Metric And Feedback

Predeclare the reliability-first aggregate ordering:

1. total schema-and-evidence-valid outputs across Qwen and Phi;
2. lower of the two model-valid counts;
3. minimum pooled task-valid count across the four tasks;
4. deterministic semantic/contract agreement against FABLE references;
5. complete-package UTS when available outside the optimizer inner loop;
6. lower prompt-token overhead;
7. stable candidate identity as the final deterministic tie-break.

No lower criterion may compensate for a loss on a higher criterion.

The per-case GEPA feedback may include only structured diagnostic facts needed to
explain the result, such as schema path, invalid enum, evidence mismatch,
cross-field violation, date mismatch, expected label versus candidate label, or
timeout/context boundary. Do not ask the proposer to invent a score. Do not send
fixed-judge rationales into the search.

Produce a scalar adapter only where DSPy requires one, and prove by tests that its
ordering cannot let semantic gains overcome a reliability loss. Preserve the
full lexicographic components alongside any scalar.

## BootstrapFewShot Baseline

Run one predeclared BootstrapFewShot configuration with a fixed seed. Start with
at most one labeled and one bootstrapped demonstration per task unless the
compatibility dry-run proves that configuration invalid. Any different bounded
configuration requires manager approval before private calls.

Use only the six optimizer-train conversations. Validate the compiled package on
the four optimizer-validation conversations across both Qwen and Phi.

Because bootstrapped demonstrations can contain private development text, treat
the resulting package as private and non-deployable by default. It may be a
research comparator, but it is not eligible for the final transferable shortlist
unless a privacy scan proves it contains no private title, URL, evidence ID,
message span, or meaningful source-text overlap. Do not sanitize it after seeing
results and then claim the sanitized prompt achieved the original score.

## GEPA Search

Use GEPA as an instruction-only reflective optimizer. Keep the student program
zero-shot unless the manager explicitly changes that decision. GEPA may use the
six optimizer-train conversations for traces and feedback and the four frozen
optimizer-validation conversations for candidate comparison.

Required search controls:

- fixed random seed;
- deterministic ordered manifests;
- `track_stats` or the stable-version equivalent enabled;
- complete candidate lineage and Pareto/search trace retained;
- maximum 12 GEPA candidate packages in the four-hour pilot;
- maximum 40 GEPA candidate packages for the complete initial search;
- maximum 3,000 Qwen/Phi task invocations across pilot and continuation,
  including bounded infrastructure retries;
- maximum 250 proposer calls unless the consolidated approval sets a lower cap;
- concurrency one per loaded candidate model unless accepted runtime evidence
  supports an unchanged higher setting;
- no candidate-output repair and no semantic-result retry.

If the stable GEPA API uses a different budget unit, translate these ceilings into
that API conservatively and record the exact mapping before calls.

## Prompt Privacy And Promotion Gate

GEPA receives private development traces and can echo them into proposed
instructions. Every candidate must remain ignored and private during search.

Before a candidate can enter the transferable shortlist, scan it against all ten
development inputs and references for:

- exact titles, URLs, IDs, paths, and long numeric identifiers;
- exact sentence or message spans;
- meaningful n-gram overlap above a predeclared threshold;
- copied reference rationales or summaries;
- credentials or environment values.

Record the scanner version, threshold, and result. A failing candidate is
disqualified, not edited. Human inspection may confirm a suspected leak but may
not rewrite the candidate. The tracked reports contain only aggregate privacy
results.

## Remote Execution Target

Preferred target: owner-controlled RunPod Secure Cloud RTX 5090 32 GB, using the
accepted WP-5.2C1 service pattern. An RTX 4090 24 GB is an allowed availability
fallback only if the same artifacts, context, runtime behavior, and validation
gates pass.

At allocation time record privately:

- provider, region, instance/Pod identity, GPU model and VRAM;
- vCPU and RAM allocation;
- container and volume sizes;
- image and driver/runtime identities;
- exact console hourly price and storage price;
- allocation, start, stop, and deletion times;
- actual final billing.

Do not claim a physical CPU model unless it was directly captured. Do not keep a
stopped paid volume after returned artifacts verify locally.

## Remote Transfer

Transfer only:

- the exact committed application source or immutable source archive;
- the accepted Qwen and Phi GGUF artifacts or independently verified downloads;
- the six-train/four-validation development bundle;
- accepted task schemas, selectors, deterministic validators, and FABLE
  references required by the metric;
- the privacy-safe optimization configuration;
- temporary secrets through the approved secret mechanism, never inside the
  bundle.

Do not transfer the twenty-conversation holdout, live database, unrelated
conversation history, historical candidate packages not needed as controls, or
fixed-judge credentials.

Use encrypted transfer. Generate source and destination manifests and verify
hashes before private execution. Return packages and traces in checksummed
archives. Verify locally before deleting remote data.

## Proposer Model And Credential Boundary

The proposer model must be configured externally through LiteLLM. Prefer a
strong model from a different family than the fixed Gemini Pro judge when the
owner has suitable credentials. If only a Gemini proposer is practical, disclose
the same-family risk explicitly and keep the fixed judge out of the inner loop.

The executor must not select a paid proposer silently. At the Gate 1 checkpoint,
present no more than two practical proposer profiles with:

- exact provider/model ID and LiteLLM route;
- current availability and region;
- expected input/output disclosure;
- estimated call and token budget;
- expected maximum API cost;
- credential source and revocation method;
- same-family or evaluation-bias implications;
- recommended option.

Use a temporary least-privilege key or ADC/service identity supplied by the
owner. Inject it through RunPod secrets or process environment. Never write it to
YAML, bundles, images, logs, shell history, reports, or Git. Revoke or rotate it
after teardown.

## Consolidated Manager Checkpoint

Stop once, before private transfer or spending, and provide:

1. generic implementation diff and test evidence;
2. exact clean application commit proposed for remote execution;
3. frozen 6/4 manifest identity and zero-holdout-access proof;
4. pinned DSPy/GEPA versions and compatibility evidence;
5. selected RunPod target, current price, four-hour estimate, and twelve-hour
   maximum estimate;
6. proposer options and recommended API budget;
7. model artifacts, context, call ceilings, retry policy, and transfer manifest;
8. exact external disclosure statement;
9. final `git status --short`, with nothing staged.

The manager will validate and commit the generic patch. The owner will confirm
the selected proposer and API budget. Once both are supplied, resume from that
clean commit without asking again for each authorized candidate, feedback trace,
or bounded retry.

## External Disclosure Authorization

The approved work package authorizes, after the consolidated checkpoint:

- encrypted transfer of the frozen ten-conversation development inputs and
  FABLE references to the owner-controlled RunPod Pod;
- local inference on those inputs with the accepted Qwen and Phi artifacts;
- disclosure to the selected proposer provider of only the selected development
  input, candidate output, accepted reference fields, schema/contract, and
  structured deterministic feedback required for BootstrapFewShot or GEPA;
- the approved proposer-call and cost ceiling;
- one bounded infrastructure/provider retry per failed operation where the first
  attempt did not yield a valid semantic result;
- ordinary RunPod compute and storage cost within the approved time ceiling.

This authorization excludes the holdout, unrelated conversations, live DB,
fixed-judge credentials, arbitrary providers, expanded retries, prompt repair,
and costs above the approved ceiling. Stop if the required disclosed fields or
provider differ materially from the approved checkpoint.

## Pilot And Continuation Rule

The first paid phase is a maximum four-hour pilot. It must include:

- remote environment and artifact verification;
- one synthetic four-task gate per candidate model;
- P0 reproduction on the four optimizer-validation conversations;
- the single BootstrapFewShot baseline;
- no more than 12 GEPA candidate packages;
- verified append-only traces and resumability;
- current spend and projected completion cost.

Continue beyond four hours, up to the twelve-hour compute ceiling, only if:

1. all safety, privacy, accounting, and resume checks pass;
2. at least one GEPA candidate is no worse than P0 on validation total validity,
   worst-model validity, and minimum task validity;
3. the search is producing distinct, privacy-eligible candidates rather than
   repeated or leaked prompts;
4. projected compute and proposer cost remain inside the approved ceilings.

If continuation criteria fail, stop and deliver the pilot as a valid
no-improvement result. Do not spend the remaining budget merely because it is
available.

## Retry, Recovery, And Defect Policy

Inside the approved scope, diagnose and fix ordinary generic defects, add focused
tests, and continue without requesting a new work package. Preserve failed
attempts and use append-only recovery.

Allowed without another owner approval:

- one retry for a transient infrastructure/provider failure;
- restart from the last verified optimizer checkpoint;
- bounded atomic-write/sharing-violation retries already supported by the bench;
- correcting a generic serialization or resume defect that does not alter
  metrics, prompts, split, models, context, or already completed outcomes.

Stop for manager review if a fix changes the metric ordering, feedback content,
split, privacy scanner, optimizer budget, prompt mutation surface, model/runtime,
context, or authority of completed attempts. Do not rewrite accepted evidence to
fit a fix.

## Shortlist Rule

Return P0 plus three to five immutable GEPA candidates. BootstrapFewShot may be
included only as a separately labelled research comparator unless it passes the
promotion privacy gate.

Rank candidates lexicographically using the declared aggregate ordering on the
four-conversation optimizer validation subset. Apply these guardrails:

- no candidate below P0 total pooled validity is eligible;
- no candidate may reduce either model by more than one valid case;
- no candidate may reduce any pooled task by more than one valid case;
- no privacy-gate failure is eligible;
- no unaccounted position or non-terminal retry state is eligible;
- prompt size must fit every accepted 8K case under the existing estimator and
  safety margin.

Keep diversity where candidates tie: prefer different GEPA lineages or prompt
strategies rather than near-duplicate text. Do not choose a single final winner
in B3B.1. WP-5.2B3B.2 reruns P0 and the shortlist locally and owns winner freeze.

## Local Return Verification

After remote execution:

1. stop paid inference before downloading results;
2. download checksummed source-independent candidate packages, traces, metrics,
   usage, telemetry, and billing evidence;
3. verify every archive and internal manifest locally;
4. verify every candidate can be loaded and deterministically rescored without
   provider calls;
5. prove P0/P1/P2, frozen/live DBs, and holdout artifacts are unchanged;
6. retain a verified ignored local backup;
7. delete the Pod, attached volume, transferred private bundle, and temporary
   secrets;
8. verify ongoing RunPod spend is zero and record final billing.

Do not run B3B.2 local candidate generation or Gemini portability testing in this
handoff.

## Required Tests

Add focused synthetic tests for:

- strict optimization config and unknown-field rejection;
- optional dependency behavior when DSPy/GEPA is absent;
- pinned optimizer API/result compatibility;
- deterministic 6/4 manifests, disjointness, ordering, and tamper rejection;
- prohibition on holdout paths and IDs;
- four-task package structural equivalence outside prompt text;
- lexicographic metric ordering and scalar-adapter dominance;
- rich feedback content without raw secret/environment leakage;
- BootstrapFewShot private/non-deployable classification;
- GEPA candidate lineage, Pareto/search trace, and stable identities;
- candidate privacy scanning and disqualification;
- time, candidate, task-call, proposer-call, retry, and cost ceilings;
- append-only attempts, resume, interrupted recovery, and current-attempt
  authority;
- safe package serialization and archive extraction;
- shortlist guardrails and deterministic tie-breaking;
- backward compatibility for all accepted historical packages;
- zero provider calls during verify, inspect, package, and local rescore;
- no regression to Chronicle CLI, AI tasks, MCP, or normal installs.

Use only synthetic fixtures in tracked tests. Real-data execution remains private
and ignored.

## Validation Commands

At minimum run:

```powershell
poetry env info --path
poetry run pytest <focused optimizer and bench tests> -q
poetry run pytest
poetry run ruff check .
poetry check
poetry run python -m bench --help
poetry run python -m bench optimize --help
poetry run chronicle --help
git diff --check
git status --short
```

Also validate installation without the optimization extra and with the
optimization extra in isolated environments. The ordinary installed wheel must
not import DSPy during non-optimization commands.

## Documentation Deliverables

Update:

- `docs/development-evaluation.md` with optimizer setup, dry-run, remote pilot,
  resume, verification, shortlist export, privacy, secrets, teardown, and local
  transfer workflow;
- a tracked privacy-safe optimizer configuration template;
- `md/development-ledger.md` to `Ready for PM validation` only, never `Accepted`.

Do not update production prompt defaults or user-facing AI task instructions in
this work package.

## Required Completion Report

Create:

`md/handoffs/reports/WP-5.2B3B.1-completion-report.md`

The report must include:

1. status: `Ready for PM validation`, `Partial`, or `Blocked` with exact reason;
2. executive summary;
3. files changed;
4. branch, clean application commit, environment, and package versions;
5. DSPy/GEPA compatibility decision and official sources;
6. frozen authority and selected P0 verification;
7. 6/4 development split method and aggregate quotas;
8. explicit zero-holdout-access evidence;
9. optimizer program, mutation surface, metric, scalar mapping, and feedback;
10. BootstrapFewShot configuration and results;
11. GEPA seed, budgets, candidate count, Pareto/search trace, and lineage;
12. proposer identity, region, usage, calls, latency, errors, and estimated/actual
    cost;
13. Qwen/Phi artifact, runtime, context, concurrency, calls, failures, latency,
    tokens, and hardware evidence;
14. pilot checkpoint and continuation decision;
15. per-candidate and aggregate reliability, worst-model, minimum-task,
    deterministic, UTS-available, and prompt-overhead results;
16. full failure taxonomy and retry accounting;
17. prompt privacy scan method and results;
18. shortlist with exact immutable identities and selection arithmetic;
19. P0/P1/P2 comparison and an explicit no-improvement result if appropriate;
20. remote versus local interpretation boundaries;
21. transfer, verification, backup, deletion, secret revocation, final billing,
    and zero ongoing spend;
22. full validation results;
23. privacy/tracking scan and final Git status;
24. known limitations, especially ten-conversation development overfitting and
    proposer/judge family bias;
25. acceptance checklist;
26. exact next step for B3B.2.

Do not include private IDs, titles, URLs, paths, prompt contents derived from real
data, candidate outputs, reference rationales, credentials, cloud project IDs,
private hashes, Pod IDs, or billing-account identity.

## Article Evidence Brief

Create:

`md/handoffs/reports/WP-5.2B3B.1-automatic-optimization-evidence-brief.md`

It must provide article-ready aggregate tables and observations, not final article
copy. Include:

- controlled manual P0/P1/P2 baseline versus BootstrapFewShot and GEPA;
- search budget, candidates explored, compute time, API usage, and cost;
- reliability-first result and failure taxonomy;
- per-task difficulty and model tradeoffs;
- remote search speed separated from local deployment speed;
- shortlist and privacy eligibility;
- negative results and full denominators;
- chart-ready data and proposed figures;
- supported claims, unsupported claims, limitations, and confidence;
- placeholders for B3B.2 transfer and B3C holdout evidence.

## Acceptance Criteria

WP-5.2B3B.1 is complete only when:

- the optional generic optimizer bridge is tested and backward compatible;
- stable DSPy/GEPA versions are pinned and proven compatible;
- the frozen 6/4 development split is reproducible;
- the holdout has zero access and zero calls;
- the four-hour pilot is complete and any continuation obeyed the declared rule;
- BootstrapFewShot and bounded GEPA results are terminal and fully accounted;
- every candidate, lineage, failure, usage, latency, and cost is reproducible;
- P0 remains an immutable control;
- a privacy-eligible three-to-five-candidate shortlist, or a rigorous
  no-improvement result, is delivered;
- returned artifacts verify locally and remote resources/secrets are removed;
- ongoing RunPod spend is verified at zero;
- the full repository validation passes;
- the completion report and evidence brief are delivered;
- nothing is staged or committed by the executor.

## Mandatory Stop Conditions

Stop and return to the manager if:

- the Poetry environment points outside this repository;
- accepted baseline, DB, split, or prompt hashes do not match;
- the holdout is opened or transferred;
- stable DSPy/GEPA APIs cannot support the required trace and result contracts;
- a prerelease dependency appears necessary;
- a proposed fix changes metrics, feedback, split, schemas, selectors, context,
  models, generation settings, or completed-attempt authority;
- a candidate prompt leaks private development content;
- credentials appear in files, logs, images, reports, or Git;
- provider/model/region/disclosed fields differ from the approved checkpoint;
- the four-hour or twelve-hour compute ceiling, proposer-call ceiling, or owner-
  approved API cost ceiling would be exceeded;
- remote artifacts cannot be verified before teardown;
- a destructive or unbounded operation is proposed.

Do not stop merely because a model returns invalid JSON, a candidate performs
poorly, an authorized transient retry is needed, or the optimizer finds no
improvement. Those are experiment outcomes and must be recorded.

## Delivery And Git Boundary

At the manager checkpoint and final delivery:

- leave every change unstaged and uncommitted;
- report `git status --short` and identify every intended file;
- preserve unrelated owner changes;
- track only code, tests, privacy-safe templates, documentation, handoff reports,
  and article evidence;
- keep DBs, inputs, references, candidates, outputs, traces, caches, archives,
  credentials, manifests with private paths, and cloud artifacts ignored;
- do not update the ledger to `Accepted`;
- do not begin WP-5.2B3B.2 or WP-5.2B3C.

The development manager will validate the delivery and commit only after an
explicit owner request.
