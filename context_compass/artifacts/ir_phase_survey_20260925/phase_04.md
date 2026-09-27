# Survey record: phase 4 (structural validation)

Recorded 2026-09-26 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, task 1, step S4).
Status: COMPLETE for the phase and the runner; strategies recorded by name except two read whole.
Read whole: `phases/compiler_phase_4.py` (178 lines), `validation/validation_system.py` (350),
`validation/spell_validation_context.py` (183), `validation/spell_validation_issue.py` (114),
`validation/strategies/contract_provider_presence_strategy.py` (244),
`validation/strategies/binding_resolution_cycle_strategy.py` (392). Eleven other strategies
(1,717 lines) are listed by name below and are UNKNOWN at source tier.
Ranges without a file name are into `compiler_phase_4.py`.

## Entry
- `CompilerPhase4.run(spell, artifact, spell_validator, spell_system_states, cancel_event,
  validation_pass_cache)` (:56-178); the validator is an injected `SpellValidationSystem`
  collaborator whose constructor registers 13 built-in strategies in a fixed order
  (validation_system.py:158-191); `validate_spell` runs them in registry order over one
  `SpellValidationContext` and tags issues with the strategy class name (:264-350).
- Skip rule: if `artifact._validated_phase4` is set AND the lineage state is missing or `valid`,
  return (:112-119). Because phase 3 marks the lineage gated on every conjure (phase_03.md,
  `update_dependencies`), this skip never fires inside a conjure; validation runs every time.
- Hard contract: phases 1-3 artifacts must exist or RuntimeError (:121-130).

## Consumes
- `artifact._requirements`, `_symbolic_graph`, `_resolution_frame` (:133-140).
- `spell.spell_index.id` -> `spell_system_states.get_by_index_id` (:115, :155).
- WORLD (through the context and strategies): `spell._spellbook` (validation_system.py:306);
  `spellbook._aetheric_frame_configuration.system_state` - the frame POSTURE decides whether a
  contract socket is an error (automatic) or a warning (dynamic)
  (contract_provider_presence_strategy.py:103-110, :139, :151-168); `spellbook._contracted_spells`
  (provider map, pass-cached as `contract_provider_map`) (:112-137); `spellbook._spell_id_pool`
  items with `spell.key`, `spell.resolvable`, `spell.requirements` (OTHER spells' phase-1 rows) and
  `spell._spell_system_states.get_local_topology(spell_index)` (OTHER spells' phase-3 topology)
  (binding_resolution_cycle_strategy.py:206-244, :140-150).
- `validation_pass_cache` (driver-owned dict; entries `contract_provider_map`,
  `binding_resolution_graph`; benign last-writer-wins) (spell_validation_context.py:50-56).

## Produces
- `SpellValidationResult(spell_id, spell_name, issues)` (validation_system.py:344-348); each
  `SpellValidationIssue` = severity ("error"|"warning"), code, message, source, details dict
  (spell_validation_issue.py:57-96). Codes seen: CONTRACT_IN_AUTOMATIC_MODE, SPELL_CONTRACT_INVALID,
  SPELL_CONTRACT_AMBIGUOUS, SPELL_CONTRACT_MISSING_PROVIDER, SPELL_CONTRACT_NON_RESOLVABLE_PROVIDER,
  BINDING_RESOLUTION_CYCLE. Details carry ids, keys, names (values) - and
  `"system_state": str(system_state)`.
- Artifact: `_validation_result_phase4`, `_validated_phase4 = True`, `_is_broken = result.has_errors`
  (:142-147).

## Mutates (the hydrate obligations of phase 4)
- On the lineage `SpellSystemState` (:153-177): broken -> `set_validity(invalid,
  validation_failed)`; otherwise `clear_dirty(time.time())` then either `set_validity(gated,
  contract_unvalidated, flags_to_add=[contract_unvalidated])` when a SPELL_CONTRACT_MISSING_PROVIDER
  issue exists, or `set_validity(valid, validation_passed, flags_to_remove=[contract_unvalidated])`.
  This is what clears the gated/dirty state phase 3 sets on every conjure.
- Nothing on the Spell, Spellbook or frame (:84-85); the context drops its references after the run
  (spell_validation_context.py:151-182) and does not clean the artifacts (`cleanup_artifacts=False`,
  validation_system.py:318).

## Holds (classified)
- Result and issue objects: VALUE-EXPRESSIBLE (strings, codes, detail dicts of ids/keys); the
  dormant export already carries "validation codes" (phase_01/driver records). Each issue and the
  result are Cleanable objects, not values.
- The context holds live Spell/Spellbook/artifact references for the duration of one validation.
- The pass caches hold value graphs: `contract_provider_map: Dict[(frame_key, binding_key),
  List[(spell_id, resolvable)]]` and `binding_resolution_graph: Dict[key, Set[key]]` - both are
  VALUE-shaped world snapshots already, built from pool truth once per pass.

## Reflection points (user objects)
- None in the phase or the runner. In the two strategies read: none (they read Melder descriptors
  and keys). Eleven strategies unread; by name, `annotation_shape_guard`, `callable_profile_hygiene`
  and `existing_creation_compatibility` are the likely reflection points -> UNKNOWN.

## Python-callback points
- None in the phase, the runner, or the two strategies read (Melder cancellation checks only).
  `frame_configuration.system_state` is read under `try/except Exception`
  (contract_provider_presence_strategy.py:107-110). Unread strategies: UNKNOWN.

## World reads (the query surface)
- Frame posture (`system_state`), the contracted-spell provider map, and the pool's per-spell
  (`key`, `resolvable`, phase-1 requirements, phase-3 topology). Phase 4 is therefore CROSS-SPELL:
  it depends on other spells' phase-1 and phase-3 outputs, which is why the driver runs it behind a
  phase barrier (binding_resolution_cycle_strategy.py:85-90).

## Determinism
- `state.clear_dirty(time.time())` writes wall-clock time into the lineage state (:164): a
  diagnostic value that must not enter any snapshot key or signature.
- Strategy order is fixed by registration (validation_system.py:179-191); issue order follows.

## Snapshot relevance
- A hydrate of phase 4 must set the lineage validity exactly as the final `set_validity` call did
  (valid / gated+contract_unvalidated / invalid) and re-mark clean; a snapshot taken from a broken
  world must not be stored (conjure raises before the conduit exists). The frame posture is a key
  input (D3): the same rows validate differently under automatic and dynamic.

## Contradictions
- `SpellValidationSystem` docstring says it is "created per validation run and cleaned up
  afterwards" (validation_system.py:74-76), while the phase receives it as an injected collaborator
  and the architecture map says the Spellbook initializes it at construction
  (src_architecture.md `Spellbook.__init__` step 3). Which is current is settled at S5.
- "SpellCrafter" residue in error strings (:128, validation_system.py:68, :71).

## Strategies registered (validation_system.py:179-191), read status
- ResolutionFramePresenceStrategy (103), DanglingDependenciesStrategy (114), SelfDependencyStrategy
  (92), CircularDependencyStrategy (165), RequiredHolesStrategy (133), DuplicateSpellNameStrategy
  (148), AnnotationShapeGuardStrategy (226), SpellMapShapeValidationStrategy (165),
  ContractProviderPresenceStrategy (244, READ), BindingResolutionCycleStrategy (392, READ),
  ParameterPolicyStrategy (195), CallableProfileHygieneStrategy (193),
  ExistingCreationCompatibilityStrategy (163). Unread ones: world reads and reflection UNKNOWN.

## UNKNOWN (with where to look)
- Which of the eleven unread strategies read the pool or reflect over user objects:
  validation/strategies/*.py (read when the design story needs the full phase-4 query surface).
- `Spell.requirements` property source (profile-borrowed or artifact): spell.py.
- `SpellSystemState.set_validity` / `clear_dirty` / `mark_dependency_change` semantics and the
  `_dirty_indexes` consumer: spell_system_state.py, spell_system_states.py (S5/S7).
- Who constructs `SpellValidationSystem` and how long it lives: spellbook.py / the driver (S5).
