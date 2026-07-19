# Task: Cleanup RiftSpace Viewer Target Surface
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-cleanup-rift-space-viewer-target-surface
- Story: STORY-2026-04-18-rift-space-viewer-attachment-seam-cleanup
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T22:10:00Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Remove the remaining viewer-backed and selected-target room methods from
`RiftSpace` so the room stops proxying viewer behavior and stops carrying dead
selected-target state.

## Ticket Contract
- ENTRY_GATE: user explicitly identified these room methods as wrong and asked
  for investigation plus cleanup.
- EXECUTION_BOUNDARY: `RiftSpace`, `IRiftSpace`, directly affected tests, and
  focused integration helpers only.
- DEPENDENCIES:
  - tickets/epics/2026-04-18_rift_space_viewer_attachment_seam_cleanup_epic.md
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_rift_space.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: the room no longer proxies viewer-target methods or stores
  selected-target state, and the focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a real runtime caller depends
  on the room-owned selected-target behavior.

## Scope Boundaries
- In scope:
  - remove room methods:
    - `list_frame_names`
    - `list_available_targets`
    - `describe_available_targets`
    - `get_required_frame_viewer`
    - `list_selected_target_ids`
    - `select_target`
    - `clear_selected_targets`
    - `describe_selected_targets`
  - remove `_selected_target_ids_by_frame_name`
  - remove matching `IRiftSpace` methods
  - port focused callers/tests
- Out of scope:
  - redesigning viewer methods
  - redesigning command methods
  - adding replacement target-selection systems

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: investigation showed the selected-target state is dead
  outside `RiftSpace` and the viewer-backed room methods are only proxy seams.

## Steps / Checklist
- [x] Remove the viewer-backed and selected-target methods from `RiftSpace`.
- [x] Remove `_selected_target_ids_by_frame_name` from room state and cleanup.
- [x] Remove the matching methods from `IRiftSpace`.
- [x] Port focused callers/tests to viewer/property/projection access or delete obsolete tests.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- slimmer `RiftSpace` surface
- no dead selected-target room state
- updated focused tests/helpers

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_rift_space.py
- tests/unit/melder/aether/test_nexus.py
- tests/integration/melder/aether/rift/static_rift_json_testbench_support.py
- tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_nexus.py tests/integration/melder/aether/rift/static_rift_json_testbench_support.py tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py`
- `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py`
- Result: `340 passed`

## Risks / Rollback Notes
- Risk: tests or helpers still assume the room proxies viewer behavior.
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
- DATETIME: 2026-04-18T22:21:20Z
  TYPE: FACT
  CLAIM: `RiftSpace` no longer proxies viewer methods or owns selected-target
    state. The room now holds only viewer/projection ownership plus the other
    real room systems.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-614
  - src/melder/utilities/interfaces/interfaces.py:7488-7570
  IMPACT: The room surface is materially smaller and no longer pretends to be a
    target-selection API.
  NEXT: hold for review unless the next cleanup is explicit `frame_name`
    enforcement end-to-end.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T22:21:20Z
  TYPE: MEASURE
  CLAIM: The focused room/runtime ring is green after removing the viewer-backed
    and selected-target room surface.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_nexus.py tests/integration/melder/aether/rift/static_rift_json_testbench_support.py tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py` -> 340 passed
  IMPACT: The bounded room-surface cleanup is stable enough to review.
  NEXT: wait for user acceptance or the next bounded frame-target cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T22:10:00Z
  TYPE: FACT
  CLAIM: The room-owned selected-target map is dead outside `RiftSpace`
    itself, and the viewer-backed room methods are only proxy seams into the
    attached viewer.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:523-771
  - src/melder/utilities/interfaces/interfaces.py:7526-7599
  - tests/unit/melder/aether/test_rift_space.py:126-193
  - tests/unit/melder/aether/test_nexus.py:3483-3547
  IMPACT: We can remove this room surface cleanly instead of trying to move it.
  NEXT: patch the room and interface, then port the focused callers/tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task removes the remaining viewer-backed and selected-target room surface
from `RiftSpace`.