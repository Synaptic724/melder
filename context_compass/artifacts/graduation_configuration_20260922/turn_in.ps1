$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath '.').Path
$stamp = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
$compassRoot = Join-Path $taskRoot 'context_compass'
$epicName = '2026-09-22_graduated_conduit_spellbook_ownership_and_configuration_epic.md'
$implementationName = '2026-09-22_implement_graduation_configuration_and_hook_ownership_task.md'
$regressionName = '2026-09-22_add_graduation_ownership_red_regressions_task.md'
$followupName = '2026-09-22_refresh_graduation_packaged_assets_when_approved_task.md'
$moves = [ordered]@{
    "tickets/epics/$epicName" = "tickets/epics/completed/$epicName"
    "tickets/tasks/$implementationName" = "tickets/tasks/completed/$implementationName"
    "tickets/tasks/$regressionName" = "tickets/tasks/completed/$regressionName"
    'system_docs/patches/active/graduation_configuration_2026_09_22' = 'system_docs/patches/completed/graduation_configuration_2026_09_22'
}

# Every move is explicit and confined to this repository before any mutation.
foreach ($entry in $moves.GetEnumerator()) {
    foreach ($relative in @($entry.Key, $entry.Value)) {
        $absolute = [IO.Path]::GetFullPath((Join-Path $compassRoot $relative))
        if (-not $absolute.StartsWith(($compassRoot + '\'), [StringComparison]::OrdinalIgnoreCase)) {
            throw "Outside ContextCompass: $absolute"
        }
    }
    if (-not (Test-Path -LiteralPath (Join-Path $compassRoot $entry.Key))) { throw "Missing source: $($entry.Key)" }
    if (Test-Path -LiteralPath (Join-Path $compassRoot $entry.Value)) { throw "Existing destination: $($entry.Value)" }
}

$completionNote = @'
- DATETIME: STAMP
  TYPE: DECISION
  CLAIM: Owner explicitly requested additional hook-isolation tests and graduation epic turn-in.
    The added twelve cases pass within a 157-test focused selection; prior broad qualification
    remains 4118 passes and two existing owner-deferred skips. Source behavior did not change in
    the final test tranche. Graduation source, regressions and canonical documentation are complete.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/hook_isolation_final.log:1-4
  - artifacts/graduation_configuration_20260922/qualification_final.log
  - artifacts/graduation_configuration_20260922/upgrade_review.md
  - artifacts/graduation_configuration_20260922/documentation_preservation.json
  IMPACT: Close the graduation epic and its implementation/red-regression tasks. Retain evidence
    and archive promoted patch contracts. Packaged build generation remains explicitly held in
    TASK-2026-09-22-refresh-graduation-packaged-assets-when-approved; no build runner was invoked.
  NEXT: None for graduation source. The separate packaged-asset task waits for owner authorization.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

'@
$completionNote = $completionNote.Replace('STAMP', $stamp)
$handoff = @'
## Context / Handoff Summary
CLOSED by owner-requested turn-in after additional hook-isolation qualification. Graduation creates
an independent empty Book, preserves the Conduit/ID/creation stores, and resets old Book-specific
hooks and runtime overlays. Frame-wide rich configuration stays canonical and frame-owned; its
deliberately configured defaults may seed the new Book without sharing runtime registration state.

All twelve added scenarios pass within 157 focused tests. Prior affected qualification: 4118 pass,
two existing owner-deferred skips. Canonical architecture/components, measured ranges and the scoped
graph descriptions are promoted; document indexes validate. Packaged build assets remain untouched.
See artifacts/graduation_configuration_20260922/upgrade_review.md for behavior and concurrency limits.
Only TASK-2026-09-22-refresh-graduation-packaged-assets-when-approved remains queued for packaging.
'@

foreach ($relative in @("tickets/epics/$epicName", "tickets/tasks/$implementationName", "tickets/tasks/$regressionName")) {
    $path = Join-Path $compassRoot $relative
    $content = Get-Content -LiteralPath $path -Raw
    $content = $content -replace '(?m)^- Status: .*$', '- Status: done'
    $content = $content -replace '(?m)^- Updated: .*$', ('- Updated: ' + $stamp)
    $content = $content.Replace('## Metadata', ("## Metadata`n- Completed: $stamp`n- Summary: Graduation source, hook isolation and shared-frame behavior qualified and turned in; packaging held separately."))
    $content = $content -replace '(?m)^- from_state: .*$', '- from_state: review'
    $content = $content -replace '(?m)^- to_state: .*$', '- to_state: done'
    $content = $content -replace '(?m)^- transition_reason: .*$', '- transition_reason: Owner requested turn-in after additional regression tests, which now pass.'
    $content = $content.Replace('- [ ] Documentation/assets approved and delivered.', '- [x] Canonical documentation promoted; packaged build hold transferred to its own task.')
    $content = $content -replace '(?s)## Context / Handoff Summary.*$', ($completionNote + $handoff)
    foreach ($entry in $moves.GetEnumerator()) { $content = $content.Replace($entry.Key, $entry.Value) }
    [IO.File]::WriteAllText($path, $content)
}

$followupPath = Join-Path $compassRoot "tickets/tasks/$followupName"
$followup = (Get-Content -LiteralPath $followupPath -Raw).Replace('pending final turn-in timestamp', $stamp)
[IO.File]::WriteAllText($followupPath, $followup)

foreach ($entry in $moves.GetEnumerator()) {
    $source = Join-Path $compassRoot $entry.Key
    $destination = Join-Path $compassRoot $entry.Value
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    Move-Item -LiteralPath $source -Destination $destination
}

$boardPath = Join-Path $compassRoot 'attention_board.md'
$board = Get-Content -LiteralPath $boardPath -Raw
$board = $board -replace '(?m)^\| graduation_(configuration_implementation|configuration|ownership_regressions) \|.*\r?\n', ''
$newRow = "| graduation_packaged_assets | blocked | handoff | codex | updater_0 | Owner build-asset hold. | Wait for packaged generation authorization. | Preserve completed source while packaging stays queued. | Owner releases build hold. | tickets/tasks/$followupName | $stamp | REQUIRED |"
$board = $board.Replace('<!-- BEGIN USER-DEFINED: active_items -->', ("<!-- BEGIN USER-DEFINED: active_items -->`n" + $newRow))
$board = $board -replace '(?ms)^- graduation_configuration_implementation:.*?(?=^- graduation_configuration:)', ''
$board = $board -replace '(?ms)^- graduation_configuration:.*?(?=^- graduation_ownership_regressions:)', ''
$board = $board -replace '(?ms)^- graduation_ownership_regressions:.*?(?=^- next_version_release:)', ''
$board = $board.Replace('### Active Attention Details', ("### Active Attention Details`n- graduation_packaged_assets: SWITCH_TRIGGER is owner approval of packaged build generation.`n  RESUME_HIERARCHY: tickets/tasks/$followupName."))
$anchors = @(
    "| graduated_conduit_epic | done | updater_0 | tickets/epics/completed/$epicName | Independent Book and hooks; shared policy verified; packaging held separately. | $stamp |"
    "| graduation_implementation | done | updater_0 | tickets/tasks/completed/$implementationName | 4118 broad passes and 157 final focused passes; canonical docs promoted. | $stamp |"
    "| graduation_red_regressions | done | updater_0 | tickets/tasks/completed/$regressionName | Original 32 failures now green; regression evidence retained. | $stamp |"
)
$anchorMatch = [regex]::Match($board, '(?s)<!-- BEGIN USER-DEFINED: closed_anchors -->\r?\n(.*?)<!-- END USER-DEFINED: closed_anchors -->')
$previousAnchors = @($anchorMatch.Groups[1].Value -split '\r?\n' | Where-Object { $_.StartsWith('|') })
$retained = @($anchors + $previousAnchors | Select-Object -First 12)
$board = $board.Replace($anchorMatch.Value, ("<!-- BEGIN USER-DEFINED: closed_anchors -->`n" + ($retained -join "`n") + "`n<!-- END USER-DEFINED: closed_anchors -->"))
[IO.File]::WriteAllText($boardPath, $board)

$artifactPath = Join-Path $compassRoot 'artifact_board.md'
$artifacts = Get-Content -LiteralPath $artifactPath -Raw
$artifacts = $artifacts -replace '(?m)^\| tickets/tasks/2026-09-22_(implement_graduation_configuration_and_hook_ownership|add_graduation_ownership_red_regressions)_task.md \|.*\r?\n', ''
$clearedRows = @(
    "| tickets/tasks/completed/$implementationName | artifacts/graduation_configuration_20260922/ | retain_as_reference | Owner turn-in; source, additional hook tests, preservation and closeout evidence retained. | $stamp |"
    "| tickets/tasks/completed/$implementationName | system_docs/patches/completed/graduation_configuration_2026_09_22/ | promote_to_documentation | Scoped contracts promoted to canonical maps; original patches archived. | $stamp |"
    "| tickets/tasks/completed/$regressionName | artifacts/graduation_ownership_regressions_20260922/ | retain_as_reference | Original failing evidence retained alongside now-passing regressions. | $stamp |"
)
$artifacts = $artifacts.Replace('<!-- BEGIN USER-DEFINED: cleared_artifacts -->', ("<!-- BEGIN USER-DEFINED: cleared_artifacts -->`n" + ($clearedRows -join "`n")))
[IO.File]::WriteAllText($artifactPath, $artifacts)

# The candidate graph was a disposable staging copy. Only five descriptors were promoted.
$staging = [IO.Path]::GetFullPath((Join-Path $compassRoot 'artifacts/graduation_configuration_20260922/graph_candidate'))
$intendedParent = [IO.Path]::GetFullPath((Join-Path $compassRoot 'artifacts/graduation_configuration_20260922')) + '\'
if (-not $staging.StartsWith($intendedParent, [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe staging deletion target' }
Remove-Item -LiteralPath $staging -Recurse -Force

[ordered]@{ completed_at=$stamp; archived=@($moves.Values); pending="tickets/tasks/$followupName" } |
    ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $compassRoot 'artifacts/graduation_configuration_20260922/turn_in_receipt.json')
$stamp
