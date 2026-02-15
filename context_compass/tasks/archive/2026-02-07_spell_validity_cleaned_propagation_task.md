Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Task: Propagate cleaned validity through meld gating

## Metadata
- Task ID: TASK-2026-02-07-spell-validity-cleaned-propagation
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Treat SpellValidity.cleaned as a hard block during meld gating and resolution
validation, and document the new validity semantics.

## Scope Boundaries
- In scope:
  - Update Meld resolution gating to block cleaned validity.
  - Add unit tests covering cleaned validity gating.
  - Update architecture/components docs to reflect cleaned semantics.
- Out of scope:
  - Any additional public API changes.
  - Broader refactors of SpellSystemStates or RiskManager.

## Steps / Checklist
- [x] Update meld resolution validity gating to treat cleaned as a hard block.
- [x] Add unit tests for cleaned validity in meld gating.
- [x] Update architecture/components docs with cleaned validity semantics.

## Deliverables
- Meld resolution gating blocks cleaned validity.
- Unit tests proving cleaned validity is blocked.
- Updated docs reflecting cleaned validity semantics.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld.py
- tests/unit/melder/aether/conduit/meld/test_meld.py
- context_compass/architecture/src_architecture.md
- context_compass/components/src_components.md
- context_compass/tasks/2026-02-07_spell_validity_cleaned_propagation_task.md

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld/test_meld.py

## Risks / Rollback Notes
- If cleaned gating blocks legitimate usage, revert the cleaned checks in meld.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Meld resolution gating now treats SpellValidity.cleaned as a hard block
  alongside invalid/disabled. Tests cover cleaned lineage gating and cleaned
  resolution gating, and docs now reference cleaned for unregister-triggered
  RiskManager notifications.

