# Survey record: phase 3 (local frame, DAG, topology)

Recorded 2026-09-26 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, task 1, step S3).
Status: COMPLETE. Read whole: `phases/compiler_phase_3.py` (1035 lines, three chunks),
`dag/directed_acyclic_work_graph.py` (391), `dag/dag_node.py` (239), `dag/socket_kind.py` (37),
`dag/target_spec.py` (129), `topology/spell_local_topology.py` (240). Read by method:
`utilities/helpers/general_helpers.py:372-423` (`normalize_spell_key`), `spell.py:1443-1480`
(`_add_build_details`), `spell_system_states.py:470-527` (`update_dependencies`) and
`:1262-1318` (`register_local_topology`). Not read: `dag/dag_index.py` (768; phase 5/8 interning,
deferred to S6), `dag/resolution_frame/resolution_frame.py` (279; not imported by phase 3).
Ranges without a file name are into `compiler_phase_3.py`.

## Entry
- `CompilerPhase3.run(spell, artifact, spellbook, spell_system_states, cancel_event,
  resolution_pass_cache)` (:928-1033). Requires phases 1-2 outputs on the artifact (:988-992) and a
  live `SpellSystemStates` (:994-996). Body: `_build_local_frame_dag` (:770-926).

## Consumes
- `artifact._requirements` (parameter kinds by name, :732) and `artifact._symbolic_graph`
  (edges, :734, :847).
- `spell`: `spell_index.selected_spell_id` (:90-93), `spell_index` (:823, :913-921), `resolvable`
  (:746, :833, :847), `spell_name` (error text).
- WORLD: `spellbook._spell_id_pool.values()` - every spell in the book, in insertion order
  (:118-137) - through the pass-scoped candidate index (:277-346) when `resolution_pass_cache` is
  supplied, else by scan per dependency (:477-484, :544-551). SpellMap defaults always scan
  (:609-627). Per candidate: `spell` (bound object), `spellframe`, `spell_name`, `binding_name`,
  `spell_type`, `resolvable`, `spell_index.selected_spell_id`, and the `__eq__` of the bound
  object's and frame's types (:311-337, :252-275).
- `spellbook._nexus_publish_enabled` (:1031); `resolution_pass_cache` dict (driver-owned, :364-372).
- SpellMap descriptor fields: `.spell`, `.spellframe`, `.binding_name`, `.canonical_key`,
  `.spell_override` (:605-607, :676, :884).

## Produces
- DAG `DirectedAcyclicWorkGraph` (:827): root node keyed by the spell id with the live Spell as
  payload (:837); one node per resolved dependency, payload = that Spell (:897); edges
  parent=dependency -> child=root tagged `param_name` and `SocketKind` (:898-903;
  directed_acyclic_work_graph.py:181-221). Each DAG mints its own `IDBuilder.create_id()` and owns an
  RLock (directed_acyclic_work_graph.py:65-66). Topological order ties break on node id string, so
  `collect_dependency_ids()` is deterministic (:255-296, :363-370).
- `artifact._resolution_frame = SpellResolutionFrame(spell_id, ordered_node_ids)` (:1016-1019) -
  VALUE-ONLY, and already the resolution-profile family's class (:40-42).
- `SpellLocalTopology(spell_id, sockets)` (:764-767) of frozen `SpellSocketDescriptor` dataclasses
  (spell_local_topology.py:11-99): spell_id, param_name, position, socket_kind, is_collection,
  is_optional, target_spell_ids, dependency_key, contract_key, referenced_spell_ids,
  parameter_kind - ALL VALUES (strings, ints, bools, enum, tuples of strings).
- `dependency_spell_ids` (ordered, duplicates removed at :1022) and per-socket `socket_targets` /
  `socket_references` maps (:844-845, :892-895).

## Mutates (the hydrate obligations of phase 3)
1. `spell_system_states.update_dependencies(spell.spell_index, dependency_spell_ids)` (:914-917):
   creates the lineage `SpellSystemState` if missing, diffs direct dependencies, maintains reverse
   `dependents` edges on the dependency states, then `state.mark_dependency_change()` and adds the
   index to `_dirty_indexes` (spell_system_states.py:470-527). So EVERY conjure gates and dirties
   every spell it compiles; whatever clears that is a later phase's write (S4/S7).
2. `spell_system_states.register_local_topology(spell.spell_index, topology)` (:918-921): stores the
   live topology under `selected_spell_id` and rebuilds the owner-spellbook-scoped collection-frame
   and contract reverse indexes (spell_system_states.py:1262-1318).
3. `spell._add_build_details(dag=dag, dependencies=unique_dependencies)` (:1022-1030): sets
   `Spell.dependency_graph` (the live DAG object) and `Spell.dependencies` (ids), then
   `_cleanup_creation_context()` - INVALIDATES the spell-owned CreationContext so the runtime shape
   is rebuilt (spell.py:1443-1480). Wrapped in `except AttributeError: pass` for test stubs.
4. `spellbook._publish_spell_record_to_nexus(spell)` when `_nexus_publish_enabled` (:1031-1032).
5. `resolution_pass_cache["phase3_candidate_index"]` memo, benign last-writer-wins (:364-372).
6. The artifact: `_resolution_frame` (:1016).

## Holds (classified)
- DAG node payloads = live Spells (:837, :897) and node-to-node references (dag_node.py:67-68,
  :79-83) -> the DAG is VALUE-EXPRESSIBLE as node ids plus (parent, child, param_name, socket_kind)
  rows; payloads are recoverable by id -> Spell lookup at hydration. Whether any runtime reader
  uses `Spell.dependency_graph` (and thus needs a DAG object rebuilt) is UNKNOWN.
- Candidate index buckets hold live Spells keyed by `id(bound_object)` / `id(frame)` (:331-335);
  pass-scoped and transient.
- Topology descriptors: values only; `SpellLocalTopology` adds a Cleanable wrapper and a
  by-param index (spell_local_topology.py:160-165).
- `contract_key`, `dependency_key`: `(frame_key, binding_key)` string pairs from
  `SpellInputUtils.normalize_spell_key` / descriptor `canonical_key` (:672-689;
  general_helpers.py:372-423) -> VALUE.

## Identity vs name (answer to the epic's matching question)
- BOTH, by annotation type. String and ForwardRef annotations match BY NAME: `spell_name ==`,
  str frame `==`, class frame `__name__ ==` (:219-237). Non-string annotations match BY IDENTITY:
  `spell_obj.spell is annotation` (:239) and `frame is annotation or frame == annotation` (:244-245).
- The indexed path keys on `id(bound_object)` and `id(frame)` (:331-335, :403) and is used only when
  every bound object and frame is "eq-safe" (default `type.__eq__` / `object.__eq__`); a custom
  `__eq__` anywhere in the pool disables the index and restores the `==` scan (:252-275, :313-317,
  :370-371). SpellMap resolution is identity on `.spell` (:611) and identity-or-equality on frames
  (:616, :625), never indexed.
- Consequence for a value-only IR: a canonical type reference (module, qualname) reproduces the
  identity match exactly when both sides resolve to the same object, which is the bind-fingerprint
  guarded case; the `==` fallback on frames with custom `__eq__` is the one place an identity
  concept is genuinely needed (or a canonical frame key must be defined and ruled by the owner).
  `dependency_key` shows the canonical form already exists for the NORMAL sockets.

## Late binding and fail-fast
- Non-resolvable root: no candidate index and no dependency loop; topology is still built and
  registered (:833, :847, :906-921). Non-resolvable candidates become `socket_references` and the
  socket kind becomes OVERRIDE_REQUIRED (:881-893, :742-744); a SpellMap with `spell_override`
  selecting a non-resolvable definition raises (:882-891).
- SpellContract and PLAIN sockets produce topology descriptors but no DAG edge (:868-872, :718-719).
- Zero SINGLE candidates or more than one raises RuntimeError at conjure (:492-511); an ambiguous
  SpellMap default raises (:629-645); an empty collection is valid (:529-531).
- Collection injection order = `_spell_id_pool` insertion order, preserved by re-sorting bucket
  unions (:288-292, :407-433): a WORLD property that the topology already records as
  `target_spell_ids` order.

## Reflection points (user objects)
- `inspect.isclass(frame)` and `frame.__name__` (:234, :326-327); `type(obj).__eq__` identity
  checks (:271-275); `id()` of bound objects and frames (:332-335, :403);
  `typing.ForwardRef.__forward_arg__`, `get_origin`, `get_args` on annotations (:155-175, :219-220).

## Python-callback points
- `frame == annotation`, `spell_frame == frame`, `spellframe == spellmap.spellframe` can invoke a
  user `__eq__` (:245, :616, :625) - on the scan path (eq-risky pools) and always on the SpellMap
  path. No user callable is invoked otherwise. Melder callbacks: `spell._add_build_details`,
  `_publish_spell_record_to_nexus`, cancellation checks (:821, :848, :986).

## World reads (the query surface, consolidated)
- One query: "all spells of this book in pool order, each as (selected_spell_id, spell_name,
  spellframe, bound object, spell_type, binding_name, resolvable, eq-safety of object and frame)".
  Everything else is local. A value-shaped pool snapshot with those columns (frames and objects as
  type refs plus an `eq_safe` bit) lets phase 3 run closed; its outputs are already rows.

## PLAIN default (identity candidate #1)
- Phase 3 never reads `default_value` (`parameter_kinds` is the only requirements read, :732).
  Remaining candidates: phase 5 blueprints and the phase 8-11 emitters.

## Contradictions
- None against the maps. Residues: "SpellCrafter" in error strings and docstrings (:65, :92, :114,
  :494, :504, :631, :641, :824, :990, :1009). `_iter_all_spells` docstring says "no scanner wrapper"
  (:125-127) while the index is a wrapper introduced later; cosmetic.

## Policy notes (recorded, not judged)
- `except AttributeError: pass` around `spell._add_build_details` "for test stubs" (:1023-1030):
  a defensive fallback on an owned contract.

## UNKNOWN (with where to look)
- Which runtime or later-phase readers use `Spell.dependency_graph` (the DAG object) versus
  `Spell.dependencies` (ids): grep `dependency_graph` under `aether/conduit/meld/`, `spell_compiler/`.
- What clears the gated/dirty state that `update_dependencies` sets on every conjure: S4 (phase 4)
  and S7 (phase 6/7); `spell_system_states.py` transition methods.
- What `_extract_collection_frame_keys` / `_extract_contract_keys` derive (frame-key sensitivity
  index): spell_system_states.py, S5.
- `dag_index.py` (768) PathRegistry/PathId/SocketRef: S6.
