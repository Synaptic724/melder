# Task: Implement RiftSpace-Owned FrameViewer Builder And Remove Nexus Viewer Seams
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-implement-rift-space-owned-frame-viewer-builder-and-remove-nexus-viewer-seams
- Story: STORY-2026-04-18-implement-rift-space-owned-frame-viewer-migration
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T23:05:00Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Move generic `FrameViewer` assembly into `RiftSpace`, keep static viewer
composition room-local, and remove the old `Nexus` / `Rift` viewer-builder and
cache seams.

## Ticket Contract
- ENTRY_GATE: user approved implementation of the viewer ownership move.
- EXECUTION_BOUNDARY: `Nexus`, `Rift`, `RiftSpace`, `StaticRiftSpace`,
  focused viewer docs/tests, and the directly affected patch docs only.
- DEPENDENCIES:
  - system_docs/patches/active/rift_space_owned_frame_viewer/architecture_patch.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_nexus.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_rift.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_rift_space.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_static_rift_space.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/code_description_patch_viewer_refresh_flow.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
  - tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
- EXIT_GATE: room-owned viewer assembly is live, old builder/cache seams are
  gone, focused validation is green, and docs/ticket state are synced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the migration forces a
  larger explicit-frame redesign instead of staying a viewer-ownership slice.

## Scope Boundaries
- In scope:
  - room-owned generic viewer builder
  - static room viewer wrapping
  - Rift refresh/orchestration updates
  - Nexus viewer-builder/cache seam removal
  - focused tests and AR docs
- Out of scope:
  - command/codegen redesign
  - explicit `frame_name` enforcement
  - unrelated room API cleanup

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the room-owned viewer migration is implemented, the old
  builder/cache seams are gone, and the focused validation ring is green.

## Steps / Checklist
- [x] Add the room-owned generic viewer builder on `RiftSpace`.
- [x] Keep static wrapping room-local in `StaticRiftSpace`.
- [x] Switch `Rift.refresh_runtime_projections(...)` to rebuild the viewer
      through the room after projection replacement.
- [x] Remove `Nexus.create_frame_viewer*`, cache fields/helpers, and ACL-change
      viewer-cache invalidation seams.
- [x] Remove `Rift.create_frame_viewer*` and `Rift.attach_frame_viewer(...)`.
- [x] Port focused tests to the room-owned viewer path.
- [x] Update `codex/context_compass/system_docs/src_architecture.md` and
      `codex/context_compass/system_docs/src_components.md` to match the landed
      ownership model.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- room-owned generic viewer builder
- removed Nexus/Rift viewer-builder and cache seams
- updated focused tests/docs

## Files / Paths Impacted
- src/melder/aether/nexus/nexus.py
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/aether/nexus/rift/rift_space/static_rift_space.py
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_nexus.py
- tests/unit/melder/aether/test_nexus_frame_surface_projection.py
- tests/unit/melder/aether/test_rift_runtime_contracts.py
- tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md

## Validation
- `python -m py_compile src/melder/aether/nexus/nexus.py src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py`
- `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py`
- Result: `196 passed`

## Risks / Rollback Notes
- Risk: doc drift in AR architecture/components docs after the seam removal.
- Risk: focused tests may still assume old Nexus viewer-builder APIs.
- Rollback: restore the removed builder seams only if the migration proves
  internally inconsistent; no compatibility layer planned.

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
  - system_docs/patches/active/rift_space_owned_frame_viewer/architecture_patch.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_nexus.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_rift.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_rift_space.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_static_rift_space.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/code_description_patch_viewer_refresh_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: apply artifact disposition when the task closes

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-18T23:38:15Z
  TYPE: FACT
  CLAIM: The post-implementation debris pass did not find any remaining live
    runtime references to the removed Nexus/Rift viewer-builder seam. The only
    follow-on cleanup needed was minor test/helper debris: stale room-viewer
    injection assumptions, stale room-viewer helper names, and missing
    `selected_contract_names` metadata in one synthetic projection helper.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1631-2106
  - src/melder/aether/nexus/rift/rift.py:361-563
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:369-616
  - tests/unit/melder/aether/test_nexus.py:311-404
  - tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py:106-254
  - tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py:16-137
  IMPACT: The ownership slice is clean at the code level rather than merely
    green by chance.
  NEXT: keep the lane in review unless you want another bounded AR cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T23:27:29Z
  TYPE: FACT
  CLAIM: Viewer assembly now lives in `RiftSpace`. The room builds the generic
    viewer from installed `ViewProjection` objects, `StaticRiftSpace` keeps the
    static wrapper locally, `Rift.refresh_runtime_projections(...)` rebuilds the
    room-owned viewer, and the old Nexus/Rift viewer-builder/cache seams are
    removed.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:369-576
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:80-113
  - src/melder/aether/nexus/rift/rift.py:463-535
  - src/melder/aether/nexus/nexus.py:1811-2096
  IMPACT: The ownership model is now coherent: Nexus builds projections, Rift
    orchestrates refresh, and the room owns the live viewer.
  NEXT: hold for review unless you want another bounded AR ownership follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T23:27:29Z
  TYPE: FACT
  CLAIM: The migration also fixed the old frame-scoped refresh bug where
    `Rift.refresh_runtime_projections(frame_name=...)` replaced the room's
    whole projection dict with only the refreshed subset. Partial refreshes now
    merge into the installed projection state instead.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:489-535
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:577-616
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:233-260
  IMPACT: ACL-driven per-frame refresh no longer drops unrelated room
    projections in multi-frame rooms.
  NEXT: keep this invariant if the explicit-`frame_name` cleanup lane resumes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T23:27:29Z
  TYPE: MEASURE
  CLAIM: The focused viewer/Rift/Nexus validation ring is green after the
    ownership move and test/doc migration.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/nexus.py src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py` -> 196 passed
  IMPACT: The bounded ownership migration is stable enough to review.
  NEXT: wait for user acceptance or the next bounded follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T23:11:00Z
  TYPE: FACT
  CLAIM: The current frame-scoped refresh path is already wrong for
    multi-frame rooms: `Rift.refresh_runtime_projections(frame_name=...)`
    asks `Nexus` for only that frame's projection set and then
    `RiftSpace.replace_projection_sets(...)` replaces the whole room-owned
    projection dict with that subset.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:593-629
  - src/melder/aether/nexus/nexus.py:2002-2041
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:425-443
  IMPACT: The ownership migration must merge single-frame refreshes into the
    existing room projection dict instead of preserving the current replace-all
    subset behavior.
  NEXT: implement the room-owned builder on top of a corrected partial-refresh
    merge path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T23:05:00Z
  TYPE: PLAN
  CLAIM: Patch-consumption mapping for this task is:
    architecture patch -> ownership boundary and non-goals,
    Nexus patch -> projection-only + cache-seam removal,
    Rift patch -> refresh/orchestration change,
    RiftSpace patch -> generic builder + replacement path,
    StaticRiftSpace patch -> static wrapper preservation,
    code-description patch -> end-to-end refresh flow and ACL-change refresh
    behavior.
  EVIDENCE:
  - system_docs/patches/active/rift_space_owned_frame_viewer/architecture_patch.md:1-26
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_nexus.md:1-18
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_rift.md:1-18
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_rift_space.md:1-18
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_static_rift_space.md:1-12
  - system_docs/patches/active/rift_space_owned_frame_viewer/code_description_patch_viewer_refresh_flow.md:1-25
  IMPACT: The patch gate is satisfied and the implementation/validation steps
    are explicitly mapped before code edits.
  NEXT: patch the runtime in the same ownership order as the mapping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task is the bounded implementation slice for moving viewer ownership into
`RiftSpace` and removing the old Nexus/Rift builder seams. The code/doc/test
slice is implemented and waiting on review.