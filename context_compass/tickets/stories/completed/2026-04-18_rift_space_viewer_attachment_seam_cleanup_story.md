# Story: Rift Space Viewer Attachment Seam Cleanup
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-18-rift-space-viewer-attachment-seam-cleanup
- Epic: EPIC-2026-04-18-rift-space-viewer-attachment-seam-cleanup
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-18T20:56:00Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a runtime maintainer, I want `RiftSpace` to stop exposing public
attach/detach viewer methods, so that viewer replacement is treated as an
internal room lifecycle operation instead of a public room API seam.

## Value / MRP Alignment
This keeps room APIs smaller and more honest while preserving the actual viewer
replacement behavior the runtime needs.

## Ticket Contract
- ENTRY_GATE: bounded cleanup approved by the user.
- EXECUTION_BOUNDARY: room viewer replacement seam, Rift caller update, and
  focused tests only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_remove_rift_space_public_viewer_attach_detach_seam_task.md
- EXIT_GATE: `RiftSpace` public attach/detach seam is gone, focused validation
  is green, and the task is ready for review.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the cleanup forces a broader
  viewer lifecycle redesign.

## Requirements (Functional)
- `RiftSpace` must not expose public attach/detach viewer methods.
- viewer replacement/cleanup must still work internally.
- `StaticRiftSpace` must still wrap plain viewers into `StaticFrameViewer`.
- `Rift` must keep a valid orchestration path for attaching a freshly built viewer.

## Requirements (Non-Functional)
- No backward-compat shim for the removed room-level seam.
- Keep the patch scoped and reviewable.

## Scope Boundaries
- In scope:
  - room seam cleanup
  - focused callers/tests
- Out of scope:
  - viewer semantic redesign
  - projection redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: investigation showed the seam is local and removable, and
  the user explicitly requested its removal.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-18-remove-rift-space-public-viewer-attach-detach-seam - remove the room-level public seam and port callers/tests
- [ ] Enforce Ticket Microcycle across linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `RiftSpace` no longer has public attach/detach viewer methods.
- Runtime caller path still replaces viewers correctly.
- Focused tests pass.

## Validation / Test Plan
- `python -m py_compile ...`
- `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Mitigations
- Risk: tests currently overfit to the public room seam.
  Mitigation: port them to the internal room helper or the Rift-level path.

## Notes
- DATETIME: 2026-04-18T22:01:03Z
  TYPE: FACT
  CLAIM: The child task landed the bounded room-level viewer seam cleanup and
    the focused ring is green.
  EVIDENCE:
  - tickets/tasks/2026-04-18_remove_rift_space_public_viewer_attach_detach_seam_task.md:1-170
  IMPACT: The story is ready for review instead of further implementation.
  NEXT: wait for acceptance or a bounded follow-on request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-04-18T20:56:00Z
  TYPE: PLAN
  CLAIM: The bounded cleanup is to make viewer replacement internal to
    `RiftSpace`, leave `Rift` as the external orchestration point, and port the
    focused tests away from the room's old public attach/detach methods.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:554-624
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:370-406
  - tests/unit/melder/aether/test_rift_space.py:114-122
  IMPACT: This keeps the seam cleanup small and avoids reopening viewer design.
  NEXT: implement the task and validate the focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
This story tracks the bounded removal of the room-level public viewer
attach/detach seam.