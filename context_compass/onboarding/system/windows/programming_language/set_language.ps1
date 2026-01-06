Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$contextRoot = Resolve-Path (Join-Path $scriptDir "..\..\..\..")
$langFile = Join-Path $contextRoot "system\config\languages.json"

$langDir = Split-Path -Parent $langFile
if (-not (Test-Path -LiteralPath $langDir)) {
    New-Item -ItemType Directory -Path $langDir | Out-Null
}

$payload = '{"default_language":"unknown","directory_hints":{},"extensions":{"py":"python"},"schema_version":1}'
$payload | Set-Content -LiteralPath $langFile -Encoding utf8

Write-Host "Wrote python-only language config: $langFile"
