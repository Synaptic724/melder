param(
    [string]$ManifestPath = "context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt",
    [string]$OutputPath = "context_compass/agent_onboarding/agent/general/skills/onboarding_read_dump.txt"
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

$scriptDir = (Split-Path -Parent $PSCommandPath)
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..\..\..")).Path

$manifestResolved = Resolve-ExistingPath -Candidates @(
    $(if ([System.IO.Path]::IsPathRooted($ManifestPath)) { $ManifestPath } else { "" }),
    (Join-Path $repoRoot $ManifestPath),
    (Join-Path $scriptDir $ManifestPath),
    $ManifestPath
)

$outputResolved = if ([System.IO.Path]::IsPathRooted($OutputPath)) {
    [System.IO.Path]::GetFullPath($OutputPath)
}
else {
    Join-Path $repoRoot $OutputPath
}

$outputDir = Split-Path -Parent $outputResolved
if (-not (Test-Path -LiteralPath $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

$manifestEntries = @(Get-Content -LiteralPath $manifestResolved -Encoding UTF8 | ForEach-Object {
    $_.Trim()
} | Where-Object {
    $_ -and -not $_.StartsWith("#")
})

if ($manifestEntries.Count -eq 0) {
    throw "Manifest '$manifestResolved' produced no readable entries."
}

$builtAtUtc = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
$builtAtEpoch = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$manifestHash = (Get-FileHash -LiteralPath $manifestResolved -Algorithm SHA256).Hash

$fileRecords = [System.Collections.Generic.List[object]]::new()
foreach ($relativePath in $manifestEntries) {
    $resolvedPath = Resolve-ExistingPath -Candidates @(
        $(if ([System.IO.Path]::IsPathRooted($relativePath)) { $relativePath } else { "" }),
        (Join-Path $repoRoot $relativePath),
        (Join-Path $scriptDir $relativePath),
        $relativePath
    )
    $content = Get-Content -Raw -LiteralPath $resolvedPath -Encoding UTF8
    $hash = (Get-FileHash -LiteralPath $resolvedPath -Algorithm SHA256).Hash
    $fileRecords.Add([PSCustomObject]@{
            RelativePath = $relativePath
            ResolvedPath = $resolvedPath
            Content = $content
            Hash = $hash
        })
}

$builder = [System.Text.StringBuilder]::new()
[void]$builder.AppendLine("ONBOARDING_DUMP_VERSION: 2")
[void]$builder.AppendLine("ONBOARDING_DUMP_BUILT_AT_UTC: $builtAtUtc")
[void]$builder.AppendLine("ONBOARDING_DUMP_BUILT_AT_EPOCH: $builtAtEpoch")
[void]$builder.AppendLine("ONBOARDING_DUMP_MANIFEST: $ManifestPath")
[void]$builder.AppendLine("ONBOARDING_DUMP_SOURCE: $manifestResolved")
[void]$builder.AppendLine("ONBOARDING_DUMP_MANIFEST_SHA256: $manifestHash")
[void]$builder.AppendLine("ONBOARDING_DUMP_HASH_ALGO: SHA256")
[void]$builder.AppendLine("ONBOARDING_DUMP_TOTAL_PATHS: $($manifestEntries.Count)")
[void]$builder.AppendLine("ONBOARDING_DUMP_FILE_HASHES_BEGIN")

foreach ($record in $fileRecords) {
    [void]$builder.AppendLine("ONBOARDING_DUMP_FILE_SHA256: $($record.RelativePath)|$($record.Hash)")
}

[void]$builder.AppendLine("ONBOARDING_DUMP_FILE_HASHES_END")
[void]$builder.AppendLine("ONBOARDING_DUMP_CONTENT_BEGIN")

foreach ($record in $fileRecords) {
    [void]$builder.AppendLine("===== BEGIN FILE: $($record.RelativePath) =====")
    if ($record.Content.Length -gt 0) {
        [void]$builder.Append($record.Content)
    }

    $endsWithNewline = $record.Content.EndsWith("`n") -or $record.Content.EndsWith("`r")
    if (-not $endsWithNewline) {
        [void]$builder.AppendLine()
    }

    [void]$builder.AppendLine("===== END FILE: $($record.RelativePath) =====")
}

[void]$builder.AppendLine("ONBOARDING_DUMP_CONTENT_END")
[void]$builder.AppendLine("ONBOARDING_DUMP_COMPLETE: $($manifestEntries.Count) files serialized.")

Set-Content -LiteralPath $outputResolved -Value $builder.ToString() -Encoding UTF8
$dumpHash = (Get-FileHash -LiteralPath $outputResolved -Algorithm SHA256).Hash
Write-Output "ONBOARDING_DUMP_WRITTEN: $outputResolved"
Write-Output "ONBOARDING_DUMP_FILES: $($manifestEntries.Count)"
Write-Output "ONBOARDING_DUMP_BUILT_AT_UTC: $builtAtUtc"
Write-Output "ONBOARDING_DUMP_SHA256: $dumpHash"
