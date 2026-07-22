# WP-5.2B1.2 Validation Review

## Decision

**Accepted on 2026-07-22.** The hosted-candidate extension, real provider evidence, cache proofs,
README/runbook guidance, judge-sensitivity analysis, and tracked primary-judge policy pass PM
validation. The required local template-alignment rework is complete; no provider rerun was
required.

## Rework closure

The repository templates now resolve the primary judge as
`vertex_ai/gemini-3.1-pro-preview`, rubric v1, temperature 0, `max_tokens: 1000`, and
`reasoning_effort: none`. Documentation identifies Gemini 2.5 Flash as diagnostic sensitivity
only. A focused regression loads the tracked templates and asserts the complete effective policy,
so drift back to the diagnostic profile fails the test suite.

## PM validation

- Poetry resolved to the repository-local `.venv`.
- Focused tracked-policy regression: passed.
- Full suite: 429 passed, 1 explicitly opt-in Vertex test skipped.
- Ruff: passed.
- `poetry check`: passed.
- Hosted `bench generate --help`: passed and exposes both disclosure gates.
- `git diff --check`: passed.
- No staged files.
- No tracked `.chronicle`, database, SQLite, ZIP, or export artifacts.
- Tracked documentation privacy scan found no private paths, project IDs, credentials, or tokens.
- README differs from accepted commit `d0736cc` only by the intended hosted-candidate guidance.

The skipped test performs real Vertex calls and remains correctly opt-in. The executor ran the
authorized real synthetic and private provider gates separately and recorded privacy-safe evidence
in the completion report.

## Accepted behavior

- Candidate provenance is structurally either `local-artifact` or `hosted-api`; mixed/fake local
  provenance is rejected.
- Existing implicit-local bundle/package identity remains compatible.
- Hosted generation requires both `--allow-remote` and `--confirm-private-eval` before reading the
  private bundle or constructing provider work.
- Hosted package provenance records provider/model/runtime/application/request identity without
  fake GGUF fields or private provider credentials.
- Candidate reasoning policy reaches provider requests.
- Interrupted judge finalization can be reconciled from complete authoritative attempts and
  metrics without another provider call; inconsistent state still fails closed.
- Candidate and judge identities remain independent, so both diagnostic and primary judges reuse
  immutable candidate packages.

## Accepted evidence

- Both arms used the same frozen two-conversation/eight-case identity.
- Llama 3.2 1B: 8 terminal, 6 schema-valid, 2 invalid; all 6 eligible outputs judged.
- Gemini 3.5 Flash: 8 terminal and 8 schema-valid; all 8 outputs judged.
- Gemini 3.1 Pro Preview completed both primary judge arms with zero failures.
- Gemini 2.5 Flash completed the diagnostic Gemini arm 8/8 with zero failures.
- All cache-only replays exited successfully with zero provider calls and unchanged attempts.
- Candidate packages, historical judge runs, and live/frozen databases remained unchanged.

## Interpretation

The primary comparison remains Gemini 3.1 Pro Preview with frozen rubric v1 for both candidates.
Gemini 2.5 Flash is sensitivity evidence only. Candidate ordering did not change, but Llama's
absolute semantic score moved materially between judges. This demonstrates judge dependence; it
does not establish which judge is correct.

The primary judge is a preview alias, so fixed configuration does not guarantee immutable provider
weights. Future comparisons should run in a bounded time window or repeat a fixed anchor package.
Any prompt/rubric/schema-semantics change requires a new version and rerunning every compared
candidate.

## Residual limits

Two conversations are insufficient for statistical quality, latency, cost, or judge-stability
claims. Before all 120 development cases, use a somewhat larger bounded pilot, explicitly retain
or version rubric v1, and consider automating privacy-safe comparison reports with a generic
`bench compare` command.

## Commit state

Validated changes remain unstaged and uncommitted. Commit ownership remains with the manager after
explicit owner instruction.
