# Survey record: resolution driver - the full-hit load path (D6)

Recorded 2026-09-26 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, task 2, step S8).
Status: COMPLETE. Read by function: `spellbook_creation_system.py:226-262` (conjure: classify ->
prepare -> enforce), `:319-347` (`_prepare_resolution_for_conjure`), `:349-409`
(`_enforce_conduit_resolution_valid`), `:520-573` (`_load_cached_spell_payloads_for_conjure`),
`:576-655` (`_publish_cached_creation_context_for_spell`), `:657-759` (legacy executor rebuild),
`:960-1018` (post-construction finalize), `:1021-1057` (`_load_cached_creation_contexts_for_conjure`),
`:1060-1101` (`_stage_spell_payloads_at_conjure_end`), `:1708-1786`
(`_register_conduit_resolution_phases`), `:1996-2015` (`_conduit_resolution_has_errors`);
`codegen_creation_system/shared_assets/manifest_creation_cache.py` (122, whole);
`strategies/generalized/generalized_creation_cache.py:1-141`;
`strategies/generalized/hydration/generalized_binding_resolver.py:1-60`, `:153-264`;
`strategies/generalized/hydration/generalized_hydrator.py:380-422`, `:540-573`;
`codegen_creation/spell_codegen_creation_cache.py:1-34` (docstring); `dag/dag_index.py:26-150`
(`PathRegistry`). Located by grep, not read: solo and many_only hydrators (touch list below).
Earlier records cover the rest of the driver: driver.md (cache classification `:412-518`),
structural_driver.md (`:1476-1538` `run_resolution_phases_for_conduit`).

## The conjure path, in order (who runs on a full hit)
1. Structural phases 1-4 run on every conjure (structural_driver.md).
2. `_build_conjure_cache_state` classifies the cache BEFORE the conduit phases (:231-236;
   driver.md): `full_hit` when every live resolvable, non-existing-creation spell id is cached.
3. `_prepare_resolution_for_conjure` mints the conduit id (`IDBuilder.create_id()`, :339) and runs
   `run_resolution_phases_for_conduit(force_skip_plan_phases=True)` on a full hit (:237-241, :344).
   The scheduler registers `root_blueprints`, `system_validation`, `change_control` unconditionally
   and `plan_group` (8-11 fused per spell) behind `_should_skip_plan_phases` (:1743-1786): the skip
   is unconditional when forced; otherwise it samples `_conduit_resolution_has_errors` ONCE at the
   plan boundary (:1762-1773; :1996-2015 reads the phase-6 registry bucket `has_errors()`).
   So phases 5, 6 and 7 RUN on a full hit; only 8-11 are skipped.
4. `_enforce_conduit_resolution_valid` runs only when NOT a full hit (:242-250): it reads the
   phase-6 registry bucket (`get_conduit_resolution_state(conduit_id).has_errors()`,
   `list_diagnostics()`), collects ERROR diagnostics' `spell_id`s (fallback: every pool spell) and
   raises `SpellbookValidationError(offending spells)` (:377-409). The full hit trusts the verdict
   enforced when the bundle was built.
5. After the Conduit is constructed and ownership is wired into spells (`define_conduit_into_spells`,
   :990-993), a full hit calls `_load_cached_creation_contexts_for_conjure` (:994-998); `mixed` and
   `full_miss` instead stage payloads for the missing spells (:999-1006, :1060-1101) and every path
   emits the conduit cache file once (:1007-1009).

## What the full-hit load reads and writes (:1021-1057, :520-573)
- Reads `cache_state["caching_system"]` and `cache_state["live_spell_ids"]`; intersects them with
  `spellbook._spell_id_pool.keys()` and `caching_system.cached_spell_ids` (:553-557); per spell
  `caching_system.get_spell_payload(spell_id)` (the `.melc` payload, S9).
- Per loaded spell: publishes a `CreationContext` (below), then sets `spell.resolution_complete =
  True`, `spell.resolution_required = False` (:570-571). Any exception degrades that spell silently
  (`except Exception: continue`, :568-569); spells not loaded get `resolution_required = True` and
  `spell._door_epoch += 1` (:1048-1057) so meld re-runs 8-11 for them (JIT path).
- Docstring contract (:1029-1033): must run after ownership wiring (`spell._owner_creations`) and
  after phases 1-7 "so the phase-5 path registry is live".

## Publish dispatch (:576-655) - three payload shapes
- Manifest-first package (`{"package_version": 2, "family_id", "spell_id", "manifest"}`,
  manifest_creation_cache.py:1-25, :70-82): `load_creation_context_lazy` dispatches on family to
  generalized / solo / many_only (:85-122). The generalized loader (generalized_creation_cache.py:
  86-141) validates the manifest, reads `spell._creation_context_factory` and
  `_resolve_runtime_gate_for_spell(spell)` (creation gate: RUNTIME), builds three COLD doors from
  `(manifest, spell)` and publishes `CreationContext.load_cached(spell, spell._dynamic_environment,
  gate, gate_index_id, doors...)`. ZERO phase 1-7 reads at conjure; hydration happens on the first
  meld (:93-104).
- Legacy `CodeType` payload (:626-643): rebuilds both executors from code objects with closure cells
  over `spell`, `spell_id`, the error type and the override runtime (:657-759) - phase 1-7 free at
  load; the override runtime builds lazily on first override meld (:715-739).
- Non-mapping / other mapping payloads: `spell_codegen_creation_cache.load_creation_context`
  (:613-625, :644-655), whose docstring states it rebuilds executors "against the live Spellbook +
  live phase-5 path registry" (`artifact._root_blueprint_phase5`; spell_codegen_creation_cache.py:
  16-34).

## D6 - what hydration consumes from phase 1-7 objects (the answer)
The hydration seam is one class per family, and it names exactly two live inputs
(generalized_binding_resolver.py:1-18, :155-171): "A binding resolver is the single seam where
executor hydration touches live runtime state. Everything else the hydrator consumes is manifest
data."
1. `spellbook._spell_id_pool[spell_id]` for every step spell id in the manifest
   (`SpellbookBindingResolver.resolve_spell`, :208-233; `_resolve_spell_lookup`,
   generalized_hydrator.py:409-422): live `Spell` objects (BIND-time objects, not phase products).
2. `spell._compiler_artifact._root_blueprint_phase5.path_registry` (`resolve_path_registry`,
   :235-264; used at generalized_hydrator.py:405 for the override runtime): the PHASE-5 blueprint's
   `PathRegistry`. A missing blueprint RAISES ("a hydration without phases 1-7 is a sequencing bug",
   :163-164, :259-263). The many_only hydrator reads the same two things
   (many_only_hydrator.py:359-366, :376-391, located by grep); the solo hydrator has no such touch
   (grep: none).
3. Manifest rows carry phase-5 PATH IDS as ints (`SpellOverrideTargetRef(param_path_id=row[1])`,
   generalized_hydrator.py:425-440), so the live registry must reproduce the exact id assignment
   of the build. `PathRegistry` assigns ids sequentially in insertion order (`new_id =
   len(self._segments)`, dag_index.py:118-150) over `(parent_id, segment)` pairs; phase 5 interns
   paths by sorted BFS (phase_05.md), so the assignment is deterministic and the registry is a
   value table: rows of `(id, parent_id, segment)`.
4. Configuration: `spellbook.get_configuration().get_property(
   "generalized_singleton_specialization_enabled")` once per hydration (generalized_hydrator.py:
   540-573; best-effort read).
5. Ownership wiring: `spell._owner_creations` (runtime; set by conjure before the load, :1032).
NOT consumed by the load or hydration: phase 1-4 artifacts (reset anyway, structural_driver.md),
`_spell_system_index_phase5`, `_entire_dag_blueprint_phase5`, phase-6 verdict objects,
`_validated_phase6`, component-of or revalidator state (grep over the cache-load modules and the
hydration package: none of these names appear).

## The registry rows the full hit still depends on (indirect D6)
- The plan-skip decision on a NON-forced path reads the phase-6 bucket (:1762-1773); the forced
  full-hit skip does not.
- Meld-time gating reads registry validity, not artifacts: the structural verdict on
  `SpellSystemState` (phases 3-4 writes) and the per-conduit verdict on `ConduitResolutionState`
  (phase 6 writes); UNKNOWN/GATED triggers a local rerun (architecture "Sequence: Meld-Time
  Validation Gate", :684-692; the meld door itself is another agent's lane and was not read).
  A snapshot that hydrates 1-7 must therefore restore BOTH registry tiers, or the first meld re-runs
  the phases it skipped.
- `_is_broken` per spell (phase 4) is read by the conjure driver (`spell.is_broken`, :1954, S5) and
  by phase 6; it persists across the post-pass reset (phase_06.md).

## Holds (classified) on this path
- `cache_state`: a dict of value fields plus a reference to the Spellbook-owned `CachingSystem`
  (RUNTIME; S9). Payloads: marshal-safe dicts (manifest families) or one `CodeType` (legacy).
- Published `CreationContext`: RUNTIME lane object (doors, gate, dynamic environment); out of the
  survey's boundary beyond its constructor arguments.
- Spell flags written: `resolution_complete`, `resolution_required`, `_door_epoch` (ints/bools).

## Contradictions
- None against the maps: `src_architecture.md:646-670` (conjure sequence: classification before
  the conduit phases; full hit skips only 8-11; verdict not re-enforced) matches source.
- `_prepare_resolution_for_conjure`'s docstring omits its `force_skip_plan_phases` parameter
  (:325-337) and the JIT comment at :1725-1726 calls the forced skip "deferred/JIT conjure mode"
  while the only caller passes it on the full-hit path (:240) - naming residue, not behaviour.

## UNKNOWN (with where to look)
- `caching_system.get_spell_payload` / `cached_spell_ids` shapes and the envelope: S9
  (`utilities/caching_system/caching_system.py`).
- `CreationContext.load_cached` internals and the first-meld hydration trigger
  (`generalized_hydrator.build_lazy_creation_executors`): runtime lane; read only if the snapshot
  design needs to move hydration earlier.
- Whether `spell._creation_context_factory` and the creation gate exist before the cached load on
  a restored world (crystallizer restore conjures through the public path: S9/S10 note only).
