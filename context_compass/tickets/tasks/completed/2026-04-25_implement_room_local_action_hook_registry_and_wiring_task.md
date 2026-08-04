# Task: Implement Room-Local Action Hook Registry And Wiring
- Completed: 2026-04-25T13:39:06Z
- Summary: Closed during cleanup after the room-owned registry, category-wide
  plus exact-action hooks, and shared viewer wrapper all landed with focused
  tests green.

## Metadata
- Task ID: TASK-2026-04-25-implement-room-local-action-hook-registry-and-wiring
- Story: STORY-2026-04-25-wire-room-local-action-hooks-into-rift-space-command-viewer-and-codegen
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T11:54:04Z
- Updated: 2026-04-25T13:39:06Z

## Objective
Implement the room-owned action hook registry and wire pre/post hooks into
command, codegen, and viewer actions.

## Ticket Contract
- ENTRY_GATE: the user approved room-owned pre/post hooks, three categories,
  no payload object, and later widened the requirement to include both
  category-wide and action-specific registration.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/rift_space/rift_space.py`
  - `src/melder/aether/nexus/rift/command_system/command_system.py`
  - `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
  - `src/melder/aether/nexus/rift/frame_viewer/`
  - `src/melder/utilities/interfaces/interfaces.py`
  - `tests/unit/melder/aether/test_nexus.py`
- DEPENDENCIES:
  - `tickets/stories/2026-04-25_wire_room_local_action_hooks_into_rift_space_command_viewer_and_codegen_story.md`
- EXIT_GATE: hooks are room-owned and fire for command, codegen, and viewer
  actions in focused unit coverage.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if viewer helper coverage cannot
  be achieved through one shared wrapper pattern.

## Scope Boundaries
- In scope:
  - hook registry
  - category-wide registration
  - action-specific registration
  - category separation
  - command/codegen/viewer action wrapper wiring
- Out of scope:
  - payload objects
  - event replacement
  - wildcard/global hook routing

## Steps / Checklist
- [ ] Implement room-owned action hook registration/unregistration.
- [ ] Wire command actions.
- [ ] Wire codegen actions.
- [ ] Add shared viewer action wrapper and wire viewer actions.
- [ ] Add focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- room-local action hook registry
- command/codegen/viewer hook wiring
- focused validation results

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/aether/nexus/rift/command_system/command_system.py
- src/melder/aether/nexus/rift/command_system/codegen_command_system.py
- src/melder/aether/nexus/rift/frame_viewer/
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_nexus.py

## Validation
- Executed:
  - `python -m py_compile src/melder/utilities/interfaces/interfaces.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/command_system/command_system.py src/melder/aether/nexus/rift/command_system/codegen_command_system.py src/melder/aether/nexus/rift/frame_viewer/view_action_hooks.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py src/melder/aether/nexus/rift/frame_viewer/view_frame.py src/melder/aether/nexus/rift/frame_viewer/view_conduit.py src/melder/aether/nexus/rift/frame_viewer/view_spell.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "hook or codegen or viewer"`
- Result:
  - `45 passed, 95 deselected, 2 warnings`

## Risks / Rollback Notes
- Risk: viewer hook wrapping becomes inconsistent and fires nested hooks for
  internal helper-to-helper calls.
  Rollback: keep one shared top-level-per-category hook boundary with nested
  suppression.

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
- DATETIME: 2026-04-25T11:54:04Z
  TYPE: FACT
  CLAIM: Command and codegen already have natural action seams, but viewer does
    not. The viewer surface is broad enough that a shared wrapper pattern is
    required if we want all three categories covered coherently.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:915-1043
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:84-3968
  - src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py:38-1909
  - src/melder/aether/nexus/rift/frame_viewer/view_frame.py:53-1907
  - src/melder/aether/nexus/rift/frame_viewer/view_conduit.py:46-1182
  - src/melder/aether/nexus/rift/frame_viewer/view_spell.py:54-1960
  IMPACT: The registry is straightforward, but viewer hook coverage needs a
    deliberate wrapper design instead of inline scattered calls.
  NEXT: implement the room registry with nested category suppression and then
    add the shared viewer wrapper.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T13:02:44Z
  TYPE: FACT
  CLAIM: The hook registry and wiring are now landed. `RiftSpace` owns both
    category-wide and exact-action pre/post hook registration, `CommandSystem` runs
    category `command`, `CodegenCommandSystem` runs category `codegen`, and
    the viewer layer now uses a shared wrapper/decorator so `viewer` hooks fire
    for both top-level and helper-surface actions with nested-category
    suppression.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-560
  - src/melder/aether/nexus/rift/command_system/command_system.py:915-1087
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:542-637
  - src/melder/aether/nexus/rift/frame_viewer/view_action_hooks.py:1-56
  - tests/unit/melder/aether/test_nexus.py:1449-1644
  IMPACT: Agents can now trigger generalized category hooks and exact-action
    hooks across command, viewer, and codegen through one room-owned mechanism.
  NEXT: close the slice if the user accepts this hook model as sufficient MRP.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the full room-local action hook implementation slice.
