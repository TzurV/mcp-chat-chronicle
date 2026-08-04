# WP-5.2B3B Prompt-Catalog Patch Validation Review

## Decision

**Accepted for manager commit.**

The generic patch resolves the accepted-input catalog blocker without changing P0 authority data,
P1/P2 prompt bytes, non-prompt task settings, private selection artifacts, or historical benchmark
behavior. Private candidate generation remains paused until this complete checkpoint is committed
on `codex/wp-5.2b3b-prompt-development` and the executor resumes from the resulting clean HEAD.

## Requirements Review

The manager confirmed that the implementation:

- keeps the exact P0 catalog hash as authority for accepted inputs and FABLE references;
- introduces a separately pinned active prompt-catalog hash;
- permits changes only to `system_prompt` and `user_prompt`;
- structurally rejects changes to catalog version, task order, task version, enabled state,
  description, model profile, selector, schema, generation settings, dependencies, input limits,
  and recent-message count;
- retains strict application parsing and prompt-placeholder validation for both catalogs;
- binds authority, active, policy, non-prompt contract, and per-task prompt identities through
  bundle preparation, generation work, candidate packaging, verification, deterministic scoring,
  judge cache identity, and judge accounting;
- keeps portable artifacts free of catalog filesystem paths;
- omits all new fields when the optional declaration is absent, preserving historical
  serialization and verification behavior;
- continues to open only selected input/reference files for ordered non-prefix scopes.

## Independent Validation

Manager-run evidence on the repository Poetry environment:

```text
poetry env info --path
C:\work\Github\mcp-chat-chronicle\.venv

poetry run pytest tests/test_bench.py -q
passed (complete benchmark module; one expected skip)

poetry run pytest
474 passed, 1 skipped

poetry run ruff check .
All checks passed!

poetry check
All set!

poetry run python -m bench --help
passed

git diff --check
passed
```

The tracking scan found no tracked `.chronicle`, export, database, SQLite, or ZIP artifact.

## Scope And Integrity

No production AI-task behavior was changed. The patch is confined to the development benchmark
harness, its strict configuration models, tests, templates, and evaluation documentation.

The executor reports that the frozen 10/20 split, P0 reconstruction, P1/P2 catalogs and hashes,
prompt freeze, accepted historical packages, databases, and WP-5.2C1 artifacts remain unchanged.
No private candidate was generated and no Gemini, fixed-judge, or other external provider call was
made during the patch. The manager's source review and Git/privacy checks found no contradiction.

## Non-Blocking Note

Judge execution validates the package/config catalog identity before constructing or sending a
private prompt. A reused scoring directory with a different catalog identity is rejected when its
run manifest is finalized. B3B uses distinct scoring paths for each prompt package, so this does
not block the checkpoint. A future generic hardening change may move that reused-directory check
before the judge loop, but it is outside this narrow blocker fix and is not required for B3B.

## Resume Conditions

After the manager commit, the executor must:

1. start from the new clean HEAD on `codex/wp-5.2b3b-prompt-development`;
2. append, not replace, the private provenance amendment required by the blocker review;
3. revalidate unchanged split and P1/P2 hashes;
4. rerun the fictional Qwen P1 and P2 gates under the new commit and require 4/4 each;
5. then resume the handoff at private 40-case development generation;
6. leave the 20-conversation holdout unopened until WP-5.2B3C.

Commit ownership remains with the manager.

## Commit Record

The manager committed the accepted implementation as `0e920c8` with subject
`feat: support prompt catalog experiments`. No private candidate or provider call occurred before
that commit.
