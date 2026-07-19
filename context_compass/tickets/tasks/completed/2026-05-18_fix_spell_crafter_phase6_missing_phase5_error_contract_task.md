# Task: fix spell crafter phase6 missing phase5 error contract

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-spell-crafter-phase6-missing-phase5-error-contract
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T14:14:28Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the next non-Nexus integration blocker where `Spell.run_phase_system_validation(...)`
raises the wrong Phase 5 precondition error before any Phase 5 artifacts exist.

## Ticket Contract
- ENTRY_GATE: the next stop-on-first non-Nexus suite failure is
  `test_spell_crafter_phase6_requires_phase5`
  expecting `Phase 5 root blueprint map is required` while runtime currently raises
  `SpellCrafter Phase 5 system index is required.`
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spell_crafter/spell_crafter.py`
  - `tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py`
- DEPENDENCIES:
  - current non-Nexus suite-driving lane
  - existing SpellCrafter integration coverage
- EXIT_GATE:
  - the targeted integration test is green
  - the runtime now raises the expected Phase 5 precondition error first
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if code evidence shows the test is stale
  and the system-index error is the intended canonical contract

## Scope Boundaries
- In scope:
  - Phase 6 precondition ordering/error contract for missing Phase 5 artifacts
  - the directly affected integration expectation only if runtime evidence proves drift
- Out of scope:
  - broader SpellCrafter phase redesign
  - unrelated SpellCrafter failures after this contract is corrected

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the next live non-Nexus failure is a bounded Phase 6
  precondition contract mismatch with direct source and test evidence

## Steps / Checklist
- [ ] confirm the live failure and exact precondition order in `SpellCrafter`
- [ ] patch the smallest truthful Phase 6 contract fix
- [ ] rerun the targeted integration test
- [ ] continue to the next non-Nexus blocker only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- a bounded `SpellCrafter` Phase 6 precondition contract fix

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\integration\melder\spellbook\test_spellbook_integration_spell_crafter.py::test_spell_crafter_phase6_requires_phase5`

## Risks / Rollback Notes
- Low risk if the issue is only precondition ordering.
- Medium risk if the broader Phase 5 missing-artifact contract is inconsistent across
  local and frame-wide Phase 6 entrypoints.

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
- DATETIME: 2026-05-18T14:14:28Z
  TYPE: FACT
  CLAIM: The next live non-Nexus blocker is a narrow Phase 6 precondition mismatch.
    `run_phase_system_validation(...)` currently evaluates the Phase 5 system-index
    requirement before the Phase 5 root-blueprint requirement, but the integration
    contract expects the root-blueprint error to surface first when Phase 5 has not run.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py:539-578
  - src/melder/spellbook/spell_crafter/spell_crafter.py:457-482
  - src/melder/spellbook/spell_crafter/spell_crafter.py:5267-5311
  IMPACT: The suite stops on an error-message contract mismatch before reaching the next
    substantive non-Nexus runtime issue.
  NEXT: patch the Phase 6 precondition order in `SpellCrafter`, then rerun the targeted
    integration test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:14:28Z
  TYPE: PLAN
  CLAIM: The smallest truthful fix is to make frame-wide Phase 6 retrieve the
    required root-blueprint map before it retrieves the required system index, so the
    public error contract stays aligned with the existing integration expectation when
    Phase 5 has not run.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:457-482
  - src/melder/spellbook/spell_crafter/spell_crafter.py:5267-5311
  - tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py:539-578
  IMPACT: This keeps the fix source-local, preserves both existing helper methods, and
    avoids widening the lane into broader Phase 5 contract redesign.
  NEXT: patch `run_phase_system_validation(...)` to fetch the root-blueprint map first,
    then rerun the exact failing integration test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:14:28Z
  TYPE: FACT
  CLAIM: Frame-wide Phase 6 now resolves the required root-blueprint map before the
    required system index, and `validator.validate(...)` consumes those locals instead
    of triggering the old left-to-right helper order inline.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:5324-5333
  IMPACT: The missing-Phase-5 contract should now surface the root-blueprint error
    first without changing any broader Phase 6 behavior.
  NEXT: rerun the targeted integration test for `test_spell_crafter_phase6_requires_phase5`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-18T14:14:28Z
  TYPE: MEASURE
  CLAIM: The targeted Phase 6 integration contract is now green.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:5324-5333
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\integration\melder\spellbook\test_spellbook_integration_spell_crafter.py::test_spell_crafter_phase6_requires_phase5` -> `1 passed`
  IMPACT: This bounded non-Nexus blocker is cleared, so the useful next move is to
    resume the broader stop-on-first non-Nexus suite run and capture the next failure.
  NEXT: rerun the non-Nexus suite filter and route the next blocker into its own task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active lane for the next non-Nexus suite blocker. The current hypothesis is
that Phase 6 only needs a bounded precondition-order fix so the missing
root-blueprint error remains the first contract surfaced when Phase 5 has not run.
