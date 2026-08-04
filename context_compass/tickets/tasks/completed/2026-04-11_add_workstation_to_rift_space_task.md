# Task: Add Workstation To Rift Space
- Completed: 2026-04-13T11:34:18Z
- Summary: Closed the first room-local workstation slice after later room/runtime work confirmed it as settled foundation.

## Metadata
- Task ID: TASK-2026-04-11-add-workstation-to-rift-space
- Story: STORY-2026-04-11-add-workstation-to-rift-space
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T15:34:59Z
- Updated: 2026-04-13T11:34:18Z

## Objective
Add a room-local workstation object to `RiftSpace` that stores saved bindings,
tracks the active target, and exposes local target operations such as
`clear_target`, `cleanup_target`, and `call_target`.

## Ticket Contract
- ENTRY_GATE: the workstation responsibility split was agreed explicitly, and
  this slice is limited to workstation state/lifecycle only.
- EXECUTION_BOUNDARY: workstation object, `RiftSpace` integration, interface
  updates, focused tests, and ticket sync only.
- DEPENDENCIES:
  - tickets/stories/2026-04-11_add_workstation_to_rift_space_story.md
  - system_docs/patches/active/rift_space_workstation/architecture_patch.md
  - system_docs/patches/active/rift_space_workstation/component_patch_workstation.md
  - system_docs/patches/active/rift_space_workstation/component_patch_rift_space.md
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: `RiftSpace` owns a workstation, the workstation object is fully
  integrated into cleanup/lifecycle, and the focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the workstation needs the
  command system in the same slice to be coherent.

## Scope Boundaries
- In scope:
  - workstation class
  - binding stores for objects, attributes, and methods
  - target selection and release
  - `cleanup_target(*method_names)`
  - `call_target(..., bind_as_name=..., bind_as_store=...)`
  - `RiftSpace` ownership/integration
  - focused tests
- Out of scope:
  - command/discovery system
  - ACL enforcement
  - dynamic codegen execution context

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved implementing the workstation
  before the command system.

## Steps / Checklist
- [ ] Re-open `RiftSpace`, interfaces, and current Rift tests.
- [ ] Create patch docs for the workstation slice.
- [ ] Add `Workstation`.
- [ ] Integrate `RiftSpace` ownership/cleanup.
- [ ] Add/update focused tests.
- [ ] Record findings, implementation, and validation in `## Notes`.

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/rift_space_workstation/architecture_patch.md
  - system_docs/patches/active/rift_space_workstation/component_patch_workstation.md
  - system_docs/patches/active/rift_space_workstation/component_patch_rift_space.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until workstation semantics are merged into canonical docs or intentionally retired.

## Notes
- DATETIME: 2026-04-11T15:38:35Z
  TYPE: FACT
  CLAIM: The room-local workstation slice is now landed in source. The runtime
    has a dedicated `Workstation` object with separate object/attribute/method
    stores, active-target state, target release/clear/cleanup operations, and
    `call_target(...)` with optional result binding. `RiftSpace` now owns and
    cleans that workstation, and the interface surface now exposes it as a
    first-class room-local canvas.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/workstation.py:8-443
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:5-238
  - src/melder/utilities/interfaces/interfaces.py:6154-6302
  IMPACT: `RiftSpace` now has the local canvas we need before building the
    command/discovery system or wiring dynamic codegen execution context.
  NEXT: run the focused Rift/Nexus unit slice and confirm the workstation
    integration stays green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T15:38:35Z
  TYPE: MEASURE
  CLAIM: The focused workstation slice is green. The new workstation tests and
    the existing `RiftSpace` room tests pass together in the focused
    `test_nexus.py` slice.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:713-836
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py` -> 58 passed
  IMPACT: The first workstation-only cut is ready for review. The next logical
    move is to build the command/discovery system on top of this room-local
    canvas.
  NEXT: review the workstation slice and choose the first command-system/tools
    slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T15:34:59Z
  TYPE: PLAN
  CLAIM: The workstation slice should be purely room-local. It stores saved
    bindings and an active target and exposes operations against those saved
    bindings only. It should not discover Melder/Rift targets and should not
    own command-system behavior yet.
  EVIDENCE:
  - user_instruction: "the workstation is only responsible for retaining objects and using the objects you've saved there"
  - user_instruction: "the command system is responsible for all the available commands"
  - user_instruction: "we should still talk it out"
  IMPACT: The workstation class can be implemented now without dragging in
    selector, ACL, or command-system design.
  NEXT: create the patch docs and then implement the workstation object plus
    `RiftSpace` integration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:34:18Z
  TYPE: DECISION
  CLAIM: The workstation foundation slice is complete and can move to the
    completed lane. The later reference-mode, queue, and lock-hardening slices
    all build on this landed workstation substrate, and the user explicitly
    asked to clean up older finished tickets.
  EVIDENCE:
  - tickets/tasks/2026-04-11_add_workstation_reference_modes_to_rift_space_task.md:1-142
  - tickets/tasks/2026-04-11_add_rift_space_event_queue_and_weak_binding_events_task.md:1-162
  - tickets/tasks/2026-04-11_harden_rift_space_and_workstation_locking_task.md:1-157
  - codex/context_compass/system_docs/src_components.md:699-756
  IMPACT: The workstation base task no longer needs to remain in active review
    state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task adds the workstation object to `RiftSpace` only.
