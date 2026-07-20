# RS-3: Codex Cross-Client Workspace Visibility

## Status

Recorded research observation and backlog input. This file is not a change order and
does not authorize implementation.

## Observation

Conversations created through the VS Code ChatGPT/Codex extension were initially not
visible in the Codex desktop application even though both clients used the same
authenticated OpenAI account.

The repository used in VS Code had not been opened in Codex Desktop. After the same
local repository was opened in Codex Desktop, the previously missing conversations
became visible there.

## Current Interpretation

Conversation visibility appears to depend on both:

- OpenAI account identity; and
- project or workspace association known to the desktop application.

The observation is a correlation, not proof of the underlying mechanism. Opening the
repository may register, synchronize, index, or reveal an existing project mapping.
Do not yet claim that an absolute path is the authoritative conversation key.

## Potentially Recoverable Metadata

- project or workspace association;
- local repository/path association;
- grouping of conversations by project;
- client-specific project registration state;
- a local or service-maintained project identifier.

This metadata could improve conversation grouping, filtering, project search, and
cross-client visibility diagnostics if a reliable source and stable identity contract
are verified.

## Current Chronicle Boundary

The accepted `chronicle scan-local` command detects the OpenAI Codex local store,
normally `%USERPROFILE%\.codex`, through shallow read-only signatures. The accepted
OpenAI Codex adapter imports supported JSONL sessions and optional
`session_index.jsonl` metadata.

Chronicle does not currently:

- inspect Codex Desktop project-registration state;
- prove that VS Code and desktop sessions share a workspace identifier;
- map visibility to an absolute path, repository identity, remote URL, or service ID;
- synchronize conversations between OpenAI clients;
- modify a client workspace registry.

## Open Questions

1. Is a project identified by absolute path, canonical path, repository root, Git
   remote, repository identity, or another internal identifier?
2. Is the association stored locally, maintained by the OpenAI service, or both?
3. Does opening a repository register it, trigger synchronization, or only reveal
   already-associated conversations?
4. Is the association stable if a repository is renamed or moved?
5. Is it portable across machines where the same repository lives at a different
   path?
6. Do ChatGPT Desktop, Codex Desktop, VS Code, and future clients use the same
   project identity?
7. Is relevant metadata present in Codex `session_index.jsonl`, session JSONL,
   desktop configuration, workspace databases, logs, or an authenticated service
   response?
8. Can the metadata be read safely without depending on fragile cache content or
   mutating client state?

## Future Investigation Candidate

A future time-boxed research spike may:

1. create an invented test repository with no private project content;
2. record read-only local metadata before and after opening it in Codex Desktop;
3. compare VS Code and desktop conversation/session metadata;
4. repeat after repository rename/move and, if practical, on a second machine;
5. identify stable join keys and distinguish local-path identity from service-side
   identity;
6. produce synthetic fixtures and a format/behavior memo before proposing extractor,
   schema, or `scan-local` changes.

Do not inspect credentials, authentication tokens, or unrelated private client data.
Do not add a project join or visibility claim based solely on the current observation.

## Useful Existing Command

Read-only source inventory:

```powershell
poetry run chronicle scan-local
```

This command confirms that a known local store exists; it does not diagnose whether
a conversation is visible in a particular OpenAI client.
