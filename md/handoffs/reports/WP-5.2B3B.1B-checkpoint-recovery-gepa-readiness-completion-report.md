# WP-5.2B3B.1B checkpoint recovery and GEPA readiness — Gate 1 report

## Status

Gate 0 and Gate 1 are complete from manager commit
`be33ee986554a2482e3a3287358b3449f678fcb0`. This delivery is stopped at the
mandatory manager checkpoint. Gate 2 private recovery and Gate 3 private
readiness evidence have not been run.

The first manager review required three bounded corrections. All three findings
and the additional evidence requirements are now addressed. All tracked changes
remain unstaged and uncommitted, so the manager's Gate 1 commit identity is
still pending.

## Executive summary

The failure was an authority-resolution defect, not invalid P0 or Bootstrap
evidence. Historical verification compared every result's creation commit and
configuration identity directly with the current optimizer configuration. That
retroactively applied the newer Bootstrap application commit to the older P0
result and produced `optimizer result application identity mismatch`.

The repair resolves each historical result to exactly one consumed execution
authorization from the same run. Each authorization is independently
hash-validated and must match the current immutable experiment after replacing
only the application commit with its historical value. New execution remains
pinned to the configured current clean commit.

The no-call recovery command reconstructs P0/Bootstrap membership, writes a
separate stable GEPA-readiness checkpoint, explicitly selects P0 as the next
GEPA parent, and classifies Bootstrap as a completed non-promotable comparator.
It rejects any pre-existing GEPA result, candidate, attempt, or proposer usage.

## First-review findings resolved

### Finding 1 — clean pinned commit

`recover_gepa_readiness()` now calls `measure_implementation()` by default and
applies the same clean/pinned rule as new optimizer execution. The measured
checkout must be clean and its commit must exactly equal
`config.application_commit`. This check occurs after configuration loading but
before resolving or reading the private run root, and therefore before either
recovery write. The identity probe is injectable for deterministic tests.

Regressions prove exact-clean success, dirty-checkout rejection, wrong-commit
rejection, no run-state access after either rejection, and continued clean
commit enforcement for later optimizer execution.

### Finding 2 — complete GEPA evidence detection

Recovery now rejects any filesystem entry matching `proposal-gepa-*` below the
trial root, whether it is a directory or file and whether it is complete,
empty, malformed, current-only, or partially written. It continues to reject
GEPA state membership, GEPA candidate/result lineage, and nonzero historical
proposer usage. No detected evidence is deleted, normalized, or repaired.

Regressions cover a normal attempt, state-only result membership, a current-only
pointer, an empty trial directory, a candidate-only package, and a malformed
pointer.

### Finding 3 — operation-scoped provider accounting

The ambiguous `provider_calls` readiness field is replaced by the literal
`recovery_provider_calls: 0`. It means only that this recovery operation makes
no new provider call. It does not claim that the historical P0/Bootstrap run
contains no candidate-model activity. Historical budget and retained provider
response accounting are neither rewritten nor reinterpreted.

## Gate 0 evidence

- Branch: `main`.
- Starting HEAD: `be33ee986554a2482e3a3287358b3449f678fcb0`.
- Starting tracked checkout: clean.
- Poetry environment: this repository's `.venv`.
- Ordinary `chat_chronicle` and `bench` imports loaded zero DSPy, LiteLLM,
  Google-auth, or Vertex client modules.
- The known ignored immutable evidence index verified all 130 files.
- Inventory: one P0 package/result, one Bootstrap package/result, Bootstrap
  attempts `0001`/`0002`/`0003`, one current proposal pointer, three execution
  authorizations, three corresponding consumed-authorization records, one
  budget state, and 82 retained provider-response records.
- Both historical results resolved uniquely in the metadata-only inventory.
- The frozen train and validation manifest bindings verified as 6/4.
- Recorded GEPA results, GEPA attempts, proposer calls, and holdout files opened:
  zero.

Raw private paths, artifact identities, hashes, selected inputs, references,
candidate outputs, and provider records remain only in ignored operator
storage. Gate 0 performed hash/count verification and did not inspect semantic
conversation content.

## Authority and compatibility design

Historical validity now requires all of the following:

1. Structural candidate/result identity verification.
2. Exact terminal candidate and Bootstrap proposal-trial authority.
3. Exact membership in the append-only authorization sequence and consumed
   authorization directory.
4. Exactly one matching consumed authorization per result.
5. Exact run, manifest, model-artifact, proposer-policy, optimizer-policy, seed,
   framework-version, and budget identities.
6. Exact configuration identity after substituting only the historical
   authorization's application commit.
7. Accepted P0 contracts, 8,192 context, and Bootstrap-to-P0 lineage.

New results record the exact `execution_authority_sha256` in `ResultAuthority`.
This removes ambiguity when several executions use the same application commit.
The field is optional and omitted from serialization when absent, so existing
format-v1 results retain their original identity and continue to validate by a
strict unique legacy match. No historical artifact or `PilotCheckpoint` schema
is rewritten or overloaded.

The recovery artifact uses a dedicated `RecoveryReadiness` model. It binds the
canonical run-state hash, immutable-experiment hash, budget hash, ordered
authorization membership, both resolved results, the non-promotable Bootstrap
disposition, P0 parent, and literal zero GEPA/recovery-provider counts into one
stable hash.

Bootstrap's `complete-non-promotable` disposition is explicitly recorded with
the basis `manager-policy` and the exact recovered Bootstrap result identity.
Recovery does not recompute a quality or promotion decision. Parsing the
retained result verifies the internal hashes and consistency of its
`PrivacyEvidence` and complete `RequestEnvelopeEvidence`, but recovery does not
independently re-evaluate private prompt text or require those two retained
fields to reproduce the historical privacy/context failures. That would be a
private quality evaluation outside Gate 1. The policy disposition is therefore
not presented as a new metric-derived conclusion.

Writes use the existing canonical `atomic_json` path and its bounded Windows
sharing-violation retry. Repeating recovery produces byte-identical state and
readiness artifacts and does not touch candidates, results, attempts, current
pointers, authorizations, or budget evidence. Each destination separately
passes the Windows sharing-violation retry regression. A failure injected after
the atomic run-state replacement but before the readiness write leaves a valid
canonical state; an ordinary rerun creates the missing readiness artifact and
then repeats as a byte-stable no-op.

## Synthetic regression matrix

| Requirement | Result |
|---|---|
| P0 and Bootstrap from different clean commits | Passed |
| Historical validity independent of current checkout | Passed |
| Recovery exact clean/pinned checkout | Passed |
| Dirty or wrong recovery checkout before run-state access | Rejected |
| New execution remains pinned to current clean commit | Passed |
| Missing consumed authorization | Rejected |
| Dangling consumed authorization | Rejected |
| Duplicate or stale state membership | Rejected |
| Foreign-run or hash-invalid authorization | Rejected |
| Immutable experiment change | Rejected |
| Commit change without matching consumed authorization | Rejected |
| Candidate, result, trial, and authorization identity tampering | Rejected with bounded diagnostics |
| Bootstrap registration without an adapter | Passed |
| P0 selected as GEPA parent | Passed |
| GEPA attempt, state result, current-only pointer, empty directory, candidate, or malformed pointer | Rejected |
| Attempts `0001`/`0002`/`0003` and current pointer preserved | Passed |
| Repeated recovery byte stability | Passed |
| Windows atomic replacement sharing violation | Retried and passed |
| Failure between state/readiness writes | Repaired by idempotent rerun |
| Recovery import isolation | No production adapter, DSPy, LiteLLM, Google-auth, or Vertex client import |
| Legacy result serialization and ordinary optimizer lifecycle | Passed |

All regressions are synthetic, network-free, credential-free, and contain no
private source or model output.

## Files changed

- `bench/optimization/recovery.py` — historical authorization resolution,
  clean-commit gate, complete GEPA evidence detection, recovery verification,
  canonical state registration, and readiness model.
- `bench/optimization/package.py` — backward-compatible optional exact
  execution-authorization binding.
- `bench/optimization/execution.py` — binds newly created results to their exact
  consumed execution authorization.
- `bench/optimization/operations.py` — uses historical consumed-authorization
  resolution for no-call verification and inspection.
- `bench/__main__.py` — adds `recover-gepa-readiness`.
- `tests/test_bench_optimization.py` — required synthetic recovery and
  compatibility regressions.
- This Gate 1 report.

## Validation

- `poetry env info --path` — repository `.venv`.
- `poetry run pytest tests/test_bench_optimization.py -q` — 132 passed.
- `poetry run pytest -q` — 606 passed, 1 skipped.
- `poetry run ruff check .` — passed.
- Ruff formatting check for all modified Python files — passed.
- `poetry check` — passed.
- `poetry run python -m bench --help` — passed; recovery command listed.
- `poetry run python -m bench recover-gepa-readiness --help` — passed.
- Fresh-process recovery import isolation — passed; no production adapter,
  DSPy, LiteLLM, Google-auth, or Vertex client module loaded.
- `git diff --check` — passed.
- `git diff --cached --name-only` — empty.
- `git ls-files .chronicle` — empty.

## Privacy and execution boundary

No private recovery was executed. No P0, Bootstrap, GEPA, candidate inference,
fixed judging, model loading, RunPod, ADC, credential, network, or provider
operation occurred. No holdout path, identity, or content was opened. Provider
calls and new budget reservations made by recovery are zero. Historical
candidate response records and budget accounting remain intact.

A fresh-process import regression imports `bench.optimization.recovery` and
asserts that it does not load the production adapter, DSPy, LiteLLM,
`google.auth`, or the Vertex client. The recovery implementation constructs no
candidate or optimizer adapter.

## Mandatory stop and next boundary

The manager must review and commit this generic Gate 1 patch. Gate 2 must not be
run from this dirty checkout. After the manager supplies the exact clean commit,
the executor may reverify the private inventory and run the recovery command
under the handoff's separately recorded no-call authorization. GEPA still
requires a later explicit owner authorization; this report does not authorize
compute allocation, credentials, or the first proposer call.

The progress report, research activity log, and development ledger are not
updated at this checkpoint because the handoff assigns those final delivery
updates to the post-recovery Gate 2/3 report commit.
