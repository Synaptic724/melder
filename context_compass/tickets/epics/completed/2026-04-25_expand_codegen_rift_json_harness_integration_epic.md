# Epic: Expand Codegen Rift JSON Harness Integration

## Metadata
- Epic ID: EPIC-2026-04-25-expand-codegen-rift-json-harness-integration
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T21:13:53Z
- Updated: 2026-04-25T21:35:17Z

## Problem / Opportunity
The earlier codegen integration matrix proved the live room/runtime path, but it
did not use the existing Rift JSON harness style the way the static and
capability suites do. The user explicitly wants a second integration tranche
that tests codegen in a more agent-like turn-based way:
- through a JSON harness
- across frames and frame links
- with created runtime objects and workstation bindings
- with codegen itself driving the work
- with hooks explicitly exercised

## MRP Alignment (Most Reasonable Product)
The MRP is:
- one `CodegenRiftJsonBench`
- one integration suite with 40 more real cases
- turn-script and request-driven execution over the live codegen room
- explicit coverage for hooks, frame links, workstation bindings, and codegen
  behavior

## Ticket Contract
- ENTRY_GATE: the user explicitly rejected the earlier matrix as insufficiently
  harness-driven and asked for 40 more real integration tests.
- EXECUTION_BOUNDARY: codegen JSON harness support and integration tests only.
- DEPENDENCIES:
  - `tests/integration/melder/aether/rift/`
  - `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
  - `src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py`
- EXIT_GATE: the codegen JSON harness exists and 40 focused integration cases
  are green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested turn-based
  harness needs wider runtime support than the current codegen room exposes.

## Notes
- DATETIME: 2026-04-25T21:13:53Z
  TYPE: DECISION
  CLAIM: This needs a second integration tranche, not a rewording of the
    existing matrix. The right fix is to use the same JSON bench style already
    present for static and capability rooms.
  EVIDENCE:
  - user_instruction: requested 40 more integration tests using the mock system and harness
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:1-337
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:1-399
  IMPACT: The new integration lane is now explicitly harness-driven.
  NEXT: stage the story/task and build the codegen JSON harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:32:44Z
  TYPE: MEASURE
  CLAIM: The epic outcome is now in place. Codegen has a dedicated JSON
    harness plus a green 40-case turn-script suite covering validation,
    execution, frame navigation, workstation-bound runtime objects, and hook
    sequencing.
  EVIDENCE:
  - tests/integration/melder/aether/rift/codegen_rift_json_testbench_support.py:1-349
  - tests/integration/melder/aether/rift/test_codegen_rift_json_testbench_integration.py:1-1011
  - src/melder/aether/nexus/rift/codegen_system/execution/codegen_executor.py:1-90
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:1-205
  IMPACT: The second integration tranche is no longer a request or a promise;
    it is a real harness lane that also hardened the live codegen runtime.
  NEXT: wait for user review before closing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:35:17Z
  TYPE: MEASURE
  CLAIM: The epic outcome is complete. Codegen now has the requested
    second integration tranche in the native Rift JSON harness style, and the
    implementation also hardened live name-resolution and exec behavior.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:1-205
  - src/melder/aether/nexus/rift/codegen_system/execution/codegen_executor.py:1-90
  - tests/integration/melder/aether/rift/test_codegen_rift_json_testbench_integration.py:1-1011
  IMPACT: The epic can move to `completed/` and drop out of active routing.
  NEXT: none
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
