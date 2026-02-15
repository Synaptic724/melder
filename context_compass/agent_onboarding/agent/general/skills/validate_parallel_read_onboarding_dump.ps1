param(
    [string]$ManifestPath = "context_compass/agent_onboarding/parallel_read_onboarding_dump/manifest.txt",
    [int]$MaxAgeMinutes = 120
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

function Get-HeaderValue {
    param(
        [string[]]$Lines,
        [string]$Prefix
    )

    foreach ($line in $Lines) {
        if ($line.StartsWith($Prefix, [System.StringComparison]::Ordinal)) {
            return $line.Substring($Prefix.Length).Trim()
        }
    }

    return $null
}

function Parse-SourceHashes {
    param(
        [string[]]$Lines
    )

    $prefix = "ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_SHA256: "
    $inSection = $false
    $map = @{}

    foreach ($line in $Lines) {
        if ($line -eq "ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_HASHES_BEGIN") {
            $inSection = $true
            continue
        }
        if ($line -eq "ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_HASHES_END") {
            break
        }
        if (-not $inSection -or -not $line.StartsWith($prefix, [System.StringComparison]::Ordinal)) {
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

function Parse-ChunkRecords {
    param(
        [string[]]$Lines
    )

    $prefix = "ONBOARDING_PARALLEL_DUMP_CHUNK: "
    $inSection = $false
    $records = [System.Collections.Generic.List[object]]::new()

    foreach ($line in $Lines) {
        if ($line -eq "ONBOARDING_PARALLEL_DUMP_CHUNK_HASHES_BEGIN") {
            $inSection = $true
            continue
        }
        if ($line -eq "ONBOARDING_PARALLEL_DUMP_CHUNK_HASHES_END") {
            break
        }
        if (-not $inSection -or -not $line.StartsWith($prefix, [System.StringComparison]::Ordinal)) {
            continue
        }

        $payload = $line.Substring($prefix.Length)
        $parts = $payload.Split("|", 6, [System.StringSplitOptions]::None)
        if ($parts.Count -ne 6) {
            continue
        }

        [int]$chunkNumber = 0
        [int]$startLine = 0
        [int]$endLine = 0
        [int]$lineCount = 0
        if (-not [int]::TryParse($parts[0], [ref]$chunkNumber)) { continue }
        if (-not [int]::TryParse($parts[2], [ref]$startLine)) { continue }
        if (-not [int]::TryParse($parts[3], [ref]$endLine)) { continue }
        if (-not [int]::TryParse($parts[4], [ref]$lineCount)) { continue }

        $records.Add([PSCustomObject]@{
                ChunkNumber = $chunkNumber
                ChunkName = $parts[1].Trim()
                StartLine = $startLine
                EndLine = $endLine
                LineCount = $lineCount
                ChunkHash = $parts[5].Trim().ToUpperInvariant()
            })
    }

    return @($records | Sort-Object -Property ChunkNumber)
}

$scriptDir = (Split-Path -Parent $PSCommandPath)
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..\..\..")).Path

$manifestResolved = Resolve-ExistingPath -Candidates @(
    $(if ([System.IO.Path]::IsPathRooted($ManifestPath)) { $ManifestPath } else { "" }),
    (Join-Path $repoRoot $ManifestPath),
    (Join-Path $scriptDir $ManifestPath),
    $ManifestPath
)

$manifestDir = Split-Path -Parent $manifestResolved
$lines = @(Get-Content -LiteralPath $manifestResolved -Encoding UTF8)
$reasons = [System.Collections.Generic.List[string]]::new()

$builtAtEpochRaw = Get-HeaderValue -Lines $lines -Prefix "ONBOARDING_PARALLEL_DUMP_BUILT_AT_EPOCH: "
$sourceManifestRaw = Get-HeaderValue -Lines $lines -Prefix "ONBOARDING_PARALLEL_DUMP_SOURCE_MANIFEST: "
$sourceManifestHashRaw = Get-HeaderValue -Lines $lines -Prefix "ONBOARDING_PARALLEL_DUMP_SOURCE_MANIFEST_SHA256: "
$chunkSizeRaw = Get-HeaderValue -Lines $lines -Prefix "ONBOARDING_PARALLEL_DUMP_CHUNK_SIZE_LINES: "
$totalSourceFilesRaw = Get-HeaderValue -Lines $lines -Prefix "ONBOARDING_PARALLEL_DUMP_TOTAL_SOURCE_FILES: "
$totalLinesRaw = Get-HeaderValue -Lines $lines -Prefix "ONBOARDING_PARALLEL_DUMP_TOTAL_LINES: "
$totalChunksRaw = Get-HeaderValue -Lines $lines -Prefix "ONBOARDING_PARALLEL_DUMP_TOTAL_CHUNKS: "

[int]$chunkSize = 0
if (-not [int]::TryParse($chunkSizeRaw, [ref]$chunkSize) -or $chunkSize -le 0) {
    $reasons.Add("Missing/invalid chunk size header: ONBOARDING_PARALLEL_DUMP_CHUNK_SIZE_LINES")
}

[int]$totalSourceFiles = 0
if (-not [int]::TryParse($totalSourceFilesRaw, [ref]$totalSourceFiles) -or $totalSourceFiles -le 0) {
    $reasons.Add("Missing/invalid total source files header.")
}

[int]$totalLines = 0
if (-not [int]::TryParse($totalLinesRaw, [ref]$totalLines) -or $totalLines -le 0) {
    $reasons.Add("Missing/invalid total lines header.")
}

[int]$totalChunks = 0
if (-not [int]::TryParse($totalChunksRaw, [ref]$totalChunks) -or $totalChunks -le 0) {
    $reasons.Add("Missing/invalid total chunks header.")
}

[long]$builtAtEpoch = 0
if (-not [long]::TryParse($builtAtEpochRaw, [ref]$builtAtEpoch)) {
    $reasons.Add("Missing/invalid build epoch header.")
}
else {
    $ageMinutes = [int][Math]::Floor(([DateTimeOffset]::UtcNow.ToUnixTimeSeconds() - $builtAtEpoch) / 60)
    if ($ageMinutes -lt 0) {
        $reasons.Add("Manifest build epoch is in the future.")
    }
    elseif ($MaxAgeMinutes -ge 0 -and $ageMinutes -gt $MaxAgeMinutes) {
        $reasons.Add("Manifest is stale. age_minutes=$ageMinutes max_age_minutes=$MaxAgeMinutes")
    }
}

$sourceHashes = Parse-SourceHashes -Lines $lines
$chunkRecords = Parse-ChunkRecords -Lines $lines
if ($sourceHashes.Count -eq 0) {
    $reasons.Add("No source-file hash entries found.")
}
if ($chunkRecords.Count -eq 0) {
    $reasons.Add("No chunk records found.")
}

if ($chunkRecords.Count -ne $totalChunks) {
    $reasons.Add("Chunk count mismatch. header=$totalChunks parsed=$($chunkRecords.Count)")
}

for ($i = 0; $i -lt $chunkRecords.Count; $i += 1) {
    $expectedChunk = $i + 1
    if ($chunkRecords[$i].ChunkNumber -ne $expectedChunk) {
        $reasons.Add("Chunk numbering gap/mismatch at position $expectedChunk.")
    }
}

$sourceManifestResolved = $null
if ([string]::IsNullOrWhiteSpace($sourceManifestRaw)) {
    $reasons.Add("Missing source manifest path header.")
}
else {
    try {
        $sourceManifestResolved = Resolve-ExistingPath -Candidates @(
            $(if ([System.IO.Path]::IsPathRooted($sourceManifestRaw)) { $sourceManifestRaw } else { "" }),
            (Join-Path $repoRoot $sourceManifestRaw),
            (Join-Path $scriptDir $sourceManifestRaw),
            $sourceManifestRaw
        )
    }
    catch {
        $reasons.Add("Source manifest path cannot be resolved: $sourceManifestRaw")
    }
}

if ($null -ne $sourceManifestResolved) {
    $sourceManifestHashActual = (Get-FileHash -LiteralPath $sourceManifestResolved -Algorithm SHA256).Hash.ToUpperInvariant()
    if ([string]::IsNullOrWhiteSpace($sourceManifestHashRaw)) {
        $reasons.Add("Missing source manifest hash header.")
    }
    elseif ($sourceManifestHashRaw.ToUpperInvariant() -ne $sourceManifestHashActual) {
        $reasons.Add("Source manifest hash mismatch. manifest=$($sourceManifestHashRaw.ToUpperInvariant()) current=$sourceManifestHashActual")
    }

    $manifestEntries = @(Get-Content -LiteralPath $sourceManifestResolved -Encoding UTF8 | ForEach-Object {
        $_.Trim()
    } | Where-Object {
        $_ -and -not $_.StartsWith("#")
    })

    if ($manifestEntries.Count -ne $totalSourceFiles) {
        $reasons.Add("Total source files mismatch. header=$totalSourceFiles current=$($manifestEntries.Count)")
    }

    foreach ($relativePath in $manifestEntries) {
        if (-not $sourceHashes.ContainsKey($relativePath)) {
            $reasons.Add("Missing source hash entry for: $relativePath")
            continue
        }

        $resolvedSourcePath = Resolve-ExistingPath -Candidates @(
            $(if ([System.IO.Path]::IsPathRooted($relativePath)) { $relativePath } else { "" }),
            (Join-Path $repoRoot $relativePath),
            (Join-Path $scriptDir $relativePath),
            $relativePath
        )
        $actualSourceHash = (Get-FileHash -LiteralPath $resolvedSourcePath -Algorithm SHA256).Hash.ToUpperInvariant()
        if ($actualSourceHash -ne $sourceHashes[$relativePath]) {
            $reasons.Add("Source file hash mismatch: $relativePath")
        }
    }
}

[int]$sumChunkLines = 0
$expectedStart = 1
foreach ($record in $chunkRecords) {
    $chunkPath = Join-Path $manifestDir $record.ChunkName
    if (-not (Test-Path -LiteralPath $chunkPath)) {
        $reasons.Add("Missing chunk file: $($record.ChunkName)")
        continue
    }

    $actualChunkHash = (Get-FileHash -LiteralPath $chunkPath -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($actualChunkHash -ne $record.ChunkHash) {
        $reasons.Add("Chunk hash mismatch: $($record.ChunkName)")
    }

    $actualLineCount = @(Get-Content -LiteralPath $chunkPath -Encoding UTF8).Count
    if ($actualLineCount -ne $record.LineCount) {
        $reasons.Add("Chunk line-count mismatch: $($record.ChunkName) manifest=$($record.LineCount) actual=$actualLineCount")
    }

    if ($record.StartLine -ne $expectedStart) {
        $reasons.Add("Chunk start-line discontinuity at $($record.ChunkName): expected=$expectedStart actual=$($record.StartLine)")
    }
    if ($record.EndLine -lt $record.StartLine) {
        $reasons.Add("Chunk end-line is before start-line: $($record.ChunkName)")
    }

    $expectedStart = $record.EndLine + 1
    $sumChunkLines += $record.LineCount
}

if ($sumChunkLines -ne $totalLines) {
    $reasons.Add("Total lines mismatch. header=$totalLines chunks_sum=$sumChunkLines")
}

if ($reasons.Count -gt 0) {
    throw "Parallel onboarding dump validation failed: $($reasons -join ' ; ')"
}

$manifestHash = (Get-FileHash -LiteralPath $manifestResolved -Algorithm SHA256).Hash.ToUpperInvariant()
Write-Output "ONBOARDING_PARALLEL_DUMP_VALIDATED: true"
Write-Output "ONBOARDING_PARALLEL_DUMP_MANIFEST: $manifestResolved"
Write-Output "ONBOARDING_PARALLEL_DUMP_MANIFEST_SHA256: $manifestHash"
Write-Output "ONBOARDING_PARALLEL_DUMP_CHUNK_SIZE_LINES: $chunkSize"
Write-Output "ONBOARDING_PARALLEL_DUMP_TOTAL_SOURCE_FILES: $totalSourceFiles"
Write-Output "ONBOARDING_PARALLEL_DUMP_TOTAL_LINES: $totalLines"
Write-Output "ONBOARDING_PARALLEL_DUMP_TOTAL_CHUNKS: $totalChunks"
