param(
    [string]$ManifestPath = "context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt",
    [switch]$EmitContent
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

$manifestHash = (Get-FileHash -LiteralPath $manifestResolved -Algorithm SHA256).Hash
$manifestEntries = Get-Content -LiteralPath $manifestResolved | ForEach-Object {
    $_.Trim()
} | Where-Object {
    $_ -and -not $_.StartsWith("#")
}

if ($manifestEntries.Count -eq 0) {
    throw "Manifest '$manifestResolved' produced no readable entries."
}

Write-Output "READSET_MANIFEST: $manifestResolved"
Write-Output "READSET_MANIFEST_SHA256: $manifestHash"
Write-Output "READSET_TOTAL_PATHS: $($manifestEntries.Count)"

$index = 0
foreach ($relativePath in $manifestEntries) {
    $index += 1
    $resolvedPath = Resolve-ExistingPath -Candidates @(
        $(if ([System.IO.Path]::IsPathRooted($relativePath)) { $relativePath } else { "" }),
        (Join-Path $repoRoot $relativePath),
        (Join-Path $scriptDir $relativePath),
        $relativePath
    )

    $content = Get-Content -Raw -LiteralPath $resolvedPath
    $lineCount = if ($content.Length -eq 0) { 0 } else { ($content -split "`r?`n").Count }
    $byteCount = [System.Text.Encoding]::UTF8.GetByteCount($content)
    $fileHash = (Get-FileHash -LiteralPath $resolvedPath -Algorithm SHA256).Hash

    Write-Output ("READSET_ITEM[{0}/{1}]: {2} | lines={3} | bytes={4} | sha256={5}" -f $index, $manifestEntries.Count, $relativePath, $lineCount, $byteCount, $fileHash)

    if ($EmitContent) {
        Write-Output ("===== BEGIN FILE: {0} =====" -f $relativePath)
        Write-Output $content
        Write-Output ("===== END FILE: {0} =====" -f $relativePath)
    }
}

Write-Output "READSET_COMPLETE: $($manifestEntries.Count) files processed."
