# Task: Implement Rift-Managed Room Asset Projection Orchestration
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-19-implement-rift-managed-room-asset-projection-orchestration
- Story: STORY-2026-04-19-implement-rift-managed-room-asset-projection-orchestration
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T12:16:10Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Move projection registry and projection-application ownership from `RiftSpace`
to `Rift`, and remove room projection-management seams.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for the corrected Rift-owned design to
  be implemented.
- EXECUTION_BOUNDARY: `Rift`, `RiftSpace`, `CommandSystem`, focused tests/docs,
  and the required patch-doc set only.
- DEPENDENCIES:
  - system_docs/patches/active/rift_managed_room_asset_projection_orchestration/architecture_patch.md
  - system_docs/patches/active/rift_managed_room_asset_projection_orchestration/component_patch_rift.md
  - system_docs/patches/active/rift_managed_room_asset_projection_orchestration/component_patch_rift_space.md
  - system_docs/patches/active/rift_managed_room_asset_projection_orchestration/component_patch_command_system.md
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/command_system/command_system.py
  - src/melder/aether/nexus/rift/command_system/static_command_system.py
  - tests/unit/melder/aether/test_command_system_direct.py
  - tests/unit/melder/aether/test_static_command_system_direct.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py
- EXIT_GATE: Rift owns projection registry/application, room seams are gone,
  focused tests/docs are green, and durable state is synced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a real codegen asset is
  required for this lane rather than a Rift-internal codegen projection store.

## Scope Boundaries
- In scope:
  - Rift-owned projection registry
  - command projection access rebasing
  - room seam removal
  - focused tests/docs
- Out of scope:
  - command vocabulary redesign
  - viewer helper redesign
  - codegen execution system design

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the Rift-owned projection orchestration implementation is
  landed and the broader AR/command/viewer ring is green.

## Steps / Checklist
- [x] Move projection registry ownership into `Rift`.
- [x] Add Rift-owned projection access helpers for internal asset use.
- [x] Rebase `CommandSystem` onto Rift-owned projection access.
- [x] Remove projection-management methods from `RiftSpace`.
- [x] Update focused tests/docs.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- Rift-owned projection registry/apply path
- room projection seam removal
- command-system projection access rebase
- focused tests/docs

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/aether/nexus/rift/command_system/command_system.py
- src/melder/aether/nexus/rift/command_system/static_command_system.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_command_system_direct.py
- tests/unit/melder/aether/test_static_command_system_direct.py
- tests/unit/melder/aether/test_nexus.py
- tests/unit/melder/aether/test_nexus_frame_surface_projection.py
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py src/melder/aether/nexus/rift/command_system/command_system.py src/melder/aether/nexus/rift/command_system/static_command_system.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_static_command_system_direct.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py`
- `python -m pytest -q tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_static_command_system_direct.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py`
- `python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_static_command_system_direct.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py`
- Result: `321 passed`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/rift_managed_room_asset_projection_orchestration/architecture_patch.md
  - system_docs/patches/active/rift_managed_room_asset_projection_orchestration/component_patch_rift.md
  - system_docs/patches/active/rift_managed_room_asset_projection_orchestration/component_patch_rift_space.md
  - system_docs/patches/active/rift_managed_room_asset_projection_orchestration/component_patch_command_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: apply artifact disposition when the task closes

## Notes
- DATETIME: 2026-04-19T12:16:10Z
  TYPE: PLAN
  CLAIM: The key implementation constraint is that `CommandSystem` currently
    still depends on `space.get_required_command_projection(...)`. That
    dependency has to move first, otherwise room projection seam removal will
    just break command access.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:242-2666
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:78-354
  IMPACT: The clean order is Rift registry first, then command rebase, then
    room seam removal.
  NEXT: consume the patch docs and patch Rift + CommandSystem together.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T12:39:30Z
  TYPE: FACT
  CLAIM: `Rift` now owns the applied projection registry and projection
    access helpers. `refresh_runtime_projections(...)` stores projection state
    on the Rift itself and applies it to the hosted viewer asset from there.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:87-88
  - src/melder/aether/nexus/rift/rift.py:203-216
  - src/melder/aether/nexus/rift/rift.py:490-667
  IMPACT: Projection ownership is now Rift-centric instead of room-centric.
  NEXT: hold for review unless you want the codegen side widened further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T12:39:30Z
  TYPE: FACT
  CLAIM: `RiftSpace` no longer exposes projection registry or projection
    accessors, and `CommandSystem` now reads command projection truth from
    `Rift` instead of `space`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:35-84
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:146-221
  - src/melder/aether/nexus/rift/command_system/command_system.py:21-39
  - src/melder/aether/nexus/rift/command_system/command_system.py:63-91
  - src/melder/aether/nexus/rift/command_system/command_system.py:242-2673
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:78-354
  IMPACT: The room is now an asset host, not a projection manager, and command
    access follows the same ownership model as viewer sync.
  NEXT: hold for review unless you want one more bounded cleanup on the room
    public surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T12:39:30Z
  TYPE: MEASURE
  CLAIM: The broader AR/command/viewer ring is green after the ownership
    correction.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_static_command_system_direct.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py` -> 135 passed
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_static_command_system_direct.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py` -> 321 passed
  IMPACT: The bounded ownership refactor is stable enough to move into review.
  NEXT: wait for user acceptance or the next bounded follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T19:05:00Z
  TYPE: FACT
  CLAIM: One bounded cleanup pass is still needed after the ownership move.
    The live runtime behavior is right, but a few stale pre-sync seams remain
    in comments/docstrings/imports: `Rift.refresh_runtime_projections(...)`
    still says it rebuilds the viewer, `RiftSpace` still describes a viewer
    attachment point instead of a durable asset in one room-mode line, and
    `StaticRiftSpace` still carries unused viewer imports from the old
    rebuild/wrap path.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:476-489
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:59-60
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:3-6
  IMPACT: The ownership correction is functionally landed, but the code/docs
    still carry small debris from the older lifecycle model.
  NEXT: patch the stale wording/imports and re-check `src_architecture.md` /
    `src_components.md` against the landed model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-19T19:08:00Z
  TYPE: FACT
  CLAIM: The main component doc still carries one older file-layout seam. The
    AR command-system entries still point at the old
    `rift_space/command_system/...` paths even though the live command-system
    modules now live directly under `src/melder/aether/nexus/rift/command_system/`.
  EVIDENCE:
  - codex/context_compass/system_docs/src_components.md:1982-1985
  - src/melder/aether/nexus/rift/command_system/command_system.py:1-39
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:1-22
  IMPACT: The ownership story is mostly current, but the code map still has one
    stale path family that will misroute a reader.
  NEXT: patch the stale command-system paths while cleaning the smaller runtime
    wording/import debris.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-19T13:19:22Z
  TYPE: FACT
  CLAIM: The bounded cleanup patch is landed. It removes the leftover unused
    static-viewer imports, fixes stale pre-sync wording in `Rift` and
    `RiftSpace`, fixes the last `dynamic` wording drift in
    `CapabilityRiftSpace`, and updates the main architecture/component docs to
    the live `rift/command_system/...` file layout plus current update dates.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:476-489
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:58-60
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:192-197
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:24-29
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:73-79
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:1-10
  - codex/context_compass/system_docs/src_architecture.md:6-10
  - codex/context_compass/system_docs/src_architecture.md:1029-1033
  - codex/context_compass/system_docs/src_architecture.md:1198-1201
  - codex/context_compass/system_docs/src_components.md:6-10
  IMPACT: The landed ownership model is now cleaner and the main docs no longer
    misroute readers to the pre-move command-system paths.
  NEXT: run a focused validation ring for the touched Rift/room/viewer/runtime
    docs slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-19T13:19:52Z
  TYPE: MEASURE
  CLAIM: The post-cleanup AR/command/viewer validation ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_static_command_system_direct.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py` -> 321 passed
  IMPACT: The cleanup stayed bounded to debris/doc drift and did not regress the
    landed ownership/viewer/runtime model.
  NEXT: hold for review unless you want another narrower cleanup pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:17:10Z
  TYPE: FACT
  CLAIM: `FrameViewer` is still materially oversized. It does not just host
    methods that view descriptors; it also owns descriptor/config/access-surface
    snapshot maps, binds selected profiles per frame, clones projection-derived
    state on sync, and exposes a large host-side descriptor inventory/comparison
    API plus AST introspection helpers. That is why it feels like more than a
    viewer.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:72-81
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:380-487
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:606-2398
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:14-31
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:238-338
  IMPACT: The current implementation still mixes "viewer host", "projection
    snapshot owner", and "profile binding runtime" responsibilities into one
    object, which is the next real design smell after the Rift-owned
    projection move.
  NEXT: decide whether to slim `FrameViewer` into a true projection-backed
    reader with only viewer-local state, or to keep the snapshot-host design
    intentionally.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task implements the ownership correction after the user explicitly
rejected room-owned projection management.