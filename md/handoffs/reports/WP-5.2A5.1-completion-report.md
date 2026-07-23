# WP-5.2A5.1 Completion Report

## 1. Status and executive summary

Ready for PM validation.

Phi-4 Mini Instruct, Llama 3.2 3B Instruct, and the approved Gemma 3 4B IT fallback
each produced eight of eight schema-valid results under the frozen Chronicle contracts.
All 24 qualification-matrix positions are terminal and successful. No output was repaired,
rewritten, retried, or accepted through a model-specific adapter.

The preferred Gemma 4 E2B IT artifact was evaluated only at the required pre-matrix compatibility
gate. It loaded successfully but returned empty answer content with a length finish reason despite
disabled-thinking controls, and the application path rejected the empty structured response.
Gemma 4 is therefore **not qualified - runtime/structured-output compatibility**. Its probes are
not included in the 24-position matrix.

## 2. Clean preflight and immutable-baseline evidence

Execution began from the manager-provided clean HEAD. `git status --short` was empty and Poetry
resolved to this repository's `.venv`.

The accepted frozen database opened read-only and immutable, passed `PRAGMA integrity_check`, kept
schema version 3, contained 711 conversations and 28,370 messages, had no WAL/SHM sidecars, and
rejected a write probe. The frozen database, live database, snapshot manifest, accepted
WP-5.2B1.4 package identities, and WP-5.2B1.3 historical package identities matched their private
accepted baselines.

Preflight recorded approximately 276 GB free disk, approximately 32 GiB physical RAM, AC power,
AC sleep disabled, a 4-core/8-thread 11th-generation Intel mobile CPU, and integrated Intel Iris Xe
graphics. LM Studio CLI commit `9902c3a` used the selected
`llama.cpp-win-x86_64-vulkan-avx2@2.25.2` engine.

## 3. Common input, task, and settings contract

The same invented four-message conversation and the same shortest accepted frozen development
conversation were selected and hashed before candidate output was inspected. The accepted task
and model templates were also hashed privately before execution.

The matrix used:

- conversation summary, work-mode classification, last activity, and title assessment;
- configured context 8,192;
- parallelism and concurrency 1;
- temperature 0;
- retries 0;
- strict structured output;
- accepted task-owned output limits;
- no FABLE reference in candidate generation;
- deterministic application schema, evidence-membership, date, output-length, and cross-field
  validation.

## 4. Phi artifact, runtime, transport, and eight-case results

The official lineage was Microsoft Phi-4 Mini Instruct: a 3.8B dense Phi-family model with an
advertised 128K context and MIT license. A reputable LM Studio Community Q4_K_M GGUF was pinned
privately by repository revision, filename, exact byte size, and SHA-256. The public, ungated
artifact was downloaded only after owner approval and independently matched both pinned values
before import.

LM Studio loaded the artifact as a 2.49 GB local model at context 8,192 and parallelism 1. The
intended identifier appeared at `/v1/models`. A direct strict OpenAI-compatible probe and the
application-owned LiteLLM probe both returned non-empty schema-valid JSON with stop finish reasons,
correct model/provider identity, and no reasoning-budget loss.

Phi completed 8/8 matrix positions: 4/4 synthetic and 4/4 frozen.

## 5. Llama 3B artifact, runtime, transport, and eight-case results

The official lineage was Meta Llama 3.2 3B Instruct: a 3.21B autoregressive Llama model with an
advertised 128K context under the Llama 3.2 Community License and Acceptable Use Policy. The owner
personally completed the gated access process before download approval. A reputable LM Studio
Community Q4_K_M GGUF was pinned privately and independently matched its exact expected size and
SHA-256 before import.

LM Studio loaded the artifact as a 2.02 GB local model at context 8,192 and parallelism 1. The
intended identifier appeared at `/v1/models`. Direct and application-owned strict probes returned
non-empty schema-valid JSON with stop finish reasons and coherent identity.

Llama completed 8/8 matrix positions: 4/4 synthetic and 4/4 frozen. Two last-activity outputs used
the literal string `"[]"` as a blocker item. This awkward semantic value remained schema-valid
under the accepted contract and was preserved without repair or retry.

## 6. Gemma 4 compatibility decision, selected Gemma artifact, and eight-case results

The preferred Google Gemma 4 E2B IT model is 2.3B effective parameters but 5.1B total parameters
including Per-Layer Embeddings. Its selected Q4_K_M artifact was 3.43 GB, demonstrating why the
effective label is not a storage or runtime-memory figure. The Apache-2.0 LM Studio Community
artifact matched its privately pinned size and SHA-256 before loading.

Gemma 4 imported and loaded at context 8,192, parallelism 1, with the correct API identifier.
However, a direct strict-schema request using disabled-thinking controls ended with a length finish
reason and empty answer content. The equivalent application request also returned empty structured
content, which Chronicle normalized to `invalid_json`. The attempt stopped at that exact boundary:
no retry, task call, fallback substitution, runtime change, context change, reasoning change,
output-limit change, or code change occurred.

Gemma 4 is **not qualified - runtime/structured-output compatibility**. These compatibility probes
are outside the qualification matrix.

The approved fallback was Google Gemma 3 4B IT under the custom Gemma Terms. The owner personally
completed the official access process. The selected LM Studio Community Q4_K_M GGUF was 2.49 GB
and matched its privately pinned size and SHA-256 before loading. LM Studio loaded it at context
8,192 and parallelism 1. Direct and application-owned strict probes both returned non-empty,
schema-valid JSON with stop finish reasons.

Gemma 3 completed 8/8 matrix positions: 4/4 synthetic and 4/4 frozen.

## 7. Complete 24-position accounting

| Candidate | Synthetic summary | Synthetic mode | Synthetic activity | Synthetic title | Frozen summary | Frozen mode | Frozen activity | Frozen title | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Phi-4 Mini Instruct | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 8/8 |
| Llama 3.2 3B Instruct | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 8/8 |
| Gemma 3 4B IT | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 8/8 |
| **Total** | **3/3** | **3/3** | **3/3** | **3/3** | **3/3** | **3/3** | **3/3** | **3/3** | **24/24** |

Each fraction reports schema-valid successes over required positions. All positions are terminal;
there are no unaccounted, cached, repaired, or retried positions.

## 8. Schema, evidence, cross-field, and failure matrix

| Candidate | Schema valid | Evidence IDs valid | Dates valid | Cross-field valid | Output limits valid | Matrix failures |
|---|---:|---:|---:|---:|---:|---:|
| Phi-4 Mini Instruct | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | 0 |
| Llama 3.2 3B Instruct | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | 0 |
| Gemma 3 4B IT | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | 0 |

Gemma 4's separate compatibility failure is deliberately excluded from these denominators.

## 9. Latency, usage, and runtime comparison

Stored task latency measures the application call and validation boundary, not download, import,
model-load, or operator time.

| Candidate | Sum | Minimum | Median | Maximum | Usage available |
|---|---:|---:|---:|---:|---:|
| Phi-4 Mini Instruct | 126.293s | 13.422s | 14.180s | 19.717s | 8/8 |
| Llama 3.2 3B Instruct | 168.682s | 18.311s | 21.163s | 23.593s | 8/8 |
| Gemma 3 4B IT | 301.605s | 24.140s | 35.344s | 62.734s | 8/8 |

| Candidate | Prompt tokens | Completion tokens | Total tokens | Usage missing |
|---|---:|---:|---:|---:|
| Phi-4 Mini Instruct | 2,689 | 574 | 3,263 | 0 |
| Llama 3.2 3B Instruct | 2,946 | 534 | 3,480 | 0 |
| Gemma 3 4B IT | 3,172 | 1,049 | 4,221 | 0 |

Provider-reported usage reflects the same local LM Studio route but can still differ because each
model uses its own tokenizer. The values are not a quality metric.

## 10. Qualified and rejected admission decisions

- **Qualified: Phi-4 Mini Instruct.** Provenance and transport are coherent; all eight positions
  passed without repair, retry, or adapter; runtime fit and latency are operationally feasible.
- **Qualified: Llama 3.2 3B Instruct.** Owner-controlled license access, provenance, transport,
  8/8 contract validity, and runtime fit all passed. The preserved blocker-string oddity is a
  semantic-quality observation for a later benchmark, not a contract failure.
- **Qualified: Gemma 3 4B IT fallback.** Owner-controlled access, provenance, strict transport,
  8/8 contract validity, and runtime fit passed. It is slower but feasible.
- **Rejected: Gemma 4 E2B IT.** Not qualified under the installed fixed runtime because
  disabled-thinking strict structured output returned empty answer content and exhausted the
  answer limit. No matrix run was authorized after that gate.

## 11. Implementation defects and fixes

No generic application defect was identified and no tracked code, prompt, selector, schema,
finalizer, reasoning policy, output limit, runtime, or model-profile implementation was changed.
No focused fix cycle was used.

The only temporary private configuration adjustment made before matrix execution set the already
accepted local profile explicitly to context 8,192 and retries 0. It was common to all three
matrix candidates, did not alter tracked files, and the owner's prior private profile was restored
after execution.

## 12. Privacy, immutability, and tracking checks

All downloaded models, machine-specific paths, private model revisions and hashes, selected source
content, prompts, raw outputs, invalid responses, databases, result records, and operator notes
remain ignored under `.chronicle/eval/dev-v1/`.

No remote provider received private data. The frozen database was never written. Qualification
used separate writable copies. No accepted WP-5.2B1.4 or WP-5.2B1.3 artifact was regenerated,
repackaged, judged, or mutated. No model file or private evidence is tracked or staged.

Post-run checks passed for immutable baselines, ignored/private tracking, Ruff, Poetry metadata,
relevant focused tests, `git diff --check`, and staged-file inspection.

## 13. Recommendation for the next 40/120-case handoff

Admit Phi-4 Mini Instruct, Llama 3.2 3B Instruct, and Gemma 3 4B IT to the next common 40-case
checkpoint using the unchanged frozen contracts. Preserve per-candidate no-retry semantics and
explicitly measure semantic quality so schema-valid but awkward values remain visible.

Only candidates meeting the separately approved checkpoint policy should advance to a 120-case
arm. Do not include Gemma 4 E2B IT unless a future work package explicitly authorizes a newer
runtime compatibility recheck; it should not be retried opportunistically.

## 14. Line-by-line acceptance checklist

1. Clean tracked checkout and full HEAD recorded privately: pass.
2. Poetry environment resolved to repository `.venv`: pass.
3. Frozen/live/database/package/historical baselines unchanged: pass.
4. Frozen database read-only at 711 conversations and 28,370 messages: pass.
5. Disk, AC power, sleep policy, runtime, and hardware class recorded: pass.
6. Common synthetic and frozen inputs selected before candidate output: pass.
7. Accepted task/model templates and selected inputs hashed privately: pass.
8. Official identity, license/access, conversion provenance, revision, size, and hash pinned
   privately for every downloaded artifact: pass.
9. Owner approval obtained before every exact download; gated terms accepted only by owner: pass.
10. Every downloaded artifact independently matched exact size and SHA-256 before load: pass.
11. LM Studio identity, context 8,192, parallelism 1, device class, and loaded footprint recorded:
    pass.
12. Direct and application-owned transport gates completed for each matrix candidate: pass.
13. Phi matrix completed and accounted 8/8: pass.
14. Llama 3B matrix completed and accounted 8/8: pass.
15. Gemma 4 failure stopped at the exact compatibility boundary without automatic changes: pass.
16. Gemma 3 fallback matrix completed and accounted 8/8: pass.
17. Complete 24-position schema/evidence/cross-field/failure accounting provided: pass.
18. No output repair, silent retry, prompt tuning, or model-specific adapter used: pass.
19. No 40-case/120-case run, Vertex call, judge call, or database write occurred: pass.
20. No code change or generic fix cycle was required: pass.
21. Private evidence remains ignored, untracked, and unstaged: pass.
22. Required no-code validation completed successfully: pass.
23. Delivery is unstaged and uncommitted for manager validation: pass.
