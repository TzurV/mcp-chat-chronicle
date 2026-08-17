# WP-5.2B3B.1D.4.2 Four-Proposal Hosted GEPA Search

## Manager authorization and objective

Continue the accepted WP-5.2B3B.1D.4.1 work from the clean committed `main`
revision containing this handoff. Work on a dedicated branch named
`codex/wp-5.2b3b-d4.2-gepa-search`.

The objective is to complete one auditable four-position GEPA prompt search
over the frozen ten-conversation development corpus. Use:

- `vertex_ai/gemini-2.5-flash-lite` as the single hosted candidate model;
- `vertex_ai/gemini-3.5-flash` as the GEPA proposer;
- the existing application-owned LiteLLM/Vertex ADC route in `global`;
- the unchanged four AI tasks, FABLE references, 6/4 development split, and
  8,192-token complete-request contract;
- the accepted graded GEPA-only search metric and unchanged strict promotion
  rule.

This is an autonomous bounded execution handoff. Do not stop for routine
manager commits, ordinary provider calls, ADC refresh, a generic implementation
defect, or a recoverable Windows sharing violation. You may implement, validate,
and commit narrowly scoped generic repairs on the dedicated branch and continue
from a new ignored append-only run root. Do not rewrite accepted evidence.

## External disclosure authorization

The owner explicitly authorizes the following private development disclosures
for this work package:

- sending the frozen ten selected development-conversation inputs, task
  prompts, and response schemas to Vertex AI Gemini 2.5 Flash-Lite for P0 and
  candidate evaluation;
- sending the minimum frozen development traces, candidate outputs, and
  structured FABLE-derived feedback required by GEPA to Vertex AI Gemini 3.5
  Flash as proposer;
- if a distinct candidate passes every deterministic qualification gate,
  sending the same bounded development source, P0/finalist outputs, and FABLE
  references required by the already configured fixed Gemini Pro judge;
- ordinary Vertex usage charges within the ceilings below.

Do not send the twenty-conversation holdout, unrelated archive content,
credentials, local paths, private hashes, or repository metadata to a model.
Do not place credentials, project IDs, tokens, private prompts, source text,
references, model outputs, or generated proposals in tracked files or ordinary
logs.

## Budget authorization

### Optimizer lifecycle

- Cumulative conservatively charged call ceiling: **850**.
- Cumulative configured/reserved cost ceiling: **US$35**.
- Accepted starting accounting from D.4.1: 441 charged calls and
  US$7.5983975014 configured/reserved cost.
- Therefore the maximum newly available optimizer allowance is 409 charged
  calls and US$27.4016024986 configured/reserved cost.
- The expected clean four-proposal operation reservation is 376 calls and must
  be recalculated before execution. Refuse before any call if it exceeds either
  remaining ceiling.
- Synthetic provider calls, route probes, candidate transports, explicit
  Chat-to-JSON fallbacks, provider retries, and proposer calls all count.
- Do not reinterpret a reservation as measured provider billing. Report
  observed, charged, measured, and reserved figures separately.

### Conditional fixed judge

The optimizer ceiling above does not consume or replace the existing fixed-
judge accounting ledger. Construct and call the fixed judge only after exactly
one distinct finalist passes deterministic qualification. Before judging,
resolve the tracked judge policy, verify its model/location/rubric identity,
calculate its separate eligible-case call and cost ceiling, and confirm that it
fits the previously accepted judge authorization. If it does not fit, stop
before constructing the judge and report the exact additional authorization
needed.

## Immutable authority and experiment contract

Preserve and verify all prior ignored D.1, D.4, and D.4.1 roots append-only.
Create a fresh D.4.2 ignored run root. Never use a prior result as writable
state.

Freeze and verify before private calls:

- exactly ten selected development inputs;
- exactly 40 FABLE references, four tasks per conversation;
- exact 6-conversation train and 4-conversation validation manifests;
- zero holdout paths or files;
- accepted task catalog and P0 prompt identities;
- candidate and proposer model identities, provider, location, generation
  settings, context limit, and retry settings;
- accepted D.3 graded-search version and strict-promotion version;
- source application commit and clean-worktree identity.

The seven known 8K-ineligible positions remain terminal no-call outcomes and
remain in all final denominators. Do not truncate source, increase context,
change selectors, repair outputs, add semantic retries, change references, or
exclude failures after seeing outcomes.

GEPA remains instruction-only. Disable prompt-component merges and model-
specific prompt branches. A candidate ID must change because prompt bytes
changed, not merely because lineage changed.

## Gate 0: clean source and private preflight

1. Confirm the repository Poetry environment and clean dedicated branch.
2. Confirm this handoff and the D.4.1 accepted reports are present in `HEAD`.
3. Verify the existing private authority without opening holdout content.
4. Reconcile accepted cumulative optimizer and judge accounting.
5. Run credential-free supported preflight and dry-run checks.
6. Confirm `.chronicle` remains ignored and untracked.

Do not ask the owner to commit manager-owned preparation: this handoff is the
committed authority. Do not ask again for the disclosures or budgets explicitly
authorized above.

## Gate 1: provider-free proposer lifecycle observability

Before any new private provider call, prove that every logical proposer position
has an append-only lifecycle record independent of DSPy's final candidate store.

At minimum persist privately:

- pre-call proposer intent and canonical request identity;
- GEPA iteration/proposal ordinal, selected component, and selected example
  identities without source text;
- configured and actual provider/model/location identity;
- response/failure terminal category, latency, finish availability, usage, and
  retry/fallback accounting where available;
- generated proposal bytes in the private ignored envelope before optimizer
  acceptance/rejection whenever proposal text exists;
- an explicit terminal `no-generated-proposal`, parse failure, provider failure,
  privacy rejection, context rejection, duplicate-P0, accepted, or rejected
  decision as applicable;
- linkage from proposer attempt to proposal envelope, decision, candidate, and
  result when those artifacts exist.

Required provider-free regressions:

- interruption before transport, after response, before proposal persistence,
  after proposal persistence, and during decision/checkpoint replacement;
- exact resume without duplicate completed proposer calls;
- Windows sharing-violation recovery through the application atomic writer;
- proposal text survives optimizer rejection and process restart privately;
- no proposal text enters tracked files or sanitized logs;
- a proposer response that yields no candidate remains a terminal auditable
  outcome rather than disappearing;
- historical D.3/D.4/D.4.1 evidence remains readable and byte-identical.

Run focused tests, the full suite, Ruff, Poetry validation, CLI/import checks,
privacy/tracking scans, and `git diff --check`. Commit the generic Gate 1 repair
on the dedicated branch. Continue without returning for manager approval if all
checks pass.

## Gate 2: route qualification and P0

Use the documented Windows Vertex ADC procedure. Environment assignments must
be process-scoped. Never print or persist credential content.

1. Verify ADC principal capability, quota/resource-project agreement, and
   `global` routing in the same process that will run the application.
2. Reuse a still-valid exact route qualification when authoritative. Otherwise
   run at most one synthetic qualification call per route plus its configured
   infrastructure retry.
3. Run the fresh P0 over all 40 positions through the accepted per-case journal.
4. Verify 40 terminal outcomes, including all deterministic context no-calls.
5. Package and verify P0 from a fresh process.
6. Prove a zero-call, byte-stable replay.

P0 is the search parent and development comparator. It is not automatically a
promoted production prompt.

## Gate 3: four logical GEPA proposal positions

Run exactly four logical GEPA proposal positions. Do not run a fifth proposal.
Use the frozen train split for optimizer feedback and the frozen validation
split for candidate comparison as already implemented.

For every position:

1. reserve the complete bounded operation before its first call;
2. persist proposer intent before transport;
3. retain generated proposal text privately before acceptance/rejection;
4. evaluate distinct candidates through the resumable per-case journal;
5. persist graded-search metrics and strict qualification metrics separately;
6. persist the terminal proposal decision and all accounting links;
7. continue to the next authorized position unless a mandatory stop condition
   below is reached.

A position with a provider response but no generated candidate still counts as
a terminal proposal position only when its proposer lifecycle record explains
the exact boundary. It does not count as an accepted or rejected prompt
proposal and must not be described as prompt-quality evidence.

The search may legitimately end with zero qualified finalists. That is a valid
negative outcome only if all four logical positions are terminal and auditable.

## Gate 4: finalist selection and conditional fixed judging

Apply the frozen reliability-first selection rule. A finalist must:

- contain prompt bytes distinct from P0;
- pass provenance and private proposal-envelope linkage;
- have zero privacy findings;
- satisfy the unchanged complete-request/context policy;
- complete all required train and validation positions with exact denominators;
- beat the frozen strict promotion rule rather than only the graded search
  score.

If no candidate qualifies, record explicit P0 retention and make zero judge
calls.

If one or more candidates qualify, select exactly one finalist using the frozen
rule, then judge P0 and that finalist with the tracked fixed judge. Do not use
judge feedback to edit prompts or change finalist selection. Persist judge
attempts append-only and prove a cache-only zero-call replay.

## Autonomous repair policy

You may complete up to three narrowly scoped generic repair cycles after Gate 1
without returning for routine approval. For each cycle:

1. stop new provider calls;
2. preserve the failed ignored root append-only;
3. diagnose from sanitized metadata and provider-free reproductions;
4. implement only a generic application/harness repair;
5. add focused regressions and run the complete validation matrix;
6. commit the repair on the dedicated branch;
7. create a fresh ignored successor root and resume within the same frozen
   scope and remaining budgets.

Do not count configuration tuning, prompt edits, model substitution, context
changes, selector changes, output repair, semantic retry, reference changes, or
scope reduction as generic repairs. Those require a manager decision.

## Mandatory stop conditions

Stop immediately and report when any of the following occurs:

- the next complete reservation exceeds a call or cost ceiling;
- holdout or unrelated archive content would be opened;
- a credential/private artifact might enter Git, logs, or persistent public
  storage;
- candidate, proposer, judge, task, reference, selector, context, or frozen
  metric identity drifts;
- accepted historical evidence would need mutation;
- more than three generic repair cycles are required;
- a semantic/model/experiment change is needed;
- the four logical proposal positions and conditional judging are complete.

Do not stop merely because one provider call fails, a Windows checkpoint needs
the already bounded retry, a generated proposal is rejected, no candidate is
produced at one position, or a generic defect can be repaired within this
policy.

## Required deliverables

Create:

- `md/handoffs/reports/WP-5.2B3B.1D.4.2-completion-report.md`;
- `md/handoffs/reports/WP-5.2B3B.1D.4.2-article-evidence-brief.md`;
- updates to `md/development-ledger.md` and
  `md/research/WP-5.2B3B.1-prompt-optimization-activity-log.md`.

The completion report must include:

- branch, commits, environment, model/provider, context, and frozen authority;
- P0 and per-proposal terminal accounting;
- proposal/candidate linkage and explicit missing-evidence fields;
- per-task train/validation validity, failures, deterministic/FABLE metrics,
  prompt lengths, tokens, latency, fallbacks, retries, and costs;
- observed versus charged calls and measured versus reserved cost;
- finalist decision and fixed-judge results or explicit zero-judge no-finalist
  result;
- fresh verification and byte-stable zero-call replay;
- holdout/privacy/tracking proof;
- every repair cycle and checkpoint commit;
- defensible conclusions and limitations suitable for later publication.

Keep final delivery changes unstaged for manager validation. Generic checkpoint
commits explicitly allowed by this handoff may remain committed on the dedicated
branch. Do not push, merge, tag, or delete branches or private evidence. End on
the dedicated branch with a clear status and `git status --short` output.
