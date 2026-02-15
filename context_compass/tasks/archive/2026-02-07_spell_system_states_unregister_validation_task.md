Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Task: Trigger validation on lineage unregister

## Metadata
- Task ID: TASK-2026-02-07-spell-system-states-unregister-validation
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Ensure SpellSystemStates.unregister_lineage triggers validation mode for
all spellbooks that reference the unregistered lineage.

## Scope Boundaries
- In scope:
- Update SpellSystemStates.unregister_lineage to notify RiskManager.
- Add unit test coverage for the risk notification.
- Update architecture/components docs for the behavior.
- Out of scope:
- New enums or public API shape changes.
- Changes to RiskManager contract or Spellbook cleanup flow.

## Steps / Checklist
- [x] Add RiskManager notification in unregister_lineage.
- [x] Update SpellSystemStates unregister_lineage docstring.
- [x] Add unit test for risk notification.
- [x] Update architecture/components docs with evidence.

## Deliverables
- Unregister lineage triggers RiskManager validation gating.
- Unit test verifying risk notification.
- Updated architecture/components docs.

## Files / Paths Impacted
- src/melder/aether/dev_ops/spell_system_states/spell_system_states.py
- tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py
- context_compass/architecture/src_architecture.md
- context_compass/components/src_components.md

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py

## Risks / Rollback Notes
- RiskManager notification could surface validation-required flags more often;
  rollback by removing the notification call.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Planned: notify RiskManager on lineage unregister to force validation mode
  for spellbooks referencing the lineage, with tests and docs updated.

