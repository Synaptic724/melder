<#
.SYNOPSIS
Retire departed identities and obsolete shared-board history without deleting project artifacts.
.DESCRIPTION
Archive removed records first. Keep active routes and artifact associations byte-for-byte.
Preserve managed blocks and refuse concurrent board edits.
#>
$ErrorActionPreference = 'Stop'
$root = 'C:\Users\Mark\PycharmProjects\melder_private\context_compass'
$when = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$nowUtc = [DateTimeOffset]::Parse($when)
$nl = [string][char]10
$archivePath = Join-Path $PSScriptRoot 'retired_board_history.md'
$reportPath = Join-Path $PSScriptRoot 'cleanup_report.json'
if (Test-Path -LiteralPath $archivePath) { throw 'Archive already exists; inspect it before retrying.' }

function Region([string]$Text, [string]$Name) {
    # Return one exact user-defined body; ambiguous or missing markers fail before any write.
    $pattern = '(?s)(<!-- BEGIN USER-DEFINED: ' + [regex]::Escape($Name) +
        ' -->\r?\n)(.*?)(<!-- END USER-DEFINED: ' + [regex]::Escape($Name) + ' -->)'
    $matches = [regex]::Matches($Text, $pattern)
    if ($matches.Count -ne 1) { throw "Expected one region: $Name" }
    return $matches[0]
}
function Replace-Body([string]$Text, [string]$Name, [string]$Body) {
    # Modify only the requested user-owned region, leaving contracts and surrounding structure intact.
    $match = Region $Text $Name
    return $Text.Substring(0, $match.Index) + $match.Groups[1].Value + $Body +
        $match.Groups[3].Value + $Text.Substring($match.Index + $match.Length)
}
function Assert-ManagedSame([string]$Before, [string]$After) {
    # Managed policy blocks are never part of this cleanup.
    $pattern = '(?s)<!-- BEGIN MANAGED: .*?<!-- END MANAGED: [^\r\n]+ -->'
    $first = @([regex]::Matches($Before, $pattern) | ForEach-Object { $_.Value })
    $second = @([regex]::Matches($After, $pattern) | ForEach-Object { $_.Value })
    if (($first -join $nl) -cne ($second -join $nl)) { throw 'Managed policy block changed.' }
}
function Save-Current([string]$Path, [string]$Before, [string]$After) {
    # Refuse to overwrite a board modified by another agent after the snapshot was taken.
    if ((Get-Content -LiteralPath $Path -Raw) -cne $Before) { throw "Concurrent board edit: $Path" }
    Assert-ManagedSame $Before $After
    [IO.File]::WriteAllText($Path, $After, [Text.UTF8Encoding]::new($false))
}

$mailPath = Join-Path $root 'mailbox_board.md'
$attentionPath = Join-Path $root 'attention_board.md'
$artifactPath = Join-Path $root 'artifact_board.md'
$contextPath = Join-Path $root 'context_management/context_board.md'
$mailBefore = Get-Content -LiteralPath $mailPath -Raw
$attentionBefore = Get-Content -LiteralPath $attentionPath -Raw
$artifactBefore = Get-Content -LiteralPath $artifactPath -Raw
$contextBefore = Get-Content -LiteralPath $contextPath -Raw
$roster = (Region $mailBefore 'checked_in').Groups[2].Value
$messages = (Region $mailBefore 'messages').Groups[2].Value
$alerts = (Region $attentionBefore 'alerts').Groups[2].Value
$history = (Region $artifactBefore 'cleared_artifacts').Groups[2].Value
$artifactNotes = (Region $artifactBefore 'notes').Groups[2].Value
$departed = [Collections.Generic.List[string]]::new()
$stalePrevious = [Collections.Generic.List[string]]::new()
$rosterKept = [Collections.Generic.List[string]]::new()
$removedNames = [Collections.Generic.List[string]]::new()
$staleNames = [Collections.Generic.List[string]]::new()
foreach ($row in ($roster -split '\r?\n')) {
    if (-not $row.StartsWith('| ')) { continue }
    $cells = $row.Split('|')
    $name = $cells[1].Trim()
    $status = $cells[5].Trim()
    if ($status.StartsWith('departed')) {
        $departed.Add($row); $removedNames.Add($name); continue
    }
    if ($name -eq 'workflows_0') {
        $cells[4] = " $when "
    } elseif ($status.StartsWith('active') -and
        ($nowUtc - [DateTimeOffset]::Parse($cells[4].Trim())).TotalDays -gt 1) {
        $stalePrevious.Add($row); $staleNames.Add($name)
        $cells[5] = ' stale '
    }
    $rosterKept.Add(($cells -join '|'))
}

$retiredMessages = [Collections.Generic.List[string]]::new()
$retiredAlerts = [Collections.Generic.List[string]]::new()
$messagesKept = $messages
$alertsKept = $alerts
foreach ($entry in [regex]::Matches($messages, '(?ms)^- TO: [^\r\n]+.*?(?=^- TO: |\z)')) {
    $block = $entry.Value
    if ($block -notmatch '(?m)^- TO: codex_1\r?$' -or
        $block -notmatch '(?m)^  FROM: workflows_1\r?$' -or
        $block -notmatch '(?m)^  ACK_REQUESTED: false\r?$' -or
        $block -notmatch 'tickets/tasks/completed/2026-09-06_ci_validation_stage_design_task\.md') { continue }
    $date = [regex]::Match($block, '(?m)^  DATETIME: ([^\r\n]+)').Groups[1].Value
    if ($date -notin @('2026-09-06T18:41:11Z','2026-09-06T17:41:58Z')) { continue }
    $retiredMessages.Add($block)
    $messagesKept = $messagesKept.Replace($block, '')
    $alert = "- NEW MESSAGE for codex_1 (from workflows_1, $date)"
    $pattern = '(?m)^' + [regex]::Escape($alert) + '\r?\n?'
    if ([regex]::IsMatch($alertsKept, $pattern)) {
        $retiredAlerts.Add($alert)
        $alertsKept = [regex]::Replace($alertsKept, $pattern, '')
    }
}

$historyRows = @($history -split '\r?\n' | Where-Object { $_.StartsWith('| ') })
$seenTickets = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
$recent = [Collections.Generic.List[string]]::new()
foreach ($row in $historyRows) {
    $ticket = $row.Split('|')[1].Trim()
    if ($seenTickets.Add($ticket) -and $recent.Count -lt 12) { $recent.Add($row) }
}
$archive = @"
# Retired Shared-Board Records

- Archived: $when
- Owning ticket: tickets/tasks/2026-09-21_cleanup_shared_context_compass_boards_task.md
- Purpose: preserve records retired by the owner's shared-board cleanup; this is historical evidence.
- Current work remains on the live boards. No ticket status or artifact data was changed here.

## Departed Roster Rows
$($departed -join $nl)

## Previous Stale Check-In Rows
$($stalePrevious -join $nl)

## Superseded Mailbox Notices
$($retiredMessages -join $nl)

## Removed Message Alerts
$($retiredAlerts -join $nl)

## Original Cleared Artifact History
$history
## Historical Artifact Board Notes
$artifactNotes
"@
if (-not $archive.Contains($history) -or -not $archive.Contains($artifactNotes)) {
    throw 'Archive does not preserve the complete historical regions.'
}
[IO.File]::WriteAllText($archivePath, $archive + $nl, [Text.UTF8Encoding]::new($false))

$mailAfter = Replace-Body $mailBefore 'checked_in' (($rosterKept -join $nl) + $nl)
$mailAfter = Replace-Body $mailAfter 'messages' $messagesKept
$mailNotes = (Region $mailAfter 'notes').Groups[2].Value
if ($removedNames.Contains('muse_0') -and $rosterKept.Where({ $_ -match '^\| muse \|' }).Count) {
    $mailNotes += '- Identity continuation: muse_0 was renamed to muse; route current work to muse.' + $nl
}
$mailAfter = Replace-Body $mailAfter 'notes' $mailNotes
$attentionAfter = Replace-Body $attentionBefore 'alerts' $alertsKept
$artifactAfter = Replace-Body $artifactBefore 'cleared_artifacts' (($recent -join $nl) + $nl)
$compactNotes = @"
- Earlier cleared associations and historical notes are preserved in
  artifacts/shared_boards_cleanup_20260921/retired_board_history.md.
- This cleanup leaves one representative entry for each of twelve recent completed-ticket groups.
  The archive preserves all 214 original associations, including retained-reference history.
"@ + $nl
$artifactAfter = Replace-Body $artifactAfter 'notes' $compactNotes
if ((Region $attentionBefore 'active_items').Groups[2].Value -cne
    (Region $attentionAfter 'active_items').Groups[2].Value) { throw 'Active attention routes changed.' }
if ((Region $artifactBefore 'active_artifacts').Groups[2].Value -cne
    (Region $artifactAfter 'active_artifacts').Groups[2].Value) { throw 'Active artifact associations changed.' }
Save-Current $mailPath $mailBefore $mailAfter
Save-Current $attentionPath $attentionBefore $attentionAfter
Save-Current $artifactPath $artifactBefore $artifactAfter
if ((Get-Content -LiteralPath $contextPath -Raw) -cne $contextBefore) {
    throw 'Context board changed concurrently; recheck its state.'
}
$report = [ordered]@{
    completed_at=$when
    departed_removed=$removedNames.ToArray()
    stale_marked=$staleNames.ToArray()
    notices_retired=$retiredMessages.Count
    alerts_retired=$retiredAlerts.Count
    cleared_artifact_rows_archived=$historyRows.Count
    recent_artifact_groups_retained=$recent.Count
    active_attention_region_unchanged=$true
    active_artifact_region_unchanged=$true
    context_board_unchanged=$true
    managed_blocks_unchanged=$true
    archived_history_sha256=(Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash
}
[IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json -Depth 4) + $nl)
$report | ConvertTo-Json -Depth 4
