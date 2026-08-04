# WP-5.2C1 Validation Review

**Review date:** 2026-08-04
**Decision:** Accepted after narrow report-only rework
**Execution/model status:** Accepted; no additional model, judge, or RunPod activity required

## Findings

### 1. Full confusion matrices are missing from the canonical report

**Severity:** Required documentation acceptance gap

The handoff requires full categorical confusion matrices for work mode, last activity, and title fit.
The completion report provides exact agreement and per-label precision/recall/support, then says the
full matrices remain in private evaluator storage. That does not satisfy the canonical-report
requirement.

**Required fix:** Add compact, readable confusion matrices for all four compared arms. Include the
`no_valid_output` column/row treatment used by deterministic scoring and preserve exact 30-case task
denominators. Values must be reproduced from the accepted deterministic artifacts; do not rerun or
rewrite scoring.

### 2. The required compact arm-by-arm publication table is missing

**Severity:** Required documentation acceptance gap

The report contains separate generation, judge, hardware, and cost tables, but not the single
article-ready comparison table requested by the handoff.

**Required fix:** Add one table with rows for R8 original, R8 repeat, R262K, and Gemini control. Its
columns must include at least:

- context/execution environment;
- schema-valid count/rate;
- outer wall time;
- overall p50/p95;
- judge eligible/completed/failed;
- semantic score and exact denominator;
- verification status;
- candidate execution cost boundary.

Keep RunPod candidate cost, Vertex judge cost, and historical Gemini candidate/judge estimates
distinct. Do not imply that a shared RunPod bill is attributable to one arm.

### 3. Model provenance and missing-usage accounting should be explicit

**Severity:** Minor completeness gap

The report gives model identity, quantization, exact size, hash status, runtime, context, and
parallelism, but omits the public GGUF repository and filename and does not explicitly state the
artifact revision status. The task tables show usage-present counts but require readers to calculate
usage-missing counts.

**Required fix:**

- add the accepted public repository and filename;
- state whether the exact repository revision is retained privately and verified; do not invent one
  if it was not captured;
- add explicit usage-missing counts overall and per task, either as columns or an adjacent compact
  table;
- retain the exact private hash outside the canonical tracked report if that remains the chosen
  privacy policy.

### 4. A private judge-artifact hash appears in a tracked supporting audit

**Severity:** Privacy-policy consistency gap

`WP-5.2C1-runpod-three-arm-evidence-audit.md` includes the exact aggregate SHA-256 for the private
R262K judge-attempt tree. The continuation handoff says private artifact hashes should remain in
ignored storage.

**Required fix:** Replace that judge-tree hash with a statement that its identity was retained
privately and verified unchanged. The Qwen model-binary SHA-256 may remain if deliberately treated as
public artifact provenance; clarify that distinction or redact it as well for consistency. Do not
remove the zero-call cache proof.

## Independently Validated Evidence

The manager validated the following without model/provider calls:

- all four package summaries reconcile to the canonical headline counts;
- the ordered case identity, fixed-prefix scope, judge profile, and rubric match across the four
  comparison arms;
- R8 repeatability, R8-to-R262K recovery, and common-case Qwen/Gemini judge aggregates reconcile to
  the private consolidation record;
- the private closure record reports zero model/judge calls and the final RunPod billing/cleanup
  state described in the report;
- the local backup archive SHA-256 matches the closure record;
- the archive contains 743 files and 25,534,080 uncompressed bytes;
- every archived file independently matches the corresponding retained source file by SHA-256:
  743 compared, zero mismatches;
- `git ls-files .chronicle` is empty;
- `git diff --check` passes;
- no credentials, private absolute paths, account IDs, or Pod IDs were found in the tracked
  WP-5.2C1 documents;
- the only private-artifact identity exposed in supporting documentation is the judge-tree hash
  identified above.

The RunPod deletion itself is supported by the retained private control-plane record: exact Pod
lookup `not_found`, empty Pod/network-volume inventories, attached-volume deletion, and US$0/hour
ongoing spend. The manager did not make a new external RunPod API call during this review.

## Accepted Scope And Interpretation

- No 16K or 32K remote arm is required.
- R262K is the maximum-context Qwen reference for comparison with Gemini, not proof of minimum
  sufficient context.
- The R8 packages remain `waiver-judged, not strict manager-valid`.
- R262K remains strict-verifier valid.
- Gemini 3.5 Flash is a strong hosted control, not ground truth.
- Reliability, deterministic agreement, and fixed-judge semantic quality remain separate metrics.
- The second backup is a verified same-workstation copy, not off-device disaster recovery.

## Rework Instructions

Return this review to the same executor. The rework is documentation-only:

1. update `md/handoffs/reports/WP-5.2C1-completion-report.md` for findings 1-3;
2. update `md/handoffs/reports/WP-5.2C1-runpod-three-arm-evidence-audit.md` for finding 4;
3. add a dated PM-rework addendum to the completion report;
4. rerun only arithmetic/structured-data checks needed to prove the new tables;
5. run `git diff --check`, the privacy scan, `git status --short`, and
   `git ls-files .chronicle`;
6. do not run the full repository suite, because no code changed;
7. do not call any model, judge, RunPod, Vertex, or other provider;
8. do not stage or commit.

The refreshed completion report must return with status `ready for PM validation` and confirm that
the accepted packages, scores, judge attempts, databases, archive, and cleanup record were not
modified.

## PM Acceptance Addendum

The executor completed all four documentation corrections without code changes, model/provider
access, or accepted-artifact modification.

The manager independently confirmed:

- all 48 confusion-matrix rows match the private deterministic artifacts cell by cell;
- all 12 task matrices retain exact 30-position denominators;
- the compact publication table reconciles to accepted reliability, timing, judge, semantic, cost,
  and verification evidence;
- overall and per-task missing-usage counts reconcile;
- the public repository/filename and uncaptured-revision status are stated accurately;
- private judge-tree and model-binary hashes are absent from tracked WP-5.2C1 documentation;
- `git diff --check`, privacy scanning, and `.chronicle` tracking checks pass;
- the verified 743-file local backup and completed RunPod cleanup evidence remain unchanged.

WP-5.2C1 is accepted. No further inference, judging, cloud access, testing, or documentation rework is
required. The manager may commit the tracked WP-5.2C1 delivery with the associated plan and ledger
updates after owner request.
