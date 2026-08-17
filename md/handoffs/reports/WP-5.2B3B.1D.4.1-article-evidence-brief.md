# WP-5.2B3B.1D.4.1 Article Evidence Brief

Date: 2026-08-17

## Publication-safe headline

Resumability changed a failed prompt-optimization run from an unknowable batch
into exact per-case evidence—but it did not turn an incomplete GEPA search into
a quality result.

## Strong evidence available

- A 40-case hosted baseline can be made restart-safe at individual-case
  granularity: every intent, transport, usage record, terminal outcome, and
  batch reconciliation is append-only and byte-verifiable.
- Complete-request context checks matter before inference. Seven of 40 frozen
  development requests exceeded the 8,192-token boundary and were preserved as
  terminal no-call outcomes instead of being silently dropped or truncated.
- P0 completed 40/40 terminals with 16 valid outputs: 10/24 train and 6/16
  validation. Validity was concentrated in work-mode classification and title
  assessment; summary and last-activity produced no valid outputs in this run.
- Fresh-process verification made zero calls, and terminal replay left 260
  files byte-for-byte unchanged.
- Exact transport evidence separated 101 observed D.4.1 calls from 284
  conservatively charged calls. Partial measured incremental provider cost was
  US$0.025798; reservations remained deliberately separate.
- A real Windows checkpoint failure occurred after two proposer attempts.
  Instrumentation exposed a completed temporary JSON write, a failed atomic
  replacement, and a misleading provider classification caused by a recovered
  adapter fallback. The generic repair is tested and committed.

## Evidence not available

- The four-proposal target and three-proposal minimum were not completed.
- No proposal reached the private envelope/decision boundary, no GEPA candidate
  was created, and no finalist exists.
- The operational `pilot-no-improvement` label is not evidence that four GEPA
  proposals failed to improve P0.
- P0 exceeds the frozen context limit and is retained only as the development
  baseline; it is not a deployable or promoted winner.
- No fixed-judge result, holdout result, local-model transfer result, or
  production-quality claim exists for this work package.

## Defensible article angles

1. **A retry is an accounting event, not a loop.** Pre-transport intent and
   terminal persistence make interruption recovery auditable and prevent paid
   duplication.
2. **Context failures belong in the denominator.** Terminal no-call boundaries
   expose infeasible requests without changing the frozen prompt or silently
   shrinking the evaluation set.
3. **Operational labels need evidentiary qualifiers.** A terminal state can be
   correct for orchestration while still being insufficient for a scientific
   no-improvement claim.
4. **Optimizer integration is part of the experiment.** Adapter fallbacks,
   atomic persistence, callback evidence, and fail-closed budgets materially
   affect what conclusions are supportable.
5. **A hard budget can force the honest ending.** After 441 cumulative charged
   calls, the 159-call remainder could not fund a complete 376-call operation;
   stopping preserved validity better than spending selectively.

## Required caveats

This is one private silver development set of ten conversations and four tasks,
not an untouched evaluation set. FABLE references are development references,
not human-adjudicated ground truth. Costs are partial measured provider cost
plus separate configured/reserved budget accounting. The GEPA search is
incomplete, and no causal conclusion about Gemini model quality or GEPA
effectiveness should be drawn. Private prompts, inputs, references, outputs,
identifiers, paths, hashes, and credentials must remain unpublished.
