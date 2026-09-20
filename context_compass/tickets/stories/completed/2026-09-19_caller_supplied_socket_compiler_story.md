# Story: Compile explicit caller-supplied dependencies without construction edges

## Completion
- Completed: 2026-09-20T00:25:59Z
- Summary: Delivered OVERRIDE_REQUIRED reference metadata without construction edges and preserved normal provider/default semantics.
- Acceptance: Owner requested turn-in, then required two repairs first; both are verified.

## Metadata
- Story ID: STORY-2026-09-19-caller-supplied-socket-compiler
- Epic: EPIC-2026-09-19-discoverable-non-resolvable-registrations
- Sequence: S3
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T17:25:45Z
- Updated: 2026-09-20T00:25:59Z

## User Narrative
As a user, I can declare a required input whose registered target is non-resolvable, and Melder
keeps its graph relationship while compiling an explicit requirement for caller supply.

## Value / MRP Alignment
Give validation, graph publication and execution the same resolved meaning without corrupting signatures.

## Ticket Contract
- ENTRY_GATE: S1 resolves category/schema semantics; S2 exposes per-Spell mode; implementation task
  and system-impacting patch contracts exist.
- EXECUTION_BOUNDARY: Signature-to-resolved-socket flow, target selection, structural validation,
  executable root eligibility, and handoff into analyzer/model/planner.
- DEPENDENCIES: S1 and S2. Publish a stable resolved input contract to S4, S5 and S6.
- EXIT_GATE: Compiler tests prove correct classification, preserved graph targets and no executable
  dependency on discovery-only targets, including pre/post-conjure paths.
- FAILURE_ESCALATION: Stop on ambiguous matching/default/collection rules; do not mutate private phase fields.

## Requirements (Functional)
- Preserve Phase-1 declaration/default facts and Phase-2 symbolic annotation information.
- Introduce the explicit caller-supplied category in the resolved socket model chosen by S1.
- Phase 3 distinguishes real provider matches from discovery-only definition matches.
- Preserve ordinary provider ambiguity and missing-target rules; a discoverable frame definition must
  not displace a separate resolvable implementation.
- Caller-supplied sockets retain their registered target/version, type and required/default policy.
- Keep descriptive relationships separate from executable DAG edges and construction cycles.
- Make Phase-4 validation consume resolved input policy instead of reconstructing false injection edges.
- Do not demand construction dependencies or codegen plans for non-resolvable roots.
- Preserve enough declaration/relationship data to inspect those roots in Nexus.
- Carry the category through Phase 5 and phase-8/9/10 artifacts for S4 execution and S5 graph publication.
- Preserve ordinary PLAIN and real SpellContract semantics; neither is renamed or repurposed.

## Requirements (Non-Functional)
- One authoritative resolved result; avoid scattered booleans disagreeing across compiler phases.
- No private _di_shape mutation, fake defaults, blanket annotation-wide policy, or optionality guesswork.
- Preserve transactional pass caches and phase barriers; no new global caching service.

## Scope Boundaries
- In scope: selected-target semantics, compiler artifacts, validation, graph/plan admission and tests.
- Out of scope: actual override execution, public Nexus commands, durable storage, instance ownership.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner-authorized turn-in after delivered scope and reported failure repairs passed.

## Dependencies / Related Work
- Parent: `tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md`
- S1: `tickets/stories/completed/2026-09-19_discoverable_registration_contract_discovery_story.md`
- S2: `tickets/stories/completed/2026-09-19_discoverable_registration_modifier_story.md`
- Next: `tickets/stories/completed/2026-09-19_discoverable_resolution_runtime_story.md`

## Required Reading Before Work
1. Parent epic, S1 resolved-socket decision, S2 mode/identity contract and predecessor trace notes.
   Read the proposed schema and propagation map in:
   `tickets/tasks/completed/2026-09-19_define_caller_supplied_socket_contract_task.md`.
   It is a review proposal until S1 records acceptance.
   The owner selected OVERRIDE_REQUIRED. Also read the selector table in
   `tickets/tasks/completed/2026-09-19_define_discoverable_registration_selection_task.md`; root lookup,
   annotations, explicit descriptors and collections have different selection contracts.
2. Verify `system_docs/src_components_index.md`; read DI Descriptors and Contract Sockets,
   SpellCompiler and Validation Pipeline, and the Parameter DI Shape Classification subcomponent.
3. Verify `system_docs/src_graph_index.md` and read wiring slices for each changed source owner.
4. Read declaration and resolved-record owners in full:
   - `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py`
   - `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_parameter_requirements.py`
   - `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements.py`
   - `src/melder/aether/spellbook/spell_compiler/symbolic_graph/spell_symbolic_dependency.py`
   - `src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py`
   - `src/melder/aether/spellbook/spell_compiler/dag/socket_kind.py`
5. Trace the actual compiler consumers, reading complete relevant methods and their direct callees:
   - `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py`
   - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py`
   - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py`
   - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py`
   - `src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py`
   - `src/melder/aether/spellbook/spellbook_creation_system.py`
   - `src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py`
   - `src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py`
   - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py`
   - `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py`
   - `src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py`
   - `src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py`
6. Before tests, read test architecture/components via indexes and relevant compiler fixtures:
   - `tests/component/melder/spellbook/test_spellbook_component_spell.py`
   - `tests/component/melder/spellbook/spell_crafter/topology/test_spellbook_component_spell_local_topology.py`
   - `tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_binding_resolution_cycle_strategy.py`
   - `tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_required_holes_strategy.py`
   - `tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py`


## S2 Implementation Handoff
S2 supplies the native read-only Spell.resolvable bool through active/inactive binding; default True
retains legacy identities, False uses v4-binding-non-resolvable. 42 new cases and 1845 focused tests
pass. Read the implementation task before opening the S3 compiler patch:
`tickets/tasks/completed/2026-09-19_implement_resolvable_registration_modifier_task.md`.
S3 now consumes that bool through resolved topology, compiler validation and root eligibility.
Runtime enforcement is still S4 work. Continue the per-story source/graph reads; do not treat S2/S3
tests as proof that every execution door enforces the capability or required supplied values.

## Tasks (Implementation Checklist)
- [x] Execute
  `tickets/tasks/completed/2026-09-19_implement_override_required_compiler_task.md`.
- [x] Create the compiler task and map S1 schema to patch/source/validation sections.
- [x] Add regressions for required/defaulted input, matching alternatives and preserved targets.
- [x] Implement resolved category and make structural/cycle/required-hole validation agree.
- [x] Exclude discovery-only construction roots while retaining descriptive metadata.
- [x] Carry resolved policy through occurrence/model/planner and publish the S4/S5/S6 contract.

## Acceptance Criteria
- Required external inputs compile as caller-supplied; registered targets remain navigable in metadata.
- No executable edge or construction plan is produced for a discovery-only target.
- A False root with unregistered constructor dependencies does not invalidate runnable consumers.
- Cycles made only of descriptive references are not mistaken for construction cycles.
- Default/Optional/descriptor/collection cases follow the accepted S1 table, with unsupported cases explicit.
- Pre/post-conjure and target-local revalidation agree and preserve provider artifact ownership.

## Validation / Test Plan
- 2098 distinct focused tests pass, including all 42 new compiler component cases. The two final
  XML reports have no overlapping case keys. See the child task's validation artifact for exact scope.
- Source/LLM assets regenerated and pass freshness checks; scoped lint, whitespace and indexes pass.
- Real direct-consumer notch/new-provider transitions pass through existing revalidation machinery.
- Full repository suite/coverage and full nested runtime/cache matrices: Not run. Execution-specific
  enforcement remains S4; compiler metadata alone does not prove runtime safety.

## UX / API / Data Notes
The owner-selected internal category is OVERRIDE_REQUIRED. Public callers use resolvable and overrides.

## Risks / Mitigations
Phase-4 declaration-based cycles and Phase-5 executable roots are separate consumers; trace both.

## Applicable Anti-Patterns
- [x] No forced PLAIN conversion or mutation of read-only declaration records.
- [x] No lost target edge, accidental executable cycle, or eager construction requirement.
- [x] No runtime-safety claim for metadata awaiting S4 execution enforcement.

## Open Questions
S3 schema and selection policy are implemented. S4 still owns supplied-value validation and execution
ordering; S5/S6 own public graph and durable schemas. These remain separate acceptance obligations.

## Decision Log
- Dedicated resolved caller-supplied meaning; original signature and ordinary PLAIN remain intact.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: accepted story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: declaration versus resolved input, target matching, validation and plan admission.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-19T17:25:45Z
  TYPE: PLAN
  CLAIM: Stage compiler semantics separately from runtime execution to keep its data contract explicit.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:126-898
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:173-279
  IMPACT: S4/S5/S6 consume one resolved interpretation instead of inferring from PLAIN or annotation alone.
  NEXT: Read the accepted S1 resolved-socket contract and open the compiler implementation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:36:34Z
  TYPE: PLAN
  CLAIM: S1's new source trace proposes CALLER_SUPPLIED, separate descriptive reference IDs and
    requiredness on resolved topology, plus explicit supplied injection rows. Phase 4 reconstructs
    declaration-based facts; Phase 8 expands every target ID; Phase 9 omits non-dependency inputs.
    Phase 5 already emits no-edge SocketRefs. Preserve both lane variants' required-input metadata.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_define_caller_supplied_socket_contract_task.md:89-215
  IMPACT: S3 has a concrete schema review input and known propagation gaps; implementation is unstarted.
  NEXT: Consume S1's accepted schema and finish all changed-source/graph reads before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:38:40Z
  TYPE: FACT
  CLAIM: S3 is review-ready with OVERRIDE_REQUIRED local topology, descriptive references, executable
    root exclusion, Phase-4/8 contract capability checks and required-input transport through both
    planner families/variants and injection exports. The existing selector watcher and Meld validity
    handoff now rebuild changed direct-consumer plans. 2098 focused tests and final asset checks pass.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_implement_override_required_compiler_task.md
  - artifacts/override_required_compiler_20260919/validation.md:1-72
  IMPACT: S4 has a concrete compiler contract to enforce; S5/S6 have reference metadata to publish
    and preserve. This advances compiler delivery without claiming the complete feature is safe to ship.
  NEXT: Open the first S4 runtime task and consume the delivered required_override_params schema.
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

## Closure Confirmation
- [x] Owner accepts compiler behavior and evidence.
- [x] Child tasks, artifacts and boards synchronized.

## Noting Behavior
Record shared compiler schema and cross-task decisions here; detailed traces belong in tasks.

## Context / Handoff Summary
CLOSED at 2026-09-20T00:25:59Z. Delivered OVERRIDE_REQUIRED reference metadata without construction edges and preserved normal provider/default semantics.
Final evidence and limits are in the graph/replay and follow-up validation artifacts.
No next implementation step remains in this accepted record.

### Historical pre-closure handoff
S3 is implemented and in review. Read its child task and validation artifact for exact changes,
2098 distinct passing cases, generated assets and remaining limits. Original declarations/defaults
remain unchanged; local topology owns descriptive references separately from executable targets.

Both planner variants retain required_override_params rows: (name, position, parameter-kind name,
reference-ID tuple). S4 must carry these through live CodegenCreationSchemaHelpers and emitted/cached
execution before claiming required-value safety. S5 must publish the connected descriptive graph;
S6 must persist/replay policy and relationships. Existing version rules and object ownership remain.
