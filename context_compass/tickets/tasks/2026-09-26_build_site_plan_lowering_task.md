

# Task: S2/S3 - one site-plan lowering; override key-set plans and the normal lane

## Metadata
- Task ID: TASK-2026-09-26-build-site-plan-lowering
- Story: STORY-2026-09-26-implement-override-site-plan-lowering
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-26T12:29:50Z
- Updated: 2026-09-26T13:50:34Z

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

## Context / Handoff Summary
Discovery: reading the Phase-10/11 pipelines to fix the production lowering plan.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
