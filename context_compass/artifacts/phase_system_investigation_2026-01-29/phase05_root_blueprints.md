# Phase 5 Investigation (Root Blueprints)

## Metadata
- Created: 2026-01-29
- Updated: 2026-01-29
- Task: TASK-2026-01-29-phase05-root-blueprints-investigation

## Scope
Analyze root blueprint construction, root selection semantics, and artifact attachment rules.

## Key Questions
- How are root spell ids selected?
- Are non-root spells intentionally excluded? Why?
- What artifacts are attached to root spells vs non-roots?
- What would change to treat every spell as a root?

## Evidence
- src/melder/spellbook/spell_crafter/system/spell_system_adjacency_builder.py: SpellSystemAdjacencyBuilder.build
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter.run_phase_root_blueprints
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter._filter_snapshot_to_visible_spells
- src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py: SpellSystemRootBlueprintBuilder.build_root_blueprints
- src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py: SpellSystemRootBlueprintBuilder._build_single_root_dag
- src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py: SpellSystemRootBlueprintBuilder._overlay_sockets_and_index
- src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py: RootResolutionBlueprint
- src/melder/spellbook/spell_crafter/system/spell_system_index.py: SpellSystemIndex
- src/melder/spellbook/spellbook.py: Spellbook._run_resolution_phases_for_conduit

## Findings
- Root selection uses SpellSystemAdjacencyBuilder to compute root_spell_ids as all_spell_ids minus all_dependency_ids (version ids) from SpellSystemStates direct_dependencies.
- SpellCrafter.run_phase_root_blueprints requires Phase 4 validation; it builds a frame-wide adjacency snapshot, filters it to spellbook-visible spells via SpellbookScanner.iter_spells, and recomputes roots after filtering.
- SpellSystemRootBlueprintBuilder builds a RootResolutionBlueprint per root id with a deep DAG of all reachable version ids; edges are provider -> dependent and socket refs + DagIndex are overlaid from SpellLocalTopology.
- SpellCrafter attaches root blueprints and the SpellSystemIndex to root spell crafters only; non-root spells do not receive root blueprints.
- SpellSystemIndex is built for all visible spells and records SpellSystemNode metadata (dependencies, existence, spell_type, conduit_id, is_root).
- Phase 5 also rebuilds ChangeControlManager component_of and registers a revalidator hook when available (duplicated later in Phase 7 wiring).

## Risks / Concerns
- Root detection depends on SpellSystemStates direct_dependencies populated in Phase 3. Missing or stale edges change root selection and blueprint coverage.
- Non-root spells have no root blueprint by design; downstream Phases 8-11 are no-ops for those spells.

## Unknowns
- Whether root_lineage_id should be populated on RootResolutionBlueprint (builder sets None). Investigate downstream consumers.
- Whether root selection should be expanded beyond structural roots (design decision).

## Next Steps
- Trace any runtime or tooling uses of RootResolutionBlueprint.root_lineage_id.
- If the requirement is "every spell has a plan", decide whether to change root selection or add per-spell blueprint generation.
