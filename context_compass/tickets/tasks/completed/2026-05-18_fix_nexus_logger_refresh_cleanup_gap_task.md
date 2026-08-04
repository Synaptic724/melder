# Task: fix nexus logger refresh cleanup gap

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-nexus-logger-refresh-cleanup-gap
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T14:50:22Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the next `nexus`-lane blocker by making repeated `Nexus(...)` logger refresh
tear down the prior `SafeLogger` instead of silently replacing it.

## Ticket Contract
- ENTRY_GATE: the next stop-on-first `-k nexus` failure is
  `test_nexus_repeated_init_with_logger_override_reuses_singleton_and_replaces_logger`
  expecting the old logger to be cleaned when repeated singleton init refreshes
  the logger override.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/nexus.py`
  - directly implicated unit test in
    `tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py`
- DEPENDENCIES:
  - current `nexus` test-driving lane
  - `SafeLogger.cleanup()` lifecycle contract
- EXIT_GATE:
  - the targeted repeated-init logger unit is green
  - logger refresh explicitly cleans the prior `SafeLogger`
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if source evidence shows logger
  refresh should intentionally leak/abandon the old `SafeLogger`

## Scope Boundaries
- In scope:
  - `Nexus._initialize_logging(...)` logger replacement lifecycle
- Out of scope:
  - broader cross-class logger refresh policy
  - unrelated Nexus failures after this one

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the next live `nexus` blocker is a bounded logger-lifecycle
  gap in repeated singleton initialization

## Steps / Checklist
- [ ] confirm the repeated-init logger-refresh contract and current overwrite path
- [ ] patch `_initialize_logging(...)` to cleanup the replaced logger safely
- [ ] rerun the targeted unit test
- [ ] continue to the next `nexus` blocker only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- a narrow Nexus logger-refresh lifecycle fix

## Files / Paths Impacted
- `src/melder/aether/nexus/nexus.py`
- `tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\aether\test_nexus_orchestration_and_lifecycle.py::test_nexus_repeated_init_with_logger_override_reuses_singleton_and_replaces_logger`

## Risks / Rollback Notes
- Low to medium risk. The change is small, but it touches logger lifecycle and
  must not break initial boot or fallback error logging.

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
- DATETIME: 2026-05-18T14:50:22Z
  TYPE: FACT
  CLAIM: The next `nexus` blocker is a real logger-lifecycle gap. Repeated
    singleton init with `logger=...` enters the “refresh the logger override”
    path, but `_initialize_logging(...)` simply assigns a new `SafeLogger`
    without cleaning the old one first.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:129-160
  - src/melder/aether/nexus/nexus.py:284-316
  - src/melder/utilities/logger/safe_logger.py:61-75
  - tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py:691-702
  IMPACT: The `nexus` lane has now reached a small runtime lifecycle bug rather
    than another stale test.
  NEXT: patch `Nexus._initialize_logging(...)` to cleanup the previous
    `SafeLogger` during logger refresh, then rerun the targeted unit test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active `nexus` lane for a narrow runtime logger-refresh cleanup gap. Current
evidence points to a source fix in `Nexus`, not a test-only adjustment.
