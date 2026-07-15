# WP-5.1.3 Completion Report: Local LM Studio AI-Task Smoke And Compatibility Fix

## Status

`ready for PM validation`

The deterministic implementation, direct localhost diagnostics, full synthetic
real-model smoke, and owner-selected short real-conversation smoke are complete.
All four tasks complete through LM Studio, and unchanged summary reruns are cache
hits with no new model call or result row.

## Manager summary

WP-5.1.3 is implemented and ready for PM validation. Chronicle now supports the
tested local LM Studio route end to end with strict structured output, actionable
and privacy-safe failures, context preflight, deterministic evidence enforcement,
configuration-source diagnostics, and documented local operating guidance.

The original route/configuration failure and the later schema, timeout, and evidence
failures were each reproduced at the narrowest useful layer and fixed without
weakening the accepted stored contracts. All four AI tasks passed on synthetic data
and on owner-selected conversation 699. The additional owner-selected conversation
685 summary also passed after evidence IDs were constrained to the exact selected
message set. The full automated suite passed with 371 tests, Ruff passed, and no
normalized archive data was mutated. The changes remain unstaged and uncommitted for
manager review.

## Root cause

The initial unprefixed value `qwen3.5-4b` was not a LiteLLM route. LiteLLM could not
select a provider, which Chronicle collapsed into the generic message `provider
error from model provider`. The required working value is:

```text
lm_studio/qwen3.5-4b
```

Adding the prefix was necessary but insufficient. With the prefixed route, direct
LM Studio text and strict JSON Schema calls and direct LiteLLM calls succeeded.
Chronicle then reached client-side Pydantic validation and exposed the concrete
second failure:

- summary JSON had the correct keys/types/evidence, but the model emitted one
  compound sentence while the accepted contract requires 2-5 sentences;
- last-activity JSON had the correct keys/types/evidence, but emitted a null action
  with `next_action_basis=explicit`, violating the accepted relationship.

Those relationships were enforced only by Pydantic validators and were absent from
the provider JSON Schema. The patch makes them structural at the provider boundary:
summary is requested as a 2-5 item sentence array and finalized to the accepted
stored string; last activity requests either null or a nested action+basis object
and finalizes it to the accepted stored `next_action`/`next_action_basis` fields.
Stored v1 result shapes and semantic validation remain unchanged. Finalizer identity
advanced to version 2 so pre-patch successes cannot cross-hit.

Conversation 699 exposed a separate operational boundary after schema compatibility
was fixed: its 7K-character selection fit the 8192-token context comfortably, but
schema-constrained local generation exceeded the template's 60-second timeout. The
old timeout plus one retry caused two approximately two-minute failures. The local
template now allows 180 seconds and uses zero automatic retries, avoiding duplicate
queued generations while leaving both fields locally configurable. All four real
tasks then completed in 65-105 seconds each.

A later owner smoke on conversation 685 exposed an evidence-adherence boundary:
the complete selection contained 56 meaningful messages with non-contiguous local
IDs because excluded normalized records occupied gaps. Qwen returned valid structured
content but cited an ID outside the selected set, so Chronicle correctly persisted a
retryable `evidence_validation` failure with no result JSON. Provider schemas now
bind `evidence_message_ids.items.enum` to the exact structurally selected IDs for
every task (or require an empty list for an empty selection). Client-side evidence
validation remains mandatory. Synthetic regressions cover all four tasks, exact
non-contiguous IDs, and the empty-selection case.

The owner reran `conversation-summary` on conversation 685 after this fix. It
completed successfully through `lm_studio` / `qwen3.5-4b` in 197,906 ms with 6,774
reported total tokens. The stored final schema validated; both cited evidence IDs
belonged to the 56-message selected set; and both application-owned dates exactly
matched DB metadata. This report intentionally omits the generated summary and IDs.

## Runtime and configuration

- Python: 3.12.0 in the repository `.venv`.
- LiteLLM: 1.83.0.
- LM Studio CLI: commit `9902c3a`; the CLI reports the server running on port 1234.
- LM Studio desktop/server semantic version: not exposed by the CLI/version command,
  standard desktop metadata lookup, or the `/v1/models` response header.
- Generation model exposed by `/v1/models`: `qwen3.5-4b`.
- Separate embedding model was present and was not used for generation.
- Model artifact: owner-reported Community Qwen3.5-4B GGUF `Q4_K_M`.
- Reasoning: owner-reported off.
- Configured smoke context: 8192 tokens.
- Tracked default request policy: 180-second timeout and zero automatic retries.
- Endpoint: loopback OpenAI-compatible `/v1`; no API key required.

The tracked model template remains environment-driven and now includes an explicit
8192 context-window setting for the short smoke. Initial controlled validation used
a temporary copy of the tracked templates. The owner later calibrated the private
repository-local profile independently; it is not a tracked deliverable and was not
edited by this implementation. `--verbose` made that distinction observable without
printing a private absolute path.

## Layer-by-layer diagnostics

### Environment and server

- Poetry resolved to the repository virtualenv.
- The `lms` executable was not inherited on the process PATH, but the standard
  per-user CLI location worked without changing PATH.
- Server status reported running on port 1234.
- `/v1/models` returned HTTP 200 and exposed the expected generation model.

### Direct LM Studio probes

All probes used invented text only.

- Minimal non-streaming text completion: succeeded with usable assistant text.
- `response_format.type=json_object`: rejected with HTTP 400; this server accepts
  `json_schema` or `text`, not `json_object`.
- Minimal strict JSON Schema completion: succeeded and parsed as valid JSON.

This evidence means `structured_output: true` is the correct configuration for the
installed runtime. Disabling it would select a JSON-object mode known to fail here.

### Direct LiteLLM probes

- `lm_studio/qwen3.5-4b` plus the loopback API base completed invented text.
- The same route completed a strict JSON Schema probe.
- No API key was supplied.
- LiteLLM routed with the prefix while the endpoint used the local model.
- The configured API base was loopback; no remote fallback was configured or used.

### Chronicle synthetic smoke

One temporary conversation with four invented normalized messages was used.

- Dry-run: one selection, zero cache hits, 579 selected characters, estimated 306
  input tokens, estimated 656 request tokens including maximum output, configured
  context 8192, and zero model calls.
- `conversation-summary`: completed and validated.
- `work-mode-classification`: completed and validated.
- `last-activity`: completed and validated.
- `title-assessment`: completed and validated.
- Unchanged summary rerun: cached with no appended result/model call.
- Forced summary rerun: completed and appended a new auditable success.
- Final provenance after normalization: provider `lm_studio`, model `qwen3.5-4b`.

Across the final executed successes (four tasks plus one forced summary), aggregate
stored latency was 157,764 ms and aggregate reported tokens were 2,347. The summary
had two executed successes because of the explicit force check; the cache rerun did
not append a row.

The diagnostic database contains one conversation, four normalized messages, four
distinct successfully completed task names, seven total success rows across all
pre/post-fix probes, two retryable pre-fix failure rows, and zero foreign-key
errors. Normalized conversation/message counts remained one/four and FTS remained
unchanged at zero rows. No title/source/normalized/FTS write path was invoked.

### Short real-conversation smoke

The owner selected numeric conversation ID 699. No title, transcript, prompt,
generated field, reason, URL, path, UUID, or source identifier was printed or added
to this report. Long conversation 673 was not used.

Dry-run evidence:

- conversation summary: 6,996 selected characters; 1,910 estimated input tokens;
  2,260 maximum estimated request tokens;
- work-mode classification: 6,996 characters; 1,954 input tokens; 2,204 request;
- last activity: 4,177 characters; 1,291 input tokens; 1,641 request;
- title assessment: 6,996 characters; 1,948 input tokens; 2,198 request;
- configured context: 8,192; all four were safely within the window and initially
  missed cache under the final model configuration.

Final aggregate results:

- `conversation-summary`: success; 105,468 ms; 2,565 reported total tokens;
- `work-mode-classification`: success; 89,936 ms; 2,529 tokens;
- `last-activity`: success; 64,672 ms; 1,671 tokens;
- `title-assessment`: success; 80,983 ms; 2,486 tokens;
- provider/model for every success: `lm_studio` / `qwen3.5-4b`;
- all four final Pydantic schemas valid;
- every evidence ID belongs to that attempt's selected normalized messages;
- summary start and last-active dates exactly equal DB-owned conversation metadata;
- unchanged summary rerun: cache hit, no model call, no appended row.

Before/after archive counts remained 699 conversations, 27,681 messages, 699 FTS
rows, and five sources. `PRAGMA foreign_key_check` returned zero errors. AI result
rows were appended as designed; normalized archive, title, source, message, and FTS
content was not modified. Two timeout failures from the superseded 60-second policy
remain append-only and retryable as audit evidence.

## Owner-requested add-ons and iterative validation

The following requests were added during hands-on validation and are included in
the completed scope:

1. The requested conversation was changed to ID 699. Dry-run, all four real-model
   tasks, schema/evidence/date checks, archive-integrity checks, and the unchanged
   summary cache check were completed for that ID.
2. PowerShell command lines were supplied for running the same task loop locally,
   including explicit conversation and database arguments.
3. After the default 60-second limit timed out, the tracked local timeout was raised
   to 180 seconds and automatic retries were set to zero. Timeout failures now tell
   the operator to increase `timeout` in the active model catalog and retry, while
   recommending zero retries during local calibration to avoid duplicate queued
   generations.
4. When a larger value in `.chronicle/ai-models.yaml` appeared not to take effect,
   investigation showed that configuration-source visibility was missing. A root
   `--verbose` option was added. It reports the selected catalog source, symbolic
   catalog paths, effective task settings, endpoint/credential classification,
   timeout, retries, concurrency, structured-output mode, and context window without
   disclosing selected content, credentials, or private absolute paths.
5. Verbose output confirmed that runtime behavior depends on the active catalog,
   including any `CHAT_CHRONICLE_AI_CONFIG_DIR` override. It also distinguishes the
   tracked defaults (`timeout: 180`, `retries: 0`, `context_window: 8192`) from an
   owner's separately calibrated repository-local values.
6. Conversation 685 then progressed past timeout but produced a correctly rejected
   `evidence_validation` failure. Analysis showed the model had cited outside the
   56-message selected set. Provider JSON Schema is now bound per attempt to the
   exact, potentially non-contiguous selected IDs, with the existing client-side
   check retained as defense in depth.
7. The owner reran conversation 685 after that fix. The summary completed, its final
   schema validated, every evidence ID belonged to the selected set, and both
   application-owned dates exactly matched database metadata. Generated private
   content and concrete evidence IDs are intentionally omitted from this report.

These add-ons did not broaden Chronicle's write scope: only append-only AI result
rows were created by executions. No title, source, normalized message, conversation,
or FTS content was rewritten.

## Files changed

- `src/chat_chronicle/ai.py`: structural provider schemas/finalizers, safe provider
  categories, provenance normalization, token estimate/context preflight, validation
  facts, stronger redaction, and per-attempt evidence-ID schema binding.
- `src/chat_chronicle/ai_config.py`: optional context window and actionable rejection
  of an unprefixed default LM Studio environment value.
- `src/chat_chronicle/cli.py`: privacy-safe dry-run character/token/context reporting
  and `--verbose` effective catalog/task/profile summaries that label environment
  overrides without printing private absolute paths.
- Root and packaged AI task templates: byte-identical provider-shape prompt updates.
- Root and packaged model templates: byte-identical 8192 context setting and
  180-second/no-retry local request policy.
- Focused AI/config/execution/CLI/conversation-intelligence tests: route, API base,
  no-key, schema propagation, error categories/redaction, context retryability,
  provider finalization, and cache identity coverage.
- `README.md`: reproducible LM Studio setup, prefix, GGUF/quantization, short versus
  longer context guidance, strict-schema decision, storage/cache/retry behavior, and
  privacy guidance.
- This report.

Pre-existing PM edits in the README, planning documents, ledger, WP-5.1.2 handoff,
and the untracked WP-5.1.3 handoff were preserved. Nothing was staged or committed.

## Failure diagnostics and redaction

Provider failures now distinguish:

- missing/unknown provider route;
- connection failure;
- model missing/not loaded;
- authentication failure;
- context-length rejection;
- unsupported parameter/structured-output mode;
- provider HTTP status and generic provider rejection;
- timeout and rate limit.

Existing `invalid_json`, `schema_validation`, and `evidence_validation` categories
remain separate. Provider details retain only bounded allowlisted facts: category,
exception class, HTTP status, and safe provider code. Provider-controlled raw text
is not retained. Schema failures expose only known field locations and validation
types, never values. Redaction removes credentials, transcript fragments,
credential-bearing URLs, and private Windows paths. Failed rows remain append-only
and retryable; provider output is not stored on failure. Timeout failures explicitly
recommend increasing the selected profile's `timeout` in the active
`ai-models.yaml`, retrying, and keeping local retries at zero while calibrating.

## Context handling

Dry-run reports selected characters, a conservative four-characters-per-token input
estimate, maximum estimated request tokens including configured output, and the
configured context window. Before a provider call, Chronicle records a retryable
`context_length` failure when estimated input plus maximum output exceeds that
window. It does not silently truncate outside the accepted deterministic selector.
8192 is validated for both short smokes; 16K/32K are documented operational settings
for longer chats, not substitutes for route/schema compatibility.

## Automated validation

- Focused WP-5.1.3/accepted AI matrices: passed, including the final verbose-config
  and exact evidence-schema subsets.
- Full suite: 371 passed in 34.99 seconds after the evidence-schema update.
- `poetry run ruff check .`: all checks passed.
- `poetry run chronicle --help`: passed; normal commands remain present.
- `poetry run chronicle --ai-task list`: all four tasks and local profile listed
  without a model call.
- Verbose CLI tests prove catalog-source/override labels and effective timeout,
  retry, context, schema, selector, and generation reporting without private paths
  or selected content.
- `git diff --check`: passed.
- Root/package template identity: covered and passed in the focused/full suite.
- Tracked DB/SQLite/ZIP/local-config/export query: no output.

## Known limitations

- Token estimates are deliberately conservative and are not a model-specific
  tokenizer count.
- Local schema-constrained inference took 65-105 seconds for conversation 699;
  the larger conversation 685 summary took about 198 seconds. Performance and
  semantic quality depend on hardware/model settings.
- Semantic task quality is not evaluated here; WP-5.1.2/WP-5.2 remain separate.
- `structured_output: false` depends on provider support for JSON-object mode and is
  specifically incompatible with the probed LM Studio server.
- LM Studio did not expose a semantic desktop/server version through the available
  local metadata surfaces; the CLI commit and live endpoint behavior are recorded.

## Acceptance checklist

1. Concrete second failure identified: complete.
2. Direct LM Studio invented text/schema behavior understood: complete.
3. Direct LiteLLM dedicated route probes: complete.
4. Synthetic real-model summary: complete.
5. All four synthetic real-model tasks: complete.
6. Unchanged cache hit with no second call: complete.
7. Owner-selected short real conversation: all four tasks complete for ID 699;
   additional summary validation complete for ID 685.
8. Schema/evidence/date contracts: complete for synthetic and both real smokes.
9. No normalized/title/source/FTS mutation: complete for synthetic and real smokes.
10. Actionable privacy-safe failures: complete.
11. Reproducible README/config guidance: complete.
12. Focused/full/Ruff/help/diff validation: complete.
13. No private artifact tracked: complete.
14. WP-5.1.2/remote teacher work not started: complete.
15. Detailed report at required path: complete.

## Working tree

Final status contains pre-existing PM documentation edits plus the uncommitted
WP-5.1.3 source/template/test/README/report changes:

```text
 M README.md
 M ai-models.default.yaml
 M ai-tasks.default.yaml
 M md/development-ledger.md
 M md/handoffs/WP-5.1.2-real-data-teacher-reference-corpus.md
 M md/master-plan.md
 M src/chat_chronicle/ai.py
 M src/chat_chronicle/ai_config.py
 M src/chat_chronicle/cli.py
 M src/chat_chronicle/resources/ai-models.default.yaml
 M src/chat_chronicle/resources/ai-tasks.default.yaml
 M tests/test_ai_adapter.py
 M tests/test_ai_config_matrix.py
 M tests/test_ai_execution_matrix.py
 M tests/test_cli_ai_tasks.py
 M tests/test_conversation_intelligence.py
?? md/handoffs/WP-5.1.3-local-lm-studio-ai-task-smoke-fix.md
?? md/handoffs/reports/WP-5.1.3-completion-report.md
```

Nothing was staged or committed.
