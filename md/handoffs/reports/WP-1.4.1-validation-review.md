# WP-1.4.1 PM Validation Review

## Decision

Accepted.

WP-1.4.1 satisfies the handoff requirements for directory sweep support on the existing `chronicle ingest <path>` command.

## Review Summary

The implementation adds directory sweep behavior only when the provided directory is not already a recognized single source. This preserves the critical existing behavior for provider export directories, OpenAI Codex local sources, and Claude Code project sources.

The completion report includes the required evidence:

- status is `ready for PM validation`;
- changed files are listed;
- directory detection and sweep behavior are described;
- single-source directory preservation is explicitly called out;
- idempotency evidence is included;
- validation command results are included;
- privacy-safe manual smoke evidence is included;
- git status and privacy checks are included;
- limitations and follow-ups are documented.

## Independent Validation

Ran from `C:\work\Github\mcp-chat-chronicle`.

```powershell
poetry env info --path
```

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

```powershell
poetry run pytest tests/test_cli_ingest_stats.py -q
```

```text
.......................                                                  [100%]
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
174 passed in 29.17s
```

## Acceptance Criteria Check

| Criterion | Result | Notes |
| --- | --- | --- |
| `chronicle ingest <directory>` can ingest multiple supported child sources | Pass | Covered by synthetic mixed-source tests and manual smoke. |
| Recognized single-source directories still ingest as one source | Pass | Explicit regression test added. |
| Mixed-provider directory ingest works with `--provider auto` | Pass | ChatGPT, Claude, and OpenAI Codex synthetic sources covered. |
| Explicit-provider directory ingest only uses compatible sources | Pass | Incompatible source summary is tested. |
| Reruns are idempotent | Pass | Second run added `0` and skipped existing records; no duplicate DB rows. |
| Output summarizes discovered sources and aggregate results | Pass | Reported output includes parent path, discovered sources, totals, errors, and run IDs. |
| Tests and Ruff pass | Pass | Independently verified. |
| Completion report written at required path | Pass | `md/handoffs/reports/WP-1.4.1-completion-report.md`. |
| No private transcript, DB, export ZIP, JSONL, or dump committed | Pass | Git status/report show only source, tests, handoff, report, and ledger changes. |

## Residual Notes

- This does not replace the broader deferred WP-1.6 source-management workflow.
- The implementation intentionally uses existing provider detection and adapters only.
- For real owner smoke, the recommended command after commit is:

```powershell
poetry run chronicle ingest .\exports --provider auto --db-path .\.chronicle\chronicle.db
```

Rerun the same command once more to confirm owner-DB idempotency before relying on it for routine use.
