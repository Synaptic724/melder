# Epic: Rift Space Viewer Attachment Seam Cleanup
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Epic ID: EPIC-2026-04-18-rift-space-viewer-attachment-seam-cleanup
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-18T20:56:00Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Remove the public-looking viewer attach/detach seam from `RiftSpace` and keep
viewer replacement as an internal room lifecycle operation instead.

## Value / MRP Alignment
This reduces another misleading room-surface API seam and keeps viewer
management where it actually belongs: internal room state plus Rift-level
orchestration.

## Ticket Contract
- ENTRY_GATE: user explicitly asked to remove the room-level attach/detach seam.
- EXECUTION_BOUNDARY: `RiftSpace`, `StaticRiftSpace`, `Rift`, directly affected
  tests, and no unrelated viewer redesign.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_remove_rift_space_public_viewer_attach_detach_seam_task.md
- EXIT_GATE: `RiftSpace` no longer exposes public attach/detach methods, the
  focused validation ring is green, and board routing reflects the task.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removing the seam forces a
  broader Rift/viewer lifecycle redesign.

## Scope Boundaries
- In scope:
  - remove public `RiftSpace.attach_frame_viewer(...)`
  - remove public `RiftSpace.detach_frame_viewer(...)`
  - replace with internal/private room helpers
  - port focused callers/tests
- Out of scope:
  - changing viewer semantics
  - projection semantics

## Story Checklist
- [x] Story: STORY-2026-04-18-rift-space-viewer-attachment-seam-cleanup
- [ ] Enforce Ticket Microcycle across linked work.

## Notes
- DATETIME: 2026-04-18T22:01:03Z
  TYPE: FACT
  CLAIM: The bounded room-level viewer seam cleanup epic is now implemented and
    waiting on user review.
  EVIDENCE:
  - tickets/stories/2026-04-18_rift_space_viewer_attachment_seam_cleanup_story.md:1-90
  IMPACT: No further implementation is needed in this epic unless the user asks
    for more room/viewer lifecycle cleanup.
  NEXT: hold for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-04-18T20:56:00Z
  TYPE: FACT
  CLAIM: The room-level attach/detach seam is currently used only by
    `Rift.attach_frame_viewer(...)`, `StaticRiftSpace` wrapping, and focused
    tests. It is not part of `IRiftSpace`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:554-624
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:370-406
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:93-108
  - tests/unit/melder/aether/test_rift_space.py:114-122
  - tests/unit/melder/aether/test_static_rift_space.py:18-38
  IMPACT: We can remove the public room seam cleanly without widening into broader viewer redesign.
  NEXT: implement the bounded seam cleanup task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This epic tracks the bounded removal of the room-level public viewer
attach/detach seam.