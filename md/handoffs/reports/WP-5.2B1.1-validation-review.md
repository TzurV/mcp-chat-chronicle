# WP-5.2B1.1 Validation Review

## Decision

**Accepted on 2026-07-22.** The final delivery satisfies the complete acceptance chain. The real
synthetic Vertex gate passed 4/4, the private gate passed exactly 6 completed / 0 failed / 2
skipped, and the identical `--judge-cache-only` verification exited zero with no provider call.
Judge attempts and their aggregate identity, the candidate package, and both live and frozen
databases remained unchanged. Aggregate JSON and Markdown each retain one coherent judge section.

The final local rerun failure was traced to a serialization-only Windows newline difference in
`work-mode-confusion.csv`: universal-newline decoding changed canonical CRLF to LF although parsed
rows and metrics were identical. The accepted implementation canonicalizes newline-only and
parsed-row-equivalent legacy serialization, while semantic JSON differences still fail with a
logical artifact and field path and other semantic text/CSV differences still fail closed.

PM validation passed with repository-local Poetry environment, 81 focused tests, 424 full tests,
Ruff, `poetry check`, bench and Chronicle help checks, `git diff --check`, no staged files, and no
tracked `.chronicle`, database, SQLite, ZIP, or export artifacts. The historical rework sections
below remain as the audit trail and are superseded by this final decision.

## Validation Performed By The PM

- Poetry resolved to the repository-local `.venv`.
- `poetry run pytest tests/test_bench.py -q` passed: 41 tests.
- First-delivery `poetry run pytest -q` passed: 414 tests.
- `poetry run ruff check .` passed.
- `git diff --check` passed.
- The implementation diff and completion report were reviewed against the handoff.
- The executor left the delivery unstaged and uncommitted.

## Second Delivery Review Addendum

### Verified progress

- Real synthetic Vertex gate: 4 completed, 0 failed.
- Identical synthetic rerun: zero new Vertex calls.
- Private gate: 5 completed, 1 failed, 2 skipped-invalid.
- The one failure was valid JSON with normalized finish reason `stop`.
- Strict application validation identified only `rationale: string_too_long`.
- No automatic retry, truncation, or private scope expansion occurred.
- Candidate package, deterministic metrics, live DB, and frozen DB remained unchanged.
- Executor and PM full-suite runs: 418 passed; PM focused revalidation, Ruff, and diff checks also
  passed.

The automatic-thinking diagnosis is therefore resolved. The remaining problem is contract
alignment: the application requires a rationale of at most 500 characters, but the provider schema
currently describes `rationale` only as an unconstrained string.

### Superseding decision on the rationale provider field

The original handoff and first review conservatively excluded provider-side string length
constraints because the first Vertex request had not yet succeeded. That restriction is superseded
for the `rationale` field only.

Current Google API references expose `maxLength` for string schemas, and the installed LiteLLM
version maps Gemini 2.x `json_schema` requests to Vertex `responseJsonSchema`. The next rework must
therefore align the provider field with the existing strict application limit rather than weaken
the application model or truncate output.

Reference:

- Google Vertex schema reference: https://docs.cloud.google.com/go/docs/reference/cloud.google.com/go/vertexai/latest/genai

### Required second rework

1. Define the 500-character rationale limit once in application-owned judge contract code and use
   that value in both provider-schema construction and strict application validation where
   practical. Do not introduce two drifting numeric literals.
2. Add `maxLength: 500` to the provider-facing `rationale` schema.
3. Add a short provider-schema `description` stating that the rationale must be a concise verdict,
   contain no chain-of-thought, and remain within 500 characters.
4. Retain the application-side `max_length=500` validation as authoritative.
5. Do not truncate, summarize, repair, or retry an already generated over-limit rationale.
6. Increment the provider schema version. Increment the request-construction version as well if
   any system/user instruction changes.
7. Ensure the schema/version/hash change creates a fresh judge cache identity while preserving all
   existing attempts, including the 5/1/2 run.
8. Update the provider-keyword allowlist and schema tests for `description` and `maxLength`.

### Required gate sequence

The PM authorizes the same bounded remote scope:

1. Run all four real synthetic tasks with the revised provider schema.
2. Require 4 completed and 0 failed, with every rationale at most 500 characters.
3. Rerun the identical synthetic gate and prove zero new Vertex calls.
4. Only then use a fresh private scoring destination with the existing package and references.
5. Require exactly 6 completed, 0 failed, 2 skipped-invalid, and non-empty dimension means.
6. Assert every accepted private rationale is non-empty and at most 500 characters.
7. Rerun identically and prove zero new Vertex calls.
8. Reconfirm unchanged package, deterministic metrics, live DB, frozen DB, and historical attempts.

Because the provider schema identity changes, all six eligible private cases may require new judge
calls; this is expected and authorized for the same two-conversation scope. Do not regenerate
candidate outputs and do not expand the conversation scope.

If Vertex rejects `maxLength`, or any synthetic/private case still fails, stop once with bounded
diagnostics and leave status `Partial`. Do not remove the 500-character application bound.

### Additional tests

Add or update focused tests proving:

1. the provider schema contains `rationale.maxLength == 500`;
2. its rationale description carries concise/no-chain-of-thought guidance;
3. the strict application contract retains the same bound;
4. a 500-character rationale is accepted and a 501-character rationale is rejected;
5. over-limit output is never truncated or repaired;
6. provider schema version/hash invalidates old judge cache identity;
7. prior attempts remain immutable;
8. synthetic 4/0 and private 6/0/2 cache-resume accounting remain deterministic.

Refresh the existing completion report. It may be marked `Ready for PM validation` only after the
exact 6/0/2 private gate and the zero-call rerun pass.

## Third Delivery Review Addendum

### Decision

**Final local rework required.** Provider schema v3 and the private semantic gate are accepted in
substance: 6 eligible cases completed, no case failed, and 2 invalid candidates were skipped. The
remaining blocker is not a Vertex or cache-content failure. It is an idempotency and consistency
defect in the composed local scoring workflow.

The executor correctly stopped after the identical rerun failed before judge execution. The six
immutable judge attempt files remained unchanged, proving that no second disclosure occurred.
However, that control-flow proof does not exercise the judge cache path, so the original cache
acceptance criterion is still incomplete.

PM revalidation of this delivery passed the focused benchmark suite, the full 419-test suite,
Ruff, and `git diff --check`.

### PM artifact finding

The failed deterministic phase partially rewrote the existing judged run:

- `judge/metrics.json` still records the accepted 6/0/2 semantic result;
- the top-level aggregate JSON no longer contains the judge-semantic section;
- the aggregate Markdown no longer contains judge coverage;
- the run manifest still identifies a judged run.

This is an internally inconsistent output set. A normal rerun must not erase accepted judge
reporting before cache lookup, and a simple retry must not be used to conceal the defect.

Do not include private paths, case identities, hashes, content, scores, or rationales in tracked
evidence. Aggregate counts and logical artifact names are sufficient.

### Required local implementation

1. Reproduce the rerun behavior with synthetic data and an injected no-call judge client.
2. Identify the exact local failing operation and exception class without recording a private path.
3. Make deterministic scoring idempotent when the scoring directory already belongs to the same
   verified candidate package and scope.
4. Generate aggregate JSON and Markdown canonically from deterministic metrics plus any accepted
   judge metrics. Do not overwrite judge results with a deterministic-only report and do not append
   duplicate judge sections on repeated runs.
5. Preserve the original judged run identity and existing judge attempts during a same-package
   deterministic refresh or cache rerun.
6. If existing deterministic artifacts differ from freshly computed canonical values, fail closed
   with a bounded actionable error instead of silently accepting or replacing inconsistent data.
7. If an interrupted prior rerun left only the aggregate report inconsistent while canonical
   deterministic metrics and accepted judge metrics remain valid, rebuild the aggregate reports
   deterministically from those authoritative local artifacts.
8. Keep different-package protection unchanged.
9. Do not regenerate candidate outputs, alter judge scores, retry a semantic failure, or call
   Vertex during implementation or synthetic testing.

The executor may choose a small shared report-rendering function or another repository-consistent
design. Avoid a broad filesystem abstraction refactor unless the exact reproduced failure proves
it necessary.

### Required tests

Add synthetic coverage proving:

1. deterministic scoring can run twice in the same destination;
2. a judged destination can pass through deterministic scoring again without losing judge metrics;
3. aggregate JSON retains exactly one judge-semantic section;
4. aggregate Markdown retains exactly one judge-coverage section;
5. an injected judge client receives zero calls on the composed cache rerun;
6. judge attempt count and hashes remain unchanged;
7. run-manifest state remains coherent after the rerun;
8. interrupted/partially overwritten aggregate reports are repaired from canonical deterministic
   and judge metrics without a provider call;
9. differing package identity still fails closed;
10. unexpected deterministic artifact differences fail closed;
11. Windows and Linux tests remain network- and private-data-independent.

### Authorized final cache verification

Only after the synthetic regression passes, the PM authorizes one final verification against the
existing schema-v3 private run:

- use the same package, configuration, two-conversation scope, and scoring destination;
- reuse the six existing successful judge attempts;
- do not use a retry-failures option;
- require command exit code zero;
- require final accounting 6 completed / 0 failed / 2 skipped-invalid;
- require unchanged judge attempt count and aggregate attempt hash;
- require no new Vertex calls or disclosures;
- require canonical aggregate JSON/Markdown to include both deterministic and judge sections once;
- require the run manifest to remain coherent;
- reconfirm unchanged package, deterministic metrics, live DB, and frozen DB.

This authorizes cache verification only. If the application detects any cache miss, it must stop
before calling Vertex. Do not make a new remote call. If necessary, add an internal or CLI
cache-only/fail-on-miss guard so this boundary is enforceable rather than assumed.

If the final verification fails, stop once and leave status `Partial` with bounded local failure
facts. If it passes, refresh the completion report to `Ready for PM validation` and record the
exact zero-call/canonical-report evidence.

## Findings

### 1. Blocker: the mandatory real synthetic gate still fails

The first real `vertex_ai/gemini-2.5-flash` task returned non-JSON content. The executor stopped
without retrying and did not disclose any private evaluation case, which is exactly what the
handoff required. However, local injected-client success cannot replace the real provider gate.

Acceptance remains blocked until all four real synthetic tasks produce strict `JudgeResult`
values, after which the existing private package must produce exactly:

```text
eligible: 6
completed: 6
failed: 0
skipped_invalid: 2
```

### 2. High: Gemini thinking configuration is absent and is the leading root-cause hypothesis

Gemini 2.5 Flash uses automatic thinking by default. Current Google documentation states that the
automatic budget may use up to 8,192 thinking tokens and that `thinking_budget: 0` disables
thinking for Gemini 2.5 Flash. The judge request currently sets only `max_tokens: 500` and does not
configure thinking.

The installed LiteLLM implementation supports `reasoning_effort="none"` and maps it for Gemini
2.5 Flash to `thinkingBudget: 0` with thoughts excluded. Chronicle's `ModelProfile`,
`CompletionRequest`, and LiteLLM call boundary do not currently expose this setting.

This does not yet prove truncation caused the observed invalid JSON, but it is a concrete,
provider-documented compatibility gap and must be tested before changing the schema again.

References:

- Google thinking configuration: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/thinking
- Vertex controlled JSON generation sample: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/samples/generativeaionvertexai-gemini-controlled-generation-response-schema-2
- Vertex OpenAI compatibility notes: https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/call-vertex-using-openai-library

### 3. High: the current failure record is too coarse for the next safe decision

`CompletionResponse` retains content, provider, model, and usage, but not the completion finish
reason. When JSON parsing fails, the judge persists neither safe finish metadata nor usage. The
single category `provider_invalid_json` cannot distinguish likely boundaries such as output-token
exhaustion, content filtering, an empty response, a fenced response, or another format mismatch.

Because this gate uses synthetic data only, the executor may inspect the exact synthetic response
locally for diagnosis. No raw response, prompt, identifier, provider exception, or model reasoning
may enter tracked files. The durable diagnostic contract must remain safe for later private runs.

## Required Rework

### A. Add bounded response metadata

Extend the application-owned LLM response boundary so a caller can receive a constrained finish
reason and provider usage metadata without exposing content. At minimum:

- capture a normalized finish reason from the selected completion choice;
- retain existing usage counters, including reasoning/thought token counters when LiteLLM exposes
  them;
- on judge failure, persist only allowlisted finish category, response-present boolean, response
  character count, usage counters, provider/model identity already approved by configuration, and
  the existing failure category;
- never persist response text, prefixes/suffixes, provider exception text, prompts, rationales, or
  private values in a normal evaluation run.

For this synthetic investigation only, the executor may inspect the complete raw response in the
terminal or an ignored temporary file. Delete any temporary diagnostic file before delivery. The
completion report may state only structural conclusions such as truncation, fencing, empty output,
or other invalid JSON; it must not reproduce the response.

### B. Make reasoning control configuration-driven

Add an optional, strictly validated reasoning control to the existing model-profile/request
boundary rather than hard-coding a Gemini special case in the judge. The accepted narrow value
for this package is LiteLLM's provider-neutral `reasoning_effort` with a constrained supported
enum that includes `none`.

- Add the optional setting to the YAML model profile.
- Pass it through `CompletionRequest` to `litellm.acompletion` only when configured.
- Set `reasoning_effort: none` on the tracked and private `gemini-judge` profiles.
- Leave local candidate profiles unchanged.
- Include the effective reasoning setting in request/model/cache identity.
- Prove that `none` reaches LiteLLM and that omission preserves existing behavior.
- Fail clearly if an invalid configured value is supplied.

Do not add unrestricted `extra_body` or arbitrary provider parameters to YAML in this package.

### C. Run the synthetic gates in this order

The PM authorizes the following synthetic-only remote calls:

1. Run one diagnostic call for the first synthetic task with `reasoning_effort: none`, the current
   provider schema, and sufficient safe metadata capture.
2. If it succeeds, run one call for each of the other three accepted tasks.
3. Require four strict application results with exact task dimensions.
4. Rerun the same synthetic gate and prove zero additional provider calls through cache reuse.
5. If the first diagnostic call still fails, stop after recording safe finish/usage/shape facts.
   Do not repeatedly retry and do not run the private gate.

Do not revise the provider schema merely to force a pass unless the new synthetic evidence
identifies a schema-translation defect. The installed LiteLLM path already maps Gemini 2.x
`json_schema` requests to Vertex `responseJsonSchema`, which supports lowercase JSON Schema and
`additionalProperties`.

### D. Preserve the original private success gate

Only after all four synthetic tasks pass:

- reuse the existing verified candidate package and accepted references;
- use a fresh scoring destination;
- run exactly the same six eligible private judge cases, with the two invalid candidates skipped;
- require 6 completed, 0 failed, 2 skipped, and non-empty dimension means;
- rerun and prove zero additional Vertex calls;
- prove candidate package, deterministic metrics, live DB, and frozen DB remain unchanged;
- preserve all earlier failed attempts.

## Additional Tests Required

Add focused synthetic tests for:

1. reasoning setting validation and YAML round-trip;
2. omitted reasoning setting preserving the existing LiteLLM request;
3. `reasoning_effort: none` reaching `litellm.acompletion` exactly once;
4. effective reasoning setting participating in cache identity;
5. changing reasoning setting invalidating cache;
6. normalized finish reason capture;
7. usage/thought-token metadata retained without content leakage;
8. invalid JSON failure records containing bounded metadata only;
9. private markers absent from failure records and terminal output;
10. existing AI tasks and local LM Studio requests remaining compatible;
11. four-task real synthetic cache-resume accounting;
12. existing six-eligible/two-invalid regression remaining green.

## Completion Report Update

Refresh:

```text
md/handoffs/reports/WP-5.2B1.1-completion-report.md
```

Document the verified cause, effective reasoning configuration, safe finish/usage evidence,
four-task synthetic accounting, cache proof, and private accounting. Status may become **Ready for
PM validation** only after the exact private 6/0/2 gate and zero-call rerun both pass. Otherwise
leave status **Partial** and stop.

## Commit Ownership

Leave all implementation, test, documentation, and report changes unstaged and uncommitted. The
PM validates the rework and commits only after an explicit owner request.
