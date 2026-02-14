# Task: Phase 4 shared views + Phase 6 spell lookup reuse

## Metadata
- Task ID: TASK-2026-01-31-conjure-phase5-validation-microwins
- Story:
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Reduce conjure overhead by sharing Phase 4 global views across validation
strategies within a single validation run and reusing the spellbook-owned
spell lookup in Phase 6 without rebuilding it.

## Scope Boundaries
- In scope:
  - Phase 4: compute shared global views once per validation run and pass
    them through the validation context for strategies to reuse.
  - Phase 6 system validation uses `spellbook._spell_id_pool` directly
    (no dict copy).
- Out of scope:
  - Public API changes.
  - Module-level caches or persistent shared state across runs.
  - Phase 5 lazy blueprinting (explicitly deferred; keep eager).
  - Phase 11 plan variant changes (tracked separately).

## Steps / Checklist
- [ ] Define the shared Phase 4 view object (ephemeral, per-validation run).
- [ ] Update Phase 4 strategies to use shared views when present.
- [ ] Implement Phase 6 spell_lookup reuse (use spellbook-owned mapping).
- [ ] Update docstrings/comments to match new behavior.
- [ ] Add/update tests to cover shared view usage and Phase 6 lookup reuse.

## Deliverables
- Phase 4 shared view object + strategy reuse.
- Phase 6 spell_lookup reuse (no per-phase dict rebuild).
- Tests for the new behaviors.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/spellbook/spell_crafter/validation/validation_system.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/` (multiple)
- `tests/unit/melder/spellbook/spell_crafter/` (new or updated tests)

## Validation
- Not run.
- Recommended commands:
  - `pytest -q tests/unit/melder/spellbook/spell_crafter`

## Risks / Rollback Notes
- Risk: shared views introduce stale data if not per-run.
  Mitigation: build once per validation run only; never store on Spellbook.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Ticket created to implement shared Phase 4 validation views (ephemeral per run)
and Phase 6 spell lookup reuse without rebuilding spell maps.
