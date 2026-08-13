# WP-5.2B3B.1C Handoff: GEPA Pilot And Bounded Search

## Status

Owner-authorized and ready for execution from the clean committed `main`
revision containing this handoff. The owner supplied the authorization in
**Owner Authorization** when dispatching the executor.

This package continues the accepted WP-5.2B3B.1 experiment. It does not rerun
P0, BootstrapFewShot, checkpoint recovery, or fixed judging. The accepted
WP-5.2B3B.1B readiness state selects P0 as the sole GEPA parent.

## Recommended Executor

Continue with the same executor that performed B3B.1, BootstrapFewShot, the
RunPod persistence work, and B3B.1B recovery. That executor already knows the
append-only state, retained-volume layout, model/runtime setup, ADC boundary,
and prior failure history. A new executor is acceptable only if the current
one is unavailable or its context has degraded; a replacement must read every
document listed below before accessing RunPod or private state.

## Executor Role And Commit Ownership

Act as the prompt-optimization executor. Restore the accepted retained state,
run the bounded GEPA pilot, continue only when the frozen pilot criteria permit
it, return an immutable shortlist or explicit no-improvement result, and write
privacy-safe completion evidence.

The development manager owns scope, acceptance, staging, commits, merges,
tags, pushes, and publication. Do not run `git add`, `git commit`, amend,
rebase, merge, tag, or push. Leave all delivery changes unstaged and
uncommitted with status `Ready for PM validation`.

Do not stop for routine recoverable operations already covered by this
handoff. Stop only at a listed stop condition or when owner interaction is
genuinely required for allocation, SSH, ADC browser authentication, or an
unapproved lifecycle decision.

## Read First

Read and follow:

- `md/agent-operating-notes.md`, especially the public-repository security and
  scarce-cloud-resource rules;
- `docs/public-repository-security.md`;
- `md/master-plan.md`, WP-5.2B3B.1 through WP-5.2B3C;
- `md/handoffs/WP-5.2B3B.1-automatic-prompt-optimization-remote-search.md`;
- `md/handoffs/reports/WP-5.2B3B.1-execution-progress.md`;
- `md/handoffs/reports/WP-5.2B3B.1B-checkpoint-recovery-gepa-readiness-completion-report.md`;
- `md/research/WP-5.2B3B.1-prompt-optimization-activity-log.md`;
- `docs/development-optimization.md`;
- `docs/runpod-vertex-adc.md`;
- `docs/windows-vertex-adc.md` for later local-only operations;
- `bench/optimization.default.yaml`;
- the ignored recovered readiness, P0, run-state, authorization, budget, model,
  and split manifests;
- the official DSPy 3.3 GEPA and GEPA 0.1.1 documentation pinned by the
  existing compatibility gate.

## Objective

Determine whether GEPA can produce one globally portable four-task instruction
package that improves the accepted P0 prompts jointly for Qwen3.5-4B and
Phi-4 Mini without opening the holdout.

GEPA may mutate only the four accepted system prompts. It must use:

- P0 as the only parent;
- six frozen optimizer-train conversations for traces and feedback;
- four frozen optimizer-validation conversations for candidate comparison;
- Qwen and Phi as joint candidate models through the accepted local LM Studio
  route on RunPod;
- context 8,192, concurrency one, accepted model bytes, and unchanged
  generation settings;
- deterministic schema/evidence/contract checks and the existing FABLE
  references for optimizer feedback;
- Google Vertex AI `vertex_ai/gemini-3.1-pro-preview` in `global` as the GEPA
  proposer through LiteLLM and temporary user ADC.

Do not optimize weights, selectors, schemas, finalizers, evidence rules,
generation settings, model profiles, task-specific variants, or holdout cases.

## Roles: Proposer, References, And Judge

Keep these roles separate:

1. **Gemini Pro proposer:** GEPA sends development traces and structured
   diagnostics to Vertex Gemini Pro, which proposes revised instructions.
2. **Development scoring:** candidate outputs are evaluated by deterministic
   validators and the already-created private FABLE references. This is the
   optimization feedback loop.
3. **Fixed Gemini Pro judge:** the semantic judge used in prior benchmark work
   is not called during GEPA and its rationales are never optimizer feedback.
   It remains local for finalist comparison after packages return, under
   WP-5.2B3B.2 or a separate explicit authorization.

Therefore no separate judge credential or judge service is required on
RunPod. Vertex ADC is required only because Gemini Pro is the GEPA proposer.
The proposer and later fixed judge are from the same model family; preserve
that disclosed evaluation-bias limitation in all reports.

## Accepted Starting State

Require and verify before any call:

- the repository is clean at the committed handoff revision;
- GitHub CI is green for Ubuntu/Windows and Python 3.11/3.12 with both `mcp`
  and `optimization` extras;
- DSPy 3.3.0 and GEPA 0.1.1 pass `verify_compatibility()`;
- the recovered private state resolves one P0 result and one Bootstrap result
  against three consumed historical execution authorizations;
- P0 is the explicit GEPA parent;
- Bootstrap attempt `0003` is `complete-non-promotable` by manager policy;
- GEPA attempts, results, proposer calls, and recovery-provider calls are zero;
- attempts `0001` through `0003`, P0, Bootstrap, budgets, current pointers,
  fixed-judge evidence, and provider-response indexes are unchanged;
- frozen split remains 6 train / 4 validation and holdout access remains zero;
- retained model and checkpoint hashes pass.

Do not rerun recovery merely because a fresh application commit exists. Follow
the accepted configuration-transition procedure, update only the ignored
configuration's current `application_commit`, and verify all other parsed
fields are identical.

## Hard Experiment Boundaries

- Do not open, copy, transfer, score, judge, summarize, or inspect any holdout
  input, reference, outcome, path, or identity.
- Do not rerun P0, BootstrapFewShot, or historical candidate generation.
- Do not call the fixed judge during optimization.
- Do not repair, truncate, reinterpret, or manually correct model output.
- Do not retry semantic failures. Allow only the configured single bounded
  infrastructure retry.
- Do not change proposer model, region, credential mode, model artifacts,
  context, prompt fields, split, seed, scoring, privacy scanner, budgets, or
  continuation criteria.
- Keep private inputs, references, traces, proposed prompts, responses,
  manifests, hashes, cloud identifiers, and result packages ignored and
  untracked.
- Tracked reports may contain only privacy-safe aggregates, public application
  commits, public model identities, and generalized operational evidence.

## Budget And Authorization Envelope

Existing persisted accounting remains authoritative. Do not reset or enlarge
it. At the accepted readiness checkpoint, remaining proposer capacity was:

- 244 logical proposer calls;
- 12,249,977 input tokens;
- 1,959,729 output/reasoning tokens;
- US$49.016702 proposer cost.

Remaining configured optimizer compute capacity was:

- 11.128676 compute hours;
- US$17.282016 compute cost.

The effective limit is always the smallest of the persisted ledger, the
configuration, observed platform availability, and the owner's authorization.
Storage already retained is reported separately and does not authorize more
GPU spend.

Reserve before each operation and reconcile measured usage afterward. Unknown
provider retries or usage fail conservatively. Never infer additional budget
from a successful call or unused owner ceiling.

## RunPod Restoration And Capacity Loop

Use RunPod CLI/API first for discovery, compatible allocation, status, price,
and lifecycle operations. Use provider-issued SSH and standard `scp`/`rsync`
when the CLI has no equivalent transfer operation. Do not give the owner a
custom Python operator script unless no supported CLI or standard transfer path
exists and the reason is documented.

Compatible target:

- preferred RTX 5090 32 GB in the retained volume's data center;
- RTX 4090 24 GB only if already allowed by the parent handoff and the accepted
  runtime/model/context gates pass unchanged;
- attach the existing private network volume at its established mount point;
- do not create a second private state tree when the retained canonical tree is
  recoverable.

If compatible capacity is unavailable, run a bounded wait/retry loop with
backoff. Report availability and spend state without repeatedly asking the
owner to approve the same search. Do not allocate an incompatible GPU merely
to end the wait.

Immediately after allocation, ask the owner to run the exact provider-issued
SSH command. Wait for the owner to confirm an interactive shell before
declaring the Pod inaccessible or modifying lifecycle state.

Never delete the Pod, network volume, repository, model cache, or results
unless the owner explicitly says `delete` for that named resource in the
current activity. A failure is a diagnostic checkpoint, not deletion
authority. If the owner does not respond for two hours while paid compute is
running, stop/release compute only after hash-verifying persistent state; keep
the network volume and data. Record the action and ongoing storage cost.

## Pre-Call Gate

Before configuring ADC or loading private traces:

1. Verify the local and remote repository commit and clean status.
2. Verify the retained restart/checkpoint manifests and accepted model hashes.
3. Verify the recovered GEPA-readiness artifact and P0 parent.
4. Verify no GEPA evidence or proposer usage has appeared since readiness.
5. Verify the ignored config differs only at the current application commit.
6. Run optimizer preflight, dry-run, inspect, and compatibility checks.
7. Load Qwen and Phi one at a time under accepted LM Studio settings and verify
   localhost-only identity without candidate calls.
8. Recalculate operation capacity against all persisted ceilings.
9. Confirm zero holdout access.

Do not add another synthetic provider probe. The first real GEPA proposer call
is the authentication boundary. If it fails, preserve append-only evidence and
stop without switching route or retrying beyond the configured infrastructure
policy.

## Temporary Vertex ADC On RunPod

Follow `docs/runpod-vertex-adc.md` exactly. Do not request or create a Gemini API
key. Do not place a Google service-account key in the Pod environment or
persistent volume.

Inside the interactive Pod shell:

```bash
umask 077
export CHRONICLE_ADC_HOME=/dev/shm/chronicle-vertex-adc
export HOME="$CHRONICLE_ADC_HOME"
export CLOUDSDK_CONFIG="$CHRONICLE_ADC_HOME/.config/gcloud"
mkdir -p "$CLOUDSDK_CONFIG"

gcloud auth application-default login \
  --no-browser \
  --project=<PROJECT_ID>
```

The owner runs the generated `--remote-bootstrap` command on the trusted local
computer and returns its result directly to the waiting Pod prompt. Never paste
the command, URL, code, credential path, token, or project value into chat,
tracked reports, shell-history captures, or Git.

Then, in the same private `tmux`/execution shell:

```bash
gcloud auth application-default set-quota-project <PROJECT_ID>

export GOOGLE_APPLICATION_CREDENTIALS="$CHRONICLE_ADC_HOME/.config/gcloud/application_default_credentials.json"
export GOOGLE_CLOUD_PROJECT="<PROJECT_ID>"
export GOOGLE_CLOUD_LOCATION="global"
export VERTEXAI_PROJECT="<PROJECT_ID>"
export VERTEXAI_LOCATION="global"
export GOOGLE_GENAI_USE_VERTEXAI="true"

gcloud auth application-default print-access-token >/dev/null
```

Do not print environment values or tokens. A successful no-output ADC check is
not a model call.

## GEPA Pilot

Start `optimize` from P0 using the four explicit authorization flags required
by the CLI:

- `--allow-remote`;
- `--confirm-private-eval`;
- `--confirm-proposer-disclosure`;
- `--confirm-paid-budget`.

Use the accepted append-only run and trial authorities. The pilot limits are:

- at most 12 GEPA candidate packages;
- at most four compute hours;
- within the persisted task/proposer/token/cost/retry ceilings;
- Qwen and Phi jointly evaluated on the frozen validation subset;
- instruction-only mutations from P0;
- fixed seed, detailed GEPA statistics, candidate lineage, parents, discovery
  counts, subscores, usage, latency, and failures retained.

The pilot continuation gate requires at least one privacy-eligible GEPA
candidate that is component-wise no worse than P0 on:

1. total valid validation outputs;
2. worst-model valid count;
3. minimum-task valid count.

It must also fit the complete 8,192-token request envelope, contain a prompt
distinct from P0, have terminal/reconciled accounting, and leave enough budget
for a complete next operation. Semantic agreement, UTS, and prompt overhead may
rank candidates only after those reliability conditions; they cannot
compensate for a reliability loss.

If the pilot gate fails, persist `pilot-no-improvement`, export the evidence,
and stop. Do not invent another prompt scheme or relax the criteria.

## Authorized Continuation

If and only if the durable pilot checkpoint passes all frozen criteria, resume
without asking for another approval. Continue until the first of:

- GEPA exhaustion;
- 40 total GEPA candidates;
- 3,000 total candidate-model task invocations across the accepted experiment;
- 12 total configured compute hours;
- the persisted proposer call/token/cost ceiling;
- the persisted compute-cost ceiling;
- insufficient capacity for one complete next operation.

Resume must not rewrite prior candidates, attempts, responses, current
pointers, usage, or pilot evidence.

## Privacy And Shortlist Gate

Every proposed four-prompt package remains private. Before shortlist admission,
run the accepted scanner against all ten development inputs and references for
titles, URLs, paths, IDs, long numbers, exact spans, source n-grams, reference
language, credentials, and environment values.

A failing candidate is disqualified, not edited. Do not publish candidate
prompt text. Export:

- immutable P0;
- three to five diverse eligible GEPA packages when available; or
- an explicit no-improvement artifact when fewer than three qualify.

Rank using the frozen reliability-first rule. Do not call the fixed judge to
choose the shortlist.

## Return, Verification, And Resource State

Keep authoritative state on the retained persistent volume throughout. Return
only the checksummed shortlist, required traces/metrics/accounting, and
privacy-safe operator evidence through supported encrypted transfer. Verify
every returned hash locally before changing compute state.

After a terminal pilot/search or an owner-approved pause:

1. stop all optimizer and LM Studio processes;
2. revoke temporary ADC in the same RAM-backed environment;
3. unset Vertex variables;
4. remove only `/dev/shm/chronicle-vertex-adc`;
5. verify no credential-shaped material exists on persistent storage;
6. hash and record restart-critical persistent state;
7. report Pod rate, accumulated compute estimate, volume state, and options;
8. stop/release compute when authorized or under the two-hour no-response rule;
9. retain the network volume unless the owner explicitly orders deletion.

## Required Deliverables

Update:

- `md/handoffs/reports/WP-5.2B3B.1-execution-progress.md`;
- `md/research/WP-5.2B3B.1-prompt-optimization-activity-log.md`;
- `md/development-ledger.md` only to `Ready for PM validation`.

Create:

- `md/handoffs/reports/WP-5.2B3B.1C-gepa-pilot-and-bounded-search-completion-report.md`;
- a privacy-safe article evidence addendum covering method, negative and
  positive findings, complete denominators, cost, search effort, failures, and
  limitations without exposing prompt text or private identities.

The completion report must include:

- exact clean application commit and environment versions;
- restored persistent-state verification;
- RunPod hardware, region class, actual price, timing, and retained storage;
- ADC method and cleanup evidence without credential/project values;
- proposer identity, region, calls, retries, tokens, latency, and cost;
- candidate-model invocations, retries, tokens, latency, and compute cost;
- pilot gate components and pass/fail decision;
- continuation accounting when applicable;
- complete candidate/failure/privacy/eligibility denominators;
- P0 comparison by model and task;
- shortlist or explicit no-improvement outcome;
- proof of zero fixed-judge calls and zero holdout access;
- cache/resume/append-only and immutability evidence;
- resource lifecycle and retained-volume status;
- tests, lint, package, privacy, tracking, and Git checks;
- exact remaining budget and next authorization boundary.

## Validation

At minimum:

```powershell
poetry env info --path
poetry run python -c "from bench.optimization.compat import verify_compatibility; assert verify_compatibility()['compatible'] is True"
poetry run pytest tests/test_bench_optimization.py -q
poetry run pytest -q
poetry run ruff check .
poetry check
poetry run python -m bench inspect --config <ignored-config>
poetry run python -m bench verify --config <ignored-config> --package <each-shortlist-package>
git diff --check
git diff --cached --name-only
git ls-files .chronicle
```

Also verify the pushed CI matrix remains green at the application commit used
for execution.

## Stop Conditions

Stop without unapproved retry or lifecycle action if:

- the repository or recovered authority is dirty, missing, or hash-invalid;
- P0 is not the unique GEPA parent;
- prior GEPA evidence or proposer usage exists unexpectedly;
- any holdout path or content would be accessed;
- config differs beyond the current application commit;
- model/runtime/context/split/scoring/privacy/budget identity differs;
- private prompt or response content would enter tracked files;
- ADC cannot remain temporary and RAM-backed;
- Vertex resolves to a different project, region, provider, or model;
- a call would exceed any persisted reservation or owner ceiling;
- output repair, semantic retry, or untracked provider retry is required;
- append-only/current-pointer authority cannot be proven;
- the pilot criteria fail;
- returned persistent evidence cannot be hash-verified.

Do not delete resources at a stop condition. Preserve evidence, report the
reversible options, and await owner direction while applying the two-hour
stop-compute/retain-data rule.

## Owner Authorization

The handoff records scope but is not itself consent to disclose private data or
spend money. Before execution, the owner must send the following statement to
the executor in the task:

```text
I authorize WP-5.2B3B.1C to send only the frozen six-train/four-validation
development inputs, task prompts, response schemas, deterministic diagnostics,
and FABLE-reference-derived feedback required by GEPA to Google Vertex AI
vertex_ai/gemini-3.1-pro-preview in global through LiteLLM and temporary user
ADC. I authorize the first real GEPA proposer call without another synthetic
provider probe, one configured infrastructure retry, and ordinary Vertex
charges within the existing persisted remaining ceilings: 244 logical calls,
12,249,977 input tokens, 1,959,729 output/reasoning tokens, and US$49.016702.

I authorize compatible RunPod compute for the pilot and automatic continuation
only if the frozen pilot criteria pass, within the existing persisted remaining
limits of 11.128676 compute hours and US$17.282016 compute cost. Use RunPod
CLI/API first, attach the retained private network volume, and ask me only when
allocation, the first SSH connection, or interactive ADC browser authentication
requires owner action.

Do not open or transfer the holdout. Do not call the fixed Gemini judge during
GEPA. Do not rerun P0, BootstrapFewShot, or recovery. Do not change provider,
model, region, credentials, prompts outside the four system prompts, scoring,
context, models, split, retry policy, or budgets. Never delete the Pod, network
volume, repository, models, or results without my explicit current instruction.
If I do not respond for two hours while paid compute is running, stop/release
compute after verifying persistent state, but retain the network volume and all
data.
```

## Acceptance Criteria

1. Execution starts from the accepted recovered readiness with P0 as parent.
2. Temporary Vertex ADC is RAM-backed and removed; no credential/project value
   reaches Git, logs, bundles, or persistent storage.
3. The pilot is terminal and fully accounted under all frozen limits.
4. Continuation occurs only after the durable component-wise pilot gate passes.
5. Every candidate position and provider call is append-only and accounted.
6. No fixed-judge call or holdout access occurs.
7. P0 and all prior evidence remain unchanged.
8. A privacy-eligible immutable shortlist or explicit no-improvement result is
   returned and locally hash-verified.
9. Compute lifecycle follows owner instructions; the retained volume is never
   deleted implicitly.
10. Focused/full tests, Ruff, Poetry, package, privacy, tracking, and CI checks
    pass.
11. Tracked reports are privacy-safe and complete enough for later article
    analysis.
12. All changes remain unstaged and uncommitted for PM validation.
