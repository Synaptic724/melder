# Story: Contract-Backed Assigned Frame Views
- Completed: 2026-04-09T21:59:36Z
- Summary: Closed the downstream assigned-frame-view story after its child implementation tasks were already completed.


## Metadata
- Story ID: STORY-2026-04-06-contract-backed-assigned-frame-views
- Epic: EPIC-2026-04-06-rift-assigned-frame-view-availability-and-hosted-viewer
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T14:31:44Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Implement the first real runtime chain where Rift-assigned frames become
contract-backed available views, and each assigned `FrameView` owns the full
filtered target surface for its frame.

## Ticket Contract
- ENTRY_GATE: the epic is active and the user explicitly approved building the
  chain instead of discussing more ownership models.
- EXECUTION_BOUNDARY: assigned views and frame-local available-target surfaces.
- DEPENDENCIES:
  - codex/context_compass/tickets/epics/2026-04-06_rift_assigned_frame_view_availability_and_hosted_viewer_epic.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- EXIT_GATE: assigned views exist as a real runtime concept and the viewer only
  consumes those assigned views.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if assigned views require a
  broader contract-class rewrite in the same slice.

## Deliverables
- assigned-view runtime behavior
- frame-local available-target surface
- focused tests

## Notes
- DATETIME: 2026-04-06T14:31:44Z
  TYPE: PLAN
  CLAIM: The first useful runtime cut is not the full workspace model. It is
    the assigned-view layer: contract-backed frame availability, explicit
    `available_views` on the viewer, and frame-local `available_targets` on the
    view.
  EVIDENCE:
  - user_instruction: "the viewer can only see views its been assigned inside it"
  - user_instruction: "the viewbuilder automatically populates available views assigned for that specific frame"
  IMPACT: This story gives the current frame-surface code a real chain without
    widening into unrelated workspace/runtime concerns.
  NEXT: execute the bounded task for assigned views and available targets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

