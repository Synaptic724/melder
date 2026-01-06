Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

param(
    [switch]$DryRun
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$contextRoot = Resolve-Path (Join-Path $scriptDir "..")
$repoRoot = Resolve-Path (Join-Path $contextRoot "..")
$bootstrap = Join-Path $repoRoot "context_compass\system\installation\windows\bootstrap.ps1"

if (-not (Test-Path -LiteralPath $bootstrap)) {
    throw "Missing bootstrap script at $bootstrap"
}

if ($DryRun) {
    & $bootstrap -DryRun
} else {
    & $bootstrap
}
