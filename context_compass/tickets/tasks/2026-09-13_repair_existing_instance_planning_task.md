# Task: Reproduce and repair existing-instance planning

## Metadata
- Task ID: TASK-2026-09-13-repair-existing-instance-planning
- Story: STORY-2026-09-13-existing-instance-planning
- Status: review
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-13T18:14:07Z
- Updated: 2026-09-13T23:35:50Z

## Objective
Investigate existing-object planning, deferred annotations, type-frame admission and disposal;
preserve supplied-object injection and distinguish implementation bugs from policy decisions.

## Current Focus
Owner-requested fresh direct-dependency test passes: externally created A is registered and supplied
by exact identity to newly constructed B. Broader reference/blueprint/lifetime ideas remain discussion only.
Existing-instance injection repair is implemented and verified natively; see instance_repair_result.md.
Original Iris construction now succeeds, but its subsequent builder-cleanup assertion still fails.
Owner parks disposal/lifecycle in EPIC-2026-09-13-existing-object-lifecycle-ownership, including transfer.
Resume the remaining existing-instance frame-admission error: compare Protocol rejection for class
and instance providers, preserving ordinary concrete/string frame grouping policy.
Native Protocol regressions now reproduce four failures with fourteen passing controls; no source fix yet.
Owner folds Protocol validation into the deferred existing-object epic's construction/validation/ownership model.
Annotation work is accepted and closed. Provider-artifact repair remains parked separately.

## Ticket Contract
- ENTRY_GATE: linked owner-authorized epic/story and routed native task.
- EXECUTION_BOUNDARY: rerun the existing direct supplied-value dependency test; no new design discovery or runtime edits.
- DEPENDENCIES: real dedicated Iris ChannelLogger ActivityBootstrap test and accepted consultation.
- EXIT_GATE: native regressions/control cases and original logger/bootstrap/cleanup assertions pass.
- FAILURE_ESCALATION: preserve the supplied object/API; no wrapper, fake acceptance logger or validation bypass.

## Scope Boundaries
- In scope: existing-instance injection and frame-admission consistency, with focused native regression evidence.
- Deferred lifecycle epic: tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md.
- Out of scope: Optional/default semantics, Iris ownership redesign, release/publication or consumer changes.

## Steps
- [x] Read original logger test and both current iterators.
- [x] Reproduce non-callable dependency planning and cover both stages.
- [x] Experiment with root/direct/nested/collection/map/late-bound injection and callable factory behavior.
- [x] Expand existing-object characterization across lookup, sharing, overrides, reuse and cleanup.
- [x] Compare stock planning against a labeled test-only two-iterator correction to expose later gaps.
- [ ] Investigate all four confirmed gaps and identify source owners, repair boundaries and open decisions.
- [x] Apply the separately approved Python 3.14 annotation acquisition fix and verify its regression suites/assets.
- [x] Correct existing-object branches according to the recorded leaf-provider contract.
- [x] Validate exact object identity and ordinary class/factory contract-default controls.
- [x] Run original dedicated logger acceptance unchanged against a process-local source overlay.
- [x] Refresh and verify generated source/test assets.
- [ ] Obtain full downstream acceptance; original builder-cleanup failure remains outside this injection repair.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: requested direct existing-object dependency regression passed on the current checkout.

## Validation
The expanded 66-case characterization distinguishes stock outcomes from the test-only scanner
diagnostic. Two stock regression files contain 21 cases: 14 expected failures and 7 passing controls.
The earlier 11-case characterization remains preserved. See gap_analysis.md for proof limits.
Those are pre-repair observations. The annotation-only repair now passes 271 selected tests,
including 15 live deferred-annotation regressions. Existing-object planning remains unfixed.
Current result supersedes that planning status: all 21 instance regressions now pass within a
140-test selected set. The original dedicated-Iris test reaches construction and fails at cleanup.

## Risks / Rollback Notes
Both iterators contain the reported branch. The callable-object acceptance wording needs discussion:
BindingProfileStrategy currently classifies non-class callables as factories. Do not change that
public binding policy while repairing supported non-callable existing-instance planning.

## Catch-up Read Map (Required Before Resuming)
Current Protocol focus:
- tests/component/melder/spellbook/test_existing_instance_protocol_admission.py: 18 native cases.
- artifacts/existing_instance_planning_20260913/protocol_admission_red.log/xml: four failures, fourteen controls.
- artifacts/existing_instance_planning_20260913/frame_admission_characterization.log: original stock behavior.
- src/melder/aether/spellbook/bind/bind.py: _bind_logic Protocol branch and _structurally_implements_protocol.
- src/melder/aether/spellbook/spell_compiler/validation/strategies/existing_creation_compatibility_strategy.py.
- tests/unit/melder/spellbook/bind/test_bind.py:1091-1102 currently asserts incompatible-instance acceptance.
- Disposal/transfer resumption belongs to the separately deferred existing-object lifecycle epic.

Start with this task's latest Notes and the parent epic. Existing-instance planning is now the
owner-selected active repair. Existing objects MUST remain injectable into
consumers; opacity means no new constructor discovery on the supplied object, not exclusion from DI.

Orientation (verify indexes before slicing):
- system_docs/src_architecture.md: System Context, Bind/Conjure/Meld sequences and Operational Invariants.
- system_docs/src_components_index.md -> SpellCompiler and Validation Pipeline; Binding Pipeline;
  DI Descriptors and Contract Sockets; Meld Resolution Runtime.
- system_docs/src_graph_index.md -> the exact source-file sections below. Source is authoritative:
  some graph source stamps lag the current files.

Source / contracts:
- src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:
  build_profile class/callable/instance dispatch, _build_instance_profile and _build_callable_profile.
- src/melder/aether/spellbook/bind/bind.py: _bind_logic, _validate_binding and _determine_spell_type.
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py: _matches_annotation and
  candidate-index construction; concrete-type instance DI matches the explicit spellframe, not type(instance).
- src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:
  build_requirements existing-creation branch (no constructor DI).
- src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:
  analyze, _build_occurrence_graph, _collect_occurrence_dependencies, _apply_spell_contract_dependencies,
  _iter_spell_contract_defaults. Entire 1,173-line file was read before this handoff.
- src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:
  process, _compile_contract_overrides_for_occurrence and _iter_spell_contract_defaults.
  Entire 409-line file was read.
- src/melder/aether/conduit/meld/creation_context/creation_context_builder.py: build and the three
  existing-object executors, including the existing-object override refusal.
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:
  _resolve_single_by_annotation (435-507) refuses a missing ordinary inferred provider.
- src/melder/aether/conduit/meld/conduit_meld.py: meld normalizes the override before validation,
  but only consumes it in the runtime executor after validation/readiness (349-451).
- src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py:
  PLAIN supports caller/default values; SPELL_CONTRACT represents the deferred provider socket.
- src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:
  _build_parameter_requirements (968-1086) requests inspect.signature with eager annotation values;
  a missing deferred annotation name raises before the later annotation resolver can run.
- src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/resolution_profile_strategy.py:
  build_profile calls Phase 1 during bind, explaining the earlier annotation failure boundary.
- src/melder/aether/spellbook/bind/bind.py: class-only disposal matching (424-443) and class-only
  protocol structural validation (468-491); these differ from admitting an existing instance.
- src/melder/aether/conduit/conduit.py: _register_to_creations (1386-1427) and meld_existing_spell
  (4109 onward; its ID input is spell=, not the newer meld facade's spell_id=).
- src/melder/aether/conduit/creations/creations.py: cleanup and disposal (150-254), add_creation
  (267-300); lifetime tracking and explicit disposal metadata remain distinct.

Tests and original real-input evidence:
- tests/integration/melder/spellbook/test_existing_instance_planning.py (new native red regressions;
  initial callable-instance assumptions and missing type-frame setup are corrected).
- tests/experimentation/test_existing_instance_injection_experiment.py (11 characterization cases).
- tests/experimentation/test_existing_instance_gap_experiment.py (66 stock/diagnostic observations).
- tests/integration/melder/spellbook/test_existing_instance_additional_regressions.py (11 new stock cases).
- artifacts/existing_instance_planning_20260913/instance_repair_result.md (current implementation and limits).
- artifacts/existing_instance_planning_20260913/instance_repair_final.log/xml (140 native checks pass).
- artifacts/existing_instance_planning_20260913/iris_existing_logger_acceptance.xml (original cleanup failure).
- tests/unit/melder/spellbook/spell_compiler/test_contract_scanner_failure_types.py (negative-path controls).
- tests/integration/melder/spellbook/test_deferred_annotations.py (15 live annotation-repair regressions).
- artifacts/existing_instance_planning_20260913/annotation_patch_result.md (implemented annotation scope/proofs).
- artifacts/existing_instance_planning_20260913/annotation_acquisition_probe_before_fix.py:
  archived test-only prototype, moved out of default pytest collection after the production fix.
- src/melder/aether/conduit/meld/meld.py: _iter_spell_contract_defaults now uses FORWARDREF too;
  the original two-file prototype did not exercise this separate late-bind inspection point.
- artifacts/existing_instance_planning_20260913/gap_analysis.md (expanded findings and boundaries).
- artifacts/existing_instance_planning_20260913/gap_observations.json (all 66 measured rows).
- artifacts/existing_instance_planning_20260913/expanded_regressions.log (14 red, 7 green).
- tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:1767-1844:
  misleading injection-success title currently asserts the known failure; fix with the eventual repair.
- tests/component/melder/spellbook/test_ordered_disposal_binding.py:210-220:
  explicit existing-policy control excludes prebuilt objects from disposal matching.
- tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:314-343:
  existing tests for supplying a required plain argument and replacing a registered dependency.
- artifacts/existing_instance_planning_20260913/experiment_findings.md (concise outcomes and proof limits).
- artifacts/existing_instance_planning_20260913/experiments_corrected.log (all 11 recorded outcomes).
- artifacts/existing_instance_planning_20260913/red_native.log (initial run; distinguish fixture
  precondition failures from the two actual iterator TypeErrors).
- ../../priv_commandops/context_compass/tickets/tasks/2026-09-13_native_provider_runtime_expert_review_task.md
- ../../priv_commandops/tests/component/spectrum/test_area_bootstraps.py:
  test_activity_root_uses_real_dedicated_logger_and_releases_builder_custody, lines 197-255.
- ../../priv_commandops/tests/component/spectrum/conftest.py (real singleton reset fixture).
- ../../priv_commandops/src/command_ops/command_center/activity/builder.py: TYPE_CHECKING logger
  annotation remains a name token in that module; do not confuse it with the concrete-type native fixture.
- ../../priv_commandops/context_compass/artifacts/2026-09-13_area_bootstraps/dedicated_logger_0240.log

Open experiment questions:
- Compare root lookup with direct, nested, collection and explicit SpellMap injection of existing objects.
- Compare unqualified registration, explicit type-frame registration and named string-frame lookup.
- Characterize callable-object factory binding separately; the public classification is not decided by
  the Phase-8/9 existing-creation branch, and changing it requires a separate owner decision.
- Preserve original CommandOps test bodies and real Iris input; native fixtures are complementary evidence.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/existing_instance_planning_20260913/
  - artifacts/existing_instance_planning_20260913/existing_object_disposal_blast_radius.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain compact reproduction/validation evidence for owner acceptance.

## External DI References and Discussion Boundaries
Owner supplied these comparisons; their primary documentation was read on 2026-09-13.

- [Autofac instance components](https://docs.autofac.org/en/latest/register/registration.html#instance-components):
  an existing component exposes service types; external disposal ownership is a separate explicit choice.
- [Autofac resolve parameters](https://docs.autofac.org/en/latest/resolve/parameters.html):
  callers can provide required arguments during resolution by name, exact type or a matching predicate.
- [Autofac log4net integration](https://docs.autofac.org/en/latest/examples/log4net.html):
  middleware obtains the logger from LogManager for the consuming component and supplies it.
- [Dishka context inputs](https://dishka.readthedocs.io/en/latest/provider/from_context.html):
  a declared type is supplied by context at its scope; consumers request the normal dependency type.
- [Dishka providers/finalization](https://dishka.readthedocs.io/en/latest/provider/provide.html):
  factories and generator teardown provide separate construction/lifecycle mechanisms.
- [Dependency Injector Object](https://python-dependency-injector.ets-labs.org/providers/object.html):
  returns the supplied object unchanged.
- [Dependency Injector Factory](https://python-dependency-injector.ets-labs.org/providers/factory.html):
  injects configured dependencies and gives call-time keyword values precedence.
- [Dependency Injector Dependency](https://python-dependency-injector.ets-labs.org/providers/dependency.html):
  supports typed required placeholders, checked on provision, with an error when unsupplied.
- [Dependency Injector Resource](https://python-dependency-injector.ets-labs.org/providers/resource.html):
  provides explicit initialization/shutdown and injection of the resulting resource.

Melder interpretation for discussion, not a selected implementation:
- Keep requirement type/name, value-supply mechanism and cleanup ownership as separate concerns.
- A required logger: ChannelLogger can be satisfied by a registered existing instance. Registering
  ChannelLogger itself as a constructor/factory is not necessary; Optional/default=None is not necessary.
- Preserve the consumer-to-provider dependency edge. The existing provider has no new constructor work.
- An already registered instance and an argument promised only at meld time are different cases.
  Declared runtime-only input, validation timing, type checks and actual supplied-instance recording
  need an explicit graph contract; they are not silently added to the current two bug repairs.
- Iris acquisition and logger teardown custody remain explicit. Creation outside Melder alone does
  not settle which owner is responsible for cleanup.
- Current native tests already preserve required consumer parameters. Explicit type-frame matching
  versus automatic type(instance) exposure remains a lookup/API question for owner discussion.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: record concrete uncertainty before patching.

## Notes
- DATETIME: 2026-09-13T18:14:07Z
  TYPE: FACT
  CLAIM: Current analyzer SHA256 is 5b6de6157a1f8bbd963da56491c0ed7570217c0032c62b7ce456948ff40b6cdb;
    processor SHA256 is b2254bbf4f0d9cbc83334b86283d57cac9827fb10a8ecfc3a1e4fb5de1cb7529.
    Both exactly match the accepted 0.2.40 consultation, without new execution claims.
  EVIDENCE:
  - ../../priv_commandops/context_compass/tickets/tasks/2026-09-13_native_provider_runtime_expert_review_task.md
  - tickets/epics/2026-09-13_provider_artifact_ownership_and_existing_instance_planning_epic.md:134-143
  IMPACT: Verify current branches and retain the original real logger acceptance input.
  NEXT: Read original test and planning iterator bodies, then write the native failing cases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-13T18:20:50Z
  TYPE: FACT
  CLAIM: Both complete iterator implementations explicitly inspect existing instances. Phase 8
    calls its iterator for every dependency occurrence; Phase 9 does so when compiling occurrence
    overrides. Existing-root exclusion does not cover either dependency traversal. Phase 1 and
    CreationContextBuilder instead treat existing objects as supplied values without constructor DI.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:710-1032
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:125-261
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:68-234
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:231-257
  IMPACT: Existing instances must return an empty contract-default sequence in both helpers. Preserve
    the later requirements/signature discovery paths for ordinary class and factory bindings.
  NEXT: Add native non-callable/callable instance and both-iterator regressions before changing source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T18:29:42Z
  TYPE: DECISION
  CLAIM: Owner pauses production changes and requests further experiments, regression cases and
    explicit catch-up read maps in both tasks. Existing objects remain injectable into consumers;
    opaque planning means no constructor discovery on already-supplied values. Added those maps.
    Native setup exposed two facts: concrete-type instance injection requires a matching spellframe,
    and BindingProfileStrategy currently treats non-class callable objects as factories. Correct
    those new fixture assumptions instead of widening the two-fix scope or changing public binding.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:42-64
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:177-250
  - artifacts/existing_instance_planning_20260913/red_native.log
  - Owner's experiment-before-change instruction in this conversation.
  IMPACT: No production source changes are authorized in this step. The initial draft regression
    source is archived; supported existing-instance regressions and separate callable characterization follow.
  NEXT: Compare root, direct/nested/collection/explicit-map injection and callable factory behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T18:37:44Z
  TYPE: MEASURE
  CLAIM: Eleven characterization cases pass while recording current outcomes: existing root identity
    works in three lookup forms; concrete instance injection needs matching type-frame metadata;
    direct/nested/collection/SpellMap/late-bound injection then reaches signature inspection failure.
    Callable object binding is a factory path: root and explicit-map controls each call it once at meld.
    Corrected-contract regressions: seven expected failures and three root controls passing, zero errors.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/experiments_corrected.log:1-13
  - artifacts/existing_instance_planning_20260913/experiment_findings.md
  - artifacts/provider_artifact_ownership_20260913/regressions_discussion_final.xml
  IMPACT: Existing-object injection is the intended preserved contract, not merely direct lookup.
    No source change has been made; current callable dispatch remains an open separate API question.
  NEXT: Discuss these results with the owner before choosing a production patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T18:42:49Z
  TYPE: FACT
  CLAIM: Read the owner's primary Autofac, Dishka and Dependency Injector references. They support
    typed externally supplied values without registering the value's class as a constructor and
    without making the consuming parameter optional. Required input, provider mechanism and cleanup
    ownership are distinct. Added exact external reread links and bounded Melder design questions.
  EVIDENCE:
  - This ticket's External DI References and Discussion Boundaries section.
  - https://docs.autofac.org/en/latest/register/registration.html#instance-components
  - https://dishka.readthedocs.io/en/latest/provider/from_context.html
  - https://python-dependency-injector.ets-labs.org/providers/dependency.html
  IMPACT: Existing-instance injection remains the current repair contract. Required meld-time inputs
    and recording their supplied object need separate design discussion; no source/API change is selected.
  NEXT: Continue owner discussion of provider identity, runtime-only inputs and explicit lifecycle custody.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T18:50:19Z
  TYPE: FACT
  CLAIM: After compaction, reread the role baseline and the relevant component sections through
    the verified current index (8,460 lines, 136 sections). The documented contract distinguishes
    type-frame instance injection from constructor work, and per-call overrides from provider
    selection. The statement that existing creations bypass phases 8-11 must be read alongside
    the recorded dependency-occurrence failures, not used to claim those paths already work.
  EVIDENCE:
  - system_docs/src_components.md:339-716
  - system_docs/src_components.md:2330-2846
  - system_docs/src_components.md:3507-3611
  - system_docs/src_components.md:4056-4100
  - system_docs/src_components.md:4127-4189
  - system_docs/src_components.md:4710-4753
  - system_docs/src_components.md:5356-5421
  - artifacts/existing_instance_planning_20260913/experiment_findings.md:1-34
  IMPACT: Owner explicitly requested these component rereads. Keep the supplied value injectable;
    constructor opacity is not removal of the consumer dependency. Production changes remain paused.
  NEXT: Reopen the current classification, matching, iterator and existing-object execution methods.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T18:50:19Z
  TYPE: FACT
  CLAIM: Current source reread confirms the existing-instance mismatch: Phase 1 returns zero
    constructor requirements, Phase 3 can match its explicit type frame, and runtime executors
    return the supplied object. Both Phase-8/9 contract iterators nevertheless inspect that
    instance's signature. The existing-root override refusal concerns overriding an already
    created object; it must not be confused with supplying that object to a new consumer.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:42-64
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:177-250
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:187-270
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:851-1032
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:125-261
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:68-234
  IMPACT: The repair proposal remains local to constructor-contract discovery for existing values.
    Automatic concrete-type exposure, callable-as-value binding, meld-time required inputs and
    cleanup custody remain separate decisions. No production code was edited or tests rerun.
  NEXT: Discuss the preserved required consumer edge and supplied-instance identity with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T18:56:25Z
  TYPE: FACT
  CLAIM: The conventional-DI comparison needs a narrower distinction than "Melder lacks runtime
    input support." Melder has per-call overrides and declared SpellContract holes. Existing
    tests cover a required PLAIN argument supplied by override and replacement of a registered
    dependency. Ordinary SINGLE_BY_ANNOTATION resolution still refuses zero providers in Phase 3;
    ConduitMeld performs validation/readiness before consuming the override in its executor.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-507
  - src/melder/aether/conduit/meld/conduit_meld.py:349-451
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:10-201
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py:3-70
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:314-343
  - https://docs.autofac.org/en/latest/resolve/parameters.html
  - https://python-dependency-injector.ets-labs.org/providers/dependency.html
  IMPACT: The ordinary required typed parameter cannot rely on a future override to satisfy the
    earlier registry lookup. Autofac resolve parameters and Dependency Injector typed placeholders
    establish the comparison. This is distinct from the existing-instance planning bug; do not
    generalize it into a claim that all Melder deferred-provider paths are absent or unusable.
    New tests were not run in this comparison; no production changes were made.
  NEXT: Discuss whether the owner wants a declared caller-supplied typed input beyond current overrides/contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:01:45Z
  TYPE: PLAN
  CLAIM: Owner requests more existing-object gap tests. Extend characterization around matching,
    direct/linked/scope injection, overrides and lifecycle. Use stock behavior as the baseline;
    a separately labeled test-only replacement of the two known signature-inspection branches
    may reveal downstream failures currently hidden behind them. All other validation remains real.
  EVIDENCE:
  - Owner instruction to check current existing-object gaps and run more testing.
  - tests/experimentation/test_existing_instance_injection_experiment.py:1-137
  - tests/integration/melder/spellbook/test_existing_instance_planning.py:1-178
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:985-1032
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:218-261
  IMPACT: Scope is test code, evidence and ticket/read-map maintenance. A test-only correction is
    hypothesis isolation, not shipped code, passing acceptance or permission to change runtime policy.
    Keep callable-as-value and new meld-time-input APIs out of implementation.
  NEXT: Read the test maps and existing-object registration/disposal paths, then add the gap experiment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:03:57Z
  TYPE: FACT
  CLAIM: Broader reads expose a coverage problem and a lifecycle boundary. The older test named
    test_existing_instance_frame_type_hint_injects_existing actually expects the non-callable
    planning failure, so a green result does not prove injection. Bind explicitly retains disposal
    methods only for ClassBindingProfile; prebuilt objects receive an empty disposal list even
    when names are requested. Protocol structural validation also checks class profiles only.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:1767-1844
  - src/melder/aether/spellbook/bind/bind.py:364-520
  - src/melder/aether/conduit/conduit.py:1386-1427
  - src/melder/aether/conduit/creations/creations.py:150-254
  - src/melder/aether/conduit/creations/creations.py:267-300
  IMPACT: Characterize existing-object disposal and mismatched declared frames rather than assuming
    ownership/type enforcement. Preserve the old test for now, but flag it for correction with the
    eventual repair. Source/test maps were reread; graph index hash and line count verified current.
  NEXT: Add stock/isolated-scanner experiments with observable identity, call and disposal outcomes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:09:01Z
  TYPE: PLAN
  CLAIM: Added tests/experimentation/test_existing_instance_gap_experiment.py. It compares stock
    and test-only leaf planning, plus public lookup forms, linked providers, scoped reuse,
    default/override precedence, mismatched frames and observable disposal calls. Runtime errors
    are recorded as refusals; successful paths assert exact identity. Assertions are not swallowed.
  EVIDENCE:
  - tests/experimentation/test_existing_instance_gap_experiment.py:1-411
  - tests/component/melder/spellbook/test_ordered_disposal_binding.py:210-220
  IMPACT: The new diagnostic does not modify production code. Existing disposal exclusion is
    separately corroborated by an older component test, so report it as policy scope, not a new fix.
  NEXT: Execute the expanded experiment and review every GAP row before adding regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:09:01Z
  TYPE: FACT
  CLAIM: The first expanded run stopped all 53 cases in fixture setup: the reused book's config
    was already frozen, so setting worker count was invalid. Removed that unnecessary setup
    mutation; this is a test error, not an existing-object runtime gap. Full Ruff also flags
    repository-required Optional/descriptor-default/fixture-alias patterns; use the scoped F/I
    check and fix import ordering without changing those contracts.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/gaps_initial.log:1-20
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:207-246
  IMPACT: No valid runtime observations came from that run; do not count its setup errors as defects.
  NEXT: Rerun the corrected fixture and review the actual stock/leaf-probe outcomes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-13T19:10:43Z
  TYPE: MEASURE
  CLAIM: Corrected 53-case run produced 51 recorded cases and two NameError failures. Stock
    ordinary/linked injection stops at the known scanners; the isolated two-scanner correction
    preserves identity through direct/nested/collection/pair/function/map/override/linked paths.
    All six real root lookup forms and six eager/late direct scope cases succeed. Existing
    disposal invokes nothing despite requested dispose; the class control invokes it once.
    Incompatible instance frames are accepted at bind and reach consumers after scanner isolation.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/gaps_corrected.log:1-51
  - artifacts/existing_instance_planning_20260913/gaps_corrected.log:53-173
  - src/melder/aether/spellbook/bind/bind.py:424-491
  IMPACT: A genuinely deferred TYPE_CHECKING-only annotation fails in inspect.signature during
    requirements extraction before planning; compare an explicit string and class-provider control.
    Scope identity and disposal are distinct. Matching metadata does not prove runtime type
    compatibility. None of the diagnostic successes constitutes an implemented repair.
  NEXT: Add annotation controls, consumer scope cases and stock regressions for the expanded paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:15:40Z
  TYPE: MEASURE
  CLAIM: Expanded experiment now records all 66 cases without setup errors. Fourteen correct
    injection scenarios blocked by stock scanners complete with exact identity under the isolated
    correction, including consumer scope reuse. Deferred TYPE_CHECKING annotations fail during
    bind in both modes and also with a class provider; a literal string annotation gets past bind.
    Protocol class controls distinguish invalid rejection from the admitted existing instance.
    Added eleven stock regression cases; together with the original ten: 14 failed, 7 passed.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/gaps_final.log:1-68
  - artifacts/existing_instance_planning_20260913/expanded_regressions.log
  - tests/integration/melder/spellbook/test_existing_instance_additional_regressions.py
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:968-1086
  IMPACT: The stock failures are 13 planning refusals and one deferred-annotation NameError.
    The existing object is usable and retains identity once the two known scanners are isolated.
    Disposal and type-frame admission remain policy gaps for discussion, not newly selected fixes.
    Scoped Ruff F/I checks pass. No production source changes or downstream environment replacement.
  NEXT: Publish the gap matrix and regenerate/verify the test corpus, then return to owner discussion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:19:34Z
  TYPE: FACT
  CLAIM: Published gap_analysis.md and all 66 parsed observations. Rebuilt the tests corpus with
    --include-untracked (820 files); --check confirms matching fingerprint/output proofs and both
    new files appear in the index. Scoped F/I lint passes. Interpreter is confirmed Python 3.14.7
    free-threaded; source version is 0.2.40. git diff --numstat -- src is empty.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/gap_analysis.md
  - artifacts/existing_instance_planning_20260913/gap_observations.json
  - artifacts/existing_instance_planning_20260913/gaps_test_bundle_build.log:1-2
  - artifacts/existing_instance_planning_20260913/gaps_test_bundle_check.log:1-1
  - llm_support/llm_full_tests_index.md:173-173
  - llm_support/llm_full_tests_index.md:300-300
  IMPACT: The expanded experiment tranche is complete and durable; tasks/boards route back to
    discussion. Production fixes, cached-plan/serialization stress and original Iris acceptance
    remain outside this completed test tranche.
  NEXT: Owner reviews the confirmed injection/annotation bugs and decides frame/cleanup semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:29:49Z
  TYPE: PLAN
  CLAIM: Owner authorizes deeper investigation of all four reported areas: the two planning
    scanners, Python 3.14 deferred annotations, existing-instance frame validation and disposal.
    Trace each source owner and existing test/policy boundary, then record a bounded repair
    proposal and unresolved decisions. Use focused diagnostic tests where source leaves uncertainty.
  EVIDENCE:
  - Owner instruction: those four areas should be investigated.
  - artifacts/existing_instance_planning_20260913/gap_analysis.md
  IMPACT: Investigation/test authorization is explicit; production semantics remain unchanged.
    The separate provider-artifact ownership failure remains in its own task.
  NEXT: Read existing-creation validation and annotation acquisition, then examine frame/disposal policy seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:34:39Z
  TYPE: DECISION
  CLAIM: Owner narrows execution to annotation acquisition only, one issue at a time. Existing
    planning, frame validation and disposal investigations are parked. Two annotation acquisition
    hazards are confirmed: inspect.signature defaults to value evaluation, and the fallback reads
    __annotations__ directly while catching only AttributeError. Both can raise NameError.
  EVIDENCE:
  - Owner instruction to focus only on the annotation issue first.
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:425-545
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:968-1086
  - https://docs.python.org/3.14/library/annotationlib.html
  IMPACT: Probe Python 3.14 FORWARDREF acquisition with real class providers to avoid mixing in
    the existing-instance scanner bug. Preserve known annotation objects, ordinary defaults and
    missing-provider refusal. Production changes remain paused while the localized correction is tested.
  NEXT: Compare stock, signature-only and complete annotation acquisition in one focused experiment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:34:39Z
  TYPE: MEASURE
  CLAIM: Thirteen focused annotation checks pass as diagnostic comparisons. Stock acquisition
    raises NameError in all four inputs (class/function/list/default). Signature-only partial
    evaluation reaches the second NameError at direct __annotations__ access. Partial signature
    plus partial annotation acquisition succeeds through real class-provider meld in all four.
    One known-signature control retains exact signature equality and fingerprint text.
  EVIDENCE:
  - tests/experimentation/test_deferred_annotation_acquisition_experiment.py
  - artifacts/existing_instance_planning_20260913/annotation_acquisition.log:1-14
  - https://docs.python.org/3.14/library/annotationlib.html
  IMPACT: The correction is localized to acquisition; normalizing ForwardRefs and provider lookup
    already work for these inputs. The prototype touches only two module references and one finder
    method in memory. It does not change production files, other three gaps, or public DI semantics.
  NEXT: Verify missing required providers still fail, refresh the test bundle and report the isolated result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:38:36Z
  TYPE: MEASURE
  CLAIM: Fourteen annotation-only diagnostics pass. Partial acquisition preserves required
    class/function injection, collection elements, None defaults and the known-signature control;
    a missing provider still fails at normal Phase-3 validation. The owner now explicitly requests
    an explanation of the proposed patch before any production implementation.
  EVIDENCE:
  - tests/experimentation/test_deferred_annotation_acquisition_experiment.py
  - artifacts/existing_instance_planning_20260913/annotation_acquisition_final.log:1-14
  - artifacts/existing_instance_planning_20260913/annotation_acquisition_final.xml
  - Owner instruction: explain the patch before doing it.
  IMPACT: Proposed scope is BindingProfileStrategy signature acquisition plus requirements-finder
    signature/annotation acquisition. Preserve the existing namespace normalization and DI
    classification; unresolved names remain dependency requests, never empty requirements or Any.
    No source patch is applied; other gaps remain parked. Scoped F/I lint passes.
  NEXT: Explain the annotation-only patch and its proof limits to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:44:37Z
  TYPE: DECISION
  CLAIM: Owner approves applying the annotation-only correction using Python 3.14+ facilities.
    TYPE_CHECKING controls import execution; ForwardRef is the runtime representation retained
    when an annotation name is unavailable. Read both source implementations completely. Keep
    class-level profile annotation semantics and existing namespace/string normalization intact.
  EVIDENCE:
  - Owner approval to apply the explained patch and stay on the Python 3.14+ baseline.
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:1-244
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1-1321
  - tests/integration/melder/spellbook/test_deferred_annotations.py
  IMPACT: This internal acquisition repair restores documented normalization behavior without
    changing graph schema, dependency policy, API, lifecycle, or subsystem boundaries. Update
    touched docstrings and regenerate source/test assets; the other gaps remain out of scope.
  NEXT: Record the new live-regression red baseline, then change only the two acquisition modules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:44:37Z
  TYPE: MEASURE
  CLAIM: New unpatched live regressions reproduced nine NameError failures and two passing
    compatibility controls. Applied the approved correction to the two source modules: FORWARDREF
    signature acquisition for classes/callables/fresh requirements, partial raw annotation reads,
    and a partial-evaluation fallback after namespace-aware string evaluation fails.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/annotation_red.log
  - tests/integration/melder/spellbook/test_deferred_annotations.py
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py
  IMPACT: Existing normalizers/classifiers and class-level profile annotations are preserved.
    No changes to the other gaps, runtime ownership or lifetime policy. Touched docstrings explain
    deferred acquisition. Validate live behavior now, not the earlier monkeypatched prototype.
  NEXT: Run the new live regressions plus existing binding/requirements/future-annotation suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T19:47:43Z
  TYPE: MEASURE
  CLAIM: First live suite run passed 117 cases. Three late-bind cases expose the same eager
    signature read in Meld._iter_spell_contract_defaults; this reader runs during meld-time
    contract checks. Two other failures are a new test's wrong has_live_creation keyword
    (its public ID input is spell=). Correct the fixture and the third annotation reader.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/annotation_patch_validation.log
  - src/melder/aether/conduit/meld/meld.py:595-638
  - src/melder/aether/conduit/meld/meld.py:891-1005
  - src/melder/aether/conduit/conduit.py:4188-4205
  IMPACT: The necessary scope now includes one Format keyword and import in Meld; its contract
    detection/gating logic remains unchanged. Read the complete 1,558-line implementation before
    editing. This is the same approved annotation defect, not the parked existing-object planner repair.
  NEXT: Correct that signature acquisition and verify late-bind plus explicit override cases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T20:28:39Z
  TYPE: FACT
  CLAIM: The 212-case run has no annotation NameErrors. Its five failures are unrelated extra
    assertions in the new tests: three successful late-bind injections are followed by a provider
    remeld that hits the separately tracked missing-codegen failure; two required overrides
    preserve replacement identity but still materialize the registered provider. Use the public
    reuse-only door for identity checks and restrict non-materialization assertions to PLAIN defaults.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/annotation_patch_final.log:1-97
  - src/melder/aether/conduit/meld/conduit_meld.py:458-580
  - tests/integration/melder/spellbook/test_deferred_annotations.py
  IMPACT: Preserve the original failure logs; do not widen the annotation patch to fix provider
    artifact ownership or override execution policy. No original acceptance test was weakened.
    The former prototype must be archived because its stock-NameError assertions are now obsolete.
  NEXT: Run corrected annotation validation and rebuild the generated source/test assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T20:31:42Z
  TYPE: MEASURE
  CLAIM: The corrected live validation set passes 271 tests: 15 native deferred-annotation
    regressions plus existing requirements, binding profiles, future/string annotations, Meld,
    defaults and overrides. No temporary scanner/acquisition override is installed in this run.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/annotation_patch_green.log:1-5
  - artifacts/existing_instance_planning_20260913/annotation_patch_green.xml
  - tests/integration/melder/spellbook/test_deferred_annotations.py
  IMPACT: The approved annotation-only fix works before/after conjure, retains exact injected and
    overridden values, honors defaults and preserves missing-provider refusal. Archive the now-
    obsolete stock-failure prototype; refresh the three touched source descriptors and build assets.
  NEXT: Refresh generated assets, verify their checks and review the final three-module diff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T20:38:21Z
  TYPE: FACT
  CLAIM: Annotation-only repair is complete locally: 271 selected tests pass, new test lint and
    source correctness checks pass, graph/index proof passes, all source asset checks pass, and
    source/test bundle proofs match. Archived the obsolete in-memory diagnostic. Final result
    document and source read map are current; the three other existing-object gaps stay parked.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/annotation_patch_result.md
  - artifacts/existing_instance_planning_20260913/annotation_patch_green.log:1-5
  - artifacts/existing_instance_planning_20260913/annotation_source_assets_check.log:1-3
  - artifacts/existing_instance_planning_20260913/annotation_src_bundle_check.log:1-1
  - artifacts/existing_instance_planning_20260913/annotation_live_tests_bundle_check.log:1-1
  IMPACT: Review the three production modules plus their generated assets. No source changes to
    the existing-instance scanners, frame admission or disposal; no new wheel or downstream install.
  NEXT: Owner reviews the annotation-only result and selects any next issue separately.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T20:42:12Z
  TYPE: DECISION
  CLAIM: Owner accepts annotation work, requests its ticket turn-in, and authorizes the next issue.
    Materialized a completed annotation-only record so this unresolved instance task stays open.
    Select the original injection bug next: both contract scanners must treat existing providers
    as leaves while preserving consumer edges. Frame/disposal and provider-artifact repairs stay parked.
  EVIDENCE:
  - Owner instruction to close annotations and continue with the next issue.
  - tickets/tasks/completed/2026-09-13_repair_deferred_annotation_acquisition_task.md
  - artifacts/existing_instance_planning_20260913/gap_analysis.md
  IMPACT: Preserve the approved annotation changes. Re-read both complete scanner implementations,
    run the existing red regressions, then make the focused correction and update obsolete failure assertions.
  NEXT: Complete both source reads and record the current instance-regression baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T20:45:53Z
  TYPE: MEASURE
  CLAIM: Fresh instance baseline on the synchronized environment (pytest 9.1.1) remains 14 failed,
    seven passed. Both complete scanner implementations were read. Existing provider occurrences
    reach both helpers even though existing roots skip analysis; their constructor-contract scan
    is the incorrect operation. Five older integration cases assert that defect instead of injection.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/instance_repair_red.log
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1-1173
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:1-409
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:1545-1656
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:1767-1846
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_more.py:390-491
  IMPACT: Return an empty contract sequence for existing values in both helpers. Preserve class/
    factory discovery, dependency edges and all ownership semantics. Environment sync completed
    before the baseline; no competing environment mutation was performed by this task.
  NEXT: Apply the two guards and run the native regression files before changing legacy expectations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T20:52:43Z
  TYPE: MEASURE
  CLAIM: Both existing-value branches now return no constructor contracts. The 21 existing-object
    regressions and 15 accepted annotation regressions pass (36 total). Updated five legacy tests
    from asserting the known failure to asserting selected instance identity, named/frame routing,
    and mixed collection ordering/lifetimes. Their original purpose is now actually tested.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/instance_repair_initial_green.log:1-2
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_more.py
  IMPACT: Consumer edges and normal class/factory discovery remain unchanged. Annotation work is
    closed separately. Broader existing resolution/contract tests and the real Iris acceptance
    remain to be verified before claiming the instance repair complete.
  NEXT: Run the relevant resolution/contract suites and inspect the original downstream logger setup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T20:58:50Z
  TYPE: MEASURE
  CLAIM: Native resolution/contract validation passes 115 cases; compiler analyzer/migration/family
    controls pass another 23. The original unchanged CommandOps dedicated-Iris test was run with
    its .venv314 interpreter and a process-local PYTHONPATH pointing at current Melder source.
    Source identity was asserted before execution; no package/environment replacement occurred.
    Logger binding, builder creation and both activity/default/many-lifetime assertions pass;
    the test then fails at builder.cleaned after root.cleanup, line 244.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/instance_repair_validation.log:1-3
  - artifacts/existing_instance_planning_20260913/instance_compiler_controls.log:1-2
  - artifacts/existing_instance_planning_20260913/iris_source_preflight.log:1-1
  - artifacts/existing_instance_planning_20260913/iris_existing_logger_acceptance.xml
  - ../../priv_commandops/tests/component/spectrum/test_area_bootstraps.py:197-255
  - ../../priv_commandops/tests/conftest.py:1-25
  IMPACT: The original planning failure is repaired on the real input, but full downstream
    acceptance remains red at cleanup. Its root cause is not established and is outside the
    current injection-only patch. Pytest's sessionfinish os._exit explains the terse console;
    JUnit preserves the complete assertion. Do not claim the whole real-Iris test passed.
  NEXT: Refresh source/test assets and hand off the injection repair with the cleanup failure explicit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T21:03:07Z
  TYPE: FACT
  CLAIM: Source checks found an existing missing MeldExecutionError import in the same analyzer's
    missing/ambiguous-contract failure path. Added that import and a two-scanner negative-path
    control so the preserved class/factory contract behavior raises the documented exception.
    Two F821 findings in the legacy integration file are intentional unresolved annotation strings.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1033-1072
  - tests/unit/melder/spellbook/spell_compiler/test_contract_scanner_failure_types.py
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:542-542
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:1097-1097
  IMPACT: This is a same-scanner error-contract correction; no frame or lifecycle policy changed.
    Keep intentional missing-name test inputs rather than suppressing or resolving them.
  NEXT: Verify the negative controls and final focused set, then refresh the two scanner descriptors/assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T21:11:38Z
  TYPE: FACT
  CLAIM: Existing-instance injection repair is ready for review. Final 140-test native set passes,
    source/new-test checks pass, graph/index proof passes, all durable source asset checks pass,
    and source/test bundle proofs match. Final source diff is limited to the two scanners and
    the same analyzer's missing exception import; prior annotation changes are preserved.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/instance_repair_result.md
  - artifacts/existing_instance_planning_20260913/instance_repair_final.log:1-3
  - artifacts/existing_instance_planning_20260913/instance_source_assets_check.log:1-3
  - artifacts/existing_instance_planning_20260913/instance_src_bundle_check.log:1-1
  - artifacts/existing_instance_planning_20260913/instance_test_bundle_check.log:1-1
  IMPACT: Full original Iris acceptance remains red at builder cleanup; no frame/disposal fix or
    installed CommandOps package replacement was performed. Annotation closure is recorded separately.
  NEXT: Owner reviews the injection repair and chooses the next investigation, including the cleanup failure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T21:24:53Z
  TYPE: DECISION
  CLAIM: Owner selects issue #4, cleanup/disposal, and points at creation objects. Re-onboarding
    is complete under the retained updater_0 identity and earlier CERTIFY: APPROVED authorization.
    Trace bind-time callback selection and creation cleanup before choosing a production change.
  EVIDENCE:
  - Owner instruction: keep moving and hit up 4 in the creations objects.
  - artifacts/existing_instance_planning_20260913/instance_repair_result.md
  - This task's 2026-09-13T20:58:50Z original-Iris cleanup result.
  IMPACT: Do not assume the builder cleanup failure is caused by the prebuilt-instance exclusion.
    Keep the two cases distinguishable; preserve the accepted annotation and injection repairs.
  NEXT: Read verified component/graph slices and trace callback selection through Creations teardown.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T21:29:00Z
  TYPE: FACT
  CLAIM: Complete reads of Creations, ConduitCreations, Bind and BindingProfileStrategy establish
    the disposal path: the store executes received method lists; Bind filters candidates against
    ClassBindingProfile.method_names only. That profile enumerates cls.__dict__ callables only,
    excluding inherited-only methods. Prebuilt profiles have no such list and receive no disposal.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:150-300
  - src/melder/aether/spellbook/bind/bind.py:315-522
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:66-136
  - tests/component/melder/spellbook/test_ordered_disposal_binding.py:210-220
  - system_docs/src_components.md:499-615
  - system_docs/src_components.md:2330-2456
  IMPACT: The old test explicitly preserves both exclusions; they are recorded behavior, not
    evidence of a broken cleanup loop. Original Iris fixture disables book disposal and its logger
    is deliberately borrowed, so inspect the builder's declared methods and bootstrap candidates.
  NEXT: Trace ActivityBootstrap registration and ActivityBuilder cleanup inheritance, then reproduce natively.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T21:30:26Z
  TYPE: FACT
  CLAIM: The original ActivityBuilder cleanup failure has a separate configuration explanation:
    ActivityBuilder declares cleanup directly, ActivityBootstrap binds without disposal names,
    and the original fixture leaves book names at the empty default. Creations receives no
    disposal entry. The prebuilt logger is deliberately borrowed by the book in that test.
  EVIDENCE:
  - ../priv_commandops/tests/component/spectrum/test_area_bootstraps.py:22-64 (repository-relative)
  - ../priv_commandops/tests/component/spectrum/test_area_bootstraps.py:197-255 (repository-relative)
  - ../priv_commandops/src/command_ops/command_center/spectrum/bootstraps/activity_bootstrap.py:27-45
  - ../priv_commandops/src/command_ops/command_center/activity/builder.py:48-110
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:564-594
  - src/melder/aether/spellbook/spellbook.py:5134-5161
  - src/melder/aether/conduit/conduit.py:1386-1427
  IMPACT: Do not claim that enabling prebuilt-instance disposal repairs this downstream test.
    No new tests or production changes were made during the disposal investigation so far.
  NEXT: Discuss explicit instance-bind custody separately from configuring downstream class disposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T21:30:26Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner asks to discuss the contract and favors explicit prebound disposal names on bind.
    Recommendation: an existing instance without explicit per-bind names is borrowed; explicit
    per-bind names opt into cleanup by its owning container. Book-level defaults should not
    silently transfer cleanup custody for prebuilt objects. This is a proposal, not an applied change.
  EVIDENCE:
  - Owner message: association provides reference and maybe management; explicit names in bind seem reasonable.
  - src/melder/aether/spellbook/bind/bind.py:315-522
  IMPACT: Discussion supersedes the pending choice question and pauses implementation/testing.
    Preserve existing class/factory behavior and the accepted annotation/injection fixes.
  NEXT: Settle the prebuilt-instance explicit-disposal ownership contract with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T21:36:13Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner proposes the exact configuration key existing_objects_configured_dispose_applied,
    disabled by default, with a setter. Recommended meaning: False excludes book-level names
    for prebuilt objects while explicit per-bind names remain effective; True merges both groups
    under the same order, overlap ownership and priority rules as class bindings. Configure before bind.
  EVIDENCE:
  - Owner message proposing the exact setter/key and default-disabled posture, asking for design discussion.
  - src/melder/aether/spellbook/bind/bind.py:315-522
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:1128-1179
  IMPACT: This refines the prior explicit-only proposal with a book-wide opt-in. No implementation
    has begun. Do not broaden factory handling, inherited class-method discovery or ownership scopes.
  NEXT: Discuss this two-mode contract and its configuration/recording update map with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T21:36:13Z
  TYPE: FACT
  CLAIM: The recording path already carries arbitrary registered plain configuration values:
    freeze emits every property, SpellbookCrystal retains/describes the dictionary, and restore
    reloads it before binding. Property allowlisting/defaults and honest legacy backfill reporting
    belong to SpellbookConfiguration. No separate Crystallizer boolean field is required by this path.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:112-156
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:265-402
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:440-493
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:567-675
  - src/melder/crystallizer/crystals/spellbook_crystal.py:92-141
  - src/melder/crystallizer/crystals/spellbook_crystal.py:244-264
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1738-1818
  - tests/component/melder/crystallizer/test_disposal_configuration_transport.py:45-112
  IMPACT: Proposed implementation must cover eager/default/reset property state, bool validation,
    fluent setter/freeze, reload/backfill, normal and inactive binding forwarding, instance method
    matching, ordered metadata, docs and generated assets. Test False/True/legacy checkpoint transport.
    The existing Creations path needs no new policy lookup; this does not recreate supplied objects.
  NEXT: Present the bounded implementation scope while preserving discussion-only status.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T21:44:39Z
  TYPE: DECISION
  CLAIM: Owner accepts the proposed default-disabled configuration contract and requests the
    blast-radius map before implementation. Explicit per-bind names apply in both modes; True
    additionally applies configured book names under ordinary disposal composition rules.
  EVIDENCE:
  - Owner message accepting the contract and requesting a blast-radius map, then implementation later.
  - This task's 2026-09-13T21:36:13Z proposal and recording-path evidence.
  IMPACT: This tranche is source inspection and durable design only. Map exact producers, carriers,
    consumers, legacy records, public documentation, generated assets and regressions.
  NEXT: Trace remaining configuration/binding adapters and lifecycle/persistence consumers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T21:48:00Z
  TYPE: FACT
  CLAIM: The flag's producer path is concentrated in configuration, Spellbook.bind/bind_inactive,
    and Bind. SpellBinder forwards kwargs; Nexus frame conversion constructs ordinary defaults.
    Spell already retains ordered disposal metadata; Phase-11 signatures already include it.
    Existing-value executors return the supplied object without registering it on each meld.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4752-4949
  - src/melder/aether/spellbook/spellbinder.py:641-660
  - src/melder/aether/spellbook/spellbinder.py:826-870
  - src/melder/nexus/nexus_frame_configuration.py:334-349
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1150-1198
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:155-234
  IMPACT: Treat direct and staged registration consistently. Verify where staged supplied objects
    enter cleanup tracking; preserving metadata alone does not prove a registered disposal entry.
    Existing explicit-name exclusion tests and public configuration prose must change with the feature.
  NEXT: Trace conjure/staged activation ownership and remaining persistence replay carriers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T21:51:00Z
  TYPE: FACT
  CLAIM: Source trace identifies a staged-existing-object tracking gap. Conjure registers only
    active _spells. bind_inactive does not register its supplied object, and _reactivate_owned_spell
    plus _apply_notch only update selection/metadata and validity. Direct existing-object executors
    return the value without registration. Preserving disposal names alone cannot establish its entry.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1188-1240
  - src/melder/aether/spellbook/spellbook.py:1507-1565
  - src/melder/aether/spellbook/spellbook.py:3681-3821
  - src/melder/aether/spellbook/spellbook.py:4752-4949
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:155-234
  IMPACT: This is source evidence, not an executed regression result. Include parked admission,
    promotion/re-promotion and cleanup tracking in the blast radius. Decide the ownership start
    point before widening this feature into staging lifecycle repair. Book-before-conjure cleanup
    and aliasing the same instance also require explicit proof boundaries, not global once-only claims.
  NEXT: Record the complete map with core edits, conditional lifecycle edits and the necessary regression matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T21:54:05Z
  TYPE: FACT
  CLAIM: Published the 238-line source-backed disposal blast-radius map. It identifies three core
    production files and a fourth creation-system file for the recommended staged-adoption extension;
    configuration reload/backfill, crystal carriers, adapter behavior, regression updates, public
    docs and regenerated assets are mapped. All 36 referenced file paths resolve except the one
    explicitly planned new integration file. Runtime tests were not run during this mapping pass.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/existing_object_disposal_blast_radius.md:1-238
  IMPACT: The accepted flag policy is ready to implement after the owner reviews the map. Staged
    custody is recommended when a root exists, independent of resolution. Do not claim new disposal
    behavior is present yet, or that this flag repairs the separate CommandOps class-configuration omission.
  NEXT: Owner reviews staged-value adoption; prepare patch contracts and red regressions before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:00:20Z
  TYPE: FACT
  CLAIM: Owner asks where owned/supplied objects are stored. The value is retained on
    Spell.user_created_object, and active/inactive book maps retain the Spell. Direct existing-value
    executors and the reuse-only door return that field. Active eager/late admission also places the
    same object reference in owner Creations; its optional disposal entry is separate metadata.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:412-415
  - src/melder/aether/spellbook/spellbook.py:1507-1565
  - src/melder/aether/spellbook/spellbook.py:4881-4930
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:155-234
  - src/melder/aether/conduit/meld/conduit_meld.py:541-546
  - src/melder/aether/conduit/meld/conduit_meld.py:724-735
  - src/melder/aether/conduit/creations/creations.py:266-300
  IMPACT: The staged gap is not loss of the supplied object. Cleanup walks a different registry
    from the Spell reference used by direct resolution. Existing-object live probes also inspect
    the Spell reference, so a successful live probe is not proof of disposal registration.
  NEXT: Explain the two storage roles before settling staged cleanup adoption.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:04:24Z
  TYPE: DECISION
  CLAIM: Owner requests a separate deferred lifecycle epic because disposal admission also affects
    transfer and related ownership concepts. Created the epic with accepted flag semantics, five
    story boundaries, unresolved custody questions and full source/doc/test catch-up pointers.
    Resume gap #3: existing-instance frame admission, starting with Protocol class/instance parity.
  EVIDENCE:
  - tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md
  - Owner instruction to make the epic and move onto the other flagged errors.
  IMPACT: The narrow disposal implementation estimate is superseded. No disposal or transfer changes
    are authorized in the next tranche. Distinguish Protocol validation from concrete frame grouping.
  NEXT: Reopen Protocol admission and existing experiments, then reproduce the class/instance mismatch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:08:00Z
  TYPE: FACT
  CLAIM: Current Bind source still restricts Protocol structural admission to ClassBindingProfile.
    ExistingCreationCompatibilityStrategy checks presence, unique existence, profile and zero
    constructor parameters, but not Protocol conformance. The old unit test explicitly admits a
    bare object under a foo Protocol-shaped frame, so green legacy tests preserve this hole.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:464-490
  - src/melder/aether/spellbook/bind/bind.py:865-913
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/existing_creation_compatibility_strategy.py:76-162
  - tests/unit/melder/spellbook/bind/test_bind.py:1091-1102
  - tests/experimentation/test_existing_instance_gap_experiment.py:295-302
  - tests/experimentation/test_existing_instance_gap_experiment.py:410-431
  IMPACT: This is distinct from concrete/string frame grouping and deferred disposal ownership.
    Reproduce through the current real runtime, then add minimal rejection/identity controls before
    choosing a Protocol-only source correction. Keep factory grouping and the current shallow check scope.
  NEXT: Run existing class/instance Protocol characterization without the historical scanner monkeypatch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:10:00Z
  TYPE: MEASURE
  CLAIM: Fresh stock characterization records four scenarios: incompatible Protocol class is
    rejected at bind; compatible class binds; mismatched concrete-frame instance is injected;
    mismatched Protocol instance also injects and then raises AttributeError on its missing read.
    Four observation tests passed, two historical monkeypatch cases were deselected.
  EVIDENCE:
  - artifacts/existing_instance_planning_20260913/frame_admission_characterization.log:1-8
  - artifacts/existing_instance_planning_20260913/frame_admission_characterization.xml
  IMPACT: Passing observation tests do not mean Protocol admission is correct. Preserve concrete
    frame grouping as a separate policy; encode native expected-rejection and valid identity controls.
    Pytest reported a cache-directory creation warning; disable its optional cache for the next run.
  NEXT: Add focused Protocol admission regressions for existing values and preserve class/factory/grouping controls.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:12:00Z
  TYPE: MEASURE
  CLAIM: Added 18 native Protocol admission regressions/controls. Four existing-instance cases
    fail because bind does not raise for missing/non-callable read, before and after conjure.
    Four equivalent invalid-class cases pass, alongside valid/inherited instance injection,
    concrete/string frame grouping and callable-factory controls (14 passing controls total).
  EVIDENCE:
  - tests/component/melder/spellbook/test_existing_instance_protocol_admission.py:1-132
  - artifacts/existing_instance_planning_20260913/protocol_admission_red.log
  - artifacts/existing_instance_planning_20260913/protocol_admission_red.xml
  IMPACT: Narrow proposal: run the same existing Protocol member check on a supplied instance
    at bind, without nominal checks on ordinary frames or a factory-result policy. Existing
    tests that explicitly expect incompatible-instance acceptance must be updated with that fix.
    No production source changes have been made in this resumed frame-validation tranche.
  NEXT: Check new test lint and refresh its corpus, then report the bounded repair proposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:15:07Z
  TYPE: FACT
  CLAIM: Deferred lifecycle epic is complete as a planning record, with five story boundaries and
    all 29 referenced source/test paths verified. Protocol admission reproduction is ready for
    review: 18 native cases, four expected failures and fourteen controls; F/I lint passes.
    Rebuilt the tests corpus (823 files) and its fingerprint/output check passes.
  EVIDENCE:
  - tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md:1-250
  - tests/component/melder/spellbook/test_existing_instance_protocol_admission.py:1-132
  - artifacts/existing_instance_planning_20260913/protocol_admission_red.xml
  - artifacts/existing_instance_planning_20260913/protocol_test_bundle_build.log:1-2
  - artifacts/existing_instance_planning_20260913/protocol_test_bundle_check.log:1-1
  IMPACT: Runtime disposal and Protocol source changes remain unapplied. The precise next correction
    is extending the existing bind-time Protocol check to supplied instances, preserving class,
    callable and non-Protocol frame policy and the current shallow member-validation contract.
  NEXT: Review the Protocol-only correction, then apply it with legacy expectation updates and focused checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:22:06Z
  TYPE: DECISION
  CLAIM: Owner asks to update the deferred epic with Protocol validation as part of existing-object
    management. Added the separate construction, contract-validation and lifecycle-ownership rules,
    a Protocol story, source/test catch-up links, regression results and acceptance criteria.
  EVIDENCE:
  - tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md
  - Owner's ticket-update instruction after agreeing that these are parts of the same existing-object model.
  IMPACT: This task retains the native evidence; future Protocol implementation is coordinated through
    the deferred epic instead of being treated as an unrelated local exception. No source/test edits or new test runs.
  NEXT: Resume existing-object implementation only under the epic's agreed registration and ownership contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T23:33:43Z
  TYPE: DECISION
  CLAIM: Owner asks to test the specific supported flow: a user-created object A is bound, then
    object B relies on it. Use the existing native direct-dependency regression and assert exact
    supplied identity. Treat reference-only blueprint/lifetime/compiler ideas as discussion only.
  EVIDENCE:
  - Owner's explicit test request and no-discovery boundary for the other concepts.
  - tests/integration/melder/spellbook/test_existing_instance_planning.py:23-37
  - tests/integration/melder/spellbook/test_existing_instance_planning.py:127-136
  IMPACT: This verifies injection into a B that Melder constructs, not retroactive filling of
    constructor parameters on an already-created B. Do not resume Protocol/disposal/compiler design.
  NEXT: Run the single existing-instance dependency regression against the current checkout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T23:35:50Z
  TYPE: MEASURE
  CLAIM: The requested direct dependency test passes on the current checkout: one passed in
    0.38 seconds. ExistingValue is instantiated externally, bound unique with its type as spellframe,
    and supplied to ValueConsumer's required constructor dependency. The assertion uses is identity.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_existing_instance_planning.py:127-136
  - artifacts/existing_instance_planning_20260913/direct_owned_dependency_confirmation.log:1-2
  - artifacts/existing_instance_planning_20260913/direct_owned_dependency_confirmation.xml
  IMPACT: Registered user-created A can be injected into a B that Melder constructs. No test/source
    edits, additional design discovery, runtime changes or build regeneration were needed for this check.
  NEXT: Report the exact successful scenario; retain broader reference/blueprint concepts as unselected ideas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Annotation work is accepted and turned in under the completed annotation task. The latest
owner-requested direct A-to-B dependency check passes with exact supplied identity.
No discovery was performed on the accompanying compiler/reference/lifetime ideas.
The earlier existing-instance planning repair is implemented: both Phase-8/9 scanners treat supplied values
as leaves, preserving consumer dependency edges and exact object identity. All 21 instance regressions
pass within 140 selected native checks; five legacy failure expectations now test successful injection.
Generated graph/source/test assets are current. Read instance_repair_result.md first. The original
CommandOps/Iris test reaches successful construction but fails builder.cleaned after root.cleanup.
The subsequent source trace identifies omitted disposal configuration for the builder's class;
the original test has not been changed. The task remains open for review/downstream acceptance.
Owner now parks disposal in tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md.
It preserves the accepted flag but supersedes the narrow implementation estimate with a full ownership,
transfer/rollback and persistence program. No disposal implementation or new wheel exists.
Current work: Protocol/frame admission for existing instances. Eighteen native cases are written and
executed: four expected missing/non-callable-member rejection failures, fourteen passing controls.
Current stock injection reaches a missing Protocol method and fails at consumer use. Proposal is to
extend the same bind-time Protocol check to instances; no source fix yet. Test lint and corpus checks pass.
Owner now includes that validation issue in the deferred epic alongside construction and lifecycle ownership.
Provider-artifact ownership remains parked separately. The original builder test still lacks class disposal names.
