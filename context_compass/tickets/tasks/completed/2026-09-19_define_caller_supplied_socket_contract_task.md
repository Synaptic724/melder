# Task: Define the resolved caller-supplied socket contract

## Completion
- Completed: 2026-09-20T00:25:59Z
- Summary: Defined the accepted OVERRIDE_REQUIRED schema and propagation; later owner direction retained ordinary constructor errors.
- Acceptance: Owner requested turn-in, then required two repairs first; both are verified.

## Metadata
- Task ID: TASK-2026-09-19-define-caller-supplied-socket-contract
- Story: STORY-2026-09-19-discoverable-registration-contract-discovery
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T17:25:45Z
- Updated: 2026-09-20T00:25:59Z

## Objective
Choose the smallest explicit resolved socket representation that preserves target/requiredness/graph
meaning and is consumed consistently by validation, planning and override execution.

## Ticket Contract
- ENTRY_GATE: Complete ContextCompass re-entry if a compaction occurred; read the parent epic, S1,
  previous trace's latest recommendation, and this task before investigating.
- EXECUTION_BOUNDARY: Read Phase-3 output records, required-hole/cycle validation, analyzer/model/planner
  and override-targeting consumers. Record a schema and semantic table; no runtime/test edits.
- DEPENDENCIES: Default-True per-Spell modifier direction and prior registration/compiler trace.
- EXIT_GATE: Proposed category/fields, lifecycle owner, propagation path, semantics and first regression
  cases are concrete enough to scope S2-S4 implementation tasks; unresolved decisions are explicit.
- FAILURE_ESCALATION: Record genuine product choices; do not resurrect PLAIN coercion or add unrelated APIs.

## Scope Boundaries
- In scope: one required dependency targeting a False registration, plus the minimum contrasting cases.
- Out of scope: implementing the feature, broad source graph redesign, new ownership/lifetimes or full test runs.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner-authorized turn-in after delivered scope and reported failure repairs passed.

## Current Direction
- Public API: resolvable: bool = True on bind/bind_inactive and forwarding facades.
- Store capability per Spell version; activity/index selection stays independent.
- Preserve the original signature/annotation/default declaration.
- Use an explicit caller-supplied category in resolved sockets. Do not mutate _di_shape or make
  ordinary PLAIN carry unrelated special flags.
- A required input needs caller supply at construction; an ordinary default remains honored.
- Keep the registered target relationship in Nexus without creating an executable dependency edge.
- Normal matching implementations remain resolvable; definition registration does not globally poison a type.

## Required Reading Before Work
1. `tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md`.
2. `tickets/stories/completed/2026-09-19_discoverable_registration_contract_discovery_story.md`.
3. `tickets/tasks/completed/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md` — read the
   latest strategy note and handoff before the earlier PLAIN proposal; that proposal is superseded.
4. Verify `system_docs/src_components_index.md`; read SpellCompiler and Validation Pipeline,
   DI Descriptors and Contract Sockets, and Meld Resolution Runtime. Verify graph-index slices
   for the specific source files before changing implementation in later tasks.
5. Reopen the declaration/result records and Phase-3/4 consumers:
   - `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_parameter_requirements.py`
   - `src/melder/aether/spellbook/spell_compiler/symbolic_graph/spell_symbolic_dependency.py`
   - `src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py`
   - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py`
   - `src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py`
   - `src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py`
6. Follow the resolved socket through the first downstream consumers:
   - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py`
   - `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py`
   - `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_override_targeting_processor_strategy.py`
   - `src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_override_targeting_analysis.py`
   - `src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py`
   - `src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py`
   - `src/melder/aether/conduit/meld/overrides/spell_overrider.py`
   Select the generated-lane consumer only after identifying its actual input; read complete relevant code.
7. Before designing executable tests, read test architecture/component indexes and existing required-hole,
   binding-cycle, default-precedence, and nested override tests named in S3/S4.

## Steps / Checklist
- [x] Re-establish latest direction and existing evidence without repeating broad orientation unnecessarily.
- [x] Trace what required-hole validation considers an unresolved failure today.
- [x] Trace which fields analyzer/model/planner and override targeting need for one caller-supplied input.
- [x] Specify category location, target reference, required/default policy and lifecycle ownership.
- [x] Explain how Phase-4 validation consumes resolved input policy without rewriting Phase-1 declarations.
- [x] Define direct target, normal provider, required input, defaulted input and absent-target cases.
- [x] List remaining Optional/collection/descriptor/ambiguous-target decisions without silently choosing them.
- [x] Record the smallest real Base/Consumer regression set for the first implementation slice.
- [x] Hand the proposed schema and dependency changes to S1, S3 and S4; retain one next action.

## Deliverables
- Source-backed field/category proposal and propagation diagram/table.
- Semantic table separating declarations, graph references and executable input supply.
- First regression cases and remaining decisions before implementation.

## OVERRIDE_REQUIRED Contract (Name and Meaning Accepted; Not Implemented)

Use the existing resolved socket vocabulary: append SocketKind.OVERRIDE_REQUIRED. Leave
ParameterDIShape and Phase-1/2 declaration objects unchanged. NORMAL still covers ordinary PLAIN
and normal DI sockets; SPELL_CONTRACT keeps its linked-provider lifecycle.

| Owner / field | Proposed meaning |
| --- | --- |
| Spell.resolvable | Default-True, immutable registration/version capability from the parent epic. |
| SpellSocketDescriptor.socket_kind | OVERRIDE_REQUIRED after Phase 3 identifies a required input targeting a non-resolvable registration. |
| SpellSocketDescriptor.target_spell_ids | Execution providers only; empty for caller-supplied input. |
| SpellSocketDescriptor.referenced_spell_ids | New tuple of registered version IDs for descriptive graph links; never executable dependencies. |
| OVERRIDE_REQUIRED requiredness | Encoded by the category itself; no separate requires_caller_value boolean is necessary. |
| SpellInjectionParamSource.kind | Add override_required rows even when the occurrence dependency map has no entry. |
| Injection/plan input row | Preserve consumer instance/path, parameter name/position/kind, requiredness and referenced target IDs. |

The owner selected OVERRIDE_REQUIRED and accepted its explained meaning on 2026-09-19. Detailed
projection fields remain the implementation proposal. Ordinary defaults remain PLAIN, so this category
always means the value is required and needs no independent requiredness flag. Reuse the
current ownership chain: SpellSystemStates owns local topology; the compiler artifact owns model/plan
outputs; model.injection_shape owns its parameter-source mapping. Runtime call values remain borrowed
inputs. No new source registry, creation store, lifetime, or automatic disposal of supplied values.

Derive requiredness from the resolved supply policy and the real declaration. For this initial
annotation case, no Python default means a value is required even with Optional[T]. Ordinary defaults
stay PLAIN and retain their value. Do not use has_default blindly for a future SpellMap/SpellContract
case: those objects are DI instructions, not usable application defaults.

## Propagation and Validation Boundary

```text
Phase 1/2: original annotation, signature kind and default facts
    -> Phase 3: selected provider OR caller-supplied outcome
         -> descriptive reference IDs -> Nexus / history / persistence (S5/S6)
         -> executable target IDs -> DAG / order / reuse (normal providers only)
         -> caller-supplied socket -> Phase-4 diagnostic + Phase-5 SocketRef
              -> Phase-9 explicit input row -> both Phase-10 lane variants
                   -> Phase-11 emitted checks and hydrated namespaces (S4)
```

- Phase 4: retain existing PLAIN required-hole warnings and add a distinct diagnostic for resolved
  caller-supplied requirements, including consumer/parameter/target. Missing call data is not a
  conjure-time error. Borrow topology into the validation context or use its canonical registry;
  do not rewrite requirements or reconstruct provider edges from the annotation alone.
- Binding cycles: consume executable resolved policy. A descriptive caller-supplied reference cannot
  cause a construction cycle; actual executable cycles must still fail. Audit other construction
  validators in S3 rather than assuming the binding-key strategy is the only one.
- Phase 5 already creates the consumer SocketRef even without targets. Preserve that behavior and
  stop traversal at caller-supplied sockets. Do not expose a fake child construction path below them.
- Phase 8 must not enqueue referenced_spell_ids. Include kind/requiredness/reference-policy fields
  in the existing signature inputs where they affect consumed semantics; use normal invalidation.
- Phase 9 should read the resolved topology for explicit caller-supplied rows, retaining collection
  handling independently. Empty dependency lists already mean an empty collection in existing paths.
- Phase 10 must retain required-input rows in both lane variants. They are construction obligations,
  so stripping optional override-targeting metadata must not strip them.
- Phase 11/S4 must bind the same input contract into solo, generalized and many-only executors and
  cached hydration. Solo currently compiles from Spell directly, so adding plan fields alone is insufficient.
- Normalize existing override targeting and effective arguments before checking presence. Use mapping
  membership / valid positional coverage, never truthiness of the value. An explicit None is present;
  whether a particular type permits it is a separate validation policy, not an omission test.
- Check only consumers that the operation will construct. A reused consumer or a supplied whole branch
  must not require its unexecuted constructor inputs again. Preserve existing override-on-shared-instance
  restrictions. Preflight reachable missing inputs before avoidable construction side effects; S4 must
  prove its ordering against reuse, branch replacement and hooks with real execution tests.
- Proposed runtime failure uses the existing structured MeldExecutionError with consumer, parameter
  and target identity, e.g. Consumer.base requires a supplied value for non-resolvable Base; pass
  override={"base": value}. Direct meld of Base is a separate non-resolvable-registration error.

## Semantic Table for the First Slice

These are recommended outcomes to qualify after the remaining S1 choices, not observed feature results.

| Input / selection | Resolved meaning | Construction behavior |
| --- | --- | --- |
| Directly select a False registration | Discoverable definition | Meld/reuse-only resolution refuses. |
| Required Base input; unique False target, no real provider | OVERRIDE_REQUIRED, graph reference retained | Supplied value passed by identity; omission raises clearly. |
| Optional[Base] without default; same selection | OVERRIDE_REQUIRED, still required | Omission fails; explicit None counts as supplied. |
| Base or Optional[Base] with an ordinary default | Existing PLAIN | Default wins; explicit override can replace it. |
| Required Base; one eligible resolvable provider | Existing provider DI | Resolve normally; a discoverable definition does not poison the type. |
| Required Base; no matching registration at all | Existing missing provider | Keep the current failure; no implicit external-input feature. |
| Multiple eligible resolvable providers | Existing ambiguity | Keep the current disambiguation requirement. |
| Consumer already exists and normal reuse applies | Existing lifetime/reuse | Return it without demanding constructor inputs again. |
| Whole consumer branch supplied as an override | Existing branch replacement | Do not demand inputs below the replaced branch. |

## Remaining Product Choices and Unverified Paths

- Matching precedence needs an explicit S1 ruling: recommend normal eligible providers first for
  annotation/frame lookup, then a unique discovery-only definition when no provider exists. An explicit
  selection of a False registration must not silently switch to another registration. Multiple False
  matches, named selections and parked versions still need a complete decision table.
- Collection and explicit SpellMap/SpellContract references to False targets remain undecided. Preserve
  existing valid collection/descriptor behavior; do not silently convert a whole collection or contract.
- Recommend retaining current override type-check policy for this feature. Introducing general runtime
  ABC/Protocol/Optional value validation would be a separate policy change; this pass only defines presence.
- Generalized dual-plan packing, many-only fast arrays, runtime hook input changes, branch pruning,
  reuse door ordering, IR serialization and cold/warm hydration were not traced fully here. S3/S4 carry
  exact entry points and must prove all lanes before feature completion. No performance claim is made.
- Registration fingerprint compatibility, body-only source revisions, graph-only edge revisions,
  abstract-root descriptive analysis and S5/S6 graph persistence remain broader S1/epic obligations.

## First Regression Design

Read test architecture/component slices and the required-hole/default-precedence tests plus the custom
nested override fixture/cases. Tests below are proposed, not created, executed or marked xfail.

1. Bind an abstract Base as False and a required Consumer. Conjure succeeds; Base has no creation plan
   and is not constructed, while the consumer's resolved metadata retains Base's version reference.
   Include a descriptive back-reference: it must not create a construction-cycle error, while the
   corresponding cycle made of real executable providers must still fail.
2. Supply a real Concrete(Base) instance through override={"base": instance}; Consumer.base is that
   exact object. Direct meld of the registered Base refuses with a capability-specific message.
3. Omit the required value: get the targeted missing-input error before Consumer constructor effects;
   include an otherwise constructible dependency with a counter to test earlier preflight ordering.
4. Optional[Base] without a default still rejects omission; explicit None is distinguishable from
   omission. Use a falsey Base implementation to prove presence checks do not test object truthiness.
5. Defaulted Base/Optional[Base] keeps None or its selected instance even with the False registration;
   retain the existing ordinary-default suite as compatibility evidence.
6. Add one real resolvable Base provider; normal DI still works under the accepted selection rule.
   Keep no-registration and multiple-provider failures as contrasting controls.
7. Add Outer -> Consumer and supply consumer>base; test exact path and existing broadcast/unique
   precedence. Supplying Consumer itself prunes its constructor's required Base input.
8. Reuse an already-created unique Consumer without repeating the input; preserve the established
   failure when an override attempts to mutate an already-existing shared consumer.
9. Repeat the first direct/nested cases after cache hydration and target-local revalidation. Include
   the real no-overrides lane so the feature cannot pass by testing only override executors.

Initial placement: compiler metadata/validation cases in S3 component tests; actual construction,
side effects, nested values, reuse and cache parity in S4 runtime tests. Keep the first Base/Consumer
case small, then add the above contrasts as each execution boundary is implemented.

## Files / Paths Impacted
- This task and parent story/epic notes plus coordination boards.
- No production or test source changes in this task.

## Validation
- Runtime tests: Not run. This task is discovery/schema design; no executable tests or runtime edits.
- Documentation: relevant index hashes/counts verified, source/test paths checked, changed sections
  reread, and whitespace checks run. Source and test trees remain unchanged.
- Reopen full relevant methods; search output only locates the consumer.

## Risks / Rollback Notes
- Required-hole or cycle validation may still treat supplied inputs as missing runtime providers.
- Ordinary Optional flags do not necessarily mean callers may omit a required Python argument.
- Existing plan families may infer supply from empty target lists; trace rather than assume parity.

## Applicable Anti-Patterns
- [x] No PLAIN coercion or private declaration mutation.
- [x] No target-edge loss or fake None default.
- [x] No schema selected before reading its consumers.

## Done Checklist
- [x] Required consumers read and evidence recorded.
- [x] Schema, semantic table and regression plan prepared.
- [x] Remaining choices visible and parent story synchronized.
- [x] Owner discussion/acceptance recorded before implementation proceeds.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none until a separate artifact is produced.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: required-hole validation, resolved input category, target references and override IR.
- IF_UNKNOWN: none

## Noting Behavior
Read one complete unit, then append evidence, impact and one NEXT before continuing into another consumer.

## Notes
- DATETIME: 2026-09-19T18:23:39Z
  TYPE: PLAN
  CLAIM: Owner directed this ready task to begin. Re-entry is complete and the prior trace's latest
    recommendation is reread. Start at required-hole validation, then trace resolved socket records
    into occurrence analysis, injection/override models, planning and the selected execution consumer.
    This is the discovery/schema task; feature implementation remains a subsequent story.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md:355-392
  - tickets/stories/completed/2026-09-19_discoverable_registration_contract_discovery_story.md:62-114
  IMPACT: Work proceeds from the selected explicit supplied-input direction without repeating bind discovery.
  NEXT: Read the relevant component slices and required-hole validation with its resolved input records.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-19T17:25:45Z
  TYPE: PLAN
  CLAIM: This is the next bounded discovery after the first trace. Registration/API placement is
    established as direction; the unresolved question is the shared caller-supplied socket contract.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py:11-228
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:173-279
  IMPACT: Future implementation begins from explicit semantics rather than another interpretation of PLAIN.
  NEXT: Read required_holes_strategy.py and trace its treatment of empty-target required sockets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:25:29Z
  TYPE: FACT
  CLAIM: RequiredHolesStrategy only warns for Phase-1 PLAIN parameters with has_default=False;
    it never reads Phase-3 topology. BindingResolutionCycleStrategy separately rebuilds key edges
    from Phase-1 annotations/descriptors. SpellSocketDescriptor only carries NORMAL/CONTRACT kind,
    DI optionality, target IDs and keys; it has no caller-supplied category or has_default field.
    SpellParameterRequirement already keeps has_default separate from DI optionality, so declaration
    truth need not be rewritten to express a later supplied-input decision.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py:61-104
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements.py:261-305
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:170-275
  - src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py:11-87
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_parameter_requirements.py:72-152
  IMPACT: Adding a resolved kind alone will not update either validator. Requiredness must follow
    real default presence, and execution-cycle validation must exclude resolved supplied edges while
    their descriptive target relationships survive. No source or executable tests changed.
  NEXT: Read Phase 3 end to end, then its occurrence analyzer to locate where resolved policy is lost.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:26:25Z
  TYPE: FACT
  CLAIM: Phase 3 currently uses one resolved-candidate list to produce both topology target_spell_ids
    and executable DAG edges/dependency IDs. It maps socket kind solely from the original symbolic
    shape. Single-annotation lookup raises on zero/multiple matches; collection lookup may be empty.
    Therefore a supplied target needs an explicit resolution outcome before DAG publication, with
    descriptive target IDs retained separately from executable target IDs. Filtering candidates out
    without preserving that outcome would turn a known supplied input into an ordinary missing provider.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-572
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:681-898
  IMPACT: The category belongs to resolved policy, not Phase-1 declaration mutation. The current
    candidate-index and scan lanes both need the same policy split; matching/ambiguity semantics must
    stay explicit when real providers and discovery-only definitions share an annotation.
  NEXT: Trace the occurrence analyzer's parameter records and construction-edge selection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:27:02Z
  TYPE: FACT
  CLAIM: Phase 8 expands every topology target_spell_id as an executable occurrence without inspecting
    socket_kind. Empty required collection targets become an empty dependency list for [] injection;
    other empty sockets are omitted. Its topology reuse signature currently contains parameter names
    and target IDs only. A new kind with descriptive IDs stuffed into target_spell_ids would therefore
    still construct the definition, while a kind-only change could be absent from that signature.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:373-468
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:850-964
  IMPACT: Keep target_spell_ids execution-only. Carry descriptive registration references separately,
    explicitly preserve supplied-input metadata outside the dependency map, and add semantic fields
    to the existing input-signature machinery. Do not invent a replacement cache invalidation system.
  NEXT: Trace Phase-9 injection and override targeting to determine the narrow required-input payload.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:28:15Z
  TYPE: FACT
  CLAIM: Phase 9 builds param_sources only from occurrence dependency entries and contract payloads.
    SpellInjectionParamSource already has an explicit kind, but currently documents dependency/contract
    only and carries no required-input metadata. Ordinary no-edge parameters do not acquire a source
    row. Override targeting is independently derived from blueprint socket_refs and preserves their
    kind as an integer alongside consumer node, parameter name and path; its geometry need not become
    a new target-selection system. SpellCodegenModel owns the injection/targeting sections.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:129-272
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:9-191
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_override_targeting_processor_strategy.py:48-125
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:43-301
  IMPACT: Recommend explicit supplied rows in injection_shape, populated from resolved topology rather
    than fabricated dependency entries. Reuse targeting geometry while carrying requiredness, position
    and descriptive target identity through the existing owned model/plan sections.
  NEXT: Follow blueprint socket publication, solo plan selection and its actual compiled override input.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:31:19Z
  TYPE: FACT
  CLAIM: Phase 5 already publishes a SocketRef for every topology socket before traversing that
    socket's target IDs, so a caller-supplied parameter can remain override-addressable with zero
    construction targets. Solo discovery accepts one executable visible spell when collections are
    absent. Its plan builder retains injection specs but strips override keys from the no-overrides
    variant; its actual generated executors receive Spell and directly call the target (or forward
    args/kwargs) without consulting a required-input plan. Adding a source-kind row alone cannot enforce
    the requested missing-input diagnostic. This is source analysis, not a public-meld test.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:435-490
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/solo_codegen_plan_discovery_strategy.py:48-81
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1463-1608
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1893-1952
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2700-2758
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:6-237
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:7-307
  IMPACT: Existing socket paths can be reused; required-input metadata must survive BOTH lane variants
    and reach compiler/hydrator namespaces. Enforcement belongs at construction boundaries after effective
    override/reuse decisions, with earlier preflight where side effects can be avoided. Full generalized,
    many-only, hooks, and cache hydration qualification remains S3/S4 work, not proven by this solo trace.
  NEXT: Read targeted test context, then record the concrete schema, semantic table and minimal regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:38:58Z
  TYPE: FACT
  CLAIM: The concrete schema, propagation boundary, semantic table, remaining choices and nine
    regression groups are recorded above. Read required-hole and default-precedence tests in full;
    read cyclic/acyclic/key-shape and nested override fixture/precedence/reuse cases by complete units.
    Existing required-hole tests use Phase-1 stubs, so add real resolved-topology tests rather than
    treating those stubs as proof of the new contract. Parent S1/epic and S3/S4 now carry this result.
    Source/test trees are unchanged; no runtime test, build, benchmark, or release was executed.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_required_holes_strategy.py:41-97
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_binding_resolution_cycle_strategy.py:295-402
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_binding_resolution_cycle_strategy.py:624-680
  - tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py:218-404
  - tests/component/melder/aether/conduit/test_conduit_component_meld_overrides_deep.py:717-974
  IMPACT: This discovery task can be reviewed from its durable result. It does not claim S1 or the
    feature is complete; candidate matching, descriptor/collection policy and identity remain open.
  NEXT: Discuss the supplied-socket proposal and settle provider-versus-definition selection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:45:34Z
  TYPE: DECISION
  CLAIM: Owner selected OVERRIDE_REQUIRED instead of CALLER_SUPPLIED for clarity and approved
    continuing. The accepted meaning is a known registered target whose required consumer argument
    must be provided through overrides. Ordinary defaults remain PLAIN. The category already states
    requiredness, so the earlier separate requires_caller_value boolean is unnecessary in the proposal.
    Prior notes retain the old spelling as historical evidence; current contract text uses the new name.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_define_caller_supplied_socket_contract_task.md:89-116
  IMPACT: The internal category name and core meaning are settled. Continue the selection decision
    in the new bounded S1 task; no runtime rename or feature code exists yet.
  NEXT: Read tickets/tasks/completed/2026-09-19_define_discoverable_registration_selection_task.md.
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
CLOSED at 2026-09-20T00:25:59Z. Defined the accepted OVERRIDE_REQUIRED schema and propagation; later owner direction retained ordinary constructor errors.
Final evidence and limits are in the graph/replay and follow-up validation artifacts.
No next implementation step remains in this accepted record.

### Historical pre-closure handoff
Review-ready. Proposed Contract, Propagation, Semantic Table, Remaining Product Choices and First
Regression Design contain the result. The owner selected SocketKind.OVERRIDE_REQUIRED, execution-only target IDs,
separate referenced IDs, explicit requiredness, and a supplied row propagated through injection/plan
and emitted/hydrated execution. Phase 5 already retains no-edge SocketRefs. Phase 4 and Phase 8 do not
currently understand this distinction; solo execution also needs an explicit enforcement handoff.

Next: use tickets/tasks/completed/2026-09-19_define_discoverable_registration_selection_task.md to settle S1
candidate-selection/descriptor/collection decisions. Source traces are recorded below the initial plan; no source/test code changed
and no tests were executed. After compaction, complete REONBOARD and read this result before reopening
source. The 2,758-line lane-plan module was read by complete relevant methods/classes, not in full;
full source reads remain required before edits. Other generated families/hydrators remain S3/S4 work.
