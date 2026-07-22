# WP-5.2B1.3 Validation Review

## Decision

**Accepted on 2026-07-22.** Both accepted candidate arms completed the same frozen
10-conversation/40-case scope, every candidate and eligible judge position is accounted for, both
packages verify, deterministic and semantic scoring completed, and both cache-only replays exited
zero without provider calls.

## PM validation

- Poetry resolved to the repository-local `.venv`.
- Private aggregate inspection independently confirmed 40 expected cases per arm, 21 valid/19
  invalid Llama outcomes, 39 valid/1 invalid Gemini outcomes, matching frozen-prefix identity, and
  complete judge accounting.
- Candidate generation provenance remains pinned to `dcca7b2`; the later Windows atomic-write fix
  at `3580d6d` is correctly recorded as scoring/cache-finalization code and was not rewritten into
  either immutable candidate package.
- Full repository suite: 431 passed, 1 explicitly opt-in provider test skipped.
- Ruff: passed.
- `poetry check`: passed after retrying the known Windows sandbox launcher failure outside the
  sandbox; the project command itself did not fail.
- No staged files and no tracked private evaluation, database, SQLite, ZIP, credential, raw output,
  reference, transcript, or judge-attempt artifact.
- Only the privacy-safe completion report was delivered by the executor.

## Accepted evidence

| Measure | Local Llama 3.2 1B | Hosted Gemini 3.5 Flash |
| --- | ---: | ---: |
| Candidate cases | 40 | 40 |
| Schema-valid | 21 (52.5%) | 39 (97.5%) |
| Candidate invalid/failed | 19 | 1 |
| Pro-judge completed/failed | 21 / 0 | 39 / 0 |
| Invalid skipped from judging | 19 | 1 |
| Candidate wall time | 257.653 s | 382.652 s |
| Candidate latency p50/p95 | 5.516 / 12.405 s | 8.929 / 20.045 s |
| Cache-only provider calls | 0 | 0 |

Llama failures remain visible as six context-length, seven evidence-validation, and six
schema-validation outcomes. Gemini retains one invalid-JSON outcome. Neither arm's candidate
outputs were repaired, truncated, removed, or semantically retried.

The local Llama 120-case planning projection is approximately 12 minutes 53 seconds. This supports
continuing locally at the current stage; it does not predict the runtime of larger retained models.

## Interpretation

This pilot establishes operational direction, not statistical superiority. On these 40 frozen
cases, hosted Gemini was substantially more reliable under the application contracts, while local
Llama completed generation faster but failed nearly half the cases. The evaluation floor is doing
its job by exposing context, evidence, and schema boundaries rather than setting a quality target.

Proceed to WP-5.2A5 model qualification using the unchanged frozen contracts. Each new model must
pass all four tasks on one synthetic and one frozen conversation before entering the same 40-case
pilot.

## Residual limits

- Ten conversations are too few for publication or stable latency/quality claims.
- FABLE references are silver development labels and Gemini Pro is an automated judge, not ground
  truth.
- Candidate Gemini and judge Gemini are from the same provider/model family. Candidate identity is
  blinded, but possible family/style affinity remains a limitation; deterministic metrics and
  FABLE comparisons must remain separately visible.
- Cross-provider token totals use different tokenizers/accounting semantics and are not directly
  comparable. Six local context failures also lack usage records.
- The linear 120-case projection includes six fast context-limit failures and may underestimate a
  model that processes every long case successfully.
- The Pro endpoint is a preview alias and may drift. Keep future compared runs in a bounded window
  or repeat an accepted anchor package.

## Commit state

The completion report and this PM validation review remain unstaged and uncommitted. The manager
will update plan/ledger state and commit only after explicit owner instruction.
