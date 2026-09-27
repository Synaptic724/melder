# Survey record: structural driver (phases 1-4 orchestration and the artifact lifecycle)

Recorded 2026-09-26 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, task 1, step S5).
Status: COMPLETE. Read by function (each whole): `spellbook_creation_system.py`
`run_structural_phases` (:1359-1403), `run_post_conjure_structural_phases` (:1406-1473),
`run_resolution_phases_for_conduit` (:1476-1538), `run_resolution_phases_for_target_spell`
(:1541-1634), `run_deferred_resolution_phases_for_target_spell` (:1637-1705),
`_new_phase_scheduler` (:1789-1813), `_cleanup_phase_scheduler` (:1816-1849),
`_run_scheduler_with_phases` (:1852-1893), `_register_structural_phases` (:1896-1937),
`_collect_broken_spells` (:1940-1958), `_raise_structural_validation_error` (:1961-1993),
`cleanup_phase_artifacts_after_resolution` (:2390-2427), `_build_per_spell_phase_units`
(:2430-2480), `_chunk_spells` (:2483-2509), `_run_spell_chunk` (:2512-2547),
`_build_chunked_phase_units` (:2550-2617), `_is_spell_plan_phase_eligible` (:2620-2659), the
phase 1-4 factories (:2662-2846); `spell_compiler/spell_compiler_system.py` :1-252 and :686-822;
`spell_compiler/spell_compiler_artifact.py` :225-363. Ranges without a file name are into
`spellbook_creation_system.py`.

## Entry and shape
- `SpellbookCreationSystem.run_structural_phases(spellbook)` (:1359-1403) creates one
  `SpellCompilerSystem()` per run (owning one `SpellCompiler` and one `SpellValidationSystem` with
  its 13 strategies; spell_compiler_system.py:44-57), registers three scheduler phases, runs them,
  collects broken spells over `spellbook._spells` and raises `SpellbookValidationError`, then cleans
  the compiler system. Phase 1 and 2 are FUSED per spell ("requirements_symbolic": phase 2 reads
  only its own spell's phase-1 rows, :1913-1925, :2720-2767); "local_frame" (phase 3) keeps hard
  barriers on both sides because it reads the whole pool; "validation" (phase 4) runs behind the
  phase-3 barrier (:1913-1937).
- Every run borrows the Spellbook-owned persistent `PhaseScheduler` under
  `spellbook._phase_run_lock` (register -> `run_all_phases` -> `clear_phases`) (:1852-1893).
- Units are CHUNKED: at most `workers * multiplier` units per phase, each running its spells
  sequentially on one worker; chunk order = `spellbook._spells` dict order; unit metadata carries
  the spell ids (:2430-2617). Cancellation is checked per spell (:2542-2547).
- Per-spell front: `SpellCompilerSystem.run_phase_*` pass `spell._compiler_artifact` (the
  spell-owned artifact), `spellbook`, `spellbook._spell_system_states` and the pass caches to
  `SpellCompiler` (spell_compiler_system.py:85-252). Phase 3's `resolution_pass_cache` and
  phase 4's `validation_pass_cache` are fresh dicts per pass created in the factories
  (:2789-2806, :2833-2846).

## The artifact lifecycle (decisive for the snapshot)
- After EVERY conduit resolution pass, `cleanup_phase_artifacts_after_resolution(spellbook)`
  (:1537, :2390-2427) calls `spell._compiler_artifact.cleanup_phase_artifacts()` for every spell,
  which RESETS the phase 1-4 and phase 6 artifact group: requirements (cleaned only when not
  borrowed), symbolic graph, resolution frame, validation results 4 and 6, the shape profile, and
  `reset_phase2_5_codegen_ir` (spell_compiler_artifact.py:225-302). Phase 5 blueprints and the
  phase 8-11 state are PRESERVED (:262, :304-324).
- Consequence: the phase 1-4 OBJECTS are transient by design. What survives a pass is what the
  phases wrote elsewhere: SpellSystemStates (dependencies, topology, validity), the Spell
  (`dependency_graph`, `dependencies`, creation-context invalidation), the phase-5 blueprint on the
  artifact, and the change-control registrations (S7). A structural snapshot therefore hydrates
  REGISTRY STATE, not artifact objects, for phases 1-4 - unless phases 5-7 read the 1-4 artifacts
  during the same pass (S6/S7 decide).
- The same cleanup runs on the meld-time local paths (:1588-1591, :1625-1633, :1695-1704).
- Cost note: `cleanup_phase_artifacts_after_resolution` constructs a full `SpellCompilerSystem`
  (compiler plus validator plus 13 strategies) only to call artifact resets, then cleans it
  (:2408-2427); "Not run.", counted from source.

## Late binding and local recompile paths
- `run_post_conjure_structural_phases(spellbook, spells)` (:1406-1473): spells bound AFTER the
  conduit exists run phases 1-4 sequentially (no scheduler) through
  `SpellCompilerSystem.run_structural_phases` (spell_compiler_system.py:771-822); broken spells
  raise. Only the new spells run; other spells' phase-3 results that could now match them are
  handled by the frame-key sensitivity index (`register_local_topology`, phase_03.md) and the
  change-control revalidator (S7).
- `run_resolution_phases_for_target_spell` (:1541-1634): the meld-time gate's local path (per
  src_architecture "Meld-Time Validation Gate"): target foundational phases, then a
  `SpellbookValidationError` when the conduit resolution has errors (:1584-1598), then target plan
  phases; missing-dependency `PhaseExecutionError`s are converted into visibility failure records
  (:1614-1629). `run_deferred_resolution_phases_for_target_spell` (:1637-1705) runs the plan phases
  8-11 only.
- `_is_spell_plan_phase_eligible` (:2620-2659): plan phases need `resolvable`, not
  existing-creation, and a live phase-5 blueprint (`_root_blueprint_phase5 is not None`).

## Two spell maps
- Units are built over `spellbook._spells` (`dict[SpellIndex, Spell]`, "ACTIVE: index -> active
  spell") while phase 3 resolves over `spellbook._spell_id_pool` (`dict[str, Spell]`,
  "ACTIVE: spell_id -> active spell (warm pool)") (spellbook.py:330, :333). Whether the two always
  hold the same spell set is UNKNOWN (notch parks and promotes members; bind_inactive parks).

## Holds and writes at this level
- The driver holds no compile state of its own; the `SpellCompilerSystem` and pass caches die with
  the run. Writes: scheduler phase registrations (cleared per run), `spell._compiler_artifact`
  fields (through the phases), and the resets above. Broken detection reads `spell.is_broken`
  (any exception counts as broken, :1951-1958).

## Contradictions
- `SpellValidationSystem` is constructed per `SpellCompilerSystem` (per run), not by the Spellbook:
  `spellbook.py` has no reference to it (grep, 0 hits). src_architecture.md's Spellbook
  initialization step "Initializes spell registries and SpellValidationSystem" is STALE at the
  validator half; resolves phase_04.md's open contradiction. Candidate doc correction (owner
  authorized system-doc fixes).
- `SpellCompilerSystem.__init__` docstring still reads "Create a new SpellCrafter for one bound
  Spell" (spell_compiler_system.py:45-54) while the class is a per-run front over all spells.

## Policy notes (recorded, not judged)
- `getattr(compiler_system, phase_callable_attr)` dispatch by attribute name (:2470);
  `try/except AttributeError` probes on owned `spell.is_existing_creation`,
  `spell._compiler_artifact`, `_root_blueprint_phase5` (:2646-2659);
  `hasattr(self._spell_validator, "cleanup")` on an owned field (spell_compiler_system.py:80).

## UNKNOWN (with where to look)
- Whether phases 5-7 read the phase 1-4 artifacts (`_resolution_frame`, `_symbolic_graph`) during
  the pass or only SpellSystemStates: S6/S7.
- Whether `_spells` and `_spell_id_pool` can diverge in membership: spellbook.py bind/notch paths.
- What the persistent scheduler costs per run and whether `workers` follows configuration:
  utilities/synchronization/phase_scheduler.py (outside this epic; note only).
