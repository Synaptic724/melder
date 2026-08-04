# Task: Implement Command System Room Mode Runtime Gating
- Completed: 2026-04-13T11:43:06Z
- Summary: Archived the historical room-mode runtime-gating slice after later capability work superseded the capability half of the boundary.

## Metadata
- Task ID: TASK-2026-04-12-implement-command-system-room-mode-runtime-gating
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T10:39:05Z
- Updated: 2026-04-13T11:43:06Z

## Objective
Enforce the current Rift room-mode contract in `CommandSystem` so `static` and
`capability` spaces do not expose raw runtime-object getters while `dynamic`
keeps the current ACL-gated runtime getter behavior.

## Ticket Contract
- ENTRY_GATE: the command ACL access-enforcement slice is landed and green, the
  user explicitly asked to continue, and the access-mode artifact still says
  `static` and `capability` should not expose raw runtime power.
- EXECUTION_BOUNDARY: room-mode artifact/ticket sync, `CommandSystem`, focused
  `RiftSpace`/Nexus tests, patch docs, and board/artifact routing only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-12_implement_command_acl_access_enforcement_in_command_system_task.md
  - tickets/tasks/2026-04-11_design_command_acl_enforcement_plan.md
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
  - src/melder/aether/nexus/rift/rift_space/command_system.py
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: static/capability rooms fail fast on raw runtime-object getters,
  dynamic keeps ACL-gated runtime getter behavior, and the focused runtime ring
  is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if room-mode gating requires a
  new handle/proxy surface instead of a narrow command-system policy change.

## Scope Boundaries
- In scope:
  - room-mode gating for raw runtime-object getters in `CommandSystem`
  - selected-target runtime-object gating
  - direct conduit/spell runtime-object getter gating
  - focused tests
- Out of scope:
  - workstation-bound object policing after bind
  - new handle/proxy wrapper systems
  - capability handle lifecycle design
  - ACL/compiler schema changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the focused command ACL slice is green, and the next
  runtime gap is room-mode gating for raw object exposure.

## Steps / Checklist
- [x] Stage patch docs and route the new task from the board.
- [x] Enforce room-mode gating on selected-target runtime-object access.
- [x] Enforce room-mode gating on direct conduit/spell runtime-object getters.
- [x] Update focused tests for static/capability vs dynamic behavior.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- room-mode-gated raw runtime-object access in `CommandSystem`
- focused room-mode tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/command_system.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: we overreach and start policing workstation-bound objects again.
  Rollback: keep the slice limited to raw runtime-object getters in
  `CommandSystem` and leave workstation-bound objects alone.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/command_system_room_mode_runtime_gating/architecture_patch.md
  - system_docs/patches/active/command_system_room_mode_runtime_gating/component_patch_command_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until room-mode runtime gating is merged into canonical
  ACL/runtime docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T10:39:05Z
  TYPE: FACT
  CLAIM: The current command ACL slice now cleanly gates frame/conduit/spell
    access by compiled ACL state, but room mode still does not shape raw
    runtime-object getters. The access-mode artifact and earlier command
    design task still say:
    - `static` should not expose raw runtime-object getters
    - `capability` should stay out of naked raw-object exposure until a better
      handle/capability surface exists
    So the next narrow runtime slice is room-mode gating on the raw
    runtime-object getters already exposed by `CommandSystem`.
  EVIDENCE:
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md:33-59
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md:72-108
  - tickets/tasks/2026-04-11_design_command_acl_enforcement_plan.md:60-76
  - src/melder/aether/nexus/rift/rift_space/command_system.py:220-517
  IMPACT: We can keep the next slice narrow and honest:
    - no new ACL schema
    - no workstation policing
    - no fake capability wrappers
    just raw runtime-object gating by room kind.
  NEXT: create the patch docs and route the board to this room-mode runtime task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T10:41:56Z
  TYPE: FACT
  CLAIM: The room-mode runtime slice is now landed in source. `CommandSystem`
    now blocks raw runtime-object getters in:
    - `static`
    - `capability`
    while leaving `base` and `dynamic` behavior unchanged. The gated surface is
    limited to:
    - `get_selected_target_runtime_object(...)`
    - direct conduit runtime-object getters
    - direct spell runtime-object getters
    Descriptor/record access and already-bound workstation objects remain
    outside this gate.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system.py:223-537
  - src/melder/aether/nexus/rift/rift_space/command_system.py:699-736
  - tests/unit/melder/aether/test_nexus.py:1586-1636
  IMPACT: The runtime now matches the current access-mode direction more
    honestly without inventing a wrapper/handle system we do not have yet.
  NEXT: validate the focused room-mode runtime ring and record the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T10:41:56Z
  TYPE: MEASURE
  CLAIM: The room-mode runtime gating slice is green on the focused and nearby
    ACL/Nexus/runtime rings. The updated static/capability denial tests pass,
    and the nearby ACL/viewer/compiler ring still passes with the new room-mode
    checks in place.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py` -> 82 passed
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py` -> 161 passed
  IMPACT: This tranche is ready for review or for the next runtime design step,
    not more local stabilization.
  NEXT: summarize the landed room-mode behavior and ask for the next direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:43:06Z
  TYPE: DECISION
  CLAIM: This task is now historical rather than current. The static half of
    the room-mode boundary still matters, but the capability half was later
    superseded by the explicit capability-room model and the composed
    `CapabilityCommandSystem`, which now allows broad manual runtime access.
  EVIDENCE:
  - tickets/epics/2026-04-12_capability_rift_space_runtime_model_epic.md:13-37
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py:6-23
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:9-97
  IMPACT: The task should not remain in active review state because its
    objective no longer matches the live capability runtime contract.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task applies the next runtime boundary after command ACL access gating:
room-mode control over raw runtime-object exposure in `CommandSystem`.
