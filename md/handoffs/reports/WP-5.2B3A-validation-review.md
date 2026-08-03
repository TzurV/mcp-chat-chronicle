# WP-5.2B3A Validation Review

## Decision

**Accepted.**

WP-5.2B3A satisfies its handoff and acceptance criteria. The common context
policy for WP-5.2B3B is frozen at **8,192 tokens**.

## Delivery Reviewed

- `md/handoffs/WP-5.2B3A-full-context-comparison.md`
- `md/handoffs/reports/WP-5.2B3A-completion-report.md`
- `md/handoffs/reports/WP-5.2B3A-context-comparison-article-brief.md`

## Independent PM Validation

The manager independently confirmed:

- the repository Poetry environment resolves to the repository `.venv`;
- the Qwen 16K package verifies at its pinned benchmark implementation with
  120 expected cases, 84 successes, 36 failures, and 120 attempts;
- the Phi 16K package verifies at its pinned benchmark implementation with
  120 expected cases, 69 successes, 51 failures, and 120 attempts;
- both packages use the same frozen 30-conversation/120-case scope identity;
- the transition matrices total 120 cases per model;
- task-valid totals and failure categories reconcile to each arm's 120 cases;
- the reports contain no private case identifiers or private content;
- no `.chronicle`, database, ZIP, SQLite, or export artifact is tracked;
- `poetry run pytest -q` passes the complete 446-pass/one-skip suite;
- `poetry run ruff check .`, `poetry check`, and `git diff --check` pass.

The first full-suite PM invocation exceeded its three-minute command timeout
and then hit a Windows stdout-flush error. A quiet rerun with a longer timeout
completed successfully. This is not a product or test failure.

The packages record application version `0.1.0` and benchmark commit
`ea00f45d3e085cf5aae52fb1163bac17f948e411`. Verification from current
v0.2.0 `main` correctly rejects that provenance mismatch. The manager therefore
verified both packages from a temporary detached worktree at the pinned commit,
using that worktree's source package. The worktree was removed afterward.

## Result Reconciliation

| Model | 8K valid | 16K valid | Change | 8K context failures recovered |
| --- | ---: | ---: | ---: | ---: |
| Qwen3.5-4B | 84/120 | 84/120 | 0 | 0/29 |
| Phi-4 Mini | 77/120 | 69/120 | -8 | 0/21 |
| Combined | 161/240 | 153/240 | -8 | 0/50 |

Qwen's 29 context failures became timeouts. Its four invalid-to-valid
transitions came from other failure categories and were offset by four
valid-to-invalid regressions.

Phi retained 11 context failures, moved ten context failures to other failure
boundaries, and recovered none. It had one unrelated invalid-to-valid
transition and nine valid-to-invalid regressions.

Fixed-Pro accounting is accepted:

- Qwen: 84 eligible, 84 completed, zero failed;
- Phi: 69 eligible, 68 completed, one explicit terminal output-schema failure;
- both cache-only replays exited successfully with zero new provider calls and
  byte-stable judge evidence.

## Context Decision

The evidence supports common 8K for prompt development:

- combined validity fell at 16K;
- no prior context failure became a valid output;
- Qwen validity stayed flat while median latency rose materially;
- Phi reliability and whole-case utility regressed;
- 13 previously valid cases became invalid across the two models;
- 16K did not provide a demonstrated recovery benefit under this contract.

The higher Qwen 16K valid-output quality and UTS are retained as useful
survivor-quality evidence, but they do not outweigh flat reliability, zero
context-case recovery, and increased runtime cost for the next prompt study.

## Caveat

Phi's 14 local provider-HTTP failures are retained as observed terminal
failures. They are not proven to have been caused by the larger context window.
This limits causal interpretation of Phi's exact reliability delta. It does not
change the common-context decision because both models had zero recovered
context cases and Qwen showed no validity gain at a substantial latency cost.

## Article Evidence

The companion brief meets the handoff's article-evidence requirements:

- controlled variables and pre-result hypotheses;
- baseline and 16K aggregate tables;
- task-level validity and failure decompositions;
- paired case-transition matrices;
- deterministic and fixed-judge metrics;
- UTS formulas and denominators;
- latency, token, memory, and telemetry limitations;
- chart-ready aggregates;
- supported/prohibited claims;
- publication limitations, observations, headline directions, and outline.

Final article drafting and graphics remain separate owner-approved activities.

## Next Step

WP-5.2B3B is unblocked. Its handoff must:

- pin common context to 8,192;
- freeze the balanced 10-development/20-holdout split before prompt work;
- optimize one global four-task prompt package on the ten development
  conversations;
- preserve the twenty-conversation holdout untouched until WP-5.2B3C;
- retain Qwen, Phi, and Gemini portability evidence without model-specific
  prompt variants.

No executor rework is required for WP-5.2B3A.
