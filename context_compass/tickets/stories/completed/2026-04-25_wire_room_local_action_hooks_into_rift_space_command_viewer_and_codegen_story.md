# Story: Wire Room-Local Action Hooks Into RiftSpace Command Viewer And Codegen
- Completed: 2026-04-25T13:39:06Z
- Summary: Closed during cleanup after the room-owned registry and shared
  wrapper wiring made category-wide and exact-action hooks work across command,
  viewer, and codegen.

## Metadata
- Story ID: STORY-2026-04-25-wire-room-local-action-hooks-into-rift-space-command-viewer-and-codegen
- Epic: EPIC-2026-04-25-implement-room-local-action-hooks-for-command-viewer-and-codegen
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T11:54:04Z
- Updated: 2026-04-25T13:39:06Z

## User Narrative
As an engineer, I want a room-owned pre/post action hook system, so that
command, viewer, and codegen actions can trigger both category-wide and
action-specific synchronous hook methods without inventing another event
payload model.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved the room-owned registry, exact-action
  pre/post hooks, and all three categories.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/rift_space/`
  - `src/melder/aether/nexus/rift/command_system/`
  - `src/melder/aether/nexus/rift/frame_viewer/`
  - directly affected interfaces/tests
- DEPENDENCIES:
  - `tickets/epics/2026-04-25_implement_room_local_action_hooks_for_command_viewer_and_codegen_epic.md`
- EXIT_GATE: room-owned registry exists and hooks fire across command, viewer,
  and codegen actions.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one shared viewer wrapper
  cannot cover the viewer surface coherently.

## Tasks (Implementation Checklist)
- [x] Task: implement the room-local action hook registry and wire it into command/codegen/viewer

## Validation / Test Plan
- Focused unit tests for:
  - command pre/post hooks
  - codegen pre/post hooks
  - viewer pre/post hooks
  - category separation

## Notes
- DATETIME: 2026-04-25T11:54:04Z
  TYPE: PLAN
  CLAIM: The clean implementation order is:
    1. room-owned registry in `RiftSpace`
    2. command/codegen action wiring
    3. shared viewer action wrapper
  EVIDENCE:
  - user_instruction: "you can start with the wrapper for the viewers please"
  IMPACT: The feature can land as one coherent slice instead of half-wiring
    viewer later.
  NEXT: implement the room registry and then add the shared wrappers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-25T13:02:44Z
  TYPE: FACT
  CLAIM: The room-local action hook slice is now implemented with one
    `RiftSpace`-owned registry supporting both category-wide hooks and
    `category + action_name + phase` hooks,
    nested-category suppression, command/category wiring, codegen/category
    wiring, and a shared viewer wrapper that covers `FrameViewer`,
    `ViewMultiFrame`, `ViewFrame`, `ViewConduit`, and `ViewSpell`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-560
  - src/melder/aether/nexus/rift/command_system/command_system.py:915-1087
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:508-692
  - src/melder/aether/nexus/rift/frame_viewer/view_action_hooks.py:1-56
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-3993
  - src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py:1-1932
  - src/melder/aether/nexus/rift/frame_viewer/view_frame.py:1-1943
  - src/melder/aether/nexus/rift/frame_viewer/view_conduit.py:1-1201
  - src/melder/aether/nexus/rift/frame_viewer/view_spell.py:1-1980
  IMPACT: All three categories now share one room-owned generalized + exact
    hook model without payload objects or another event system.
  NEXT: return the hook slice for review and decide whether to close it or
    widen the hook model later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owns the actual room-local action-hook implementation slice.
