<#
.SYNOPSIS
Apply the owner's completion instruction to five delivered workflow tickets.
.DESCRIPTION
Changes only ticket and board records and moves five Markdown files to completed.
Does not delete artifacts, move patch directories, execute source, or publish anything.
The rejected destructive cleanup remains blocked in the existing closeout task.
#>
$ErrorActionPreference = 'Stop'
$root = 'C:\Users\Mark\PycharmProjects\melder_private\context_compass'
$when = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$nl = [string][char]10
$names = @(
    '2026-09-06_ci_validation_stage_design_task.md',
    '2026-09-08_reproducible_uv_environment_task.md',
    '2026-09-13_sync_owner_uv_environment_task.md',
    '2026-09-19_document_positional_meld_calls_task.md',
    '2026-09-20_teach_meld_string_names_task.md'
)
$cleanupTicket = 'tickets/tasks/2026-09-20_transfer_workflows_1_responsibility_task.md'
$reportPath = Join-Path $PSScriptRoot 'records_only_report.json'
$report = [ordered]@{completed_at=$when; completed_tickets=@(); deleted_artifacts=0; moved_patch_directories=0; cleanup_status='blocked_pending_explicit_approval'; error=$null}

function Write-Current([string]$Path, [string]$Original, [string]$Content) {
    # Refuse a concurrent edit rather than overwrite another agent's current record.
    if ((Get-Content -LiteralPath $Path -Raw) -cne $Original) { throw "Concurrent edit: $Path" }
    [IO.File]::WriteAllText($Path, $Content, [Text.UTF8Encoding]::new($false))
}
function Fix-TicketPointers([string]$Content) {
    # Update only the five moved ticket paths; artifact and patch paths remain unchanged.
    foreach ($name in $names) {
        $Content = $Content.Replace("tickets/tasks/$name", "tickets/tasks/completed/$name")
    }
    return $Content
}
function Finish-Ticket([string]$Name) {
    # Mark one previously read, delivered ticket done and move its Markdown record without overwriting.
    if ($Name -notin $names) { throw "Ticket outside allowlist: $Name" }
    $source = [IO.Path]::GetFullPath((Join-Path $root "tickets/tasks/$Name"))
    $destination = [IO.Path]::GetFullPath((Join-Path $root "tickets/tasks/completed/$Name"))
    if (-not $source.StartsWith($root + '\tickets\tasks\') -or
        -not $destination.StartsWith($root + '\tickets\tasks\completed\')) { throw 'Ticket path escapes scope.' }
    if (Test-Path -LiteralPath $destination) { throw "Completed record already exists: $Name" }
    $original = Get-Content -LiteralPath $source -Raw
    if ($original -notmatch '(?m)^- Agent Name: workflows_0\r?$' -or
        $original -notmatch '(?m)^- Status: review\r?$') { throw "Unexpected ticket metadata: $Name" }
    $content = $original -replace '(?m)^- Status: review\r?$', '- Status: done'
    $content = $content -replace '(?m)^- Updated: [^\r\n]+', "- Updated: $when"
    $closure = @"
## Owner-Approved Completion
- Completed: $when
- Summary: Recorded implementation and validation are complete; owner directed marking finished work done.
- Acceptance: Owner instruction on 2026-09-20.
- Validation: Prior recorded results retained; no new runtime or hosted test run is claimed.
- Artifact cleanup: deferred to $cleanupTicket.
  Files remain in place because automatic approval review requires explicit deletion approval.
- Earlier review/rollout NEXT statements and the previous handoff below are historical context.

"@
    $content = $content.Replace('## Metadata', $closure + $nl + '## Metadata')
    $transition = @"
## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner-authorized completion of delivered work; artifact cleanup tracked separately.
"@
    $content = [regex]::Replace($content,
        '(?s)## State Transition Event\r?\n.*?(?=\r?\n## )', $transition + $nl)
    $validation = [regex]::Match($content, '(?s)## Validation\r?\n.*?(?=\r?\n## )')
    if (-not $validation.Success) { throw "Validation record missing: $Name" }
    $first = $content.Substring(0, $validation.Index).Split([char]10).Count
    $last = $first + $validation.Value.Split([char]10).Count - 1
    $note = @"
- DATETIME: $when
  TYPE: DECISION
  CLAIM: Owner authorizes marking this delivered work completed. Prior validation supports the
    implementation result; destructive artifact cleanup remains a separately tracked approval blocker.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/$($Name):$first-$last
  - context_compass/tickets/tasks/completed/$($Name):1-11
  IMPACT: Implementation ticket is done. No artifact deletion or new test execution is implied.
  NEXT: none for implementation; cleanup remains in the linked closeout task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

"@
    $content = $content.Replace('## Context / Handoff Summary', $note + $nl + '## Context / Handoff Summary')
    $content = Fix-TicketPointers $content
    Write-Current $source $original $content
    Move-Item -LiteralPath $source -Destination $destination
    $report.completed_tickets += "tickets/tasks/completed/$Name"
    [IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json -Depth 5) + $nl)
}

try {
    Finish-Ticket '2026-09-06_ci_validation_stage_design_task.md'
    Finish-Ticket '2026-09-08_reproducible_uv_environment_task.md'
    Finish-Ticket '2026-09-13_sync_owner_uv_environment_task.md'
    Finish-Ticket '2026-09-19_document_positional_meld_calls_task.md'
    Finish-Ticket '2026-09-20_teach_meld_string_names_task.md'

    $pattern = ($names | ForEach-Object { [regex]::Escape($_) }) -join '|'
    $attentionPath = Join-Path $root 'attention_board.md'
    $attentionOriginal = Get-Content -LiteralPath $attentionPath -Raw
    $attention = [regex]::Replace($attentionOriginal,
        '(?m)^\|[^\r\n]*tickets/tasks/(' + $pattern + ')[^\r\n]*\r?\n', '')
    $workItems = 'ci_validation_stage_design|reproducible_uv_environment|sync_owner_uv_environment|document_positional_meld_calls|teach_meld_string_names'
    $attention = [regex]::Replace($attention,
        '(?m)^- (' + $workItems + '):[^\r\n]*\r?\n(?:[ \t]+[^\r\n]*\r?\n)*', '')
    $newRoute = "| workflows_responsibility_transfer | blocked | handoff | codex | workflows_0 | Explicit artifact-deletion approval required. | Owner decides on deleting the two disposable CI/uv roots. | Five implementation tickets are completed; cleanup is separately recorded. | Artifact cleanup is authorized or retention is directed. | $cleanupTicket | $when | REQUIRED |"
    $attention = [regex]::Replace($attention,
        '(?m)^\| workflows_responsibility_transfer \|[^\r\n]*', $newRoute)
    $attention = [regex]::Replace($attention,
        '(?m)^- workflows_responsibility_transfer:[^\r\n]*',
        '- workflows_responsibility_transfer: SWITCH_TRIGGER is explicit artifact cleanup or retention direction.')
    $anchors = [regex]::Match($attention,
        '(?s)(<!-- BEGIN USER-DEFINED: closed_anchors -->\r?\n)(.*?)(<!-- END USER-DEFINED: closed_anchors -->)')
    if (-not $anchors.Success) { throw 'Closed-anchor region missing.' }
    $oldRows = @($anchors.Groups[2].Value -split '\r?\n' | Where-Object { $_.StartsWith('| ') })
    $newRows = @($names | ForEach-Object {
        "| $([IO.Path]::GetFileNameWithoutExtension($_)) | done | workflows_0 | tickets/tasks/completed/$_ | Owner-authorized completion; cleanup tracked separately. | $when |"
    })
    $body = (@(($newRows + $oldRows) | Select-Object -First 12) -join $nl) + $nl
    $attention = $attention.Substring(0, $anchors.Index) + $anchors.Groups[1].Value +
        $body + $anchors.Groups[3].Value + $attention.Substring($anchors.Index + $anchors.Length)
    Write-Current $attentionPath $attentionOriginal $attention

    $artifactPath = Join-Path $root 'artifact_board.md'
    $artifactOriginal = Get-Content -LiteralPath $artifactPath -Raw
    $active = [regex]::Match($artifactOriginal,
        '(?s)(<!-- BEGIN USER-DEFINED: active_artifacts -->\r?\n)(.*?)(<!-- END USER-DEFINED: active_artifacts -->)')
    if (-not $active.Success) { throw 'Active-artifact region missing.' }
    $kept = [Collections.Generic.List[string]]::new()
    $cleared = [Collections.Generic.List[string]]::new()
    foreach ($row in ($active.Groups[2].Value -split '\r?\n')) {
        if (-not $row.StartsWith('| ')) { continue }
        $cells = $row.Split('|')
        $ticket = $cells[1].Trim()
        if ($ticket -notmatch ('^tickets/tasks/(' + $pattern + ')$')) { $kept.Add($row); continue }
        $artifact = $cells[2].Trim()
        $disposition = $cells[5].Trim()
        if ($disposition -eq 'retain_as_reference') {
            $closedTicket = Fix-TicketPointers $ticket
            $cleared.Add("| $closedTicket | $artifact | retain_as_reference | Completed delivery; dated evidence retained. | $when |")
        } else {
            $kind = $cells[3].Trim()
            $kept.Add("| $cleanupTicket | $artifact | $kind | blocked | $disposition | Preserved in place pending explicit cleanup authorization. | $when | HELPFUL |")
        }
    }
    $artifactContent = $artifactOriginal.Substring(0, $active.Index) + $active.Groups[1].Value +
        ($kept -join $nl) + $nl + $active.Groups[3].Value +
        $artifactOriginal.Substring($active.Index + $active.Length)
    $marker = '<!-- BEGIN USER-DEFINED: cleared_artifacts -->'
    $artifactContent = $artifactContent.Replace($marker, $marker + $nl + ($cleared -join $nl))
    Write-Current $artifactPath $artifactOriginal $artifactContent

    $mailPath = Join-Path $root 'mailbox_board.md'
    $mailOriginal = Get-Content -LiteralPath $mailPath -Raw
    Write-Current $mailPath $mailOriginal (Fix-TicketPointers $mailOriginal)
    $cleanupPath = Join-Path $root $cleanupTicket
    $cleanupOriginal = Get-Content -LiteralPath $cleanupPath -Raw
    Write-Current $cleanupPath $cleanupOriginal (Fix-TicketPointers $cleanupOriginal)
    $report.selected_active_routes_remaining = [regex]::Matches($attention, 'tickets/tasks/(' + $pattern + ')').Count
    $report.retained_evidence_rows_closed = $cleared.Count
    [IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json -Depth 5) + $nl)
    $report | ConvertTo-Json -Depth 5
} catch {
    $report.error = $_.Exception.Message
    [IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json -Depth 5) + $nl)
    throw
}
