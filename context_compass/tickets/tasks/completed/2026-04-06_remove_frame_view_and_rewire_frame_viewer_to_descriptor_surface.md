# Task: Remove FrameView And Rewire FrameViewer To Descriptor Surface
- Completed: 2026-04-09T11:31:39Z
- Summary: Removed FrameView from the live runtime path and rewired the viewer directly to descriptor plus ACL truth.


## Metadata
- Task ID: TASK-2026-04-06-remove-frame-view-and-rewire-frame-viewer-to-descriptor-surface
- Story: STORY-2026-04-06-validate-descriptor-acl-payload-contracts-and-collapse-frame-view
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T16:52:25Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Remove `FrameView`, `FrameViewProfile`, and `FrameViewProfileBuilder` from the
runtime path and make `FrameViewer` execute directly against
descriptor-organized frame -> conduit -> spell data through ACL filtering.

## Ticket Contract
- ENTRY_GATE: descriptor<->ACL payload validation is landed first.
- EXECUTION_BOUNDARY: runtime collapse of the `FrameView` layer only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_implement_descriptor_acl_payload_contract_validation.md
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile_builder.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/nexus.py
- EXIT_GATE: `FrameViewer` no longer depends on `FrameView` and the old view
  files are deleted or fully removed from the runtime path.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a hidden intermediate
  projection object is still required.

## Scope Boundaries
- In scope:
  - remove `FrameView` runtime ownership
  - remove `FrameViewProfile` and builder
  - rewire `FrameViewer`
  - rewire Nexus creation/caching paths
  - focused tests
- Out of scope:
  - payload contract validation
  - codegen behavior
  - mutation work

## Steps / Checklist
- [ ] Move frame-local target/description behavior onto `FrameViewer`.
- [ ] Rewire `FrameViewer` to descriptor-organized data through ACL filtering.
- [ ] Remove `FrameView` and its profile/builder layer from the runtime path.
- [ ] Update Nexus creation/caching paths.
- [ ] Add/update focused tests.

## Deliverables
- descriptor-driven `FrameViewer`
- removed `FrameView` runtime path
- focused tests

## Validation
- Completed:
  - `python -m py_compile <local-workspace>\src\melder\aether\nexus\rift\frame_link\frame_link.py <local-workspace>\src\melder\aether\nexus\rift\frame_viewer\frame_viewer.py <local-workspace>\src\melder\aether\nexus\rift\rift_space\rift_space.py <local-workspace>\src\melder\aether\nexus\nexus.py <local-workspace>\tests\unit\melder\aether\test_frame_viewer_projection.py <local-workspace>\tests\unit\melder\aether\test_frame_view_and_viewer_profiles.py <local-workspace>\tests\unit\melder\aether\test_nexus.py <local-workspace>\tests\unit\melder\aether\test_nexus_frame_surface_projection.py <local-workspace>\tests\integration\melder\aether\test_nexus_frame_surface_projection_integration.py`
  - `python -m pytest -q tests\unit\melder\aether\test_frame_view_and_viewer_profiles.py tests\unit\melder\aether\test_frame_viewer_projection.py tests\unit\melder\aether\test_nexus.py tests\unit\melder\aether\test_nexus_frame_surface_projection.py tests\integration\melder\aether\test_nexus_frame_surface_projection_integration.py tests\unit\melder\aether\test_frame_acl_profile.py tests\unit\melder\aether\test_frame_acl_validator.py`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/frame_view_collapse_to_descriptor_viewer/architecture_patch.md
  - system_docs/patches/active/frame_view_collapse_to_descriptor_viewer/component_patch_frame_viewer.md
  - system_docs/patches/active/frame_view_collapse_to_descriptor_viewer/component_patch_nexus.md
  - system_docs/patches/active/frame_view_collapse_to_descriptor_viewer/component_patch_frame_view.md
  - system_docs/patches/active/frame_view_collapse_to_descriptor_viewer/code_description_patch_descriptor_viewer_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: merge into canonical docs or explicitly retire after the
  runtime collapse settles

## Notes
- DATETIME: 2026-04-06T16:52:25Z
  TYPE: PLAN
  CLAIM: This task is intentionally second. The system should not delete the
    intermediate layer until descriptor<->ACL payload validation is strong
    enough to replace it.
  EVIDENCE:
  - tickets/tasks/2026-04-06_investigate_frame_view_removal_impacts_and_payload_contract_gates.md:1-125
  IMPACT: This task should stay ready, not active, until the payload gate lands.
  NEXT: wait for the payload-validation task to complete first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-06T17:24:39Z
  TYPE: FACT
  CLAIM: The second tranche is now properly staged as a patch-governed
    runtime-cut task. The patch docs define the intended viewer collapse:
    remove `FrameView` from the runtime path, move target/description behavior
    onto `FrameViewer`, and rewire `Nexus` to project viewers directly from
    descriptor truth plus compiled ACL output.
  EVIDENCE:
  - system_docs/patches/active/frame_view_collapse_to_descriptor_viewer/architecture_patch.md:1-40
  - system_docs/patches/active/frame_view_collapse_to_descriptor_viewer/component_patch_frame_viewer.md:1-26
  - system_docs/patches/active/frame_view_collapse_to_descriptor_viewer/component_patch_nexus.md:1-20
  - system_docs/patches/active/frame_view_collapse_to_descriptor_viewer/component_patch_frame_view.md:1-17
  - system_docs/patches/active/frame_view_collapse_to_descriptor_viewer/code_description_patch_descriptor_viewer_flow.md:1-17
  IMPACT: The runtime collapse now has an explicit contract and should not
    devolve into ad hoc deletion.
  NEXT: sync artifact tracking and then start the code changes against this
    patch set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T17:45:40Z
  TYPE: FACT
  CLAIM: The live viewer runtime path is now descriptor-driven. `FrameViewer`
    hosts descriptor references plus compiled ACL surfaces, builds visible
    `FrameLink` targets on demand, and no longer depends on `FrameView` for
    target/query behavior. `Nexus.create_frame_viewer(...)` and the Rift-facing
    viewer builders now populate the viewer directly from descriptor truth plus
    compiled ACL output, and `RiftSpace` selection now validates against the
    viewer surface instead of `FrameView` accessors.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-707
  - src/melder/aether/nexus/nexus.py:1557-1811
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:388-472
  - src/melder/aether/nexus/rift/frame_link/frame_link.py:1-182
  IMPACT: The main runtime objective of the collapse is landed.
  NEXT: decide whether to keep going and hard-delete the dead `FrameView`
    source/tests or spin that into a separate cleanup task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T17:45:40Z
  TYPE: MEASURE
  CLAIM: The focused runtime-collapse slice is green. The compile sanity pass
    succeeded on the touched runtime/test files, and the broader pytest slice
    covering viewer profiles, descriptor-driven viewer behavior, RiftSpace host
    behavior, Nexus projection, the integration viewer path, and the
    payload-validation tests passed with 112 tests green. The warnings were the
    unchanged GIL-enabled runtime warning and pytest cache access-denied noise.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py:1-140
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-292
  - tests/unit/melder/aether/test_nexus.py:1-730
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:1-486
  - tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py:1-176
  - tests/unit/melder/aether/test_frame_acl_profile.py:1-270
  - tests/unit/melder/aether/test_frame_acl_validator.py:1-401
  - command:python -m py_compile <local-workspace>\src\melder\aether\nexus\rift\frame_link\frame_link.py <local-workspace>\src\melder\aether\nexus\rift\frame_viewer\frame_viewer.py <local-workspace>\src\melder\aether\nexus\rift\rift_space\rift_space.py <local-workspace>\src\melder\aether\nexus\nexus.py <local-workspace>\tests\unit\melder\aether\test_frame_viewer_projection.py <local-workspace>\tests\unit\melder\aether\test_frame_view_and_viewer_profiles.py <local-workspace>\tests\unit\melder\aether\test_nexus.py <local-workspace>\tests\unit\melder\aether\test_nexus_frame_surface_projection.py <local-workspace>\tests\integration\melder\aether\test_nexus_frame_surface_projection_integration.py
  - command:python -m pytest -q tests\unit\melder\aether\test_frame_view_and_viewer_profiles.py tests\unit\melder\aether\test_frame_viewer_projection.py tests\unit\melder\aether\test_nexus.py tests\unit\melder\aether\test_nexus_frame_surface_projection.py tests\integration\melder\aether\test_nexus_frame_surface_projection_integration.py tests\unit\melder\aether\test_frame_acl_profile.py tests\unit\melder\aether\test_frame_acl_validator.py
  IMPACT: The runtime path is stable enough to stop and review without claiming
    the dead `FrameView` cleanup is finished.
  NEXT: review whether to continue into hard-delete cleanup in this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T17:52:00Z
  TYPE: FACT
  CLAIM: The dead `FrameView` layer is now actually removed from live source
    and tests. `frame_view.py`, `frame_view_profile.py`, and
    `frame_view_profile_builder.py` are deleted, the dead `create_frame_view(...)`
    path and frame-view cache plumbing are removed from `Nexus`, stale
    view-centric tests were deleted or rewritten, and a final live-source scan
    found no remaining `FrameView`/`FrameViewProfile`/`create_frame_view(...)`
    references outside transient bytecode caches, which were then removed too.
  EVIDENCE:
  - deleted:src/melder/aether/nexus/rift/frame_viewer/frame_view.py
  - deleted:src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile.py
  - deleted:src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile_builder.py
  - src/melder/aether/nexus/nexus.py:1-1870
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-292
  - tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py:1-140
  - tests/component/melder/aether/test_frame_acl_compiler_component.py:1-250
  - tests/integration/melder/aether/test_frame_acl_compiler_integration.py:1-250
  - command:Get-ChildItem -Recurse -File src,tests | Select-String -Pattern '\bFrameView\b|\bFrameViewProfile\b|\bFrameViewProfileBuilder\b|create_frame_view\('
  IMPACT: The repo no longer carries a split-brain live runtime path for frame
    viewing.
  NEXT: review the cleanup result with the user and close or continue as
    directed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
The live runtime path is now descriptor-driven and green. The remaining gap is
cleanup of dead `FrameView` files and stale view-centric tests/methods.

