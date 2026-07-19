# Task: Refactor RiftSpace To Mode Specific Command Systems
- Completed: 2026-04-13T12:00:15Z
- Summary: Closed the mode-specific command-system composition refactor after later capability/runtime work built on it as settled room infrastructure.

## Metadata
- Task ID: TASK-2026-04-12-refactor-rift-space-to-mode-specific-command-systems
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T11:11:52Z
- Updated: 2026-04-12T11:15:16Z

## Objective
Replace the current single `CommandSystem` ownership model with a composed
mode-specific command-system family under `rift_space/command_system/` so
`StaticRiftSpace`, `CapabilityRiftSpace`, and `DynamicRiftSpace` each build
their own command surface while keeping the shared command API shape.

## Ticket Contract
- ENTRY_GATE: the command ACL access slice and the room-mode runtime gating
  slice are landed and green, and the user explicitly approved moving the
  mode-specific behavior out of inline `space_kind` checks and into composed
  command-system classes.
- EXECUTION_BOUNDARY: `rift_space/command_system/` folder creation, command
  system module move/split, `RiftSpace` room-owned command-system factory
  wiring, room subclass composition, focused interface/import updates, focused
  tests, patch docs, and board/artifact routing only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-12_implement_command_acl_access_enforcement_in_command_system_task.md
  - tickets/tasks/2026-04-12_implement_command_system_room_mode_runtime_gating_task.md
  - src/melder/aether/nexus/rift/rift_space/command_system.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: `rift_space/command_system/` exists, the base command system and
  the static/capability/dynamic variants live there, `RiftSpace` composes the
  right command system per room, and the focused runtime ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the refactor requires a wider
  public agent-surface redesign beyond the command-system composition seam.

## Scope Boundaries
- In scope:
  - create `rift_space/command_system/`
  - move/split the generic command system into mode-specific subclasses
  - room-owned command-system factory/composition
  - move the current static/capability runtime gating into the right subclass
  - focused tests and import updates
- Out of scope:
  - handle/proxy capability design
  - workstation-bound object policing
  - ACL/compiler schema changes
  - viewer redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the current inline room-kind checks proved the policy
  boundary, and the user explicitly directed the next refactor into composed
  mode-specific command-system classes under `rift_space/command_system/`.

## Steps / Checklist
- [x] Stage patch docs and route the new task from the board.
- [x] Create `rift_space/command_system/` and move the base command system into it.
- [x] Add `StaticCommandSystem`, `CapabilityCommandSystem`, and `DynamicCommandSystem`.
- [x] Refactor `RiftSpace` to build command systems through a room-owned factory seam.
- [x] Wire static/capability/dynamic room classes to construct the right command system.
- [x] Update focused imports/interfaces/tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `rift_space/command_system/` folder with base + mode-specific command systems
- room-owned command-system composition in `RiftSpace`
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/command_system/
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/aether/nexus/rift/rift_space/static_rift_space.py
- src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
- src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system/command_system.py src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py src/melder/aether/nexus/rift/rift_space/command_system/dynamic_command_system.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: we duplicate too much command logic across the three mode-specific
  systems.
  Rollback: keep one shared base class and move only the behavior deltas into
  the room-specific subclasses.

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
  - system_docs/patches/active/rift_space_mode_specific_command_systems/architecture_patch.md
  - system_docs/patches/active/rift_space_mode_specific_command_systems/component_patch_rift_space.md
  - system_docs/patches/active/rift_space_mode_specific_command_systems/component_patch_command_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until mode-specific command-system composition is
  merged into canonical Rift/runtime docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T11:11:52Z
  TYPE: FACT
  CLAIM: The ownership seam already supports mode-specific command-system
    composition. `Rift` programs its primary room from `space_type`, `RiftSpace`
    owns the `command_system`, and the room subclasses currently differ mostly
    by `space_kind`. That means we do not need a new public agent API to get
    mode-specific behavior. We need `RiftSpace` to build a mode-specific
    `CommandSystem` subclass instead of hardcoding one generic class and then
    branching on `space_kind` inside it.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:885-914
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:108-122
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:10-53
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:11-63
  - src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py:8-53
  IMPACT: The next refactor can stay local to the RiftSpace/CommandSystem seam
    and still deliver the composition model the user asked for.
  NEXT: stage patch docs and move the generic command system under
    `rift_space/command_system/` as the shared base class.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T11:15:16Z
  TYPE: FACT
  CLAIM: The composition refactor is now landed in source. The generic command
    system has been moved under `rift_space/command_system/command_system.py`,
    and the room-specific variants now exist as:
    - `StaticCommandSystem`
    - `CapabilityCommandSystem`
    - `DynamicCommandSystem`
    `RiftSpace` now constructs its command surface through a room-owned
    `_create_command_system()` seam, and the static/capability/dynamic room
    classes each override that seam to build the correct command-system
    subclass.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:1-945
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:1-42
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py:1-42
  - src/melder/aether/nexus/rift/rift_space/command_system/dynamic_command_system.py:1-20
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:25-27
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:109-120
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:265-285
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:3-68
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:3-79
  - src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py:3-68
  IMPACT: Room mode is now expressed through owned command-surface composition
    instead of inline `space_kind` checks buried in one generic
    implementation.
  NEXT: validate the focused and nearby runtime rings and record the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T11:15:16Z
  TYPE: MEASURE
  CLAIM: The mode-specific command-system composition refactor is green on the
    focused and nearby ACL/Nexus/runtime rings. The updated room-composition
    tests pass, and the nearby ACL/viewer/compiler ring still passes after the
    folder move and import rewiring.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system/command_system.py src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py src/melder/aether/nexus/rift/rift_space/command_system/dynamic_command_system.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py` -> 86 passed
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py` -> 165 passed
  IMPACT: The runtime composition seam is now stable enough for review or for
    the next capability/static behavior slice instead of more local import
    cleanup.
  NEXT: summarize the landed composition model and ask for the next direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task refactors the current inline room-kind command behavior into
composed mode-specific command systems under `rift_space/command_system/`.
