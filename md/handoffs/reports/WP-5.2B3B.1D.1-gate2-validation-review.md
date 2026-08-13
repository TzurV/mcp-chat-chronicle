# WP-5.2B3B.1D.1 Gate 2 Validation Review

**Status:** Offline repair accepted; fresh private execution blocked on budget authorization

## Manager decision

The Gate 2 failure is a local persistence defect, not a model-quality result.
Gemini 2.5 Flash-Lite qualification passed and all eight P0 provider responses
returned, but `CandidateAccounting` rejected the fractional provider-cost field
before an authoritative P0 result could be written.

The generic repair is accepted:

- candidate usage accepts finite, nonnegative integer or fractional values;
- negative, non-finite, Boolean, unnamed, and unsupported values fail closed;
- Vertex provider aliases remain bound to the configured Vertex route;
- hosted-candidate preflight validates provider-route identity without requiring
  a local artifact;
- a failure after terminal evaluation but before result persistence appends an
  interrupted trial instead of leaving an ambiguous in-progress boundary.

Manager validation passed:

- complete AI adapter and optimizer matrix: 178 passed;
- full repository suite: 634 passed, 1 expected skip;
- Ruff: passed;
- Poetry validation: passed;
- `git diff --check`: passed.

## Recovery decision

Do not resume or rewrite the stopped Gate 2 run. Its eight responses were held
in process memory and no authoritative result/output package was persisted.
Reconstructing a result from logs or provider traces would bypass the accepted
application validation boundary. Preserve the stopped run append-only as
diagnostic evidence.

A fresh run must use a new ignored run root and repeat P0 generation. The
successful synthetic route qualification may be reused as route evidence if
its model/configuration identity remains exact; do not spend another
qualification call merely to recreate the same proof.

## Budget consequence

Existing cumulative conservative accounting is 53 charged calls and
US$5.8336808. The current ceiling of 80 leaves 27 charged calls, which is not
enough to reserve a fresh P0, one bounded GEPA proposal, and tuned evaluation
under the accepted infrastructure-retry policy.

The recommended revised cumulative ceiling is:

- **120 conservatively charged calls**;
- **US$35**, unchanged.

This leaves enough capacity for the supported-path reservations without
weakening retry, accounting, or stop rules. No fresh private call is authorized
until the owner explicitly approves the revised call ceiling.
