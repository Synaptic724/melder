# Task: Remove SpellbookScanner and update tests/docs

## Metadata
- Task ID: TASK-2026-01-31-remove-spellbook-scanner
- Story: N/A
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Remove SpellbookScanner from runtime usage and tests, replacing lookups with live Spellbook registries, and update documentation/tests to reflect new behavior.

## Scope Boundaries
- In scope:
  - Eliminate SpellbookScanner references in runtime code and tests.
  - Update tests to use live spellbook registries and new occurrence-plan/DagIndex behavior.
  - Update architecture/components docs to remove SpellbookScanner references.
- Out of scope:
  - Behavior changes unrelated to spell scanning/removal.
  - Refactors not required by the removal.

## Steps / Checklist
- [x] Remove SpellbookScanner references from runtime code and tests.
- [ ] Update occurrence-plan and DagIndex tests for new behavior.
- [x] Remove/delete SpellbookScanner-specific test files.
- [x] Update architecture/components docs to remove SpellbookScanner references.
- [x] Update validation strategy stubs to use live spell_id pools.
- [ ] Run or report validation status.

## Deliverables
- Updated runtime code without SpellbookScanner usage.
- Updated tests reflecting live spellbook registries.
- Updated docs with SpellbookScanner removed.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/validation/strategies/dangling_dependency_strategy.py`
- `tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py`
- `tests/unit/melder/spellbook/spell_crafter/dag/test_dag_index.py`
- `tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `tests/unit/melder/spellbook/spell_crafter/validation/test_validation_system.py`
- `tests/unit/melder/spellbook/spell_crafter/validation/test_spell_validation_context.py`
- `tests/unit/melder/spellbook/spell_crafter/validation/strategies/*.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spellbook_scanner.py` (remove)
- `tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py`
- `tests/component/melder/spellbook/test_spellbook_component_spellbook_scanner.py` (remove)
- `tests/integration/melder/spellbook/test_spellbook_integration_spellbook_scanner.py` (remove)
- `tests/component/melder/spellbook/spell_crafter/validation/test_spellbook_component_validation_context.py`
- `tests/component/melder/spellbook/spell_crafter/validation/test_spellbook_component_validation_strategies.py`
- `context_compass/architecture/src_architecture.md`
- `context_compass/components/src_components.md`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py`
  - `pytest tests/unit/melder/spellbook/spell_crafter/dag/test_dag_index.py`
  - `pytest tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine.py`

## Risks / Rollback Notes
- Removing SpellbookScanner may affect ordering assumptions in tests; adjust expectations to match registry iteration order.
- Rollback by restoring SpellbookScanner references and tests if needed.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Task created to remove SpellbookScanner usage and update tests/docs accordingly.
- Replaced remaining component/validation test usage of SpellbookScanner with live
  Spellbook `_spell_id_pool` access and updated related docstrings.
- Removed SpellbookScanner references from architecture/components docs.
- Updated binding cycle validation to iterate `_spell_id_pool` and refreshed
  strategy test stubs to always define `dependencies`/`dependency_graph`.
- Work in progress; no validation run yet.
