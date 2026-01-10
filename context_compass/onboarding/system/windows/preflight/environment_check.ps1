Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CcRoot = Resolve-Path (Join-Path $ScriptDir "..\\..\\..\\..")

& (Join-Path $CcRoot "system\\ai_restricted\\system_management\\environment_check.ps1") @args
