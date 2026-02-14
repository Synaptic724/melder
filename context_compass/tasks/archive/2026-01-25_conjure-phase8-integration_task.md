# Task: Integrate plan compilation as conjure Phase 8

## Metadata
- Task ID: TASK-2026-01-25-conjure-phase8-integration
- Story: STORY-2026-01-25-plan-compilation-phase8
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Wire plan compilation into the SpellCrafter and Spellbook conjure pipeline as
Phase 8, scoped per conduit.

## Scope Boundaries
- In scope:
  - Phase 8 entrypoint and wiring.
  - Conduit-scoped plan cache integration.
- Out of scope:
  - Fast-path runtime execution.

## Steps / Checklist
- [ ] Add Phase 8 entrypoint in SpellCrafter.
- [ ] Invoke Phase 8 during Spellbook.conjure after Phase 5 or Phase 7.
- [ ] Ensure cleanup nulls plan references.

## Deliverables
- Conjure pipeline wires plan compilation.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/spell_crafter.py
- src/melder/spellbook/spellbook.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/component/melder/spellbook -k conjure

## Risks / Rollback Notes
- Risk: Phase 8 ordering conflicts with existing validation.
  Mitigation: document required phase ordering and add tests.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; Phase 8 integration pending.
