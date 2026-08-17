# WP-5.2B3B.1D.4 Validation Review

**Status:** Diagnostic stop accepted; multi-proposal objective not started

## Manager decision

The Gate 3 stop and conservative accounting are accepted. Authority copying,
the 6/4 split, ADC, route configuration, preflight, privacy, and budget gates
passed. The first train-scope P0 evaluation then raised a persisted
`ValueError` before an authoritative batch or result was written. No GEPA
proposal, tuned candidate, finalist, fixed-judge call, or holdout access
occurred.

This is not model-quality or prompt-optimization evidence. Preserve the D.4
root append-only and do not rerun it.

## Observability finding

Ordinary `LiteLLMCandidateAdapter` evaluation lacks the per-position append-only
transport and terminal evidence now available inside GEPA. A batch-level
failure therefore leaves an irreducible zero-to-reserved-attempt call range,
loses completed in-memory outcomes, and cannot resume without repeating
unknown work.

Before another private run, add provider-free ordinary-evaluation evidence:

- append a request intent before each case transport;
- append each transport attempt and retry separately;
- retain sanitized configured/actual route identity and a typed terminal
  category;
- persist usage, cost, latency, finish, and availability fields;
- persist each terminal case outcome before advancing;
- reconcile a completed batch from its case journal; and
- resume by skipping byte-verified terminal cases without duplicate calls.

Unexpected response-identity, usage, accounting, callback, and application
errors must remain distinct and fail closed without provider-controlled text in
tracked output.

## Accounting decision

The cumulative conservative state is accepted as 157 charged calls and
US$6.2616008. The previous 540-call ceiling has 383 calls remaining, which is
insufficient for a completely fresh maximum-five-proposal path using the
current worst-case estimate. Any future ceiling must be recalculated after the
ordinary-evaluation journal is implemented. No increase is authorized here.

## Validation

- Focused observability: 23 passed.
- Complete optimizer tests: 178 passed.
- Full repository suite: 658 passed, 1 expected skip.
- Ruff, Poetry, CLI/import, privacy, tracking, and `git diff --check`: passed.
- Provider, proposer, judge, holdout, RunPod, and local-model activity after the
  stop: zero.

## Next action

Create a provider-free D.4.1 handoff for ordinary candidate transport
observability and resumable per-case persistence. Commit that repair before any
synthetic provider probe or fresh private D.4 run.
