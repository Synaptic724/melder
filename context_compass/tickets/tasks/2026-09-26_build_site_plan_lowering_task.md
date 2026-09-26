

# Task: S2/S3 - one site-plan lowering; override key-set plans and the normal lane

## Metadata
- Task ID: TASK-2026-09-26-build-site-plan-lowering
- Story: STORY-2026-09-26-implement-override-site-plan-lowering
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-26T12:29:50Z
- Updated: 2026-09-26T12:51:34Z

## Objective
Overrides run through per-key-set plans compiled from the site graph: supplied dependencies and everything
only they need are never built, and an override meld costs about a normal meld. The same lowering serves
the empty key set; the normal lane switches to it only when it meets the parity gate (design v2 S2).

## Ticket Contract
- ENTRY_GATE: S1 done; collection fix in review; production lowering plan, patch docs (component +
  code-description) and the exact file list in Notes before code.
- EXECUTION_BOUNDARY: files named in Notes once the plan is fixed; no public API change; no value checks.
- DEPENDENCIES: design_v2.md (B1-B8, P1-P3, E1, K1), S1 site graph and resolver, melder_1's regression
  matrix, fable_0's task 5 (live contract operands, touches the no-overrides hydrators and manifest
  compilers): notices before shared files.
- EXIT_GATE: override semantics per B1/B3/B5/B7/B8 and unchanged key errors; melder_1's matrix and the Codex
  corpus; throughput targets of design section 14; suites on 3.14t and GIL; cache generation 14.
- FAILURE_ESCALATION: DECISION_REQUEST for any semantic change outside B1-B8; CONFLICT with fable_0's files;
  BLOCKER if a green baseline is unavailable.

## Scope Boundaries
- In scope: override dispatcher and key-set plan emission for solo, many_only and generalized roots; the
  normal lane behind the parity gate; cache payload/generation changes the plans need.
- Out of scope: S4 (unresolved inputs decided in the plan) and S5 (Phase-5 overlay retirement) unless the
  plan requires them; docs promotion (S6).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner instruction to keep working after S1 acceptance, 2026-09-26T12:13:26Z.

## Steps / Checklist
- [x] Read the family pipelines (Phase 10 plans, Phase 11 finalize/override runtimes, CreationContext slots,
      manifests and hydrators on the cache-hit path) and record the seams.
- [x] Decide the lowering's inputs on both paths (fresh conjure and full cache hit) and write patch docs.
- [x] Implement the dispatcher and plan emission; tests.
- [ ] Parity gate for the normal lane; switch only if met.
- [ ] Validate on 3.14t and GIL; measure.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Lowering module, dispatcher wiring, tests, measurements.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py (new)
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py (new)
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py
- tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py (new)
- tests/component/melder/spellbook/test_spellbook_component_override_key_set_plans.py (new)

## Validation
- Not run.

## Risks / Rollback Notes
- Concurrent edits by fable_0 in the no-overrides family files; B2 constructor order if the normal lane
  switches; R1 recursion depth for long shared chains.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
  - system_docs/patches/active/override_site_plan_2026_09_26/
  - artifacts/melder_override_design_20260926/design_v2.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Phase 10/11 family pipelines, CreationContext override slots, cache-hit hydration
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T12:29:50Z
  TYPE: PLAN
  CLAIM: The override lane is the owner's goal (supplied dependencies not built, override speed near normal),
    so the lowering is built once and used first for key-set plans; the empty key set runs through the same
    lowering in tests as the S2 parity gate, and the normal slots switch only if it meets the gate (design v2
    section 13 keeps the gate; this orders the slot switch after S3 instead of before). The generalized
    normal emitter is step-row driven (existence routing, slot guards, registration, generic construct for
    collections/contracts), which is the production knowledge the prototype lacked.
  EVIDENCE:
  - artifacts/melder_override_design_20260926/design_v2.md:345-420
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:900-1182
  IMPACT: Owner value first, one lowering, the normal-lane risk (R5) stays behind a measured gate.
  NEXT: Read CreationContext slots and the finalize steps' override runtimes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T12:30:10Z
  TYPE: DECISION
  CLAIM: Owner: "ignore melder_1 go work on what you need to work on hes not working on cache atm". Cache
    generation and caching_system.py changes proceed without waiting on melder_1 (M0-23 already sent as FYI;
    no ACK needed).
  EVIDENCE: tickets/tasks/2026-09-26_fix_collection_member_many_sharing_task.md
  IMPACT: No coordination wait for cache work in this story.
  NEXT: Read CreationContext slots and the finalize steps' override runtimes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T12:30:41Z
  TYPE: MEASURE
  CLAIM: Owner-run baseline (benchmarks/testing_other_di/test_overrides_all.py, 1 thread, 15 s, current tree),
    roots/s: solo (meld of a bound existing object, no override) melder 156,754 vs dependency-injector
    378,462, lagom 308,788, dishka 245,725, injector 219,198; shallow (key "a") melder 123,953 vs DI 168,901,
    dishka 179,517, lagom 151,692; wide (key "l0") melder 96,838 vs dishka 146,785, DI 139,023, lagom 103,413;
    diamond ("**leaf", all many) melder 107,596 vs dishka 157,237, DI 146,507, lagom 122,055; deep (8-segment
    PATH, 511 many sites) melder 5,341 vs dishka 19,353, DI 8,328, lagom 4,278. Owner: "overrides still needs
    work". The four override graphs are all-many (many_only family); solo is the existing-object normal door.
  EVIDENCE: benchmarks/testing_other_di/test_overrides_all.py:266-598
  IMPACT: Targets for S3: the many_only override lane first (shallow, wide, diamond, deep), then the
    existing-object solo door as a separate normal-lane cost.
  NEXT: Read the many_only override runtime (per-call path) and the generalized one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:36:41Z
  TYPE: FACT
  CLAIM: Seams read. Override melds enter the per-family `execute_with_overrides(meld, overrides) -> instance`,
    wrapped by the unchanged door compiler (root refusal and root store/guard handling live in the door). It
    is built in four places: many_only finalize `_build_overrides_runtime` (fresh) and many_only hydrator
    `_hydrate_overrides_runtime` (cache hit; reuses the finalize builder), generalized finalize
    `_build_overrides_runtime` and generalized hydrator `_hydrate_overrides_runtime` (lazy door). Both
    manifests carry the no-overrides lane as portable `steps_rows` (many_only rows have no existence/lock
    fields: the family is all-many, CALLER store); each family has its own row hydration, which fable_0's
    task 5 is changing to resolve contract payload references to live values. The generalized normal
    lowering emits per-existence routing, slot guards/Spell lock, `add_creation`/`add_many_creations`
    registration and a generic construct helper; today's equal-rank conflict and P2 messages are in the
    targeting artifact and `_raise_override_on_existing_instance`. Solo roots have no dependencies to skip
    and stay on their own override executor.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py:49-470
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:208-349
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:268-538
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:309-1182
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:697-882
  IMPACT: One runtime object can replace all four override runtimes from the no-overrides steps, on both
    paths, without touching doors, CreationContext, manifests or the normal lane.
  NEXT: Write patch docs and the file list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:36:41Z
  TYPE: PLAN
  CLAIM: S3a file list. New: codegen_creation_system/shared_assets/site_plan_lowering.py (step view, site
    graph from steps, demand, operands, emission) and shared_assets/site_plan_override_runtime.py (runtime,
    dispatcher, compile, arity plans, FIFO); tests tests/unit/melder/spellbook/spell_compiler/shared_assets/
    test_site_plan_lowering.py and tests/component/melder/spellbook/test_spellbook_component_override_key_set_plans.py.
    Edited (runtime construction only): many_only_finalize_creation_context_step.py, many_only_hydrator.py,
    generalized_finalize_creation_context_step.py, generalized_hydrator.py. Existing tests that pin old
    override internals are updated only where they assert the replaced runtime. Old override emitters stay
    until S3b retires them (cache generation 14 then). Patch mapping: component_patch_override_key_set_plans.md
    "After" 1-2 -> runtime module + the four construction sites; "After" 3 and code description steps 3-6 ->
    lowering module; steps 1-2, 7 -> runtime; validation -> existing override suites, new component tests,
    owner benchmark graphs. Development on the consistent VM tree (fable_0's task 5 is mid-edit in the
    device tree's no-overrides compilers); device application after an anchor check and a notice to fable_0.
  EVIDENCE:
  - system_docs/patches/active/override_site_plan_2026_09_26/component_patch_override_key_set_plans.md
  - system_docs/patches/active/override_site_plan_2026_09_26/code_description_patch_site_plan_lowering.md
  IMPACT: Fixes S3a's surface before code.
  NEXT: Notify fable_0 (M0-24), then implement site_plan_lowering.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:51:34Z
  TYPE: FACT
  CLAIM: Correction to the 12:36:41Z seams note. All three families are manifest-first: the live pipelines run
    ManifestStep then LazyDoorStep, so fresh conjures and cache hits both hydrate through the family hydrators.
    The finalize steps' apply() is not in any family pipeline; ManyOnlyFinalizeCreationContextStep is used only
    for its _build_overrides_runtime helper. The live override runtimes are built in exactly two places:
    many_only_hydrator._hydrate_overrides_runtime and generalized_hydrator._hydrate_overrides_runtime (called
    from _build_lazy_overrides_door). The live generalized no-overrides emitter is
    generalized_manifest_no_overrides_compiler (direct _creations reads, slot guard for per-conduit, spellspace,
    cluster and lineage; Spell._lock for unique with the lock hint; direct _creations store without disposal,
    add_creation/add_many_creations with disposal). Phase-3 topologies stay in SpellSystemStates until the spell
    index is removed, so a lazily compiled plan can read every constructor parameter at first override meld.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_strategy.py:55-107
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:208-349
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:268-538
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:281-740
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:780-800
  IMPACT: S3a edits only the two hydrators (not the finalize steps); the lowering mirrors the manifest emitter.
  NEXT: Record the S3a scope decisions, then finish the two modules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:51:34Z
  TYPE: DECISION
  CLAIM: S3a scope, kept to B1/B3/B5/B7/B8 plus P1-P3/E1/K1. (1) Emission keeps today's straight-line step
    order (a shared site's children are built before its store check); the L1/L3 nested-miss form and B2
    belong to the S2 normal-lane switch. (2) Steps with a contract payload or contract positional payload use
    the family's generic construct (no constant binding), so live contract operands from fable_0's task 5 keep
    one source; their dependencies are still built as today. (3) Unresolved inputs stay on the interim
    constructor-failure path (S4). (4) The empty key set and an arity-0 __args__ delegate to the inner
    no-overrides executor. (5) The runtime is one Cleanable object per root, compiled lazily and held by the lazy
    override door, as the old closure runtime was. Edited files shrink to the two hydrators plus the two new
    modules and tests; the finalize steps are not touched.
  EVIDENCE:
  - artifacts/melder_override_design_20260926/design_v2.md:86-356
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:697-882
  IMPACT: Override melds skip supplied subtrees with today's locking and registration; no normal-lane change.
  NEXT: Write site_plan_lowering.py and site_plan_override_runtime.py in the session workspace.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T13:02:26Z
  TYPE: MEASURE
  CLAIM: S3a implemented on the consistent VM tree (site_plan_lowering.py, site_plan_override_runtime.py, the two
    hydrator functions via apply_s3a_edits.py). Probe (3.14t): Root(a, b, limit) all many with {"a": obj} builds
    B and Root only; ("limit": 9) builds A, B, Root; override=(obj,) and [obj, B(), 5] build Root only (B5); a bad
    key raises "Failed to apply overrides." chained from "No sockets found for override path 'nosuch'."; generalized
    GRoot(a, s: S unique_per_conduit) with {"s": obj} builds A and GRoot, with {"s>a": obj} builds A, S, GRoot and a
    repeat raises today's P2 message. Suites on 3.14t: unit spellbook 2142, aether 4124, utilities 785+2s+7xf,
    build_assets 116, crystallizer 565, mutation_research 277, root files 145; component spellbook 735+1xf,
    mutation_research 40, utilities 41+23s, crystallizer 106 + the known 4 file_backed_morph environment failures;
    integration spellbook 574, conduit 267, aether 716, mutation_research 66, crystallizer 258, multithreading 42.
    Only other failures: 5 cases in test_conduit_component_non_resolvable_overrides.py that characterize the old
    eager construction of a supplied branch (they expect the child's missing input to fail) - exactly B1. Stale
    __conjure_cache__ dirs in the VM tree caused 6 spurious failures until cleared (base tree passes the same tests).
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/site_plan_lowering.py:1-1058
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s3a_edits.py:1-356
  - tests/component/melder/aether/conduit/test_conduit_component_non_resolvable_overrides.py:146-194
  IMPACT: No regression outside B1; the two characterization tests must move to the B1 behavior.
  NEXT: Update the two characterization tests (in scope, test only), then write the new unit and component tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T13:11:26Z
  TYPE: MEASURE
  CLAIM: Owner benchmark (benchmarks/testing_other_di/test_overrides_all.py, DI_LIBS=melder, 3 s per graph, 1 thread,
    2-core VM), roots/s before -> after S3a. 3.14t: solo 158,840 -> 166,992 (no override; unchanged within noise),
    shallow 135,899 -> 174,767 (+29%), wide 107,283 -> 168,427 (+57%), diamond 120,613 -> 172,549 (+43%), deep 6,555
    -> 28,733 (x4.4). GIL: solo 151,154 -> 165,624, shallow 99,561 -> 146,448 (+47%), wide 92,401 -> 125,621 (+36%),
    diamond 107,831 -> 138,832 (+29%), deep 9,541 -> 31,166 (x3.3). errors=0 in every run (the benchmark validates
    results every 200 steps). Tests: 25 new unit + 22 new component cases pass; the two B1 characterization tests
    were moved to B1 (renamed, apply_s3a_test_edits.py). After switching the generalized hydrator to the family's
    _hydrate_steps_from_rows (it resolves fable_0's contract payload references in the device tree), 3.14t and GIL:
    unit spellbook 2164, component spellbook 760+1xf, component aether 1186+1s+1xf, integration spellbook 574,
    multithreading 42, aether 716 (GIL), conduit 267 (3.14t). One GIL-flaky test
    (test_conduit_concurrent_meld_across_linked_conduits_isolated_per_conduit, no overrides) fails 1-4 times in 6
    runs on the base tree as well (creation_context_race lane). apply_s3a_edits.py and apply_s3a_test_edits.py
    anchors match the device tree (--check).
  EVIDENCE:
  - benchmarks/testing_other_di/test_overrides_all.py:620-700
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s3a_edits.py:1-356
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/test_spellbook_component_override_key_set_plans.py:1-405
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/test_site_plan_lowering.py:1-491
  IMPACT: Override melds now beat the other libraries' owner-measured figures on shallow, wide, diamond and deep
    (owner machine numbers still needed); no suite regressions.
  NEXT: Apply S3a to the device tree (new modules, hydrator edits, test edit, new tests), A/B on a device-state copy,
    notify fable_0 (M0-25).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T13:16:33Z
  TYPE: FACT
  CLAIM: S3a applied to the device tree after the anchor check: new site_plan_lowering.py and
    site_plan_override_runtime.py (cp -n), apply_s3a_edits.py on the two hydrators, apply_s3a_test_edits.py on
    test_conduit_component_non_resolvable_overrides.py, new tests test_site_plan_lowering.py and
    test_spellbook_component_override_key_set_plans.py; all seven files are byte-identical to the validated VM copies.
    Device-state A/B (fresh rsync of src/tests, with vs without S3a), 3.14t: unit spellbook 2192 vs 2170, component
    spellbook 768 vs 743, component aether 1186+1s+1xf both, integration spellbook 577 both, conduit 267 vs 263 + 4
    base-side concurrency flakes (race lane); unit aether 4124, integration aether 716, multithreading 42,
    build_assets 116, crystallizer component the known 4 file_backed_morph. GIL with S3a: unit spellbook 2192,
    component spellbook 768, component aether 1186+1s+1xf, integration spellbook 577, multithreading 42. fable_0's
    task 5 is now green in the device tree; the many_only and generalized _hydrate_steps_from_rows there resolve
    contract payload references, which the override runtime now reads through.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:299-356
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:370-431
  IMPACT: S3a is in the working tree (uncommitted); the old override emitters and targeting runtime are now unused
    at run time.
  NEXT: Notify fable_0 (M0-25), then plan S3b (retire the old override lane, drop the manifest override payload,
    cache generation 14).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T13:16:59Z
  TYPE: FACT
  CLAIM: Consumed fable_0 F0-10 and F0-12. Task 5 landed in the device tree: phase 9 passes
    contract_override_refs_by_occurrence; rows carry a value-only ref for every non-scalar contract payload entry;
    both legacy _hydrate_steps_from_rows (generalized, many_only) keep their signature and adapter attributes (plus
    contract_payload_refs) and hold LIVE values in contract_payload/contract_positional_override; the generalized
    manifest compiler resolves rows before build_runtime_rows; _build_kwargs_no_overrides is untouched; F0-6 stands
    (S2/S3 read payload operands live). Files fable_0 touched beside phase 9: codegen_signature.py,
    codegen_creation_schema_helpers.py, generalized_manifest_no_overrides_compiler.py,
    generalized_no_overrides_codegen_creation_compiler.py, many_only helpers/manifest/compiler,
    manifest_creation_cache.py, spell_codegen_creation_cache.py, spellbook.py:_emit_spell_cache - re-read before
    editing any of them (S3b touches several).
  EVIDENCE: tickets/tasks/2026-09-26_live_contract_override_operands_task.md
  IMPACT: S3a's step source (the families' _hydrate_steps_from_rows) carries live contract values, as the normal lane.
  NEXT: Plan S3b from the current device-tree sources.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Discovery: reading the Phase-10/11 pipelines to fix the production lowering plan.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
