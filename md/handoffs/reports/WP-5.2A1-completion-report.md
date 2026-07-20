# WP-5.2A1 Completion Report: Llama 3.2 1B Evaluation Floor

## Status

Ready for PM validation.

## Executive summary

The downloaded Bartowski Llama 3.2 1B Instruct `Q4_K_M` GGUF is now a pinned,
reproducible Chronicle evaluation-floor candidate. Fresh direct LM Studio and
LiteLLM probes succeeded with strict JSON Schema through the loopback-only
`lm_studio/llama-3.2-1b-instruct` route. Chronicle synthetic and bounded private
smokes each produced three schema-valid successes and one explicit
`title-assessment` schema failure. No prompt, task, schema, selector, finalizer,
cache, or product-code change was needed.

Schema validity was not treated as semantic correctness. The baseline was not
prompt-tuned, repaired, retried automatically, or auto-corrected to improve the
floor model.

## Evidence basis and preflight

The handoff's owner smoke was diagnostic context only. All evidence below is fresh
executor evidence. Poetry resolved to the repository `.venv`; the starting
application commit was `8881c9afd79b9429f2e829062167389afcda7e03`.

The accepted WP-5.1.2A/B private basis revalidated unchanged:

- recomputed snapshot SHA-256 matched the accepted private WP-5.1.2A manifest;
- SQLite integrity `ok`, schema version 3, no WAL/SHM dependency;
- 711 conversations and 28,370 messages;
- frozen selection resolves to 30 cases;
- 120/120 FABLE references pass the accepted validation;
- task catalog and selection hashes match their recorded values;
- `.chronicle` remains ignored and untracked.

No tracked planning/private-manifest discrepancy was found.

## Candidate provenance

| Field | Pinned value |
| --- | --- |
| Display model | Llama 3.2 1B Instruct |
| Repository | `bartowski/Llama-3.2-1B-Instruct-GGUF` |
| Artifact | `Llama-3.2-1B-Instruct-Q4_K_M.gguf` |
| Format / quantization | GGUF / `Q4_K_M` |
| Size | 807,694,464 bytes |
| SHA-256 | `6f85a640a97cf2bf5b8e764087b1e83da0fdb51d7c9fab7d0fece9385611df83` |
| Architecture / parameters | Llama / 1B |
| LM Studio model ID | `llama-3.2-1b-instruct` |
| LiteLLM route | `lm_studio/llama-3.2-1b-instruct` |
| Endpoint | loopback `127.0.0.1:1234`; no credential |
| Advertised / configured context | 131,072 / 8,192 tokens |

Runtime provenance: LM Studio CLI commit `9902c3a` (server semantic version is not
exposed by the installed CLI/API), local automatic device selection, Python
3.12.0, LiteLLM 1.83.0, and Windows 11 Pro 64-bit. Hardware was an Intel Core
i7-1185G7 (4 cores/8 threads), 31.7 GB RAM, Intel Iris Xe integrated graphics,
with no NVIDIA runtime. Reasoning was not applicable/enabled.

The dedicated ignored profile used strict JSON Schema, temperature 0, timeout 180
seconds, retries 0, and concurrency 1. Task limits remained unchanged:
conversation summary 350, work mode 250, last activity 350, and title assessment
250 output tokens. The copied task catalog changed only the four profile aliases;
prompt/schema/selector/version/finalizer/generation content remained accepted.

## Direct invented probes

| Probe | Outcome | Latency |
| --- | --- | ---: |
| `/v1/models` intended model | exposed | n/a |
| LM Studio text completion | success | 2,548 ms |
| LM Studio JSON object | explicit HTTP rejection | 21 ms |
| LM Studio strict JSON Schema | success | 1,415 ms |
| LiteLLM strict JSON Schema | success | 3,639 ms |

The JSON-object rejection matches the accepted runtime boundary. Strict schema
was passed through LiteLLM to the loopback endpoint; no remote fallback existed.

## Synthetic Chronicle smoke

Dry-run selected 366 characters for each task. Estimated input/request token
ceilings were respectively 253/603, 297/547, 338/688, and 289/539, all below the
8,192 configured context.

| Task | Provider | JSON/schema/evidence/date result | Latency |
| --- | --- | --- | ---: |
| conversation-summary | response received | valid success | 13,311 ms |
| work-mode-classification | response received | valid success | 13,531 ms |
| last-activity | response received | valid success | 15,703 ms |
| title-assessment | response received; JSON parsed | `schema_validation` failure | 12,843 ms |

The unchanged summary rerun was a cache hit and appended no row. A subsequent
`--force` run appended a second successful summary attempt (12,125 ms). Thus all
calls terminated cleanly and at least one task proved full end-to-end integration.

## Bounded private-development smoke

Exactly one frozen case was selected before output inspection by the required
smallest accepted-input estimate, with ties broken by frozen selection order. A
disposable writable database was created from the frozen snapshot with SQLite's
online backup API. All private output remained in the ignored candidate area.

| Task | Request/provider | JSON/application boundary | Latency |
| --- | --- | --- | ---: |
| conversation-summary | completed/received | schema, cross-field, evidence, dates valid | 13,014 ms |
| work-mode-classification | completed/received | schema, cross-field, evidence valid | 13,375 ms |
| last-activity | completed/received | schema, cross-field, evidence valid | 15,172 ms |
| title-assessment | completed/received | JSON parsed; `schema_validation` failure | 13,390 ms |

The known title-assessment failure shape was preserved as benchmark evidence. No
private title, path, URL, identifier, message, prompt, reference, or generated
content appears here. These smoke results make no semantic-quality claim.

## Private manifest and no-write evidence

The machine-readable manifest is at
`.chronicle/eval/dev-v1/candidates/llama-3.2-1b-instruct-q4_k_m/candidate-manifest.json`
relative to `.chronicle`. Its schema is
`chronicle-evaluation-floor-candidate-v1`, its ID is
`llama-3.2-1b-instruct-q4_k_m`, and deterministic JSON parsing/provenance checks
pass. It contains no credentials, prompts, inputs, outputs, references, or
chain-of-thought.

Post-smoke evidence:

- frozen snapshot SHA-256 unchanged;
- live database SHA-256 unchanged;
- scratch `PRAGMA integrity_check` is `ok`;
- conversations, messages, sources, projects, ingest runs, enrichments,
  knowledge items, and FTS rows match the frozen source exactly;
- only allowed append-only `ai_task_results` state differs in scratch;
- synthetic/scratch DBs, manifests, outputs, and logs are ignored and untracked.

## Tracked files changed

- `docs/ai-tasks.md`: added the optional pinned evaluation-floor setup while
  retaining Qwen3.5-4B as the recommended functional smoke.
- `md/handoffs/reports/WP-5.2A1-completion-report.md`: this privacy-safe report.

No product code, tracked YAML template, prompt, schema, finalizer, or test changed.
The PM-owned `md/master-plan.md` modification and untracked handoff were preserved.

## Validation

- Focused AI adapter/config/execution/cache/CLI suite: 76 passed.
- Full suite: 373 passed in 47.00 seconds.
- `poetry run ruff check .`: passed.
- `poetry run chronicle --help`: passed.
- `poetry run chronicle --ai-task list`: passed without a model call.
- `git diff --check`: passed.
- Tracking query showed only committed synthetic test fixtures; no private
  `.chronicle` artifact, database, archive, or export is tracked.

## PM-validation rework

The evidence-contract and report-privacy corrections requested in
`WP-5.2A1-validation-review.md` are complete:

- Private smoke records now distinguish `attempt_row_stored` from
  `validated_result_json_stored`. Both failed title attempts report a persisted
  attempt row and no validated result JSON.
- Every boundary now uses `pass`, `fail`, `not_evaluated`, or `not_applicable`.
  Checks skipped after title application-schema failure are `not_evaluated`, not
  false failures. Existing evidence did not directly establish a separate
  cross-field boundary beyond application-schema validation, so it is not
  misreported as a cross-field failure.
- Direct, synthetic, and private-development smokes have three distinct stable
  run IDs and three distinct relative artifact references.
- The private summary and candidate manifest were regenerated from persisted
  evidence only. No model call, prompt change, contract change, task-catalog
  change, or product-code change occurred.
- Before/after SHA-256 comparison confirmed all 11 existing evidence artifacts
  in the rework set were byte-identical, including model evidence, private logs,
  databases, catalogs, frozen selection, and frozen snapshot.
- The private snapshot fingerprint was removed from this tracked report. The
  public model GGUF hash remains as permitted artifact provenance.

Fresh post-rework validation again passed the private manifest/summary parsing,
tri-state consistency, distinct run/artifact identity, frozen/live no-write
checks, the full suite (373 passed in 44.76 seconds), Ruff, CLI help/task
discovery, an empty private database/archive tracking query, and diff hygiene.

## Limitations and WP-5.2B1 follow-up

LM Studio does not expose a semantic server version or exact automatic device
identifier through the available local surfaces. The runtime advertises 131,072
tokens, but only 8,192 was configured and tested. Smoke validity does not establish
semantic quality. WP-5.2B1 should treat this private manifest as a precursor,
define its portable generation-package schema independently, preserve invalid raw
responses privately, and score valid and failed cases without excluding failures.

## Acceptance checklist

1. Poetry/worktree preflight: pass.
2. Frozen snapshot/corpus/task catalogs: pass.
3. Exact artifact hash and stable locator: pass.
4. Runtime/device/context/settings provenance: pass, with disclosed device/version limitation.
5. Loopback-only LiteLLM route: pass.
6. Direct invented structured probes: pass.
7. Dedicated ignored profile: pass.
8. Four synthetic calls explicitly accounted for: pass.
9. At least one synthetic schema-valid result: pass (three).
10. Cache hit: pass.
11. Forced append: pass.
12. Exactly one preselected private case: pass.
13. Private task boundary accounting: pass.
14. Title failure preserved: pass.
15. No contract/version changes: pass.
16. No semantic-quality claim: pass.
17. Complete private manifest/no credentials: pass.
18. Live/frozen fingerprints unchanged: pass.
19. No private artifact tracked: pass.
20. Documentation distinguishes floor/control: pass.
21. Focused/full/Ruff/help/diff validation: pass.
22. Required report: pass.
23. Nothing staged or committed: pass.

## Final worktree

```text
 M docs/ai-tasks.md
 M md/master-plan.md
?? md/handoffs/WP-5.2A1-llama-3.2-1b-evaluation-floor-integration.md
?? md/handoffs/reports/WP-5.2A1-completion-report.md
?? md/handoffs/reports/WP-5.2A1-validation-review.md
```

Nothing was staged or committed.
