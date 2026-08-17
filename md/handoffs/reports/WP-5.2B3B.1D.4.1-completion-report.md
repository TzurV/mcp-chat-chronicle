# WP-5.2B3B.1D.4.1 Resumable Candidate Evaluation And GEPA Completion Report

Date: 2026-08-17

## Executive outcome

The provider-free ordinary candidate journal, complete 40-case P0, package
verification, and byte-stable zero-call replay are complete. The bounded GEPA
search is not complete: two proposer attempts occurred, but neither produced a
candidate or the required private proposal envelope/decision. A pinned GEPA
0.1.1 Windows JSON-checkpoint replace failure then interrupted the search. The
third and final permitted generic repair is committed and fully validated.

A fresh ignored successor root is bound to that repair, contains the exact
authorized 6/4 development authority, and passes preflight. No provider call
was made from it because a complete four-proposal operation would project 817
cumulative charged calls against the hard ceiling of 600. This is therefore an
authorized budget stop, not a completed four-proposal no-improvement result.
P0 is retained explicitly as the development result; it is not promoted.

## Frozen scope and protected boundaries

- Candidate: `vertex_ai/gemini-2.5-flash-lite` in Vertex `global`, 8,192
  complete-request tokens, reasoning disabled.
- Proposer: `vertex_ai/gemini-3.5-flash` in Vertex `global`, reasoning disabled.
- Development authority: six train plus four validation conversations, four
  tasks each, 40 cases total. Each fresh private copy contained exactly 54
  authorized files and matched the accepted source byte-for-byte.
- GEPA: `gepa-reliability-v1`, instruction-only, merge disabled, four-proposal
  target, strict `new_sum > old_sum`, no Bootstrap.
- Fixed judge: zero construction and zero calls.
- Holdout: zero configured paths, enumeration, reads, or calls.
- RunPod, LM Studio, alternate/fallback models, output repair, and semantic
  retries: zero.
- One synthetic route canary was used; the authorized second canary was not
  needed.

No private content, path, identifier, hash, credential, prompt, reference, or
model output is present in tracked files.

## Engineering delivery

### Per-case ordinary candidate journal

The new journal appends an intent before transport and separately appends every
transport, usage record, terminal outcome, interruption, and reconciled batch.
It records privacy-safe configured/actual route identity, typed terminal
categories, retry ordinal, usage/cost/latency/finish availability, and canonical
event identity. Resume verifies terminal bytes, skips completed positions, and
cannot duplicate their calls.

Injected tests cover interruption before transport, after response, during
identity validation, usage adaptation, output validation, case persistence,
and batch finalization. A synthetic 24/16 resume calls only unfinished
positions, and a completed replay makes zero calls.

### Three bounded repair cycles

1. Complete-request estimation showed seven of 40 frozen requests exceeded the
   8,192-token boundary. The generic repair persists those positions as typed
   no-call `context-boundary` terminals and keeps them in the denominator.
2. Result accounting was repaired to reconcile terminal no-call context
   boundaries without weakening the context-fit promotion guard.
3. The interrupted GEPA checkpoint proved that pinned GEPA 0.1.1 had written a
   complete JSON temporary file before Windows replacement failed. GEPA JSON
   checkpoints now use Chronicle's unique-temporary, fsync, and bounded
   sharing-violation retry writer. Recovered Chat-to-JSON parse fallbacks no
   longer mask a later local failure as a provider failure.

Each post-call repair preserved the prior ignored root, passed complete offline
validation, and received a local checkpoint commit. The third repair's fresh
successor root was prepared and preflighted but not executed because of the
hard call ceiling.

## Provider execution

The one synthetic candidate canary returned a schema-valid response with exact
route/model identity, `stop`, no retry, 13 input tokens, five output tokens,
zero reasoning tokens, 15,281 ms latency, and US$0.0000033 measured cost.

Across private D.4.1 execution, the append-only evidence records 100 additional
observed calls: 70 ordinary candidate transports, 28 GEPA candidate transports,
and two proposer calls. The GEPA candidate transports cover 18 logical score
positions: 18 primary Chat transports plus ten explicit JSON fallbacks. Every
recorded transport ended in a response, and provider retry ordinal remained
zero. The four proposer calls and four retry allowances in the terminal budget
are retained fail-closed reservations, not four observed proposals or retries.

## P0 quality

P0 has 40/40 terminal outcomes: 33 candidate transports and seven no-call
context-boundary terminals. Sixteen outputs are schema/contract-valid and 17
transported outputs are schema-invalid. There were no infrastructure retries.

| Scope / task | Valid | Cases | Mean deterministic agreement |
| --- | ---: | ---: | ---: |
| Train — conversation summary | 0 | 6 | 0.000000 |
| Train — work-mode classification | 5 | 6 | 0.166667 |
| Train — last activity | 0 | 6 | 0.000000 |
| Train — title assessment | 5 | 6 | 0.300000 |
| **Train total** | **10** | **24** | **0.116667** |
| Validation — conversation summary | 0 | 4 | 0.000000 |
| Validation — work-mode classification | 3 | 4 | 0.312500 |
| Validation — last activity | 0 | 4 | 0.000000 |
| Validation — title assessment | 3 | 4 | 0.250000 |
| **Validation total** | **6** | **16** | **0.140625** |

The maximum complete request is 15,256 tokens, so P0 fails the frozen context
guard despite having zero privacy findings. The result is authoritative and
verifiable as development evidence but is not promotion-eligible.

## GEPA proposal outcome

GEPA recorded 28 candidate transports and measured two proposer calls before
the checkpoint interruption. Two trace iterations reached bounded reflection,
but neither reached a generated candidate: the candidate store still contains
only the seed program, and there is no proposal envelope or decision. There are
zero GEPA results, zero tuned candidates, and zero accepted/rejected proposal
decisions that satisfy the D.3 evidence contract.

Consequently:

- the normal four-proposal target and three-proposal minimum were not met;
- no fifth proposal was eligible or affordable;
- no finalist exists;
- the run-state label `pilot-no-improvement` is an operational budget-stop
  label and must not be presented as four-proposal prompt-quality evidence; and
- P0 is retained explicitly, without promotion or a claim that GEPA matched it.

## Observed and conservative accounting

Measured provider cost is partial because the GEPA adapter envelopes retain
tokens and latency but not portable per-call cost, and proposer usage/cost was
retained fail-closed. Budget-side configured/reserved cost is not a provider
invoice.

| Activity | Observed calls | Charged calls | Partial measured provider cost | Budget-side configured/reserved cost |
| --- | ---: | ---: | ---: | ---: |
| Accepted state before D.4.1 | 72–120 | 157 | US$0.06636632 | US$6.2616008 |
| D.4.1 synthetic canary | 1 | 1 | US$0.0000033 | US$0.0000033 |
| First preserved root | 4 | 5 | US$0.0005707 | US$0.0042900593 |
| Second preserved root | 33 | 33 | US$0.0126324 | US$0.0060881642 |
| Third preserved root | 63 | 245 | US$0.0125916 partial | US$1.3264151779 |
| **D.4.1 incremental** | **101** | **284** | **US$0.025798 partial** | **US$1.3367967014** |
| **Cumulative** | **173–221** | **441** | **US$0.09216432 partial** | **US$7.5983975014** |

The remaining ceilings are 159 charged calls and US$27.4016024986 of
budget-side headroom. The fresh successor root requires a complete 376-call
reservation, projecting 817; it therefore made zero calls. Nothing from an
unused future plan is counted as consumed.

## Verification and validation

- Fresh-process `bench verify`: valid authoritative P0 package, 40 terminal
  outcomes, privacy eligible, request context ineligible, zero provider calls.
- Provider-free shortlist export: zero finalists, status `no-improvement`, with
  P0 retained as baseline only.
- Credential-free terminal resume: zero authorization, zero calls, and all 260
  files byte-identical before and after replay.
- Focused optimizer suite after the final repair: 169 passed.
- Full repository suite: 673 passed and one expected skip.
- Ruff lint and changed-file formatting: passed.
- Poetry metadata, CLI help, offline imports, and `git diff --check`: passed.
- Successor preflight: 10 conversations, 40 cases, 24/16 split, seven context
  boundaries, exact frozen routes, zero holdout, and pinned DSPy/GEPA versions.

## Decision

The engineering and P0 portions of WP-5.2B3B.1D.4.1 are complete. The GEPA
experiment closes at a mandatory budget stop after incomplete proposal
generation. Preserve every ignored root append-only. Do not resume or start a
new provider run under the current authorization, and do not characterize this
as a completed no-improvement search. Any future search needs a separately
reviewed plan that can fund a complete operation from a clean, repair-bound
root. Fixed judge and holdout remain deferred.
