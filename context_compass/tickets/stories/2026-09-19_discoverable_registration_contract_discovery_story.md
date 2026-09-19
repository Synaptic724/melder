# Story: Settle discoverable registration and supplied-input semantics

## Metadata
- Story ID: STORY-2026-09-19-discoverable-registration-contract-discovery
- Epic: EPIC-2026-09-19-discoverable-non-resolvable-registrations
- Status: review
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T16:34:27Z
- Updated: 2026-09-19T19:25:38Z

## User Narrative
As the owner, I want to settle how a registered definition stays visible and versioned while being
unresolvable, so we can reuse Melder's machinery without losing graph information or weakening inputs.

## Value / MRP Alignment
Resolve registration, selection, and graph semantics before committing to an API or compiler patch.
The result must explain where existing machinery fits and where it needs an explicit new contract.

## Ticket Contract
- ENTRY_GATE: Parent epic and this story are read; the active child task is routed from attention_board.
- EXECUTION_BOUNDARY: Read-only source investigation, semantic tables, and proposed regression cases.
  No production edits, test-file creation, or feature release is part of this discovery story.
- DEPENDENCIES: Parent source read map and predecessor orientation/PLAIN findings.
- EXIT_GATE: Owner accepts a source-grounded decision record for mode ownership, target matching,
  supplied inputs, graph metadata and version/restore requirements; later stories can be scoped from it.
- FAILURE_ESCALATION: Keep competing designs explicit when code cannot decide the product contract.
  Do not widen into instance-ownership redesign or replace existing identity/cache models by assumption.

## Requirements (Functional)
- Define supported registration targets and the difference between descriptive role and resolution mode.
- Locate the canonical owner of the mode and determine how callers, metadata, and fingerprints carry it.
- Explain direct target lookup versus abstract spellframe implementation matching with concrete cases.
- Specify required/defaulted/Optional/collection/SpellMap/SpellContract combinations without guessing.
- Define an explicit resolved caller-supplied category that keeps the target and declaration metadata.
- Keep ordinary PLAIN/default semantics intact; do not mutate Phase-1 classifications in place.
- Identify where discovery-only roots leave construction scheduling and where required inputs are checked.
- Map the accepted mode through source custody, research versions, cache keys and restore/graft.

## Requirements (Non-Functional)
- Preserve existing registration/override behavior when the mode is absent.
- Reuse current subsystems and invariants where they fit; record evidence for every claimed reuse.
- Keep application definitions free of mandatory framework inheritance or decorators.
- Capture durable pointers so discovery can resume without replaying the whole conversation.

## Scope Boundaries
- In scope: exact registration/compiler boundary first; trace downstream consumers only as needed.
- Out of scope: implementing the epic, blanket type-checking changes, new lifetimes, live instance migration.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Four source traces and concrete recommendations are recorded; owner chose category and version rules.

## Dependencies / Related Work
- Parent: `tickets/epics/2026-09-19_discoverable_non_resolvable_registrations_epic.md`
- Predecessor: `tickets/tasks/2026-09-19_understand_nexus_crystallizer_spellbook_task.md`
- Required task: `tickets/tasks/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md`
- Socket proposal: `tickets/tasks/2026-09-19_define_caller_supplied_socket_contract_task.md`
- Selection result: `tickets/tasks/2026-09-19_define_discoverable_registration_selection_task.md`
- Admission/identity result: `tickets/tasks/2026-09-19_define_non_resolvable_admission_identity_task.md`
- S2 successor: `tickets/tasks/2026-09-19_implement_resolvable_registration_modifier_task.md`

## Required Reading Before Work
1. Parent epic's current direction, story dependency map and remaining identity/graph questions.
2. The first trace task's latest strategy note and handoff; older PLAIN recommendations are superseded.
3. `system_docs/src_architecture_index.md` and `system_docs/src_components_index.md` after required onboarding.
   Read Binding Pipeline, DI Descriptors and Contract Sockets, SpellCompiler and Validation Pipeline,
   and Meld Resolution Runtime slices. Verify source graph-index ranges for the exact code being traced.
4. Registration context, as needed to settle still-open compatibility questions:
   - `src/melder/aether/spellbook/bind/bind.py` — explicit parameters, SHA inputs, admission.
   - `src/melder/aether/spellbook/spell.py` — per-version policy and compiler artifacts.
   - `src/melder/aether/spellbook/bind/spell_index.py` — selection versus capability.
5. Resolved-input contract and requiredness:
   - `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_parameter_requirements.py`
   - `src/melder/aether/spellbook/spell_compiler/symbolic_graph/spell_symbolic_dependency.py`
   - `src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py`
   - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py`
   - `src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py`
   - `src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py`
   Follow the next task's exact analyzer/model/planner/override read map for propagation.
6. Version identity before final S1 approval:
   - `src/melder/crystallizer/crystals/spell_crystal.py`
   - `src/melder/mutation_research/mutation_research.py` — source material and record_world_entry.
   - `src/melder/mutation_research/research_set/research_node.py`
   Distinguish the structural bind SHA from body-only source and relationship revisions.
7. Before test authoring, read test architecture/components and the relevant cases identified in S2-S7.

## Tasks (Implementation Checklist)
- [ ] TASK-2026-09-19-trace-discoverable-registration-compiler-boundary — first bounded source trace.
- [ ] TASK-2026-09-19-define-caller-supplied-socket-contract — name/meaning accepted; source proposal retained.
- [ ] TASK-2026-09-19-define-discoverable-registration-selection — table ready for review.
- [ ] TASK-2026-09-19-define-non-resolvable-admission-identity — results and owner version decision recorded.
- [ ] Add another scoped discovery task only if unresolved graph/persistence decisions need it.
- [ ] Record meaningful findings after each completed source unit, before continuing.
- [ ] Produce the accepted contract and minimum regression scenarios for subsequent implementation stories.

## Acceptance Criteria
- The decision table distinguishes direct unresolvable registration from resolvable spellframe providers.
- A required supplied input remains required; defaults retain precedence; omission differs from explicit None.
- The proposed graph retains target relationships without turning them into construction dependencies.
- Mode identity, candidate selection, compiler admission, cache, and restore owners are identified in source.
- Open decisions are explicitly presented; no unknown branch is described as already supported.
- Implementation scope and the necessary initial failing tests can be derived from the accepted result.

## Validation / Test Plan
- Tests: Not run. This story specifies future tests; it does not claim current feature support.
- Start with an abstract Base, a concrete internal Helper, and a Consumer requiring Base.
- Add one resolvable implementation registered under Base as a spellframe to expose selection ambiguity.
- Follow with a defaulted input and one nested consumer to separate required-input and override behavior.
- Record observed/source-backed behavior separately from proposed expected results.

## UX / API / Data Notes
- Public modifier: resolvable: bool = True. Owner-selected internal category: OVERRIDE_REQUIRED.
- Proposed errors should explain target non-resolution or the consumer's missing supplied input.
- Nexus graph access and runtime resolution must remain distinguishable to tools and agents.

## Risks / Mitigations
- Flagging an annotation instead of a selected registration can block normal implementation injection.
- Treating PLAIN as the entire feature can drop graph edges and produce generic Python errors.
- Treating registration as always constructible can make an abstract/helper entry break conjure.
- Treating a metadata toggle as harmless can create identity/cache/restore disagreements.

## Applicable Anti-Patterns
- [ ] No production patch before the contract is settled.
- [ ] No claim of full override-path support from the inspected solo helper alone.
- [ ] No unrecorded scope expansion or revived backlog design.

## Open Questions
Use the parent epic's Open Questions as the program list. This story starts with mode ownership,
target matching, and socket metadata; it does not attempt every downstream detail in one pass.

## Decision Log
- 2026-09-19: First slice is discovery. Reuse registration with resolvable=True by default.
- 2026-09-19: Plan a distinct resolved caller-supplied category, superseding the original PLAIN proposal.
- Connected/versioned Nexus graph behavior is a requirement, not optional documentation work.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none until the story produces a separate artifact.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: mode ownership, selected target, supplied input, descriptive graph.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-19T16:34:27Z
  TYPE: PLAN
  CLAIM: Start at the registration-to-socket boundary, using the predecessor's verified PLAIN facts.
    Later graph/persistence work packages remain unstarted until this story resolves the shared model.
  EVIDENCE:
  - tickets/tasks/2026-09-19_understand_nexus_crystallizer_spellbook_task.md:407-478
  IMPACT: One concrete decision unit leads discovery instead of reopening every subsystem at once.
  NEXT: Execute the first source-trace task and record its mode/matching decision table.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-19T17:01:48Z
  TYPE: FACT
  CLAIM: The first task has a review-ready modifier design: bool default True at both Spellbook
    entry points and Conduit facades, stored per Spell with identity/inspection consistency.
    It also traced Phase-3 matching, Phase-4 declaration-based cycles and concrete meld fast doors.
    Exact resolved-socket metadata and descriptor/collection policy remain open; no code was changed.
  EVIDENCE:
  - tickets/tasks/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md:74-162
  - tickets/tasks/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md:207-354
  IMPACT: The API/storage direction is small and concrete; the next discovery decision is how
    resolved caller-supplied policy reaches validation and Nexus without private shape mutation.
  NEXT: Discuss the task result and settle that one socket-policy boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T17:45:45Z
  TYPE: PLAN
  CLAIM: Full implementation stories S2-S7 and their reading requirements are staged. Continue S1
    through the new ready caller-supplied contract task rather than repeating the completed source trace.
  EVIDENCE:
  - tickets/tasks/2026-09-19_define_caller_supplied_socket_contract_task.md:13-85
  IMPACT: Resolved input semantics are the next bounded design decision; implementation remains unstarted.
  NEXT: Read required_holes_strategy.py and trace the resolved socket through its immediate consumers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-19T18:36:34Z
  TYPE: FACT
  CLAIM: The resolved-input discovery task is ready for review with a concrete schema and regression
    design. Recommend CALLER_SUPPLIED in the existing socket vocabulary, separate descriptive IDs,
    explicit requiredness and propagation through injection/plan/compiled execution. Phase 5 already
    preserves no-edge override sockets; Phase 4, Phase 8 and solo executors need explicit adaptation.
    The proposal is not an implemented or owner-accepted contract. Matching, descriptors/collections
    and version identity remain S1 decisions; S3/S4 now link the propagation findings.
  EVIDENCE:
  - tickets/tasks/2026-09-19_define_caller_supplied_socket_contract_task.md:89-215
  IMPACT: The compiler boundary is concrete enough to review without committing to a PLAIN workaround.
  NEXT: Discuss the proposed socket contract, then settle provider-versus-definition selection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:45:34Z
  TYPE: DECISION
  CLAIM: Owner selected OVERRIDE_REQUIRED and accepted the explained required-override meaning.
    Continue with the bounded selection task: root lookup, implicit annotation matching, explicit
    descriptor selection and collections, preserving inactive-version and uniqueness constraints.
  EVIDENCE:
  - tickets/tasks/2026-09-19_define_caller_supplied_socket_contract_task.md:89-116
  IMPACT: S1 no longer treats category spelling as open. No new lifetime or instance ownership is implied.
  NEXT: Execute tickets/tasks/2026-09-19_define_discoverable_registration_selection_task.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T19:05:38Z
  TYPE: FACT
  CLAIM: Selection source trace and recommendations are recorded: preserve exact root lookup,
    candidate-based annotation selection, explicit descriptor cardinality, active/parked separation
    and binding uniqueness. Required collections keep their empty behavior. The next independent
    admission/identity investigation begins while these detailed policies remain reviewable.
  EVIDENCE:
  - tickets/tasks/2026-09-19_define_discoverable_registration_selection_task.md:84-210
  IMPACT: OVERRIDE_REQUIRED has a concrete selection boundary; admission and version identities remain open.
  NEXT: Trace Bind admission and fingerprint inputs in the new task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T19:25:38Z
  TYPE: DECISION
  CLAIM: Owner chose existing version rules after the source identity trace. Keep structural binding
    IDs and research/custody identity behavior; no automatic body hashing. Admission/fingerprint
    recommendations are ready, including False discrimination and current valid target-family rules.
    S2 registration work is staged; S1 remains review, not closed, with all evidence preserved.
  EVIDENCE:
  - tickets/tasks/2026-09-19_define_non_resolvable_admission_identity_task.md:77-174
  IMPACT: The next work is implementation preparation instead of another open-ended identity investigation.
  NEXT: Prepare S2 patch contracts and registration regressions in the successor task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Findings discussed with owner.
- [ ] Semantic decision record accepted.
- [ ] Task and board state synchronized.

## Noting Behavior
- Synthesize child-task findings; keep detailed source traces in the task.
- Preserve decisions and unresolved branches with evidence and one next action.

## Context / Handoff Summary
Four source traces are in review: registration, sockets, selection, and admission/identity. Owner
selected OVERRIDE_REQUIRED and existing version rules. S2 successor is ready for patch contracts and
regressions. Read the current result sections in those tasks; no new body-only identity, lifetime,
or ownership model. No runtime feature or new executable tests have been written in discovery.
