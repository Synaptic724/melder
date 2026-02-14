# Task: Lock SpellSystemState Reads in Meld Front Door

## Metadata
- Task ID: TASK-2026-01-30-spell-system-state-locked-reads
- Story: 
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Ensure SpellSystemState state/validity reads are synchronized via the state lock and that Meld front-door paths use those locked reads, without introducing snapshots or copies.

## Scope Boundaries
- In scope:
  - Add state-lock protection to SpellSystemState getters for validity/state data.
  - Use locked access in Meld front-door and other owned call sites that read state/validity.
  - Guard direct SpellSystemAdjacencyBuilder reads with the state lock (no copies).
- Out of scope:
  - Changing dependency/topology snapshot semantics or returning copies in hot paths.
  - Refactoring ConduitResolutionState or unrelated validation behavior.

## Steps / Checklist
- [x] Identify all SpellSystemState state/validity reads in owned code and list them.
- [x] Add lock-protected getters for validity/state fields (no copy).
- [x] Update meld front door and other owned call sites to use locked getters.
- [x] Guard adjacency builder raw field reads with state._lock (no copy).
- [x] Verify docstrings for touched methods reflect locking semantics.

## Deliverables
- Updated SpellSystemState getter locking.
- Updated Meld front door state reads.
- Updated adjacency builder state reads.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/spell_system_states/spell_system_state.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/spellbook/spell_crafter/system/spell_system_adjacency_builder.py`
- Additional call sites if discovered during audit (to be listed before edit).

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/integration/melder/conduit/test_conduit_integration_lifecycle.py::test_conduit_transfer_spell_ownership_moves_registry_and_meld`

## Risks / Rollback Notes
- Locking read paths could add minor overhead; avoid copies to keep hot paths fast.
- Rollback: revert getter locking changes and call-site updates.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Audit: direct private reads of SpellSystemState state/validity fields outside the class were not found; Meld uses `state.validity` already. The only private-field consumer found was `SpellSystemAdjacencyBuilder` (reads `_current_spell_id` and `_direct_dependencies`), now guarded by `state._lock` with no copies. SpellSystemState getters for state/validity fields now lock on read. RiskManager now updates the Spellbook validation flag under SafeGuard using the RiskManager lock + Spellbook validation lock, with no try/except and no snapshots. Meld runtime now reads the flag via `check_spellbook_validation_required()`.
