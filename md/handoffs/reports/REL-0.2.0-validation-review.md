# REL-0.2.0 Validation Review

## Decision

**Accepted after rework on 2026-07-28.**

The version bump, README positioning, release-note coverage, fictional examples,
privacy explanation, local-AI direction, and revised LinkedIn narrative are
substantively sound. The initial review required removal of unrelated formatting
churn and several publication-specific corrections. The executor completed that
rework, and the manager independently validated the narrowed release candidate.

No production defect was found. Rework is limited to release hygiene and public
documentation.

The original findings and instructions remain below as the audit trail.

## Findings

### 1. Remove unrelated pre-commit formatting churn

The all-files pre-commit run reformatted accepted files that are outside the
release package:

- `bench/core.py`;
- `bench/judge.py`;
- `src/chat_chronicle/ai.py`;
- `src/chat_chronicle/cli.py`;
- `src/chat_chronicle/mcp_server.py`;
- `tests/test_ai_config_matrix.py`;
- `tests/test_bench.py`;
- `tests/test_mcp_server.py`;
- `md/handoffs/LP-4.1-local-model-results-analysis-and-article-planning.md`;
- `md/handoffs/WP-5.2A5.1-remaining-lm-studio-candidate-qualification.md`;
- `md/handoffs/WP-5.2B2.1-three-qualified-candidate-40-case-checkpoint.md`;
- `md/handoffs/reports/20260721-vertex-ai-llm-judge-connectivity.md`;
- `md/handoffs/reports/WP-5.2A5.1-validation-review.md`.

These changes add no release behavior and obscure the version/release diff.
Some Markdown changes also remove intentional hard line breaks, so they should
not be described merely as harmless release formatting.

Restore these files exactly to the starting `HEAD`. Do not restore or overwrite:

- manager-owned `md/master-plan.md`;
- manager-owned `md/development-ledger.md`;
- the REL-0.2.0 handoff;
- concurrent owner-authored untracked MCP/LinkedIn drafts;
- the actual release-candidate files.

For this rework, the manager waives another repository-wide formatter rewrite.
Run pre-commit only against the retained release-candidate files. The earlier
all-files pass remains recorded as diagnostic evidence; the final release diff
must remain narrowly scoped.

### 2. Make the GitHub release body publication-ready

`md/releases/v0.2.0.md` is intended to be copied into the GitHub release. Its
opening currently calls v0.2.0 a “source-release candidate.” Change the opening
to describe what v0.2.0 **adds**, without claiming that it is already published
and without retaining “candidate” in the final GitHub release body.

Example meaning:

> Chat Chronicle v0.2.0 adds local, read-only MCP recall for tested Codex and
> Claude clients.

The current relative documentation links are appropriate when reading the file
inside the repository but are not a sufficiently robust GitHub release-body
contract. Use absolute repository URLs pinned to tag `v0.2.0` for:

- README;
- MCP Recall User Manual;
- Optional AI Tasks;
- Development Ledger;
- the release completion report, if it remains linked.

Do not add a release-page URL before it exists.

### 3. Pin upgrade instructions to the release tag

The current upgrade block uses `git pull`, which can install whatever happens
to be at the tip of `main`, not necessarily v0.2.0.

Replace it with a tag-pinned source workflow, for example:

```powershell
git fetch --tags
git checkout v0.2.0
poetry install -E mcp
poetry run chronicle --version
```

State that this intentionally checks out the immutable release tag. Do not
recommend `main` as the reproducible release installation.

### 4. Tighten the local-model privacy statement

The release notes currently say that clients can be paired with local models
where their configuration supports it. That path was not part of WP-4.1B
client acceptance.

Use the narrower verified distinction:

- Chronicle's normal SQLite/FTS CLI workflow remains local and requires no
  model;
- MCP disclosure depends on the selected client and its configured model
  provider;
- the tested Codex and Claude client paths are cloud-backed;
- optional Chronicle AI tasks can use local models through the separately
  documented LM Studio/LiteLLM path.

Do not imply that the tested MCP clients were validated with local models.

### 5. Make the publication-time LinkedIn edits explicit

The LinkedIn draft is suitable as a pre-publication draft and may retain
“release candidate” for now. The manager publication checklist must explicitly
require both:

1. replace the candidate wording with published-release wording after the
   GitHub release exists;
2. replace the release URL placeholder with the verified public URL.

The post remains owner-controlled and must not be published during rework.

### 6. Refresh the completion report and final status accurately

Refresh `md/handoffs/reports/REL-0.2.0-completion-report.md` after rework:

- record this PM rework and the exact files restored;
- state that targeted pre-commit was used under the manager waiver;
- remove the broad-formatting files from the final changed-file set;
- record the corrected release-body links and tag-pinned upgrade instructions;
- record the narrowed local-model statement;
- add both LinkedIn publication-time substitutions;
- include every concurrent owner file present in final `git status --short`
  without claiming or modifying it.

The currently appearing owner drafts must remain untouched unless the owner
separately selects one for incorporation.

## Retained Accepted Content

Preserve:

- version `0.2.0` in `pyproject.toml` and
  `src/chat_chronicle/__init__.py`;
- the README's CLI-first structure and release-candidate status;
- clearly fictional examples;
- the local-storage versus cloud-provider processing explanation;
- the statement that more deliberately selected bounded evidence can improve
  grounding;
- the four local-AI task directions;
- the revised LinkedIn problem/progress narrative;
- the explicit owner/manager publication gates.

## Required Validation

After rework run:

```powershell
poetry env info --path
poetry check
poetry run pytest tests/test_mcp_server.py -q
poetry run pytest
poetry run ruff check .
poetry run pre-commit run --files `
  pyproject.toml `
  src/chat_chronicle/__init__.py `
  README.md `
  md/releases/v0.2.0.md `
  md/release-artifacts/linkedin/chat-chronicle-v0.2.0-mcp-post.md `
  md/handoffs/reports/REL-0.2.0-completion-report.md
poetry run chronicle --version
poetry run chronicle serve --help
git diff --check
git diff --cached --name-only
git status --short
```

Reuse the existing successful build and installed-wheel evidence unless a
version/package file changes beyond the already validated 0.2.0 bump. If it
does, rebuild and repeat the wheel smoke.

Repeat the targeted privacy scan over all retained public release files.

## Delivery Rule

Leave everything unstaged and uncommitted. Do not tag, push, create a GitHub
release, or publish LinkedIn content.

Return `ready for PM validation` after completing all six rework items. Do not
report `partial` merely because manager/owner publication gates remain.

## Final PM Acceptance

The rework closed every finding:

- all 13 unrelated Python, test, and historical Markdown formatting changes
  were restored exactly to the starting `HEAD`;
- the GitHub release body now describes what v0.2.0 adds without candidate
  wording;
- public documentation links in the release body are absolute and pinned to
  tag `v0.2.0`;
- upgrade instructions check out the immutable release tag instead of following
  `main`;
- the local-model statement now distinguishes model-free local CLI use,
  cloud-backed tested MCP clients, and separate local-model AI tasks;
- the LinkedIn draft requires both publication-time wording and URL
  replacements;
- the refreshed completion report accurately records the narrowed diff and
  concurrent owner files.

Independent manager validation passed:

```text
poetry env info --path
  -> repository-local .venv

poetry run pytest tests/test_mcp_server.py -q
  -> 14 passed

poetry run pytest -q
  -> full suite passed with one skip

poetry run ruff check .
  -> All checks passed

poetry check
  -> All set

targeted poetry run pre-commit run --files ...
  -> all hooks passed

poetry run chronicle --version
  -> chat-chronicle 0.2.0

poetry run chronicle serve --help
git diff --check
git diff --cached --name-only
  -> passed; nothing staged
```

The recurring Windows sandbox process-launch failure affected `poetry check`
and targeted pre-commit on their first attempts. Both passed unchanged when
rerun through the documented accepted execution path; this was not a project
failure.

**Final PM decision: the REL-0.2.0 release candidate is accepted.** It remains
uncommitted, untagged, unpushed, unreleased, and unpublished. Commit, push, CI,
tag, GitHub release, and LinkedIn publication remain separate owner-controlled
gates.
