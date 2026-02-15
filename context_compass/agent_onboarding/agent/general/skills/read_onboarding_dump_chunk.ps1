param(
    [string]$DumpPath = "context_compass/agent_onboarding/agent/general/skills/onboarding_read_dump.txt",
    [int]$ChunkSize = 500,
    [int]$ChunkIndex = 0,
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

if ($ChunkSize -le 0) {
    throw "ChunkSize must be > 0. Received: $ChunkSize"
}

if ($ChunkIndex -lt 0) {
    throw "ChunkIndex must be >= 0. Received: $ChunkIndex"
}

$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..\..\..")).Path

if ($ValidateFirst) {
    $validateScript = Join-Path $scriptDir "read_onboarding_dump.ps1"
    & $validateScript -DumpPath $DumpPath -ValidateOnly | Out-Null
}

$dumpResolved = Resolve-ExistingPath -Candidates @(
    $(if ([System.IO.Path]::IsPathRooted($DumpPath)) { $DumpPath } else { "" }),
    (Join-Path $repoRoot $DumpPath),
    (Join-Path $scriptDir $DumpPath),
    $DumpPath
)

$lines = @(Get-Content -LiteralPath $dumpResolved -Encoding UTF8)
$totalLines = $lines.Count

if ($totalLines -eq 0) {
    throw "Dump file is empty: $dumpResolved"
}

$totalChunks = [int][Math]::Ceiling($totalLines / [double]$ChunkSize)
if ($ChunkIndex -ge $totalChunks) {
    throw "ChunkIndex out of range. chunk_index=$ChunkIndex total_chunks=$totalChunks max_index=$($totalChunks - 1)"
}

$startZero = $ChunkIndex * $ChunkSize
$endZero = [Math]::Min($startZero + $ChunkSize - 1, $totalLines - 1)
$startOne = $startZero + 1
$endOne = $endZero + 1
$chunkLineCount = $endZero - $startZero + 1

Write-Output "DUMP_CHUNK_PATH: $dumpResolved"
Write-Output "DUMP_CHUNK_SIZE: $ChunkSize"
Write-Output "DUMP_TOTAL_LINES: $totalLines"
Write-Output "DUMP_TOTAL_CHUNKS: $totalChunks"
Write-Output "DUMP_CHUNK_INDEX: $ChunkIndex"
Write-Output "DUMP_CHUNK_START_LINE: $startOne"
Write-Output "DUMP_CHUNK_END_LINE: $endOne"
Write-Output "DUMP_CHUNK_LINE_COUNT: $chunkLineCount"

if ($SummaryOnly) {
    return
}

Write-Output "DUMP_CHUNK_CONTENT_BEGIN: index=$ChunkIndex"
for ($i = $startZero; $i -le $endZero; $i += 1) {
    Write-Output $lines[$i]
}
Write-Output "DUMP_CHUNK_CONTENT_END: index=$ChunkIndex"
