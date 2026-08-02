# Story: Expand Codegen Rift JSON Harness Integration

## Metadata
- Story ID: STORY-2026-04-25-expand-codegen-rift-json-harness-integration
- Epic: EPIC-2026-04-25-expand-codegen-rift-json-harness-integration
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T21:13:53Z
- Updated: 2026-04-25T21:35:17Z

## User Narrative
As an engineer, I want a real codegen-room JSON harness and a turn-based
integration suite around it, so codegen is exercised the way an agent would
actually use it instead of only through direct method calls.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested this second integration tranche.
- EXECUTION_BOUNDARY:
  - `tests/integration/melder/aether/rift/`
  - directly required support helpers
- DEPENDENCIES:
  - `tickets/tasks/2026-04-25_expand_codegen_rift_json_harness_integration_task.md`
- EXIT_GATE: the JSON harness and 40 integration cases are implemented and
  green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested turn script
  behavior exceeds the current codegen-room public surface.

## Notes
- DATETIME: 2026-04-25T21:13:53Z
  TYPE: PLAN
  CLAIM: The story should mirror the existing Rift JSON bench pattern:
    request dispatch, turn scripts, manifest placeholders, and live room
    surfaces, but target the codegen room and codegen command seams instead.
  EVIDENCE:
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:1-420
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:1-430
  IMPACT: The new suite can stay native to the repo's current integration style.
  NEXT: implement the task with a codegen-specific harness and 40 cases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:32:44Z
  TYPE: MEASURE
  CLAIM: The story is now materially landed. The codegen room has a real
    JSON-bench integration surface and the 40-case turn-script matrix is
    green.
  EVIDENCE:
  - tests/integration/melder/aether/rift/codegen_rift_json_testbench_support.py:1-349
  - tests/integration/melder/aether/rift/test_codegen_rift_json_testbench_integration.py:1-1011
  IMPACT: Codegen now has an agent-like integration harness in the same
    family as the static and capability benches instead of only direct-call
    integration coverage.
  NEXT: return the story for user review and close it only if accepted.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T21:35:17Z
  TYPE: MEASURE
  CLAIM: The story is complete. The codegen room now has a reusable
    harness-driven integration surface plus a green 40-scenario turn-script
    suite that exercises the room the way an agent actually uses it.
  EVIDENCE:
  - tests/integration/melder/aether/rift/codegen_rift_json_testbench_support.py:1-349
  - tests/integration/melder/aether/rift/test_codegen_rift_json_testbench_integration.py:1-1011
  IMPACT: The story can move to `completed/` and stop occupying active routing.
  NEXT: none
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
