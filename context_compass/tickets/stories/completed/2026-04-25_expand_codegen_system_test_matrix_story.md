# Story: Expand Codegen System Test Matrix
- Completed: 2026-04-25T21:13:53Z
- Summary: Closed after the codegen-system lane landed a three-level matrix
  with explicit unit, component, and integration coverage instead of a count
  chase.

## Metadata
- Story ID: STORY-2026-04-25-expand-codegen-system-test-matrix
- Epic: EPIC-2026-04-25-expand-codegen-system-test-matrix
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T20:50:00Z
- Updated: 2026-04-25T21:13:53Z

## User Narrative
As an engineer, I want an aggressive test matrix around the codegen-system
runtime so the codegen lane is hardened through real behavioral coverage
instead of scattered smoke tests.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested this test-expansion pass.
- EXECUTION_BOUNDARY:
  - `tests/unit/melder/aether/`
  - `tests/component/melder/aether/`
  - `tests/integration/melder/aether/`
  - directly required test helpers
- DEPENDENCIES:
  - `tickets/tasks/2026-04-25_expand_codegen_system_test_matrix_task.md`
- EXIT_GATE: the requested counts are met with high-signal matrices.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the count target can only be
  met with low-value filler.

## Notes
- DATETIME: 2026-04-25T20:50:00Z
  TYPE: PLAN
  CLAIM: The story should be built around the codegen-system seams we actually
    own now: validation, namespace, execution, observability, room orchestration,
    and profile-driven ACL behavior.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py
  - src/melder/aether/nexus/rift/codegen_system/validation/
  - src/melder/aether/nexus/rift/codegen_system/namespace/
  - src/melder/aether/nexus/rift/codegen_system/execution/
  - src/melder/aether/nexus/rift/codegen_system/observability/
  IMPACT: The test lane can be decomposed into meaningful matrices instead of a
    raw count chase.
  NEXT: audit the current codegen test surface and build the first tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:09:50Z
  TYPE: FACT
  CLAIM: The story is now implemented and the requested three-level matrix is
    real: internal unit seams, small real-wiring component seams, and full
    live room/runtime integration seams are all covered.
  EVIDENCE:
  - tests/unit/melder/aether/test_codegen_validation_strategy_unit_matrix.py:1-519
  - tests/component/melder/aether/test_codegen_system_component_matrix.py:1-183
  - tests/integration/melder/aether/test_codegen_system_integration_matrix.py:1-136
  IMPACT: This lane is ready for review on both quality and count, not just on
    a partial first tranche.
  NEXT: return the story for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
