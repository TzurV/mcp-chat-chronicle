# REL-0.2.0 Completion Report

## 1. Status

ready for PM validation

## 2. Executive Summary

Prepared the Chat Chronicle v0.2.0 source-release candidate with read-only MCP
recall as the headline. Version metadata, README release positioning, reusable
GitHub release notes, fictional examples, privacy/context wording, local-AI
direction, and a LinkedIn-ready progress post are complete. The candidate was
built and validated without staging, committing, tagging, pushing, publishing,
or posting.

### PM rework

The first PM review found no production defect and required a narrower release
diff plus publication-specific documentation corrections. The following files,
which the first repository-wide pre-commit pass had changed, were restored
exactly to the starting `HEAD`:

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

The PM waived another repository-wide formatting pass. Final pre-commit
validation was limited to the retained release-candidate files. Manager-owned
and concurrently authored owner files were preserved.

## 3. Starting Commit And Clean-Checkout Evidence

- Starting commit: `3b02d34b5d2cdb56d72ce24a2771629601cc7654`.
- Poetry resolved to the repository-local `.venv`.
- Local tag `v0.1.0` existed; no `v0.2.0` tag existed.
- Both version files reported `0.1.0` before editing.
- The checkout was not clean: manager-owned plan/ledger edits and two untracked
  documentation drafts already existed.
- The owner explicitly approved continuing despite that failed clean-checkout
  gate. Existing work was preserved. The executor did not edit the manager-owned
  plan or ledger intentionally.

## 4. v0.1.0-to-HEAD Change Inventory

The accepted public diff since `v0.1.0` was classified as follows:

1. **MCP server and client integration:** FastMCP stdio server, exactly three
   read-only tools, CLI serving command, portable project configuration, client
   setup manual, synthetic protocol/read-only tests, and successful Codex and
   Claude client evidence.
2. **Configurable AI-task/runtime improvements:** external YAML task/model
   definitions, strict structured outputs, cache/provenance behavior, hosted
   execution controls, reasoning settings, and local LM Studio compatibility.
3. **Evaluation/benchmark tooling:** separated preparation, candidate
   generation, package verification, deterministic scoring, optional judging,
   retry/cache behavior, and privacy-safe aggregate reports.
4. **Documentation and operations:** expanded task, evaluation, MCP, planning,
   evidence, troubleshooting, and Windows usage guidance.
5. **Tests, CI, and portability:** substantially expanded synthetic coverage,
   MCP CI dependencies on Windows/Ubuntu, and Windows atomic-write, wrapping,
   and launcher guidance.
6. **Excluded private/local artifacts:** databases, exports, local sessions,
   evaluation inputs/packages/results, credentials, local client settings,
   hashes, private IDs, and transcripts remain excluded.

MCP is presented as the release headline without implying it is the only
accepted progress since v0.1.0.

## 5. Version Decision And Modified Version Files

The backward-compatible addition of public MCP recall is a semantic-version
minor release. The prepared version is `0.2.0` in:

- `pyproject.toml`;
- `src/chat_chronicle/__init__.py`.

No package, repository, CLI, schema, dependency, extra, or tool-contract name
changed. `poetry.lock` did not require an update.

## 6. MCP Release Claims And Evidence Sources

Claims are grounded in the accepted WP-4.1A and WP-4.1B handoffs, completion
reports, validation reviews, implementation tests, README, MCP manual, and
portable `.mcp.json`.

Public text states that Chronicle is a local archive launched as a stdio child
process and exposes exactly `search_chats`, `get_conversation`, and
`list_recent_topics`. It states that the server is read-only, the calling model
writes the answer, Chronicle IDs support the answer, and archived text is
untrusted input.

Tested clients are described consistently: Codex in VS Code, Windows Codex/OWL,
Claude Code, and Claude Desktop. Unsupported local-stdio claims are avoided for
classic ChatGPT Windows, ChatGPT web, `claude.ai`, mobile, and remote sessions.

## 7. Fictional Examples Added

README contains three concise illustrative prompts. The release notes contain
five prompts covering:

- recent-topic metadata;
- search-first recall;
- bounded detail;
- comparison across two fictional IDs;
- multi-result synthesis with cited Chronicle IDs.

The LinkedIn post contains four short fictional prompts. All are explicitly
marked fictional or illustrative and use invented projects/IDs only.

## 8. Privacy And Remote-Processing Wording

README, release notes, and LinkedIn draft distinguish local storage from model
processing:

- the database and MCP server remain local;
- selected MCP results enter the client model request;
- cloud-backed clients therefore send that selected output to their configured
  provider under user/account settings;
- more relevant bounded evidence can improve grounding;
- this is a deliberate context/privacy tradeoff, not automatic archive export;
- users should search metadata first, select IDs, limit `max_chars`, and avoid
  secrets or third-party confidential material.

No provider retention or training behavior is asserted.

## 9. Local-AI Direction Wording

Release materials describe optional, asynchronous, cacheable, externally
configured, local-model-first conversation intelligence that remains separate
from normal SQLite/FTS search. They identify the four intended tasks:

1. dated concise summary;
2. `manager`/`executor`/`one_off`/`mixed`/`unknown` work mode;
3. recent activity, blockers, and next action;
4. suggestion-only title assessment.

Existing infrastructure/contracts are distinguished from future reliability,
prompting, and evaluation work. Automatic or production-complete enrichment is
not claimed.

## 10. GitHub Release Notes Summary

`md/releases/v0.2.0.md` is a reusable proposed GitHub release body containing
the required summary, MCP highlights, clients, exact tools, setup pointer,
examples, privacy boundary, other accepted changes, upgrade steps, limitations,
local-AI direction, documentation links, source-install statement, and final
validation summary. Its opening describes what v0.2.0 adds without retaining
release-candidate wording. Documentation and completion-report links are
absolute repository URLs pinned to tag `v0.2.0`; no nonexistent release-page
URL appears. Upgrade instructions fetch and check out immutable tag `v0.2.0`
rather than following `main`.

The privacy wording now states the verified boundary precisely: normal
SQLite/FTS CLI use is local and model-free; disclosure from MCP depends on the
client/provider; the tested Codex and Claude paths are cloud-backed; and local
models apply to the separately documented optional Chronicle AI-task path. It
does not imply that MCP acceptance used local models.

## 11. README Changes

README remains CLI-first. MCP remains visible near the top and has:

- three fictional prompts;
- a strengthened provider-processing warning;
- a link to the detailed MCP manual;
- v0.2.0 release-candidate status and release-notes link;
- concise MCP/package/client limitations.

Unrelated source/export documentation was not restructured.

## 12. LinkedIn Post Summary

The approximately 400-word draft at
`md/release-artifacts/linkedin/chat-chronicle-v0.2.0-mcp-post.md` is
progress-oriented and technical. It covers the silo problem, MCP change,
fictional prompts, trust boundary, bounded-evidence quality observation,
local-AI direction, testing invitation, repository link, clearly marked release
placeholder, and an optional first comment. Its publication notes require both
replacement of release-candidate wording with published-release wording and
replacement of both URL placeholders with the verified GitHub release URL. It
was not published or scheduled.

## 13. Known Limitations

- MCP does not ingest or refresh history; `chronicle collect` remains separate.
- MCP cannot capture the current chat or infer its Chronicle ID.
- No MCP writes, migrations, enrichment, arbitrary SQL, or remote transport.
- Local stdio is unavailable in many web/mobile/classic/remote clients.
- Current installation assumes a source checkout and Poetry.
- Topic quality depends on imported metadata or valid stored summaries.
- PyPI/pipx, remote hosting, WorkTrail rename, embeddings/hybrid search, and
  automatic enrichment are outside this candidate.

## 14. Focused And Full Test Results

- `poetry run pytest tests/test_mcp_server.py -q`: 14 passed.
- `poetry run pytest`: 446 passed, 1 skipped in 100.33 seconds.

## 15. Ruff, Pre-commit, Poetry, CLI, And Build Results

- `poetry env info --path`: repository-local `.venv`.
- `poetry check`: passed.
- `poetry run ruff check .`: passed.
- Targeted `poetry run pre-commit run --files ...`: passed under the PM waiver
  against only the retained release-candidate files.
- `poetry run chronicle --version`: `chat-chronicle 0.2.0`.
- Base help passed and retained the accepted CLI commands.
- Serve help passed and describes exactly three read-only recall tools over
  stdio.
- `poetry build`: produced
  `chat_chronicle-0.2.0-py3-none-any.whl` and
  `chat_chronicle-0.2.0.tar.gz`.
- `git diff --check`: passed.
- `git diff --cached --name-only`: empty.

The earlier repository-wide pre-commit pass remains diagnostic history. Its
unrelated changes were restored during PM rework and are absent from the final
release diff.

## 16. Installed-Wheel Smoke Evidence

The built wheel was installed with `--no-deps` into a fresh temporary virtual
environment. That environment was then given read access to the repository
environment's already-installed dependencies while Chat Chronicle itself loaded
from the temporary wheel path.

The installed-wheel smoke passed:

- `chronicle --version`;
- base `chronicle --help`;
- `chronicle serve --help`;
- package metadata version `0.2.0`;
- imported package version `0.2.0`;
- imported module resolved inside the temporary wheel environment.

The initial dependency-isolated attempt correctly failed help imports because
`--no-deps` omitted Typer; no package defect was indicated, and the corrected
dependency-visible smoke passed.

## 17. Privacy And Tracking Review

- `git ls-files` found no tracked private databases, SQLite files, ZIP exports,
  or `.chronicle` artifacts.
- Tracked JSONL files are synthetic test fixtures only.
- Ignored private/local roots remain ignored, including `.chronicle/`,
  `exports/`, and `dist/`.
- A targeted scan of release-public files found no private user path,
  credential pattern, token, or private UUID-style conversation identifier.
- A release-link scan confirmed that README/manual/AI-task/ledger/report links
  in the GitHub release body are absolute and pinned to tag `v0.2.0`.
- Changed public artifacts were reviewed for fictional-only examples and no
  private transcript/title/snippet/hash/provider response.
- Build artifacts remain ignored and were not staged.

## 18. Acceptance-Criteria Matrix

| Criterion | Result | Evidence |
| --- | --- | --- |
| Version metadata is `0.2.0` | pass | source, CLI, wheel metadata |
| Actual post-v0.1.0 diff inventoried | pass | section 4 |
| MCP headline plus secondary progress | pass | README/release notes |
| GitHub release notes exist | pass | required path |
| README presents release candidate | pass | status/MCP sections |
| At least three fictional examples | pass | README, notes, post |
| Privacy/context tradeoff is accurate | pass | all public artifacts |
| Four-task local-AI direction | pass | release notes/post |
| Limitations and clients are explicit | pass | release notes/README |
| LinkedIn text publication-ready | pass | final URL placeholder only |
| Focused/full tests | pass | 14; 446 passed/1 skipped |
| Ruff/pre-commit/Poetry/build | pass | section 15 |
| Installed-wheel smoke | pass | section 16 |
| Privacy/tracking review | pass | section 17 |
| Completion report exists | pass | this report |
| Nothing staged/committed/published | pass | cached diff empty; no external action |

## 19. Files Changed

Release-candidate delivery:

- `pyproject.toml`;
- `src/chat_chronicle/__init__.py`;
- `README.md`;
- `md/releases/v0.2.0.md`;
- `md/release-artifacts/linkedin/chat-chronicle-v0.2.0-mcp-post.md`;
- `md/handoffs/reports/REL-0.2.0-completion-report.md`.

The PM-listed Python, test, and historical Markdown formatting changes were
restored to `HEAD` and are not part of the final changed-file set. Pre-existing
owner/manager plan, ledger, handoff/review, and MCP/LinkedIn drafts remain
present and are not claimed as executor-authored release content.

## 20. Manager Publication Checklist

1. Validate the complete candidate diff and this report.
2. Obtain owner approval for every public release and LinkedIn artifact.
3. Commit the accepted candidate.
4. After explicit owner authorization, push `main`.
5. Wait for CI on the exact release commit.
6. After explicit authorization, create and push annotated tag `v0.2.0`.
7. After explicit authorization, create the GitHub release from the prepared
   release notes and verify repository/tag/release URLs.
8. Replace LinkedIn “release candidate” wording with published-release wording.
9. Replace both LinkedIn release URL placeholders with the verified public
   GitHub release URL.
10. Obtain final owner approval and have the owner publish the LinkedIn post.
11. Record publication evidence and final branch state in manager-owned
    planning records.

## 21. Final `git status --short`

```text
 M README.md
 M md/development-ledger.md
 M md/master-plan.md
 M pyproject.toml
 M src/chat_chronicle/__init__.py
?? md/20260728_chronical_mcp_setting_post_v0.1.md
?? md/20260728_chronical_mcp_setting_post_v0.2.md
?? md/handoffs/REL-0.2.0-mcp-recall-release-linkedin-progress.md
?? md/handoffs/reports/REL-0.2.0-completion-report.md
?? md/handoffs/reports/REL-0.2.0-validation-review.md
?? md/linkedin-mcp-windows-post.md
?? md/release-artifacts/linkedin/chat-chronicle-v0.2.0-mcp-post.md
?? md/releases/
```

Nothing is staged. The manager-owned plan/ledger, REL handoff/review, and three
concurrent owner MCP/LinkedIn drafts were preserved without claiming them as
executor changes.
