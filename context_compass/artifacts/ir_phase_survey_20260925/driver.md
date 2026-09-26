# Survey record: compiler driver, artifact container, and the IR export seams

Recorded 2026-09-25 by fable_0 (STORY-2026-08-03-phase-pipeline-survey, tranche task 1).
Evidence tier: SOURCE, read in full unless a range is given. Paths are repo-relative.

## Entry and sequencing (spell_compiler.py, 693 lines, read whole)

- `SpellCompiler` (Cleanable) owns eleven phase objects `_phase_1.._phase_11` and forwards
  `run_phase_*` calls to them; it holds no spell-scoped state (spell_compiler.py:57-97).
- Phase 5, 6 and 7 each expose two entry points: `run_frame_wide` and `run_local`
  (spell_compiler.py:314-366, :403-490, :492-560). The local variants are the target-local
  compilation path the component map describes.
- Per-run memo dicts are threaded through phases 3, 4 and 8: `resolution_pass_cache`,
  `validation_pass_cache`, `analysis_pass_cache` (spell_compiler.py:206-214, :265-273, :562-597).
- Docstrings still name the retired `SpellCrafter` and describe phase 1 as storing
  `self._requirements` on the crafter (spell_compiler.py:100-111, :129-150). Stale; the artifact
  container is the home now. CONFLICT-lite: doc drift inside source, not a behavior claim.

## World-read surface by signature (coarse grain; bodies not yet read)

| phase | inputs beyond (spell, artifact) | evidence |
| --- | --- | --- |
| 1 requirements | none | spell_compiler.py:129-158 |
| 2 symbolic graph | none | :160-193 |
| 3 local frame | spellbook, spell_system_states, resolution_pass_cache | :195-261 |
| 4 validation | spell_validator, spell_system_states, validation_pass_cache | :263-312 |
| 5 root blueprints | spellbook, spell_system_states, conduit_id | :314-366, :367-401 |
| 6 system validation | spellbook, spell_system_states, conduit_id | :403-490 |
| 7 change control | spellbook, conduit_id (no cancel token) | :492-560 |
| 8 occurrence plan | spellbook, spell_system_states, analysis_pass_cache | :562-597 |
| 9 injection plan | none | :599-610 |
| 10 patch maps | none | :612-623 |
| 11 execution plan | spellbook | :625-660 |

Reading: phases 1, 2, 9 and 10 are closed over (spell, artifact) at the signature level; phases
3-8 and 11 read the live world. Docstrings state phase 3 stores the local DAG on the Spell via
`Spell._add_build_details` and registers into SpellSystemStates (:239-252), and phase 4 updates
global structural validity (:284-292) - runtime mutation points to confirm in the bodies.

## Artifact container (spell_compiler_artifact.py, 398 lines, read whole)

- 27 slots plus an RLock (spell_compiler_artifact.py:78-108). Phase outputs are OBJECTS, each
  Cleanable: `_requirements`, `_symbolic_graph`, `_resolution_frame`, two validation results,
  `_root_blueprint_phase5`, `_spell_system_index_phase5`, `_entire_dag_blueprint_phase5`
  (dict of blueprints), four occurrence analyses, `_spell_codegen_model/_plan/_creation`.
- Value-shaped slots: `_codegen_ir: Optional[Dict[str, Any]]`, `_phase8_11_codegen_ir_dirty`,
  `_occurrence_analysis_input_signature: Optional[str]`, `_occurrence_analysis_fast_key: Tuple`,
  `_requirements_shape_profile_phase1: Optional[Dict]` (:130-146).
- `_requirements_borrowed`: phase-1 requirements can be BORROWED from "the spell's bind-time
  resolution profile", which owns disposal (:120-124). Bind already produces requirements in
  some cases. Level-0 lead: `profiles/resolution_profile.py` (UNKNOWN until read).
- `reset_phase_artifacts` clears phases 1-4 and 6 objects and calls
  `SharedCompilerExecutions.reset_phase2_5_codegen_ir`; phase-5+ artifacts survive (:226-243).
  `clear_phase5_artifacts` drops 5 and everything after it (:302-320).

## The IR export seams (phases/shared_compiler_executions.py, 1516 lines; ranges read: 1-400,
## 400-640, 1018-1100, 1278-1516)

- `ensure_codegen_ir` allocates `{"phase2_5": {}, "phase8_11": {}, "signatures": {}}` on the
  artifact (:34-57).
- `capture_phase2_5_codegen_ir` exports VALUE-ONLY rows for phases 2-5: symbolic dependency
  tuples (param, position, di_shape name, optional, collection, contract key), local ordered node
  ids, dependency ids, phase-4 validated/broken flags and issue codes, phase-5 root spell/lineage
  ids, ordered node ids, socket rows `(node_id, param_name, param_path_id, socket_kind)`, DAG edge
  rows `(parent, child, param_name, socket_kind)`, index spell ids; and a SHA256 signature over all
  of it (:266-376). Row builders explicitly avoid leaking live socket objects (:166-263).
- DORMANT BY DESIGN: compiler_phase_2.py:179-184 records that the eager capture "had no production
  readers" and was removed, and that the helper "remains ... as the seam for a future incremental
  recompile path; call it on demand if that path materializes."
- `capture_phase8_11_codegen_ir` is a DIGEST (root ids, counts, strategy ids, executor signature),
  not plan content (:1360-1450). Plan content is in `build_phase11_variant_ir_payload`: step rows
  plus the transient schema, each signed (:1278-1345).
- The fast transient plan is a 40-slot tuple: step_count, root_step_index, call targets (slot 2,
  objects, DROPPED from the schema), call_modes, and dependency index arrays dep1..dep8h. The
  schema "contains only ints and tuples of ints" (:503-565). This is an interpretable index-array
  plan with the hydration handles already factored out.
- Step rows (`build_phase11_step_ir_row`, :1018-1100) carry instance_key, spell id, existence,
  dependency resolution order, override metadata, contract payload items, lock hints, disposal
  method names - primitives/tuples only, except values frozen by `freeze_phase11_schema_value`.
- CONSUMED, NOT JUST EXPORTED: phase-11 codegen creation reads the step rows
  (`CodegenCreationSchemaHelpers.get_phase11_step_ir_rows`, memoized on the plan because "Phase-11
  build, conjure-end cache export, override specialization, and the family manifest each rowified
  the same immutable plan steps independently (up to 4x per lane on a cold pass)")
  (codegen_creation_schema_helpers.py:300-345).

## Hashing infrastructure and hazards

- `hash_codegen_signature` = SHA256 over `serialize_codegen_signature_part` bytes with a `|`
  separator; typed one-byte tags for scalars; containers via `pickle.dumps(protocol=5)`; `repr`
  fallback (:60-137).
- HAZARD (HYPOTHESIS): `set`/`frozenset` parts are pickled in iteration order, which is
  hash-seed dependent for str members; a set reaching the serializer unsorted yields a per-process
  signature. `freeze_phase11_schema_value` sorts sets (:414-423) but the serializer accepts raw
  sets (:78-90). Need: audit callers for unsorted set parts.
- HAZARD (HYPOTHESIS): `freeze_phase11_schema_value` returns `repr(value)` for non-primitive
  objects (:424). Default reprs carry addresses. Step rows freeze user-supplied
  `contract_payload` values and `contract_positional_override` (:1045-1052, :1085-1087), so an
  object-valued contract payload makes the executor signature process-local: a creation-cache
  miss every process, and a false hit only if two distinct objects repr identically.
- DUPLICATION: `CodegenCreationSchemaHelpers` re-implements serialize/hash/freeze/step-row
  builders (codegen_creation_schema_helpers.py:1-60, :300-345) and several consumers import it
  under the alias `SharedCompilerExecutions`. Two serializers that must stay byte-identical or
  cache keys silently diverge.
- POLICY NOTE: `get_phase11_step_ir_rows` probes memo slots with `getattr(plan, memo_attr, None)`
  on owned plan objects (:337-345); the overlay's attribute-access rule forbids defensive
  introspection in owned code. Recorded, not judged here.

## Contradictions with documents

- The epic states "the plan is not an artifact" and "there is nothing to record". Source: the
  phase 2-5 structural rows and the phase-11 step rows plus transient index schema ARE value-only,
  signed artifacts; what is missing is a reader for 2-5 and persistence of anything but the
  executors. The epic's premise is right about 1-7 as WORKING representation and wrong that no
  serializable form exists.

## UNKNOWN (with where to look)

- What the bind-time resolution profile contains and when `_requirements_borrowed` is true:
  `profiles/resolution_profile.py`, `spell.py` (search `resolution_profile`).
- Whether phases 9 and 10 are closed in their BODIES, not just their signatures:
  `compiler_phase_9.py`, `compiler_phase_10.py`, `artifact_processor/`, `codegen_planner/`.
- Whether any set part reaches `serialize_codegen_signature_part` unsorted: grep callers of
  `hash_codegen_signature` for set-typed arguments.
- What the creation cache persists and what its key is: `utilities/caching_system/caching_system.py`,
  `spellbook_creation_system.py:_build_conjure_cache_state`.
