# WP-5.2B1 Validation Review

## Decision

**Partial delivery acknowledged. Continuation required before the owner-controlled
private transfer gate.**

The current work establishes a useful skeleton for deterministic archives,
configuration strictness, atomic JSON writes, and command separation. It is not yet
safe or functionally compatible with the accepted WP-5.1.2B corpus, and it is not
ready for private one-case or remote execution.

The next executor pass must complete and test the offline implementation first. Do
not transfer private inputs, run the 120-case candidate batch, or call Gemini from
this partial implementation.

## PM Validation Performed

The PM independently confirmed:

- Poetry resolves to the repository `.venv`;
- the six current focused tests pass;
- Ruff passes;
- the current command surface exists;
- the accepted private input corpus consists of 30 files, each with separate
  `overview` and `recent` selector payloads;
- accepted references consist of four task directories x 30 files, with the
  structured reference under each file's `output` field;
- no private artifact was opened by the executor's implementation run;
- nothing is staged or committed.

The six focused tests currently cover only:

- config strictness/accounting;
- deterministic ZIP bytes across two roots;
- three unsafe archive-name examples;
- checksum tampering.

They do not execute `prepare`, `generate`, `verify`, `score`, resume, real-corpus
loading, local-authority verification, confusion-matrix reconciliation, or judge
behavior.

## Blocking Finding 1: The Harness Does Not Read The Accepted Corpus Format

Current preparation in `bench/core.py` expects one JSON list and reads shared
top-level `transcript` and `selected_message_ids` values for all tasks. The accepted
WP-5.1.2B corpus instead contains:

```text
.chronicle/eval/dev-v1/inputs/c001.json ... c030.json
```

Each input contains separate accepted selector records:

- `overview` for `conversation-summary`, `work-mode-classification`, and
  `title-assessment`;
- `recent` for `last-activity`.

Each selector record has its own:

- selector and selector version;
- canonical input hash;
- transcript;
- selected message IDs;
- selection metadata.

Current scoring expects one flat references JSON map. The accepted references are:

```text
references/<task-name>/c001.json ... c030.json
```

The FABLE result is nested under `output`, with task/schema/selector/finalizer/input
provenance in the surrounding envelope.

### Required Correction

1. Implement strict read-only loaders for the accepted input and reference directory
   formats.
2. Validate all 30 input envelopes and all 120 reference envelopes with explicit
   Pydantic contracts.
3. Preserve frozen selection order.
4. Route the accepted `overview` selector to the three overview tasks and `recent`
   only to `last-activity`.
5. Use each accepted selector's canonical input hash, message IDs, transcript,
   selector/version, and metadata.
6. Validate every reference task/case/input/schema/finalizer/catalog identity before
   scoring.
7. Read the actual reference from `output`; do not flatten or rewrite the accepted
   files.
8. Reject missing, extra, duplicate, misordered, cross-task, or mismatched files.
9. Keep private content out of exceptions, default CLI output, tests, and tracked
   reports.

Do not convert the accepted corpus into the temporary format assumed by the current
code. The harness must consume the accepted frozen format directly.

## Blocking Finding 2: Local Verification Is Not Authoritative

Current `verify` checks checksums and internal package accounting, then compares the
candidate config. It does not reconstruct the authoritative 120 expected cases from
the local accepted inputs and contracts.

A self-consistent candidate package produced from the wrong source, wrong selector,
wrong prompt, wrong schema, or wrong finalizer can therefore pass current
verification.

### Required Correction

Local `verify` must:

1. load the accepted local corpus and task catalog;
2. deterministically reconstruct the 120 authoritative case aliases/fingerprints;
3. compare the returned package one-for-one against that authority;
4. compare task, selector, prompt, provider schema, application schema, finalizer,
   dates, evidence IDs, and generation identities;
5. locally revalidate every successful candidate result;
6. validate every failed attempt's boundary/raw-artifact relationship;
7. reconcile expected/completed/success/failed counts;
8. reject any mismatch before deterministic or judge scoring;
9. make zero candidate/judge model calls.

Verification must not treat hashes supplied only by the returned package as local
authority.

## Blocking Finding 3: Retry History Is Not Append-Only

Current generation writes one canonical `attempt.json` per case. Explicit failure
retry replaces that file and can replace the raw-invalid file. This violates the
handoff's audit and first-attempt baseline requirements.

### Required Correction

- Store every attempt under an immutable attempt/run identity.
- Preserve the first baseline attempt permanently.
- Keep an explicit case index/pointer rather than overwriting history.
- Associate each raw-invalid file with its exact attempt.
- Resume matching completed attempts without another model call.
- Retry failures only under the explicit flag and append the new attempt.
- Never select the best retry silently.
- Package the baseline attempt plus complete retry accounting according to an
  explicit policy.

## Blocking Finding 4: Judge Execution Is Not Implemented

The CLI currently rejects every authorized judge invocation. This is an
implementation gap, not an owner-credential gate.

Complete before asking for a private Gemini smoke:

- external judge profile resolution;
- three-flag authorization and credential preflight;
- candidate-identity blinding;
- task-specific anchored rubrics;
- structured judge result schemas;
- source evidence-ID validation;
- concise rationale without chain-of-thought;
- schema-invalid candidate skipping/accounting;
- append-only judge attempts;
- cache/resume and full invalidation identity;
- explicit judge failures;
- deterministic-only zero-LiteLLM behavior;
- judge JSONL/metrics/report output.

Use injected/mocked clients and synthetic content for committed tests. No real
Gemini call is permitted until this implementation passes PM review and the owner
supplies the credential/authorization.

## Blocking Finding 5: Provenance And Package Privacy Validation Are Incomplete

The candidate package does not yet enforce or record the full required application,
artifact, runtime, hardware, context, settings, and run provenance. Verification
also lacks the required content-leakage checks.

### Required Correction

Record and verify:

- application commit/version;
- bundle and case authority identities;
- candidate logical/profile/resolved provider/model identities;
- exact GGUF repository/file/hash/size/quantization;
- runtime/version/execution device;
- OS and privacy-safe hardware;
- configured and advertised context;
- structured-output mode;
- task generation settings;
- timeout/retry/concurrency;
- UTC run boundaries;
- latency and usage availability;
- complete case accounting.

Reject candidate packages containing:

- source transcript/request content;
- FABLE references or teacher output;
- credentials or secret-shaped config fields;
- machine-specific absolute paths;
- unexpected files;
- case/task identities not in the local authority.

The leakage scanner must be structural and allowlist-based where possible. Do not
scan only for a few literal strings and call that proof.

## Blocking Finding 6: Configured Paths Can Trigger Unsafe Recursive Deletion

`prepare` and candidate packaging call `shutil.rmtree` on configured destinations.
A malformed or mistaken config can point those destinations at a repository,
corpus, or unrelated directory.

### Required Correction

- Do not recursively delete an arbitrary configured path.
- Resolve and validate every output path under an explicitly configured private
  evaluation root.
- Reject filesystem root, drive root, repository root, `.git`, `.chronicle/eval`
  source/corpus directories, parent traversal, and input/output overlap.
- Prefer unique run directories and atomic promotion over destructive replacement.
- Require an explicit safe `--force` policy if replacement is genuinely needed.
- Add regression tests for dangerous absolute/relative paths and overlap.

## Blocking Finding 7: Archive Validation Is Not Complete

The current extraction checks a useful subset, but the handoff requires a stronger
portable boundary.

Add tests and rejection for:

- backslash traversal such as `..\escape`;
- Windows drive-relative and absolute forms using backslashes;
- UNC paths;
- duplicate archive names;
- case-insensitive path collisions on Windows;
- file/directory collisions;
- symlinks and unsupported special file modes;
- excessive file count, individual size, and expanded total size;
- archive entries outside the package allowlist.

Extract to a fresh private temporary directory only after all entries pass
preflight.

## Blocking Finding 8: Deterministic Metrics And Reports Are Incomplete

Complete the handoff-defined metrics rather than only emitting initial matrices:

- global and per-task completion/schema/failure rates;
- boundary counts;
- evidence/date/cross-field/length validity;
- per-task p50/p95 latency;
- token usage and missing-usage counts;
- work-mode confusion matrix totaling 30, exact agreement, support, precision, and
  recall;
- last-activity status matrix totaling 30;
- title-fit matrix totaling 30;
- explicit `no_valid_output` columns;
- deterministic CSV, JSON/JSONL, aggregate JSON, and private Markdown outputs;
- no composite score.

Validate accepted enum labels from code rather than duplicating unchecked label
lists.

## Blocking Finding 9: End-To-End Tests Are Missing

Implement the handoff test scenarios at behavior level. The handoff's numbered list
is a coverage matrix, not necessarily a requirement for exactly 65 test functions,
but all contracts must have deterministic coverage.

At minimum, add a synthetic 2-conversation x four-task cross-stage test that:

1. prepares eight cases;
2. generates injected successes and failures;
3. interrupts and resumes;
4. appends an explicit retry without replacing baseline evidence;
5. packages and copies across different roots;
6. verifies against independently reconstructed local authority;
7. scores with the candidate runtime unavailable;
8. reconciles all matrices and denominators;
9. runs mocked judge scoring and resumes its cache;
10. proves no private/source/reference leakage in the candidate package.

Add focused negative tests for every verification, security, authorization, cache,
and config boundary specified in the handoff. CI must remain network/model/private-
data independent on Windows and Linux.

## Report Corrections

Refresh `md/handoffs/reports/WP-5.2B1-completion-report.md` after the implementation
continuation.

The current delivery message says Ruff passed, while the report says the final Ruff
rerun is still required. Replace this with one fresh, internally consistent
validation record.

The refreshed report must distinguish:

- completed implementation evidence;
- synthetic end-to-end evidence;
- owner-controlled private smoke/transfer/full-run gates;
- anything still outstanding.

Do not claim the harness is ready for private transfer until the PM has validated
the completed offline implementation.

## Required Continuation Sequence

### Gate 1: Complete Offline Implementation

Implement all blocking findings above using synthetic fixtures and injected model
clients. Run the complete focused matrix, full suite, Ruff, CLI help, diff, and
privacy checks.

Return a refreshed report with status:

```text
partial - ready for PM review before private smoke
```

Do not open the real corpus except for read-only structural/preflight validation and
do not call Gemini.

### Gate 2: PM Review Before Private Smoke

The PM validates corpus compatibility, package authority, safety, judge fail-closed
behavior, and synthetic end-to-end evidence. Only after this gate may the owner
authorize one private candidate case and one Gemini judge case.

### Gate 3: Owner-Controlled One-Case Smoke

After explicit owner approval:

- prepare from the accepted private corpus;
- run one frozen-order candidate case;
- package/copy/verify/score locally;
- make one authorized Gemini judge call;
- validate privacy and no-write behavior.

### Gate 4: Remote 120-Case Run And Local Scoring

Only after the one-case smoke passes:

- obtain explicit target-machine/transfer approval;
- run all 120 candidate cases remotely;
- return and verify the package locally;
- run deterministic scoring;
- run/resume Gemini judging for every eligible case;
- verify cleanup and live/frozen no-write evidence.

WP-5.2B1 reaches `Ready for PM validation` only after Gate 4.

## Validation Commands For The Next Pass

```powershell
poetry env info --path
poetry run pytest tests/test_bench.py -q
poetry run pytest
poetry run ruff check .
poetry run python -m bench --help
poetry run python -m bench prepare --help
poetry run python -m bench generate --help
poetry run python -m bench verify --help
poetry run python -m bench score --help
poetry run chronicle --help
poetry run chronicle --ai-task list
git diff --check
git status --short
git ls-files ".chronicle/*" "*.db" "*.sqlite" "*.zip" "exports/*"
```

## Delivery Rules

- Continue in the same executor thread if practical.
- Do not stage or commit anything.
- Do not edit the development ledger or master plan.
- Preserve PM-owned handoff/plan/ledger changes.
- Do not transfer real private data or call Gemini during Gate 1.
- Keep all generated private artifacts ignored.
- Return a concise summary pointing to the refreshed completion report.

## Gate 1 Revalidation Addendum

### Decision

**Gate 1 is substantially complete, but private-smoke authorization is withheld
pending narrow rework.**

The executor completed the accepted-corpus loaders, authoritative case
reconstruction, append-only candidate attempts, hardened archives, deterministic
metrics/reports, mocked Gemini judge path, and synthetic cross-stage test. The PM
confirmed the accepted private structure is recognized as 30 inputs and 120
references without printing content.

The following findings must be corrected before Gate 2 approval. Do not open a
private candidate case or call Gemini during this rework.

### Gate 1 Finding A: Default CLI Output Exposes Absolute Private Paths

`prepare` and candidate packaging return `str(archive)`, and the CLI emits the
returned mapping as JSON. On this machine that exposes the absolute private
evaluation path by default. Normal config/read errors can also include absolute
config paths through raw exception text.

The handoff requires privacy-safe default terminal output.

Required correction:

- print a path relative to the configured private evaluation root, or a stable
  artifact label, by default;
- reserve absolute paths for an explicit allowlisted `--verbose` mode if genuinely
  useful;
- sanitize normal configuration, filesystem, validation, and provider errors so
  private paths/content/credentials are not echoed;
- retain actionable error category and safe bounded detail;
- add CLI tests using long private Windows-shaped paths and private marker strings;
- prove default `prepare`, `generate`, `verify`, and `score` output contains none of
  those markers.

### Gate 1 Finding B: Application Commit Is Declared, Not Measured

The candidate manifest copies `candidate.application_commit` from YAML. Generation
does not independently determine the checked-out implementation identity and
compare it with the pinned value before the first candidate call. A remote machine
can therefore run different code while packaging the expected configured commit.

Required correction:

- derive the actual repository commit from the running checkout before generation;
- compare it with the required prepared-bundle/config identity;
- fail before the model call on mismatch;
- record the measured commit, not only the configured value;
- detect and either reject a dirty tracked implementation or record and verify a
  deterministic tracked-diff identity under an explicitly approved development
  policy;
- keep private/untracked evaluation artifacts out of dirty-state identity;
- test matching, mismatching, and dirty implementation states without depending on
  the host repository.

Because the remote run should use a committed implementation, the preferred
operational path is: PM accepts Gate 1, PM commits it, owner transfers/pulls that
commit to the candidate machine, then generation enforces the commit.

### Gate 1 Finding C: Actual Candidate Provider/Model Is Not Enforced

The package records provider/model values returned by baseline attempts, but local
verification does not require those values to match the accepted LM Studio/Llama
candidate. The manifest's resolved model and runtime settings are config-derived.

Required correction:

- define the expected actual provider/model identity for the accepted LiteLLM LM
  Studio route;
- require every response-bearing baseline attempt to match it;
- reject mixed or unexpected actual providers/models before packaging or during
  local verification;
- preserve provider-less transport failures as explicit failures rather than
  inventing provenance;
- measure/record the runtime preflight evidence available from LM Studio, and state
  clearly which runtime/device fields remain operator-attested;
- add tests for wrong provider, wrong model, mixed models, and transport failure.

Do not imply that hashing a GGUF file proves that LM Studio loaded that same file.
The Gate 3 operator preflight must still compare `lms ls --json`, loaded model ID,
artifact identity, and response provenance.

### Gate 1 Finding D: Judge Failure Handling Hides Programming Errors

The judge catches a tuple containing `Exception`, so coding defects, filesystem
errors, and unexpected internal failures are converted into cached per-case judge
failures. This can make a broken judge implementation look like model/provider
failure.

Required correction:

- catch only known provider/transport and output-validation exceptions;
- normalize those into allowlisted privacy-safe failure categories;
- let unexpected implementation errors fail the run visibly without persisting
  provider-controlled exception text;
- test a known provider failure, known schema failure, and unexpected programming
  exception separately.

### Gate 1 Finding E: Cached Judge Failures Have No Explicit Retry Path

Matching judge failures are currently reused forever. A transient Gemini failure
cannot be retried without changing rubric/profile identity or manually deleting
private cache state, neither of which is an acceptable operator workflow.

Required correction:

- add an explicit judge-failure retry option;
- append a new immutable judge attempt while preserving the first failure;
- keep successful matching results cached;
- never retry failures silently;
- report baseline/current attempt accounting;
- test failure resume without retry, explicit append-only retry, and subsequent
  success caching.

### Gate 1 Finding F: Judge Enablement Is Not Enforced

`judge.enabled` exists in strict configuration, but an authorized `--with-judge`
invocation does not check it.

Required correction:

- reject `--with-judge` before private reads/prompt construction when the configured
  judge is disabled;
- retain all three authorization flags even when enabled;
- test disabled, enabled-but-unauthorized, missing credential, and fully authorized
  injected-client paths.

### Additional Hardening Required In The Same Pass

- Replace whole-file GGUF hashing with a streaming hash so the 807 MB model is not
  loaded into one Python bytes object.
- Expand tests for authoritative package mismatch, actual attempt/result local
  revalidation, matrix totals, judge failures, and privacy-safe CLI output. The
  existing 20 tests are a good cross-stage base but do not yet prove these Gate 1
  findings.
- Refresh the completion report with one internally consistent final Ruff/test/help
  record and a Gate 1 rework section.

### Gate 1 Revalidation Required

Run:

```powershell
poetry env info --path
poetry run pytest tests/test_bench.py -q
poetry run pytest
poetry run ruff check .
poetry run python -m bench --help
poetry run python -m bench prepare --help
poetry run python -m bench generate --help
poetry run python -m bench verify --help
poetry run python -m bench score --help
poetry run chronicle --help
poetry run chronicle --ai-task list
git diff --check
git status --short
git ls-files ".chronicle/*" "*.db" "*.sqlite" "*.zip" "exports/*"
```

Return status as:

```text
partial - ready for repeat PM Gate 1 review
```

No candidate model call, Gemini call, private bundle generation, or private transfer
is authorized by this addendum.

## Repeat Gate 1 PM Review And Short-Smoke Addendum

### Decision

**The seven Gate 1 rework findings pass PM validation, but Gate 2 private-smoke
authorization remains withheld because the required short smoke cannot currently be
selected.**

The PM independently confirmed:

- the Poetry environment resolves to this repository's `.venv`;
- the focused bench suite passes with 30 tests;
- the full suite passes with 403 tests;
- Ruff and `git diff --check` pass;
- the main bench help and all four subcommand help surfaces pass;
- normal Chronicle help and AI-task listing remain functional;
- no `.chronicle`, database, SQLite, ZIP, or export artifact is tracked;
- default CLI output uses artifact labels and the marker-based privacy regressions
  cover `prepare`, `generate`, `verify`, deterministic scoring, and authorized judge
  scoring;
- application commit and tracked-diff identities are measured before candidate calls;
- candidate response provider/model identities are enforced;
- judge failures, retries, enablement, and unexpected-error behavior are separated;
- GGUF hashing is streamed in bounded chunks.

The first unelevated bench-help launch hit the documented Windows sandbox error
`CreateProcessAsUserW failed: 1312`. The exact commands passed when retried using the
approved sandbox-validation path. This was an execution-host issue, not a project
failure.

### Blocking Finding: The Short Private Smoke Has No Supported Scope

The handoff requires a short real boundary smoke before a complete candidate run.
The owner has now explicitly selected this initial progression:

1. one frozen conversation x all four tasks locally with the accepted Llama 3.2 1B
   evaluation-floor model;
2. local deterministic scoring and authorized Gemini judging;
3. a small local pilot if the first smoke passes;
4. the complete 30-conversation x four-task development run locally;
5. remote generation remains optional and deferred.

The current command surface cannot perform step 1. `prepare` always builds all 120
cases, `generate` has no frozen-prefix limit, and verification/scoring reconstruct all
120 cases from configuration. Running the current commands would therefore start the
complete candidate run, contrary to the owner-approved staged gate.

### Required Narrow Rework

Add one explicit, deterministic conversation-scope option to the split harness. The
recommended operator contract is:

```text
bench prepare --config <config> --conversation-limit <N>
```

Requirements:

1. `N` must be an integer from 1 through the configured frozen conversation count.
2. Selection must be exactly the first `N` conversations in the already frozen order.
   Do not inspect content and do not accept arbitrary conversation IDs or aliases.
3. Every selected conversation must include all four tasks in fixed task order. Thus
   `N=1` means four cases and `N=3` means twelve cases.
4. Record the requested limit, effective conversation count, case count, and frozen-
   prefix selection identity in the bundle manifest and content identity.
5. Generation must process only the cases in that prepared bundle and retain every
   existing commit, artifact, provider/model, append-only, and privacy control.
6. Local verification must reconstruct the same frozen prefix directly from the full
   accepted local corpus and reject any non-prefix, missing, extra, reordered, or
   cross-task case.
7. Deterministic and judge scoring must use the scoped denominators and still reconcile
   every matrix and accounting total.
8. The portable candidate package must not include source transcripts, references,
   private paths, or credentials. Scope metadata may contain only privacy-safe counts
   and deterministic identities.
9. Existing no-limit behavior must remain the complete 30-conversation/120-case run.
10. Do not require copying, rewriting, or creating a subset of the frozen corpus or
    FABLE reference directories.
11. Add synthetic tests for limits 1, an intermediate value, the full count, zero,
    negative, above maximum, tampered scope metadata, a non-prefix package, matrix
    totals, judge accounting, and default CLI privacy.
12. Refresh the operator documentation with the exact four-stage local sequence, but
    do not include private paths, IDs, outputs, or credentials in tracked material.

### Rework Boundary

- Use only synthetic fixtures and injected clients.
- Do not prepare the private bundle.
- Do not call the Llama candidate model.
- Do not call Gemini.
- Do not transfer private data.
- Do not stage or commit changes.
- Preserve PM-owned plan, ledger, handoff, and review changes.

Return status as:

```text
partial - ready for PM short-smoke-scope review
```

After that repeat review passes, the PM may commit the implementation and provide the
owner with exact commands for the one-conversation/four-task local smoke. The full
120-case run remains blocked until the smoke and optional small pilot pass.

## Short-Smoke Scope PM Review

### Decision

**Passed. Gate 2 is approved. WP-5.2B1 may proceed to the owner-controlled local
Gate 3 smoke after the implementation is committed and the private configuration is
pinned to that accepted commit.**

The PM independently confirmed:

- `prepare --conversation-limit N` exists and accepts positive integer input;
- limit 1 produces one frozen conversation x four fixed task cases;
- intermediate, explicit-full, and unlimited scopes are covered;
- unlimited scope retains complete 30-conversation/120-case behavior;
- selection is a deterministic prefix of the accepted frozen order;
- scope and prefix identity are bound into bundle, generation-work, package,
  verification, deterministic-score, judge, and run-manifest accounting;
- verification reconstructs the prefix from the complete accepted corpus;
- invalid, oversized, tampered, and non-prefix scopes are rejected;
- deterministic matrices reconcile to the scoped conversation count;
- judge accounting reconciles to the scoped four-task cases;
- no subset of the frozen input or reference directories is created or required;
- focused tests pass: 36;
- full suite passes: 409;
- Ruff and `git diff --check` pass;
- the new CLI help surface passes;
- no private database, ZIP, export, or `.chronicle` artifact is tracked;
- nothing is staged or committed.

The first unelevated prepare-help launch hit the documented Windows sandbox error
`CreateProcessAsUserW failed: 1312`; the exact check passed through the approved
sandbox-validation retry. This is not a project failure.

### Gate 3 Authorization Boundary

Authorization is limited to the following local sequence:

1. PM commits the reviewed implementation.
2. Owner pins the private candidate configuration to that measured commit and the
   already accepted Llama 3.2 1B `Q4_K_M` artifact/runtime identity.
3. Prepare exactly one frozen-prefix conversation, producing four task cases.
4. Generate those four candidate results locally through LM Studio.
5. Verify the returned package locally.
6. Run deterministic scoring locally.
7. After inspecting candidate and deterministic artifacts, make the explicitly
   authorized Gemini judge calls for eligible results only.
8. Confirm live and frozen database fingerprints remain unchanged and no private
   artifact is tracked.

Do not run an intermediate pilot or the complete 120 cases under this authorization.
Do not transfer the private bundle to another machine. Those actions require review of
the Gate 3 evidence and a further owner decision.
