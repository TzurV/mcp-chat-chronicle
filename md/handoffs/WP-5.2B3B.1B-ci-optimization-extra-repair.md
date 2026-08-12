# WP-5.2B3B.1B Handoff: CI Optimization-Extra Repair

## Status

Ready for manager review and execution from the clean manager commit that
contains this handoff.

This is a narrow CI dependency-installation repair discovered after completion
of the WP-5.2B3B.1B Gate 2/3 executor delivery. It must be completed before any
GEPA authorization or further optimization work.

Diagnostic baseline: `fbe1f12a0d872902c088fce1c830cdc81b90b90a` on `main`.

## Incident summary

GitHub Actions ran:

```text
poetry install -E mcp
poetry run pytest
```

The full test suite then reported:

```text
66 failed, 540 passed, 1 skipped
```

The dominant failure was:

```text
ModuleNotFoundError: No module named 'dspy'
RuntimeError: optimizer dependencies are absent; install the 'optimization' extra
```

Sixty-five failures are direct optimizer dependency/compatibility failures. The
remaining CLI lifecycle assertion exited with status 2 after entering the same
optimizer execution path and is treated as a downstream symptom unless a fresh
run with the correct extras proves otherwise.

## Confirmed root cause

The project correctly declares optimization dependencies as optional:

```toml
[project.optional-dependencies]
optimization = [
    "dspy==3.3.0; python_version < '3.15'",
    "gepa[dspy]==0.1.1; python_version < '3.15'",
]
```

`poetry.lock` already contains the `optimization` extra and the accepted pinned
DSPy/GEPA versions. No dependency declaration or lock regeneration is currently
indicated.

The CI workflow, however, installs only the `mcp` extra while running every
test, including `tests/test_bench_optimization.py`. Those tests deliberately
exercise real, network-free DSPy 3.3 types and APIs and therefore require the
`optimization` extra. The local validation environment had those dependencies
installed, which explains why 132 focused optimizer tests and the full local
suite passed while the clean GitHub runner failed.

This is a CI environment parity defect. It is not evidence that the accepted
checkpoint recovery, P0 result, Bootstrap result, or private optimizer state is
invalid.

## Goal

Make the GitHub Actions test environment install every optional dependency
required by the test suite it executes, while preserving the public package's
optional-extra design.

The expected minimal correction is to install both existing extras in the CI
dependency step, for example:

```yaml
- name: Install dependencies
  run: poetry install -E mcp -E optimization
```

An equivalent supported Poetry syntax is acceptable if it is clearer and is
proved on both matrix operating systems. Do not make DSPy or GEPA unconditional
runtime dependencies merely to fix CI.

## Required work

1. Start from the exact clean manager commit containing this handoff.
2. Confirm `.github/workflows/ci.yml` still runs the full suite on:
   - Ubuntu and Windows;
   - Python 3.11 and 3.12.
3. Confirm `pyproject.toml` and `poetry.lock` still declare and lock:
   - `dspy==3.3.0`;
   - `gepa[dspy]==0.1.1`;
   - the `optimization` extra.
4. Change only the CI dependency installation needed to provide both `mcp` and
   `optimization` to the existing full-suite job.
5. Do not skip, deselect, mark, or conditionally suppress optimizer tests.
6. Do not catch or reinterpret missing optimizer dependencies in production
   code. `verify_compatibility()` must continue to fail clearly when a user
   invokes optimizer execution without the extra.
7. Do not change optimizer behavior, schemas, prompts, models, budgets,
   authority, recovery, or retry contracts.
8. Do not regenerate `poetry.lock` unless the accepted extra installation fails
   because the lock is genuinely inconsistent. If regeneration appears
   necessary, stop and report the exact resolver evidence before changing it.
9. Add no networked tests and make no provider/model call.

## Required regression and validation

Validate from a clean environment representative of CI, not only from the
existing developer `.venv` that already contains optimization packages.

At minimum, prove:

1. The CI install command succeeds from the committed lockfile.
2. The installed environment reports the exact accepted versions without
   initializing credentials or a provider:

   ```text
   dspy 3.3.0
   gepa 0.1.1
   ```

3. The real DSPy compatibility check passes network-free.
4. `tests/test_bench_optimization.py` passes in full.
5. The repository full suite passes.
6. The CLI smoke test still passes.
7. Ruff, Poetry validation, and diff checks pass.

Run at minimum:

```powershell
poetry check
poetry run python -c "import importlib.metadata as m; assert m.version('dspy') == '3.3.0'; assert m.version('gepa') == '0.1.1'"
poetry run python -c "from bench.optimization.compat import verify_compatibility; assert verify_compatibility()['compatible'] is True"
poetry run pytest tests/test_bench_optimization.py -q
poetry run pytest -q
poetry run ruff check .
poetry run chronicle --help
git diff --check
git diff --cached --name-only
```

The manager should also require the pushed GitHub Actions matrix to pass on all
four OS/Python combinations. A local pass alone does not close this CI incident.

## Negative regression boundary

Preserve the optional dependency contract:

- ordinary Chronicle installation/import must remain usable without DSPy or
  GEPA;
- explicit optimizer execution without the `optimization` extra must still
  fail with the current actionable dependency message; and
- CI may install the extra because CI chooses to run optimizer tests, without
  making the extra mandatory for all end users.

If practical without broadening the patch, demonstrate ordinary-import
isolation in a clean base-only environment. Do not create a complex new matrix
or duplicate the entire test run solely for that proof unless manager review
requests it.

## Safety and data boundary

This repair is repository- and CI-only.

Do not:

- access or modify ignored private optimizer evidence;
- rerun recovery, P0, or Bootstrap;
- start GEPA;
- allocate or access RunPod;
- access ADC or credentials;
- make Vertex, Gemini, fixed-judge, candidate-model, or other provider calls;
- inspect training or holdout content; or
- change the retained Pod or private network volume.

The stopped-resource and recovered-readiness evidence from WP-5.2B3B.1B remains
authoritative and must not be rewritten as part of this CI repair.

## Expected files changed

Expected implementation change:

- `.github/workflows/ci.yml`

Expected reporting change:

- a concise completion report under `md/handoffs/reports/` documenting the
  clean-environment install, local validation, and four-job GitHub Actions
  result.

Any production Python, `pyproject.toml`, `poetry.lock`, optimizer evidence, or
additional workflow change requires a specific evidence-backed explanation.

## Completion report requirements

Report:

- the exact failed CI run/job context supplied by the manager;
- root cause and why local validation did not reproduce it;
- exact workflow change;
- confirmation that package optionality remains unchanged;
- dependency/version verification;
- focused and full local results;
- GitHub Actions results for Ubuntu/Windows and Python 3.11/3.12;
- confirmation of zero provider, credential, private-data, holdout, and RunPod
  activity;
- files changed; and
- final unstaged Git status.

## Stop conditions

Stop and report before broadening the patch if:

- installing the existing `optimization` extra does not resolve the failures;
- the remaining CLI failure persists after DSPy/GEPA are installed;
- Poetry resolves versions other than DSPy 3.3.0 and GEPA 0.1.1;
- the lockfile must change;
- a production-code or test-skip change appears necessary;
- any test attempts network, credential, model, or provider access; or
- any private optimizer or holdout artifact would be accessed.

## Acceptance criteria

1. CI installs both `mcp` and `optimization` extras from the accepted lockfile.
2. DSPy 3.3.0 and GEPA 0.1.1 are present in every full-suite CI job.
3. All 132 optimizer tests pass without network/provider activity.
4. The complete repository suite passes.
5. All four GitHub Actions OS/Python jobs pass.
6. Ordinary package optionality and the missing-extra failure contract remain
   unchanged.
7. No production optimizer behavior or private evidence changes.
8. All changes remain unstaged and uncommitted for manager validation.

## Commit boundary

The executor must leave changes unstaged and uncommitted. The manager owns the
handoff commit and the eventual CI repair/completion commit. Do not resume GEPA
work until this repair is accepted and the GitHub Actions matrix is green.
