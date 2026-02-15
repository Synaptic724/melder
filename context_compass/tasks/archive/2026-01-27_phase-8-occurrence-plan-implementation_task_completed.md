# Task: Implement Phase 8 OccurrencePlan compilation and wiring

- Completed: 2026-01-27
- Summary: Archived Phase 8 occurrence plan implementation ticket per user
  direction; checklist items remain as recorded below.

## Metadata
- Task ID: TASK-2026-01-27-phase-8-occurrence-plan-implementation
- Story: STORY-2026-01-25-plan-compilation-phase8
- Status: complete
- Owner:
- Priority: p1
- Created: 2026-01-27
- Updated: 2026-01-27

## Objective
Compile and store the Phase 8 OccurrencePlan during conjure and expose it via
Spell/SpellCrafter phase APIs, with unit tests covering plan generation.

## Scope Boundaries
- In scope:
  - SpellCrafter Phase 8 entrypoint and artifact storage.
  - Spell facade + ISpell interface updates for Phase 8.
  - Spellbook phase scheduler integration for Phase 8.
  - Unit tests for OccurrencePlan builder + Phase 8 integration.
- Out of scope:
  - MeldRuntime consumption of the plan.
  - Phase 9/10 plan compilation.
  - Runtime gating changes.

## Steps / Checklist
- [x] Add Phase 8 artifact storage and cleanup to SpellCrafter.
- [x] Implement SpellCrafter.run_phase_occurrence_plan.
- [x] Add Spell.run_phase_occurrence_plan facade and update run_all_phases.
- [x] Update ISpell interface for Phase 8 surface.
- [x] Add Spellbook Phase 8 scheduler factory and phase registration.
- [x] Add unit tests for OccurrencePlan compilation and Phase 8 wiring.

## Deliverables
- Phase 8 OccurrencePlan compiled and stored in SpellCrafter.
- Spell/ISpell expose Phase 8 method.
- Spellbook scheduler runs Phase 8.
- New unit tests for OccurrencePlan.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/spell_crafter.py
- src/melder/spellbook/spell.py
- src/melder/utilities/interfaces/interfaces.py
- src/melder/spellbook/spellbook.py
- tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/spellbook/spell_crafter/blueprints -k occurrence_plan

## Risks / Rollback Notes
- Risk: Phase ordering mismatch with existing validation expectations.
  Mitigation: mirror Phase 5/6 ordering and keep Phase 8 optional for non-roots.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Phase 8 wiring added in SpellCrafter/Spell/ISpell/Spellbook with OccurrencePlan
storage, compilation, and scheduler integration. Unit tests added for the
OccurrencePlan builder and the Phase 8 entrypoint. Components and architecture
docs updated to reflect Phase 8 in conjure phase flows. Validation not run.
