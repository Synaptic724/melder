# context_compass/installation/windows/bootstrap.ps1
# Contract:
# - Safe to inspect; nothing happens unless user runs it.
# - If Python is missing or <3.10, prints instructions and exits non-zero.
# - Creates venv at: context_compass\.venv
# - Installs: pydantic + graphiti-core[kuzu]
# - Smoke test: imports pydantic, kuzu, graphiti_core

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
$RepoRoot  = Resolve-Path (Join-Path $ScriptDir "..\..")
$VenvDir   = Join-Path $RepoRoot "context_compass\.venv"

function Pick-Python {
  if (Get-Command py -ErrorAction SilentlyContinue) { return "py" }
  if (Get-Command python -ErrorAction SilentlyContinue) { return "python" }
  if (Get-Command python3 -ErrorAction SilentlyContinue) { return "python3" }
  return $null
}

$Py = Pick-Python
if (-not $Py) {
  Say "ERROR: Python not found."
  Say "Install Python 3.10+ (Graphiti requires 3.10+), then re-run:"
  Say "  powershell -ExecutionPolicy Bypass -File context_compass\installation\windows\bootstrap.ps1"
  exit 10
}

# Enforce Python >= 3.10 (Graphiti requirement)
$VersionOk = $false
try {
  if ($Py -eq "py") {
    & py -c "import sys; raise SystemExit(0 if sys.version_info[:2] >= (3,10) else 1)"
  } else {
    & $Py -c "import sys; raise SystemExit(0 if sys.version_info[:2] >= (3,10) else 1)"
  }
  $VersionOk = $true
} catch {
  $VersionOk = $false
}
if (-not $VersionOk) {
  $ver = (& $Py -V 2>&1) -join ""
  Say "ERROR: Python must be 3.10+ (Graphiti requirement)."
  Say "Current: $ver"
  exit 11
}

Say "Repo root: $RepoRoot"
Say "Using Python: $Py"
Say "Venv path: $VenvDir"

if (-not (Test-Path $VenvDir)) {
  if ($Py -eq "py") { Run "py -m venv `"$VenvDir`"" }
  else { Run "$Py -m venv `"$VenvDir`"" }
}

$VenvPy = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPy)) {
  Say "ERROR: venv python not found at $VenvPy"
  exit 12
}

Run "`"$VenvPy`" -m pip install --upgrade pip"
Run "`"$VenvPy`" -m pip install --upgrade pydantic `"graphiti-core[kuzu]`""

# Smoke test: imports only (no config)
Run "`"$VenvPy`" -c `"import sys; import pydantic; import kuzu; from graphiti_core import Graphiti; sys.stdout.write('deps ok`n')`""

Say ""
Say "OK: deps installed."
Say "Next steps:"
Say "  1) Use this interpreter for tooling:"
Say "     `"$VenvPy`" context_compass\tools\validate.py --repo-root ."
Say "  2) Then run scan once your certification gate allows it:"
Say "     `"$VenvPy`" context_compass\tools\scan.py --repo-root ."
