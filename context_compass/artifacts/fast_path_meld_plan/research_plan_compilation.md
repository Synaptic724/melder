# Research: Plan compilation inputs (occurrence graph and arg binding)

Date: 2026-01-25

## Scope
Document runtime structures that are currently built inside MeldEngine and would
need to move into conjure for a compiled plan.

## Evidence
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:MeldEngine.run
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_occurrence_graph
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_instance_plan
- src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py:RootResolutionBlueprint
- src/melder/spellbook/spell_crafter/topology/spell_local_topology.py:SpellLocalTopology

## Findings
- MeldEngine.run builds an occurrence graph and instance plan on each execution.
- _build_occurrence_graph returns a mapping of occurrence -> param_name -> child
  occurrences and uses local topology when available (docstring).
- _build_instance_plan produces instance keys by spell id, canonical
  occurrences for shared existences, and a root instance key (docstring).
- RootResolutionBlueprint already exposes a deep DAG, ordered node list, and
  DagIndex for socket targeting.
- SpellLocalTopology captures per-spell socket descriptors (param name, position,
  socket kind, and target spell ids) and is produced in Phase 3.

## Unknowns
- UNKNOWN: Exact data needed from SpellLocalTopology and SpellRequirements to
  precompute argument binding recipes for each plan step.
  - Why it matters: arg binding shape determines whether the compiled plan can
    avoid per-call kwargs construction.
  - Where to investigate: src/melder/spellbook/spell_crafter/spell_examiner/
    spell_requirements_finder/spell_requirements.py and
    src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_instance_kwargs.
  - Status: uninvestigated.

- UNKNOWN: Whether occurrence expansion is stable across conduits when contract
  visibility changes, or if it must be recomputed per conduit link state.
  - Why it matters: plan caching and invalidation must include conduit wiring
    state if occurrences depend on contracted spells.
  - Where to investigate: src/melder/aether/conduit/meld/meld_engine/meld_engine.py
    and SpellSystemStates contract visibility data.
  - Status: uninvestigated.
