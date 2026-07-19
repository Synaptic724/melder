# Task: Expand Viewer Surface Matrix Coverage For Descriptor Host And Helpers
- Completed: 2026-04-09T11:31:39Z
- Summary: Added the large viewer-surface regression matrix for descriptor-host and helper behavior.


## Metadata
- Task ID: TASK-2026-04-07-expand-viewer-surface-matrix-coverage-for-descriptor-host-and-helpers
- Story: STORY-2026-04-06-contract-backed-assigned-frame-views
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-07T00:16:19Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Add a large new regression matrix for the expanded descriptor-host
`FrameViewer` surface plus the widened `view_frame`, `view_conduit`, and
`view_spell` helper methods.

## Ticket Contract
- ENTRY_GATE: the expanded viewer/runtime surface is landed and green, and the
  user explicitly requested another large test tranche with strong unit,
  component, and integration counts.
- EXECUTION_BOUNDARY: viewer-surface tests only.
- DEPENDENCIES:
  - tests/_nexus_viewer_matrix_support.py
  - tests/unit/melder/aether/
  - tests/component/melder/aether/
  - tests/integration/melder/aether/
  - src/melder/aether/nexus/rift/frame_viewer/
- EXIT_GATE: at least 300 new unit cases, 80 new component cases, and 50 new
  integration cases are added for the expanded viewer surface and the targeted
  validation slices pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current runtime/test
  scaffolding cannot support the requested counts without introducing broader
  fixture architecture work first.

## Scope Boundaries
- In scope:
  - descriptor-host matrix tests
  - `view_frame` matrix tests
  - `view_conduit` matrix tests
  - `view_spell` matrix tests
  - component/integration viewer transaction matrix tests
  - test helpers/fixtures needed for the new surface
- Out of scope:
  - runtime feature changes unless a real bug is exposed
  - mutation work
  - descriptor payload schema changes

## Validation
- `python -m py_compile tests/_nexus_viewer_matrix_support.py`
- `python -m py_compile tests/unit/melder/aether/test_nexus_viewer_general_helper_matrix.py`
- `python -m py_compile tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py`
- `python -m py_compile tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py`
- `python -m pytest -q tests/unit/melder/aether/test_nexus_viewer_general_helper_matrix.py`
- `python -m pytest -q tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py`
- `python -m pytest -q tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py`

## Notes
- DATETIME: 2026-04-07T00:16:19Z
  TYPE: PLAN
  CLAIM: The runtime surface just got much larger, so the next correct move is
    a dedicated viewer-surface matrix expansion instead of burying a giant test
    push inside the runtime task. The user explicitly wants another large
    tranche with strong category floors:
    - 300 new unit cases
    - 80 new component cases
    - 50 new integration cases
    The right shape is to widen the existing viewer matrix support/helpers
    around the new descriptor-host methods, the new frame/conduit/spell helper
    methods, and the new detailed dunder-member path.
  EVIDENCE:
  - user_instruction: "add tests for all the new stuff you made continue"
  - user_instruction: "I want 300 Unit, 80 component and 50 integration tests"
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:502-1290
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:252-698
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:174-497
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:178-777
  IMPACT: This needs to be treated as a real matrix-expansion program, not a
    few appended spot tests.
  NEXT: inspect the current viewer matrix support and map the new host/helper
    methods into large parametric unit/component/integration test sets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T00:16:19Z
  TYPE: MEASURE
  CLAIM: The viewer-surface matrix expansion is now green and meets the
    requested floors:
    - 304 new unit cases
    - 80 new component cases
    - 50 new integration cases
    The new files cover the expanded descriptor-host `FrameViewer` methods,
    the widened `view_frame` / `view_conduit` / `view_spell` helper surface,
    and the real Nexus/Rift viewer execution path. The broader targeted
    viewer/Nexus validation slice is also green after integrating the new
    files.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py:1-371
  - tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py:1-451
  - tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py:1-153
  - tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py:1-237
  - validation_result: "python -m pytest --collect-only -q tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py" -> 304 collected
  - validation_result: "python -m pytest --collect-only -q tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py" -> 80 collected
  - validation_result: "python -m pytest --collect-only -q tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py" -> 50 collected
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_nexus_viewer_general_helper_matrix.py tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py" -> 775 passed
  IMPACT: The expanded viewer surface now has a substantially deeper regression
    net, including the new descriptor-host methods and detailed dunder-member
    visibility path.
  NEXT: review the new matrix tranche and either accept it or direct another
    round of viewer-surface testing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task isolates the large post-expansion viewer-surface test push from the
runtime implementation lane so the counts and validation target stay explicit.

