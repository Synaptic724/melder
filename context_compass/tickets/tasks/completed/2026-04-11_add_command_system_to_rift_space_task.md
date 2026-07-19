# Task: Add Command System To Rift Space
- Completed: 2026-04-13T11:34:18Z
- Summary: Closed the first room-local command-system slice after later ACL and room-mode work confirmed it as settled base infrastructure.

## Metadata
- Task ID: TASK-2026-04-11-add-command-system-to-rift-space
- Story: STORY-2026-04-11-add-command-system-to-rift-space
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T16:01:14Z
- Updated: 2026-04-13T11:34:18Z

## Objective
Add a room-local command system to `RiftSpace` that performs controlled
getter/execute operations against viewer targets and workstation bindings
without owning persistence itself.

## Ticket Contract
- ENTRY_GATE: the workstation is landed, the responsibility split is agreed,
  and patch docs exist for the system-impacting command-system slice.
- EXECUTION_BOUNDARY: command-system object, `RiftSpace` integration, interface
  updates, focused tests, and ticket sync only.
- DEPENDENCIES:
  - tickets/stories/2026-04-11_add-command-system-to-rift-space_story.md
  - system_docs/patches/active/rift_space_command_system/architecture_patch.md
  - system_docs/patches/active/rift_space_command_system/component_patch_command_system.md
  - system_docs/patches/active/rift_space_command_system/component_patch_rift_space.md
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/frame_viewer/
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: `RiftSpace` owns a command system, the first controlled
  getter/execute surface is live, and the focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the first cut requires ACL
  enforcement or target-aware command configuration in the same tranche.

## Scope Boundaries
- In scope:
  - command system object
  - `RiftSpace` ownership/integration
  - first getter surface for viewer-selected targets
  - first execute surface against viewer-selected/bound targets
  - focused tests
- Out of scope:
  - ACL enforcement
  - command discovery/describe APIs
  - dynamic codegen execution context
  - full static/capability command policy

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved building the command system
  next on top of the workstation.

## Steps / Checklist
- [ ] Inspect live viewer target objects and selected-target flow.
- [ ] Create patch docs for the command-system slice.
- [ ] Add command system object.
- [ ] Integrate it into `RiftSpace`.
- [ ] Add/update focused tests.
- [ ] Record findings, implementation, and validation in `## Notes`.

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/rift_space_command_system/architecture_patch.md
  - system_docs/patches/active/rift_space_command_system/component_patch_command_system.md
  - system_docs/patches/active/rift_space_command_system/component_patch_rift_space.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the command-system model is merged into canonical docs or intentionally retired.

## Notes
- DATETIME: 2026-04-11T16:31:16Z
  TYPE: FACT
  CLAIM: The general command-system surface is now materially fuller. On top of
    the earlier selected-target record getters and workstation-target member
    operations, the command system now exposes runtime-object getters:
    - `get_selected_target_runtime_object(...)`
    - `get_conduit_object_by_id(...)`
    - `get_conduit_object_by_name(...)`
    - `get_spell_object_by_source_id(...)`
    - `get_spell_object_by_id(...)`
    The conduit getter now falls back through lesser-conduit lineage traversal
    when root/normal lookup misses, so the command system can use the richer
    lesser-conduit topology we just published into the descriptor.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system.py:10-410
  - tests/unit/melder/aether/test_nexus.py:877-1042
  IMPACT: The room now has a genuinely useful general command surface before
    ACL enforcement is layered on top.
  NEXT: rerun the focused Rift/Nexus unit slice and confirm the expanded
    command-system surface stays green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T16:31:16Z
  TYPE: MEASURE
  CLAIM: The expanded command-system slice is green. The new runtime-object
    getter tests pass together with the earlier workstation and selected-target
    command tests in the focused `test_nexus.py` slice.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:840-1042
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py` -> 66 passed
  IMPACT: The general command system is ready for review. The next logical
    step is to start layering command ACL constraints onto this surface.
  NEXT: review the completed general command-system surface and choose the
    first ACL-enforcement slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T16:07:59Z
  TYPE: FACT
  CLAIM: The first command-system slice is now landed in source. `RiftSpace`
    owns a `CommandSystem` sibling beside the workstation. The command system
    now provides:
    - `get_selected_target_link(...)`
    - `get_selected_target_record(...)`
    - `get_target_attribute(...)`
    - `get_target_method(...)`
    - `execute_target_method(...)`
    It resolves selected targets through the attached viewer and uses the
    workstation target for attribute/method getters and explicit method
    execution. It does not own persistence, discovery/describe APIs, or ACL
    enforcement in this cut.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system.py:9-353
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:5-265
  - src/melder/utilities/interfaces/interfaces.py:6247-6375
  IMPACT: `RiftSpace` now has the first real command layer on top of the
    workstation without smearing viewer discovery and workstation persistence
    together.
  NEXT: run the focused Rift/Nexus unit slice and confirm the command-system
    integration stays green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T16:07:59Z
  TYPE: MEASURE
  CLAIM: The focused command-system slice is green. The new command-system
    tests and the existing `RiftSpace`/workstation room tests pass together in
    the focused `test_nexus.py` unit slice.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:822-940
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py` -> 63 passed
  IMPACT: The first command-system cut is ready for review. The next logical
    move is to add the first runtime-object getters or the first ACL-shaped
    command-policy constraints on top of this surface.
  NEXT: review the command-system slice and choose the next command/runtime
    cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T16:01:14Z
  TYPE: PLAN
  CLAIM: The first command-system cut should be getter/execute only. Viewer
    discovery remains with the viewer, and workstation persistence remains with
    the workstation. The command system should therefore resolve and execute,
    then let callers bind results explicitly into the workstation when they
    want persistence.
  EVIDENCE:
  - user_instruction: "viewer takes care of that"
  - user_instruction: "it should be getters they can just use with bind"
  - user_instruction: "getters is all you get in command registry and you can execute methods and execute things right here"
  IMPACT: The first command-system slice can avoid command discovery APIs and
    keep the runtime surface narrow.
  NEXT: inspect the live `RiftSpace` selected-target and viewer target model,
    then choose the exact first getter/execute methods.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T16:01:14Z
  TYPE: FACT
  CLAIM: The live command seams are narrow enough for a clean first cut.
    `RiftSpace` already owns selected viewer target ids and can resolve
    `FrameLink` entries through the attached viewer. `FrameViewer` already has
    internal helpers for resolving conduit/spell records by source ids. On the
    runtime side, `Conduit` already exposes concrete helpers for
    `get_conduit_by_id`, `get_conduit_by_name`, `get_spell_by_id`,
    `find_spell_id`, and `find_spell_key`. The first command-system slice can
    therefore stay on:
    - selected-target getters over the viewer/descriptor surface
    - workstation-target attribute/method getters
    - explicit target-method execution
    without adding command discovery APIs or binding APIs.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:122-398
  - src/melder/aether/nexus/rift/frame_link/frame_link.py:1-177
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:3000-3049
  - src/melder/aether/conduit/conduit.py:1593-1718
  - src/melder/aether/conduit/conduit.py:2705-2750
  - tests/unit/melder/aether/test_nexus.py:745-788
  - tests/unit/melder/aether/conduit/test_conduit_facade.py:259-376
  - tests/unit/melder/aether/conduit/test_conduit_facade.py:479-530
  - tests/unit/melder/aether/conduit/test_conduit_facade.py:959-1047
  IMPACT: The command system can be implemented now without dragging in ACL
    enforcement or a second discovery layer.
  NEXT: implement the command-system object and wire the first selected-target
    getters plus workstation-target method execution into `RiftSpace`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:34:18Z
  TYPE: DECISION
  CLAIM: The first command-system slice is complete and can move to the
    completed lane. Later room-mode gating, shared manual-runtime expansion,
    and capability work all treat this command system as landed foundation
    rather than pending review work.
  EVIDENCE:
  - tickets/tasks/2026-04-12_refactor_rift_space_to_mode_specific_command_systems_task.md:1-153
  - tickets/tasks/2026-04-12_expand_shared_command_system_manual_runtime_surface_task.md:1-170
  - codex/context_compass/system_docs/src_components.md:738-756
  IMPACT: The initial command-system task no longer belongs on the active
    board.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task adds the first room-local command system on top of `RiftSpace` and
the workstation only.
