# Survey record: phase 6 (system validation)

Recorded 2026-09-26 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, task 2, step S7).
Status: COMPLETE. Read whole: `phases/compiler_phase_6.py` (509 lines, two chunks),
`system/spell_system_validation_system.py` (268), `system/spell_system_validation_state.py` (94),
`system/system_diagnostic.py` (165), `system/validation/strategy_base.py` (78). Read by method:
`spell_system_states.py:934-1106`, `:1343-1360`; `conduit_resolution_state.py:1-230`, `:327-386`,
`:485-604`, `:647-727`; `spell_compiler.py:441-494`; `spell_compiler_system.py:474-520`;
`spellbook_creation_system.py:3171-3209`; `missing_phase4_strategy.py:81-101`;
`spell_compiler_artifact.py:186-224`, `:280-302`. The other 22 strategies are named, not read; their
read surface below is grep-characterized and marked so. Ranges without a file are into
`compiler_phase_6.py`.

## Entry
- Frame-wide: `CompilerPhase6.run_frame_wide(artifact, spellbook, spell_system_states, conduit_id,
  cancel_event)` (:329-389). ONE unit per conjure on the lead spell (`next(iter(spellbook._spells
  .values()))`, spellbook_creation_system.py:3193-3209, phase name `system_validation`), reached via
  `SpellCompilerSystem.run_phase_system_validation` (spell_compiler_system.py:474-479: passes the
  lead's `_compiler_artifact` and `spellbook._spell_system_states`) and
  `SpellCompiler.run_phase_system_validation` (spell_compiler.py:441-447).
- Local: `run_local(spell, artifact, spellbook, spell_system_states, conduit_id, cancel_event)`
  (:391-508), scheduled as `system_validation_local` for meld-time target recompiles
  (spellbook_creation_system.py:2179-2181; driver body is S8).

## Consumes (world reads)
- Lead artifact `_spell_system_index_phase5` and `_entire_dag_blueprint_phase5` (:129-160, :373-374;
  local: :428-431) - the phase-5 outputs (phase_05.md).
- EVERY spell in `spellbook._spell_id_pool` (:364-368): `_compiler_artifact._validation_result_phase4`
  stored under its id, and `_compiler_artifact._is_broken` collected into `broken_spell_ids`.
  `_is_broken` is written by phase 4 (compiler_phase_4.py:147) and is NOT cleared by the post-pass
  reset (spell_compiler_artifact.py:296-302 clears the result object only); only artifact cleanup
  clears it (:206). The result value is never dereferenced by a strategy: the only reader is
  `missing_phase4_strategy.py:83-101`, which tests key PRESENCE (`node_id not in phase4_results`),
  so a `None` left by the S5 reset passes.
- Local path: `spell_system_states.get_local_topology_by_id(spell_id)` (spell_system_states.py:1343-1360,
  live object, no clone) and `socket.target_spell_ids` per scoped spell (:201-206), plus every
  blueprint's `dag.nodes` (:260-262), to find dependencies not visible in the pool.
- Strategies: 23 instances in a fixed order, a fresh list per run (:289-327); each gets `index`,
  `blueprints`, `phase4_results`, `broken_spell_ids`, `spell_system_states`, `spell_lookup`,
  `diagnostics`, `cancel_event` (strategy_base.py:40-52) and must not mutate inputs (:34-35).
  Grep over `system/validation/*.py` (locating, not a read): registry reads are
  `get_local_topology_by_id` (3 sites) and `get_by_spell_id` (visibility_gap_strategy.py:83); Spell
  reads are `spellframe`, `spell_name`, `binding_name` (contract_graph_cycle_strategy.py:84-86),
  `spell_index.id` (contracted_version_drift_strategy.py:82) and
  `spell._spellbook._aetheric_frame_configuration` (empty_collection_strategy.py:62, :146 - the frame
  POSTURE, a key input); no `spell_system_states.set_/mark_/record_/clear_/bulk_/update_/register_`
  call exists in any strategy.

## Produces
- `SpellSystemValidationState(is_valid, errors, warnings, nodes=index.nodes)`
  (spell_system_validation_state.py:22-43): a bool, two lists of `SystemDiagnostic`, and the phase-5
  node map by reference. `SystemDiagnostic` fields are values: code, message, severity enum,
  spell_id, root_id, source (strategy class name, auto-filled at
  spell_system_validation_system.py:178-182), details dict of tooling values
  (system_diagnostic.py:47-91).
- The validator is verdict-only: it never raises on errors; the BUILD lane enforces
  (spell_system_validation_system.py:207-218). Conjure-time enforcement is
  `SpellbookCreationSystem._enforce_conduit_resolution_valid` (spellbook_creation_system.py:349; S8).

## Mutates (the hydrate obligations of phase 6)
1. Registry, per conduit, via `SpellSystemStates` -> `ConduitResolutionState`
   (`get_or_create_conduit_resolution_state`, spell_system_states.py:960, :1016, :1041):
   `bulk_set_conduit_spell_validity(conduit_id, {every index node id: valid|invalid},
   change_reason=validation_passed|validation_failed)` (spell_system_states.py:934-961 ->
   conduit_resolution_state.py:327-385), `bulk_set_conduit_root_validity(conduit_id, {every blueprint
   root id: ...})` (:992-1017 -> :485-543), `record_conduit_diagnostics(conduit_id, diagnostics)`
   (:1019-1042 -> :548-585: signature-compared, cloned, replaces), and on success only
   `clear_conduit_dirty(conduit_id, time.time())` (:1088-1106 -> :694-714). Verdict writes mark the
   bucket dirty when any value changes and forward each changed `(conduit_id, id, validity)` to the
   attached `RiskManager.on_resolution_validity_change` callback (conduit_resolution_state.py:29-42,
   :375-385, :533-543; exceptions swallowed). The whole block is best-effort:
   `except Exception: return` (spell_system_validation_system.py:250-267).
   Value shape: `Dict[str, SpellValidity]` x2, `List[SystemDiagnostic]`, dirty bool,
   `last_validated_at` float (wall clock), `last_change_reason` enum. Replayable from rows: YES.
   Local failure branch (:461-488): the same two validity writes with `invalid` for the scoped ids
   plus the gap diagnostics; no `clear_dirty`.
2. Artifact: `_validation_result_phase6 = state` and `_validated_phase6 = True` on the lead artifact
   AND on every pool spell's artifact, the same object shared by reference (:384-389; local: scoped
   spells only, :482-487, :503-508). Reader: `Spell.validation_result_phase6` (spell.py:1237-1263);
   grep over `src/` finds no other production reader. The post-pass reset nulls the object
   (spell_compiler_artifact.py:302) but leaves `_validated_phase6` True (cleared only at :205).

## Holds (classified)
- `phase4_results` values (phase-4 result objects or None): consumed as an id set -> VALUE.
- `broken_spell_ids`: `Set[str]` -> VALUE. `spell_lookup` (live `Spell` objects): strategies read
  names, ids, frame and posture -> VALUE-EXPRESSIBLE reads.
- Verdict and diagnostics: Cleanable wrappers over values; `nodes` is a reference to the phase-5
  index map (values). Validator and strategy list: per-run transients. No lock in the phase itself.

## Reflection points (user objects)
- None. `spellframe` is read as a Melder field, not inspected.

## Python-callback points
- None in-phase. The RiskManager callback is Melder code, invoked synchronously by the registry.

## World reads
- `spellbook._spell_id_pool` whole (visibility scope); strategy reads listed above; frame posture.

## Snapshot relevance
- Phase 6 is a deterministic function of (phase-5 index and blueprints, per-spell broken flags and
  phase-4 presence, registry topologies, spell facts, frame posture); the strategy set is fixed in
  code. The per-conduit tier can recompute it from hydrated phase-5 rows and registry state, or
  hydrate the resolution rows directly: two validity maps, the diagnostics rows, the dirty flag and
  `last_validated_at`. The timestamp is the only non-deterministic value and is not a key input.
- Every artifact's `_validation_result_phase6` is nulled by the post-pass reset, so no consumer of
  the OBJECT exists by the time a later full hit runs; the registry bucket is what a hydrate must
  restore, and D6 (S8) decides whether `_validated_phase6` matters to the cache-load path.
- `_is_broken` survives the reset on every spell and feeds phase 6 on the next conjure; a per-spell
  row for the snapshot must carry it (already captured by the dormant export as `phase4_is_broken`,
  shared_compiler_executions.py:362).

## Contradictions
- None against the maps on behaviour. Docstring residue: `SpellCrafter` (:122, :143, :159).
- The verdict object is documented as frame-level (`spell_system_validation_state.py:12-14`) but is
  published into PER-CONDUIT registry buckets keyed by `conduit_id` - the registry is the durable
  form; the object is transient.

## UNKNOWN (with where to look)
- Strategy internals (22 files unread): read when the row set phase 6 needs is designed.
- `RiskManager.on_resolution_validity_change` effect: `dev_ops/risk_manager/risk_manager.py` (S10).
- `_enforce_conduit_resolution_valid` and how `_validated_phase6` is consumed on a full hit: S8.
