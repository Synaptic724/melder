# Task: Remove Spell owned_spell flag

## Metadata
- Task ID: TASK-2026-05-22-remove-spell-owned-spell-flag
- Story: STORY-2026-05-22-define-spellindex-transfer-and-registration-semantics
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-22T14:00:54Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Remove the write-only `Spell.owned_spell` flag from runtime code and update the
directly implicated tests to assert the concrete ownership signals instead.

## Ticket Contract
- ENTRY_GATE: the investigation task already established that `owned_spell` is
  write-only in `src` and only read by tests and test stubs.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell.py`
  - directly implicated tests and test stubs that read or write `.owned_spell`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-22_investigate_spellindex_transfer_semantic_drift_task.md`
- EXIT_GATE: runtime no longer carries `owned_spell`, directly implicated tests
  use concrete ownership signals instead, and the focused ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if a real runtime read of
  `owned_spell` is discovered during the removal pass.

## Scope Boundaries
- In scope:
  - remove runtime field and writes
  - replace direct test assertions and stubs
  - focused validation
- Out of scope:
  - broader ownership semantic changes
  - spell index mechanics
  - transfer semantics redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the runtime field is removed, the focused tests are
  updated, and the narrow validation ring is green.

## Steps / Checklist
- [x] Remove `owned_spell` from `Spell`.
- [x] Remove direct test-stub writes where they are only mirroring runtime.
- [x] Replace assertions with concrete ownership checks already present on the
      spell.
- [x] Run the focused pytest ring.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- runtime no longer carries `owned_spell`
- focused tests assert concrete ownership state instead

## Files / Paths Impacted
- `src/melder/aether/spellbook/spell.py`
- `tests/unit/melder/spellbook/test_spell.py`
- `tests/component/melder/spellbook/test_spellbook_component_conduit_definition.py`
- `tests/component/melder/spellbook/test_spellbook_component_spellbook.py`
- directly implicated test stubs under conduit_ward transfer/contracts

## Validation
- `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\test_spell.py tests\component\melder\spellbook\test_spellbook_component_conduit_definition.py tests\component\melder\spellbook\test_spellbook_component_spellbook.py tests\unit\melder\aether\conduit\conduit_ward\transfer\test_transfer_of_ownership.py tests\unit\melder\aether\conduit\conduit_ward\transfer\test_transfer_of_ownership_contracts.py tests\unit\melder\aether\conduit\conduit_ward\test_conduit_ward_contracts.py`
- Result: `366 passed, 1 warning`

## Risks / Rollback Notes
- Risk: a hidden runtime consumer still relies on the flag.
- Rollback: keep the removal narrow and restore only if an actual runtime read
  is found.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into larger ownership cleanup in this task.
- [ ] No silent removal without concrete replacement assertions in tests.

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
- DATETIME: 2026-05-22T14:00:54Z
  TYPE: PLAN
  CLAIM: The field removal is now bounded enough to execute. In live `src`,
    `Spell.owned_spell` is initialized, set to `True` in `_add_owned_conduit`,
    and deleted during cleanup, but not read by runtime behavior. The cleanup
    therefore needs to remove the field and update the directly implicated
    tests to use `_owner_conduit_id`, `_owner_conduit_name`, and
    `_owner_creations` instead.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:389-389
  - src/melder/aether/spellbook/spell.py:520-522
  - src/melder/aether/spellbook/spell.py:1049-1052
  - source_scan: `rg -n "\\bowned_spell\\b|\\.owned_spell\\b" src/melder -g "*.py"`
  - source_scan: `rg -n "\\bowned_spell\\b|\\.owned_spell\\b" tests -g "*.py"`
  IMPACT: The next step can stay narrow and remove misleading state without
    touching broader ownership semantics.
  NEXT: patch runtime and focused tests, then run the narrow pytest ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T14:00:54Z
  TYPE: MEASURE
  CLAIM: The `owned_spell` field is gone from runtime and the focused ring is
    green. `Spell` no longer initializes, sets, or deletes `owned_spell`;
    directly implicated tests and stubs now assert or carry the concrete
    ownership signals that actually matter (`_owner_conduit_id`,
    `_owner_conduit_name`, `_owner_creations`) instead of the removed boolean.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:383-391
  - src/melder/aether/spellbook/spell.py:516-523
  - src/melder/aether/spellbook/spell.py:1046-1052
  - tests/unit/melder/spellbook/test_spell.py:760-780
  - tests/unit/melder/spellbook/test_spell.py:1221-1232
  - tests/component/melder/spellbook/test_spellbook_component_conduit_definition.py:136-141
  - tests/component/melder/spellbook/test_spellbook_component_spellbook.py:286-296
  - tests/component/melder/spellbook/test_spellbook_component_spellbook.py:870-876
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1078-1117
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py:1021-1060
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_contracts.py:100-105
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\test_spell.py tests\component\melder\spellbook\test_spellbook_component_conduit_definition.py tests\component\melder\spellbook\test_spellbook_component_spellbook.py tests\unit\melder\aether\conduit\conduit_ward\transfer\test_transfer_of_ownership.py tests\unit\melder\aether\conduit\conduit_ward\transfer\test_transfer_of_ownership_contracts.py tests\unit\melder\aether\conduit\conduit_ward\test_conduit_ward_contracts.py` -> `366 passed, 1 warning`
  IMPACT: The runtime no longer carries a redundant boolean for conduit
    ownership, and the next ownership/index cleanup can reason directly from
    the real ownership fields.
  NEXT: return to the SpellIndex and transfer mechanics lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the narrow removal of the write-only `Spell.owned_spell` field
and the directly implicated test updates.

