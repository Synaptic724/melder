# Story: Cleanup RiftSpace And AR Room Documentation Drift
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-18-cleanup-rift-space-and-ar-room-documentation-drift
- Epic: EPIC-2026-04-18-rehome-frame-viewer-ownership-to-rift-space
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-19T00:02:00Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a runtime maintainer, I want the `RiftSpace` docstrings and AR
architecture/component docs to match the current room/viewer model, so that the
repo no longer describes the old `dynamic` room or removed selected-target room
state as if they were still real.

## Value / MRP Alignment
This keeps the durable docs honest after the room/viewer ownership migration.
It reduces drift between code and docs without widening back into another
runtime change.

## Ticket Contract
- ENTRY_GATE: user explicitly asked to fix the drifts and update the
  architecture docs after the room/viewer ownership move.
- EXECUTION_BOUNDARY: `RiftSpace` / room docstrings plus
  `codex/context_compass/system_docs/src_architecture.md` and
  `codex/context_compass/system_docs/src_components.md` only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-19_fix_rift_space_and_ar_room_documentation_drift_task.md
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
- EXIT_GATE: stale room-kind, viewer-ownership, and removed selected-target
  wording is corrected and the focused validation ring is still green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if fixing the docs would require
  reopening broader AR architecture design.

## Requirements (Functional)
- Replace stale `dynamic` room references with the live `capability` /
  `codegen` room model where appropriate.
- Remove stale room-selected-target ownership wording.
- Update AR docs to reflect room-owned viewer assembly and config-backed
  projection refresh gating.

## Requirements (Non-Functional)
- Keep the patch bounded to documented drift proven by current source.
- Do not widen into unrelated architecture prose cleanup.

## Scope Boundaries
- In scope:
  - `RiftSpace` docstring cleanup
  - AR room/viewer architecture/component doc cleanup
- Out of scope:
  - runtime behavior changes
  - command/codegen API redesign
  - broader documentation sweep

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the bounded doc drift cleanup is implemented and the
  focused ring stayed green.

## Dependencies / Related Work
- viewer ownership migration story/task
- config-driven refresh barrier story/task

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-19-fix-rift-space-and-ar-room-documentation-drift
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `RiftSpace` docstrings no longer describe the old room-kind model.
- `src_architecture.md` and `src_components.md` no longer describe removed
  selected-target room state or old `dynamic_*` room files as live.
- Focused validation remains green.

## Validation / Test Plan
- compile touched Python file(s)
- rerun the focused AR/Nexus viewer ring

## Risks / Mitigations
- Risk: doc drift may exist outside the bounded room/viewer areas.
  Mitigation: fix only the source-proven lines in this story.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- None at story start; this is bounded drift correction.

## Decision Log
- Pending implementation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-19T00:14:29Z
  TYPE: FACT
  CLAIM: The child task landed the bounded drift cleanup and the focused
    AR/Nexus viewer ring is still green.
  EVIDENCE:
  - tickets/tasks/2026-04-19_fix_rift_space_and_ar_room_documentation_drift_task.md:1-130
  IMPACT: The story is ready for review instead of more implementation.
  NEXT: hold for acceptance or a bounded follow-on request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-04-19T00:02:00Z
  TYPE: PLAN
  CLAIM: The drift is bounded to room-kind wording, stale room-selected-target
    ownership language, and old `dynamic_*` room file references in the AR
    docs.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:39-81
  - codex/context_compass/system_docs/src_architecture.md:463-505
  - codex/context_compass/system_docs/src_components.md:507-590
  IMPACT: This can be cleaned without reopening runtime design.
  NEXT: patch the linked task and rerun the focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story tracks the bounded post-migration documentation drift cleanup for
`RiftSpace` and the AR room/viewer architecture docs. It is now implemented and
waiting on review.