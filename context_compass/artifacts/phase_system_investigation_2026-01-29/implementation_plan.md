# Implementation Plan: Phase 11 Fast Path (Constructed Spells) + Existing-Creation Bypass

## Metadata
- Date: 2026-01-29
- Epic: EPIC-2026-01-29-phase-system-investigation
- Story: STORY-2026-01-29-phase11-fast-path-implementation
- Task: TASK-2026-01-29-phase11-fast-path-implementation

## Objective
Ensure every constructed spell (class/method/lambda) receives Phase 11 artifacts via the phase system, while existing-creation spells bypass Phase 8-11 compilation.

## Scope
- In scope:
  - Phase 5 attaches a RootResolutionBlueprint to each constructed spell.
  - Phase 8-11 compile for spells with attached blueprints.
  - Existing-creation spells skip Phase 8-11.
  - Root-only blueprint map remains root-scoped for Phase 6 validation.
  - Documentation updates (SpellCrafter, Spellbook phase factory docs, architecture/components).
- Out of scope:
  - Performance tuning.
  - Test updates (explicitly skipped by user).

## Evidence Targets
- Phase 5 root blueprints builder: src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py
- Phase 5 attachment in SpellCrafter: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints
- Phase 8-11 compilation gates: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_occurrence_plan, run_phase_injection_plan, run_phase_patch_maps, run_phase_execution_plan
- Phase 6 validation expects root-only blueprint map: src/melder/spellbook/spell_crafter/system/validation/root_coverage_strategy.py
- Resolution phase scheduling docs: src/melder/spellbook/spellbook.py:_run_resolution_phases_for_conduit

## Proposed Changes
1) Add a Phase 5 builder method for per-spell blueprints.
   - Build a RootResolutionBlueprint for an arbitrary spell id using the existing DAG builder.
   - Overlay sockets and DagIndex.

2) Attach per-spell blueprints in Phase 5.
   - Keep the root-only blueprint map for Phase 6 validation.
   - Attach the per-spell blueprint to each constructed spell's SpellCrafter.

3) Skip Phase 8-11 compilation for existing-creation spells.
   - Early return from Phase 8-11 methods when spell.is_existing_creation is True.

4) Update docstrings and architecture/components docs.
   - SpellCrafter: remove root-only wording where no longer accurate.
   - Spellbook phase factories: clarify compilation applies to any spell with an attached blueprint, with existing-creation bypass.
   - Architecture/components: update phase pipeline semantics for Phase 5-11.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py
- src/melder/spellbook/spell_crafter/spell_crafter.py
- src/melder/spellbook/spellbook.py
- context_compass/architecture/src_architecture.md
- context_compass/components/src_components.md

## Step-by-Step Plan
- [ ] Add build_blueprint_for_spell_id to SpellSystemRootBlueprintBuilder.
- [ ] Update SpellCrafter.run_phase_root_blueprints to attach per-spell blueprints.
- [ ] Add existing-creation bypass in Phase 8-11 methods.
- [ ] Update SpellCrafter docstrings to match new semantics.
- [ ] Update Spellbook phase factory docstrings to match new semantics.
- [ ] Update architecture/components docs with the new Phase 5-11 behavior.

## Acceptance Criteria
- Every constructed spell has a Phase 5 blueprint attached after Phase 5 runs.
- Phase 8-11 compilation runs for constructed spells and is skipped for existing-creation spells.
- Phase 6 validation still uses root-only blueprint maps without misclassifying non-roots.
- Documentation accurately reflects the updated semantics.

## Validation
- Not run (user requested no tests).
- Recommended command (later): pytest -q

## Risks / Notes
- Risk: Per-spell blueprint attachment could be mistaken as root coverage by Phase 6 strategies.
  - Mitigation: keep root-only blueprint map for system validation.
- Risk: Skipping tests hides regressions.
  - Mitigation: document validation as not run and recommend follow-up test run.
