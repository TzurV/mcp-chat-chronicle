# LP-4.1 - Local Model Results Analysis and Article Planning

## Status

Ready for a separate analysis/chat thread. This is a discussion and editorial-planning handoff,
not permission to publish or to write the final article without the owner's explicit approval.

## Analyst role

Act as a technical evaluation analyst and article-planning collaborator. Do not write application
code. Work from accepted privacy-safe aggregate evidence. Discuss conclusions, scoring choices,
article scope, and visual priorities with the owner before creating a final brief or article draft.

The owner expects the detailed plan, exact context, interpretation, and order of editorial
activities to be discussed first. An explicit owner request is required before drafting the final
LinkedIn post/article or creating publication graphics.

## Objective

Interpret the accepted local-model evaluation results and design a technically honest LinkedIn
article framework that can absorb additional model results later.

The analysis must:

1. extract the main observations from the accepted results;
2. explain what the numbers mean in product terms;
3. classify the relative difficulty of the four AI tasks;
4. consider whether different models should be routed to different tasks;
5. assess whether one composite number is useful and defensible;
6. treat hosted Gemini 3.5 Flash as the practical cloud quality/control baseline;
7. distinguish schema reliability, semantic quality, deterministic agreement, and speed;
8. leave placeholders for the additional local candidates being qualified in parallel;
9. propose an article narrative and a small, owner-selectable metric set;
10. identify claims that the evidence does not support.

## Required source material

Read:

- `md/master-plan.md`, especially WP-5.1, WP-5.2, and LP-4;
- `md/development-ledger.md`;
- `md/handoffs/reports/WP-5.2B1.4-completion-report.md`;
- `md/handoffs/reports/WP-5.2B1.4-validation-review.md`;
- `md/handoffs/reports/WP-5.2B1.3-completion-report.md`;
- `md/handoffs/reports/WP-5.2B1.2-completion-report.md`;
- the four accepted task definitions in `chronicle.default.ai-tasks.yaml`;
- `docs/development-evaluation.md`.

Use private aggregate metrics only if a calculation cannot be reproduced from the tracked report.
Do not inspect or quote raw conversations, conversation titles, candidate outputs, FABLE
references, judge rationales, private paths, IDs, or cloud account/project information.

## Accepted baseline results

Use the complete 30-conversation / 120-case arms as the primary evidence:

| Candidate | Schema-valid | Valid rate | Observed wall span | Role |
|---|---:|---:|---:|---|
| Vertex Gemini 3.5 Flash | 112/120 | 93.3% | 10m 39.524s | hosted cloud control |
| Qwen3.5-4B Q4_K_M | 84/120 | 70.0% | 4h 43m 30.782s | local control |
| Llama 3.2 1B Q4_K_M | 57/120 | 47.5% | 42m 13.023s | local evaluation floor |

Deterministic exact agreement:

| Candidate | Work mode | Last activity | Title fit |
|---|---:|---:|---:|
| Gemini | 63.3% | 70.0% | 83.3% |
| Qwen | 33.3% | 60.0% | 56.7% |
| Llama 1B | 3.3% | 20.0% | 6.7% |

Task-valid counts:

| Candidate | Summary | Work mode | Last activity | Title |
|---|---:|---:|---:|---:|
| Gemini | 23/30 | 30/30 | 29/30 | 30/30 |
| Qwen | 17/30 | 19/30 | 30/30 | 18/30 |
| Llama 1B | 16/30 | 20/30 | 14/30 | 7/30 |

Use the full judge-by-task means, confusion matrices, failure categories, exact token accounting,
and latency tables from the accepted report rather than copying only the selected values above.

## Important terminology

The owner wants Gemini represented as the strong cloud or "golden performance" comparator. Use
careful technical language:

- call Gemini the `cloud control`, `practical quality ceiling`, or `strong hosted baseline`;
- do not call it ground truth;
- FABLE references are silver development references, not human-adjudicated gold labels;
- Gemini 3.1 Pro is also the judge, so same-family/provider bias is possible;
- Gemini itself had eight invalid candidate outputs and two terminal judge failures;
- this is a bounded development comparison on the owner's real work, not a general leaderboard.

The article can say "how close did local models get to the cloud control?" It must not say Gemini
defines objective correctness.

## First response to the owner

Do not immediately write an article. Start by:

1. summarizing the evidence in plain language;
2. identifying three to five likely headline findings;
3. explaining the composite-score decision and its risks;
4. proposing two possible article narratives;
5. listing the editorial decisions that require owner input.

Discuss those choices with the owner. Only create the tracked analysis brief after the owner
explicitly approves the interpretation direction.

## Analysis workstreams

### A. Reliability versus quality

Keep these layers separate:

1. **Product reliability:** schema-valid outputs / all 120 cases.
2. **Deterministic task agreement:** exact label/date/evidence/constraint agreement against FABLE.
3. **Semantic quality:** fixed-Pro judge dimensions over successfully judged, schema-valid outputs.
4. **Operational performance:** wall time, p50/p95 latency, timeout/context failures, and usage.

Explain survivorship bias: Qwen's valid outputs often received strong semantic scores, but 36/120
positions were invalid. A quality average over only successful outputs must never be presented as
whole-product quality.

### B. Task difficulty

Classify difficulty along three separate axes:

- **structural difficulty:** ability to return consumable schema-valid output;
- **semantic difficulty:** agreement with the reference and fixed judge;
- **operational difficulty:** context pressure, output budget, latency, and timeout behavior.

Test these provisional observations against the full evidence:

- work-mode classification appears semantically hardest, especially distinguishing manager,
  executor, mixed, and one-off;
- last-activity extraction appears comparatively suitable for Qwen because it achieved 30/30
  valid outputs and 60% deterministic agreement, although next-action support was weaker;
- summary generation creates context/material-selection pressure and had lower validity for every
  candidate than some categorical tasks;
- title assessment was easy for Gemini but structurally and semantically difficult for Llama 1B;
- task difficulty is model-dependent, so avoid one universal easiest-to-hardest ranking unless the
  evidence supports it.

Produce a task-by-model interpretation table with explicit denominators.

### C. Model routing by task

Assess whether a practical system should use:

- one model for all tasks;
- the best local model per task;
- a local-first route with cloud fallback on invalid/low-confidence cases;
- a reliability threshold before a model is admitted to a task.

For each routing proposal include expected benefit, operational complexity, privacy/cost trade-off,
failure detection requirements, and whether current evidence is sufficient. Do not finalize routing
until the WP-5.2A5.1/B2 candidate results are added.

### D. A possible single number

The first benchmark plan intentionally kept metrics separate. The owner now wants to know whether
a single number could help communication.

Evaluate, but do not automatically adopt, this candidate:

**Usable Task Score (UTS), 0-100**

1. For each case, assign zero when the candidate is invalid, has no valid output, or has no
   completed judge result.
2. For a successfully judged case, average only the applicable rubric dimensions and normalize the
   1-4 judge scale to 0-1 using an explicitly stated formula.
3. Average cases within each task so every task retains its 30-case denominator.
4. Macro-average the four task scores so each task has equal weight.
5. Multiply by 100.

This combines reliability and judged quality while preventing failed outputs from disappearing.
It is still a policy choice, not a scientific truth.

Also compare at least two alternatives:

- reliability-adjusted judge mean using `schema-valid rate x normalized valid-output judge mean`;
- a geometric or harmonic combination of reliability and quality;
- no composite, using a two-axis reliability-versus-quality chart instead.

Run a sensitivity check:

- show whether model ranking changes across reasonable formulas;
- identify how judge failures are treated;
- show the effect of equal-task versus equal-case weighting;
- explain the chosen 1-4 normalization;
- do not combine latency into the quality score;
- keep speed as a separate axis.

Recommend a single number only if it is stable, transparent, and adds clarity. Otherwise recommend
a compact scorecard or two-axis chart.

### E. Main observations

Extract observations that are supported now, such as:

- the cloud control was far more reliable than both local candidates;
- Qwen's successful outputs were often semantically strong, but context and timeout failures
  materially reduced utility;
- the 1B model was faster than Qwen locally but too unreliable for these production contracts;
- larger parameter count did not translate into faster local execution on the tested CPU/iGPU
  machine;
- structured-output reliability is a first-order product metric, not benchmark housekeeping;
- task-specific routing may be more useful than one overall winner.

For every proposed claim include the supporting metric, denominator, caveat, and confidence level.

### F. Article design

Propose:

- two headline/title options;
- one recommended narrative arc;
- a short post version and a longer technical-article outline;
- three candidate visuals using only privacy-safe aggregate data;
- a minimal metric set for the public article;
- a larger appendix/private evidence set;
- clear methodology and limitation language;
- placeholders for Phi-4 Mini, Llama 3.2 3B, and Gemma results.

Do not create final graphics or publication copy before owner approval.

## Future prompt-tuning study

Treat prompt tuning as a later backlog experiment, not part of the current baseline comparison.

After all baseline candidate runs:

1. select the best one or two **local** models by task and overall usable reliability;
2. retain Gemini-120 as the unchanged cloud control target;
3. compare a small number of versioned prompt strategies, including a concise schema-first prompt
   and task-specific few-shot examples;
4. do not request or publish chain-of-thought;
5. keep context, model artifact, generation settings, and scoring fixed within each prompt study;
6. run on the current development set and label the result as prompt development/overfitting;
7. freeze the selected prompt before a later untouched evaluation set;
8. report whether tuning closes reliability, semantic, or task-specific gaps.

The analysis thread may propose the study design but must not execute it.

## Discussion deliverable

After owner approval of the interpretation direction, write:

`md/handoffs/reports/LP-4.1-local-model-results-analysis-brief.md`

Required sections:

1. evidence boundary and terminology;
2. current model scorecard;
3. main observations with metric/denominator/caveat;
4. task-difficulty analysis;
5. task-routing options;
6. composite-score formulas and sensitivity;
7. recommended public metric subset;
8. article narrative options;
9. visual concepts;
10. limitations and prohibited claims;
11. placeholders for incoming models;
12. owner decisions still required;
13. prompt-tuning follow-up proposal.

Leave the brief unstaged and uncommitted. The development manager validates and commits only after
an explicit owner request.

