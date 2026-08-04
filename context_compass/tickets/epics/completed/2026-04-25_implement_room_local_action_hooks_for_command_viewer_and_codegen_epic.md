# Epic: Implement Room-Local Action Hooks For Command Viewer And Codegen
- Completed: 2026-04-25T13:39:06Z
- Summary: Closed during cleanup after the room-owned hook registry, category-
  wide plus exact-action pre/post hooks, and command/viewer/codegen wiring all
  landed and validated green.

## Metadata
- Epic ID: EPIC-2026-04-25-implement-room-local-action-hooks-for-command-viewer-and-codegen
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T11:54:04Z
- Updated: 2026-04-25T13:39:06Z

## Problem / Opportunity
The Rift layer already has room-local event and memory systems, but it does not
yet have a simple synchronous action-hook seam for command, viewer, and codegen
actions.

The existing command layer already has a clean action wrapper:
- `CommandSystem._entered_command_action(...)`

The viewer layer does not. It exposes a broad public method surface across:
- `FrameViewer`
- `ViewMultiFrame`
- `ViewFrame`
- `ViewConduit`
- `ViewSpell`

The opportunity is to add one room-owned hook registry and wire it into all
three categories:
- `command`
- `viewer`
- `codegen`

without inventing a payload-heavy hook system or a second event system.

## MRP Alignment (Most Reasonable Product)
The MRP is:
- room-owned pre/post hook registration
- category-wide hooks
- category + action-name keyed hooks
- no hook payload object
- command and codegen wired through their existing action seams
- viewer wrapped through one shared viewer action wrapper instead of scattered
  inline calls

This gives us a coherent execution hook surface without bloating the design.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested pre/post hooks by action and agreed
  that room-owned registry plus command/viewer/codegen categories is the right
  model.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/rift_space/`
  - `src/melder/aether/nexus/rift/command_system/`
  - `src/melder/aether/nexus/rift/frame_viewer/`
  - directly affected interfaces/tests
- DEPENDENCIES:
  - `src/melder/aether/nexus/rift/rift_space/rift_space.py`
  - `src/melder/aether/nexus/rift/command_system/command_system.py`
  - `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
  - `src/melder/aether/nexus/rift/frame_viewer/`
- EXIT_GATE: all three categories can register and execute pre/post hooks
  through one room-owned registry and the focused hook tests are green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the viewer surface cannot be
  wrapped coherently without a broader viewer architecture cut.

## Goals (Outcomes)
- Add room-owned action hook registration.
- Support categories `command`, `viewer`, and `codegen`.
- Support category-wide pre/post hook lists.
- Support exact-action pre/post hook lists.
- Wire command and codegen actions through the shared hook boundary.
- Add a shared wrapper for viewer actions so hooks work across the viewer
  surface.

## Non-Goals (Explicit Exclusions)
- hook payload objects
- hook event replacement
- hook-local retained history
- global wildcard hook routing beyond category/action registration

## Stories (Required to Complete)
- [x] Story: wire room-local action hooks into `RiftSpace`, command/codegen, and viewer

## Acceptance Criteria (Epic Done)
- A room can register category-wide and action-specific pre/post hooks.
- `command` actions fire hooks.
- `codegen` actions fire hooks.
- `viewer` actions fire hooks through a shared wrapper.

## Notes
- DATETIME: 2026-04-25T11:54:04Z
  TYPE: DECISION
  CLAIM: The hook model should stay simple: room-owned registry, category-wide
    and exact-action pre/post hooks, no payload object, and all three
    categories supported.
  EVIDENCE:
  - user_instruction: "pre and post hooks by action"
  - user_instruction: "we split out the hooks into a manner where you can register it for any of the 3 categories"
  - user_instruction: "we want a generalized system as well not just action defined"
  IMPACT: Implementation should focus on wrapper seams and category routing,
    not on designing a second event system.
  NEXT: stage the implementation story/task and wire the room registry into the
    command and viewer execution seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic owns the room-local action-hook feature for command, viewer, and
codegen.
