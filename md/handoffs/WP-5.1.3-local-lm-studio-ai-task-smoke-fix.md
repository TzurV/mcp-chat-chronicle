# WP-5.1.3 Handoff: Local LM Studio AI-Task Smoke And Compatibility Fix

## Status

Ready for execution in a separate executor thread.

This is a focused operational/runtime patch before WP-5.1.2. It does not reopen
the accepted WP-5.1/WP-5.1.1 task semantics and does not implement teacher-reference
evaluation.

## Objective

Make the accepted YAML-defined Chronicle AI tasks complete successfully through the
owner's running local LM Studio server, starting with `conversation-summary` on a
short synthetic conversation and then proving all four tasks on short conversations.

Diagnose and fix the actual compatibility boundary across:

1. LM Studio's OpenAI-compatible endpoint;
2. LiteLLM's `lm_studio/` provider route;
3. Chronicle model-profile resolution and structured-output request;
4. Chronicle schema/evidence validation and result persistence;
5. privacy-safe, actionable failure reporting.

Do not mask the problem with mocks, disable validation globally, or begin WP-5.1.2.

## Current Environment And Reproduction History

The owner has completed the following setup on Windows:

- Poetry resolves correctly to `C:\work\Github\mcp-chat-chronicle\.venv`.
- LM Studio is installed.
- LM Studio local server is running on `127.0.0.1:1234`.
- `lms server status` reports the server running on port `1234`.
- LM Studio model: Community Model Qwen3.5-4B by Qwen.
- Local model format/quantization: GGUF `Q4_K_M`.
- Reported LM Studio context: `8192`.
- Reasoning: Off.
- `GET http://127.0.0.1:1234/v1/models` returns:
  - `qwen3.5-4b`;
  - `text-embedding-nomic-embed-text-v1.5`.
- The embedding model is not used for generation tasks.
- Project-local AI task/model YAML files now exist after `chronicle init`.
- Optional LiteLLM enrichment dependencies are installed or must be verified.

Initial model environment value:

```powershell
$env:CHRONICLE_LOCAL_MODEL = "qwen3.5-4b"
```

With that value:

- `conversation-summary --dry-run` succeeded;
- the dry run resolved `qwen3.5-4b`;
- the real call failed;
- LiteLLM printed its provider-list guidance twice, consistent with the configured
  initial call plus one retry;
- Chronicle stored a failed attempt and displayed only
  `provider: provider error from model provider`.

LiteLLM's current LM Studio documentation requires the provider route prefix:

```text
lm_studio/<model-id>
```

The owner then changed the intended value to:

```powershell
$env:CHRONICLE_LOCAL_MODEL = "lm_studio/qwen3.5-4b"
```

The owner reports that a second attempt using a shorter conversation also failed.
The exact second underlying provider/HTTP/schema error has not yet been established.
Do not assume the provider prefix was the only defect.

Relevant documentation:

- LiteLLM LM Studio provider: <https://docs.litellm.ai/docs/providers/lm_studio>
- LM Studio local server: <https://lmstudio.ai/docs/developer/core/server>
- LM Studio OpenAI-compatible endpoints: <https://lmstudio.ai/docs/developer/openai-compat>
- LM Studio structured output: <https://lmstudio.ai/docs/developer/openai-compat/structured-output>

Verify current behavior against installed versions rather than assuming the linked
documentation exactly matches the local installation.

## Source Of Truth

Read before changing anything:

- `md/master-plan.md`;
- `md/development-ledger.md`;
- `md/agent-operating-notes.md`;
- accepted WP-5.1 and WP-5.1.1 handoffs, completion reports, and validations;
- `ai-models.default.yaml` and packaged byte-identical resource;
- `ai-tasks.default.yaml` and packaged byte-identical resource;
- local git-ignored `.chronicle/ai-models.yaml` and `.chronicle/ai-tasks.yaml` without
  copying private configuration into tracked files;
- `src/chat_chronicle/ai.py` and `src/chat_chronicle/ai_config.py`;
- current AI adapter/config/execution/cache/CLI tests;
- current README local-AI setup edits.

## Worktree And Ownership

The PM worktree already contains unrelated uncommitted documentation edits in at
least README/planning/WP-5.1.2 files. Preserve and work with them. Do not revert,
overwrite, stage, or commit them.

The PM/manager exclusively owns staging and commits. Leave this delivery and all
rework uncommitted for PM validation.

## Required Diagnostic Sequence

Proceed layer by layer. Stop guessing once a layer produces concrete evidence.

### 1. Environment Preflight

From the repository root:

```powershell
poetry env info --path
lms server status
(Invoke-RestMethod http://127.0.0.1:1234/v1/models).data.id
```

Record privacy-safe versions for Python, LiteLLM, LM Studio CLI/server, and the
resolved local model ID. Do not install a second runtime or another model unless the
existing model is proven incompatible and the PM approves the substitution.

The executor process may not inherit the owner's terminal environment. Ensure each
test explicitly resolves:

```text
CHRONICLE_LOCAL_MODEL=lm_studio/qwen3.5-4b
```

Do not add that machine-specific choice to tracked private configuration.

If the sandbox blocks localhost while the owner's terminal can reach it, identify
that as a sandbox boundary and request only the scoped permission needed for the
smoke. Do not modify Chronicle to bypass sandboxing.

### 2. Direct LM Studio Health

Use invented content only. Prove through the OpenAI-compatible endpoint:

1. model listing works;
2. a minimal non-streaming `/v1/chat/completions` request to `qwen3.5-4b` succeeds;
3. the response contains usable assistant text;
4. a minimal JSON-object request succeeds;
5. a minimal JSON Schema structured-output request succeeds or returns a concrete,
   privacy-safe compatibility error.

Do not send any real Chronicle transcript during this layer.

If strict JSON Schema fails directly, determine whether the cause is LM Studio
version, model capability/load settings, request shape, grammar/schema limits, or
context configuration. Do not immediately set `structured_output: false` without
evidence.

### 3. Direct LiteLLM LM Studio Route

Using an injected/minimal diagnostic that is not committed as product code, prove:

- `lm_studio/qwen3.5-4b` routes to the configured local API base;
- no API key is required unless this LM Studio server has authentication enabled;
- a basic invented completion succeeds;
- the exact structured-output request shape used by Chronicle succeeds or returns a
  concrete error;
- LiteLLM strips/routes the provider prefix correctly while LM Studio receives the
  actual local model ID;
- no remote provider is contacted.

Do not use `openai/qwen3.5-4b` unless the dedicated `lm_studio/` route is proven
broken for the installed LiteLLM version and the alternative is justified with
tests. The accepted preference is the dedicated provider route.

### 4. Chronicle Synthetic End-To-End Smoke

Create a temporary synthetic DB with one short invented conversation that includes
stable normalized message IDs and timestamps. Use the real running LM Studio model,
not a mocked client.

Run in this order:

1. `conversation-summary --dry-run`;
2. real `conversation-summary`;
3. rerun unchanged summary to prove a cache hit;
4. `work-mode-classification`;
5. `last-activity`;
6. `title-assessment`.

Verify each successful result against its accepted Pydantic schema, evidence IDs,
deterministic dates, result status, actual provider/model provenance, and append-only
storage behavior.

If one task fails because Qwen produces invalid structured content, establish
whether the cause is request compatibility or model semantic/schema adherence.
Apply the narrowest fix consistent with accepted task contracts. Do not weaken
evidence checks, enums, date ownership, or title no-write behavior.

### 5. Short Real-Conversation Smoke

Only after the synthetic real-model smoke passes, ask the owner for or use the
owner-selected short real conversation ID. Do not default to long conversation 673.

Run all four tasks locally against that one short conversation. The report may show
only conversation ID, task names, statuses, timing/token aggregates, cache behavior,
and schema validity. Do not include title, transcript, summary, classification
reason, suggested title, evidence text, URL, path, UUID, or generated result content.

The local run is allowed to append AI task result rows. It must not change normalized
conversation/message/source content or FTS data.

## Context-Length Handling

The owner's current LM Studio context is `8192`. That may be sufficient for a short
smoke but is below the accepted overview task's maximum input of 50,000 characters.

Requirements:

- first prove a genuinely short synthetic/real conversation at 8192;
- expose/report selected character count and estimated/request token count in a
  privacy-safe way where available;
- fail clearly when selected input exceeds effective model context;
- do not silently truncate outside the accepted selector;
- document 16K/32K as operational settings for longer chats only after the short
  smoke succeeds;
- do not make a larger context a substitute for fixing provider/schema routing.

## Failure Diagnostics Requirement

The current CLI message `provider error from model provider` is insufficient for a
local runtime smoke.

Improve diagnostics narrowly so a user can distinguish at least:

- unknown/missing LiteLLM provider route;
- localhost connection failure;
- model not loaded/not found;
- authentication configuration failure;
- context-length rejection;
- unsupported request parameter or structured-output mode;
- HTTP status/provider API error;
- invalid JSON;
- output-schema validation;
- evidence validation;
- timeout/rate limit.

Diagnostics must remain privacy-safe:

- never print prompts, transcript text, model output, API keys, URLs containing
  credentials, private paths, titles, or source identifiers;
- preserve only allowlisted exception class/category, HTTP status, safe provider
  error code, and a bounded sanitized detail;
- keep stored failure rows retryable;
- test redaction against secrets and transcript fragments;
- do not enable verbose LiteLLM request/response logging by default.

If the root cause can be solved only by local YAML configuration, still improve the
README and safe error guidance, but do not add unnecessary application abstractions.

## Configuration And README Requirements

Make the working model syntax explicit:

```text
lm_studio/qwen3.5-4b
```

README must cover:

- GGUF and `Q4_K_M` at a concise operational level;
- server start/status and `/v1/models` verification;
- selecting the generation model rather than `text-embedding-*`;
- LiteLLM's required `lm_studio/` prefix;
- temporary PowerShell environment setup;
- context/reasoning recommendation for the short smoke;
- dry-run versus real call;
- structured-output fallback only when supported by evidence;
- where successful/failed attempts are stored and how cache/retry behaves;
- privacy warning for logs and real outputs.

Root and packaged default YAML resources must remain byte-identical if either is
changed. Do not track `.chronicle` configuration.

## Required Tests

Use synthetic content for committed tests. Add focused coverage for:

1. raw LM Studio model ID versus required provider-prefixed resolved ID behavior;
2. accepted `lm_studio/` profile resolution and local/remote classification;
3. API base propagation;
4. no API-key requirement for unauthenticated LM Studio;
5. structured-output request propagation;
6. safe provider-route/connection/model/context/parameter error categorization;
7. transcript/key/output redaction from CLI and stored failure details;
8. failed attempts remain retryable and successful reruns cache;
9. all four task schemas through an injected provider response;
10. normal non-AI commands remain zero-LLM and regression-clean;
11. root/package template identity and installed-wheel initialization if templates
    change.

Tests must not require LM Studio or a downloaded model in CI. The real local-model
smokes are manual validation evidence in addition to deterministic automated tests.

## Acceptance Criteria

WP-5.1.3 is accepted only when:

1. The concrete second failure is identified and documented with privacy-safe evidence.
2. Direct LM Studio invented text and structured-output probes are understood.
3. Direct LiteLLM `lm_studio/qwen3.5-4b` invented probes succeed.
4. `conversation-summary` completes through Chronicle on a short synthetic conversation using the real local model.
5. All four tasks complete and validate on that synthetic conversation.
6. An unchanged successful rerun is a cache hit with no second model call.
7. All four tasks complete on one owner-selected short real conversation, or any remaining model-quality failure is reported precisely rather than mislabeled as infrastructure success.
8. Real smoke results contain valid schema/evidence/date contracts.
9. No normalized archive content, title, source data, or FTS row is modified.
10. Failure messages are actionable and privacy-safe.
11. README/config instructions reproduce the working setup from a fresh local initialization.
12. Focused and full tests pass; Ruff and `git diff --check` pass.
13. No private DB/export/transcript/model output/log/config artifact is tracked.
14. WP-5.1.2 code or remote teacher execution is not started.
15. The detailed completion report exists at the exact required path.

## Required Validation Commands

Follow `md/agent-operating-notes.md` and verify Poetry first:

```powershell
poetry env info --path
poetry run pytest <focused WP-5.1.3 tests> -q
poetry run pytest
poetry run ruff check .
poetry run chronicle --help
poetry run chronicle --ai-task list
git diff --check
git status --short
git ls-files "*.db" "*.sqlite" "*.zip" ".chronicle/*" "exports/*"
```

Also report privacy-safe aggregate evidence for direct LM Studio, direct LiteLLM,
synthetic Chronicle, cache rerun, and short real-conversation smokes.

## Completion Report

Write the detailed report at exactly:

```text
md/handoffs/reports/WP-5.1.3-completion-report.md
```

The report must include:

1. Status: `ready for PM validation`, `partial`, or `blocked`.
2. Root cause and why the initial prefix correction was insufficient or not applied.
3. Installed runtime/provider/model versions and privacy-safe configuration summary.
4. Layer-by-layer diagnostic results.
5. Files changed and why.
6. Final working model/profile syntax.
7. Structured-output compatibility decision.
8. Failure-diagnostic/redaction behavior.
9. Synthetic real-model smoke aggregate results for all four tasks.
10. Short real-conversation smoke aggregate results without generated/private content.
11. Cache/retry/result-persistence evidence.
12. Focused/full/Ruff/help/diff evidence.
13. Git privacy/tracking evidence.
14. Known limitations, including context requirements and semantic quality not yet evaluated.
15. Requirement-by-requirement acceptance checklist.
16. Final `git status --short` and confirmation that nothing was staged or committed.

## Executor Delivery Rules

- Do not commit or stage any files.
- Do not mark the ledger `Accepted`; only the PM does that.
- Leave status `Ready for PM validation` only when every acceptance criterion passes.
- Preserve all PM/user/pre-existing worktree changes.
- Do not paste private prompts, outputs, transcripts, titles, paths, or IDs into the
  delivery message or completion report beyond an owner-approved numeric
  conversation ID used as privacy-safe smoke evidence.
- Return a concise delivery message pointing to the completion report.
