# WP-5.1.2B Completion Report: Direct FABLE Development References

## Status

Ready for PM validation

## 1. Executive Summary

WP-5.1.2B is complete. Using the accepted frozen WP-5.1.2A snapshot, a
deterministic development set of exactly 30 conversations was selected and
frozen before any content inspection, exactly 30 task-input files were created
with the accepted production selectors, and FABLE directly created all 120
expected reference records (4 tasks x 30 cases) in the execution chat. All 120
references are successes; there are no failure records. All references passed
mechanical structural, evidence-membership, and date validation. All private
artifacts remain ignored and untracked. This report is the only tracked
delivery file.

## 2. FABLE Directly Created The References

Confirmed. Every semantic judgment in all 120 reference records was produced
directly by FABLE inside this execution chat. No semantic labeling was
delegated to another model, a local model, a remote API, a sub-agent, or a
programmatic classifier. Mechanical helpers performed only hashing, SQL reads,
selector invocation, JSON validation, counting, and progress bookkeeping, and
never generated, corrected, or normalized reference content. Every validation
failure (four word-limit overruns during the summary pass) was fixed by FABLE
rewriting the reference from the same frozen input.

## 3. FABLE Model Identity

The execution environment reports the model name `Fable 5` with exact model ID
`claude-fable-5`, running in Anthropic Claude Code (VSCode extension / Claude
Agent SDK harness). No more specific version string was exposed. No
credentials are recorded. The run manifest records the interface, the
execution-session identifier, and the note that judgments were produced in the
chat itself with no API call.

## 4. No Teacher-Generation Or Reconciliation Code Added

Confirmed. No application source, tests, schemas, task YAML, benchmark runner,
LiteLLM call, or teacher-generation/reconciliation/corpus-generation product
code was added or modified. All helpers are disposable private scripts under
the ignored `tmp/` directory of the private corpus root (listed in section 27).

## 5. No Second Teacher Or Additional Model API

Confirmed. No second teacher, no Gemini judge, no GPT, no local model, and no
additional model API of any kind was used. `chronicle --ai-task` was not run;
`ai_task_results` was not written; neither the live nor the frozen database was
modified or migrated; no ingest or collect ran.

## 6. Snapshot Preflight Result

All snapshot preflight checks passed: the private manifest parsed as JSON with
`corpus_version = dev-v1`, `freeze_status = frozen`, and the recorded work
package WP-5.1.2A; the recomputed SHA-256 of the frozen database equaled both
recorded destination hashes; no `-wal` or `-shm` sidecar existed; the snapshot
opened read-only with URI `mode=ro` and `immutable=1` under
`PRAGMA query_only=ON`; integrity check returned `ok`; and a write attempt was
rejected with a read-only database error. Paths and hash values are recorded
privately, not here.

## 7. Snapshot Schema And Aggregate Counts

Schema version (SQLite `user_version`) is 3. Aggregate counts match the
accepted values: 711 conversations and 28,370 messages. These were verified at
preflight, at every five-case checkpoint, and again in final validation.

## 8. Selection Algorithm Version And Freeze Result

Selection algorithm version: `wp512b-selection-v1`. Selection ran strictly
before any title or body inspection, using only mechanical eligibility,
deduplication, per-provider NTILE(3) length stratification by meaningful
characters, and deterministic date-spread positions. The ordered selection was
serialized canonically (UTF-8 JSON, sorted keys, no insignificant whitespace),
hashed, and frozen with `selection_status: "frozen"` before labeling. No
conversation was substituted, reordered, or re-stratified afterward.

## 9. Provider Distribution

Achieved exactly as required: 10 chatgpt, 10 openai_codex, 5 claude,
5 claude_code (total 30).

## 10. Length-Stratum Aggregate Distribution

Achieved exactly as required. Per provider with quota 10: 3 short, 4 medium,
3 long. Per provider with quota 5: 2 short, 1 medium, 2 long. Aggregate across
all providers: 10 short, 10 medium, 10 long.

## 11. Date-Coverage Method

Within each provider/length stratum, candidates were ordered by accepted
last-activity date ascending, then conversation ID ascending, and rows were
picked at the handoff's deterministic zero-based positions (midpoint for one
row; endpoints for two; endpoints plus midpoint for three; endpoints plus
thirds for four), with the duplicate-position fallback rule. No dates or IDs
are disclosed here.

## 12. Deduplication Aggregate Count

The eligible pool was deduplicated by exact `content_hash`. Zero duplicate
groups were found; zero rows were removed. No provider quota was affected.

## 13. Input File Count

Exactly 30 input files exist (one per case group), each containing the frozen
`conversation-overview-v1` and `recent-meaningful-v1` selector outputs from the
accepted `chat_chronicle.ai.select_input` implementation, with selection
metadata, exact selected message IDs, canonical input hashes, and
application-owned dates. Post-write validation confirmed unique selected IDs,
membership in the frozen conversation, and rendered-header/ID agreement for
all 30 files. No input file was altered after any reference was created from
it.

## 14. Case Counts By Task

| Task | Expected | Successful | Failed |
| --- | ---: | ---: | ---: |
| conversation-summary | 30 | 30 | 0 |
| work-mode-classification | 30 | 30 | 0 |
| last-activity | 30 | 30 | 0 |
| title-assessment | 30 | 30 | 0 |
| **Total** | **120** | **120** | **0** |

Every case group c001-c030 is accounted for in every task with no duplicate
case IDs.

## 15. Work-Mode Aggregate Label Distribution

executor 14, one_off 12, manager 3, mixed 1, unknown 0.

## 16. Last-Activity Aggregate Status Distribution

completed 16, awaiting_input 7, in_progress 7, blocked 0, unknown 0.

## 17. Title-Fit Aggregate Distribution

title_fits true: 19; title_fits false: 11 (each false record carries a
non-empty suggested title within the 3-10 word / 80 character limits).

## 18. Aggregate Confidence Statistics

- work-mode-classification: n=30, mean 0.798, median 0.80, min 0.60, max 0.95.
- title-assessment: n=30, mean 0.810, median 0.875, min 0.60, max 0.95.

Confidences are uncalibrated teacher self-assessments per the handoff bands.

## 19. Evidence-Membership Validation Count

All 120 successful records passed evidence validation: every evidence ID is an
integer, unique within its record, a member of the exact task-selected input ID
list, in chronological (selected-input) order, and within the per-task count
limits. Validation ran once at write time for each record and again over all
120 records in final validation.

## 20. Deterministic Summary-Date Validation Count

All 30 conversation-summary records passed exact string equality checks of
`start_date` and `last_active_date` against the frozen input files (30 of 30,
verified twice).

## 21. JSON/Schema Validation Result

All 120 records parse as JSON, contain the exact required envelope fields, and
their outputs contain exactly the canonical task fields with no extras. Types,
enumerated labels, confidence bounds, word/sentence/list/character limits, and
task-specific null-consistency rules (last-activity action/basis and title
fit/suggestion) all validate. Final validation result: PASS with zero
problems.

## 22. Snapshot And Selection Hash Re-Verification

Both re-verified successfully in final validation (and the snapshot hash at
every five-case checkpoint): the frozen database hash still equals the
WP-5.1.2A accepted value, and the recomputed canonical selection hash equals
the frozen selection hash. Hash values are recorded privately, not here.

## 23. Private Artifact Ignore/Tracking Evidence

`git check-ignore -v` confirms the selection file, input files, reference
files, and run manifest are all ignored (by the `.chronicle/` rule).
`git ls-files .chronicle` returns nothing. `git status --short` shows no
selection, input, reference, run, report, helper, DB, manifest, sidecar, or
transcript artifact. `git add -f` was not used and nothing is staged.

## 24. Live And Frozen DBs Not Modified

Confirmed. The frozen snapshot was opened only read-only/immutable with
`query_only=ON`; its SHA-256 was identical before, during (every checkpoint),
and after the run. The live product database was never opened by this work
package. No migration, ingest, or collect ran.

## 25. No Human Semantic Adjudication

Confirmed. No human reviewed, edited, adjudicated, or relabeled any reference
content. The owner's no-human-review decision is recorded in the run manifest.

## 26. Limitations And Explicit Failures

- Zero failure records: all 120 cases succeeded.
- These are silver development references from a single teacher (FABLE) with
  no reconciliation; they carry that model's judgment biases, and confidence
  values are uncalibrated.
- Four conversation-summary drafts initially exceeded the 120-word limit and
  one exceeded it twice; each was rewritten by FABLE from the same frozen
  input until valid. No semantic auto-correction occurred.
- One transient Windows file-lock error interrupted a progress-file update;
  the progress updater was made idempotent (counts recomputed from reference
  files) and the update re-ran. No reference content was affected.
- Selected inputs for long conversations are truncated by the accepted
  selectors; references describe only the selected input by design.
- Independently produced task outputs were not reconciled; mechanical
  validation surfaced no cross-task condition requiring a private note.

## 27. Temporary Private Helpers

All helpers live under the ignored private `tmp/` directory of the corpus
root and are retained for PM inspection (none are tracked):

- `preflight_snapshot.py` (snapshot checks) - retained
- `select_conversations.py` (deterministic selection) - retained
- `freeze_inputs.py` (selector invocation and input freeze) - retained
- `show_case.py` (renders one case input at a time) - retained
- `write_reference.py` (envelope wrap + mechanical validation + progress) - retained
- `checkpoint.py` (five-case batch checks) - retained
- `final_validation.py` (final private validation and summaries) - retained
- `current-case.txt`, `pending_output.json` (working files) - retained
- `make_snapshot.py` (pre-existing WP-5.1.2A helper) - untouched

During execution, two temporary permission allow-rules for running these
`tmp/` helpers were added to the git-ignored local Claude settings file at the
owner's request. Both wildcard rules were removed during PM rework (see the
Rework Addendum); the settings file retains only its pre-existing entries and
remains ignored, untracked, and valid JSON.

## 28. Exact Tracked Files Changed

- `md/handoffs/reports/WP-5.1.2B-completion-report.md` (this report; new)

No other tracked file was created or modified by this work package. The
pre-existing modifications to `md/development-ledger.md` and
`md/master-plan.md` and the untracked handoff file are PM-owned state from
before execution and were preserved untouched.

## 29. Final `git status --short` Summary

```text
 M md/development-ledger.md
 M md/master-plan.md
?? md/handoffs/WP-5.1.2B-direct-fable-development-references.md
?? md/handoffs/reports/WP-5.1.2B-completion-report.md
```

(The last line appears once this report file exists.) Nothing is staged;
`git diff --check` passes.

## 30. Acceptance-Criteria Checklist

| # | Criterion | Status |
| ---: | --- | --- |
| 1 | Poetry resolves to repository `.venv` | pass |
| 2 | Snapshot hash/integrity/schema/counts/read-only/no-sidecar reverified | pass |
| 3 | Root and packaged task catalogs byte-identical and pinned | pass |
| 4 | Selection before title/body inspection | pass |
| 5 | Eligibility and exact-content deduplication followed | pass |
| 6 | Exactly 30 conversations selected | pass |
| 7 | Provider quotas 10/10/5/5 | pass |
| 8 | Required short/medium/long allocations achieved | pass |
| 9 | Deterministic date-spread positions used | pass |
| 10 | Selection frozen and privately hashed before labeling | pass |
| 11 | No frozen conversation substituted after inspection | pass |
| 12 | Exactly 30 task-input files | pass |
| 13 | Inputs use accepted selector behavior | pass |
| 14 | Each reference uses only its exact selected input | pass |
| 15 | FABLE directly created all semantic references | pass |
| 16 | Exactly 120 expected reference records | pass |
| 17 | Every case is success or explicit failure | pass (120 success) |
| 18 | Exact canonical schema, no extra fields | pass |
| 19 | Evidence unique, chronological, within selected input | pass |
| 20 | Summary dates exactly match input dates | pass |
| 21 | Work-mode labels within approved taxonomy | pass |
| 22 | Last-activity status/action/null consistency | pass |
| 23 | Title fit/suggestion consistency | pass |
| 24 | No task used another task's output as evidence | pass |
| 25 | No chain-of-thought requested or stored | pass |
| 26 | No human semantic review | pass |
| 27 | No second teacher or additional model API | pass |
| 28 | No teacher-generation/reconciliation/benchmark code added | pass |
| 29 | Live and frozen DBs unchanged | pass |
| 30 | Snapshot, selection, and task-catalog hashes still match | pass |
| 31 | All private artifacts ignored and untracked | pass |
| 32 | No private case data in tracked files | pass |
| 33 | Report at the mandatory path | pass (this file) |
| 34 | `git diff --check` passes | pass |
| 35 | Tracked delivery changes unstaged and uncommitted | pass |

## 31. Data Classification Statement

These references are private silver development references produced by a
single teacher for development and prompt/model calibration only. They are not
ground truth, not a holdout, and not sufficient for final or
publication-grade model-quality claims.

## 32. Downstream Work Not Started

WP-5.2A (local model/runtime selection and integration), WP-5.2B
(deterministic evaluation plus a different Gemini judge through LiteLLM/YAML),
and WP-5.2C (remote execution and the separate untouched evaluation set) have
not been started. The master plan and development ledger were not modified.

## 33. Rework Addendum (PM Validation Review)

Both corrections from the WP-5.1.2B validation review were applied:

1. **Broad permission rules removed.** The two exact wildcard allow-rules that
   permitted any Python file under the private ignored `tmp/` directory to run
   without prompting were removed from the git-ignored local Claude settings
   file. All pre-existing, unrelated permission entries were preserved
   unchanged. The file parses as valid JSON, contains no rule referencing the
   private corpus directory, and remains ignored and untracked.

2. **Run completion provenance corrected.** The private run manifest's
   `completed_at_utc`, which had been recorded as a future-dated estimate, was
   replaced with the accurate UTC completion time equal to the original
   final-validation event. The corrected value is no earlier than the latest
   completed reference, not in the future, and carries an explicit UTC offset;
   a provenance note in the manifest records the correction. The manifest
   reparses as valid JSON.

Post-rework verification:

- The private final mechanical validation was rerun and still reports PASS
  with zero problems: snapshot hash, integrity, and counts; selection hash;
  task-catalog pin; 120 reference files with all schemas, evidence membership,
  and deterministic dates unchanged; and per-task counts of 30/30 successes
  each.
- All 120 reference files are byte-for-byte identical before and after rework
  (per-file SHA-256 lists compared and equal; no reference was regenerated or
  edited, and no FABLE labeling reran).
- No model call was made during rework; no application code, test, dependency,
  task YAML, plan, or ledger file changed; no private artifact became tracked
  (`git ls-files .chronicle` remains empty); `git diff --check` passes; and
  nothing is staged or committed.
