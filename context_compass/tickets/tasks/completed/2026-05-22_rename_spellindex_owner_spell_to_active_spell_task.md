# Task: Rename SpellIndex owner spell field to active spell

## Metadata
- Task ID: TASK-2026-05-22-rename-spellindex-owner-spell-to-active-spell
- Story: STORY-2026-05-22-define-spellindex-transfer-and-registration-semantics
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-22T13:01:36Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Rename the misleading `SpellIndex._owner_spell` field to `_active_spell` and
update the narrow runtime/test surfaces that reference it.

## Ticket Contract
- ENTRY_GATE: the investigation task already established that the field is a
  narrow active-spell convenience cache, not a broad ownership truth surface.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/bind/spell_index.py`
  - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
  - directly implicated tests and narrow component stubs that reference the field
- DEPENDENCIES:
  - `tickets/tasks/2026-05-22_investigate_spellindex_transfer_semantic_drift_task.md`
- EXIT_GATE: source and focused tests use `_active_spell` consistently and no
  `_owner_spell` references remain in active code/tests for this slice.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the rename exposes a
  wider semantic mismatch that cannot stay a narrow field-level cleanup.

## Scope Boundaries
- In scope:
  - runtime field rename
  - local docstring/error-string cleanup
  - focused test updates
- Out of scope:
  - removing the field entirely
  - multi-spell-per-index mechanics
  - broader ownership semantic rewrites

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the runtime rename and the focused test ring are complete,
  so this narrow field-level cleanup is ready for review.

## Steps / Checklist
- [x] Rename `_owner_spell` to `_active_spell` in `SpellIndex`.
- [x] Update narrow transfer-of-ownership references.
- [x] Update directly implicated tests and stubs.
- [x] Run the focused pytest ring for the touched seams.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- renamed runtime field and matching focused tests

## Files / Paths Impacted
- `src/melder/aether/spellbook/bind/spell_index.py`
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
- `tests/unit/melder/spellbook/bind/test_spell_index.py`
- `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py`
- `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py`
- `tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py`
- `tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py`
- `tests/component/melder/spellbook/test_spellbook_component_spellbook.py`
- `tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py`

## Validation
- `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\bind\test_spell_index.py tests\unit\melder\aether\conduit\conduit_ward\transfer\test_transfer_of_ownership.py tests\unit\melder\aether\conduit\conduit_ward\transfer\test_transfer_of_ownership_contracts.py tests\unit\melder\aether\conduit\conduit_ward\test_conduit_ward.py tests\unit\melder\aether\dev_ops\spell_system_states\test_spell_system_states.py tests\component\melder\spellbook\test_spellbook_component_spellbook.py tests\component\melder\spellbook\test_spellbook_component_spell_crafter.py`
- Result: `377 passed, 1 xfailed, 1 warning`

## Risks / Rollback Notes
- Risk: some tests may be asserting broader semantic meaning on the field than
  the runtime actually uses.
- Rollback: keep the rename narrow and update only the touched field language,
  not the larger mechanics.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into field removal or broader semantic cleanup in this task.
- [ ] No silent runtime rename without matching tests.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-22T13:01:36Z
  TYPE: PLAN
  CLAIM: The narrow cleanup slice is a field rename only. Current investigation
    shows the field is just the active spell convenience cache used by
    `SpellIndex.update(...)`, transfer assertions, and direct test fixtures.
    Renaming it to `_active_spell` fixes the misleading ownership wording
    without widening into field removal or membership mechanics yet.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:152-168
  - src/melder/aether/spellbook/bind/spell_index.py:194-200
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:797-799
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1332-1340
  - source_scan: `rg -n "_owner_spell\\b" src tests`
  IMPACT: This gives the runtime a more truthful local name before the broader
    semantics work continues.
  NEXT: patch the runtime field name and the focused tests, then run the
    targeted pytest ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T13:01:36Z
  TYPE: MEASURE
  CLAIM: The narrow rename slice is landed and green. `SpellIndex._owner_spell`
    is now `SpellIndex._active_spell` in runtime code, the transfer paths now
    use the new name and error wording, the directly implicated unit/component
    tests and stubs were updated to the same contract, and the focused pytest
    ring passed.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:32-41
  - src/melder/aether/spellbook/bind/spell_index.py:72-77
  - src/melder/aether/spellbook/bind/spell_index.py:152-168
  - src/melder/aether/spellbook/bind/spell_index.py:194-200
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:797-799
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1332-1340
  - tests/unit/melder/spellbook/bind/test_spell_index.py:300-380
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1210-1260
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:3438-3710
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py:1150-1200
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py:2384-2505
  - tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py:58-66
  - tests/component/melder/spellbook/test_spellbook_component_spellbook.py:101-114
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:556-564
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\bind\test_spell_index.py tests\unit\melder\aether\conduit\conduit_ward\transfer\test_transfer_of_ownership.py tests\unit\melder\aether\conduit\conduit_ward\transfer\test_transfer_of_ownership_contracts.py tests\unit\melder\aether\conduit\conduit_ward\test_conduit_ward.py tests\unit\melder\aether\dev_ops\spell_system_states\test_spell_system_states.py tests\component\melder\spellbook\test_spellbook_component_spellbook.py tests\component\melder\spellbook\test_spellbook_component_spell_crafter.py` -> `377 passed, 1 xfailed, 1 warning`
  IMPACT: The misleading ownership wording is out of the active runtime field,
    and the next mechanics discussion can talk about active spell semantics
    without that naming drift.
  NEXT: decide whether the next narrow cleanup is `_owner_spellbook` semantics
    or a larger index-membership mechanic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the narrow `_owner_spell` -> `_active_spell` rename and the
focused test updates required to keep that field-level cleanup honest.

