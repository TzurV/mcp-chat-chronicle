# WP-5.2B3B.1D.4.2 PM Validation Review

Date: 2026-08-18

Status: **Accepted**

## Decision

Accept WP-5.2B3B.1D.4.2 as a complete four-position hosted GEPA development
experiment with an explicit no-finalist result. Accept checkpoint commits
`7d3af24` and `96154c6`, the final reports, the private append-only evidence,
and P0 retention. Do not promote the evaluated candidate.

## Evidence reviewed

- Fresh P0 completed 40/40 terminal positions with 16 valid outputs, 17 schema
  failures, and seven deterministic 8K no-call outcomes.
- Four GEPA positions completed with decisions reject, reject, accept, reject.
- Every position has durable private intent, response, generated proposal,
  privacy, decision, and terminal evidence.
- The accepted position-3 proposal produced the only evaluated candidate.
- The candidate completed 40/40 terminal positions and passed six of seven
  mechanical `_eligible` conditions.
- Context fit alone failed: 15,381 versus 8,192 tokens. Validation validity
  matched P0 at 6/16, while FABLE agreement declined from 0.128125 to 0.112500.
- Removing the complete task prompt could theoretically recover only one of
  seven no-call envelopes; six remain 6,770–6,839 tokens over 8K.
- Fresh execution used 142 observed and charged calls with zero retries;
  cumulative charged accounting is 647/950.
- Fixed judge, holdout, RunPod, LM Studio, alternate models, semantic retries,
  and output repair remained unused.
- Fresh verification, shortlist export, inspection replay, privacy scans, and
  historical byte-integrity checks passed without provider calls.

## Cost interpretation

The owner reports a Google account billing snapshot of £0.18 GBP due
2026-08-30. Its exact scope, billing lag, taxes, and attribution to D.4.2 are
not independently proven. It must remain separate from partial measured
provider telemetry and conservative USD budget/reservation ledgers.

## PM validation checks

- Focused proposer-observability tests: passed.
- Ruff: passed.
- Poetry validation: passed.
- Documentation tables and whitespace: passed.
- `git diff --check`: passed.
- Privacy/tracking boundary: passed; `.chronicle` remains untracked.

## Program consequence

Do not spend further prompt-search calls under the unchanged 8K/input contract.
The dominant context limitation is mostly source-envelope size rather than task
prompt size. WP-5.2B3B.2 remains gated because no qualified finalist exists.
Keep the twenty-conversation holdout closed pending a manager decision about
input selection/context feasibility or explicit P0 retention as the final
package.
