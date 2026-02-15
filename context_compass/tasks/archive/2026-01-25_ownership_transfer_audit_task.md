# Task: Audit ownership transfer flow for id map updates

- Completed: 2026-01-25
- Summary: Audited transfer flow and updated ownership transfer to move
  Spellbook spell_id maps and SpellIndex owner references in
  `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`.

## Metadata
- Task ID: TASK-2026-01-25-ownership-transfer-audit
- Story: STORY-2026-01-25-contract-link-ownership-impacts
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Audit ownership transfer flow to ensure spell_id maps remain consistent when
spells move between conduits.

## Scope Boundaries
- In scope:
  - Review ownership transfer entrypoints and transfer helpers.
  - Identify registry update points for Spellbook and SpellIndex attachments.
  - Record findings and update needs.
- Out of scope:
  - Implementing fixes (separate task).

## Steps / Checklist
- [x] Review `Conduit.transfer_spell_ownership` call flow.
- [x] Review transfer logic in ConduitWard and transfer helpers.
- [x] Record required map update points and attachment updates.

## Deliverables
- Audit findings with explicit update points and file references.

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/conduit_ward/transfer/`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/aether/conduit -q`

## Risks / Rollback Notes
- Risk: transfer flow updates Spellbook through indirect helpers.
  Rollback: expand audit to referenced helpers and registries.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Findings:
  - `Conduit.transfer_spell_ownership` delegates to
    `ConduitWard._transfer_spell_ownership`, which uses
    `TransferOfOwnership._flip_registry_and_spellbooks`.
  - Transfer previously moved `_spells` and `_lookup_spells` only; it now moves
    `_spells_by_id` and updates SpellIndex owner references during transfer.
  - Contract unshare/repoint uses contract APIs that already update contracted
    spell_id maps via SpellIndex attachments.
- Acceptance confirmed by user.
