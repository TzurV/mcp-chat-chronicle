# WP-5.2B3B Handoff: Global Prompt Development

## Status

**Approved for execution on branch
`codex/wp-5.2b3b-prompt-development` after the development manager commits
this handoff and the tracked checkout is clean.**

WP-5.2C1 remains active independently on its pinned Google Cloud study commit.
Do not modify its local or remote artifacts, manifests, packages, branch, VM, or
report. WP-5.2B3B uses the accepted local frozen corpus and distinct ignored run
directories.

This handoff contains one mandatory manager checkpoint before private model
generation. The current benchmark supports only a frozen prefix; the first ten
frozen conversations are all from ChatGPT and cannot satisfy the approved
provider-balanced split. The executor must first implement the bounded
non-prefix selection-manifest support in Gate 1, leave it uncommitted, and wait
for manager validation and commit. Resume the same handoff from that clean
commit. This checkpoint is not a separate work package.

## Executor Role And Commit Ownership

Act as the benchmark and prompt-development executor. Implement only the
development-harness capability required by this handoff, freeze the private
split, author the declared global prompt packages, run the accepted candidate
and judge pipelines, select one complete prompt package, and deliver detailed
privacy-safe evidence.

The development manager:

- owns scope, acceptance, branch history, staging, and commits;
- validates the Gate 1 benchmark patch before generation;
- validates the final completion report and selected prompt package;
- decides whether the selected package may proceed to WP-5.2B3C.

The executor must not run `git add`, `git commit`, amend, rebase, merge, tag,
push, or mark the ledger accepted. Executor status is `Ready for PM
validation`, never `Accepted`. Gate 1 and final delivery changes must remain
unstaged and uncommitted until the manager acts after an explicit owner
request.

## Read First

Read and follow:

- `md/agent-operating-notes.md`;
- `docs/development-evaluation.md`;
- `md/master-plan.md`, especially WP-5.2B1 through WP-5.2B3C;
- `md/handoffs/WP-5.2B3A-full-context-comparison.md`;
- `md/handoffs/reports/WP-5.2B3A-completion-report.md`;
- `md/handoffs/reports/WP-5.2B3A-validation-review.md`;
- `md/handoffs/reports/WP-5.2B3A-context-comparison-article-brief.md`;
- `md/handoffs/reports/WP-5.2B1.4-completion-report.md`;
- `md/handoffs/reports/WP-5.2B2.2-completion-report.md`;
- `md/handoffs/reports/LP-4.1-local-model-results-analysis-brief.md`;
- accepted private manifests for the Qwen3.5-4B, Phi-4 Mini, and Gemini 3.5
  Flash 8K arms;
- the frozen WP-5.1.2A snapshot, WP-5.1.2B selection, inputs, and FABLE
  references.

This handoff is authoritative for B3B scope, prompt variants, selection rules,
privacy authorization, retry limits, reporting, and stop rules. Earlier
handoffs provide provenance but cannot broaden this work.

## Objective

Select and freeze one globally applied four-task prompt package using only ten
frozen development conversations at the accepted common 8,192-token context.

"Global" means that the same version of each task prompt is used unchanged by:

1. Qwen3.5-4B Q4_K_M through local LM Studio;
2. Phi-4 Mini Instruct Q4_K_M through local LM Studio;
3. Vertex AI Gemini 3.5 Flash as the unchanged cloud portability control.

It does not mean one prompt shared by all four tasks. A prompt package contains
one prompt for each accepted task:

1. `conversation-summary`;
2. `work-mode-classification`;
3. `last-activity`;
4. `title-assessment`.

The package must be selected as one unit. Do not create model-specific prompts,
combine different winning variants per task after viewing results, or optimize
for Gemini at the expense of the local models.

The selected package will be evaluated once on the untouched twenty-
conversation internal prompt holdout in WP-5.2B3C. B3B must not generate,
score, judge, or inspect per-case outcomes for those holdout conversations.

## Decisions Already Approved

The owner and manager have approved:

- common context: 8,192 for every B3B arm;
- development/holdout split: 10 conversations / 20 conversations;
- development provider quotas: three ChatGPT, three OpenAI Codex, two Claude,
  and two Claude Code conversations;
- Qwen and Phi as the local optimization models;
- Gemini 3.5 Flash as a portability guardrail and cloud control;
- fixed Gemini Pro judge through LiteLLM;
- global prompt optimization only;
- P0/P1/P2 comparison and at most one bounded P3 revision;
- direct, inspectable prompt authoring rather than an automated prompt
  optimizer;
- use of the private real development corpus within the disclosure boundary
  below;
- preservation of the twenty-conversation holdout for B3C;
- publication-oriented methodology evidence, while final article drafting and
  publication remain separate work.

## Research Questions

Answer:

1. Can clearer global prompts improve small-model structured-output reliability?
2. Does concise schema-first prompting outperform the accepted baseline?
3. Do bounded synthetic few-shot examples improve reliability or semantic
   quality enough to justify their token and latency cost?
4. Are gains shared by Qwen and Phi, or are they model-specific?
5. Does the same prompt package remain reliable with Gemini 3.5 Flash?
6. Which tasks are easiest and hardest to improve?
7. Which failure categories move: context, timeout, JSON, schema, evidence, or
   semantic disagreement?
8. Does improved schema validity translate into better deterministic and
   fixed-judge quality?
9. How much prompt-token and latency overhead does each strategy add?
10. Is there one defensible package to freeze before the one-shot holdout?

## Accepted Baselines And Invariants

Treat all accepted packages and private artifacts as immutable.

### Full 120-Case Context Baselines

| Candidate | Valid | Total | Valid rate | Macro UTS |
| --- | ---: | ---: | ---: | ---: |
| Gemini 3.5 Flash | 112 | 120 | 93.3% | 88.4 |
| Qwen3.5-4B 8K | 84 | 120 | 70.0% | 61.9 |
| Phi-4 Mini 8K | 77 | 120 | 64.2% | 50.0 |

B3A found no recovered prior context failure at 16K and selected common 8K.
Do not use the 16K packages as B3B baselines.

### Hold Constant Across P0/P1/P2 And Optional P3

- exact ten development conversations and 40 ordered task cases;
- exact twenty holdout identities, kept inaccessible to B3B execution;
- frozen source inputs and FABLE references;
- task names and task versions unless a prompt version field is explicitly
  separated from the semantic task contract;
- input selectors, truncation, `max_input_chars`, and recent-message counts;
- response schemas and application finalizers;
- common 8,192 context;
- exact accepted Qwen and Phi GGUF bytes, revisions, Q4_K_M quantization, and
  loaded model identities;
- accepted local runtime/device policy and parallelism one;
- accepted Gemini 3.5 Flash provider/model/region/authentication identity;
- temperature, output-token limits, reasoning policy, timeouts, retries, and
  concurrency;
- fixed judge model, region, ADC route, rubric v1, schema contracts, and
  generation policy;
- scoring formulas, invalid-output treatment, and UTS formula;
- application code after the Gate 1 manager commit.

The only intended experimental variable after Gate 1 is the complete four-task
prompt package.

## Scope

### In Scope

- add generic, backward-compatible non-prefix selection-manifest support to the
  development-only `bench` harness;
- add focused tests and operator documentation for that support;
- freeze a metadata-only, provider/length/date-balanced private 10/20 split;
- prove the split was frozen without model outcomes, FABLE labels, or raw
  conversation content;
- reconstruct the ten development cases from complete accepted authority data;
- reuse exact P0 candidate and judge evidence for the ten development
  conversations from accepted 8K packages;
- author P1 and P2 as complete global four-prompt packages;
- run P1/P2 on Qwen, Phi, and Gemini Flash;
- verify, deterministically score, and fixed-Pro judge every eligible result;
- allow one predeclared P3 global revision only when its trigger is met;
- apply the predeclared package-selection rule;
- freeze the selected package and full provenance before holdout access;
- produce a detailed completion report and article-ready methodology brief.

### Out Of Scope

- accessing holdout raw text or references after the metadata split is frozen;
- generating, scoring, or judging any of the 80 holdout task cases;
- changing context above or below 8,192;
- model-specific prompts or generation settings;
- per-task cherry-picking across prompt packages;
- automatic prompt optimization frameworks or vendor prompt optimizers;
- DSPy, prompt search, evolutionary search, reinforcement learning, fine-
  tuning, LoRA, or weight changes;
- new teacher references or human review;
- output repair, JSON repair, automatic truncation, or hidden retries;
- another local or hosted candidate;
- judge replacement or rubric revision;
- production AI-task default promotion;
- final independent evaluation-set creation;
- B3C execution;
- WP-5.2C1 VM work;
- final article copy, graphics, publication, or statistical significance
  claims;
- embeddings, retrieval, MCP, or ingestion changes.

## Private Working Layout

Use distinct ignored roots. Exact local absolute paths remain private.

```text
.chronicle/eval/dev-v1/runs/wp-5.2b3b/
  split/
  p0-reuse/
  p1/
    qwen/
    phi/
    gemini/
  p2/
    qwen/
    phi/
    gemini/
  p3/                 # only when the trigger is met
  analysis/
  selected/
  tmp/
```

Do not modify or place output under:

- WP-5.2C1 roots;
- accepted P0 candidate packages or judge runs;
- B3A 16K roots;
- the frozen database;
- the live database;
- accepted input/reference directories;
- accepted selection or task catalogs.

## Gate 0: Preflight And Isolation

Follow `md/agent-operating-notes.md`.

Verify and record:

```powershell
poetry env info --path
git status --short
git branch --show-current
git rev-parse HEAD
poetry run python -m bench --help
poetry run python -m bench prepare --help
poetry run python -m bench generate --help
poetry run python -m bench verify --help
poetry run python -m bench score --help
poetry run chronicle --ai-task list
```

Require:

- Poetry resolves to this repository's `.venv`;
- branch is `codex/wp-5.2b3b-prompt-development`;
- tracked checkout is clean;
- the handoff is present in HEAD;
- frozen DB integrity, schema version, and expected accepted counts pass;
- live/frozen DB fingerprints are captured privately;
- accepted Qwen/Phi/Gemini P0 packages and judge evidence verify unchanged;
- accepted 30-conversation selection, 120 inputs, 120 FABLE references, and
  task catalogs verify unchanged;
- WP-5.2C1 artifacts are identified and excluded from all writes;
- no competing LM Studio generation is running.

## Gate 1: Generic Non-Prefix Selection Support

### Required Behavior

Extend only the development `bench` harness so preparation, generation,
verification, deterministic scoring, and judge accounting can bind to an
explicit private ordered conversation-selection manifest.

The implementation must:

1. add a strict, versioned selection-manifest schema;
2. accept a manifest through evaluation configuration or an equally coherent
   repository pattern used by every stage;
3. make it mutually exclusive with `--conversation-limit` prefix scoping;
4. resolve every selected conversation against the complete accepted 30-
   conversation authority;
5. reject duplicate, unknown, missing, reordered, or out-of-authority entries;
6. preserve the declared ordered identities;
7. bind the selection format/version/role/content identity into bundle,
   package, verification, scoring, and judge scope identity;
8. reconstruct the same scope independently during verification and scoring;
9. bind only content identities, never a machine-private absolute path;
10. support at least `development` and `holdout` role values without allowing a
    B3B development config to load the holdout role;
11. keep existing no-limit 30/120 behavior unchanged;
12. keep existing `--conversation-limit` frozen-prefix behavior unchanged;
13. remain resumable, deterministic, and archive-safe;
14. preserve existing package backward compatibility;
15. avoid private IDs, paths, or content in tracked tests and documentation.

The private manifest should contain, at minimum:

- format and algorithm versions;
- role: `development` or `holdout`;
- source 30-conversation selection identity;
- ordered selected conversation identities;
- conversation and expected task-case counts;
- provider, length-stratum, and date-bin aggregate counts;
- deterministic serialization/hash identity;
- creation timestamp.

### Focused Test Matrix

Add synthetic tests for:

- a valid non-prefix ordered selection;
- development and holdout role validation;
- expected conversation/case counts;
- unknown conversation rejection;
- duplicate rejection;
- order-tampering rejection;
- source-selection identity mismatch;
- manifest content/hash mismatch;
- private-path non-leakage;
- prepare/generate/package/verify/score scope continuity;
- judge eligibility using only selected cases;
- mutual exclusion with `conversation_limit`;
- unchanged frozen-prefix behavior;
- unchanged full 30-conversation behavior;
- historical package compatibility.

Update `docs/development-evaluation.md` with the generic operator workflow. Do
not document private paths or IDs.

### Mandatory Manager Commit Checkpoint

After Gate 1:

1. run focused tests, full tests, Ruff, Poetry, CLI help, and `git diff --check`;
2. write a concise Gate 1 addendum in the eventual completion report or a
   temporary privacy-safe checkpoint note;
3. report exact changed files and `git status --short`;
4. leave everything unstaged and uncommitted;
5. stop before freezing prompts or calling any model.

The manager will validate and commit the generic patch. Resume this handoff
from the new clean commit. Do not ask the owner to run Git commands and do not
continue generation from a dirty tracked implementation.

## Gate 2: Freeze The 10/20 Split

Create the split from metadata only. Do not inspect raw messages, FABLE
references, per-case model outputs, per-case judge results, or per-case
historical failures before the split is frozen.

### Required Quotas

| Provider | Development | Holdout |
| --- | ---: | ---: |
| ChatGPT | 3 | 7 |
| OpenAI Codex | 3 | 7 |
| Claude | 2 | 3 |
| Claude Code | 2 | 3 |
| **Total** | **10** | **20** |

The development set must contain:

- four short, three medium, and three long conversations;
- representation across the available activity-date span;
- no duplicate source-content hash;
- exactly four task cases per conversation, 40 total.

Use a deterministic metadata-only algorithm with an explicit version and stable
tie-break. Prefer a constrained selection over manual choice:

1. satisfy provider quotas exactly;
2. satisfy 4/3/3 short/medium/long quotas exactly;
3. maximize date-bin coverage using only accepted activity date metadata;
4. break remaining ties by deterministic hash derived from the frozen source
   content identity plus a fixed public seed such as
   `wp-5.2b3b-split-v1`;
5. assign the remaining twenty conversations to holdout in their accepted
   frozen order.

If the exact quotas are mathematically impossible, stop and report the
constraint conflict. Do not hand-pick alternatives after seeing outcomes.

Freeze separate private development and holdout selection manifests and their
hashes. After freezing:

- B3B may load only the development manifest;
- the holdout manifest may be validated structurally but its raw inputs,
  references, historical per-case outputs, and labels must remain unopened;
- no B3B bundle, package, scoring run, analysis file, or prompt-authoring note
  may contain a holdout case identity;
- record proof that the split predates every P1/P2/P3 model call.

## Gate 3: Freeze Prompt Hypotheses Before Calls

Prompt authoring is direct and inspectable. Do not use an automated optimizer,
prompt marketplace, external tuning service, or unrecorded auxiliary model.

The executor may use its own reasoning to draft prompts. Record the executor
model/interface used for prompt authorship in the completion report. If any
additional model is used to draft or critique a prompt, stop and obtain manager
approval before disclosing private development material to it.

Prompt candidate files must contain no private conversation content, private
IDs, paths, credentials, FABLE reference text, or model outputs. Use synthetic,
obviously fictional examples only.

Create versioned prompt catalogs under a tracked development-only location such
as:

```text
bench/prompts/wp-5.2b3b/
  README.md
  p1-schema-first.yaml
  p2-bounded-few-shot.yaml
  p3-global-revision.yaml       # only when triggered
  selected-prompt-package.yaml # written only after selection
```

These files remain unstaged/uncommitted during execution and may coexist as
expected untracked files after the Gate 1 clean commit. The manager decides
what to commit after final validation. Do not alter production
`ai-tasks.default.yaml` or packaged resources in B3B.

### P0: Accepted Baseline

- Reuse exact accepted P0 outputs and fixed-Pro judge evidence for the ten
  development conversations.
- Reconstruct the 40-case subset without changing accepted packages.
- Pin prompt catalog hashes, task versions, schemas, selectors, finalizers, and
  generation settings.
- Do not regenerate P0 unless runtime identity drift makes the comparison
  invalid and the manager explicitly approves a contemporaneous paired rerun.

### P1: Concise Contract And Schema First

Create one revised prompt per task. Apply the same principles consistently:

- state the task and output contract before descriptive guidance;
- require one JSON object and no prose, Markdown, code fences, or hidden
  reasoning;
- enumerate allowed enum values exactly;
- state field limits and cross-field rules concisely;
- require evidence IDs only from the supplied allowed message-ID set;
- forbid inventing evidence IDs, dates, blockers, or next actions;
- require dates to be copied from authoritative supplied metadata;
- distinguish `null`, empty list, `unknown`, and absent information;
- request concise reasons rather than chain-of-thought;
- avoid repeating the full schema unnecessarily in natural language;
- retain the exact response schema as application authority.

Record a pre-run hypothesis for each task and the expected failure categories
P1 is intended to reduce.

### P2: Contract First Plus Bounded Synthetic Few-Shot

Start from P1 and add bounded synthetic examples:

- at most two short examples per task;
- all examples must be fictional and privacy-safe;
- use valid-looking but synthetic message IDs and timestamps;
- include at least one boundary or `unknown`/`null` example where relevant;
- show only final JSON, never chain-of-thought;
- keep total prompt growth measured and reported;
- do not change schemas or application validation to fit examples.

Record a pre-run hypothesis for each task and the expected benefit versus token
and latency overhead.

Before any P1/P2 candidate call, freeze and hash:

- both complete four-prompt packages;
- normalized prompt text and byte representation;
- prompt token/character counts;
- task catalog identity;
- hypotheses;
- comparison invariants;
- selection rule;
- P3 trigger;
- external-call budget.

## Gate 4: Local Qwen And Phi Runs

Run P1 and P2 locally before Gemini portability generation.

For each prompt package and model:

1. reproduce the accepted artifact/runtime identity;
2. load at context 8,192 and parallelism one;
3. confirm API identity and effective settings;
4. run a four-task synthetic strict-schema transport gate;
5. require 4/4 terminal schema-valid synthetic outputs;
6. prepare a fresh ten-conversation/40-case bundle bound to the development
   selection manifest and prompt hash;
7. generate all 40 positions;
8. resume interruptions without repeating completed positions;
9. preserve first-attempt failures and normalized categories;
10. package and verify;
11. run deterministic-only scoring;
12. capture wall time, p50/p95 by task and overall, tokens, resource settings,
    and interruption/resume events;
13. unload one model before loading the other when needed.

Expected new local positions before optional P3:

```text
2 prompt packages x 2 models x 10 conversations x 4 tasks = 160
```

Do not change timeout, output tokens, reasoning, runtime, context, prompt, or
schema to rescue a failed case.

## Gate 5: Gemini 3.5 Flash Portability Runs

After P1/P2 prompts are frozen and local candidate generation is terminal, run
the same two prompt packages unchanged with the accepted hosted Gemini 3.5
Flash profile.

Expected new hosted candidate positions before optional P3:

```text
2 prompt packages x 10 conversations x 4 tasks = 80
```

Requirements:

- exact accepted logical provider/model identity;
- Vertex region `global`;
- ADC authentication;
- explicit `--allow-remote --confirm-private-eval` flags;
- no FABLE reference sent during candidate generation;
- candidate-model identity captured in private provenance;
- one unique bundle/work/package identity per prompt package;
- every position terminal and accounted;
- package verification and deterministic scoring local;
- no hidden retry or model substitution.

## External Disclosure Authorization

The owner has approved the following bounded B3B disclosure so the executor
must not request repetitive confirmation inside this exact scope.

### Hosted Candidate Authorization

The owner authorizes sending the selected ten private development conversation
inputs, the applicable P1/P2 task prompt, and structured response schema to
Vertex AI `gemini-3.5-flash` in `global` through ADC for up to 80 planned
candidate positions. If and only if the P3 trigger below is met, the same owner
authorization covers one additional P3 wave of up to 40 positions. FABLE
references and judge results must not be sent during candidate generation.

### Fixed-Judge Authorization

The owner authorizes sending each eligible B3B development source input,
candidate output, applicable FABLE reference, task schema, and rubric to Vertex
AI `gemini-3.1-pro-preview` in `global` through ADC. This covers P1/P2 results
for Qwen, Phi, and Gemini, plus P3 results only when the trigger is met. Maximum
planned eligible judge positions are 240 before P3 and 360 with P3, plus the
accepted configured bounded retry for terminal provider failures and one
four-task synthetic judge gate. Ordinary Vertex usage cost is approved.

Do not request confirmation again unless any of these change:

- the ten-conversation development scope;
- disclosed fields;
- provider, model, region, authentication route, or rubric;
- retry/call ceiling;
- a new prompt package beyond P1, P2, and the single conditional P3;
- a materially different expected cost;
- an unexpected sensitive-field or credential exposure.

Stop immediately for any such expansion.

## Gate 6: Fixed-Pro Judging And Cache Proof

Use the accepted fixed judge:

```text
model: vertex_ai/gemini-3.1-pro-preview
region: global
authentication: ADC
rubric: 1
temperature: 0
max_tokens: 1000
reasoning_effort: none
```

1. Run the four-task synthetic judge gate and require 4/4 valid results.
2. Judge every eligible P1/P2 candidate output.
3. Preserve terminal judge failures after only the accepted bounded retry.
4. Run identical cache-only replay for every package.
5. Require zero new provider calls and byte-stable attempt evidence.
6. Keep candidate identity hidden from the judge prompt.
7. Do not rejudge accepted P0 cases; reuse matching accepted judge evidence.

## Gate 7: Optional Single P3 Revision

P3 is allowed only when all conditions below are met:

1. P1 and P2 have completed across Qwen and Phi;
2. the same task plus normalized failure category appears in both local models;
3. at least four development cases across the two local models exhibit that
   shared pattern;
4. the pattern can plausibly be addressed through model-neutral prompt wording;
5. the change does not alter schema, selector, finalizer, context, generation
   settings, or application behavior;
6. the trigger and aggregate evidence are recorded before P3 text is authored.

If triggered:

- choose P1 or P2 as the declared base using the selection rule below;
- make one bounded global revision addressing only the shared pattern;
- write and freeze all four task prompts as one P3 package, even if only one
  task wording changes;
- record exact normalized diffs and rationale;
- run P3 on Qwen, Phi, and Gemini for 120 new positions total;
- verify, deterministically score, judge, and cache-prove exactly as above.

If the trigger is not met, do not invent P3 merely to improve the narrative.
Record `P3 not triggered` and continue selection among P0/P1/P2.

No P4 or second revision is allowed in B3B.

## Package Selection Rule

Apply this rule exactly after all authorized packages are terminal. Invalid
candidate outputs and terminal judge failures remain in denominators and score
zero where required by the accepted UTS contract.

### Primary Local Reliability

For each complete prompt package, calculate across Qwen and Phi:

- usable cases: schema-valid and evidence-valid;
- pooled usable count out of 80;
- usable count per local model out of 40;
- usable count per task out of 20;
- minimum task usable rate;
- failure taxonomy by model and task.

Rank packages lexicographically by:

1. highest pooled Qwen+Phi usable count;
2. highest lower-of-two local-model usable count;
3. highest minimum pooled task usable count;
4. highest pooled whole-case macro UTS;
5. lowest prompt-token overhead;
6. simpler/earlier package, with P0 winning a complete tie.

### Regression Guardrails

A non-P0 package is not eligible for selection when:

- either local model loses more than one usable case versus its exact P0
  ten-conversation baseline without a larger pooled gain;
- any task loses more than one pooled usable case versus P0 without a larger
  gain in the task targeted by the declared hypothesis;
- Gemini loses more than two usable cases out of 40 versus its P0 development
  baseline;
- any Gemini task loses more than one usable case out of ten;
- prompt changes introduce a new dominant failure category;
- package identity or invariant verification fails.

These are development guardrails, not statistical significance thresholds.

### Semantic Tie-Break And Interpretation

Use deterministic agreement, confusion matrices, fixed-judge dimensions, and
whole-case UTS only after reliability ranking. Report them separately rather
than collapsing all behavior into one unexplained score.

Gemini is a portability guardrail, not the optimization target. A package does
not win merely because Gemini improves. Do not select different prompt versions
for different tasks or models.

If the rule produces an operationally unreasonable result, report the exact
conflict and leave selection to the manager. Do not alter the rule after seeing
results.

## Metrics And Analysis Requirements

Report P0/P1/P2 and optional P3 for every model and task.

### Reliability

- expected, valid, invalid, and unaccounted cases;
- schema-valid and evidence-valid rates;
- JSON, schema, evidence, context, timeout, provider, and other failures;
- first-attempt versus current-attempt accounting;
- retry and resume events.

### Deterministic Semantics

- work-mode confusion matrix, exact agreement, precision, recall, support;
- last-activity confusion matrix and corresponding statistics;
- title-fit confusion matrix and corresponding statistics;
- summary date, length, and evidence validity;
- all denominators.

### Fixed-Judge Semantics

- eligible, completed, failed, skipped invalid;
- dimension means by model and task with denominators;
- whole-case UTS with invalid and judge-failed cases scoring zero;
- macro UTS and task UTS;
- valid-output quality separately from whole-case utility;
- judge failure categories;
- cache-only proof.

### Operational Cost

- prompt characters and estimated/observed prompt tokens by task/package;
- candidate prompt/completion/total usage when available;
- p50/p95 latency overall and by task;
- observed wall time and model load/setup time separately;
- local runtime, CPU/RAM/graphics provenance;
- hosted call counts and privacy-safe cost estimate;
- token and latency overhead relative to P0;
- optional P3 incremental cost separately.

### Task Difficulty

Classify task difficulty from evidence, not intuition. Include:

- baseline and best-package reliability by task;
- common failure categories;
- semantic agreement and judge quality;
- sensitivity to schema-first and few-shot prompting;
- whether improvement is shared across models;
- confidence and corpus limitations.

## Freeze The Selected Package

Before any B3C holdout access, create a private immutable selection manifest and
a privacy-safe tracked selected prompt package.

Bind:

- selected package ID and prompt texts;
- all four normalized prompt hashes and aggregate package hash;
- P0/P1/P2/P3 trial identities;
- exact selection-rule calculations;
- rejected variants and reasons;
- task/schema/selector/finalizer versions and hashes;
- model/runtime/generation/judge identities;
- development split identity;
- holdout split identity without exposing private IDs;
- context 8,192;
- freeze timestamp and application commit;
- confirmation that no holdout per-case content/outcome was inspected.

After freeze, do not edit selected prompts. Any later edit creates a new work
package and invalidates B3C as a one-shot holdout.

Do not promote the selected package into production defaults during B3B. That
decision follows B3C manager review.

## Article-Ready Methodology Brief

Create:

```text
md/handoffs/reports/WP-5.2B3B-prompt-development-evidence-brief.md
```

It must be privacy-safe and contain enough evidence for a future technical
article:

1. problem statement and research questions;
2. why 8K was frozen after B3A;
3. 10-development/20-holdout methodology;
4. proof that split selection used metadata rather than outcomes;
5. P0/P1/P2 hypotheses and normalized prompt differences;
6. optional P3 trigger, evidence, and exact bounded change;
7. model/runtime/generation/judge provenance;
8. complete aggregate reliability tables;
9. per-task failure taxonomies;
10. deterministic confusion matrices and statistics;
11. fixed-judge dimensions and denominators;
12. UTS and valid-output-quality comparisons;
13. prompt-token, latency, wall-time, and cost comparisons;
14. global portability comparison across Qwen, Phi, and Gemini;
15. task-difficulty interpretation;
16. selected package and rejected variants;
17. development-set overfitting risks;
18. explicit statement that holdout results do not yet exist;
19. chart-ready aggregate tables;
20. three to six supported observations with metric, denominator, caveat,
    confidence, and prohibited overclaim;
21. suggested figures and article outline;
22. links to B3A, B3B completion evidence, and future B3C placeholder.

Suggested figures:

1. usable-rate change by prompt package, model, and task;
2. failure-category movement from P0 to each variant;
3. UTS versus schema/evidence reliability;
4. prompt-token overhead versus usable-case gain;
5. local-model gain with Gemini portability guardrail;
6. task-difficulty heatmap.

Do not write final article copy or claim holdout generalization.

## Required Completion Report

Write:

```text
md/handoffs/reports/WP-5.2B3B-completion-report.md
```

Required sections:

1. status: `ready for PM validation`, `partial`, or `blocked`;
2. executive summary;
3. branch, starting commit, Gate 1 commit, and final application identity;
4. scope and exclusions;
5. Gate 1 implementation and compatibility evidence;
6. frozen DB, source selection, input, reference, and P0 verification;
7. metadata-only split algorithm and aggregate quotas;
8. holdout non-access proof;
9. P0 reconstruction and reuse evidence;
10. P1 hypotheses, prompt diffs, and hashes;
11. P2 hypotheses, examples policy, prompt diffs, and hashes;
12. Qwen P1/P2 accounting;
13. Phi P1/P2 accounting;
14. Gemini P1/P2 accounting;
15. package verification and deterministic scoring;
16. external authorization and exact call accounting;
17. fixed-judge results and cache-only replay;
18. P3 trigger decision and evidence;
19. P3 results when applicable;
20. complete reliability and failure taxonomy;
21. deterministic semantic metrics;
22. fixed-judge metrics and UTS;
23. prompt-token, latency, wall-time, resource, and hosted-cost evidence;
24. task-difficulty analysis;
25. exact package-selection calculation;
26. selected package freeze and rejected variants;
27. B3C readiness statement;
28. methodology/article brief delivery;
29. privacy and external-disclosure accounting;
30. live/frozen DB immutability;
31. historical package and WP-5.2C1 immutability;
32. focused/full/Ruff/Poetry/help/diff validation;
33. known limitations and unresolved questions;
34. acceptance checklist;
35. exact tracked and untracked delivery files;
36. final `git status --short`;
37. confirmation that nothing was staged or committed.

Do not include private conversation/message IDs, titles, URLs, raw inputs,
outputs, references, rationales, absolute private paths, private hashes,
credentials, cloud project identity, or machine-user identity.

## Acceptance Criteria

B3B is ready for final PM validation only when:

1. Poetry resolves to the repository `.venv`.
2. Execution occurs on the dedicated B3B branch.
3. Gate 1 starts from a clean tracked checkout.
4. Generic non-prefix selection support is strict and backward compatible.
5. Gate 1 focused and full tests pass.
6. The manager validates and commits Gate 1 before model calls.
7. Frozen/live DB and accepted evidence identities are captured unchanged.
8. P0 Qwen/Phi/Gemini packages and judge evidence verify unchanged.
9. Development/holdout provider quotas are exactly 3/3/2/2 and 7/7/3/3.
10. Development length quotas are exactly 4/3/3.
11. Split creation uses metadata only and is frozen before prompt calls.
12. Development contains 10 conversations and 40 task cases.
13. Holdout contains 20 conversations and 80 task cases.
14. B3B never generates, scores, judges, or inspects holdout per-case data.
15. P1 and P2 are frozen before their first candidate calls.
16. P1/P2 contain no private data and use no automated optimizer.
17. Qwen P1 and P2 each have 40 terminal positions.
18. Phi P1 and P2 each have 40 terminal positions.
19. Gemini P1 and P2 each have 40 terminal positions.
20. All six P1/P2 candidate packages verify.
21. Deterministic scoring completes for every package.
22. Every eligible output is judged or has an explicit terminal judge failure.
23. Every judged package passes zero-call cache-only replay.
24. Invalid outputs remain in denominators and are not repaired.
25. Context and all non-prompt experimental variables remain fixed.
26. P3 is absent unless every trigger condition is documented.
27. If triggered, P3 has 120 terminal positions across all three models and all
    corresponding verification/scoring/judging/cache evidence.
28. No P4, model-specific prompt, or per-task cherry-picked package exists.
29. The predeclared selection rule is applied without post-hoc changes.
30. One complete four-task prompt package is selected or a precise unresolved
    selection conflict is reported.
31. The selected package and decision provenance are frozen before B3C.
32. Production prompt defaults remain unchanged.
33. The methodology brief exists at the required path.
34. The completion report exists at the required path.
35. Live/frozen DBs, accepted packages, and WP-5.2C1 artifacts are unchanged.
36. No private artifact or credential is tracked.
37. Full tests, Ruff, Poetry, CLI help, and `git diff --check` pass.
38. Nothing is staged or committed by the executor.

## Required Validation Commands

At Gate 1 and final delivery, run at minimum:

```powershell
poetry env info --path
poetry run pytest
poetry run ruff check .
poetry check
poetry run python -m bench --help
poetry run python -m bench prepare --help
poetry run python -m bench generate --help
poetry run python -m bench verify --help
poetry run python -m bench score --help
poetry run chronicle --help
poetry run chronicle --ai-task list
git diff --check
git status --short
git ls-files ".chronicle/*" "*.db" "*.sqlite" "*.zip" "exports/*"
```

Also run and record privacy-safe results for:

- selection-manifest focused tests and compatibility matrix;
- private split validation;
- P0 subset reconstruction;
- every synthetic transport gate;
- every candidate generation/package verification;
- deterministic scoring reconciliation;
- fixed-judge synthetic gate and accounting;
- cache-only zero-call replay;
- selected-package freeze validation;
- holdout non-access validation;
- DB, accepted-package, and WP-5.2C1 immutability.

## Failure And Retry Policy

Every expected candidate position must finish as a valid success or explicit
terminal normalized failure.

Allowed without new approval:

- resume missing positions after interruption;
- accepted bounded retry for infrastructure write/sharing failures;
- accepted bounded judge retry for terminal provider failures;
- the one conditional P3 wave when its trigger is met.

Not allowed:

- retry invalid JSON, schema, evidence, semantic, timeout, or context failures
  to improve model metrics;
- repair or truncate outputs;
- change prompt text after a package's first call;
- increase context, output tokens, timeout, retries, or concurrency;
- change runtime, artifact, quantization, model, provider, region, rubric, or
  schema;
- replace failed cases with another model;
- access holdout cases;
- add another prompt package.

Model failure is experimental evidence, not automatically a software defect.
If a genuine generic harness defect appears after Gate 1, preserve all evidence
and stop for manager review. Do not silently patch and continue from a dirty
implementation.

## Stop Rules

Stop and report when:

- the exact accepted model/runtime or fixed judge identity cannot be
  reproduced;
- split quotas cannot be met without outcome/label/content inspection;
- a holdout case is accidentally loaded or disclosed;
- any non-prompt experimental variable drifts;
- the P1/P2 prompt text changes after first use;
- P3 would require model-specific or schema/application changes;
- provider/model/region/rubric differs from authorization;
- projected calls or cost exceed the authorized ceiling;
- package or cache verification fails;
- frozen/live DB, accepted packages, or WP-5.2C1 artifacts change;
- private data, credentials, or private identities appear in Git;
- destructive cleanup or unbounded retry would be required.

Do not report a safety stop as completion.

## Final Delivery Message

Return:

- status;
- Gate 1 commit identity;
- split aggregate counts and holdout non-access proof;
- P0/P1/P2 and optional P3 valid counts by model and task;
- deterministic, judge, UTS, latency, token, and cost summary;
- P3 trigger decision;
- selected complete prompt package and selection-rule result;
- B3C readiness;
- methodology brief path;
- completion report path;
- validation totals;
- exact delivery files;
- final `git status --short`;
- confirmation that nothing was staged or committed.
