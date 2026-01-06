Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$envRoot = [IO.Path]::GetFullPath((Join-Path $scriptDir "..\active_environments"))
$pyVersionFile = Join-Path $scriptDir "..\python_version.md"
$requirementsFile = Join-Path $scriptDir "..\requirements.txt"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Output "uv is not installed. Installing uv..."
    try {
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    } catch {
        throw "uv install failed: $($_.Exception.Message)"
    }
    $cargoBin = Join-Path $HOME ".cargo\bin"
    if (Test-Path $cargoBin) {
        $env:Path = "$cargoBin;$env:Path"
    }
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is still unavailable after install. Restart your shell and retry."
}

if (-not (Test-Path $pyVersionFile)) {
    throw "Missing python_version.md at $pyVersionFile"
}

$pyVersion = (Get-Content -Raw $pyVersionFile).Trim()
if (-not $pyVersion) {
    throw "python_version.md is empty."
}

if (-not (Test-Path $requirementsFile)) {
    throw "Missing requirements.txt at $requirementsFile"
}

if (-not (Test-Path $envRoot)) {
    New-Item -ItemType Directory -Force -Path $envRoot | Out-Null
}

$envName = "context_compass_py$($pyVersion -replace '\.', '_')"
$envPath = Join-Path $envRoot $envName

uv python install $pyVersion
if (-not (Test-Path $envPath)) {
    uv venv $envPath --python $pyVersion
}

& (Join-Path $envPath "Scripts\Activate.ps1")
uv pip install -r $requirementsFile

Write-Output "Environment ready: $envPath"
