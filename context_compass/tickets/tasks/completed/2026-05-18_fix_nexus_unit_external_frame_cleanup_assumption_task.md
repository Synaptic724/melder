# Task: fix nexus unit external frame cleanup assumption

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-nexus-unit-external-frame-cleanup-assumption
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T14:45:16Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the next `nexus`-lane blocker by aligning the unit test for external frame
cleanup to the owner-driven frame-disposal contract.

## Ticket Contract
- ENTRY_GATE: the next stop-on-first `-k nexus` failure is
  `test_external_aether_frame_cleanup_clears_nexus_frame_manager_state`
  calling `rift.get_nexus_frame().cleanup()` while expecting external Aether frame
  disposal semantics.
- EXECUTION_BOUNDARY:
  - `tests/unit/melder/aether/test_nexus.py`
- DEPENDENCIES:
  - current `nexus` test-driving lane
  - owner-driven frame cleanup contract
- EXIT_GATE:
  - the targeted unit test is green
  - the test performs actual frame-owner cleanup instead of conduit cleanup
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if source evidence shows conduit
  cleanup should again collapse the frame manager state directly

## Scope Boundaries
- In scope:
  - the single unit-test assumption drift around external frame cleanup
- Out of scope:
  - runtime cleanup semantics
  - unrelated Nexus failures after this one

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the next live `nexus` blocker is a bounded unit-test
  cleanup assumption drift

## Steps / Checklist
- [ ] confirm the mismatch between the test name/intent and the actual cleanup call
- [ ] patch the unit test to use owner-driven frame cleanup
- [ ] rerun the targeted unit test
- [ ] continue to the next `nexus` blocker only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- a narrow Nexus unit-test cleanup correction

## Files / Paths Impacted
- `tests/unit/melder/aether/test_nexus.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\aether\test_nexus.py::test_external_aether_frame_cleanup_clears_nexus_frame_manager_state`

## Risks / Rollback Notes
- Low risk. This lane should remain unit-test only.

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
- DATETIME: 2026-05-18T14:45:16Z
  TYPE: FACT
  CLAIM: The next `nexus` blocker is another cleanup-assumption drift. The unit
    test says “external Aether frame cleanup” but it currently executes
    `rift.get_nexus_frame().cleanup()`, which is conduit cleanup rather than
    owner-driven frame disposal.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:5996-6012
  - tests/integration/melder/aether/test_aether_integration_frames.py:387-387
  IMPACT: The unit test is asserting the right outcome through the wrong action,
    so it fails under the current cleanup contract.
  NEXT: patch the unit test to call `nexus._aether._ensure_frame(frame_name).cleanup()`,
    then rerun the targeted unit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:45:16Z
  TYPE: MEASURE
  CLAIM: The targeted external-frame-cleanup unit is green after switching the
    test to real owner-driven frame cleanup.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:5996-6012
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\aether\test_nexus.py::test_external_aether_frame_cleanup_clears_nexus_frame_manager_state` -> `1 passed`
  IMPACT: This `nexus` blocker is cleared, so the next useful move is another
    stop-on-first `-k nexus` pass.
  NEXT: rerun `pytest -vv -x --tb=long -k nexus` and route the next failure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active `nexus` lane for a narrow unit-test cleanup assumption drift. Current
evidence points to a unit-only fix, not a runtime regression.
