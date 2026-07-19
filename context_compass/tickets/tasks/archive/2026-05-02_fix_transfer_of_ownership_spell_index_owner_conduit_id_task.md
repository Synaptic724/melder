# Task: Fix Transfer Ownership SpellIndex Owner Conduit Id

## Metadata
- Task ID: TASK-2026-05-02-fix-transfer-ownership-spell-index-owner-conduit-id
- Story:
- Epic:
- Status: review
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-05-02T23:10:56Z
- Updated: 2026-05-02T23:16:13Z

## Objective
Fix the ownership-transfer path so `SpellIndex._owner_conduit_id` is updated at
the same time as the new owner spellbook and owner spell, then add regression
tests so transfer cannot leave the lineage-side conduit owner stale.

## Ticket Contract
- ENTRY_GATE: the exact stale-owner seam was already identified in the
  ownership-transfer path and the user explicitly requested the code fix plus
  regression coverage.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
  - focused transfer/spell-index tests under `tests/`
  - this task ticket
  - `attention_board.md`
- DEPENDENCIES:
  - `src/melder/spellbook/bind/spell_index.py`
  - `src/melder/spellbook/spell.py`
  - existing transfer-of-ownership tests
- EXIT_GATE: the transfer path updates all three lineage-owner fields
  consistently and a focused test ring proves the fix.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the focused tests show a
  broader ownership-transfer inconsistency than the bounded conduit-id fix.

## Scope Boundaries
- In scope:
  - fix the stale `SpellIndex._owner_conduit_id` update
  - add/update focused regression tests
  - record validation
- Out of scope:
  - broader transfer-of-ownership redesign
  - unrelated mutation or crystallizer changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved the bounded owner-conduit-id
  fix and asked for regression coverage.

## Steps / Checklist
- [ ] Inspect the relevant transfer and test files.
- [ ] Patch the ownership-flip block to keep `SpellIndex._owner_conduit_id` in sync.
- [ ] Add focused regression coverage.
- [ ] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- transfer-of-ownership fix for lineage-side conduit owner state
- focused regression test coverage
- focused validation result

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-02_fix_transfer_of_ownership_spell_index_owner_conduit_id_task.md
- codex/context_compass/attention_board.md
- src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py
- tests/

## Validation
- Executed:
  - `python -m pytest -q tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py tests/unit/melder/spellbook/bind/test_spell_index.py`
- Result:
  - `146 passed, 1 xfailed`

## Risks / Rollback Notes
- Risk: the stale field is only one visible symptom of a larger transfer owner-state mismatch.
  Rollback: keep the fix narrow first and let focused tests tell us whether the seam is wider.

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
- DATETIME: 2026-05-02T23:10:56Z
  TYPE: FACT
  CLAIM: The ownership-transfer path updates `SpellIndex._owner_spellbook` and
    `SpellIndex._owner_spell`, then stamps spell-side conduit ownership, but it
    never updates `SpellIndex._owner_conduit_id`. The normal bind/conjure path
    does update that field through `SpellIndex._set_owner_conduit_id(...)`, so
    transfer currently leaves the lineage-side conduit owner stale.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:772-812
  - src/melder/spellbook/spell.py:1241-1280
  - src/melder/spellbook/spellbook.py:2754-2767
  - src/melder/spellbook/spellbook_creation_system.py:494-506
  IMPACT: The right bounded fix is to update the lineage-side conduit owner in
    the same ownership-flip block and then lock that behavior down with tests.
  NEXT: inspect the focused tests around transfer/spell-index ownership and patch the code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T23:10:56Z
  TYPE: FACT
  CLAIM: The bounded fix is now in place. `TransferOfOwnership` updates
    `SpellIndex._owner_conduit_id` in the same forward owner-flip block that
    already sets the new owner spellbook and owner spell, and the rollback
    mirror now restores that field back to the source conduit id. The existing
    transfer tests were extended to assert the lineage-side conduit owner both
    after execute and after rollback.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1142-1154
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:854-862
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1034-1044
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1064-1071
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1554-1563
  IMPACT: Validation can now focus on whether the existing transfer ring agrees
    that lineage-side and spell-side conduit ownership stay synchronized.
  NEXT: run the focused transfer/spell-index pytest ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T23:16:13Z
  TYPE: MEASURE
  CLAIM: The focused transfer/spell-index regression ring is green after the
    owner-conduit-id fix. The transfer path now keeps `SpellIndex` lineage-side
    owner spellbook, owner spell, and owner conduit id synchronized in both the
    forward flip and rollback path without breaking the existing transfer or
    spell-index expectations.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1142-1154
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:854-862
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1034-1044
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1064-1071
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1554-1563
  - validation_result: `python -m pytest -q tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py tests/unit/melder/spellbook/bind/test_spell_index.py` -> `146 passed, 1 xfailed`
  IMPACT: The immediate stale-owner bug is fixed and regression coverage now
    locks the lineage-side conduit owner into the same transfer boundary as the
    owner spellbook/spell fields.
  NEXT: return the bounded fix for review and let the user decide whether any
    broader transfer ownership audit is still needed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded fix for stale `SpellIndex._owner_conduit_id` during
ownership transfer.
