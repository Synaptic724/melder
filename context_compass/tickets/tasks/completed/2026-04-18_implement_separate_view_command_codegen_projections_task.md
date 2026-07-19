# Task: Implement Separate View Command And Codegen Projections
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-implement-separate-view-command-codegen-projections
- Story: STORY-2026-04-18-separate-view-command-codegen-projections
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T17:14:19Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Split the current viewer-hosted projection model into separate view, command,
and codegen projections, and make Nexus own the synchronous ACL refresh
cascade for all three.

## Ticket Contract
- ENTRY_GATE: the ACL propagation investigation is complete and the user
  accepted the split direction.
- EXECUTION_BOUNDARY: `Nexus`, `Rift`, `RiftSpace`, frame viewer, command
  system, and the bounded new command/codegen projection objects needed for the
  split.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_investigate_frame_viewer_acl_propagation_and_refresh_task.md
  - tickets/tasks/2026-04-18_implement_rift_gate_and_rift_gate_controller_task.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/command_system/command_system.py
- EXIT_GATE: command no longer depends on viewer state, separate projections
  exist, and Nexus refreshes all downstream surfaces on ACL change.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if command/codegen target
  selection semantics need to change in a way that would widen this slice too
  far.

## Scope Boundaries
- In scope:
  - separate view/command/codegen projections
  - removal of viewer dependency from `CommandSystem`
  - Nexus-owned ACL refresh cascade
  - direct tests/docs needed by the split
- Out of scope:
  - unrelated room/workstation redesign
  - deferred action model

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the investigation made the projection split explicit
  enough to stage the next implementation slice.

## Steps / Checklist
- [x] Add separate command/codegen projection objects parallel to the viewer model.
- [x] Make `Nexus` build view, command, and codegen projections from the selected
      frame contract names.
- [x] Make `RiftSpace` own the three downstream surfaces.
- [x] Remove `CommandSystem` dependence on `FrameViewer`.
- [x] Add explicit ACL refresh hooks for viewer, command, and codegen surfaces.
- [x] Add a Nexus-owned synchronized refresh method that closes impacted
      `RiftGate`s, waits for drain, swaps fresh projections, and then reopens
      the gates.
- [x] Replace unsafe viewer-swap assumptions with the synchronized projection
      refresh path.
- [x] Rewrite the directly affected tests.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- separate view/command/codegen projection model
- command surface decoupled from viewer
- Nexus-owned ACL refresh protocol

## Files / Paths Impacted
- src/melder/aether/nexus/nexus.py
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- src/melder/aether/nexus/rift/command_system/command_system.py

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/projection/view_projection.py src/melder/aether/nexus/rift/projection/command_projection.py src/melder/aether/nexus/rift/projection/codegen_projection.py src/melder/aether/nexus/rift/projection/frame_projection_set.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/nexus.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py src/melder/aether/nexus/rift/command_system/command_system.py src/melder/aether/nexus/rift/command_system/static_command_system.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_gate.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py`
- `python -m pytest -q tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_gate.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py`
- Result: `290 passed`

## Risks / Rollback Notes
- Risk: command-target selection currently assumes viewer-selected targets.
- Rollback: keep the first implementation cut bounded to direct command
  projection usage and escalate if a separate command-target model is required.

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
- DATETIME: 2026-04-18T19:25:29Z
  TYPE: FACT
  CLAIM: The static-command direct-test helper still modeled the old viewer-era
    room contract after the no-compat projection port. It needed explicit
    `get_default_runtime_frame_name(...)` and
    `get_required_command_projection(...)` support to match the current
    command-system contract.
  EVIDENCE:
  - tests/unit/melder/aether/test_static_command_system_direct.py:49-67
  - src/melder/aether/nexus/rift/command_system/command_system.py:2120-2132
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:178-365
  IMPACT: The remaining failing direct tests were harness drift, not a runtime regression.
  NEXT: keep the projection task in review unless broader validation exposes
    another contract mismatch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T19:25:29Z
  TYPE: MEASURE
  CLAIM: The focused static-command direct test file is green after porting the
    helper to the projection-era room contract.
  EVIDENCE:
  - validation_result: `python -m py_compile tests/unit/melder/aether/test_static_command_system_direct.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_static_command_system_direct.py` -> 4 passed
  IMPACT: The direct static-command harness now matches the projection split.
  NEXT: none unless the user requests a broader rerun.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-04-18T19:07:00Z
  TYPE: FACT
  CLAIM: The no-backward-compat cleanup is now complete for this lane. The old
    selected-target command API is gone, the viewer-to-projection synthesis
    fallback is gone, the affected unit/integration harnesses now seed
    projection sets explicitly, and the selected-target command scripts were
    removed from the static JSON testbench matrix instead of being preserved as
    shims.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:1-2300
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:384-466
  - src/melder/utilities/interfaces/interfaces.py:1-9999
  - tests/unit/melder/aether/test_command_system_direct.py:1-520
  - tests/unit/melder/aether/test_nexus.py:1-3600
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:640-870
  IMPACT: This projection split is now a full port instead of a compatibility
    slice.
  NEXT: hold for review and decide whether the next bounded follow-on is a real
    `CodegenProjection` consumer or further room-level command/view cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T19:07:00Z
  TYPE: MEASURE
  CLAIM: The strict no-compat projection ring is green after removing the
    transitional command/viewer bridges.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/projection/view_projection.py src/melder/aether/nexus/rift/projection/command_projection.py src/melder/aether/nexus/rift/projection/codegen_projection.py src/melder/aether/nexus/rift/projection/frame_projection_set.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/nexus.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py src/melder/aether/nexus/rift/command_system/command_system.py src/melder/aether/nexus/rift/command_system/static_command_system.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_gate.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_gate.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py` -> 290 passed
  IMPACT: The projection/runtime split is stable in the no-compat configuration.
  NEXT: wait for review/acceptance before closing or widening the lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T18:48:44Z
  TYPE: CONFLICT
  CLAIM: Two transition bridges are still present and violate the no-backward-
    compat direction:
    1. `CommandSystem` still exposes the old selected-target methods
       (`get_selected_target_link`, `get_selected_target_record`,
       `get_selected_target_runtime_object`)
    2. `RiftSpace.attach_frame_viewer(...)` can still synthesize projection
       sets from an attached viewer when no projection sets exist yet.
    Those were left in place only to keep old tests/harnesses alive.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:222-394
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:407-414
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:533-689
  - tests/unit/melder/aether/test_command_system_direct.py:192-265
  - tests/unit/melder/aether/test_nexus.py:1173-1226
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:688-738
  IMPACT: The first slice is green, but it is not yet a full port.
  NEXT: remove the old selected-target command API and the viewer-to-projection
    synthesis fallback, then port the affected tests/harnesses to explicit
    projection seeding and explicit command identifiers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T18:48:44Z
  TYPE: FACT
  CLAIM: The first projection-split slice is now landed. A new projection
    substrate exists (`ViewProjection`, `CommandProjection`,
    `CodegenProjection`, `FrameProjectionSet`), `Nexus` now builds projection
    sets from the selected frame contract names, `RiftSpace` owns those sets,
    `CommandSystem` explicit-id paths now read `CommandProjection` instead of
    `FrameViewer`, and `Nexus` now coordinates synchronized ACL refresh by
    disabling impacted Rift gates, waiting for drain, rebuilding projections,
    swapping them into the owning space, and reopening the gates.
  EVIDENCE:
  - src/melder/aether/nexus/rift/projection/view_projection.py:1-112
  - src/melder/aether/nexus/rift/projection/command_projection.py:1-94
  - src/melder/aether/nexus/rift/projection/codegen_projection.py:1-94
  - src/melder/aether/nexus/rift/projection/frame_projection_set.py:1-103
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-886
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:58-96
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:2128-2156
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:2670-2695
  - src/melder/aether/nexus/rift/command_system/command_system.py:20-35
  - src/melder/aether/nexus/rift/command_system/command_system.py:222-2293
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:125-415
  - src/melder/aether/nexus/rift/rift.py:430-760
  - src/melder/aether/nexus/nexus.py:1530-2115
  IMPACT: Viewer, command, and codegen now have a real shared projection substrate,
    and command explicit-id paths are no longer viewer-hosted.
  NEXT: review this first slice and decide whether the next follow-on should
    remove the remaining selected-target bridge or start a real codegen-system
    consumer on top of `CodegenProjection`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T18:48:44Z
  TYPE: MEASURE
  CLAIM: The focused projection-split validation ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/projection/view_projection.py src/melder/aether/nexus/rift/projection/command_projection.py src/melder/aether/nexus/rift/projection/codegen_projection.py src/melder/aether/nexus/rift/projection/frame_projection_set.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/nexus.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py src/melder/aether/nexus/rift/command_system/command_system.py src/melder/aether/nexus/rift/command_system/static_command_system.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_gate.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_gate.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py` -> 297 passed
  IMPACT: The first projection/runtime cut is stable enough to review before we
    widen into the next command/codegen slice.
  NEXT: wait for acceptance before closure or the next bounded follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T17:14:19Z
  TYPE: PLAN
  CLAIM: The implementation lane is now explicit: separate view/command/codegen
    projections, command decoupled from viewer, and Nexus-owned ACL refresh
    across all downstream surfaces.
  EVIDENCE:
  - tickets/tasks/2026-04-18_investigate_frame_viewer_acl_propagation_and_refresh_task.md:92-140
  - user_instruction: "those 2 things should be seperate"
  - user_instruction: "codegen will also follow this paradigm"
  IMPACT: We can implement the next cut without pretending the current
    viewer-centric command model is acceptable.
  NEXT: wait for approval before code edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T18:20:00Z
  TYPE: PLAN
  CLAIM: The synchronized refresh sequence is now part of the implementation
    contract: `Nexus` closes every impacted Rift gate through the controller,
    waits for drain, rebuilds projection sets, swaps them into the owning
    spaces, and reopens the gates afterward. This is the mechanism that should
    update command and viewer together instead of relying on incidental viewer
    replacement.
  EVIDENCE:
  - tickets/stories/2026-04-18_separate_view_command_codegen_projections_story.md:41-48
  - user_instruction: "can we setup this process to so its synchronized properly?"
  IMPACT: The code patch needs both the projection split and the gate-driven
    refresh method in `Nexus`.
  NEXT: start the projection object implementation and the synchronized refresh
    path together.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task stages the next major Rift runtime cut: separate projections for
view, command, and codegen with Nexus-owned ACL refresh.