# Task: Compile OVERRIDE_REQUIRED sockets and exclude non-resolvable construction roots

## Completion
- Completed: 2026-09-20T00:25:59Z
- Summary: Implemented resolved reference-only inputs, executable-root filtering and existing revalidation integration.
- Acceptance: Owner requested turn-in, then required two repairs first; both are verified.

## Metadata
- Task ID: TASK-2026-09-19-implement-override-required-compiler
- Story: STORY-2026-09-19-caller-supplied-socket-compiler
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T20:13:54Z
- Updated: 2026-09-20T00:25:59Z

## Objective
Deliver S3's resolved socket policy and compiler propagation using the native Spell.resolvable field.
Preserve descriptive target identity while preventing False definitions from becoming executable dependencies.

## Ticket Contract
- ENTRY_GATE: Owner approved continuing after S2; active board routes here. Read the S3 story,
  S1 socket/selection tables, source/component/graph slices, then create and consume patch contracts.
- EXECUTION_BOUNDARY: Compiler records, Phase-3 selection, validation, construction-root admission,
  Phase-5/8/9/10 propagation, relevant input/cache signatures, and focused compiler regressions/docs.
- DEPENDENCIES: S2 native per-Spell flag is implemented and tested. S4 consumes the compiler contract
  for direct/fast/nested/cached runtime enforcement. S5/S6 consume descriptive target and wire metadata.
- EXIT_GATE: New and compatibility compiler tests pass, graph references survive, False roots/providers
  produce no construction plans, normal defaults/providers retain behavior, S4/S5/S6 handoff is concrete.
- FAILURE_ESCALATION: Resolve source-backed compiler ownership/schema conflicts before implementation.
  Do not expand into owned-object lifecycle, source-body versioning or a new invalidation framework.

## Scope Boundaries
- In scope: the S3 story's required source owners and their direct compilation callers/consumers.
- Out of scope: runtime execution enforcement, Nexus command/projection implementation, crystal replay,
  supplied-object ownership, named lesser conduits, release/version bump and publication.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner-authorized turn-in after delivered scope and reported failure repairs passed.

## Required Reading
- `tickets/stories/completed/2026-09-19_caller_supplied_socket_compiler_story.md` and its required source/test read map.
- `tickets/tasks/completed/2026-09-19_define_caller_supplied_socket_contract_task.md`: resolved schema and propagation.
- `tickets/tasks/completed/2026-09-19_define_discoverable_registration_selection_task.md`: selector/collection table.
- `tickets/tasks/completed/2026-09-19_implement_resolvable_registration_modifier_task.md`: native flag and test/build state.
- Relevant verified src_components/src_graph slices before reading changed implementations in full.
- Reuse unchanged orientation/policy already read this session; REONBOARD after every compaction.

## Working Implementation Contract
- Append SocketKind.OVERRIDE_REQUIRED; retain original Phase-1/2 declaration and default facts.
- Store descriptive referenced_spell_ids separately from executable target_spell_ids.
- Implicit single-annotation selection prefers eligible True providers; a unique False-only match requires
  override; zero/multiple keep missing/ambiguity behavior. Ordinary defaults remain PLAIN.
- Explicit SpellMap selection retains cardinality/target; a selected False requires a consumer override
  and cannot carry a provider-construction spell_override payload.
- SpellContract remains linked-provider DI and diagnoses a selected False as incompatible.
- Collections select True providers in existing order; empty collections remain empty collections.
- Non-resolvable roots retain descriptive metadata without construction dependency/plan obligations.
- Validation and Phase-5/8/9/10 consumers share the resolved policy; no phantom construction cycles.
- Preserve required-input metadata in both planner variants and existing cache/signature invalidation.
- S3 does not claim that compiled metadata alone enforces runtime safety; S4 remains required.

## Steps / Checklist
- [x] Read records and Phase-3 selection completely; document exact propagation/ownership seams.
- [x] Read root admission, validators and downstream model/planner consumers; record implementation mapping.
- [x] Create and consume architecture/component/control-flow patch contracts with indexes.
- [x] Add failing compiler regressions and establish the baseline.
- [x] Implement resolved metadata, target selection and construction/validation policy.
- [x] Carry policy through Phase-5/8/9/10 and required signatures.
- [x] Run focused compiler/default/provider compatibility checks and document remaining limits.
- [x] Update source docs/graph, generated assets and S4/S5/S6 handoff.

## Deliverables
- Source-backed S3 compiler patch, meaningful regressions, and validation evidence.
- Stable input/reference contract for the remaining runtime/graph/persistence stories.

## Files / Paths Impacted
- S3 story's records, compiler_phase_3/5, validators, compiler-system/creation-system admission,
  occurrence analyzer, injection processor/model/planner, and direct compiler consumers when required.
- Focused unit/component tests; required patch/source docs, descriptors and normal generated assets.
- ContextCompass ticket/board/artifact state for this lane only.

## Validation
- S3: 2098 distinct focused tests pass (1961 expanded + 137 disjoint remaining cases), including
  all 42 new compiler component cases. XML case keys were checked for overlap: zero.
- Source/LLM asset checks and scoped Ruff pass. Architecture/components indexes and graph range checks pass.
- Whitespace passes with existing CRLF tolerated. Full repository suite and coverage: Not run.
- Environment: .venv_new Python 3.14.7 free-threaded via uv --no-sync --offline, -X gil=0;
  task-owned cache/output paths and disabled pytest cacheprovider.
- Exact evidence and limits: `artifacts/override_required_compiler_20260919/validation.md`.

## Risks / Rollback Notes
- Phase-4 declaration-based edges can manufacture cycles after Phase 3 removed an executable target.
- Empty target tuples alone do not express required supplied inputs; model/planner must preserve the kind.
- False definitions must not poison separate True providers under the same frame.
- Existing uncommitted S2/source-assets and earlier owner closure/backlog work must be preserved.

## Applicable Anti-Patterns
- [x] No forced PLAIN or private declaration mutation.
- [x] No lost graph reference or speculative alternate provider for an explicit selector.
- [x] No construction plan for a non-resolvable root.
- [x] No new ownership/lifetime model, source-body hash or invalidation system.
- [x] No feature-completion claim before runtime/graph/replay qualification.

## Done Checklist
- [x] Compiler contract implemented and verified.
- [x] Documentation and required generated artifacts updated.
- [x] S4/S5/S6 handoff and board routing synchronized.
- [x] Owner acceptance before closure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- PATCH_ID: override_required_compiler_2026_09_19
- ARTIFACT_PATHS:
  - system_docs/patches/completed/override_required_compiler_2026_09_19/architecture_patch.md
  - system_docs/patches/completed/override_required_compiler_2026_09_19/component_patch_compiler.md
  - system_docs/patches/completed/override_required_compiler_2026_09_19/component_patch_revalidation.md
  - system_docs/patches/completed/override_required_compiler_2026_09_19/component_patch_resolution_revalidation.md
  - system_docs/patches/completed/override_required_compiler_2026_09_19/component_patch_spellbook_creation.md
  - system_docs/patches/completed/override_required_compiler_2026_09_19/code_description_patch_compiler.md
  - artifacts/override_required_compiler_20260919/
  - artifacts/override_required_compiler_20260919/validation.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: accepted task closure; patch deltas promoted and archived normally.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: selected target policy, descriptive references, validation, root eligibility and compiler propagation.
- IF_UNKNOWN: none

## Noting Behavior
Read complete source units; then record evidence, impact and a single NEXT before the next tranche.

## Notes
- DATETIME: 2026-09-19T20:13:54Z
  TYPE: PLAN
  CLAIM: Owner approved continuing after S2. Open the bounded S3 compiler task using the existing
    schema/selection proposals and native Spell.resolvable contract. No new source work has started.
  EVIDENCE:
  - tickets/stories/completed/2026-09-19_caller_supplied_socket_compiler_story.md:17-138
  - tickets/tasks/completed/2026-09-19_implement_resolvable_registration_modifier_task.md:1-128
  IMPACT: Compiler work has a durable owner and execution boundary; S2 changes remain intact.
  NEXT: Read resolved-record owners and Phase 3, then trace construction-root admission.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:15:21Z
  TYPE: FACT
  CLAIM: Completed source reads for all six declaration/resolved-record owners and the full 989-line
    Phase 3. Phase 1/2 preserve immutable signature/default/annotation facts. Phase 3 resolves into
    per-socket target lists, emits dependency DAG edges, then reconstructs socket_kind from declaration
    alone in _build_local_topology. Both scan and pass-index candidates converge before cardinality.
    SpellContract currently has no Phase-3 targets; linked-provider validation is a separate path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:403-901
  - src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py:12-228
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_parameter_requirements.py:15-311
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements.py:15-305
  - src/melder/aether/spellbook/spell_compiler/symbolic_graph/spell_symbolic_dependency.py:12-256
  IMPACT: Add per-socket reference metadata and resolved kind at Phase 3, not a declaration enum mutation.
    Filter implicit candidates after existing matching; explicit SpellMap cardinality remains unchanged.
    Graph prose still names removed MUTATION_CONTRACT enum members; correct relevant descriptor prose
    when refreshing, using the source's actual two SocketKind/six ParameterDIShape values.
  NEXT: Trace validation and root admission plus Phase-5/8/9/10 consumers before patching propagation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:17:19Z
  TYPE: FACT
  CLAIM: Phase-4 strategy/context reads confirm two independent construction checks: id-based
    circular/self validation consumes spell.dependencies and will follow Phase-3 edge exclusion;
    BindingResolutionCycleStrategy reconstructs declaration binding keys and must consult resolved
    socket policy to avoid reintroducing OVERRIDE_REQUIRED edges. RequiredHolesStrategy only examines
    Phase-1 PLAIN holes today. ContractProviderPresenceStrategy caches IDs, without capability, and
    needs a distinct False-provider diagnostic. ValidationContext owns no topology field yet.
    AnnotationShapeGuard and ParameterPolicy apply DI limits (set/tuple, variadics) even to otherwise
    ordinary Python definitions, so non-resolvable roots need targeted construction-policy exclusions.
    Callable/profile hygiene, SpellMap shape and existing-instance admission invariants can remain.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/validation_system.py:264-350
  - src/melder/aether/spellbook/spell_compiler/validation/spell_validation_context.py:27-183
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:75-279
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py:61-104
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:69-223
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/annotation_shape_guard_strategy.py:70-182
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/parameter_policy_strategy.py:65-177
  IMPACT: Preserve registration/profile validation rather than bypassing all validators for False roots.
    Pass-cached graphs/provider maps must include the same resolved capability boundary as uncached runs.
  NEXT: Read Phase-5 snapshot/root selection and plan eligibility before defining the patch contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:19:15Z
  TYPE: FACT
  CLAIM: Phase 5 currently builds executable roots for every visible disconnected spell, then builds
    fallback per-spell blueprints for non-root owned spells. Skipping only the Phase-8 scheduler would
    leave False construction blueprints and root-coverage obligations behind. RootCoverageStrategy
    explicitly requires blueprint/index-root parity. Blueprint SocketRefs already preserve socket_kind
    and stop expansion at empty target IDs. Conjure cache eligibility independently includes every
    non-existing spell, so it must exclude non-resolvable entries too. The later plan eligibility helper
    and direct phase facade entry points are separate paths that must be checked.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:261-709
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:63-193
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:433-490
  - src/melder/aether/spellbook/spell_compiler/system/validation/root_coverage_strategy.py:45-152
  - src/melder/aether/spellbook/spellbook_creation_system.py:412-489
  - src/melder/aether/spellbook/spellbook_creation_system.py:2611-2648
  IMPACT: Treat Phase-5 snapshot/index as the executable view while retaining descriptive local topology
    in SpellSystemStates and original declarations on Spell artifacts. Do not touch provider artifacts
    outside the existing publication scope. Verify empty/False-only books as well as mixed consumers.
  NEXT: Read injection/model/planner and occurrence analyzer propagation, then write the patch mapping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:21:19Z
  TYPE: FACT
  CLAIM: Completed injection/model/planner facade and full 1163-line occurrence-analyzer reads.
    Phase 9 already borrows durable local topology for collection truth, making it the source for
    OVERRIDE_REQUIRED input rows even with no occurrence dependency entry. ParamSource currently
    carries only dependency/contract/key/collection data; signature position/kind/reference identity
    need explicit transport. Model owns injection_shape. Planner strategy paths include generalized
    dual-build, solo and both many-only families; no-overrides variants intentionally drop inject_spec,
    so required-input obligations must be carried separately from optional targeting metadata.
    Phase 8 expands only target_spell_ids; its topology signature currently omits kind/flags/references.
    Its late SpellContract selector already returns the provider object before reducing to ID, a direct
    capability-check seam. Existing-provider leaf handling remains intact.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:50-338
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:9-220
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:33-301
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:62-143
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:118-463
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:852-1114
  IMPACT: No new model root or service registry is needed. Preserve required override rows as plain
    value metadata across both planner variants; keep ordinary PLAIN/empty collection behavior stable.
  NEXT: Finish generalized/many-only builder-step and IR serialization reads, then author patch contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:22:52Z
  TYPE: FACT
  CLAIM: Correction to the previous planner note: complete builder reads show generalized steps
    retain inject_spec in BOTH variants (and build_dual shares full step objects). What is stripped
    is override-targeting data in standalone no-overrides construction or row export. Standalone
    ManyOnlyCodegenPlanStep carries no inject_spec. A shared plain-value required_override_params
    tuple derived from injection sources should therefore be copied into every family step before
    variant stripping. Preserve per-parameter name, position, parameter-kind and reference IDs.
    SharedCompilerExecutions injection-row exporters omit these new fields today; the live Phase-11
    step-row helper is a separate codegen_creation_system.module surface, not the legacy twin.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1093-1306
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1463-1610
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:58-230
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:960-1059
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:861-944
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1200-1262
  IMPACT: Do not add duplicated input obligations to dependency_keys or rely on optional override
    payload metadata. S4 must bind the value rows into emitted/cached executors; S3 tests stop at the
    model/plan contract plus root eligibility and normal compilation compatibility.
  NEXT: Author and consume S3 patch contracts, then establish Phase-3 compiler regression baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:25:27Z
  TYPE: DECISION
  CLAIM: Created and reread S3 patch contracts in architecture/component/control-flow order.
    Mapping: selected-target flow -> SocketKind/local topology/Phase 3 -> scan/index/default/selector
    component regressions; validation/root policy -> Phase 4/5 and construction eligibility ->
    descriptive-cycle/False-only/mixed-root tests; required-input transport -> injection records and
    generalized/many-only steps -> both-variant row parity. Existing declaration and ownership contracts
    remain unchanged. First implementation tranche is Phase 3 and its records; subsequent consumers
    follow the same patch contract after their complete source reads and regression baselines.
  EVIDENCE:
  - system_docs/patches/completed/override_required_compiler_2026_09_19/architecture_patch.md:7-54
  - system_docs/patches/completed/override_required_compiler_2026_09_19/component_patch_compiler.md
  - system_docs/patches/completed/override_required_compiler_2026_09_19/component_patch_revalidation.md
  - system_docs/patches/completed/override_required_compiler_2026_09_19/component_patch_resolution_revalidation.md:3-44
  - system_docs/patches/completed/override_required_compiler_2026_09_19/component_patch_spellbook_creation.md:3-21
  - system_docs/patches/completed/override_required_compiler_2026_09_19/code_description_patch_compiler.md:3-35
  IMPACT: S3 now has an explicit code/test map and no unrequested runtime or ownership expansion.
  NEXT: Establish failing Phase-3 component tests, then implement the resolved records and selection path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:27:42Z
  TYPE: MEASURE
  CLAIM: Phase-3 baseline is red in all 18 new component cases (0.61s): no OVERRIDE_REQUIRED or
    reference fields, True/False annotation ambiguity, False collection elements, False-root missing
    constructor providers and accepted incompatible SpellMap construction payloads. Direct and indexed
    matching are both exercised with real records and compiler phases. Ordinary default classification
    already remains PLAIN; its new reference field assertion is the failure.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/phase3_red.log:1-170
  - tests/component/melder/spellbook/test_spellbook_component_override_required.py:1-242
  IMPACT: The first compiler tranche has a concrete failing baseline rather than inferred coverage.
  NEXT: Implement SocketKind/local topology and Phase-3 capability selection against these cases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:29:30Z
  TYPE: FACT
  CLAIM: First source tranche adds OVERRIDE_REQUIRED and local reference/kind metadata; Phase 3 now
    prefers True implicit providers, filters False collection elements, records selected False inputs
    as references, rejects False SpellMap construction payloads, and skips constructor lookup for False
    roots while retaining declarations/topology. The private topology helper now receives requirements
    and reference maps explicitly; its two direct unit callers will need aligned fixture inputs.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/dag/socket_kind.py:5-37
  - src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py:12-102
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:438-941
  IMPACT: Phase-3 policy is implemented; validation/root/model/planner work is still outstanding.
  NEXT: Run the 18 regression cases and existing Phase-3/topology tests; correct genuine fixture drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:30:36Z
  TYPE: MEASURE
  CLAIM: All 18 new Phase-3 cases pass after the first patch. Combined Phase-3/topology run is
    50 passed, 9 failed (0.65s); failures are the old SimpleNamespace spell factory lacking native
    resolvable and two private helper calls missing new required inputs. Requirements placeholders
    also need a parameters sequence now that Phase 3 preserves parameter kind. Real topology tests pass.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/phase3_first.log:1-85
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py:77-108
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py:294-360
  IMPACT: Align fixtures to the native Spell/requirements contract without defensive runtime probes.
  NEXT: Update the focused stubs/helper calls and rerun this first-tranche suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-09-19T20:33:04Z
  TYPE: MEASURE
  CLAIM: First S3 tranche is green: 59 Phase-3/topology cases pass in 0.44s, including all 18 new
    reference/selection/default/collection/False-root cases. Native capability and requirements fixture
    updates resolved the prior nine failures. No runtime probes or extra fallback logic were added.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/phase3_green.log:1-2
  IMPACT: Phase 3 now supplies real OVERRIDE_REQUIRED metadata. Phase 4/5 and model/planner still need
    to consume it, so S3 and the overall feature remain incomplete.
  NEXT: Add validation and executable-root regression cases, then align those compiler consumers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:35:06Z
  TYPE: MEASURE
  CLAIM: Five new validation/root cases fail as expected: missing required-override diagnostic,
    declaration-reconstructed cycle, DI set/variadic restrictions on a descriptive constructor, and
    False blueprint/index inclusion in both False-only and mixed books. Prior 18 tests remain separate.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/validation_roots_red.log:1-44
  - tests/component/melder/spellbook/test_spellbook_component_override_required.py:248-344
  IMPACT: Apply targeted validator changes and Phase-5 executable filtering. Read topology directly
    from the existing SpellSystemStates registry; no new context object or duplicate topology owner.
  NEXT: Implement validation/root changes and run the combined compiler regression file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:35:08Z
  TYPE: FACT
  CLAIM: Added reference-specific required-input warnings, removed False constructors and resolved
    OVERRIDE_REQUIRED edges from binding-key cycles, skipped DI annotation/variadic rules on False
    roots, and filtered Phase-5 executable snapshots to resolvable entries. Existing profile/descriptor
    validity and provider artifact publication scope remain unchanged. Contract-provider capability
    checking and direct/scheduler/cache plan eligibility remain for the following part of this tranche.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py:62-138
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:75-250
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:471-709
  IMPACT: The five new validation/root contracts have direct implementation paths to verify.
  NEXT: Run the full new compiler component file, then remaining admission and propagation work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-09-19T20:35:35Z
  TYPE: MEASURE
  CLAIM: All 23 new compiler component cases pass in 0.39s after the Phase-4/5 patch, including
    required diagnostics, descriptive-cycle success, Python-only constructor shapes and False-only
    or mixed executable-root exclusion. Remaining work is contract-provider capability, scheduler/
    direct/cache eligibility, model/planner required-input transport, broad compatibility and docs/builds.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/validation_roots_first.log:1-2
  IMPACT: Early compiler semantics are verified; no runtime enforcement claim is made.
  NEXT: Add and implement remaining admission/plan regressions before compatibility expansion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:38:48Z
  TYPE: MEASURE
  CLAIM: Five construction-admission regressions are red: cache eligibility includes the False
    definition, and direct compiler phase 8/9/10/11 calls still demand missing executable artifacts.
    The wrappers and creation-system eligibility/cache methods have been read before this patch.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/admission_red.log:1-77
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:75-118
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:62-88
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:76-113
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:81-127
  IMPACT: Exclude False at existing phase boundaries and the cache/eligibility predicates; preserve
    structural metadata capture and normal phase dispatch.
  NEXT: Implement those capability checks and rerun the new compiler suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-09-19T20:38:50Z
  TYPE: FACT
  CLAIM: Cache payload eligibility and plan scheduling now exclude False definitions. CompilerPhase8-11
    wrappers return before delegated executable work for False, including lazy planner/codegen creation.
    Existing structural recording and public registration remain intact.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:412-489
  - src/melder/aether/spellbook/spellbook_creation_system.py:2611-2651
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:75-121
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:81-130
  IMPACT: Direct phase calls and scheduler/cache admission share the native capability boundary.
  NEXT: Validate the combined component file; then complete contract and injection/planner propagation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-09-19T20:39:26Z
  TYPE: MEASURE
  CLAIM: Direct Phase8-11 admission cases pass; combined run is 27 passed and one cache-fixture
    failure before its assertion. The cache helper requires the future conduit_name before conjure
    when caching is enabled; its fixture now supplies that name as the real conjure caller does.
    The initial red cache result must not be described as proof of False membership until its actual
    assertion is reached; production eligibility is independently source-backed.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/admission_green.log:1-17
  - src/melder/aether/spellbook/spellbook.py:881-940
  IMPACT: Correct test setup rather than introducing a runtime None guard or changing cache lifecycle.
  NEXT: Verify the repaired admission case and implement the remaining contract/provider checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-09-19T20:42:16Z
  TYPE: MEASURE
  CLAIM: Contract-specific baseline is 4 failed, 2 passed: False providers are accepted in both fresh
    and pass-cached validation, while False roots still receive automatic-mode/missing-provider
    obligations. True-provider control cases pass. Extend the cached provider row atomically with its
    bool so a partially published auxiliary map cannot lose capability under parallel validation.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/contract_red.log:1-37
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_contract_provider_presence_strategy.py:337-397
  IMPACT: Cardinality stays unchanged; only a unique False provider gets the targeted incompatibility.
  NEXT: Add capability to cached provider rows and skip construction obligations on descriptive roots.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:42:17Z
  TYPE: FACT
  CLAIM: Phase-4 provider-map rows now carry (spell_id, resolvable) together. Ambiguity retains all
    candidates; a unique False provider emits SPELL_CONTRACT_NON_RESOLVABLE_PROVIDER. False consumers
    retain descriptor integrity checks but skip executable provider/mode obligations.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:69-245
  IMPACT: No False-to-missing-provider downgrade and no parallel partial-map publication hazard.
  NEXT: Verify contract validation, then carry required-input metadata through injection and planners.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-09-19T20:45:46Z
  TYPE: MEASURE
  CLAIM: Contract/admission file plus existing contract unit cases pass (44 total, 0.47s). New
    solo/many-only/generalized planner cases each fail because Phase 9 omits the required input
    entirely from param_sources. Implement native source position/kind/reference fields and immutable
    required_override_params rows, then preserve them through both plan variants.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/contract_green.log:1-2
  - artifacts/override_required_compiler_20260919/planner_red.log:1-25
  - tests/component/melder/spellbook/test_spellbook_component_override_required.py:384-427
  IMPACT: The model/plan data gap is now independently reproduced across all three family shapes.
  NEXT: Add required input records in Phase 9 and carry their value rows into generalized/many-only steps.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:45:48Z
  TYPE: FACT
  CLAIM: Phase 9 now creates override_required sources from durable topology, preserving signature
    position/kind and descriptive IDs even without occurrence edges. Injection specs derive immutable
    required_override_params rows. Generalized dual/single builders and standalone many-only steps
    retain those rows across both variants; contract payload merging preserves the source metadata.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:9-160
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:204-280
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:77-297
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:58-224
  IMPACT: The required-input contract is available to S4 without a dependency edge or live supplied reference.
  NEXT: Run all three planner-family regressions; then complete signatures and broad compatibility.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:48:04Z
  TYPE: MEASURE
  CLAIM: All 31 component cases passed after input transport. Six new signature tests demonstrate
    omitted reference/kind/position/optional/collection fields in graph-shape keys. The initial late
    contract test bound its required consumer before granting visibility; post-conjure bind runs
    structural validation at transaction commit and correctly refused that setup. Reordered the grant
    before bind, then reran the late selector baseline separately.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/planner_green.log:1-2
  - artifacts/override_required_compiler_20260919/signature_contract_red.log:1-130
  - tests/component/melder/spellbook/test_spellbook_component_override_required.py:430-488
  IMPACT: Preserve real post-bind validation and fix the test ordering. Compiler signatures need to
    track complete required-input policy, and the late contract selector must reject False explicitly.
  NEXT: Add signature fields and the late selected-provider capability check, then rerun the component suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:48:58Z
  TYPE: FACT
  CLAIM: Phase-8 graph-shape signatures now include kind, position, parameter-kind, optional/collection
    flags and descriptive references. The late contract selector rejects a uniquely selected False
    provider without treating it as missing; the corrected real-conduit baseline failed by not raising.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:374-471
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1033-1102
  - artifacts/override_required_compiler_20260919/late_contract_red.log:1-12
  IMPACT: Warm compilation and late linked-provider selection retain the same required-input policy.
  NEXT: Run component contracts and the affected compiler unit/component compatibility groups.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:49:43Z
  TYPE: MEASURE
  CLAIM: First broad compiler pass reports 1525 passed and 53 failed (3.06s). The new component cases
    pass; failures cluster in old unit doubles that lack native capability/required-input fields and
    one expected graph-signature row. Inspect each failure family before fixture edits; preserve actual
    behavior assertions and do not add runtime fallback probes to make incomplete doubles pass.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/compiler_compatibility.xml:1-1
  - artifacts/override_required_compiler_20260919/compiler_compatibility.log:1-80
  IMPACT: Broad compatibility is not yet green. Remaining work includes fixture alignment, schema-row
    transport checks, complete lifecycle/selection contrasts, and source docs/graph/build regeneration.
  NEXT: Group failures by cause and read the affected fixture factories before updating them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:52:36Z
  TYPE: FACT
  CLAIM: Failure grouping confirmed 52 missing native fields on unit doubles plus one old topology
    signature expectation. Updated fixture producers rather than production fallback logic: default
    resolvable=True on spell doubles, empty required_override_params on legacy injection specs, and
    explicit absent-topology registry stubs for declaration-only strategy tests. Removed the no-hole
    test's incidental precheck call-count assertions while retaining its no-diagnostics contract.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/codegen_planner/test_generalized_dual_build_differential.py:70-89
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_required_holes_strategy.py:91-113
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:182-241
  IMPACT: Real runtime behavior remains strict; old tests now model the expanded data contract.
  NEXT: Rerun compiler compatibility and verify reference-only sockets still participate in key-based revalidation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:53:56Z
  TYPE: MEASURE
  CLAIM: Broad compiler compatibility is now green: 1578 cases pass in 2.18s after native fixture
    alignment. Required-input signatures and late False-provider tests pass. Before closing S3,
    verify how reference-only sockets become dirty on provider/index changes: they deliberately have
    no executable dependency IDs, and the existing key-sensitive invalidation registry currently
    names collections. This remains an investigation question, not a new invalidation design decision.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/compiler_compatibility_second.log:1-24
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1362-1388
  IMPACT: Revalidation must preserve the distinction between dependency traversal and selector sensitivity.
  NEXT: Read the existing watcher path and test a False-to-True notch before deciding whether it needs adaptation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:56:51Z
  TYPE: MEASURE
  CLAIM: Real dynamic tests reproduce stale consumer plans after False-to-True notch and after adding
    a new matching True provider (2 failed). The next meld invokes the old solo constructor without
    its now-resolvable dependency. Source confirms the existing commit dirty-marker notifies a
    spellbook-scoped frame-key reverse index, whose extractor only admits NORMAL collection sockets.
    OVERRIDE_REQUIRED must join that existing selector-sensitive index without adding executable edges.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/revalidation_probe.log:1-39
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1108-1175
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1259-1386
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:837-873
  IMPACT: Extend the existing watcher, not a new invalidation framework. False roots themselves should
    carry no dependency_key because their constructors perform no selection. Normalize watched single
    annotations the same way matching normalizes Optional/ForwardRef wrappers.
  NEXT: Update the patch contract for this one additional owner, then test the existing watcher adaptation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:57:54Z
  TYPE: DECISION
  CLAIM: Consumed the added revalidation component contract. Map its watcher rule to
    SpellSystemStates._extract_collection_frame_keys, preserving existing maps and replacement/cleanup;
    map producer semantics to Phase-3 normalized dependency_key and no watched key for False roots.
    Real notch/new-bind tests (including Optional) verify the complete existing commit-to-meld path.
  EVIDENCE:
  - system_docs/patches/completed/override_required_compiler_2026_09_19/component_patch_revalidation.md
  - system_docs/patches/completed/override_required_compiler_2026_09_19/component_patch_resolution_revalidation.md:3-23
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:127-172
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1362-1460
  IMPACT: Extend one existing sensitivity index; no new registry, locks or cache lifecycle.
  NEXT: Apply watcher and normalized-key changes, then rerun the four transition tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:57:55Z
  TYPE: FACT
  CLAIM: OVERRIDE_REQUIRED now joins the existing frame-key watcher. Phase 3 unwraps Optional/ForwardRef
    for watched keys just as for candidate matching and publishes no watched constructor key for False
    roots. Existing registry update/cleanup, transaction notifications and dependency-change gates remain.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:672-755
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1365-1391
  IMPACT: Reference sensitivity is recorded separately from executable dependencies using existing machinery.
  NEXT: Verify dynamic notch/new-provider transitions, then rerun affected compatibility groups.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:59:06Z
  TYPE: MEASURE
  CLAIM: The watcher adaptation alone does not pass the four new dynamic transitions. Ordinary
    consumers now reach a missing spell_codegen_creation path; Optional consumers can still execute
    the prior solo shape. Do not call revalidation fixed. These tests use named conduit caches across
    runs, so first distinguish persisted old partial-feature payloads from a cold revalidation defect.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/revalidation_green.log:1-75
  IMPACT: Need direct cache/target-revalidation call-path evidence before another fix. Preserve the
    existing automatic invalidation framework and do not paper over missing plans with runtime guards.
  NEXT: Run isolated cache-disabled transition cases and trace target-local plan eligibility/validity.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T21:01:23Z
  TYPE: FACT
  CLAIM: Cache-disabled probe proves the remaining failure: the watcher correctly gates the consumer's
    structural SpellSystemState and keeps the book validation gate enabled. The next meld reruns Phase
    1-4 and updates consumer.dependencies to the new provider, but ConduitResolutionState still reports
    the previous root/spell verdict valid, so resolution phases 5-11 are skipped and the old solo plan
    executes. This is a split between structural and conduit-local validity, not persisted-cache stalling.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/probe_revalidation.log:1-10
  - src/melder/aether/conduit/meld/meld.py:596-642
  - src/melder/aether/conduit/meld/meld.py:835-893
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:551-581
  IMPACT: Use the existing conduit-local validity gate when required-input selection changes. Do not
    add a runtime missing-plan fallback or a new cache lookup layer.
  NEXT: Identify the canonical resolution-invalidating seam and apply it at the selector-change boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T21:07:09Z
  TYPE: DECISION
  CLAIM: Extend this compiler revalidation tranche to the two existing Meld validity helpers, with
    a consumed component patch. A successful structural rerun must gate the old conduit-local
    resolution verdict through _force_resolution_revalidation before accepting it. Add a reason
    parameter so existing contract calls retain their reason and structural reruns record theirs.
  EVIDENCE:
  - system_docs/patches/completed/override_required_compiler_2026_09_19/component_patch_resolution_revalidation.md:3-23
  - src/melder/aether/conduit/meld/meld.py:596-642
  - src/melder/aether/conduit/meld/meld.py:1011-1050
  - system_docs/src_components.md:2578-2592
  IMPACT: Repairs the documented structural-to-resolution handoff using its existing per-spell lock,
    verdict setters and rebuild path. S4 supplied-value/direct-meld enforcement remains separate.
  NEXT: Apply the handoff correction and run transition plus existing Meld gating tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T21:07:10Z
  TYPE: FACT
  CLAIM: Meld now gates conduit-local resolution after successful structural recompilation, using
    the existing helper and structure_changed reason. The old contract call preserves its default
    reason. No cache service, missing-plan fallback or runtime argument policy was added.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:596-647
  - src/melder/aether/conduit/meld/meld.py:1016-1063
  IMPACT: A watcher-gated consumer must rebuild its executor after the new Phase-3 selection.
  NEXT: Run the four dynamic transitions and existing Meld tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-09-19T21:08:39Z
  TYPE: MEASURE
  CLAIM: All four real transition cases pass after the existing resolution-handoff correction.
    Combined component/Meld unit result is 127 passed and one old unit fixture that omits its owning
    book because it assumed structural rerun could reuse prior resolution validity. Update that test
    to exercise the new rebuild handoff. Added export assertions identify one remaining S3 data gap:
    Phase9 IR/signature rows omit position/kind/reference metadata even though model/plan carries it.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/revalidation_resolution.log:1-16
  - tests/unit/melder/aether/conduit/meld/test_meld.py:1522-1546
  - artifacts/override_required_compiler_20260919/injection_export_red.log:1-41
  IMPACT: Preserve existing normal row shapes; append the required metadata only for the new
    override_required source kind, independent of optional override targeting.
  NEXT: Complete injection-row export and align the structural-rebuild fixture, then run expanded checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T21:10:05Z
  TYPE: FACT
  CLAIM: Required-input metadata is appended to the new source kind's injection IR/signature rows;
    ordinary six-field rows remain unchanged. The existing Meld success fixture now models the
    owning book/resolution callback and asserts resolution rebuild after structural revalidation.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:861-955
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1210-1280
  - tests/unit/melder/aether/conduit/meld/test_meld.py:1527-1559
  IMPACT: S3 has complete model/plan and injection-export metadata without changing ordinary row layouts.
  NEXT: Run expanded compiler, DevOps state, runtime gating and default-precedence compatibility; then refresh docs/assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T21:13:05Z
  TYPE: MEASURE
  CLAIM: Expanded compiler/DevOps/Meld/default/post-bind suite passes 1961 tests in 4.11s. Runtime
    transition and injection-export regressions are green. Remaining validation adds the specific
    creation-system fast-path/chunking tests and final style checks; no repeated full-suite churn.
    Ruff UP045 contradicts the selected role's explicit Optional/Union requirement; retain that
    typing policy and exclude only UP045 in the scoped style command, without editing lint policy.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/expanded_compatibility.log:1-30
  - artifacts/override_required_compiler_20260919/lint.log:1-100
  IMPACT: Compiler behavior is qualified within the affected scope; S4 direct/input/cache enforcement remains.
  NEXT: Complete the remaining focused checks and refresh source docs/graph/builds.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T21:18:28Z
  TYPE: MEASURE
  CLAIM: Remaining creation-system/state/multithreading/matrix checks pass: 137 tests in 0.64s after
    five native capability fixture updates. Together with the disjoint 1961-case expanded group,
    2098 focused tests pass. New-file Ruff passes with only role-required UP045 excluded. Whitespace
    passes with existing CRLF tolerated. Production changes and new tests are ready for doc/asset sync.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/remaining_compatibility_green.log:1-3
  - artifacts/override_required_compiler_20260919/expanded_compatibility.log:1-30
  IMPACT: No known failures remain in the checked groups. Full repository coverage, S4 runtime input
    enforcement, nested runtime transition matrices and S6 cache/replay qualification remain unclaimed.
  NEXT: Refresh changed descriptors and authored compiler/revalidation docs, then rebuild generated assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:35:03Z
  TYPE: MEASURE
  CLAIM: Re-entry verified the saved 1961-case and disjoint 137-case passing reports. Source build
    recorded 452 documentation entries, 629 guard entries and four system documents for 0.2.40;
    LLM build recorded 585 source files and 826 test files. Final check outputs were not retained
    before compaction, so no final check result is inferred from those successful build logs.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/expanded_compatibility.log:1-30
  - artifacts/override_required_compiler_20260919/remaining_compatibility_green.log:1-3
  - artifacts/override_required_compiler_20260919/build_source.log:1-3
  - artifacts/override_required_compiler_20260919/build_llm.log:1-4
  IMPACT: Source implementation is preserved. Finish check-mode/style verification, then replace
    the stale early-stage handoff and synchronize S3 with its downstream story contracts.
  NEXT: Run source/LLM asset checks, scoped style and whitespace verification with retained outputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:36:40Z
  TYPE: MEASURE
  CLAIM: Final source build check and LLM check pass with exit 0; src/tests/other fingerprints and
    output proofs match. Scoped Ruff passes for the new component file and three retained tools,
    excluding only UP045 to follow the role's Optional/Union requirement. Whitespace check also
    exits 0 with existing CRLF tolerated. No feature or lint configuration changed in this pass.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/check_source.log:1-3
  - artifacts/override_required_compiler_20260919/check_llm.log:1-3
  - artifacts/override_required_compiler_20260919/check_style.log:1-1
  IMPACT: Generated assets and scoped style qualification are current. Compiler delivery can enter
    review after its durable handoff is synchronized; S4/S5/S6 remain required before release.
  NEXT: Record validation scope and update the S3 task/story plus the S4/S5/S6 handoffs and routing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:38:40Z
  TYPE: FACT
  CLAIM: S3 delivery is review-ready. XML inspection confirms 2098 distinct passing cases and all
    42 new component cases. Authored source docs and indexes are refreshed; 22 S3 descriptors were
    mechanically refreshed with scoped authored deltas. Source/LLM builds and final checks pass.
    The task/story and S4/S5/S6 handoffs now separate delivered compiler metadata from unimplemented
    runtime enforcement and graph/replay work. Patch contracts remain available pending acceptance.
  EVIDENCE:
  - artifacts/override_required_compiler_20260919/validation.md:1-72
  - artifacts/override_required_compiler_20260919/graph_refresh.log:1-22
  - system_docs/src_architecture.md:802-827
  IMPACT: S3 can be reviewed without reconstructing early notes. No release or feature-completion
    claim is made; the required next implementation boundary is S4.
  NEXT: Open S4's runtime task from its delivered-schema handoff before any execution-policy edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T00:25:59Z
  TYPE: DECISION
  CLAIM: Owner-authorized feature turn-in is complete for this record. Both later reported failures
    are repaired: crystal test-double capability and current-run local cancellation forwarding.
    This acceptance retains ordinary Python errors, existing version rules and documented limits.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/validation.md:1-78
  - artifacts/non_resolvable_followup_20260919/validation.md:1-50
  IMPACT: Record is done; validation evidence is retained and promoted patch contracts are archived.
  NEXT: none; reopen only for a new owner-requested change or new failure evidence.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
CLOSED at 2026-09-20T00:25:59Z. Implemented resolved reference-only inputs, executable-root filtering and existing revalidation integration.
Final evidence and limits are in the graph/replay and follow-up validation artifacts.
No next implementation step remains in this accepted record.

### Historical pre-closure handoff
S3 is implemented and in review. 2098 distinct focused tests pass, including 42 new compiler component
cases. Source/LLM generated assets, scoped Ruff, whitespace and document-index checks pass. Read
`artifacts/override_required_compiler_20260919/validation.md` for exact evidence and limits. Full
repository suite/coverage and complete feature qualification are not claimed. Existing S2 and earlier
owner closure/backlog changes remain intact; no S3 release, commit, wheel or version bump occurred.

Delivered: resolved SocketKind.OVERRIDE_REQUIRED; descriptive referenced_spell_ids and parameter_kind;
Phase-3 implicit/explicit/collection/default policy; Phase-4 construction/contract/cycle diagnostics;
Phase-5 executable root filtering; direct Phase8-11 and scheduling/cache admission; Phase-8 complete
topology signatures; Phase-9 injection sources and IR/signature export; both planner families/variants.
Original declarations, ordinary defaults and provider artifact publication authority remain intact.

Required-input rows are immutable tuples of (name, position, parameter-kind name, reference-ID tuple),
derived from local topology into injection specs and retained on every plan step. Generalized steps
retain inject_spec in both variants; standalone many-only steps have no inject_spec. Requiredness is
separate from optional override-targeting metadata, so stripped targeting cannot discard it.

Selector sensitivity reuses SpellSystemStates' existing frame-key watcher, including Optional/ForwardRef
normalization. Meld now gates the old conduit-local resolution verdict after a successful structural
rerun through _force_resolution_revalidation(reason=structure_changed). Real direct-consumer notch and
new-provider transitions pass. Full nested transition matrices still belong to later qualification.

NEXT: read `tickets/stories/completed/2026-09-19_discoverable_resolution_runtime_story.md`, create its first
runtime task/patch and follow the source map. Live Phase11 export is CodegenCreationSchemaHelpers,
not the legacy SharedCompilerExecutions twin. S4 must hydrate/enforce required_override_params in
executors and cover direct/reuse/fast/nested/scoped/cached doors. S5 consumes local descriptive
references for Nexus graph/history; S6 persists/replays the native policy and accepted graph schema.
These remaining layers are required before the feature can ship.

Use .venv_new (Python 3.14.7 free-threaded) via uv --no-sync --offline with task-local UV_CACHE_DIR.
Disable pytest cacheprovider; no agents. REONBOARD after compaction before resuming. The owner selected
OVERRIDE_REQUIRED and existing version rules. Patch docs stay in their active directory until turn-in.
