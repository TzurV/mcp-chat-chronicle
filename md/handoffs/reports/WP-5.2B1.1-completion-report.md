# WP-5.2B1.1 Completion Report

## Status

**Ready for PM validation.** Provider schema version 3 passed the four-task real synthetic Vertex
gate and zero-call rerun. The fresh private gate passed exactly `6/0/2`. The final private
`--judge-cache-only` verification exited zero, reconstructed coherent aggregate reports, returned
the same `6/0/2` accounting, and made zero provider calls. The six immutable judge attempt files
and their aggregate identity remained unchanged.

## Executive summary

Chronicle now has separate task-specific Vertex provider schemas and strict application validation,
schema/request-versioned judge caching, YAML-controlled reasoning effort, normalized finish
reasons, and bounded usage diagnostics. Configuring the Gemini judge with `reasoning_effort: none`
made all four real synthetic structured outputs pass. The prior invalid JSON is therefore
consistent with automatic thinking exhausting the 500-token completion budget.

The existing private package was then verified and scored in a fresh schema-v3 destination. All six
eligible judge results passed strict validation and the two invalid candidates remained skipped.
Every accepted rationale was non-empty and at most 500 characters.

## Implementation

- Provider schema: `chronicle-judge-provider` version `3`, exact closed task dimensions and a
  shared 500-character rationale maximum with concise/no-chain-of-thought guidance.
- Application schema: `JudgeResult` version `1`, strict integers and bounded rationale.
- Normalizer version `1`; request-construction version `2`.
- `ModelProfile.reasoning_effort` accepts only `none`, `minimal`, `low`, `medium`, or `high`.
- Omitted reasoning settings do not enter legacy profile identity or LiteLLM request arguments.
- Configured settings pass to `CompletionRequest` and then `litellm.acompletion`.
- The tracked and private `gemini-judge` profiles use `reasoning_effort: none`; local candidate
  profiles remain unchanged.
- Judge cache identity includes the effective profile, both schema layers/hashes, normalizer,
  request version, rubric dimensions, and reasoning setting.

## Privacy-safe response metadata

`CompletionResponse` now carries an allowlisted normalized finish category. Failed judge records
contain only finish category, response-present boolean, response character count, and allowlisted
non-negative usage counters, including nested reasoning counters when present. Raw content,
prefixes/suffixes, prompts, rationales, private values, provider exceptions, and credentials are
never persisted by this diagnostic path.

The preserved schema-v2 private failure that motivated version 3 was limited to:

```text
failure_category: output_schema
field: rationale
category: string_too_long
finish_reason: stop
reasoning_effort: none
```

## Real synthetic Vertex evidence

Route: `vertex_ai/gemini-2.5-flash` with ADC and synthetic content only.

```text
first run: accepted 4, calls 4, failures 0
finish categories: stop 4
second run: accepted 4, calls 0, failures 0
```

These results use provider schema version 3. Every accepted rationale was non-empty and no longer
than the shared 500-character application bound.

No reasoning-token counter was reported. Temporary diagnostic scripts and the synthetic cache were
deleted before delivery.

## Private gate evidence

The existing two-conversation candidate package was reused without regeneration. All historical
destinations were preserved and a fresh schema-v3 destination was used.

```text
eligible: 6
completed: 6
failed: 0
skipped_invalid: 2
failure_categories: none
dimension_means: non-empty
rationales non-empty and <= 500 characters: true
```

The final cache-only command exited zero and returned the same accounting. Its fail-before-provider
guard would abort on any missing or failed cache entry. The attempt count remained six and the
aggregate attempt identity was identical before and after verification, proving no new attempt or
disclosure. Aggregate JSON contains one `judge_semantic` section; aggregate Markdown contains one
judge-coverage section; and the run manifest remains judged and profile-bound. The preserved
schema-v2 `5/1/2` run and all earlier attempts remain untouched.

## No-change evidence

- Candidate package SHA-256 was identical before and after the gate.
- Frozen database SHA-256 was identical before and after the gate.
- Live database SHA-256 was identical before and after the gate.
- Canonical deterministic metrics from the previous accepted run and new run had identical hashes
  and values.
- Candidate generation was not invoked.

## Files changed by the executor

- `src/chat_chronicle/ai_config.py`
- `src/chat_chronicle/ai.py`
- `bench/__main__.py`
- `bench/core.py`
- `bench/io.py`
- `bench/judge.py`
- `bench/models.py`
- `bench/ai-models.evaluation.default.yaml`
- `tests/test_ai_adapter.py`
- `tests/test_ai_config_matrix.py`
- `tests/test_bench.py`
- `docs/development-evaluation.md`
- `md/handoffs/reports/20260721-vertex-ai-llm-judge-connectivity.md`
- `md/handoffs/reports/WP-5.2B1.1-completion-report.md`

The ignored private judge profile and scoring destination were updated locally. PM-owned plan,
ledger, handoff, and validation-review changes were preserved.

## Test coverage

Committed tests cover strict reasoning validation/YAML round-trip, omitted-argument compatibility,
exact LiteLLM propagation, normalized finish reason, safe nested reasoning-token usage, invalid JSON
metadata without content leakage, reasoning-driven cache invalidation, provider/application schema
contracts, unexpected-error abort, authorization boundaries, four-task injected judging, and the
six-eligible/two-invalid regression with zero-call cache resume.

Final local validation: 424 tests passed; Ruff, Poetry consistency, bench score help, Chronicle
help, and `git diff --check` passed. No private database, SQLite file, ZIP, export, or `.chronicle`
artifact is tracked, and the staged-file list is empty.

## Requirement checklist

### Third-delivery local rework

- Same-package deterministic artifacts are compared against freshly computed canonical values.
- Identical JSON/text writes are no-ops; matrix and report writes use canonical atomic text.
- Aggregate JSON/Markdown are composed from authoritative deterministic plus judge metrics, with
  exactly one judge section.
- A judged manifest is preserved instead of being downgraded by deterministic refresh.
- Interrupted aggregate-only damage is reconstructed locally from authoritative metrics.
- `--judge-cache-only` makes any cache miss fail before provider execution.
- Synthetic tests cover repeated deterministic scoring, judged reruns, interrupted-report repair,
  attempt immutability, coherent manifest state, cache miss fail-closed, and deterministic
  divergence fail-closed.
- The earlier private rerun's exact control-flow boundary was an `OSError` during atomic judged
  run-manifest replacement after deterministic aggregate overwrite. The new implementation avoids
  that downgrade operation.
- The exact mismatch was `work-mode-confusion.csv`. The old comparator used universal-newline text
  decoding, which converted canonical Windows CRLF CSV into LF before comparing it with canonical
  CRLF output. This was a serialization-only false positive; parsed rows and semantic metric values
  were identical. The controlled migration/compare path now accepts newline-only and canonical
  legacy serialization while still rejecting semantic differences.
- Bounded semantic errors name the logical artifact and, for metrics JSON, the first differing JSON
  field path without values.
- The final authorized private cache-only verification exited zero with unchanged attempt count and
  aggregate attempt identity.

- Provider/application schema separation: complete.
- Schema/request/rubric/reasoning cache identity: complete.
- Privacy-safe finish/usage diagnostics: complete.
- YAML-controlled `reasoning_effort: none`: complete.
- Four real synthetic tasks: passed 4/4.
- Synthetic repeat: passed with zero calls.
- Existing private package reused; invalid candidates skipped: complete.
- Private schema-v3 gate: passed exactly **6 completed, 0 failed, 2 skipped**.
- Private cache-only verification: passed with exit code zero and zero provider calls.
- Aggregate JSON/Markdown: coherent, exactly one judge section each.
- Judged run manifest: coherent and preserved.
- Candidate/deterministic/live/frozen no-change evidence: passed.
- Historical attempts preserved: passed.
- Nothing staged or committed: confirmed at delivery.

## Known limitations

The cache-only option still performs local package verification and deterministic recomputation
before reading judge cache entries; this is intentional so stale or semantically divergent local
artifacts fail closed. It never permits a provider call on cache miss. No broader evaluation scope,
candidate regeneration, semantic retry, or provider fallback was introduced.
