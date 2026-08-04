# WP-5.2C1 RunPod Remote LM Studio Service Note

Status: future-reference design; no always-on service has been deployed.

## Purpose

Use a stopped-by-default RunPod GPU Pod as an on-demand LM Studio accelerator
for Chronicle integration tests, prompt-development batches, and private
evaluation candidate generation. Deterministic unit tests should continue to
run locally because they do not benefit from a remote GPU.

The WP-5.2C1 experiment demonstrated that this is technically useful. On the
same 120-case Chronicle workload, the retained RTX 5090 Pod completed the two
8,192-context runs in 131 and 129 seconds, and the 262,144-context run in 169
seconds. The accepted local 8K baseline took 4 hours 43 minutes 30.782 seconds.

## Recommended Topology

Keep LM Studio bound to loopback on the Pod and reach it through an encrypted
SSH local-forward:

```text
Chronicle -> 127.0.0.1:12340 -> SSH tunnel -> Pod 127.0.0.1:1234 -> LM Studio
```

Use RunPod full SSH over an exposed TCP port 22, authenticated only with the
owner SSH key. The current basic `ssh.runpod.io` proxy was suitable for an
interactive terminal but did not support the unattended command/tunnel
workflow used by WP-5.2C1. RunPod documents full SSH through a public-IP TCP
mapping separately from its limited basic SSH proxy:

- <https://docs.runpod.io/pods/configuration/use-ssh>
- <https://docs.runpod.io/pods/configuration/expose-ports>

Example local tunnel, with the actual address and assigned external SSH port
resolved from the Pod's Connect panel after every start or reset:

```powershell
ssh -N `
  -L 12340:127.0.0.1:1234 `
  root@<POD_PUBLIC_IP> `
  -p <POD_EXTERNAL_SSH_PORT> `
  -i $env:USERPROFILE\.ssh\id_ed25519 `
  -o ExitOnForwardFailure=yes `
  -o ServerAliveInterval=30
```

Use a dedicated Chronicle model profile rather than changing the accepted
local LM Studio profile:

```yaml
runpod-qwen:
  model: lm_studio/qwen3.5-4b
  api_base: http://127.0.0.1:12340/v1
  api_key_env: null
  remote: true
  timeout: 180
  retries: 0
  concurrency: 1
  structured_output: true
  reasoning_effort: none
  context_window: 262144
  generation: {temperature: 0, max_tokens: 500}
```

The profile must remain marked `remote: true`: although Chronicle connects to
localhost, prompts leave the owner's computer through the tunnel and execute
on RunPod.

## Security Boundary

Do not expose LM Studio port 1234 directly through the RunPod HTTP proxy.
RunPod states that proxied HTTP services are publicly accessible and should
implement authentication. Its HTTP proxy can also time out requests longer
than 100 seconds, while Chronicle permits 180-second model calls.

LM Studio does not require API authentication by default. Newer releases can
enforce API tokens, but that capability has not been qualified on the pinned
WP-5.2C1 headless runtime. Keep the inference listener on `127.0.0.1` and rely
on SSH key authentication until token enforcement is separately qualified:

- <https://beta.lmstudio.ai/docs/developer/rest/quickstart>
- <https://www.lmstudio.ai/docs/cli/serve/server-start>

Never place Google Cloud, Vertex, Gemini, AWS, database, or unrelated service
credentials on the Pod. Transfer private Chronicle inputs only for an
owner-authorized test. Do not send FABLE references, rubrics, judge caches, or
judge outputs when the Pod is used only for candidate inference.

## On-Demand Operating Sequence

1. Confirm the intended private-data scope, provider/region, price, model,
   context, and maximum runtime.
2. Start the retained Pod and verify its control-plane hardware identity.
3. Start `llmster` and the LM Studio server on Pod loopback.
4. Load the pinned model by its canonical key, with the required context and
   `--gpu max`.
5. Verify model identifier, context, model-file SHA-256, listener binding, and
   absence of forbidden cloud credentials.
6. Establish the local SSH tunnel on port 12340.
7. Check `http://127.0.0.1:12340/v1/models` locally.
8. Run only inference-bearing integration, benchmark, or prompt-development
   tests against the dedicated remote profile.
9. Package, hash, return, and locally verify evidence where the workflow
   requires immutable results.
10. Close the tunnel and stop GPU compute. Retain or delete storage according
    to the approved lifecycle decision.

## Performance And Capacity Evidence

The WP-5.2C1 maximum-context arm loaded Qwen3.5 4B Q4_K_M at 262,144 context in
2.34 seconds. Its structured synthetic request passed in 11.697 seconds, and
the full 120-case arm used a sampled peak of 11,896 MiB GPU memory. This leaves
substantial capacity on a 24 GB GPU, but concurrency above one remains
unqualified and must not be assumed safe or deterministic.

## Limitations

- A stopped Pod may not regain the same GPU immediately; this is a development
  accelerator, not an availability-guaranteed production endpoint.
- Secure Cloud public addresses may remain stable, but external TCP mappings
  can change after resets. Resolve them at each start.
- Network latency and tunnel setup reduce the benefit for very small requests.
- Increasing context improves long-input coverage; it does not make a 4B model
  semantically equivalent to Gemini.
- The service design requires a separate authorization before changing an
  existing proxy-only Pod to public-IP TCP SSH.
