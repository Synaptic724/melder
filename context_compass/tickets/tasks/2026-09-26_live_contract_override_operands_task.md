# Task: Make SpellContract/SpellMap override values live meld operands and rename `spell_override` to `override`

## Metadata
- Task ID: TASK-2026-09-26-live-contract-override-operands
- Story: STORY-2026-09-26-signature-determinism-phase8-digest
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T11:38:58Z
- Updated: 2026-09-26T12:22:59Z

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
- [ ] P5: row builder emits `contract_payload_items` from refs; gate helpers, both `build_package` gates,
      the `_emit_spell_cache` hunk and their tests removed; replayability asserted on the row builder.
- [ ] P6: resolver helper on `CodegenCreationSchemaHelpers` (`resolve_contract_override_ref(ref, spell_id_pool)`)
      reading the consumer's live descriptor (FORWARDREF signature default); no-overrides-lane binding sites
      of the three families call it at hydration.
- [x] P7 (owner opt-in): SpellMap defaults with an `override` payload recorded through the same refs against
      the phase-3 dependency occurrence.
- [ ] P8: tests (unit: refs, resolver, row builder; component: object payload by identity in-process and
      across a cache hit; xfail removed); docstring ritual; notes; task -> review with "Not run.".
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

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
- Recommended commands (owner-run, 3.14t):
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/contracts tests/unit/melder/spellbook/spell_compiler`
  - `python -m pytest -q tests/component/melder/spellbook tests/component/melder/aether/conduit tests/integration/melder/conduit/test_conduit_integration_links_contracts.py`

## Risks / Rollback Notes
- Rollback: revert the rename and the refs; rows go back to frozen values and the gate returns.
- Signature bytes change only for spells whose rows carried payload values (refs replace values): those
  spells rebuild once; payload-free books keep their bytes (no generation bump).
- The overrides lane keeps today's literalized values until v2 S3: an object payload melded WITH caller
  overrides is still mangled there (documented; same as today; no regression).

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No edit under `src/` before the owner confirms the file/symbol proposal and the patch docs exist.
- [ ] No compatibility alias for the renamed keyword unless the owner asks (overlay 5.15).

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

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

## Context / Handoff Summary
STATE 2026-09-26T11:38:58Z: ready; waiting on the owner's P1 confirmation. No edit under src/ yet.
STATE 2026-09-26T11:49:59Z: IN_PROGRESS. P1 confirmed; next: NOTICEs (melder_0, melder_1, updater_0, updater_1), then P2 patch docs.
STATE 2026-09-26T11:57:47Z: IN_PROGRESS. P1, P2 done (patch docs linked, artifact row added). Resume at P3 (rename).
STATE 2026-09-26T12:22:59Z: IN_PROGRESS. P3, P4 done; P5 helpers/row builders done (pre-REONBOARD edit disclosed). Resume at P5
tail: many_only row builders, both build_package gates, _emit_spell_cache; then P6.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
