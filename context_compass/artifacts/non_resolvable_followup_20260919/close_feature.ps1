param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath 'C:/Users/Mark/PycharmProjects/melder_private').Path
$compass = Join-Path $workspace 'context_compass'
$stamp = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
$utf8 = [System.Text.UTF8Encoding]::new($false)

# This explicit selection is the owner's completed feature and its repair, not a repository sweep.
$selected = @(
    'tasks/2026-09-19_fix_feature_turn_in_failures_task.md'
    'epics/2026-09-19_discoverable_non_resolvable_registrations_epic.md'
    'stories/2026-09-19_discoverable_registration_contract_discovery_story.md'
    'stories/2026-09-19_discoverable_registration_modifier_story.md'
    'stories/2026-09-19_caller_supplied_socket_compiler_story.md'
    'stories/2026-09-19_discoverable_resolution_runtime_story.md'
    'stories/2026-09-19_discoverable_nexus_graph_and_history_story.md'
    'stories/2026-09-19_discoverable_registration_persistence_story.md'
    'stories/2026-09-19_discoverable_registration_qualification_story.md'
    'tasks/2026-09-19_publish_and_replay_non_resolvable_definitions_task.md'
    'tasks/2026-09-19_enforce_non_resolvable_runtime_admission_task.md'
    'tasks/2026-09-19_enforce_required_override_execution_task.md'
    'tasks/2026-09-19_implement_override_required_compiler_task.md'
    'tasks/2026-09-19_implement_resolvable_registration_modifier_task.md'
    'tasks/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md'
    'tasks/2026-09-19_define_caller_supplied_socket_contract_task.md'
    'tasks/2026-09-19_define_discoverable_registration_selection_task.md'
    'tasks/2026-09-19_define_non_resolvable_admission_identity_task.md'
)
$patchIds = @(
    'discoverable_registration_modifier_2026_09_19'
    'override_required_compiler_2026_09_19'
    'non_resolvable_runtime_admission_2026_09_19'
    'non_resolvable_graph_replay_2026_09_19'
    'local_phase_cancellation_2026_09_19'
)
$summaries = @{
    'fix_feature_turn_in_failures' = 'Fixed crystal fixture capability and stale local cancellation; 394 distinct passes and 25 churn runs.'
    'discoverable_non_resolvable_registrations' = 'Delivered default-True registration policy, compiler/runtime refusal, Nexus graph/history and safe crystal replay.'
    'discoverable_registration_contract_discovery' = 'Accepted the registration, socket, selection and identity discovery contract used by the delivered feature.'
    'discoverable_registration_modifier' = 'Delivered native immutable per-version resolvable policy with compatible True identities and distinct False identities.'
    'caller_supplied_socket_compiler' = 'Delivered OVERRIDE_REQUIRED reference metadata without construction edges and preserved normal provider/default semantics.'
    'discoverable_resolution_runtime' = 'Delivered direct non-resolution admission and verified existing supplied-value and cached execution semantics.'
    'discoverable_nexus_graph_and_history' = 'Delivered ACL-filtered definition/reference/base navigation with existing source, history and version-selection workflows.'
    'discoverable_registration_persistence' = 'Delivered capability capture, active/staged replay and graft with legacy True defaults and record major 2 protection.'
    'discoverable_registration_qualification' = 'Qualified the integrated feature, repaired both owner-reported failures, and synchronized documentation and generated assets.'
    'publish_and_replay_non_resolvable_definitions' = 'Delivered Nexus publication and crystal replay; integrated qualification and final follow-up repairs are retained.'
    'enforce_non_resolvable_runtime_admission' = 'Delivered selected-target refusal across direct/reuse/scoped doors while preserving observational lookup.'
    'enforce_required_override_execution' = 'Verified supplied inputs, omission, reuse and hydration using ordinary Python errors; no new preflight or pruning.'
    'implement_override_required_compiler' = 'Implemented resolved reference-only inputs, executable-root filtering and existing revalidation integration.'
    'implement_resolvable_registration_modifier' = 'Implemented explicit bool transport, per-Spell storage, identity discrimination and registration inspection.'
    'trace_discoverable_registration_compiler_boundary' = 'Completed source-grounded registration ownership and consumer-socket discovery for the accepted implementation.'
    'define_caller_supplied_socket_contract' = 'Defined the accepted OVERRIDE_REQUIRED schema and propagation; later owner direction retained ordinary constructor errors.'
    'define_discoverable_registration_selection' = 'Defined exact lookup, provider/definition matching and descriptor/collection semantics without changing uniqueness.'
    'define_non_resolvable_admission_identity' = 'Defined target admission and capability fingerprints while preserving the owner-selected existing version rules.'
}

function Resolve-CompassTarget([string]$relative) {
    $absolute = [System.IO.Path]::GetFullPath((Join-Path $compass $relative))
    if (-not $absolute.StartsWith($compass + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Target escapes ContextCompass: $relative"
    }
    return $absolute
}

$mapping = [ordered]@{}
foreach ($relative in $selected) {
    $parts = $relative.Split('/')
    $old = 'tickets/' + $relative
    $new = 'tickets/' + $parts[0] + '/completed/' + $parts[1]
    $source = Resolve-CompassTarget $old
    $destination = Resolve-CompassTarget $new
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing ticket: $source" }
    if (Test-Path -LiteralPath $destination) { throw "Destination already exists: $destination" }
    $mapping[$old] = $new
}
$patchMapping = [ordered]@{}
$patchHashes = [ordered]@{}
foreach ($patchId in $patchIds) {
    $old = 'system_docs/patches/active/' + $patchId
    $new = 'system_docs/patches/completed/' + $patchId
    $source = Resolve-CompassTarget $old
    $destination = Resolve-CompassTarget $new
    if (-not (Test-Path -LiteralPath $source -PathType Container)) { throw "Missing patch: $source" }
    if (Test-Path -LiteralPath $destination) { throw "Patch destination exists: $destination" }
    $patchMapping[$old] = $new
    foreach ($file in Get-ChildItem -LiteralPath $source -Recurse -File) {
        $suffix = $file.FullName.Substring($source.Length).Replace('\', '/')
        $patchHashes[$new + $suffix] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    }
}
if (-not $Apply) {
    Write-Output "Ready: $($mapping.Count) tickets, $($patchMapping.Count) patch directories, $($patchHashes.Count) archived files."
    $mapping.GetEnumerator() | ForEach-Object { Write-Output $_.Value }
    exit 0
}

function Update-References([string]$content) {
    foreach ($entry in $mapping.GetEnumerator()) { $content = $content.Replace($entry.Key, $entry.Value) }
    foreach ($entry in $patchMapping.GetEnumerator()) { $content = $content.Replace($entry.Key, $entry.Value) }
    return $content
}

function Write-PreservedText([string]$path, [string]$content, [bool]$crlf) {
    if ($crlf) { $content = $content.Replace("`n", "`r`n") }
    [System.IO.File]::WriteAllText($path, $content, $utf8)
}

foreach ($entry in $mapping.GetEnumerator()) {
    $path = Resolve-CompassTarget $entry.Key
    $original = [System.IO.File]::ReadAllText($path)
    $crlf = $original.Contains("`r`n")
    $content = $original.Replace("`r`n", "`n")
    $oldStatus = [regex]::Match($content, '(?m)^- Status: (.+)$').Groups[1].Value
    if ($oldStatus -notin @('review', 'in_progress')) { throw "Unexpected status $oldStatus in $path" }
    $slug = [System.IO.Path]::GetFileNameWithoutExtension($path) -replace '^2026-09-19_', '' -replace '_(task|story|epic)$', ''
    $summary = $summaries[$slug]
    if (-not $summary) { throw "Missing summary: $slug" }
    $content = [regex]::Replace($content, '(?m)^- Status: .+$', '- Status: done')
    $content = [regex]::Replace($content, '(?m)^- Updated: .+$', '- Updated: ' + $stamp)
    $content = $content.Replace('## Metadata', "## Completion`n- Completed: $stamp`n- Summary: $summary`n- Acceptance: Owner requested turn-in, then required two repairs first; both are verified.`n`n## Metadata")
    $content = [regex]::Replace($content, '(?s)## State Transition Event\n.*?(?=\n## )', "## State Transition Event`n- from_state: $oldStatus`n- to_state: done`n- transition_reason: Owner-authorized turn-in after delivered scope and reported failure repairs passed.`n")
    $notesIndex = $content.IndexOf('## Notes')
    if ($notesIndex -lt 0) { throw "Missing Notes: $path" }
    $content = $content.Substring(0, $notesIndex).Replace('- [ ]', '- [x]') + $content.Substring($notesIndex)
    $content = [regex]::Replace($content, '(?s)(## Closure Confirmation\n)(.*?)(?=\n## |$)', {
        param($match)
        $match.Groups[1].Value + $match.Groups[2].Value.Replace('- [ ]', '- [x]')
    })
    $content = [regex]::Replace($content, '(?m)^(- \[x\] S[1-7]: .+?) — .+$', '$1 — accepted and turned in.')
    $closureNote = @"
- DATETIME: $stamp
  TYPE: DECISION
  CLAIM: Owner-authorized feature turn-in is complete for this record. Both later reported failures
    are repaired: crystal test-double capability and current-run local cancellation forwarding.
    This acceptance retains ordinary Python errors, existing version rules and documented limits.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/validation.md:1-78
  - artifacts/non_resolvable_followup_20260919/validation.md:1-50
  IMPACT: Record is done; validation evidence is retained and promoted patch contracts are archived.
  NEXT: none; reopen only for a new owner-requested change or new failure evidence.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

"@
    $afterNotes = $content.IndexOf("`n## ", $notesIndex + 8)
    if ($afterNotes -lt 0) { throw "Missing section after Notes: $path" }
    $content = $content.Insert($afterNotes, "`n" + $closureNote)
    $content = $content.Replace('## Context / Handoff Summary', "## Context / Handoff Summary`nCLOSED at $stamp. $summary`nFinal evidence and limits are in the graph/replay and follow-up validation artifacts.`nNo next implementation step remains in this accepted record.`n`n### Historical pre-closure handoff")
    $content = Update-References $content
    Write-PreservedText $path $content $crlf
    Move-Item -LiteralPath $path -Destination (Resolve-CompassTarget $entry.Value)
}

foreach ($entry in $patchMapping.GetEnumerator()) {
    Move-Item -LiteralPath (Resolve-CompassTarget $entry.Key) -Destination (Resolve-CompassTarget $entry.Value)
}

# Repair references in the directly related orientation record and retained validation summaries only.
$referenceFiles = @(
    'tickets/tasks/2026-09-19_understand_nexus_crystallizer_spellbook_task.md'
    'artifacts/non_resolvable_graph_replay_20260919/validation.md'
    'artifacts/non_resolvable_runtime_admission_20260919/validation.md'
    'artifacts/override_required_compiler_20260919/validation.md'
    'artifacts/non_resolvable_followup_20260919/validation.md'
)
foreach ($relative in $referenceFiles) {
    $path = Resolve-CompassTarget $relative
    $original = [System.IO.File]::ReadAllText($path)
    $content = Update-References $original.Replace("`r`n", "`n")
    Write-PreservedText $path $content $original.Contains("`r`n")
}

$attentionPath = Resolve-CompassTarget 'attention_board.md'
$attention = [System.IO.File]::ReadAllText($attentionPath).Replace("`r`n", "`n")
$otherRowsBefore = @([regex]::Matches($attention, '(?m)^\| .+\| (?:REQUIRED|HELPFUL) \|$') | ForEach-Object { $_.Value } | Where-Object { $_ -notmatch '^\| discoverable_non_resolvable_registrations \|' })
$attention = [regex]::Replace($attention, '(?m)^\| discoverable_non_resolvable_registrations \|.*\n', '')
$attention = [regex]::Replace($attention, '(?m)^- discoverable_non_resolvable_registrations:[\s\S]*?(?=^- |^<!-- END USER-DEFINED: notes -->)', '')
$anchors = foreach ($entry in $mapping.GetEnumerator()) {
    $name = [System.IO.Path]::GetFileNameWithoutExtension($entry.Value)
    "| $name | done | updater_0 | $($entry.Value) | Owner turn-in; feature and reported repairs accepted; evidence retained. | $stamp |"
}
$anchors = @($anchors | Select-Object -First 12)
$attention = [regex]::Replace($attention, '(?s)(<!-- BEGIN USER-DEFINED: closed_anchors -->\n).*?(<!-- END USER-DEFINED: closed_anchors -->)', '$1' + ($anchors -join "`n") + "`n" + '$2')
[System.IO.File]::WriteAllText($attentionPath, $attention, $utf8)

$artifactPath = Resolve-CompassTarget 'artifact_board.md'
$artifactText = [System.IO.File]::ReadAllText($artifactPath).Replace("`r`n", "`n")
$cleared = [System.Collections.Generic.List[string]]::new()
$artifactText = [regex]::Replace($artifactText, '(?m)^\| tickets/[^\n]+\n', {
    param($match)
    $cells = $match.Value.TrimEnd().Split('|')
    $ticket = $cells[1].Trim()
    if (-not $mapping.Contains($ticket)) { return $match.Value }
    $artifact = Update-References $cells[2].Trim()
    $disposition = $cells[5].Trim()
    $reason = if ($disposition -eq 'promote_to_documentation') {
        'Durable deltas promoted; original patch contracts and indexes archived intact.'
    } else {
        'Owner-authorized turn-in; validation and recorded limitations retained as reference.'
    }
    $cleared.Add("| $($mapping[$ticket]) | $artifact | $disposition | $reason | $stamp |")
    return ''
})
if ($cleared.Count -ne 11) { throw "Expected 11 artifact associations, found $($cleared.Count)" }
$artifactText = $artifactText.Replace("<!-- BEGIN USER-DEFINED: cleared_artifacts -->`n", "<!-- BEGIN USER-DEFINED: cleared_artifacts -->`n" + ($cleared -join "`n") + "`n")
[System.IO.File]::WriteAllText($artifactPath, $artifactText, $utf8)

$mailboxPath = Resolve-CompassTarget 'mailbox_board.md'
$mailbox = [System.IO.File]::ReadAllText($mailboxPath)
$mailbox = [regex]::Replace($mailbox, '(?m)^\| updater_0 \| codex \| ([^|]+) \| [^|]+ \| [^|]+ \|\r?$', '| updater_0 | codex | $1 | ' + $stamp + ' | departed |')
[System.IO.File]::WriteAllText($mailboxPath, $mailbox, $utf8)

foreach ($entry in $patchHashes.GetEnumerator()) {
    if ((Get-FileHash -LiteralPath (Resolve-CompassTarget $entry.Key) -Algorithm SHA256).Hash -ne $entry.Value) {
        throw "Archived bytes changed: $($entry.Key)"
    }
}
$otherRowsAfter = @([regex]::Matches($attention, '(?m)^\| .+\| (?:REQUIRED|HELPFUL) \|$') | ForEach-Object { $_.Value })
if (($otherRowsBefore -join "`n") -ne ($otherRowsAfter -join "`n")) { throw 'Unrelated active routing changed' }
foreach ($entry in $mapping.GetEnumerator()) {
    if (Test-Path -LiteralPath (Resolve-CompassTarget $entry.Key)) { throw "Old ticket remains: $($entry.Key)" }
    if (-not (Test-Path -LiteralPath (Resolve-CompassTarget $entry.Value))) { throw "Missing completed ticket: $($entry.Value)" }
}
$report = [ordered]@{
    completed_at = $stamp
    tickets_closed = $mapping.Count
    patches_archived = $patchMapping.Count
    archived_files_verified = $patchHashes.Count
    artifact_associations_cleared = $cleared.Count
    closed_anchor_count = $anchors.Count
    unrelated_active_rows_preserved = $otherRowsAfter.Count
    ticket_moves = $mapping
    archived_sha256 = $patchHashes
}
$reportPath = Resolve-CompassTarget 'artifacts/non_resolvable_followup_20260919/closure_result.json'
[System.IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json -Depth 6) + "`n", $utf8)
Write-Output "Closed $($mapping.Count) tickets; archived $($patchHashes.Count) files in $($patchMapping.Count) patch directories; cleared $($cleared.Count) artifact rows."
