# Vertex ADC from Windows, VS Code, and Codex

This guide records the accepted local authentication procedure for Chronicle
development commands that call Google Vertex AI through LiteLLM or DSPy. It is
specifically designed for Windows work started from VS Code, Codex, or another
tool that launches fresh PowerShell processes.

This is separate from the temporary RunPod procedure in
[`runpod-vertex-adc.md`](runpod-vertex-adc.md).

## Why the environment matters

Google Cloud CLI and Application Default Credentials (ADC) are related but
different credential paths. A successful `gcloud` command does not prove that a
Python process will read the same ADC file.

The failure mode seen during WP-5.2B3B.1A combined three conditions:

- a custom `CLOUDSDK_CONFIG` directory held the current ADC file;
- `GOOGLE_APPLICATION_CREDENTIALS` pointed to a different, stale ADC file; and
- fresh Codex command processes did not inherit variables set in an unrelated
  interactive PowerShell session.

The result was confusing but correct: interactive `gcloud` checks passed while
the application-owned Vertex request failed authentication or authorization.

## Tracked configuration boundary

Never store these values in tracked files:

- Google Cloud project IDs or account email addresses;
- ADC paths, credential JSON, refresh tokens, or access tokens;
- OAuth return URLs or authorization codes.

Tracked YAML may declare only the required environment-variable names. Private
values belong in the operator process environment.

## Establish ADC

Use the intended Google account and project in a trusted PowerShell session:

```powershell
gcloud auth application-default login --project=<PROJECT_ID>
gcloud auth application-default set-quota-project <PROJECT_ID>
```

The consent grant must include the
`https://www.googleapis.com/auth/cloud-platform` scope. If browser consent does
not grant that scope, stop and correct the Google account/consent flow instead
of repeatedly calling Vertex.

Do not assume the default AppData path. Resolve ADC from the active gcloud
configuration directory:

```powershell
$gcloudConfig = if ($env:CLOUDSDK_CONFIG) {
    $env:CLOUDSDK_CONFIG
} else {
    Join-Path ([Environment]::GetFolderPath("ApplicationData")) "gcloud"
}

$adc = Join-Path $gcloudConfig "application_default_credentials.json"
if (-not (Test-Path -LiteralPath $adc)) {
    throw "ADC file is missing from the active gcloud configuration."
}
```

## Launch the application in one process boundary

Set all values before Python imports `google.auth`, LiteLLM, or DSPy:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = $adc
$env:GOOGLE_CLOUD_PROJECT = "<PROJECT_ID>"
$env:VERTEXAI_PROJECT = "<PROJECT_ID>"
$env:GOOGLE_CLOUD_LOCATION = "global"
$env:VERTEXAI_LOCATION = "global"
$env:GOOGLE_GENAI_USE_VERTEXAI = "true"
Remove-Item Env:CLOUDSDK_AUTH_ACCESS_TOKEN -ErrorAction SilentlyContinue

poetry run python -m bench <approved-command-and-flags>
```

The assignments and the Chronicle command must run in the same PowerShell
process. A variable set in one Codex tool call is not guaranteed to exist in
the next call. For a multi-step operation, use one ignored operator script or
one persistent shell that performs this bootstrap and then launches every
child command.

If VS Code or Codex itself must inherit the values, close all existing VS Code
and Codex processes, set the variables in PowerShell, and launch the application
from that same shell. Reloading only the editor window may not replace every
background process.

## Pre-call checks

Before a private provider call:

1. confirm the ADC file exists without printing its path;
2. confirm the resource and quota projects are the intended project;
3. confirm both location variables resolve to the task-approved location;
4. confirm `GOOGLE_GENAI_USE_VERTEXAI` is true;
5. refresh ADC without printing the token;
6. run at most the specifically authorized synthetic or real boundary.

```powershell
gcloud auth application-default print-access-token > $null
if ($LASTEXITCODE -ne 0) { throw "ADC refresh failed." }
```

For privacy-safe evidence, record booleans and hashes rather than account,
project, path, token, or credential values. Token metadata can be used to verify
the active principal and scopes, but the token itself must never be logged or
pasted into a report.

Do not rely on `credentials.scopes` alone to prove the scopes in the issued
token. Do not treat a successful IAM permission test as proof that the provider
request used the same credential unless both checks run in the same initialized
process.

## Failure procedure

Classify failures before requesting another provider call:

- credential discovery or refresh;
- IAM permission or quota project;
- provider request;
- empty response;
- invalid JSON;
- output-schema validation;
- application contract validation.

The diagnostic recorder must not collapse these boundaries into one provider
error. Preserve append-only evidence, clear process-scoped values when the run
ends, and do not retry until the failed boundary is understood and a new call is
authorized.

Once a same-process probe succeeds, proceed to the approved workload. Do not add
repeated authentication probes to every case.
