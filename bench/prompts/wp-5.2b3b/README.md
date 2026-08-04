# WP-5.2B3B Global Prompt Packages

## Scope

These development-only catalogs define complete four-task prompt packages for the WP-5.2B3B
10-conversation development split. They do not change production defaults.

- P0: exact accepted `ai-tasks.default.yaml` baseline, reused rather than regenerated.
- P1: concise contract- and schema-first prompting.
- P2: P1 plus bounded fictional final-JSON examples.
- P3: absent unless the predeclared shared-failure trigger is met.

Every package is global: its four prompts are applied unchanged to Qwen3.5-4B Q4_K_M, Phi-4 Mini
Instruct Q4_K_M, and Vertex AI Gemini 3.5 Flash. A package is selected as one unit; task-level or
model-level prompt cherry-picking is prohibited.

## Authorship and privacy

P1 and P2 were authored directly by the OpenAI Codex agent executing this work package, using the
accepted task contracts, application schemas, handoff rules, and aggregate P0 failure categories.
No auxiliary model, automated optimizer, private conversation text, private identifier, FABLE
reference, candidate response, or judge rationale was used during authorship. All examples are
obviously fictional.

## P1 pre-run hypotheses

| Task | Prompt change | Expected movement |
| --- | --- | --- |
| Conversation summary | Put the one-object contract, array shape, sentence/word bounds, and evidence rule first. | Reduce schema and evidence failures; preserve factuality and coverage. |
| Work mode | Put exact enum values and whole-conversation distinctions before explanation. | Reduce invalid labels and improve manager/executor/one-off/mixed distinction without increasing unsupported claims. |
| Last activity | State the provider-facing nested `next_action` object unambiguously and separate `blocked`, `awaiting_input`, and `unknown`. | Reduce schema/cross-field failures and unsupported blockers/actions. |
| Title assessment | Put the `title_fits`/`suggested_title` dependency before fit guidance. | Reduce cross-field schema failures while preserving suggestion quality. |

P1 is not expected to repair provider failures. A shorter static prompt may reduce marginal context
or timeout pressure, but context and timeout outcomes remain failures rather than rescue targets.

## P2 pre-run hypotheses

| Task | Fictional examples | Expected benefit and cost |
| --- | --- | --- |
| Conversation summary | Valid sentence-array output plus an empty-content boundary. | Reinforce array/evidence shape at added prompt-token cost. |
| Work mode | A bounded executor example and an insufficient-evidence `unknown` example. | Improve enum and evidence behavior; may anchor labels too strongly. |
| Last activity | Completed/null-action and awaiting-input/explicit-action examples. | Reinforce nested action and status boundaries; largest expected schema benefit and prompt overhead. |
| Title assessment | One fitting and one non-fitting title. | Reinforce the null/suggestion dependency at moderate overhead. |

P2 should be preferred over P1 only when its reliability or semantic gain justifies measured token
and latency overhead.

## Frozen invariants

- ten development conversations and 40 ordered cases;
- common context 8,192;
- accepted Qwen, Phi, and Gemini model identities;
- task names, task versions, selectors, schemas, finalizers, input limits, recent-message counts,
  temperature, output-token limits, timeouts, retries, and concurrency;
- fixed Gemini Pro judge, rubric, schema, and generation policy;
- invalid-output, deterministic-scoring, judge, and UTS treatment;
- no output repair, hidden retry, truncation change, or model-specific prompt branch.

Only prompt text differs across P0, P1, and P2.

## Optional P3 trigger

P3 may be authored once only when the same task and normalized failure category appears in both
local models on at least four development cases in total, is plausibly addressable by model-neutral
wording, and requires no schema, selector, finalizer, context, generation, runtime, or application
change. The aggregate trigger evidence must be frozen before P3 text is written. No P4 is allowed.

## Selection rule

Rank complete packages lexicographically by pooled Qwen+Phi usable count, lower-of-two local-model
usable count, minimum pooled task usable count, pooled whole-case macro UTS, prompt-token overhead,
and then simpler/earlier package with P0 winning a complete tie. Apply all local and Gemini
regression guardrails from the authoritative handoff before selection.

## External-call ceiling

Before optional P3, the authorized ceiling is 160 new local candidate positions, 80 new Gemini
candidate positions, and up to 240 eligible fixed-judge positions plus the accepted bounded retry
and one four-task synthetic judge gate. P3, if triggered, adds at most 120 candidate and 120 eligible
judge positions. Any scope, provider, model, region, disclosure, retry, or cost expansion requires a
new approval.
