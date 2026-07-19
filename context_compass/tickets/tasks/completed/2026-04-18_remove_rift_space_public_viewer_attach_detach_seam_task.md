# Task: Remove RiftSpace Public Viewer Attach Detach Seam
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-remove-rift-space-public-viewer-attach-detach-seam
- Story: STORY-2026-04-18-rift-space-viewer-attachment-seam-cleanup
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-18T20:56:00Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Remove the public-looking `attach_frame_viewer(...)` and
`detach_frame_viewer(...)` seam from `RiftSpace` and replace it with internal
viewer replacement helpers.

## Ticket Contract
- ENTRY_GATE: user explicitly requested removal of the room-level public seam.
- EXECUTION_BOUNDARY: `RiftSpace`, `StaticRiftSpace`, `Rift`, and directly
  affected tests only.
- DEPENDENCIES:
  - tickets/stories/2026-04-18_rift_space_viewer_attachment_seam_cleanup_story.md
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py
  - src/melder/aether/nexus/rift/rift.py
  - tests/unit/melder/aether/test_rift_space.py
  - tests/unit/melder/aether/test_static_rift_space.py
- EXIT_GATE: the room-level public attach/detach seam is gone, focused
  validation is green, and board/task state is synced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removing the seam forces a
  broader viewer lifecycle redesign.

## Scope Boundaries
- In scope:
  - remove public room attach/detach methods
  - add internal/private room viewer replacement helpers
  - port focused callers/tests
- Out of scope:
  - projection redesign
  - viewer behavior redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the room-level seam is small, localized, and user-directed
  for removal.

## Steps / Checklist
- [x] Remove public `RiftSpace.attach_frame_viewer(...)`.
- [x] Remove public `RiftSpace.detach_frame_viewer(...)`.
- [x] Replace them with internal/private room viewer replacement helpers.
- [x] Port `Rift` and focused tests to the new path.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- no public room-level attach/detach viewer seam
- internal/private room viewer replacement path
- updated focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/aether/nexus/rift/rift_space/static_rift_space.py
- src/melder/aether/nexus/rift/rift.py
- tests/unit/melder/aether/test_rift_space.py
- tests/unit/melder/aether/test_static_rift_space.py
- tests/unit/melder/aether/test_nexus.py

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`
- `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`
- Result: `129 passed`

## Risks / Rollback Notes
- Risk: a focused test may still overfit to the public room seam.
- Rollback: none planned; this is a bounded no-compat cleanup.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-18T22:01:03Z
  TYPE: FACT
  CLAIM: The room-level public attach/detach seam is gone. `RiftSpace` now
    uses internal `_replace_frame_viewer(...)` / `_clear_frame_viewer(...)`
    helpers, `StaticRiftSpace` overrides the internal replacement hook for
    static wrapping, and `Rift` now calls the internal room path directly.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:370-406
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:93-108
  - src/melder/aether/nexus/rift/rift.py:554-624
  IMPACT: Viewer replacement still works, but it no longer pretends to be a
    public room API.
  NEXT: hold for review/acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T22:01:03Z
  TYPE: MEASURE
  CLAIM: The focused room/viewer seam cleanup ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> 129 passed
  IMPACT: The bounded seam cleanup is stable enough to review.
  NEXT: wait for user acceptance or the next bounded room/viewer follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T20:56:00Z
  TYPE: FACT
  CLAIM: The room-level attach/detach seam is only used by `Rift`, the static
    room wrapper, and focused tests; it is not part of `IRiftSpace`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:554-624
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:370-406
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:93-108
  - tests/unit/melder/aether/test_rift_space.py:114-122
  - tests/unit/melder/aether/test_static_rift_space.py:18-38
  IMPACT: We can remove the public room seam without widening into interface redesign.
  NEXT: implement the private room replacement path and port the focused callers/tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task removes the public room-level attach/detach seam while preserving the
actual viewer replacement behavior the runtime still needs.