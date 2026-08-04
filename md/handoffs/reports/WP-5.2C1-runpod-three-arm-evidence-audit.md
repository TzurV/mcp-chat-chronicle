# WP-5.2C1 RunPod Three-Arm Evidence Audit

Date: 2026-08-04

Status: all three arms evaluated locally and with Vertex; the two R8 results
are waiver-judged and remain not strict manager-valid.

Publication purpose: source-of-truth notes for a future LinkedIn article.

## Scope

The study ran the same frozen first 30 Chronicle conversations and four
accepted tasks, producing 120 terminal candidate positions per arm:

1. remote R8 original at context 8,192;
2. remote R8 independent repeat at context 8,192;
3. remote R262K at the model-advertised maximum context 262,144.

Candidate generation ran on one retained RunPod Secure Cloud Pod. Package
verification, deterministic scoring, and Vertex judging ran on the owner's
Windows computer. No repository commit was created for the study.

## Article-Safe Hardware And Runtime Specification

| Field | Audited value | Evidence status |
|---|---|---|
| Provider | RunPod Secure Cloud | control-plane record |
| Datacentre | EU-CZ-1, Czech Republic | control-plane record |
| GPU allocation | 1 x NVIDIA GeForce RTX 5090 | control plane and `nvidia-smi` agree |
| GPU memory | 32 GB marketed; 32,607 MiB visible | `nvidia-smi`; NVIDIA specification |
| GPU architecture | NVIDIA Blackwell | NVIDIA specification |
| CUDA cores | 21,760 | NVIDIA specification; not measured by the study |
| Allocated CPU | 32 vCPUs | RunPod control plane |
| Physical CPU model | not captured | publication limitation |
| Allocated RAM | 62 GB | RunPod control plane |
| Container disk | 50 GB | RunPod control plane |
| Persistent volume | 50 GB mounted at `/workspace` | RunPod control plane |
| Container image | RunPod PyTorch 2.8.0, Python 3.11, CUDA 12.8.1, cuDNN development image on Ubuntu 22.04; exact image digest retained privately | pinned control-plane identity |
| Guest OS | Ubuntu 22.04, x86-64 | returned runtime evidence |
| Kernel | Linux 6.8.0-124-generic | returned runtime evidence |
| NVIDIA driver | 595.71.05 | returned `nvidia-smi` evidence |
| Candidate runtime | LM Studio `lms` CLI commit `71bd99c`; `llmster 0.0.20-1` | returned runtime evidence |
| Candidate model | Qwen3.5 4B, GGUF Q4_K_M | returned model inventory |
| Model size | 2,707,513,696 bytes | returned model inventory |
| Model SHA-256 | retained privately and verified | binary-provenance hash; intentionally omitted from tracked documentation |
| Candidate concurrency | 1 | pinned model profile |
| Generation | temperature 0, maximum 500 output tokens | pinned task/model profile |
| Connectivity | proxied SSH only; no public inference endpoint | control-plane and listener gates |
| Compute rate | US$0.99/hour; US$1.004/hour including retained storage while running | account/control-plane evidence |

NVIDIA documents the RTX 5090 as a Blackwell GPU with 32 GB GDDR7 and 21,760
CUDA cores:

- <https://marketplace.nvidia.com/en-us/consumer/graphics-cards/geforce-rtx-5090-founders-edition/>
- <https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf>

### Hardware-evidence limitation

The container reported `nproc=256` and approximately 504 GiB through
`/proc/meminfo`. These are host-visible totals and conflict with the purchased
32-vCPU/62-GB control-plane allocation. They must not be presented as the Pod
specification. The physical CPU model and cgroup quota files were not captured
before the Pod stopped. The study therefore has a complete service-level Pod
specification but not a complete physical-host specification.

All three arms ran in one uninterrupted resumed-Pod session, so the audited
hardware/runtime identity applies to every arm.

## Candidate Generation Results

| Measure | R8 original | R8 repeat | R262K maximum |
|---|---:|---:|---:|
| Context | 8,192 | 8,192 | 262,144 |
| Terminal positions | 120 | 120 | 120 |
| Schema-valid outputs | 89 | 89 | 119 |
| Reliability | 74.17% | 74.17% | 99.17% |
| Failures | 31 | 31 | 1 |
| Generation wall time | 131 s | 129 s | 169 s |
| Peak sampled GPU memory | 3,712 MiB | 4,219 MiB | 11,896 MiB |
| Strict package verification | blocked | blocked | passed |

The accepted local 8K baseline took 4 hours 43 minutes 30.782 seconds. Against
that baseline, the two comparable remote R8 runs were approximately 129.9x and
131.9x faster. The R262K arm was approximately 100.7x faster in wall time, but
that ratio is contextual rather than like-for-like because the context setting
changed.

R262K took about 31% longer than the R8 repeat but converted 30 failed
positions into valid outputs. Peak R262K GPU memory was about 11.6 GiB, below
half of a 24 GiB target card.

## R8 Repeatability

The original and repeat R8 runs had identical success/failure status on all
120 positions:

- 89 `success -> success`;
- 31 `failed -> failed`;
- no reliability transition.

Among the 89 shared successes, 85 results were structurally identical and
four changed, exactly one in each task. This is 95.51% exact structured-result
stability among successful outputs.

Both R8 packages reproduced the same failure boundaries:

- 29 context-length failures;
- one schema-validation failure;
- one `invalid_json` failure on the same summary case.

The `invalid_json` failure occurred before the client returned a response
object. Exact commit `7e4dbc4` therefore recorded no raw-invalid payload, while
the exact verifier requires raw evidence for every `invalid_json` attempt.
Both immutable R8 packages consequently fail strict manager verification. This
is an evaluation-evidence implementation defect, not transfer corruption; all
archive and candidate hashes matched.

## R8 Evaluator Waiver And Vertex Evaluation

The owner approved an evaluator-only waiver for the original and repeat R8
packages. A separate detached checkout of exact commit `7e4dbc4` bypassed only
the missing `raw_invalid_file` gate when all of these conditions matched:

- the immutable package content ID was one of the two approved R8 IDs;
- the alias was exactly `c014--conversation-summary`;
- the attempt was a failed `invalid_json` result with no result, raw file, or
  provider/model response provenance;
- the explicit dated waiver environment value was present.

The candidate ZIPs were not modified and no evidence was fabricated. All
other verification gates remained active. These results are therefore
labelled **waiver-judged, not strict manager-valid**.

| Measure | R8 original | R8 repeat |
|---|---:|---:|
| Judge-eligible outputs | 89 | 89 |
| Successful judge verdicts | 89 | 89 |
| Terminal judge failures | 0 | 0 |
| Invalid candidates skipped | 31 | 31 |
| Overall mean (0-4) | 3.813 | 3.815 |
| Percentage of maximum | 95.33% | 95.38% |
| Conversation summary | 3.958 (19) | 3.958 (19) |
| Last activity | 3.772 (30) | 3.789 (30) |
| Title assessment | 3.910 (20) | 3.890 (20) |
| Work-mode classification | 3.613 (20) | 3.613 (20) |

Both cache-only replays passed with 89 attempt files and zero cache misses or
new provider calls. The overall scores differ by only 0.0022 points on the
four-point scale, or 0.055 percentage points.

Of the 89 shared valid positions, 85 had identical candidate cache identities
and four changed between candidate runs. Fresh independent judging produced
identical score vectors on 83 positions. For the 85 identical candidates, 81
score vectors were identical and four differed, demonstrating a small amount
of judge variance even at temperature zero.

## R262K Deterministic Evaluation

The R262K package passed full frozen-authority verification. It produced 119
valid outputs and one properly evidenced summary schema-validation failure.
All 119 successful outputs passed evidence-membership and cross-field checks.

Reference-label exact agreement was:

- title fit: 76.67%;
- work mode: 56.67%;
- last activity: 53.33%.

These are deterministic label-agreement measures, not semantic quality scores.

## R262K Vertex Gemini Evaluation

The owner explicitly authorized disclosure for judging. Local orchestration
used ADC, Vertex AI `gemini-3.1-pro-preview` in `global`, rubric v1,
temperature 0, and a maximum of 1,000 judge output tokens. Candidate requests
were blinded. The frozen database itself was not sent; each eligible request
contained only its selected source excerpt, candidate output, FABLE reference,
and rubric.

Judge accounting:

| Measure | Result |
|---|---:|
| Candidate positions | 120 |
| Judge-eligible candidate outputs | 119 |
| Successful judge verdicts | 118 |
| Terminal judge failures | 1 (`provider_invalid_json`) |
| Invalid candidates skipped | 1 |
| Unaccounted | 0 |

Aggregate semantic score across the completed verdicts was 3.846/4, or 96.14%
of the maximum. Because tasks have different rubric dimensions, this combined
figure is a compact summary rather than a substitute for task-level results.

| Task | Completed judge verdicts | Mean score (0-4) |
|---|---:|---:|
| Conversation summary | 28 | 3.957 |
| Last activity | 30 | 3.817 |
| Title assessment | 30 | 3.900 |
| Work-mode classification | 30 | 3.692 |

The identical cache-only replay exited successfully, retained all 119 judge
attempt files, verified the privately retained aggregate tree identity
unchanged, and made zero additional provider calls.

## Online-Evaluation Status Of All Three Arms

| Arm | Online judge status | Reason |
|---|---|---|
| R8 original | complete under waiver | 89 verdicts; not strict manager-valid |
| R8 repeat | complete under waiver | 89 verdicts; not strict manager-valid |
| R262K | complete | 118 successful verdicts, one terminal judge failure |

The waiver does not cure either candidate archive. Both R8 packages still fail
the exact verifier and must not be presented as ordinary manager-valid runs.

## Cost And Retention

Recorded RunPod spend was approximately US$6.28. The Pod is stopped and
retained, not deleted, at US$0.014/hour storage-only.

Successful judge verdicts recorded 1,526,131 input tokens and 85,888 output
tokens across all three arms. At Google's published Standard Gemini 3.1 Pro
Preview rates for requests below 200K input tokens (US$2/million input and
US$12/million output), these successes estimate to US$4.083. Conservatively
allowing the maximum configured output and a full 200K input for the one failed
judge request keeps estimated Vertex usage below US$4.50. Combined RunPod and
estimated Vertex spend remains below US$10.80, leaving more than US$11.20 of
the hard US$22 ceiling. The Cloud billing account remains authoritative:

- <https://cloud.google.com/vertex-ai/generative-ai/pricing>

## Publication Guidance

Safe claims for the LinkedIn article:

- RunPod changed this inference-heavy 120-case workflow from hours to minutes.
- The two remote 8K runs were highly repeatable in reliability and successful
  structured outputs, and their independently judged aggregate scores differed
  by only 0.055 percentage points.
- Context capacity, not just GPU speed, was decisive: maximum context recovered
  30 otherwise-failed cases at modest additional time and memory.
- The 4B Qwen model produced strong rubric scores on the verifier-valid maximum-
  context arm, while classification agreement shows useful remaining quality
  limitations.
- Evidence engineering matters: a single missing raw-invalid artifact blocked
  otherwise usable R8 packages from strict validation and required a visibly
  labelled evaluator waiver for semantic judging.

Claims to avoid:

- do not publish the host-visible 256-CPU/504-GiB totals as the Pod allocation;
- do not claim all three arms passed strict manager verification;
- do not imply maximum context makes Qwen semantically equivalent to Gemini;
- do not present the R262K speed ratio as a like-for-like local 8K comparison;
- do not publish private prompts, references, rationales, identifiers, or cloud
  account details.
