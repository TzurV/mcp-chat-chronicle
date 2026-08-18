# WP-5.2B3B.1D.4.2 Article Evidence Brief

Date: 2026-08-18

## Publication-safe headline

A four-position hosted GEPA search produced one minibatch-improving candidate.
It passed six of seven frozen eligibility conditions, but the decisive 8K
complete-request context gate rejected it and retained the baseline.

## Strong evidence available

- The fresh experiment completed P0 plus exactly four auditable proposal
  positions. All four generated instructions survived privately with intent,
  response, proposal, privacy, decision, and terminal linkage.
- Proposal score sums were 0.6 -> 0.6, 0.5 -> 0.4, 0.5 -> 0.7, and 0.6 ->
  0.4. Strict GEPA decisions were reject, reject, accept, reject.
- The accepted proposal changed only conversation-summary. It was distinct,
  provenance-linked, and privacy-clean, then completed all 40 terminal
  positions through Gemini 2.5 Flash-Lite.
- P0 and the candidate each produced 16/40 valid outputs. This unchanged total,
  the unchanged per-model count, and every per-task count pass the actual
  frozen validity comparisons; improvement and universal validity are not
  eligibility requirements.
- Validation FABLE agreement declined from 0.128125 to 0.112500, while
  conversation-summary and last-activity remained 0/4 valid. The decline is
  relevant to shortlist ranking, but it is not an `_eligible` conjunct.
- Complete-request evidence was decisive: P0 required up to 15,256 tokens and
  the candidate up to 15,381 against the frozen 8,192-token limit. Neither is
  promotion-eligible.
- Across the candidate's seven no-call envelopes, request excess was
  241–7,189 tokens. Packaged task-prompt estimates contributed 171–254 tokens
  per case; removing the entire system prompt could theoretically rescue only
  one case. The other six would remain 6,770–6,839 tokens over 8K.
- GEPA scoring used 45 logical positions but 72 actual candidate transports:
  45 primary Chat calls and 27 explicit JSON fallbacks. Logical evaluations
  and paid transports are not interchangeable units.
- The fresh root used 142 observed/charged calls with zero retries. Cumulative
  charged calls are 647/950. Partial known fresh provider cost is US$0.1454048;
  adapter-transport cost is unavailable.
- Provider-free packaging, verification, shortlist export, and inspection
  replay left all 418 run files byte-identical. All eight historical roots also
  remained byte-identical.

## Evidence not available

- No candidate passed every deterministic qualification gate, so no finalist
  or fixed-judge comparison exists.
- GEPA adapter records do not carry proposal ordinal; per-proposal transport,
  latency, token, and cost attribution is unavailable.
- Portable provider cost is unavailable for the 72 adapter transports, so
  measured provider cost is partial.
- Proposer responses do not expose provider retry counts, although each intent
  has one recorded transport and no retry was observed or charged.
- There is no holdout, RunPod, LM Studio, local-transfer, alternate-model, or
  generalization evidence.

## Defensible article angles

1. **Search acceptance is not deployment promotion.** Position 3 improved its
   three-example minibatch from 0.5 to 0.7 and passed all validity-comparison
   eligibility conditions, yet failed the frozen context gate after complete
   evaluation.
2. **Persist before interpretation.** Rejected and accepted proposal bytes must
   survive independently of the optimizer's final candidate store to support
   an honest negative result.
3. **Count transports, not just logical positions.** JSON fallback expanded 45
   GEPA score positions into 72 paid candidate transports.
4. **Keep full denominators.** Seven deterministic context no-calls and 17
   schema failures remained in every 40-position result rather than being
   truncated, repaired, or excluded.
5. **A larger instruction can worsen the binding constraint.** The accepted
   conversation-summary instruction grew from 569 to 1,013 bytes and increased
   the maximum request from 15,256 to 15,381 tokens.
6. **Budget accounting needs parallel vocabularies.** Observed calls, charged
   calls, partial provider cost, compute accounting, proposer cost, and
   pre-call reservation answer different questions and should not be collapsed
   into one invoice-like number.

## Owner-reported billing snapshot

- Total amount due: £0.18.
- Due date: 2026-08-30.
- Currency: GBP.

This is an owner-reported account billing snapshot. Its exact scope, billing
lag, taxes, and attribution to D.4.2 are not independently proven. It is not
currency-converted or reconciled directly to measured/reserved US-dollar
figures.

## Required caveats

This is one private ten-conversation silver development set with FABLE-derived
references, not human-adjudicated ground truth or untouched evaluation. Four
proposal positions produced only one fully evaluated candidate. The result
supports a no-finalist conclusion under this frozen contract, not a general
claim that GEPA is ineffective, Gemini is better or worse than another model,
P0 is deployable, or performance transfers to holdout data. Costs are partial
where adapter transport billing is unavailable. Private prompts, inputs,
references, outputs, identifiers, paths, hashes, project values, and
credentials remain unpublished.
