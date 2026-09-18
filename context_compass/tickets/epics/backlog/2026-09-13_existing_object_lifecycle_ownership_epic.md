# Epic: Explore reference registration and lifecycle ownership for user-created objects

## Metadata
- Epic ID: EPIC-2026-09-13-existing-object-lifecycle-ownership
- Status: in_progress
- Owner: codex
- Agent Name: updater_0
- Priority: p2
- Created: 2026-09-13T22:04:24Z
- Updated: 2026-09-17T22:21:43Z
- Target Window: active discovery; implementation remains unselected
- Related Program/Initiative: existing-instance injection and disposal investigation

## Primary Exploration: Register the Reference, Preserve the Blueprint, Forbid New Creations

**Start the next deep dive here. This is the central design question of the epic.**

Current owner clarification: the user binds an actual existing object. Treat it through normal object
machinery with creation disabled, studying the supplied reference/type. Transfer of ownership must
carry the existing object and its applicable responsibility. Work in stages and reuse existing systems
where the source supports it; no new compiler architecture is presumed.

The authoritative stage sequence and current checkpoint are in:
- tickets/stories/2026-09-17_existing_object_reference_blueprint_discovery_story.md

Current Stage 1 task:
- tickets/tasks/2026-09-17_existing_object_bind_representation_design_task.md

The definition-first/later-supply extension below is retained for future exploration. It must not
replace the supplied-instance input case or expand the current bind-representation stage.

Melder is a Dependency Graph Runtime with explicit uniqueness requirements; conventional DI
registration patterns do not determine its model. The owner considers the current owned-object
system incomplete and wants to explore registering an existing object's reference through the broader
graph/blueprint machinery, while hard-restricting that binding from creating a new instance.

The proposed exploration includes multiple registered versions and broader lifetime modes such as
unique_per_conduit. What those modes mean for a supplied reference, how its blueprint participates in
compilation, and how ownership follows it are deliberately unresolved. The owner's expectation of
substantial compiler work is a design hypothesis to investigate, not a verified implementation estimate.

This front-page proposal supersedes the narrow disposal-flag framing as the epic's starting point.
The accepted disposal setting, Protocol validation and transfer concerns remain part of the eventual
model. No implementation or additional discovery is performed by recording this proposal.

Also preserve the owner's subsequent configuration idea: a type/blueprint may be registered before
any value is supplied, with construction by Melder forbidden and external code responsible for
providing the reference. Existing Conduit and SpellSpace machinery provides the scopes; this does
not propose a new request-scope system. The exact admission and missing-value contracts remain open.

The live-reference-only case is part of this design: a supplied object may have no physical source
file or importable module. Investigate how SpellCrystal and SyntheticModule represent available
definitions and required external participation without silently permitting construction or claiming
that recording structure restores the previous live object and its state.

### Dependent Repair: Provider Executable Artifacts

The owner places the remaining provider-artifact repair under this ownership program. Do not schedule
it as an independent small repair or choose its ownership policy in isolation. The existing repair
epic/story/task retain their reproductions and acceptance evidence, but their implementation must
follow the owned-object contracts and required ownership work selected here.

- tickets/epics/2026-09-13_provider_artifact_ownership_and_existing_instance_planning_epic.md
- tickets/stories/2026-09-13_provider_artifact_ownership_story.md
- tickets/tasks/2026-09-13_repair_provider_artifact_ownership_task.md

This is the owner's architectural sequencing decision. No new source investigation in this update
establishes that every proposed redesign feature is technically required to repair the existing failure.

### Owner's Proposal (Verbatim; Line-Wrapped Only)

> ok so right now we're stuck deciding how to manage these objects, ok so first off, melder is not a DI
> container system, not strictly, we do rely on uniqueness so registering multiple owned objects is a
> strange concept to me because like maybe its something we can do, like lets talk about it more, what
> if we just registered the reference of the owned object, and treated it like other objects, but they
> are hard-restricted to never allow new creations of it, so this produces a whole new compiler process
> and it will require a lot of rework but it will allow users to register n number of many versions or
> unique per conduit etc etc, but this would mean we do record the blueprint but then treat it
> differently, and it introduces a new layer of problems,

### Questions the Deep Dive Must Resolve

1. Reference and uniqueness: what identifies the registered reference, its blueprint/version and
   the actual user-created object? Which repetitions are legal, aliases, replacements or collisions?
2. Compiler treatment: how does the blueprint participate in discovery, validation, planning and
   generated execution while creation of the supplied target remains impossible on every path?
3. Lifetime/version meaning: what do multiple versions, many and unique_per_conduit represent for
   an already-created object when new physical instances may not be constructed from that binding?
4. Existing dependencies: preserve the verified ability to inject supplied A into newly constructed
   B, using the exact original reference. Reference-only treatment must preserve that dependency edge.
5. Ownership: how do registration, staged activation, scope release, transfer/rollback and cleanup
   operate consistently across the Spell, blueprint, runtime stores and any aliases of the same object?
6. Recording: what blueprint/reference restrictions and lifecycle policy must Crystallizer and
   version records retain? Keep recording structure distinct from restoring an external live instance.
7. Required external inputs: how is a registered type/blueprint fulfilled before resolution, through
   existing scope/lifetime rules, while Melder remains forbidden from constructing it?
8. Fileless/live-only values: what can be captured into SpellCrystal or represented by SyntheticModule,
   and what must remain an explicit external-supply requirement after structural restore?

### Required Deep-Dive Output Before Implementation

- A source-backed comparison of the current existing-object path and the proposed reference/blueprint path.
- Explicit identity, no-new-creation, validation, lifetime/version and ownership contracts.
- A complete compiler/runtime/persistence impact map with migration and regression requirements.
- Owner decisions on unresolved semantics before committing to a compiler redesign or broader lifetimes.

The direct A-to-B scenario already works: the latest native check passed with an identity assertion.
Evidence remains in the existing-instance task and direct_owned_dependency_confirmation.log/xml.
The next investigation concerns the model around that working capability, not rediscovering basic injection.

## Problem / Opportunity
An externally constructed object is already retained on Spell.user_created_object and can be returned
directly during resolution. Active admission also registers that reference in the owning root's
Creations store. Disposal has its own registry and method-list contract. Staged prebuilt objects are
retained by their Spell but are not currently registered through the same admission path.

Binding currently discards all disposal candidates for prebuilt objects. The owner accepted a
default-disabled configuration opt-in for book-level names, while explicit per-bind names remain
effective. Further tracing showed that implementing this coherently reaches creation admission,
staging, transfer, rollback, cleanup ownership and persistence. The owner requests a separate epic
and explicitly defers this work while other existing-instance errors are investigated.

This epic supersedes the narrow three/four-file implementation estimate in the earlier blast-radius
artifact. That artifact remains source evidence and a starting map, not a complete ownership design.
No disposal flag, instance method matching or lifecycle change has been implemented.

Protocol admission is another part of this same model: the class binding path checks the declared
Protocol members, while the existing-instance path skips that check. An incompatible supplied value
can be injected and fail when the consumer uses its missing method. The owner requests that this
validation gap be included here, alongside reference retention and lifecycle ownership.

## MRP Alignment
An existing object must have a clear lifecycle owner, remain injectable by identity, and move between
owners without being lost, duplicated or disposed by the wrong scope. Establish one coherent contract
across runtime storage and structural records before enabling a convenience configuration flag.

## Ticket Contract
- ENTRY_GATE: owner explicitly starts the reference/blueprint deep dive; implementation additionally
  requires accepted design decisions, linked story/task routes and patch contracts.
- EXECUTION_BOUNDARY: existing-object registration/Protocol validation, reference retention, lifecycle custody,
  disposal configuration,
  creation admission, staging, ownership transfer, rollback, and persistence compatibility.
  The reference/blueprint/no-new-creation model and its compiler implications are the primary exploration.
- DEPENDENCIES: accepted annotation and existing-instance injection repairs; current source/doc rereads.
- EXIT_GATE: all required stories accepted with native lifecycle and persistence evidence.
- FAILURE_ESCALATION: record unresolved ownership choices and source contradictions before implementation;
  do not fix transfer or staging by bypassing normal transactions, validation or custody boundaries.

## Goals
- Determine whether and how user-created reference bindings can participate in Melder's blueprint,
  version and lifetime machinery while preserving uniqueness and prohibiting fresh target construction.
- Specify construction, contract validation and lifecycle ownership as separate decisions.
- Validate the contract advertised by an existing provider without reconstructing the object.
- Separate supplying/injecting an existing value from taking responsibility for its disposal.
- Keep the same supplied instance through lookup, injection, scope use, ownership moves and rollback.
- Make the lifecycle owner and disposal admission point explicit for active and parked values.
- Preserve correct method order and ensure only the designated owner executes the cleanup contract.
- Record configuration and structural policy without claiming external live instances are restored.

## Non-Goals
- Implementing any part of this epic while it is parked.
- Changing callable objects into prebuilt values or adding factory-return disposal by implication.
- Regressing the repaired Python defaults, annotation acquisition or exact existing A-to-B injection behavior.
- Changing named lesser conduits, general frame grouping or release versions.
- Patching provider-artifact ownership independently of this program's ownership contracts.
- Editing CommandOps/Iris to mask native Melder behavior.

## Scope Boundaries
- In scope: Protocol registration validation, ownership policy, existing-object storage consistency,
  admission/release, transfer and
  rollback, parked/active transitions, disposal matching and recording, tests/docs/assets.
  Explore reference registration, blueprint recording, compiler treatment, version selection and
  possible expansion beyond unique-only lifetime admission as part of that same model.
- Out of scope: unrelated disposal-order changes, global reference counting or deduplication unless
  explicitly selected as part of the ownership contract, and external resource reconstruction.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: owner explicitly requests the reference/blueprint discovery story and investigation.

## Accepted Configuration Contract
- Property: existing_objects_configured_dispose_applied, bool, default False.
- Fluent setter: with_existing_objects_configured_dispose_applied(enabled: bool = True).
- False: prebuilt values use explicit per-bind disposal names only; configured book names are ignored.
- True: prebuilt values combine explicit and configured names under ordinary priority/overlap rules.
- Preserve configured group order, book ownership of overlapping names, missing-name filtering and
  one occurrence of each retained method in the effective list.
- Configure before binding; freeze seals configuration. The effective list remains bind-established.
- Explicit names formerly ignored for prebuilt objects become effective: document this behavior change.
- This accepted flag contract does not settle when lifecycle custody begins or transfers.

## Existing-Object Contract: Three Independent Decisions
- Construction: the supplied object already exists. Preserve its identity and skip constructor discovery
  or execution; do not remove the consumer-to-provider dependency edge.
- Contract validation: registration under a Protocol must validate the required member contract.
  Being prebuilt does not exempt a provider from this check. A valid structural implementation need
  not inherit from the Protocol. Define parity with the existing class admission check explicitly.
- Lifecycle ownership: separately determine who retains, transfers and disposes the supplied object,
  and when custody begins/ends. Borrowed versus managed is not decided by construction origin alone.

These are coordinated parts of one existing-object model. Neither constructor opacity nor a successful
lookup proves Protocol compatibility or cleanup ownership. Do not implement independent exceptions
that leave these three decisions inconsistent.

## Requirements
- Treat hard no-new-creation enforcement for the supplied target as an explicit design constraint.
  It must remain distinct from allowing that reference to satisfy another object's dependencies.
- Do not equate a requested lifetime/version label with creation of additional physical objects;
  establish its semantics for existing references during the primary deep dive.
- Specify the uniqueness boundary: service key, registration, supplied value and scope are distinct.
  Two registrations may identify two different same-class values or alias one value; cleanup ownership
  must be decided independently of that selection/reuse topology.
- Reject existing providers missing a required Protocol member or exposing a non-callable member where
  the Protocol requires a method, consistently with the accepted class-provider admission contract.
- Preserve valid existing-provider injection by exact identity, including inherited implementations.
- Keep the current concrete/string frame grouping and callable/factory contracts explicit. Broader
  Protocol inheritance, annotated-data or signature/type checking requires a separately settled scope.
- Define whether a value is borrowed or managed independently of its original construction location.
- Map every owning reference: Spell, binding profiles, active/parked book maps, runtime Creations,
  detached transfer payloads, and compiled occurrence captures.
- Determine which reference is authoritative for value resolution and for lifecycle ownership.
- Keep storage, disposal metadata and owner identifiers coherent through every admitted transition.
- A borrowed conduit/scope must not silently adopt provider cleanup based on its own configuration.
- Transfer must state whether custody, effective names and live value move together; honor the existing
  transfer/discard options and transaction/rollback contracts rather than inventing a second path.
- On rollback, restore the same object and its appropriate cleanup responsibility without double disposal.
- Decide behavior for the same instance under multiple bindings/owners before claiming exactly-once cleanup.
- Define cleanup behavior before conjure, while parked, after selection, on removal and at final scope release.
- Preserve runtime reuse and injection without re-running an existing object's constructor.
- Keep ownership transitions synchronized with active execution under supported free-threaded Python.
- Preserve default-disabled behavior for existing callers that supplied no explicit disposal names.
- Crystallizer round-trips the flag and resolved names; old records default/report False appropriately.
- External-instance replay remains a code-participation boundary, with explicit shortfalls.

## Source Findings and Unknowns
Verified:
- Current bind-time Protocol validation applies to ClassBindingProfile only. The Phase-4 existing-creation
  compatibility strategy checks presence/lifetime/profile/parameters and does not close the Protocol gap.
- Native Protocol tests record four rejection failures and fourteen passing controls, including class
  rejection, valid/inherited instance injection, concrete/string grouping and factory admission.
- Bind resolves disposal only for ClassBindingProfile today.
- Direct existing-value execution returns Spell.user_created_object.
- Active prebuilt admission forwards the same instance and metadata into Creations.
- Creations stores live references separately from disposal entries and executes established method lists.
- Staged admission/promotion lacks the same eager registration in the inspected paths.
- Existing-object live probes inspect the Spell reference, so they do not prove disposal registration.
- Generic Spellbook configuration emission/reload can transport the proposed boolean.

Not yet established:
- Complete transfer-of-ownership behavior for every existing-object lifecycle transition.
- Whether current transfer code can leave Spell references, detached entries and owner stores inconsistent.
- The intended custody start/end for never-conjured books and never-selected parked instances.
- Alias/multiple-binding ownership semantics and disposal guarantees across roots.
- Complete error/rollback and concurrent execution behavior for the new managed-existing contract.
- Whether and when transferred/re-published providers require revalidation; define this explicitly
  without introducing repeated checks into every meld or treating visibility as ownership.

## Catch-up Read Map
Begin with the Primary Exploration section above. The comparative DI material below is supporting
context only; Melder's own DGR, uniqueness and user-created reference contracts drive the design.

Comparative research:
- context_compass/artifacts/existing_object_di_comparison_20260913/comparison.md:
  cited Dishka, Dependency Injector and Autofac identity/multiplicity/cleanup comparison.
- context_compass/tickets/tasks/2026-09-13_compare_existing_object_ownership_di_task.md:
  source/proof limits; documentation research, not an executed interop test suite.

Read this epic and the blast-radius artifact first. Descend source architecture -> component slices
-> graph slices -> implementation. Earlier map line ranges are leads; verify current source before use.

System documents:
- context_compass/system_docs/src_architecture.md: Bind/Conjure/Meld, cleanup, ownership transfer,
  operational invariants and persistence architecture.
- context_compass/system_docs/src_components_index.md, then relevant src_components.md slices:
  Binding Pipeline; Spellbook Configuration; Conduit Runtime; Creations and SpellSpace;
  ConduitWard and Contracts; Ownership Transfer; Crystallizer capture/replay; SpellCompiler validation.
- context_compass/system_docs/src_graph_index.md -> exact source-file sections below.

Core source:
- src/melder/aether/spellbook/configuration/spellbook_configuration.py: property lifecycle and reload.
- src/melder/aether/spellbook/bind/bind.py: classification, _bind_logic Protocol admission,
  _structurally_implements_protocol, disposal matching and fingerprint.
- src/melder/aether/spellbook/spell_compiler/validation/strategies/existing_creation_compatibility_strategy.py:
  current existing-provider checks and the absent Protocol conformance check.
- src/melder/aether/spellbook/spell.py: user_created_object, cleanup, owner fields/context captures.
- src/melder/aether/spellbook/spellbook.py: bind/bind_inactive, active/parked maps, notch, removal, cleanup.
- src/melder/aether/spellbook/spellbook_creation_system.py: define_conduit_into_spells.
- src/melder/aether/spellbook/bind/spell_index.py: version membership and active selection.
- src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:
  current no-constructor-requirements treatment of existing values.
- src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:
  existing-value occurrences, preserved consumer edges and repaired constructor-contract discovery.
- src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:
  corresponding existing-value contract processing boundary.
- src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:
  planner entrypoint to inspect when mapping the proposed reference/blueprint compiler treatment.
- src/melder/aether/conduit/conduit.py: _register_to_creations, cleanup, upgrade and ownership-transfer API.
- src/melder/aether/conduit/creations/creations.py: add/extract/restore/clear/reset/cleanup.
- src/melder/aether/conduit/creations/conduit_creations.py: scope-specific transfer facade.
- src/melder/aether/conduit/creations/cluster_creations.py: elected-owner storage facade.
- src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py: preflight, move/dispose, rollback.
- src/melder/aether/conduit/conduit_ward/conduit_ward.py: contracts, owner references and borrower updates.
- src/melder/aether/conduit/meld/creation_context/creation_context_builder.py: direct supplied-value returns.
- src/melder/aether/conduit/meld/conduit_meld.py: reuse/live probes and scope selection.
- src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py: disposal signatures.
- src/melder/crystallizer/crystals/spellbook_crystal.py: configuration payload.
- src/melder/crystallizer/crystals/spell_crystal.py: disposal names and replay_required classification.
- src/melder/crystallizer/synthetic_module.py: representation/materialization when no physical module file exists.
- src/melder/crystallizer/crystal_loader_system/restore_engine.py: configuration-first replay and shortfalls.
- src/melder/crystallizer/crystal_loader_system/graft_runner.py: normal-bind policy on graft.

Evidence/tests:
- tests/component/melder/spellbook/test_existing_instance_protocol_admission.py: 18 native cases.
- tests/unit/melder/spellbook/bind/test_bind.py:1091-1102 preserves the old incompatible-instance admission.
- context_compass/artifacts/existing_instance_planning_20260913/protocol_admission_red.xml:
  four failing regressions and fourteen controls; source is still unpatched.
- context_compass/artifacts/existing_instance_planning_20260913/frame_admission_characterization.log:
  stock class rejection versus incompatible instance injection and later consumer AttributeError.
- context_compass/artifacts/existing_instance_planning_20260913/existing_object_disposal_blast_radius.md.
- context_compass/artifacts/existing_instance_planning_20260913/gap_analysis.md and gap_observations.json.
- tests/experimentation/test_existing_instance_gap_experiment.py.
- tests/component/melder/spellbook/test_ordered_disposal_binding.py.
- tests/integration/melder/conduit/test_ordered_disposal_runtime.py.
- tests/unit/melder/aether/conduit/creations/test_creations_disposal_references.py.
- tests/component/melder/crystallizer/test_disposal_configuration_transport.py.
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py.
- Existing transfer tests: locate through tests architecture/components and transfer source callers on resumption.

## Milestones and Required Stories
Active discovery story:
- tickets/stories/2026-09-17_existing_object_reference_blueprint_discovery_story.md

These story boundaries are defined now; materialize their linked story/task files when the epic resumes.
- [ ] STORY-existing-object-reference-blueprint-design: deep-dive the owner's primary proposal,
  establish no-new-creation and uniqueness constraints, and settle version/lifetime semantics before coding.
- [ ] STORY-existing-object-custody-contract: accepted construction/validation/ownership model and custody boundaries.
- [ ] STORY-existing-object-protocol-admission: consistent Protocol validation for class and supplied providers.
- [ ] STORY-existing-object-storage-and-admission: coherent Spell/store/cleanup references and transitions.
- [ ] STORY-existing-object-transfer-and-rollback: transfer, discard, borrowers, rollback and concurrent use.
- [ ] STORY-existing-object-disposal-configuration-and-recording: accepted flag, bind policy and legacy replay.
- [ ] STORY-existing-object-lifecycle-qualification: lifecycle matrix, documentation and generated assets.

## Tasks
- [ ] Start with the reference/blueprint proposal; produce its source-backed compiler and ownership impact map.
- [x] Compare existing-object identity, scope and cleanup across Dishka, Dependency Injector and Autofac.
- [ ] Reproduce current lifecycle behavior independently for each transition before modifying code.
- [ ] Write architecture/component/control-flow patch contracts for the accepted ownership model.
- [ ] Implement and verify one story at a time, preserving unrelated repairs.
- [ ] Qualify all cross-story invariants and retain reproducible source/test evidence.

## Acceptance Criteria
- The owner's reference/blueprint proposal has been investigated and accepted or rejected with evidence;
  any selected broader lifetime/version semantics have an explicit, reviewable contract.
- The chosen implementation cannot construct a new instance of a reference-bound supplied target,
  while preserving its use as a dependency of other objects.
- Existing-provider construction, contract validation and lifecycle ownership are independently specified.
- Invalid Protocol providers fail at the accepted admission boundary; valid supplied providers remain
  injectable by identity. Existing concrete/string grouping and callable-family behavior are preserved.
- Ownership and custody start/end are explicit for every supported prebuilt registration mode.
- Exact supplied identity is preserved through resolution, injection, scope use, transfer and rollback.
- Borrowers cannot dispose provider-owned values unless the accepted contract explicitly transfers custody.
- Parked/promoted/removed values obey the selected lifecycle policy without stranded cleanup entries.
- Same-instance multiple bindings follow a documented, tested ownership rule.
- Default False and explicit per-bind disposal work; True applies ordinary configured ordering semantics.
- Failure handling and repeated cleanup obey the selected idempotency/aggregation contract.
- Recorded False/True/legacy configuration survives reload; external live objects are not claimed restored.
- Required tests, docs, descriptors and build assets are verified before acceptance.

## Risks / Mitigations
- Constructor opacity can be confused with a validation exemption: test admission independently of construction.
- A local matching fix can create partial ownership: verify all transitions before enabling it.
- Independent Spell and Creations references can outlive one another: map authority and test every move.
- A successful meld/live probe can hide absent disposal metadata: assert actual cleanup and retained usability.
- Shared configuration can leak intended ownership across books: test distinct/shared configuration explicitly.
- Transfer can dispose a borrowed dependency or leave two cleanup owners: test provider/receiver/rollback identity.

## Applicable Anti-Patterns
- [ ] No small-flag implementation presented as a complete lifecycle repair.
- [ ] No transfer/rollback fix inferred from method names without reading source.
- [ ] No disposal based on mere visibility or a successful live-object probe.
- [ ] No closure without accepted story-level lifecycle evidence.

## Validation / Test Approach
Use native Python 3.14.7 tests with isolated runtime worlds. Cover active and parked bind before/after
conjure; never-melded objects; direct/nested/collection injection; root/lesser/SpellSpace/linked borrowers;
transfer with preserved or discarded creations; failed transfer/rollback; removal/reselection; repeated
cleanup; aliases; failures and concurrent execution. Test configuration and checkpoint serialization
separately from runtime object identity. Keep original CommandOps acceptance inputs unchanged.
Include the retained Protocol regressions: missing and non-callable members, class/instance parity,
pre/post-conjure binding, valid/inherited implementations, concrete/string grouping and factory controls.

## Rollout / Adoption Plan
Initial discovery is now ready for owner review. Settle the source/admission/custody contracts, then
implement under the story sequence. No release/version/environment changes are authorized by this epic.

## Decision Log
- Owner makes the provider-artifact repair dependent on the owned-object program; retain its separate
  regression records and resume implementation only through the selected ownership contracts.
- Owner makes reference registration, blueprint participation and hard no-new-creation enforcement
  the central exploration topic. Deep compiler/lifetime implications require investigation before design selection.
- Owner accepted the flag name, False default, and explicit-versus-configured disposal semantics.
- Owner rejects treating the whole change as a small binding-only patch and defers implementation.
- Earlier staged-adoption recommendations remain proposals; this epic must settle the larger model first.
- Owner includes Protocol validation in the same existing-object design; prebuilt means construction
  is complete, with validation and lifecycle responsibility determined separately.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/existing_instance_planning_20260913/existing_object_disposal_blast_radius.md
  - artifacts/existing_instance_planning_20260913/gap_analysis.md
  - artifacts/existing_instance_planning_20260913/protocol_admission_red.xml
  - artifacts/existing_instance_planning_20260913/frame_admission_characterization.log
  - artifacts/existing_object_di_comparison_20260913/comparison.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain source-backed discovery for this deferred ownership program.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: resolve ownership choices through source evidence and owner discussion before implementation.

## Notes
- DATETIME: 2026-09-13T22:04:24Z
  TYPE: DECISION
  CLAIM: Owner requests this epic and defers existing-object lifecycle/disposal work to resume other errors.
    The accepted flag is one part of a larger ownership contract; no runtime changes have landed for it.
  EVIDENCE:
  - Owner instruction to create an epic because creations also affect transfer and related concepts.
  - artifacts/existing_instance_planning_20260913/existing_object_disposal_blast_radius.md
  - tickets/tasks/2026-09-13_repair_existing_instance_planning_task.md
  IMPACT: Preserve the findings and full catch-up map; do not implement the earlier narrow proposal.
  NEXT: On owner resumption, investigate the custody model and transfer/rollback source path first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:22:06Z
  TYPE: DECISION
  CLAIM: Owner requests inclusion of the Protocol problem in this existing-object epic. Record three
    separate decisions: construction is already complete; declared provider contracts still require
    validation; lifecycle ownership governs retention, transfer and cleanup independently.
  EVIDENCE:
  - Owner request to update the ticket with the agreed existing-object construction/validation/ownership distinction.
  - src/melder/aether/spellbook/bind/bind.py:464-490
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:155-234
  - tests/component/melder/spellbook/test_existing_instance_protocol_admission.py:1-132
  - artifacts/existing_instance_planning_20260913/protocol_admission_red.xml
  IMPACT: Protocol admission is now a required story/acceptance boundary in this deferred program.
    Retain the four red cases and fourteen controls; no runtime implementation is authorized by this update.
  NEXT: On explicit resumption, settle the coherent existing-object contract before implementing its stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:38:30Z
  TYPE: FACT
  CLAIM: Owner-requested comparative research is recorded in the linked comparison task/artifact.
    It distinguishes registration reuse, multiple same-type values, aliasing and cleanup ownership,
    with different framework defaults. This research supplies design evidence, not implementation approval.
  EVIDENCE:
  - tickets/tasks/2026-09-13_compare_existing_object_ownership_di_task.md
  - artifacts/existing_object_di_comparison_20260913/comparison.md:1-167
  IMPACT: Keep provider keys, value identity, scopes and cleanup owner explicit in the lifecycle model.
    Do not infer arbitrary transfer/rollback support or identical runtime Protocol checking from these sources.
  NEXT: Owner reviews the comparison before selecting Melder's existing-object ownership contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T23:35:50Z
  TYPE: HYPOTHESIS
  CLAIM: Owner proposes, for discussion only, registering a user-created object's reference and
    recording its blueprint while hard-forbidding new creations of that supplied target. This may
    permit broader version/lifetime handling, including per-conduit modes, through a different compiler
    treatment. The owner explicitly requests no discovery on these ideas in this turn.
  EVIDENCE:
  - Owner message proposing reference registration, no-new-creation enforcement and broader lifecycle modes.
  IMPACT: This is not a selected design or an established rewrite estimate. Melder remains a DGR
    with registration-uniqueness requirements; conventional DI analogies do not define its contract.
    The separately requested current A-to-B injection test passed; no discovery on this proposal occurred.
  NEXT: Discuss the reference/blueprint proposal only when the owner chooses to continue it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T23:37:46Z
  TYPE: DECISION
  CLAIM: Owner explicitly asks to put the quoted reference/blueprint proposal front and center in
    this epic and identifies the existing owned-object model as an improvement area. Preserved the
    original wording and promoted the topic into the entry gate, first story, goals and acceptance criteria.
  EVIDENCE:
  - Owner's quoted proposal and instruction to record it prominently for a future deep dive.
  - This epic's Primary Exploration section.
  - artifacts/existing_instance_planning_20260913/direct_owned_dependency_confirmation.xml
  IMPACT: The primary question is now the broader reference/blueprint/compiler model, with disposal
    and Protocol policy underneath it. The proposal remains unselected; no discovery or source changes here.
  NEXT: On explicit resumption, deep-dive the reference model and no-new-creation constraint first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T01:07:11Z
  TYPE: DECISION
  CLAIM: Owner rejects the provider-artifact issue as an independent weekend repair and places it
    behind the broader owned-object work. Linked both epics and the repair story/task, preserving
    the existing red evidence. Confirmed the verbatim reference/blueprint proposal remains front and center.
  EVIDENCE:
  - Owner direction linking this repair to fixing the owned-object model.
  - tickets/epics/2026-09-13_provider_artifact_ownership_and_existing_instance_planning_epic.md
  - tickets/tasks/2026-09-13_repair_provider_artifact_ownership_task.md
  IMPACT: Independent patch selection is paused. Also made the previously discussed external-supply-only
    registration and fileless/live-reference SpellCrystal/SyntheticModule cases explicit on this epic's front page.
    This records architectural direction; it is not a new proof that no narrower technical repair could exist.
  NEXT: Begin with the primary owned-object design exploration when the owner resumes the program.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T21:22:19Z
  TYPE: DECISION
  CLAIM: Owner resumes the primary reference/blueprint exploration and requests a discovery story.
    Created the linked story and tactical source-trace task. This phase will produce evidence,
    candidate contracts, impact mapping and owner decisions rather than change runtime behavior.
  EVIDENCE:
  - Owner instruction to make a discovery story and figure out how this works.
  - tickets/stories/2026-09-17_existing_object_reference_blueprint_discovery_story.md
  - tickets/tasks/2026-09-17_trace_existing_object_reference_model_task.md
  IMPACT: Discovery is active. Prior discussion-only restrictions are lifted for investigation;
    implementation and independent provider-artifact repair remain outside the current tranche.
  NEXT: Trace the current registration/compiler path before selecting a reference representation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T21:46:58Z
  TYPE: FACT
  CLAIM: The primary proposal now has a source-backed initial discovery story, candidate contracts,
    impact map and nine native observations. Storage/admission and direct-reference resolution can
    diverge today; pre-conjure staged selection has a factory-wiring gap. Synthetic source custody
    preserves definitions, while existing instances remain external replay requirements.
  EVIDENCE:
  - tickets/stories/2026-09-17_existing_object_reference_blueprint_discovery_story.md
  - tickets/tasks/2026-09-17_trace_existing_object_reference_model_task.md
  IMPACT: Recommended direction is explicit external-only source policy plus existing scope admission,
    with definition/value identities, cleanup custody and executable-artifact authority kept distinct.
    This is a candidate design; source findings do not establish a full compiler rewrite as necessary.
  NEXT: Review the external-only definition and scoped-admission direction before selecting implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T22:21:43Z
  TYPE: DECISION
  CLAIM: Owner narrows the working starting point to an actual existing object supplied at bind,
    treated through normal machinery with creation disabled. Transfer must carry that object.
    Sequential continuation is now recorded in the discovery story with one Stage-1 task ready.
  EVIDENCE:
  - Owner clarification and repeated-compaction continuation request in this conversation.
  - tickets/stories/2026-09-17_existing_object_reference_blueprint_discovery_story.md
  - tickets/tasks/2026-09-17_existing_object_bind_representation_design_task.md
  IMPACT: Keep broader possibilities in this epic without allowing them to drive every stage at once.
    The story owns stage order; the active task owns exact reads, decisions and the next source action.
  NEXT: Follow Stage 1's bind representation comparison before progressing to storage or transfer design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with owner.
- [ ] All story acceptance criteria confirmed by owner.
- [ ] Boards and artifact disposition synchronized.

## Noting Behavior
Record program boundaries and owner decisions here; keep tactical evidence in future linked tasks.

## Context / Handoff Summary
CURRENT: staged design under STORY-2026-09-17-existing-object-reference-blueprint-discovery.
Read that story's Owner Intent and Current Checkpoint, then the bind-representation design task.
Stage 1 starts with the actual user-supplied instance, normal machinery and construction disabled.
The original discovery task/artifact retains nine observations and the impact map; no production implementation.
START with Primary Exploration and the owner's verbatim reference/blueprint
proposal. Resolve its uniqueness, hard no-new-creation, compiler and lifetime/version implications first.
The remaining provider-artifact implementation is downstream of this ownership program, by owner direction.
Include definitions awaiting external supply and fileless/live-only objects in the exploration.
Then read the three-decision construction/validation/ownership model, accepted
flag contract, unknown custody boundaries and catch-up map. Protocol admission belongs to this program
and has four native red regressions plus fourteen passing controls; evidence remains in the original
investigation task. The earlier narrow implementation estimate is superseded by this broader design.
Read the linked DI comparison for multiple-instance/reuse and cleanup-default distinctions. Research
is complete for review; lifecycle/Protocol implementation remains deferred.
