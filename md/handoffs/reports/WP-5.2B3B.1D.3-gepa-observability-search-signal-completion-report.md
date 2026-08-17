# WP-5.2B3B.1D.3 GEPA Observability and Graded Search Signal Completion Report

Date: 2026-08-17

Executor start: clean `main` at accepted manager commit `82e1af5`

Delivery state: complete, unstaged, uncommitted, awaiting manager validation

## Manager summary

The provider-free D.3 foundation is implemented. Chronicle now persists a
private, append-only GEPA proposal envelope after proposal scoring and before
GEPA's strict acceptance decision, then appends a separate accepted/rejected
decision. Rejected proposals therefore remain auditable. DSPy's ChatAdapter to
JSONAdapter fallback now has exact logical-position and transport accounting,
separate from provider retries, with fail-closed reconciliation. Optimizer
configuration v2 adds an explicit graded GEPA-only reliability ladder while the
final deterministic promotion rule is unchanged.

All evidence was synthetic. Focused optimizer validation passed 178 tests. The
full suite passed 658 tests with one existing skip. No candidate, proposer,
fixed-judge, network, ADC, RunPod, LM Studio, private development, historical
ignored-run, or holdout activity occurred.

## Implemented proposal lifecycle

`bench/optimization/observability.py` defines the application-owned contract
and append-only store. A pre-decision envelope contains:

- contract/event version and SHA-256 event identity;
- run ID, optimizer ID, optimizer authority identity, and proposal ordinal;
- selected `task_0` through `task_3` component and parent identity;
- the proposed prompt text, restricted to the configured ignored run root;
- parent/proposal prompt SHA-256, UTF-8 byte lengths, and signed byte delta;
- demonstration identities and sampled example-local IDs;
- aligned parent and proposal score vectors;
- bounded allowlisted feedback categories and schema paths only; and
- privacy scanner identity, counts, eligibility, and evidence hash.

The observer uses GEPA 0.1.1's public callback events. It captures the parent
evaluation, selected component, reflective dataset, proposed instruction, and
proposal evaluation. The proposal evaluation callback writes the envelope. The
later candidate accepted/rejected callback writes a separate decision record.
This ordering matches GEPA's strict `new_sum > old_sum` decision boundary.

The proposed text is deliberately present only in the private envelope. A
logging filter replaces GEPA's ordinary `Proposed new text` message with a
fixed redaction. Public reports and ordinary logs retain hashes/lengths and no
proposal body.

GEPA and DSPy swallow callback exceptions by design. Chronicle therefore also
records a sanitized observer-error state and requires post-compile
reconciliation before returning a proposal. Missing envelopes, pending
decisions, tampering, duplicate ordinals, foreign run/optimizer identities,
ambiguous decisions, privacy failure, or callback failure stops the operation.
A pending envelope can be verified after interruption and finalized only by
appending its matching decision; existing evidence is never rewritten.

## Adapter fallback and retry accounting

Chronicle supplies an explicit public DSPy adapter with ChatAdapter fallback
disabled internally, invokes ChatAdapter once, and invokes JSONAdapter once
only after DSPy's explicit `AdapterParseError`. `LMError`, `ValueError`,
`TypeError`, callback errors, configuration errors, and unexpected exceptions
propagate after the single Chat transport and cannot cause JSON fallback. There
is no output repair, semantic retry, or manual reinterpretation.

The public DSPy LM callback records each actual candidate transport with:

- logical score position;
- monotonically contiguous transport ordinal;
- `chat` or `json` adapter;
- explicit fallback boolean;
- sanitized `response` or `provider-error` terminal;
- provider retry ordinal, fixed at zero because GEPA candidate LMs retain
  `num_retries=0`;
- input/output token usage or explicit unavailability; and
- measured latency with explicit availability.

Allowed sequences are exactly one Chat transport, or Chat followed by one JSON
fallback, per logical score position. JSON-first, repeated, incomplete,
foreign, tampered, or noncontiguous evidence fails. The transport count must
equal DSPy's independent task-call callback count. Proposer infrastructure
retry allowance remains separate in `AdapterReservation.retries`.

Budget reservation now allows two candidate transports at every GEPA score
position before execution. With 16 validation cases, a three-example reflection
minibatch, and `N` proposals, the maximum GEPA candidate transports are:

`2 * (16 + N * (2 * 3 + 16))`

This yields 164, 208, and 252 candidate transports for three, four, and five
proposals. Each option separately reserves `N` proposer primary calls and `N`
proposer infrastructure retries.

## Graded optimization-only search score

Optimizer config v2 requires this exact `gepa-reliability-v1` contract:

| Deterministic stage | Score |
| --- | ---: |
| Provider-invalid or empty | 0.0 |
| Invalid JSON | 0.1 |
| Schema invalid | 0.3 |
| Evidence invalid | 0.6 |
| Cross-field/date invalid | 0.8 |
| Fully valid | `0.999 + FABLE agreement * 0.000001` |

Only fully valid output receives a FABLE tie-breaker. Its range is 0.999 through
0.999001. Every invalid stage remains below 0.999, so partial validity cannot
cross the existing validity threshold.

The schema-invalid boundary catches only Pydantic `ValidationError` raised
while validating parsed model output. Schema identity lookup occurs outside
that boundary. Unknown schema IDs, injected application defects, and unrelated
exceptions therefore propagate and stop the optimizer; they do not become a
0.3 model-quality score, append a proposal decision, or trigger another model
transport.

The score contract participates in optimization-config identity, optimizer and
result authority identity, and the GEPA state/cache namespace. Version 1
configs omit the new field from their serialized identity and continue using
the historical binary valid/invalid GEPA scalar. This preserves interpretation
of existing results and prevents score-version state reuse.

Version 2 explicitly disables GEPA merge proposals. This keeps every bounded
proposal tied to one proposer-selected component and makes the pre-decision
contract and call reservation exact. Version 1 retains its historical merge
behavior and identity.

No package/result schema or final promotion rule changed. Final selection still
uses complete deterministic validity, model/task reliability, privacy,
terminal accounting, context fit, lineage, and P0 comparisons in
`bench/optimization/operations.py`. Existing partial-output promotion
regressions remain green.

## Synthetic regression evidence

The new provider-free suite covers:

- pre-decision envelope presence before a decision;
- retained rejected-proposal text and the observed `[0, 2, 1]`, all-zero tie;
- interrupted finalization completed by decision append only;
- tampered, duplicate, foreign, ambiguous, and unmatched evidence rejection;
- proposal-text redaction from ordinary logging;
- explicit Chat/JSON fallback sequences and provider-retry separation;
- exact transport/task-call reconciliation and exact 3/4/5 budget reservation;
- strict score-ladder ordering and the `< 0.999` invalid ceiling;
- v1 identity compatibility and v2 authority/state identity separation; and
- offline imports that do not initialize DSPy, LiteLLM, or Google auth.

The existing supported tracked optimizer lifecycle test also runs the pinned
DSPy/GEPA path with synthetic authority and dummy LMs, completes proposal,
evaluation, persistence, verification, and zero-call replay, and remains green.
The prior lineage-only/no-distinct-prompt behavior remains unchanged.

Validation completed so far:

- focused new suite: `23 passed`;
- complete optimizer suites: `178 passed`;
- full repository suite: `658 passed, 1 skipped`;
- Poetry environment preflight: repository `.venv` confirmed.

Ruff, Poetry metadata, CLI/import, diff, tracking, and privacy validation are
recorded in the final validation section below.

## Future private experiment assessment — design only

No experiment is authorized by this report. A future separately authorized
handoff should use:

- candidate: `vertex_ai/gemini-2.5-flash-lite`, single model, 8,192 context;
- proposer: `vertex_ai/gemini-3.5-flash`, Vertex `global`;
- unchanged frozen six-conversation train and four-conversation validation
  manifests, totaling 24/16 cases and 40 development cases;
- target four proposals, minimum three, maximum five;
- failure-focused reflection using the lowest graded failures plus valid
  anchors, while retaining trace-aligned component selection;
- one finalist evaluated across all 40 development cases;
- fixed judge only after deterministic finalist selection; and
- zero holdout access.

Conservative call and cost planning, using the previously accepted per-call
bounds, is:

| Proposals | Fresh charged calls | Cumulative after prior 109 | Incremental conservative cost | Cumulative after prior US$6.0814776 |
| ---: | ---: | ---: | ---: | ---: |
| 3 | 330 | 439 | US$1.4867808 | US$7.5682584 |
| 4 | 376 | 485 | US$1.9209856 | US$8.0024632 |
| 5 | 422 | 531 | US$2.3551904 | US$8.4366680 |

The fresh call totals include 160 candidate attempts for P0 plus finalist over
all 40 cases, fallback-aware GEPA candidate reservations of 164/208/252, and
both primary and one infrastructure retry for each proposer call. A future
handoff may consider a 540 cumulative-call ceiling while retaining the US$35
ceiling. The old 510 estimate did not fully reserve adapter fallback and is
superseded as planning evidence only. Neither figure is authorization.

## Activity and privacy boundary

- Candidate calls: 0.
- Proposer calls: 0.
- Fixed-judge calls: 0.
- Network calls: 0.
- ADC/authentication reads or refreshes: 0.
- RunPod, LM Studio, and local-model activity: 0.
- Private development/FABLE inputs read: 0.
- Historical ignored run roots read or modified: 0.
- Holdout reads: 0.
- Output repair, semantic retries, or model-output reinterpretation: 0.
- New private artifacts: 0; tests used pytest temporary synthetic roots only.

The source tree was inspected without enumerating `.chronicle` or other ignored
private roots. All delivery files are tracked-source candidates; no prompt text,
credentials, project values, private provenance, or provider response is in the
diff.

## Delivery files

- `bench/optimization/observability.py`
- `bench/optimization/models.py`
- `bench/optimization/production.py`
- `bench/optimization/dspy_bridge.py`
- `bench/optimization/execution.py`
- `bench/optimization/recovery.py`
- `bench/optimization/feedback.py`
- `bench/optimization.default.yaml`
- `tests/test_bench_optimization_observability.py`
- `docs/development-optimization.md`
- `md/research/WP-5.2B3B.1-prompt-optimization-activity-log.md`
- `md/development-ledger.md`
- this report

## Final validation

- Poetry environment: `poetry env info --path` resolved to the repository
  `C:\work\Github\mcp-chat-chronicle\.venv`.
- Focused new regressions: `23 passed`.
- Full optimizer regressions: `178 passed`.
- Full repository suite: `658 passed, 1 skipped`.
- Ruff lint: `poetry run ruff check .` passed.
- Ruff formatting: all eight changed Python files passed
  `poetry run ruff format --check`. A repository-wide format check identified
  nine pre-existing, untouched files outside this delivery; they were not
  reformatted.
- Poetry metadata: `poetry check` returned `All set!`.
- CLI smoke: `poetry run python -m bench --help` passed and listed the supported
  optimizer commands. Sandboxed CLI/import launches intermittently failed before
  Python started with Windows `CreateProcessAsUserW` error 1920; the identical
  read-only commands passed outside that runner boundary.
- Import smoke: importing `bench.optimization.models` and
  `bench.optimization.observability` reported `offline-import-ok`, with `dspy`,
  `litellm`, and `google.auth` absent from `sys.modules`.
- `git diff --check`: passed.
- Credential-pattern scan across every delivery file: zero matches.
- Prior private-authority/root provenance scan across every delivery file: zero
  matches.
- Tracking: existing delivery files remain tracked modifications; the new
  observability module, regression file, and this report are visible untracked
  files, not ignored payloads. The manager-supplied validation review remains
  unmodified and untracked.
- Staging: the index is unchanged; every delivery change is unstaged and
  uncommitted for manager review.

## 2026-08-17 validation-review rework addendum

The manager review found two overbroad exception catches. This bounded rework
corrected only those boundaries:

1. The ChatAdapter wrapper now catches only DSPy's `AdapterParseError` and
   performs exactly one JSONAdapter fallback. Exact-count regressions prove
   Chat/JSON counts of `1/1` for `AdapterParseError`, and `1/0` for `LMError`,
   `ValueError`, `TypeError`, synthetic callback errors, synthetic configuration
   errors, and unexpected `RuntimeError`.
2. The graded score now resolves the schema before its validation catch and
   catches only Pydantic `ValidationError` from model-output validation.
   Malformed output still receives the configured schema-invalid 0.3 score.
   Regressions prove that an unknown schema, an injected model-validation defect,
   and an unrelated agreement-scoring defect propagate while the transport
   count remains one and the proposal store remains empty.

All earlier D.3 contracts remain unchanged: append-only pre-decision evidence,
separate decisions, privacy scanning, v1 compatibility, v2 score/state identity,
strict final promotion, no merge for v2, and the 540-call planning-only status.
The rework made zero provider, ADC, private-data, fixed-judge, RunPod, or LM
Studio calls.
