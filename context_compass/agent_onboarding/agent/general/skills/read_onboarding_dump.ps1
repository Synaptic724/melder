param(
    [string]$DumpPath = "context_compass/agent_onboarding/agent/general/skills/onboarding_read_dump.txt",
    [string]$ManifestPath = "context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt",
    [int]$MaxAgeMinutes = 120,
    [bool]$AutoRebuild = $true,
    [switch]$ValidateOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-ExistingPath {
    param(
        [string[]]$Candidates
    )

    foreach ($candidate in $Candidates) {
        if ([string]::IsNullOrWhiteSpace($candidate)) {
            continue
        }
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    throw "No existing path found. Candidates: $($Candidates -join '; ')"
}

function Normalize-AbsolutePath {
    param(
        [string]$PathInput,
        [string]$RepoRoot
    )

    if ([System.IO.Path]::IsPathRooted($PathInput)) {
        return [System.IO.Path]::GetFullPath($PathInput)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $PathInput))
}

function Get-HeaderValue {
    param(
        [string[]]$Lines,
        [string]$Prefix
    )

    foreach ($line in $Lines) {
        if ($line -eq "ONBOARDING_DUMP_CONTENT_BEGIN") {
            break
        }
        if ($line.StartsWith($Prefix, [System.StringComparison]::Ordinal)) {
            return $line.Substring($Prefix.Length).Trim()
        }
    }

    return $null
}

function Get-DumpFileHashes {
    param(
        [string[]]$Lines
    )

    $map = @{}
    $inSection = $false
    $prefix = "ONBOARDING_DUMP_FILE_SHA256: "

    foreach ($line in $Lines) {
        if ($line -eq "ONBOARDING_DUMP_FILE_HASHES_BEGIN") {
            $inSection = $true
            continue
        }

        if ($line -eq "ONBOARDING_DUMP_FILE_HASHES_END") {
            break
        }

        if (-not $inSection) {
            continue
        }

        if (-not $line.StartsWith($prefix, [System.StringComparison]::Ordinal)) {
            continue
        }

        $payload = $line.Substring($prefix.Length)
        $parts = $payload.Split("|", 2, [System.StringSplitOptions]::None)
        if ($parts.Count -ne 2) {
            continue
        }

        $relativePath = $parts[0].Trim()
        $hash = $parts[1].Trim().ToUpperInvariant()
        if ($relativePath.Length -eq 0 -or $hash.Length -eq 0) {
            continue
        }

        $map[$relativePath] = $hash
    }

    return $map
}

function Get-DumpValidationState {
    param(
        [string]$DumpResolved,
        [string]$ManifestResolved,
        [string[]]$ManifestEntries,
        [string]$RepoRoot,
        [string]$ScriptDir,
        [int]$MaxAgeMinutes
    )

    $reasons = [System.Collections.Generic.List[string]]::new()

    if (-not (Test-Path -LiteralPath $DumpResolved)) {
        $reasons.Add("Dump file missing: $DumpResolved")
        return [PSCustomObject]@{
            IsValid = $false
            Reasons = $reasons.ToArray()
            DumpLines = @()
            BuiltAtUtc = $null
            BuiltAtEpoch = $null
            AgeMinutes = $null
        }
    }

    $lines = @(Get-Content -LiteralPath $DumpResolved -Encoding UTF8)
    $builtAtUtcRaw = Get-HeaderValue -Lines $lines -Prefix "ONBOARDING_DUMP_BUILT_AT_UTC: "
    $builtAtEpochRaw = Get-HeaderValue -Lines $lines -Prefix "ONBOARDING_DUMP_BUILT_AT_EPOCH: "
    $manifestHashRaw = Get-HeaderValue -Lines $lines -Prefix "ONBOARDING_DUMP_MANIFEST_SHA256: "
    $declaredTotalRaw = Get-HeaderValue -Lines $lines -Prefix "ONBOARDING_DUMP_TOTAL_PATHS: "

    if ([string]::IsNullOrWhiteSpace($builtAtUtcRaw)) {
        $reasons.Add("Missing ONBOARDING_DUMP_BUILT_AT_UTC header.")
    }

    [long]$builtAtEpoch = 0
    $hasBuiltEpoch = [long]::TryParse($builtAtEpochRaw, [ref]$builtAtEpoch)
    if (-not $hasBuiltEpoch) {
        $reasons.Add("Missing/invalid ONBOARDING_DUMP_BUILT_AT_EPOCH header.")
    }

    if ([string]::IsNullOrWhiteSpace($manifestHashRaw)) {
        $reasons.Add("Missing ONBOARDING_DUMP_MANIFEST_SHA256 header.")
    }
    else {
        $currentManifestHash = (Get-FileHash -LiteralPath $ManifestResolved -Algorithm SHA256).Hash.ToUpperInvariant()
        if ($manifestHashRaw.ToUpperInvariant() -ne $currentManifestHash) {
            $reasons.Add("Manifest hash mismatch. dump=$($manifestHashRaw.ToUpperInvariant()) current=$currentManifestHash")
        }
    }

    [int]$declaredTotal = -1
    if (-not [int]::TryParse($declaredTotalRaw, [ref]$declaredTotal)) {
        $reasons.Add("Missing/invalid ONBOARDING_DUMP_TOTAL_PATHS header.")
    }
    elseif ($declaredTotal -ne $ManifestEntries.Count) {
        $reasons.Add("Path count mismatch. dump=$declaredTotal current=$($ManifestEntries.Count)")
    }

    $ageMinutes = $null
    if ($hasBuiltEpoch) {
        $nowEpoch = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        $ageMinutes = [int][Math]::Floor(($nowEpoch - $builtAtEpoch) / 60)
        if ($ageMinutes -lt 0) {
            $reasons.Add("Dump timestamp is in the future: epoch=$builtAtEpoch")
        }
        elseif ($MaxAgeMinutes -ge 0 -and $ageMinutes -gt $MaxAgeMinutes) {
            $reasons.Add("Dump is stale. age_minutes=$ageMinutes max_age_minutes=$MaxAgeMinutes")
        }
    }

    $dumpHashes = Get-DumpFileHashes -Lines $lines
    if ($dumpHashes.Count -eq 0) {
        $reasons.Add("No ONBOARDING_DUMP_FILE_SHA256 entries found.")
    }

    foreach ($relativePath in $ManifestEntries) {
        $resolvedPath = Resolve-ExistingPath -Candidates @(
            $(if ([System.IO.Path]::IsPathRooted($relativePath)) { $relativePath } else { "" }),
            (Join-Path $RepoRoot $relativePath),
            (Join-Path $ScriptDir $relativePath),
            $relativePath
        )

        if (-not $dumpHashes.ContainsKey($relativePath)) {
            $reasons.Add("Missing file hash entry for: $relativePath")
            continue
        }

        $expectedHash = $dumpHashes[$relativePath]
        $actualHash = (Get-FileHash -LiteralPath $resolvedPath -Algorithm SHA256).Hash.ToUpperInvariant()
        if ($expectedHash -ne $actualHash) {
            $reasons.Add("File hash mismatch for $relativePath. dump=$expectedHash current=$actualHash")
        }
    }

    $contentStart = [Array]::IndexOf($lines, "ONBOARDING_DUMP_CONTENT_BEGIN")
    $contentEnd = [Array]::IndexOf($lines, "ONBOARDING_DUMP_CONTENT_END")
    if ($contentStart -lt 0 -or $contentEnd -lt 0 -or $contentEnd -le $contentStart) {
        $reasons.Add("Missing or invalid ONBOARDING_DUMP_CONTENT_* markers.")
    }

    return [PSCustomObject]@{
        IsValid = ($reasons.Count -eq 0)
        Reasons = $reasons.ToArray()
        DumpLines = $lines
        BuiltAtUtc = $builtAtUtcRaw
        BuiltAtEpoch = if ($hasBuiltEpoch) { $builtAtEpoch } else { $null }
        AgeMinutes = $ageMinutes
    }
}

$scriptDir = (Split-Path -Parent $PSCommandPath)
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..\..\..")).Path
$manifestResolved = Resolve-ExistingPath -Candidates @(
    $(if ([System.IO.Path]::IsPathRooted($ManifestPath)) { $ManifestPath } else { "" }),
    (Join-Path $repoRoot $ManifestPath),
    (Join-Path $scriptDir $ManifestPath),
    $ManifestPath
)
$dumpResolved = Normalize-AbsolutePath -PathInput $DumpPath -RepoRoot $repoRoot

$manifestEntries = @(Get-Content -LiteralPath $manifestResolved -Encoding UTF8 | ForEach-Object {
    $_.Trim()
} | Where-Object {
    $_ -and -not $_.StartsWith("#")
})

if ($manifestEntries.Count -eq 0) {
    throw "Manifest '$manifestResolved' produced no readable entries."
}

$state = Get-DumpValidationState `
    -DumpResolved $dumpResolved `
    -ManifestResolved $manifestResolved `
    -ManifestEntries $manifestEntries `
    -RepoRoot $repoRoot `
    -ScriptDir $scriptDir `
    -MaxAgeMinutes $MaxAgeMinutes

if (-not $state.IsValid -and $AutoRebuild) {
    $buildScript = Join-Path $scriptDir "build_onboarding_dump.ps1"
    & $buildScript -ManifestPath $ManifestPath -OutputPath $DumpPath | Out-Null

    $state = Get-DumpValidationState `
        -DumpResolved $dumpResolved `
        -ManifestResolved $manifestResolved `
        -ManifestEntries $manifestEntries `
        -RepoRoot $repoRoot `
        -ScriptDir $scriptDir `
        -MaxAgeMinutes $MaxAgeMinutes
}

if (-not $state.IsValid) {
    $reasonText = ($state.Reasons -join " ; ")
    throw "Onboarding dump validation failed: $reasonText"
}

$dumpHash = (Get-FileHash -LiteralPath $dumpResolved -Algorithm SHA256).Hash
Write-Output "ONBOARDING_DUMP_VALIDATED: true"
Write-Output "ONBOARDING_DUMP_PATH: $dumpResolved"
Write-Output "ONBOARDING_DUMP_BUILT_AT_UTC: $($state.BuiltAtUtc)"
if ($null -ne $state.AgeMinutes) {
    Write-Output "ONBOARDING_DUMP_AGE_MINUTES: $($state.AgeMinutes)"
}
Write-Output "ONBOARDING_DUMP_SHA256: $dumpHash"

if ($ValidateOnly) {
    return
}

$contentStart = [Array]::IndexOf($state.DumpLines, "ONBOARDING_DUMP_CONTENT_BEGIN")
$contentEnd = [Array]::IndexOf($state.DumpLines, "ONBOARDING_DUMP_CONTENT_END")
for ($i = $contentStart + 1; $i -lt $contentEnd; $i += 1) {
    Write-Output $state.DumpLines[$i]
}
