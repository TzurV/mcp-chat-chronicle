# WP-5.1.2B Handoff: Direct FABLE Development References

## Status

Ready for execution after the PM commits this handoff.

This is a private data-curation and direct teacher-labeling task. It is not an
application-code implementation task.

## Objective

Use the accepted frozen WP-5.1.2A database to create a local development set of:

- exactly 30 frozen conversations;
- exactly four WP-5.1.1 task cases per conversation;
- exactly 120 expected conversation-task cases;
- direct structured reference outputs created by FABLE in the execution chat.

FABLE is the only teacher for this work package. There is no second teacher,
answer reconciliation, human label review, or teacher-generation program.

The resulting references are private **silver development references**. They are
not ground truth, not a holdout, and not sufficient for final or
publication-grade model-quality claims.

## Plan Position

This handoff implements WP-5.1.2B from `md/master-plan.md`.

Dependencies:

- WP-5.1 is accepted;
- WP-5.1.1 is accepted;
- WP-5.1.2A is accepted;
- the frozen snapshot exists at the approved private location;
- the snapshot manifest and frozen hash have passed PM validation.

This work precedes:

1. WP-5.2A local model/runtime selection and integration;
2. WP-5.2B deterministic evaluation plus a different Gemini judge through
   LiteLLM/YAML;
3. WP-5.2C later remote execution and a separate untouched evaluation set.

The old handoff
`md/handoffs/WP-5.1.2-real-data-teacher-reference-corpus.md` is superseded
planning history. Do not execute its GPT/FABLE dual-provider orchestration,
300-conversation corpus, reconciliation, or remote API-runner scope.

## Executor Identity And Responsibility

This handoff is intended for a FABLE execution chat that can:

- read files in this repository;
- open the private frozen SQLite snapshot read-only;
- inspect selected private conversation content;
- create ignored local JSON artifacts;
- create one privacy-safe tracked completion report.

FABLE itself must produce the reference judgments. Do not delegate semantic
labeling to another model, a local model, a remote API, a sub-agent, or a
programmatic classifier.

The executor may use mechanical local commands for:

- read-only SQL;
- invoking the existing accepted input selector;
- hashing files;
- parsing and validating JSON;
- checking evidence-ID membership;
- counting records;
- maintaining resumable local progress.

Mechanical helpers must not:

- call any model;
- generate or rewrite reference content;
- infer labels;
- score candidate outputs;
- reconcile answers;
- replace FABLE judgment;
- be committed to the repository.

Any disposable helper must remain below `.chronicle/eval/dev-v1/tmp/`, be
ignored, and be identified in the completion report.

## Required Operating Notes

Read and follow `md/agent-operating-notes.md` before starting.

Mandatory rules:

- verify Poetry resolves to this repository's `.venv`;
- preserve all pre-existing user/PM changes;
- do not stage or commit;
- do not modify Git history;
- use direct reads and simple commands where practical because of the known
  Windows sandbox launcher issue;
- leave delivery status as `Ready for PM validation`.

## Owner Privacy Authorization

The owner explicitly authorizes FABLE to inspect the complete raw content of
every selected conversation for this development-reference task.

The owner has explicitly chosen:

- no conversation-level secret quarantine;
- no human semantic review at this stage;
- FABLE as the single teacher;
- all 30 conversations for development and prompt/model calibration;
- a separate evaluation set later.

This authorization is limited to the 30 conversations frozen by this handoff.
It does not authorize:

- sending the complete Chronicle archive to any model;
- sending unselected conversations;
- sending the snapshot database itself to another service;
- calling Gemini in this work package;
- calling FABLE through an additional API;
- sharing the corpus outside this execution chat and the local ignored files;
- committing private content.

If selected transcripts contain credentials or other secrets, do not copy those
secrets into summaries, reasons, suggested titles, reports, or logs unless the
literal value is indispensable to a task result. In normal cases, refer to the
existence or function of a credential without reproducing its value.

## Non-Negotiable Evaluation Fairness Rule

FABLE may inspect full selected conversations because the owner authorized it,
but each task reference must be based only on the exact task-selected input that
future candidate models will receive.

Therefore:

- `conversation-summary`, `work-mode-classification`, and `title-assessment`
  may use only the frozen `conversation-overview-v1` input and title metadata;
- `last-activity` may use only the frozen `recent-meaningful-v1` input;
- no reference may cite or depend on an omitted message;
- no task may use another task's output as evidence;
- no full-conversation fact may be introduced when it is absent from the task's
  selected input;
- if the selected input is insufficient, use the contract's conservative or
  unknown behavior, or record an explicit failure.

This rule prevents teacher information advantage and is required for valid
later candidate comparison.

## Explicit Non-Scope

Do not:

- modify application source or tests;
- add teacher-generation or corpus-generation product code;
- add a benchmark runner;
- add a LiteLLM call;
- use GPT, Gemini, a local LLM, a different teacher model, or a parallel
  independent FABLE teacher;
- run `chronicle --ai-task` for these references;
- write to `ai_task_results`;
- write to the live product DB;
- write to the frozen DB;
- migrate either DB;
- run ingest or collect;
- tune prompts during this work package;
- change WP-5.1.1 task prompts, selectors, schemas, or labels;
- create few-shot examples;
- judge local model outputs;
- create the later independent evaluation set;
- update the master plan or development ledger;
- commit or stage files.

## Required Private Layout

Use the accepted private root:

```text
.chronicle/eval/dev-v1/
```

Required layout after completion:

```text
.chronicle/eval/dev-v1/
  source/
    chronicle-frozen.db
    snapshot-manifest.json
  selection/
    selected-conversations.json
    selection-manifest.json
  inputs/
    c001.json
    c002.json
    ...
    c030.json
  references/
    conversation-summary/
      c001.json ... c030.json
    work-mode-classification/
      c001.json ... c030.json
    last-activity/
      c001.json ... c030.json
    title-assessment/
      c001.json ... c030.json
  runs/
    fable-direct-v1/
      task-catalog.yaml
      run-manifest.json
      progress.json
      validation-summary.json
  reports/
    fable-direct-v1-private-summary.json
  tmp/
    <optional disposable mechanical helpers>
```

All files below `.chronicle/eval/dev-v1/` are private, ignored, and untracked.

The tracked completion report is separate:

```text
md/handoffs/reports/WP-5.1.2B-completion-report.md
```

## Phase 0: Preflight And Stop Checks

### Poetry

From the repository root:

```powershell
poetry env info --path
```

Expected:

```text
C:\work\Github\mcp-chat-chronicle\.venv
```

If Poetry resolves outside this repository, stop before running any Poetry
command.

### Git

Record:

```powershell
git status --short
git rev-parse HEAD
```

Preserve pre-existing changes. Do not revert or stage them.

### Snapshot

Before reading conversation content:

1. Confirm the frozen DB and private manifest exist.
2. Parse the manifest as JSON.
3. Require `corpus_version = "dev-v1"`.
4. Require `freeze_status = "frozen"`.
5. Require the recorded WP to be WP-5.1.2A.
6. Recompute the frozen DB SHA-256.
7. Require it to equal both private manifest destination hashes.
8. Require no snapshot `-wal` or `-shm` sidecar.
9. Open the snapshot with SQLite URI `mode=ro` and `immutable=1`.
10. Set `PRAGMA query_only=ON`.
11. Require `PRAGMA integrity_check` to return `ok`.
12. Require schema version 3.
13. Require the accepted aggregate counts:
    - 711 conversations;
    - 28,370 messages.
14. Demonstrate that a write attempt is rejected.

Stop if any snapshot check fails. Do not repair, refresh, migrate, or replace the
snapshot inside this work package.

### Task Catalog And Schema Pin

Before selection:

1. Require root `ai-tasks.default.yaml` and packaged
   `src/chat_chronicle/resources/ai-tasks.default.yaml` to be byte-identical.
2. Compute and privately record the task-catalog SHA-256.
3. Record the Git HEAD used for input selection and labeling.
4. Record these task versions:
   - `conversation-summary`: task version `1`;
   - `work-mode-classification`: task version `1`;
   - `last-activity`: task version `1`;
   - `title-assessment`: task version `1`.
5. Record these schema/finalizer identities:
   - `conversation-summary-v1`: provider schema `1`, finalizer `2`;
   - `work-mode-classification-v1`: provider schema `1`, finalizer `1`;
   - `last-activity-v1`: provider schema `1`, finalizer `2`;
   - `title-assessment-v1`: provider schema `1`, finalizer `1`.
6. Copy the exact task catalog used into the private run directory for later
   reproducibility.

Stop if the root and packaged task catalogs differ or if the accepted task names,
selectors, labels, or schema identities cannot be confirmed.

## Phase 1: Deterministic Conversation Selection

Selection must occur before FABLE reads any title or body from candidate
conversations.

### Eligibility

A conversation is eligible when:

- provider is one of `chatgpt`, `openai_codex`, `claude`, or `claude_code`;
- it has at least two meaningful messages;
- meaningful roles are `user`, `human`, or `assistant`, case-insensitive;
- meaningful message bodies are non-empty after trimming;
- it has a usable last-activity date from accepted conversation/message
  metadata;
- `content_hash` is non-empty;
- it is not an exact `content_hash` duplicate retained elsewhere in the
  eligible pool.

Do not use title text, message text, existing AI-task results, search rank, or
subjective interest when deciding which eligible rows are selected.

### Deduplication

Deduplicate the eligible pool by `conversations.content_hash` before assigning
strata.

For an exact duplicate group:

- retain the row with the smallest conversation ID;
- record only aggregate duplicate counts in the private selection manifest;
- do not inspect content to choose between duplicates.

If deduplication makes a provider quota impossible, stop and report the blocker.
Do not silently substitute another provider.

### Provider Quotas

Select exactly:

| Provider | Conversations |
| --- | ---: |
| `chatgpt` | 10 |
| `openai_codex` | 10 |
| `claude` | 5 |
| `claude_code` | 5 |
| **Total** | **30** |

These quotas deliberately provide more than proportional representation for the
two smaller providers while keeping the two largest sources dominant.

### Length Strata

For each provider independently:

1. Calculate meaningful message count.
2. Calculate total meaningful body characters.
3. Order by meaningful characters, then meaningful messages, then conversation
   ID.
4. Apply SQL-equivalent `NTILE(3)` over that order.
5. Map tile 1 to `short`, tile 2 to `medium`, and tile 3 to `long`.

Required allocation:

| Provider quota | Short | Medium | Long |
| ---: | ---: | ---: | ---: |
| 10 | 3 | 4 | 3 |
| 5 | 2 | 1 | 2 |

If tied rows cross a tertile boundary, use conversation ID as the final
deterministic tie-breaker.

### Date Coverage Within Each Stratum

Within each provider/length stratum, order candidates by:

1. accepted last-activity date ascending;
2. conversation ID ascending.

For a stratum containing `N` candidates, use zero-based positions:

- one required row: `floor((N - 1) / 2)`;
- two required rows: `0`, `N - 1`;
- three required rows: `0`, `floor((N - 1) / 2)`, `N - 1`;
- four required rows: `0`, `floor((N - 1) / 3)`,
  `floor(2 * (N - 1) / 3)`, `N - 1`.

If a formula yields the same row twice, move the later duplicate to the nearest
higher unused position. If none exists, use the nearest lower unused position.
Stop if the stratum does not contain enough distinct candidates.

### Freeze Before Content Inspection

Create:

```text
.chronicle/eval/dev-v1/selection/selected-conversations.json
.chronicle/eval/dev-v1/selection/selection-manifest.json
```

`selected-conversations.json` must be a JSON object with:

- `format_version`;
- `corpus_version`;
- `selection_status`;
- `conversations`, containing exactly 30 records ordered by:

1. provider in this order: `chatgpt`, `openai_codex`, `claude`,
   `claude_code`;
2. length stratum: `short`, `medium`, `long`;
3. accepted last-activity date;
4. source conversation ID.

Assign opaque local case-group IDs:

```text
c001 ... c030
```

Each private selection record must contain:

- corpus version;
- case-group ID;
- selection index 1-30;
- source conversation ID;
- provider;
- source `content_hash`;
- meaningful message count;
- meaningful character count;
- length stratum;
- accepted activity date;
- date-selection position/method;
- selection algorithm version.

The selection manifest must contain:

- format version;
- corpus version;
- snapshot hash reference;
- Git HEAD;
- task-catalog hash;
- eligibility rules;
- deduplication rule and aggregate duplicate count;
- provider quotas and achieved counts;
- length quotas and achieved counts;
- date-position method;
- canonical SHA-256 of the final selected-ID/order payload;
- UTC freeze timestamp;
- `selection_status: "frozen"`.

For the selection hash, serialize only the ordered `conversations` array as
UTF-8 JSON with keys sorted, no insignificant whitespace, and stable JSON
primitive types. Record the serialization rule beside the hash.

After the selection hash is recorded:

- do not replace a difficult, ambiguous, sensitive, or failed conversation;
- do not reorder case-group IDs;
- do not alter provider or stratum membership;
- record failures against the frozen case instead of substituting another one.

Only after this freeze may FABLE inspect titles or message content.

## Phase 2: Freeze Exact Task Inputs

Create exactly one private input file for each case group:

```text
.chronicle/eval/dev-v1/inputs/c001.json
...
.chronicle/eval/dev-v1/inputs/c030.json
```

### Use Accepted Selectors

Use the existing accepted `chat_chronicle.ai.select_input` behavior against the
read-only frozen snapshot. Do not reimplement the selectors by intuition.

The executor may use a private mechanical helper to invoke the accepted selector
and serialize its output. That helper must not call a model or generate labels.

### Meaningful Message Definition

For both selectors, a meaningful message:

- has role `user`, `human`, or `assistant`, case-insensitive;
- has a non-empty trimmed body.

The rendered form is:

```text
[message_id=<id> seq=<seq> timestamp=<timestamp> role=<role>]
<trimmed body>
```

### `conversation-overview-v1`

Used by:

- `conversation-summary`;
- `work-mode-classification`;
- `title-assessment`.

Rules:

- maximum selected input: 50,000 characters;
- use all meaningful messages when they fit;
- otherwise use the accepted deterministic allocation:
  - beginning 25 percent;
  - distributed middle 25 percent;
  - end 50 percent;
- preserve chronological order in the final rendered input;
- preserve accepted truncation metadata;
- store the exact selected message IDs.

### `recent-meaningful-v1`

Used by:

- `last-activity`.

Rules:

- begin with the newest 12 meaningful messages;
- maximum selected input: 24,000 characters;
- select newest complete messages first;
- preserve chronological order in the final rendered input;
- preserve accepted truncation metadata;
- store the exact selected message IDs.

### Deterministic Dates And Title

For each conversation input:

- source title is the exact stored title, or an empty string;
- `start_date` is the accepted selector's application-owned start date;
- `last_active_date` is the accepted selector's application-owned last-active
  date;
- FABLE must not infer or rewrite either date.

### Input File Contract

Each `inputs/cNNN.json` file must contain:

```text
format_version
corpus_version
case_group_id
selection_index
source_conversation_id
provider
source_content_hash
source_title
start_date
last_active_date
overview:
  selector
  selector_version
  selected_message_ids
  selection_metadata
  transcript
  canonical_input_hash
recent:
  selector
  selector_version
  selected_message_ids
  selection_metadata
  transcript
  canonical_input_hash
created_at_utc
snapshot_hash_reference
task_catalog_hash_reference
```

Compute each canonical input hash from the task-relevant input payload using
UTF-8 JSON with sorted keys and no insignificant whitespace. Include title and
application-owned dates in the overview-task payload where the production task
uses them. Record the exact hash-payload field list privately.

Do not include source URL, origin path, resume hint, export path, or other
metadata that the four tasks do not use.

After each input file is created:

- parse it as JSON;
- require the case-group/source mapping to match the frozen selection;
- require selected message IDs to be unique;
- require selected message IDs to exist in that frozen conversation;
- require rendered header IDs to match the selected-ID list;
- require no write to the frozen DB;
- compute and record the input hashes.

Do not alter an input file after FABLE creates a reference from it. Any required
correction invalidates that case's references and must be recorded and regenerated
from the corrected frozen input.

## Phase 3: FABLE Direct Reference Creation

### Run Manifest

Before labeling, create:

```text
.chronicle/eval/dev-v1/runs/fable-direct-v1/run-manifest.json
```

Record:

- format version;
- run ID: `fable-direct-v1`;
- corpus version: `dev-v1`;
- teacher alias: `fable`;
- exact FABLE model/display name shown by the execution environment;
- provider/interface used;
- execution thread/task ID when available, otherwise `null`;
- additional session IDs if work resumes in another FABLE thread;
- UTC start timestamp;
- handoff path and Git HEAD;
- snapshot hash reference;
- selection hash reference;
- task-catalog hash;
- task names and versions;
- schema/finalizer identities;
- selector names and versions;
- owner remote-disclosure authorization;
- no-quarantine decision;
- no-human-review decision;
- no-chain-of-thought policy;
- expected conversation count: 30;
- expected task count: 120;
- run status.

Do not invent a model version. If the UI exposes only `FABLE`, record exactly
that and note that no more specific version was available.

### Processing Strategy

Process four task passes:

1. all 30 `conversation-summary` cases;
2. all 30 `work-mode-classification` cases;
3. all 30 `last-activity` cases;
4. all 30 `title-assessment` cases.

Within each pass:

- process `c001` through `c030` in order;
- read only one case input at a time;
- reread the exact task prompt and contract before each five-case batch;
- write and validate each reference immediately;
- checkpoint progress after every five cases;
- do not keep unpersisted reference work only in chat context;
- do not load all transcripts into context together;
- do not use previous task outputs while judging a later task.

This ordering keeps the rubric stable within a task and makes the work resumable
across context compaction.

### Progress File

Maintain:

```text
.chronicle/eval/dev-v1/runs/fable-direct-v1/progress.json
```

Record:

- expected and completed counts by task;
- success/failure counts by task;
- last completed case group per task;
- completed case IDs;
- missing case IDs;
- duplicate case IDs;
- last checkpoint UTC;
- current run status;
- session/thread history.

On resume, treat local artifacts as authoritative. Reopen the run manifest,
progress file, task catalog, and next case input. Do not rely on conversational
memory.

## Reference Record Envelope

Create one JSON file per task/case:

```text
.chronicle/eval/dev-v1/references/<task-name>/cNNN.json
```

Each record must contain:

```text
format_version
corpus_version
run_id
case_id
case_group_id
source_conversation_id
provider
task_name
task_version
output_schema
provider_schema_version
finalizer_version
input_selector
selector_version
input_hash
task_catalog_hash
teacher_alias
teacher_model
teacher_session_id
status
output
failure
created_at_utc
validated_at_utc
```

`teacher_session_id` may be `null` only when the execution environment exposes
no stable session/task identifier. The run manifest must state that limitation.

Required case ID format:

```text
dev-v1-cNNN-<task-name>-v1
```

For success:

- `status` is `success`;
- `output` is the exact canonical task output object;
- `failure` is `null`.

For failure:

- `status` is `failed`;
- `output` is `null`;
- `failure` contains a concise structured `code` and `detail`;
- failure detail must not reproduce private transcript text.

Never omit a frozen case. A failure record is preferable to substitution,
fabrication, or a missing file.

## Task 1: `conversation-summary`

### Input

Use only:

- `overview.transcript`;
- `overview.selected_message_ids`;
- deterministic `start_date`;
- deterministic `last_active_date`.

### Teacher Instruction

Summarize the selected conversation factually in 2-5 concise sentences and at
most 120 words total.

Cover:

- principal goal or topic;
- material work or decisions;
- supported outcome or current position.

Do not invent:

- success;
- decisions;
- blockers;
- completion;
- future commitments;
- next steps not present in the selected input.

### Canonical Output

The `output` object must contain exactly:

```json
{
  "summary": "A 2-5 sentence string of at most 120 words.",
  "start_date": "<exact application-owned date>",
  "last_active_date": "<exact application-owned date>",
  "evidence_message_ids": [1, 2]
}
```

Rules:

- `summary` is one string, not an array;
- exactly 2-5 sentences;
- at most 120 words;
- dates must be copied exactly from the input file;
- FABLE must not infer or normalize dates;
- evidence list contains 1-8 unique selected overview message IDs when
  meaningful content exists;
- evidence IDs should be chronological;
- evidence must support the material summary claims.

## Task 2: `work-mode-classification`

### Input

Use only:

- `overview.transcript`;
- `overview.selected_message_ids`.

Classify the conversation as a whole, not an individual speaker and not only the
latest turn.

### Approved Labels

- `manager`: project coordination, scope, delegation, prioritization,
  validation, approval, or rework dominates;
- `executor`: concrete inspection, implementation, testing, debugging, and
  delivery dominates;
- `one_off`: a bounded standalone question, explanation, recommendation,
  troubleshooting exchange, or small request;
- `mixed`: substantial manager and executor phases, or another substantial
  independent purpose; ordinary planning within execution is not enough;
- `unknown`: evidence is insufficient, malformed, or fragmentary.

### Canonical Output

The `output` object must contain exactly:

```json
{
  "mode": "manager",
  "confidence": 0.9,
  "reason": "A concise evidence-grounded reason of at most 60 words.",
  "evidence_message_ids": [1, 2]
}
```

Rules:

- confidence is numeric from 0 through 1;
- reason is non-empty and at most 60 words;
- evidence contains at most 8 unique selected overview message IDs;
- evidence IDs should be chronological;
- use `unknown` rather than guessing from weak fragments;
- confidence is an uncalibrated teacher self-assessment, not probability truth.

For consistency, use these broad confidence interpretations:

- `0.90-1.00`: explicit and highly unambiguous;
- `0.75-0.89`: strong evidence with minor ambiguity;
- `0.55-0.74`: defensible but meaningfully mixed or incomplete;
- below `0.55`: weak evidence; consider `unknown`.

Do not force exact decimal values or class balance.

## Task 3: `last-activity`

### Input

Use only:

- `recent.transcript`;
- `recent.selected_message_ids`.

Do not use older overview context.

### Status Labels

- `in_progress`: active incomplete work that is not clearly blocked;
- `completed`: completion or acceptance with no explicit unfinished follow-up
  in the selected range;
- `blocked`: progress cannot continue because of a stated technical or external
  blocker;
- `awaiting_input`: specifically waiting for owner/user decision, credentials,
  data, approval, or another report;
- `unknown`: the current state is not reliable from the selected input.

### Canonical Output

The `output` object must contain exactly:

```json
{
  "recent_work": "A factual description of at most 100 words.",
  "status": "in_progress",
  "blockers": [],
  "next_action": "A supported action of at most 40 words.",
  "next_action_basis": "explicit",
  "evidence_message_ids": [1, 2]
}
```

Rules:

- `recent_work` is non-empty and at most 100 words;
- `blockers` has 0-3 non-empty strings;
- each blocker is at most 40 words;
- use an empty blocker list when none is evidenced;
- `next_action` is `null` or a non-empty string of at most 40 words;
- `next_action_basis` is `explicit`, `inferred`, or `unknown`;
- `unknown` basis requires `next_action: null`;
- `explicit` or `inferred` requires a non-null next action;
- `explicit` is allowed only when the selected messages state the action;
- `inferred` is allowed only for a conservative directly supported
  continuation;
- do not turn a suggestion into a commitment;
- evidence contains at most 8 unique selected recent message IDs;
- evidence IDs should be chronological.

## Task 4: `title-assessment`

### Input

Use only:

- exact `source_title`;
- `overview.transcript`;
- `overview.selected_message_ids`.

### Fit Rules

A title fits when it specifically and accurately represents the dominant
conversation activity.

A title does not fit when it is:

- empty;
- a placeholder;
- unrelated;
- obsolete after a substantial topic change;
- materially misleading;
- too generic to distinguish the work;
- claiming an unsupported project, outcome, or topic.

### Canonical Output

The `output` object must contain exactly:

```json
{
  "title_fits": false,
  "confidence": 0.9,
  "reason": "A concise evidence-grounded reason of at most 60 words.",
  "suggested_title": "Concrete Replacement Title",
  "evidence_message_ids": [1, 2]
}
```

Rules:

- `title_fits` is boolean;
- confidence is numeric from 0 through 1;
- reason is non-empty and at most 60 words;
- `title_fits: true` requires `suggested_title: null`;
- `title_fits: false` requires a non-empty suggested title;
- suggested title is approximately 3-10 words and at most 80 characters;
- preserve meaningful names and acronyms;
- avoid provider/date labels, clickbait, unsupported outcomes, and generic
  wording;
- evidence contains at most 8 unique selected overview message IDs;
- evidence IDs should be chronological;
- this task never renames source data.

## Evidence Rules For All Tasks

Every evidence ID must:

- be an integer;
- be unique within the record;
- belong to the exact selected-ID list for that task input;
- identify a message in the same frozen conversation;
- support at least one material output claim;
- never come from an omitted message;
- appear in chronological order.

The following are invalid:

- provider conversation IDs;
- message sequence numbers used in place of DB message IDs;
- decimal numbers copied from message bodies;
- IDs quoted inside message text;
- IDs from another conversation;
- IDs selected only because they appear in another task output.

Dates are application-owned metadata and do not require a separate evidence
message solely to prove the date.

## Independence And Contamination Rules

Each task is independent.

Do not:

- use `conversation-summary` to decide work mode;
- use summary or work-mode output to determine last activity;
- use a generated summary as the basis for title assessment;
- revise one task because another task disagrees;
- enforce cross-task narrative consistency at the expense of source evidence;
- use existing local-model `ai_task_results` as references;
- inspect candidate model outputs before references are frozen.

If independently produced tasks appear inconsistent, preserve the independent
outputs and record the condition in the private validation summary. Do not
reconcile them in WP-5.1.2B.

## No Chain-Of-Thought Rule

Do not request, create, or store hidden reasoning or chain-of-thought.

Allowed:

- concise `reason` fields required by the task schemas;
- short failure detail;
- privacy-safe operator notes;
- concise evidence-grounded verdict rationale.

Not allowed:

- step-by-step private reasoning;
- scratchpad reasoning copied into artifacts;
- internal deliberation logs;
- transcript annotations beyond the structured task output.

## Mechanical Validation After Every Reference

After writing each reference:

1. Parse the file as JSON.
2. Require the exact envelope fields.
3. Require the exact task output fields and no extras.
4. Validate data types.
5. Validate enumerated labels.
6. Validate confidence bounds.
7. Validate word, sentence, list, and character limits.
8. Validate task-specific null consistency.
9. Validate evidence uniqueness and membership.
10. Validate case-group, task, selector, and input-hash linkage.
11. Require no transcript text outside the private input/output artifact.
12. Update progress atomically.

A private disposable validator is allowed for these mechanical checks. It must
not modify reference meaning or auto-correct output. On validation failure,
FABLE must reread the same selected input and rewrite the invalid reference
directly.

Do not silently normalize a semantically invalid reference.

## Batch Checkpoints

After every five cases in a task pass:

- verify five new distinct files exist;
- parse all five;
- verify evidence membership;
- update progress;
- record the current teacher session ID;
- recompute counts;
- confirm snapshot hash still matches;
- confirm no private file is tracked;
- continue from persisted state.

After each 30-case task pass:

- require 30 records for that task;
- require no duplicate case IDs;
- require all c001-c030 case groups accounted for;
- record success/failure counts;
- record aggregate label/status/title-fit distributions where applicable;
- record aggregate confidence statistics where applicable;
- do not expose case-level content in the tracked report.

## Failure Handling

Use an explicit failure record when:

- the input file is missing or invalid;
- selector/source linkage cannot be verified;
- the selected input is malformed;
- task output cannot be made schema-valid after a careful retry;
- the FABLE execution environment cannot safely continue;
- snapshot or selection hash verification fails.

Failure codes should be stable and concise, for example:

- `input_missing`;
- `input_invalid`;
- `selector_mismatch`;
- `evidence_unresolvable`;
- `schema_validation_failed`;
- `teacher_interrupted`;
- `snapshot_hash_mismatch`;
- `selection_hash_mismatch`.

Do not:

- replace the conversation;
- copy a prior case's answer;
- fabricate an output to reach 120 successes;
- downgrade a mechanical failure into `unknown`;
- expose private content in failure detail.

`unknown` is a valid semantic label only where the task schema permits it.
Technical failures must remain technical failures.

## Resumption And Context Compaction

This task may exceed one chat context.

To resume safely:

1. verify FABLE model identity remains the approved teacher;
2. read this handoff;
3. read the private run manifest;
4. verify snapshot, selection, and task-catalog hashes;
5. read progress;
6. identify the first missing task/case file;
7. reread that task's exact rubric;
8. process only the next input;
9. record the new execution session/thread ID;
10. continue without regenerating valid completed references.

Do not use chat memory as the source of truth for completed work.

If a different model would take over, stop. A mixed-teacher corpus requires a
new owner decision and provenance design.

## Final Private Validation

Create:

```text
.chronicle/eval/dev-v1/runs/fable-direct-v1/validation-summary.json
.chronicle/eval/dev-v1/reports/fable-direct-v1-private-summary.json
```

The private validation must confirm:

- snapshot hash still matches WP-5.1.2A;
- snapshot integrity remains `ok`;
- snapshot counts remain 711/28,370;
- selection hash matches;
- exactly 30 selected conversations;
- provider quotas are 10/10/5/5;
- required length allocations match;
- exactly 30 input files;
- exactly 120 expected reference files;
- every task has c001-c030 accounted for;
- success/failure counts total 120;
- no duplicate case IDs;
- all success outputs pass structural validation;
- all evidence IDs belong to task-selected inputs;
- all summary dates match input dates exactly;
- no cross-conversation evidence;
- no missing case without a failure record;
- task-catalog and Git provenance are recorded;
- teacher identity/session provenance is recorded;
- no FABLE API, Gemini, GPT, local model, or second-teacher call occurred;
- frozen and live DBs were not modified;
- no private artifact is tracked.

The private summary may contain case IDs, local IDs, hashes, and detailed failure
records. The tracked completion report may not.

## Git Privacy Verification

Verify:

```powershell
git check-ignore -v .chronicle/eval/dev-v1/selection/selected-conversations.json
git check-ignore -v .chronicle/eval/dev-v1/inputs/c001.json
git check-ignore -v .chronicle/eval/dev-v1/references/conversation-summary/c001.json
git check-ignore -v .chronicle/eval/dev-v1/runs/fable-direct-v1/run-manifest.json
git ls-files .chronicle
git status --short
```

Expected:

- every private artifact is ignored;
- `git ls-files .chronicle` returns no private corpus artifact;
- `git status --short` shows no selection, input, reference, run, report,
  temporary helper, DB, manifest, sidecar, or transcript artifact;
- `git add -f` was not used;
- nothing is staged.

## Required Completion Report

Create:

```text
md/handoffs/reports/WP-5.1.2B-completion-report.md
```

Required status:

```text
Ready for PM validation
```

The tracked report must include:

1. executive summary;
2. confirmation that FABLE directly created the references;
3. exact FABLE display/model identity available to the executor, without
   credentials;
4. confirmation that no teacher-generation or reconciliation code was added;
5. confirmation that no second teacher, Gemini judge, GPT, local model, or
   additional model API was used;
6. snapshot preflight result without path or hash disclosure;
7. snapshot schema and aggregate counts;
8. selection algorithm version and freeze result;
9. provider distribution: 10/10/5/5;
10. length-stratum aggregate distribution;
11. date-coverage method, without dates or IDs;
12. deduplication aggregate count;
13. input file count;
14. expected, successful, and failed case counts by task;
15. work-mode aggregate label distribution;
16. last-activity aggregate status distribution;
17. title-fit aggregate true/false distribution;
18. aggregate confidence statistics, where present;
19. evidence-membership validation count;
20. deterministic summary-date validation count;
21. JSON/schema validation result;
22. snapshot and selection hash re-verification result, without hashes;
23. private artifact ignore/tracking evidence;
24. confirmation that live and frozen DBs were not modified;
25. confirmation that no human semantic adjudication occurred;
26. limitations and explicit failures;
27. temporary private helper list and whether each was retained or removed;
28. exact tracked files changed;
29. final `git status --short` summary;
30. acceptance-criteria checklist;
31. explicit statement that this is development data, not ground truth or final
    evaluation data;
32. explicit statement that WP-5.2A/B/C have not started.

The tracked report must not contain:

- source conversation or message IDs;
- case-level IDs if they expose source mapping;
- titles;
- transcript text;
- snippets;
- URLs;
- origin paths;
- usernames or private absolute paths;
- UUIDs;
- content hashes;
- snapshot, selection, input, prompt, or reference hashes;
- per-case teacher output;
- credentials or tokens;
- chain-of-thought;
- private failure details that reveal content.

Aggregate counts and distributions are allowed.

## Completion Report Location Is Mandatory

The executor must create the report exactly at:

```text
md/handoffs/reports/WP-5.1.2B-completion-report.md
```

Do not place it in `.chronicle/eval/`, another reports directory, or only in the
chat response.

## Acceptance Criteria

WP-5.1.2B is ready for PM validation only when:

1. Poetry preflight resolves to the repository `.venv`.
2. The accepted WP-5.1.2A snapshot hash, integrity, schema, counts, read-only
   mode, and no-sidecar state are reverified.
3. Root and packaged task catalogs are byte-identical and pinned.
4. Selection occurs before title/body inspection.
5. Eligibility and exact-content deduplication rules are followed.
6. Exactly 30 conversations are selected.
7. Provider quotas are exactly 10 ChatGPT, 10 OpenAI Codex, 5 Claude, and 5
   Claude Code.
8. Required short/medium/long allocations are achieved.
9. Deterministic date-spread positions are used.
10. Selected IDs/order are frozen and privately hashed before labeling.
11. No frozen conversation is substituted after content inspection.
12. Exactly 30 task-input files exist.
13. Inputs use accepted `conversation-overview-v1` and
    `recent-meaningful-v1` behavior.
14. Each task reference uses only its exact selected input.
15. FABLE directly creates all semantic references.
16. Exactly 120 expected reference records exist.
17. Every expected case is success or explicit failure.
18. Every successful output has the exact canonical schema and no extra fields.
19. Every evidence ID is unique, chronological, and within the selected input.
20. Every summary date exactly matches application-owned input dates.
21. Work-mode labels use only the approved taxonomy.
22. Last-activity status/action/null consistency passes.
23. Title-fit/suggestion consistency passes.
24. No task uses another task's output as evidence.
25. No chain-of-thought is requested or stored.
26. No human semantic review or adjudication occurs.
27. No second teacher, GPT, Gemini, local model, or additional model API is
    used.
28. No teacher-generation, reconciliation, candidate evaluation, or benchmark
    code is added.
29. Live and frozen DBs remain unchanged.
30. Snapshot, selection, and task-catalog hashes still match.
31. All private artifacts remain ignored and untracked.
32. No private case data appears in tracked files.
33. The detailed completion report exists at the mandatory path.
34. `git diff --check` passes.
35. All tracked delivery changes remain unstaged and uncommitted.

## PM Validation Boundary

The PM validates:

- process compliance;
- selection determinism and aggregate distribution;
- snapshot and selection freeze evidence;
- artifact completeness;
- JSON/schema validity;
- evidence-ID membership;
- deterministic dates;
- privacy boundary;
- provenance;
- report completeness.

The owner has chosen no human semantic review at this stage. Therefore the PM
does not:

- rewrite FABLE references;
- adjudicate whether a summary is best;
- relabel work mode;
- revise status or next action;
- choose a preferred title;
- reconcile disagreements.

Semantic quality is measured later by WP-5.2B using deterministic metrics and a
different Gemini model as judge.

## Validation Commands

This package changes no application code. A full pytest or Ruff run is not
required solely for WP-5.1.2B.

Required tracked-delivery checks:

```powershell
git diff --check
git status --short
```

Required private checks are defined throughout this handoff. Mechanical
validation may use private disposable helpers, but those helpers must not become
tracked product code.

If the executor changes application code, tests, dependencies, schemas, task
YAML, plan, or ledger, stop and report the scope deviation. Do not expand the
task to legitimize it.

## Delivery And Commit Ownership

Follow `md/agent-operating-notes.md`.

The executor must:

1. create and freeze the selection;
2. create exact task inputs;
3. create all FABLE references;
4. validate and checkpoint private artifacts;
5. write the detailed completion report;
6. leave all tracked changes unstaged and uncommitted;
7. report `git status --short`;
8. deliver status as `Ready for PM validation`.

The executor must not run:

- `git add`;
- `git commit`;
- commit amendment;
- rebase;
- squash;
- history rewrite.

The PM/manager owns validation and commits. Only after successful PM validation
and an explicit owner request may the PM stage and commit the accepted tracked
documents.
