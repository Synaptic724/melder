param(
    [string]$ManifestPath = "context_compass/agent_onboarding/parallel_read_onboarding_dump/manifest.txt",
    [int]$ChunkNumber = 1,
    [switch]$SummaryOnly,
    [switch]$ValidateFirst
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

if ($ChunkNumber -lt 1) {
    throw "ChunkNumber must be >= 1. Received: $ChunkNumber"
}

$scriptDir = (Split-Path -Parent $PSCommandPath)
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..\..\..")).Path

if ($ValidateFirst) {
    $validateScript = Join-Path $scriptDir "validate_parallel_read_onboarding_dump.ps1"
    & $validateScript -ManifestPath $ManifestPath | Out-Null
}

$manifestResolved = Resolve-ExistingPath -Candidates @(
    $(if ([System.IO.Path]::IsPathRooted($ManifestPath)) { $ManifestPath } else { "" }),
    (Join-Path $repoRoot $ManifestPath),
    (Join-Path $scriptDir $ManifestPath),
    $ManifestPath
)

$manifestDir = Split-Path -Parent $manifestResolved
$lines = @(Get-Content -LiteralPath $manifestResolved -Encoding UTF8)
$chunkRecords = Parse-ChunkRecords -Lines $lines

if ($chunkRecords.Count -eq 0) {
    throw "No chunk records found in manifest: $manifestResolved"
}

$record = $chunkRecords | Where-Object { $_.ChunkNumber -eq $ChunkNumber } | Select-Object -First 1
if ($null -eq $record) {
    throw "ChunkNumber out of range. chunk_number=$ChunkNumber total_chunks=$($chunkRecords.Count)"
}

$chunkPath = Join-Path $manifestDir $record.ChunkName
if (-not (Test-Path -LiteralPath $chunkPath)) {
    throw "Chunk file not found: $chunkPath"
}

$chunkSizeRaw = Get-HeaderValue -Lines $lines -Prefix "ONBOARDING_PARALLEL_DUMP_CHUNK_SIZE_LINES: "

Write-Output "ONBOARDING_PARALLEL_CHUNK_MANIFEST: $manifestResolved"
Write-Output "ONBOARDING_PARALLEL_CHUNK_NUMBER: $($record.ChunkNumber)"
Write-Output "ONBOARDING_PARALLEL_CHUNK_FILE: $($record.ChunkName)"
Write-Output "ONBOARDING_PARALLEL_CHUNK_PATH: $chunkPath"
Write-Output "ONBOARDING_PARALLEL_CHUNK_SIZE_LINES: $chunkSizeRaw"
Write-Output "ONBOARDING_PARALLEL_TOTAL_CHUNKS: $($chunkRecords.Count)"
Write-Output "ONBOARDING_PARALLEL_CHUNK_START_LINE: $($record.StartLine)"
Write-Output "ONBOARDING_PARALLEL_CHUNK_END_LINE: $($record.EndLine)"
Write-Output "ONBOARDING_PARALLEL_CHUNK_LINE_COUNT: $($record.LineCount)"

if ($SummaryOnly) {
    return
}

Write-Output "ONBOARDING_PARALLEL_CHUNK_CONTENT_BEGIN: chunk=$($record.ChunkNumber)"
Get-Content -LiteralPath $chunkPath -Encoding UTF8
Write-Output "ONBOARDING_PARALLEL_CHUNK_CONTENT_END: chunk=$($record.ChunkNumber)"
