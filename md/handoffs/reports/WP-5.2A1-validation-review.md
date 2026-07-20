# WP-5.2A1 Validation Review

## Decision

**Accepted after rework.**

The Llama 3.2 1B integration is operationally successful. Independent PM checks
confirmed the installed artifact identity and SHA-256, frozen/live database
no-write evidence, ignored private candidate area, documentation command syntax,
373 passing tests, clean Ruff output, working CLI help/task discovery, and clean
diff hygiene.

The original review identified two evidence-contract corrections that did not
require a new model call, prompt change, schema change, or product-code change.
The executor completed both without another model call, and the PM revalidated
them as recorded in the acceptance addendum.

## Confirmed Evidence

PM validation independently confirmed:

- Poetry resolves to the repository-local `.venv`.
- `lms ls --json` identifies the intended Bartowski Llama 3.2 1B Instruct
  `Q4_K_M` GGUF, 807,694,464 bytes, with the reported LM Studio model id and
  131,072-token advertised maximum context.
- A fresh SHA-256 of the installed GGUF matches the pinned candidate/report hash.
- A fresh SHA-256 of the frozen WP-5.1.2A database matches its accepted private
  manifest.
- A fresh SHA-256 of the live Chronicle database matches the WP-5.2A1 preflight
  fingerprint.
- Git confirms the private candidate manifest is ignored by `.chronicle/`.
- No `.chronicle` file, database, SQLite file, or ZIP is tracked.
- The private synthetic database contains a persisted failed
  `title-assessment` attempt as well as the successful attempts.
- `lms load --help` supports the documented `--context-length` and `--parallel`
  options.
- `poetry run pytest` passes: 373 tests.
- `poetry run ruff check .` passes.
- `poetry run chronicle --help` passes.
- `poetry run chronicle --ai-task list` passes without a model call.
- `git diff --check` passes.

The observed three-valid/one-schema-failure outcome is accepted as the correct
evaluation-floor baseline. Do not tune or repair it.

## Rework 1: Correct Private Run-Evidence Semantics

The private `runs/summary.json` currently records the schema-invalid title attempt
with:

```text
result_stored: false
```

The synthetic database independently shows that the failed attempt row was stored.
The current field actually appears to mean that no validated `result_json` was
stored. Its name therefore gives the wrong answer to the acceptance question
"was the failed attempt persisted?"

The same record reports evidence/date checks as `false` after application-schema
failure. A downstream check that was not reached is not equivalent to a check that
ran and failed. WP-5.2B1 must distinguish:

- `pass`;
- `fail`;
- `not_evaluated` or `not_applicable`.

Required correction:

1. Replace or supplement `result_stored` with unambiguous fields such as:
   - `attempt_row_stored`;
   - `validated_result_json_stored`.
2. Verify the failed title attempt reports:
   - stored attempt row: true;
   - validated result JSON stored: false.
3. Represent every boundary with tri-state semantics. Do not report `false` when a
   check was skipped because an earlier boundary failed.
4. Preserve a genuine cross-field failure as `fail` when it was directly
   established from the parsed response.
5. Add a stable run identifier and distinct relative artifact reference for each
   `direct`, `synthetic`, and `private_development` smoke in the private candidate
   manifest. Do not make both Chronicle smokes indistinguishable pointers without
   their run identity.
6. Regenerate only the private summary/manifest metadata from existing evidence.
   Do not call the model again.
7. Verify all existing model outputs, logs, database attempt rows, task catalogs,
   source selection, and snapshot artifacts remain unchanged.

This is private evidence preparation, not the final WP-5.2B1 portable package
schema. Do not add product code that depends on this precursor format.

## Rework 2: Remove The Private Snapshot Hash From The Tracked Report

The tracked completion report includes the exact frozen private database SHA-256.
The handoff explicitly permits artifact/model hashes in the tracked report, but it
does not require publishing the private corpus fingerprint.

Required correction:

1. Remove the exact frozen database SHA-256 from
   `md/handoffs/reports/WP-5.2A1-completion-report.md`.
2. State instead that the recomputed hash matched the accepted private
   WP-5.1.2A manifest.
3. Keep the model GGUF hash; it is public artifact provenance and was explicitly
   permitted.
4. Do not add live database hashes, selection hashes, case IDs, private paths, or
   other private corpus fingerprints to tracked files.

## Required Revalidation

After the metadata-only rework:

```powershell
poetry env info --path
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
poetry run chronicle --ai-task list
git diff --check
git status --short
git ls-files ".chronicle/*" "*.db" "*.sqlite" "*.zip"
```

Also validate privately that:

- the candidate manifest and summary parse successfully;
- all smoke stages have distinct run identities and relative artifact references;
- stored-attempt versus validated-result state is unambiguous;
- boundary states are tri-state and internally consistent;
- the frozen and live database hashes still match their private preflight values;
- existing model-output/log/reference bytes are unchanged;
- no model call occurred during rework.

## Completion Report Update

Refresh:

```text
md/handoffs/reports/WP-5.2A1-completion-report.md
```

Add a rework section covering:

- the evidence-field correction;
- run-identity/artifact-pointer correction;
- tracked-report privacy correction;
- proof that no model call or prompt/contract change occurred;
- proof that existing private model evidence remained unchanged;
- fresh validation results.

Return status to `Ready for PM validation` only after both rework items pass.

## Delivery Rules

- Do not stage or commit anything.
- Do not edit the development ledger.
- Preserve PM-owned `md/master-plan.md` and handoff changes.
- Leave all rework unstaged for repeat PM validation.
- Return a concise message pointing to the refreshed completion report.

## Acceptance Addendum

The executor completed both required corrections:

- failed task records now distinguish a persisted attempt row from the absence of
  validated result JSON;
- all validation boundaries use `pass`, `fail`, `not_evaluated`, or
  `not_applicable`;
- skipped downstream checks are no longer represented as failures;
- direct, synthetic, and private-development smokes have distinct stable run IDs
  and distinct relative artifact references;
- the tracked report no longer contains the frozen private database fingerprint;
- existing private model evidence remained unchanged and no model call occurred.

PM revalidation independently confirmed:

- the corrected private summary and candidate manifest parse and agree;
- the synthetic database contains the persisted failed title-assessment attempt;
- the installed GGUF SHA-256 matches the pinned public artifact hash;
- fresh live and frozen database fingerprints match their private preflight
  records;
- the candidate area remains ignored and no database/archive is tracked;
- the documented LM Studio command options exist;
- the full test suite passes with 373 tests;
- Ruff, CLI help, AI-task discovery, privacy tracking, and `git diff --check`
  pass.

WP-5.2A1 is accepted. The three schema-valid results and one title-assessment
schema failure remain baseline evaluation-floor evidence, not a semantic-quality
claim.
