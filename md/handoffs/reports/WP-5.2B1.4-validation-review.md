# WP-5.2B1.4 Validation Review

## Review status

Accepted after report-only rework on 2026-07-23.

The evaluation execution is complete and the reported accounting is coherent:

- 400/400 candidate positions are terminal;
- the three complete arms use the same 120 cases;
- Qwen-40 is the accepted first-40 checkpoint;
- all four packages verify and score deterministically;
- all schema-valid candidates have a terminal fixed-Pro outcome;
- all four cache-only replays report zero additional calls;
- repository validation and private-artifact immutability passed.

No candidate generation, judging, retry, model call, package mutation, or private-corpus change is
authorized or required by this review. Rework only the tracked completion report using existing
private aggregate evidence.

## Blocking reporting gaps

### 1. Complete performance timing

The handoff requires wall time and overall and per-task p50/p95 latency. The report currently gives
only per-task p50/p95 values.

For Gemini-120, Llama-120, Qwen-120, and the separately labelled Qwen-40 checkpoint, add:

- observed candidate-generation wall time;
- overall candidate latency p50 and p95;
- existing per-task p50 and p95;
- the measurement source and whether wall time includes pauses, retries, wrapper interruption, or
  idle time;
- a clear distinction between elapsed wall time and summed per-case latency.

If an interruption prevents a reliable continuous wall-time value, report the best reproducible
measurement available, label it explicitly, and explain the limitation. Do not invent or silently
estimate a duration.

### 2. Publishable deterministic classification detail

The handoff requires confusion matrices and per-label support, precision, and recall. The report
currently includes only exact agreement and a prose summary.

Add privacy-safe aggregate tables for each complete arm covering:

- work-mode classification;
- last-activity status;
- title-fit classification.

Include the confusion counts and per-label support, precision, and recall already present in the
private deterministic artifacts. Keep Qwen-40 separate from the complete-arm comparison. It is
acceptable to use compact tables or a clearly structured appendix, but do not replace the
required values with a pointer to private evidence.

### 3. Judge metrics by task

The handoff requires primary-judge dimension means by task. The report currently gives selected
overall dimension means only.

For each complete arm, add a privacy-safe task-by-dimension table derived from completed judge
results. At minimum, show the applicable rubric dimensions for:

- conversation summary;
- work-mode classification;
- last activity;
- title assessment.

Retain completed/failed/skipped accounting beside these values so readers do not mistake means
over schema-valid, successfully judged outputs for whole-corpus scores. Keep the three retained
terminal judge failures visible.

### 4. Reproducible local-runtime context

The report needs enough privacy-safe provenance to interpret the local performance comparison.
Expand the provenance section to include:

- Llama model name, parameter size, GGUF quantization, configured context, parallelism, LM Studio
  version, and execution device class;
- the equivalent Qwen details already pinned privately;
- privacy-safe machine characteristics relevant to inference, such as CPU class, RAM, GPU/NPU
  class, and available VRAM when applicable;
- Gemini provider/model/location and the warning that hosted latency is not directly comparable
  with local inference.

Do not include hostname, username, serial number, private path, account/project identity, or exact
artifact hash in the tracked report.

### 5. Exact usage accounting

Replace approximate aggregate token totals with the exact values available from the generated
metrics, including:

- usage-available and usage-missing counts;
- prompt, completion, and total tokens where the provider reports them;
- a per-task breakdown when already present in the aggregate artifacts;
- the existing cross-provider tokenizer/cache-semantics caveat.

Do not derive false precision when a provider omits usage. Label unavailable values as unavailable.

## Required report corrections

Update:

`md/handoffs/reports/WP-5.2B1.4-completion-report.md`

The revised report must:

1. preserve all current terminal, validity, failure, judge, cache, provenance, and immutability
   accounting;
2. add the five missing evidence groups above;
3. distinguish candidate schema-valid rate, deterministic agreement, and judge means throughout;
4. state denominators for every percentage or mean;
5. keep Qwen-40 labelled as an operational checkpoint, not a fourth complete-arm result;
6. avoid leaderboard or statistical-generalization claims;
7. remain free of private conversation data, identifiers, paths, credentials, model responses,
   references, judge rationales, and cloud project/account identity.

## Validation after report-only rework

No full model or repository test rerun is required when only Markdown changes.

Provide evidence that:

- all four candidate package hashes remain unchanged;
- candidate attempt trees and judge-attempt aggregates remain unchanged;
- live and frozen database hashes remain unchanged;
- WP-5.2B1.3 historical package hashes remain unchanged;
- no provider call occurred;
- `git diff --check` passes;
- no private evaluation artifact is tracked or staged;
- Git status contains only the completion report and this PM validation review unless a separate
  pre-existing PM file is present.

Leave all changes unstaged and uncommitted for final PM validation.

## Final PM validation

The revised completion report closes every reporting gap without changing evaluation evidence or
making another provider/model call.

Accepted evidence includes:

- observed wall span, summed case latency, and overall/per-task p50/p95 for all four arms;
- complete-arm confusion matrices and per-label precision, recall, and support;
- fixed-Pro judge dimension means by task with explicit denominators;
- privacy-safe local hardware, runtime, model, quantization, context, and parallelism provenance;
- exact usage availability and prompt/completion/total token accounting with provider caveats;
- unchanged candidate packages, judge attempts, databases, and historical packages;
- clean Markdown diff/tracking/privacy checks.

WP-5.2B1.4 is accepted. The three retained judge failures remain measured terminal outcomes and do
not block acceptance.
