<#
.SYNOPSIS
Close the six owner-approved workflow tickets and synchronize their ContextCompass records.
.DESCRIPTION
The file and directory allowlists are fixed. Refuse existing destinations, unexpected ticket
ownership, reparse points, or concurrent board changes. Archive patch bytes unchanged, remove
only the two delete-on-close scratch roots, and retain a JSON disposition report.
#>
throw 'Disabled: automatic approval review rejected this combined cleanup. Use the records-only procedure.'
$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath 'C:\Users\Mark\PycharmProjects\melder_private').Path
$compass = Join-Path $workspace 'context_compass'
$when = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$nl = [string][char]10
$reportPath = Join-Path $PSScriptRoot 'closure_report.json'
$ticketNames = @(
    '2026-09-06_ci_validation_stage_design_task.md',
    '2026-09-08_reproducible_uv_environment_task.md',
    '2026-09-13_sync_owner_uv_environment_task.md',
    '2026-09-19_document_positional_meld_calls_task.md',
    '2026-09-20_teach_meld_string_names_task.md',
    '2026-09-20_transfer_workflows_1_responsibility_task.md'
)
$workItems = @(
    'ci_validation_stage_design', 'reproducible_uv_environment', 'sync_owner_uv_environment',
    'document_positional_meld_calls', 'teach_meld_string_names', 'workflows_responsibility_transfer'
)
$patchNames = @('ci_stage_qualification_2026_09_06', 'uv_environment_2026_09_08')
$report = [ordered]@{
    completed_at = $when
    tickets = @()
    patch_archives = @()
    deleted_scratch = @()
    cleared_artifact_rows = 0
    verification = $null
    error = $null
}

function Save-Report {
    # Persist each completed operation so an interrupted closeout can be inspected without guessing.
    [IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json -Depth 10) + $nl,
        [Text.UTF8Encoding]::new($false))
}

function Assert-ContainedPath([string]$Path, [string]$Boundary) {
    # Never recursively mutate a path outside the exact repository lane selected by the caller.
    $absolute = [IO.Path]::GetFullPath($Path)
    $prefix = [IO.Path]::GetFullPath($Boundary).TrimEnd('\') + '\'
    if (-not $absolute.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escapes the allowed lane: $absolute"
    }
    return $absolute
}

function Get-SafeEntries([string]$Path, [string]$Boundary) {
    # Reject root and descendant reparse points before any recursive deletion or directory move.
    $absolute = Assert-ContainedPath $Path $Boundary
    $root = Get-Item -LiteralPath $absolute -Force
    if ($root.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw "Reparse root is not permitted: $absolute"
    }
    $entries = @(Get-ChildItem -LiteralPath $absolute -Recurse -Force)
    if (@($entries | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) {
        throw "Reparse descendants are not permitted: $absolute"
    }
    return $entries
}

function Write-UnchangedFile([string]$Path, [string]$Original, [string]$Replacement) {
    # Compare against the current bytes immediately before writing; never overwrite a newer board edit.
    $current = Get-Content -LiteralPath $Path -Raw
    if ($current -cne $Original) { throw "Concurrent edit detected: $Path" }
    [IO.File]::WriteAllText($Path, $Replacement, [Text.UTF8Encoding]::new($false))
}

function Rewrite-LiveReferences([string]$Content) {
    # Move only the selected canonical ticket and patch pointers; preserve historical prose.
    foreach ($name in $ticketNames) {
        $Content = $Content.Replace("tickets/tasks/$name", "tickets/tasks/completed/$name")
    }
    foreach ($name in $patchNames) {
        $Content = $Content.Replace("patches/active/$name/", "patches/completed/$name/")
    }
    return $Content
}

function Archive-PatchLane([string]$Name) {
    # Move the complete document/index pair set and prove every destination retains its original hash.
    if ($Name -notin $patchNames) { throw "Patch is outside the closure allowlist: $Name" }
    $source = Assert-ContainedPath (Join-Path $compass "system_docs/patches/active/$Name") $compass
    $destination = Assert-ContainedPath (Join-Path $compass "system_docs/patches/completed/$Name") $compass
    if (Test-Path -LiteralPath $destination) { throw "Archive already exists: $destination" }
    $entries = @(Get-SafeEntries $source (Join-Path $compass 'system_docs/patches/active'))
    $hashes = @($entries | Where-Object { -not $_.PSIsContainer } | ForEach-Object {
        [pscustomobject]@{
            relative_path = $_.FullName.Substring($source.Length + 1)
            sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
        }
    })
    Move-Item -LiteralPath $source -Destination $destination
    foreach ($item in $hashes) {
        $actual = (Get-FileHash -LiteralPath (Join-Path $destination $item.relative_path) -Algorithm SHA256).Hash
        if ($actual -cne $item.sha256) { throw "Archive hash mismatch: $($item.relative_path)" }
    }
    $report.patch_archives += [ordered]@{
        source = $source; destination = $destination; files = $hashes; hashes_preserved = $true
    }
    Save-Report
}

function Remove-TaskScratch([string]$Name) {
    # Apply the tickets' explicit delete_on_close disposition to the two verified disposable roots.
    if ($Name -notin @('ci_stage_qualification_20260906', 'uv_environment_20260908')) {
        throw "Scratch directory is outside the closure allowlist: $Name"
    }
    $boundary = Join-Path $compass 'artifacts'
    $path = Assert-ContainedPath (Join-Path $boundary $Name) $boundary
    $entries = @(Get-SafeEntries $path $boundary)
    $files = @($entries | Where-Object { -not $_.PSIsContainer })
    $bytes = ($files | Measure-Object Length -Sum).Sum
    Remove-Item -LiteralPath $path -Recurse -Force
    if (Test-Path -LiteralPath $path) { throw "Scratch root remains: $path" }
    $report.deleted_scratch += [ordered]@{path = $path; files = $files.Count; bytes = $bytes}
    Save-Report
}

function Complete-Ticket([string]$Name, [string]$Summary) {
    # Stamp owner-authorized delivery, retain all previous notes, and move into the completed lane.
    if ($Name -notin $ticketNames) { throw "Ticket is outside the closure allowlist: $Name" }
    $source = Assert-ContainedPath (Join-Path $compass "tickets/tasks/$Name") $compass
    $destination = Assert-ContainedPath (Join-Path $compass "tickets/tasks/completed/$Name") $compass
    if (Test-Path -LiteralPath $destination) { throw "Completed ticket already exists: $destination" }
    $original = Get-Content -LiteralPath $source -Raw
    if ($original -notmatch '(?m)^- Agent Name: workflows_0\r?$') {
        throw "Unexpected ticket owner: $Name"
    }
    $state = [regex]::Match($original, '(?m)^- Status: (review|in_progress)\r?$')
    if (-not $state.Success) { throw "Unexpected ticket state: $Name" }
    $content = $original -replace '(?m)^- Status: (review|in_progress)\r?$', '- Status: done'
    $content = $content -replace '(?m)^- Updated: [^\r\n]+', "- Updated: $when"
    $closure = @"

## Owner-Approved Closure
- Completed: $when
- Disposition: delivered
- Summary: $Summary
- Acceptance: Owner directed completing finished inherited work on 2026-09-20.
- Validation: Existing recorded results support delivery; no fresh runtime or hosted test claim.
- Historical plans, review/rollout NEXT entries and earlier handoff text below are retained as history.
- Closeout record: tickets/tasks/completed/2026-09-20_transfer_workflows_1_responsibility_task.md
- Artifact handling: retained evidence stays linked; disposable CI/uv workspaces were removed.
  Patch contracts and indexes are archived intact; durable guidance remains in the repository.

"@
    $content = $content.Replace('## Metadata', $closure + $nl + '## Metadata')
    $transition = @"
## State Transition Event
- from_state: $($state.Groups[1].Value)
- to_state: done
- transition_reason: Owner-authorized closure of delivered work with recorded validation and board sync.
"@
    $content = [regex]::Replace($content,
        '(?s)## State Transition Event\r?\n.*?(?=\r?\n## )', $transition + $nl, 1)
    $validationSection = [regex]::Match($content,
        '(?s)## Validation\r?\n.*?(?=\r?\n## )')
    if (-not $validationSection.Success) { throw "Missing validation record: $Name" }
    $validationStart = $content.Substring(0, $validationSection.Index).Split([char]10).Count
    $validationEnd = $validationStart + $validationSection.Value.Split([char]10).Count - 1
    $note = @"
- DATETIME: $when
  TYPE: DECISION
  CLAIM: Owner authorizes completion of this delivered item. $Summary
    Earlier test results and hosted-run limits remain dated evidence; no new execution is implied.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/$($Name):$($validationStart)-$($validationEnd)
  - context_compass/tickets/tasks/completed/$($Name):1-16
  IMPACT: Ticket is done and removed from active routing; ongoing responsibility remains workflows_0's.
  NEXT: none; new failures or work requests receive their own scoped follow-up.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

"@
    $content = $content.Replace('## Context / Handoff Summary', $note + $nl + '## Context / Handoff Summary')
    $content = Rewrite-LiveReferences $content
    if ($Name -eq '2026-09-20_transfer_workflows_1_responsibility_task.md') {
        $content = $content.Replace('- [ ] Owner acceptance is recorded before archival.',
            '- [x] Owner acceptance is recorded before archival.')
    }
    Write-UnchangedFile $source $original $content
    Move-Item -LiteralPath $source -Destination $destination
    $report.tickets += [ordered]@{name = $Name; source = $source; destination = $destination; status = 'done'}
    Save-Report
}

function Replace-Region([string]$Content, [string]$Region, [string[]]$Rows) {
    # Replace one user-owned region only; managed text, headers and unrelated regions remain byte-stable.
    $pattern = '(?s)(<!-- BEGIN USER-DEFINED: ' + [regex]::Escape($Region) +
        ' -->\r?\n)(.*?)(<!-- END USER-DEFINED: ' + [regex]::Escape($Region) + ' -->)'
    $match = [regex]::Match($Content, $pattern)
    if (-not $match.Success) { throw "Missing region: $Region" }
    $replacement = $match.Groups[1].Value + ($Rows -join $nl) + $nl + $match.Groups[3].Value
    return $Content.Substring(0, $match.Index) + $replacement + $Content.Substring($match.Index + $match.Length)
}

try {
    foreach ($name in $ticketNames) {
        if (-not (Test-Path -LiteralPath (Join-Path $compass "tickets/tasks/$name"))) {
            throw "Missing active ticket: $name"
        }
        if (Test-Path -LiteralPath (Join-Path $compass "tickets/tasks/completed/$name")) {
            throw "Refusing overwrite of completed ticket: $name"
        }
    }
    Save-Report
    Archive-PatchLane 'ci_stage_qualification_2026_09_06'
    Archive-PatchLane 'uv_environment_2026_09_08'
    Remove-TaskScratch 'ci_stage_qualification_20260906'
    Remove-TaskScratch 'uv_environment_20260908'

    Complete-Ticket '2026-09-06_ci_validation_stage_design_task.md' 'CI stages, no-GIL matrix and coverage corrections delivered.'
    Complete-Ticket '2026-09-08_reproducible_uv_environment_task.md' 'Reproducible uv setup and matrix-aware locked CI delivered.'
    Complete-Ticket '2026-09-13_sync_owner_uv_environment_task.md' 'Existing environment synchronized and package preservation verified.'
    Complete-Ticket '2026-09-19_document_positional_meld_calls_task.md' 'Positional meld documentation and cache-reset follow-up completed.'
    Complete-Ticket '2026-09-20_teach_meld_string_names_task.md' 'Quoted-name examples corrected and publication checks completed.'
    Complete-Ticket '2026-09-20_transfer_workflows_1_responsibility_task.md' 'Ownership transferred and all five delivered inherited tasks closed.'

    $attentionPath = Join-Path $compass 'attention_board.md'
    $attentionOriginal = Get-Content -LiteralPath $attentionPath -Raw
    $ticketPattern = ($ticketNames | ForEach-Object { [regex]::Escape($_) }) -join '|'
    $attention = [regex]::Replace($attentionOriginal,
        '(?m)^\|[^\r\n]*tickets/tasks/(' + $ticketPattern + ')[^\r\n]*\r?\n', '')
    $workPattern = ($workItems | ForEach-Object { [regex]::Escape($_) }) -join '|'
    $attention = [regex]::Replace($attention,
        '(?m)^- (' + $workPattern + '):[^\r\n]*\r?\n(?:[ \t]+[^\r\n]*\r?\n)*', '')
    $closedMatch = [regex]::Match($attention,
        '(?s)<!-- BEGIN USER-DEFINED: closed_anchors -->\r?\n(.*?)<!-- END USER-DEFINED: closed_anchors -->')
    $previous = @($closedMatch.Groups[1].Value -split '\r?\n' | Where-Object { $_.StartsWith('| ') })
    $newAnchors = @($ticketNames | ForEach-Object {
        $stem = [IO.Path]::GetFileNameWithoutExtension($_)
        "| $stem | done | workflows_0 | tickets/tasks/completed/$_ | Owner-authorized completion; evidence and artifact disposition recorded. | $when |"
    })
    $attention = Replace-Region $attention 'closed_anchors' @(($newAnchors + $previous) | Select-Object -First 12)
    Write-UnchangedFile $attentionPath $attentionOriginal $attention

    $artifactPath = Join-Path $compass 'artifact_board.md'
    $artifactOriginal = Get-Content -LiteralPath $artifactPath -Raw
    $activeMatch = [regex]::Match($artifactOriginal,
        '(?s)<!-- BEGIN USER-DEFINED: active_artifacts -->\r?\n(.*?)<!-- END USER-DEFINED: active_artifacts -->')
    $keptRows = [Collections.Generic.List[string]]::new()
    $clearedRows = [Collections.Generic.List[string]]::new()
    foreach ($row in ($activeMatch.Groups[1].Value -split '\r?\n')) {
        if (-not $row.StartsWith('| ')) { continue }
        $cells = $row.Split('|')
        $ticket = $cells[1].Trim()
        if ($ticket -notmatch '^tickets/tasks/(' + $ticketPattern + ')$') {
            $keptRows.Add($row)
            continue
        }
        $path = Rewrite-LiveReferences $cells[2].Trim()
        $disposition = $cells[5].Trim()
        $closedTicket = Rewrite-LiveReferences $ticket
        $reason = switch ($disposition) {
            'delete_on_close' { 'Task-owned temporary files removed; validation retained in completed ticket.' }
            'promote_to_documentation' { 'Durable guidance verified; original patch documents and indexes archived intact.' }
            'retain_as_reference' { 'Owner-authorized completion; dated evidence retained as reference.' }
            default { throw "Unknown artifact disposition: $disposition" }
        }
        $clearedRows.Add("| $closedTicket | $path | $disposition | $reason | $when |")
    }
    $artifact = Replace-Region $artifactOriginal 'active_artifacts' $keptRows.ToArray()
    $clearedMarker = '<!-- BEGIN USER-DEFINED: cleared_artifacts -->'
    $artifact = $artifact.Replace($clearedMarker,
        $clearedMarker + $nl + ($clearedRows -join $nl))
    Write-UnchangedFile $artifactPath $artifactOriginal $artifact
    $report.cleared_artifact_rows = $clearedRows.Count

    $mailboxPath = Join-Path $compass 'mailbox_board.md'
    $mailboxOriginal = Get-Content -LiteralPath $mailboxPath -Raw
    $mailbox = Rewrite-LiveReferences $mailboxOriginal
    $mailbox = [regex]::Replace($mailbox,
        '(?m)^(\| workflows_0 \| codex \| [^|]+ \| )[^|]+( \| active \|)\r?$',
        ('$' + '{1}' + $when + '$' + '{2}'))
    Write-UnchangedFile $mailboxPath $mailboxOriginal $mailbox

    $report.verification = [ordered]@{
        completed_tickets = $report.tickets.Count
        archived_patch_files = @($report.patch_archives | ForEach-Object { $_.files }).Count
        selected_active_routes_remaining = [regex]::Matches($attention,
            'tickets/tasks/(' + $ticketPattern + ')').Count
        selected_active_artifact_rows_remaining = @($keptRows | Where-Object {
            $_ -match 'tickets/tasks/(' + $ticketPattern + ')'
        }).Count
        closed_anchor_count = @($newAnchors + $previous | Select-Object -First 12).Count
    }
    Save-Report
    $report | ConvertTo-Json -Depth 10
}
catch {
    $report.error = $_.Exception.Message
    Save-Report
    throw
}
