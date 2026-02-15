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

$builder = [System.Text.StringBuilder]::new()
[void]$builder.AppendLine("ONBOARDING_DUMP_MANIFEST: $ManifestPath")
[void]$builder.AppendLine("ONBOARDING_DUMP_SOURCE: $manifestResolved")
[void]$builder.AppendLine("ONBOARDING_DUMP_TOTAL_PATHS: $($manifestEntries.Count)")

foreach ($relativePath in $manifestEntries) {
    $resolvedPath = Resolve-ExistingPath -Candidates @(
        $(if ([System.IO.Path]::IsPathRooted($relativePath)) { $relativePath } else { "" }),
        (Join-Path $repoRoot $relativePath),
        (Join-Path $scriptDir $relativePath),
        $relativePath
    )

    [void]$builder.AppendLine("===== BEGIN FILE: $relativePath =====")
    $content = Get-Content -Raw -LiteralPath $resolvedPath -Encoding UTF8
    if ($content.Length -gt 0) {
        [void]$builder.Append($content)
    }

    $endsWithNewline = $content.EndsWith("`n") -or $content.EndsWith("`r")
    if (-not $endsWithNewline) {
        [void]$builder.AppendLine()
    }

    [void]$builder.AppendLine("===== END FILE: $relativePath =====")
}

[void]$builder.AppendLine("ONBOARDING_DUMP_COMPLETE: $($manifestEntries.Count) files serialized.")
Set-Content -LiteralPath $outputResolved -Value $builder.ToString() -Encoding UTF8

Write-Output "ONBOARDING_DUMP_WRITTEN: $outputResolved"
Write-Output "ONBOARDING_DUMP_FILES: $($manifestEntries.Count)"
