# WP-4.1B - Local-Client Integration And End-To-End Validation

## Status

Ready for execution from the clean manager commit containing this handoff.

## Executor Role And Commit Boundary

You are the execution agent. The project owner will perform interactive client
configuration, application restart, approval, and prompt steps that only the
owner can perform. Remain in the same execution chat and guide the owner one
bounded step at a time.

Do not stage or commit files. The development manager owns validation and
commits after the owner explicitly requests one.

Read `md/agent-operating-notes.md` before running commands. In particular:

- verify that Poetry resolves to this repository's `.venv`;
- clear inherited `VIRTUAL_ENV` / `POETRY_ACTIVE` values if they point
  elsewhere;
- treat Windows sandbox process-launch failures as environment failures and
  retry important read-only commands using the accepted direct path;
- avoid fragile piped PowerShell command composition;
- preserve unrelated owner changes.

## Objective

Configure the accepted WP-4.1A read-only FastMCP stdio server for the owner's
local OpenAI and Anthropic clients, prove useful natural-language recall against
the existing frozen private development database, and write setup instructions
based only on steps the owner actually completed successfully.

This is an owner-in-the-loop integration package. It is not primarily a
production-code package.

## Accepted Starting Point

WP-4.1A is accepted at:

- handoff: `md/handoffs/WP-4.1A-fastmcp-core-server.md`;
- completion report:
  `md/handoffs/reports/WP-4.1A-completion-report.md`;
- validation:
  `md/handoffs/reports/WP-4.1A-validation-review.md`.

The accepted implementation provides:

- `chronicle serve`;
- FastMCP 3.x stdio transport;
- exactly three read-only tools:
  - `search_chats`;
  - `get_conversation`;
  - `list_recent_topics`;
- lazy optional MCP dependencies;
- read-only SQLite URI access plus `PRAGMA query_only = ON`;
- CLI, environment, config, and default database precedence;
- protocol-level subprocess coverage;
- database hash/count/schema/mtime and sidecar immutability coverage.

Do not redesign the server or tool contracts.

## Frozen Private Database

Use the accepted WP-5.1.2A frozen development snapshot:

```text
.chronicle/eval/dev-v1/source/chronicle-frozen.db
```

Its private manifest is:

```text
.chronicle/eval/dev-v1/source/snapshot-manifest.json
```

The snapshot contains real private conversation history. It is a fixed
development copy, not the active archive. The accepted aggregate baseline is
711 conversations and 28,370 messages at schema version 3. Recompute and verify
the private manifest evidence locally; do not copy hashes, paths, conversation
IDs, titles, URLs, snippets, or transcript content into tracked files.

Do not use, modify, migrate, initialize, ingest into, or run AI tasks against:

```text
.chronicle/chronicle.db
```

unless a later manager-approved rework explicitly requires it. WP-4.1B client
recall uses the frozen snapshot.

## Approved Target Clients

Target these installed/local surfaces:

1. Codex in the ChatGPT desktop app;
2. ChatGPT desktop local Work/Codex surface sharing the Codex host
   configuration;
3. Claude Code;
4. Claude Desktop.

Also document how the shared OpenAI configuration applies to Codex CLI and the
Codex IDE extension when current official and installed behavior confirms it.

For this package, "Claude" means Claude Desktop. Claude Code is a separate
target.

ChatGPT web, `claude.ai`, Claude Cowork remote sessions, mobile clients, remote
MCP connectors, and public plugin marketplaces are not local stdio targets.

## Current Documentation Baseline

Before giving configuration instructions, verify the current official docs and
record the page title, URL, and access date in the completion report.

At handoff creation time, the relevant official facts were:

- ChatGPT desktop, Codex CLI, and the Codex IDE extension support local stdio
  MCP and share MCP configuration for the same Codex host;
- Codex MCP configuration supports `command`, `args`, `env`, and `cwd`;
- ChatGPT web uses hosted plugins/remote MCP and does not read local Codex
  configuration;
- Claude Code supports local stdio registration through `claude mcp add` and
  accepts per-server environment variables;
- Claude Desktop supports local MCP servers, while current product guidance
  emphasizes desktop extensions for packaged distribution;
- `.mcpb` packaging is not required for WP-4.1B.

Primary sources:

- OpenAI Codex MCP guidance:
  `https://learn.chatgpt.com/docs/extend/mcp`;
- OpenAI Codex configuration reference:
  `https://learn.chatgpt.com/docs/config-file/config-reference`;
- Claude Code MCP guidance:
  `https://code.claude.com/docs/en/mcp`;
- Claude Desktop local MCP guidance:
  `https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop`;
- MCP specification:
  `https://modelcontextprotocol.io`.

Product configuration can change. Prefer verified current documentation and the
installed client's visible behavior over copied historical syntax. Document any
difference.

## Owner Authorization Already Granted

The owner has authorized this bounded WP-4.1B development activity. Do not ask
for the same authorization again for every client or tool call.

The authorization covers:

- local read-only access to the frozen WP-5.1.2A database;
- local CLI baseline queries against that snapshot;
- configuring the four approved local client surfaces;
- sending the selected search snippets and one bounded conversation extract
  through the relevant OpenAI and Anthropic cloud model service during the
  client E2E tests;
- ordinary service usage associated with those bounded prompts;
- reusing the same selected conversation and phrase across clients;
- one additional no-result or invalid-argument check that contains no private
  transcript content.

The authorization does not cover:

- bulk retrieval or disclosure of the archive;
- unrestricted exploration of private conversations;
- sending full transcripts when a bounded extract is sufficient;
- using the active database;
- remote hosting, tunnels, public endpoints, OAuth, or web-client bridging;
- changing privacy/account/admin settings;
- writing to either database;
- ingestion, migration, repair, AI-task execution, or generated enrichment;
- publishing private content in reports, README, screenshots, or logs.

Use `get_conversation(max_chars=2000)` initially. Increase it only when the
selected evidence cannot be validated within that bound and the owner approves
the specific increase.

## Working Mode

Follow this loop for every owner-controlled operation:

1. State the goal of the step.
2. Show the exact command or configuration change.
3. Explain what it reads or changes.
4. State the expected success evidence.
5. Ask the owner to perform the step and return the requested privacy-safe
   output.
6. Validate that output before continuing.

Do not dump the entire runbook on the owner at once. Keep enough state in your
execution chat to resume after application restarts.

Do not edit user-level Codex, ChatGPT, Claude Code, or Claude Desktop
configuration on the owner's behalf unless the owner explicitly requests that
specific edit after seeing the exact proposed change. Prefer supported client
commands or UI steps.

Before any config edit:

- inspect the current relevant server entry without exposing unrelated
  credentials;
- make or instruct the owner to make a local backup;
- preserve unrelated settings;
- use a stable server name such as `chat-chronicle`;
- avoid duplicate definitions at different scopes.

## Database Selection And Easy Switching

Client configuration must own the database selection through:

```text
CHAT_CHRONICLE_DB
```

For WP-4.1B, set it to the absolute resolved form of:

```text
.chronicle/eval/dev-v1/source/chronicle-frozen.db
```

The server command must remain stable and must not hardcode `--db-path` in the
normal client configuration:

```text
<repo>\.venv\Scripts\chronicle.exe
```

Arguments:

```text
serve
```

Set the working directory to the repository root where the client supports
`cwd`. Use absolute Windows paths in user-level client configuration.

The accepted database precedence remains:

1. `--db-path`;
2. `CHAT_CHRONICLE_DB`;
3. `.chronicle/config.yaml` `paths.db`;
4. built-in `.chronicle/chronicle.db`.

The client config intentionally sets `CHAT_CHRONICLE_DB`, so the MCP server does
not depend on whichever database the owner's interactive shell or Chronicle
config currently selects.

Document how to switch later:

```text
frozen development:
<repo>\.chronicle\eval\dev-v1\source\chronicle-frozen.db

active archive:
<repo>\.chronicle\chronicle.db
```

Switching requires changing only the `CHAT_CHRONICLE_DB` value and restarting or
reloading the client/server. Do not perform a cloud-client test against the
active archive in this work package.

Prove the precedence/switching mechanism locally without disclosing data:

- launch a read-only CLI command with `CHAT_CHRONICLE_DB` pointing to the
  frozen snapshot and confirm the displayed resolved path/count baseline;
- launch the same read-only CLI command with it pointing to the active archive
  and confirm the displayed path changes;
- restore the shell and client configuration to the frozen snapshot before MCP
  E2E testing;
- confirm neither database changed.

Do not include private absolute paths or counts from the active archive in
tracked documentation.

## Phase 0 - Repository And Dependency Preflight

1. Verify:

   ```powershell
   poetry env info --path
   git status --short
   git rev-parse HEAD
   ```

2. The Poetry path must be:

   ```text
   <repo>\.venv
   ```

3. Install or verify the accepted optional dependency:

   ```powershell
   poetry install -E mcp
   ```

   Do not change dependency versions merely because install refreshes local
   metadata. `poetry.lock` already contains the accepted FastMCP dependency.

4. Verify:

   ```powershell
   poetry run chronicle --help
   poetry run chronicle serve --help
   poetry run python -c "import fastmcp; print(fastmcp.__version__)"
   ```

5. Verify the direct executable exists:

   ```text
   <repo>\.venv\Scripts\chronicle.exe
   ```

6. Run the existing MCP focused tests before changing client configuration:

   ```powershell
   poetry run pytest tests/test_mcp_server.py -q
   ```

## Phase 1 - Frozen Snapshot Preflight

Before content inspection:

1. Parse the private snapshot manifest.
2. Recompute the frozen DB SHA-256.
3. Verify the manifest hash.
4. Verify exact file size.
5. Open using SQLite read-only/immutable mode.
6. Verify:
   - `PRAGMA integrity_check` is `ok`;
   - `PRAGMA user_version` is 3;
   - aggregate conversation/message counts match the accepted snapshot;
   - no `-wal` or `-shm` sidecar exists.
7. Capture private before-state evidence:
   - hash;
   - size;
   - mtime;
   - schema version;
   - conversation count;
   - message count;
   - AI-task-result count;
   - sidecar state.

Store any detailed local evidence only under a git-ignored path such as:

```text
.chronicle/mcp-e2e/
```

Do not change the snapshot's read-only attribute.

## Phase 2 - Establish The CLI Baseline

Set a shell-local variable for the frozen DB and use explicit `--db-path` only
for baseline clarity:

```powershell
$DB = ".\.chronicle\eval\dev-v1\source\chronicle-frozen.db"

poetry run chronicle stats --db-path $DB
poetry run chronicle recent -n 10 --db-path $DB
```

Ask the owner to select one suitable conversation from the output. Selection
requirements:

- contains no credentials, access tokens, personal secrets, medical details, or
  third-party confidential data;
- has a clear topic that can be searched by a short phrase;
- is short enough that a 2,000-character bounded extract is useful;
- is suitable for disclosure to both OpenAI and Anthropic under the approved
  development test;
- exists in the frozen snapshot.

Then guide the owner through:

```powershell
poetry run chronicle search --phrase "<selected phrase>" --db-path $DB
poetry run chronicle open <selected-id> --db-path $DB
```

Do not allow the `open` command to launch an external browser during baseline
inspection when that would distract from the local test. Use the accepted
no-browser environment behavior if needed.

Record privately:

- selected conversation ID;
- provider;
- selected phrase;
- expected search result position;
- expected title;
- expected date;
- expected message count or bounded transcript landmarks;
- whether it appears in the selected recent range.

Tracked reports may state only that one owner-selected conversation passed the
baseline.

Also establish:

- a no-result invented phrase;
- one invalid argument for a single-client negative test.

## Phase 3 - Stable Server Launch Contract

Verify the server starts through the exact executable and environment shape
that clients will use.

Conceptual configuration:

```text
name: chat-chronicle
transport: stdio
command: <repo>\.venv\Scripts\chronicle.exe
args: ["serve"]
cwd: <repo>
env:
  CHAT_CHRONICLE_DB: <repo>\.chronicle\eval\dev-v1\source\chronicle-frozen.db
```

Run one supported MCP inspector/client smoke if available, then close it. Do not
run the server manually in a persistent terminal for normal client usage; stdio
clients spawn and own the process.

Verify:

- initialization succeeds;
- the server identifies itself as Chat Chronicle;
- exactly the three accepted tools appear;
- stdout contains protocol frames only;
- diagnostics go to stderr;
- shutdown is clean;
- no database state changes.

## Phase 4 - OpenAI Client Integration

### 4.1 Registration

Use the current supported Codex configuration path. Prefer one user-level
configuration shared by ChatGPT desktop, Codex CLI, and the IDE extension unless
the owner explicitly chooses trusted project scope.

The expected durable form is equivalent to:

```toml
[mcp_servers.chat-chronicle]
command = "<repo>\\.venv\\Scripts\\chronicle.exe"
args = ["serve"]
cwd = "<repo>"

[mcp_servers.chat-chronicle.env]
CHAT_CHRONICLE_DB = "<repo>\\.chronicle\\eval\\dev-v1\\source\\chronicle-frozen.db"
```

Do not paste this blindly. Verify the installed Codex configuration schema and
Windows TOML escaping first.

Supported alternatives include the current `codex mcp add` command or the
ChatGPT desktop **Settings > MCP servers** UI. Use the simplest method that:

- preserves the environment variable in persistent configuration;
- keeps the command and database path separate;
- avoids duplicate server definitions;
- can be inspected and removed cleanly.

### 4.2 Verification Surfaces

Verify configuration with the available supported controls, such as:

```powershell
codex mcp list
codex mcp --help
```

In Codex/ChatGPT desktop, use the current MCP server settings and `/mcp` view.
Restart the application after configuration when required.

Record installed client versions privately. Track only privacy-safe version
information in the completion report.

### 4.3 OpenAI E2E

Run:

1. discovery of exactly three tools;
2. explicit `search_chats` request with the selected phrase;
3. `get_conversation` for the selected ID with `max_chars=2000`;
4. `list_recent_topics` with a bounded range;
5. one natural-language recall question that does not name the MCP tool.

The natural-language answer must:

- use Chronicle rather than unsupported model memory;
- match the CLI baseline;
- identify the supporting Chronicle conversation ID;
- not invent a URL or unsupported detail;
- remain bounded to the selected topic.

Verify the shared configuration in the installed OpenAI surfaces that are
available. Distinguish:

- config shared and server visible;
- tool manually callable;
- natural-language model-selected call successful.

Do not claim all three when only configuration visibility was tested.

## Phase 5 - Claude Code Integration

Use the supported Claude Code local stdio registration path. Prefer local or
user scope rather than a tracked project `.mcp.json`, because the frozen absolute
path is private and machine-specific.

The expected command shape is:

```powershell
claude mcp add --transport stdio `
  --env CHAT_CHRONICLE_DB="<absolute-frozen-db-path>" `
  --scope local `
  chat-chronicle -- `
  "<absolute-chronicle-exe>" serve
```

Verify option ordering against current `claude mcp --help` before asking the
owner to run it.

Inspect with:

```powershell
claude mcp list
claude mcp get chat-chronicle
```

Within Claude Code, use `/mcp` to confirm connection and exactly three tools.

Run the same explicit and natural-language E2E sequence against the same
selected conversation. Use the same `max_chars=2000` bound.

## Phase 6 - Claude Desktop Integration

First determine which supported path the installed Claude Desktop version
offers:

1. local developer MCP configuration;
2. an existing `claude_desktop_config.json` local stdio entry;
3. a custom desktop extension installation path.

For this package, prefer direct local developer configuration when supported.
Do not build an `.mcpb` merely because current product documentation recommends
extensions for distribution. Packaging is not required for owner-local E2E.

If direct local stdio configuration is available, use the equivalent of:

```json
{
  "mcpServers": {
    "chat-chronicle": {
      "type": "stdio",
      "command": "<repo>\\.venv\\Scripts\\chronicle.exe",
      "args": ["serve"],
      "env": {
        "CHAT_CHRONICLE_DB": "<repo>\\.chronicle\\eval\\dev-v1\\source\\chronicle-frozen.db"
      }
    }
  }
}
```

Preserve all unrelated JSON entries and validate the file before restart.

Use Claude Desktop developer settings, logs, and the Connectors/tools view to
verify the server. Run the same explicit and natural-language E2E sequence.

If the installed client allows local stdio only through `.mcpb`, stop that
client lane and report the exact verified limitation. Do not package an
extension without a manager-approved follow-up because packaging introduces a
separate distribution and configuration surface.

## Phase 7 - Negative And Switching Checks

Run these once, not in every client:

- no-result search returns an empty bounded result without a model invention;
- invalid bounded argument is surfaced as a tool error and does not disconnect
  the server.

Prove database switching without cloud disclosure:

1. Inspect the client config and show that `CHAT_CHRONICLE_DB` is a standalone
   environment value.
2. Use local CLI environment override checks for frozen and active paths.
3. Restore the client value to the frozen path.
4. Restart/reload and confirm the frozen baseline still works.

Do not send an active-archive conversation through a cloud client in this work
package.

## Phase 8 - Final Immutability And Privacy Verification

After all client tests, recompute the frozen before-state evidence and require:

- identical SHA-256;
- identical size and mtime;
- schema version still 3;
- identical conversation, message, and AI-result counts;
- `PRAGMA integrity_check` still `ok`;
- no `-wal` or `-shm` sidecars;
- write attempt still rejected;
- active DB hash/count/mtime unchanged from the locally recorded preflight;
- no private database/export/transcript/config artifact tracked or staged.

Run:

```powershell
git status --short
git ls-files .chronicle
git diff --check
```

Do not print private user-level client configuration into tracked logs.

## Production Defects And Allowed Rework

You may implement and test a narrow generic Chronicle fix without requesting a
new owner authorization when all are true:

- a currently supported local stdio client exposes a reproducible Chronicle
  defect;
- the fix stays within WP-4.1B local read-only integration;
- the accepted three-tool contracts do not change;
- no new transport, authentication, database write, or packaging layer is
  introduced;
- regression tests are added;
- changes remain unstaged and uncommitted for PM validation.

Pause and request manager review before continuing when resolution requires:

- remote HTTP, SSE, WebSocket, tunnel, or public hosting;
- OAuth or another new authentication system;
- ChatGPT web or `claude.ai` integration;
- `.mcpb` packaging;
- database writes, schema migration, ingest, repair, or enrichment;
- a fourth MCP tool or changes to accepted tool fields/bounds;
- broad client-specific compatibility abstractions;
- use of the active archive in cloud-client E2E;
- disclosure beyond the owner-authorized bounded cases.

Do not report `partial` merely because one product surface lacks a feature.
Classify it accurately as passed, unsupported by the verified installed
surface, or externally blocked. Continue independent client lanes.

## Documentation Deliverables

Write documentation only after the owner has followed the instructions and the
result is verified.

### README

Update `README.md` with a concise **MCP recall** section covering:

- what MCP recall does and does not do;
- `poetry install -E mcp`;
- the stable direct executable plus `serve`;
- `CHAT_CHRONICLE_DB` configuration;
- database precedence;
- frozen versus active database switching;
- tested client summary;
- the three tool names;
- the read-only guarantee;
- warning that selected tool output is processed by the client's model
  provider;
- link to the detailed guide.

Remove or update statements saying the MCP layer is only planned.

### Detailed Guide

Create:

```text
docs/mcp-client-setup.md
```

Include:

1. prerequisites;
2. architecture and stdio lifecycle;
3. server executable and optional dependency;
4. database selection and precedence;
5. switching frozen/active databases;
6. Codex/ChatGPT desktop setup;
7. Codex CLI/IDE shared-config note;
8. Claude Code setup;
9. Claude Desktop setup;
10. exact reload/restart steps;
11. tool discovery checks;
12. privacy-safe test prompts using invented placeholders;
13. expected behavior;
14. troubleshooting:
    - wrong Poetry/virtual environment;
    - executable not found;
    - invalid TOML/JSON;
    - wrong working directory;
    - server timeout;
    - duplicate server scope;
    - missing `mcp` extra;
    - database missing/unreadable/newer schema;
    - stdout contamination;
    - client admin policy disabling local MCP;
15. removal/disable instructions;
16. tested versions and validation date;
17. unsupported and unverified surfaces.

Tracked examples must use placeholders such as `<repo>` and contain no owner
username, private path, conversation ID, title, phrase, URL, UUID, or transcript.

## Automated Validation

At minimum run:

```powershell
poetry env info --path
poetry run pytest tests/test_mcp_server.py -q
poetry run pytest
poetry run ruff check .
poetry check
poetry run chronicle --help
poetry run chronicle serve --help
git diff --check
git status --short
```

Add focused tests only for a production or documentation-contract defect found
during client E2E. Do not add tests that depend on installed GUI clients,
user-level config, real database contents, network access, or private paths.

## Acceptance Matrix

WP-4.1B is complete only when:

- the frozen snapshot passes before/after integrity and immutability checks;
- the CLI baseline is established for one owner-selected conversation;
- database selection is set in client config through
  `CHAT_CHRONICLE_DB`;
- switching is documented and locally verified without cloud disclosure from
  the active archive;
- the server command remains stable and has no embedded `--db-path`;
- exactly three tools are visible in every successfully connected client;
- at least one OpenAI local surface completes explicit search, detail, recent,
  and natural-language recall;
- Claude Code completes the same E2E sequence;
- Claude Desktop completes the same sequence when its installed supported local
  configuration allows direct stdio;
- the natural-language answers match the CLI baseline and cite Chronicle
  conversation IDs;
- one no-result and one invalid-input check are handled safely;
- no database changed and no sidecar was created;
- README instructions were followed successfully by the owner before being
  finalized;
- `docs/mcp-client-setup.md` reflects tested behavior and honest limitations;
- no remote MCP, web bridge, `.mcpb`, write tool, or active-archive cloud smoke
  entered scope;
- focused/full tests, Ruff, Poetry, CLI help, diff, privacy, and tracking checks
  pass;
- the completion report exists;
- all delivery changes remain unstaged and uncommitted for PM validation.

An unavailable externally controlled client capability does not fail the whole
package when:

- current official documentation and installed behavior were both checked;
- the limitation is recorded precisely;
- the required OpenAI and Claude Code E2E lanes pass;
- no unsupported success is claimed.

## Completion Report

Write exactly:

```text
md/handoffs/reports/WP-4.1B-completion-report.md
```

Required sections:

1. **Status** - `ready for PM validation` or `blocked`;
2. **Executive Summary**;
3. **Starting Commit And Clean-Checkout Evidence**;
4. **Poetry And MCP Dependency Preflight**;
5. **Official Documentation And Installed-Client Verification**;
6. **Frozen Snapshot Preflight**;
7. **Owner Authorization And Disclosure Boundary**;
8. **Private CLI Baseline** - aggregate/pass evidence only;
9. **Server Launch Contract**;
10. **Database Configuration And Switching Evidence**;
11. **OpenAI Shared Configuration Result**;
12. **Codex Desktop E2E Result**;
13. **ChatGPT Desktop E2E Result**;
14. **Codex CLI/IDE Shared-Config Result**;
15. **Claude Code E2E Result**;
16. **Claude Desktop E2E Result**;
17. **Cross-Client Comparison**;
18. **Negative-Test Evidence**;
19. **Defects Found And Rework**;
20. **README And Detailed-Guide Changes**;
21. **Final Database Immutability Evidence**;
22. **Automated Validation Results**;
23. **Privacy And Git Tracking Check**;
24. **Client Compatibility Matrix** - `passed`, `unsupported`,
    `externally blocked`, or `not attempted`, with reason;
25. **Acceptance-Criteria Matrix** - every criterion marked `pass`, `fail`, or
    `not attempted`;
26. **Known Limitations And WP-4.2 Inputs**;
27. **Changed Files**;
28. **Final `git status --short`**.

Do not include:

- private absolute paths;
- database hashes;
- conversation IDs;
- conversation titles;
- search phrases;
- URLs or origin paths;
- transcript/snippet/summary content;
- account, machine, organization, or workspace identifiers;
- complete user-level configuration;
- credentials, tokens, or unrelated environment variables.

## Expected Changed Files

Normally:

- `README.md`;
- `docs/mcp-client-setup.md`;
- `md/handoffs/reports/WP-4.1B-completion-report.md`.

Only when a genuine generic defect is found:

- narrowly relevant source file(s);
- narrowly relevant test file(s).

Do not edit the master plan or development ledger; those remain PM-owned.

## Final Executor Instruction

Start with preflight and the frozen CLI baseline. Then guide the owner through
one client at a time. Do not write final documentation from assumed syntax.
Write it only after the owner has completed the corresponding step and you have
validated the result.
