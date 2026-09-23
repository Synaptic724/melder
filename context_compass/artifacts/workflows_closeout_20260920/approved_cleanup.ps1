<#
.SYNOPSIS
Execute the owner's explicit approval for two disposable scratch roots and two patch archives.
.DESCRIPTION
Only the fixed paths below may be mutated. Recheck containment and reparse points before
recursive operations. Keep original patch hashes and an incremental cleanup receipt.
#>
$ErrorActionPreference = 'Stop'
$workspace = 'C:\Users\Mark\PycharmProjects\melder_private'
$compass = Join-Path $workspace 'context_compass'
$receiptPath = Join-Path $PSScriptRoot 'approved_cleanup_receipt.json'
$scratchNames = @('ci_stage_qualification_20260906', 'uv_environment_20260908')
$patchNames = @('ci_stage_qualification_2026_09_06', 'uv_environment_2026_09_08')
$receipt = [ordered]@{
    approval = 'Owner explicitly approved the two named scratch deletions and patch archival on 2026-09-20.'
    started_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    deleted = @()
    archived = @()
    finished_at = $null
    error = $null
}
function Save-Receipt {
    # Persist completed operations immediately so a failure never requires inferring what was changed.
    [IO.File]::WriteAllText($receiptPath, ($receipt | ConvertTo-Json -Depth 8) + [Environment]::NewLine)
}
function Get-VerifiedRoot([string]$Path, [string]$Boundary) {
    # Reject lexical escapes and every reparse point from the selected root up to its allowed parent.
    $absolute = (Resolve-Path -LiteralPath $Path).Path
    $limit = [IO.Path]::GetFullPath($Boundary).TrimEnd('\')
    if (-not $absolute.StartsWith($limit + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Target outside approved boundary: $absolute"
    }
    $cursor = Get-Item -LiteralPath $absolute -Force
    while ($cursor.FullName.Length -ge $limit.Length) {
        if ($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "Reparse point in target path: $($cursor.FullName)"
        }
        $cursor = $cursor.Parent
        if ($null -eq $cursor) { break }
    }
    return $absolute
}
function Get-VerifiedEntries([string]$Path) {
    # Do not traverse or remove reparse descendants, even inside an otherwise approved scratch root.
    $entries = @(Get-ChildItem -LiteralPath $Path -Recurse -Force)
    if (@($entries | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) {
        throw "Reparse descendant in $Path"
    }
    return $entries
}
try {
    Save-Receipt
    foreach ($name in $patchNames) {
        $source = Get-VerifiedRoot (Join-Path $compass "system_docs/patches/active/$name") $compass
        $destination = [IO.Path]::GetFullPath((Join-Path $compass "system_docs/patches/completed/$name"))
        if (-not $destination.StartsWith($compass + '\system_docs\patches\completed\',
            [StringComparison]::OrdinalIgnoreCase)) { throw "Archive target escapes scope: $destination" }
        if (Test-Path -LiteralPath $destination) { throw "Archive target already exists: $destination" }
        $archiveParent = Get-VerifiedRoot (Split-Path -Parent $destination) $compass
        $entries = @(Get-VerifiedEntries $source)
        $hashes = @($entries | Where-Object { -not $_.PSIsContainer } | ForEach-Object {
            [pscustomobject]@{
                path = $_.FullName.Substring($source.Length + 1)
                sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
            }
        })
        Move-Item -LiteralPath $source -Destination $destination
        foreach ($item in $hashes) {
            if ((Get-FileHash -LiteralPath (Join-Path $destination $item.path) -Algorithm SHA256).Hash -cne $item.sha256) {
                throw "Archived bytes changed: $($item.path)"
            }
        }
        $receipt.archived += [ordered]@{source=$source; destination=$destination; files=$hashes; hashes_preserved=$true}
        Save-Receipt
    }
    foreach ($name in $scratchNames) {
        $root = Get-VerifiedRoot (Join-Path $compass "artifacts/$name") $compass
        if ($root -cne (Join-Path $compass "artifacts\$name")) { throw "Unexpected resolved scratch path: $root" }
        $files = @(Get-VerifiedEntries $root | Where-Object { -not $_.PSIsContainer })
        $count = $files.Count
        $bytes = ($files | Measure-Object Length -Sum).Sum
        Remove-Item -LiteralPath $root -Recurse -Force
        if (Test-Path -LiteralPath $root) { throw "Scratch root still exists: $root" }
        $receipt.deleted += [ordered]@{path=$root; files=$count; bytes=$bytes; absent_after=$true}
        Save-Receipt
    }
    $receipt.finished_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    Save-Receipt
    [ordered]@{
        deleted_roots = $receipt.deleted.Count
        deleted_files = (@($receipt.deleted | ForEach-Object { $_['files'] }) | Measure-Object -Sum).Sum
        deleted_bytes = (@($receipt.deleted | ForEach-Object { $_['bytes'] }) | Measure-Object -Sum).Sum
        archived_lanes = $receipt.archived.Count
        archived_files = @($receipt.archived | ForEach-Object { $_.files }).Count
        hashes_preserved = $true
        receipt = $receiptPath
    } | ConvertTo-Json -Depth 4
} catch {
    $receipt.error = $_.Exception.Message
    Save-Receipt
    throw
}
