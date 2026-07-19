# Task: Bind FrameViewer Profiles To Frames Through Rift
- Completed: 2026-04-09T11:31:39Z
- Summary: Bound one selected viewer profile per frame and routed frame-specific viewer creation through Rift.


## Metadata
- Task ID: TASK-2026-04-06-bind-frame-viewer-profiles-to-frames-through-rift
- Story: STORY-2026-04-06-validate-descriptor-acl-payload-contracts-and-collapse-frame-view
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T18:41:02Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Bind one selected `FrameViewerProfile` to one frame's descriptor + ACL state,
route the frame-specific viewer creation transaction through `Rift`, and make
per-frame profile selection explicit on the descriptor-driven viewer path.

## Ticket Contract
- ENTRY_GATE: the dead `FrameView` runtime layer is removed and the
  descriptor-driven viewer path is green.
- EXECUTION_BOUNDARY: frame-bound profile references and Rift-scoped
  frame-specific viewer creation only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile_builder.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
  - src/melder/aether/nexus/nexus.py
- EXIT_GATE: the viewer has one selected profile per frame, the selected
  profile is bound by reference to that frame's descriptor + ACL state, and
  `Rift` can create a frame-specific viewer transaction only when the contract
  allows the frame.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a separate binding object is
  required instead of binding the selected profile directly.

## Scope Boundaries
- In scope:
  - profile binding to frame descriptor + ACL state
  - per-frame selected profile tracking on `FrameViewer`
  - Rift frame-specific viewer creation transaction
  - focused unit tests
- Out of scope:
  - new snapshot/view layers
  - codegen execution
  - mutation work

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py`
- `python -m py_compile src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py`
- `python -m py_compile src/melder/aether/nexus/rift/rift.py`
- `python -m py_compile src/melder/aether/nexus/nexus.py`
- `python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py`
- `python -m pytest -q tests/unit/melder/aether/test_nexus.py`
- `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_surface_projection.py`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/frame_bound_viewer_profile_binding/architecture_patch.md
  - system_docs/patches/active/frame_bound_viewer_profile_binding/component_patch_frame_viewer_profile.md
  - system_docs/patches/active/frame_bound_viewer_profile_binding/component_patch_frame_viewer.md
  - system_docs/patches/active/frame_bound_viewer_profile_binding/component_patch_rift.md
  - system_docs/patches/active/frame_bound_viewer_profile_binding/code_description_patch_frame_bound_profile_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: merge into canonical docs or explicitly retire after the
  frame-bound profile model settles

## Notes
- DATETIME: 2026-04-06T18:41:02Z
  TYPE: PLAN
  CLAIM: The cleaned viewer path still lacks one explicit runtime concept:
    the selected profile for a specific frame should be bound by reference to
    that frame's descriptor and ACL state, and the public transaction that
    creates that frame-specific viewer surface should start from `Rift` after
    checking the frame-availability contract.
  EVIDENCE:
  - user_instruction: "the profile itself should take in a single FrameDescriptor and the ACLConfiguration"
  - user_instruction: "the rift itself should have a method called create new frame_view and this method does the entire transaction targetting a specific frame if the contract exists"
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-707
  - src/melder/aether/nexus/rift/rift.py:1-581
  IMPACT: The next slice should add frame-bound profile references and a Rift
    transaction boundary without reopening the dead `FrameView` model.
  NEXT: add patch docs, then bind selected profiles per frame and add the Rift
    frame-specific viewer creation method.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T18:57:49Z
  TYPE: FACT
  CLAIM: The interrupted frame-bound binding slice is already partially landed
    in source. `FrameViewerProfile` now carries frame-bound reference fields
    plus ACL-view requirements, `FrameViewer` now tracks ACL configurations and
    selected profiles by frame, `Nexus` now seeds per-frame selected profile
    state and exposes a frame-specific Rift viewer builder, and `Rift` now has
    `engage_frame(...)` plus `create_new_frame_viewer(...)`. This tranche has
    not been compile- or test-validated yet after the interruption.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:1-568
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-999
  - src/melder/aether/nexus/nexus.py:1494-1680
  - src/melder/aether/nexus/rift/rift.py:390-538
  IMPACT: The next safe step is validation and repair of the partial slice, not
    a fresh reimplementation.
  NEXT: inspect the touched symbols for completeness, run focused compile/tests,
    and fix the slice until the frame-bound profile flow is green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T18:57:49Z
  TYPE: FACT
  CLAIM: The first focused validation pass is failing in two specific places.
    First, the new `FrameViewerProfile.bind_to_frame(...)` configuration-id
    equality check rejects the existing test helpers because
    `FrameACLConfiguration.create_default(...)` generates a new configuration id
    while the compiled access surface fixtures still use fixed ids like
    `ops-cfg`. Second, `Rift.engage_frame(...)` currently trips Nexus target
    frame budget checks in tests that create a Rift with the default frame and
    then engage one more frame while multiple target frames remain disabled.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_viewer_projection.py:127-127
  - tests/unit/melder/aether/test_nexus.py:164-164
  - tests/unit/melder/aether/test_nexus.py:760-791
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:448-454
  - src/melder/aether/nexus/rift/rift.py:423-434
  - src/melder/aether/nexus/nexus.py:2492-2501
  IMPACT: The slice is structurally close, but it needs either fixture
    realignment or contract relaxation for configuration identity, plus a
    correct Rift-engagement rule that does not collide with existing target
    frame budget semantics.
  NEXT: inspect the failing helpers and the target-frame budget semantics, then
    decide whether to fix runtime behavior, tests, or both.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T19:02:07Z
  TYPE: MEASURE
  CLAIM: The frame-bound viewer-profile slice is now green on the focused
    runtime tests. `FrameViewerProfile` can bind clones by reference to one
    frame's descriptor + ACL state, `FrameViewer` keeps one selected bound
    profile per frame and now rebinds the default frame when
    `set_default_profile(...)` changes, `Rift` can engage a frame and create a
    frame-specific viewer transaction through `Nexus`, and the focused tests
    were realigned to the stricter configuration-id and target-frame-budget
    contracts instead of weakening those runtime checks.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:389-547
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:673-744
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:977-999
  - src/melder/aether/nexus/rift/rift.py:393-537
  - src/melder/aether/nexus/nexus.py:1623-1684
  - tests/unit/melder/aether/test_frame_viewer_projection.py:93-135
  - tests/unit/melder/aether/test_frame_viewer_projection.py:196-358
  - tests/unit/melder/aether/test_nexus.py:135-164
  - tests/unit/melder/aether/test_nexus.py:741-799
  IMPACT: The task exit gate is satisfied and this slice can move to user
    review instead of staying in implementation.
  NEXT: review the frame-bound profile binding tranche and either accept it or
    direct the next Nexus viewer step.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This is the next live Nexus step after the descriptor-driven viewer cleanup. It
binds selected viewer profiles to frame-specific descriptor + ACL state and
routes the frame-specific transaction through Rift.

