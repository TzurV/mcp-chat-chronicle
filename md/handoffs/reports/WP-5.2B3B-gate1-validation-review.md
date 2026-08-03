# WP-5.2B3B Gate 1 Validation Review

## Decision

**Accepted for the mandatory manager Gate 1 commit.**

No prompt authoring, candidate generation, judge call, private split freeze, or
holdout access may begin until the manager commits this Gate 1 delivery and the
executor confirms a clean tracked checkout at that new commit.

## Scope Reviewed

The manager reviewed the nine-file delivery against
`md/handoffs/WP-5.2B3B-global-prompt-development.md`:

- `bench/__main__.py`;
- `bench/core.py`;
- `bench/evaluation.default.yaml`;
- `bench/judge.py`;
- `bench/loaders.py`;
- `bench/models.py`;
- `docs/development-evaluation.md`;
- `tests/test_bench.py`;
- `md/handoffs/reports/WP-5.2B3B-execution-progress.md`.

## Findings

No blocking correctness, compatibility, privacy, or scope finding was found.

The implementation provides the required strict ordered non-prefix selection
scope while preserving the accepted full-corpus and frozen-prefix contracts.
Selected conversation aliases retain their original frozen authority indexes,
and every selected conversation identity is resolved against its accepted input
envelope before use.

Preparation, generation, package verification, deterministic scoring, and
fixed-judge accounting carry or independently reconstruct the same role,
manifest identity, complete source-selection identity, conversation count, case
count, and ordered selected-case authority.

The selected-input and reference loaders enumerate the complete expected file
shape but deserialize only selected files. The focused synthetic regression
replaced unselected input and reference contents with invalid non-JSON text and
still completed every selected stage, providing direct evidence that unselected
raw content remains unopened.

Historical prefix serialization remains compatible because the newly optional
scope fields are omitted from the portable frozen-prefix representation.

## Independent Validation

The manager reran:

```text
poetry env info --path
```

Result: repository-local `.venv` confirmed.

Focused ordered-manifest matrix:

```text
poetry run pytest tests/test_bench.py -k
  "selection_manifest or non_prefix_ordered or ordered_package_scope" -q
```

Result: 8 passed.

Full suite:

```text
poetry run pytest
```

Result: 455 passed, 1 skipped in 177.97 seconds. An earlier manager invocation
hit its command-wrapper timeout without a reported test failure; the clean
rerun completed under the expanded validation window.

Additional checks:

```text
poetry run ruff check .
poetry check
poetry run python -m bench prepare --help
git diff --check
git ls-files ".chronicle/*" "*.db" "*.sqlite" "*.zip" "exports/*"
```

Results:

- Ruff passed;
- Poetry metadata passed;
- bench prepare help passed;
- diff check passed;
- no private database, archive, export, or `.chronicle` artifact is tracked.

The Windows sandbox launcher blocked two read-only Poetry commands before they
ran. They passed when repeated under the repository's documented sandbox
validation procedure. This is not a project failure.

## Gate 2 Required Control

The generic manifest validates provider metadata against selected accepted
inputs and validates length-stratum/date-bin aggregates against its ordered
entries. Length strata and date bins are metadata owned by the frozen private
selection source rather than fields in the accepted input envelopes.

Therefore Gate 2 must:

1. derive provider, length-stratum, activity-date bin, authority index,
   case-group identity, and source-content identity only from the accepted
   metadata-only 30-conversation selection artifacts;
2. apply the handoff's deterministic quota algorithm before reading raw inputs,
   references, or per-case outcomes;
3. independently reconcile 3/3/2/2 provider and 4/3/3 length quotas;
4. freeze both development and holdout manifests and hashes before prompt calls;
5. prove that every development entry resolves to accepted authority;
6. preserve the holdout raw-content and per-case-outcome non-access boundary.

This is an expected Gate 2 validation responsibility, not a Gate 1 blocker.

## Commit Boundary

The Gate 1 implementation and this review must be committed by the manager as
one clean checkpoint before execution resumes. The executor must not stage or
commit files and must not continue from a dirty tracked implementation.

After the manager commit, the executor should report:

- the new Gate 1 commit hash;
- branch `codex/wp-5.2b3b-prompt-development`;
- empty `git status --short`;
- confirmation that no prompt or model/provider call occurred before the
  checkpoint.

The next authorized activity is Gate 2 metadata-only split freezing.
