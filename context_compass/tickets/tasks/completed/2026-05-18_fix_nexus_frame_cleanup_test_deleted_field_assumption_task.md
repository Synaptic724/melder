# Task: fix nexus frame cleanup test deleted field assumption

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-nexus-frame-cleanup-test-deleted-field-assumption
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T14:35:07Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the first `nexus`-lane blocker by aligning the integration cleanup test with
the current deleted-owned-fields cleanup contract.

## Ticket Contract
- ENTRY_GATE: the first stop-on-first `-k nexus` failure is
  `test_integration_nexus_frame_cleanup_matrix[external-single]`
  reading `conduit._aetheric_frame` after `conduit.cleanup()`.
- EXECUTION_BOUNDARY:
  - `tests/integration/melder/aether/test_nexus_frame_authoring_integration.py`
- DEPENDENCIES:
  - current `nexus` test-driving lane
  - deleted-owned-fields cleanup contract for conduit teardown
- EXIT_GATE:
  - the targeted cleanup integration test is green
  - the test no longer reads deleted conduit-owned fields after cleanup
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if runtime evidence shows
  `_aetheric_frame` should remain available after cleanup

## Scope Boundaries
- In scope:
  - cleanup-test normalization in the Nexus frame authoring integration file
- Out of scope:
  - runtime cleanup behavior
  - unrelated Nexus failures after this one

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the first live `nexus` failure is a bounded integration
  test assumption drift against the current cleanup contract

## Steps / Checklist
- [ ] confirm the stale post-cleanup field access pattern
- [ ] patch the test to capture stable frame identity before cleanup
- [ ] rerun the targeted integration test
- [ ] continue to the next `nexus` blocker only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- a narrow Nexus cleanup integration test fix aligned to deleted-field cleanup

## Files / Paths Impacted
- `tests/integration/melder/aether/test_nexus_frame_authoring_integration.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\integration\melder\aether\test_nexus_frame_authoring_integration.py::test_integration_nexus_frame_cleanup_matrix[external-single]`

## Risks / Rollback Notes
- Low risk. This lane should remain test-only unless source evidence contradicts
  the deleted-field cleanup contract.

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
- DATETIME: 2026-05-18T14:35:07Z
  TYPE: FACT
  CLAIM: The first `nexus`-lane failure is test drift against the cleanup contract.
    The integration test asks `nexus.frame_manager.exists(conduit._aetheric_frame)`
    after `conduit.cleanup()`, but `_aetheric_frame` is an owned conduit field and
    cleanup now deletes owned fields instead of leaving `None` tombstones.
  EVIDENCE:
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py:307-332
  IMPACT: The `nexus` lane stops on stale post-cleanup field access before reaching
    the next real Nexus runtime issue.
  NEXT: patch the test to keep the frame identifier before cleanup and assert
    manager state from that stable value.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:35:07Z
  TYPE: PLAN
  CLAIM: `NexusFrameManager.exists(...)` takes a frame-name string, and the
    integration test can preserve that contract by snapshotting
    `managed_frame_name = conduit._aetheric_frame` before cleanup and reusing
    that stable value for all post-cleanup assertions.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:145-145
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py:321-332
  IMPACT: The fix stays test-only and aligns the assertion to the deleted-field
    cleanup contract without changing runtime behavior.
  NEXT: patch the integration test to use `managed_frame_name` for the cleanup
    assertions, then rerun the targeted Nexus case.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-18T14:35:07Z
  TYPE: FACT
  CLAIM: The integration file is also stale on the ownership policy itself.
    The component cleanup matrix already expects `conduit.cleanup()` to leave the
    Nexus frame-manager entry alive and only clear it after explicit frame cleanup
    through the owner path, but the integration matrix still expects implicit frame
    removal from conduit cleanup.
  EVIDENCE:
  - tests/component/melder/aether/test_nexus_frame_authoring_component.py:276-303
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py:321-333
  IMPACT: The integration assertion is contradicting the current owner-driven
    cleanup contract that the component lane already codified.
  NEXT: align the integration matrix to the component contract, then rerun the
    full cleanup matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:35:07Z
  TYPE: MEASURE
  CLAIM: The Nexus cleanup integration matrix is green after aligning it to the
    deleted-field and owner-driven frame-cleanup contracts.
  EVIDENCE:
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py:307-335
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\integration\melder\aether\test_nexus_frame_authoring_integration.py::test_integration_nexus_frame_cleanup_matrix` -> `6 passed`
  IMPACT: The first `nexus` blocker is cleared, so the next useful move is to
    resume the broader `-k nexus` stop-on-first slice.
  NEXT: rerun `pytest -vv -x --tb=long -k nexus` and route the next failure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active `nexus` lane for the first cleanup-assumption drift. Current evidence
points to a narrow integration-test fix, not a runtime cleanup regression.
