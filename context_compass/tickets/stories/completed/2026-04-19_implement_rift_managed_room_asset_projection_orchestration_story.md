# Story: Implement Rift-Managed Room Asset Projection Orchestration
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-19-implement-rift-managed-room-asset-projection-orchestration
- Epic: EPIC-2026-04-19-rift-managed-room-asset-projection-orchestration
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T12:16:10Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a Rift runtime maintainer, I want `Rift` to own projection-driven asset
orchestration so the room just hosts assets and the agent never sees or manages
projections.

## Value / MRP Alignment
This keeps the runtime honest:
- `Nexus` compiles projections
- `Rift` owns contract/projection application
- `RiftSpace` hosts assets

That is a cleaner, more durable ownership model than room-owned projection
state.

## Ticket Contract
- ENTRY_GATE: the user explicitly rejected room-owned projection management
  and approved the corrected Rift-owned model.
- EXECUTION_BOUNDARY: `Rift`, `RiftSpace`, `CommandSystem`, focused tests/docs,
  and the required patch-doc set only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-19_implement_rift_managed_room_asset_projection_orchestration_task.md
  - system_docs/patches/active/rift_managed_room_asset_projection_orchestration/architecture_patch.md
  - system_docs/patches/active/rift_managed_room_asset_projection_orchestration/component_patch_rift.md
  - system_docs/patches/active/rift_managed_room_asset_projection_orchestration/component_patch_rift_space.md
  - system_docs/patches/active/rift_managed_room_asset_projection_orchestration/component_patch_command_system.md
- EXIT_GATE: Rift owns projection orchestration, room projection seams are
  gone, focused tests/docs are green, and durable state is synced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the lane requires a broader
  codegen asset design or explicit-frame redesign.

## Requirements (Functional)
- Move projection registry ownership to `Rift`.
- Make `Rift` apply view/command/codegen projections internally.
- Remove projection-management seams from `RiftSpace`.
- Rebase `CommandSystem` onto Rift-owned command projection access.

## Requirements (Non-Functional)
- Keep projections hidden from the agent-facing room surface.
- Do not invent a fake codegen asset.
- Keep the change bounded to ownership/orchestration.

## Scope Boundaries
- In scope:
  - Rift-owned projection registry/apply path
  - room seam removal
  - command projection access rebasing
  - focused tests/docs
- Out of scope:
  - broader command redesign
  - viewer helper redesign
  - codegen execution system design

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the ownership correction is landed and the broader
  validation ring is green.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-19-implement-rift-managed-room-asset-projection-orchestration

## Acceptance Criteria
- `Rift` owns current projection state and applies it to hosted assets.
- `RiftSpace` no longer exposes projection-management methods.
- `CommandSystem` gets projection truth from `Rift`.
- Focused tests pass.

## Validation / Test Plan
- Focused command-system direct tests.
- Focused Rift/space projection tests.
- Focused AR integration ring.

## Notes
- DATETIME: 2026-04-19T12:16:10Z
  TYPE: PLAN
  CLAIM: The implementation split is:
    1. move projection registry ownership into `Rift`,
    2. update viewer sync to consume Rift-owned projections,
    3. rebase `CommandSystem` onto Rift-owned command projection access,
    4. remove room projection seams,
    5. update focused tests/docs.
  EVIDENCE:
  - tickets/epics/2026-04-19-rift-managed-room-asset-projection-orchestration-epic.md:1-120
  IMPACT: The task can stay bounded to ownership cleanup without reopening the
    larger ACL/viewer design.
  NEXT: land the linked task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T12:39:30Z
  TYPE: FACT
  CLAIM: The child task landed the ownership correction. `Rift` now owns
    projection registry/application, `RiftSpace` is projection-blind, and
    `CommandSystem` gets projection truth from `Rift`.
  EVIDENCE:
  - tickets/tasks/2026-04-19_implement_rift_managed_room_asset_projection_orchestration_task.md:1-170
  - codex/context_compass/system_docs/src_architecture.md:472-538
  - codex/context_compass/system_docs/src_components.md:500-590
  IMPACT: The story is ready for review instead of more implementation.
  NEXT: hold for acceptance or one more bounded follow-on request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This story implements the Rift-owned projection orchestration model after the
user explicitly rejected the remaining room-owned seams.