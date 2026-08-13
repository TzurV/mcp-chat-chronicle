# WP-5.2B3B.1C GEPA pilot article evidence addendum

## Publication status

This is privacy-safe evidence for later analysis, not a publishable claim that
GEPA succeeded or failed. The experiment stopped at a provider/runtime boundary
before a candidate existed. Private prompts, inputs, references, responses,
identities, resource identifiers, credentials, project values, and hashes are
not publication sources.

## Method and complete denominators

The accepted P0 was frozen as the sole parent. One bounded instruction-only GEPA
proposal position was started with deterministic validators and existing FABLE
development references as optimization feedback. Gemini 3.1 Pro was configured
only as the Vertex AI proposer in `global`; the fixed judge was excluded. The
development split remained six train and four validation conversations, with
24 and 16 task positions respectively. The holdout was not accessed.

| Search denominator | Count |
|---|---:|
| Proposal positions started | 1 |
| Proposals completed | 0 |
| Proposals interrupted | 1 |
| Candidate packages generated | 0 |
| Candidate results generated | 0 |
| Terminal candidate evaluations | 0 |
| Privacy/context eligible candidates | 0 |
| Shortlisted candidates | 0 |
| Continuation operations | 0 |
| Fixed-judge calls during GEPA | 0 |
| Holdout conversations opened | 0 |

## Negative and positive findings

Negative finding: the exact authorized provider/runtime route did not yield a
candidate. Provider attempts returned HTTP 400/model-not-found responses, and
the append-only proposal terminated as an unwrapped `PicklingError`. Because no
candidate existed, reliability, semantic agreement, privacy, context fit, and
local-transfer effects are all unmeasured.

Positive process finding: fail-closed controls worked. The operation reserved
budget before the boundary, retained an interrupted attempt and current
authority, released the unused candidate position, left no pending reservation,
did not reinterpret infrastructure failure as prompt-quality evidence, and
blocked automatic continuation. P0 and Bootstrap evidence remained immutable.

Operational finding: temporary user ADC can be bootstrapped into a RAM-only
remote shell, validated without a provider request, revoked, and erased without
placing credential or project values in persistent storage. The paid Pod can be
stopped while retaining its 30 GB network volume and all experiment state.

## Cost and search effort

The Pod used one RTX 5090 32 GB GPU in an EU Secure class at US$0.99/hour for
approximately 1.761 hours, an estimated US$1.744. The proposal itself ran for
329.682 seconds.

Measured provider usage was unavailable because the exception escaped before
adapter accounting returned. The ledger therefore retained the complete
reservation: 20 task invocations, 20 proposer calls, 20 retries, 1,000,000 input
tokens, 160,000 output/reasoning tokens, 0.833333 configured compute hours,
US$3.92 proposer cost, and US$1.294105 configured compute cost. These figures are
conservative capacity accounting, not claimed invoice or consumption values.

## Baseline context

The untouched P0 development-validation baseline remains 11/32 schema-valid:
Qwen 5/16, Phi 6/16, conversation summary 0/8, work-mode classification 6/8,
last activity 0/8, and title assessment 5/8. Its FABLE-reference semantic
agreement remains 0.1266. There is no GEPA comparison row.

## Limitations and allowed interpretation

- One interrupted proposal is an infrastructure/provider observation, not a
  prompt-method sample.
- Actual provider attempts, retries, tokens, and local candidate-model calls are
  unknown; only the fail-closed reservation is authoritative.
- Model-not-found can reflect preview availability or account access. No public
  claim should assign a cause more specific than the retained evidence.
- The `PicklingError` obscures clean measured-usage reconciliation and may need
  a generic harness repair.
- No candidate means no privacy, context, reliability, semantic, cost-benefit,
  remote-to-local, or holdout generalization conclusion is available.
- FABLE references are frozen development targets, not independent human gold
  labels.

The defensible article lesson is narrow: reproducible prompt optimization is a
systems experiment, and a well-designed negative checkpoint preserves
uncertainty instead of converting a provider failure into a model-quality story.
