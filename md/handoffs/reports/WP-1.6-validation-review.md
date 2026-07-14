# WP-1.6 PM Validation Review

## Decision

Accepted after rework.

The initial implementation was substantially complete but required two fixes before acceptance:

1. DB path precedence had to be coherent across implementation, README, template, and tests.
2. Task Scheduler documentation had to be added because it was explicitly in handoff scope.

The refreshed implementation resolves both findings. WP-1.6 is accepted.

## Independent Validation

Ran from `C:\work\Github\mcp-chat-chronicle`.

```powershell
poetry env info --path
```

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

```powershell
poetry run pytest tests/test_cli_config_collect.py -q
```

```text
...............................                                          [100%]
```

```powershell
poetry run ruff check .
```

```text
All checks passed!
```

```powershell
poetry run pytest
```

```text
213 passed in 37.00s
```

```powershell
poetry run chronicle init --help
poetry run chronicle collect --help
poetry run chronicle --help
```

Result: all rendered successfully and showed the expected command surface.

## Original Findings And Rework Result

### 1. DB path precedence is incomplete relative to the handoff

The handoff says DB path precedence should be:

1. CLI `--db-path`
2. `CHAT_CHRONICLE_DB`
3. config YAML `paths.db`
4. built-in default `.chronicle/chronicle.db`

The implementation provides `resolve_db_path()` and uses it for `chronicle collect`, but existing read commands still call `connect(db_path)` directly and therefore do not consult config YAML:

- `chronicle stats`
- `chronicle search`
- `chronicle recent`
- `chronicle open`
- `chronicle ingest`

This also creates a documentation mismatch. `README.md` and `chronicle.default.yaml` say "Commands" resolve DB path using config, but the completion report says only `collect` applies config-aware precedence.

Rework result: pass.

The preferred fix was implemented:

- added shared `_resolve_effective_db_path()`;
- applied it to `ingest`, `stats`, `search`, `recent`, and `open`; `collect` already used config-aware resolution;
- preserved `--db-path` and `CHAT_CHRONICLE_DB` override behavior;
- added tests proving `stats`, `search`, and `recent` read config `paths.db`, plus CLI/env override and invalid-config cases;
- updated README/template/report wording so code and docs agree.

### 2. Task Scheduler documentation is missing

The handoff says Task Scheduler docs are in scope and should document a one-line Windows Task Scheduler setup for recurring `chronicle collect`.

The completion report notes this as a follow-up instead. That does not satisfy the handoff.

Rework result: pass.

README now includes an optional Windows Task Scheduler section with:

- `schtasks /Create` one-liner for recurring `chronicle collect`;
- `schtasks /Query`;
- `schtasks /Run`;
- `schtasks /Delete`;
- explicit note that Chat Chronicle never registers a scheduled task automatically.

## Non-Blocking Notes

- Treating WP-1.5 `scan-local` integration as N/A is acceptable because WP-1.5 had not landed.
- Adding PyYAML is acceptable and matches the handoff guidance.
- The config schema, `init`, `collect`, idempotency, and privacy posture look aligned with the handoff.
- The completion report itself is in the required directory and contains the required sections.

## Acceptance Criteria Check

| Criterion | Result | Notes |
| --- | --- | --- |
| `chronicle init` creates local config/DB/export structure explicitly | Pass | No package-install side effects; existing config/DB are preserved. |
| YAML stores DB/export/source/engine-interest defaults | Pass | `chronicle.default.yaml` and generated config are path-clean and validated. |
| `chronicle collect` ingests enabled configured sources | Pass | Uses accepted adapters and directory sweep behavior. |
| Missing optional paths are reported without crashing routine collection | Pass | Missing/empty/unsupported statuses are reported. |
| Reruns are idempotent | Pass | Reported and test-covered. |
| DB path precedence implemented and tested | Pass | Now applies to all DB-opening commands. |
| README documents workflow and Task Scheduler line | Pass | README covers init, collect, config, precedence, cloud export note, and optional `schtasks`. |
| Tests and Ruff pass | Pass | Independently verified. |
| Completion report written at required path | Pass | `md/handoffs/reports/WP-1.6-completion-report.md`. |
| No private data committed | Pass | Current changes are source, docs, tests, template, lockfile, and reports only. |
