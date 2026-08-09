# Development prompt optimization

The optimizer is a development-only extension of the private benchmark harness. Install it with:

```console
poetry install -E optimization
```

Normal Chronicle search, MCP, AI tasks, and benchmark commands do not import DSPy or GEPA. The
optimization extra pins DSPy 3.3.0 and its compatible GEPA 0.1.1 integration on Python 3.11-3.14.
`python -m bench preflight` rejects a different version or result shape.

## Safety model

The four accepted system prompts are the only mutable fields. Candidate packages bind immutable
task, schema, selector, finalizer, user-prompt, generation, context, model, and artifact identities.
BootstrapFewShot packages additionally bind at most one labeled and one bootstrapped demonstration
per task. Each demonstration records its frozen train case/model authority and hashes its selected
input and response as part of the stable candidate identity.
Packages and state use JSON. DSPy state is saved with `save_program=False` and loaded with
`allow_pickle=False` and `allow_unsafe_lm_state=False`.

Optimization configuration is strict and fail-closed. Paths containing `holdout` are rejected.
Qwen and Phi each run with context 8,192, concurrency one, at most one infrastructure retry, and no
semantic retry or output repair. Budget enforcement covers candidate, task-invocation, proposer-call,
compute-time, proposer-cost, compute-cost, and retry accounting.

GEPA receives only structured facts such as schema path, invalid enum, evidence mismatch, cross-field
violation, date mismatch, label mismatch, timeout, or context boundary. Fixed-judge rationale and raw
provider errors are not feedback. The reliability-first metric is lexicographic; its scalar adapter
cannot trade semantic gains for a loss in valid outputs.

Before promotion, each complete four-prompt package, including any demonstration input/output, is
scanned against all ten development inputs and
references, credential/environment values, URLs, paths, long identifiers, and eight-word source
n-grams. A failing candidate is disqualified and is never rewritten into eligibility.

## Local lifecycle

Start from [the privacy-safe template](../bench/optimization.default.yaml), replacing placeholder
paths and hashes only in an ignored private copy.

```console
poetry run python -m bench preflight --config <private-optimization.yaml>
poetry run python -m bench dry-run --config <private-optimization.yaml>
poetry run python -m bench package --config <private-optimization.yaml> --output <p0.json>
poetry run python -m bench verify --config <private-optimization.yaml> \
  --package <candidate.json>
poetry run python -m bench inspect --config <private-optimization.yaml>
```

`optimize` and `resume` are the tracked provider-facing execution entry points. They require all four
explicit flags: `--allow-remote`, `--confirm-private-eval`, `--confirm-proposer-disclosure`, and
`--confirm-paid-budget`. The orchestrator verifies the clean pinned application commit and complete
development authority, persists and consumes an append-only execution authority, reserves every
candidate/proposer/task/retry/token/time/cost allowance before its adapter call, and reconciles actual
usage afterward. Missing or inconsistent usage fails closed while retaining the reservation. No
credential or Google Cloud project value is stored in YAML. The selected `vertex-adc` route declares
only the names `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `VERTEXAI_PROJECT`,
`VERTEXAI_LOCATION`, and `GOOGLE_GENAI_USE_VERTEXAI`; production resolves their values and checks ADC
only after authorization has been consumed. The paired project variables must agree, both locations
must resolve to `global`, and the Vertex enable flag must be true. Resume reloads the hashed budget/run state and strict
latest `current.json` attempt authorities while preserving interrupted history.

A new `optimize` invocation stops after a durable four-hour/12-GEPA-maximum pilot checkpoint. The
checkpoint hashes the completed pilot result IDs, budget state, achievable next-operation count, and
the four predeclared continuation criteria: safety/privacy/accounting/resume validity; at least one
GEPA result no worse than P0 on validation total, worst-model, and minimum-task validity; distinct
privacy-eligible prompts; and a next operation projected inside every total ceiling. A failed decision
is terminal `pilot-no-improvement`. A passing decision allows `resume` to continue without rewriting
completed candidates, results, or attempt authorities. Continuation stops on optimizer exhaustion,
the 40-candidate maximum, or before the first complete candidate/proposer/evaluation operation that
would exceed the 3,000-task, 12-hour, proposer-call/token/cost, or compute-cost ceilings.

## RunPod Operator Boundary

RunPod work is CLI-first. Use supported RunPod CLI/API operations for allocation, inventory,
lifecycle state, pricing metadata, and transfer where available; use standard SSH/SCP when the
installed CLI lacks the operation. Do not substitute a custom Python operator script for a supported
CLI command.

Immediately after allocation, the owner runs the provider-issued SSH command and confirms an
interactive shell. Do not declare a Pod inaccessible or change its lifecycle state before that check.
Decide before allocation whether recoverable state belongs on a persistent volume, especially when
the owner may release compute while retaining the repository, model cache, private bundle, and
results.

A failed check freezes further experimental calls but does not authorize teardown. The executor must
not stop, restart, release, delete, resize, or detach a Pod or volume without explicit owner direction
for that action. Report state, spend, storage location, and reversible options first. In particular,
never infer deletion authority from task completion, cleanup text, cost guidance, or a semantic model
miss. Persist response metadata and usage before semantic assertions; an unexpected schema-valid
label is model-quality evidence rather than an infrastructure failure unless the experiment contract
explicitly says otherwise.

BootstrapFewShot explicitly uses the candidate model as teacher, so those task calls are reserved and
accounted as candidate-model disclosure. The selected GEPA proposer is Google Vertex AI
`vertex_ai/gemini-3.1-pro-preview` in `global`, authenticated only with Application Default
Credentials. Its tracked profile permits at most 250 calls, 12.5 million input tokens, and 2 million
output tokens including separately reported reasoning tokens. At US$2/million input and
US$12/million output the maximum token envelope is US$49 beneath the US$50 hard ceiling. One
infrastructure retry, no semantic retry, no repair, temperature zero, reasoning `none`, cache disabled,
and concurrency one are fixed. Provider/model, credential mode and environment-variable names,
resolved location, settings, pricing, and ceilings participate in configuration, authorization, cache,
trial, and result authority; environment values and ADC material do not. The older
`api-key-environment` mode remains supported for compatible providers but is not the selected route.

The proposer and later fixed judge are both Gemini 3.1 Pro. The judge remains outside the optimization
loop, and no fixed-judge score or rationale reaches BootstrapFewShot or GEPA. This same-family design
creates evaluation-bias risk and must be disclosed in the completion report and any article; it does
not invalidate deterministic schema, evidence, reliability, runtime, or cost measurements.

For RunPod GEPA execution, use the accepted temporary user ADC procedure in
[`runpod-vertex-adc.md`](runpod-vertex-adc.md). It stores ADC only under
`/dev/shm`, requires no Gemini API key or Pod restart, and defines the cleanup
and persistent-volume boundary.

BootstrapFewShot is fixed at one labeled demo, one bootstrapped demo, and one round. Its package is
private and ineligible unless the same promotion scanner passes. The production candidate adapter
replays packaged examples as ordered user/assistant messages before the current user request; they are
not discarded when DSPy compilation ends. GEPA is instruction-only, uses a
fixed seed and Pareto selection, enables detailed statistics, and retains candidate parents, validation
subscores, discovery counts, best outputs, usage, latency, failures, and search logs.

Context-fit evidence uses the same messages and response schema as the production adapter. For every
required development case it conservatively estimates the serialized system prompt, packaged
demonstrations, selected input/user prompt, schema/tool surface, fixed wrapper allowance, and output
token allowance. The maximum case envelope is persisted in the result and must be at most 8,192
tokens for promotion. Inspection aggregates monotonic wall time for every BootstrapFewShot/GEPA
attempt—including interrupted history—separately from candidate batch latency; no provider-specific
latency is fabricated when DSPy history lacks it.

After a terminal pilot, config-aware verification binds a candidate to accepted P0 contracts, its
separate immutable result envelope, clean commit, run/config, split manifests, model artifacts,
proposer/optimizer identities, terminal trial authority, accounting, and privacy-scanner provenance.
Shortlist export ranks the complete GEPA results by the declared lexicographic metric and applies P0
total-valid, model/task reliability, privacy, terminal-accounting, prompt-fit, and lineage controls.
It exports immutable P0 plus three to five diverse eligible GEPA packages, or an explicit
`no-improvement` artifact when fewer than three qualify:

```console
poetry run python -m bench export-shortlist --config <private-optimization.yaml> \
  --output <private-shortlist-directory> --limit 5
```

Transfer only the approved development subset, four-task references needed by the metric, exact model
artifacts, selected P0 catalog, private config, code/environment lock, and checksummed return paths.
Never transfer the holdout, live database, unrelated conversation history, judge credentials, or
historical packages not required as controls. Verify returned checksums locally before deleting the
pod, then remove cloud volumes and clear the bounded Vertex runtime environment.

## Compatibility sources

The bridge follows the pinned [DSPy GEPA API](https://dspy.ai/api/optimizers/GEPA/overview/),
[BootstrapFewShot API](https://dspy.ai/api/optimizers/BootstrapFewShot/), and
[safe state-only serialization guidance](https://dspy.ai/tutorials/saving/). The compatibility test
asserts the exact GEPA result fields exposed by DSPy 3.3.0 rather than relying on an older example.
