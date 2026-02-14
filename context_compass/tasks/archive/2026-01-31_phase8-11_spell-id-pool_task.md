# Task: Use spell_id_pool for Phase 8/11 spell lookup

## Metadata
- Task ID: TASK-2026-01-31-phase8-11-spell-id-pool
- Story: N/A
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Remove redundant spell lookup construction in Phase 8/11 by reusing the
Spellbook-maintained spell_id_pool map (spell_id -> ISpell) instead of
iterating via SpellbookScanner each time.

## Scope Boundaries
- In scope:
  - Use Spellbook._spell_id_pool for spell_lookup in Phase 8 and Phase 11.
  - Update docstrings to document the new lookup source and contract.
- Out of scope:
  - Public API changes or new public accessors on Spellbook.
  - Changes to SpellbookScanner behavior outside Phase 8/11.
  - Behavioral changes to occurrence or execution planning.

## Steps / Checklist
- [x] Replace Phase 8 spell_lookup construction with Spellbook._spell_id_pool.
- [x] Replace Phase 11 spell_lookup construction with Spellbook._spell_id_pool.
- [x] Update docstrings for the modified methods.
- [ ] Document validation status.

## Deliverables
- Updated Phase 8/11 spell lookup source.
- Docstrings aligned with the new lookup contract.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/spellbook/spell_crafter`

## Risks / Rollback Notes
- Risk: Using the live spell_id_pool map could expose concurrent mutation
  hazards if the map is modified during phase execution.
- Mitigation: Phase execution is already serialized per Spellbook; this change
  keeps semantics identical and avoids copying to reduce overhead.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Updated Phase 8/11 to use Spellbook._spell_id_pool directly for spell lookup
and documented the contract in method docstrings. Validation not run.
