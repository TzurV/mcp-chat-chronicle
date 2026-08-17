# WP-5.2B3B.1D.4 GEPA Search Article Evidence Brief

Date: 2026-08-17

## Publication decision

Not suitable as a GEPA-search or prompt-quality article result. The experiment
stopped during the first P0 train evaluation, before a baseline result or any
proposal existed. It provides systems evidence about authority handling,
budget reservation, privacy boundaries, and a missing candidate-transport
diagnostic, but no evidence that GEPA improved, matched, or failed to improve
P0.

## Publishable measured facts

- The frozen development authority was copied by exact allowlist: 10 inputs,
  40 FABLE references, a 6/4 split, byte identity for all 54 payloads, zero
  destination extras, and zero holdout.
- The supported optimizer preflight verified the single 8K Gemini 2.5
  Flash-Lite candidate, Gemini 3.5 Flash proposer, pinned DSPy/GEPA versions,
  graded score contract, and fallback-aware four-proposal budget.
- Same-process ADC refresh and private route configuration passed without
  disclosing credential, project, account, or token values.
- The run stopped with a persisted `ValueError` during the first P0 train
  evaluation. No P0 result, proposal, candidate comparison, or finalist exists.
- D.4 actual candidate transports are bounded at zero to 48, including zero to
  24 retries, because the ordinary evaluation path did not persist per-position
  transport events. No proposer call occurred.
- Conservative accounting retained 48 charged candidate attempts and
  US$0.1801232, producing cumulative totals of 157 charged calls and
  US$6.2616008 against the authorized 540-call and US$35 ceilings.
- Judge, holdout, RunPod, local-model, fallback-model, semantic-retry, and
  output-repair activity were all zero.

## Required caveats

The FABLE references are private silver development data, not ground truth.
The stopped operation yielded no score denominator, no proposal acceptance
decision, and no paired baseline/finalist comparison. The missing precise
failure subcategory and transport event must not be reconstructed from elapsed
time or the generic exception class.

## Engineering lesson

Pre-decision GEPA proposal evidence is now strong, but ordinary candidate
evaluation still lacks an equivalent pre-transport/terminal transport record.
Future work should persist a privacy-safe event before each explicit candidate
transport and a terminal category afterward, including configured/actual route
identity, usage availability, retry ordinal, latency availability, and the
application validation stage. That work should be provider-free and
regression-tested before another private run is authorized.

## Article status

Use only as a short failure-observability case study after manager review. Do
not present it as a multi-proposal GEPA experiment, a Gemini model comparison,
or a P0-improvement result.
