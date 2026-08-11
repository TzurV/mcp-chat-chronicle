# Temporary Vertex ADC on RunPod

This guide records the accepted authentication method for running the GEPA
proposer on a RunPod Pod while calling Gemini through Google Vertex AI.

For Vertex calls made locally from Windows, VS Code, or Codex, use
[`windows-vertex-adc.md`](windows-vertex-adc.md) instead. Local Codex commands
have a distinct fresh-process inheritance boundary that this RunPod guide does
not address.

## Decision

Use temporary user Application Default Credentials (ADC) stored only in the
Pod's RAM-backed `/dev/shm` filesystem.

Do not use a Gemini API key for this route. Chat Chronicle's optimizer is
configured for `vertex-adc` and requires Google Vertex AI ADC. Do not create or
attach a service-account JSON key unless the owner separately approves a
fallback after this method fails.

This approach:

- keeps credentials off the persistent network volume, repository, bundles,
  configuration files, logs, and container image;
- does not require a RunPod environment update or Pod restart;
- uses the repository's accepted LiteLLM/Vertex integration without code or
  configuration changes; and
- allows credentials to be revoked and removed immediately after GEPA.

Google documents remote ADC login through
[`gcloud auth application-default login --no-browser`](https://docs.cloud.google.com/sdk/gcloud/reference/auth/application-default/login).
Google also recommends avoiding service-account keys where a safer method is
available: [service-account security guidance](https://docs.cloud.google.com/iam/docs/best-practices-service-accounts).

## Preconditions

1. The owner has established an interactive SSH connection to the allocated
   Pod.
2. The exact approved repository commit is checked out and clean.
3. The frozen development bundle and all experiment checkpoints are on the
   persistent network volume.
4. The BootstrapFewShot checkpoint has passed. Vertex is not required for P0 or
   BootstrapFewShot and should not be configured while either remains blocked.
5. Google Cloud CLI is installed on both the Pod and the owner's trusted
   browser-equipped computer.
6. The owner account can use Vertex AI in the selected project and can consume
   service quota. The usual predefined roles are Vertex AI User and Service
   Usage Consumer.
7. The owner has explicitly authorized the private development disclosure,
   proposer model, region, call/token/cost ceilings, and normal Vertex charges.

## Create Temporary ADC

Run these commands in the interactive Pod shell. Use the approved project ID in
place of `<PROJECT_ID>`.

```bash
umask 077
export CHRONICLE_ADC_HOME=/dev/shm/chronicle-vertex-adc
export HOME="$CHRONICLE_ADC_HOME"
export CLOUDSDK_CONFIG="$CHRONICLE_ADC_HOME/.config/gcloud"
mkdir -p "$CLOUDSDK_CONFIG"

gcloud auth application-default login \
  --no-browser \
  --project=<PROJECT_ID>
```

The Pod prints a long command beginning with
`gcloud auth application-default login --remote-bootstrap=`. Run that generated
command on the owner's trusted computer. Return its generated result only to the
waiting interactive Pod prompt.

The bootstrap command, returned URL, authorization material, credential file,
and tokens must not be pasted into chat, reports, shell-history captures, or
Git.

Set the quota project from the same temporary environment:

```bash
gcloud auth application-default set-quota-project <PROJECT_ID>
```

## Configure GEPA

Export these values only in the shell or `tmux` session that starts GEPA:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$CHRONICLE_ADC_HOME/.config/gcloud/application_default_credentials.json"
export GOOGLE_CLOUD_PROJECT="<PROJECT_ID>"
export GOOGLE_CLOUD_LOCATION="global"
export VERTEXAI_PROJECT="<PROJECT_ID>"
export VERTEXAI_LOCATION="global"
export GOOGLE_GENAI_USE_VERTEXAI="true"
```

Verify ADC without printing a token or calling Gemini:

```bash
gcloud auth application-default print-access-token >/dev/null
```

Do not add another synthetic provider gate when the approved workflow says to
proceed directly to the real GEPA pilot. The first real proposer call is the
authentication boundary. If it fails, preserve append-only evidence and budget
accounting, then stop without silently changing provider, model, region,
credentials, or retry policy.

## Cleanup

After GEPA finishes, or before releasing compute, use the same temporary `HOME`
and `CLOUDSDK_CONFIG` values to revoke ADC:

```bash
gcloud auth application-default revoke --quiet
unset GOOGLE_APPLICATION_CREDENTIALS GOOGLE_CLOUD_PROJECT GOOGLE_CLOUD_LOCATION
unset VERTEXAI_PROJECT VERTEXAI_LOCATION GOOGLE_GENAI_USE_VERTEXAI
```

Remove only `/dev/shm/chronicle-vertex-adc` after confirming that GEPA has
stopped. Verify that no credential-shaped file exists on the persistent volume.
Never delete experiment checkpoints as part of credential cleanup.

## Fallbacks

Use fallbacks only after a documented failure and new owner approval:

1. User ADC with service-account impersonation, when a dedicated
   least-privilege service account and required IAM role are available.
2. A temporary service-account JSON key delivered through a RunPod secret,
   materialized with mode `0600` under `/dev/shm`, then revoked and deleted after
   use.

RunPod secrets are substituted into Pod environment variables. Updating Pod
environment variables restarts the Pod, so this is not the preferred method for
scarce running capacity: [RunPod environment variables](https://docs.runpod.io/pods/templates/environment-variables).

Workload Identity Federation is a future production option only if the remote
platform supplies a suitable trusted external identity. It is outside this
bounded experiment.

## RunPod Lifecycle Boundary

Before releasing compute, copy and hash-verify all required state on the
persistent network volume. RunPod documents that stopping a Pod releases its GPU
and preserves volume data, but Pods with network volumes might require compute-
Pod termination instead of stop. In that case, terminate only the compute Pod
after persistence verification and retain the network volume:
[RunPod Pod lifecycle](https://docs.runpod.io/pods/manage-pods).

Never delete the persistent network volume without a new, explicit owner
instruction. A later restart should allocate compatible compute in the same data
center, attach the retained volume, establish SSH immediately, verify checkpoint
hashes, and resume from the accepted append-only state.
