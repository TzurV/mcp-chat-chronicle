# WP-5.2B3B PM Validation Review

**Date:** 2026-08-05  
**Decision:** Accepted

## Scope reviewed

The PM reviewed the controlled ten-conversation manual global-prompt experiment,
its selected P0 package, completion report, article evidence brief, execution
record, and manager exception record. The ignored private candidate and judge
artifacts remain outside Git.

## Acceptance findings

- All 240 P1/P2 development candidate positions are terminal and accounted for.
- The fixed judge completed 182 of 184 eligible results; the two remaining
  provider-invalid-JSON failures are retained rather than hidden or repaired.
- Six cache-only replays made zero provider calls and preserved attempt evidence.
- P0 produced 62/80 pooled usable local outputs; P1 and P2 each produced 58/80.
- P1 and P2 breached the predefined reliability and Gemini portability
  guardrails, so unchanged P0 is correctly selected without semantic tie-breaking.
- P3 was correctly not triggered because the shared failures required context,
  selector, or application changes rather than another global prompt revision.
- The tracked selected P0 catalog is byte-identical to both default task catalogs;
  all three files have SHA-256
  `bd332905a78e74fd26251d85cb9acc417af940279e022c4dd725bb4f1a0cd1c5`.
- Production task defaults were not changed.
- The twenty-conversation holdout remained unopened and received zero candidate,
  scoring, or judge calls.
- The executor's focused, full-suite, Ruff, Poetry, CLI, privacy, and diff
  validations passed.

## Independent PM validation

- `poetry env info --path` resolved to the repository-local `.venv`.
- `poetry run pytest` completed with 474 passed and 1 skipped.
- `poetry run ruff check .` passed.
- `poetry check` passed.
- `git diff --check` passed.
- A privacy-pattern scan of the B3B tracked delivery returned no private user
  path, credential token, or configured cloud-project value.

## Interpretation

This closes WP-5.2B3B as a valid negative controlled experiment. It supports the
bounded conclusion that the two manually authored global prompt variants did not
improve this frozen development sample. It does not establish that schema-first
or few-shot prompting is generally inferior.

The completion report's direct transition to B3C is superseded by the approved
plan sequence: WP-5.2B3B.1 automatic BootstrapFewShot/GEPA search, WP-5.2B3B.2
local transfer qualification and winner freeze, then WP-5.2B3C one-shot holdout
evaluation. The holdout must remain unopened until B3B.2 freezes a winner or
explicitly retains P0.

## Residual controls

- Preserve the ignored B3B private split, packages, judge evidence, and selected
  manifest until B3B.1/B3B.2 no longer need them or a verified backup exists.
- Do not overwrite accepted P0 evidence.
- Do not use RunPod timing as local deployment evidence.
- Any optimizer/proposer credential used remotely must be temporary,
  least-privilege, untracked, and revoked after teardown.

## Decision

WP-5.2B3B is accepted and may be closed. The next deliverable is the detailed
WP-5.2B3B.1 handoff; WP-5.2B3C remains gated.
