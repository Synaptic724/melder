# Task: Advance the version for four completed feature epics

- Completed: 2026-09-22T19:57:59Z
- Summary: Corrected by owner direction to 0.2.47: baseline 0.2.43 plus four completed feature epics.
  The original 0.2.49 result double-counted two increments. Its dated evidence remains below.
- Correction: tickets/tasks/completed/2026-09-22_correct_epic_version_baseline_task.md

## Metadata
- Task ID: TASK-2026-09-22-notch-version-for-completed-epics
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-22T19:56:34Z
- Updated: 2026-09-22T20:11:00Z

## Objective
Apply four total notches in the established 0.2.x sequence: 0.2.43 to 0.2.47. The completed
feature epics are scoped purge, independent graduation, bind lifecycle hooks and pooled hook repair.

## Ticket Contract
- ENTRY_GATE: Owner requests one notch per completed epic and clarifies there were three to four.
- EXECUTION_BOUNDARY: Canonical version literal, next-release heading and durable tracking only.
- DEPENDENCIES: Four completed epic records; setuptools and docs read the canonical version file.
- EXIT_GATE: Canonical version and release heading agree on 0.2.47; held assets remain unchanged.
- FAILURE_ESCALATION: Do not invent intermediate published releases or regenerate held assets.

## Scope
Use the same last-component increments as the earlier 0.2.44 to 0.2.45 change. The original target
0.2.49 was superseded when the owner clarified the baseline. This is the established convention, not a
claim that the last component is the semantic-version minor field. No publication, wheel or lock sync.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner-requested version notches applied and static agreement/preservation checks pass.

## Work
- [x] Verify current version and completed epic count.
- [x] Update the canonical literal and release draft heading.
- [x] Check agreement and asset preservation; turn in this metadata change.

## Validation
Original validation (superseded target): AST and draft-heading checks passed for 0.2.49.
Setuptools still reads the canonical version
attribute; all 26 held assets match their prior hashes. Scoped whitespace checks pass. Runtime tests
were not rerun for this metadata-only change, and no generator, wheel or publication ran.

## Artifact Links
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Notes
- DATETIME: 2026-09-22T19:56:34Z
  TYPE: DECISION
  CLAIM: Count four feature epics, not their child tasks: purge, graduation, bind hooks and pool
    hooks. Apply the requested four additional notches to current 0.2.45, yielding 0.2.49 in the
    existing 0.2.x convention. Setuptools uses dynamic metadata; uv's editable root has no version.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - pyproject.toml:139-142
  - uv.lock:334-337
  - tickets/epics/completed/2026-09-19_scope_aware_creation_purge_epic.md
  - tickets/epics/completed/2026-09-22_graduated_conduit_spellbook_ownership_and_configuration_epic.md
  - tickets/epics/completed/2026-09-20_bind_lifecycle_hooks_and_reference_strategies_epic.md
  - tickets/epics/completed/2026-09-21_runtime_hook_lifecycle_and_adjustment_epic.md
  IMPACT: Only the canonical version file and current draft need edits. Prior version labels in
    historical tickets remain intact; generated assets still await separate authorization.
  NEXT: Update and verify both version surfaces.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
The owner corrected the baseline to 0.2.43, yielding 0.2.47 for four feature epics total. Follow the
linked correction task for current verification. The earlier 0.2.49 decision above is historical;
future build generation must use the canonical version, currently 0.2.47. The asset hold continues.
