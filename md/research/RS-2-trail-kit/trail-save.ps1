# WorkTrail trail-save — clipboard-catcher for composer-tier engines (ChatGPT, Copilot, Claude web).
# Usage: copy the engine's JSON code block, then run this script (pin to a shortcut for one-click use).
param(
    [string]$TrailDir = "C:\work\worktrail\trail"
)

New-Item -ItemType Directory -Force -Path $TrailDir | Out-Null

$raw = Get-Clipboard -Raw
if (-not $raw) { Write-Error "Clipboard is empty."; exit 1 }

# Strip Markdown code fences if present (```json ... ```)
$clean = $raw.Trim()
$clean = $clean -replace '(?s)^\s*```(?:json)?\s*', ''
$clean = $clean -replace '(?s)\s*```\s*$', ''

try {
    $obj = $clean | ConvertFrom-Json
} catch {
    Write-Error "Clipboard content is not valid JSON. Copy ONLY the JSON code block."; exit 1
}

if (-not $obj.note) { Write-Warning "Record has no 'note' — consider re-asking the engine." }
if ($obj.conversation_url -eq "<PASTE_URL>") {
    $url = Read-Host "Paste the conversation URL (or Enter to leave null)"
    $obj.conversation_url = if ($url) { $url } else { $null }
    $clean = $obj | ConvertTo-Json -Depth 5
}

$engine = if ($obj.engine) { $obj.engine } else { "unknown" }
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$path = Join-Path $TrailDir "$ts-$engine.json"
$clean | Out-File -FilePath $path -Encoding utf8
Write-Host "Trail record saved: $path"
