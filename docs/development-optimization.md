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
GEPA's own ignored, resumable working state uses its pinned cloudpickle serializer because DSPy
creates dynamic signature classes that standard pickle cannot serialize. This internal optimizer
checkpoint is never accepted as a candidate/result package and is never loaded by Chronicle's
package verification path; accepted Chronicle artifacts remain state-only JSON.

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

For local Windows scoring, diagnostics, or proposer work launched from VS Code
or Codex, use [`windows-vertex-adc.md`](windows-vertex-adc.md). It resolves ADC
from the active `CLOUDSDK_CONFIG`, prevents a stale explicit credential path
from winning, and requires the environment bootstrap and Python command to run
inside the same process boundary.

Future handoffs that authorize a local Vertex call must cite that guide and
name the same-process environment bootstrap as a precondition. Do not rediscover
the VS Code/Codex inheritance boundary through repeated provider probes.

BootstrapFewShot is fixed at one labeled demo, one bootstrapped demo, and one round. Its package is
private and ineligible unless the same promotion scanner passes. The production candidate adapter
replays packaged examples as ordered user/assistant messages before the current user request; they are
not discarded when DSPy compilation ends. GEPA is instruction-only, uses a
fixed seed and Pareto selection, enables detailed statistics, and retains candidate parents, validation
subscores, discovery counts, best outputs, usage, latency, failures, and search logs.

Mixed-task GEPA runs use Chronicle's deterministic trace-aligned component selector. It starts at the
candidate's round-robin cursor and selects the first component represented by an eligible trace in the
captured reflection minibatch; the cursor then advances past that component. A minibatch with no
eligible component trace fails explicitly. Bounded lifecycle qualifications may set all three tracked
controls: `gepa_train_conversation_limit`, `gepa_validation_conversation_limit`, and
`gepa_max_candidate_proposals`. Train and validation limits must be supplied together, select manifest
entries in frozen order without content inspection, and participate in configuration authority.

`add_format_failure_as_feedback` is explicitly disabled. DSPy's enabled behavior embeds the raw
malformed completion in reflection data, which is incompatible with Chronicle's bounded sanitized
feedback boundary. Schema/JSON failures remain terminal scored failures represented by deterministic
diagnostic categories; output is not repaired, semantically retried, or manually reinterpreted.
Chronicle explicitly wraps DSPy's normal `ChatAdapter` to `JSONAdapter` format fallback. Only DSPy's
explicit `AdapterParseError` may trigger the one JSON fallback; LM/provider errors, callback errors,
`ValueError`, `TypeError`, configuration failures, and unexpected exceptions propagate without a
second transport. Each score position and actual transport receive separate append-only ignored
evidence with adapter, fallback
status, sanitized terminal state, latency, and provider usage or an explicit unavailable marker. A
JSON fallback is a second task invocation, never a provider retry. Candidate LMs keep
`num_retries=0`; infrastructure retries remain a separate budget field. GEPA reservations therefore
allow two transports per logical score position and reconciliation fails closed if the transport
ledger and DSPy task-call callbacks differ.

Ordinary `LiteLLMCandidateAdapter` evaluation has a separate per-case journal below the ignored run
root. Before every candidate transport it appends a request intent bound to the complete request
SHA-256 without persisting request text. It then appends the transport result, sanitized configured
and actual route identities, finish and latency availability, normalized usage and provider-cost
availability, and the terminal `CaseOutcome`. Provider failures and infrastructure retries are
separate attempts. Response identity, usage adaptation, output validation, case persistence, and
batch-finalization interruptions remain typed append-only evidence instead of being converted into
model-quality failures.

A resumed batch verifies every journal file against its canonical bytes and event hash. It skips
only terminal cases whose request hash still matches, refuses a later call intent for a completed
case, and rebuilds the batch from terminal journals in frozen manifest/task order. Historical and
incremental usage are kept separate: result accounting includes the complete journal, while budget
reconciliation charges only transports added since the prior interrupted checkpoint. A completed
batch replay performs zero transports and leaves the journal byte-stable. Tampered, foreign,
duplicate, ambiguous, incomplete, or request-mismatched evidence fails closed before a new call.

Version 2 optimizer configurations must declare `gepa-reliability-v1`. This optimization-only scalar
orders provider-invalid/empty output at `0.0`, invalid JSON at `0.1`, schema-invalid output at `0.3`,
evidence-invalid output at `0.6`, cross-field/date-invalid output at `0.8`, and fully valid output at
`0.999` plus FABLE agreement multiplied by `0.000001`. Every invalid stage stays below `0.999`.
Only Pydantic model-output `ValidationError` maps to schema-invalid. Unknown schema identities,
application defects, and unrelated exceptions propagate and stop optimization without another call
or proposal decision.

The score contract participates in configuration, optimizer-authority, result-authority, and GEPA
state/cache identity. Historical version 1 configurations retain their prior scalar and identity.
This gradient exists only to guide reflection; shortlist eligibility and final promotion still use
the unchanged strict deterministic reliability gates.

Version 2 also explicitly disables GEPA merge proposals so every bounded proposal has one
proposer-selected component, one pre-decision envelope, and an exactly reservable call path;
historical version 1 behavior is unchanged.

Every GEPA proposal is observed through GEPA's public callbacks. After the proposal minibatch is
scored, but before GEPA accepts or rejects it, Chronicle writes a private append-only envelope under
the ignored run root. It binds proposal ordinal, optimizer/run identity, selected component, parent
identity, private proposed text, prompt hashes and byte delta, demonstrations, example-local IDs,
both score vectors, bounded category/path feedback, privacy evidence, and an event hash/version.
Acceptance or rejection is a separate append-only decision record. Rejected proposals remain
auditable, interrupted envelopes remain pending until a decision is appended, and tampered,
duplicate, foreign, ambiguous, privacy-ineligible, or incompletely reconciled evidence fails closed.
The proposed text is redacted from GEPA's ordinary logger and must not enter tracked reports.

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
