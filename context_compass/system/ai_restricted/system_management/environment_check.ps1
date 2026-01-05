$now = (Get-Date).ToUniversalTime().ToString("o")
$os = Get-CimInstance -ClassName Win32_OperatingSystem
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
$python3Cmd = Get-Command python3 -ErrorAction SilentlyContinue
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
$rgCmd = Get-Command rg -ErrorAction SilentlyContinue
$pytestCmd = Get-Command pytest -ErrorAction SilentlyContinue

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
}

$payload | ConvertTo-Json -Compress -Depth 6
if (-not $pythonAvailable) {
    exit 2
}
