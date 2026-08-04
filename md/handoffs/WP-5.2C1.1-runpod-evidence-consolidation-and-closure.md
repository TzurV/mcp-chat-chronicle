# WP-5.2C1.1 Handoff: RunPod Evidence Consolidation And Closure

**Status:** Approved report-only continuation after manager review
**Parent:** WP-5.2C1
**Execution type:** Evidence consolidation, comparison, validation, and resource cleanup
**Code changes:** Not authorized
**New model/provider calls:** Not authorized
**Commit owner:** Development manager

## 1. Executor Role

Act as the evidence and closure executor for WP-5.2C1. Do not generate new candidate outputs,
repeat judge calls, change prompts, modify benchmark code, or inspect unrelated private data.

The owner has explicitly decided that no 16K or 32K arm is required. The intended experiment is:

1. an 8,192-context RunPod Qwen baseline with a repeatability run;
2. a 262,144-context RunPod Qwen maximum-context reference; and
3. comparison of that maximum-context result with the accepted Gemini 3.5 Flash 120-case cloud
   control.

The endpoint study does not identify the minimum sufficient context. State that as a scope
boundary, not as missing work.

## 2. Required Inputs

Read before starting:

1. `md/handoffs/WP-5.2C1-qwen-remote-speed-context-study.md`
2. `md/handoffs/reports/WP-5.2C1-validation-review.md`
3. `md/handoffs/reports/WP-5.2C1-runpod-three-arm-evidence-audit.md`
4. `md/handoffs/reports/WP-5.2B1.4-completion-report.md`
5. `md/research/WP-5.2C1-runpod-remote-lm-studio-service.md`
6. the ignored private WP-5.2C1 operator diary, candidate packages, deterministic scoring
   artifacts, judge artifacts, telemetry, manifests, and transfer records
7. the accepted private Gemini 3.5 Flash 120-case package and its scoring/judge artifacts

Do not modify any accepted candidate package, judge attempt, database, frozen corpus, or historical
benchmark package.

## 3. Accepted Existing Results

Treat these as claims to verify from retained artifacts, not values to copy without checking:

| Arm | Context | Schema-valid | Outer generation time | Peak VRAM | Judge accounting |
|---|---:|---:|---:|---:|---:|
| RunPod Qwen R8 original | 8,192 | 89/120 | 131 s | 3,712 MiB | 89/89 |
| RunPod Qwen R8 repeat | 8,192 | 89/120 | 129 s | 4,219 MiB | 89/89 |
| RunPod Qwen R262K | 262,144 | 119/120 | 169 s | 11,896 MiB | 118/119 |
| Accepted Gemini control | hosted | 112/120 | verify from accepted evidence | N/A | verify from accepted evidence |

The R8 packages remain immutable and waiver-judged rather than strict manager-valid because of the
documented missing raw-invalid artifact. R262K is strict-verifier valid. Preserve this distinction.

## 4. Objective

Create one canonical, publication-grade source report at:

`md/handoffs/reports/WP-5.2C1-completion-report.md`

It must consolidate all material needed to close the work package and later draft a technical
LinkedIn article. Existing audit and research files remain supporting evidence; the canonical report
must be understandable without reading them first.

## 5. Required Validation

### 5.1 Artifact integrity

For all three RunPod packages and the accepted Gemini control:

- verify package identity, case count, ordered case fingerprints, prompt/task/schema identities,
  candidate model identity, and authoritative-attempt policy;
- recompute and record privacy-safe aggregate/hash validation outcomes;
- prove candidate and judge artifacts were not modified during this activity;
- verify the frozen and live database hashes/counts remain unchanged where retained baselines permit;
- inventory all private evidence and its local backup location without exposing private paths or
  hashes in tracked files.

Do not repair the two R8 packages. Document their precise waiver and its effect on confidence.

### 5.2 Matched comparison gate

Before comparing R262K with Gemini, prove that both arms use the same ordered 120 case identities,
the same four task contracts, compatible P0 prompt/schema versions, and the same fixed-Pro judge
rubric/settings. If any identity differs, report the exact mismatch and restrict the comparison to
the compatible dimensions; do not silently call it matched.

### 5.3 No-call cache evidence

Use existing cache-only evidence or a local cache-only command if it cannot invoke a provider.
There must be no new RunPod inference, Gemini candidate generation, or Vertex judge request.

## 6. Canonical Report Contents

The completion report must include all of the following.

### 6.1 Executive summary

- plain-language result;
- explicit experiment question;
- accepted endpoint scope: 8K original/repeat, 262K reference, Gemini control;
- recommendation and confidence level;
- what the experiment does and does not establish.

### 6.2 Protocol and provenance

- frozen corpus identity and counts, without private identifiers;
- exact Git commit used for remote execution;
- Qwen model, artifact revision/hash status, quantization, runtime, context, parallelism, structured
  output, reasoning, timeout, retry, prompt, selector, schema, and generation settings;
- fixed judge model, location, rubric, temperature, token cap, reasoning policy, and retry policy;
- all approved deviations from the original handoff: RunPod instead of Google Cloud, R8 repeat plus
  R262K instead of intermediate context arms, and the R8 verification waiver.

### 6.3 Hardware and service evidence

- provider, cloud type, region, GPU model and captured VRAM;
- captured service allocation: vCPU count, RAM, container disk, and volume;
- exact runtime/container/driver/CUDA/LM Studio or serving-stack versions where retained;
- observed peak VRAM, GPU utilization methodology, peak temperature, and peak power for each arm;
- state explicitly that the physical CPU model, trustworthy process CPU/RAM usage, TTFT, or other
  unavailable measurements were not captured rather than estimating them;
- distinguish the captured Pod allocation from generic RunPod RTX 5090 product specifications.

### 6.4 Complete generation metrics

For each RunPod arm and the Gemini control, where the accepted evidence supports it:

- 120-case terminal accounting and schema-valid rate;
- failure taxonomy by task and category;
- outer wall time and authoritative-attempt time-span definition;
- p50/p95 overall and per task;
- exact prompt, completion, and total token counts per task and overall;
- usage-missing counts;
- load/setup time where captured, clearly noting that the R8 and R262K setup boundaries are not
  necessarily directly comparable;
- throughput only if derivable consistently; otherwise mark unavailable.

### 6.5 Deterministic and semantic metrics

- full categorical confusion matrices for work mode, last activity, and title fit;
- exact agreement plus per-label precision, recall, and support;
- summary date, length, evidence, cross-field, and title-suggestion validity;
- fixed-Pro dimension means by task and overall, with denominators;
- retained judge failures and their categories;
- reliability and semantic quality reported as separate axes.

### 6.6 Repeatability analysis

Compare the two R8 runs:

- validity and failure-category identity;
- timing difference and percentage;
- result identity count among shared valid cases;
- telemetry differences;
- judge-score differences;
- a bounded conclusion about repeatability.

### 6.7 Context endpoint analysis

Compare R8 with R262K:

- 30 recovered outputs and the remaining failure;
- whether any R8 success regressed;
- wall-time, p50/p95, VRAM, utilization, temperature, and power deltas;
- task-by-task recovery and failure changes;
- common-case semantic comparison over outputs valid in both arms;
- separate all-case judge means, with their different denominators;
- state that 262K is a maximum-context reference, not evidence that 262K is the minimum necessary
  context.

### 6.8 Qwen R262K versus Gemini control

This is the principal publication comparison. On the matched 120 cases, report:

- schema-valid outputs: Qwen R262K versus Gemini 3.5 Flash;
- per-task validity and failure categories;
- generation wall time and latency distributions, with the caveat that dedicated RunPod GPU
  inference and managed Vertex service latency are different execution environments;
- deterministic task metrics and full confusion matrices;
- fixed-Pro judge dimension means with exact denominators;
- common-valid-case paired semantic comparison so coverage does not bias the quality claim;
- token accounting with tokenizer/provider comparability caveats;
- candidate runtime cost and judge cost kept separate;
- local/private-data implications: Qwen candidate generation ran in the owner-controlled rented Pod,
  while Gemini candidate generation used a managed cloud model.

Do not describe Gemini as ground truth. It is the accepted strong hosted control. Do not claim Qwen
is equivalent or superior from aggregate judge means alone.

### 6.9 Cost and practicality

- actual or bounded RunPod compute/storage spend with billing evidence;
- Vertex judge token-based estimate, formula, pricing date, and official source;
- combined bounded expenditure;
- retained stopped-resource storage cost per day;
- practical implications for a prospective home workstation, limited to measured GPU/VRAM/runtime
  evidence and without claiming that the cloud Pod exactly predicts consumer-desktop performance.

### 6.10 Article-ready evidence table

Provide one compact table whose rows are R8 original, R8 repeat, R262K, and Gemini control and whose
columns include validity, wall time, p50/p95, eligible/completed judge outcomes, semantic score with
denominator, execution environment, and candidate cost boundary.

Then provide:

- five defensible headline observations;
- one caveat for each observation;
- confidence level for each observation;
- three suggested charts with exact source fields;
- a list of claims that must not be published.

Do not write the final LinkedIn article in this task.

## 7. Resource Closure

The Pod is currently stopped but retained. Do not restart it.

After all remote artifacts are proven present in the local private archive and its backup, report to
the owner that the Pod and volume can be deleted. The owner controls deletion unless explicitly
delegated. After deletion is confirmed, append a dated cleanup addendum to the canonical report with:

- deletion confirmation;
- final RunPod charge if available;
- confirmation that no required evidence existed only on the deleted resource.

If the owner chooses to delete immediately after local archive validation, that is acceptable; no
additional inference is needed.

## 8. Validation Commands

Run only read-only/report validation appropriate to the retained evidence:

- package verification for all compared packages;
- deterministic scoring consistency checks without rewriting accepted evidence;
- cache-only judge checks only where guaranteed fail-closed before provider access;
- hash/inventory checks;
- arithmetic reproduction scripts retained under ignored private evaluation storage;
- `git diff --check`;
- `git status --short`;
- `git ls-files .chronicle`.

Do not rerun the repository test suite unless tracked code changes unexpectedly become necessary. If
code changes appear necessary, stop and request a new manager decision.

## 9. Completion Report Requirements

Update the canonical report itself as the completion report. End it with:

- status: `ready for PM validation` or `blocked`;
- acceptance checklist mapped to this handoff;
- tracked files changed;
- private artifacts retained and backup status, described without private paths/hashes;
- resource state and exact owner cleanup action;
- known limitations;
- confirmation that no model/provider call occurred;
- confirmation that nothing was staged or committed.

The executor must not commit. The development manager validates and commits after owner request.

## 10. Acceptance Criteria

WP-5.2C1.1 is complete when:

- one canonical report contains the complete publication-grade evidence;
- all three RunPod arms and the Gemini control have verified identities and immutable evidence;
- the R8 waiver remains explicit;
- repeatability, context endpoint, and matched Gemini comparisons are all present;
- reliability and semantic quality are not collapsed into one unsupported claim;
- hardware, runtime, timing, telemetry, token, cost, and limitation data are complete or explicitly
  marked unavailable;
- the local private archive and backup are verified;
- the Pod/volume is either deleted or has one explicit owner cleanup action remaining;
- no private artifact is tracked;
- no new model or judge call occurred;
- the repository remains unstaged and uncommitted for manager review.
