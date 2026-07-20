# WP-5.1.2B PM Validation Review

## Decision

**Accepted after narrow rework.**

The frozen selection, inputs, 120 FABLE references, schemas, evidence linkage,
dates, distributions, privacy boundary, and completion report are mechanically
sound. No semantic adjudication was performed, consistent with the owner's
decision.

Two local operational/provenance issues must be corrected before acceptance.
Neither issue requires regenerating references or changing application code.

Both issues were subsequently corrected and independently revalidated by the
PM. The original findings remain below as the rework record.

## Evidence Reviewed

The PM reviewed:

- the WP-5.1.2B handoff;
- the tracked completion report;
- the private snapshot and selection manifests;
- the private run manifest, progress, and validation summary;
- the selection and input-freeze helpers;
- the reference writer/validator and checkpoint/final-validation helpers;
- the complete private artifact inventory;
- the local Claude permission settings;
- Git ignore, tracking, status, and whitespace evidence.

The PM independently validated all 120 successful outputs against the actual
product Pydantic final schemas:

| Task | Records | Pydantic failures |
| --- | ---: | ---: |
| `conversation-summary` | 30 | 0 |
| `work-mode-classification` | 30 | 0 |
| `last-activity` | 30 | 0 |
| `title-assessment` | 30 | 0 |
| **Total** | **120** | **0** |

Private paths, IDs, hashes, transcripts, titles, and reference outputs are
omitted from this tracked review.

## Confirmed Passing Areas

- Repository Poetry environment is correct.
- WP-5.1.2A snapshot hash, integrity, schema, counts, and read-only state pass.
- Selection was deterministic and frozen before semantic content inspection.
- Exactly 30 conversations were selected with the required 10/10/5/5 provider
  distribution.
- Required length and date-spread selection rules were implemented.
- Exactly 30 accepted-selector input files exist.
- Exactly 120 reference files exist and all report success.
- All 120 outputs pass product Pydantic final-schema validation.
- All evidence IDs are mechanically linked to task-selected inputs.
- All 30 summary date pairs match deterministic input dates.
- No model/network client exists in the private helpers.
- No application, test, dependency, task-catalog, or schema file changed.
- Private corpus artifacts and local Claude settings are ignored and untracked.
- `git ls-files .chronicle` returns no corpus artifact.
- `git diff --check` passes.

## Rework 1: Remove Broad Persistent Permission Rules

The executor added these two ignored local Claude allow-rules:

```text
PowerShell(poetry run python .chronicle/eval/dev-v1/tmp/*)
Bash(poetry run python .chronicle/eval/dev-v1/tmp/*)
```

These rules permit any future Python file placed in the ignored private `tmp/`
directory to execute without another permission prompt. That permission is
broader and longer-lived than the completed data-curation task.

Required correction:

1. Remove only the two exact wildcard rules above from
   `.claude/settings.local.json`.
2. Preserve all pre-existing permission entries.
3. Keep the settings file valid JSON.
4. Confirm the two wildcard rules are absent.
5. Confirm the settings file remains ignored and untracked.

Do not delete or rewrite unrelated local Claude settings.

## Rework 2: Correct Run Completion Provenance

The private run manifest records a `completed_at_utc` value later than both the
manifest file's actual UTC modification time and the PM validation time. The
recorded completion time is therefore not valid provenance.

Required correction:

1. Replace `completed_at_utc` with the accurate UTC completion time.
2. Require it to be:
   - no earlier than the latest completed reference;
   - no earlier than the original final-validation event when used as the
     run-completion boundary;
   - not in the future;
   - correctly marked with a UTC offset or `Z`.
3. Reparse the run manifest as JSON.
4. Rerun the private final mechanical validation after correcting provenance.
5. Confirm snapshot, selection, task-catalog, reference counts, schemas,
   evidence, and dates remain unchanged.

Do not alter any semantic reference output.

## Completion Report Refresh

Update `md/handoffs/reports/WP-5.1.2B-completion-report.md` with a short rework
addendum that records:

- the two broad permission rules were removed;
- unrelated local permission rules were preserved;
- the run completion timestamp was corrected to accurate UTC;
- private final validation was rerun and still passes;
- all 120 references remain byte-for-byte unchanged;
- no application code or private artifact was tracked.

Update section 27 so it no longer states that the two wildcard permission rules
remain installed.

Do not include the private timestamp, hashes, IDs, paths, or reference content
in the tracked report.

## Required Rework Validation

Provide privacy-safe evidence for:

1. valid `.claude/settings.local.json`;
2. absence of the two exact wildcard rules;
3. settings file ignored and untracked;
4. valid private run-manifest JSON;
5. corrected completion time is ordered correctly and not future-dated;
6. private final validation result remains `PASS`;
7. exactly 120 reference files remain;
8. reference-content hashes before and after rework match;
9. snapshot and selection hashes still match;
10. `git diff --check` passes;
11. nothing is staged or committed.

## Scope Boundary

Do not:

- regenerate or edit semantic references;
- rerun FABLE labeling;
- add model calls;
- change selection or input files;
- modify application code, tests, dependencies, task YAML, plan, or ledger;
- stage or commit.

Return the delivery as `Ready for PM validation` with the refreshed completion
report and final `git status --short`.

## Rework Validation And Final Acceptance

The PM independently confirmed:

- `.claude/settings.local.json` parses as valid JSON;
- exactly the four pre-existing permission entries remain;
- neither removed wildcard permission is present;
- no remaining permission references the private corpus `tmp/` directory;
- the settings file remains ignored and untracked;
- the run manifest parses as valid JSON;
- corrected `completed_at_utc` has an explicit UTC offset;
- corrected completion is no earlier than the latest reference;
- corrected completion is not future-dated;
- the refreshed private validation result is `PASS` with zero problems;
- exactly 120 reference files remain;
- the before/after reference-hash lists each contain 120 entries and are
  byte-identical;
- no semantic reference was regenerated or edited;
- snapshot, selection, schema, evidence, and deterministic-date checks remain
  unchanged;
- no model call occurred during rework;
- `git diff --check` passes;
- private artifacts remain ignored and untracked;
- nothing is staged or committed.

WP-5.1.2B is accepted as a private FABLE-generated silver development corpus:

- 30 frozen conversations;
- four tasks per conversation;
- 120/120 successful, product-schema-valid references;
- no human semantic adjudication;
- not ground truth and not a final evaluation set.

WP-5.2A/B/C remain unstarted. The next planning gate is owner approval of the
local model/runtime shortlist for WP-5.2A.
