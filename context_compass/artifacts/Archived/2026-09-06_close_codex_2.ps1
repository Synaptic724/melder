# Mechanical, owner-authorized closure of codex_2's Read the Docs program.
# Only selected tickets, their references, and their coordination records change.
$ErrorActionPreference = 'Stop'
$taskRepo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$taskContext = (Resolve-Path -LiteralPath (Join-Path $taskRepo 'context_compass')).Path
$taskUtc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$taskNl = [string][char]10
$taskLedger = Join-Path $taskContext 'artifacts/2026-09-06_codex_2_ticket_closure.md'
$taskEp = 'tickets/epics/2026-09-04_readthedocs_documentation_epic.md'
$taskMoves = @{}
$taskSelected = @{}

function Read-ClosureText([string]$Path) {
    return (Get-Content -LiteralPath $Path -Raw).Replace(([string][char]13 + [char]10), [string][char]10)
}
function Write-ClosureText([string]$Path, [string]$Text) {
    [System.IO.File]::WriteAllText($Path, $Text, [System.Text.UTF8Encoding]::new($false))
}
function Assert-ClosurePath([string]$Path) {
    $resolved = [System.IO.Path]::GetFullPath($Path)
    if (-not $resolved.StartsWith($taskContext + [System.IO.Path]::DirectorySeparatorChar,
                                  [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Closure path escapes ContextCompass: $resolved"
    }
    return $resolved
}
function Update-ClosureReferences([string]$Text, [string]$OldOrigin, [string]$NewOrigin) {
    $oldDirectory = Split-Path -Parent $OldOrigin
    $newDirectory = Split-Path -Parent $NewOrigin
    # Rebase actual local Markdown links; leave URLs and unresolved historical examples alone.
    $Text = [regex]::Replace($Text, '\]\(([^)\r\n]+)\)', {
        param($match)
        $target = $match.Groups[1].Value
        if ($target -match '^([a-zA-Z][\w+.-]*:|/|#)' -or $target.Contains('"')) { return $match.Value }
        $bare = ($target -split '[?#]', 2)[0]
        if (-not $bare) { return $match.Value }
        $absolute = [System.IO.Path]::GetFullPath((Join-Path $oldDirectory $bare))
        if ($taskMoves.ContainsKey($absolute)) { $absolute = $taskMoves[$absolute] }
        elseif (-not (Test-Path -LiteralPath $absolute)) { return $match.Value }
        $relative = [System.IO.Path]::GetRelativePath($newDirectory, $absolute).Replace('\', '/')
        return '](' + $relative + $target.Substring($bare.Length) + ')'
    })
    $Text = [regex]::Replace($Text, '(?m)^(- (?:Story|Epic) Path: )([^\r\n]+)$', {
        param($match)
        $absolute = [System.IO.Path]::GetFullPath((Join-Path $oldDirectory $match.Groups[2].Value))
        if ($taskMoves.ContainsKey($absolute)) { $absolute = $taskMoves[$absolute] }
        return $match.Groups[1].Value + [System.IO.Path]::GetRelativePath($newDirectory, $absolute).Replace('\', '/')
    })
    foreach ($old in $taskMoves.Keys) {
        $oldRelative = [System.IO.Path]::GetRelativePath($taskContext, $old).Replace('\', '/')
        $newRelative = [System.IO.Path]::GetRelativePath($taskContext, $taskMoves[$old]).Replace('\', '/')
        $Text = $Text.Replace($oldRelative, $newRelative)
    }
    return $Text
}

$taskPaths = @(rg -l '^[-] Agent Name:.*codex_2' (Join-Path $taskContext 'tickets') -g '*.md' -g '!**/completed/**' -g '!**/archive/**')
if ($LASTEXITCODE -ne 0 -or $taskPaths.Count -ne 22) { throw 'Expected the reviewed 22-ticket closure set.' }
$taskRecords = @()
foreach ($path in $taskPaths) {
    $source = Assert-ClosurePath (Resolve-Path -LiteralPath $path).Path
    $relative = [System.IO.Path]::GetRelativePath($taskContext, $source).Replace('\', '/')
    if ($relative -notmatch '^tickets/(epics|stories|tasks)/2026-09-04_(rtd|readthedocs)') {
        throw "Unexpected ticket in closure set: $relative"
    }
    $kind = $Matches[1]
    $destination = Assert-ClosurePath (Join-Path (Split-Path -Parent $source) ('completed/' + (Split-Path -Leaf $source)))
    if (Test-Path -LiteralPath $destination) { throw "Closure destination already exists: $destination" }
    $body = Read-ClosureText $source
    if ($body -match 'CONTEXT_MANAGEMENT_REQUIRED: true') { throw "Unexpected required context pack: $relative" }
    $record = [pscustomobject]@{
        Source=$source; Destination=$destination; Relative=$relative; Kind=$kind; Body=$body
        Title=[regex]::Match($body, '(?m)^# (?:Task|Story|Epic): (.+)$').Groups[1].Value
        PriorStatus=[regex]::Match($body, '(?m)^- Status: (.+)$').Groups[1].Value
    }
    $taskRecords += $record
    $taskMoves[$source] = $destination
    $taskSelected[$relative] = $record
}
if (@($taskRecords | Where-Object Kind -eq 'epics').Count -ne 1 -or
    @($taskRecords | Where-Object Kind -eq 'stories').Count -ne 9 -or
    @($taskRecords | Where-Object Kind -eq 'tasks').Count -ne 12) { throw 'Ticket kind counts changed.' }

$taskPatchSource = Assert-ClosurePath (Resolve-Path -LiteralPath (Join-Path $taskContext 'system_docs/patches/active/rtd_site_2026_09_04')).Path
$taskPatchDestination = Assert-ClosurePath (Join-Path $taskContext 'system_docs/patches/completed/rtd_site_2026_09_04')
if (Test-Path -LiteralPath $taskPatchDestination) { throw 'Patch archive already exists.' }
if ((Get-Item -LiteralPath $taskPatchSource).Attributes -band [System.IO.FileAttributes]::ReparsePoint) { throw 'Patch directory is redirected.' }
$taskPatchHashes = @{}
foreach ($file in Get-ChildItem -LiteralPath $taskPatchSource -File) {
    $destination = Assert-ClosurePath (Join-Path $taskPatchDestination $file.Name)
    $taskMoves[$file.FullName] = $destination
    $taskPatchHashes[$destination] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
}

$taskArtifactPath = Join-Path $taskContext 'artifact_board.md'
$taskArtifactText = Read-ClosureText $taskArtifactPath
$taskArtifactRows = [regex]::Match($taskArtifactText,
    '(?s)<!-- BEGIN USER-DEFINED: active_artifacts -->(.*?)<!-- END USER-DEFINED: active_artifacts -->').Groups[1].Value -split $taskNl
$taskKeepArtifacts = @()
$taskClearedArtifacts = @()
$taskRetainedHashes = @{}
foreach ($row in $taskArtifactRows) {
    if (-not $row.StartsWith('| ')) { continue }
    $cells = @($row.Trim('|').Split('|') | ForEach-Object { $_.Trim() })
    if (-not $taskSelected.ContainsKey($cells[0])) { $taskKeepArtifacts += $row; continue }
    if ($cells[4] -eq 'delete_on_close') { throw "Unexpected destructive artifact disposition: $row" }
    $artifact = Assert-ClosurePath (Join-Path $taskContext $cells[1])
    if (-not (Test-Path -LiteralPath $artifact)) { throw "Missing retained artifact: $artifact" }
    if ([System.IO.Path]::GetExtension($artifact) -ne '.md') {
        $taskRetainedHashes[$artifact] = (Get-FileHash -LiteralPath $artifact -Algorithm SHA256).Hash
    }
    $newArtifact = if ($taskMoves.ContainsKey($artifact)) {
        [System.IO.Path]::GetRelativePath($taskContext, $taskMoves[$artifact]).Replace('\', '/')
    } else { $cells[1] }
    $newTicket = [System.IO.Path]::GetRelativePath($taskContext, $taskSelected[$cells[0]].Destination).Replace('\', '/')
    $reason = if ($cells[4] -eq 'promote_to_documentation') {
        'Implemented in docs content/tools and maintaining.md; original design/contract retained as history.'
    } else { 'Owner-accepted program; retained validation and investigation evidence.' }
    $taskClearedArtifacts += '| ' + $newTicket + ' | ' + $newArtifact + ' | ' + $cells[4] + ' | ' + $reason + ' | ' + $taskUtc + ' |'
}

$taskEdits = @{}
foreach ($record in $taskRecords) {
    $body = Update-ClosureReferences $record.Body $record.Source $record.Destination
    $body = [regex]::Replace($body, '(?m)^- Status: [^\r\n]+$', '- Status: done')
    $body = [regex]::Replace($body, '(?m)^- Updated: [^\r\n]+$', '- Updated: ' + $taskUtc)
    $metadata = '- Completed: ' + $taskUtc + $taskNl + '- Summary: Owner accepted this RTD deliverable and requested closure of the complete codex_2 program.' + $taskNl
    $body = [regex]::Replace($body, '(?m)(^- Updated: [^\r\n]+\n)', ('$1' + $metadata))
    $transition = '## State Transition Event' + $taskNl + '- from_state: ' + $record.PriorStatus + $taskNl + '- to_state: done' + $taskNl + '- transition_reason: Owner explicitly accepted the delivered work and requested all codex_2 tickets turned in.' + $taskNl + $taskNl
    $body = [regex]::Replace($body, '(?ms)^## State Transition Event\n.*?(?=^## |\z)', $transition)
    $ledgerLink = [System.IO.Path]::GetRelativePath((Split-Path -Parent $record.Destination), $taskLedger).Replace('\', '/')
    $acceptance = 'Closed at owner direction. See the [closure record](' + $ledgerLink + '). Historical checklists and' + $taskNl + 'validation limits below are retained; closure does not claim that unperformed checks passed.' + $taskNl + $taskNl
    $body = $body.Replace('## Metadata' + $taskNl, '## Closure Acceptance' + $taskNl + $taskNl + $acceptance + '## Metadata' + $taskNl)
    $note = @"
- DATETIME: $taskUtc
  TYPE: DECISION
  CLAIM: Owner selected all codex_2 tickets for closure after accepting the delivered documentation.
    Historical findings and validation limits remain intact. The later hosted diagnosis supersedes
    the original 404 blocker; the owner also confirmed current-version updates work.
  EVIDENCE:
  - Owner instruction: turn in all your tickets and call it; continue.
  - artifacts/2026-09-06_codex_2_ticket_closure.md
  IMPACT: This ticket is closed under owner acceptance; no further work is routed here.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

"@
    if ($body -notmatch '(?m)^## Notes$') { throw "Missing Notes section: $($record.Relative)" }
    $body = [regex]::Replace($body, '(?ms)(^## Notes\n)(.*?)(?=^## |\z)', {
        param($match)
        return $match.Groups[1].Value + $match.Groups[2].Value.TrimEnd() + $taskNl + $taskNl + $note + $taskNl
    })
    $body = $body.Replace('## Context / Handoff Summary' + $taskNl,
        '## Context / Handoff Summary' + $taskNl + $taskNl + $acceptance + 'The previous handoff is preserved below as historical context.' + $taskNl)
    if ($record.Relative -eq $taskEp) {
        $body = $body.Replace('- ARTIFACT_PATHS:' + $taskNl,
            '- ARTIFACT_PATHS:' + $taskNl + '  - artifacts/2026-09-06_codex_2_ticket_closure.md' + $taskNl + '  - artifacts/2026-09-06_close_codex_2.ps1' + $taskNl)
    }
    $taskEdits[$record.Source] = $body
}

# Prepare inbound link repairs while original ticket paths still exist.
$taskInbound = @(rg -l '2026-09-04_(rtd_|readthedocs_)' $taskContext -g '*.md' -g '!**/agent_onboarding/**' -g '!**/graph/**')
foreach ($path in $taskInbound) {
    $absolute = [System.IO.Path]::GetFullPath($path)
    if ($taskEdits.ContainsKey($absolute) -or $absolute -eq $taskArtifactPath -or
        $absolute -eq (Join-Path $taskContext 'attention_board.md')) { continue }
    $body = Read-ClosureText $absolute
    $updated = Update-ClosureReferences $body $absolute $absolute
    if ($updated -ne $body) { $taskEdits[$absolute] = $updated }
}

$taskLedgerLines = @('# codex_2 ticket closure', '', ('- Closed: ' + $taskUtc),
    '- Owner instruction: turn in all your tickets and call it; continue.',
    '- Scope: 22 tickets (1 epic, 9 stories, 12 tasks).', '',
    'The four-level site, full contents, 133-example catalog, API/architecture references, CI/RTD',
    'builds, offline formats, accessibility fixes, capstone revision, and maintenance guide are accepted.',
    'The later hosted diagnosis records healthy latest on prod; the owner confirms current-version',
    'updates now work. The old stable-tag limitation and unperformed zoom/clipboard/addon checks',
    'remain historical or owner-controlled limits, not fabricated verification passes.', '',
    'Evidence: tickets/tasks/completed/2026-09-05_diagnose_readthedocs_hosted_build_task.md.',
    'Detailed local evidence: artifacts/2026-09-05_rtd_final_quality_audit.md.', '',
    'The blueprint is implemented in docs content/navigation and maintaining.md. Its original record',
    'is retained. The three publication patch contracts are archived unchanged under',
    'system_docs/patches/completed/rtd_site_2026_09_04/. Validation logs and source proofs are retained.', '',
    '| Kind | Completed ticket | Title |', '| --- | --- | --- |')
foreach ($record in ($taskRecords | Sort-Object Kind,Relative)) {
    $target = [System.IO.Path]::GetRelativePath($taskContext,$record.Destination).Replace('\','/')
    $taskLedgerLines += '| ' + $record.Kind + ' | [' + (Split-Path -Leaf $target) + '](../' + $target + ') | ' + $record.Title + ' |'
}

# Every recursive move target has been resolved and bounded above. Keep one shell end-to-end.
Write-Output ('Validated patch move: ' + $taskPatchSource + ' -> ' + $taskPatchDestination)
Write-Output ('Validated ticket moves: ' + $taskRecords.Count + ' files inside ' + $taskContext)
foreach ($path in $taskEdits.Keys) { Write-ClosureText $path $taskEdits[$path] }
Move-Item -LiteralPath $taskPatchSource -Destination $taskPatchDestination
foreach ($record in ($taskRecords | Sort-Object @{Expression={switch ($_.Kind) {'tasks' {0} 'stories' {1} 'epics' {2}}}},Relative)) {
    Move-Item -LiteralPath $record.Source -Destination $record.Destination
}

$taskArtifactText = [regex]::Replace($taskArtifactText,
    '(?s)(<!-- BEGIN USER-DEFINED: active_artifacts -->).*?(<!-- END USER-DEFINED: active_artifacts -->)',
    ('$1' + $taskNl + ($taskKeepArtifacts -join $taskNl) + $taskNl + '$2'))
$taskClosedEpic = 'tickets/epics/completed/2026-09-04_readthedocs_documentation_epic.md'
foreach ($path in @('artifacts/2026-09-06_codex_2_ticket_closure.md','artifacts/2026-09-06_close_codex_2.ps1')) {
    $taskClearedArtifacts += '| ' + $taskClosedEpic + ' | ' + $path + ' | retain_as_reference | Owner-authorized closure record and mechanical procedure. | ' + $taskUtc + ' |'
}
$taskArtifactText = $taskArtifactText.Replace('<!-- BEGIN USER-DEFINED: cleared_artifacts -->',
    '<!-- BEGIN USER-DEFINED: cleared_artifacts -->' + $taskNl + ($taskClearedArtifacts -join $taskNl))
Write-ClosureText $taskArtifactPath $taskArtifactText

$taskBoardPath = Join-Path $taskContext 'attention_board.md'
$taskBoard = Read-ClosureText $taskBoardPath
$taskBoard = [regex]::Replace($taskBoard, '(?m)^\| readthedocs_documentation \|[^\n]*\n', '')
$taskOldAnchors = [regex]::Match($taskBoard,
    '(?s)<!-- BEGIN USER-DEFINED: closed_anchors -->(.*?)<!-- END USER-DEFINED: closed_anchors -->').Groups[1].Value -split $taskNl | Where-Object { $_.StartsWith('| ') }
$taskAnchors = @()
foreach ($record in ($taskRecords | Sort-Object @{Expression={switch ($_.Kind) {'epics' {0} 'stories' {1} 'tasks' {2}}}},Relative)) {
    $target = [System.IO.Path]::GetRelativePath($taskContext,$record.Destination).Replace('\','/')
    $taskAnchors += '| ' + [System.IO.Path]::GetFileNameWithoutExtension($record.Source) + ' | done | codex_2 | ' + $target + ' | Owner accepted; evidence retained in the completed program. | ' + $taskUtc + ' |'
}
$taskAnchors = @($taskAnchors + $taskOldAnchors | Select-Object -First 12)
$taskBoard = [regex]::Replace($taskBoard,
    '(?s)(<!-- BEGIN USER-DEFINED: closed_anchors -->).*?(<!-- END USER-DEFINED: closed_anchors -->)',
    ('$1' + $taskNl + ($taskAnchors -join $taskNl) + $taskNl + '$2'))
Write-ClosureText $taskBoardPath $taskBoard

$taskMailPath = Join-Path $taskContext 'mailbox_board.md'
$taskMail = Read-ClosureText $taskMailPath
$taskMail = [regex]::Replace($taskMail, '(?m)^\| codex_2 \| codex \| ([^|]+) \| [^|]+ \| active \|$',
    ('| codex_2 | codex | $1 | ' + $taskUtc + ' | departed |'))
Write-ClosureText $taskMailPath $taskMail
Write-ClosureText $taskLedger (($taskLedgerLines -join $taskNl) + $taskNl)

# Verify destinations, retained byte evidence, and the original patch contracts.
foreach ($record in $taskRecords) {
    if ((Test-Path -LiteralPath $record.Source) -or -not (Test-Path -LiteralPath $record.Destination)) {
        throw "Ticket move failed: $($record.Relative)"
    }
    if ((Read-ClosureText $record.Destination) -notmatch '(?m)^- Status: done$') { throw 'Incomplete ticket status.' }
}
foreach ($path in $taskRetainedHashes.Keys) {
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $taskRetainedHashes[$path]) { throw "Evidence changed: $path" }
}
foreach ($path in $taskPatchHashes.Keys) {
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $taskPatchHashes[$path]) { throw "Patch history changed: $path" }
}
Write-Output ('Closed 22 tickets; cleared ' + $taskClearedArtifacts.Count + ' artifact associations; archived ' + $taskPatchHashes.Count + ' unchanged patch contracts.')
