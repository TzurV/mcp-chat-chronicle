# Optional Local AI Tasks

Chat Chronicle's core archive, collection, and search commands have no AI
dependency and make no model calls. This document covers the separate, explicitly
invoked YAML-defined AI-task layer.

The AI-task layer is advanced, optional functionality. Its scaffolding and task
contracts exist, but model-quality evaluation and comparative benchmarking remain
work in progress.

## Install and discover tasks

```powershell
poetry run chronicle init
poetry install -E enrich
poetry run chronicle --ai-task list
```

`init` creates missing `.chronicle/ai-tasks.yaml` and
`.chronicle/ai-models.yaml` files without replacing the existing database or local
configuration. Existing local catalogs are kept unless `--force` is explicitly
supplied.

## First local setup with LM Studio

Chat Chronicle does not install or start a local model runtime. Install LM Studio
for Windows separately, then use its local OpenAI-compatible server.

For the first smoke test, use this conservative model choice:

```text
Model: qwen/qwen3.5-4b
Format: GGUF
Quantization: Q4_K_M
```

In LM Studio:

1. Open **Discover** and search for `qwen/qwen3.5-4b`.
2. Download the LM Studio Community GGUF `Q4_K_M` revision.
3. Load the model. For an initial short structured extraction test, disable model
   thinking. The tested 8192-token context is sufficient for a genuinely short
   conversation; use 16K or 32K for longer chats when memory permits.
4. Open **Developer**, keep the bind address at `127.0.0.1`, set port `1234`, and
   start the server. Do not bind to `0.0.0.0` unless network exposure and
   authentication have been deliberately configured.

Verify the server and obtain the exact model ID it exposes:

```powershell
lms server status
(Invoke-RestMethod http://127.0.0.1:1234/v1/models).data.id
```

Select a chat/generation model from the returned IDs, not an embedding model such
as `text-embedding-*`. LiteLLM requires its LM Studio provider prefix:

```powershell
$env:CHRONICLE_LOCAL_MODEL = "lm_studio/<returned-chat-model-id>"
```

For the recommended first model:

```powershell
$env:CHRONICLE_LOCAL_MODEL = "lm_studio/qwen3.5-4b"
```

The prefix is part of LiteLLM routing; LM Studio still receives the local ID
`qwen3.5-4b`. Chat Chronicle rejects an unprefixed value from this default profile
before making a request. An unauthenticated loopback server needs no API key, so
keep `api_key_env: null` unless authentication was deliberately enabled.

## Optional Llama 3.2 1B evaluation floor

Keep Qwen3.5-4B `Q4_K_M` as the recommended initial functional smoke. For
evaluation work, the smaller
`bartowski/Llama-3.2-1B-Instruct-GGUF/Llama-3.2-1B-Instruct-Q4_K_M.gguf`
artifact is a useful floor candidate: it is deliberately small enough to expose
structured-output, instruction-following, latency, and context limitations.

Download that exact artifact in LM Studio, load it with an 8192-token context,
keep the server on `127.0.0.1:1234`, and verify that the returned generation
model ID is `llama-3.2-1b-instruct`:

```powershell
lms load llama-3.2-1b-instruct --context-length 8192 --parallel 1
lms server status
(Invoke-RestMethod http://127.0.0.1:1234/v1/models).data.id
$env:CHRONICLE_LOCAL_MODEL = "lm_studio/llama-3.2-1b-instruct"
```

Use temperature zero, no automatic retries, and one Chronicle task at a time.
The model advertises a larger maximum context, but only 8192 was tested for this
floor integration; advertised capacity is not evidence of useful long-context
quality or acceptable local latency. A schema-valid response can still be
semantically weak, while a captured schema failure is expected and useful
benchmark evidence. Do not relax task schemas or prompts to make a floor-model
failure pass.

## Context window, timeout, and dry run

Set `context_window` in `.chronicle/ai-models.yaml` to the context configured when
the model was loaded. Fresh initialization uses 8192 for the short-smoke profile.
Chat Chronicle reports selected characters and estimated input/request tokens
during `--dry-run`, and fails before the model call when the estimate plus requested
output exceeds the configured window.

The local template allows 180 seconds per schema-constrained generation and uses no
automatic retry. On slower hardware, raise `timeout` deliberately after a bounded
dry run; a retry can queue the same expensive generation twice.

Select a short or medium conversation, inspect the request, then run the task:

```powershell
poetry run chronicle recent -n 5
poetry run chronicle --ai-task conversation-summary --conversation-id <id> --dry-run --verbose
poetry run chronicle --ai-task conversation-summary --conversation-id <id>
```

`--verbose` prints a privacy-safe summary of the effective AI configuration. It
reports the selected profile's timeout, retries, context window, structured-output
mode, selector/schema, and generation limits. It does not print credentials,
prompts, transcript text, generated output, or an absolute configuration-override
path.

## Tasks and configuration

The tracked privacy-safe templates `ai-tasks.default.yaml` and
`ai-models.default.yaml` are copied to the local `.chronicle` directory by `init`.
Prompts/tasks and model profiles are separate, strictly validated YAML files. The
initial task contracts are:

- `conversation-summary`: a short factual overview with dates injected from
  normalized database metadata;
- `work-mode-classification`: whole-conversation classification as `manager`,
  `executor`, `one_off`, `mixed`, or `unknown`;
- `last-activity`: recent work and state from a bounded selection of meaningful
  messages;
- `title-assessment`: a suggestion-only title check that never updates stored
  conversation or source data.

For isolated automation or testing, `CHAT_CHRONICLE_AI_CONFIG_DIR` can point to a
directory containing `ai-tasks.yaml` and `ai-models.yaml`. Normal use keeps the
default `.chronicle` location.

Generation precedence is per field: the selected model profile supplies
`temperature` and `max_tokens` defaults, and a task may override either or both.
Chat Chronicle sends and caches the resolved effective values.

## Structured output and validation

The default local profile expects `http://127.0.0.1:1234/v1` and strict JSON Schema
output. Current LM Studio supports `json_schema`. Do not use
`structured_output: false` as a generic fallback. A provider proven not to support
schema output may explicitly use JSON-object mode; mandatory client-side Pydantic
validation still applies.

Evidence-bearing tasks bind the provider JSON Schema to the exact normalized
message IDs selected for that attempt. Client-side evidence validation rejects
incompatible provider responses.

Every executed attempt is appended to `ai_task_results`. Validated successes become
configuration/input-aware cache hits; sanitized failures remain retryable. `--force`
bypasses a successful cache entry and appends another auditable attempt.

## Privacy and remote execution

Runnable tasks require one `--conversation-id` or a positive bounded `--limit`.
Loopback profiles run locally by default. Cloud and non-loopback profiles are
blocked unless the invocation includes `--allow-remote`.

Selected transcript content is private. Prefer the local profile, inspect task
bounds with `--dry-run`, and use `--allow-remote` only when you intentionally
authorize transmission to a remote provider. Keep real outputs and logs private.
Do not enable verbose LiteLLM request/response logging because it can expose
prompts, transcripts, credentials, titles, and generated content.

Successful structured execution does not establish semantic model quality. The
real-data teacher-reference corpus and comparative benchmarking remain deferred.

## Troubleshooting

- If LM Studio is unreachable, confirm the server is running on
  `127.0.0.1:1234`.
- If the model is rejected before a request, confirm
  `CHRONICLE_LOCAL_MODEL` begins with `lm_studio/` and names a generation model.
- If the request exceeds the context window, choose a shorter conversation or load
  the model with a larger context and update `context_window` to match.
- If generation times out, increase the local profile timeout deliberately after a
  bounded dry run; do not add retries automatically.
- If schema validation fails, keep the failure private and inspect the sanitized
  diagnostic. Do not disable structured output without a direct provider probe.
