# Task: Audit contract and link flows for id map updates

- Completed: 2026-01-25
- Summary: Contract/link flows already update contracted spell_id maps via
  SpellIndex attachments and Spellbook contract helpers.

## Metadata
- Task ID: TASK-2026-01-25-contract-link-audit
- Story: STORY-2026-01-25-contract-link-ownership-impacts
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Audit contract and link flows to identify where spell_id maps must be updated.

## Scope Boundaries
- In scope:
  - Review Spellbook contract methods and link setup/teardown.
  - Review Conduit and ConduitWard contract flows for registry updates.
  - Capture required update points and risks.
- Out of scope:
  - Implementing fixes (separate task).

## Steps / Checklist
- [x] Review Spellbook contract methods for map update needs.
- [x] Review Conduit contract APIs for registry interactions.
- [x] Review ConduitWard contract paths for map updates.
- [x] Record findings and required follow-ups in this ticket.

## Deliverables
- Audit findings with explicit update points and file references.

## Files / Paths Impacted
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/conduit_ward/`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/aether/conduit -q`

## Risks / Rollback Notes
- Risk: audit misses an indirect registry update path.
  Rollback: expand audit to adjacent contract helpers.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Findings:
  - `Spellbook._add_contracted_spell` attaches SpellIndex via
    `_attach_contracted`, which registers contracted spell_id entries.
  - `Spellbook._remove_contracted_spell` and `_clear_contracted_spells_for_conduit`
    detach SpellIndex and clear `_contracted_spells_by_id`.
  - `ConduitWard._add_spell_to_contract` and `_remove_spell_from_contract` drive
    the Spellbook contract helpers that update the id maps.
- Acceptance confirmed by user.
