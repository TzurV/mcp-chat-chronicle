# WP-4.1B Validation Review

## Decision

**Accepted on 2026-07-27.**

WP-4.1B completed the owner-in-the-loop integration objective without changing
the accepted WP-4.1A server or tool contracts. The tested configuration uses the
repository virtual environment's Python executable directly, which proved more
reliable across Windows MCP hosts than the Poetry-generated command shim.

## Evidence Reviewed

The manager reviewed:

- `md/handoffs/WP-4.1B-local-client-integration-e2e.md`;
- `md/handoffs/reports/WP-4.1B-completion-report.md`;
- `docs/mcp-client-setup.md`;
- the README MCP and quick-start changes;
- the portable project `.mcp.json`;
- the WP-4.1 plan and ledger status.

The completion evidence records:

- successful frozen-snapshot preflight and final immutability comparison;
- one owner-selected CLI baseline;
- exactly three read-only tools in connected clients;
- bounded search, detail, recent-topic, and natural-language recall;
- supporting Chronicle conversation IDs in grounded answers;
- safe no-result and invalid-bound behavior;
- successful Codex in VS Code, Windows Codex/OWL, Claude Code, and Claude
  Desktop lanes;
- an explicit later owner decision to switch all working clients to the active
  archive through `CHAT_CHRONICLE_DB` and run a bounded metadata-only smoke;
- 14 focused MCP tests and 446 full-suite passes with one skip;
- clean Ruff, Poetry, CLI-help, diff, privacy, and database checks.

## Accepted Integration Findings

- The stable Windows launch contract is:

  ```text
  <repo>\.venv\Scripts\python.exe -m chat_chronicle.cli serve
  ```

- Database selection remains separate in `CHAT_CHRONICLE_DB`.
- Client settings can switch between frozen and active databases without
  changing the server command.
- Claude Desktop's tested legacy direct configuration must omit
  `"type": "stdio"`.
- Client UI visibility is not sufficient evidence; successful tool calls are
  the acceptance boundary.
- ChatGPT web, classic ChatGPT Windows, and remote/mobile surfaces are not local
  stdio targets.
- Selected tool output is disclosed to the client's configured model provider,
  even though the server and database are local.

## Documentation Decision

The README remains CLI-first. It now provides:

- a compact route selector near the top;
- a link from the five-minute CLI flow to the MCP manual;
- a concise MCP capability and launch summary;
- a shortened project-status statement.

The detailed client configuration, restart, switching, privacy,
troubleshooting, and removal procedures remain in
`docs/mcp-client-setup.md`.

The tracked `.mcp.json` is accepted as a portable Claude Code project
configuration. It points only to the repository-local virtual environment and
ignored active database. No database, transcript, credential, username, or
absolute private path is tracked.

## Acceptance Matrix

| Requirement | Result |
| --- | --- |
| Frozen snapshot integrity before and after E2E | Pass |
| CLI baseline and bounded cross-client recall | Pass |
| Exactly three accepted read-only tools | Pass |
| OpenAI local client lane | Pass |
| Claude Code lane | Pass |
| Claude Desktop supported direct-config lane | Pass |
| Grounded answers cite Chronicle IDs | Pass |
| Negative behavior remains nonfatal | Pass |
| Active/frozen selection uses `CHAT_CHRONICLE_DB` | Pass |
| No production server or database change | Pass |
| README and detailed manual reflect verified behavior | Pass |
| Privacy and Git tracking boundary | Pass |

## Final PM Decision

WP-4.1B is accepted. Together, WP-4.1A and WP-4.1B complete the WP-4.1
FastMCP recall program. WP-4.2 remains an experimental remote-bridge
documentation backlog item and is not implied by this acceptance.
