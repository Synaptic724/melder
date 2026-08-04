# Task: Implement RiftSpace Target Selection Context
- Completed: 2026-04-09T11:31:39Z
- Summary: Added selected-target context to RiftSpace over the hosted viewer without widening into execution.


## Metadata
- Task ID: TASK-2026-04-06-implement-rift-space-target-selection-context
- Story: STORY-2026-04-06-contract-backed-assigned-frame-views
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T15:50:03Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Add a small target-selection context to `RiftSpace` so the workspace can hold a
selected-target surface over the hosted viewer for later codegen use, without
implementing codegen itself in this slice.

## Ticket Contract
- ENTRY_GATE: the hosted frame-surface chain and direct `RiftSpace`
  delegation are landed.
- EXECUTION_BOUNDARY: selection state over the hosted viewer only.
- DEPENDENCIES:
  - codex/context_compass/tickets/tasks/2026-04-06_implement_rift_space_frame_surface_delegation.md
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: `RiftSpace` can hold and describe selected targets over the hosted
  viewer and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the clean selection model
  requires a broader codegen/runtime design in the same slice.

## Scope Boundaries
- In scope:
  - target selection state on `RiftSpace`
  - selection helpers over the hosted viewer
  - interface updates
  - focused unit tests
- Out of scope:
  - codegen execution
  - raw runtime object binding
  - broader workspace redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the selection-context slice is implemented, the focused
  tests passed, and the task is ready for review.

## Steps / Checklist
- [ ] Add selected-target state to `RiftSpace`.
- [ ] Add hosted-viewer-backed selection/description helpers.
- [ ] Update the interface contract.
- [ ] Add/update focused tests.
- [ ] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- `RiftSpace` target selection context
- interface updates
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`

## Risks / Rollback Notes
- Risk: the selection layer drifts into real object binding or codegen.
  Rollback: keep selection state on view-safe target identities/descriptions
  only.

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
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T15:50:03Z
  TYPE: PLAN
  CLAIM: The smallest codegen-facing workspace step is target selection state,
    not codegen execution. The host seam now exists on `RiftSpace`, so the next
    bounded cut is to let the space remember selected targets over the hosted
    viewer and expose those selections as view-safe descriptions for later
    codegen consumption.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:18-245
  - user_instruction: "The next clean move is: start the codegen-facing workspace use path next."
  IMPACT: This gives the workspace a real target-selection surface without
    widening into raw object binding or execution yet.
  NEXT: add selected-target state and hosted-viewer-backed selection helpers to
    `RiftSpace`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:50:03Z
  TYPE: FACT
  CLAIM: The codegen-facing workspace preparation layer is now in code as a
    selection context on `RiftSpace`. The space now owns selected target ids by
    frame and exposes:
    - `list_selected_target_ids(...)`
    - `select_target(...)`
    - `clear_selected_targets(...)`
    - `describe_selected_targets(...)`
    These operate only on view-safe target identities/descriptions pulled from
    the hosted viewer, so the slice prepares for later codegen use without
    widening into raw object binding or execution.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:18-329
  - src/melder/utilities/interfaces/interfaces.py:5942-6050
  IMPACT: `RiftSpace` now has a real selected-target surface over the hosted
    viewer instead of only a passive viewer attachment.
  NEXT: run the focused host/selection tests and confirm the new selection
    layer holds.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:50:03Z
  TYPE: MEASURE
  CLAIM: The focused selection-context slice is green. The targeted
    unit/integration surface covering `RiftSpace`, `Rift`, `FrameViewer`, and
    the Nexus projection path passed cleanly after adding the selected-target
    context to the space host.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:520-650
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The workspace-facing host now supports target selection and is stable
    enough to review as the next bounded frame-surface slice.
  NEXT: review whether the next cut should start binding selected targets into a
    codegen-facing workspace context or deepen selection semantics further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

