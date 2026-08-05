# WP-5.2B3B Global Prompt Development Completion Report

## 1. Status

**Ready for PM validation.** The development experiment is complete, P0 is selected and frozen,
and the twenty-conversation holdout remains unopened. The executor made no commit and staged
nothing.

## 2. Executive summary

The schema-first P1 and bounded-few-shot P2 packages did not improve global structured-output
reliability. On the two optimization models, P0 produced 62/80 usable outputs while P1 and P2 each
produced 58/80. Both variants lost four Qwen cases and neither gained a Phi case. Gemini portability
also regressed: P1 fell from 38/40 to 32/40, while P2 reached 36/40 but lost two title outputs.
These are explicit guardrail failures, so semantic tie-breaks cannot rescue either variant.

The predeclared rule therefore selects the unchanged complete P0 four-task package. A byte-identical
privacy-safe copy is delivered at `bench/prompts/wp-5.2b3b/selected-p0.yaml`; production defaults
remain unchanged. P3 was not created because the only repeated cross-model pattern was the same
fixed-context failure already present at P0 and it was not plausibly repairable by model-neutral
prompt wording.

## 3. Repository and execution identity

| Item | Identity |
|---|---|
| Branch owned by manager | `codex/wp-5.2b3b-prompt-development` |
| Starting commit | `25877b01e375e191a95e14f29f254f1523f0df77` |
| Gate 1 commit | `b15bf9632a344c0cac3b42a68142a6829c973b47` |
| Prompt-catalog implementation | `0e920c8` |
| Accepted clean application identity | `f25505ae3762fae337d3ed0b7a364689f0cc8853` |
| Continuation checkout | dedicated detached clean checkout pinned to `f25505a` |

The active branch checkout was not used for continuation writes. All new candidate, judge, freeze,
and report work occurred in the dedicated checkout. The active checkout's pre-existing report edits
were not modified.

## 4. Scope and exclusions

In scope were the frozen ten-conversation development subset, four task cases per conversation,
P0/P1/P2, Qwen3.5-4B, Phi-4 Mini, Gemini 3.5 Flash, deterministic scoring, the fixed Gemini Pro
judge, the bounded P3 decision, and one complete package selection. Excluded were holdout content,
production promotion, model-specific prompts, schema or selector changes, output repair, rescue
retries, P4, WP-5.2C1, and any article publication.

## 5. Gate 1 implementation and compatibility

Gate 1 added strict ordered-manifest support across preparation, generation, verification,
deterministic scoring, and judge accounting while preserving historical full-corpus and prefix
behavior. Independent manager validation passed eight focused tests, 455 full-suite tests with one
skip, Ruff, Poetry, CLI, and privacy checks before commit `b15bf96`.

The later narrow prompt-catalog patch separated immutable task-catalog authority from the active
prompts-only experiment catalog. It bound both identities through every benchmark stage while
enforcing structural identity of all non-prompt fields. Manager validation passed 20 focused tests,
474 full-suite tests with one skip, Ruff, Poetry, CLI, historical compatibility, and prompt-only
end-to-end checks before commits `0e920c8` and `f25505a`.

## 6. Frozen sources and P0 verification

The frozen/live database identities, source selection, accepted inputs, references, and accepted
P0 candidate/judge evidence were captured and verified before prompt calls. P0 was reconstructed
as a 40-case development projection without generation or judging. Counts were Qwen 30 valid,
Phi 32 valid, and Gemini 38 valid. No accepted source artifact was rewritten.

## 7. Metadata-only split

The versioned split was selected from accepted metadata only. Development has 10 conversations and
40 task cases with provider quotas 3 ChatGPT, 3 OpenAI Codex, 2 Claude, and 2 Claude Code, and length
quotas 4 short, 3 medium, and 3 long. Holdout has 20 conversations and 80 task cases with provider
quotas 7/7/3/3. The two manifests are disjoint and cover all 30 accepted authority positions.

## 8. Holdout non-access proof

Holdout manifest identity and aggregate quotas were verified, but raw holdout inputs, references,
titles, URLs, per-case identities, candidates, scores, and judge outcomes were never opened. Holdout
generation calls, deterministic scores, and judge calls are all zero. Hard links in the dedicated
checkout made accepted files path-contained for the harness; only selected development files were
loaded. The 20 holdout conversations remain reserved for WP-5.2B3C.

## 9. P0 reconstruction and reuse

The accepted Qwen, Phi, and Gemini 120-case packages were projected to the frozen development
manifest. Candidate and judge attempt evidence was checksum-verified and the projection accounted
for exactly 40 cases per model. There were no P0 provider calls. The P0 development reliability was:

| Model | Valid/40 | Summary / work / last / title | Failures |
|---|---:|---|---|
| Qwen | 30 | 6/7/10/7 | context 6, schema 1, timeout 3 |
| Phi | 32 | 7/8/10/7 | context 6, schema 2 |
| Gemini | 38 | 8/10/10/10 | invalid JSON 1, schema 1 |

## 10. P1 hypothesis and frozen identity

P1 placed the response contract first, demanded one schema-matching JSON object, named exact enums,
made cross-field rules explicit, constrained evidence IDs, and removed date generation from the
summary task. It was frozen before calls and used unchanged across all three models. Its aggregate
prompt identity is `cebb28d8e8a0b38ddf22becf50cb88993ffdd94db5ee4fe79616062c28a9dddd`;
the file identity is `2f9f403232684fb67e44bb50df44d340c4494d8479600b98707d842065c6cc16`.
The package contains 4,202 characters and an estimated 870 `cl100k_base` tokens, 212 more than P0.

## 11. P2 hypothesis and frozen identity

P2 retained P1 and added bounded fictional examples for valid and edge-case output shapes. Examples
were synthetic, dated 2032, and contained no private data. P2 was frozen before calls and used
unchanged across all models. Its aggregate identity is
`132d6524dd5244e089bd157d639bd73b70ab97e4c72dc1cdee50bb1ac407c953`;
the file identity is `1d549e26b97bd015b6f36f328bde09511db3db0d2afbd7e36f41aa92f026c432`.
It contains 6,849 characters and an estimated 1,516 tokens, 858 more than P0.

## 12. Qwen P1/P2 accounting

Both fictional gates passed 4/4. Each package has exactly 40 terminal positions and one attempt per
position. P1 and P2 each produced 26 valid and 14 failed outputs: six context-length failures and
eight timeouts. P1's wrapper reached its orchestration timeout after 36 positions, but the original
generator completed the remaining four; no position was called twice. No failed output was retried,
repaired, or truncated.

## 13. Phi P1/P2 accounting

The required P1 fictional gate and one unchanged diagnostic reproduction each produced 3/4, with
the same title schema failure. The manager-approved Option A exception treated that repeatable
result as experimental evidence and authorized exactly one unchanged private 40-position run from
the clean `f25505a` checkout. That run produced 32 valid and eight failed outputs (six context,
two schema) with 40 attempts and zero rescue retries.

Phi P2 retained the original prerequisite: its fictional gate passed 4/4 before private generation.
Its one 40-position run also produced 32 valid and eight failed outputs (six context, two schema),
again with no rescue retry.

## 14. Gemini P1/P2 accounting

Both packages used the authorized global `vertex_ai/gemini-3.5-flash` route. P1 produced 32 valid,
seven invalid-JSON failures, and one provider-response failure. P2 produced 36 valid and four
invalid-JSON failures. Each arm had exactly 40 calls, no candidate retries, unchanged context and
generation settings, and a verified terminal package.

## 15. Package verification and deterministic scoring

All six packages verified with 40 accounted cases. Deterministic scoring completed for every
package and preserved invalid outputs in denominators. Exact agreement is shown below; full
confusion matrices, per-label precision/recall/support, and summary contract counts are in the
evidence brief.

| Package/model | Work | Last | Title |
|---|---:|---:|---:|
| P0 Qwen / Phi / Gemini | 60% / 10% / 70% | 70% / 70% / 70% | 70% / 20% / 100% |
| P1 Qwen / Phi / Gemini | 20% / 50% / 60% | 60% / 40% / 70% | 50% / 20% / 90% |
| P2 Qwen / Phi / Gemini | 30% / 40% / 60% | 60% / 50% / 80% | 60% / 20% / 80% |

## 16. Authorization and call accounting

Existing owner authorization covered the private Gemini candidate fields and fixed-judge
disclosures. Provider, model, global region, data scope, case count, retry boundary, and cost scope
did not change. The completed hosted call count is 268: 80 Gemini candidate calls, 184 development
judge calls, and four fictional judge-gate calls. Local fictional calls were Qwen 8, Phi P1 8, and
Phi P2 4. No P3 or holdout call occurred.

## 17. Fixed judge and cache-only replay

The fixed judge was global `vertex_ai/gemini-3.1-pro-preview`, rubric v1, temperature 0,
`max_tokens: 1000`, reasoning none, concurrency one, and one bounded provider-failure retry. The
fictional gate passed 4/4. Across the six new packages, 184 outputs were eligible; 182 completed and
two Qwen cases ended as preserved `provider_invalid_json` judge failures. Fifty-six invalid
candidate positions were skipped. Six cache-only replays found zero cache misses, made zero provider
calls, and left all 184 judge attempt files byte-stable.

## 18. P3 trigger decision

P3 was not created. Context-length failures appeared in at least four pooled local cases for
summary, work, and title under both P1 and P2, but the same six context failures already existed in
each local P0 baseline. A reliable correction would require input selection, context, or application
changes, not a model-neutral prompt-only revision. Qwen timeouts and Phi schema failures were not a
shared category. Therefore every trigger condition was not met.

## 19. P3 results

Not applicable: zero prompt files, zero candidate calls, and zero judge calls.

## 20. Reliability and failure taxonomy

| Package | Qwen valid | Phi valid | Gemini valid | Pooled local/80 |
|---|---:|---:|---:|---:|
| P0 | 30 | 32 | 38 | 62 |
| P1 | 26 | 32 | 32 | 58 |
| P2 | 26 | 32 | 36 | 58 |

No candidate position is unaccounted. P1/P2 failures were: Qwen context 12 and timeout 16; Phi
context 12 and schema 4; Gemini invalid JSON 11 and provider response 1. First attempt equals current
attempt for all 240 new candidate positions. There were no metric-improving resumes or retries.

## 21. Deterministic semantic metrics

P1 improved Phi work-mode exact agreement from 10% to 50% but reduced Qwen work from 60% to 20%.
P2 Qwen title agreement reached 60%, below P0's 70%, while Gemini title fell from 100% to 80%.
The strongest stable task was last activity by validity (P0 20/20 local; P2 18/20), though label
agreement and judge dimensions show status/next-action weakness on Phi. Full matrices and label
statistics prevent these aggregate rates from hiding class imbalance.

## 22. Judge metrics and UTS

UTS v1 gives invalid, absent, or judge-failed cases zero, averages normalized `(score - 1) / 3`
within each task over all ten expected cases, macro-averages four tasks, and multiplies by 100.
Valid-output quality averages only successfully judged valid survivors and is always paired with
reliability.

| Package/model | Completed/eligible | Macro UTS | Valid-output quality |
|---|---:|---:|---:|
| P0 Qwen / Phi / Gemini | 30/30; 32/32; 37/38 | 69.4 / 56.6 / 89.5 | 0.934 / 0.713 / 0.968 |
| P1 Qwen / Phi / Gemini | 25/26; 32/32; 32/32 | 51.5 / 63.5 / 78.6 | 0.822 / 0.795 / 0.982 |
| P2 Qwen / Phi / Gemini | 25/26; 32/32; 36/36 | 54.2 / 58.7 / 87.3 | 0.870 / 0.746 / 0.971 |

The survivor-quality gains in some arms do not overcome reliability losses. Full task UTS and all
judge dimension means with denominators are in the evidence brief.

## 23. Prompt, latency, wall-time, resource, token, and cost evidence

| Package/model | Candidate p50/p95 | Wall span | Reported total tokens; usage availability |
|---|---:|---:|---:|
| P1 Qwen | 102.812/180.188s | 68.42m | 64,947; 26/40 |
| P2 Qwen | 73.406/180.108s | 61.26m | 68,629; 26/40 |
| P1 Phi | 51.344/149.765s | 43.09m | 100,576; 34/40 |
| P2 Phi | 55.000/156.297s | 45.25m | 106,205; 34/40 |
| P1 Gemini | 2.467/8.436s | 2.22m | 204,062; 39/40 |
| P2 Gemini | 2.186/7.265s | 2.04m | 215,652; 40/40 |

The accepted local execution identity used LM Studio, Windows, the accepted Q4_K_M GGUF bytes,
8,192 context, parallelism one, and the accepted device policy; model setup/load was performed and
verified separately from run wall time. No comparable hardware claim is made between local and
hosted latency.

Hosted candidate usage was 407,192 prompt and 12,522 completion tokens. Development judging
reported 806,078 prompt and 56,371 completion tokens for 182/184 calls; the two terminal failures
had no usage. The judge gate added 3,709 prompt and 1,467 completion tokens. Using
[current Google global list rates](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)
of $2.70/$16.20 per million Gemini 3.5 Flash input/output tokens and $3.60/$21.60 per million
Gemini 3.1 Pro input/output tokens, estimated hosted cost is $5.47 ($1.30 candidate, $4.12
development judge, $0.05 judge gate). This is an estimate, not a billing export.

## 24. Task difficulty

- **Conversation summary:** reliability moved from 13/20 local at P0 to 14/20 for both variants,
  but this one-case gain was not shared across the full package and context remained dominant.
- **Work mode:** fell from 15/20 at P0 to 13/20; Phi deterministic agreement improved under P1,
  but Qwen and Gemini reliability regressed. This is the clearest semantic/schema tradeoff.
- **Last activity:** highest local reliability at P0 (20/20), then 17/20 P1 and 18/20 P2. Phi P2
  survivor scores exposed weak blocker, next-action, and status judgment despite 10/10 validity.
- **Title assessment:** P0 had 14/20 local and 10/10 Gemini; P2 fell to 13/20 local and 8/10 Gemini.
  Few-shot examples did not generalize reliably.

Confidence is moderate for this frozen development set and low for generalization beyond it. Ten
conversations cannot establish population-level superiority.

## 25. Exact package-selection calculation

| Package | Pooled local usable/80 | Lower local model/40 | Summary/work/last/title pooled | Minimum task/20 | Pooled local macro UTS | Result |
|---|---:|---:|---|---:|---:|---|
| P0 | 62 | 30 | 13/15/20/14 | 13 | 63.0 | selected |
| P1 | 58 | 26 | 14/13/17/14 | 13 | 57.5 | ineligible |
| P2 | 58 | 26 | 14/13/18/13 | 13 | 56.4 | ineligible |

The lexicographic rule stops at the first criterion because P0 has the highest pooled usable count.
Guardrails independently reject P1: Qwen -4, pooled local -4, Gemini -6 overall and -3 work. They
reject P2: Qwen -4, pooled local -4, and Gemini title -2. No tie-break or prompt-overhead criterion
is needed.

## 26. Selected package freeze and rejected variants

Selected package: **P0**, all four tasks as one unit. The private manifest binds prompt texts and
hashes, all trial identities, selection arithmetic, schemas/selectors/finalizers, models, runtime,
judge, both split identities, context, commit, timestamp, and holdout attestation. The tracked
package copy is byte-identical to `ai-tasks.default.yaml`; its SHA-256 is
`bd332905a78e74fd26251d85cb9acc417af940279e022c4dd725bb4f1a0cd1c5`.

P1 and P2 are rejected for reliability/portability guardrails, not deleted. P3 is absent because
its trigger was false. Production `ai-tasks.default.yaml` was not edited.

## 27. WP-5.2B3C readiness

B3B evidence is ready for manager validation. B3C must not start until the manager validates and
commits this selection/report delivery. After that checkpoint, B3C may perform the one-shot
20-conversation holdout using this exact selected P0 package and no prompt edits.

## 28. Article-ready methodology brief

Delivered at `md/handoffs/reports/WP-5.2B3B-prompt-development-evidence-brief.md`. It contains
chart-ready tables, full confusion matrices, judge dimensions and denominators, supported
observations, limitations, figure proposals, and a future B3C placeholder. It does not claim holdout
generalization or contain final article copy.

## 29. Privacy and external disclosure

No tracked report contains private IDs, titles, URLs, prompts built from private content, raw input,
candidate output, reference rationale, credentials, cloud-project identity, machine-user identity,
or private evidence hashes. Hosted candidate disclosure was limited to the authorized development
inputs and task fields; judge disclosure was limited to the authorized input, candidate, reference,
schema, and rubric fields. Holdout disclosure was zero.

## 30. Database immutability

Live and frozen database identities remained unchanged. The fictional Phi gates used isolated
synthetic state and a fictional database. No accepted DB was written.

## 31. Historical and WP-5.2C1 immutability

Accepted P0 packages, frozen inputs/references, existing P1/P2 Qwen packages, and WP-5.2C1
artifacts were preserved unchanged. The report-only WP-5.2C1 text pasted during execution was
treated as unrelated and no C1 work was performed.

## 32. Validation

Final validation passed:

- Poetry environment: dedicated checkout `.venv`, junctioned to the existing repository `.venv`;
- focused ordered-manifest/prompt-catalog matrix: 26 passed;
- isolated packaging environment test: passed;
- full repository suite: 474 passed, 1 skipped in 110.42 seconds;
- repository-wide Ruff: passed;
- `poetry check`: passed;
- benchmark root, prepare, generate, verify, and score help: passed;
- Chronicle root help and AI-task listing: passed;
- `git diff --check`: passed;
- private tracking query: zero tracked `.chronicle`, DB, SQLite, ZIP, or export artifacts;
- final private reconciliation: six packages, 240 terminal candidates, 182 completed judges,
  two terminal judge failures, zero cache provider calls, no P3, no holdout access, active checkout
  unchanged, and zero staged files.

The first full-suite attempt used a temporary external `VIRTUAL_ENV` override and correctly failed
only the checkout-local environment identity assertion (473 passed, 1 failed, 1 skipped). The
validation-only `.venv` junction corrected the checkout identity; the isolated failing test and the
complete suite then passed. The first AI-task listing likewise required ignored checkout-local
copies of the default task/model catalogs; after adding them, the command passed. Neither setup
correction changed source, prompts, packages, or experiment evidence.

## 33. Known limitations and unresolved questions

- The development corpus has only ten conversations and was quota-balanced, not randomly sampled.
- FABLE references and a fixed preview judge are evaluation instruments, not ground truth.
- P0 judge evidence is historical while P1/P2 judging occurred in the current preview-model window.
- Provider token reporting is missing for failed/locally rejected calls; cost is list-price estimate.
- The Phi P1 gate exception was deliberate manager policy and weakens comparability of gate pass
  status, though the private run itself was unchanged and terminal.
- Holdout performance is intentionally unknown. The final deployment decision remains unresolved
  until WP-5.2B3C.

## 34. Acceptance checklist

- [x] Dedicated accepted application identity and frozen variables used.
- [x] 10/20 split quotas and disjointness verified from metadata.
- [x] P0 reconstructed without calls; P1/P2 frozen before calls.
- [x] Six packages have 40 terminal positions, verify, and score deterministically.
- [x] Every eligible result completed judging or has an explicit terminal judge failure.
- [x] Cache-only replay made zero provider calls.
- [x] P3 was absent under the predefined trigger.
- [x] One complete global package was selected and privately frozen.
- [x] Holdout content/outcomes remained unopened.
- [x] Production defaults, accepted evidence, DBs, and WP-5.2C1 remained unchanged.
- [x] Completion report and methodology brief delivered.
- [ ] Manager validation and commit (manager-owned next step).

## 35. Delivery files

Tracked delivery files in the dedicated checkout:

- `bench/prompts/wp-5.2b3b/selected-p0.yaml` (new, byte-identical P0 selection copy);
- `md/handoffs/reports/WP-5.2B3B-completion-report.md` (new);
- `md/handoffs/reports/WP-5.2B3B-prompt-development-evidence-brief.md` (new);
- `md/handoffs/reports/WP-5.2B3B-manager-decision-report.md` (new decision record retained);
- `md/handoffs/reports/WP-5.2B3B-execution-progress.md` (updated).

Ignored private delivery includes frozen split/provenance, prompt freeze/amendment, all six package
and scoring trees, synthetic gates, manager exception, judge/cache evidence, aggregate analysis,
P3 decision, and selected-package manifest/checksums. These remain untracked under `.chronicle/`.

## 36. Final Git state and commit ownership

Final `git status --short` in the dedicated checkout:

```text
 M md/handoffs/reports/WP-5.2B3B-execution-progress.md
?? bench/prompts/wp-5.2b3b/selected-p0.yaml
?? md/handoffs/reports/WP-5.2B3B-completion-report.md
?? md/handoffs/reports/WP-5.2B3B-manager-decision-report.md
?? md/handoffs/reports/WP-5.2B3B-prompt-development-evidence-brief.md
```

Nothing is staged or committed. The manager owns validation, staging, commit, and authorization to
begin WP-5.2B3C.
