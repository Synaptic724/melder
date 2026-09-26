# Survey record: phase 7 (change-control wiring)

Recorded 2026-09-26 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, task 2, step S7).
Status: COMPLETE. Read whole: `phases/compiler_phase_7.py` (265). Read by method:
`change_control_manager.py:1257-1443` (`set_revalidator`, `has_revalidator_for_conduit`,
`rebuild_component_of`, `upsert_component_of`), `:1445-1519` (`notify_spell_changed`,
`notify_provider_changed`), `:1521-1576` (`revalidate_dirty_roots`), `:1595-1625` (`is_root_dirty`),
slots `:131-135`, `:194-198`; `aether.py:2415-2454`; `dev_ops_manager.py:343-350`;
`spell_compiler.py:496-572`; `spell_compiler_system.py:522-591`;
`spellbook_creation_system.py:3212-3250`. Boundary touch, disclosed: `conduit/meld/meld.py:941-963`
(the `is_root_dirty` gate branch only) to name the production consumer of this wiring; the meld door
is another agent's lane and nothing else in `meld.py` was opened. Ranges without a file are into
`compiler_phase_7.py`.

## Entry
- Frame-wide: `CompilerPhase7.run_frame_wide(artifact, spellbook, conduit_id)` (:55-76) ->
  `_ensure_change_control_ready` (:111-185). ONE unit per conjure on the lead spell, phase name
  `change_control`, args `(spellbook, lead_spell, conduit_id)` - no cancel event is threaded
  (spellbook_creation_system.py:3234-3250); reached via `SpellCompilerSystem.run_phase_change_control`
  (spell_compiler_system.py:522-556) and `SpellCompiler.run_phase_change_control`
  (spell_compiler.py:496-533).
- Local: `run_local` (:78-109) -> `_ensure_change_control_ready_local` (:187-262), scheduled as
  `change_control_local` (spellbook_creation_system.py:2187-2189).

## Consumes (world reads)
- Lead artifact `_entire_dag_blueprint_phase5` (:37-53, :136, :212), filtered to OWNED roots by
  `CompilerPhase5()._filter_root_blueprints_to_owned(spellbook, ...)` (phase_05.md: the
  `spellbook._spells_by_id` key set). Two throwaway `CompilerPhase5()` instances are built per call
  to borrow that helper and `_get_required_spellbook_frame_name` (:132-137, :208-213).
- `spellbook._aether._get_change_control_manager(frame_name)` (:133, :209) ->
  `Aether._get_devops_manager(frame).change_control_manager` (aether.py:2415-2423): the frame-owned
  `ChangeControlManager` (CCM). Nothing else is read.

## Produces
- Nothing on the artifact. Every output is CCM state (below).

## Mutates (the hydrate obligations of phase 7)
1. `ChangeControlManager.rebuild_component_of(conduit_id, {root_id: blueprint})` (:138-141; CCM
   :1322-1375): under the CCM lock, clears and rebuilds `_component_of_by_conduit[conduit_id]:
   Dict[node_id, Set[root_id]]` from each owned blueprint's `dag.nodes.keys()` (every node maps to
   every owned root containing it; each root maps to itself), then CLEARS
   `_dirty_spells_by_conduit[conduit_id]` and `_dirty_roots_by_conduit[conduit_id]` and sets
   `_monitor_active_by_conduit[conduit_id] = False`. Value shape: `Dict[str, Set[str]]`, two
   `Set[str]`, a bool. Replayable from rows: YES - a pure function of the phase-5 blueprint node
   sets. Ordering: after phase 5; it resets dirty state on every conjure.
   Local variant `upsert_component_of` (:214-217; CCM :1377-1443): replaces memberships for the
   supplied roots only, drops nodes left without owners, removes those roots from the dirty set and
   flips monitoring off when no dirty root remains.
2. `set_revalidator(conduit_id, _revalidate_dirty_roots)` once per conduit, guarded by
   `has_revalidator_for_conduit` (:181-185, :258-262; CCM :1257-1320): stores a CLOSURE over
   `(spellbook, conduit_id)` in `_revalidate_fn_by_conduit`. The closure (:143-179; local twin
   :219-256) resolves each dirty root from `spellbook._spell_id_pool`, builds a fresh
   `SpellCompilerSystem()` and calls `run_all_phases(spellbook, spell, conduit_id, cancel_event)`,
   then `cleanup()`, and returns the roots it processed. RUNTIME-ONLY callable; not storable;
   reconstructible from `(spellbook, conduit_id)` at hydration. In the normal conjure order this
   call is a no-op: phase 5 already registered a closure of the same shape for the conduit
   (phase_05.md item 4, compiler_phase_5.py:568-615), so the guard is already True and the first
   registration lives for the conduit's lifetime.

## Consumers of the wiring (production paths)
- `is_root_dirty(conduit_id, root_id)` (CCM :1595-1625) is read by the meld gate
  (meld.py:944-958) and raises `MeldExecutionError` for a dirty root. It returns False unless
  `_monitor_active_by_conduit[conduit_id]` is True.
- Monitoring is set True in exactly one place: `notify_spell_changed` (CCM :1480; alias
  `notify_provider_changed` :1500-1519), which marks the dependent roots dirty through the
  component-of map and mirrors `mark_dependency_change()` onto each root's `SpellSystemState`
  (:1485-1498). A grep over `src/` (doc payloads excluded, quoted names included) finds NO
  production caller of either; callers exist only under `tests/` (11 files).
- `revalidate_dirty_roots(conduit_id)` (CCM :1521-1576) invokes the closure outside the lock and
  clears the roots it reports validated. It is reached only through
  `DevOpsManager.revalidate_dirty_roots` (dev_ops_manager.py:343-350) and
  `Aether._revalidate_dirty_roots` (aether.py:2425-2454); no production caller of either exists in
  `src/` (grep). CONCLUSION: as shipped, the component-of index and the revalidator are rebuilt on
  every conjure and exercised only by tests and by callers of the DevOps/Aether facades. The
  transaction-side `_default_dirty_marker` hook (CCM :244, :837) is a separate dirty path (S10).

## Holds (classified)
- Blueprint objects, read for `dag.nodes.keys()` only -> VALUE (node ids). CCM maps -> VALUES.
- The revalidator closure -> RUNTIME-ONLY (holds the live `spellbook`).

## Reflection points (user objects)
- None.

## Python-callback points
- None in-phase. The registered closure is Melder code, invoked later by `revalidate_dirty_roots`.

## World reads
- `spellbook._spells_by_id` keys (owned scope), `spellbook._aether`, the frame name.

## Snapshot relevance
- Per-conduit tier: the component-of rows are derivable from the owned phase-5 blueprint rows, so a
  hydrate can replay `rebuild_component_of` from rows or recompute it after phase 5 is hydrated; the
  revalidator needs no row, only one `set_revalidator` call from `(spellbook, conduit_id)`.
- Phase 5 and phase 7 perform the same two writes; `rebuild_component_of` runs twice per conjure
  (compiler_phase_5.py:556-566, then :138-141 here), each clearing dirty state. A hydrator needs one
  pass; the design story can fold phase 7 into the phase-5 hydrate (the epic's "emit-and-wire, 11
  absorbing 7" reading).
- D5 input: `notify_spell_changed` is the only path that arms the meld gate and no shipped path
  calls it; S10 must establish which production path (if any) produces dirty roots
  (`_default_dirty_marker`, `SpellSystemStates.mark_*_dirty`, transfer's `_mark_lineage_dirty`).

## Contradictions
- CONFLICT candidate for summary.md: `src_architecture.md:485-486` ("ChangeControl track ... dirty
  roots used by Meld to gate execution and trigger revalidation") and the "Sequence: Change-Control
  Revalidation" (:768-773) describe a live loop; source shows the loop is mechanically present but
  armed only by `notify_spell_changed`, which no shipped call path invokes. Owner ruling needed:
  intended public DevOps API (document fine) or dead wiring (document overstates).
- Phase 7 as listed in the maps duplicates work phase 5 already does (see above).
- Facade docstrings name `spell` and `cancel_event` parameters the signatures do not carry
  (spell_compiler.py:514-524; spell_compiler_system.py:541-548).
- Docstring residue: `SpellCrafter` (:30).

## UNKNOWN (with where to look)
- Whether the phase-5 and phase-7 closures differ in any line: diff compiler_phase_5.py:568-609
  against compiler_phase_7.py:143-179 (both call `run_all_phases`; not diffed line by line).
- The production producer of dirty roots and the RiskManager interplay: S10.
