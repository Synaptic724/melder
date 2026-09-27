# architecture_patch

## Metadata
- Patch ID: live_contract_override_operands_2026_09_26
- Status: implemented (owner-run suites pending)
- Owner: fable_0 (cowork)
- Created: 2026-09-26T11:57:20Z
- Updated: 2026-09-26T12:42:22Z

## Patch Scope and Non-Goals
- Objective (owner ruling 2026-09-26): the values inside a `SpellContract(override=...)` payload may be
  anything and must reach the provider's constructor as LIVE meld operands - the object itself - on the
  in-process path and after a cross-process creation-cache hit alike; persisted rows never carry a payload
  VALUE that is not a scalar; the descriptor keyword `spell_override` becomes `override` on `SpellContract`
  and `SpellMap`; `SpellMap.override` (never applied today) joins the same path.
- Non-goals: no change to the meld doors, to `Spell.mutation_override`, to the override key grammar
  (PATH/UNIQUE/BROADCAST), to `caching_system.py` or the cache generation, to the override emitters and
  the targeting runtime (melder_0's design v2 S3 replaces them; the requirement is filed there), to
  phases 1-8.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| DI Descriptors and Contract Sockets (`SpellContract`, `SpellMap`) | modify | keyword and slot rename `spell_override` -> `override`; docstrings state that values are read live at meld | none |
| SpellCompiler and Validation Pipeline (phase 3 reader; phase-9 contract processor and injection spec; planner step classes) | modify | phase 9 records a value-only REF per payload entry beside the raw value; SpellMap defaults with a payload are compiled like contract defaults | descriptors |
| SpellCompiler IR seams (phase-11 row builders and signature rows) | modify | rows carry the REF for every non-scalar payload value (scalars keep today's frozen bytes) | phase-9 refs |
| Codegen creation system (no-overrides hydration of generalized, many_only and legacy families) | modify | refs are resolved to live values through the consumer's descriptor at hydration | row schema |
| Creation cache emission seam (task-4 gate) | modify | the gate is removed: every row is replayable by construction | row schema |

## Interface and Boundary Deltas
- Boundary delta 1: the phase-11 subsystem (`codegen_creation_schema_helpers.py`) imports the two
  descriptor classes from `conduit/meld/contracts/` to read a payload live; the descriptors import only
  utilities, so no cycle is introduced and the phase helper surface is not reached back into. The
  stdlib-only leaf `CodegenSignature` owns the ref shape, the scalar classifier and the row projection
  rule, so the many_only family (which must not reach the generalized helper surface) applies the same
  rule through the leaf; the generalized manifest and legacy compilers and the many_only compiler import
  the resolver from `shared_assets/codegen_creation_schema_helpers.py`.
- Interface delta 1: `SpellContract.__init__(spell=None, *, spellframe=None, binding_name=None,
  override=None)` and `SpellMap.__init__(...)` likewise; attribute `override`; `__repr__` renders
  `override=...`. No compatibility alias (owner-requested rename; overlay rule 5.15).
- Interface delta 2: a contract override REF is the value-only tuple
  `("__contract_override__", consumer_spell_id, consumer_param_name, key)` where `key` is the kwarg name
  (str) or the positional index (int). `SpellOccurrenceContractAnalysis` gains
  `contract_override_refs_by_occurrence`; `SpellInjectionInstanceSpec` and both planner step classes
  gain `contract_payload_refs` (same keys as `contract_payload`; `__args__` maps to a tuple of refs).
- Interface delta 3 (rows): `contract_payload_items` and `contract_positional_override` keep their field
  names; `CodegenSignature.project_contract_payload_entry(param, value, refs)` writes a value that is
  `None`/`bool`/`int`/`float`/`str` (or an exact tuple of those) as itself - a fixed point of every freeze
  in the compiler, so the bytes equal today's frozen bytes - and any other value as its REF; a positional
  payload projects element by element into a tuple. The generalized row/signature builders, the many_only
  helpers and the many_only manifest row builder all apply it; payload-free and scalar-payload books keep
  byte-identical rows and signatures. The phase-side legacy twin
  (`shared_compiler_executions.build_phase11_step_ir_row`, digest-only input of the artifact-local
  `_codegen_ir` export) is unchanged.
- Interface delta 4 (hydration): `CodegenCreationSchemaHelpers.resolve_contract_override_ref(ref,
  spell_lookup, descriptor_cache)`, `resolve_contract_payload_row_values(row, spell_lookup,
  descriptor_cache)` and `contract_payload_refs_from_row(row)` are the resolver surface. Three sites
  call it: `generalized_manifest_no_overrides_compiler.resolve_contract_payload_rows(rows, spell_lookup)`
  at the top of `hydrate_no_overrides_executor` and `build_specialized_no_overrides_executor` (so runtime
  rows, bindings and the generic constructor path all see live values), the generalized legacy
  `_hydrate_steps_from_rows` and the many_only `_hydrate_steps_from_rows` (adapters gain
  `contract_payload_refs`). The solo family carries no contract payloads (verified: no payload field in
  `strategies/solo/`), so it is not a site. The override lanes' row hydration is unchanged (v2 S3).
- Interface delta 5 (emission): `manifest_creation_cache.build_package` and
  `spell_codegen_creation_cache.build_package` return `Dict` again (never `None`);
  `plan_contract_payloads_are_replayable` and `spell_codegen_plan_is_replayable` are removed;
  `is_replayable_contract_payload_value` moves to the leaf (`CodegenSignature`) with the facade
  delegating; `Spellbook._emit_spell_cache` loses the `None` branch.

## Cross-Component Invariants
- Invariant 1 (identity): a non-scalar override value reaches the provider's constructor as the same
  object the descriptor holds, on the no-overrides lanes of every family, in-process and after a cache hit.
- Invariant 2 (rows): a persisted step row never contains a payload value outside the scalar set; every
  row is replayable by construction, so no emission gate is needed.
- Invariant 3 (byte-compatibility): books whose payload values are all scalars keep their executor
  signatures and rows byte-identical to today; only object/container/enum payload rows change bytes
  (they were process-local before task 2 and marker tuples after it).
- Invariant 4 (precedence): meld override > contract payload value > dependency, unchanged; the caller
  payload still replaces `Spell.mutation_override`.
- Invariant 5 (descriptor as source of truth): the value bound at meld is read from the consumer's
  descriptor at hydration time; a descriptor mutated after conjure is read as it is at hydration.

## Migration and Rollout Order
1. Rename the descriptor keyword and update the two source readers, tests and docs.
2. Phase 9 records refs; injection spec and planner steps carry them.
3. Row builders emit refs for non-scalar values; signature rows likewise.
4. Hydration resolves refs (three sites); gate removed; tests.
5. Promotion into `src_components.md` (DI descriptors block, IR seams block) at story closure.

## Rollback Strategy
- Rollback trigger: any compiler suite regression; a hydration site that cannot reach the consumer.
- Rollback steps: revert the rename, the refs plumbing and the three hydration hunks; restore the gate
  from task 4 (pure functions; no persisted-format migration exists to undo).
- Post-rollback verification: compiler suites green owner-run.

## Validation Expectations and Evidence Plan
- Validation item 1: unit - descriptor rename (constructor, repr, cleanup); ref construction; resolver
  (kwarg, positional, missing consumer, missing parameter); row builder emits refs for objects and
  frozen bytes for scalars.
- Validation item 2: component - object payload delivered by identity through the linked-contract
  fixture (`test_codegen_signature_determinism.py`, in-process, package rows carry the ref and marshal)
  and through a single-book `SpellMap` fixture (`test_spellbook_component_contract_override_operands.py`:
  in-process, and after a cross-process creation-cache full hit in a subprocess);
  `test_spellbook_component_caching_system.py` proves the object-payload spell is staged as a reference.
- Validation item 3: the strict xfail in `test_codegen_signature_determinism.py` was already removed by
  melder_1's spell-id task; the gate tests are replaced by `test_contract_override_refs.py`.
- Evidence source: owner-run `python -m pytest -q tests/unit/melder/aether/conduit/meld/contracts
  tests/unit/melder/spellbook/spell_compiler tests/component/melder/spellbook
  tests/component/melder/aether/conduit tests/integration/melder/conduit/test_conduit_integration_links_contracts.py`.
  "Not run." until reported.

## Ticket Coverage Map
- Epic: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md
- Story: tickets/stories/2026-09-26_signature_determinism_and_phase8_digest_story.md
- Task: tickets/tasks/2026-09-26_live_contract_override_operands_task.md

## Unknowns and Decision Requests
- UNKNOWN: whether any test relies on a SpellMap payload being ignored (P7 makes it live).
- DECISION: P7 (SpellMap) taken as approved on the owner's "spellmap might be similar?" plus the go-ahead.

## Context / Handoff Summary
- What changed (2026-09-26T12:42:22Z): implemented on the device tree - rename, phase-9 refs, leaf projection rule,
  three hydration sites, gate removed, tests. "Not run." until the owner reports.
- Remaining risks: hydration sites sit in files other lanes propose changes to (NOTICEs sent); the
  override lanes literalize a ref tuple where they literalized a marker tuple (objects still unusable there
  until v2 S3, scalars unchanged).
- Next entrypoint: owner-run suites; promotion into `src_components.md` at story closure.
