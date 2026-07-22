# Development Evaluation Operator Runbook

This development-only workflow keeps candidate generation separate from local reference
scoring. Input bundles and candidate packages are private. Never put them in Git or transfer
them without owner approval.

## Staged local preparation

Copy `bench/evaluation.default.yaml` to the ignored private configuration directory as
`evaluation.yaml`, copy `bench/ai-models.evaluation.default.yaml` beside it as `ai-models.yaml`,
and replace all placeholders with accepted identities. Use a unique run ID for every output path.

Start with the first conversation in frozen order. This creates exactly four cases, one for each
accepted AI task, without inspecting conversation content or creating input/reference subsets:

```powershell
poetry run python -m bench prepare --config .\.chronicle\eval\dev-v1\config\evaluation.yaml --conversation-limit 1
```

After the short smoke has passed local verification, deterministic scoring, and any separately
authorized judge review, use a new run ID and increase the prefix for a small pilot:

```powershell
poetry run python -m bench prepare --config .\.chronicle\eval\dev-v1\config\evaluation.yaml --conversation-limit 3
```

Only after the pilot passes should a new run ID be used for the complete frozen corpus. Omitting
the option preserves the 30-conversation/120-case behavior:

```powershell
poetry run python -m bench prepare --config .\.chronicle\eval\dev-v1\config\evaluation.yaml
```

Every stage reads the complete accepted input directory as authority and selects only its declared
frozen prefix. Verification and scoring independently reconstruct that same prefix from the
complete local corpus and complete FABLE reference directories. Never copy, rewrite, or make
subset directories for either authority source.

The command prints the scoped case count, content identity, archive transfer hash, and privacy warning.
Stop here until the owner confirms the target machine, transfer method, control, temporary
storage, deletion timing, and pinned candidate readiness. Transfer is manual.

## Candidate generation

On the approved candidate machine, verify the repository environment and local runtime first:

```powershell
poetry env info --path
lms ls --json
lms server status
poetry run python -m bench generate --bundle <copied-input-bundle> --config <remote-candidate-config>
```

The configured GGUF file is hashed before the first model call. Ordinary reruns resume matching
completed attempts. `--retry-failures` appends a new attempt without changing the baseline.
Return the package manually and compare its printed transfer hash on both machines.

Generation also measures `git rev-parse HEAD` and tracked dirty state before the first call. The
preferred remote checkout is clean and exactly matches the commit pinned by the prepared bundle.
Untracked private evaluation files do not affect this check. A dirty tracked checkout is rejected
unless the owner explicitly approved and pinned its deterministic tracked-diff hash.

Runtime version, execution device, advertised context, and the GGUF-to-loaded-model relationship
remain operator-attested preflight facts. Hashing a GGUF does not prove LM Studio loaded it. Compare
`lms ls --json`, loaded model ID, artifact identity, and returned provider/model provenance.

## Local verification and deterministic scoring

```powershell
poetry run python -m bench verify --package <returned-candidate-package> --config .\.chronicle\eval\dev-v1\config\evaluation.yaml
poetry run python -m bench score --package <returned-candidate-package> --config .\.chronicle\eval\dev-v1\config\evaluation.yaml --deterministic-only
```

These commands do not contact the candidate runtime or a judge. Verification reconstructs all
cases from the local accepted inputs and contracts before accepting the returned package.

## Authorized Vertex AI scoring

Only after PM review and explicit owner approval:

```powershell
poetry run python -m bench score --package <returned-candidate-package> --config .\.chronicle\eval\dev-v1\config\evaluation.yaml --with-judge --allow-remote --confirm-private-eval
```

The accepted judge route is `vertex_ai/gemini-2.5-flash` using Google Application Default
Credentials and externally supplied Vertex project/location environment variables. No
`GEMINI_API_KEY` is required and there is no API-key fallback. Before private judging, run the
four-task synthetic exact-schema gate and require four accepted results.

The Gemini judge profile sets `reasoning_effort: none`. This provider-neutral LiteLLM setting
disables Gemini 2.5 Flash thinking for the bounded structured verdict. Reasoning effort is a
strict optional model-profile field; omitted local profiles preserve their prior request and cache
identity. Judge failures retain only normalized finish category, response presence/character
count, and allowlisted numeric usage counters—never response content.

The provider-facing controlled-generation schema is deliberately separate from the strict
application `JudgeResult` schema. The provider schema uses the verified Vertex JSON Schema
subset and fixes the exact rubric dimensions for each task; application validation remains
authoritative for identity, rationale, evidence, and all cross-field checks. Judge cache identity
binds both schema names, versions, and hashes, plus the response normalizer and request-builder
versions and the task-specific dimension identity.

Selected source, candidate result, and the FABLE reference are disclosed to the configured remote
judge. Candidate model identity is not included in judge prompts. Matching successful results
resume without another disclosure. Historical failed runs are immutable and retained. A private
retry uses a fresh approved scoring run identity, or `--retry-judge-failures` where an explicit
append-only retry of the same contract is intended.

To retry only cached judge failures while preserving their baseline attempts, add
`--retry-judge-failures`. Successful matching judge results remain cached and are not retried by
that option.

For verification that must never disclose again, add `--judge-cache-only` alongside the three
judge authorization flags. Any cache miss fails before provider execution. Same-package reruns
recompute deterministic metrics, preserve accepted judge metrics and judged manifest identity,
and render aggregate JSON/Markdown canonically with one judge section.

After local verification succeeds and the owner confirms retention is no longer required,
manually delete the remote input bundle, generation work, package copy, and invalid raw output.
Inspect each exact path before deletion; cleanup is intentionally not automated.
