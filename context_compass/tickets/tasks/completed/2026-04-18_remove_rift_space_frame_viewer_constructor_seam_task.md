# Task: Remove RiftSpace Frame Viewer Constructor Seam
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-remove-rift-space-frame-viewer-constructor-seam
- Story: STORY-2026-04-18-rift-space-frame-viewer-constructor-cleanup
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-18T20:49:23Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Remove the optional `frame_viewer` constructor seam from `RiftSpace` so viewers
attach only through the explicit runtime attachment path.

## Ticket Contract
- ENTRY_GATE: user approved the bounded cleanup after investigation.
- EXECUTION_BOUNDARY: `RiftSpace`, `StaticRiftSpace`, `CapabilityRiftSpace`,
  `CodegenRiftSpace`, and directly affected tests only.
- DEPENDENCIES:
  - tickets/stories/2026-04-18_rift_space_frame_viewer_constructor_cleanup_story.md
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py
  - tests/unit/melder/aether/test_rift_space.py
- EXIT_GATE: no constructor accepts `frame_viewer`, focused validation is
  green, and board/task state is synced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a real runtime dependency on
  constructor-time viewer injection is discovered.

## Scope Boundaries
- In scope:
  - remove `frame_viewer` constructor arg and initialization
  - keep explicit `attach_frame_viewer(...)`
  - port focused tests
- Out of scope:
  - viewer redesign
  - projection redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the investigation proved the seam is dead and the user
  approved removing it.

## Steps / Checklist
- [x] Remove `frame_viewer` constructor injection from `RiftSpace`.
- [x] Remove any constructor pass-through from concrete room subclasses.
- [x] Port focused tests to the explicit attach path.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- room construction without constructor-time viewer injection
- updated focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/aether/nexus/rift/rift_space/static_rift_space.py
- src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
- src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py
- tests/unit/melder/aether/test_rift_space.py

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py tests/unit/melder/aether/test_rift_space.py`
- `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_nexus.py`
- Result: `117 passed`

## Risks / Rollback Notes
- Risk: one focused test still assumes constructor-time injection.
- Rollback: none planned; this lane is explicitly no-backward-compat.

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
- DATETIME: 2026-04-18T20:51:04Z
  TYPE: FACT
  CLAIM: `RiftSpace` now always starts with no attached viewer, and the dead
    `frame_viewer` constructor seam is gone from room construction.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:103-145
  - tests/unit/melder/aether/test_rift_space.py:14-22
  IMPACT: Room construction now matches the real runtime lifecycle where
    viewers attach later through `attach_frame_viewer(...)`.
  NEXT: hold the task for review/acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T20:51:04Z
  TYPE: MEASURE
  CLAIM: The focused room/viewer constructor cleanup ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py tests/unit/melder/aether/test_rift_space.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_nexus.py` -> 117 passed
  IMPACT: The constructor cleanup is stable enough to review.
  NEXT: wait for user acceptance or the next bounded room cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T20:49:23Z
  TYPE: FACT
  CLAIM: No real runtime path constructs a room with `frame_viewer=`; the seam
    is only a constructor convenience plus one unit-test tether.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:103-160
  - src/melder/aether/nexus/rift/rift.py:554-624
  - src/melder/aether/nexus/nexus.py:1923-2071
  - tests/unit/melder/aether/test_rift_space.py:14-24
  IMPACT: We can remove the seam cleanly and rely only on explicit viewer attachment.
  NEXT: patch the room constructors and focused test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task removes the dead constructor-time viewer seam while keeping the live
`attach_frame_viewer(...)` path intact.