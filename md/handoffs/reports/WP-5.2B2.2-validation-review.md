# WP-5.2B2.2 Validation Review

## PM decision

**Accepted on 2026-07-24.**

WP-5.2B2.2 completes the planned common 120-case development measurement for the three retained
local candidates:

- Phi-4 Mini;
- Llama 3.2 3B;
- Gemma 3 4B.

The six aligned complete-scope arms now available for LP-4.1 are:

- Gemini 3.5 Flash cloud control;
- Qwen3.5-4B local control;
- Llama 3.2 1B local floor;
- Phi-4 Mini;
- Llama 3.2 3B;
- Gemma 3 4B research comparator.

This acceptance closes the baseline model-execution phase. It does not approve article claims,
prompt tuning, a composite score, or an independent evaluation claim.

## Acceptance evidence

### Candidate accounting

| Candidate | Expected | Schema-valid | Failed | Terminal | Unaccounted |
|---|---:|---:|---:|---:|---:|
| Phi-4 Mini | 120 | 77 | 43 | 120 | 0 |
| Llama 3.2 3B | 120 | 71 | 49 | 120 | 0 |
| Gemma 3 4B | 120 | 62 | 58 | 120 | 0 |
| **Total** | **360** | **210** | **150** | **360** | **0** |

The per-task validity counts reconcile to each candidate total:

- Phi: 14 summary + 18 work mode + 29 last activity + 16 title = 77;
- Llama 3B: 12 + 19 + 23 + 17 = 71;
- Gemma 3: 12 + 19 + 25 + 6 = 62.

All candidate failures remain explicit. No candidate response was repaired, promoted from the
checkpoint, or retried as a quality correction.

### Judge accounting

| Candidate | Eligible | Completed | Failed | Skipped invalid |
|---|---:|---:|---:|---:|
| Phi-4 Mini | 77 | 77 | 0 | 43 |
| Llama 3.2 3B | 71 | 69 | 2 | 49 |
| Gemma 3 4B | 62 | 62 | 0 | 58 |
| **Total** | **210** | **208** | **2** | **150** |

The two Llama judge failures remain terminal provider-invalid-JSON outcomes after the one
authorized bounded retry. They were not converted to scores or silently excluded from accounting.

### Identity and immutability

- all three complete arms independently reconstruct the accepted ordered 120-case identity;
- their first 40 positions match the accepted checkpoints;
- the complete packages are new and independent;
- checkpoint attempts were not merged, copied, promoted, or modified;
- frozen/live databases, snapshot manifest, historical packages, and historical judge evidence
  remained unchanged;
- candidate and judge cache-only replays retained byte-identical evidence;
- no private evaluation artifact or credential is tracked.

### Contract preservation

The accepted contract remained:

- Q4_K_M artifacts;
- LM Studio/llama.cpp accepted runtime;
- context 8,192;
- parallelism 1;
- temperature 0;
- candidate retries 0;
- accepted task prompts, selectors, schemas, finalizers, and FABLE references;
- Vertex AI `gemini-3.1-pro-preview` in `global`;
- ADC authentication;
- rubric v1, temperature 0, 1,000-token cap, reasoning `none`.

No prompt, schema, context, runtime, quantization, judge, rubric, provider, or authentication route
was substituted.

## Report review

The completion report contains the required privacy-safe:

- complete and per-task reliability;
- failure taxonomy;
- full deterministic confusion matrices;
- per-label precision, recall, and support;
- fixed-Pro task dimensions and denominators;
- wall time and overall/per-task latency;
- exact usage availability and totals;
- runtime, artifact class, context, and hardware provenance;
- six-candidate reliability, deterministic, and latency comparison;
- cache, privacy, immutability, and limitation evidence.

The three historical arms' detailed semantic dimensions remain in the accepted
`WP-5.2B1.4-completion-report.md`; the three new arms are in this completion report. LP-4.1 must
consolidate those tracked aggregate sources before selecting article metrics. A single semantic
number must not be invented without an explicit formula and sensitivity analysis.

## PM validation commands

```text
poetry env info --path
-> C:\work\Github\mcp-chat-chronicle\.venv

poetry run pytest tests/test_ai_adapter.py tests/test_bench.py -q
-> 74 passed, 1 skipped

poetry run ruff check .
-> All checks passed!

poetry check
-> All set!

git diff --check
-> passed
```

The first focused-test invocation exceeded the shell's two-minute command timeout; the identical
command completed successfully when rerun with a longer timeout. `poetry check` initially met the
documented Windows sandbox launcher error and passed when rerun outside that launcher boundary.
Neither event was a project or test failure.

The full repository suite was not rerun during PM validation because the executor made no tracked
application, harness, dependency, or test change.

## Baseline observations carried to LP-4.1

These are development observations, not publication-ready claims:

1. Gemini is the strongest reliability control at 112/120 schema-valid.
2. Qwen is the strongest local reliability result at 84/120.
3. Phi follows at 77/120 and is particularly reliable on last activity.
4. Llama 3B improves materially over Llama 1B but remains weak on work-mode and blocker quality.
5. Gemma's valid outputs can score well, but 62/120 whole-package validity and 6/30 title validity
   make it a weak operational candidate.
6. Fixed context and timeout failures materially affect every local model's effective utility.
7. Quality among valid outputs and whole-package reliability must remain separate axes.

## Residual limitations

- The corpus is selected development data, not an untouched evaluation set.
- FABLE provides silver references without owner adjudication.
- The judge is a preview model and historical/current judge windows differ.
- Two Llama outputs have no semantic judge score.
- Local runtime results apply to one laptop/runtime/quantization configuration.
- Token totals are tokenizer-specific and not directly comparable across providers.
- Prompt tuning could change results and therefore remains a separately versioned follow-up.

## Next action

Return to LP-4.1 and:

1. consolidate the accepted B1.4 and B2.2 aggregate evidence;
2. reproduce the proposed utility score and sensitivity analysis from private per-case aggregates;
3. select the smaller publication metric set;
4. identify task difficulty and model-routing observations;
5. agree article claims, caveats, visualizations, and headline with the owner;
6. keep WP-5.2B3 prompt strategy testing separate from the baseline article dataset.

## Commit ownership

The executor correctly left the delivery unstaged and uncommitted. The PM/manager commits only
after explicit owner instruction.
