# Task: Test Aether Rift System Facade

## Metadata
- Task ID: TASK-2026-03-16-test-aether-rift-system-facade
- Story: STORY-2026-03-16-aethericrift-system-bootstrap
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-03-16T00:31:16Z
- Updated: 2026-03-16T00:31:16Z

## Objective
Add focused unit tests proving that `Aether` only facades Rift-system access
and that the registry/state dictionaries remain owned by `AethericRiftSystem`.

## Ticket Contract
- ENTRY_GATE: the system registry and Aether facade tasks are complete enough to
  exercise the delegation path.
- EXECUTION_BOUNDARY: focused tests only for facade access, registry ownership,
  and basic lookup behavior.
- DEPENDENCIES:
  - TASK-2026-03-16-implement-aethericrift-system-registry
  - TASK-2026-03-16-facade-aether-rift-system-access
  - tests/unit/melder/aether/test_aether.py
- EXIT_GATE: unit tests exist for add/remove/list/get-style facade access and
  verify the dict ownership boundary explicitly.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if testing the facade requires
  broader runtime behavior than the bootstrap should expose.

## Scope Boundaries
- In scope:
  - `tests/unit/melder/aether/test_aether.py`
  - new focused test modules under `tests/unit/melder/aether/`
  - façade/registry assertions
- Out of scope:
  - integration tests
  - dynamic room behavior
  - validation/profile logic

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: existing `Aether` tests already provide a clear local
  pattern for this delegation-style test slice.

## Steps / Checklist
- [ ] Add tests for hosted system initialization/access.
- [ ] Add tests for add/remove/list/get facade delegation.
- [ ] Assert the registry dictionaries remain inside `AethericRiftSystem`.
- [ ] Add tests for ULID/name lookup seams only if those APIs exist by then.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Focused Aether facade/unit tests for the hosted Rift system

## Files / Paths Impacted
- tests/unit/melder/aether/test_aether.py
- tests/unit/melder/aether/test_aetheric_rift_system.py

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/aether/test_aether.py -k rift -v`
  - `pytest tests/unit/melder/aether -k rift_system -v`

## Risks / Rollback Notes
- Risk: tests accidentally assert internal implementation details outside the
  documented facade/ownership boundary.
  Rollback: keep tests on observable facade outcomes and documented registry
  ownership rules only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-03-16T00:31:16Z
  TYPE: PLAN
  CLAIM: The existing Aether tests already prove singleton/lifecycle behavior
    and direct delegation into subordinate dictionaries, so the Rift-system
    facade tests should extend the same style rather than introducing a new
    test harness.
  EVIDENCE:
  - tests/unit/melder/aether/test_aether.py:69-91
  - tests/unit/melder/aether/test_aether.py:248-280
  IMPACT: The test slice can stay small and high-signal once the facade methods
    exist.
  NEXT: add the focused Rift-system facade tests after the implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task keeps the first test slice narrow and aligned to current Aether test
patterns: singleton host, facade delegation, and system-owned dictionaries.
