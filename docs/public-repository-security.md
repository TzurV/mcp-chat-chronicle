# Public Repository Security

Chat Chronicle is developed against real conversation archives, private evaluation
corpora, local model runtimes, and paid cloud services. The GitHub repository is
public. These two facts require a strict publication boundary.

This document is the manager's mandatory review gate before every commit, tag,
push, release, or publication-artifact update. Passing automated checks reduces
risk but does not prove that a file is safe to publish.

## Public-By-Default Rule

Assume that every tracked byte is immediately copied, indexed, cached, and retained
in Git history. A later deletion from the working tree does not make published data
private again.

Do not track:

- passwords, API keys, OAuth codes, access or refresh tokens, private keys, ADC or
  service-account JSON, credential databases, or environment files;
- real Chronicle databases, WAL/SHM files, provider exports, raw transcripts,
  downloaded archives, screenshots containing private text, or model binaries;
- private evaluation inputs, FABLE references, candidate responses, judge
  responses, provider-response caches, run directories, manifests, or transfer
  packages;
- personal email addresses, user-profile paths, IP addresses, SSH targets, cloud
  project/account numbers, RunPod Pod or volume IDs, or private provider URLs;
- real conversation URLs, source filenames, session UUIDs, database conversation
  or message IDs when they can correlate with private material;
- hashes of private databases, corpora, reference sets, response trees, credential
  files, or private transfer packages. A hash is not the source data, but it is a
  stable fingerprint that can disclose identity or enable correlation;
- customer, employer, colleague, or third-party confidential information.

## Allowed Tracked Evidence

The following is normally acceptable after review:

- deliberately synthetic fixtures with fictional names, IDs, timestamps, paths,
  URLs, and content;
- configuration templates containing placeholders and environment-variable names,
  but no resolved values;
- public source-code commit IDs, public model repository revisions, public model
  artifact hashes, licenses, and published documentation links;
- aggregate counts, rates, latency, token totals, costs, hardware classes, and
  confusion matrices that cannot reconstruct or identify a private conversation;
- redacted completion reports and publication drafts whose examples are explicitly
  fictional or irreversibly generalized.

External model disclosure and GitHub publication are separate decisions. Approval
to send bounded private inputs to a named provider never authorizes committing
those inputs, responses, references, IDs, paths, or hashes.

## High-Review Files

Documentation is not automatically safe. Apply a full content review to:

- manager-chat or conversation-history publications;
- handoffs, completion reports, incident reports, and operator diaries;
- LinkedIn drafts, release notes, screenshots, generated images, diagrams, CSVs,
  and copied terminal output;
- test fixtures derived from a real conversation;
- any file produced by an executor from ignored `.chronicle/` content.

Manager-chat artifacts must be curated exports, never automatic copies of the live
chat. Replace titles, message text, URLs, paths, timestamps, source filenames,
UUIDs, conversation/message IDs, project identifiers, and personal details unless
each value is intentionally public and necessary.

## Manager Commit Gate

Run from the repository root before each commit:

```powershell
git status --short
git diff --name-only
git diff
git diff --check
```

After selecting files, stage only the reviewed paths and inspect the exact staged
snapshot:

```powershell
git diff --cached --name-status
git diff --cached --stat
git diff --cached
git diff --cached --check
```

Check for prohibited tracked artifact classes:

```powershell
git ls-files "*.db" "*.sqlite*" "*.zip" "*.7z" "*.tar" "*.tgz" `
  "*.jsonl" "*.ndjson" "*.gguf" "*.safetensors" "*.onnx" `
  "*.pem" "*.key" "*.p12" "*.pfx" ".env*"
```

Only deliberate synthetic fixtures may appear in that output. Confirm that local
private data is ignored before relying on the ignore rule:

```powershell
git check-ignore -v .chronicle\chronicle.db
git ls-files .chronicle
```

Run repository checks, including the private-key hook:

```powershell
poetry run pre-commit run --all-files
```

Also search the staged diff for project-specific values known during the activity:
account emails, project IDs/numbers, Pod/volume IDs, SSH hosts, local usernames,
private paths, real conversation URLs, and credential environment values. Do not
print secret values into a terminal log merely to search for them.

If the staged diff is large enough that it cannot be read carefully, split the
commit. Never approve a security-sensitive commit from `--stat` output alone.

## GitHub Controls

Public repositories receive GitHub secret scanning for supported secret patterns,
and GitHub provides push protection that can block supported secrets before they
are published. Keep repository and user push protection enabled. Never bypass a
warning without proving that the value is synthetic or a false positive.

These controls are supplemental. Pattern scanners cannot identify every private
conversation, path, resource ID, custom credential, or sensitive business fact.

## If Sensitive Data Is Found

Before commit: remove it from the file or leave the file untracked. Do not stage it.

After a local commit but before push: stop. Remove the data from the commit under
manager control, re-run the complete gate, and inspect the resulting commit.

After any public push:

1. revoke or rotate exposed credentials immediately; assume they are compromised;
2. preserve a private incident record without copying the secret into another
   tracked file;
3. remove the data from the current branch;
4. decide explicitly whether coordinated history rewriting with `git filter-repo`
   is required;
5. account for forks, clones, cached views, releases, tags, pull-request refs, and
   generated artifacts;
6. review GitHub secret-scanning alerts and contact GitHub Support when cached
   content or inaccessible references require assistance;
7. document only a sanitized incident summary publicly.

History rewriting is disruptive and does not replace credential rotation. Do not
force-push or rewrite repository history without explicit owner approval and a
coordinated recovery plan.

## Current Audit Baseline

The manager's August 2026 audit found no tracked high-confidence credentials,
private keys, personal database/export/model files, or known private cloud account
identifiers in the current tree or scanned Git history. Tracked JSONL files were
limited to synthetic test fixtures.

The audit did identify the curated manager-chat document as an intrinsically
high-risk publication artifact and found one missed local transcript identifier,
which was redacted. The repository did not have a dedicated secret-scanning CI job;
the existing pre-commit configuration now includes `detect-private-key` as a local
guard. GitHub secret scanning and push protection should also be verified in the
repository settings.
