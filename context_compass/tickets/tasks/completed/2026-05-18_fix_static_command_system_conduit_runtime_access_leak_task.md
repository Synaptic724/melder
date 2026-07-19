# Task: fix static command system conduit runtime access leak

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-static-command-system-conduit-runtime-access-leak
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T14:37:53Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the next `nexus`-lane blocker by stopping `StaticCommandSystem` from
exposing direct conduit runtime-object helpers that belong to broader room types.

## Ticket Contract
- ENTRY_GATE: the next stop-on-first `-k nexus` failure is
  `test_static_room_does_not_expose_direct_conduit_runtime_object_access`
  because `StaticCommandSystem.get_conduit_by_id(...)` still resolves through the
  inherited base helper.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/command_system/static_command_system.py`
  - directly implicated static-room tests in
    `tests/unit/melder/aether/test_nexus.py`
- DEPENDENCIES:
  - current `nexus` test-driving lane
  - static-room command-surface contract
- EXIT_GATE:
  - the targeted static-room runtime-access unit test is green
  - static rooms no longer expose the leaked direct conduit runtime helper
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if source evidence shows static
  rooms are supposed to expose this runtime helper after all

## Scope Boundaries
- In scope:
  - static-room runtime surface leak for direct conduit object access
- Out of scope:
  - broader interface graph cleanup
  - capability/codegen room redesign
  - unrelated Nexus failures after this one

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the next live `nexus` blocker is a bounded static-room
  runtime surface leak with direct source and test evidence

## Steps / Checklist
- [ ] confirm the inherited helper leak and static-room contract
- [ ] patch the smallest truthful runtime denial at `StaticCommandSystem`
- [ ] rerun the targeted static-room unit test
- [ ] continue to the next `nexus` blocker only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- a bounded static-room runtime surface fix

## Files / Paths Impacted
- `src/melder/aether/nexus/rift/command_system/static_command_system.py`
- `tests/unit/melder/aether/test_nexus.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\aether\test_nexus.py::test_static_room_does_not_expose_direct_conduit_runtime_object_access`

## Risks / Rollback Notes
- Low risk if the fix stays limited to the leaked static-room runtime helper.
- Medium risk if other static-room command helpers rely on the inherited direct
  conduit-object access path unexpectedly.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-18T14:37:53Z
  TYPE: FACT
  CLAIM: The next `nexus` blocker is a real static-room surface leak.
    `StaticCommandSystem` inherits `get_conduit_by_id(...)` from the base
    `CommandSystem`, and that helper still resolves a live conduit object even
    though the static-room tests and supported-method contract say static rooms
    do not expose direct conduit runtime helpers.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:3660-3699
  - tests/unit/melder/aether/test_nexus.py:5098-5113
  - src/melder/aether/nexus/rift/command_system/command_system.py:316-334
  - src/melder/aether/nexus/rift/command_system/command_system.py:177-198
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:12-33
  IMPACT: The `nexus` suite now stops on a runtime contract mismatch instead of a
    stale test.
  NEXT: patch `StaticCommandSystem` so the leaked direct conduit runtime helper
    is no longer exposed, then rerun the targeted unit test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:37:53Z
  TYPE: PLAN
  CLAIM: The smallest truthful runtime fix is to override the leaked static-room
    direct conduit-object helpers on `StaticCommandSystem` itself and raise
    `AttributeError`, matching both the static supported-method contract and the
    existing absent-method test style.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:12-33
  - src/melder/aether/nexus/rift/command_system/command_system.py:177-198
  - tests/unit/melder/aether/test_nexus.py:3660-3699
  - tests/unit/melder/aether/test_nexus.py:5098-5113
  IMPACT: This keeps the lane bounded to static-room surface exposure and avoids
    widening into broader interface cleanup right now.
  NEXT: add explicit static-room stubs for the leaked conduit-object helpers, then
    rerun the targeted unit test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-18T14:37:53Z
  TYPE: MEASURE
  CLAIM: The targeted static-room conduit runtime leak is green.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:33-119
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\aether\test_nexus.py::test_static_room_does_not_expose_direct_conduit_runtime_object_access` -> `1 passed`
  IMPACT: This `nexus` blocker is cleared, so the next useful move is another
    stop-on-first `-k nexus` pass.
  NEXT: rerun `pytest -vv -x --tb=long -k nexus` and route the next failure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active `nexus` lane for the next real runtime contract mismatch. The current
leak is limited to static-room direct conduit runtime access.
