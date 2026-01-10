param(
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$contextRoot = Resolve-Path (Join-Path $scriptDir "..\..\..\..")
$bootstrap = Join-Path $contextRoot "system\installation\windows\bootstrap.ps1"

if (-not (Test-Path -LiteralPath $bootstrap)) {
    throw "Missing bootstrap script at $bootstrap"
}

if ($DryRun) {
    & $bootstrap -DryRun
} else {
    & $bootstrap
}
