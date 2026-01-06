# context_compass/system/installation/windows/bootstrap.ps1
# Contract:
# - Safe to inspect; nothing happens unless user runs it.
# - Installs uv (if missing), then creates the active environment.
# - Installs dependencies from installation/environments/requirements.txt.
# - Seeds SQLite/Kuzu DBs via installation/build_runner.py.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

param(
  [switch]$DryRun
)

function Say([string]$Msg) { Write-Host $Msg }
function Run([string]$Cmd) {
  if ($DryRun) { Say "[dry-run] $Cmd"; return }
  iex $Cmd
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstallRoot = Resolve-Path (Join-Path $ScriptDir "..")
$SystemRoot = Resolve-Path (Join-Path $InstallRoot "..")
$RepoRoot = Resolve-Path (Join-Path $SystemRoot "..\..")
$EnvScript = Join-Path $InstallRoot "environments\windows\install_active_env.ps1"
$PyVersionFile = Join-Path $InstallRoot "environments\python_version.md"
$EnvRoot = Join-Path $InstallRoot "environments\active_environments"

if (-not (Test-Path $EnvScript)) {
  throw "Missing env installer at $EnvScript"
}
if (-not (Test-Path $PyVersionFile)) {
  throw "Missing python_version.md at $PyVersionFile"
}

$PyVersion = (Get-Content -Raw $PyVersionFile).Trim()
if (-not $PyVersion) {
  throw "python_version.md is empty."
}

$EnvName = "context_compass_py$($PyVersion -replace '\.', '_')"
$EnvPath = Join-Path $EnvRoot $EnvName
$VenvPy = Join-Path $EnvPath "Scripts\python.exe"

Say "Repo root: $RepoRoot"
Say "Install root: $InstallRoot"
Say "Python version: $PyVersion"
Say "Environment path: $EnvPath"

Run "& `"$EnvScript`""

if (-not (Test-Path $VenvPy)) {
  throw "venv python not found at $VenvPy"
}

$BuildRunner = Join-Path $InstallRoot "build_runner.py"
$Manifest = Join-Path $InstallRoot "build_manifest.json"
Run "& `"$VenvPy`" `"$BuildRunner`" --manifest `"$Manifest`""

Say ""
Say "OK: environment ready and databases seeded."
Say "Next steps:"
Say "  `"$VenvPy`" context_compass\system\ai_restricted\system_management\validate.py --repo-root ."
