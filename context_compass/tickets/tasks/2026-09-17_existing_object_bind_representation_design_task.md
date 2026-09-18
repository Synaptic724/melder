# Task: Define normal bind representation for an existing object with construction disabled

## Metadata
- Task ID: TASK-2026-09-17-existing-object-bind-representation-design
- Story: STORY-2026-09-17-existing-object-reference-blueprint-discovery
- Status: in_progress
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-17T22:21:43Z
- Updated: 2026-09-17T23:14:23Z

## Objective
Design only the bind-time representation for the owner's basic target: the user supplies an existing
object; Melder studies that reference and its type, treats it through normal object machinery, and
explicitly forbids construction. Identify which current metadata can be reused and which distinction
must be represented. Do not assume a new compiler subsystem is necessary.

## Ticket Contract
- ENTRY_GATE: parent story's Current Checkpoint routes Stage 1 here; owner clarified the supplied-instance target.
- EXECUTION_BOUNDARY: representation discovery, focused diagnostics if needed, and a concrete design proposal.
  No production patch or work on later stages in this task.
- DEPENDENCIES: initial source trace and nine retained characterization cases; existing annotation/injection repairs.
- EXIT_GATE: field/ownership comparison, proposed construction distinction, compatibility impact and exact
  source changes are reviewable; unsettled representation choices are explicit before implementation.
- FAILURE_ESCALATION: record any downstream constraint that prevents representation design. Follow only
  the dependency needed to answer it and return here; do not resume the whole epic's investigation at once.

## Scope Boundaries
- In scope: the actual bound instance, inspection of its type, binding profiles, Spell/SpellType flags,
  identity inputs, metadata ownership, admission classification and the construction-disabled distinction.
- Constraints carried forward: exact-reference dependency injection; transfer must carry the existing
  object and applicable ownership; ordinary defaults and constructor-opacity repairs stay intact.
- Later stages: scope-store adoption, compiler/executor changes, transfer/rollback/disposal implementation,
  Crystallizer/replay and broad lifecycle qualification.
- Parked extension: register only a definition and supply its value later. Preserve the idea, but it is
  not the input case this first task is designing and does not gate its progress.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: owner asks how the distinction propagates to dependent resolution and explicit meld failure.

## Steps / Checklist
- [ ] Compare the current class and instance bind paths using the recorded source entrypoints.
- [ ] Write a small metadata table: supplied reference, inspected type, profile, SpellType/family,
  identity/signature, construction permission, advertised contract and disposal metadata.
- [ ] Identify normal metadata and machinery that can be reused without invoking the target or treating
  its already-satisfied constructor arguments as DI requirements.
- [ ] Propose where the explicit construction prohibition belongs, with affected readers and compatibility costs.
- [ ] Carry the dependency-aware failure contract below into the representation proposal and later plan metadata.
- [ ] State how a callable existing object can remain an existing value when that is the binding intent.
- [ ] Present the bounded representation proposal and any owner decision needed. Record the result here
  and update the story checkpoint before beginning another stage.

## Deliverables
- A source-backed current/proposed bind representation table in this ticket or a linked design artifact.
- Proposed fields/classification and exact affected symbols, with no production implementation claim.
- The representation contract passed to Stage 2 and any unresolved decision that prevents that handoff.

## Dependency Resolution Contract Added By Owner

Construction disabled does not mean the object is unresolvable. The supplied object must remain a
normal provider dependency. When B depends on A, retain the B -> A edge and the parameter/occurrence
attribution. If the selected resolution can use A's supplied reference, inject that exact object.

If the selected resolution cannot be satisfied, refuse that meld with a specific diagnostic naming
the consumer and provider. A path requiring fresh construction cannot silently construct A. A missing
or unusable reference cannot silently become None, lose its dependency edge, or use an arbitrary instance.
The owner explicitly accepts resolution invalidation/refusal through Melder's existing structures.

Candidate representation, not selected field/API:
- Keep an explicit construction policy on the registration and carry it into compiled resolution metadata.
  Conceptually this is construction_allowed=False for an existing supplied object.
- Keep current resolvability separate. That verdict depends on the selected plan, eligible reference,
  permissions and relevant scope. The construction restriction stays in force when availability changes.
- This is separate from contract Permissions; disabling construction of A must not by itself prohibit
  injecting A into a newly constructed B.

Proposed error content:
- Stable reason/code for failure to resolve an existing object, with the actual cause preserved.
- Requested root, immediate consumer, provider identity/binding and parameter or dependency path.
- Relevant conduit/scope and whether the failure is unavailable reference or construction-required resolution.
- Example: Cannot meld B: B.service requires A, but no eligible existing A is available in this scope.
  Construction is disabled for A.

Use the existing validation/Meld error families and diagnostic structures. The exact code, exception
subclass/payload and publication seam remain to be selected; MeldExecutionError does not currently have
a general code/details field. Do not invent that support in a report.

Refusal should affect the resolution context that is actually invalid. Existing global structural
validity, per-conduit spell/root verdicts and request-local conditions are not interchangeable.
Do not mark the definition globally invalid for a failure confined to a resolution scope. The exact
mapping to gated/invalid/runtime refusal and recovery belongs to the scoped execution design in Stage 3.
When the active path no longer requires A (for example a supported override replaces that edge), an
unrelated missing A must not produce this dependency failure; qualification must follow the actual plan.
Missing executable artifacts remain a distinct failure cause, not evidence that the live reference is gone.

## Supplied Application State: Proposal For Discussion

Owner asks how Melder could know an incoming object's intended base state and proposes leaving that
to the user: map the supplied object and use it. This is a proposed boundary, not an implemented rule
or a final decision on all lifecycle behavior.

- Treat the supplied instance's current application state as the user's selected baseline. The user
  is responsible for constructing/configuring it for use; binding does not reset or normalize that state.
- Study the reference/type and validate the advertised binding contract without claiming to know the
  application's intended values, readiness or hidden invariants. Any additional required facts must be explicit.
- Keep Melder's own registration, construction policy, scope eligibility, ownership and release state
  separate from the object's application state. A retained reference does not prove application health.
- Preserve the known B -> A edge when Melder injects A into B. A constructor annotation on A does not
  establish what its already-created instance currently holds or make those internals managed dependencies.
- Transfer carries the same reference in its current state under the chosen ownership contract.
  Binding/transfer does not promise a snapshot, reset, deep copy or restoration of earlier application state.
- The dedicated resolution error must describe failures Melder can establish, such as missing reference,
  inaccessible scope or required-but-forbidden construction. It cannot diagnose arbitrary object health
  without a declared mechanism for doing so.

## Verified Error And Validity Seams

- Spell currently derives is_existing_creation from its SpellType, independently of value presence.
- MeldExecutionError retains spell_id/spell_name, node_id, param_name and inner; its renderer includes them.
- SpellValidationIssue has code/message/details, and SystemDiagnostic adds spell_id/root_id/source.
  SpellbookValidationError renders available Phase-4/6 diagnostics and their details.
- Meld._ensure_lineage_resolvable separates structural checks from conduit-local resolution checks.
- Meld._get_resolution_validity selects root versus spell validity within the conduit state.
- ConduitResolutionState publishes spell/root verdicts independently and records changed-state dirtiness.
- Current existing-object executor failures are generic RuntimeErrors naming user_created_object/spell_id;
  these closures do not themselves add consumer/parameter context.

Evidence:
- src/melder/aether/spellbook/spell.py:384-412
- src/melder/aether/spellbook/spell.py:955-979
- src/melder/utilities/custom_exceptions/meld_execution_error.py:90-185
- src/melder/utilities/custom_exceptions/spellbook_validation_error.py:78-287
- src/melder/aether/spellbook/spell_compiler/validation/spell_validation_issue.py:57-95
- src/melder/aether/spellbook/spell_compiler/system/system_diagnostic.py:48-90
- src/melder/aether/conduit/meld/meld.py:596-642
- src/melder/aether/conduit/meld/meld.py:760-961
- src/melder/aether/conduit/meld/meld.py:1052-1075
- src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:271-325
- src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:427-483
- src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:155-234

## Required Reread Order
After the required ContextCompass re-onboarding, use this order for this task:
1. Parent story: Owner Intent, Current Checkpoint and Stage 1 in the staged sequence.
2. This task: Objective, Scope Boundaries, latest Notes and Context / Handoff Summary.
3. Initial discovery artifact: Current registration and execution boundary, plus source/identity observations.
   Existing results are evidence to reuse; do not rerun all nine probes merely because context compacted.
4. Relevant src_components slices through its verified index: Binding Pipeline and Spellbook Core.
   Use the graph index for the exact nodes when wiring detail is needed; then read the relevant source.
5. Read a later-stage source only if a concrete representation question depends on it; record why.

## Source Entry Points
The initial trace identifies these entrypoints. Read the current implementations before relying on them.
- src/melder/aether/spellbook/bind/bind.py: Bind._bind_logic, sha256_profile, _validate_binding,
  _determine_spell_type.
- src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:
  build_profile, _build_class_profile, _build_instance_profile.
- src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.py:
  ClassBindingProfile, InstanceBindingProfile and their retained-reference contracts.
- src/melder/aether/spellbook/spell.py: __init__, family flags, has_existing_object, cleanup.
- src/melder/aether/spellbook/spell_types/spell_types.py: classification vocabulary.
- src/melder/aether/spellbook/resolution_style_matrix.py: binding-family policy.
- src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:
  build_requirements, only to verify how the chosen distinction protects constructor opacity.

## Evidence To Carry Forward
- tickets/tasks/2026-09-17_trace_existing_object_reference_model_task.md: original investigation record.
- artifacts/existing_object_discovery_20260917/discovery.md: source map, observations and broader candidate options.
- artifacts/existing_object_discovery_20260917/reference_transitions.log: transfer and staging outcomes.
- artifacts/existing_object_discovery_20260917/reference_crystals.log: source availability and fingerprint outcomes.

## Validation
No new tests run. Read existing error/validity source contracts for the owner's dependency-failure question.
Earlier nine observations remain in the initial trace task; they are not acceptance of a new representation.

## Risks / Rollback Notes
- Inspecting an object's type must not silently turn the instance into a factory registration.
- A constructor description can be useful metadata without being executable DI requirements.
- A fingerprint is not proof of Python object identity; preserve the recorded equal-repr control.
- Do not select a new flag, enum or wrapper solely from its name; map existing readers before recommending it.
- No production edits in this stage, so there is no runtime rollback to perform.

## Applicable Anti-Patterns
- [ ] Do not replace supplied-instance design with definition-first external-supply design.
- [ ] Do not repeat the initial broad source/probe sweep after every compaction.
- [ ] Do not implement a representation while its construction and reference-ownership semantics are unknown.
- [ ] Do not start storage, transfer or persistence implementation from this design-only task.

## Done Checklist
- [ ] Comparison and proposed distinction are evidenced.
- [ ] Required owner decisions are recorded and resolved or left explicitly pending.
- [ ] Validation status is accurate.
- [ ] Story checkpoint and attention-board route reflect the next single step.
- [ ] Owner acceptance recorded before ticket closure.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none produced; prior evidence is referenced above and remains owned by the initial trace task.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: use the explicit reread order and source entrypoints above; record the remaining question.

## Noting Behavior
Keep findings and the next single source/design action here. The story owns the overall stage sequence;
do not copy that sequence into this task. Update the checkpoint when the current stage changes.

## Notes
- DATETIME: 2026-09-17T22:21:43Z
  TYPE: DECISION
  CLAIM: Owner clarified the basic target as an existing object bound by the user, studied through its
    reference, handled like a normal object with creation disabled, and carried through ownership transfer.
    Owner asks for a durable stepwise continuation plan because this work will span many compactions.
  EVIDENCE:
  - Owner's latest two messages in this task, recorded in the parent story's Owner Intent section.
  - tickets/stories/2026-09-17_existing_object_reference_blueprint_discovery_story.md
  IMPACT: Stage 1 designs bind representation only. The broader initial discovery remains useful evidence;
    definition-first supply and downstream lifecycle work do not displace the current input case.
  NEXT: Compare Bind._bind_logic and BindingProfileStrategy's class/instance paths to draft the metadata reuse table.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T23:08:39Z
  TYPE: FACT
  CLAIM: Existing validity/error mechanisms already distinguish structural and per-conduit root/spell
    resolution verdicts and carry diagnostic attribution. Existing-instance executor closures return
    the reference or raise generic missing-object RuntimeError without their own consumer/parameter context.
    Owner requires a specific dependency-aware refusal when the existing object cannot satisfy resolution.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:596-642
  - src/melder/aether/conduit/meld/meld.py:834-961
  - src/melder/aether/conduit/meld/meld.py:1052-1075
  - src/melder/utilities/custom_exceptions/meld_execution_error.py:90-185
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:155-234
  - Owner request for a special error identifying the dependent object and permitting resolution invalidation.
  IMPACT: Proposed bind metadata must preserve a construction prohibition independently of resolution
    validity and retain incoming dependency context. Exact flag/error schema and scope verdict mapping
    remain design choices; no runtime patch or new test execution occurred.
  NEXT: Compare class/instance metadata and propose the construction-policy placement within normal representation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T23:14:23Z
  TYPE: HYPOTHESIS
  CLAIM: Owner raises the unknown intended base state of a supplied object and suggests mapping/using
    what the user supplies. Recommended boundary: the current application state is user-selected,
    while Melder manages explicit registration/resolution/ownership facts and declared contract validation.
  EVIDENCE:
  - Owner's current base-state question and tentative map-and-use proposal in this conversation.
  IMPACT: Do not infer object readiness, hidden configuration or managed internal dependencies from type
    inspection alone. Preserve incoming injection edges and exact reference identity; this is a design
    proposal, with no new source investigation, test execution or runtime implementation in this turn.
  NEXT: Discuss the supplied-state boundary, then carry the chosen rule into the bind metadata comparison.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
CURRENT STAGE: 1, bind representation. STATUS: in_progress; design/source reads only, no implementation.
TARGET: user binds an existing instance; reuse normal object machinery with an explicit construction prohibition.
DEPENDENCY CONTRACT: preserve B -> A, inject eligible supplied A, or refuse the affected resolution with
consumer/provider/path context. Construction policy and resolution validity are distinct; see the source-backed section.
CURRENT DISCUSSION: user-selected application state versus Melder's explicit registration/lifecycle state;
see Supplied Application State. Do not claim that a live reference proves application readiness.
NEXT SINGLE STEP: settle that boundary, then finish the bind metadata comparison and construction-policy placement.
Read the parent story checkpoint and this task's reread order. Keep the initial nine probe outcomes as baseline.
