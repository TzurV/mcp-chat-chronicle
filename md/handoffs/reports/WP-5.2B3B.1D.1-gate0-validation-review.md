# WP-5.2B3B.1D.1 Gate 0 Validation Review

**Status:** Offline implementation accepted; authority retrieval authorized

## Manager decision

The generic Gate 0 implementation is accepted for commit. It adds a single
hosted candidate model, Vertex ADC routing, exact Gemini 2.5 Flash-Lite thinking
disablement, direct and DSPy 8K guards, infrastructure-only retries, distinct
evaluation/GEPA limits, and a direct P0-to-GEPA lifecycle with Bootstrap
disabled.

Manager validation passed:

- focused new route/lifecycle regressions: 6 passed;
- complete AI adapter and optimizer matrix: 175 passed;
- Ruff: passed;
- Poetry validation: passed;
- `git diff --check`: passed.

## Authority retrieval authorization

The owner authorizes read-only access to the ignored prior B3B.1D authority
root solely to copy the following frozen authority artifacts into the new
ignored B3B.1D.1 authority root:

- development selection manifest;
- frozen six-conversation optimizer-train manifest;
- frozen four-conversation optimizer-validation manifest;
- the first selected train and first selected validation input files identified
  by those manifests;
- the eight corresponding FABLE reference files, one per selected conversation
  and accepted task;
- catalog/manifest hash metadata strictly required to verify that authority.

This authorization permits metadata reads needed to identify those exact files
and content reads needed to copy and hash them. It does not authorize reading or
copying prior candidate outputs, provider responses, generated prompts, trial
state, budgets, logs, caches, judge artifacts, credentials, or unrelated input
and reference files.

## Copy requirements

1. Treat the prior root as read-only; do not modify timestamps, permissions,
   files, indexes, pointers, or state.
2. Copy only the bounded authority allowlist into
   `.chronicle/wp-5.2b3b.1d.1/authority/`.
3. Keep source and destination ignored and untracked.
4. Record a private source-to-destination SHA-256 inventory and prove every
   copied file is byte-identical.
5. Prove the destination contains no extra authority payloads.
6. Configure D.1 to read only the copied destination, not the prior D root.
7. Run authority verification before ADC refresh or provider calls.
8. Stop if the exact bounded authority cannot be proven without opening files
   outside this allowlist.

After the manager commits this gate, the executor may continue under the model,
private-disclosure, 80-call, and US$35 authorization already contained in the
D.1 handoff. Reconfirmation is not required while all boundaries remain
unchanged.
