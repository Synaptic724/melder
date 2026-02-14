- Completed: 2026-01-28
- Summary: Phase 8 now compiles SpellContract override maps and MeldEngine consumes them without re-deriving.

# Task: Migrate SpellContract override mapping into Phase 8

## Metadata
- Task ID: TASK-2026-01-28-phase8-contract-override-migration
- Story: N/A
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-28
- Updated: 2026-01-28

## Objective
Move SpellContract override mapping out of MeldEngine runtime planning and into
Phase 8 occurrence plan compilation, preserving existing validation behavior
while reducing per-meld work.

## Scope Boundaries
- In scope:
  - Extend OccurrencePlan to carry contract override payload maps + completeness flag.
  - Compute SpellContract override payloads in OccurrencePlanBuilder.
  - Update MeldEngine to consume plan-provided contract override maps instead of
    recomputing them on each run.
  - Update unit tests that construct OccurrencePlan or assert meld plan usage.
- Out of scope:
  - Behavior changes to SpellContract resolution semantics.
  - Mutation override handling changes.
  - Broad refactors of MeldRuntime or SpellCrafter phases beyond required wiring.

## Steps / Checklist
- [x] Review MeldEngine contract override mapping logic and normalization.
- [x] Add contract override payload fields + completeness flag to OccurrencePlan.
- [x] Mirror MeldEngine normalization rules in OccurrencePlanBuilder.
- [x] Populate contract override maps during Phase 8 build when providers resolve.
- [x] Update MeldEngine to use OccurrencePlan fields and remove plan-time rebuilds.
- [x] Update unit tests for OccurrencePlan and MeldEngine plan usage.

## Deliverables
- Phase 8 OccurrencePlan includes contract override maps and completeness indicator.
- MeldEngine uses Phase 8 artifacts for contract overrides (behavior preserved).
- Updated unit tests reflecting the new plan data.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py
- tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py
  - pytest tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine.py

## Risks / Rollback Notes
- Risk: contract override normalization diverges from runtime behavior.
  Mitigation: mirror MeldEngine normalization logic exactly and add tests.
- Risk: plan completeness check blocks valid runs.
  Mitigation: preserve existing MeldEngine behavior for missing/ambiguous contracts.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Added Phase 8 OccurrencePlan fields for contract override payload maps and a
  contract-dependencies-complete flag.
- OccurrencePlanBuilder now compiles contract override maps (defers missing or
  invalid payloads by marking the plan incomplete).
- MeldEngine now consumes OccurrencePlan contract override maps when complete,
  removing the plan-time rebuild logic.
- Updated unit tests to reflect the new OccurrencePlan fields.
