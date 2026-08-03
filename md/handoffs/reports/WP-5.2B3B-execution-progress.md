# WP-5.2B3B Execution Progress

## Current status

**Gate 1 ready for PM validation. Mandatory checkpoint stop is active. No prompt authoring or
model calls have started.**

Last updated: 2026-08-03

## Gate 0 preflight

- Branch: `codex/wp-5.2b3b-prompt-development`
- Starting commit: `25877b01e375e191a95e14f29f254f1523f0df77`
- Handoff present at the starting commit: yes
- Poetry environment resolves to this repository's `.venv`: yes
- Tracked checkout was clean before execution: yes
- WP-5.2C1 and accepted private artifact roots are excluded from writes: yes

## Gate 1 plan

1. Add a strict, versioned ordered selection-manifest contract.
2. Bind the manifest's role and content identity through every benchmark stage.
3. Reject authority, count, duplicate, order, hash, role, and prefix-scope conflicts.
4. Preserve existing full-corpus, frozen-prefix, and historical-package behavior.
5. Add synthetic focused tests and generic operator documentation.
6. Run focused tests, the full suite, Ruff, Poetry checks, CLI help, and Git diff checks.
7. Stop before prompt authoring or model generation for manager validation and commit.

## Progress log

- Completed the read-only repository and handoff review.
- Completed Gate 0 branch, clean-state, HEAD, and Poetry-environment checks.
- Mapped the current prefix scope through preparation, generation, verification,
  deterministic scoring, and fixed-judge eligibility.
- Implemented the strict version-1 selection-manifest and configuration schemas.
- Implemented role, content-hash, source-authority, count, aggregate, duplicate, and unknown-entry
  validation.
- Propagated the ordered scope through bundle, generation-work, candidate-package, verification,
  deterministic-scoring, and judge identity/accounting paths.
- Preserved the existing full-corpus and frozen-prefix serialization used by historical packages.
- Added synthetic tests for non-prefix cross-stage continuity, both declared roles, development
  versus holdout separation, counts, missing and duplicate entries, unknown authority entries,
  source-identity mismatch, hash/order tampering, scope tampering, private-path non-leakage, and
  mutual exclusion with `conversation_limit`.
- New focused selection-manifest tests: 8 passed.
- Existing benchmark suite passed before the new tests were added; the complete expanded benchmark
  suite will be rerun after documentation review.
- Added the generic operator workflow to `docs/development-evaluation.md` and an optional config
  example to `bench/evaluation.default.yaml`.

## Gate 1 checkpoint result

The benchmark now supports a strict `ordered-manifest-v1` scope alongside the unchanged
`frozen-prefix-v1` scope. The private evaluation configuration independently pins manifest role,
content hash, complete source-selection identity, expected conversation count, and expected
task-case count. The manifest binds its format version, algorithm version, complete
source-authority identity, ordered selected conversation identities, provider/length/date
aggregates, creation time, and canonical content hash.

Every stage preserves or independently reconstructs the same scope as appropriate:

- preparation validates the complete accepted directory shape and resolves every selected entry
  against its accepted input-envelope content identity;
- generation requires the bundle role, manifest hash, and counts to match configuration;
- package identity carries the complete portable scope without the manifest path;
- verification reconstructs the ordered authority and source bundle independently;
- deterministic scoring deserializes references only for selected cases;
- fixed-judge accounting includes only valid outputs in the selected scope.

The focused cross-stage test deliberately replaces every unselected input and reference file with
invalid non-JSON text after freezing the synthetic manifest. Preparation, generation,
verification, deterministic scoring, and judge scoring still complete successfully for the
selected scope. This proves that ordered-manifest execution checks the complete authority's file
shape without opening unselected raw inputs or references.

Existing unlimited 30/120 behavior, `conversation_limit` prefix behavior, and historical prefix
package serialization remain unchanged. An ordered manifest and `conversation_limit` are mutually
exclusive.

## Gate 1 validation

- Focused new selection-manifest matrix: 8 passed.
- Full repository suite: 455 passed, 1 skipped.
- Repository-wide Ruff: passed.
- Poetry metadata check: passed.
- Poetry environment: repository `.venv` confirmed.
- Bench root/prepare/generate/verify/score help: passed.
- Chronicle root help and AI-task listing: passed.
- `git diff --check`: passed.
- Staged-file check: empty; nothing staged.
- Private artifact tracking check: no tracked `.chronicle`, database, SQLite, ZIP, or export
  artifact reported.
- One full-suite invocation hit its 120-second command timeout without a test failure; the same
  suite was immediately rerun with a larger execution window and completed successfully with the
  totals above.

## Gate 1 delivery files

- `bench/__main__.py`
- `bench/core.py`
- `bench/evaluation.default.yaml`
- `bench/judge.py`
- `bench/loaders.py`
- `bench/models.py`
- `docs/development-evaluation.md`
- `tests/test_bench.py`
- `md/handoffs/reports/WP-5.2B3B-execution-progress.md`

## Final checkpoint Git status

```text
 M bench/__main__.py
 M bench/core.py
 M bench/evaluation.default.yaml
 M bench/judge.py
 M bench/loaders.py
 M bench/models.py
 M docs/development-evaluation.md
 M tests/test_bench.py
?? md/handoffs/reports/WP-5.2B3B-execution-progress.md
```

All delivery changes are unstaged and uncommitted. Per the handoff, the manager must validate and
commit Gate 1. Execution resumes from that new clean commit with Gate 2 metadata-only split
freezing. Prompt authoring, local generation, hosted generation, deterministic development
analysis, and fixed-judge calls remain prohibited until then.

## Privacy and experiment boundary

- No private conversation content, references, model outputs, or holdout identities have
  been inspected for this gate.
- No external provider call has been made.
- Nothing has been staged or committed.
