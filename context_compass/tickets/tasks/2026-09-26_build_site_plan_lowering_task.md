

# Task: S2/S3 - one site-plan lowering; override key-set plans and the normal lane

## Metadata
- Task ID: TASK-2026-09-26-build-site-plan-lowering
- Story: STORY-2026-09-26-implement-override-site-plan-lowering
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-26T12:29:50Z
- Updated: 2026-09-26T17:31:14Z

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
- [x] Parity gate for the normal lane; switch only if met (met and switched, S2b-2, 2026-09-26).
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
- tests/experimentation/test_melder_creation_overrides_performance.py (solo matrix inputs, 2026-09-26)
- tests/experimentation/test_generalized_cache_strategy_experiment.py (code-cache assertion, S2b-2)

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

- DATETIME: 2026-09-26T13:22:58Z
  TYPE: FACT
  CLAIM: Consumed fable_0 F0-13. Tranche T1 closed (owner accepted). src_components.md now carries the `override`
    rename and the live-operand mechanics in the DI descriptors entry (:762-790), the SpellMap/SpellContract
    subcomponents and a dated block in the SpellCompiler entry (:3293-3330); indexes regenerated. The override-lane
    row copies are documented there as unchanged until S3. No src change in that closure.
  EVIDENCE: tickets/stories/completed/2026-09-26_signature_determinism_and_phase8_digest_story.md
  IMPACT: S3b changes what that SpellCompiler block says about the override lane; S6 promotion must re-read those
    ranges and edit them in place, not add a parallel paragraph.
  NEXT: Record the S3b override-lane cost measure and the S3b-1 plan with its file list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T13:23:46Z
  TYPE: MEASURE
  CLAIM: With S3a in place the old override lane is built at every conjure and never used. Probe (conjure setup of the
    owner's four graphs, disk cache off, median of 7, 3.14t, device tree + S3a): deep 42.44 ms setup, of which the
    override lane is 5.33 ms (12.6%): Phase-9 spell_override_targeting_processor 2.24, Phase-10 overrides plan 1.44,
    many_only override step rows 1.26, target serialization 0.39. Phase-9 spell_site_graph_processor adds 3.88 ms and
    its artifact is not read at run time either (the override runtime rebuilds its site graph lazily from the kept
    Phase-3 topologies). Shallow, wide and diamond spend under 0.1 ms there.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/override_lane_cost.py:1-60
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/override_lane_cost_results.txt:1-6
  IMPACT: S3b removes up to ~9 ms (21%) of deep conjure: 5.3 ms by retiring the lane, 3.9 ms more if the Phase-9
    site-graph processor is unregistered (S1's builder stays as library code for the runtime).
  NEXT: Read every consumer of overrides_plan, the targeting/site-graph artifacts and manifest["overrides"], then
    write the S3b-1 plan and file list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T13:26:20Z
  TYPE: FACT
  CLAIM: How the unused lane is built at conjure. Phase 9: SpellArtifactProcessor runs every registered strategy in
    registration order; the builder registers site_graph and override_targeting after injection (the only writers of
    model.site_graph_shape / override_targeting_shape and the target_* counters). Phase 10: the many_only and
    generalized_many_only plan strategies each run a second builder for the OVERRIDES variant (many_only
    _build_overrides_plan re-walks _build_ordered_steps); the generalized strategy's build_dual walks once and only
    adds a second _assemble_lane_plan over the shared steps (cheap). Solo builds its own overrides_plan and keeps it.
    Readers of override_targeting_shape: the two manifests (raise when it is None), the two overrides steps (not in
    any pipeline) and the legacy spell_codegen_creation_cache codec (already tolerates None). Readers of
    overrides_plan besides those: generalized_binding_resolver and shared_compiler_executions (both skip None).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy_builder.py:77-118
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:61-100
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_many_only_codegen_plan_strategy.py:36-77
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:36-68
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1120-1335
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:949-1369
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_binding_resolver.py:60-100
  IMPACT: S3b-1 can stop the build at three points (Phase-9 registration, the two many_only-family plan strategies,
    the two manifests) without touching solo or the generalized step walk.
  NEXT: Read the two manifests, lazy door steps, legacy codec and the tests that pin the old lane, then write the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T13:29:42Z
  TYPE: PLAN
  CLAIM: S3b splits in two. S3b-1 stops building and serializing the unused lane (edits only, no deletions):
    (1) spell_artifact_processor_strategy_builder.py drops the site-graph and override-targeting registrations
    (S1's build_site_graph stays as the library the runtime calls); (2) spell_many_only_codegen_plan_strategy.py
    stops building the OVERRIDES variant (plan.overrides_plan stays None; solo and the generalized build_dual are
    unchanged in S3b-1 - the generalized second lane is one constructor over shared steps and goes in S3b-2);
    (3) many_only_manifest.py and generalized_manifest.py drop the "overrides" section, its validation and the
    targeting requirement (MANIFEST_VERSION 3 -> 4); (4) many_only_lazy_door_step.py and
    generalized_lazy_door_step.py drop the four override_* metadata keys read from it; (5) the two hydrators drop
    the imports and helpers only the old runtime used; (6) caching_system.py generation 14
    "override_site_plan_lanes". Readers that already skip a None lane are left alone (binding resolver,
    shared_compiler_executions, legacy spell_codegen_creation_cache). Tests pinning the removed registrations,
    manifest section or metadata are updated; the exact list comes from the suite run on the VM copy and is
    recorded before device application. S3b-2 (owner-confirmed deletions) then removes the dead modules: both
    override compilers, the overrides/finalize steps, both targeting artifacts, the targeting processor and
    analysis, generalized_manifest_overrides_runtime, the generalized OVERRIDES lane variant, the
    generalized_many_only plan strategy (registered nowhere) and their tests.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/manifest/many_only_manifest.py:52-143
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/manifest/generalized_manifest.py:38-181
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_lazy_door_step.py:45-117
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:98-219
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy_builder.py:75-95
  - src/melder/utilities/caching_system/caching_system.py:99-161
  IMPACT: About 9 ms (21%) off deep conjure with no runtime change; the deletion sweep stays separate and asked for.
  NEXT: Implement S3b-1 on a fresh VM copy of the device tree and run the suites to find the pinned tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T13:41:05Z
  TYPE: FACT
  CLAIM: S3b-1 implemented on a fresh VM copy of the device tree (~/work/melder_s3b; untouched twin
    ~/work/melder_s3bbase) by apply_s3b1_edits.py (anchor-checked, per-line line endings; caching_system.py mixes LF
    and CRLF). Nine files: strategy builder (two registrations and imports), many_only plan strategy (no OVERRIDES
    build), both manifests (version 4, no overrides section, validators, dead serializers/signature builders), both
    lazy door steps (four override_* metadata keys), both hydrators (imports and helpers only the old runtime used:
    targeting refs/artifacts, old compilers, finalize step, _NULL_MODEL, path-registry and target deserializers),
    caching_system.py generation 14 "override_site_plan_lanes". An AST import check finds no new unused names
    (generalized_manifest's MANIFEST_METADATA_KEY was already unused).
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s3b1_edits.py:1-441
  IMPACT: The diff is exactly the planned surface; suites decide the test list.
  NEXT: Read the 3.14t suite results and fix or move the tests that pin the removed lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T13:41:25Z
  TYPE: MEASURE
  CLAIM: S3b-1 validated on the VM copy. Tests that pinned the removed lane (six files, apply_s3b1_test_edits.py):
    processor registry order; many_only plan strategy (one builder call, overrides_plan None); the S1 oracle now fits
    both retired Phase-9 sections itself on the conjured model; required-input rows check only the no-overrides
    variant for many_only; the spell-crafter "*service" target now resolves through the site graph and
    OverrideKeyResolver; cache history pin gains 14. 3.14t: unit spellbook 2192, component spellbook 768, integration
    spellbook 578+2s+3xf+1xp, component aether 1186+1s+1xf, conduit 267+1s, unit aether 4124, integration aether 716,
    multithreading 42, unit utilities 785+2s+7xf, crystallizer unit 565, mutation_research 277/40/66, root files 26;
    only the known environment failures (crystallizer file_backed_morph x4; build_assets x2, also on the untouched twin
    because the copy has no context_compass). GIL: unit spellbook 2192, component spellbook 768, integration spellbook
    578, component aether 1186, multithreading 42, unit aether 4124; conduit concurrency flakes 2-5 per run on both
    trees (race lane). Conjure setup (median of 9, 3.14t): deep 42.8/45.6 -> 32.0/33.0 ms (-25%); shallow, wide,
    diamond unchanged within noise. Override benchmark (3 s): shallow 195,565 -> 200,489, wide 187,930 -> 181,262,
    diamond 201,918 -> 197,509, deep 31,393 -> 31,214 roots/s, errors=0 (noise). The solo graph sometimes reports
    duration 0.00s / 0 steps on both trees (harness quirk, not a failure). All 15 device files still match the
    snapshot the VM copy was taken from.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s3b1_test_edits.py:1-152
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/conjure_setup.py:1-14
  - tests/integration/melder/spellbook/test_cache_schema_version_integration.py:12-27
  IMPACT: S3b-1 is ready for the device tree: conjure -25% on deep with no runtime or test regression.
  NEXT: Notify fable_0 (many_only_manifest.py) and melder_1 (cache generation 14), then apply both scripts to the
    device tree and verify byte-identity with the VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T13:42:48Z
  TYPE: FACT
  CLAIM: Consumed fable_0 F0-14: release_docs/next_version_release.md (0.2.56) says a meld that passes its own
    override still renders descriptor payload values into generated code. Probe (SpellMap payload object on a many
    consumer, meld with override={"other": obj}): without S3a (~/work/melder_devbase) the provider gets a different
    object (False); with S3a (device tree, and with S3b-1) it gets the same object (True), normal melds True on all.
    The bullet is obsolete once S3a ships.
  EVIDENCE:
  - release_docs/next_version_release.md:42-45
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/payload_override_identity.py:1-40
  IMPACT: The release section for this story (S6) retires that bullet and says override melds deliver payload
    objects by identity too.
  NEXT: Apply S3b-1 to the device tree after the notices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T13:44:05Z
  TYPE: FACT
  CLAIM: S3b-1 applied to the device tree after --check on both scripts: nine src files (apply_s3b1_edits.py) and six
    test files (apply_s3b1_test_edits.py); all fifteen are byte-identical to the validated VM copy. Notices M0-26
    (fable_0: the two manifests) and M0-27 (melder_1: cache generation 14) sent. Uncommitted, like S3a.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/manifest/many_only_manifest.py:41-100
  - src/melder/utilities/caching_system/caching_system.py:99-166
  IMPACT: Conjure stops paying for the unused override lane; the dead modules remain for S3b-2.
  NEXT: Map every importer of the retired override modules on the S3b-1 tree and write the S3b-2 deletion list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T13:45:11Z
  TYPE: DECISION_REQUEST
  CLAIM: S3b-2 (delete the dead lane) is a many-file sweep with deletions, so it waits for the owner. Importer map on
    the S3b-1 tree: nothing reachable from conjure or meld imports these 12 modules - many_only overrides compiler,
    many_only overrides step, many_only finalize step, many_only targeting artifact, generalized overrides compiler,
    generalized_manifest_overrides_runtime, generalized overrides step, generalized finalize step, generalized
    targeting artifact, the Phase-9 targeting processor and its analysis, and the unregistered
    generalized_many_only plan strategy. Their remaining importers are: the legacy non-manifest codec
    spell_codegen_creation_cache.py (reached only by tests - plan discovery always picks solo/many_only/generalized,
    all three emit manifests, so the fallback family and legacy build_package never run from conjure);
    spellbook_creation_system._rebuild_cached_creation_context_executors (legacy override branch);
    generalized_runtime_library (override re-exports; the module stays, it serves the live no-overrides compiler);
    and nine test files (codegen_creation_core, codegen_creation_compilers_core, ordered_disposal_compiler,
    spell_strategy_migrations, spell_artifact_processor_data_migrations, contract_override_refs, the S1 oracle,
    spell_codegen_pipeline_component, the experimentation cache playground). Also trimmed with it: the model's
    override fields and counters, the family states' override slots, the generalized OVERRIDES lane variant, the
    override metadata in shared_compiler_executions. The bind-guard and system-document build assets name these
    classes, so an asset rebuild (owner approval) follows in S6. Options: (1) S3b-2 as listed, legacy codec and
    fallback family kept minus their override halves (recommended: the story's scope, nothing live changes, git
    restores); (2) also retire the legacy codec and fallback family (broader than this story); (3) leave the dead
    modules in place.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/generalized_codegen_plan_discovery_strategy.py:55-83
  - src/melder/aether/spellbook/spellbook.py:995-1024
  - src/melder/aether/spellbook/spellbook_creation_system.py:667-830
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:98-219
  IMPACT: No runtime or conjure change either way (S3b-1 already removed the cost); this is code and test removal.
  NEXT: Ask the owner; meanwhile measure the S2 parity gate (empty key set through the lowering vs the normal lane).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T13:48:43Z
  TYPE: MEASURE
  CLAIM: S2 parity probe (S3b-1 tree, direct calls, median of 7): the lowering's empty-key-set plan vs the many_only
    inner no-overrides executor runs at 92-107% (3.14t) and 90-97% (GIL) speed on shallow/wide/diamond, 97-99% on
    deep. The emitted bodies are identical (same transient targets, same try/except per step); the plan differs only
    in its signature - `(meld, ov, <every namespace name as a default>)` - where the inner executor reads module
    globals. Filling defaults costs per call, which matches the 10-30 ns gap. Public meld adds ~200 ns over the inner
    executor on small graphs (fast-door path); the override experiment (MELDER_OVERRIDE_PERF=1, 3.14t) shows override
    melds at 66-83% of normal on shallow/wide/diamond (root_one_reused 488 vs normal 341 ns on shallow), so the
    remaining override cost is meld entry and dispatch, not the plan.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/s2_parity.py:1-65
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/s2_sources.py:1-25
  - src/melder/aether/conduit/meld/conduit_meld.py:500-545
  IMPACT: S2 parity is within reach by emitting plans into a globals namespace (as the inner executor does); the
    same change trims every override plan call. The override-vs-normal gap is in the meld entry path.
  NEXT: Record the owner's S3b-2 decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T13:48:43Z
  TYPE: DECISION
  CLAIM: Owner answered the S3b-2 request with "1 and 2": delete the dead override modules as listed AND retire the
    legacy non-manifest codec (spell_codegen_creation_cache.py) and the fallback no-overrides family, with their
    callers and tests. melder_0 reads this as the union of both options (option 2 is option 1 plus the legacy codec
    and fallback family). Build-asset rebuilds still wait for owner approval (S6).
  EVIDENCE: tickets/tasks/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: S3b-2 scope is fixed; exact file list recorded before code after reading every caller.
  NEXT: Read the legacy codec's callers (spellbook._emit_spell_cache, spellbook_creation_system cache publish) and the
    fallback registrations, then record the S3b-2 file list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T13:50:34Z
  TYPE: PLAN
  CLAIM: S3b-2 file list (prefix src/melder/aether/spellbook/spell_compiler/, "ccs" = codegen_creation_system/).
    DELETE (17): ccs/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py,
    ccs/strategies/many_only/steps/many_only_overrides_codegen_creation_step.py,
    ccs/strategies/many_only/steps/many_only_finalize_creation_context_step.py,
    ccs/strategies/many_only/artifacts/spell_override_targeting_codegen_creation.py,
    ccs/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py,
    ccs/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py,
    ccs/strategies/generalized/steps/generalized_overrides_codegen_creation_step.py,
    ccs/strategies/generalized/steps/generalized_finalize_creation_context_step.py,
    ccs/strategies/generalized/steps/generalized_no_overrides_codegen_creation_step.py (fallback-only),
    ccs/strategies/generalized/artifacts/spell_override_targeting_codegen_creation.py,
    ccs/strategies/generalized/generalized_codegen_creation_state.py (used only by the deleted steps),
    ccs/strategies/fallback_no_overrides/fallback_no_overrides_codegen_creation_strategy.py,
    ccs/codegen_creation_discovery_system/strategies/fallback_no_overrides_codegen_creation_discovery_strategy.py,
    ccs/codegen_creation/spell_codegen_creation_cache.py (legacy codec),
    artifact_processor/strategies/spell_override_targeting_processor_strategy.py,
    artifact_processor/data/spell_override_targeting_analysis.py,
    codegen_planner/strategies/spell_generalized_many_only_codegen_plan_strategy.py; plus the three emptied folders.
    EDIT: spellbook.py _emit_spell_cache (a creation without a manifest is not cached); spellbook_creation_system.py
    (_publish_cached_creation_context_for_spell accepts manifest packages only; the CodeType/legacy rebuild helpers and
    their module helpers go - no producer of those payloads exists and generation 14 rejects older bundles);
    ccs/spell_codegen_strategy_builder.py and ccs/codegen_creation_discovery_system/
    codegen_creation_discovery_strategy_builder.py (unregister fallback; an unclaimed plan raises the existing
    "could not select" error); generalized_runtime_library.py (override exports); spell_codegen_model.py
    (override_targeting_shape, target_* counters, override_shape_family); phases/shared_compiler_executions.py (the
    target_spec_count export key); many_only_codegen_creation_state.py (override slots); spell_site_graph_analysis.py
    (docstring naming the targeting section). Kept for S2 as the design orders: the generalized Phase-10 OVERRIDES
    variant (build_dual) and solo's own override executor. TESTS: delete test_spell_codegen_cache_rehydration_exec.py,
    the S1 oracle test and the experimentation cache-asset playground; trim the targeting/legacy/fallback cases from
    the other files that reference them (list recorded after the suite run).
  EVIDENCE: tickets/tasks/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: Removes roughly 8k lines of dead override and legacy-codec code with no runtime change.
  NEXT: Implement on the VM copy (edits by anchored script, deletions by rm), then run the suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T13:53:10Z
  TYPE: FACT
  CLAIM: S3b-2 src applied to the VM copy by apply_s3b2_edits.py: 17 modules deleted and 3 emptied folders pruned; 12
    files edited (spellbook._emit_spell_cache returns False for a creation without a manifest;
    _publish_cached_creation_context_for_spell accepts manifest packages only and the legacy rebuild helpers and their
    module helpers are gone; fallback unregistered from both creation builders; runtime-library override exports,
    model override fields, the target_spec_count export, many_only state override slots removed; site-graph docstrings
    corrected - the processor docstring still claimed S3b-1's removed registration). The tree compiles, no src file
    imports a deleted module, and no edited file has an unused import. Integration spellbook 578 passes unchanged;
    11 test files fail at collection because they import deleted modules.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s3b2_edits.py:1-411
  IMPACT: The src side of S3b-2 is complete; the test side follows the collection errors.
  NEXT: Rework or delete the 11 test files, then run all suites on 3.14t and GIL.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T14:07:47Z
  TYPE: FACT
  CLAIM: S3b-2 tests reworked on the VM copy by apply_s3b2_test_edits.py (AST prune of named defs/imports or of defs
    naming a deleted module alias, then anchored edits). DELETE (5): test_spell_codegen_cache_rehydration_exec.py, the
    S1 oracle component test, the experimentation cache-asset playground and its two experiment tests (all built on the
    deleted targeting modules). EDIT (12): codegen_creation_core and codegen_discovery_pipeline_component (fallback
    test -> "a plan no family claims raises"), codegen_creation_discovery_core (fallback strategy removed),
    codegen_creation_compilers_core (22 generalized-overrides-compiler tests dropped; shared helpers kept),
    ordered_disposal_compiler (no-overrides only; the cache test hydrates through the generalized manifest payload and
    hydrate_no_overrides_executor), artifact_processor_data_migrations, strategy_migrations, artifact_processor_core
    (model section list), contract_override_refs (legacy package test), cache_runtime_verification (manifest-only
    emit/publish; new "no manifest -> not cached" test), creation_system_resolution_fastpath and
    codegen_signature_determinism (manifest only). Two engine fixes during the check: prune lines keep their own endings
    (two files mix CRLF and LF), and one import name was wrong from memory. Full collection: 12,547 tests, no import
    errors apart from the yaml/llm_support environment gaps that the untouched base shares. Process note: after the
    compaction the first draft of this script was written and --check-ed on the VM copy before REONBOARD (disclosed in
    the attestation); nothing else was touched.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s3b2_test_edits.py:1-470
  - tests/unit/melder/spellbook/spell_compiler/test_ordered_disposal_compiler.py:1-240
  - tests/unit/melder/spellbook/test_cache_runtime_verification.py:1-645
  IMPACT: The S3b-2 tree collects; the suites decide whether any behavior test needs more than removal.
  NEXT: Run all suites on 3.14t and GIL on ~/work/melder_s3b.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T14:15:16Z
  TYPE: MEASURE
  CLAIM: S3b-2 validated on the VM copy (src by apply_s3b2_edits.py, tests by the final apply_s3b2_test_edits.py run
    fresh against the device tree's current test files). Suite changes beyond the 14:07 list: one more component test
    retargeted (the creation facade test used the fallback's "other_plan"; it now drives the real generalized claim),
    the model-section list in test_spell_artifact_processor_core, and the helpers/imports the pruning orphaned
    (_make_overrides_step_row, _OverrideSocketRef, SocketKind, TargetSpecKind, List); an AST scan finds no new unused
    import or helper against the base. 3.14t: unit spellbook 2149, component spellbook 764, integration spellbook
    578+2s+3xf+1xp, component aether 1186+1s+1xf, unit aether 4124, integration aether 716, multithreading 42, unit
    utilities 785+2s+7xf, component utilities 21+43s, crystallizer 565/106/258+3xf, mutation_research 277/40/66,
    experimentation 250+4s, live_sim 1+1xf, root files 144. GIL: unit spellbook 2149, component spellbook 764,
    integration spellbook 578, component aether 1186, multithreading 42, unit aether 4124, integration aether 716,
    experimentation 250, crystallizer 565, mutation_research 277. Failures, all shared with the untouched base: conduit
    concurrency 3-5 per run on both builds (race lane), crystallizer file_backed_morph x4, build_assets x2 (VM copy has
    no context_compass), test_generated_build_assets_are_stamped_for_the_live_version (assets stamped 0.2.54 against
    the 0.2.56 release; waits for the owner-approved asset rebuild). Deep conjure 33.45 ms (S3b-1: 32-33), no change.
    melder_1's pending race patch touches none of the S3b-2 files. Follow-up (out of scope):
    GeneralizedCacheCodegenCreationDiscoveryStrategy is registered nowhere in src.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s3b2_test_edits.py:1-503
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s3b2_edits.py:1-411
  - tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py:198-234
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery_system.py:55-82
  IMPACT: S3b-2 is ready for the device tree: dead override lane, legacy codec and fallback family gone, no regression.
  NEXT: --check both S3b-2 scripts on the device tree, send notices (fable_0, melder_1), apply, verify byte-identity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T14:21:48Z
  TYPE: FACT
  CLAIM: S3b-2 applied to the device tree after --check on both scripts and notices M0-28 (fable_0) and M0-29 (melder_1).
    The first apply wrote all edits, then stopped at the first deletion (mount deletes not enabled in this session);
    the owner-approval prompt enabled deletes for melder_private and the 22 deletions and 3 folder prunes ran from the
    scripts' own lists. All 22 edited files are byte-identical to the validated VM copy; all 22 deleted paths are
    gone. Since the snapshot, melder_1's race fix (conduit_meld, meld, spellspace_meld, creation-context
    factory/rebuild, spell.py and tests) and restamped build assets landed on the device. Fresh copy of the combined
    device state, 3.14t: unit spellbook 2151, component spellbook 764, integration spellbook 578+2s+3xf+1xp, component
    aether 1188+1xf, multithreading 42, conduit 268 (race fix: no concurrency failures), unit aether 4145, integration
    aether 716, experimentation 250+4s, unit utilities 785+2s+7xf, crystallizer 565/258+3xf, mutation_research
    277/40/66, root files 145, live_sim 1+1xf; only crystallizer file_backed_morph x4 and build_assets x2 (copy lacks
    context_compass). GIL: unit spellbook 2151, component spellbook 764, integration spellbook 578, component aether
    1188, multithreading 42, conduit 268, unit aether 4145, experimentation 250. Build assets still name the deleted
    classes (bind guard 13 entries, graph adjacency 181 rows): harmless at run time, rebuilt in S6 with owner approval.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s3b2_edits.py:1-411
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s3b2_test_edits.py:1-503
  - src/melder/aether/spellbook/spellbook_creation_system.py:667-700
  IMPACT: S3 is complete in the working tree (uncommitted): override melds run key-set plans and the old lane, legacy
    codec and fallback family are gone. Next is S2 (normal lane through the lowering behind the parity gate).
  NEXT: Read the lowering's plan emission and the many_only inner executor's globals binding, then write the S2 plan
    and file list (emit plans into a globals namespace).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T14:24:02Z
  TYPE: PLAN
  CLAIM: S2 splits. S2a (now, no semantic change): emitted key-set plans read their constants as globals of the plan's
    own namespace (they already exec into it) instead of re-binding each one as a default argument, which costs a
    default fill per call (the 13:48 parity gap). Namespace names (helpers, spells, root ids, cf*/sid*/dm*/key*/st*/t*)
    never collide with body locals (args, instance_results, many_store, v*, c*, exc), so no read becomes an unbound
    local. Files: shared_assets/site_plan_lowering.py (render signature `def _site_plan_executor(meld, ov):`, the
    emit/_bind docstrings) and the code-description patch; tests unchanged (they exec into the namespace). No cache
    generation (plans compile lazily from rows; the code cache keys on source). Gate: unit/component spellbook and
    override suites on 3.14t and GIL; s2_parity.py and the owner's test_overrides_all.py before/after. S2b (later):
    empty-key-set plans fill the normal slots behind the parity gate with the L1/L3 nested-miss form and B2 - its own
    plan and file list. Development on ~/work/melder_dev_s3b2 (fresh device copy) with a twin for A/B.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:669-1059
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:312-342
  - artifacts/melder_override_design_20260926/design_v2.md:124-146
  IMPACT: Every override plan call drops its default fill; the empty-key-set plan becomes a fair parity candidate.
  NEXT: Snapshot the twin, apply the render change by anchored script, run the suites and measure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T14:28:39Z
  TYPE: MEASURE
  CLAIM: S2a validated on a fresh device copy (apply_s2a_edits.py: render signature `(meld, ov)`, three docstrings;
    twin ~/work/melder_s2base for A/B). s2_parity.py, lowering plan vs the many_only inner executor, median of 7 direct
    calls: 3.14t shallow 91.4% -> 99.4%, wide 96.1% -> 97.6%, diamond 93.0% -> 99.4%, deep 96.6% -> 101.9%; GIL
    shallow 91.9% -> 98.9%, wide 94.9% -> 98.3%, diamond 93.0% -> 99.9%, deep 98.2% -> 101.0%. Owner benchmark
    (test_overrides_all.py, 3 s, 3.14t) roots/s: shallow 180,178 -> 184,564, wide 166,135 -> 174,309, diamond
    177,556 -> 185,707, deep 31,664 -> 31,790, errors=0; the GIL runs swing +-20% between repeats on this machine (solo,
    untouched, moved -16%), so they do not resolve a ~3% effect. Suites 3.14t and GIL: unit spellbook 2151, component
    spellbook 764, integration spellbook 578, component aether 1188, conduit 268, multithreading 42 (GIL also
    experimentation 250). The S2 parity gate's plan-level criterion is met: the empty-key-set plan runs at the inner
    executor's speed on both builds.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s2a_edits.py:1-71
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/s2_parity.py:1-65
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:856-900
  IMPACT: Override plans lose their per-call default fill (bigger on deep graphs); S2b can switch the normal lane
    without a speed penalty.
  NEXT: --check and apply S2a on the device tree, verify byte-identity, update the code-description patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T14:30:42Z
  TYPE: MEASURE
  CLAIM: S2a applied to the device tree (byte-identical to the validated copy; code-description patch updated).
    Per-layer cost of a root-key override meld (override_entry_layers.py, device state + S2a, median of 7, ns;
    shallow key "a" / wide "l0" / diamond "left"). 3.14t: normal public 340/567/445, inner executor 128/322/211,
    override public 460/709/518, ConduitMeld.meld 394/634/444, override door 200/442/254, dispatcher 179/404/224,
    plan 107/322/149. GIL: normal 312/559/381, inner 112/323/182, override public 424/659/468, ConduitMeld.meld
    365/588/403, door 177/390/218, dispatcher 149/364/185, plan 91/291/125. So on shallow (3.14t) the plan itself is
    cheaper than a normal build (A is not built); above it the dispatcher adds ~72 ns (frame, 3 defaults,
    tuple(ov), dict get), the door ~21 ns, ConduitMeld.meld's full lane ~194 ns (normal melds skip it through the
    fast meld door: pool read, capability/spellspace/validation/resolution/hook/gate checks, context read,
    (instance, created) tuple) and Conduit.meld's wrapper ~66 ns (paid by both).
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/override_entry_layers.py:1-67
  - src/melder/aether/conduit/meld/conduit_meld.py:259-600
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:176-200
  IMPACT: The remaining override-vs-normal gap (~120 ns of ~460) is meld entry, not plans: an override fast door in
    ConduitMeld.meld is the big lever (Meld runtime, melder_1's race-fix file); dispatcher inlining is the small
    in-scope lever.
  NEXT: Read the override door (creation_runtime_door_compiler) and micro-measure the dispatcher's parts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T14:33:53Z
  TYPE: DECISION
  CLAIM: Override melds get the fast meld door (S3 exit gate: design section 14 wants root-key overrides at >=90% of
    normal; public override melds sit at ~74% on shallow, and the gap is ConduitMeld's full lane). melder_1's race lane
    that last edited these files closed at 14:24:40Z (owner accepted). Change: in ConduitMeld.meld and
    SpellSpaceMeld.meld, an id-string meld with a non-empty dict payload uses the existing fast-door entry and the same
    guard ladder (no meld hooks, door epoch, context identity, no spellbook validation) and calls the live
    `_overrides_executor(self, payload)[0]`; any miss, a list/tuple payload or an empty dict takes today's full lane.
    The full lane's non-dynamic, no-hook override branch also builds the entry after success when the spell has no
    mutation override (belt and braces: automatic spells cannot hold one - pinned by
    test_component_fast_door_mutation_override_requires_dynamic_pin). The fast-door dispatcher adds no lock and no
    new state. FILES: src/melder/aether/conduit/meld/conduit_meld.py, spellspace_meld.py, meld.py (registry
    docstring); tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py (the "skipped for
    override payloads" test flips to "serves dict payloads"; new guard-trip, full-lane-payload, key-error and
    spellspace cases); patch doc component_patch_override_meld_fast_door.md.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:259-600
  - src/melder/aether/conduit/meld/spellspace_meld.py:330-530
  - src/melder/aether/conduit/meld/meld.py:60-110
  - src/melder/aether/spellbook/spell.py:770-802
  - tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py:273-302
  IMPACT: About 150 ns off every warm override meld; no behavior change under the existing guard contract.
  NEXT: Write the patch doc, then implement on a fresh device copy with an A/B twin.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T14:37:01Z
  TYPE: FACT
  CLAIM: Override fast door implemented on the VM copy only (~/work/melder_fd; twin ~/work/melder_fdbase; script
    apply_fastdoor_edits.py, --check clean; patch doc component_patch_override_meld_fast_door.md written). 3.14t: unit
    aether 4145, component spellbook 764, conduit 268, component aether 1187 + 1 expected failure
    (test_component_fast_door_skipped_for_override_payloads pins the old "override payloads take the full lane"
    contract; to flip to "dict payloads are served by the fast lane"). Device tree NOT touched. Paused on an owner
    interrupt: owner-run test_overrides_all.py solo graph (bound existing object, plain meld, 15 s) melder 176,479
    steps/s vs dependency-injector 369,982, lagom 346,628, dishka 279,292, injector 237,972.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_fastdoor_edits.py:1-166
  - benchmarks/testing_other_di/test_overrides_all.py:560-590
  IMPACT: Solo is the owner's current focus; the fast-door change resumes from the VM copy afterwards.
  NEXT: Measure the solo plain meld per layer (public meld, fast door, existing-creation door).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T14:37:20Z
  TYPE: MEASURE
  CLAIM: Owner run (owner machine, device tree with S3a, S3b-1, S3b-2 and S2a; test_overrides_all.py, 15 s, 1 thread),
    steps/s. solo: melder 176,479 vs dependency-injector 369,982, lagom 346,628, dishka 279,292, injector 237,972
    (last). shallow: melder 150,962 vs DI 173,291, lagom 148,256, dishka 143,935 (second). wide: melder 139,827 vs
    dishka 142,590, DI 123,424, lagom 106,060. diamond: melder 141,174 vs dishka 150,261, DI 142,097, lagom 120,886.
    deep: melder 24,393 vs dishka 19,762, DI 8,293, lagom 4,268 (first). Against the 12:30:41Z baseline: shallow
    123,953 -> 150,962, wide 96,838 -> 139,827, diamond 107,596 -> 141,174, deep 5,341 -> 24,393; solo 156,754 ->
    176,479. errors=0 everywhere.
  EVIDENCE: benchmarks/testing_other_di/test_overrides_all.py:546-600
  IMPACT: Override graphs are now competitive; the override fast door (~150 ns off ~460 ns) should put shallow,
    wide and diamond ahead. Solo (plain meld of a bound existing object) is half of dependency-injector.
  NEXT: Measure the solo plain meld per layer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T14:39:54Z
  TYPE: MEASURE
  CLAIM: The solo gap is the benchmark's periodic full gc.collect() (DI_OVERRIDE_GC_MODE=periodic, every 2000 steps)
    over melder's import footprint, not the meld. Solo get_root() (meld + isinstance) 245 ns on 3.14t, 240 GIL.
    Full collection: bare interpreter 10k tracked / 0.25 ms; + benchmark module (no melder) 38k / 1.4 ms (~0.7 us per
    step); + `import melder` (576 melder modules, 20.5k functions, 20.7k code objects on 3.14t) 87k / 5.1 ms (~2.6 us
    per step); the conjured solo world adds ~500 objects. GIL: 30k / 2.1 ms vs 66k / 6.8 ms (1.0 vs 3.4 us per step).
    The benchmark module does not import melder and no conftest loads for benchmarks/, so the four libraries that
    run solo before melder collect a heap without it; every later graph pays the same footprint for all libraries.
    melder with gc disabled: solo 1,591,665 and shallow 1,023,776 steps/s (periodic: ~176k and ~213k).
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/solo_cost.py:1-35
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/gc_footprint.py:1-34
  - benchmarks/testing_other_di/test_overrides_all.py:690-730
  IMPACT: Owner-visible solo ranking is mostly harness order plus melder's import footprint (a real cost: every full
    collection in a user process pays ~2-5 ms more with melder imported).
  NEXT: Ask the owner: import all libraries before timing (harness fairness) and/or open an import-footprint lane;
    meanwhile finish the override fast door.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T14:39:54Z
  TYPE: DECISION_REQUEST
  CLAIM: (1) Make the override benchmark fair on solo by importing every library (melder included) before the first
    timed run - a one-line warm import in test_overrides_all.py, owner's file. (2) Open a separate lane to cut
    melder's import footprint (576 modules at `import melder`; Aether boots Crystallizer, MutationResearch and Nexus
    eagerly), which lowers full-collection cost and import time for users; broader than this story. (3) Leave both.
  EVIDENCE: tickets/tasks/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: Decides whether solo is fixed by measurement (1), by product change (2), or accepted (3).
  NEXT: Resume the override fast door while the owner decides.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T14:44:37Z
  TYPE: DECISION
  CLAIM: Owner on the solo/GC request: "yeah just investigate we want to keep the melder eager import". melder_0
    reads this as: no lazy-import lane and no benchmark change yet; investigate what in the eager import makes
    collections expensive (which modules and object kinds, whether 3.14t pays it on every automatic collection) and
    report options that keep the eager import.
  EVIDENCE: tickets/tasks/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: Solo work is investigation only; the override fast door continues (already decided, 14:33:53Z).
  NEXT: Finish the fast-door GIL validation, then attribute the import footprint by module and object kind.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T14:52:17Z
  TYPE: MEASURE
  CLAIM: Solo/GC investigation (VM, fast-door copy, all five libraries installed with uv, test_overrides_all.py 3 s,
    3.14t), steps/s. A as the owner runs it: solo DI 634,700, lagom 542,755, injector 381,023, dishka 103,549 (outlier),
    melder 228,474. B with melder imported before the first timed run (simulated, owner file untouched): solo DI
    225,600, lagom 232,466, dishka 228,946, melder 230,119 - a tie; the solo ranking was run order plus import
    footprint. C with gc disabled (pure resolve): solo DI 3,411,115, lagom 2,443,859, dishka 1,794,865, melder
    1,585,857; shallow DI 1,477,217, dishka 1,428,244, melder 1,076,561; wide dishka 971,508, melder 838,891, DI 592,924;
    diamond dishka 1,238,717, melder 1,002,761, DI 949,304; deep melder 38,488, dishka 30,058, DI 10,759. So a real
    resolve gap remains on solo (~2x DI) and shallow (~1.4x), smaller on wide/diamond vs dishka. Footprint: `import
    melder` = 576 modules, 11,678 functions (plus as many code objects on 3.14t; top: nexus rift/acl/nexus ~3.6k,
    spellbook 2.0k, aetheric_frame 1.2k, conduit 1.0k). On 3.14t a YOUNG collection walks the whole heap: gen0 248 us
    before import vs 2,434 us after (full 2,647); GIL gen0 stays ~0.1 us, full 346 -> 6,118 us. gc.freeze() after
    import: 3.14t gen0/full 2,584/2,728 -> 653/693 us; GIL full 3,749 us -> 0.1 us.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/import_footprint.py:1-49
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/gc_footprint.py:1-34
  - benchmarks/testing_other_di/test_overrides_all.py:690-730
  IMPACT: Options that keep the eager import: warm-import in the harness (measurement fairness), gc.freeze() after
    import (opt-in API or documented recommendation; automatic would freeze the user's earlier objects too - owner
    call), and shaving the public meld path for the real solo/shallow gap.
  NEXT: Apply the override fast door to the device tree, then report to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T14:52:54Z
  TYPE: FACT
  CLAIM: Override fast door applied to the device tree after --check (both scripts) and notice M0-30 (melder_1, FYI;
    lane closed); all four files byte-identical to the validated copy. Validation on the copy: component fast-door file
    33 passed (6 new tests fail on the untouched twin, as intended); 3.14t unit spellbook 2151, component spellbook 764,
    integration spellbook 578, component aether 1197+1xf, unit aether 4145, conduit 268, multithreading 42,
    integration aether 716, experimentation 250, crystallizer 565/258, mutation_research 277/40/66, unit utilities 785;
    GIL unit spellbook 2151, component spellbook 764, integration spellbook 578, component aether 1197, unit aether
    4145, conduit 268, multithreading 42, experimentation 250. Public override meld (override_entry_layers.py, twin ->
    fast door, ns): 3.14t shallow 470 -> 418, wide 697 -> 660, diamond 504 -> 476; GIL 433 -> 387, 684 -> 615, 471 ->
    423. Normal melds unchanged within noise.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_fastdoor_edits.py:1-166
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_fastdoor_test_edits.py:1-350
  - src/melder/aether/conduit/meld/conduit_meld.py:420-460
  IMPACT: Warm override melds skip the full meld lane; remaining per-call overhead is the Conduit.meld wrapper,
    the override door tuple and the key-set dispatch.
  NEXT: Report the solo/GC investigation and the fast door to the owner; await the harness/gc.freeze decisions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T14:55:59Z
  TYPE: DECISION
  CLAIM: Owner: "yeah sure make sure imports are properly managed in that go ahead and fix that up we don't want
    gc.collect to run until the end of the wave library type". melder_0 reads: (1) test_overrides_all.py imports every
    library (melder included) before the first timed case, so all cases collect the same heap; (2) no collection runs
    inside a timed window - automatic GC is off during the loop and one gc.collect() runs when each library's case
    ends; (3) "yeah sure" also approves trimming the public meld path for the solo/shallow gap. gc.freeze() is not
    requested and is not added.
  EVIDENCE: benchmarks/testing_other_di/test_overrides_all.py:690-730
  IMPACT: The owner's benchmark measures resolve cost, not import-order-dependent collection cost.
  NEXT: Read test_overrides_all.py in full, then record the edit plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T14:56:49Z
  TYPE: PLAN
  CLAIM: Benchmark edit (benchmarks/testing_other_di/test_overrides_all.py only, read in full 1-765): (1) a
    module-scoped autouse fixture imports every supported library's modules (all five, whatever DI_LIBS selects) and
    collects once before the first case, so every case sees the same heap; builders keep their importorskip.
    (2) DI_OVERRIDE_GC_MODE defaults to "disabled"; GC is switched off by the main thread around the timed window
    (today each worker toggles the process-global flag, which races with threads > 1) and every case still collects
    once at its end in cleanup (all five cleanups already call gc.collect()); "periodic" and "none" stay available.
    (3) Fix the start race behind the "duration=0.00s steps=0" rows: _run_timed stores the stop time before it
    releases the start barrier (workers read it right after the barrier). Check first that no library leaves cyclic
    garbage per resolve large enough to matter over a 15 s window with GC off.
  EVIDENCE: benchmarks/testing_other_di/test_overrides_all.py:600-765
  IMPACT: Owner's benchmark compares resolve cost with import order and collection cost removed.
  NEXT: Measure cyclic garbage per resolve for all five libraries (GC off, then gc.collect() count).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T15:00:26Z
  TYPE: MEASURE
  CLAIM: Benchmark fix applied to the device (apply_bench_edits.py, byte-identical to the validated copy): all five
    libraries preloaded before the first case, GC off for the timed window by default (main thread; each case
    collects at its end in cleanup), stop time stored before the start barrier (the 0-step rows are gone). Before
    switching GC off: no library leaves cyclic garbage per warm resolve; the first melder deep override meld leaves
    6,135 objects once (plan compile), absorbed by warm-up. Fixed benchmark, 3.14t, 3 s, steps/s: solo DI 2,845,734,
    lagom 2,123,947, dishka 1,834,288, melder 1,585,267, injector 860,601; shallow dishka 1,465,775, DI 1,370,718, melder
    1,082,389, lagom 870,041; wide dishka 919,956, melder 853,233, DI 588,180; diamond dishka 1,152,279, melder
    990,192, DI 948,929; deep melder 37,516, dishka 29,462, DI 10,304. GIL 2 s: solo DI 4,757,485, lagom 3,535,398,
    dishka 3,223,621, melder 2,888,725; shallow dishka 2,072,746, melder 1,577,374, lagom 1,197,568, DI 1,168,148.
    threads=2 (3.14t) runs clean. 25 passed.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_bench_edits.py:1-213
  - benchmarks/testing_other_di/test_overrides_all.py:600-809
  IMPACT: The owner's benchmark now measures resolve cost. Remaining gaps: solo (DI ~1.8x), shallow and diamond vs
    dishka (~1.2-1.35x).
  NEXT: Profile the solo public meld path (Conduit.meld wrapper, ConduitMeld fast arm, existing-creation door).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:02:43Z
  TYPE: PLAN
  CLAIM: Public meld trim (owner "yeah sure", 14:55:59Z). Solo per layer (solo_layers.py, 3.14t / GIL ns): existing
    door 36/30, ConduitMeld.meld fast arm +111/+102, Conduit.meld wrapper +96/+57 (check_cleaned call, argument
    juggling, four-keyword call). Prototype (solo_trim_prototype.py): V1 inline cleaned check + positional call
    209 -> 171 ns (3.14t), V2 V1 plus the fast-door read inlined at the Conduit 209 -> 111 (GIL 208 -> 103); plain
    shallow 343 -> 228. Change (V2): Conduit.meld, for an automatic conduit and an id meld with no spell/spellframe/
    binding, reads `self._meld._fast_meld_doors` with the same guard ladder and both arms (plain; non-empty dict ->
    live `_overrides_executor(...)[0]`), only guard reads inside the AttributeError try; a miss calls the door
    positionally (`meld(spell_id)` / `meld(spell_id, spell_override=override)`); everything else keeps today's path,
    cleaned check first. FILES: src/melder/aether/conduit/conduit.py (Conduit.meld), meld.py (registry docstring:
    three readers keep identical guards), the fast-door component tests (direct ConduitMeld arm, cleaned conduit via
    spell_id=, Conduit-arm guard trips through existing tests), patch doc component_patch_override_meld_fast_door.md.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/solo_layers.py:1-40
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/solo_trim_prototype.py:1-70
  - src/melder/aether/conduit/conduit.py:4417-4520
  IMPACT: About 100 ns off every warm automatic id meld, plain or override.
  NEXT: Implement on the VM copy with the anchored script; run suites; measure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:11:20Z
  TYPE: MEASURE
  CLAIM: Public meld trim applied to the device (apply_conduit_trim_edits.py; four files byte-identical to the
    validated copy; patch doc updated). Tests: fast-door component file 36 (3 new: Conduit and door arms agree,
    cleaned conduit via spell_id=, spell+spell_id ValueError); three unit facade tests replaced `_meld` with a bare
    MagicMock and pinned the keyword forwarding - they now give the mock door an empty `_fast_meld_doors` and the
    explicit-id test asserts the positional call. Suites 3.14t: unit spellbook 2151, component spellbook 764,
    integration spellbook 578, component aether 1200+1xf, unit aether 4145, conduit 268, multithreading 42,
    integration aether 716, experimentation 250, crystallizer 565/258 (+ known file_backed_morph x4), mutation_research
    277/40/66, unit utilities 785, live_sim 1+1xf; GIL: unit spellbook 2151, component spellbook 764, integration
    spellbook 578, component aether 1200, unit aether 4145, conduit 268, multithreading 42, experimentation 250.
    Fixed benchmark 3.14t 3 s (steps/s, before -> after trim): melder solo 1,585,267 -> 1,691,852, shallow 1,082,389
    -> 1,145,880, wide 853,233 -> 893,279, diamond 990,192 -> 1,093,955, deep 37,516 -> 38,316. Why the benchmark
    moves less than the main-thread probe (solo 209 -> 111 ns): the benchmark resolves on a worker thread, and on
    3.14t every reference a non-owner thread takes to a main-thread object is an atomic (biased reference counting).
    Same call main vs worker thread (thread_origin_cost.py): 3.14t melder solo 188 vs 402 ns, shallow 434 vs 647;
    dependency-injector solo 69 vs 139; GIL no difference (melder solo 184/180, shallow 402/413; DI shallow 606/600).
    Trim from a worker thread: solo 556 -> 404, shallow 730 -> 670 ns. No Python-level immortal/deferred refcount
    exists (sys has only _is_immortal; gc.freeze() does not change it).
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_conduit_trim_edits.py:1-268
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/thread_origin_cost.py:1-38
  - src/melder/aether/conduit/conduit.py:4520-4580
  IMPACT: Remaining free-threaded gap is per-object shared refcounting on the meld path; the lever is touching fewer
    shared objects per warm meld.
  NEXT: Report to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:27:44Z
  TYPE: UNKNOWN
  CLAIM: Owner reports "overrides are not running on my side". The device tree itself, run from the Linux VM
    (3.14t, 1 s per case), passes all 25 benchmark cases with errors=0 and the override graphs validated every 200
    steps; the repo has no pytest warning filters. Cause on the owner's Windows run is UNKNOWN until the command and
    output are seen. That run wrote src/melder/__melder_cache__/__conjure_cache__/di-overrides/di-overrides.melc at
    15:26:36Z on the owner's disk (cache; regenerated on demand); ~500 other cache files changed around 15:25Z, which
    looks like a test run on the owner's machine.
  EVIDENCE: benchmarks/testing_other_di/test_overrides_all.py:600-809
  IMPACT: Blocks the owner-machine comparison of the benchmark fix and meld trims.
  NEXT: Get the owner's command, Python build and output (traceback or the override-perf lines).
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T15:36:37Z
  TYPE: MEASURE
  CLAIM: Owner run of the fixed benchmark (owner machine, device tree with all trims, 15 s), steps/s: solo DI 2,876,398,
    lagom 2,029,141, dishka 1,081,947, melder 727,846, injector 658,150; shallow DI 1,092,498, dishka 1,093,629, melder
    898,585, lagom 673,238; wide dishka 714,728, melder 675,935, DI 376,543; diamond dishka 925,011, melder 836,214, DI
    759,756; deep melder 29,509, dishka 22,519, DI 7,534. All errors=0 (the earlier "not running" is resolved).
    Melder's "solo" is not an override: the benchmark binds the object as an existing creation and melds it plainly;
    the door is `_spell.user_created_object` (a slot) and costs ~22 ns - the rest is the public meld lane plus, on
    3.14t, atomic reference counts from the worker thread on ~10 main-thread-owned objects. Owner per-step melder
    1.37 us vs DI 0.35 us (my VM 0.59 vs 0.29): the gap is larger on the owner machine, cause UNKNOWN until
    thread_origin_cost.py runs there. The owner's `init=` idea: key-set plans already pass root values straight into
    the root constructor and skip their dependencies (compiled once per key set); what an init route could remove is
    only the per-call dispatch (tuple of keys + plan lookup, ~66-72 ns) and the override door's (instance, True) tuple
    (~21-27 ns), and both can be removed from the override path itself without a new API.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:520-530
  - src/melder/aether/spellbook/spell.py:424-424
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/override_entry_layers.py:1-67
  IMPACT: Next levers: existing-object fast entry (return the object from the Conduit arm), instance-only override
    door with the key-set dispatch folded in; owner decision on an `init=` API vs these.
  NEXT: Answer the owner and ask which to build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:39:43Z
  TYPE: DECISION
  CLAIM: Owner: "the solo shouldn't actually be existing object, it should be me making a single object and overriding
    it ... lets go ahead and fix the existing object pathing then, and if override already works like that, then thats
    fine we can leave it that way". melder_0 reads: build the existing-object fast path now; no `init=` API and no
    override-path change for now. Solo's definition is open: override keys target constructor parameters only
    (override_key_resolver.py), so a no-parameter root cannot be overridden in melder; options sent to the owner
    (keep solo as fixed-object resolve, plain construction, or a new one-parameter "single" graph for all libraries).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/override_key_resolver.py:142-334
  - benchmarks/testing_other_di/test_overrides_all.py:266-340
  IMPACT: Existing-object work proceeds; benchmark solo change waits for the owner's pick.
  NEXT: Read how the fast-door entry is built and invalidated for existing creations, then plan the shortcut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T15:41:51Z
  TYPE: PLAN
  CLAIM: Existing-object shortcut. Facts: `user_created_object` is assigned only in Spell.__init__ and deleted in
    Spell.cleanup (which also deletes `_creation_context`, so a warm entry's guard read misses); the existing-creation
    door only returns that slot (or raises when it is None). Change: in the plain arm of all three warm-lane readers
    (Conduit.meld, ConduitMeld.meld, SpellSpaceMeld.meld), after the unchanged guards, read
    `door_spell.user_created_object`; when it is not None return it (after the pending-cache-emit check) without the
    door call; otherwise read the executor slot as today. Non-existing spells pay one read of a None slot (immortal,
    no atomic refcount). Override arms unchanged (an existing object with a payload keeps today's refusal).
    Prototype (existing_shortcut_prototype.py, solo): 3.14t main 163 -> 92 ns, worker 340 -> 227; GIL 147 -> 80.
    FILES: src/melder/aether/conduit/conduit.py, meld/conduit_meld.py, meld/spellspace_meld.py, meld/meld.py (registry
    docstring); tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py (existing objects on
    all three readers with a poisoned door slot, same override refusal on both lanes, spell-hook guard trip).
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:596-640
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:520-530
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/existing_shortcut_prototype.py:1-64
  IMPACT: Solo (existing object) meld about 40% cheaper on both builds.
  NEXT: Write apply_existing_shortcut_edits.py, run it on a fresh device copy, then the suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:45:59Z
  TYPE: FACT
  CLAIM: Process record and consumed mail. (1) After the compaction the 15:41:51Z PLAN note was written before
    REONBOARD, and its prototype range read 1-72 on a 64-line file; the range is corrected in place to 1-64 (factual
    fix), REONBOARD then completed and the owner re-certified melder_0. (2) Consumed M1-14 (melder_1, conjure error
    reporting lane): it edits spellbook_creation_system.py only in _enforce_conduit_resolution_valid and the gated raise
    of run_resolution_phases_for_target_spell, spellbook_validation_error.py and the Phase-4/Phase-6 validation
    strategies, and not meld.py, conduit_meld.py or spellspace_meld.py. The existing-object shortcut touches conduit.py,
    conduit_meld.py, spellspace_meld.py, meld.py and the fast-door test file: no overlap, no reply needed (ACK not
    requested). (3) Consumed M2-1 (melder_2 checked in; since then routed to gauntlet_runtime_speed): nothing to act on.
  EVIDENCE:
  - context_compass/mailbox_board.md:88-94
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/existing_shortcut_prototype.py:1-64
  IMPACT: File ownership stays clear for the shortcut; the plan note's evidence is valid again.
  NEXT: Add the existing-object section and mapping to the fast-door patch doc, then write the edit script.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T15:49:02Z
  TYPE: FACT
  CLAIM: Existing-object shortcut verified equivalent before code. A non-None `user_created_object` comes only from
    Bind passing `existing_object=spell if is_instance` (Instance/Other binding profiles); those profiles are siblings
    of the class and callable profiles, so `_determine_spell_type` returns EXISTING_CREATION* for them, the artifact
    processor routes them to "existing_creation", and that door's whole body is `_spell.user_created_object` plus the
    None refusal. Fast-door entries exist only after a successful non-dynamic full-lane meld (capability, spellspace,
    validation and resolution already passed), so returning the slot after the guards equals calling the door. Cleanup
    deletes `_creation_context` (guard read misses) before `user_created_object`, and a meld racing cleanup behaves as
    today (the door read the same slot). Patch doc updated (After, Behavior Deltas, Validation, Rollback). Mapping:
    After "Existing objects" -> plain arms of ConduitMeld.meld, SpellSpaceMeld.meld, Conduit.meld plus the meld.py
    registry docstring -> fast-door component tests (identity with a poisoned slot on all three readers, override
    refusal equal on both lanes, spell-hook guard trip, removed spell) and solo/shallow timings.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:719-787
  - src/melder/aether/spellbook/bind/bind.py:1164-1232
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:115-140
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:497-530
  - src/melder/aether/spellbook/spell.py:560-630
  - src/melder/aether/conduit/meld/conduit_meld.py:365-460
  - system_docs/patches/active/override_site_plan_2026_09_26/component_patch_override_meld_fast_door.md:35-73
  IMPACT: No behavior delta; the change is a pure fast-path skip of one frame.
  NEXT: Snapshot a fresh device copy with a twin, write apply_existing_shortcut_edits.py, run it with --check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T15:52:45Z
  TYPE: FACT
  CLAIM: Existing-object shortcut implemented on a fresh device copy (~/work/melder_ex; untouched twin
    ~/work/melder_exbase) by apply_existing_shortcut_edits.py; --check is clean on both the copy and the device tree.
    Edits: plain arms of ConduitMeld.meld and SpellSpaceMeld.meld (init `existing_instance = None`; inside the guard
    branch read `door_spell.user_created_object`, take the executor only when it is None; return the object after the
    pending-cache-emit check), Conduit.meld's arm (same, plain arm only), three Contract docstrings and the Meld
    registry docstring. Four new component tests: identity on all three readers with the context's no-override slot
    replaced by a raising stub and no pool read; the override refusal (MeldExecutionError "already exists") equal on
    fast and full lanes; spell hooks trip the guard and fire; a removed spell fails like the full lane. 3.14t: the
    fast-door file passes 40; on the twin the skip test fails (door entered) and the other three pass, as intended.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_existing_shortcut_edits.py:1-420
  - src/melder/aether/conduit/meld/conduit_meld.py:365-420
  - src/melder/aether/conduit/conduit.py:4527-4580
  IMPACT: Behavior is pinned before the full suites and timings.
  NEXT: Read the 3.14t and GIL suite logs, then time solo and a non-existing plain meld on both trees.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:02:13Z
  TYPE: MEASURE
  CLAIM: The slot-read shape (applied on ~/work/melder_ex) passes every suite but taxes ordinary plain melds. Suites
    with it, 3.14t: unit spellbook 2158, component spellbook 764, integration spellbook 581+2s+2xf+2xp, component aether
    1204+1xf, conduit 268, unit aether 4145, multithreading 42, integration aether 716, experimentation 250+4s, unit
    utilities 795+2s+7xf, crystallizer 565/258+3xf, mutation_research 277/40/66, live_sim 1+1xf, component utilities
    21+43s; GIL: the same counts on the first nine. Failures only crystallizer file_backed_morph x4 (known) and
    test_generated_build_assets_are_stamped_for_the_live_version, which also fails on the untouched twin (package is
    now 0.2.57, assets stamped 0.2.56; not this change). Public meld timings, 3 runs: existing object 3.14t main
    191-241 -> 164-172 ns, worker 411-483 -> 344-371; GIL main 177-180 -> 153-173; but class unique reuse on 3.14t main
    +8 to +16 ns in every run. In-process shape comparison (same process, interleaved, median of 9 x 200k, main thread):
    3.14t existing -30.3 / unique +8.4 / many +8.3 ns for the slot read; -25.9 / -0.8 / 0.0 for a bool flag carried in
    the entry (read the slot only for flagged entries); GIL -21.8 / +9.8 / +9.6 vs -18.2 / +1.7 / -1.4. Capturing the
    object itself in the entry was prototyped and rejected: spell removal does not clear fast-door entries (only the
    graduation path clears them), so a stale entry would keep a removed spell's user object alive.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/existing_shortcut_shapes.py:1-145
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/existing_shortcut_timing.py:1-69
  - tests/unit/melder/test_package_version_metadata.py:1-40
  - src/melder/aether/spellbook/spellbook.py:6815-6845
  IMPACT: The slot read costs ~5% on every non-existing warm plain meld; the flag shape removes that cost.
  NEXT: Record the shape decision and re-plan the edit script.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:02:13Z
  TYPE: DECISION
  CLAIM: Build the flag shape. Fast-door entries become `(spell, captured_context, captured_epoch,
    existing_object_entry)`, the bool computed as `target_spell.user_created_object is not None` by the four entry
    builders (ConduitMeld and SpellSpaceMeld, no-override and override branches). Plain arms of the three readers:
    inside the guards, a flagged entry reads `door_spell.user_created_object` (still inside the AttributeError try),
    others read the executor slot as before; after the try, a flagged hit returns the object and an unflagged hit calls
    the executor; the pending-cache-emit check is shared. Override arms unpack the flag and ignore it. Same files as the
    15:41:51Z plan; meld.py also gets the type (Tuple[..., bool]) and its entry comment corrected (it still says
    `creations_store` for the third element). Patch doc updated to the flag shape.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/existing_shortcut_shapes.py:80-110
  - src/melder/aether/conduit/meld/meld.py:285-300
  IMPACT: Existing objects keep ~85% of the slot-read gain with no cost to other spells and no retention change.
  NEXT: Reset the work copy from the device tree, rewrite apply_existing_shortcut_edits.py to the flag shape, rerun.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:10:38Z
  TYPE: MEASURE
  CLAIM: Flag shape (applied on ~/work/melder_ex by apply_existing_flag_edits.py) passes the same suites as the slot
    shape on 3.14t and GIL (identical counts; only file_backed_morph x4 and the 0.2.57 asset-stamp test fail, both also
    on the twin). Public timings still showed a residual on ordinary spells, so it was sized with many cross-process
    samples (unique_meld_timing.py: warm class-unique meld, 3.14t main thread, 8 alternating processes each, medians):
    twin 181.5 ns, flag checked inside the guards 187.7 (+6), flag checked only at the call site 184.4 (+3; guard code
    identical to today, the flagged hit reads `door_spell.user_created_object` where the door would have read it).
    Existing object (existing_shortcut_timing.py, 3.14t, 2 runs): twin main 187-192 / worker 401-415 ns; guard-check
    173 / 355-361; call-site check 169-173 / 368-373. GIL (guard-check shape): existing 177-185 -> 159-164 ns, other
    spells within noise.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/unique_meld_timing.py:1-33
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/existing_shortcut_timing.py:1-69
  IMPACT: The call-site check costs ordinary warm melds ~3 ns (within per-process noise) and keeps ~90% of the
    existing-object gain on the main thread.
  NEXT: Record the shape decision, update the flag script to the call-site check, rerun tests and suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:10:38Z
  TYPE: DECISION
  CLAIM: Final shape: entries carry the existing-object bool (as the 16:02:13Z decision), but the guard code stays
    exactly as today; only the call site of each plain arm branches: a flagged hit takes
    `door_spell.user_created_object`, others call the executor. The read sits outside the AttributeError try on
    purpose: the existing-creation door performs the same unguarded read, so a spell cleaned between the guards and
    the read raises the same AttributeError the door would. Ordinary spells matter more than existing objects, so
    the smaller cost on them wins over the extra ~10 ns of worker-thread gain the guard-check shape gave existing
    objects.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/unique_meld_timing.py:1-33
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:520-530
  IMPACT: Smallest diff of the three shapes (unpack, builders, call sites, docs); no behavior delta.
  NEXT: Edit apply_existing_flag_edits.py (drop the in-guard reads, branch at the call sites), rerun on a reset copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:17:25Z
  TYPE: MEASURE
  CLAIM: Final shape validated on a fresh device copy (~/work/melder_ex, apply_existing_flag_edits.py; twin
    ~/work/melder_exbase). Fast-door file + Conduit facade unit tests 78 on both builds. 3.14t: unit spellbook 2158,
    component spellbook 764, integration spellbook 581+2s+2xf+2xp, component aether 1204+1xf, conduit 268, unit aether
    4145, integration aether 716, experimentation 250+4s, unit utilities 795+2s+7xf, crystallizer 565/258+3xf,
    mutation_research 277/40/66, live_sim 1+1xf, component utilities 21+43s, multithreading 41 + 1 flake
    (test_racing_every_lazy_load_at_once_is_consistent, system-document view, no meld involvement: 0 failures in 64
    reruns on either tree; cause UNKNOWN). GIL: the same counts on the thirteen suites run. Known failures only
    (file_backed_morph x4; 0.2.57 asset stamp, also on the twin). Timings, twin -> change: existing object 3.14t main
    191-234 -> 170 ns, worker 415-442 -> 368-388; GIL main 179-187 -> 160-161, worker 180-186 -> 160-163; ordinary class
    unique meld (8 alternating processes, 3.14t main) median 182.7 -> 184.7 ns (+2, within noise). Owner benchmark
    (test_overrides_all.py, melder, 3 s, 3.14t): solo 1,801,565 / 1,807,806 -> 1,897,589 / 1,896,701 steps/s (+5%),
    shallow 1,170,215 / 1,195,363 -> 1,177,583 / 1,169,147 (unchanged).
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_existing_flag_edits.py:1-435
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/existing_shortcut_timing.py:1-69
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/unique_meld_timing.py:1-33
  - tests/integration/melder/multithreading/test_multithreading_system_document_view.py:166-193
  IMPACT: Existing-object melds ~10-12% faster on both builds with no measurable cost to other spells.
  NEXT: Confirm the five device files still match the snapshot, --check, apply, verify byte-identity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:20:38Z
  TYPE: FACT
  CLAIM: Existing-object fast path applied to the device tree after --check (apply_existing_flag_edits.py); all five
    files are byte-identical to the validated copy: conduit.py (Conduit.meld), meld/conduit_meld.py,
    meld/spellspace_meld.py, meld/meld.py (registry docstring, entry comment and type) and the fast-door component test
    file; patch doc updated to the final shape. Uncommitted, like S3. Process lapse: M2-4 (melder_2, 15:45:57Z, asked
    which meld files I would write; ACK requested) arrived after my 15:45:38Z mailbox pass and was not read before the
    apply; melder_2 had not edited those files (their P1 touched only generalized_manifest_no_overrides_compiler.py plus
    two new tests), so nothing collided; answered now (M0-31). Combined device state (my change + melder_2's P1), fresh
    copy: fast-door file 40; 3.14t unit spellbook 2178, component spellbook 771, integration spellbook 581+2s+2xf+2xp,
    component aether 1204+1xf, conduit 268, multithreading 42, unit aether 4145, integration aether 716, experimentation
    250+4s; GIL the same counts on the six suites run. Consumed F0-15 (fable_0): I-1 structural snapshot patch docs in
    review; planned generation 15 after my generation 14, touching caching_system.py, spellbook_creation_system.conjure,
    compiler_phase_3.py and spell.py (the DAG object), with notices before edits; my change reads only
    `Spell.user_created_object`, which I-1 does not list. Consumed M2-5 (melder_2 P1): generalized no-overrides step
    plans pass leading dependency params positionally (class call 170 -> 77 ns on 3.14t) and positional-only dependency
    params now meld; the same lever applies to the site-plan emitters (S2b candidate).
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:380-460
  - src/melder/aether/conduit/conduit.py:4545-4585
  - tickets/tasks/2026-09-26_emit_positional_constructor_args_task.md:1-161
  - tickets/stories/2026-09-26_structural_snapshot_story.md:1-298
  - system_docs/patches/active/override_site_plan_2026_09_26/component_patch_override_meld_fast_door.md:35-78
  IMPACT: Existing-object pathing is done in the tree; S2b is next, with P1's positional lever to fold into plan emission.
  NEXT: Report to the owner; then plan S2b (file list and patch docs first).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:25:38Z
  TYPE: DECISION
  CLAIM: Owner: "in that specific overrides test please make sure its actually using an override not a user_defined
    object ... fix that too but notch the version because of your win and lets keep moving". melder_0 reads: (1) the
    solo graph in test_overrides_all.py must meld with a real `override=`. A melder override targets constructor
    parameters only, and today's SoloRootA has none, so solo becomes `SoloRootA(leaf: SoloLeafA)` with SoloLeafA
    overridden in every library (the builders are generic over the spec, as for shallow/wide/diamond/deep): one object
    is built per step with the supplied input; melder melds `override={"leaf": obj}`. The existing-object mode and its
    two branches in the melder builder go away with it (no other graph used them). (2) Notch the version one step as
    the repo's notch tasks do: __version__ 0.2.58 -> 0.2.59 (committed 0.2.57; melder_1's lane took 0.2.58 at 15:52Z),
    release header to 0.2.59, a release section for this lane's in-tree override work (only behavior the tests pin:
    B1, B5, B7, B8, unchanged key errors; cache generation 14; the fast lanes), the now-obsolete "One path still renders
    values the old way" bullet retired (S3a delivers descriptor values by identity, 13:42:48Z), and the packaging
    bullet's version moved to 0.2.59. No asset rebuild (owner approval; the stamp test keeps failing until then).
    FILES: benchmarks/testing_other_di/test_overrides_all.py, src/melder/__version__.py,
    release_docs/next_version_release.md.
  EVIDENCE:
  - benchmarks/testing_other_di/test_overrides_all.py:97-102
  - benchmarks/testing_other_di/test_overrides_all.py:256-325
  - benchmarks/testing_other_di/test_overrides_all.py:545-600
  - src/melder/__version__.py:1-12
  - release_docs/next_version_release.md:25-47
  - tests/component/melder/spellbook/test_spellbook_component_override_key_set_plans.py:232-400
  IMPACT: Solo compares one supplied-input construction across all five libraries; the version carries the win.
  NEXT: Edit the benchmark on a VM copy, run solo for all five libraries on 3.14t and GIL, then apply.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:28:28Z
  TYPE: MEASURE
  CLAIM: Solo now melds with a real override and the version is notched. Benchmark (apply_solo_override_edits.py,
    byte-identical on the device): SoloRootA(leaf: SoloLeafA), leaf overridden in all five libraries, melder
    `override={"leaf": obj}`; the existing-object mode is gone. Fresh combined copy, 2 s, steps/s, 3.14t: DI 1,953,612,
    dishka 1,611,087, melder 1,299,995, lagom 1,141,999, injector 96,544; GIL: dishka 2,493,065, melder 1,987,143, DI
    1,958,533, lagom 1,583,579, injector 114,405. Full run (1 s, 3.14t) 25 passed, errors=0: shallow melder 1,216,874 vs
    dishka 1,478,268 / DI 1,430,564; wide dishka 981,976 / melder 922,222; diamond dishka 1,212,876 / melder 1,117,148;
    deep melder 36,346 / dishka 28,519. __version__ 0.2.58 -> 0.2.59; release note header 0.2.59, new sections
    "Overrides build only what you did not supply" and "Faster warm melds" (claims from the 12:30:41Z/14:37:20Z owner
    runs, the 13:41:25Z conjure measure and today's timings), fable_0's obsolete bullet retired (F0-14), packaging
    bullet 0.2.59. Version tests: only the asset-stamp test fails (assets 0.2.56; owner-approved rebuild pending).
    Creation caches rebuild once on first use under 0.2.59 (release-bound admission, generation 9 rule).
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_solo_override_edits.py:1-113
  - benchmarks/testing_other_di/test_overrides_all.py:97-112
  - release_docs/next_version_release.md:1-80
  - src/melder/__version__.py:12-12
  IMPACT: The overrides benchmark compares real overrides in every graph; 0.2.59 carries the override work.
  NEXT: Notices to fable_0, melder_1, melder_2; report; then S2b discovery (plan, patch docs, file list before code).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:29:25Z
  TYPE: DECISION_REQUEST
  CLAIM: S2b overlaps melder_2's lane. S2b (design v2 section 13) moves the normal lane's executors onto the site-plan
    lowering's empty-key-set plans (nested-miss form, B2 constructor order), which replaces the output of
    generalized_manifest_no_overrides_compiler.py for normal melds. melder_2 (gauntlet_runtime_speed, owner-assigned)
    applied P1 to exactly that emitter at 16:16Z and is profiling the warm meld and SpellSpace path for more levers.
    Options: (1) S2b proceeds in this lane and folds P1's positional arguments into the lowering; melder_2 keeps to
    meld entry and SpellSpace costs and hands emitter levers to this lane (recommended: one emitter, one owner);
    (2) S2b waits until melder_2's cost map and candidates land, then the owner splits the emitter work; (3) S2b moves
    to melder_2's lane. Separately recorded: git run on the device mount must use GIT_OPTIONAL_LOCKS=0 and read-only
    commands (standing note); melder_0 ran git log/show/diff --stat at 16:23-16:28Z without it - no index.lock was left
    and .git/index is unchanged since 16:04:19Z.
  EVIDENCE:
  - tickets/tasks/2026-09-26_emit_positional_constructor_args_task.md:59-62
  - attention_board.md:147-150
  - artifacts/melder_override_design_20260926/design_v2.md:403-419
  IMPACT: Avoids two agents rewriting the same normal-lane emission.
  NEXT: Owner picks; S2b discovery (read-only) can start meanwhile.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:31:17Z
  TYPE: DECISION
  CLAIM: Owner: "yeah continue 1". S2b stays in this lane: normal melds move onto the site-plan lowering's
    empty-key-set plans behind the parity gate, and melder_2's P1 positional arguments are folded into the lowering.
    melder_2 keeps to meld entry and SpellSpace costs and hands code-emission levers to melder_0 (notice M0-35).
  EVIDENCE: tickets/tasks/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: One owner for normal and override code emission.
  NEXT: Read the lowering, the P1 emitter and both families' normal-lane hydration, then write the S2b plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:36:56Z
  TYPE: FACT
  CLAIM: S2b discovery. (1) B2 waste is real today: G1 Root(a: A many, s: S upc(x: X many)) and G2 (S reached through
    P and Q) build X on every warm meld and drop it (warm counts X=1, S=0). (2) A shared site's transient child has one
    site however many paths reach the shared site (G2: X is (X, 5) once), so a many site has exactly one consumer
    and multi-consumer sites are always shared. (3) The lowering already passes operands positionally up to the first
    omitted parameter (`SitePlanEmission._call_arguments`), so P1's lever is in it. (4) Today's generalized normal lane
    (generalized_manifest_no_overrides_compiler.emit_step_plan_source) is straight-line providers-first with closure
    aliases; extras: an unrolled transient lane (all-many rows, none registering) and an opt-in singleton warm-tail
    specialization (`generalized_singleton_specialization_enabled`, default False) whose body and deopt target come
    from that compiler. (5) Hydration builds the normal inner executor at first meld; creation caches hold manifests,
    not code, so a hydration-only change needs no cache generation.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/s2b_shape_probe.py:1-103
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:653-720
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:111-315
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:250-340
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:470-476
  IMPACT: Nesting is well defined (a many site's home is its one consumer's); B2 removes real work on warm melds.
  NEXT: Record the S2b-1 plan and file list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:36:56Z
  TYPE: PLAN
  CLAIM: S2b in two steps. S2b-1 (this step, override plans only; normal lane unchanged): nested shared misses (design
    L1/L3, B2) in SitePlanEmission. Placement over kept steps, consumers before providers: the root is top level; a
    many site lives where its one consumer is built (inside the consumer's miss when the consumer is shared, else the
    consumer's home); a shared site lives at the lowest context common to all its consumers; a shared site that
    carries a winning override is pinned to top level, so today's P2 refusal and its build-and-publish stay exactly
    as they are (a rule under a stored parent is never silently skipped). Each shared site emits an inline hit read at
    its home and an out-of-line `_miss{i}(meld, ov, c{i}, ...)` that takes the build guard, rechecks, builds the
    sites homed inside it in step order, constructs, publishes and returns; outer values arrive as arguments
    (`instance_results` in dict mode, `args` when read, `many_store` recomputed per function). Warm hits unchanged;
    a stored shared site's children are no longer built. S2b-2 (next): normal lane on the lowering's empty-key-set
    plan for both families (hydrators and runtime), measured against today's inner executors (parity gate), with
    the transient lane and opt-in specialization kept or ported by measurement; separate plan note and file list.
    FILES (S2b-1): src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py;
    tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py;
    tests/component/melder/spellbook/test_spellbook_component_override_key_set_plans.py; code-description patch.
  EVIDENCE:
  - artifacts/melder_override_design_20260926/design_v2.md:124-146
  - artifacts/melder_override_design_20260926/design_v2.md:316-330
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:870-940
  IMPACT: Override plans on graphs with shared sites stop building discarded children; S2b-2 reuses the same emitter.
  NEXT: Update the code-description patch, then implement on a fresh VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:49:30Z
  TYPE: MEASURE
  CLAIM: S2b-1 tests written (apply_s2b1_test_edits.py) and applied on ~/work/melder_s2b: seven unit contracts (stored
    shared site skips its children; a shared site needed only inside T's miss is read there, stored T skips it, a
    stored S is reused by rebuilt P/Q; sibling misses receive one outer S; a supplied rule under a stored parent keeps
    P2 and is built and published when S is absent; T's guard is held while S builds inside it and a warm meld takes
    no lock; a contract-payload step inside a miss reads its inner many and the outer shared Z by key; a
    disposal-bearing many inside a miss registers in the innermost scope) and one component contract (Keeper(store:
    Store upc(leaf: Leaf many)); a warm override meld builds only Keeper, fresh and cached). Both files: 56 passed on
    3.14t. The same tests on the unchanged baseline (melder_s2bbase, restored after): 7 failed (the five B2/placement
    unit tests and both component variants), 49 passed - the sibling and pinned tests pass on both by design (they pin
    behavior that must not change).
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s2b1_test_edits.py:1-376
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s2b1_edits.py:1-429
  IMPACT: The tests fail for the regression S2b-1 removes and pass for the behavior it keeps.
  NEXT: Full suites on ~/work/melder_s2b on 3.14t and GIL.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:52:30Z
  TYPE: CONFLICT
  CLAIM: Design v2 L3/section 7 (a shared miss holds its guard across recheck, CHILDREN, construction and
    publication; risk R2) contradicts a pinned contract. Full 3.14t suites on ~/work/melder_s2b: unit spellbook 2189,
    component spellbook 773, integration spellbook 579+2s+2xf+2xp, conduit 268, component aether 1204+1xf all pass,
    but multithreading fails per_conduit-root-meld-override (the baseline twin passes it): thread A melds the upc
    consumer with an override; the unique service's miss now sits inside the consumer's miss and takes the service's
    Spell lock before building its many DeadlockLeaf, so A parks in that constructor holding the Spell lock and the
    competitor can never enter the service build ("thread A was never released"). The harness says every case must
    complete and forbids loosening it. The only compliant path: a miss builds its children BEFORE taking its guard
    (recheck, construct, publish stay under it). That keeps B2 (the hit read at the site's home still skips the
    children on warm melds) and today's locking (a plan holds at most one build lock, only across a site's own
    construction; R2 retired), at the cost of a cold race building and dropping the loser's children, which
    today's straight-line lowering already does on every cold race.
  EVIDENCE:
  - tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py:58-64
  - tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py:287-296
  - context_compass/artifacts/melder_override_design_20260926/design_v2.md:134-137
  - context_compass/artifacts/melder_override_design_20260926/design_v2.md:316-330
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s2b1_edits.py:332-332
  IMPACT: S2b-1 as designed would reintroduce a lock hazard class the 2026-09-25 fix removed (user code in a child
    constructor running under a parent's build lock); S2b-2 would spread it to normal melds.
  NEXT: Emit children before the guard in _emit_miss; update the class contract, the code-description patch
    (step 8, invariants) and the guard-order unit test; rerun all suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:52:30Z
  TYPE: FACT
  CLAIM: tests/experimentation/test_melder_creation_overrides_performance.py::test_melder_override_matrix_contracts
    [solo] fails on the baseline twin too (device state), so it is not S2b-1: it follows the 16:28Z solo benchmark
    change in this lane. Cause UNKNOWN until read.
  EVIDENCE: context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_solo_override_edits.py:1-113
  IMPACT: A regression from this lane is on the device; it must be fixed with S2b-1 or separately.
  NEXT: Read the matrix contract test after the S2b-1 guard fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:54:01Z
  TYPE: FACT
  CLAIM: The [solo] matrix failure is this lane's: `_root_inputs` in the experimentation override matrix still maps
    SoloRootA to no inputs (`return {}`), so `python_root_only` calls `SoloRootA()` and raises "missing 1 required
    positional argument: 'leaf'" since the 16:28Z benchmark gave the root a `leaf` parameter. The module docstring
    also still calls the benchmark's solo an existing-singleton case. Fix (PLAN, file list):
    tests/experimentation/test_melder_creation_overrides_performance.py only - `_root_inputs` returns
    `{"leaf": root.leaf}` for SoloRootA (so solo gets the root_one/root_args cases like the other graphs) and the
    docstring sentence is corrected; applied by apply_solo_matrix_test_edits.py. Separately, the S2b-1 guard fix
    (CONFLICT above) is applied on a fresh ~/work/melder_s2b: lowering unit + component + all 12 lock-order deadlock
    cases, 68 passed on 3.14t.
  EVIDENCE:
  - tests/experimentation/test_melder_creation_overrides_performance.py:135-147
  - tests/experimentation/test_melder_creation_overrides_performance.py:236-259
  - tests/experimentation/test_melder_creation_overrides_performance.py:12-16
  - benchmarks/testing_other_di/test_overrides_all.py:102-110
  IMPACT: Restores the matrix contract for solo; no library change.
  NEXT: Write and apply the edit on the work copy, then run all suites on 3.14t and GIL.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T16:58:50Z
  TYPE: MEASURE
  CLAIM: S2b-1 with the guard fix, its tests and the solo matrix fix, on a fresh ~/work/melder_s2b (reset from the
    melder_s2bbase twin; apply_s2b1_edits.py, apply_s2b1_test_edits.py, apply_solo_matrix_test_edits.py, each --check
    first). 3.14t and GIL identical: unit spellbook 2189, component spellbook 773, integration spellbook
    579+2s+2xf+2xp, experimentation 250+4s, component aether 1204+1xf, conduit 268, multithreading 42 (all 12
    lock-order deadlock cases), unit aether 4145, integration aether 716. Remaining 3.14t dirs: utilities 795+2s+7xf,
    mutation_research 277/40/66, component utilities 21+43s, unit crystallizer 565, integration crystallizer 258+3xf,
    live_sim 1+1xf, root unit files 144 passed. Failures, none from this change: the asset-stamp test (assets 0.2.56),
    crystallizer file_backed_morph x4 (known), and test_system_documents_builder x2, which fail on the baseline twin
    too because VM work copies carry no context_compass/system_docs for the builder to ingest (environment).
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s2b1_edits.py:1-440
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s2b1_test_edits.py:1-377
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_solo_matrix_test_edits.py:1-56
  IMPACT: S2b-1 is ready for the device; the matrix regression from this lane is fixed with it.
  NEXT: Check the mailbox, confirm the device files still equal the twin, --check and apply the three scripts,
    verify byte-identity, update the code-description patch for the guard rule.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T16:59:40Z
  TYPE: FACT
  CLAIM: Mailbox F0-17 (fable_0, 16:47:56Z) asks whether cache generation 14 is committed and whether
    caching_system.py and spellbook_creation_system.py are free for the I-1 capture task. Read-only git
    (GIT_OPTIONAL_LOCKS=0): generation 14 is in HEAD (caching_system.py:165 at HEAD); `git diff --ignore-cr-at-eol HEAD`
    on both files is empty, so this lane has no uncommitted content in them (the whole-file stat is CRLF in the working
    tree vs LF in HEAD). S2b-1 does not touch them and S2b-2 is planned without a cache generation. Answer: both free;
    melder_0 will message before touching either again (M0-36). A 0-byte .git/index.lock seen at 16:58:52Z was gone at
    16:59Z (another writer's git operation; melder_0 ran no git that wrote).
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:160-170
  - context_compass/mailbox_board.md:109-122
  IMPACT: fable_0's capture task can proceed without a file conflict with this lane.
  NEXT: Consume F0-17, send M0-36 (ACK), then apply S2b-1 to the device.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T17:01:04Z
  TYPE: FACT
  CLAIM: S2b-1 is on the device. Mailbox read first (F0-17 consumed, M0-36 sent); the four target files equalled the
    twin; apply_s2b1_edits.py, apply_s2b1_test_edits.py and apply_solo_matrix_test_edits.py passed --check and were
    applied; each file is byte-identical to the validated ~/work/melder_s2b copy. Override key-set plans now place
    shared sites' children inside their misses (a stored shared site's children are not built; B2) and a miss builds
    its children before taking its guard (CONFLICT 16:52:30Z). Code-description patch step 8 and invariants updated;
    release note bullet "A stored shared object skips its dependencies" added under the override section. No version
    notch (0.2.59 is not yet committed and carries this lane's override work). Normal melds unchanged (S2b-2).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1-1285
  - context_compass/system_docs/patches/active/override_site_plan_2026_09_26/code_description_patch_site_plan_lowering.md:40-74
  - release_docs/next_version_release.md:44-60
  IMPACT: Warm override melds on graphs with shared sites stop building discarded dependencies.
  NEXT: S2b-2 discovery: read both families' normal-lane hydration and inner executors, then write the S2b-2 plan,
    parity-gate method and file list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:03:25Z
  TYPE: FACT
  CLAIM: S2b-2 discovery. (1) Generalized hydration builds the inner normal executor from manifest rows
    (hydrate_no_overrides_executor: unrolled transient source when the schema is present and every row is a
    non-registering many, else straight-line step source with closure-cell constants), wraps it in both route-keyed
    doors, and optionally (config flag, default False) installs a warm-tail specializer whose body comes from the old
    emitter and deopts to the inner executor. The override door builds SitePlanOverrideRuntime lazily at the first
    override meld from the same rows, so today a root that sees overrides builds its site graph there. (2) many_only
    hydration compiles its inner through the many_only compiler (transient or step source) and builds the override
    runtime eagerly. (3) Construction failures in both old emitters and in the lowering go through the same
    `_raise_meld_construction_error` body (same UnresolvedInputError check and message), so error parity holds.
    (4) Design v2 S2 gate: identical results, constructor counts differ only as B2 predicts, suites on 3.14t and GIL,
    normal throughput at or above today.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:265-356
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:569-770
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:111-204
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:198-336
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:312-342
  - context_compass/artifacts/melder_override_design_20260926/design_v2.md:403-419
  IMPACT: The switch is a hydration change in both families plus a normal-mode emission; manifests are unchanged, so no
    cache generation.
  NEXT: Measure before code (PLAN below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:03:25Z
  TYPE: PLAN
  CLAIM: S2b-2 measure-first. Probe (artifact s2b2_parity.py, no production change) on the S2b-1 tree: per graph,
    today's hydrated inner executor vs the lowering's empty-key-set plan, direct warm calls, median of 7, 3.14t and
    GIL; many_only graphs from the experiment (solo, shallow, wide, diamond, deep) and generalized graphs with shared
    sites (G1 Root(a many, s upc(x many)); unique service over a many leaf; mixed upc/many; a deep many tree with a
    shared leaf); plus the first-meld cost of building the plan (steps, site graph, emission, compile). Gate: every
    graph at or above today within noise (median ratio >= 0.98), results identical, counts differ only by B2. If met,
    implementation (separate file list note first): SitePlanLowering gains a normal-mode emission (`(meld)`
    signature, misses without `ov`) for the empty key set; SitePlanOverrideRuntime builds and owns the normal plan
    and serves it as the family inner executor and its own empty-payload fallback (one site graph per root); both
    hydrators install it; the old transient lane and the opt-in specializer stay only where measurement says so.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/s2_parity.py:1-65
  - context_compass/artifacts/melder_override_design_20260926/design_v2.md:403-434
  IMPACT: No production code until the gate is measured.
  NEXT: Write and run s2b2_parity.py on ~/work/melder_s2b (3.14t, GIL).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:07:50Z
  TYPE: MEASURE
  CLAIM: S2b-2 parity gate, s2b2_parity.py on the S2b-1 tree: today's hydrated inner executor vs the lowering's
    empty-key-set plan in normal mode (`(meld)`; previewed by dropping the pass-through `ov`), warm direct calls, 11
    interleaved rounds, median per-round speed ratio. 3.14t / GIL: G1 136% / 138%, unique service 127% / 131%, mixed
    141% / 144%, tree (shared leaf under a many tree) 101% / 106%, shallow 100% / 101%, wide 101% / 100%, diamond
    101% / 99%, deep (511 transient) 103% / 101%, solo 94% / 99% in the batch run and 101.8% on 3.14t alone (median of
    five order-alternating reps of 50,000 calls; its bytecode equals today's inner, so the batch figure was
    interference on the shared VM). With `ov` still passed the small graphs sat at 95-98%, so normal mode matters.
    Results are the same type on every graph. Build cost at first meld: site graph 40-75 us on small graphs and about
    2.1 ms on deep; emission 45-110 us small, about 2-2.4 ms deep; compile is cached by source in production, as the
    old factory cache is.
  EVIDENCE: context_compass/artifacts/melder_override_design_20260926/s3_staging/s2b2_parity.py:1-300
  IMPACT: The design S2 gate (normal throughput at or above today) is met on both builds; shared-site graphs gain
    27-44% from B2 on warm normal melds. Cost: one site graph per hydrated root, about 2 ms more first-meld latency on a
    511-site graph.
  NEXT: DECISION and the implementation file list.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:07:50Z
  TYPE: DECISION
  CLAIM: Gate met, so S2b-2 switches the normal lane of both families to the lowering. Shape: (1) SitePlanLowering
    gets a normal-mode emission (`def _site_plan_executor(meld)`, misses without `ov`) for the empty key set;
    (2) SitePlanOverrideRuntime builds its site graph and that normal plan at construction and serves it as
    `execute_normal`, its own fallback for payloads with no winning key (one site graph and one step set per root);
    (3) both hydrators build the runtime at hydration and install `execute_normal` as the inner executor; the
    generalized override door reuses that runtime instead of building its own; the opt-in specializer keeps its body
    from the old emitter with the plan as its generic/deopt target; (4) the old transient/step emitters stay in the
    tree, unused by the normal lane, for S2b-3 (owner-confirmed retirement). Manifests are unchanged: no cache
    generation. FILES: shared_assets/site_plan_lowering.py, shared_assets/site_plan_override_runtime.py,
    strategies/generalized/hydration/generalized_hydrator.py, strategies/many_only/hydration/many_only_hydrator.py,
    tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py,
    tests/component/melder/spellbook/test_spellbook_component_override_key_set_plans.py, and tests that pin the old
    inner (read first: test_generalized_specializer_wrapper.py, test_ordered_disposal_compiler.py); patch docs
    component_patch_override_key_set_plans.md and code_description_patch_site_plan_lowering.md; release note.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/design_v2.md:403-419
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:312-342
  IMPACT: One emitter owns normal and override melds; warm normal melds on shared-site graphs skip B2 work.
  NEXT: Read the two tests that pin the old inner, update the patch docs, then implement on a fresh VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:19:32Z
  TYPE: FACT
  CLAIM: S2b-2 implemented on ~/work/melder_s2b (rebuilt from a fresh device twin; apply_s2b2_edits.py and
    apply_s2b2_test_edits.py, --check first). Lowering unit + key-set component tests 61 passed; the new normal-meld
    B2 component test fails on the device state (both variants) and passes with S2b-2. 3.14t: unit spellbook 2195,
    component spellbook 775, integration spellbook 584+2s+2xf+2xp, component aether 1204+1xf, conduit 268,
    multithreading 42, unit aether 4145, integration aether 716. One failure: the generalized manifest experiment
    asserts `executor_factory_cache_size() >= 1` after a cache reload; the factory cache belongs to the old emitter,
    and normal hydration now compiles through the executor code cache. File added to the list:
    tests/experimentation/test_generalized_cache_strategy_experiment.py (assert the code cache instead; the factory
    count stays in its printout). VM disk was full at the twin refresh: stale work copies and caches in the VM home
    were removed (none in the connected folder); the twin was verified identical to the device by a dry-run rsync.
  EVIDENCE:
  - tests/experimentation/test_generalized_cache_strategy_experiment.py:186-224
  - src/melder/aether/spellbook/spell_compiler/executor_code_cache.py:169-176
  IMPACT: The experiment pinned an implementation detail of the retired normal emitter path, not behavior.
  NEXT: Add the experiment edit to apply_s2b2_test_edits.py, then run GIL and the remaining suites.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T17:24:47Z
  TYPE: MEASURE
  CLAIM: S2b-2 validated on ~/work/melder_s2b (fresh device twin + apply_s2b2_edits.py + apply_s2b2_test_edits.py incl.
    the experiment assertion). Suites, 3.14t and GIL identical: unit spellbook 2195, component spellbook 775,
    integration spellbook 584+2s+2xf+2xp, experimentation 250+4s, component aether 1204+1xf, conduit 268,
    multithreading 42, unit aether 4145, integration aether 716; 3.14t also crystallizer 565/258+3xf, utilities
    796+2s+7xf, mutation_research 277/40/66, live_sim 1+1xf, root unit 144. Failures only the known ones (asset stamp,
    file_backed_morph x4, system_documents_builder x2 in VM copies). Public normal meld (override experiment timing,
    automatic, median us, device-state twin -> S2b-2): 3.14t solo 0.265 -> 0.255, shallow 0.292 -> 0.299, diamond
    0.393 -> 0.387, deep 25.46 -> 25.69; GIL solo 0.241 -> 0.239, shallow 0.268 -> 0.265, diamond 0.350 -> 0.334, deep
    20.63 -> 20.35 (all within +-3% run noise or faster). Fresh-process conjure unchanged; first meld: deep 26-28 ms ->
    19-21 ms, shallow 0.36 -> 0.52 ms, diamond 0.44 -> 0.52 ms (3.14t).
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s2b2_edits.py:1-901
  - context_compass/artifacts/melder_override_design_20260926/s3_staging/apply_s2b2_test_edits.py:1-245
  IMPACT: The design S2 gate holds at the public meld too; the switch is ready for the device.
  NEXT: Mailbox, confirm the seven target files still equal the twin, --check, apply, verify byte-identity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:25:14Z
  TYPE: FACT
  CLAIM: Mailbox M2-6 (melder_2, 17:12:22Z, ACK of M0-35): melder_2 keeps to meld entry, SpellSpace and the scope
    lifecycle; every code-emission lever (compilers, hydrators, site_plan_*) routes to melder_0, and P1's emitter file
    is melder_0's from here on. Pending the owner: P3 (deferred refcounting of the runtime graph on 3.14t, -23% to -36%
    per worker-thread cycle); if approved, melder_2 hands the hydrator/specializer lines to melder_0 (one
    RefcountDeferral.defer_graph(...) call at each hot-door publication) and sends a NOTICE before touching conduit.py,
    conduit_meld.py and spellspace_meld.py (which carry this lane's uncommitted fast-door edits). S2b-2 changes both
    hydrators, so a P3 handoff lands on the S2b-2 form.
  EVIDENCE: tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:461-527
  IMPACT: No conflict now; a later P3 handoff applies to the post-S2b-2 hydrators.
  NEXT: Apply S2b-2 to the device.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T17:26:20Z
  TYPE: FACT
  CLAIM: S2b-2 is on the device. Mailbox consumed first (M2-6); the seven target files equalled the twin;
    apply_s2b2_edits.py and apply_s2b2_test_edits.py passed --check and were applied; every file is byte-identical to
    the validated ~/work/melder_s2b copy. Normal melds of the many_only and generalized families now run the
    site-plan runtime's normal plan (solo roots unchanged); the old normal emitters stay in the tree. Public warm
    meld on shared-site graphs (ns/call, device-state twin -> S2b-2): 3.14t G1 387.5 -> 317.0, unique service 387.7
    -> 320.5, mixed 501.9 -> 408.7, tree 599.2 -> 578.8; GIL 328.4 -> 272.0, 323.0 -> 267.2, 441.2 -> 346.5, 525.7 ->
    480.9 (3-27% more throughput). Patch docs (component S2b-2 section, code-description step 9) and the release
    note ("Stored shared objects skip their dependencies on every meld") updated. No cache generation.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:1-384
  - context_compass/system_docs/patches/active/override_site_plan_2026_09_26/component_patch_override_key_set_plans.md:64-99
  - release_docs/next_version_release.md:76-84
  IMPACT: One emitter now owns normal and override melds for both families.
  NEXT: DECISION_REQUEST on S2b-3 (retiring the old normal emitters), then S4 discovery.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:28:08Z
  TYPE: DECISION_REQUEST
  CLAIM: S2b-3 (retire the old normal emitters) needs an owner decision: it is a deletion across files outside this
    lane's list. Normal hydration no longer calls them. Remaining consumers (search, then files opened as named):
    the opt-in singleton specializer (generalized_manifest_no_overrides_compiler: build_specialized_... and the row
    helpers it shares with the step emitter); tests pinning old emission (test_generalized_emission_contracts,
    test_generalized_positional_emission, test_codegen_creation_compilers_core, test_codegen_creation_core,
    test_ordered_disposal_compiler); many_only_no_overrides_codegen_creation_step.py (live-pipeline status UNKNOWN,
    to read); the packaged hardcopy docs payload (regenerated with the owner-approved asset rebuild). Options:
    (1) retire now: delete the generalized step/transient normal emission and the many_only normal compiler lane plus
    their tests, keep the specializer's emitter; (2) retire including the opt-in specializer (port its warm-tail body
    onto the lowering, or drop the flag); (3) defer the deletion to S6, alongside docs promotion and the asset
    rebuild, and do S4/S5 first. Recommendation: (3), because S4/S5 are behavior work and the deletion is safest as one
    reviewed pass with the docs; the code stays unused and tested meanwhile.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:1420-1811
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:543-744
  IMPACT: Deleting in the wrong order would break the opt-in specializer or tests that still pin old emission.
  NEXT: Owner picks; meanwhile read design v2 4.2.6 and the unresolved-input failure path for S4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T17:31:14Z
  TYPE: FACT
  CLAIM: S4 discovery. (1) The failure-path hook `UnresolvedInputError.from_failed_construction` is called from three
    places: the generalized and many_only `_raise_meld_construction_error` (also used by the lowering) and the solo
    no-overrides compiler's `guarded_call_target`, which wraps a solo root whose topology has UNRESOLVED_INPUT
    sockets; the solo override lane passes the payload straight to the constructor and is not a key-set plan.
    (2) It covers UNRESOLVED_INPUT sockets only. (3) In the lowering's site graph (built from steps) an unresolved
    input's source_kind is "plain", but socket_kind_value is UNRESOLVED_INPUT from the live Phase-3 topology, so a
    plan can see it. (4) test_conduit_component_unresolved_inputs.py asserts `__cause__` is a TypeError for solo,
    many_only and generalized (it changes for plan families under B6).
  EVIDENCE:
  - src/melder/utilities/custom_exceptions/unresolved_input_error.py:175-261
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:246-301
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_site_graph_processor_strategy.py:265-335
  - tests/component/melder/aether/conduit/test_conduit_component_unresolved_inputs.py:125-141
  IMPACT: S4 splits: plan families can decide it now; solo needs its own decision.
  NEXT: Record the scope challenge and the S4a plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T17:31:14Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: Design v2 4.2 step 6 says "an unresolved or override-required input with no key" is raised by the plan.
    The canonical architecture contract for non-resolvable registrations says ordinary supplied inputs keep
    "existing override execution and Python constructor errors ... no new preflight", and the hook itself never
    covered OVERRIDE_REQUIRED. The only path that keeps the canonical contract: S4 decides UNRESOLVED_INPUT sockets
    only; OVERRIDE_REQUIRED keeps today's constructor error. Owner may widen it later.
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/design_v2.md:106-109
  - context_compass/system_docs/src_architecture.md:1019-1027
  IMPACT: No new preflight for override-required inputs; B6 applies to unresolved inputs as the hook did.
  NEXT: PLAN below.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T17:31:14Z
  TYPE: PLAN
  CLAIM: S4a (plan families; solo and the hook's retirement wait for the owner). The lowering computes, per kept site,
    its UNRESOLVED_INPUT params without a winning key. A context (plan top, or a shared site's miss) raises for the
    first such site it builds unconditionally, in step order, before anything in it is constructed: the plan top
    after the conflict guards for top-level many sites; a miss's top (before its children) for its many children and
    then the site itself. Stored sites never demand (the hit read skips the miss). The raise is
    `_raise_unresolved_input(spells[i], names)` -> `UnresolvedInputError.for_unsupplied(spell, names)`, a new
    classmethod sharing the message builder with `from_failed_construction` (same text; no TypeError cause).
    FILES: shared_assets/site_plan_lowering.py; utilities/custom_exceptions/unresolved_input_error.py;
    tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py;
    tests/component/melder/aether/conduit/test_conduit_component_unresolved_inputs.py; patch docs
    (code-description step 10, component patch S4a); release note (B6).
  EVIDENCE:
  - context_compass/artifacts/melder_override_design_20260926/design_v2.md:344-352
  - context_compass/artifacts/melder_override_design_20260926/design_v2.md:380-381
  IMPACT: Unresolved inputs fail before any construction under the consumer in normal and override melds of both
    plan families.
  NEXT: Patch docs, then implement on the VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
In the device tree, uncommitted: S3a (key-set override plans), S3b-1/S3b-2 (old override lane, legacy codec and
fallback family retired; cache generation 14, committed), S2a, the override fast door, the Conduit.meld id-lane trim,
the existing-object fast path, the solo benchmark on a real override, version 0.2.59 with its release-note sections,
S2b-1 (override plans: shared sites' children built inside their misses, children before the guard; solo matrix
inputs fixed) and S2b-2 (normal melds of both families on the site-plan runtime's normal plan; parity gate met; the
old normal emitters remain in the tree). Next: owner decision on S2b-3 (retire the old normal emitters), then S4
(unresolved inputs decided in the plan), S5, S6 (docs, owner-approved asset rebuild, release note). Known unrelated
failures: crystallizer file_backed_morph x4; asset-stamp test (assets 0.2.56 vs package 0.2.59); VM work copies lack
context_compass/system_docs, so test_system_documents_builder x2 fails there only.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
