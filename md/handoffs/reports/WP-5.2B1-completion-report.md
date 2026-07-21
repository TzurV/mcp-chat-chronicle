# WP-5.2B1 Completion Report

## Status

**partial - ready for PM short-smoke-scope review**

Gate 1 offline implementation is complete and validated with synthetic data and injected
clients. No candidate runtime, Gemini endpoint, private transfer, or private one-case/full run
was authorized or executed. PM review is required before Gate 3.

## Executive summary

The development-only `bench` package now provides independently runnable local preparation,
candidate generation, authoritative local verification, deterministic scoring, and explicitly
authorized judge scoring. It consumes the accepted WP-5.1.2B directory envelopes directly,
preserves baseline and retry history, validates the local GGUF before generation, reconstructs
all case authority locally before scoring, and keeps deterministic and judge results separate.

The continuation resolves the original blocking findings, Gate 1 revalidation findings, and the
short-smoke scope addendum at the offline/synthetic level. Owner-controlled private smoke, transfer, real Llama
generation, and real Gemini judging remain gated.

## Frozen-prefix short-smoke rework

- `prepare --conversation-limit N` selects exactly the first `N` conversations in accepted frozen
  file order and expands each into the fixed four-task order. `N=1` therefore creates four cases.
- Scope metadata records the selection contract, requested/effective counts, case count, and a
  fingerprint-derived prefix identity without private content, paths, or arbitrary conversation IDs.
- Generation carries the scope into its work identity and candidate package. A work directory cannot
  be reused for another bundle scope, and packaging copies only the cases declared by that bundle.
- Verification opens the complete accepted input corpus, rebuilds the authoritative prefix locally,
  validates exact ordered case identities, and reconciles manifest and independent accounting counts.
- Deterministic and judge scoring first invoke the same verification boundary, then load complete
  reference directories and score only the locally reconstructed prefix.
- Intermediate prefixes and explicit full prefixes are supported. Omitting the option retains the
  existing 30-conversation/120-case behavior and shares the same identity as an explicit full prefix.
- Synthetic positive coverage exercises one-, intermediate-, explicit-full-, and unlimited scopes
  through preparation and the relevant downstream stages. Negative coverage rejects zero, negative,
  oversized, tampered-metadata, and non-prefix scopes.

## Gate 1 revalidation rework

- Default CLI archive output is now a stable artifact label. Callback filesystem/config/
  validation errors are category-normalized and cannot echo private paths, marker text, content,
  or credentials. Typer pre-validation of private paths was removed so missing-path errors pass
  through the sanitizer.
- Generation measures the checkout commit and tracked dirty state with Git before the first
  candidate call. It rejects commit mismatch and unapproved tracked differences. The optional
  development dirty policy requires a pinned deterministic tracked-diff hash; untracked private
  artifacts are excluded.
- Every response-bearing candidate attempt must match the configured actual provider and model.
  Wrong or mixed identities abort before packaging. Provider-less transport failures remain
  explicit failures. GGUF hashing is streaming rather than whole-file.
- Judge execution catches only application-classified provider failures, structured-output
  validation failures, and explicit judge contract failures. Unexpected programming/filesystem
  errors abort visibly and are not cached.
- `--retry-judge-failures` appends immutable judge attempts. Matching failures remain cached by
  default, matching successes are always reused, and reports distinguish baseline/current/total
  attempt accounting.
- `judge.enabled` is enforced before source/reference reads or prompt construction, while all
  three remote authorization flags remain mandatory.

## Architecture and files changed

- `bench/models.py`: strict config, accepted input/reference, case, candidate-attempt, and
  judge-result contracts.
- `bench/loaders.py`: accepted 30-input/four-directory reference loaders with ordering,
  identity, selector, and canonical-input-hash checks.
- `bench/paths.py`: evaluation-root containment and input/output overlap protection.
- `bench/io.py`: canonical JSON, atomic files, deterministic ZIPs, checksums, and hardened
  archive preflight/extraction.
- `bench/core.py`: authority reconstruction, preparation, generation/resume, packaging,
  verification, leakage checks, metrics, and reports.
- `bench/judge.py`: blinded task rubrics, structured results, authorization-compatible remote
  boundary, cache/resume, invalidation, failures, and judge reports.
- `bench/__main__.py`: four-stage command surface and normal operator error handling.
- `bench/evaluation.default.yaml` and `bench/ai-models.evaluation.default.yaml`: privacy-safe
  tracked templates.
- `docs/development-evaluation.md`: local/remote/return/scoring/cleanup runbook.
- `tests/test_bench.py`: synthetic cross-stage and negative security/identity tests.
- `pyproject.toml`: packages the development-only `bench` module.

## Command surface

```text
poetry run python -m bench prepare --config <local-eval-config> --conversation-limit <N>
poetry run python -m bench generate --bundle <input-bundle> --config <candidate-config>
poetry run python -m bench verify --package <candidate-package> --config <local-eval-config>
poetry run python -m bench score --package <candidate-package> --config <local-eval-config> --deterministic-only
poetry run python -m bench score --package <candidate-package> --config <local-eval-config> --with-judge --allow-remote --confirm-private-eval
```

The normal `chronicle` CLI is unchanged.

## Configuration and credential boundary

Strict Pydantic models reject unknown keys, wrong task order, invalid case accounting, local
candidate profiles classified as remote, and judge profiles classified as local. All outputs
must resolve beneath an explicit private evaluation root. Candidate and judge profiles remain
external YAML aliases. `GEMINI_API_KEY` is resolved only from its named environment variable;
it is not serialized. Missing credentials fail before prompt construction or client invocation.

The candidate config records logical/profile identity, artifact repository/file/hash/size/
quantization, runtime/version/device, advertised context, and pinned application commit. The
local artifact path is excluded from portable serialization.

## Accepted input and reference compatibility

The loader reads exactly `c001.json` through `c030.json` in frozen selection order. It validates
both accepted selector envelopes, recomputes their canonical input hashes, rejects duplicate
evidence IDs, and routes `overview` to summary/work-mode/title while routing `recent` only to
last-activity.

References are read as four task directories x 30 envelopes. Scoring uses the nested `output`
without rewriting files. Task, case group, source conversation, selector/version, input hash,
task version, application/provider schema, finalizer, catalog hash, output schema, evidence,
and deterministic dates are validated before scoring.

Read-only structural preflight accepted 30 inputs and 120 references. Their task-catalog
references matched the tracked accepted catalog. No private content was printed.

## Bundle schema and deterministic identity

Preparation creates the selected frozen-prefix cases in input file order then fixed task order;
without a limit it creates all 120 cases. Every fingerprint covers
the accepted canonical selector input, deterministic dates, task, selector/version, rendered
prompt, provider schema, application schema, finalizer, generation settings, and request-
construction version. Candidate and judge identities are excluded.

The bundle includes only its manifest/checksums, case requests, contract directory, and private
README. It includes no database, reference, teacher output, judge setting, credential, provider
path, or URL. Canonical JSON and fixed ZIP order/time/mode produce a path-independent content
identity and deterministic transfer archive. Preparation never deletes an existing destination.

## Candidate generation and append-only resume

Generation verifies the bundle, candidate/profile requirement, local model route, and exact
configured artifact file name/hash/size before the first call. It needs no database, reference,
or judge credential and does not access reference paths. Requests use the application-owned
completion boundary and schema/finalizer validator with retries fixed to zero.

The running checkout commit and tracked diff are independently measured before the first call
and compared with prepared/configured authority. The measured identity, not a YAML-only claim,
is packaged. Whole-file model loading is avoided by streaming the GGUF hash in bounded chunks.
Every response-bearing attempt must match the expected `lm_studio` provider and accepted model
identity; provider-less transport failures retain null response provenance.

Each case stores immutable numbered attempts plus an index naming the permanent first baseline.
Running markers make interruption visible. Ordinary resume skips matching completed outcomes;
`--retry-failures` appends a new attempt and raw-invalid artifact without replacing baseline
evidence. Work belonging to another candidate identity is rejected and requires a new directory.
Packaging includes complete attempt history while all metrics use the explicit first-attempt
baseline.

## Candidate package and provenance

The candidate package records local bundle authority, all case fingerprints, first-attempt and
total-attempt accounting, application version/commit, candidate logical/profile/resolved route,
actual provider/model values, GGUF provenance, runtime/OS/architecture/device, configured and
advertised context, structured-output setting, per-task generation settings, timeout/retry/
concurrency, UTC boundaries, latency, usage availability, and the absence of references/judge
results. No absolute artifact path is serialized.

Package imports reject traversal using slash or backslash, drive/UNC paths, duplicates,
case-insensitive collisions, file/directory collisions, symlinks/special modes, excessive file
counts/sizes, and entries outside the package allowlist. Extraction occurs only into a fresh
temporary directory.

Structural leakage validation rejects unexpected files, source transcripts, reference/teacher
provenance, secret-shaped fields/content, credentials, and absolute paths. Raw-invalid files must
match exact attempts one-for-one.

## Authoritative local verification

Verification makes zero model calls. It reconstructs the declared frozen prefix from the complete
local corpus and its authoritative
bundle content identity from accepted inputs and current accepted contracts, compares every
returned case one-for-one, validates complete attempt indexes and baseline pointers, locally
revalidates every successful application result, checks failed-boundary/raw relationships,
reconciles counts, confirms candidate/model/runtime provenance, and runs structural leakage
checks. Any mismatch stops before deterministic or judge scoring.

## Deterministic metrics and reports

All first attempts remain in denominators. Outputs include global and per-task success/failure/
schema-valid rates, failure-boundary counts, evidence/cross-field/date/length/title-suggestion
validity, per-task p50/p95 latency, usage availability/missing counts and numeric totals, and
explicit `no_valid_output` counts.

Work-mode metrics include an ordered confusion matrix, total, exact agreement, and per-label
support/precision/recall. Last-activity and title-fit matrices include totals/statistics and an
explicit invalid-output column. JSON, JSONL, CSV, aggregate JSON, private Markdown, verification,
and run-manifest artifacts are written under the configured ignored run root. There is no
composite score.

## Judge model, rubric, authorization, and cache

The external judge alias resolves through the accepted model loader and template route
`gemini/gemini-2.5-flash`. Every remote run requires all of `--with-judge`, `--allow-remote`, and
`--confirm-private-eval`. Missing authorization or credentials prevents client calls.

Four task-specific rubrics use anchored integer scores 0-4. Strict output permits only concise
verdict rationale, dimension scores, evidence IDs, and unsupported-claim count; no chain-of-
thought field exists. Prompts contain selected source, candidate result, FABLE output, rubric,
and allowed evidence IDs, but no candidate model/artifact/runtime identity.

Schema-invalid candidates are skipped and counted. Cache identity covers candidate output,
source input, reference, rubric/version, judge profile/resolved model/config, and generation
settings. Matching successes/failures resume without a call; changed rubric/profile/source/
reference/candidate creates a separate immutable cache identity. Failures retain only a safe
category, never provider-controlled text.

Cached failures retry only with `--retry-judge-failures`; retries append rather than replace.
Known provider, schema, and response-contract failures use allowlisted categories. Unexpected
implementation errors propagate and create no cache record. Disabled judge configuration fails
before private case/reference reads.

## Synthetic end-to-end evidence

The synthetic run used two accepted-format conversations x four tasks:

- eight authoritative cases prepared and generated through an injected client;
- first-attempt totals: eight completed, seven valid, one invalid JSON;
- explicit retry appended one successful ninth attempt while preserving the failed baseline;
- interruption resumed to exactly eight attempts without duplication;
- package copied to another root, verified against reconstructed authority, and scored with no
  candidate runtime;
- work-mode matrix: two expected executor -> two executor;
- last-activity matrix: two expected completed -> one completed and one `no_valid_output`;
- title-fit matrix: two expected true -> two true;
- judge: seven eligible/completed, one invalid skipped, zero failures;
- identical judge rerun made zero new calls; rubric-version change invalidated seven entries;
- unexpected package content, checksum changes, unsafe paths/archives, and destination reuse were
  rejected.

Synthetic usage was available for seven valid candidate results. Synthetic timings and token
values are fixtures and are not presented as model performance.

The addendum-specific synthetic run used a three-conversation accepted-format corpus. A one-
conversation prefix produced four ordered cases and passed generation, verification, deterministic
matrix accounting, and injected-judge accounting. Two-conversation, explicit three-conversation,
and unlimited preparation produced 8, 12, and 12 cases respectively. The complete synthetic input
and four complete reference directories remained in place; no subset was created or modified.
Invalid limits, altered scope accounting, and a substituted non-prefix alias were rejected.

## Proof of separation and no composite score

The scoring path imports no candidate runtime and successfully scored the copied synthetic
package after generation. Deterministic-only scoring instantiated no LiteLLM client. Judge calls
are isolated in `bench/judge.py` and invoked only after explicit CLI authorization. Aggregate
outputs retain separate `runtime_reliability`, `deterministic_contract`, and `judge_semantic`
namespaces. No overall/composite score is calculated or emitted.

## Private transfer, real run, and no-write status

No private transfer target/method/storage/cleanup was approved, so no transfer or remote cleanup
occurred. No Llama candidate call or Gemini call occurred. This short-smoke-scope rework did not
prepare or inspect private case content; all new execution coverage used synthetic fixtures and
injected clients. The earlier ignored accepted input/reference structural preflight remained
read-only. Neither live nor frozen
SQLite database was opened or modified. Before/after database fingerprints and the real one-case
smoke remain Gate 3 owner-controlled evidence.

## Validation record

- Poetry environment: repository `.venv` confirmed.
- Accepted-format read-only preflight: 30 inputs and 120 references passed.
- Focused tests: 36 passed.
- Full suite: 409 passed.
- Ruff: passed.
- `git diff --check`: passed after the final report refresh.
- Bench main help and all four subcommand help surfaces: passed.
- Normal Chronicle help/task listing: passed.
- Git privacy query returned no tracked `.chronicle`, database, ZIP, or export artifact.

## Acceptance status and remaining gates

Offline implementation criteria are satisfied for PM review: accepted loaders, split stages,
strict config, deterministic package identities, artifact enforcement, append-only generation,
authoritative verification, complete deterministic reports, implemented mocked judge behavior,
security boundaries, and CI-safe synthetic coverage.

The following acceptance items intentionally remain open until owner authorization: private
snapshot/DB before-after fingerprint evidence; one-case real Llama/Gemini smoke; approved remote
transfer; complete 120-case candidate package; real deterministic aggregates; full Gemini judge
coverage; verified remote cleanup. Therefore the package is not yet `Ready for PM validation` and
must not be used for private transfer before PM Gate 2 approval.

## Follow-ups

After PM scope review and Gate 2 approval, perform exactly the handoff's one-conversation/four-case
frozen-prefix smoke and inspect private artifacts. Only after that succeeds should the owner approve
an intermediate prefix pilot, then the remote 120-case run and local
Gemini scoring. Later WP-5.2A5/B2 work may compare candidates but must not tune against or present
this development corpus as a final benchmark.

## Worktree ownership

Nothing was staged or committed. PM-owned edits to the master plan, development ledger, handoff,
and validation review were preserved. Final status is reported after the last validation pass.
