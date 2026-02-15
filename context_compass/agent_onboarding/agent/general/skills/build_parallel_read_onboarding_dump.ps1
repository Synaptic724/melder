param(
    [string]$ManifestPath = "context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt",
    [string]$OutputDir = "context_compass/agent_onboarding/parallel_read_onboarding_dump",
    [int]$ChunkSizeLines = 500
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

if ($ChunkSizeLines -le 0) {
    throw "ChunkSizeLines must be > 0. Received: $ChunkSizeLines"
}

$scriptDir = (Split-Path -Parent $PSCommandPath)
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..\..\..")).Path

$manifestResolved = Resolve-ExistingPath -Candidates @(
    $(if ([System.IO.Path]::IsPathRooted($ManifestPath)) { $ManifestPath } else { "" }),
    (Join-Path $repoRoot $ManifestPath),
    (Join-Path $scriptDir $ManifestPath),
    $ManifestPath
)

$outputResolved = if ([System.IO.Path]::IsPathRooted($OutputDir)) {
    [System.IO.Path]::GetFullPath($OutputDir)
}
else {
    Join-Path $repoRoot $OutputDir
}

if (-not (Test-Path -LiteralPath $outputResolved)) {
    New-Item -ItemType Directory -Path $outputResolved | Out-Null
}

$manifestOutputPath = Join-Path $outputResolved "manifest.txt"

$manifestEntries = @(Get-Content -LiteralPath $manifestResolved -Encoding UTF8 | ForEach-Object {
    $_.Trim()
} | Where-Object {
    $_ -and -not $_.StartsWith("#")
})

if ($manifestEntries.Count -eq 0) {
    throw "Manifest '$manifestResolved' produced no readable entries."
}

$sourceFileRecords = [System.Collections.Generic.List[object]]::new()
$combinedLines = [System.Collections.Generic.List[string]]::new()

foreach ($relativePath in $manifestEntries) {
    $resolvedPath = Resolve-ExistingPath -Candidates @(
        $(if ([System.IO.Path]::IsPathRooted($relativePath)) { $relativePath } else { "" }),
        (Join-Path $repoRoot $relativePath),
        (Join-Path $scriptDir $relativePath),
        $relativePath
    )

    $fileHash = (Get-FileHash -LiteralPath $resolvedPath -Algorithm SHA256).Hash.ToUpperInvariant()
    $sourceFileRecords.Add([PSCustomObject]@{
            RelativePath = $relativePath
            FileHash = $fileHash
        })

    $combinedLines.Add("===== BEGIN FILE: $relativePath =====")
    $fileLines = @(Get-Content -LiteralPath $resolvedPath -Encoding UTF8)
    foreach ($line in $fileLines) {
        $combinedLines.Add($line)
    }
    $combinedLines.Add("===== END FILE: $relativePath =====")
}

$totalLines = $combinedLines.Count
if ($totalLines -eq 0) {
    throw "Combined onboarding dump is unexpectedly empty."
}

$totalChunks = [int][Math]::Ceiling($totalLines / [double]$ChunkSizeLines)
$padWidth = [Math]::Max(2, $totalChunks.ToString().Length)

# Clean previous generated artifacts for deterministic rebuilds.
Get-ChildItem -LiteralPath $outputResolved -File -Filter "onboarding_read_*" -ErrorAction SilentlyContinue | Remove-Item -Force
if (Test-Path -LiteralPath $manifestOutputPath) {
    Remove-Item -LiteralPath $manifestOutputPath -Force
}

$chunkRecords = [System.Collections.Generic.List[object]]::new()
for ($chunkNumber = 1; $chunkNumber -le $totalChunks; $chunkNumber += 1) {
    $startZero = ($chunkNumber - 1) * $ChunkSizeLines
    $endZero = [Math]::Min($startZero + $ChunkSizeLines - 1, $totalLines - 1)
    $startOne = $startZero + 1
    $endOne = $endZero + 1
    $lineCount = $endZero - $startZero + 1

    $chunkName = "onboarding_read_{0}" -f $chunkNumber.ToString("D$padWidth")
    $chunkPath = Join-Path $outputResolved $chunkName

    $chunkLines = [System.Collections.Generic.List[string]]::new()
    for ($i = $startZero; $i -le $endZero; $i += 1) {
        $chunkLines.Add($combinedLines[$i])
    }

    Set-Content -LiteralPath $chunkPath -Value $chunkLines -Encoding UTF8
    $chunkHash = (Get-FileHash -LiteralPath $chunkPath -Algorithm SHA256).Hash.ToUpperInvariant()

    $chunkRecords.Add([PSCustomObject]@{
            ChunkNumber = $chunkNumber
            ChunkName = $chunkName
            StartLine = $startOne
            EndLine = $endOne
            LineCount = $lineCount
            ChunkHash = $chunkHash
        })
}

$builtAtUtc = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
$builtAtEpoch = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$manifestSourceHash = (Get-FileHash -LiteralPath $manifestResolved -Algorithm SHA256).Hash.ToUpperInvariant()

$builder = [System.Text.StringBuilder]::new()
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_VERSION: 1")
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_BUILT_AT_UTC: $builtAtUtc")
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_BUILT_AT_EPOCH: $builtAtEpoch")
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_CHUNK_SIZE_LINES: $ChunkSizeLines")
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_SOURCE_MANIFEST: $ManifestPath")
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_SOURCE_MANIFEST_RESOLVED: $manifestResolved")
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_SOURCE_MANIFEST_SHA256: $manifestSourceHash")
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_TOTAL_SOURCE_FILES: $($sourceFileRecords.Count)")
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_TOTAL_LINES: $totalLines")
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_TOTAL_CHUNKS: $totalChunks")
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_HASHES_BEGIN")
foreach ($record in $sourceFileRecords) {
    [void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_SHA256: $($record.RelativePath)|$($record.FileHash)")
}
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_HASHES_END")
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_CHUNK_HASHES_BEGIN")
foreach ($record in $chunkRecords) {
    [void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_CHUNK: $($record.ChunkNumber)|$($record.ChunkName)|$($record.StartLine)|$($record.EndLine)|$($record.LineCount)|$($record.ChunkHash)")
}
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_CHUNK_HASHES_END")
[void]$builder.AppendLine("ONBOARDING_PARALLEL_DUMP_COMPLETE: $($chunkRecords.Count) chunks serialized.")

Set-Content -LiteralPath $manifestOutputPath -Value $builder.ToString() -Encoding UTF8
$manifestFileHash = (Get-FileHash -LiteralPath $manifestOutputPath -Algorithm SHA256).Hash.ToUpperInvariant()

Write-Output "ONBOARDING_PARALLEL_DUMP_WRITTEN: $outputResolved"
Write-Output "ONBOARDING_PARALLEL_DUMP_MANIFEST: $manifestOutputPath"
Write-Output "ONBOARDING_PARALLEL_DUMP_CHUNK_SIZE_LINES: $ChunkSizeLines"
Write-Output "ONBOARDING_PARALLEL_DUMP_TOTAL_LINES: $totalLines"
Write-Output "ONBOARDING_PARALLEL_DUMP_TOTAL_CHUNKS: $totalChunks"
Write-Output "ONBOARDING_PARALLEL_DUMP_MANIFEST_SHA256: $manifestFileHash"
