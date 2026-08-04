# Epic: Rift Space Frame Viewer Constructor Cleanup
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Epic ID: EPIC-2026-04-18-rift-space-frame-viewer-constructor-cleanup
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-18T20:49:23Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Remove the dead `frame_viewer` constructor seam from `RiftSpace` so viewer
attachment happens only through the explicit runtime attachment path.

## Value / MRP Alignment
This keeps room construction honest and removes another misleading hydration
seam from the live runtime.

## Ticket Contract
- ENTRY_GATE: user approved the bounded cleanup after investigation.
- EXECUTION_BOUNDARY: `RiftSpace`, directly affected room subclasses, and
  focused tests only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_remove_rift_space_frame_viewer_constructor_seam_task.md
- EXIT_GATE: no room constructor accepts `frame_viewer`, focused validation is
  green, and board routing reflects the task.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a real runtime caller depends
  on constructor-time viewer injection.

## Scope Boundaries
- In scope:
  - remove `frame_viewer` constructor injection
  - preserve explicit `attach_frame_viewer(...)`
  - port directly affected tests
- Out of scope:
  - viewer redesign
  - projection redesign

## Story Checklist
- [x] Story: STORY-2026-04-18-rift-space-frame-viewer-constructor-cleanup
- [ ] Enforce Ticket Microcycle across linked work.

## Notes
- DATETIME: 2026-04-18T20:51:04Z
  TYPE: FACT
  CLAIM: The bounded frame-viewer constructor cleanup epic is now implemented
    and waiting on user review.
  EVIDENCE:
  - tickets/stories/2026-04-18_rift_space_frame_viewer_constructor_cleanup_story.md:1-92
  IMPACT: No further implementation is needed in this epic unless the user asks
    for more room-lifecycle cleanup.
  NEXT: hold for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-04-18T20:49:23Z
  TYPE: FACT
  CLAIM: The current `frame_viewer` constructor seam is no longer part of the
    real runtime flow; rooms are created first and viewers are attached later
    through `attach_frame_viewer(...)`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:103-160
  - src/melder/aether/nexus/rift/rift.py:554-624
  - src/melder/aether/nexus/nexus.py:1923-2071
  - tests/unit/melder/aether/test_rift_space.py:14-24
  IMPACT: The constructor seam can be removed without widening into broader viewer work.
  NEXT: patch the room constructors and the focused test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This epic tracks one bounded ownership cleanup: remove the dead constructor-time
viewer seam from `RiftSpace`.