# Task: Expand Codegen Rift JSON Harness Integration

## Metadata
- Task ID: TASK-2026-04-25-expand-codegen-rift-json-harness-integration
- Story: STORY-2026-04-25-expand-codegen-rift-json-harness-integration
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T21:13:53Z
- Updated: 2026-04-25T21:35:17Z

## Objective
Build a codegen-room JSON harness and add 40 more real integration cases around
turn-based codegen usage, frame links, workstation bindings, live objects, and
hooks.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for 40 more real harness-driven
  integration tests.
- EXECUTION_BOUNDARY:
  - `tests/integration/melder/aether/rift/codegen_rift_json_testbench_support.py`
  - `tests/integration/melder/aether/rift/test_codegen_rift_json_testbench_integration.py`
  - directly required helper support only
- DEPENDENCIES:
  - existing static/capability JSON bench support files under
    `tests/integration/melder/aether/rift/`
- EXIT_GATE: the codegen JSON harness exists and the new 40-case integration
  ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current codegen-room
  public surface cannot support the requested turn-based harness scenarios.

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py src/melder/aether/nexus/rift/codegen_system/execution/codegen_executor.py tests/unit/melder/aether/test_codegen_validation_strategy_unit_matrix.py tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py tests/integration/melder/aether/rift/codegen_rift_json_testbench_support.py tests/integration/melder/aether/rift/test_codegen_rift_json_testbench_integration.py`
- `python -m pytest -q tests/unit/melder/aether/test_codegen_validation_strategy_unit_matrix.py -k "name_resolution"` -> `38 passed, 133 deselected`
- `python -m pytest -q tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py` -> `76 passed`
- `python -m pytest -q tests/integration/melder/aether/rift/test_codegen_rift_json_testbench_integration.py` -> `40 passed`

## Notes
- DATETIME: 2026-04-25T21:13:53Z
  TYPE: PLAN
  CLAIM: The harness contract is clear enough to implement directly:
    - live `Nexus -> Rift -> CodegenRiftSpace`
    - manifest placeholders
    - request dispatch
    - turn scripts
    - live hooks around codegen actions
    - frame creation/linking and workstation/result flows
  EVIDENCE:
  - user_instruction: requested frames, links, objects, codegen, and hooks
  IMPACT: The task can go straight into harness implementation.
  NEXT: build the codegen JSON harness support file first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:32:44Z
  TYPE: MEASURE
  CLAIM: The codegen-room JSON harness is now landed and green with 40 real
    turn-based integration scenarios. The harness exercises live codegen
    validation/execution, frame-link behavior, workstation persistence,
    recursive codegen posture, and room/action hooks through a reusable
    `CodegenRiftJsonBench`.
  EVIDENCE:
  - tests/integration/melder/aether/rift/codegen_rift_json_testbench_support.py:1-349
  - tests/integration/melder/aether/rift/test_codegen_rift_json_testbench_integration.py:1-1011
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:1-205
  - src/melder/aether/nexus/rift/codegen_system/execution/codegen_executor.py:1-90
  IMPACT: The requested second integration tranche is real and the harness
    exposed/fixed two runtime issues while landing:
    - normal local parameter names like `self` were incorrectly rejected
    - split exec globals/locals broke normal top-level class-reference flows
  NEXT: return the lane for user review and close it only if accepted.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:35:17Z
  TYPE: MEASURE
  CLAIM: The harness task is complete and ready to archive. The requested 40
    additional harness-driven codegen integration tests are landed and green,
    and the cleanup work surfaced no remaining active artifact-board state for
    this lane.
  EVIDENCE:
  - tests/integration/melder/aether/rift/test_codegen_rift_json_testbench_integration.py:1-1011
  - tests/integration/melder/aether/rift/codegen_rift_json_testbench_support.py:1-349
  IMPACT: The task can move to `completed/` without leaving stale routing or
    validation ambiguity behind.
  NEXT: none
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
