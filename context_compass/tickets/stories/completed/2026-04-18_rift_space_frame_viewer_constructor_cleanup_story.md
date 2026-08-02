# Story: Rift Space Frame Viewer Constructor Cleanup
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-18-rift-space-frame-viewer-constructor-cleanup
- Epic: EPIC-2026-04-18-rift-space-frame-viewer-constructor-cleanup
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-18T20:49:23Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a runtime maintainer, I want `RiftSpace` to be created without a viewer
constructor seam, so that room creation and viewer attachment follow the real
runtime lifecycle.

## Value / MRP Alignment
This removes misleading construction state from a core room object and keeps
the room lifecycle honest.

## Ticket Contract
- ENTRY_GATE: bounded cleanup approved by the user.
- EXECUTION_BOUNDARY: room constructors, room lifecycle docs, and focused
  tests only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_remove_rift_space_frame_viewer_constructor_seam_task.md
- EXIT_GATE: no room constructor accepts `frame_viewer`, tests are ported, and
  the task is ready for review.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any real runtime path still
  depends on constructor-time viewer injection.

## Requirements (Functional)
- `RiftSpace` must always start with no attached viewer.
- Viewers must be attached only through `attach_frame_viewer(...)`.
- Concrete room subclasses must not accept or forward `frame_viewer`.

## Requirements (Non-Functional)
- No backward-compat shim for the removed constructor arg.
- Keep the patch scoped and reviewable.

## Scope Boundaries
- In scope:
  - room constructor cleanup
  - focused tests
- Out of scope:
  - viewer semantics beyond attachment lifecycle
  - projection/runtime redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: investigation showed the seam is dead and the user
  approved removing it.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-18-remove-rift-space-frame-viewer-constructor-seam - remove the constructor seam and port tests
- [ ] Enforce Ticket Microcycle across linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `RiftSpace` and room subclasses no longer accept `frame_viewer`.
- Focused tests pass without constructor-time viewer injection.

## Validation / Test Plan
- `python -m py_compile ...`
- `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_nexus.py`

## Risks / Mitigations
- Risk: a hidden test still assumes constructor-time injection.
  Mitigation: search all source/tests for `frame_viewer=` before patching.

## Notes
- DATETIME: 2026-04-18T20:51:04Z
  TYPE: FACT
  CLAIM: The child task landed the bounded room-constructor cleanup and the
    focused room ring is green.
  EVIDENCE:
  - tickets/tasks/2026-04-18_remove_rift_space_frame_viewer_constructor_seam_task.md:1-150
  IMPACT: The story is ready for review instead of further implementation.
  NEXT: wait for acceptance or a bounded follow-on request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-04-18T20:49:23Z
  TYPE: PLAN
  CLAIM: The bounded cleanup is to remove constructor-time `frame_viewer`,
    keep explicit viewer attachment, and port the focused tests accordingly.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:103-160
  - tests/unit/melder/aether/test_rift_space.py:14-24
  IMPACT: The story stays small and does not reopen viewer/runtime design.
  NEXT: implement the task and validate the focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
This story tracks the removal of the dead constructor-time viewer seam from
room construction.