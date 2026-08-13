# WP-5.2B3B.1C GEPA pilot and bounded search completion report

## Outcome

WP-5.2B3B.1C reached a preserved diagnostic stop before candidate generation
and is ready for PM validation. The owner-authorized operation used Gemini 3.1
Pro through Vertex AI only, but the proposal did not complete. The append-only
trial is terminal as `interrupted` with failure category `PicklingError`; the
underlying provider attempts returned HTTP 400/model-not-found responses. No
GEPA candidate or result exists, so the frozen pilot continuation gate did not
pass and no continuation was attempted.

This is not evidence that GEPA improves or fails for Chronicle. It is evidence
that this exact provider/runtime route did not produce a scorable candidate.
P0 remains the only eligible optimizer parent and the current deployment
choice.

## Execution identity and restored state

- Application commit: `5ef7f0a05fce9e36cc9eed6c4db28381f195d6c6`.
- The remote repository was at that exact commit and clean before and after the
  operation.
- The ignored configuration was transitioned from its accepted predecessor by
  changing only `application_commit`; a private adjacent backup was retained.
- Restored state validated one P0 result, one Bootstrap result, P0 parentage,
  Bootstrap attempt `0003` as manager-policy non-promotable, zero prior GEPA
  results, zero prior proposer usage, and zero pending reservations.
- Remote state and budget matched the accepted recovered evidence. The
  separately recovered local readiness metadata was not transferred because it
  was outside the allowed private transfer boundary.
- P0, Bootstrap, prior attempts, results, and fixed-judge evidence were not
  rewritten. The run used `resume`; cache remained disabled.

The pre-call gate passed for the frozen six-train/four-validation development
split, 24 train and 16 validation task positions, forty FABLE references, both
candidate-model artifacts, 8,192-token context, proposer profile, scoring,
privacy, retry, and budget identities. Holdout paths and content were excluded.

## Environment and compute

| Item | Observed value |
|---|---|
| RunPod hardware | One NVIDIA RTX 5090, 32 GB VRAM |
| Region class | EU Secure Cloud |
| Pod rate | US$0.99/hour |
| Pod activity window | 2026-08-13 08:44:15 UTC to 10:29:56 UTC |
| Pod wall time / estimate | Approximately 1.761 hours / US$1.744 |
| Retained storage | 30 GB network volume |
| Python | 3.11 runtime; the patch version was not separately captured before stop |
| DSPy / GEPA | 3.3.0 / 0.1.1 |
| LiteLLM | 1.83.0 |
| Google auth / Gen AI / Vertex SDK | 2.55.2 / 2.12.1 / 1.161.0 |
| Google Cloud CLI | 580.0.0, installed only in ephemeral container storage |
| tmux | 3.2a, installed only in ephemeral container storage |
| LM Studio CLI | retained CLI commit `71bd99c` |

The accepted optimization extra did not itself install the Google Vertex client
runtime. The first `resume` therefore failed during production-adapter
construction after appending and consuming a fourth authorization. It created
no reservation, trial, candidate, model call, or provider call. Exact accepted
top-level Google runtime versions were installed into the retained virtual
environment; `pip check`, compatibility verification, and repository-clean
checks then passed. This was an environment repair, not a production optimizer
or scoring change.

Both local model artifacts were loaded one at a time before the call boundary
at context 8,192, parallelism one, and maximum GPU placement, then unloaded.
The production proposer adapter initialized through ADC without making a
provider request.

## Temporary ADC and provider boundary

ADC used Google's documented no-browser user flow. Authentication state,
Cloud SDK configuration, history, and diagnostic files lived only below the
dedicated RAM directory. The runtime required matching transient project
variables, `global` location, and the Vertex enable flag; values were never
printed or persisted.

The configured proposer was exactly:

- provider: Google Vertex AI;
- LiteLLM model: `vertex_ai/gemini-3.1-pro-preview`;
- location: `global`;
- credential mode: `vertex-adc`;
- concurrency: one;
- cache: disabled;
- configured infrastructure retry: one.

Python ADC default and explicit loading passed, as did no-call production
adapter construction. The real pilot then crossed the authorized provider
boundary. Boolean-only diagnostics classified repeated `BadRequestError`,
`LMInvalidRequestError`, and `OpenAIError` wrappers and found HTTP 400 plus a
model-not-found condition. They found no authentication, permission, billing,
quota, rate-limit, location, or timeout condition. The outer unhandled failure
was serialized as `PicklingError` after 329,682 ms.

No raw prompt, development input, FABLE reference, response, error message,
credential, project value, resource identifier, or private hash entered this
report.

## Accounting

The exception escaped before the production adapter could return measured
usage. The ledger therefore retained its full pre-call reservation, as designed
for fail-closed interruption accounting. Reserved values are conservative
charges and must not be represented as measured provider consumption or an
invoice.

| New GEPA proposal accounting | Retained amount |
|---|---:|
| Candidate positions reserved then released | 1 then 0 |
| Task invocations | 20 |
| Proposer calls | 20 |
| Infrastructure retries | 20 |
| Proposer input tokens | 1,000,000 |
| Proposer output/reasoning tokens | 160,000 |
| Configured compute | 0.833333 hours |
| Proposer cost | US$3.92 |
| Configured compute cost | US$1.294105 |
| Optimizer wall time | 329,682 ms |

Actual provider-call, retry, token, and local candidate-model invocation counts
could not be recovered reliably from the escaped exception and are reported as
unknown. There were zero completed proposals, zero terminal candidate
evaluations, and zero GEPA results. The fail-closed ledger is authoritative for
future capacity decisions.

Final cumulative optimizer-ledger counters are 0 GEPA candidates, 336 task
invocations, 20 proposer calls, 60 infrastructure retries, 1,000,000 proposer
input tokens, 160,000 proposer output/reasoning tokens, 1.704657 configured
compute hours, US$3.92 proposer cost, and US$2.647207 configured compute cost.
The configured compute ledger includes prior accepted activity and is separate
from the Pod wall-clock estimate.

Against the explicit remaining owner envelope recorded before this attempt, the
fail-closed remaining maxima are:

| Boundary | Remaining |
|---|---:|
| GEPA candidates | 12 pilot / 40 total, because no candidate was produced |
| Candidate-model task invocations | 2,664 |
| Logical proposer calls | 224 |
| Proposer input tokens | 11,249,977 |
| Proposer output/reasoning tokens | 1,799,729 |
| Proposer cost | US$45.096702 |
| Configured compute | 10.295343 hours |
| Configured compute cost | US$15.987911 |

These remaining numbers do not authorize another call. The terminal failure is
a new authorization boundary.

## Candidate and gate denominators

| Denominator | Result |
|---|---:|
| GEPA proposal positions started | 1 |
| Completed proposals | 0 |
| Interrupted proposals | 1 |
| Generated candidate packages | 0 |
| GEPA results | 0 |
| Terminal candidate evaluations | 0 |
| Privacy scans / eligible candidates | 0 / 0 |
| Context checks / fitting candidates | 0 / 0 |
| Distinct-from-P0 candidates | 0 |
| Shortlisted candidates | 0 |
| Pilot checkpoint | absent |
| Continuation operations | 0 |

The component-wise continuation gate therefore failed to establish every
candidate-dependent condition:

| Frozen component | Decision |
|---|---|
| At least one privacy-eligible candidate | Fail: none generated |
| Total valid no worse than P0 | Not evaluable; gate fails closed |
| Worst-model valid no worse than P0 | Not evaluable; gate fails closed |
| Minimum-task valid no worse than P0 | Not evaluable; gate fails closed |
| Complete request fits 8,192 tokens | Not evaluable; gate fails closed |
| Prompt distinct from P0 | Not evaluable; gate fails closed |
| Terminal/reconciled candidate accounting | Fail: proposal interrupted before candidate |
| Capacity for one next operation | Budget remained, but cannot override failed criteria |

No candidate was available for semantic agreement, UTS, overhead ranking,
privacy eligibility, local transfer, or shortlist export. The durable run state
remains `in-progress` with a terminal interrupted current attempt rather than
inventing a `pilot-no-improvement` checkpoint after an infrastructure/provider
failure.

## P0 comparison and protected boundaries

P0 was not rerun. Its accepted validation evidence remains:

| Measure | P0 |
|---|---:|
| Total valid | 11/32 |
| Qwen valid | 5/16 |
| Phi valid | 6/16 |
| Conversation summary | 0/8 |
| Work-mode classification | 6/8 |
| Last activity | 0/8 |
| Title assessment | 5/8 |
| FABLE-reference semantic agreement | 0.1266 |

GEPA has no corresponding row because it produced 0 candidates and 0 terminal
outputs. BootstrapFewShot and recovery were not rerun. The fixed judge was not
constructed or called during GEPA, and no new judge artifact appeared. Holdout
files were neither enumerated nor opened; persistent credential scanning
explicitly pruned holdout-named directories. Provider-facing scoring used only
the configured proposer plus existing development inputs and FABLE-derived
deterministic feedback.

## Persistence, immutability, and lifecycle

- The fifth authorization was appended for the real pilot. The prior
  environment-construction failure's fourth authorization remains consumed as
  append-only evidence and was not rewritten into run-state history.
- The interrupted GEPA attempt and current pointer validate. State and budget
  validate their internal hashes, and pending reservations are zero.
- P0, Bootstrap, historical attempts, candidate/result bytes, response hashes,
  fixed-judge evidence, and manifests were preserved.
- The repository remained clean at the execution commit. No result or model was
  deleted.
- ADC revocation exited successfully. Vertex variables were cleared with the
  RAM shell; the exact RAM credential directory and tmux session were removed.
- A persistent-storage scan found zero ADC or Cloud SDK credential database
  files outside pruned holdout paths.
- All models were unloaded and LM Studio was stopped.
- The paid Pod was stopped, not deleted. The Pod, 30 GB network volume,
  repository, models, and all results remain retained. Ongoing GPU spend is
  US$0/hour.
- Temporary local RunPod CLI and Cloud SDK archive downloads created for this
  activity were removed.

## Validation

The exact execution commit's GitHub Actions push run completed successfully in
all four required jobs: Ubuntu and Windows on Python 3.11 and 3.12.

Local validation completed as follows:

- Poetry environment path resolved to the repository `.venv`;
- optimizer compatibility passed with DSPy 3.3.0 and GEPA 0.1.1;
- focused `tests/test_bench_optimization.py` completed at 100%;
- the full pytest suite completed at 100% with one expected skip;
- `ruff check .` passed;
- `poetry check` passed;
- `git diff --check` passed, with only the existing line-ending notice for the
  development ledger;
- `git diff --cached --name-only` was empty;
- `git ls-files .chronicle` was empty;
- a credential/resource-identifier term scan of all changed reports returned
  no matches; and
- the intended report changes remain unstaged and uncommitted.

No shortlist package exists, so package verification is not applicable. Remote
`preflight`, dry-run, and `inspect` passed before the call; post-failure state,
budget, and current-trial validation passed directly before the Pod was stopped.

## Decision and next authorization boundary

Automatic continuation is prohibited. Do not retry, switch provider/model or
region, repair requests, alter retry policy, rerun P0/Bootstrap/recovery, call
the fixed judge, or access the holdout from this checkpoint.

Manager review should decide whether the model-not-found route is an account or
preview-access limitation and whether the unwrapped GEPA `PicklingError` needs a
generic production repair. Any later real proposer attempt requires a clean
accepted commit, revalidation of retained append-only state, a compatible
provider route that still honors the frozen model requirement, and a fresh
explicit owner instruction.
