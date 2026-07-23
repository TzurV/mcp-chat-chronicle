# WP-5.2A5.1 Validation Review

## Status

Accepted on 2026-07-23.

## PM conclusion

WP-5.2A5.1 satisfies its qualification contract without code, prompt, runtime, or evaluation-data
changes.

Accepted admission decisions:

- Phi-4 Mini Instruct: qualified, 8/8;
- Llama 3.2 3B Instruct: qualified, 8/8;
- Gemma 3 4B IT fallback: qualified, 8/8;
- Gemma 4 E2B IT: not qualified at the fixed LM Studio runtime/structured-output compatibility
  gate.

All 24 required matrix positions are terminal and schema/evidence/date/cross-field/output-limit
valid. No output was repaired or retried. The Gemma 4 probes are correctly excluded from the
24-position matrix because its compatibility gate failed before task qualification.

## Evidence reviewed

- clean repository and repository-local Poetry environment preflight;
- immutable frozen/live database and historical package identities;
- common synthetic and frozen inputs selected before candidate output;
- fixed 8,192 context, parallelism/concurrency 1, temperature 0, retries 0, accepted task prompts,
  schemas, selectors, finalizers, and task-owned output limits;
- owner-controlled download and license gates;
- exact private artifact/runtime provenance and independent size/hash verification;
- direct and application-owned strict structured-output transport probes;
- complete 24-position contract matrix;
- privacy-safe latency and provider-reported usage accounting;
- no Vertex candidate/judge call, database write, tracked private artifact, or staged file;
- focused existing tests, Ruff, Poetry metadata, and diff hygiene reported passing.

## Residual limitations

- Eight successful qualification calls per model prove compatibility only; they do not establish
  whole-corpus reliability or semantic quality.
- Llama 3B's schema-valid literal `"[]"` blocker value remains a semantic-quality warning for the
  common benchmark.
- Gemma 4's rejection applies to the pinned artifact and fixed LM Studio/llama.cpp runtime. It is
  not a general claim that the model cannot satisfy the tasks under another runtime.
- Cross-model latency is preliminary because qualification covers only two short inputs.

## Next gate

Phi-4 Mini, Llama 3.2 3B, and Gemma 3 4B may enter the common frozen-prefix 40-case checkpoint
under a separately committed WP-5.2B2 handoff. Candidates that meet that checkpoint's predefined
admission policy may proceed to complete 120-case runs.

Keep prompts, schemas, context, runtime policy, fixed-Pro judge, references, and accepted baseline
packages unchanged. Prompt tuning remains deferred to proposed WP-5.2B3.

## Tracking

The executor correctly left the completion report unstaged and uncommitted. The unrelated LP-4.1
analysis brief was not part of this validation and remains outside this delivery.

