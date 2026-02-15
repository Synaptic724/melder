Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Task: Unregister SpellSystemStates lineages during Spellbook cleanup

## Metadata
- Task ID: TASK-2026-02-07-spellbook-cleanup-unregister-states
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Ensure Spellbook cleanup unregisters its local spell lineages from
SpellSystemStates so cleaned spells are removed from system-state tracking.

## Scope Boundaries
- In scope:
- Unregister local spell lineages during Spellbook cleanup.
- Add/extend test stubs to include unregister_lineage where required.
- Add a component test verifying SpellSystemStates removal on cleanup.
- Update architecture/components docs for the cleanup behavior.
- Out of scope:
- Contract/flag changes or new state enums.
- Changes to contracted spell cleanup behavior.

## Steps / Checklist
- [x] Add SpellSystemStates.unregister_lineage calls in Spellbook cleanup flow.
- [x] Update SpellSystemStates stubs used by Spellbook tests.
- [x] Add component test for Spellbook cleanup unregister behavior.
- [x] Update architecture/components docs with evidence.

## Deliverables
- Spellbook cleanup unregisters local lineages from SpellSystemStates.
- Component test covering cleanup unregister path.
- Updated architecture/components docs.

## Files / Paths Impacted
- src/melder/spellbook/spellbook.py
- tests/component/melder/spellbook/test_spellbook_component_spellbook.py
- tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py
- tests/unit/melder/aether/conduit/meld/test_meld.py
- tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py
- context_compass/architecture/src_architecture.md
- context_compass/components/src_components.md

## Validation
- Not run.
- Recommended commands:
  - pytest tests/component/melder/spellbook/test_spellbook_component_spellbook.py

## Risks / Rollback Notes
- Removing lineage state could affect diagnostics that expect spellbook-owned
  lineages to persist after cleanup; rollback is to remove the unregister call.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Planned: unregister SpellSystemStates lineages for local spells during
  Spellbook cleanup, update test stubs, add a component test, and refresh
  architecture/components docs to reflect the cleanup behavior.

