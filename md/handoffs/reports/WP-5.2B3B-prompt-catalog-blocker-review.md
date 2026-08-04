# WP-5.2B3B Prompt-Catalog Blocker Review

## Decision

**The stop is valid. A narrow generic benchmark patch is required before
private candidate generation.**

The manager accepts the completed metadata-only split freeze, P0 subset
reconstruction, P1/P2 prompt freeze, and Qwen synthetic-gate evidence as
checkpoint progress. This is not final B3B acceptance.

No private candidate bundle, candidate generation, Gemini candidate call, or
fixed-judge call may begin until the patch below passes manager validation and
is committed on `codex/wp-5.2b3b-prompt-development`.

## Confirmed Root Cause

Accepted input envelopes and FABLE references correctly bind the exact P0 task
catalog hash. The current benchmark also treats the active generation catalog
as that same authority. Consequently, replacing only prompt text with P1 or P2
changes the active catalog file hash and fails preparation with:

```text
accepted input task catalog hash mismatch
```

Rewriting frozen input envelopes or references to contain P1/P2 hashes is not
permitted. It would alter accepted authority data and invalidate comparison
provenance.

The benchmark must distinguish:

1. **authority task catalog:** immutable P0 catalog that created the accepted
   inputs and references;
2. **active prompt catalog:** P0, P1, P2, or conditional P3 catalog used to
   construct candidate requests.

## Independent Prompt Validation

The manager loaded P0, P1, and P2 through the application task-catalog parser
and confirmed:

- all contain the same four tasks in the same order;
- every non-prompt task field is exactly equal to P0 for P1;
- every non-prompt task field is exactly equal to P0 for P2;
- all three complete prompt packages are distinct;
- tracked prompt files contain no private path, conversation identity,
  credential, source hash, raw content, FABLE reference, candidate result, or
  judge rationale.

P1/P2 prompt text remains frozen. Do not edit it during this patch.

## Required Generic Design

Add an optional strict task-catalog experiment declaration to evaluation
configuration. The executor may choose names that fit existing repository
conventions, but the contract must provide the equivalent of:

```yaml
task_catalog: <active-prompt-catalog>
task_catalog_authority:
  path: <accepted-p0-catalog>
  sha256: <accepted-p0-file-sha256>
  active_sha256: <active-catalog-file-sha256>
  allowed_changes: prompts-only
```

When the declaration is absent, preserve historical behavior byte-for-byte:
the active task catalog remains the accepted authority catalog and accepted
input references must equal its exact file hash.

When `allowed_changes: prompts-only` is configured, require all of the
following before bundle creation:

1. authority and active files exist and parse through the accepted strict task
   catalog loader;
2. configured authority and active SHA-256 values match exact file bytes;
3. accepted selected input envelopes bind the authority catalog hash;
4. accepted references continue to bind the authority catalog hash;
5. task names and order are identical;
6. task versions are identical;
7. enabled state, descriptions, model profiles, selectors, output schemas,
   generation settings, dependencies, input limits, and recent-message counts
   are exactly identical;
8. only `system_prompt` and/or `user_prompt` text may differ;
9. every prompt still passes allowed-placeholder validation;
10. active prompt text and catalog bytes are bound into candidate case,
    bundle, package, verification, scoring, and judge identities;
11. authority catalog identity is separately bound through the same stages;
12. no private filesystem path is placed in a portable artifact.

Do not weaken the existing case fingerprint. It already binds task and
interpolated prompt identities; preserve those fields and add explicit catalog
authority/active identities where needed for portable provenance and clear
verification errors.

## Portable Provenance Requirements

Bundle, generation-work, candidate-package, verification, deterministic-score,
and judge scope must make it possible to establish, without private paths:

- authority catalog hash;
- active prompt catalog hash;
- prompt-only override policy/version;
- exact per-task active prompt identity;
- unchanged non-prompt contract identity;
- application commit;
- selected conversation scope identity.

Tampering with either catalog, its configured hash, the allowed-change policy,
or package identities must fail before candidate use or scoring.

Historical packages and configurations without the new declaration must retain
their existing serialization and verification behavior.

## Focused Test Matrix

Add synthetic tests proving:

1. P0 authority plus prompt-only active catalog prepares, generates, verifies,
   scores, and reaches judge accounting;
2. selected input and reference envelopes remain bound to P0 authority;
3. system-prompt-only and user-prompt-only changes are accepted;
4. task version change is rejected;
5. selector change is rejected;
6. schema change is rejected;
7. generation change is rejected;
8. model-profile change is rejected;
9. input-limit or recent-message-count change is rejected;
10. enabled/dependency/description change is rejected;
11. wrong authority file hash is rejected;
12. wrong active file hash is rejected;
13. active catalog modification after bundle preparation is rejected during
    later local verification;
14. portable manifests contain identities but no catalog paths;
15. ordered-manifest execution still opens only selected inputs/references;
16. full-corpus and prefix workflows remain unchanged;
17. historical package serialization and verification remain compatible;
18. P1 and P2 produce distinct active prompt/package identities while sharing
    the same authority and non-prompt contract identities.

Update `bench/evaluation.default.yaml` and
`docs/development-evaluation.md` with a generic, privacy-safe example and
explanation.

## Experiment Preservation

The following accepted checkpoint artifacts must remain byte-stable:

- development and holdout split manifests;
- split provenance and hashes;
- P0 subset reconstruction;
- P1 catalog;
- P2 catalog;
- prompt hypotheses;
- prompt text and hashes;
- pre-call freeze evidence;
- accepted historical packages;
- frozen and live databases;
- WP-5.2C1 artifacts.

The original pre-call freeze must not be overwritten. After the patch commit,
append a private provenance amendment that records:

- the new clean application commit;
- the accepted prompt-catalog authority/active policy version;
- unchanged P1/P2 prompt hashes;
- unchanged split identities;
- the reason for the application-identity update;
- confirmation that no private candidate generation occurred before it.

Candidate packages must use the new clean patch commit and the amended frozen
provenance.

## Synthetic Gates After Patch

After the manager commits the patch and the tracked checkout is clean:

1. revalidate the frozen split and prompt hashes;
2. re-run the Qwen P1/P2 fictional four-task gates under the new application
   commit;
3. require 4/4 for each;
4. preserve the earlier synthetic evidence as historical rather than
   overwriting it;
5. only then prepare the first private 40-case bundle.

These local fictional reruns do not change the private-data disclosure budget.

## Mandatory Manager Checkpoint

The executor must now:

1. implement only this generic patch;
2. add focused tests and generic documentation;
3. run focused tests, full tests, Ruff, Poetry, CLI help, privacy checks, and
   `git diff --check`;
4. append the patch evidence and exact file list to
   `md/handoffs/reports/WP-5.2B3B-execution-progress.md`;
5. leave all changes unstaged and uncommitted;
6. stop again before private bundle preparation or model/provider calls.

The manager will review and commit the patch. Do not ask the owner to run Git
commands. Do not continue from a dirty tracked implementation.

## Stop Rules

Stop and report if:

- prompt-only equivalence cannot be enforced structurally;
- the fix would require rewriting accepted inputs or references;
- any P1/P2 prompt byte changes;
- any non-prompt task setting changes;
- historical package behavior changes;
- a private input/reference must be opened to test the generic patch;
- a provider call or private candidate generation would occur before commit;
- the patch expands into production AI-task behavior.

## Required Return Message

Return:

- status: ready for manager patch validation, partial, or blocked;
- root-cause confirmation;
- authority/active catalog design summary;
- focused and full test totals;
- backward-compatibility result;
- P1/P2 prompt hash immutability confirmation;
- split/P0/database/historical-package/WP-5.2C1 immutability confirmation;
- exact changed files;
- final `git status --short`;
- confirmation that nothing was staged or committed;
- confirmation that no private candidate or external provider call occurred.
