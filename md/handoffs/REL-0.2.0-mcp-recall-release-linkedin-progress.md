# REL-0.2.0 - MCP Recall Release And LinkedIn Progress Post

## Status

Ready for execution after the development manager commits this handoff and the
tracked checkout is clean.

## Roles And Publication Ownership

This work package prepares a release candidate. It does **not** publish it.

- **Executor:** prepares the version bump, release notes, public examples,
  README adjustments, LinkedIn post, validation evidence, and completion report.
  Leave all changes unstaged and uncommitted.
- **Development manager:** reviews the complete diff and completion report,
  requests rework when necessary, accepts the release candidate, and creates the
  release commit only after the owner explicitly asks for that commit.
- **Project owner:** explicitly approves the final public text, push, tag,
  GitHub release, and LinkedIn publication.
- **Development manager after owner approval:** may push the accepted commit,
  wait for CI, create and push the `v0.2.0` tag, and create the GitHub release.
- **Project owner:** publishes the LinkedIn post, normally after the public
  GitHub release URL exists.

The executor must not:

- stage or commit files;
- create or push a Git tag;
- push a branch;
- create a GitHub release;
- publish or schedule a LinkedIn post;
- change repository visibility or release permissions;
- ask the owner to commit an intermediate fix.

Publication gates are deliberately outside executor acceptance. If all
preparation requirements pass, report `ready for PM validation`, not `partial`
because the commit, tag, GitHub release, or LinkedIn publication has not yet
happened.

## Recommended Version

Prepare **Chat Chronicle v0.2.0**.

This is a semantic-version **minor** release because read-only MCP recall is a
new backward-compatible public capability. It is not a v0.1.x patch.

Version identity must be synchronized in:

- `pyproject.toml`;
- `src/chat_chronicle/__init__.py`;
- user-facing release/status documentation that refers to the current prepared
  version.

Before publication, wording must say `v0.2.0 release candidate`, `prepared`, or
`upcoming`. Do not call v0.2.0 published until the tag and GitHub release have
actually been created and verified.

## Objective

Prepare a release-quality v0.2.0 source release whose headline is:

> Chat Chronicle can now act as a local, read-only MCP recall server for tested
> Codex and Claude clients.

The release must:

1. explain the new MCP capability accurately;
2. provide several clearly fictional examples of supported recall;
3. explain the privacy/quality tradeoff when a cloud-backed chat client receives
   selected Chronicle tool output;
4. state the planned direction for optional local-model AI functionality;
5. summarize all accepted changes actually present on `main` since v0.1.0,
   rather than pretending MCP was the only intervening work;
6. provide a concise LinkedIn progress post;
7. produce reusable GitHub release notes;
8. pass release-quality validation without tracking private artifacts.

## Starting Point

Read before editing:

- `md/agent-operating-notes.md`;
- `md/master-plan.md`;
- `md/development-ledger.md`;
- `md/release-1-planning-note.md`;
- `README.md`;
- `docs/mcp-client-setup.md`;
- `docs/ai-tasks.md`;
- `docs/development-evaluation.md`;
- `md/handoffs/WP-4.1A-fastmcp-core-server.md`;
- `md/handoffs/reports/WP-4.1A-completion-report.md`;
- `md/handoffs/reports/WP-4.1A-validation-review.md`;
- `md/handoffs/WP-4.1B-local-client-integration-e2e.md`;
- `md/handoffs/reports/WP-4.1B-completion-report.md`;
- `md/handoffs/reports/WP-4.1B-validation-review.md`;
- the accepted LP-4.1 publication artifacts, only to avoid repeating the
  previous local-model article.

The accepted WP-4.1 implementation provides:

- `chronicle serve`;
- FastMCP stdio transport;
- exactly three tools:
  - `search_chats`;
  - `get_conversation`;
  - `list_recent_topics`;
- read-only SQLite access;
- bounded search/detail/recent results;
- tested integration with Codex in VS Code, Windows Codex/OWL, Claude Code, and
  Claude Desktop;
- a portable Claude Code project `.mcp.json`;
- detailed setup at `docs/mcp-client-setup.md`.

The classic ChatGPT Windows app, ChatGPT web, `claude.ai`, mobile clients, and
remote sessions are not local stdio MCP targets.

## Phase 0 - Preflight And Release-Diff Inventory

Verify:

```powershell
poetry env info --path
git status --short
git rev-parse HEAD
git tag --list
git log --oneline --decorate v0.1.0..HEAD
git diff --stat v0.1.0..HEAD
```

Requirements:

- Poetry resolves to this repository's `.venv`;
- the starting tracked checkout is clean;
- local tag `v0.1.0` exists;
- no `v0.2.0` tag exists;
- `pyproject.toml` and `src/chat_chronicle/__init__.py` both report `0.1.0`
  before the version bump;
- inventory every accepted public change since v0.1.0.

Classify the post-v0.1.0 diff into:

1. MCP server and client integration;
2. configurable AI-task/runtime improvements;
3. evaluation/benchmark tooling;
4. documentation and operational improvements;
5. tests, CI, and portability fixes;
6. private/local artifacts that must remain excluded.

Do not copy private benchmark inputs, model answers, database content,
conversation IDs, transcripts, user paths, or provider credentials into public
release material.

## Release Scope And Narrative

### Primary release headline

MCP recall is the v0.2.0 headline.

Explain it in plain language:

- Chronicle remains a local archive;
- a supported local AI client launches Chronicle as a child process;
- the client can search, list recent topics, and retrieve one bounded
  conversation;
- the MCP server itself is read-only;
- the client/model writes the final natural-language answer;
- Chronicle cites local conversation IDs as supporting evidence.

### Secondary accepted progress

Briefly summarize other accepted capabilities added since v0.1.0 when they are
present in the actual Git diff:

- YAML-defined optional AI tasks through LiteLLM;
- strict structured outputs and cache/provenance behavior;
- local LM Studio compatibility;
- split candidate/evaluation tooling and development evidence;
- Windows/CI portability and documentation improvements.

Keep this secondary. Do not turn this release post into another model-comparison
article.

### Honest limitations

State explicitly:

- MCP does not ingest or refresh history;
- users still run `chronicle collect`;
- MCP cannot capture the current chat or infer its Chronicle ID;
- there are no write, migration, enrichment, or arbitrary-SQL MCP tools;
- local stdio MCP is not available in every web/mobile/classic client;
- setup currently assumes a source checkout and Poetry virtual environment;
- PyPI/pipx packaging, remote MCP hosting, and the WorkTrail rename remain
  outside this release;
- title and topic quality depends on imported source metadata or previously
  stored valid summaries;
- embeddings/hybrid search are planned, not shipped.

## Required Fictional Examples

Release notes, README where appropriate, and the LinkedIn post must include
several **made-up** examples. Mark them as fictional or illustrative.

Use examples in this style:

```text
Using my Chronicle archive, what did I work on during the fictional Project
Lighthouse migration last week? Include dates and supporting conversation IDs.
```

```text
Search Chronicle for the conversation where I fixed a Windows terminal-wrapping
test. Return likely matches first; do not retrieve full transcripts yet.
```

```text
Retrieve fictional conversation 123 with at most 2,000 characters and summarize
the decision, blocker, and next action.
```

```text
Compare the decisions recorded in fictional conversations 123 and 456. Cite
both IDs and distinguish recorded facts from your interpretation.
```

```text
List my five most recently active Chronicle topics with dates and IDs, using
metadata only.
```

The final examples may be edited for clarity, but they must:

- use fictional topics and IDs;
- demonstrate recent topics, search, bounded detail, and multi-result synthesis;
- ask for Chronicle IDs;
- avoid real owner phrases, projects, names, paths, UUIDs, URLs, or dates;
- avoid implying that Chronicle performs unsupported semantic search,
  autonomous capture, current-chat identification, or database writes.

## Required Privacy And Remote-Use Explanation

The public wording must distinguish **local storage** from **model-provider
processing**.

Required meaning:

1. The Chronicle database and MCP server stay local.
2. Search results or bounded conversation text selected by the MCP call become
   part of the AI client's model request.
3. In cloud-backed Codex or Claude clients, that selected output is therefore
   processed by OpenAI or Anthropic under the user's account and provider
   settings.
4. Allowing the client to retrieve more relevant conversations or larger
   bounded extracts can produce a stronger, better-grounded answer because the
   model receives more evidence.
5. This is an explicit privacy-versus-context tradeoff, not an automatic bulk
   export of the archive.
6. Users should search metadata first, retrieve only selected IDs, set
   `max_chars`, and avoid secrets or third-party confidential data.

Use careful language such as:

> The archive stays local, but selected MCP results are sent to the model
> provider used by your client. If you deliberately allow more relevant
> evidence to be retrieved, the model can usually produce a richer and more
> grounded answer. That is a user-controlled context/privacy tradeoff, not a
> background upload of the database.

Do not claim:

- that cloud use is required;
- that all data remains local after a cloud client calls a tool;
- that the entire archive is exported;
- that remote models are always more accurate;
- that provider retention or training policies are known without verified
  account-specific evidence.

## Required Local-AI Direction

Explain the next local-first AI direction without presenting backlog as shipped.

The accepted direction is:

- optional and asynchronous;
- cacheable;
- does not slow normal SQLite/FTS search;
- configurable through external YAML task/model definitions;
- uses local models by default where practical;
- may use stronger remote models during development/evaluation only under
  explicit controls.

Mention the four conversation-intelligence tasks:

1. concise conversation summary with deterministic start and last-active dates;
2. work-mode classification (`manager`, `executor`, `one_off`, `mixed`, or
   `unknown`);
3. summary of the most recent activity, blockers, and next action;
4. title assessment and suggested replacement without automatic renaming.

The infrastructure and initial task contracts already exist as optional advanced
functionality. Future work focuses on improving local-model reliability,
prompting, evaluation, and eventually richer local archive intelligence. Do not
claim that local AI enrichment is automatic, production-complete, or part of
normal MCP calls.

## Phase 1 - Version And Release Metadata

Update:

```text
pyproject.toml
src/chat_chronicle/__init__.py
```

Both must become:

```text
0.2.0
```

Update version assertions or release-focused tests only where necessary.

Do not change:

- package name;
- CLI command;
- repository name;
- database schema;
- runtime dependencies;
- optional-extra membership;
- tool contracts.

Do not rewrite `poetry.lock` unless Poetry proves a lock update is genuinely
required by the version metadata. Explain any lock change precisely.

## Phase 2 - GitHub Release Notes

Create:

```text
md/releases/v0.2.0.md
```

The file is the proposed GitHub release body and must contain:

1. title and one-paragraph summary;
2. MCP recall highlights;
3. tested client surfaces;
4. exactly three read-only tool names;
5. concise installation/setup pointer;
6. fictional usage examples;
7. privacy and cloud-provider processing explanation;
8. other accepted changes since v0.1.0;
9. upgrade instructions from v0.1.0;
10. known limitations;
11. next local-AI direction;
12. links to README, MCP manual, AI-task guide, and development ledger;
13. source-release installation statement;
14. validation summary, with final numbers inserted only after validation.

Do not include a GitHub release URL before one exists. A placeholder may appear
only in private executor notes, not in the final tracked release body.

## Phase 3 - README Release Adjustment

Keep the README task-oriented and concise.

Required changes:

- update the project-status line to describe v0.2.0 as a release candidate;
- ensure MCP is visible near the top without displacing the CLI five-minute
  quick start;
- include or link to a few fictional prompts rather than duplicating the whole
  MCP manual;
- preserve the model-provider privacy warning;
- link to `md/releases/v0.2.0.md`;
- keep `docs/mcp-client-setup.md` as the detailed setup authority;
- keep advanced AI/evaluation material linked rather than expanding it in the
  quick start.

Do not restructure unrelated source/export documentation.

## Phase 4 - LinkedIn Progress Post

Create:

```text
md/release-artifacts/linkedin/chat-chronicle-v0.2.0-mcp-post.md
```

Write a LinkedIn-ready post of approximately 250-450 words.

Required structure:

1. **Progress hook:** this is the next visible step after the first source
   release, not a claim that the project is finished.
2. **Problem:** useful decisions are scattered across separate AI-chat silos.
3. **What changed:** Chat Chronicle now exposes read-only recall through MCP.
4. **Concrete examples:** include at least three short fictional prompts.
5. **Trust boundary:** local archive/read-only server, but selected results go
   to the cloud model when a cloud-backed client is used.
6. **Quality observation:** deliberately providing more relevant bounded
   evidence can produce stronger, better-grounded answers.
7. **Next direction:** optional local-model summaries, work-mode
   classification, recent-activity understanding, and title assessment;
   asynchronous, cached, and separate from normal search.
8. **Call to action:** invite technical feedback or testing from users of Codex
   and Claude.
9. **Links:** include placeholders for the final v0.2.0 GitHub release and
   repository URL. The repository URL may be concrete; the release placeholder
   must be clearly marked for owner replacement after publication.

Tone:

- technical and personal;
- progress-oriented;
- no marketing superlatives;
- no claim of scientific completeness;
- no unsupported privacy guarantee;
- no real private archive examples;
- no repetition of the previously published local-model comparison article.

Provide a short optional first comment containing the release/repository link
and setup guide, but do not publish it.

## Phase 5 - Documentation And Release Consistency

Check and reconcile:

- `README.md`;
- `docs/mcp-client-setup.md`;
- `docs/ai-tasks.md`;
- `docs/development-evaluation.md`;
- `.mcp.json`;
- `md/releases/v0.2.0.md`;
- the LinkedIn draft.

Requirements:

- direct Windows launch uses:

  ```text
  <repo>\.venv\Scripts\python.exe -m chat_chronicle.cli serve
  ```

- Claude Desktop legacy config omits `"type": "stdio"`;
- `.mcp.json` uses relative project paths and the ignored active database;
- exactly three MCP tools are named;
- supported/unsupported clients are described consistently;
- active versus frozen database guidance is consistent;
- no page says MCP is only planned;
- no page says v0.2.0 is already public;
- no page claims embeddings, remote MCP, PyPI, automatic enrichment, or current
  chat capture.

Do not edit the master plan or development ledger. Those are manager-owned and
will be updated after release acceptance/publication.

## Phase 6 - Release Validation

Run:

```powershell
poetry env info --path
poetry check
poetry run pytest tests/test_mcp_server.py -q
poetry run pytest
poetry run ruff check .
poetry run pre-commit run --all-files
poetry run chronicle --version
poetry run chronicle --help
poetry run chronicle serve --help
poetry build
git diff --check
git diff --cached --name-only
git status --short
```

Require:

- repository-local `.venv`;
- focused and full tests pass;
- Ruff and pre-commit pass;
- `chronicle --version` prints `0.2.0`;
- help still lists the accepted commands;
- `serve --help` describes exactly three read-only recall tools;
- wheel and sdist names contain `0.2.0`;
- package metadata reports `0.2.0`;
- an installed-wheel smoke can run `chronicle --version`, base CLI help, and
  `serve --help`;
- `git diff --check` passes;
- nothing is staged or committed.

Package artifacts under `dist/` may be generated locally for validation but
must remain ignored/untracked unless the existing release policy explicitly
tracks them. Do not attach or publish them.

## Phase 7 - Privacy And Public-Artifact Review

Inspect every changed tracked file.

Require no:

- real conversation ID;
- private title, phrase, snippet, summary, or transcript;
- owner username or home path;
- database/export/session path;
- account, organization, project, or workspace identifier;
- token, key, credential, or complete environment dump;
- raw benchmark candidate/reference/judge output;
- private database hash or manifest;
- unpublished provider response.

Verify:

```powershell
git ls-files ".chronicle/*" "exports/*" "*.db" "*.sqlite" "*.zip" "*.jsonl"
git status --short --ignored
```

Use a targeted local sensitive-value scan without writing those private values
into a tracked script or report.

## Defect Handling And Streamlined Execution

If validation exposes a narrow generic release defect, the executor may fix it,
add a regression when appropriate, rerun the affected checks, and continue.
Leave the fix uncommitted with the release candidate.

Do **not** stop for an intermediate manager commit merely because:

- version metadata changed;
- documentation needed correction;
- a release-focused test needed updating;
- a narrow packaging defect was fixed.

Stop and request manager direction only if resolution would:

- change database schema or stored data;
- change MCP tool fields, bounds, names, or read-only behavior;
- add a runtime dependency or transport;
- expose a private artifact;
- change supported-provider claims materially;
- require rewriting accepted historical evidence;
- require remote publication or permission changes.

No private model call, remote archive disclosure, or external AI generation is
needed for this package.

## Acceptance Criteria

REL-0.2.0 preparation is complete when:

- version metadata is consistently `0.2.0`;
- the actual diff since v0.1.0 has been inventoried;
- MCP is the release headline without hiding other accepted shipped changes;
- GitHub release notes exist at the required path;
- the README accurately presents the release candidate;
- at least three clearly fictional MCP examples are public-ready;
- privacy versus richer remote-model context is explained accurately;
- the local-model AI direction and four tasks are described without
  overclaiming;
- limitations and unsupported clients are explicit;
- the LinkedIn post is polished and publication-ready except for the final
  release URL;
- full validation, build, installed-wheel, privacy, and Git checks pass;
- the completion report exists;
- nothing is staged, committed, tagged, pushed, released, or posted.

## Completion Report

Write exactly:

```text
md/handoffs/reports/REL-0.2.0-completion-report.md
```

Required sections:

1. **Status** - `ready for PM validation` or `blocked`;
2. **Executive Summary**;
3. **Starting Commit And Clean-Checkout Evidence**;
4. **v0.1.0-to-HEAD Change Inventory**;
5. **Version Decision And Modified Version Files**;
6. **MCP Release Claims And Evidence Sources**;
7. **Fictional Examples Added**;
8. **Privacy And Remote-Processing Wording**;
9. **Local-AI Direction Wording**;
10. **GitHub Release Notes Summary**;
11. **README Changes**;
12. **LinkedIn Post Summary**;
13. **Known Limitations**;
14. **Focused And Full Test Results**;
15. **Ruff, Pre-commit, Poetry, CLI, And Build Results**;
16. **Installed-Wheel Smoke Evidence**;
17. **Privacy And Tracking Review**;
18. **Acceptance-Criteria Matrix**;
19. **Files Changed**;
20. **Manager Publication Checklist**;
21. **Final `git status --short`**.

Do not include private paths, values, or content in the report.

## Expected Changed Files

Expected:

- `pyproject.toml`;
- `src/chat_chronicle/__init__.py`;
- `README.md`;
- `md/releases/v0.2.0.md`;
- `md/release-artifacts/linkedin/chat-chronicle-v0.2.0-mcp-post.md`;
- `md/handoffs/reports/REL-0.2.0-completion-report.md`;
- narrowly necessary version/release tests, if any.

Do not edit:

- `md/master-plan.md`;
- `md/development-ledger.md`;
- private `.chronicle/` data;
- accepted historical reports;
- raw manager/executor chat artifacts;
- Git tags or GitHub release state.

## Manager Publication Checklist After Acceptance

This section is for the completion report; the executor does not execute it.

Recommended order:

1. Manager validates the complete release-candidate diff and report.
2. Owner reviews and explicitly approves every public release and LinkedIn
   artifact.
3. Manager commits the accepted v0.2.0 release candidate.
4. Owner explicitly authorizes push; manager or owner pushes `main`.
5. Wait for GitHub CI on the exact release commit to pass.
6. Owner explicitly authorizes tagging.
7. Manager creates annotated tag `v0.2.0` on the CI-green release commit and
   pushes only that tag.
8. Owner explicitly authorizes GitHub publication.
9. Manager creates the GitHub release from `md/releases/v0.2.0.md` and verifies
   the public repository, tag, and release URLs.
10. Replace the LinkedIn release placeholder with the verified public URL.
11. Owner explicitly approves and publishes the LinkedIn post.
12. Manager records the published commit, tag, release URL, publication status,
    and final branch cleanliness in the plan and ledger.

## Final Executor Instruction

Prepare one coherent release candidate end to end. Do not publish it and do not
stop at every internal correction. Return `ready for PM validation` only when
the public artifacts, package metadata, build, tests, privacy review, and
completion report are all complete and everything remains uncommitted.
