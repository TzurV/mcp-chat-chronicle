# WP-5.2A5.1 - Remaining LM Studio Candidate Qualification

## Status

Ready for execution after the manager commits this handoff and the tracked checkout is clean.

## Executor role

Act as the implementation and evaluation executor. Work with the owner interactively for model
downloads or license-gated access, but do not ask the owner to commit files. Leave all delivery
changes unstaged and uncommitted for manager validation.

Read `md/agent-operating-notes.md` before running commands. Keep Poetry in this repository's
`.venv`, avoid piped PowerShell commands, and run Windows sandbox-sensitive reads sequentially.

## Objective

Qualify the three remaining approved LM Studio/OpenAI-compatible local candidates, one at a time,
against the existing four Chronicle AI-task contracts:

1. Microsoft Phi-4 Mini Instruct;
2. Meta Llama 3.2 3B Instruct;
3. Google Gemma 4 E2B Instruct, with Gemma 3 4B IT allowed only as the documented compatibility
   fallback.

The output is a defensible admission decision for the next common benchmark. This work package
does not run the 40-case pilot or 120-case comparison.

## Accepted background

Treat these as immutable accepted foundations:

- WP-5.1 configurable YAML/LiteLLM task infrastructure;
- WP-5.1.1 task prompts, selectors, schemas, and finalizers;
- WP-5.1.2A/B frozen 30-conversation, 120-case private development corpus and FABLE silver
  references;
- WP-5.2A1 Llama 3.2 1B evaluation-floor integration;
- WP-5.2B1 through WP-5.2B1.4 benchmark, packaging, deterministic scoring, fixed-Pro judging,
  cache, privacy, and provenance behavior;
- accepted common local settings: LM Studio/OpenAI-compatible route, configured context 8,192,
  concurrency/parallelism 1, temperature 0, and task-owned output limits.

Accepted complete-arm context:

| Candidate | Schema-valid | Observed wall span | Role |
|---|---:|---:|---|
| Vertex Gemini 3.5 Flash | 112/120 | 10m 39.524s | hosted cloud control |
| Qwen3.5-4B Q4_K_M | 84/120 | 4h 43m 30.782s | accepted local control |
| Llama 3.2 1B Q4_K_M | 57/120 | 42m 13.023s | evaluation floor |

These values are context only. Do not rerun, rewrite, or repackage accepted WP-5.2B1.4 artifacts.

## Scope

For each candidate:

1. verify official model identity and license/access requirements;
2. locate a reputable LM Studio/llama.cpp-compatible GGUF conversion;
3. pin model repository, revision, filename, byte size, SHA-256, quantization, architecture,
   parameter size, advertised context, chat template, and license privately;
4. record LM Studio version/commit, loaded identifier, configured context, parallelism,
   execution-device class, and local hardware class;
5. prove the existing generic LM Studio/LiteLLM integration can call the model;
6. run the four accepted tasks on one synthetic conversation;
7. run the same four tasks on one deterministic short frozen development conversation;
8. classify every result as schema-valid success or explicit captured failure;
9. decide whether the model qualifies for a later common benchmark.

Use the same synthetic input and the same frozen conversation for every candidate. Freeze their
identities before inspecting candidate output. Keep exact identifiers and all private source/output
under `.chronicle/eval/dev-v1/`.

## Out of scope

- no prompt, selector, schema, finalizer, evidence-policy, task-version, or reference change;
- no few-shot examples or prompt tuning;
- no output repair, JSON rewriting, truncation repair, or post-hoc context change;
- no 40-case or 120-case run;
- no Vertex candidate or judge call;
- no Chrome Gemini Nano, Edge model, Phi Silica, Foundry Local, Ollama, or custom runtime adapter;
- no custom model-specific application adapter merely to preserve a candidate;
- no article writing or metric selection;
- no live/frozen database write;
- no commit or push.

## Owner authorization and operator interaction

The owner has approved qualification of the three named model families and local execution on the
current machine. The executor may:

- inspect public model cards and conversion metadata;
- download the selected public GGUF artifacts after reporting model name, quantization, download
  size, expected disk use, source, and license to the owner;
- start/check LM Studio and load/unload the exact selected local artifact;
- create ignored private profiles, smoke inputs, outputs, logs, manifests, and reports;
- inspect the accepted frozen inputs needed for the bounded private smoke.

Do not accept gated license terms on the owner's behalf. When a repository requires explicit
license acceptance or authentication, give the owner the exact official page and wait for the
owner to complete that action.

No private data is authorized for a new remote provider in this package.

## Candidate order and stopping rules

Run candidates in this order.

### Candidate 1 - Phi-4 Mini Instruct

- Official identity: `microsoft/Phi-4-mini-instruct`.
- Treat the official 3.8B model and its advertised 128K context as metadata only.
- Run the common comparison at configured context 8,192.
- Select a reputable Q4-class GGUF supported by the installed LM Studio/llama.cpp runtime.
- Confirm that the chat template and structured-output request are interpreted correctly.

### Candidate 2 - Llama 3.2 3B Instruct

- Official identity: `meta-llama/Llama-3.2-3B-Instruct`.
- Keep quantization as close as practical to the accepted Q4_K_M local controls.
- Use the same 8,192 context and parallelism 1.
- Do not infer compatibility from the accepted 1B model; run the complete qualification matrix.

### Candidate 3 - Gemma

- Preferred identity: `google/gemma-4-E2B-it`.
- First verify that the installed LM Studio/llama.cpp version has reliable architecture, chat
  template, text-only prompt, and structured-output support for the selected Gemma 4 GGUF.
- Gemma 4's effective-parameter label is not its storage/memory footprint; record both effective
  size and actual artifact/runtime memory characteristics.
- If no reputable compatible GGUF exists or the runtime cannot execute it reliably, stop the
  Gemma 4 attempt and document the exact compatibility boundary.
- Only then use the approved fallback `google/gemma-3-4b-it` with a comparable Q4-class GGUF.
- Do not implement a custom Gemma adapter in this package.

Complete each candidate's qualification and evidence before downloading or starting the next one.
A failure does not block testing the later candidates.

## Preflight

1. Require a clean tracked checkout and record full HEAD.
2. Prove `poetry env info --path` resolves to this repository's `.venv`.
3. Confirm WP-5.2B1.4 private package/database/historical hashes still match accepted baselines.
4. Confirm the frozen database opens read-only and remains at 711 conversations / 28,370 messages.
5. Record available disk space, AC-power state, and sleep policy.
6. Record installed LM Studio version/commit and currently available models.
7. Create unique ignored qualification directories for each candidate.
8. Freeze the common synthetic input and one short frozen conversation before candidate output is
   inspected.
9. Hash the accepted task/model templates and selected inputs.

## Artifact selection requirements

Before downloading each artifact, write a privacy-safe operator note containing:

- official base model and model-card URL;
- GGUF conversion repository and publisher;
- exact revision/commit when available;
- quantization and expected file size;
- license and any gating requirement;
- advertised context;
- expected RAM/storage fit on the recorded machine;
- why this conversion is reputable enough for the comparison.

After download, independently hash the artifact and record the exact local size privately. Never
track a model file, private model path, or machine-specific identifier.

If artifact identity, license, or conversion provenance cannot be established, mark that candidate
`not qualified - provenance` and continue.

## Generic transport qualification

For each loaded model:

1. confirm `/v1/models` exposes the intended identifier;
2. make one synthetic direct OpenAI-compatible request;
3. make one synthetic request through the application-owned LiteLLM client;
4. verify reasoning/thinking controls do not consume the answer budget or return empty content;
5. verify a strict structured-output request either succeeds or produces an actionable captured
   failure;
6. record timeout, latency, finish reason, usage availability, and provider/model identity without
   raw output in tracked files.

Use only private synthetic evidence for troubleshooting. A generic transport defect may be fixed
in shared code under the failure policy below. A model-specific incompatibility is an evaluation
result, not permission to add a custom adapter.

## Qualification matrix

Run exactly eight bounded task calls per candidate:

| Input | Summary | Work mode | Last activity | Title assessment |
|---|---:|---:|---:|---:|
| Common synthetic conversation | 1 | 1 | 1 | 1 |
| Common short frozen conversation | 1 | 1 | 1 | 1 |

For each position capture:

- terminal status;
- schema/evidence/cross-field validity;
- failure boundary;
- latency;
- prompt/completion/total usage when available;
- actual provider/model identifier;
- context estimate and context failure;
- finish reason and retry count;
- private raw invalid response when produced.

Do not send FABLE references during candidate generation. Deterministic contract validation is
required; semantic Gemini judging is deferred to the later common benchmark.

## Admission policy

A stronger comparison candidate qualifies only when:

1. all eight positions are terminal and accounted for;
2. transport and provenance are coherent;
3. all four task types produce a schema-valid result on both the synthetic and frozen inputs,
   yielding 8/8 schema-valid outputs;
4. evidence IDs, dates, cross-field constraints, and output lengths validate;
5. no task depends on output repair or a model-specific application adapter;
6. the runtime is operationally feasible on the current machine.

If a candidate misses 8/8 because of an apparent stochastic formatting failure, do not silently
retry until it passes. Preserve the result and classify the candidate as not qualified under the
current contract. The manager may later approve a separate reproducibility check.

Report both qualified and rejected candidates. Do not substitute an optional model automatically.

## Failure and fix policy

Use at most two focused implementation cycles for a genuine generic defect in:

- the shared LM Studio request path;
- portable model-profile handling;
- actionable error normalization;
- strict-schema transport shared by multiple models;
- Windows-safe private artifact writing.

Every tracked fix requires:

- a focused regression independent of private model content;
- focused tests, full suite, Ruff, and `git diff --check`;
- manager review and commit before qualification resumes from a new clean HEAD;
- honest split provenance for calls made before and after the fix.

Do not change context, task prompts, output limits, reasoning policy, quantization, or runtime
mid-candidate without PM approval. Ordinary model-quality failures are preserved, not fixed.

## Completion report

Write exactly:

`md/handoffs/reports/WP-5.2A5.1-completion-report.md`

Required sections:

1. status and executive summary;
2. clean preflight and immutable-baseline evidence;
3. common input/task/settings contract;
4. Phi artifact/runtime/transport and 8-case results;
5. Llama 3B artifact/runtime/transport and 8-case results;
6. Gemma 4 compatibility decision, selected Gemma artifact, and 8-case results;
7. complete 24-position accounting;
8. schema/evidence/cross-field/failure matrix;
9. latency/usage/runtime comparison;
10. qualified/rejected admission decisions with reasons;
11. implementation defects/fixes, if any;
12. privacy, immutability, and tracking checks;
13. recommendation for the next 40/120-case handoff;
14. line-by-line acceptance checklist.

Do not include private IDs, source, prompts, outputs, paths, hashes, credentials, account identity,
or gated-license data in the tracked report.

## Required validation

When code changes:

```powershell
poetry env info --path
poetry run pytest tests/test_ai_adapter.py tests/test_bench.py -q
poetry run pytest
poetry run ruff check .
poetry check
git diff --check
git diff --cached --name-only
git status --short
```

When no code changes, run relevant focused regression/help checks plus Ruff, `poetry check`,
`git diff --check`, privacy/tracking checks, and immutable-baseline verification.

## Completion and commit ownership

- Executor status is `ready for PM validation` only when all three candidate decisions are
  complete and the report exists.
- Leave everything unstaged and uncommitted.
- The manager validates the completion report against this handoff.
- The manager commits only after explicit owner instruction.

