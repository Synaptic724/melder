# Task: Implement Persistent RiftSpace FrameViewer Asset
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-19-implement-persistent-rift-space-frame-viewer-asset
- Story: STORY-2026-04-19-implement-persistent-rift-space-frame-viewer-asset
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T11:25:38Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Implement the durable room-owned viewer asset lifecycle so the viewer exists
from room init onward and projection updates sync it in place.

## Ticket Contract
- ENTRY_GATE: the user approved the durable-viewer implementation lane and the
  discovery task proved the constructor already supports empty state.
- EXECUTION_BOUNDARY: `RiftSpace`, `Rift`, `FrameViewer`,
  `StaticFrameViewer`, focused tests/docs, and the required patch-doc set only.
- DEPENDENCIES:
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/architecture_patch.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/component_patch_rift_space.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/component_patch_frame_viewer.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/component_patch_static_frame_viewer.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/component_patch_rift.md
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py
  - tests/unit/melder/aether/test_rift_space.py
  - tests/unit/melder/aether/test_static_rift_space.py
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py
  - tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
- EXIT_GATE: the durable viewer asset is live, replace/clear/rebuild seams are
  gone, focused tests are green, and durable state is synced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if static-viewer sync or default
  frame preservation requires a broader redesign.

## Scope Boundaries
- In scope:
  - durable empty viewer init
  - in-place viewer sync
  - static viewer sync behavior
  - Rift refresh orchestration update
  - focused test/doc rewrites
- Out of scope:
  - command/codegen redesign
  - broad viewer helper redesign
  - ACL batching changes

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the durable-viewer lifecycle implementation is landed and
  the focused viewer/rift ring is green.

## Steps / Checklist
- [x] Create the durable viewer asset during room init.
- [x] Add in-place projection sync to `FrameViewer`.
- [x] Add the static-viewer durable sync behavior.
- [x] Remove `_build_frame_viewer(...)`, `_rebuild_frame_viewer(...)`,
      `_replace_frame_viewer(...)`, and `_clear_frame_viewer(...)`.
- [x] Update `Rift` to sync the existing viewer instead of rebuilding it.
- [x] Update focused tests/docs to the stable-viewer model.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- durable empty room viewer asset
- in-place viewer sync path
- removed replace/clear/rebuild seams
- focused test/doc updates

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
- src/melder/aether/nexus/rift/rift_space/static_rift_space.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_rift_space.py
- tests/unit/melder/aether/test_static_rift_space.py
- tests/unit/melder/aether/test_rift_runtime_contracts.py
- tests/unit/melder/aether/test_nexus.py
- tests/unit/melder/aether/test_nexus_frame_surface_projection.py
- tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md
- codex/context_compass/tickets/tasks/2026-04-19_implement_persistent_rift_space_frame_viewer_asset_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`
- `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`
- `python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py`
- Result: `307 passed`

## Risks / Rollback Notes
- Risk: static viewer sync may require more invasive changes than base viewer.
- Risk: tests that currently assert replacement identity may hide edge cases in
  selected-profile preservation.
- Rollback: restore rebuild-based lifecycle only if the sync-based lifecycle
  proves internally inconsistent.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/architecture_patch.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/component_patch_rift_space.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/component_patch_frame_viewer.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/component_patch_static_frame_viewer.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/component_patch_rift.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: apply artifact disposition when the task closes

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-19T11:25:38Z
  TYPE: PLAN
  CLAIM: The implementation order is:
    1. add a durable empty viewer asset in room init,
    2. add an in-place sync/update contract on the viewer,
    3. adapt static viewer behavior to that contract,
    4. switch Rift refresh from rebuild to sync,
    5. rewrite the no-viewer and replacement-identity tests.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:152-177
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:83-212
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:15-112
  IMPACT: The lane is implementable as one bounded lifecycle refactor.
  NEXT: consume the patch docs and patch the base viewer/room first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T11:50:05Z
  TYPE: FACT
  CLAIM: `RiftSpace` now creates a durable viewer asset during init and keeps
    it alive through projection changes. The room syncs that existing viewer
    in place, and the old rebuild/replace/clear viewer lifecycle seams are
    gone.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:152-491
  - src/melder/aether/nexus/rift/rift.py:463-542
  IMPACT: The viewer now behaves like the other long-lived room assets instead
    of a disposable rebuilt snapshot.
  NEXT: hold for review unless you want to widen the lifecycle change further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T11:50:05Z
  TYPE: FACT
  CLAIM: `FrameViewer` and `StaticFrameViewer` now own an in-place projection
    sync contract. Base viewers preserve selected-profile/default-frame state
    across sync, and static viewers reapply live-only spell filtering on the
    same durable viewer object.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:359-585
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:58-156
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:254-335
  IMPACT: The durable asset model is real at the viewer layer, not just at the
    room orchestration layer.
  NEXT: hold for review unless you want a broader viewer API cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T11:50:05Z
  TYPE: MEASURE
  CLAIM: The broader viewer/rift ring is green after the durable-viewer
    lifecycle implementation.
  EVIDENCE:
  - tests/unit/melder/aether/test_rift_space.py:1-129
  - tests/unit/melder/aether/test_static_rift_space.py:1-30
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:256-305
  - tests/unit/melder/aether/test_nexus.py:391-420
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:245-376
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py` -> 136 passed
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_static_rift_space.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py` -> 307 passed
  IMPACT: The bounded lifecycle refactor is stable enough to move into review.
  NEXT: wait for user acceptance or the next bounded follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task implements the durable viewer asset model after the discovery slice
proved the current limitation is in room lifecycle, not in the viewer
constructor itself.