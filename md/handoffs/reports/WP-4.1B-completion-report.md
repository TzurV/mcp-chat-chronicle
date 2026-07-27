# WP-4.1B Completion Report

## 1. Status

Ready for PM validation.

## 2. Executive Summary

The accepted read-only Chronicle MCP server was integrated with the available
local Codex and Claude surfaces. Codex in VS Code, Claude Code, and Claude
Desktop completed bounded natural-language recall against the frozen development
snapshot. The Windows Codex desktop surface also completed MCP search/detail
calls after its launcher was changed from a Poetry command shim to the virtual
environment's native Python executable. No database, server tool contract,
transport, or production source was changed.

After completion testing, the owner explicitly requested that every working
client switch from the frozen snapshot to the active archive. Codex, Claude
Code, the repository project configuration, and Claude Desktop were updated and
restarted. Both client families returned current post-snapshot metadata,
confirming the operational switch.

## 3. Starting Commit And Clean-Checkout Evidence

Execution began at commit `5e58e36217e467d9a770d8b0612d8ac4424f15f7`.
Initial `git status --short` was empty. Later PM-owned changes to the master plan
and development ledger were preserved untouched.

## 4. Poetry And MCP Dependency Preflight

Poetry resolved to the repository `.venv`. `poetry install -E mcp` required no
dependency update. FastMCP `3.4.4`, CLI help, serve help, and 14 focused MCP tests
passed. Poetry `2.3.4` installed `chronicle.cmd`, not the handoff-expected
`chronicle.exe`.

## 5. Official Documentation And Installed-Client Verification

Reviewed on 27 July 2026:

- [Model Context Protocol | ChatGPT Learn](https://learn.chatgpt.com/docs/extend/mcp)
- [Configuration Reference | ChatGPT Learn](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Connect Claude Code to tools via MCP | Claude Code Docs](https://code.claude.com/docs/en/mcp)
- [Getting Started with Local MCP Servers on Claude Desktop | Claude Help Center](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [What is the Model Context Protocol (MCP)?](https://modelcontextprotocol.io/docs/getting-started/intro)

Installed versions were Codex CLI `0.146.0-alpha.3.1`, Codex/OWL Windows app
`26.721.41059`, Claude Code `2.1.81`, and Claude Desktop `1.24012.9`.
Installed behavior was treated as authoritative where UI/schema details differed
from historical examples.

## 6. Frozen Snapshot Preflight

The private manifest was parsed locally. Hash and exact size matched; immutable
read-only SQLite open succeeded; integrity was `ok`; schema version was 3; the
accepted 711-conversation/28,370-message aggregate matched; AI-result count was
recorded privately; and no WAL/SHM sidecars existed. Detailed identities remain
under ignored `.chronicle/mcp-e2e/`.

## 7. Owner Authorization And Disclosure Boundary

The owner selected one suitable conversation and approved bounded disclosure to
OpenAI and Anthropic. Detail retrieval used `max_chars=2000`. The owner separately
approved up to ten recent-topic metadata rows for the OpenAI check. No bulk
retrieval occurred. The acceptance-phase cloud checks used only the frozen
snapshot.

After bounded acceptance testing, the owner separately directed an operational
switch to the active database and authorized a bounded recent-metadata smoke
through Codex and Claude. That later action is distinct from the frozen-snapshot
acceptance evidence and did not retrieve full active-archive transcripts.

## 8. Private CLI Baseline

One owner-selected conversation passed exact-phrase CLI search as the sole
result, opened successfully locally, and was confirmed suitable for bounded
cross-provider testing. Private title, phrase, ID, paths, and transcript evidence
are intentionally omitted here.

## 9. Server Launch Contract

The intended `chronicle.exe` was absent. A protocol smoke proved
`chronicle.cmd`, but the Windows Codex host did not launch that shim reliably.
The cross-client tested contract became:

```text
<repo>\.venv\Scripts\python.exe -m chat_chronicle.cli serve
```

Database selection remained solely in `CHAT_CHRONICLE_DB`; `cwd` was set where
supported. Initialization identified Chat Chronicle, exposed exactly three tools,
and shut down cleanly.

## 10. Database Configuration And Switching Evidence

Every effective client entry used `CHAT_CHRONICLE_DB`. Local CLI checks resolved
first to the frozen snapshot and then to the active archive; the paths and
aggregate counts changed as expected. The shell override was restored to frozen
and cleared. No active-archive content was sent to a cloud client.

Post-validation, all working client settings were deliberately switched to the
active archive for normal use: shared Codex user configuration, Claude Code
private local configuration, the untracked repository `.mcp.json`, and Claude
Desktop developer configuration. All retained the same native Python command
and changed only `CHAT_CHRONICLE_DB`. The owner fully terminated affected
desktop processes and verified current activity newer than the frozen cutoff in
both client families.

## 11. OpenAI Shared Configuration Result

The user-level Codex TOML entry was backed up, added, inspected, and given an
explicit repository `cwd`. The native Python launcher fixed Windows host
compatibility. The same configuration was visible to installed Codex surfaces
after their required reload/restart.

## 12. Codex Desktop E2E Result

Passed MCP search and bounded detail retrieval with the native Python launcher.
The server appeared in Settings. Its `/mcp` presentation did not list the custom
server, so success is based on confirmed calls rather than that view.

## 13. ChatGPT Desktop E2E Result

The Codex/OWL desktop surface result is recorded above. The classic ChatGPT
Windows application did not expose local MCP or `/mcp` and is not a local stdio
target.

## 14. Codex CLI/IDE Shared-Config Result

Codex in VS Code loaded the global entry after **Developer: Reload Window**,
discovered exactly three tools, completed search, 2,000-character detail,
ten-row recent metadata, and model-selected recall, and cited the supporting
Chronicle conversation ID.

## 15. Claude Code E2E Result

Claude Code connected at private local project scope with the native Python
launcher. It exposed exactly three tools and completed explicit/model-selected
search and detail plus five-row recent-topic recall. Its answer matched the CLI
and Codex baseline and cited the supporting ID.

## 16. Claude Desktop E2E Result

Claude Desktop supported legacy direct local configuration through Developer
**Edit Config**. The JSON was backed up and validated. The installed build ignored
an entry containing `"type": "stdio"`; omitting that property allowed connection.
Search/detail natural recall and five-row recent-topic recall passed. No `.mcpb`
was built.

## 17. Cross-Client Comparison

All successful clients used the same Python module entry point, frozen database
environment value, three tool contracts, selected conversation, and bounded
evidence. Answers agreed on the selected work topic and supporting ID. UI
discovery differed: VS Code and Claude Code exposed tool listings, while the
Windows Codex app proved calls despite an incomplete `/mcp` view.

## 18. Negative-Test Evidence

One invented query returned an empty bounded result. One below-minimum
`max_chars` value returned a tool error. A subsequent search succeeded, proving
the server remained connected.

## 19. Defects Found And Rework

No Chronicle production defect was found. Two integration incompatibilities were
documented: Poetry produced a `.cmd` shim instead of the assumed `.exe`, and the
tested Claude Desktop legacy schema ignored an explicit stdio `type` property.
Both were resolved in client configuration without changing server contracts.

## 20. README And Detailed-Guide Changes

README now describes implemented MCP recall, installation, stable Windows
launch, database precedence/switching, privacy, tools, and tested clients.
`docs/mcp-client-setup.md` records only owner-verified setup, restart, validation,
troubleshooting, switching, and removal behavior.

The guide was expanded into a full MCP user manual covering MCP concepts,
supported clients, five-minute setup, every verified configuration format,
reload behavior, everyday prompts, result interpretation, archive refresh,
privacy boundaries, troubleshooting, switching, and removal.

### Manager README recommendations

The executor intentionally leaves broader README restructuring to the manager.
Recommended changes:

1. Keep **Start searching in 5 minutes** as the first task-oriented section.
   It should remain CLI-first and contain only install, init, source placement,
   collect/stats, and one search example.
2. At the end of that five-step block, add one sentence linking to the
   [MCP Recall User Manual](../../../docs/mcp-client-setup.md) for AI-assisted
   recall in Codex or Claude.
3. Keep the top-level **MCP recall** section short: one explanatory paragraph,
   one minimal launch contract, the model-provider privacy warning, and the
   manual link.
4. Keep per-client TOML/JSON, restart instructions, troubleshooting, switching,
   and removal only in the user manual.
5. Add a compact “Choose your path” line near the top: CLI search uses the
   five-minute quick start; AI-client recall uses the MCP manual; advanced AI
   tasks/evaluation use the existing specialist documentation.
6. Do not add client matrices to the quick start. Its job is to take a new user
   from clone to first local search.
7. Shorten the project-status paragraph to a capability list plus links to the
   master plan and development ledger, rather than accumulating implementation
   history on the landing page.

## 21. Final Database Immutability Evidence

The final private comparison passed. Frozen and active database hashes, sizes,
mtimes, schema/count evidence, and AI-result counts were identical to their
recorded preflight values. Integrity remained `ok`; both write probes were
rejected; and neither database had a WAL or SHM sidecar.

## 22. Automated Validation Results

- Focused MCP tests: 14 passed.
- Full suite: 446 passed, 1 skipped.
- Ruff: passed.
- `poetry check`: passed.
- Main and serve CLI help: passed.
- `git diff --check`: passed.
- Final private immutability script: passed.

The combined validation shell wrapper timed out after 121 seconds while printing
CLI help, after the full suite, Ruff, Poetry check, and main help had already
completed successfully. The remaining serve-help, immutability, Git, and privacy
checks were rerun separately and passed.

## 23. Privacy And Git Tracking Check

Private evidence is ignored under `.chronicle/`. `git ls-files .chronicle`
returned no tracked paths. No database, transcript,
credential, private absolute path, conversation identifier, search phrase,
origin path, or private result is included in tracked deliverables. User-level
configuration was never copied into tracked logs. A targeted tracked-document
scan found none of the prohibited private values.

## 24. Client Compatibility Matrix

| Surface | Result | Reason |
| --- | --- | --- |
| Codex in VS Code | passed | Three tools and full bounded E2E passed |
| Codex/OWL Windows app | passed | Search/detail calls passed; `/mcp` UI omission noted |
| Codex CLI shared config | passed | Entry inspected by installed CLI |
| Codex IDE shared config | passed | Same global entry loaded after window reload |
| Claude Code | passed | Three tools and full bounded E2E passed |
| Claude Desktop | passed | Direct config and bounded E2E passed without `.mcpb` |
| Classic ChatGPT Windows | unsupported | No local MCP control |
| ChatGPT web / `claude.ai` | unsupported | Remote/plugin surfaces, not local stdio |
| Mobile / remote sessions | not attempted | Outside work-package scope |

## 25. Acceptance-Criteria Matrix

| Criterion | Result |
| --- | --- |
| Frozen before/after integrity and immutability | pass |
| Owner-selected CLI baseline | pass |
| `CHAT_CHRONICLE_DB` client selection | pass |
| Local frozen/active switching; frozen restored | pass |
| Stable command without embedded `--db-path` | pass |
| Exactly three tools in connected clients | pass |
| OpenAI local full E2E | pass |
| Claude Code full E2E | pass |
| Claude Desktop supported-path E2E | pass |
| Answers match baseline and cite Chronicle ID | pass |
| No-result and invalid-input handling | pass |
| README instructions owner-verified | pass |
| Detailed guide reflects tested behavior | pass |
| No remote bridge, `.mcpb`, or write tool | pass |
| Acceptance-phase cloud smoke limited to frozen snapshot | pass |
| Later active-archive metadata smoke separately owner-authorized | pass |
| Automated validation | pass |
| Completion report | pass |
| Delivery unstaged and uncommitted | pass |

## 26. Known Limitations And WP-4.2 Inputs

- Windows installers may produce command shims that native MCP hosts cannot
  spawn; the venv Python module contract is reliable.
- Client UI status is not equivalent to successful tool execution.
- Recent-topic quality falls back to raw titles when stored summaries/titles are
  weak.
- Project `.mcp.json` can be portable only when every checkout provides the
  referenced local database; duplicate scope definitions should be avoided.
- Desktop-extension packaging remains a separate distribution concern.
- MCP does not refresh the archive; normal operation still requires periodic
  `chronicle collect`.

## 27. Changed Files

Delivery changes:

- `README.md`;
- `docs/mcp-client-setup.md`;
- `md/handoffs/reports/WP-4.1B-completion-report.md`.

A manager-created `.mcp.json` and PM-owned plan/ledger edits are not claimed as
executor delivery. During PM acceptance, the portable project configuration was
reviewed, documented, and accepted for tracking because it contains only
repository-relative paths to ignored local artifacts.

## 28. Final `git status --short`

```text
 M README.md
 M md/development-ledger.md
 M md/master-plan.md
?? .mcp.json
?? docs/mcp-client-setup.md
?? md/handoffs/reports/WP-4.1B-completion-report.md
```

`README.md` and the two new documentation files are executor delivery.
The master-plan and ledger edits are pre-existing PM-owned work. `.mcp.json` was
created in the manager/owner workflow, remains untracked, contains only relative
paths, and is not claimed as delivery. Nothing is staged or committed.
