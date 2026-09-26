# Survey record: phase 2 (symbolic graph)

Recorded 2026-09-26 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, task 1, step S2).
Status: COMPLETE. Read whole: `phases/compiler_phase_2.py` (184 lines),
`symbolic_graph/spell_symbolic_graph.py` (153), `symbolic_graph/spell_symbolic_dependency.py` (256).
Ranges without a file name are into `compiler_phase_2.py`.

## Entry
- `CompilerPhase2.run(spell, artifact, cancel_event)` (:49-178), called by
  `SpellCompiler.run_phase_symbolic_graph` (spell_compiler.py:129-158). Slot-only phase object (:47).
- Raises RuntimeError if phase 1 has not populated `artifact._requirements` (:96-100) or the spell
  has no `spell_index.selected_spell_id` (:103-105); it never auto-runs phase 1.

## Consumes
- `artifact._requirements.parameters` (phase-1 rows) (:109); per row: `di_shape`, `annotation`,
  `collection_element_annotation`, `spellmap_default`, `default_value` (only to read
  `SpellContract.canonical_key`), `name`, `position`, `is_optional` (:110-171).
- `spell.spell_index.selected_spell_id` as the versioned identity (:102-105).

## Produces
- `artifact._symbolic_graph = SpellSymbolicGraph(spell_id, dependencies)` (:175-178;
  spell_symbolic_graph.py:66-89), one `SpellSymbolicDependency` per parameter whose shape is
  SINGLE_BY_ANNOTATION, COLLECTION_BY_ANNOTATION, SPELLMAP_DEFAULT, PLAIN or SPELL_CONTRACT; IGNORE
  rows are skipped (:113-122). PLAIN parameters DO become edges, carrying the raw annotation "for
  diagnostics and override targeting" (spell_symbolic_dependency.py:48-52).
- Edge fields (spell_symbolic_dependency.py:96-138): spell_id, param_name, position, di_shape,
  is_optional, target_annotation, is_collection, spellmap_default, contract_key.
- Shape -> edge mapping (:124-160): SPELLMAP_DEFAULT -> (None, False, the SpellMap);
  SINGLE -> (annotation, False, None); COLLECTION -> (element annotation, True, None);
  PLAIN -> (annotation, False, None); SPELL_CONTRACT -> (annotation, False, None) plus
  `contract_key = default_value.canonical_key` (:154-155).
- Dropped at this boundary: `default_value` for every non-contract shape (the exact default object
  of phase 1 is NOT carried into the edge), `has_default`, `kind`, the var-arg flags.
- Read later by: phase 3 (DAG construction; docstrings :72, spell_symbolic_graph.py:41-46).
  `dependencies` returns a shallow list copy per read (spell_symbolic_graph.py:133-152).

## Holds (classified)
- `spell_id`, `param_name`, `position`, `is_optional`, `is_collection`, `di_shape` -> VALUE.
- `contract_key: Optional[Tuple[str, str]]` = "(frame_key, binding_key)" derived from the
  SpellContract descriptor (:154-155; spell_symbolic_dependency.py:62-64) -> VALUE. The contract
  socket is already value-shaped at this phase.
- `target_annotation: Any` = concrete class, Protocol type, str, or None (spell_symbolic_dependency
  .py:215-227) -> VALUE-EXPRESSIBLE as a type ref; held LIVE today. Phase 2 does not match it
  against anything; it is the DI key "used in later phases" (:48-52), so the identity-vs-name
  question passes to phase 3 unchanged.
- `spellmap_default: Any` = the live SpellMap descriptor instance -> UNKNOWN until spell_map.py is
  read (fields may be value-only).
- RUNTIME-ONLY baggage: one `threading.RLock` per graph (spell_symbolic_graph.py:86) and per edge
  (spell_symbolic_dependency.py:126); Cleanable state; rebuilt on every conjure.

## Mutates
- The artifact only (`_symbolic_graph`, :175). "Does not mutate the Spell" and "does not build any
  concrete DAG or talk to SpellSystemStates" (:72-74); no other assignment target in the file.

## Reflection points (user objects)
- None on user objects. The only introspection is `isinstance(param.default_value, SpellContract)`
  and `.canonical_key` on a Melder descriptor (:154-155).

## Python-callback points
- None. `CompilerPhaseUtility.throw_if_cancelled` (Melder-owned) at entry (:92).

## World reads
- NONE. Inputs are the artifact and one Spell attribute. Phase 2 is a pure function of the phase-1
  rows plus `selected_spell_id`; output order is signature order.

## Snapshot relevance (per-spell tier)
- Phase 2 is per-spell, closed and deterministic, so it belongs to the per-spell tier of a structural
  snapshot: either hydrate its edges from rows or recompute it from the phase-1 rows (cheap). Today it
  reallocates the graph, N edges and N+1 RLocks on every conjure even though its input is borrowed
  from bind. The resolution profile already reserves `SpellSymbolicNode/Edge/Graph` placeholders
  for a bind-time copy (profiles/resolution_profile.py:11-402, per phase_01.md).
- The dormant export serializes these edges as "symbolic dependency tuples"
  (shared_compiler_executions.py:266-376); how `target_annotation` (a live class) is rendered there
  is UNKNOWN and is a step S9 re-verification item (D3).

## Contradictions
- None against the maps. Residue: error strings still say "SpellCrafter Phase 2" (:97-99, :105) and
  the class docstring says it "ports the canonical `SpellCrafter` phase-2 behaviour" (:43); the
  architecture map records the rename to `SpellCompiler`.

## UNKNOWN (with where to look)
- Which later phase reads the phase-1 `default_value` for PLAIN parameters, given phase 2 drops it:
  phases/compiler_phase_3.py; codegen_creation_system emitters (identity candidate #1).
- Identity vs name matching of `target_annotation`: phases/compiler_phase_3.py.
- Rendering of `target_annotation` and `spellmap_default` in the dormant export:
  phases/shared_compiler_executions.py:266-376.
- SpellMap descriptor fields: conduit/meld/contracts/spell_map.py:1-344.
