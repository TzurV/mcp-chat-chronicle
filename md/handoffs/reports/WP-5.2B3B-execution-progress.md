# WP-5.2B3B Execution Progress

## Current status

**The generic prompt-catalog patch is implemented and fully validated. Execution is stopped for
manager patch validation and commit before any private candidate generation or provider/judge
call. The accepted split, P0 reconstruction, P1/P2 prompt bytes, and Qwen synthetic gates remain
unchanged.**

Last updated: 2026-08-03

## Gate 1 acceptance and resume

- Manager validation: accepted with no blocking findings.
- Gate 1 commit: `b15bf9632a344c0cac3b42a68142a6829c973b47`.
- Resume branch: `codex/wp-5.2b3b-prompt-development`.
- Resume checkout: clean before Gate 2 work.
- No prompt or model/provider call occurred before the committed checkpoint.

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

This section records the historical pre-commit checkpoint status. The manager subsequently
accepted and committed Gate 1 at the commit recorded above.

## Gate 2 metadata-only split freeze

The split was created only from the accepted 30-row selection metadata authority. The process did
not open raw conversation inputs, FABLE references or labels, candidate outputs, per-case failure
evidence, or judge results.

Algorithm `wp-5.2b3b-split-v1`:

1. require the exact accepted provider totals and three 10-conversation length strata;
2. reject duplicate source-content identities;
3. define early/middle/late date bins as chronological rank terciles over the accepted metadata;
4. enumerate every combination satisfying provider quotas;
5. retain combinations satisfying the exact 4/3/3 short/medium/long quotas;
6. maximize distinct date-bin coverage;
7. break remaining ties with the smallest deterministic selection hash derived from the fixed
   public seed `wp-5.2b3b-split-v1` and frozen source-content identities;
8. preserve accepted frozen order in both resulting manifests.

The search found 137,304 provider-and-length-feasible combinations and achieved all three date
bins. Aggregate frozen result:

| Scope | Conversations | Task cases | ChatGPT | OpenAI Codex | Claude | Claude Code | Short | Medium | Long |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Development | 10 | 40 | 3 | 3 | 2 | 2 | 4 | 3 | 3 |
| Holdout | 20 | 80 | 7 | 7 | 3 | 3 | 6 | 7 | 7 |

Development date-bin counts are early 2, middle 4, and late 4. Development and holdout have zero
overlap and partition all 30 accepted authority positions. Both private manifests passed strict
schema, self-hash, checksum, role, order, count, aggregate, complement, and source-authority
validation.

At the split freeze timestamp:

- raw input files opened: 0;
- reference/FABLE files opened: 0;
- candidate or judge result files opened: 0;
- prompt or model/provider calls: 0;
- post-split prompt/model run directories: 0.

The private manifests and provenance are frozen under the dedicated ignored B3B split root. No
private conversation identity, source hash, manifest hash, date, title, URL, or path is included
in this tracked progress note.

## Privacy and experiment boundary

- No holdout conversation content, references, historical outputs, labels, or per-case outcomes
  have been inspected.
- No external provider call has been made.
- Nothing has been staged or committed.

## P0 development-subset reconstruction

The accepted 8K P0 candidate packages and fixed-Pro judge evidence were reused without mutation or
regeneration. Reconstruction opened only the accepted attempt records required for the 40 selected
development cases. It did not open holdout cases, raw conversation inputs, FABLE references,
combined case-score files, or unselected attempt records, and it made no model/provider call.

Aggregate P0 candidate accounting:

| Model | Valid | Total | Conversation summary | Work mode | Last activity | Title assessment | Terminal failure categories |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen3.5-4B 8K | 30 | 40 | 6 | 7 | 10 | 7 | context 6; schema 1; timeout 3 |
| Phi-4 Mini 8K | 32 | 40 | 7 | 8 | 10 | 7 | context 6; schema 2 |
| Gemini 3.5 Flash 8K | 38 | 40 | 8 | 10 | 10 | 10 | invalid JSON 1; schema 1 |

Fixed-judge reuse accounting was 30 completed and 10 skipped-invalid for Qwen, 32 completed and 8
skipped-invalid for Phi, and 37 completed, 1 terminal judge failure, and 2 skipped-invalid for
Gemini. A private validator reconciled selected source-attempt identities, scope, hashes, and all
candidate/judge totals. The ignored P0 reuse artifacts are frozen separately from every accepted
package.

## P1/P2 prompt authoring

- P1 is one global four-task schema-first package with concise contracts, exact enum and field
  rules, cross-field dependencies, evidence constraints, and no chain-of-thought request.
- P2 starts from P1 and adds at most two short, obviously fictional final-JSON examples per task,
  including boundary, unknown, or null behavior where relevant.
- The same complete package will be used unchanged for Qwen, Phi, and Gemini; model-specific and
  task-level cherry-picking remain prohibited.
- Prompt authorship used the executing OpenAI Codex agent, public task contracts, application
  schemas, handoff rules, and aggregate P0 failure categories only. It used no auxiliary model,
  private conversation text, private identifier, reference, candidate response, or judge rationale.
- P3 remains absent and may be written only if the predeclared aggregate shared-local-failure
  trigger is met after P1/P2 local runs.

The catalogs passed application loading, task-order, exact non-prompt invariant, fictional-example
JSON, example-count, and privacy-marker validation. P2's examples use synthetic message IDs and
explicitly fictional future timestamps.

Pre-call prompt size comparison across all four normalized system/user prompt pairs:

| Package | Characters | UTF-8 bytes | Estimated tokens |
| --- | ---: | ---: | ---: |
| P0 | 3,109 | 3,109 | 658 |
| P1 | 4,202 | 4,202 | 870 |
| P2 | 6,849 | 6,849 | 1,516 |

Estimated tokens use `tiktoken` 0.13.0 `cl100k_base` over normalized prompt text and are explicitly
an estimator, not provider-native observed usage. P1 adds 1,093 characters and 212 estimated tokens
over P0; P2 adds 3,740 characters and 858 estimated tokens over P0.

The ignored private pre-call freeze binds both complete catalogs, normalized text and UTF-8 hashes,
catalog hashes, per-task and aggregate counts, exact non-prompt task specs, schema/finalizer
identities, implementation hashes, split identities, accepted P0 source identities, hypotheses,
invariants, selection rule, P3 trigger, call budget, authorship declaration, and the Gate 1
application commit. An independent validator confirmed its checksum and live-file equality.

At freeze time, P1/P2/P3 candidate run directories did not exist, model/provider calls remained
zero, and holdout raw/reference/outcome files opened remained zero. Prompt text is now immutable for
the experiment; any change requires stopping for manager review.

## Gate 4 local preflight and synthetic gates

- LM Studio server: running on the accepted loopback port.
- Accepted Qwen and Phi GGUF files: byte sizes and SHA-256 identities match their accepted P0
  artifacts exactly.
- Qwen loaded identity: `qwen3.5-4b`, context 8,192, parallelism one, Q4_K_M, idle after load.
- The LM Studio index reports a stale Qwen size value, but direct file size and SHA-256 validation
  match the accepted artifact; the benchmark's independent pre-call artifact validator remains the
  authority for private generation.
- Qwen P1 synthetic strict-schema gate: 4/4 valid, zero retries.
- Qwen P2 synthetic strict-schema gate: 4/4 valid, zero retries.
- Synthetic gate calls used only a fictional greenhouse-sensor conversation and synthetic message
  IDs/timestamps. No private development or holdout content was disclosed by these calls.

## Manager checkpoint: prompt-catalog preparation blocker

Both Qwen bundle preparations failed deterministically before candidate generation with:

```text
Error: accepted input task catalog hash mismatch
```

The first preparation attempt also exposed and safely corrected a private configuration mistake:
top-level evaluation counts describe the complete accepted 30-conversation/120-case authority,
while the nested ordered manifest describes the selected 10-conversation/40-case development
scope. That correction changed only ignored evaluation configuration and left no partial bundle.

The remaining blocker is in the accepted Gate 1 harness behavior. `prepare_cases` hashes the active
task-catalog file and requires it to equal every accepted input envelope's
`task_catalog_hash_reference`. Those envelopes correctly bind the exact P0 catalog, so any P1/P2
catalog is rejected even when prompts are the only changed fields and all task versions, schemas,
selectors, finalizers, generation settings, limits, and dependencies are identical. The current
harness has no separately bound prompt-package override or semantic-contract identity.

Resolving this requires a generic benchmark design change, such as separating the immutable
non-prompt task-contract identity from the experimental prompt-package identity while retaining
strict cross-stage prompt hashes. The authoritative handoff says that a genuine generic harness
defect found after Gate 1 must be preserved and returned for manager review; it must not be silently
patched after the manager commit. Execution therefore stopped before any private candidate call.

Current boundary at the stop:

- private candidate positions generated: 0;
- Qwen synthetic-only gate positions: 8, all valid;
- Phi and Gemini synthetic/candidate positions: 0;
- P1/P2 bundles, generation work, and candidate packages: absent;
- fixed-judge calls: 0;
- holdout raw inputs, references, historical outputs, labels, and per-case outcomes opened: 0;
- P1/P2 prompt text after freeze: unchanged;
- application code after Gate 1: unchanged;
- nothing staged or committed.

## Prompt-catalog blocker patch

Manager review confirmed the blocker above as a genuine generic harness defect. The narrow patch
now separates two identities:

1. the immutable authority task catalog used by accepted input envelopes and FABLE references;
2. the active experimental task catalog used to construct P1/P2 requests.

An experiment must explicitly pin the exact SHA-256 of both catalog files and declare the
`prompts-only` policy. Both files pass the existing strict task-catalog parser. Their task names
and order must match, and every non-prompt field must be structurally identical. Only
`system_prompt` and `user_prompt` may differ. Changes to task versions, enabled states,
descriptions, model profiles, selectors, schemas, generation settings, dependencies, input
limits, or recent-message counts are rejected.

The portable experimental provenance contains no catalog path. It binds the authority catalog
hash, active catalog hash, policy/version, unchanged non-prompt contract hash, and each task's
active system- and user-prompt hashes through:

- preparation and bundle content identity;
- generation-work identity;
- candidate-package identity and local verification;
- deterministic metrics and scoring run identity;
- fixed-judge cache, metrics, run identity, and accounting.

Every stage that uses a local configuration re-reads and validates the configured catalog bytes.
Catalog mutation, configured-hash mismatch, package provenance tampering, or scoring/judge reuse
under a different identity is rejected. Accepted inputs and references continue to validate
against the immutable authority hash; they were not rewritten.

When the authority declaration is absent, the original single-catalog behavior remains in force.
The new fields are omitted rather than serialized as null values, preserving historical bundle,
package, verification, scoring, and judge identities.

## Prompt-catalog patch validation

- Focused ordered-manifest and prompt-catalog matrix: 20 passed.
- Full repository suite: 474 passed, 1 skipped.
- Repository-wide Ruff: passed.
- Poetry metadata check: passed.
- Poetry environment: repository `.venv` confirmed.
- Bench root/prepare/generate/verify/score help: passed.
- Chronicle root help and AI-task listing: passed.
- Historical serialization compatibility test: passed.
- Prompt-only end-to-end prepare/generate/package/verify/score/judge test: passed with injected
  synthetic clients only.
- Ten non-prompt mutation classes, incorrect file hashes, post-generation catalog mutation, and
  package-identity tampering: rejected as required.
- `git diff --check`: passed before this progress-note update and will be rerun at handoff.
- Private artifact tracking check: no tracked `.chronicle`, database, SQLite, ZIP, or export
  artifact reported.

The final private checkpoint audit passed and confirmed:

- P0, P1, and P2 catalog bytes and the frozen hypotheses declaration are unchanged;
- the prompt-freeze artifact and both split manifests are unchanged;
- accepted P0 source packages, reconstruction artifacts, and judge evidence are unchanged;
- P1/P2 private candidate bundles, generation-work directories, packages, and scoring outputs
  remain absent;
- P3 remains absent;
- private candidate positions generated remain zero.

No private conversation was supplied to a model. No Gemini, fixed-judge, or other external
provider call occurred during this patch. The only model-shaped test calls used injected synthetic
clients; the previously accepted Qwen fictional gates were not rerun or changed. No command in
this patch targeted database state or WP-5.2C1 artifacts.

Patch delivery files:

- `bench/config.py`
- `bench/core.py`
- `bench/evaluation.default.yaml`
- `bench/judge.py`
- `bench/models.py`
- `docs/development-evaluation.md`
- `tests/test_bench.py`
- `md/handoffs/reports/WP-5.2B3B-execution-progress.md`

Pre-existing manager/accepted worktree entries preserved without patch edits:

- `md/development-ledger.md`
- `md/handoffs/reports/WP-5.2B3B-prompt-catalog-blocker-review.md`
- `bench/prompts/wp-5.2b3b/`

## Manager patch-validation stop

The patch is ready for manager validation and commit. All delivery changes are intentionally
unstaged and uncommitted. Do not amend the existing split/prompt freeze, rerun fictional gates, or
resume private generation until the manager commit exists.
