# WP-5.1.1 Completion Report

## Status

**Ready for PM validation.**

WP-5.1.1 implements the initial four conversation-intelligence task contracts on the
accepted WP-5.1 runner. WP-5.1.2 teacher-reference generation and WP-5.2 model
benchmarking remain explicitly excluded and gated until this package is accepted.
No real archive or remote model was used.

## Executive summary

The tracked and packaged task catalog now contains four enabled, independently
runnable version-1 tasks:

| Task | Selector | Output schema | Model profile |
| --- | --- | --- | --- |
| conversation-summary | conversation-overview-v1 | conversation-summary-v1 | service-local |
| work-mode-classification | conversation-overview-v1 | work-mode-classification-v1 | service-local |
| last-activity | recent-meaningful-v1 | last-activity-v1 | service-local |
| title-assessment | conversation-overview-v1 | title-assessment-v1 | service-local |

All tasks have version 1, depends_on: [], bounded input and generation settings,
externally editable zero-shot prompts, code-owned schemas/finalizers,
selected-message evidence validation, separate result/cache identities, and no
effect on normal archive commands.

## PM validation rework: structural selected IDs

The first PM review found that the overview branch reconstructed selected IDs by
searching rendered transcript text for message_id=<id>. That allowed a decimal
prefix such as message ID 2 to match the rendered header for ID 20, and allowed a
selected message body quoting message_id=3 to falsely imply that omitted ID 3 was
selected.

The narrow fix changes conversation-overview-v1 to return its chronological
selected IDs directly from the selected row tuples alongside rendered text and
selection details. _select_meaningful consumes that structural list without
parsing or searching transcript text. Sampling allocation, ordering, bounds,
truncation details, recent-meaningful behavior, schemas, cache, and persistence are
otherwise unchanged.

The new synthetic regression creates IDs 1 through 20 under a bounded overview,
with omitted ID 2 colliding with selected header ID 20 and omitted ID 3 quoted in
the selected ID-20 body. It proves:

- IDs 2 and 3 are absent from message_ids and selected_message_ids;
- selected ID 20 remains present and the selector is deterministic/bounded;
- provider responses citing ID 2 or 3 fail with evidence_validation and persist
  failed rows with no result JSON;
- a response citing genuine selected ID 20 succeeds;
- the existing recent-meaningful newest-first regression remains green.

## Files changed

### Task catalog

- ai-tasks.default.yaml
- src/chat_chronicle/resources/ai-tasks.default.yaml

The root and packaged files are byte-identical. The disabled example was removed so
the installed catalog exposes only the four production tasks.

### Selectors, schemas, and finalizers

- src/chat_chronicle/ai.py
- src/chat_chronicle/ai_config.py

The accepted legacy selectors and example schema remain available for compatibility.
The registry does not resolve YAML import paths or arbitrary callables.

### Tests

- tests/test_conversation_intelligence.py
- tests/test_ai_packaging.py

### Documentation and state

- README.md
- md/development-ledger.md
- md/handoffs/reports/WP-5.1.1-completion-report.md

The ledger state is **Ready for PM validation**, not accepted.

## Final YAML definitions and versions

Each task is enabled, task version 1, model profile service-local, and dependency
free. Task-specific maximum output sizes are 350, 250, 350, and 250 tokens
respectively. Overview tasks use a 50,000-character input ceiling. last-activity
uses a 24,000-character ceiling and an externally editable default of 12 meaningful
messages. Temperature is explicitly zero for stable structured extraction; other
profile fields continue to follow the accepted profile-default/task-override
precedence.

## Selector contracts

### Meaningful-message policy

Both new selectors read normalized rows in seq, id order. Code admits visible user,
Claude human, and assistant roles with non-empty bodies. It excludes
system/developer instructions, tool/function records, reasoning/thinking metadata,
importer metadata, unknown non-conversation roles, and empty bodies. Stored roles
are rendered as stored, not rewritten.

Each message is rendered with its local normalized message_id, seq, timestamp (or
unknown), stored role, and selected body. This makes model-visible evidence IDs
identical to the IDs validated after the provider response.

### conversation-overview-v1

If all meaningful messages fit, all are included. Oversized conversations use a
deterministic 25% beginning / 25% distributed middle / 50% end allocation. Middle
candidates are selected in deterministic center-out order; final output is
deduplicated and restored to chronological seq, id order. The first and last
meaningful messages receive their beginning/end allocations. A message exceeding an
otherwise empty allocation is deterministically truncated at message level:
beginning/middle retain the head and end retains the tail, while keeping the
evidence header when the allocation permits.

Metadata stores selector/version, selected IDs, bounded omitted IDs and omission
count, meaningful/candidate counts, selected sequence range, original/selected
character counts, truncation state, sampling strategy, and exact per-message
truncation details: message ID, original/selected characters, and retained head/tail.

### recent-meaningful-v1

The selector takes the last configured number of meaningful candidates (12 by
default), then walks newest to oldest. It retains newest complete messages first. If
a candidate cannot fit, it records deterministic message-level tail truncation only
when it is the first selected candidate, then stops; it never skips a newer omitted
message to include an older one. Selected messages are returned chronologically.

Metadata includes selected/omitted IDs and counts, sequence range, total meaningful
count, original recent candidate count, original/selected characters,
strategy/version, and truncation details. An empty meaningful conversation returns
an empty deterministic selection.

## Pydantic and finalization contracts

All models use extra=forbid and produce provider JSON Schema.

### conversation-summary-v1

Provider-owned fields:

- summary: non-empty, 2-5 sentences, at most 120 words and 1,000 characters;
- evidence_message_ids: strict integers, at most 8.

Final stored fields add start_date and last_active_date from exact normalized
conversation/DB metadata. The provider schema does not request either date. The
allowlisted version-1 summary finalizer injects them, then the full result model
validates the stored payload.

### work-mode-classification-v1

- mode: exactly manager | executor | one_off | mixed | unknown;
- confidence: 0.0 through 1.0;
- reason: non-empty and at most 60 words;
- evidence_message_ids: strict integers, at most 8.

The prompt fixes whole-conversation semantics: manager means coordination, scope,
delegation, prioritization, review, validation, approval, or rework dominates;
executor means inspection, implementation, testing, debugging, and delivery
dominates; one_off is a bounded standalone exchange; mixed requires genuinely
substantial multiple phases/purposes rather than normal planning inside execution;
unknown means insufficient, malformed, or fragmentary evidence.

### last-activity-v1

- recent_work: non-empty, at most 100 words;
- status: exactly in_progress | completed | blocked | awaiting_input | unknown;
- blockers: at most 3 non-empty strings, each at most 40 words;
- next_action: nullable, non-empty when present, at most 40 words;
- next_action_basis: exactly explicit | inferred | unknown;
- evidence_message_ids: strict integers, at most 8.

Unknown basis requires next_action=null; explicit or inferred requires a non-null
action. Prompts distinguish active incomplete work, completed work without
unfinished follow-up, a stated technical/external blocker, owner/user input waits,
and unreliable state. Empty blockers are represented as [].

### title-assessment-v1

- title_fits: boolean;
- confidence: 0.0 through 1.0;
- reason: non-empty and at most 60 words;
- suggested_title: nullable and at most 80 characters;
- evidence_message_ids: strict integers, at most 8.

title_fits=true requires a null suggestion. title_fits=false requires a non-empty
replacement. The prompt targets 3-10 words, preserves meaningful names/acronyms,
and rejects generic, unrelated, obsolete, misleading, or unsupported titles.
Execution uses only the append-only AI result path; a synthetic regression asserts
that conversations.title is unchanged.

## Evidence validation and failures

After provider-schema validation and deterministic finalization, every evidence ID
must belong to selected_message_ids. IDs are strict integers. Invalid IDs are never
removed silently: the attempt is stored as a sanitized evidence_validation failure
and remains retryable. Non-unknown factual output with meaningful selected content
must cite evidence. Empty evidence is accepted for an empty selection and explicit
unknown work-mode/last-activity results.

Default CLI summaries do not print selected transcript bodies. Stored selection
metadata contains IDs and selection facts, not an extra transcript copy.

## Cache and task independence

The existing cache key continues to cover conversation/input selection,
interpolated prompt, full task config/version, schema name/version, logical model
profile, and resolved model/generation config. Each schema specification contributes
schema-version+finalizer-version as the stored identity, so a schema or deterministic
finalizer change invalidates the affected cache identity.

Synthetic tests prove unchanged reruns hit, a finalizer-version change misses, four
tasks write four distinct result/schema identities, failure rows are retryable,
--force remains append-only through the accepted WP-5.1 matrix, and title/FTS content
is unchanged. With depends_on: [], one task failure cannot block or erase another
task's successful append-only result.

## Synthetic coverage

Invented provider-neutral cases cover manager planning/delegation/review/rework;
executor inspection/implementation/testing/delivery; one-off explanation; genuinely
mixed phases; empty content; completed, in-progress, blocked, and awaiting-input
states; explicit, inferred, and unknown next actions; accurate, generic/misleading,
and topic-changing titles; long-overview sampling; recent count/character pressure;
ChatGPT/OpenAI Codex user, Claude human, and shared assistant roles; excluded system,
developer, tool, function, reasoning, metadata, and empty rows; all approved labels
and statuses; valid/invalid evidence; application-owned summary dates; four-task
mock execution; and suggestion-only title behavior. Tests do not claim that a mock
model semantically understands these scenarios.

## Validation evidence

Poetry preflight resolved to:

    C:\work\Github\mcp-chat-chronicle\.venv

Results on the implementation:

- focused WP-5.1.1 plus accepted WP-5.1 matrices after rework: 98 passed;
- full suite after rework: 354 passed in 54.48 seconds;
- wheel/outside-checkout packaging test: 1 passed in 19.6 seconds;
- poetry run ruff check .: passed;
- poetry run chronicle --help: passed;
- isolated task list displayed all four enabled tasks and service-local without a
  LiteLLM call;
- four synthetic exact-ID dry-runs each selected ID 1, resolved local mock/local,
  reported one cache miss, and made no model call;
- git diff --check: passed;
- git status --short and git ls-files were inspected before commit.

The commit identifier is recorded in the delivery message because this report is
part of the committed tree.

## Wheel and installed-template evidence

tests/test_ai_packaging.py builds the wheel, proves both AI YAML resources exist,
extracts it outside the checkout, invokes installed chronicle init, loads the
created catalog, and asserts the exact four enabled task names. Packaging/config
tests also prove root/package byte identity and reject private paths, inline API
keys, real conversation IDs, and private markers.

## Privacy and tracked artifacts

Only invented synthetic content and temporary databases under test/temp roots were
used. No real owner archive was read for task execution. No remote provider or local
model completion was invoked. No credentials, local .chronicle catalogs, DBs,
exports, requests, responses, private paths, provider UUIDs, or real conversation
outputs are tracked. Normal archive commands retain accepted zero-LLM behavior.

## Known limitations

- This package validates contracts, deterministic selection, storage, and isolation;
  it does not evaluate real-model semantic quality.
- The overview remains one bounded sample and one model call; no map-reduce or
  retrieval layer was introduced.
- Meaningful roles are limited to currently accepted visible provider vocabulary.
  A future provider with a new visible role requires a code/test update.
- Teacher-reference quality, real-data evaluation, disagreements, and benchmarking
  remain WP-5.1.2/WP-5.2 work after acceptance.

## Acceptance checklist

- [x] Four enabled tracked and packaged task definitions.
- [x] External prompts and stable independent task versions.
- [x] Two deterministic bounded evidence-bearing selectors.
- [x] Application-owned exact summary dates.
- [x] Exact five-label whole-conversation work-mode contract.
- [x] Recent-only last-activity status/action contract.
- [x] Suggestion-only title assessment with no title write.
- [x] Evidence validated against selected normalized message IDs.
- [x] Explicit Pydantic/JSON-schema and finalizer identity.
- [x] Independent cache/failure behavior; append-only force preserved.
- [x] Normal archive behavior remains AI-free and regression-clean.
- [x] Synthetic/privacy-safe committed evidence only.
- [x] Focused/full tests, Ruff, help/list, and diff checks pass.
- [x] Wheel contains byte-identical templates and initializes all four tasks.
- [x] README documents semantics, precedence, privacy, and quality limitations.
- [x] Ledger is Ready for PM validation, not accepted.
- [x] WP-5.1.2 and WP-5.2 were not started.

## Commit statement

The original implementation exists in commit 4c15b0c. Per the PM validation review,
that commit was not amended, squashed, rebased, or otherwise rewritten. This
evidence-integrity rework remains uncommitted pending PM validation and explicit
authorization for any follow-up commit.
