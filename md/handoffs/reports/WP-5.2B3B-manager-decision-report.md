# WP-5.2B3B Global Prompt Development: Manager Decision Report

Date: 2026-08-05

Status: **Option A and the `f25505a` execution identity were approved; continuation completed**

Authoritative handoff: `md/handoffs/WP-5.2B3B-global-prompt-development.md`

Detailed execution record: `md/handoffs/reports/WP-5.2B3B-execution-progress.md`

## Decision record and outcome

The manager approved Option A exactly as recommended: one unchanged 40-position Phi P1
development run from a clean dedicated checkout pinned to `f25505a`, with both repeated 3/4
fictional gates retained as evidence and no rescue retry. Phi P2 remained subject to its original
4/4 gate. Existing Gemini candidate and fixed-judge authorization remained in force.

The approved continuation completed without a mandatory stop:

- Phi P1 produced 32/40 valid; Phi P2 passed 4/4 then produced 32/40 valid;
- Gemini P1/P2 produced 32/40 and 36/40 valid;
- all six packages verified and deterministically scored;
- the fixed judge completed 182/184 eligible results with two preserved terminal failures;
- cache-only replay made zero provider calls;
- P3 was not triggered;
- the predeclared selection rule selected and froze unchanged P0.

The final decision evidence is in `WP-5.2B3B-completion-report.md` and
`WP-5.2B3B-prompt-development-evidence-brief.md`. The historical analysis below is retained as the
exact pre-authorization decision basis.

## 1. Executive summary

WP-5.2B3B has not failed as an implementation project, but it has reached a real experimental
protocol conflict.

The development/holdout split, P0 reconstruction, P1/P2 prompt freeze, generic prompt-catalog
support, post-patch Qwen fictional gates, and Qwen P1/P2 development runs are complete and
verified. The twenty holdout conversations remain unopened and untouched.

Execution stopped before any private Phi generation because the mandatory Phi P1 fictional
strict-schema gate returned 3 valid tasks out of 4. The same gate was repeated once, unchanged,
as a separately preserved diagnostic and again returned 3/4. In both runs, only
`title-assessment` failed application-schema validation. The accepted Phi model artifact,
quantization, model identity, context, and parallelism were reproduced. This is therefore best
classified as repeatable model-plus-prompt behavior, not a transport outage or an identified
harness defect.

The handoff simultaneously says:

- require a 4/4 fictional gate before private generation; and
- preserve model failures as experimental evidence rather than rescuing them with retries or
  changed settings.

Under a strict reading, work must remain stopped. Continuing requires an explicit manager
decision to make a narrow, recorded exception to the 4/4 prerequisite.

### Recommended decision

Authorize exactly one bounded exception for **Phi P1 only**:

- accept the two preserved 3/4 fictional gates as repeatable model evidence;
- run one 40-position Phi P1 development package with all frozen settings unchanged;
- preserve every terminal failure and make no rescue retry;
- keep Phi P2 subject to the original 4/4 fictional-gate requirement;
- stop again if Phi P2 does not pass 4/4 or if any other invariant changes.

This recommendation preserves the failed gate as evidence and allows the experiment to measure
whether the failure generalizes to the private development scope. It avoids modifying the prompt,
schema, model, runtime, token limits, timeout, retry policy, or holdout boundary.

Before making further calls, execution should also be pinned to the accepted clean application
identity `f25505ae3762fae337d3ed0b7a364689f0cc8853`. The current branch HEAD has moved for unrelated
documentation work. The safest continuation is a clean dedicated worktree or equivalent checkout
at the accepted application commit, so remaining packages share the same application identity as
the completed Qwen packages.

## 2. Decision requested from the manager

The manager and owner need to decide two things:

1. **Phi gate policy:** approve the narrow Phi P1 exception above, or close B3B as an incomplete
   experiment at the present checkpoint.
2. **Execution identity:** approve continuing from an exact clean checkout of `f25505a`, rather
   than recording new candidate packages against the branch's newer documentation-only HEAD.

No additional disclosure authorization is required if the already approved provider, models,
region, private development scope, disclosed fields, call ceilings, retry boundaries, and cost
assumptions remain unchanged.

## 3. Current repository and provenance state

Observed repository state at this report checkpoint:

| Item | State |
| --- | --- |
| Branch | `codex/wp-5.2b3b-prompt-development` |
| Current branch HEAD | `b1d3f8f1ad42fb48aa8c11ee80f76dcf63ac4f1c` |
| Accepted B3B application checkpoint | `f25505ae3762fae337d3ed0b7a364689f0cc8853` |
| Prompt-catalog implementation commit | `0e920c8` |
| Gate 1 implementation commit | `b15bf9632a344c0cac3b42a68142a6829c973b47` |
| Existing unstaged B3B change before this report | execution-progress report only |
| Staged changes | none |
| Executor commits after the current B3B stop | none |

The committed difference from `f25505a` to the current branch HEAD is documentation/publication
work outside the B3B benchmark implementation. No benchmark or application code drift was found
in that committed range. Nevertheless, candidate-package provenance records an exact application
commit, so “documentation-only” is not the same as “identity-equivalent.” Mixing application
commit identities inside one experiment would create an avoidable audit qualification.

The private append-only provenance amendment already binds `f25505a`, the prompt-catalog
implementation, the prompts-only policy, the unchanged split identities, and the unchanged P1/P2
prompt identities. Existing Qwen evidence must not be rewritten merely because the branch later
moved.

## 4. Scope and experimental controls

The experiment compares one complete four-task prompt package at a time across:

- Qwen3.5-4B at 8K locally;
- Phi-4 Mini at 8K locally;
- Gemini 3.5 Flash through Vertex AI `global` as the cloud portability guardrail.

The four tasks are conversation summary, work mode, last activity, and title assessment.

The package definitions are:

- **P0:** accepted historical baseline;
- **P1:** one global schema-first four-task package;
- **P2:** P1 plus bounded, obviously fictional final-JSON examples;
- **P3:** absent and allowed only if every predeclared shared-local-failure trigger is met.

Held constant across packages are task schemas, selectors, finalizers, task versions, generation
profiles, input limits, context, runtime identity, model artifact, quantization, and evaluation
scope. Only `system_prompt` and `user_prompt` may differ between the immutable P0 authority catalog
and the active P1/P2 experimental catalog.

The prompts are global: the same full P1 or P2 package must be used unchanged for every model.
Model-specific prompts and task-by-task package selection are prohibited.

## 5. Work completed and accepted

| Phase | Result | Acceptance or verification state |
| --- | --- | --- |
| Ordered selection-manifest support | Implemented and validated across preparation, generation, verification, deterministic scoring, and judge accounting | Manager accepted; commit `b15bf96` |
| Metadata-only split | Frozen 10-conversation development and 20-conversation holdout manifests | Strict schema, identity, count, quota, disjointness, and complement checks passed |
| P0 development reconstruction | Reused accepted candidates and judge evidence for only the selected 40 development cases | Reconciled without regeneration or provider calls |
| P1/P2 authoring and freeze | Complete four-task global prompt catalogs frozen | Prompt and non-prompt invariant checks passed |
| Prompt-catalog separation | Immutable authority catalog separated from active prompts-only experiment catalog | Manager accepted; commit `0e920c8` |
| Post-patch provenance | Append-only amendment created for clean application HEAD `f25505a` | Checksum and frozen-identity checks passed |
| Qwen fictional gates | P1 4/4; P2 4/4 | Passed with fictional data only |
| Qwen private generation | P1 40/40 terminal; P2 40/40 terminal | Complete |
| Qwen package verification | P1 and P2 | Passed |
| Qwen deterministic scoring | P1 and P2 | Complete |
| Phi P1 fictional gate | 3/4, repeated once unchanged with the same result | Current blocker |
| Phi private generation | 0 positions | Not started |
| Gemini private generation | 0 positions | Not started |
| Fixed-Pro judging | 0 calls | Not started |
| P3 | Absent | Trigger cannot yet be evaluated |

## 6. Development/holdout split and privacy proof

The split was selected exclusively from accepted metadata. Raw conversation inputs, references,
historical candidate outputs, labels, judge results, and per-case outcomes were not used to choose
the development cases.

| Scope | Conversations | Cases | ChatGPT | OpenAI Codex | Claude | Claude Code | Short | Medium | Long |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Development | 10 | 40 | 3 | 3 | 2 | 2 | 4 | 3 | 3 |
| Holdout | 20 | 80 | 7 | 7 | 3 | 3 | 6 | 7 | 7 |

Development date-bin coverage is early 2, middle 4, and late 4. The two scopes have zero overlap
and together partition all 30 accepted conversations.

Privacy boundary to date:

- holdout raw conversations opened: 0;
- holdout references opened: 0;
- holdout historical outputs, outcomes, labels, or per-case results opened: 0;
- holdout candidate positions generated: 0;
- holdout cases scored or judged: 0.

The holdout remains valid for the later one-shot WP-5.2B3C evaluation.

## 7. P0 baseline reconstructed on the development scope

| Model | Valid / 40 | Summary / 10 | Work / 10 | Last / 10 | Title / 10 | Terminal failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen3.5-4B 8K | 30 | 6 | 7 | 10 | 7 | context 6; schema 1; timeout 3 |
| Phi-4 Mini 8K | 32 | 7 | 8 | 10 | 7 | context 6; schema 2 |
| Gemini 3.5 Flash 8K | 38 | 8 | 10 | 10 | 10 | invalid JSON 1; schema 1 |

Accepted fixed-judge reuse accounting is:

- Qwen: 30 completed, 10 skipped-invalid;
- Phi: 32 completed, 8 skipped-invalid;
- Gemini: 37 completed, 1 terminal judge failure, 2 skipped-invalid.

These are immutable baseline results. They were reconstructed without regenerating candidates or
rejudging them.

## 8. Frozen prompt packages

| Package | Characters | UTF-8 bytes | Estimated tokens | Purpose |
| --- | ---: | ---: | ---: | --- |
| P0 | 3,109 | 3,109 | 658 | Accepted baseline |
| P1 | 4,202 | 4,202 | 870 | Explicit schema-first contracts and cross-field rules |
| P2 | 6,849 | 6,849 | 1,516 | P1 plus bounded fictional JSON examples |

The token counts above are pre-call estimates using `cl100k_base`, not provider-native usage.
P1 adds 212 estimated tokens over P0; P2 adds 858.

P1 and P2 prompt bytes and hashes remain unchanged from the accepted freeze. Their non-prompt task
fields remain structurally identical to P0. No private conversation, identifier, reference,
candidate result, or judge rationale was used to author them.

## 9. Completed Qwen results

Both packages ran against the same frozen 40-case development scope using the accepted
Qwen3.5-4B Q4_K_M artifact, context 8,192, and parallelism one.

### Reliability and failures

| Package | Valid / 40 | Summary | Work | Last | Title | Context failures | Timeout failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| P0 | 30 | 6 | 7 | 10 | 7 | 6 | 3 |
| P1 | 26 | 6 | 6 | 8 | 6 | 6 | 8 |
| P2 | 26 | 6 | 6 | 8 | 6 | 6 | 8 |

Both P1 and P2 are four usable cases below Qwen P0. This creates a serious regression-guardrail
risk, but package eligibility cannot be finalized until the paired Phi results and Gemini
portability results exist. The predeclared rule ranks pooled Qwen+Phi reliability first and then
applies local, task, and Gemini guardrails.

### Deterministic exact agreement

| Package | Work mode | Last activity | Title fit |
| --- | ---: | ---: | ---: |
| P1 | 20% | 60% | 50% |
| P2 | 30% | 60% | 60% |

P2 improved two deterministic label-agreement measures over P1, but it did not improve Qwen
usable-case reliability. Fixed-judge scores and whole-case UTS do not yet exist for either
package, so this is not enough to select P2.

### Latency

| Package | Summary p50 | Work p50 | Last p50 | Title p50 | p95 behavior |
| --- | ---: | ---: | ---: | ---: | --- |
| P1 | 87.6 s | 102.8 s | 106.1 s | 95.6 s | Approximately 180 s per task because terminal timeouts remain included |
| P2 | 62.5 s | 60.5 s | 69.1 s | 73.4 s | Approximately 180 s per task because terminal timeouts remain included |

P2 was materially faster at the median on Qwen. This is useful operational evidence but remains
secondary to the predeclared reliability order.

### Provider-reported generation tokens

| Package | Prompt tokens | Completion tokens | Total tokens |
| --- | ---: | ---: | ---: |
| P1 | 61,454 | 3,493 | 64,947 |
| P2 | 66,394 | 2,235 | 68,629 |

P2 used 4,940 more prompt tokens and 3,682 more total tokens than P1 across the 40 Qwen positions,
while producing fewer completion tokens.

### Operational event

The P1 command wrapper reached its one-hour orchestration timeout after 36 terminal positions.
The original generator process remained active, completed the remaining positions, and produced
the package. No completed position was invoked twice. All 40 positions have exactly one terminal
attempt.

## 10. Exact Phi gate evidence and diagnosis

The accepted Phi artifact and runtime were reproduced before any private Phi input was loaded:

- model: Phi-4 Mini Instruct;
- accepted GGUF identity: matched;
- quantization: Q4_K_M;
- context: 8,192;
- parallelism: one;
- provider: local LM Studio;
- prompt package: frozen P1;
- test data: fictional synthetic fixture only.

Two separately preserved runs produced the same aggregate outcome:

| Run | Summary | Work | Last | Title | Total |
| --- | --- | --- | --- | --- | ---: |
| Required Phi P1 fictional gate | valid | valid | valid | application-schema validation failure | 3/4 |
| Unchanged diagnostic reproduction | valid | valid | valid | application-schema validation failure | 3/4 |

The diagnostic reproduction changed no prompt, schema, runtime, model, artifact, context,
parallelism, timeout, output limit, or retry setting. No private conversation was used in either
run. Phi P1 private positions remain zero.

### What this evidence supports

- The endpoint was reachable and generated terminal responses.
- Three of the four task contracts passed strict schema validation.
- The same task and normalized failure class repeated under unchanged conditions.
- Accepted artifact and runtime identity were reproduced.
- The behavior is consistent with a model-plus-prompt structured-output weakness on the title
  task.

### What this evidence does not support

- It does not prove that all private title cases will fail.
- It does not prove that P2 will behave the same way; the Phi P2 gate has not run.
- It does not justify repairing the output, changing the prompt, or adding retries.
- It does not establish that the benchmark harness is defective.
- It does not permit a final package choice without the remaining model results.

## 11. Why execution stopped

Gate 4 says that each model/package pair must pass a four-task fictional strict-schema transport
gate with 4/4 valid outputs before its 40 private development positions are generated. Phi P1 did
not meet that prerequisite.

The failure policy prohibits retrying schema failures to improve metrics and prohibits changing
the prompt, schema, timeout, token limit, context, concurrency, runtime, artifact, model, or
provider to rescue a failed case. The one unchanged reproduction was preserved as diagnostic
evidence; continuing to rerun until 4/4 would bias the gate and violate the experiment.

The correct executor action was therefore to stop before private Phi data was used and request a
manager interpretation. No safety stop is being presented as completion.

## 12. Decision options and tradeoffs

| Option | Action | Advantages | Costs and risks | Assessment |
| --- | --- | --- | --- | --- |
| A. Narrow Phi P1 exception | Treat the two 3/4 gates as model evidence and run one unchanged 40-position Phi P1 package; retain the original 4/4 requirement for Phi P2 | Preserves failure evidence; measures real development behavior; keeps model, prompt, schema, and retry boundaries fixed; enables the core cross-model comparison | Explicit protocol deviation must be disclosed; private generation proceeds despite a failed screening gate | **Recommended** |
| B. Strict stop | Do not make further B3B calls; report the study as incomplete | Perfectly literal application of the 4/4 gate; no further time or cloud cost | Cannot complete Qwen+Phi ranking, Gemini portability, judge scoring, P3 decision, package selection, or B3C freeze | Defensible, but forfeits the main research question |
| C. Run only the Phi P2 fictional gate first | Use four fictional calls to learn whether P2 passes before deciding P1 | Adds limited diagnostic information without private disclosure | Does not resolve whether Phi P1 may run; departs from the fixed P1-then-P2 sequence; likely creates a second decision point | Optional, not recommended as the primary resolution |
| D. Rescue or redesign | Change P1, schema, runtime, context, timeout, retries, model, or output handling | Might produce a passing gate | Violates frozen variables and failure policy; biases results; would require a new experiment | Reject |
| E. Skip Phi P1 and continue elsewhere | Run only Phi P2 and/or Gemini | Saves the failed arm | Produces an incomplete package/model matrix and prevents the declared selection rule from being applied fairly | Reject |

Option A is the smallest change that allows the original scientific question to be answered. It
does not reinterpret the failed output as valid; it changes only whether the fictional gate is a
hard exclusion criterion for this one arm.

## 13. Recommended authorization text

The manager can use the following text verbatim:

> Manager authorizes one bounded protocol exception for WP-5.2B3B. Treat the two preserved Phi P1
> 3/4 fictional gates, with repeated title-assessment application-schema failure under unchanged
> accepted settings, as experimental model evidence rather than a transport blocker. Proceed with
> exactly one 40-position Phi P1 development run using the frozen P1 package, accepted Phi
> artifact, context 8,192, parallelism one, and unchanged timeout, token, retry, schema, and runtime
> settings. Preserve every terminal failure and make no rescue retry. Phi P2 remains subject to
> its original 4/4 fictional-gate requirement. Stop for review if Phi P2 fails its gate or if any
> other invariant changes.

Recommended companion identity authorization:

> Perform the remaining candidate and judge work from a clean dedicated checkout pinned to
> `f25505ae3762fae337d3ed0b7a364689f0cc8853`, preserving the existing private provenance amendment
> and Qwen packages unchanged. Do not mix a later documentation-only branch HEAD into new package
> application identities.

If the manager does not accept the exception, the correct disposition is “B3B stopped incomplete
after Qwen P1/P2; no selected global package,” not “B3B completed.”

## 14. Continuation plan after approval

If Option A and the identity approach are approved, continue in this exact order:

1. Establish a clean execution checkout at the accepted `f25505a` application identity.
2. Revalidate the append-only provenance amendment, frozen 10/20 manifests, P1/P2 prompt hashes,
   model artifacts, and zero holdout access.
3. Record the manager exception beside the private run provenance before loading private Phi data.
4. Generate exactly one Phi P1 40-position development package with unchanged settings.
5. Verify and deterministically score Phi P1.
6. Run the normal fictional Phi P2 gate once and require 4/4. Stop if it fails.
7. If it passes, generate, verify, and deterministically score the 40 Phi P2 positions.
8. Run Gemini 3.5 Flash P1 and P2, in order, for 80 hosted candidate positions total using the
   existing approved Vertex `global` scope.
9. Verify and deterministically score every Gemini package locally.
10. Run the four-task synthetic fixed-judge gate and require 4/4.
11. Judge every eligible P1/P2 result across Qwen, Phi, and Gemini with the fixed Gemini Pro judge.
12. Run identical cache-only replays and prove zero new provider calls with byte-stable evidence.
13. Evaluate the P3 trigger using aggregate P1/P2 local evidence. Create no P3 unless all six
    predeclared conditions are met.
14. Apply the frozen package-selection rule and guardrails without post-hoc changes.
15. Freeze the complete selected four-task package, or explicitly report that no non-P0 package is
    eligible and select P0 if the rule requires it.
16. Produce the completion report and article-ready methodology/evidence brief, leaving all
    changes unstaged and uncommitted for manager validation.

## 15. Remaining call scope and authorization boundary

Before optional P3, the remaining candidate scope is:

| Work | Maximum remaining positions | Disclosure |
| --- | ---: | --- |
| Phi P1 | 40 | Local private development inputs; requires the manager exception |
| Phi P2 | 40 | Local private development inputs; only after a 4/4 fictional gate |
| Gemini P1/P2 | 80 | Approved private development inputs and task schemas to Vertex AI `global` |
| Fixed judge | Every eligible P1/P2 result; original ceiling 240 across all three models | Approved source input, candidate, FABLE reference, schema, and rubric to fixed Gemini Pro judge |
| Synthetic judge gate | 4 | Fictional only |

Qwen already contributes 52 eligible P1/P2 outputs. Therefore, even if every remaining candidate
is eligible, the practical pre-P3 judge maximum is 212 results, inside the approved 240 ceiling.
Accepted P0 judge evidence is reused and is not called again.

If and only if P3 triggers, the existing authorization allows 120 additional candidate positions
across Qwen, Phi, and Gemini, with judging inside the approved 360-position total ceiling. No P4
or second revision is allowed.

New authorization is required if the provider, model, Vertex region, authentication route,
development scope, disclosed fields, rubric, retries, call ceiling, prompt-package count, or
material expected cost changes.

## 16. P3 trigger and package-selection constraints

P3 may be authored only after both P1 and P2 complete on Qwen and Phi and only when:

1. the same task and normalized failure category occurs in both local models;
2. at least four development cases across the two local models show that pattern;
3. model-neutral prompt wording could plausibly address it;
4. no schema, selector, finalizer, context, generation setting, or application behavior changes;
5. the trigger evidence is recorded before P3 is written; and
6. only one bounded global revision is made.

Current evidence cannot trigger P3 because Phi P1/P2 development results do not exist.

For each complete package, selection ranks:

1. pooled Qwen+Phi usable cases out of 80;
2. the lower local-model usable count;
3. the minimum pooled task usable count;
4. pooled whole-case macro UTS;
5. lower prompt overhead;
6. simpler/earlier package, with P0 winning an exact tie.

Deterministic agreement, confusion matrices, fixed-judge dimensions, and UTS are interpretive
tie-break evidence after reliability. Gemini is a portability guardrail, not the optimization
target. No task-specific or model-specific winner may be assembled.

The current Qwen result warns that both P1 and P2 may fail the local regression guardrails because
each has 26 usable cases versus P0's 30. That risk is important but does not permit an early final
selection: the declared guardrails also depend on pooled local, per-task, and Gemini results.

## 17. Known facts, unknowns, and decision consequences

### Known

- The split is frozen, quota-correct, disjoint, and privacy-preserving.
- P1/P2 are frozen and structurally prompt-only variants of P0.
- Qwen P1 and P2 both pass their fictional gates and produce 26/40 usable development outputs.
- P2 is faster at the median and has better deterministic agreement on two labels, but not better
  Qwen reliability.
- Phi P1 repeats the same fictional title-schema failure, 3/4 twice.
- No Phi private input, Gemini private input, or fixed-judge request has been sent.
- No holdout content or outcome has been opened.

### Unknown until continuation

- Phi P1 development reliability and whether the fictional title failure generalizes.
- Whether Phi P2 passes its fictional gate.
- Phi P2 and Gemini P1/P2 development results.
- Fixed-judge dimensions and whole-case UTS for the new packages.
- Whether the aggregate P3 trigger is met.
- Whether P0, P1, P2, or conditional P3 wins the frozen selection rule.
- Whether a selected global package can be frozen for B3C.

### Consequence of approving Option A

The study continues with one transparent deviation and retains a chance to complete the planned
cross-model comparison. The exception must appear in the final methodology and limitations.

### Consequence of choosing Option B

B3B closes as a valid partial experiment with no selected package and is not ready for B3C. The
existing Qwen and fictional-gate evidence remains useful, but it cannot support the intended
global portability conclusion.

## 18. Mandatory stop conditions during continuation

Stop and return to the manager if:

- Phi P2 does not pass its unchanged 4/4 fictional gate;
- an accepted artifact, runtime, prompt, split, schema, or application identity cannot be
  reproduced;
- any holdout case is loaded or disclosed;
- a completed position would need to be repeated to improve a metric;
- private data, credentials, or private identities would enter Git;
- package verification or cache-only replay fails;
- the provider, model, region, rubric, scope, retry ceiling, or cost boundary changes;
- P3 would require model-specific wording or a schema/application change;
- destructive cleanup or unbounded retry would be required.

## 19. Recommended manager decision record

Record all of the following explicitly:

- [ ] Approve Option A, the bounded Phi P1 exception; **or**
- [ ] Choose Option B and close B3B incomplete.
- [ ] Approve execution from a clean checkout pinned to `f25505a`.
- [ ] Confirm Phi P2 retains the original 4/4 gate.
- [ ] Confirm no prompt, schema, runtime, model, context, timeout, token, retry, provider, region,
      scope, or holdout change is authorized.
- [ ] Confirm the existing Gemini candidate and fixed-judge disclosure authorization remains in
      force without expansion.

## 20. Bottom line

The project is at a controlled experimental stop, with no evidence loss and no privacy breach.
The implementation and frozen design are intact. Qwen results are complete but do not yet show a
reliability improvement over P0. Phi exposed a repeatable P1/title structured-output weakness at
the fictional gate.

The recommended path is to treat that weakness as data, authorize one unchanged Phi P1
development run, retain the strict gate for Phi P2, and continue from the exact accepted
application commit. If the manager prefers literal gate enforcement over completing the research
question, B3B should be closed explicitly as incomplete and must not advance to the holdout.
