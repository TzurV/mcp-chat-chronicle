# WP-5.2B3B.1D.4.2 Four-Proposal Hosted GEPA Search Completion Report

Date: 2026-08-18

## Executive outcome

WP-5.2B3B.1D.4.2 completed the authorized fresh experiment: one P0 evaluation
and exactly four logical GEPA proposal positions. The outcome is negative under
the frozen promotion contract. Positions 1, 2, and 4 were rejected by the
strict minibatch rule. Position 3 was accepted by GEPA and produced one
distinct, privacy-clean candidate, but that candidate failed deterministic
finalist qualification. P0 is retained as the development comparator only.

The candidate completed 40/40 terminal positions, including the same seven
deterministic 8K context no-calls as P0, and had the same 16/40 valid-output
count. Unchanged total, per-model, and per-task validity pass the actual frozen
eligibility comparisons; neither improvement over 16/40 nor universal output
validity is required by `operations.py`. Validation FABLE agreement fell from
P0's 0.128125 to 0.112500, which is relevant to ranking but is not an
eligibility conjunct. The decisive failure was `prompt_fits_context = false`:
the maximum complete request was 15,381 tokens against the frozen 8,192-token
limit. The candidate therefore did not become a finalist. The fixed judge was
not resolved, constructed, or called; judge calls and cost are zero. Holdout
access is zero.

The fresh root used 142 observed and conservatively charged calls: 66 ordinary
candidate transports, 72 GEPA adapter transports, and four proposer calls.
There were zero infrastructure retries. Cumulative charged calls are 647/950.
Fresh partial known provider cost is US$0.1454048; GEPA adapter-transport cost is
not available. The completed root reconciled US$0.1452040383 of budget-ledger
compute plus proposer cost, bringing cumulative budget-side accounting to
US$7.7819816672/US$35.

## Branch, commits, environment, and frozen authority

- Branch: `codex/wp-5.2b3b-d4.2-gepa-search`.
- Original authorized source: `5c9f9dbfb23c9272ae30e1fdaee3d0389397cc28`.
- Durable proposer-lifecycle checkpoint: `7d3af247e5b85bdcc252614c6a715a7b9ac72bbf`.
- Aligned metric/reservation checkpoint and run-bound application commit:
  `96154c683a3d8b3cc0534a0e7d888cdb9bad4595`.
- Environment: Windows, repository Poetry environment, Python 3.12.0, Poetry
  2.3.4, DSPy 3.3.0, and GEPA 0.1.1.
- Candidate: `vertex_ai/gemini-2.5-flash-lite`, Google Vertex AI, `global`,
  reasoning disabled, temperature 0, one infrastructure retry, zero semantic
  retries, and an 8,192-token complete-request contract.
- Proposer: `vertex_ai/gemini-3.5-flash`, Google Vertex AI, `global`,
  temperature 0, no requested reasoning effort, one infrastructure retry,
  zero semantic retries, no output repair, and no cache.
- Optimizer: instruction-only, merge disabled, four proposal positions,
  `gepa-reliability-v1`, and the unchanged strict `new_sum > old_sum` rule.
- Authority: exactly ten selected development conversations, 40 FABLE
  references, four tasks, a six-conversation/24-case train split, a
  four-conversation/16-case validation split, and zero holdout paths or files.

The accepted task catalog, P0 prompt identities, selectors, schemas,
references, split, context policy, model routes, generation settings, graded
search metric, and strict promotion rule did not change. ADC capability,
resource/quota-project agreement, and `global` routing were checked in the
same process as execution without retaining credential, account, token,
project, or ADC-path values. Exact successful route qualification was reused,
so synthetic qualification added zero calls.

## Engineering and repair history

Checkpoint `7d3af24` added a private append-only proposer lifecycle independent
of DSPy's final candidate store. It records pre-call intent, canonical request
identity, selected component and source-free example identities, configured and
actual route metadata, transport and response availability, raw response,
generated instruction before decision, usage, latency, and terminal linkage.
Provider-free regressions cover all required interruption boundaries, exact
resume, decision recovery, rejected-proposal retention, empty-output
terminalization, redacted logs, and Windows sharing-violation recovery.

One of the three authorized generic repair cycles was consumed. The first
private D.4.2 diagnostic root completed P0 and one rejected proposal, then
revealed that GEPA's 20-position runtime stop did not match the accepted
104-position reservation for four complete proposal lifecycles. Checkpoint
`96154c6` derives the runtime ceiling from the same reservation formula. It did
not change prompts, models, references, selectors, context, search scoring, or
promotion semantics. The diagnostic root remains immutable and its proposal
is not counted among the four fresh positions. No further repair cycle was
needed; two remain unused.

## Fresh P0 evidence

P0 completed 40/40 terminals: 33 provider transports, seven deterministic
context-boundary no-calls, 16 valid outputs, 17 transported schema failures,
and zero retries. Per-task figures include every position in the denominator.
Agreement is the deterministic FABLE-derived semantic-agreement value.

| Scope / task | Valid / cases | Calls | Context / schema failures | Mean agreement | Input / output tokens | Latency ms | Cost US$ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Train — conversation summary | 0 / 6 | 5 | 1 / 5 | 0.000000 | 19,977 / 939 | 12,233 | 0.0023733 |
| Train — work-mode classification | 5 / 6 | 5 | 1 / 0 | 0.166667 | 20,102 / 654 | 4,376 | 0.0022718 |
| Train — last activity | 0 / 6 | 5 | 1 / 5 | 0.000000 | 15,321 / 892 | 5,532 | 0.0018889 |
| Train — title assessment | 5 / 6 | 5 | 1 / 0 | 0.266667 | 20,155 / 621 | 4,797 | 0.0022639 |
| **Train total** | **10 / 24** | **20** | **4 / 10** | **0.108333** | **75,555 / 3,106** | **26,938** | **0.0087979** |
| Validation — conversation summary | 0 / 4 | 3 | 1 / 3 | 0.000000 | 7,581 / 570 | 3,328 | 0.0009861 |
| Validation — work-mode classification | 3 / 4 | 3 | 1 / 0 | 0.312500 | 7,656 / 340 | 2,437 | 0.0009016 |
| Validation — last activity | 0 / 4 | 4 | 0 / 4 | 0.000000 | 7,146 / 846 | 4,781 | 0.0010530 |
| Validation — title assessment | 3 / 4 | 3 | 1 / 0 | 0.200000 | 7,686 / 374 | 2,485 | 0.0009182 |
| **Validation total** | **6 / 16** | **13** | **3 / 7** | **0.128125** | **30,069 / 2,130** | **13,031** | **0.0038589** |

Total P0 usage was 105,624 input and 5,236 output tokens, zero reasoning
tokens, 39,969 ms candidate latency, and US$0.0126568 measured provider cost.

| Task | P0 UTF-8 bytes | Estimated tokens |
| --- | ---: | ---: |
| Conversation summary | 569 | 143 |
| Work-mode classification | 745 | 187 |
| Last activity | 917 | 230 |
| Title assessment | 682 | 171 |

P0 is privacy-clean, but its maximum complete request is 15,256 tokens. It
fails the frozen context guard and is not promotion-eligible.

## Four fresh proposal positions

All four positions have intent, one proposer transport, response, generated
proposal envelope, privacy evidence, decision, and terminal records. All
generated instructions were distinct from their parent and had zero privacy
findings. No proposer fallback occurred. Provider retry count was unavailable
from the provider response, but each intent has exactly one recorded transport
and no retry was observed or charged.

| Position | Component | Parent -> proposal bytes | Parent -> proposal score sum | Decision | Candidate/result linkage |
| ---: | --- | ---: | ---: | --- | --- |
| 1 | Last activity | 916 -> 1,949 | 0.6 -> 0.6 | Rejected; strict equality is not improvement | Generated envelope and decision present; candidate/result correctly absent |
| 2 | Title assessment | 681 -> 1,255 | 0.5 -> 0.4 | Rejected; strict score decline | Generated envelope and decision present; candidate/result correctly absent |
| 3 | Conversation summary | 568 -> 1,013 | 0.5 -> 0.7 | Accepted by GEPA | Candidate identity present; later trial and run-state link the candidate result |
| 4 | Last activity | 916 -> 1,688 | 0.6 -> 0.4 | Rejected; strict score decline | Generated envelope and decision present; candidate/result correctly absent |

The position-3 lifecycle terminal has `result_identity_sha256 = null` because
it terminalized at GEPA acceptance before ordinary candidate evaluation. This
is an explicit linkage gap in that record, not missing result authority: the
completed proposal trial, run-state, candidate trial, and result all link the
same candidate and result afterward. Rejected positions correctly have no
candidate or result identity.

| Position | Proposer input | Visible output | Reasoning | Latency ms | Finish |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 9,326 | 1,507 | 1,021 | 9,110 | `stop` |
| 2 | 6,864 | 1,027 | 733 | 7,016 | `stop` |
| 3 | 13,642 | 1,262 | 927 | 8,203 | `stop` |
| 4 | 3,929 | 1,317 | 869 | 8,640 | `stop` |
| **Total** | **33,761** | **5,113** | **3,550** | **32,969** | **4 responses** |

The proposer ledger counts 8,663 output-or-reasoning tokens and calculates
US$0.1217919 at the frozen configured rates. GEPA scoring made 72 candidate
adapter transports over 45 logical score positions: 45 primary Chat transports
and 27 explicit JSON fallbacks, 224,327 input tokens, 12,240 output tokens, and
75,935 ms aggregate latency. All 72 ended in responses with retry ordinal zero.
Portable per-transport provider cost is unavailable. Adapter records retain
logical score position but not proposal ordinal, so a defensible per-proposal
transport/cost split is unavailable and is not reconstructed.

## Evaluated GEPA candidate

Only position 3 produced a candidate package. It changed conversation-summary
from 569 bytes / 143 estimated tokens to 1,013 bytes / 254 tokens; the other
three prompts remained byte-identical to P0. The candidate completed 40/40
terminals with 33 transports, seven context no-calls, 17 schema failures, and
zero retries.

| Scope / task | Valid / cases | Calls | Context / schema failures | Mean agreement | Input / output tokens | Latency ms | Cost US$ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Train — conversation summary | 0 / 6 | 5 | 1 / 5 | 0.000000 | 20,637 / 899 | 6,250 | 0.0024233 |
| Train — work-mode classification | 5 / 6 | 5 | 1 / 0 | 0.166667 | 20,102 / 661 | 4,718 | 0.00211665 |
| Train — last activity | 0 / 6 | 5 | 1 / 5 | 0.000000 | 15,321 / 892 | 5,248 | 0.00124783 |
| Train — title assessment | 5 / 6 | 5 | 1 / 0 | 0.266667 | 20,155 / 621 | 4,031 | 0.00141889 |
| **Train total** | **10 / 24** | **20** | **4 / 10** | **0.108333** | **76,215 / 3,073** | **20,247** | **0.00720667** |
| Validation — conversation summary | 0 / 4 | 3 | 1 / 3 | 0.000000 | 7,977 / 516 | 3,843 | 0.0010041 |
| Validation — work-mode classification | 3 / 4 | 3 | 1 / 0 | 0.250000 | 7,656 / 343 | 2,782 | 0.0009028 |
| Validation — last activity | 0 / 4 | 4 | 0 / 4 | 0.000000 | 7,146 / 876 | 4,532 | 0.00091713 |
| Validation — title assessment | 3 / 4 | 3 | 1 / 0 | 0.200000 | 7,686 / 392 | 2,859 | 0.0009254 |
| **Validation total** | **6 / 16** | **13** | **3 / 7** | **0.112500** | **30,465 / 2,127** | **14,016** | **0.00374943** |

Total candidate usage was 106,680 input and 5,200 output tokens, zero reasoning
tokens, 34,263 ms candidate latency, and US$0.0109561 measured provider cost.
The complete-request maximum increased to 15,381 tokens. Privacy findings were
zero.

### Mechanical finalist eligibility

The following table evaluates every conjunct in
`bench/optimization/operations.py::_eligible` against retained candidate and
P0 metadata. The function applies `all(...)`, so one failed conjunct makes the
candidate ineligible.

| Frozen condition | Retained comparison | Result |
| --- | --- | --- |
| GEPA lineage | Candidate package lineage optimizer is `gepa` | Pass |
| Validation total-valid | Candidate 6 >= P0 6 | Pass |
| Per-model validity | Candidate 6 >= P0 6 minus allowed tolerance 1 | Pass |
| Per-task validity | Candidate/P0: conversation summary 0/0, work-mode classification 3/3, last activity 0/0, title assessment 3/3; each candidate count is at least P0 minus 1 | Pass |
| Privacy eligibility | `eligible = true`, zero findings | Pass |
| Terminal accounting | 40 terminal invocations = 40 expected invocations | Pass |
| Prompt/context fit | `prompt_fits_context = false`; maximum 15,381 > 8,192 tokens | **Fail** |

Thus the candidate passes six of seven frozen eligibility conditions. Matching
P0 at 16/40 valid is a pass, not a reliability failure, and the lower
validation FABLE agreement is descriptive/ranking evidence rather than a
failed `_eligible` condition. Context fit alone is decisive. GEPA minibatch
acceptance is therefore search evidence, not promotion.

### Aggregate analysis of the seven 8K no-call envelopes

The frozen complete-request estimator was reapplied locally to retained private
candidate metadata without provider calls. Only aggregate statistics are
published here; case values, identities, text, and paths remain private.

- Complete-request excess above 8,192 ranged from 241 to 7,189 tokens (mean
  6,109.6; median 7,045) across the seven no-call cases.
- The candidate package's task-prompt token estimates contributed 171–254
  tokens per affected case, 1,454 in aggregate (mean 207.7).
- Under the complete-request estimator's separate conservative byte/3 rule,
  deleting the entire system-prompt content would remove 230–351 estimated
  envelope tokens per affected case. This serialization-aware range differs
  from the package's byte/4 prompt metadata by design.
- Emptying the whole task system prompt could theoretically bring only 1 of 7
  cases under 8,192. The other six would still exceed the limit by 6,770–6,839
  tokens.

The empty-prompt calculation is an upper-bound diagnostic, not a viable prompt
or authorization to alter the frozen experiment. It shows that prompt-only
shortening could theoretically rescue the single marginal envelope, while the
other six are dominated by non-system-prompt request content.

## Calls, cost, and ceilings

Observed calls are actual recorded transports/calls. Charged calls apply the
accepted conservative policy. Measured provider cost and budget-ledger
compute/proposer accounting are separate; neither is treated as an invoice for
the other.

| Activity | Observed calls | Charged calls | Known provider cost | Budget-side reconciled cost |
| --- | ---: | ---: | ---: | ---: |
| Accepted state before D.4.2 | 173–221 | 441 | US$0.09216432 partial | US$7.5983975014 |
| Diagnostic D.4.2 root | 64 | 64 | US$0.0126504 partial | US$0.0383801275 |
| Fresh P0 | 33 | 33 | US$0.0126568 | Included below |
| Fresh GEPA adapter transports | 72 | 72 | Unavailable | Included below |
| Fresh evaluated candidate | 33 | 33 | US$0.0109561 | Included below |
| Fresh proposer | 4 | 4 | US$0.1217919 | Included below |
| **Fresh completed root** | **142** | **142** | **US$0.1454048 partial** | **US$0.1452040383** |
| **Cumulative** | **379–427** | **647** | **US$0.25021952 partial** | **US$7.7819816672** |

The fresh complete-operation reservation was 368 task attempts, four proposer
primaries, and four proposer retry allowances: 376 charged calls. An earlier
pre-call scalar recorded US$1.4414656 of compute reservation but omitted the
separately enforced US$0.48 proposer reservation. Append-only correction makes
the combined reservation US$1.9214656 and the pre-run cumulative projection
US$9.5582432289/US$35. Authorization remained sufficient. Because the run
completed without retries, the ledger reconciled to actual budget-side cost
rather than retaining the full reservation. Remaining optimizer headroom is
303 charged calls and US$27.2180183328 of budget-side accounting.

### Owner-reported account billing snapshot

- Total amount due: £0.18.
- Due date: 2026-08-30.
- Currency: GBP.

This is an owner-reported account billing snapshot. Its exact scope, billing
lag, taxes, and attribution to D.4.2 are not independently proven. It is not
currency-converted or reconciled directly to the measured or reserved
US-dollar figures above.

## Finalist, fixed judge, and protected boundaries

No candidate passes every deterministic qualification gate. P0 is retained
explicitly, but not promoted. The condition for resolving and preflighting the
fixed judge never became true, so judge policy resolution, construction,
eligible-case reservation, calls, tokens, and cost are all zero.

- Holdout paths, enumeration, reads, and calls: zero.
- RunPod, LM Studio, local endpoints, and alternate models: zero activity.
- Fifth proposal: zero.
- Semantic retries and output repair: zero.
- Private proposal/input/reference/output artifacts tracked by Git: zero.
- Generic repair cycles: one consumed, two unused.

## Verification and replay

- Fresh-process P0 packaging and verification succeeded twice without provider
  calls at the exact run-bound commit.
- Provider-free shortlist export succeeded twice and returned count zero with
  status `no-improvement`.
- The two P0 packages were byte-identical. The two shortlist exports were
  byte-identical.
- Provider-free inspection succeeded.
- Before and after replay, the run contained 418 files and 337,685 bytes with
  an identical private tree digest.
- The eight pre-existing D.1/D.4/D.4.1 roots match every byte and SHA-256 entry
  in the pre-experiment manifest.
- `.chronicle` is ignored and contains zero tracked files.
- Gate 1 and repair checkpoints passed focused tests, the full repository suite
  with one expected skip, Ruff, Poetry validation, formatting, CLI/import
  checks, privacy/tracking scans, and `git diff --check`.

## Conclusion and limitations

This is a complete four-position development experiment and a defensible
no-finalist result. It shows that durable proposal evidence distinguishes
strict rejection, GEPA acceptance, and final promotion; that JSON fallbacks
materially increase paid transports; and that a minibatch improvement can fail
the decisive complete-request context gate even while every validity-comparison
eligibility condition passes.

It does not show that GEPA cannot improve prompts, that P0 is deployable, or
that the result generalizes. The corpus is one private ten-conversation silver
development set with FABLE-derived references, not human-adjudicated ground
truth or untouched evaluation. Only one proposal produced a fully evaluated
candidate, adapter cost is partial, provider retry availability for proposer
responses is absent, and holdout remains unopened.
