# Task: Make SpellContract/SpellMap override values live meld operands and rename `spell_override` to `override`

- Completed: 2026-09-26T13:14:31Z
- Summary: `spell_override` -> `override` on SpellContract/SpellMap; phase 9 records value-only refs; rows carry
  scalars or refs; the no-overrides hydration of every family binds the live object (identity proven in-process
  and across a cache full hit, owner-run); task-4 gate retired. Accepted 2026-09-26T13:14:31Z; promoted.

## Metadata
- Task ID: TASK-2026-09-26-live-contract-override-operands
- Story: STORY-2026-09-26-signature-determinism-phase8-digest
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T11:38:58Z
- Updated: 2026-09-26T13:14:31Z

## Objective
Owner ruling (2026-09-26): the values inside a `SpellContract(override=...)` payload may be anything and must
ride the normal overrides path, never a plan row or a generated literal. This task (1) renames the
descriptor keyword `spell_override` -> `override` on `SpellContract` and `SpellMap`; (2) makes phase 9 record
value-only REFERENCES to the consumer's live descriptor beside the raw payload; (3) makes the phase-11 rows
carry only those references, so every plan is deterministic and replayable and the task-4 emission gate
retires; (4) resolves the references to live values at hydration in the no-overrides lanes of the three
families (in-process lazy doors and cache loads alike), so an object payload reaches the provider's
constructor by identity; (5) files the overrides-lane binding as a requirement of melder_0's override design
v2 (S3 retires those emitters); (6) optionally routes `SpellMap.override` (dead today) through the same path.

## Ticket Contract
- ENTRY_GATE: Owner confirms the Propose -> Confirm message (P1 below); patch docs exist under
  `system_docs/patches/active/live_contract_override_operands_2026_09_26/` and are linked here; NOTICEs
  sent to melder_0, melder_1, updater_0 and updater_1; the active board row routes here.
- EXECUTION_BOUNDARY: `conduit/meld/contracts/spell_contract.py` and `spell_map.py` (rename, docstrings);
  `phases/compiler_phase_3.py` (one reader hunk); `artifact_processor/strategies/
  spell_occurrence_contract_processor_strategy.py` (payload refs beside values; SpellMap opt-in);
  `artifact_processor/data/` and `codegen_planner/data/` step/instance data classes (one `contract_payload_refs`
  slot); `codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py` (row builder emits refs;
  resolver helper; gate helpers removed); `manifest_creation_cache.py`, `spell_codegen_creation_cache.py`,
  `spellbook.py:_emit_spell_cache` (gate removal); the no-overrides hydration/binding sites of the generalized,
  many_only and solo families (`_row_contract_value_binding`, hydrators); tests; docs. NOT in scope: the
  override emitters and the targeting runtime (v2 S3), `caching_system.py`, the meld doors, `Spell`.
- DEPENDENCIES: melder_0's design v2 (operand precedence override > contract > dependency; S3 retires the
  override emitters); melder_1's address-free fingerprint (on the device tree; the strict xfail in
  `test_codegen_signature_determinism.py` must be removed in this task); task 4 (gate to retire).
- EXIT_GATE: rename complete with every descriptor call site updated (src, tests, docs); rows carry refs only;
  an object payload is delivered by identity in-process and after a cross-process cache hit (component tests,
  owner-run); the strict xfail is gone; the emission gate is removed with its tests; patch docs promoted at
  story closure; status review.
- FAILURE_ESCALATION: CONFLICT if a hydration site is under concurrent edit (updater_0/1 proposals, melder_0
  S2); RISK if any consumer reads `contract_payload_items` for anything but hydration; BLOCKER if a family
  binds contract values in a way that cannot be resolved from the pool.

## Scope Boundaries
- In scope: the descriptor rename, phase-9 refs, row schema, resolver, no-overrides-lane bindings, gate
  removal, tests, docs, patch docs.
- Out of scope: the overrides lane (literalized values stay as today until v2 S3; requirement filed),
  `Spell.mutation_override`, the meld doors, `caching_system.py` generation numbers.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner ruling recorded on task 4 (2026-09-26); proposal P1 put to the owner; no
  edit under `src/` before confirmation and the patch docs.
- from_state: ready
- to_state: in_progress
- transition_reason: Owner confirmed P1 (2026-09-26); NOTICEs and patch docs precede any src edit.
- from_state: in_progress
- to_state: review
- transition_reason: P1-P8 complete on the task boundary (rename, refs, projection, three hydration sites,
  gate retired, tests, patch docs amended); nothing executed here ("Not run."); owner-run suites pending.
- from_state: review
- to_state: done
- transition_reason: Owner accepted tasks 1-5 and the story after the third owner-run green suite report
  ("yeah sure looks good", 2026-09-26T13:14:31Z); canonical docs promoted, patch folder archived, boards synced.

## Steps / Checklist
- [x] P1: Propose -> Confirm (files/symbols above; ref shape; lane split; SpellMap opt-in) and owner
      confirmation; NOTICEs (melder_0: v2 requirement + rename; melder_1: xfail removal; updater_0/1:
      hydration hunks).
- [x] P2: patch docs (architecture, component for the DI descriptors and the SpellCompiler IR seams,
      code_description for the resolver); consumption mapping note.
- [x] P3: rename `spell_override` -> `override` (descriptors, phase-3 reader, contract processor, tests,
      docs, `src_components.md` mentions).
- [x] P4: phase 9 records `contract_payload_refs` (`("__contract_override__", consumer_spell_id, param_name,
      key_or_index)`) beside the raw payload; shared-provider distinctness still compares values.
- [x] P5: row builder emits `contract_payload_items` from refs; gate helpers, both `build_package` gates,
      the `_emit_spell_cache` hunk and their tests removed; replayability asserted on the row builder.
- [x] P6: resolver helper on `CodegenCreationSchemaHelpers` (`resolve_contract_override_ref(ref, spell_id_pool)`)
      reading the consumer's live descriptor (FORWARDREF signature default); no-overrides-lane binding sites
      of the three families call it at hydration.
- [x] P7 (owner opt-in): SpellMap defaults with an `override` payload recorded through the same refs against
      the phase-3 dependency occurrence.
- [x] P8: tests (unit: refs, resolver, row builder; component: object payload by identity in-process and
      across a cache hit; xfail removed); docstring ritual; notes; task -> review with "Not run.".
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The rename; phase-9 refs; ref-only rows; the resolver and its no-overrides-lane bindings; gate removal;
  tests; patch docs; the v2 requirement filed with melder_0.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/contracts/spell_contract.py
- src/melder/aether/conduit/meld/contracts/spell_map.py
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py
- src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py
- src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py
- src/melder/aether/spellbook/spell_compiler/codegen_planner/data/ (step data classes: refs slot)
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/manifest_creation_cache.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py
- src/melder/aether/spellbook/spellbook.py (`_emit_spell_cache` gate hunk reverted)
- no-overrides hydration sites: generalized_manifest_no_overrides_compiler.py, generalized_hydrator.py,
  many_only_no_overrides_codegen_creation_compiler.py / many_only_hydrator.py, the solo family equivalent
- tests (unit + component); docs; system_docs/src_components.md (at closure)

## Validation
- Not run. (VM interpreter is 3.10 against a 3.14 floor.)
- Owner-run 2026-09-26 (3.14.7t): refs unit file 49 passed; component trio 24 passed + cross-process probe failed
  (probe fixed); compiler unit suites 439 passed + 23 test-double drift failures (fixed); broad run 1412 passed,
  1 skipped, 1 failed (same probe). Second run (after the fixes): 49 passed; 24 passed + 1 failed (the probe,
  `full_hit` False / identity True); 462 passed; 1412 passed, 1 skipped, 1 failed (same probe). Probe rewritten
  (two subprocess probes, 13:06Z). Third run: all four commands passed (owner report 13:08Z, counts not supplied).
- Recommended commands (owner-run, 3.14t):
  - `python -m pytest -q tests/unit/melder/spellbook/spell_compiler/shared_assets/test_contract_override_refs.py`
  - `python -m pytest -q tests/component/melder/spellbook/test_spellbook_component_contract_override_operands.py tests/component/melder/spellbook/test_codegen_signature_determinism.py tests/component/melder/spellbook/test_spellbook_component_caching_system.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/contracts tests/unit/melder/spellbook/spell_compiler`
  - `python -m pytest -q tests/component/melder/spellbook tests/component/melder/aether/conduit tests/integration/melder/conduit/test_conduit_integration_links_contracts.py`

## Risks / Rollback Notes
- Rollback: revert the rename and the refs; rows go back to frozen values and the gate returns.
- Signature bytes change only for spells whose rows carried payload values (refs replace values): those
  spells rebuild once; payload-free books keep their bytes (no generation bump).
- The overrides lane keeps today's literalized values until v2 S3: an object payload melded WITH caller
  overrides is still mangled there (documented; same as today; no regression).

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No edit under `src/` before the owner confirms the file/symbol proposal and the patch docs exist
      (one P5 hunk was written after a compaction and before re-onboarding; disclosed to the owner).
- [x] No compatibility alias for the renamed keyword unless the owner asks (overlay 5.15).

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed) - patch docs amended; `src_components.md` promotion at closure
- [x] Validation status recorded ("Not run.")
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/live_contract_override_operands_2026_09_26/
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: contract override refs; live operands; descriptor rename; emission gate retirement.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T11:38:58Z
  TYPE: PLAN
  CLAIM: Design (P1). Today the phase-9 contract processor reads the consumer's live descriptor, normalizes
    the payload and records VALUES against the provider occurrence; the injection processor turns the keys
    into `kind="contract"` operands (override > contract > dependency); the row builder freezes the values
    into `contract_payload_items`; the no-overrides manifest lanes bind those row values as constructor
    kwargs (in-process lazy doors and cache loads); the overrides emitters literalize them into source.
    Change: phase 9 also records a value-only REF per payload entry, `("__contract_override__",
    consumer_spell_id, param_name, key_or_index)`; rows carry refs only (freeze fixed points, so every plan
    is replayable and the task-4 gate is dead); at hydration a resolver reads the consumer's live descriptor
    from the pool (`inspect.signature(spell.spell, FORWARDREF).parameters[param].default.override`) and
    binds the VALUE - the object itself, by identity - into `step_contract_values` for the no-overrides
    lanes of all three families; the legacy plan compiler and the overrides emitters keep binding the raw
    in-process values exactly as today (the overrides lane stays literalized until v2 S3 replaces it with
    literal reads of live operands). `SpellMap.override` (dead today) can join by recording refs against the
    phase-3 dependency occurrence (P7, owner opt-in). Fingerprint: melder_1's address-free
    `init_signature` hashing makes the consumer's spell id process-stable, so the strict xfail goes.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:126-260
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:174-360
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:433-451
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:960-1037
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1348-1400
  - src/melder/aether/spellbook/bind/bind.py:892-1044
  - artifacts/melder_override_design_20260926/design_v2.md:96-135
  IMPACT: Objects reach the provider by identity on the common lane in-process and from the cache; rows
    are a hash surface again; no generation bump; the overrides lane is unchanged until v2 S3.
  NEXT: Owner confirms P1 (and P7 opt-in); then P2 patch docs and the NOTICEs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T11:49:59Z
  TYPE: DECISION
  CLAIM: Owner confirmed P1 ("ok cool continue finish off what your doing", 2026-09-26). P7 (SpellMap) is
    taken as approved on the owner's earlier "spellmap might be similar?" plus this go-ahead; it is the
    smallest additive change (record refs for SpellMap defaults against the phase-3 dependency
    occurrence) and is reversible by owner ruling. Order: NOTICEs, patch docs (P2), then P3-P8.
  EVIDENCE:
  - tickets/tasks/2026-09-26_live_contract_override_operands_task.md
  IMPACT: Task moves to in_progress; src edits begin only after the patch docs exist and are linked.
  NEXT: Send the four NOTICEs; write the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T11:57:47Z
  TYPE: FACT
  CLAIM: P2 done: three patch docs under `system_docs/patches/active/live_contract_override_operands_2026_09_26/`.
    Consumption mapping (patch section -> implementation step -> validation): architecture Interface delta 1
    (rename) -> P3 -> descriptor unit tests; Interface delta 2 (refs on analysis/spec/steps) -> P4 -> ref unit
    tests; Interface delta 3 (rows: ref for non-scalar, frozen scalar otherwise) -> P5 -> row-builder tests
    and the byte-compatibility oracle; Interface delta 4 (resolver + three hydration sites) -> P6 ->
    component identity tests (in-process, cache hit); Interface delta 5 (gate removed) -> P5 -> gate tests
    removed; P7 (SpellMap) -> phase-9 hunk -> a component test that a SpellMap payload is applied.
    Design refinement recorded from the reads: rows keep VALUES for scalars (byte-identical to today) and
    carry refs only for non-scalar values, so the override lanes (untouched) see scalars exactly as today
    and objects as a ref tuple instead of a marker tuple (equally unusable, no regression). Resolution
    points: `_row_contract_value_binding`/positional bindings in the generalized manifest compiler
    (:949-966, :1028-1035; serves lazy doors, cache loads and the specializer), the generalized legacy
    `_hydrate_steps_from_rows` (:309-400) and the many_only `_hydrate_steps_from_rows` (:425-500, the
    entry for its manifest hydrator too). `build_runtime_rows` and the four override-lane copies stay.
  EVIDENCE:
  - system_docs/patches/active/live_contract_override_operands_2026_09_26/architecture_patch.md
  - system_docs/patches/active/live_contract_override_operands_2026_09_26/component_patch_spell_compiler.md
  - system_docs/patches/active/live_contract_override_operands_2026_09_26/code_description_patch_contract_override_resolver.md
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:785-830
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:949-1037
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:309-400
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:425-500
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:268-425
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:208-240
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_runtime_rows.py:186-264
  IMPACT: Scalar-payload and payload-free books keep every byte; the change is confined to object
    payloads and to three hydration sites; the patch gate is satisfied.
  NEXT: P3: rename in the two descriptors, phase 3 and the contract processor; then tests and docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:22:59Z
  TYPE: FACT
  CLAIM: P3 and P4 landed on the device tree; P5 is half done (not run). P3: `SpellContract` and `SpellMap`
    carry slot/kwarg/attribute `override` (:117/:126/:197 and :119/:128/:202; `__repr__` :343/:350; Args
    docstrings state values may be any object, read live at hydration, provider receives it by identity);
    phase 3 reads `spellmap_default.override` (:905); the contract processor reads `contract.override`;
    tests renamed (contracts unit files, `contract_classes.py`, strategy migrations, determinism component,
    links integration, override-required component). Meld/ConduitMeld `spell_override` kwargs, the ACL
    ruleset name and the targeting module names are NOT renamed (unrelated). P4: leaf
    `CodegenSignature.build_contract_override_ref`/`is_contract_override_ref` (:67-124);
    `SpellOccurrenceContractAnalysis.contract_override_refs_by_occurrence` (required kwarg :33, cleanup
    :81-84); the contract processor builds refs beside values (`_build_override_payload_refs`, SpellMap
    defaults via `_iter_spell_map_defaults` against the phase-3 dependency occurrence, P7) and passes the
    map at :85-97; the injection processor resolves the payload's occurrence and clones its refs into
    `SpellInjectionInstanceSpec.contract_payload_refs` (:203-222, :306; slot :95-129, cleanup :273-275);
    both planner steps carry `contract_payload_refs` (generalized :109/:148/:234/:389-399, builders
    :1257/:1619; many_only :80/:101/:163/:236-240, builder :1074). P5 so far (this file edit was made
    after the compaction and BEFORE re-onboarding; disclosed to the owner): schema helpers gained
    `freeze_contract_payload_entry` (:154), `resolve_contract_override_ref` (:205),
    `resolve_contract_payload_row_values` (:292); `build_phase11_step_ir_row` (:530) and the signature
    row builder (:628) emit a frozen scalar or the ref per entry; `plan_contract_payloads_are_replayable`
    and `spell_codegen_plan_is_replayable` are removed. Imports: the helpers now import the two
    descriptors, which import utilities only - no cycle. Two unit tests construct the analysis without
    the new required kwarg (`test_spell_artifact_processor_data_migrations.py:71`,
    `test_spell_strategy_migrations.py:270`): P8 adds `contract_override_refs_by_occurrence={}`.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:117-197
  - src/melder/aether/conduit/meld/contracts/spell_map.py:119-202
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:905-905
  - src/melder/aether/spellbook/spell_compiler/shared_assets/codegen_signature.py:67-124
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_occurrence_contract_analysis.py:20-84
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:54-178
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:180-290
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:174-360
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:95-129
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1240-1265
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:1060-1080
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:108-330
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:530-686
  - tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_data_migrations.py:71-81
  - tests/unit/melder/spellbook/spell_compiler/test_spell_strategy_migrations.py:270-280
  IMPACT: Phase 9 through the row builders now carries refs; the gate call sites and the three hydration
    sites are the remaining src work (P5 tail, P6), then P8 tests and docs.
  NEXT: Consume the mailbox (M0-20, M1-13, M0-22), then finish P5: many_only row builders, both
    `build_package` gates, `_emit_spell_cache`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:22:59Z
  TYPE: FACT
  CLAIM: Mailbox consumed. M0-20 (melder_0): override lane S1 adds a phase-9 processor strategy
    (`spell_site_graph_processor`) and a model slot, no emitter/cache change; S2/S3 will touch phase 10/11
    emitters, family manifests and cache generation 12 with a NOTICE before shared files. M1-13
    (melder_1): the strict xfail in `test_codegen_signature_determinism.py` is already removed (a
    'Formerly xfail(strict=True)' comment at :498); this task removes nothing there and rebases on the
    device copy. M0-22 (melder_0, 12:07:17Z): S1 applied to `spell_codegen_model.py` and
    `spell_artifact_processor_strategy_builder.py` plus 3 new src and 3 new test files (anchored edits;
    re-read before editing those two); it also reported phase 9 failing every conjure because the
    contract processor did not yet pass `contract_override_refs_by_occurrence`. Verified on disk: the
    processor passes it (:85-97, file mtime 12:03:07Z, before the message), so the report describes the
    window between the analysis edit (12:00:49Z) and the processor edit; no src action needed.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:54-100
  - tickets/tasks/2026-09-26_build_site_graph_and_override_key_resolver_task.md
  - tickets/tasks/completed/2026-09-26_stabilize_function_spell_ids_across_processes_task.md
  IMPACT: No file collision with S1 (disjoint files); the xfail item drops from P8; the 12:00-12:03 window
    is the only time the tree could not conjure, and it is closed.
  NEXT: Finish P5 (many_only row builders, gate call sites).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T12:44:45Z
  TYPE: FACT
  CLAIM: P5, P6 and P8 landed on the device tree (not run). Design refinement while implementing: the
    scalar classifier and the row projection rule moved into the stdlib-only leaf
    (`CodegenSignature.is_replayable_contract_payload_value` :127, `project_contract_payload_entry` :171)
    because the many_only family must not import the generalized helper surface; a replayable value is
    written AS ITSELF (every freeze returns it unchanged, so scalar rows keep their bytes) and the facade
    delegates (:108, :129). Row builders using it: generalized `build_phase11_step_ir_row` :524 and the
    signature row :622; many_only helpers :202/:215/:260/:275; many_only manifest row :169/:192. Gate
    removed: both `build_package`s return `Dict` (manifest :40, legacy :101); `_emit_spell_cache` binds
    the payload unconditionally (:1026); `plan_contract_payloads_are_replayable` and
    `spell_codegen_plan_is_replayable` are gone. Resolver surface on the facade: `resolve_contract_override_ref`
    :151, `resolve_contract_payload_row_values` :238, `contract_payload_refs_from_row` :278. Hydration
    sites: the generalized manifest compiler resolves the ROWS once at both entry points
    (`resolve_contract_payload_rows` :985, called :138 and :1509) so runtime rows, bindings and the generic
    `_construct_spell_instance` path all see live values (resolving only the bindings would have left the
    generic path, taken for a non-sequence positional payload, with refs); the generalized legacy
    `_hydrate_steps_from_rows` :312 (:390, :414) and the many_only one :428 (:495, :518) resolve per row
    and give the adapter `contract_payload_refs`. Solo carries no payload field (grep of `strategies/solo/`)
    and is not a site. Unchanged by design: the four override-lane row copies, `build_runtime_rows`, and
    the phase-side twin `shared_compiler_executions.build_phase11_step_ir_row` (digest-only input of the
    artifact-local `_codegen_ir`). No generation bump: gen-12 bundles were written after task 4's gate, so
    none carries an object-payload row; scalar rows are byte-identical. Tests: unit
    `test_contract_override_refs.py` (renamed from the gate file; classifier, projection, resolver
    failures, refs-from-row, both families' row builders, both package builders); component
    `test_codegen_signature_determinism.py` fixture now asserts `instance.service.marker is PAYLOAD_MARKER`
    and `test_cache_package_carries_a_reference_for_an_object_payload` (:621) checks the packaged row
    carries the ref and marshals; `test_spellbook_component_caching_system.py` :639 stages an object-payload
    SpellMap spell as a reference and melds by identity; new
    `test_spellbook_component_contract_override_operands.py` (227 lines): in-process identity and a
    cross-process creation-cache full hit (subprocess proves phases 8-11 skipped, bundle untouched,
    provider holds that process's payload object). Two analysis constructors in unit tests gained the
    required kwarg. Patch docs amended to the implemented shape (status implemented).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/shared_assets/codegen_signature.py:127-258
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:108-330
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:524-680
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_helpers.py:180-285
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/manifest/many_only_manifest.py:145-200
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/manifest_creation_cache.py:40-80
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:101-140
  - src/melder/aether/spellbook/spellbook.py:949-1028
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:107-185
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:985-1110
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:312-420
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:428-525
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_contract_override_refs.py:1-438
  - tests/component/melder/spellbook/test_spellbook_component_contract_override_operands.py:1-227
  - tests/component/melder/spellbook/test_codegen_signature_determinism.py:274-365
  - tests/component/melder/spellbook/test_codegen_signature_determinism.py:590-655
  - tests/component/melder/spellbook/test_spellbook_component_caching_system.py:600-675
  - system_docs/patches/active/live_contract_override_operands_2026_09_26/architecture_patch.md
  IMPACT: Object payloads reach the provider by identity on every no-overrides lane, in-process and from
    the cache; every plan packages; scalar books keep their bytes; the task-4 gate is retired.
  NEXT: Task -> review; owner runs the suites under Validation; promotion into `src_components.md` (DI
    descriptors block incl. the rename, IR seams block) at story closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:47:03Z
  TYPE: FACT
  CLAIM: Mailbox M0-24 (melder_0, 12:36:41Z) consumed: S3a replaces `execute_with_overrides` at four sites and
    will touch only `generalized_hydrator._hydrate_overrides_runtime` (anchored, after a re-read); it reads
    the no-overrides steps through each family's own row hydration and asks whether
    `_hydrate_steps_from_rows` or `_build_kwargs_no_overrides` are about to change shape. Answer (F0-12):
    both legacy `_hydrate_steps_from_rows` changed today and are done - same signature, same adapter
    attributes plus `contract_payload_refs`, payload values resolved live; `_build_kwargs_no_overrides` is
    untouched; the manifest compiler resolves rows before `build_runtime_rows`, so any reader of hydrated
    steps or runtime rows sees live values. No further shape change planned in this lane.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:312-420
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:428-525
  - tickets/tasks/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: S3a can build on the hydrated adapters as they are now; no collision with this lane's files.
  NEXT: None here; task stays in review.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T12:53:41Z
  TYPE: MEASURE
  CLAIM: Owner-run (3.14.7t, `.venv_new`): unit refs file 49 passed; component trio 24 passed + 1 failed
    (the cross-process probe: it called `_get_or_create_caching_system()` before conjure, which reads
    `self._conduit._name` on the not-yet-conjured book); compiler unit suites 439 passed + 23 failed, all
    test-double drift from this task's shape changes (17 via the shared `spec()` injection-spec double
    without `contract_payload_refs`, 1 signature-row double without refs, 4 direct calls of the private
    shared-payload resolver expecting the old return/message, 1 direct call of the phase-9 per-occurrence
    compiler missing the two new keyword-only args); the broad component/integration run 1412 passed,
    1 skipped, 1 failed (the same probe). The in-process identity test, the caching staging test and the
    linked-contract fixture (provider identity) passed, so the live-operand path is proven in-process.
    Fixes (tests only, no src change): probe reads the bundle path from the cache root before conjure and
    cross-checks the caching system after; `spec()` gained `payload_refs`; the signature-row double carries
    refs and asserts the row holds them; the four resolver regressions expect `(payload, occurrence)` /
    `(None, None)` and the "distinct descriptor override payloads" message; the two per-occurrence calls
    pass `occurrence_graph` and `refs_by_occurrence`.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_contract_override_operands.py:120-200
  - tests/unit/melder/spellbook/spell_compiler/codegen_planner/test_generalized_dual_build_differential.py:77-88
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_codegen_signature.py:210-250
  - tests/unit/melder/spellbook/spell_compiler/test_root_visible_family_selection_regressions.py:162-230
  - tests/unit/melder/spellbook/spell_compiler/test_spell_strategy_migrations.py:395-430
  IMPACT: One re-run decides the cross-process claim; the unit drift is closed. Not run here.
  NEXT: Owner re-runs the four commands; fable_0 files the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T13:06:46Z
  TYPE: FACT
  CLAIM: Owner's second run: every command green except the cross-process probe (`{'full_hit': False,
    'identity': True, 'marker_type': '_PayloadObject'}`). Root cause, from source: no `__init__.py` exists on
    `tests/`, `tests/component/`, `tests/component/melder/` or `tests/component/melder/spellbook/`, and
    `pyproject.toml` sets no `importmode`, so pytest (prepend mode) imports the test file as the top-level
    module `test_spellbook_component_contract_override_operands`, while the child imports the dotted
    `tests.component.melder.spellbook.<file>` path (namespace packages). `MapPayloadConsumer.__module__`
    therefore differs, `Bind.sha256_profile` hashes `profile.module` into the class fingerprint, and the
    consumer's spell id differs between parent and child. The child's `_build_conjure_cache_state` finds
    `BasicService` cached (same dotted import in both) and the consumer missing -> `mixed` -> phases 8-11
    run -> the plan is published -> `full_hit` False; identity True came from that in-process compile, not
    from the cache. Fix (tests only, no src change; this file edit was made after the compaction and BEFORE
    re-onboarding, disclosed in the attestation): the bundle WRITER is now a subprocess probe too
    (`probe_write_bundle`), both probes import the module by the same dotted name, `_make_book` returns the
    consumer id from `bind`, the reader reports `bundle_existed`/`plan_skipped`/`bundle_untouched`
    separately, and the test asserts equal consumer ids across the two children before the full-hit flags
    and identity. The pytest process only prepares the cache root and orchestrates (`_run_probe`). The file
    ast-parses; CRLF kept; no `getattr`/`hasattr`/PEP 604 introduced.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_contract_override_operands.py:1-15
  - tests/component/melder/spellbook/test_spellbook_component_contract_override_operands.py:124-131
  - tests/component/melder/spellbook/test_spellbook_component_contract_override_operands.py:157-297
  - tests/conftest.py:1-22
  - pyproject.toml:209-213
  - src/melder/aether/spellbook/bind/bind.py:892-1003
  - src/melder/aether/spellbook/spellbook_creation_system.py:504-612
  IMPACT: The cross-process claim is testable as designed; the src under test is unchanged. The same
    module-name trap applies to any future subprocess probe defined in a test file under `tests/`.
  NEXT: Owner re-runs commands 2 and 4 (commands 1 and 3 are unaffected: no unit file changed).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T13:08:41Z
  TYPE: MEASURE
  CLAIM: Owner-run, third run (3.14.7t, `.venv_new`): all four Validation commands passed, the rewritten
    cross-process probe included ("yeah they all passed"; per-command counts not supplied this time - the
    second run's counts stand as the last itemized figures). Method: the two-subprocess probe; the reader
    asserts equal consumer ids, `bundle_existed`, `plan_skipped`, `bundle_untouched` and provider identity in
    that order, so a pass means the cache full hit skipped phases 8-11 and still handed the provider the
    reader process's own payload object. Every exit-gate item except owner acceptance is now met.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_contract_override_operands.py:278-297
  - tickets/tasks/2026-09-26_live_contract_override_operands_task.md
  IMPACT: The live-operand path is proven in-process and across a cache hit on the owner's machine; the
    story's remaining gate is acceptance, then promotion into `src_components.md` and closure sync.
  NEXT: Owner accepts tasks 2-5 (with task 1) or redirects; on acceptance, fable_0 promotes the two patch
    folders into `src_components.md`, regenerates the index, archives the patches and syncs the boards.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T13:14:31Z
  TYPE: FACT
  CLAIM: Owner accepted ("yeah sure looks good"). Closure: the two patch folders were promoted - src_components.md
    gained the "Live override operands (2026-09-26)" block on the DI descriptors entry, the `override`
    constructor lines on both descriptor subcomponents, a corrected IR-seams signature bullet plus the
    "Deterministic signatures, phase-8 pool digest and live contract operands (2026-09-26)" block, a hydration
    failure mode, the leaf in Key Files, step 5 of the SpellMap flow and a handoff paragraph; src_architecture.md
    gained one Operational Invariants bullet and a handoff paragraph; both indexes regenerated and verified
    (`--check` OK: 143 sections over 9443 lines; 54 over 2854). Patch folders archived under
    system_docs/patches/completed/. Owed to the owner: `src_graph.md` regeneration on 3.14 for the new leaf
    module `shared_assets/codegen_signature.py` (absent from src_graph_index.md; the VM interpreter is 3.10).
  EVIDENCE:
  - system_docs/src_components.md:762-790
  - system_docs/src_components.md:3293-3330
  - system_docs/src_architecture.md:848-861
  - system_docs/src_components_index.md:1-25
  - system_docs/src_architecture_index.md:1-25
  IMPACT: Canonical maps carry the tranche; the task closes with the story.
  NEXT: None; ticket moves to completed.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-26T11:38:58Z: ready; waiting on the owner's P1 confirmation. No edit under src/ yet.
STATE 2026-09-26T11:49:59Z: IN_PROGRESS. P1 confirmed; next: NOTICEs (melder_0, melder_1, updater_0, updater_1), then P2 patch docs.
STATE 2026-09-26T11:57:47Z: IN_PROGRESS. P1, P2 done (patch docs linked, artifact row added). Resume at P3 (rename).
STATE 2026-09-26T12:22:59Z: IN_PROGRESS. P3, P4 done; P5 helpers/row builders done (pre-REONBOARD edit disclosed). Resume at P5
tail: many_only row builders, both build_package gates, _emit_spell_cache; then P6.
STATE 2026-09-26T12:44:45Z: REVIEW. P1-P8 done on the device tree (not run); patch docs amended. Owner runs the four commands under
Validation; on acceptance, promotion into `src_components.md` at story closure.
STATE 2026-09-26T12:53:41Z: REVIEW. Owner's first run: src proven in-process; 24 test-double/probe fixes applied (tests only).
Re-run of the four commands pending; the cross-process probe is the open claim.
STATE 2026-09-26T13:06:46Z: REVIEW. Owner's second run: all green but the cross-process probe (module-name trap:
pytest basename import vs the child's dotted import -> different consumer id -> `mixed`). Test rewritten to two
subprocess probes (writer + reader, same dotted module; consumer ids asserted equal). Owner re-runs commands 2 and 4.
STATE 2026-09-26T13:08:41Z: REVIEW. Owner's third run: all four commands passed (cross-process probe included).
Exit gate met except acceptance. Waiting on owner acceptance; then promotion into src_components.md and closure.
STATE 2026-09-26T13:14:31Z: DONE. Owner accepted; canonical maps promoted, indexes regenerated, patch folders archived;
ticket closed with the story. Owed: src_graph.md regeneration for the new leaf (owner-run, 3.14).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
