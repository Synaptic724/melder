# Task: Add spell disposal metadata during conjure

- Completed: 2026-01-25
- Summary: Added Spell disposal metadata fields and conjure-time computation in
  `src/melder/spellbook/spell.py` and `src/melder/spellbook/spellbook.py`.
- Summary: Updated `ISpell` contracts and added component coverage in
  `tests/component/melder/spellbook/test_spellbook_component_spellbook.py`.

## Metadata
- Task ID: TASK-2026-01-25-spell-disposal-metadata
- Story: N/A (user-approved task-only)
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Add conjure-time disposal metadata to each Spell so we can cheaply decide whether
the spell has any configured disposal methods (per configuration + binding profile)
without re-inspecting spell objects during meld/runtime.

## Scope Boundaries
- In scope:
  - Compute disposal method names present on the bound spell (from binding profile).
  - Store a list of matched disposal methods and a boolean flag on Spell.
  - Run the computation during `Spellbook.conjure` after configuration is frozen.
  - Update the ISpell protocol to reflect the new fields.
  - Add a component test that proves the conjure-time metadata is set.
- Out of scope:
  - Changing Creations/LesserCreations behavior or cleanup logic.
  - Any changes to mutation paths or spell_id/lineage behavior.
  - New configuration properties or changes to validation semantics.

## Steps / Checklist
- [x] Add disposal metadata fields to Spell with clear docstrings.
- [x] Implement a Spellbook internal helper to compute disposal metadata post-freeze.
- [x] Invoke the helper during `Spellbook.conjure` before hooks are fired.
- [x] Update ISpell protocol with new attributes.
- [x] Add component test(s) validating disposal metadata set during conjure.
- [x] Review docstrings/comments touched for accuracy.

## Deliverables
- Spell disposal metadata fields and conjure-time wiring.
- Component test coverage for disposal metadata population.

## Files / Paths Impacted
- `src/melder/spellbook/spell.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/utilities/interfaces/interfaces.py`
- `tests/component/melder/spellbook/test_spellbook_component_spellbook.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/component/melder/spellbook/test_spellbook_component_spellbook.py -k disposal`

## Risks / Rollback Notes
- Risk: Binding profile method names may not reflect callable disposal methods for
  non-class spell types.
  Mitigation: Scope computation to available profile data; treat missing data as
  "no disposal methods" and avoid runtime inspection.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Conjure-time disposal metadata is computed by
  `Spellbook._define_disposal_metadata_on_spells` and stored on Spell fields
  `disposal_method_names` / `has_disposal_methods`
  (`src/melder/spellbook/spellbook.py`, `src/melder/spellbook/spell.py`).
- ISpell now exposes disposal metadata fields
  (`src/melder/utilities/interfaces/interfaces.py`).
- Component coverage validates disposal metadata results for class vs callable
  spells (`tests/component/melder/spellbook/test_spellbook_component_spellbook.py`).
- Validation: Not run.
