param(
    [string]$RepoRoot = $null
)

$now = (Get-Date).ToUniversalTime().ToString("o")
$os = Get-CimInstance -ClassName Win32_OperatingSystem
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
$python3Cmd = Get-Command python3 -ErrorAction SilentlyContinue
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
$rgCmd = Get-Command rg -ErrorAction SilentlyContinue
$pytestCmd = Get-Command pytest -ErrorAction SilentlyContinue

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $RepoRoot) {
    $RepoRoot = Join-Path $scriptDir "..\..\..\.."
}

$repoRootExists = $false
if ($RepoRoot) {
    $repoRootExists = Test-Path -LiteralPath $RepoRoot
    if ($repoRootExists) {
        $RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
    }
}

$contextCompassRoot = Join-Path $RepoRoot "context_compass"
$contextCompassExists = $repoRootExists -and (Test-Path -LiteralPath $contextCompassRoot)

$activeEnvRoot = Join-Path $contextCompassRoot "system\installation\environments\active_environments\windows"
$activeEnvExists = $false
$activeEnvPath = $null
if ($contextCompassExists -and (Test-Path -LiteralPath $activeEnvRoot)) {
    $activeEnvExists = $true
    $activeEnvPath = Get-ChildItem -Path $activeEnvRoot -Directory -Filter "context_compass_py*" -ErrorAction SilentlyContinue |
        Select-Object -First 1 | ForEach-Object { $_.FullName }
}

$activeEnvPython = $null
$activeEnvPythonExists = $false
if ($activeEnvPath) {
    $candidate = Join-Path $activeEnvPath "Scripts\python.exe"
    if (Test-Path -LiteralPath $candidate) {
        $activeEnvPythonExists = $true
        $activeEnvPython = $candidate
    }
}

$systemDbPath = Join-Path $contextCompassRoot "system\storage\sqlite\system.db"
$userDbPath = Join-Path $contextCompassRoot "system\storage\sqlite\user.db"
$systemDbExists = $contextCompassExists -and (Test-Path -LiteralPath $systemDbPath)
$userDbExists = $contextCompassExists -and (Test-Path -LiteralPath $userDbPath)
$systemReady = $contextCompassExists -and $systemDbExists -and $userDbExists

$pythonAvailable = ($pythonCmd -ne $null) -or ($python3Cmd -ne $null)
$pythonExe = $null
if ($pythonCmd -ne $null) {
    $pythonExe = $pythonCmd.Source
} elseif ($python3Cmd -ne $null) {
    $pythonExe = $python3Cmd.Source
}

$payload = @{
    schema_version = 1
    checked_at = $now
    os = @{
        name = $os.Caption
        platform = [System.Environment]::OSVersion.Platform.ToString()
        release = $os.Version
        version = $os.Version
        machine = $env:PROCESSOR_ARCHITECTURE
        processor = $env:PROCESSOR_IDENTIFIER
        is_windows = $true
        is_linux = $false
        is_macos = $false
    }
    python = @{
        available = $pythonAvailable
        executable = $pythonExe
        version = $null
        version_info = @()
        implementation = $null
    }
    tools = @{
        git = @{ available = ($gitCmd -ne $null); path = if ($gitCmd) { $gitCmd.Source } else { $null } }
        rg = @{ available = ($rgCmd -ne $null); path = if ($rgCmd) { $rgCmd.Source } else { $null } }
        pytest = @{ available = ($pytestCmd -ne $null); path = if ($pytestCmd) { $pytestCmd.Source } else { $null } }
    }
    repo = @{
        root = $RepoRoot
        exists = $repoRootExists
        context_compass = @{ path = $contextCompassRoot; exists = $contextCompassExists }
        databases = @{
            system_db = @{ path = $systemDbPath; exists = $systemDbExists }
            user_db = @{ path = $userDbPath; exists = $userDbExists }
        }
        ready = $systemReady
    }
    environment = @{
        active_env_root = $activeEnvRoot
        active_env_exists = $activeEnvExists
        active_env_path = $activeEnvPath
        active_env_python = $activeEnvPython
        active_env_python_exists = $activeEnvPythonExists
    }
    system_ready = $systemReady
}

$payload | ConvertTo-Json -Compress -Depth 6
if (-not $pythonAvailable) {
    exit 2
}
