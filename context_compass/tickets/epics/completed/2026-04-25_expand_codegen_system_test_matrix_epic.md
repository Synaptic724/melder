# Epic: Expand Codegen System Test Matrix
- Completed: 2026-04-25T21:13:53Z
- Summary: Closed after the codegen-system test-expansion program met the
  requested executed-case counts and produced a bounded, source-backed test
  matrix over the real runtime seams.

## Metadata
- Epic ID: EPIC-2026-04-25-expand-codegen-system-test-matrix
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T20:50:00Z
- Updated: 2026-04-25T21:13:53Z

## Problem / Opportunity
The codegen-system runtime is now large enough that the current test surface is
too thin relative to its moving parts. The user explicitly wants an aggressive
test build-out around the `codegen_system` lane:
- 400 unit tests
- 80 component tests
- 40 integration tests

The right response is not filler. It is one high-signal matrix built around the
actual codegen seams:
- validation strategies
- namespace strategies
- compiler/executor
- observability
- room orchestration
- profile-driven ACL behavior

## MRP Alignment (Most Reasonable Product)
The MRP is not “some more tests.”

The MRP is:
- one explicit epic owning the codegen-system test expansion
- high-signal unit/component/integration matrices
- counts achieved through real contract coverage and parameterized execution,
  not attribute/existence filler
- focused validation rings kept green while the matrix expands

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a full codegen-system test build-out.
- EXECUTION_BOUNDARY: codegen-system tests and directly required test helpers
  only.
- DEPENDENCIES:
  - `src/melder/aether/nexus/rift/codegen_system/`
  - `tests/unit/melder/aether/`
  - `tests/component/melder/aether/`
  - `tests/integration/melder/aether/`
- EXIT_GATE: the codegen-system test matrix reaches the requested executed-case
  counts with green focused validation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a requested count would force
  low-value filler instead of real behavioral coverage.

## Goals (Outcomes)
- audit the current codegen-system test surface
- build a high-signal unit matrix around codegen-system internals
- build a high-signal component matrix around small real wiring slices
- build a high-signal integration matrix around real room/runtime behavior
- meet the requested counts without fake tests

## Non-Goals (Explicit Exclusions)
- unrelated Nexus-wide test expansion outside codegen seams
- runtime feature additions unrelated to testing
- broad repo-wide quality sweeps

## Notes
- DATETIME: 2026-04-25T20:50:00Z
  TYPE: DECISION
  CLAIM: This needs its own explicit test-expansion lane instead of getting
    mixed into the current codegen implementation stories. The user asked for a
    very large bounded test program, so the ticketing and routing need to make
    that a first-class effort.
  EVIDENCE:
  - user_instruction: requested 400 unit, 80 component, and 40 integration tests for codegen system
  IMPACT: The test build-out is now an explicit program lane with its own
    acceptance target and anti-filler constraint.
  NEXT: stage the story/task and start the test-surface audit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:09:50Z
  TYPE: MEASURE
  CLAIM: The codegen-system test-expansion epic is now implemented to the
    requested executed-case counts:
    - 414 unit
    - 80 component
    - 40 integration
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-04-25_expand_codegen_system_test_matrix_task.md:1-91
  - tests/unit/melder/aether/test_codegen_validation_strategy_unit_matrix.py:1-519
  - tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py:1-382
  - tests/unit/melder/aether/test_codegen_system_unit_matrix.py:1-324
  - tests/unit/melder/aether/test_codegen_support_object_unit_matrix.py:1-155
  - tests/component/melder/aether/test_codegen_system_component_matrix.py:1-183
  - tests/integration/melder/aether/test_codegen_system_integration_matrix.py:1-136
  IMPACT: The lane can move to review while the user inspects the test matrix.
  NEXT: wait for review feedback or a follow-on gap callout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
