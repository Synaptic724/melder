# Survey record: phase 5 (root blueprints, system index, change-control bridge)

Recorded 2026-09-26 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, task 2, step S6).
Status: COMPLETE. Read whole: `phases/compiler_phase_5.py` (713 lines, two chunks),
`system/spell_system_adjacency_builder.py` (95), `system/spell_system_adjacency_snapshot.py` (166),
`system/spell_system_node.py` (173), `system/spell_system_index.py` (174),
`system/spell_system_root_blueprint_builder.py` (490), `blueprints/root_resolution_blueprint.py`
(298); `spellbook_creation_system.py:2849-2888` (`phase_root_blueprints_factory`). Not read:
`dag/dag_index.py` (768: `DagIndex`, `PathRegistry`, `SocketRef`) - named as the crossing type only.
Ranges without a file name are into `compiler_phase_5.py`.

## Entry
- Frame-wide: `CompilerPhase5.run_frame_wide(spell, artifact, spellbook, spell_system_states,
  conduit_id, cancel_event)` (:473-615), ONE unit per conjure on the "lead" spell = first value of
  `spellbook._spells` (spellbook_creation_system.py:2872-2888); the lead's artifact receives the
  frame-level index and the whole blueprint map (:546-550).
- Local: `run_local(...)` (:617-712) for the meld-time target path: same pipeline narrowed to the
  target's dependency closure, publication to the target only (:695-702).

## Consumes (world reads)
- `SpellSystemStates` PRIVATE fields under its locks: `_states_by_index_id`, each state's
  `_current_spell_id` and `_direct_dependencies`, and `_local_topologies` - the phase-3 writes -
  through `SpellSystemAdjacencyBuilder.build` (spell_system_adjacency_builder.py:30-95). Roots =
  spells never appearing as a dependency (:85-87).
- `spellbook._spell_id_pool` items: `resolvable` (visibility filter, :517-519), `existence`,
  `spell_type`, `_owner_conduit_id`, `is_existing_creation`, `_compiler_artifact` (:297-310,
  :358-367); `SpellSystemStates.get_by_spell_id(id).spell_index_id` (lineage id, :293-296).
- `spellbook._spells_by_id.keys()` = OWNED spells, the publication scope (:466-471, :543).
- `spellbook._aetheric_frame_name`; `spellbook._aether._get_change_control_manager(frame_name)`
  (:557-558).
- NOT the phase 1-4 artifacts: phase 5 reads registry state only, so the S5 reset does not affect
  it (structural_driver.md).

## Produces
- `SpellSystemAdjacencySnapshot` (live views onto SpellSystemStates collections; no copies;
  spell_system_adjacency_snapshot.py:34-57), filtered to visible ids with recomputed reverse edges
  and roots (:381-439).
- `SpellSystemIndex` of `SpellSystemNode(spell_id, lineage_id, dependencies, existence, spell_type,
  conduit_id, ward_id=None, is_root)` - values only, one Cleanable per node
  (spell_system_node.py:40-76; spell_system_index.py:93-111).
- `RootResolutionBlueprint` per structural root (:532-535) and a fallback per owned non-root
  constructed spell (:369-374): `root_spell_id`, `root_lineage_id=None`, a
  `DirectedAcyclicWorkGraph` whose nodes are version ids with payload None and edges
  provider -> consumer with no param/kind (spell_system_root_blueprint_builder.py:341-433),
  `ordered_node_ids` (dependencies first, root last), `requires_spellspace_request` (any
  `unique_per_spell_space` spell in the closure, :298-299, :294-315 of the builder), `socket_refs`
  overlaid by BFS over the topologies with `PathRegistry.extend_path(parent_path_id, param_name)`
  interning root-relative parameter paths as ints (builder :435-490), and a lazily built
  `DagIndex` (root_resolution_blueprint.py:250-269).
- Determinism: reachable sets memoized per snapshot; nodes and edges inserted in sorted order; topo
  ties break on id (builder :94, :412-431). Blueprint content is a pure function of (adjacency,
  visible ids, topologies, existence per spell).

## Mutates (the hydrate obligations of phase 5)
1. For EVERY owned spell (publication scope): `artifact._spell_system_index_phase5 = index` (the
   one shared index object) and, unless existing-creation, `artifact._root_blueprint_phase5 =
   blueprint`, `artifact._requires_spellspace_request_phase5`, `spell.requires_spellspace_request`
   (:166-217, :355-379). Each attach INVALIDATES the spell's occurrence analysis, codegen outputs
   and creation context (:191-193, :215-217) - so every conjure discards 8-11 state for every owned
   spell before the cache path decides whether to rebuild or load it.
2. Lead artifact: `_spell_system_index_phase5`, `_entire_dag_blueprint_phase5` (root id ->
   blueprint), plus the same three invalidations on the lead (:546-554).
3. `ChangeControlManager.rebuild_component_of(conduit_id, owned_root_blueprints)` (:556-566).
4. `ChangeControlManager.set_revalidator(conduit_id, _revalidate_dirty_roots)` once per conduit
   (:611-615): a CLOSURE over `spellbook` and `conduit_id` that, per dirty root, constructs a
   `SpellCompilerSystem` and runs `run_all_phases(spellbook, spell, conduit_id)` (:568-609).

## Holds (classified)
- Blueprint DAG: node ids, edges, order, socket refs (ints and enums), path registry -> all
  VALUE-EXPRESSIBLE; the containers are Cleanable objects with a lock
  (root_resolution_blueprint.py:87-100). Payloads are None by design (builder :410-411).
- `SpellSystemIndex`/`SpellSystemNode`: values (`conduit_id` is the owning conduit id string).
- Adjacency snapshot: live references into SpellSystemStates (transient; per pass).
- The revalidator closure: RUNTIME-ONLY callable held by the ChangeControlManager; reconstructible
  from `(spellbook, conduit_id)` at hydration; not serializable.
- `_entire_dag_blueprint_phase5` on the lead artifact: the blueprint map (objects).

## Reflection points (user objects)
- None. Every read is a Melder object or registry field.

## Python-callback points
- None during the phase. The registered closure runs later, on change-control revalidation, and
  executes the compiler (Melder code) for dirty roots.

## Snapshot relevance
- Phase 5 is the per-CONDUIT tier's first member: its inputs are registry rows plus per-spell facts
  and its outputs are already value-shaped rows (the dormant export's "phase-5 socket rows and DAG
  edge rows"). Hydrate = rebuild `RootResolutionBlueprint`/`SpellSystemIndex` objects from rows and
  attach them per owned spell, then replay `rebuild_component_of` and `set_revalidator`; or simply
  recompute phase 5 from hydrated registry state (it is deterministic and reads nothing else).
- Whether the cached creation contexts (full hit) need `_root_blueprint_phase5` or the index on the
  artifact is the D6 question (S8).
- The `is_root` set and the visible set depend on `resolvable` and on which spells exist: the
  snapshot key must include the resolvable-spell-id set (already the cache-classification input).

## Contradictions
- None against the maps. The map's "phase 7 change control" is partly done here: component-of
  rebuild and revalidator registration happen in phase 5 (:556-615); phase 7's own writes are S7.
- Docstring residue: "SpellCrafter" (:59, :88, :108, :131, :161) and "phase-2-5 cache" mentions in
  `run_local` (:639-640) that the code no longer performs (:709).

## UNKNOWN (with where to look)
- `DagIndex`, `PathRegistry`, `SocketRef` exact fields and the `DagIndex.rebuild` cost:
  dag/dag_index.py (768) - read when the blueprint row format is designed.
- Who reads `artifact._spell_system_index_phase5` and `_entire_dag_blueprint_phase5` downstream:
  phases 6-8 (S7) and the emitters (tranche 3).
- `ChangeControlManager.rebuild_component_of` / `set_revalidator` internals: S7.
