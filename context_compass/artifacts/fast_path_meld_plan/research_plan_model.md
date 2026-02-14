# Research: Root execution plan model and storage

Date: 2026-01-25

## Scope
Capture evidence for where RootResolutionBlueprint artifacts live today and
what fields are already available to anchor a compiled plan model.

## Evidence
- src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py:RootResolutionBlueprint
- src/melder/spellbook/spell_crafter/spell_crafter.py:SpellCrafter.run_phase_root_blueprints
- src/melder/spellbook/spell_crafter/spell_crafter.py:SpellCrafter.root_blueprint_phase5
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:MeldRuntime.execute

## Findings
- RootResolutionBlueprint already stores a deep DAG, a topological execution
  order, socket refs, and a DagIndex for targeting (RootResolutionBlueprint).
- RootResolutionBlueprint is Cleanable and owns the DAG + index cleanup.
- SpellCrafter.run_phase_root_blueprints attaches RootResolutionBlueprint and
  SpellSystemIndex artifacts to the root SpellCrafter for each root id.
- MeldRuntime.execute pulls the root blueprint from spell._crafter
  (_root_blueprint_phase5) and uses it for GraphMutator and SpellOverrider.

## Unknowns
- UNKNOWN: Where compiled plans should be stored (blueprint vs SpellCrafter vs
  Conduit) without violating cleanup and ownership rules.
  - Why it matters: plan ownership dictates cleanup ordering and cache
    invalidation correctness.
  - Where to investigate: src/melder/spellbook/spell.py (spell ownership),
    src/melder/aether/conduit/conduit.py (conduit lifecycle),
    src/melder/spellbook/spell_crafter/spell_crafter.py:cleanup.
  - Status: uninvestigated.

- UNKNOWN: Whether RootResolutionBlueprint artifacts are unique per conduit id
  or reused across conduits in the same frame.
  - Why it matters: plan signatures must include the right conduit scoping
    inputs to avoid stale wiring.
  - Where to investigate: src/melder/spellbook/spell_crafter/spell_crafter.py:
    run_phase_root_blueprints call sites and any caching of phase 5 artifacts.
  - Status: uninvestigated.
