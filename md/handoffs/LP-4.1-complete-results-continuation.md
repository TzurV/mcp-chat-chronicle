# LP-4.1 - Complete Results Analysis Continuation

## Status

Ready for the existing LP-4.1 analysis/article-planning thread.

This continuation supplies the complete six-arm development evidence. It authorizes analysis and
revision of the existing analysis brief. It does not authorize publication, final article copy,
LinkedIn posting, or publication graphics without a later explicit owner request.

## Analyst role

Continue as the technical evaluation analyst and editorial-planning collaborator.

Do not write application code or modify benchmark behavior. Work from accepted tracked aggregate
reports and, only where exact score reproduction requires it, ignored private per-case evaluation
aggregates.

The detailed interpretation, publication metric subset, claims, headline, visual selection, and
editorial order must be discussed with the owner. Draft final publication copy only after the
owner explicitly approves those decisions.

## Objective

Replace the provisional three-arm analysis and incoming-model placeholders with a technically
honest analysis of:

- five local SLM complete arms;
- one hosted Gemini cloud control;
- four production-oriented AI tasks;
- 120 common development cases per model;
- the unchanged fixed-Pro rubric-v1 judge;
- one laptop/runtime/context policy for all local candidates.

The continuation must:

1. reconcile all six accepted complete arms;
2. reproduce the Usable Task Score from private per-case aggregates;
3. test whether the ranking survives reasonable score-policy alternatives;
4. distinguish whole-package reliability from quality among successful outputs;
5. identify structural, semantic, and operational task difficulty;
6. identify credible model-by-task routing options;
7. select a compact candidate publication metric set;
8. propose article claims with evidence, denominator, caveat, and confidence;
9. identify prohibited or unsupported claims;
10. return to the owner for decisions before drafting the article.

## Required sources

Read:

- `md/master-plan.md`;
- `md/development-ledger.md`;
- `md/handoffs/LP-4.1-local-model-results-analysis-and-article-planning.md`;
- `md/handoffs/reports/LP-4.1-local-model-results-analysis-brief.md`;
- `md/handoffs/reports/LP-4.1-validation-review.md`;
- `md/handoffs/reports/WP-5.2B1.4-completion-report.md`;
- `md/handoffs/reports/WP-5.2B1.4-validation-review.md`;
- `md/handoffs/reports/WP-5.2B2.2-completion-report.md`;
- `md/handoffs/reports/WP-5.2B2.2-validation-review.md`;
- `chronicle.default.ai-tasks.yaml`;
- `docs/development-evaluation.md`.

Use accepted private per-case aggregates under `.chronicle/eval/dev-v1/` only to reproduce values
that cannot be derived exactly from tracked aggregate reports.

Do not inspect or quote raw conversations, titles, source text, candidate text, FABLE prose,
judge rationales, private IDs, private paths, credentials, tokens, or cloud project/account
identity.

## Complete accepted scorecard

### Whole-package reliability

| Candidate | Execution | Schema-valid | Valid rate | Judge completed/eligible |
|---|---|---:|---:|---:|
| Gemini 3.5 Flash | Vertex cloud control | 112/120 | 93.3% | 110/112 |
| Qwen3.5-4B Q4_K_M | local | 84/120 | 70.0% | 84/84 |
| Phi-4 Mini Q4_K_M | local | 77/120 | 64.2% | 77/77 |
| Llama 3.2 3B Q4_K_M | local | 71/120 | 59.2% | 69/71 |
| Gemma 3 4B Q4_K_M | local | 62/120 | 51.7% | 62/62 |
| Llama 3.2 1B Q4_K_M | local floor | 57/120 | 47.5% | 56/57 |

All 720 candidate positions are terminal. Every eligible judge position is terminal. Judge
failures score zero in UTS and remain visible in reporting.

### Task-valid counts

Every cell is out of 30:

| Candidate | Summary | Work mode | Last activity | Title |
|---|---:|---:|---:|---:|
| Gemini 3.5 Flash | 23 | 30 | 29 | 30 |
| Qwen3.5-4B | 17 | 19 | 30 | 18 |
| Phi-4 Mini | 14 | 18 | 29 | 16 |
| Llama 3.2 3B | 12 | 19 | 23 | 17 |
| Gemma 3 4B | 12 | 19 | 25 | 6 |
| Llama 3.2 1B | 16 | 20 | 14 | 7 |

### Deterministic exact agreement

Every percentage uses all 30 task cases and includes no-valid-output as a non-matching outcome:

| Candidate | Work mode | Last activity | Title fit |
|---|---:|---:|---:|
| Gemini 3.5 Flash | 63.3% | 70.0% | 83.3% |
| Qwen3.5-4B | 33.3% | 60.0% | 56.7% |
| Phi-4 Mini | 10.0% | 60.0% | 16.7% |
| Llama 3.2 3B | 10.0% | 40.0% | 43.3% |
| Gemma 3 4B | 16.7% | 46.7% | 10.0% |
| Llama 3.2 1B | 3.3% | 20.0% | 6.7% |

### Candidate latency and wall span

| Candidate | Candidate p50 | Candidate p95 | Observed 120-case wall span |
|---|---:|---:|---:|
| Gemini 3.5 Flash | 2.156s | 12.562s | 10m 39.524s |
| Llama 3.2 1B | 17.312s | 53.609s | 42m 13.023s |
| Llama 3.2 3B | 51.124s | 180.061s | 2h 21m 16.435s |
| Phi-4 Mini | 54.608s | 180.031s | 2h 18m 50.713s |
| Qwen3.5-4B | 62.094s | 168.375s | 4h 43m 30.782s |
| Gemma 3 4B | 61.834s | 156.592s | 2h 08m 12.976s |

Do not compare hosted and local latency as though they used the same execution environment.
Qwen's wall span and latency relationship must be explained from its accepted run evidence rather
than inferred.

## Evidence terminology

Use:

- `cloud control`, `strong hosted baseline`, or `practical quality ceiling` for Gemini;
- `silver development reference` for FABLE;
- `exact agreement with FABLE`, not accuracy;
- `bounded development comparison`, not benchmark leaderboard;
- `quality among successfully judged valid outputs`, not whole-model quality;
- `five local models plus one cloud control`, not six equivalent deployment candidates.

Do not call Gemini or FABLE ground truth.

Gemini 3.1 Pro Preview judged all candidates using the same rubric, but the judge is from the same
provider/model family as the Gemini candidate. The observed disagreement is compatible with
same-family preference but does not establish bias. Use stronger wording only if supported by a
credible source and clearly separated from what this dataset proves.

## Analysis stage 1 - Reconcile and reproduce

1. Reconcile the six arm identities and accepted aggregate values.
2. Confirm 120 cases per model and 30 per task.
3. Confirm reliability, task-valid, deterministic, judge, latency, and failure totals.
4. Reproduce all composite calculations from private per-case aggregates.
5. Record a privacy-safe calculation manifest containing:
   - source package identities by accepted alias only;
   - formula version;
   - denominator policy;
   - judge-failure policy;
   - task weighting;
   - resulting values;
   - sensitivity variants.
6. Do not change any package, reference, prompt, score, or judge attempt.

Private scratch calculations or scripts may be used under ignored `.chronicle/eval/dev-v1/`
paths. Do not add calculation code or private outputs to the repository.

## Analysis stage 2 - Exact UTS and sensitivity

Reproduce **Usable Task Score (UTS), 0-100** exactly:

1. Invalid or absent candidate output: case score 0.
2. Eligible output without a completed judge result: case score 0.
3. Successfully judged case:
   - average its applicable rubric dimensions;
   - normalize from 1-4 to 0-1 using `(score - 1) / 3`.
4. Average 30 cases within each task.
5. Macro-average the four task scores.
6. Multiply by 100.

Report:

- exact UTS for all six candidates;
- task-level UTS components;
- completed/zero-scored case counts;
- calculation precision and rounding policy.

Sensitivity must include:

- reliability-adjusted normalized valid-output judge mean;
- geometric combination of reliability and valid-output quality;
- harmonic combination where mathematically defined;
- `score / 4` normalization as a policy comparison;
- judge failures excluded versus scored zero;
- two-axis reliability-versus-valid-output-quality with no composite.

Equal-task and equal-case weighting should be mathematically identical because every task has 30
cases; verify rather than merely repeat the assumption.

Do not add latency to UTS. Speed remains a separate axis.

Recommend UTS for publication only if:

- calculation reproduces exactly;
- ranking is reasonably stable;
- its limitations can be explained in three short lines;
- it adds clarity beyond the primary two-axis chart.

## Analysis stage 3 - Task difficulty

Assess every task along:

1. **Structural difficulty:** valid output rate and failure boundary.
2. **Semantic difficulty:** FABLE agreement and fixed-Pro dimensions.
3. **Operational difficulty:** context pressure, timeout, output budget, and latency.

Produce a six-model by four-task interpretation table with explicit denominators.

Test, rather than assume:

- work-mode classification is semantically hardest;
- last activity is structurally well suited to Qwen and Phi;
- title assessment separates Qwen/Llama 3B from Phi/Gemma/Llama 1B;
- summary is context/material-selection constrained;
- task difficulty is model-dependent;
- context 8,192 explains some but not all local failure.

Do not claim context expansion will fix a model. That requires a separate measured arm.

## Analysis stage 4 - Model and routing interpretation

Assess:

- best overall local baseline;
- fastest usable local model;
- best local candidate per task;
- local-first with cloud fallback on invalid output;
- static YAML task routing;
- task admission thresholds;
- whether a weaker but faster model has a credible role.

For every routing proposal state:

- supporting metrics and denominators;
- expected benefit;
- failure-detection requirement;
- operational complexity;
- privacy/cost impact;
- evidence confidence;
- whether implementation is justified now or remains discussion only.

Qwen is currently the leading local reliability candidate. Do not automatically declare it best
for every task without checking semantic and operational evidence.

## Analysis stage 5 - Article observations

Propose five to seven findings. Each must include:

- exact supporting metric;
- denominator;
- caveat;
- confidence;
- whether it belongs in the public article or private appendix.

At minimum evaluate:

1. structured-output reliability as a product metric;
2. quality survivorship among valid outputs;
3. cloud-control versus local reliability;
4. model-dependent task difficulty;
5. context and timeout effects;
6. parameter size versus speed and reliability;
7. task-specific routing versus one-model-for-all.

Avoid forcing a surprising narrative when the evidence supports a more qualified conclusion.

## Analysis stage 6 - Publication planning

Return recommendations for:

- final headline from the existing three options or a revised alternative;
- short LinkedIn post only versus short post plus long-form technical article;
- publication sequence;
- primary and secondary visual;
- compact public metric subset;
- methodology and limitation language;
- repository/project link placement;
- whether prompt-tuning results should follow in a later article rather than delay this baseline
  article.

The primary visual should remain reliability versus valid-output semantic quality unless the
complete data clearly supports a better alternative.

The task-by-model matrix is the likely technical centerpiece. UTS, if retained, is secondary.

## First response to the owner

Do not edit the brief or draft the article immediately.

First provide:

1. a concise six-arm scorecard;
2. five provisional findings;
3. exact reproduced UTS values and ranking sensitivity;
4. the task-difficulty interpretation;
5. model-routing implications;
6. the recommended public metric subset;
7. two article narrative options;
8. the decisions requiring owner approval.

Discuss corrections and emphasis with the owner.

Only after the owner explicitly approves the final interpretation direction should you update:

`md/handoffs/reports/LP-4.1-local-model-results-analysis-brief.md`

## Updated analysis brief

Update the existing brief rather than creating a replacement.

Required changes:

1. replace the three-arm scorecard with all six complete arms;
2. remove incoming-model placeholders;
3. replace estimated UTS with exact per-case values;
4. update score sensitivity across all six;
5. update task difficulty and routing conclusions;
6. update findings with metric/denominator/caveat/confidence;
7. finalize the proposed public metric subset;
8. update article narrative and visual concepts;
9. update limitations and prohibited claims;
10. record owner decisions still outstanding;
11. keep prompt tuning and context expansion as separate future studies.

Set status to `Ready for PM validation` only after the owner approves the revised interpretation.

Leave the brief unstaged and uncommitted.

## Out of scope

- no application or benchmark code;
- no candidate generation or judge call;
- no prompt or rubric change;
- no package/reference mutation;
- no context-expansion run;
- no prompt-tuning execution;
- no new model integration;
- no owner adjudication unless separately requested;
- no final article draft;
- no final LinkedIn post;
- no publication graphic;
- no commit, push, or publication.

## Validation and delivery

Before returning the revised brief:

```powershell
poetry env info --path
git diff --check
git diff --cached --name-only
git status --short
```

Also prove:

- all accepted packages and private aggregate sources are unchanged;
- no raw/private content appears in tracked changes;
- exact UTS can be reproduced from the private calculation manifest;
- only the intended analysis brief changed;
- nothing is staged or committed.

Return:

- a concise analysis summary;
- the exact UTS and sensitivity result;
- owner decisions incorporated;
- remaining open decisions;
- the updated brief path;
- privacy-safe Git status.

Commit ownership remains with the PM/manager after validation and an explicit owner request.
