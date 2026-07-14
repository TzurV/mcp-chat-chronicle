# WP-1.2.1 Validation Review — OpenAI Split Export Compatibility

## Decision

**Accepted.**

WP-1.2.1 satisfies the handoff: the ChatGPT/OpenAI official-export importer now supports the current split `conversations-*.json` OpenAI export layout while preserving legacy `conversations.json` behavior.

## Validation Performed

Reviewed:

- `md/handoffs/WP-1.2.1-openai-split-export-compatibility.md`
- `md/handoffs/reports/WP-1.2.1-completion-report.md`
- `src/chat_chronicle/adapters/chatgpt_export.py`
- `src/chat_chronicle/cli.py`
- `tests/test_chatgpt_export.py`
- `tests/test_cli_ingest_stats.py`

Commands run by PM validation:

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv
```

```text
poetry run pytest tests/test_chatgpt_export.py -q
27 passed
```

```text
poetry run pytest
144 passed
```

```text
poetry run ruff check .
All checks passed!
```

```text
poetry run chronicle --help
```

The CLI still lists `ingest`, `ingest-folder`, `collect`, `scan-local`, `stats`, `search`, and `open`.

## Real Export Smoke

PM validation ingested the owner OpenAI split export directly with auto-detection into a temporary DB outside the repo:

```text
poetry run chronicle ingest exports\openai\<owner-zip>.zip --provider auto --db-path C:\tmp\wp121-pm-validation-20260713-auto.db
provider: chatgpt
conversations seen: 422
added: 422  updated: 0  skipped: 0
parse errors: 92
```

Stats on the same temporary DB:

```text
total conversations: 422
total messages: 5166
Counts by provider: chatgpt = 422
Recent ingest run: seen 422, added 422, updated 0, skipped 0, errors 92
```

No transcript text was printed or copied into this review.

## Acceptance Notes

- Split ZIP export auto-detects as `chatgpt`.
- Split ZIP export ingests directly; no manual merged JSON workaround is needed.
- Legacy `conversations.json` behavior remains covered by tests.
- `thoughts` and `reasoning_recap` no longer produce noisy parse errors.
- The remaining 92 real-export parse warnings are `non_text_content_part` warnings for opaque dict parts; those remain fail-visible and are acceptable for this WP.
- No real export ZIP, DB, private transcript, or generated merged JSON is tracked.

## Residual Risk

The importer still skips opaque structured `content.parts` dicts instead of attempting to extract text from unknown shapes. This is correct for the current scope, but a future follow-up can inspect those shapes if search quality appears to miss visible user-facing content.

## Follow-Up

Commit WP-1.2.1, then run the prototype private smoke against the repo-local archive DB with the real OpenAI export and Claude Code local history.
