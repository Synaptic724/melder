

# Task: Compile unprovided constructor dependencies as missing-dependency sockets instead of refusing conjure

## Metadata
- Task ID: TASK-2026-09-26-implement-missing-dependency-sockets
- Epic: EPIC-2026-09-24-override-execution-performance
- Story: STORY-2026-09-26-unresolved-input-sockets (step S1 of artifacts/melder_override_design_20260926/design.md)
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-26T00:44:21Z
- Updated: 2026-09-26T08:16:36Z

## Objective
A typed constructor parameter with no registered provider no longer fails conjure. It compiles as a
caller-supplied input; a meld that supplies it by override uses the supplied object; a meld that does not
raises a named MeldExecutionError that identifies the missing dependency and how to supply it.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("go ahead lets start looking into this") after agreeing the
  contract: no early rejection, named error at meld when not supplied. Cause trace in review.
- EXECUTION_BOUNDARY: Investigation now: read src/, tests/. Implementation only after patch docs exist and
  the owner confirms the file/symbol list. Writes now: this ticket, its patch lane and artifacts.
- DEPENDENCIES: tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md;
  completed 2026-09-19 caller-supplied socket contract (OVERRIDE_REQUIRED).
- EXIT_GATE: Behavior implemented with regression tests on 3.14t and GIL, docs promoted, owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for multiple-candidate policy, late-provider recompile policy and
  error wording; BLOCKER if a consumer assumes OVERRIDE_REQUIRED always carries references.

## Scope Boundaries
- In scope: Phase-3 single-annotation resolution and socket classification, Phase-4/6 validation of the new
  socket, Phase-5/9 consumers of OVERRIDE_REQUIRED, the meld-time missing-input error on every executor
  family and the no-override lane, Nexus publication of reference-less sockets.
- Out of scope: the override build-order rewrite (S2-S5), multi-candidate ambiguity (stays an error),
  the internal-registration guard, a per-binding declaration keyword.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved starting the investigation, 2026-09-26T00:44:21Z.

## Steps / Checklist
- [x] Trace Phase 3: where the zero-candidate raise sits and how socket kinds are assigned.
- [x] Trace every OVERRIDE_REQUIRED consumer for assumptions about non-empty references.
- [x] Trace how a missing required input fails today in each executor family and the no-override lane.
- [x] Late-provider behavior: existing OVERRIDE_REQUIRED frame-key watcher recompiles the consumer.
- [x] Write patch docs and the file/symbol list; owner confirmation before any src/ edit.
- [ ] Implement, test, promote docs. (in progress since 2026-09-26T07:12:37Z)
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Patch lane system_docs/patches/active/unresolved_input_sockets_2026_09_26/ (written 2026-09-26).
- Source and tests (after confirmation).

## Files / Paths Impacted
- Listed per component in system_docs/patches/active/unresolved_input_sockets_2026_09_26/.

## Validation
- 2026-09-26T08:09:30Z full unit/component/integration/experimentation from the VM copy: 3.14.7t 12281 passed,
  21 failed; 3.14 GIL 12280 passed, 22 failed. All failures are the pre-existing baseline plus the known
  concurrency flake (see the 08:09:30Z MEASURE note). New component files: 70 passed on both builds.
- Coverage: not measured.

## Risks / Rollback Notes
- Conjure-time detection of a forgotten binding moves to meld time; mitigate with a conjure warning.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No src/ edit before patch docs and owner confirmation.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/missing_dependency_sockets_20260926/
  - system_docs/patches/active/unresolved_input_sockets_2026_09_26/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner decision at task closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Missing-dependency sockets; meld-time missing-input error.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T00:44:21Z
  TYPE: PLAN
  CLAIM: Reuse the existing caller-supplied socket (OVERRIDE_REQUIRED) for a parameter with zero candidates
    instead of raising, so Phase 5/9 and the executors already treat it as a supplied input. Verify every
    consumer tolerates empty references, then add a named missing-input error where today a Python
    missing-argument error (or a descriptor default) surfaces.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:486-497
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:733-747
  IMPACT: Keeps the change inside an existing category; no new socket kind unless a consumer forces one.
  NEXT: Read the Phase-3 loop that calls _resolve_single_by_annotation and builds socket targets/references.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T00:46:10Z
  TYPE: FACT
  CLAIM: Phase 3 raises only in _resolve_single_by_annotation; the loop already skips empty results, collections
    may be empty, and _build_local_topology marks OVERRIDE_REQUIRED only when references exist. Consumers of
    OVERRIDE_REQUIRED: injection keeps it as an "override_required" source (no edge); the frame-key watcher
    already watches OVERRIDE_REQUIRED sockets with a dependency_key, so a provider bound later invalidates and
    recompiles the consumer; cycle validation excludes it; Nexus publishes one relation per reference (none if
    empty). One consumer rejects empty references: SpellInjectionInstanceSpec._build_required_override_params.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-513
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:693-768
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:770-926
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:216-278
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:125-150
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1362-1390
  - src/melder/nexus/frame_descriptor_manager.py:600-617
  IMPACT: Reusing OVERRIDE_REQUIRED needs two compiler edits (Phase 3 marking, the reference check); late
    provider binding already works through the existing watcher. Serialization sites still to read.
  NEXT: Record today's missing-input failure per family (probe), then read the constructor-call error paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T00:46:10Z
  TYPE: MEASURE
  CLAIM: With today's resolvable=False route (3.14.7t, many consumers): supplied root and nested inputs work by
    exact path and by broadcast; a missing root input on a dependency-free root raises a raw TypeError
    ("missing 1 required positional argument: 'work'"); on a root with dependencies, or nested, it raises
    MeldExecutionError "Error invoking spell 'X'" chained from that TypeError. Nothing names the missing
    dependency or how to supply it.
  EVIDENCE:
  - artifacts/missing_dependency_sockets_20260926/probe_required_today.py:1-75
  - artifacts/missing_dependency_sockets_20260926/probe_required_today_314t.json
  IMPACT: Execution already honors supplied inputs; S1 needs the named error on the failure path only.
  NEXT: Read each family's constructor-call exception path to place a failure-path-only missing-input check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:48:04Z
  TYPE: PLAN
  CLAIM: Proposed change set for owner confirmation. (1) Phase 3: zero candidates for SINGLE_BY_ANNOTATION
    returns empty and the socket becomes OVERRIDE_REQUIRED with no references (ambiguity still raises).
    (2) Injection: accept reference-less required inputs. (3) Required-holes warning names a missing provider.
    (4) One failure-path helper raises MeldExecutionError naming the missing parameters, its type and the
    override key; every family's existing constructor except-branch calls it (generalized, many_only, manifest
    no-override/override); solo no-override emits it at compile time; solo override adds try/except TypeError
    only for spells with required inputs. Success paths gain no work. (5) Cache generation 11. (6) Update the
    7 existing "no DI candidate" assertions and add regressions per family, nested, reuse and late provider.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1650-1735
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:603-617
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:40-190
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py:110-135
  IMPACT: Small compiler change plus one error helper wired into existing except-branches.
  NEXT: Owner confirms; then write patch docs under system_docs/patches/active/missing_dependency_sockets_2026_09_26/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:52:30Z
  TYPE: TRADEOFF
  CLAIM: Maintainer assessment for the owner. The model (a constructor parameter is either a graph edge or an
    open input the call supplies) is durable and is the same concept the S2-S5 shape plan uses for cuts and
    operands. Two parts of the proposed change set are not durable as written: encoding "no provider" as
    OVERRIDE_REQUIRED with an empty reference tuple (meaning inferred from emptiness), and naming the error from
    ~20 per-family except-branches that S4 replaces. Refinement: an explicit input-origin field on the socket
    (registered non-resolvable definition vs no registered provider) and the error decided by plan data, with
    the except-branch helper recorded as interim until S4.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:733-747
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:125-150
  - artifacts/melder_override_design_20260926/design.md:120-133
  IMPACT: Keeps S1 small without leaving an implicit encoding behind.
  NEXT: Owner decides whether S1 ships with the interim error wiring or waits for plan-level errors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:57:47Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner direction: resolvable=False (discoverable, never-constructed bindings) is a separate feature and
    must not be reused. The missing-provider case needs its own mechanism. Plan revised: a distinct open-input
    socket kind produced when a single typed parameter has zero providers; OVERRIDE_REQUIRED and the
    resolvable=False path stay unchanged. The owner asked for the full rationale before approving.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/dag/socket_kind.py:17-37
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:733-747
  IMPACT: Supersedes items (1)-(3) of the earlier PLAN note; the named-error and cache items stand.
  NEXT: Owner decides after the rationale; then patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T01:02:31Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner converges on a new socket kind assigned by default, during resolution, to any typed parameter
    that cannot be resolved outside the existing cases, so meld errors can be specific. This matches the
    open-input/requirement model: one assignment point in Phase 3, explicit data on the socket (expected type,
    name, position, kind), every consumer dispatching on the kind. Existing kinds and resolvable=False untouched.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:850-880
  - src/melder/aether/spellbook/spell_compiler/dag/socket_kind.py:17-37
  IMPACT: Design settled at concept level; naming and Nexus visibility remain open.
  NEXT: Write patch docs for owner review before any src/ edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T01:04:10Z
  TYPE: PLAN
  CLAIM: Revised change set for owner approval. New SocketKind.UNRESOLVED_INPUT assigned in Phase 3 when a
    SINGLE_BY_ANNOTATION parameter of a resolvable spell has zero providers; the socket keeps its normalized
    dependency_key (expected type). Consumers: frame-key watcher (re-resolve when a provider appears), injection
    ("unresolved_input" source, no edge) with its own value rows on plan steps, row serialization, conjure report
    in the required-holes strategy, and a failure-path helper raising UnresolvedInputError (MeldExecutionError
    subclass) from every family's constructor except-branch (interim until the build-plan rewrite). Cache
    generation 11. OVERRIDE_REQUIRED, resolvable=False, collections, SpellMap, SpellContract and ambiguity unchanged.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/dag/socket_kind.py:1-40
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:649-692
  - src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py:80-100
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1362-1390
  - src/melder/aether/spellbook/spell_compiler/system/validation/topology_dependency_mismatch_strategy.py:79-100
  IMPACT: Supersedes the earlier PLAN; UNRESOLVED_INPUT is excluded from NORMAL-only validators by construction.
  NEXT: Owner approves the plan, the name and the exception subclass; then patch docs, then implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T01:11:08Z
  TYPE: FACT
  CLAIM: Tranche A (validation). Phase-4/6 strategies that read socket kinds compare by identity against one kind,
    so UNRESOLVED_INPUT is excluded from NORMAL-only (topology/dependency mismatch), SPELL_CONTRACT-only (contract
    cycle) and dependency-id checks (dangling) by construction; socket_ref_sanity is kind-agnostic structure.
    Changes needed: required_holes gains an UNRESOLVED_INPUT warning (it already warns for PLAIN holes and
    OVERRIDE_REQUIRED); binding_resolution_cycle should skip UNRESOLVED_INPUT like OVERRIDE_REQUIRED (its key has
    no provider node, so this is hygiene, not correctness). Phase-4 warnings are stored on validation results
    and profiles but never logged at conjure, so "conjure reports" needs an explicit log line.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py:64-135
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:200-240
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/dangling_dependency_strategy.py:70-125
  - src/melder/aether/spellbook/spell_compiler/system/validation/topology_dependency_mismatch_strategy.py:79-100
  - src/melder/aether/spellbook/spell_compiler/system/validation/socket_ref_sanity_strategy.py:56-110
  - src/melder/aether/spellbook/spell_compiler/validation/spell_validation_result.py:100-145
  IMPACT: Two small validation edits; one new conjure log line (level is a decision: INFO proposed).
  NEXT: Tranche B: trace the frame-key watcher from a later bind to consumer re-resolution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T01:11:40Z
  TYPE: FACT
  CLAIM: Tranche B (late provider). Bind commits and contract additions call mark_collection_dependents_dirty
    with the new spell's frame key; that marks every consumer registered under the key in the spellbook-scoped
    index as dependency-changed and dirty, so its next meld re-runs structural phases. Consumers register only
    through _extract_collection_frame_keys, which today admits OVERRIDE_REQUIRED and NORMAL collections; adding
    UNRESOLVED_INPUT there (keyed by the socket's dependency_key frame) closes the input on a later bind. Phase 3
    matches providers by identity (spell or spellframe is the annotation, or by name), not by subclass, which
    is the same relation the frame key expresses, so the watcher and the resolver agree.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1108-1175
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1290-1310
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:840-870
  - src/melder/aether/spellbook/spellbook.py:3050-3080
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:177-252
  IMPACT: One-line watcher change; late-provider behavior must be proven by a dynamic-world regression.
  NEXT: Tranche C: serialized rows (Phase 8 graph rows, Phase 9 injection rows) and planner use of required rows.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T01:12:12Z
  TYPE: FACT
  CLAIM: Tranche C (rows and plans). Phase-8 graph-shape rows carry socket_kind.value per socket, so a socket moving
    between UNRESOLVED_INPUT and NORMAL changes the occurrence signature and forces a rebuild; appending the enum
    member keeps existing values stable. Planners treat any param source with an override_key as an override
    target and never inspect OVERRIDE_REQUIRED specially, so an "unresolved_input" source (override_key = name,
    no dependency keys) executes exactly like today's required input: omitted unless supplied. Injection row and
    signature exporters branch on kind "override_required" to append position/kind/references; the new kind needs
    its own branch (position, kind). required_override_params stays OVERRIDE_REQUIRED-only.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:374-430
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2713-2771
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:860-945
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1225-1262
  IMPACT: No planner or emitter change is needed for execution; only the injection source kind and two exporters.
  NEXT: Tranche D: exception conventions and every constructor-failure site per executor family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T01:13:28Z
  TYPE: FACT
  CLAIM: Tranche D (failure sites). Constructor failures are wrapped in exactly these places: generalized and
    many_only no-override helpers _raise_meld_construction_error and _construct_spell_instance plus one emitted
    except block each; generalized and many_only override emitters (three emitted except blocks each) and their
    _construct_spell_instance_with_overrides; the manifest no-override emitter reuses the helper; the manifest
    override runtime's excepts wrap targeting, not construction. Solo lanes call the target with no try, so
    exceptions propagate raw. MeldExecutionError already has node_id/param_name slots, so UnresolvedInputError
    can subclass it with an expected-type field. A missing required argument can only raise at call binding, so
    "an unresolved socket is absent from the supplied names" is a sufficient, parse-free trigger.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:603-617
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1252-1320
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1650-1735
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:689-703
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:628-643
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py:228-245
  - src/melder/utilities/custom_exceptions/meld_execution_error.py:1-185
  IMPACT: About 16 edit points in 8 generator files, all on failure paths; success paths unchanged.
  NEXT: Tranche E: existing tests that encode the old conjure refusal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T01:13:28Z
  TYPE: CONFLICT
  CLAIM: Six existing tests encode the old contract as intent, e.g. test_required_dependency_without_provider_still_refuses
    and test_typechecking_dependency_without_provider_still_fails_validation (conjure must raise "no DI candidate"),
    plus two forward-ref/resolution-contract integration tests, one Phase-3 unit test and one experiment classifier.
    The owner's 2026-09-26 decision supersedes that contract; the tests are rewritten to the new contract (conjure
    succeeds, the socket is UNRESOLVED_INPUT, meld raises UnresolvedInputError), not deleted.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py:365-375
  - tests/integration/melder/spellbook/test_deferred_annotations.py:100-112
  - tests/integration/melder/spellbook/test_spellbook_integration_future_annotations.py:1240-1292
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:548-572
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py:490-520
  - tests/experimentation/test_existing_instance_injection_experiment.py:100-112
  IMPACT: Deliberate contract reversal must be visible in the patch docs and release note.
  NEXT: Write the patch docs from tranches A-E.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T01:16:08Z
  TYPE: FACT
  CLAIM: Tranche F (remaining unknowns). The normalized frame key is the lowercased type __name__, so messages
    take the display name from the Phase-1 annotation and keep the frame key for watching only. The hydrated
    manifest override runtime constructs through the generalized _invoke_spell_with_kwargs (re-exported by
    generalized_runtime_library), so wiring that function covers the cached lane. The conjure report fits right
    after run_structural_phases in SpellbookCreationSystem._prepare_spellbook_for_conjure. The new exception
    class enters the internal-registration manifest, so build assets need the separate owner-approved rebuild.
  EVIDENCE:
  - src/melder/utilities/helpers/general_helpers.py:372-420
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:3031-3095
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py:26-45
  - src/melder/aether/spellbook/spellbook_creation_system.py:290-316
  IMPACT: No open technical unknown blocks implementation; policy points are recorded in the patch docs.
  NEXT: Owner reviews the patch docs; on approval, implement in the rollout order they define.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T01:16:08Z
  TYPE: DECISION
  CLAIM: Patch docs written: architecture_patch (scope, invariants, rollout, rollback, coverage matrix),
    component_patch_spell_compiler (Phases 3/4/9, watcher, exporters), component_patch_meld_runtime (exception,
    failure-path helper and every wiring site, solo handling, cache generation 11, marked interim) and
    code_description_patch_unresolved_inputs (control flow, edge semantics, non-goals).
  EVIDENCE:
  - system_docs/patches/active/unresolved_input_sockets_2026_09_26/architecture_patch.md:1-80
  - system_docs/patches/active/unresolved_input_sockets_2026_09_26/component_patch_spell_compiler.md:1-58
  - system_docs/patches/active/unresolved_input_sockets_2026_09_26/component_patch_meld_runtime.md:1-57
  - system_docs/patches/active/unresolved_input_sockets_2026_09_26/code_description_patch_unresolved_inputs.md:1-43
  IMPACT: Patch-framework entry gate is satisfied once the owner approves; implementation maps to the coverage matrix.
  NEXT: Owner approval, then implementation step 1 (SocketKind, Phase 3, injection, exporters, watcher, validation).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:12:37Z
  TYPE: DECISION
  CLAIM: Owner approved the patch docs ("yeah sure continue"). Implementation proceeds in the patch rollout order:
    step 1 compiler (SocketKind, Phase 3, watcher, injection, exporters, validation), step 2 exception and
    failure-path wiring, step 3 conjure report and cache generation 11, step 4 tests, step 5 docs.
  EVIDENCE: system_docs/patches/active/unresolved_input_sockets_2026_09_26/architecture_patch.md:52-62
  IMPACT: src/ and tests/ edits are now in scope for the files the patch docs list.
  NEXT: Step 1 edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T07:20:30Z
  TYPE: FACT
  CLAIM: Step 1 compiler core applied. SocketKind gains UNRESOLVED_INPUT (appended; existing values unchanged).
    Phase 3: _resolve_single_by_annotation returns an empty mapping on zero candidates (two-candidate
    RuntimeError unchanged); _build_local_frame_dag records (param_name, position) of an empty
    SINGLE_BY_ANNOTATION result in socket_unresolved; _build_local_topology marks those UNRESOLVED_INPUT after
    the OVERRIDE_REQUIRED rule and computes dependency_key for them. Empty COLLECTION/SPELLMAP/PLAIN/contract
    results are not recorded. Diff reviewed against HEAD (45+/13-, two files). PROCESS BREACH: the Phase-3 edit
    was applied right after context compaction, before REONBOARD and before this note; disclosed to the owner in
    the REONBOARD attestation. Not yet run: nothing imports or tests the change yet.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/dag/socket_kind.py:5-47
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-516
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:696-781
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:783-948
  IMPACT: Conjure no longer refuses a provider-less typed parameter; downstream consumers (watcher, injection,
    exporters, validation) must accept the new kind before any meld path is exercised.
  NEXT: Watcher (_extract_collection_frame_keys) admits UNRESOLVED_INPUT.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:20:30Z
  TYPE: PLAN
  CLAIM: Patch-consumption mapping (patch section -> implementation step -> validation step).
    (a) spell_compiler After: Phase 3 + SocketKind -> step 1 (done above) -> unit test_compiler_phase_3:
        zero -> UNRESOLVED_INPUT with dependency_key, one -> NORMAL, two -> RuntimeError, non-resolvable
        definition -> OVERRIDE_REQUIRED, non-resolvable root unchanged.
    (b) spell_compiler After: watcher -> step 1 spell_system_states._extract_collection_frame_keys ->
        component: dynamic world, bind provider after conjure, next meld injects it.
    (c) spell_compiler After: injection + exporters -> step 1 injection processor, analysis docstring, both
        shared_compiler_executions exporters -> unit row assertions; component: cached (hydrated) executors.
    (d) spell_compiler After: required_holes + cycle skip -> step 1 validation strategies -> unit warning/skip.
    (e) meld_runtime After: UnresolvedInputError + helper + every family, solo conditional -> step 2 ->
        component per family: supplied root/path/broadcast, missing root/nested, reused, unrelated TypeError.
    (f) architecture rollout 3: conjure INFO report + cache generation 11 -> step 3 -> integration cache
        generation history test.
    (g) architecture rollout 4-5: six old-contract tests rewritten; docs promoted -> steps 4-5 -> full
        unit/component/integration on 3.14t and GIL from the VM copy.
  EVIDENCE:
  - system_docs/patches/active/unresolved_input_sockets_2026_09_26/architecture_patch.md:54-75
  - system_docs/patches/active/unresolved_input_sockets_2026_09_26/component_patch_spell_compiler.md:24-58
  - system_docs/patches/active/unresolved_input_sockets_2026_09_26/component_patch_meld_runtime.md:24-57
  IMPACT: Satisfies the patch-consumption mapping gate before the remaining edits.
  NEXT: Watcher edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:20:30Z
  TYPE: DECISION_REQUEST
  CLAIM: Policy conflict for step 2. The approved patch exports UnresolvedInputError from the package root, but the
    synaptic_python_developer overlay rule 5.2 forbids adding __init__.py export wiring or __all__ entries. The
    package root already carries a curated public surface (owner-ruled composition, 2026-07-19) that includes
    the existing custom exceptions. Owner decides: export at the root like its siblings, or import from its
    concrete module only.
  EVIDENCE:
  - agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD:65-71
  - system_docs/patches/active/unresolved_input_sockets_2026_09_26/component_patch_meld_runtime.md:25-26
  IMPACT: Blocks only the export line in step 2; step 1 proceeds.
  NEXT: Ask the owner when step 1 completes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T07:20:30Z
  TYPE: FACT
  CLAIM: Mailbox M1-6 consumed: melder_1 works a separate long-run growth lane, read-only on src, adding tests only
    under benchmarks/testing_other_di; creations.py is on its read path. No overlap with this task's patch file
    list, so no coordination is needed for step 1-3 edits.
  EVIDENCE: tickets/tasks/2026-09-26_investigate_melder_long_run_growth_task.md
  IMPACT: None on scope; avoid touching creations.py in this lane.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T07:24:00Z
  TYPE: FACT
  CLAIM: Step 1 consumers applied. Watcher admits UNRESOLVED_INPUT under its dependency_key frame. Injection adds an
    "unresolved_input" source per UNRESOLVED_INPUT socket (no dependency keys, override_key = name, position/kind)
    before the OVERRIDE_REQUIRED branch; required_override_params stays OVERRIDE_REQUIRED-only (only carried by
    planners, no emitter reads it). Both row exporters append (position, kind) for the new kind; both are called
    only by tests today. Consumer tolerance re-read: Phase-5 socket overlay emits a SocketRef for every socket, so
    root/path/broadcast targeting addresses the new socket; the occurrence analyzer skips target-less non-collection
    sockets; Nexus publishes only target/reference IDs (none here); no emitter compares against a specific SocketKind
    member (kind values are carried as ints).
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1362-1398
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:119-302
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:10-160
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:861-958
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1213-1282
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:455-495
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:905-932
  - src/melder/nexus/frame_descriptor_manager.py:586-620
  IMPACT: The compiler now carries the socket end to end; execution omits it unless supplied (unchanged planners).
  NEXT: Validation tranche: required_holes UNRESOLVED_INPUT warning and binding_resolution_cycle skip.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:24:00Z
  TYPE: DECISION
  CLAIM: One expected-type display rule shared by the Phase-4 warning and the meld error: a static
    UnresolvedInputError.expected_type_name(annotation) that unwraps Optional/Union-with-None and ForwardRef the
    same way Phase 3 matches, then uses the class __qualname__ (repr for other annotation objects). It reads the
    Phase-1 annotation (Spell.requirements), never the lowercased frame key. The exception module is created now
    (approved file); its failure-path factory follows in step 2. No new field on the topology descriptor.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:139-175
  - src/melder/aether/spellbook/spell.py:1123-1150
  - src/melder/utilities/custom_exceptions/meld_execution_error.py:1-185
  IMPACT: Warning and error name the type identically; no scope beyond the patch file list.
  NEXT: Create unresolved_input_error.py with the class and helper; edit required_holes and the cycle strategy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T07:27:00Z
  TYPE: FACT
  CLAIM: Step 1 validation applied and the exception module created. UnresolvedInputError(MeldExecutionError) adds
    expected_type and unresolved_params slots plus the static expected_type_name rule; not yet exported (pending the
    owner's __init__.py decision) and not yet raised anywhere (step 2). required_holes emits one UNRESOLVED_INPUT
    warning per socket (message names parameter, spell, expected type, root and '>param' keys, and the error;
    details carry position, kind, expected_type, dependency_key) and fails fast if a socket has no Phase-1
    parameter. binding_resolution_cycle excludes UNRESOLVED_INPUT sockets like OVERRIDE_REQUIRED. All eight touched
    src files parse; nothing executed yet. Existing sibling exceptions say "one of the 11" types; that count goes
    stale and is left for the step-5 doc pass.
  EVIDENCE:
  - src/melder/utilities/custom_exceptions/unresolved_input_error.py:1-159
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py:71-199
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:177-248
  IMPACT: Step 1 code is complete; the conjure-time warning is stored (the INFO log line is step 3).
  NEXT: Validate step 1 on the VM copy: Phase-3 unit tests plus a conjure probe for the socket, source and warning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:30:00Z
  TYPE: MEASURE
  CLAIM: Step 1 validated on 3.14.7t (VM copy synced from the mount; fresh world per case). No Pkg registration:
    conjure succeeds for many and unique_per_conduit consumers; the socket is UNRESOLVED_INPUT with
    dependency_key ('pkg', '__default__'), position 0, no targets. Supplied root, path ('task>work'), broadcast
    ('**work') and None-by-presence all construct with the supplied object. Missing root raises the raw TypeError;
    missing nested raises MeldExecutionError chained from it (step 2 names both). Dynamic world: missing before,
    then binding Pkg after conjure makes the next meld inject a Pkg and the socket becomes NORMAL. Phase-3 unit plus
    the two override_required component files: 111 passed, 2 failed, both test_resolve_single_by_annotation_no_candidates
    parametrizations, which assert the retired "no DI candidate" contract (on the rewrite list).
  EVIDENCE:
  - artifacts/missing_dependency_sockets_20260926/probe_step1_unresolved.py:1-90
  - artifacts/missing_dependency_sockets_20260926/probe_step1_unresolved_314t.json
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py:490-520
  IMPACT: Step 1 behaves as the patch specifies; late-provider re-resolution is confirmed, not assumed.
  NEXT: Step 2 failure-path wiring (read every constructor-failure site first).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T07:30:00Z
  TYPE: FACT
  CLAIM: Phase 1-4 artifacts (Spell.requirements, validation_result_phase4) are released after resolution by
    cleanup_phase_artifacts_after_resolution, so they are None at meld time (probe: phase4_after_conjure is None).
    Consequences: (1) the step-3 conjure INFO line must be emitted before that cleanup, where the patch already
    places it; (2) the meld-time error cannot read Spell.requirements. Correction to the 07:24:00Z DECISION: the
    error re-reads the consumer's constructor signature with annotationlib FORWARDREF format on the failure path
    (unresolvable TYPE_CHECKING names render as their written name) and applies the same expected_type_name rule;
    the Phase-4 warning keeps using Phase-1 requirements. The durable topology still supplies which sockets are
    unresolved. Alternative (not taken, needs scope approval): store the display name on SpellSocketDescriptor.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:2390-2427
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:255-302
  - src/melder/aether/spellbook/spell.py:1123-1150
  IMPACT: Keeps step 2 inside the approved files; the display rule stays single-sourced.
  NEXT: Read the generalized/many_only no-override helpers and emitted except blocks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:33:00Z
  TYPE: PLAN
  CLAIM: Step-2 wiring, one decision per site, from re-reading every constructor-failure site. The trigger is exact:
    a TypeError from the call plus an UNRESOLVED_INPUT socket absent from the names/positions actually passed.
    (1) gen + many_only no-override _raise_meld_construction_error gain optional supplied_names/positional_count
    and consult UnresolvedInputError.from_failed_construction first; inlined emitted calls keep (spell, exc)
    because inlinable steps pass only dependency kwargs (no payload, no positional), which never include an
    unresolved param. (2) Both _construct_spell_instance helpers pass call_kwargs and len(args). (3) Both transient
    unrolled emitters replace their 8-line raise with the helper, passing the CALLn positional count, because
    transient calls bind dependencies positionally. (4) Manifest no-override emitter passes contract-payload names
    and the positional payload length when present. (5) gen + many_only override emitters (three blocks each) call
    the family helper with kwargs/call_kwargs and args; both _invoke_spell_with_kwargs do the same (covers the
    hydrated manifest override runtime). (6) Solo: when the spell's topology has an UNRESOLVED_INPUT socket, bind a
    guarded call_target (try/except TypeError) in the namespace; emitted source is unchanged, so the code-object
    cache is unaffected and spells without unresolved inputs keep the raw call. Positional safety checked: the
    transient CALLn eligibility excludes a step whose unresolved param precedes a dependency (unresolved sources
    are absent from dependency_keys_by_param, so positional_ok turns False and the kwargs CALLN path is used).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:603-686
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1252-1320
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1690-1720
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1860-1930
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:555-643
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1602-1730
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:3031-3091
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:1640-1712
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:1-323
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2110-2160
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2712-2775
  IMPACT: Every family names the missing input; success paths and emitted source for ordinary spells are unchanged
    except the transient/override except blocks, which now call one helper (cache generation 11 retires old code).
  NEXT: Add from_failed_construction to UnresolvedInputError, then wire the sites in this order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:37:00Z
  TYPE: FACT
  CLAIM: Step 2 wired except the root export. UnresolvedInputError.from_failed_construction (TypeError + unsupplied
    UNRESOLVED_INPUT socket by name or position) and a meld-time expected type (constructor signature read with
    FORWARDREF; frame key only if unreadable). gen + many_only _raise_meld_construction_error consult it first;
    both _construct_spell_instance, both transient emitters (CALLn positional count), manifest no-override
    (payload names, positional length), both override emitters (three blocks each) and both
    _invoke_spell_with_kwargs route through it. One site the patch did not list: the hydrated generalized
    override shape runtime executes the emitted override blocks with its own static namespace, so it needed the
    helper entry (found by a NameError in the probe; same component, one import plus one namespace line). Solo:
    _call_target_for binds a guarded call_target only for spells with UNRESOLVED_INPUT sockets.
  EVIDENCE:
  - src/melder/utilities/custom_exceptions/unresolved_input_error.py:169-291
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:604-650
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:690-736
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py:23-75
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:246-300
  IMPACT: 16 src files changed so far (+367/-137 ignoring EOL); success paths unchanged; emitted override and transient
    except blocks are shorter.
  NEXT: Run unit and component suites on 3.14t from the VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T07:37:00Z
  TYPE: MEASURE
  CLAIM: Probe (3.14.7t, fresh world per case, no cache): many and unique_per_conduit consumers raise
    UnresolvedInputError (expected_type 'Pkg', unresolved_params ['work'], chained from the binding TypeError) for
    missing root, missing nested and nested-with-other-override; supplied root/path/broadcast/None/__args__ work;
    a constructor body raising its own TypeError keeps the raw TypeError at a solo root and the generic
    MeldExecutionError when nested; dynamic world: UnresolvedInputError before, injected provider after a late bind.
  EVIDENCE:
  - artifacts/missing_dependency_sockets_20260926/probe_step1_unresolved.py:1-112
  - artifacts/missing_dependency_sockets_20260926/probe_step1_unresolved_314t.json
  IMPACT: Step-2 behavior matches the patch in the probe; suites still to run.
  NEXT: Unit and component suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:41:00Z
  TYPE: MEASURE
  CLAIM: Suites on 3.14.7t from the VM copy (GIL not run yet). unit: 8021 passed, 37 failed = 21 pre-existing
    (architecture docs tool, system documents builder, asset version stamp; same as the prior baseline) + 2 Phase-3
    old-contract + 14 solo compiler tests whose SimpleNamespace spell double lacked _spell_system_states (double
    fixed in _make_spell: a registry with no topology; both files then 69 passed). component: 1998 passed, 0 failed.
    integration spellbook: 562 passed, 11 failed, all asserting the retired conjure refusal. integration
    aether/conduit/mutation_research/multithreading: 1088 passed, 3 failed = 2 provider-removal (CONFLICT note) + 1
    concurrency flake ("Cannot build CreationContext before spell_codegen_creation exists") that also fails 1 of 8
    runs on the pre-change melder_before copy. crystallizer + live_sim: 259 passed. experimentation: 247 passed,
    5 failed = 4 old-contract + 1 provider-removal experiment.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py:246-270
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:1275-1320
  IMPACT: No regression outside the two known categories; the solo double change is test-setup drift only.
  NEXT: Owner decisions (below) before rewriting tests or starting step 3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T07:41:00Z
  TYPE: FACT
  CLAIM: Old-contract tests are 12 functions, not the 6 recorded at 01:13:28Z: that search matched the "no DI
    candidate" text, while these also assert a generic resolution error at conjure. Added: resolution_break_matrix
    test_b1_concrete_dependency_unbound_fails_conjure, test_b1_deep_chain_missing_leaf_fails_conjure,
    test_b2_provider_under_different_frame_fails_conjure, test_b2_provider_bound_under_own_class_only_fails_frame_hint;
    resolution_error_matrix test_conjure_with_unresolvable_dependency_raises; experiment
    test_optional_dependency_default_resolution_experiment::test_required_dependency_without_provider_still_refuses.
    The B2 pair covers a provider bound under a different frame or only under its own class: under the approved
    rule these also become unresolved inputs, not errors.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:424-493
  IMPACT: The rewrite list grows to 12 functions; the B2 behavior change is worth naming in the release note.
  NEXT: Rewrite after the owner decisions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T07:41:00Z
  TYPE: CONFLICT
  CLAIM: Removing a provider no longer breaks a dependent that has a stored instance. With Dep1 bound, a unique Root
    melded, then cleanup_spell(Dep1): Root goes gated, its structural rerun now succeeds (socket UNRESOLVED_INPUT
    instead of the old "no candidate" failure), and meld returns the same stored Root, still holding the disposed
    Dep1. A many Root raises UnresolvedInputError as intended. Two integration tests and one experiment state the
    opposite contract explicitly: "a dependent that still resolves after its dependency was disposed is a
    correctness violation". Before, the missing-provider refusal doubled as that invalidation; the patch invariant
    "a reused object never demands its unresolved inputs" assumed the input was never provided.
  EVIDENCE:
  - artifacts/missing_dependency_sockets_20260926/probe_provider_removal.py:1-47
  - artifacts/missing_dependency_sockets_20260926/probe_provider_removal_314t.json
  - tests/integration/melder/aether/conduit/test_index_invalidation_integration.py:124-146
  - tests/experimentation/test_cleanup_dependency_breaks_dependents_experiment.py:1-40
  IMPACT: Shipping as-is would serve objects built against a removed provider. The owner chooses the contract.
  NEXT: DECISION_REQUEST to the owner with options.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-26T07:43:00Z
  TYPE: DECISION_REQUEST
  CLAIM: Two owner decisions block the rest of step 2 and the test rewrite.
    D-A (provider removal): (1) removing a provider retires the stored instances of its dependents (transitively,
    through the existing dependents graph), so the next meld builds them and the new rule applies: supply the
    value or bind a provider; fixes the pre-existing case where rebinding a provider revived a stored dependent
    holding the disposed object; changes cleanup_spell to dispose dependents' stored objects (scope growth).
    (2) keep the old refusal only for a socket whose provider was removed (history-aware Phase 3) until a provider
    is bound again; smallest behavior change, breaks the "Phase 3 is deterministic for a registry" invariant.
    (3) accept that stored dependents keep being served; rewrite the 3 removal tests. Recommendation: (1).
    D-B (export): export UnresolvedInputError at the package root like MeldExecutionError (conflicts with overlay
    rule 5.2) or import it only from its module. Recommendation: root export, matching its siblings.
  EVIDENCE:
  - artifacts/missing_dependency_sockets_20260926/probe_provider_removal_314t.json
  - src/melder/aether/conduit/conduit.py:5243-5285
  - src/melder/utilities/custom_exceptions/meld_execution_error.py:68-69
  IMPACT: Step 3 (conjure report, cache generation 11) is independent and can proceed; tests wait for D-A.
  NEXT: Ask the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:44:34Z
  TYPE: FACT
  CLAIM: Correction: the DATETIMEs of the notes after 07:20:30Z were written as estimates and ran ahead of the clock
    (up to 09:12:00Z while `date -u` read 07:44:20Z). They are re-stamped in order within 07:24:00Z-07:43:00Z;
    note content is unchanged. From here every DATETIME comes from `date -u`.
  EVIDENCE: attention_board.md:111-111
  IMPACT: Keeps the ticket timeline truthful for re-entry.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T07:49:37Z
  TYPE: DECISION
  CLAIM: Owner decision D-B: export UnresolvedInputError at the package root ("yeah export the error thats fine"),
    overriding overlay rule 5.2 for this symbol, matching its sibling exceptions. D-A is not decided: the owner
    read the question as removing the providers when a consumer is removed; it is the reverse direction and only
    concerns already-stored consumer objects. Re-asking with the owner's own example.
  EVIDENCE: src/melder/__init__.py:145-163
  IMPACT: Root export proceeds now; the removal tests stay unresolved until D-A.
  NEXT: Add the import, the __all__ entry and the ERRORS docstring line.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T07:49:37Z
  TYPE: FACT
  CLAIM: Correction to the D-A option text sent to the owner: "rebinding a provider revived a stored dependent holding
    the disposed object" was not verified and is wrong. Probe on both the pre-change copy and the current code:
    after cleanup_spell(Dep1) and binding a new Dep1, meld(Root) raises "Cannot build CreationContext before
    spell_codegen_creation exists" in both. That failure pre-dates this change and is out of scope here.
  EVIDENCE: artifacts/missing_dependency_sockets_20260926/probe_provider_rebind.py:1-53
  IMPACT: Option (a) loses that claimed benefit; the owner gets the corrected picture.
  NEXT: Re-ask D-A with the corrected facts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:51:49Z
  TYPE: MEASURE
  CLAIM: "Disposed" in the D-A question was wrong. Probe (3.14.7t): Testing1 bound unique with
    disposal_method_names=["close"]; Tester(testing1) melded; cleanup_spell(Testing1). The spell is gone from the
    book, meld(Tester) returns the same stored Tester, tester.testing1 is the same Python object, and its close()
    was NOT called. cleanup_spell unregisters the spell and drops it from Melder's tracking; the stored consumer
    keeps an ordinary, unclosed reference. Whether other existences or stores run disposal here is UNKNOWN
    (only unique was measured).
  EVIDENCE:
  - artifacts/missing_dependency_sockets_20260926/probe_disposed_reference.py:1-49
  - artifacts/missing_dependency_sockets_20260926/probe_disposed_reference_314t.json
  IMPACT: Option (a)'s rationale (serving an object holding a disposed dependency) does not hold for this case;
    option (c) now matches the late-binding model: existing objects stay intact, only new builds change.
  NEXT: Give the owner the corrected facts and a revised recommendation (c).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:52:36Z
  TYPE: DECISION
  CLAIM: Owner decision D-A = (c): a consumer object built before its provider's spell was cleaned up keeps being
    served with the dependency it already holds ("thats actually fine"). No cascade in cleanup_spell and no
    history-aware Phase 3. The two index-invalidation tests and the cleanup experiment are rewritten to this
    contract: the dependent is gated, a stored dependent is reused unchanged, a fresh build raises
    UnresolvedInputError until the value is supplied or a provider is bound.
  EVIDENCE:
  - artifacts/missing_dependency_sockets_20260926/probe_disposed_reference_314t.json
  - tests/integration/melder/aether/conduit/test_index_invalidation_integration.py:124-146
  IMPACT: Unblocks the task. Test rewrite list: 12 old-contract functions plus these 3.
  NEXT: Step 3: conjure INFO report after the structural phases, then cache generation 11.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:53:52Z
  TYPE: FACT
  CLAIM: Step 3 done. _prepare_spellbook_for_conjure calls _report_unresolved_inputs right after the structural
    phases (Phase-4 results still exist there) and emits one INFO line only when the book's active spells carry
    UNRESOLVED_INPUT warnings, e.g. "Conjure: 1 unresolved input(s) have no registered provider and must be supplied
    by the meld that constructs them (or given a provider): Task.work -> Pkg." (seen through a stdlib logger).
    CachingSystem generation 11 "unresolved_input_sockets" added; the cache-history integration test pins it
    (11 passed on 3.14t).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:290-359
  - src/melder/utilities/caching_system/caching_system.py:99-149
  - tests/integration/melder/spellbook/test_cache_schema_version_integration.py:12-24
  IMPACT: Rollout steps 1-3 complete; executors emitted before this change are retired by the cache generation.
  NEXT: Step 4: rewrite the 15 old-contract functions, add regressions, run 3.14t and GIL.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:57:30Z
  TYPE: FACT
  CLAIM: Step 4a done: all 15 old-contract functions rewritten to the new contract (not deleted): conjure succeeds,
    meld without the value raises UnresolvedInputError with the expected type, a supplied override constructs, and
    after cleanup_spell a stored dependent is reused while an unbuilt one needs the input (D-A). Renamed where the
    name stated the retired contract; the experiment file name is kept and its docstring records the history.
    Found and fixed while rewriting: a quoted annotation in a `from __future__ import annotations` module reached
    expected_type_name as "'MissingDependency'"; the rule now strips one layer of matching quotes.
    3.14t: experimentation + integration spellbook + index invalidation + Phase-3 unit: 870 passed, 0 failed.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py:425-521
  - tests/integration/melder/aether/conduit/test_index_invalidation_integration.py:1-20
  - tests/integration/melder/spellbook/test_spellbook_integration_future_annotations.py:1243-1295
  - src/melder/utilities/custom_exceptions/unresolved_input_error.py:133-173
  IMPACT: The retired contract is gone from the suite; the display rule handles postponed-evaluation modules.
  NEXT: Step 4b: new component regressions (compiler facts and every executor family), then full 3.14t and GIL runs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T08:01:44Z
  TYPE: FACT
  CLAIM: Step 4b done: two new component files, 70 tests, pass on 3.14.7t and 3.14 GIL. Compiler side: zero
    providers -> UNRESOLVED_INPUT with watch key (indexed and scan paths, Optional without default, keyword-only
    kind), provider -> NORMAL, definition -> OVERRIDE_REQUIRED, two providers -> ambiguity error, defaults and
    collections unchanged, Phase-4 warning, injection source and both exporters per family, conjure INFO line,
    late provider -> NORMAL edge, display rule. Execution side, per family (solo, many_only, generalized) and
    fresh or marshal-reinstalled manifest: supplied object/falsey/None by root, path and broadcast key; missing
    -> UnresolvedInputError with fields, cause and keys in the message; override lane with another input;
    positional supply; reuse; unrelated body TypeError keeps the existing error; several missing inputs listed.
    Existing behavior found, out of scope: a solo root passes a broadcast key ('**work') through as a literal
    keyword, on the pre-change copy too; broadcast keys address dependencies only.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_unresolved_input.py:1-338
  - tests/component/melder/aether/conduit/test_conduit_component_unresolved_inputs.py:1-216
  IMPACT: Every row of the patch coverage matrix has a regression.
  NEXT: Full unit/component/integration/experimentation runs on 3.14t and GIL.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T08:09:30Z
  TYPE: MEASURE
  CLAIM: Full qualification from the VM copy (unit, component, integration, experimentation; github_workflows and
    llm_support ignored as before). 3.14.7t: 12281 passed, 21 failed; 3.14 GIL: 12280 passed, 22 failed. The 21 on
    both are the pre-existing baseline (architecture docs tool 18, system documents builder 2, asset version stamp
    1); the extra GIL failure is the known concurrency flake (also on the pre-change copy). Two more conjure test
    doubles lacked Spell.validation_result_phase4 (DummySpell in test_spellbook.py, one SimpleNamespace in the
    fastpath test); both now mirror the Spell read-through. Separate pre-existing finding: 3.14t and GIL share
    cache_tag "cpython-314", so a GIL run after a 3.14t run in one checkout admits the other build's conjure
    bundles and 5 resolution-contract tests fail with "generalized manifest references unknown spell_id";
    reproduced identically on the pre-change copy, gone with a cleared __conjure_cache__.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spellbook.py:39-130
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:666-697
  - src/melder/utilities/caching_system/caching_system.py:99-155
  IMPACT: Rollout step 4 is complete with no attributable failure; the cache-tag overlap is worth a separate task.
  NEXT: Step 5: promote the patch into src_architecture/src_components, update graph descriptors, add the release
    note; ask the owner about the build-asset rebuild (step 6).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T08:16:20Z
  TYPE: FACT
  CLAIM: Re-onboarded after compaction and re-certified as melder_0 (08:16Z). Mailbox M1-7 consumed from melder_1:
    long gauntlet runs are skewed by the harness (_run_gauntlet_benchmark retains ~393 worker-thread ints per
    iteration; later cycles 2-2.5x costlier on 3.14t for Melder and dishka alike). No Melder leak. Any S2-S5
    override benchmark must treat 50k-vs-100k deltas with care until the owner's harness decision lands.
  EVIDENCE: tickets/tasks/2026-09-26_measure_melder_long_run_attribution_task.md
  IMPACT: No effect on this task's code; a caveat for the S2-S5 performance measurements.
  NEXT: Repair the stale board row and this ticket's Handoff Summary/Validation, then step 5.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T08:19:35Z
  TYPE: PLAN
  CLAIM: Step 5 promotion plan, from the authoring instructions (read in full), the examples, the four patch docs
    and the current source re-read for every claim. Content-preservation baselines captured before any edit
    (multiset of both documents plus byte copies). src_components: DI Descriptors responsibility bullet; Meld
    Resolution Runtime "Unresolved inputs (2026-09-26)" block, failure mode, Key File, DI-spec decision line;
    SpellCompiler block after S3, corrected invariant and failure-mode lines (zero candidates no longer raise);
    SpellSystemStates watcher bullet; new C1 flow and diagram; C1 remeasure of __init__, caching_system,
    spell_system_states plus a new unresolved_input_error entry; Information Sources; handoff paragraph.
    src_architecture: invariant, failure mode, glossary term, conjure/meld sequence lines, diagram, C1
    remeasure, Information Sources, handoff paragraph. The Full Package Inventory is a dated generated walk
    (hand edits forbidden there), so the new module is recorded in the handoff as absent from it.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-516
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:696-935
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1362-1397
  - src/melder/utilities/custom_exceptions/unresolved_input_error.py:175-297
  - src/melder/aether/spellbook/spellbook_creation_system.py:300-360
  IMPACT: Every edit is additive or a named correction of a now-false line; nothing moves between documents.
  NEXT: Apply the src_components edits, regenerate its index, run the preservation diff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T08:19:35Z
  TYPE: RISK
  CLAIM: Pre-existing portability defect, not introduced here: both canonical documents' `## Indexing` sections
    carry tool invocations and a `Spec: agent_onboarding/...` pointer, which the authoring instructions' portability
    rule forbids (the shipped examples carry the same pattern). Left unchanged; relocating them is a separate
    owner decision because the documents ship as package hardcopies.
  EVIDENCE:
  - system_docs/src_architecture.md:33-115
  - system_docs/src_components.md:22-107
  - agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:134-175
  IMPACT: The Quality Gate's portability checks fail on pre-existing lines regardless of this promotion.
  NEXT: Raise with the owner at the step-6 question.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T08:24:08Z
  TYPE: FACT
  CLAIM: Step 5a done: both canonical documents carry the promotion and their indexes are regenerated
    (src_components 143 sections / 9234 lines, src_architecture 54 / 2783). Content-preservation diff against
    the pre-edit baselines: every lost line is accounted for: 2 metadata dates, 1 named correction ("zero or
    multiple candidates" -> multiple only), C1 remeasures of __init__ (271), caching_system (624) and
    spell_system_states (1522), and 12 path:line citations into spellbook_creation_system.py and
    shared_compiler_executions.py remapped to their symbols. Six of those 12 were already wrong before this
    change (check_system_state, _run_scheduler_with_phases/_phase_run_lock, capture_phase8_11_codegen_ir,
    its _if_dirty flush, reset_phase8_11_codegen_ir); the rest were shifted by this task's inserts. The
    citation bounds recipe reports 0 problems; no new unclosed-bracket heading; package-path hits unchanged
    (9 and 11, all pre-existing).
  EVIDENCE:
  - system_docs/src_components.md:2819-2850
  - system_docs/src_components.md:3127-3148
  - system_docs/src_components.md:6008-6021
  - system_docs/src_architecture.md:992-1001
  - system_docs/src_architecture.md:1146-1151
  - src/melder/aether/spellbook/spellbook_creation_system.py:1182-1229
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1367-1525
  IMPACT: The component and architecture maps describe the shipped behavior; the stale citations in touched
    files point at their symbols again.
  NEXT: Graph descriptors: re-extract the changed files, author the UnresolvedInputError node, reassemble.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T08:31:00Z
  TYPE: FACT
  CLAIM: Step 5b done: graph refreshed. Descriptors re-extracted (596, 0 skipped, --strict) and reassembled
    (src_graph.md 28072 lines, index verified). New node UnresolvedInputError authored (role, responsibilities,
    owns_state, one `uses` edge to SpellSystemStates) and accepted with SocketKind after reading both files
    whole. Responsibility lines added to 13 existing nodes the change affects (CompilerPhase3,
    SpellSystemStates, injection source/strategy, shared executions, required-holes, binding-cycle, creation
    system, CachingSystem, solo/generalized/many_only no-override compilers); those stay SEMANTICS_STALE
    because their full prose was not re-verified this pass. The Key Files join resolves with 0 misses.
    Writing descriptors in place on the mount failed intermittently with OSError EINVAL, so extraction and
    assembly ran against a VM copy and only changed files were copied back (byte-identical check).
    Found while reading: the UnresolvedInputError docstring still said expected_type comes from the Phase-1
    annotation and never from the frame key; corrected to the 07:30Z behavior (signature at meld, frame-key
    fallback). The file is now 298 lines (C1 entry updated); 70 component tests pass on 3.14t.
  EVIDENCE:
  - src/melder/utilities/custom_exceptions/unresolved_input_error.py:38-47
  - src/melder/utilities/custom_exceptions/unresolved_input_error.py:133-160
  - system_docs/src_graph.md:26489-26532
  IMPACT: The graph describes the new exception and the changed components; staleness of older prose is visible.
  NEXT: Release note in release_docs/next_version_release.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Patch docs owner-approved. Steps 1-4 are implemented and qualified: compiler socket and consumers (07:30Z),
failure-path wiring in every family (07:37Z), root export (D-B), conjure INFO report and cache generation 11
(07:53Z), 15 old-contract tests rewritten and 70 new component regressions (08:01Z), full 3.14t and GIL runs with
no attributable failure (08:09Z). Owner decisions in force: D-A (c) stored consumers keep their dependency after
the provider's spell is cleaned up; D-B root export of UnresolvedInputError.
Remaining: step 5 (promote to src_architecture/src_components, graph descriptors, release note), step 6 (owner
decides the build-asset rebuild), then acceptance walkthrough and patch-lane archive. Resume from the latest NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
