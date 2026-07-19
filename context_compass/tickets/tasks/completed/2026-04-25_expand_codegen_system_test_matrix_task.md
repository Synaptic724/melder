# Task: Expand Codegen System Test Matrix
- Completed: 2026-04-25T21:13:53Z
- Summary: Closed after the codegen-system test matrix landed at the requested
  executed-case counts with high-signal unit, component, and integration
  coverage across validation, namespace, execution, observability, and live
  room/runtime behavior.

## Metadata
- Task ID: TASK-2026-04-25-expand-codegen-system-test-matrix
- Story: STORY-2026-04-25-expand-codegen-system-test-matrix
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T20:50:00Z
- Updated: 2026-04-25T21:13:53Z

## Objective
Build the requested codegen-system test matrix:
- 400 unit
- 80 component
- 40 integration

using high-signal behavioral coverage rather than filler.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested this lane.
- EXECUTION_BOUNDARY:
  - codegen-system-focused tests under:
    - `tests/unit/melder/aether/`
    - `tests/component/melder/aether/`
    - `tests/integration/melder/aether/`
  - directly required test helpers only
- DEPENDENCIES:
  - `src/melder/aether/nexus/rift/codegen_system/`
- EXIT_GATE: the requested executed-case counts are reached with green focused
  validation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested count pushes the
  lane into low-value filler.

## Scope Boundaries
- In scope:
  - codegen-system-focused unit/component/integration tests
  - directly required test helpers
- Out of scope:
  - unrelated Nexus test expansion
  - runtime feature additions not directly required by tests

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether -k "codegen"`
  - `python -m pytest -q tests/component/melder/aether -k "codegen"`
  - `python -m pytest -q tests/integration/melder/aether -k "codegen"`

## Notes
- DATETIME: 2026-04-25T20:50:00Z
  TYPE: FACT
  CLAIM: The current dedicated codegen-system test surface is still mostly unit
    coverage around ACL profiles/configuration, with no dedicated component or
    integration codegen files yet.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_acl_codegen_builder.py
  - tests/unit/melder/aether/test_frame_acl_codegen_configuration.py
  - tests/unit/melder/aether/test_frame_acl_codegen_full_access_profile.py
  - tests/unit/melder/aether/test_frame_acl_codegen_hybrid_profile.py
  - tests/unit/melder/aether/test_frame_acl_codegen_permissive_profile.py
  - tests/unit/melder/aether/test_frame_acl_codegen_profile.py
  - tests/unit/melder/aether/test_frame_acl_codegen_safe_profile.py
  - tests/unit/melder/aether/test_frame_acl_codegen_validation_profiles.py
  IMPACT: The requested matrix is a real expansion lane, not an incremental top-up.
  NEXT: inspect the runtime files and start building the unit matrix around the
    internal codegen-system seams first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:09:50Z
  TYPE: FACT
  CLAIM: The codegen-system test expansion is now implemented as a real matrix
    across three levels:
    - unit matrices for validation strategies, namespace/runtime objects,
      system orchestration, and support/result objects
    - component matrix over a real `CodegenSystem` with small room/projection
      doubles
    - integration matrix through the live
      `Nexus -> Rift -> CodegenRiftSpace -> CodegenCommandSystem` path
  EVIDENCE:
  - tests/_codegen_system_support.py:1-205
  - tests/unit/melder/aether/test_codegen_validation_strategy_unit_matrix.py:1-519
  - tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py:1-382
  - tests/unit/melder/aether/test_codegen_system_unit_matrix.py:1-324
  - tests/unit/melder/aether/test_codegen_support_object_unit_matrix.py:1-155
  - tests/component/melder/aether/test_codegen_system_component_matrix.py:1-183
  - tests/integration/melder/aether/test_codegen_system_integration_matrix.py:1-136
  IMPACT: The codegen-system runtime now has a materially denser and more
    structured test surface instead of scattered codegen checks.
  NEXT: return the matrix for review and let the user inspect the new files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:09:50Z
  TYPE: MEASURE
  CLAIM: The requested executed-case counts are met on explicit rings:
    - unit: 414 passed
    - component: 80 passed
    - integration: 40 passed
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_codegen_builder.py tests/unit/melder/aether/test_frame_acl_codegen_configuration.py tests/unit/melder/aether/test_frame_acl_codegen_full_access_profile.py tests/unit/melder/aether/test_frame_acl_codegen_hybrid_profile.py tests/unit/melder/aether/test_frame_acl_codegen_permissive_profile.py tests/unit/melder/aether/test_frame_acl_codegen_profile.py tests/unit/melder/aether/test_frame_acl_codegen_safe_profile.py tests/unit/melder/aether/test_frame_acl_codegen_validation_profiles.py tests/unit/melder/aether/test_codegen_validation_strategy_unit_matrix.py tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py tests/unit/melder/aether/test_codegen_system_unit_matrix.py tests/unit/melder/aether/test_codegen_support_object_unit_matrix.py` -> `414 passed, 2 warnings`
  - validation_result: `python -m pytest -q tests/component/melder/aether/test_codegen_system_component_matrix.py` -> `80 passed, 2 warnings`
  - validation_result: `python -m pytest -q tests/integration/melder/aether/test_codegen_system_integration_matrix.py` -> `40 passed, 2 warnings`
  IMPACT: The requested count target is satisfied without leaving this lane in
    a half-built state.
  NEXT: hold the lane in review until the user inspects the new matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
