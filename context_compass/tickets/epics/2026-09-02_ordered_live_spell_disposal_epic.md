# Epic: Ordered live spell disposal

## Metadata
- Epic ID: EPIC-2026-09-02-ordered-live-spell-disposal
- Status: review
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-03T01:05:17Z
- Updated: 2026-09-05T13:21:33Z
- Target Window: 2026-Q3
- Related Program/Initiative: Melder public lifecycle contract

## Problem / Opportunity
Melder accepts an ordered `disposal_method_names` list, and its configuration API
explicitly promises order-preserving additions. The current bind path converts that
sequence into `frozenset` values at the Spellbook, Bind, and Spell boundaries. Runtime
registration then copies the unordered value into a new list, while persistence sorts it.
The declared order therefore does not survive to execution or restore.

Current configuration-to-Spell mechanics are recorded in the Phase 1 task. The owner
has now selected list storage and composition of book and explicit per-spell names.
enforce_priority_disposal_methods defaults to False (book block last); True puts that
block first. Shared names belong to the book block in BOTH modes, in configuration order.
Each group's supplied order is preserved and the resolved list is built once per new
Spell. Downstream execution and persistence follow in separate phases.

## MRP Alignment (Most Reasonable Product)
Lifecycle policy must be deterministic before public release. An ordered, spell-owned
cleanup chain aligns configuration, fingerprints, compiled paths, runtime disposal, and
restore without adding a new abstraction or weakening reverse dependency teardown.

## Ticket Contract
- ENTRY_GATE: The selected implementation task is linked/routed; its prerequisites and
  patch-consumption gates are satisfied before execution.
- EXECUTION_BOUNDARY: Disposal configuration, binding, Spell metadata, compiled creation
  lanes, Creations registration/execution, persistence/restore, documentation, assets,
  and focused tests.
- DEPENDENCIES: Source-backed current-state contact map, owner-approved correction,
  and patch-framework artifacts before implementation.
- EXIT_GATE: Supplied method order survives binding, runtime disposal, and persistence;
  the three phases are verified and the owner accepts the result.
- FAILURE_ESCALATION: Record any consumer that cannot preserve the agreed ordered list;
  retain the existing failure and duplicate-suppression behavior during this change.

## Goals (Outcomes)
- Trace the current configuration-to-Spell implementation without inference.
- Identify the exact method-existence check and absent-method behavior.
- Trace every current consumer through compiler, Creations, cleanup, and persistence.
- Identify precisely where configured/per-spell order is currently lost.
- Present the smallest Synaptic-compliant correction for owner approval.
- Preserve existing reverse creation order between objects and scopes.

## Non-Goals (Explicit Exclusions)
- Redesigning the overall Conduit cleanup cascade.
- Introducing a disposal protocol, new interface hierarchy, or immutable value object.
- Adding speculative snapshot, mutation, re-identification, or cache policy.
- Adding new `getattr`/`hasattr` probing or defensive ownership guards.
- Expanding disposal matching beyond the current class-profile behavior into
  existing-object or callable/factory spell families.
- Refactoring unrelated compiler or crystallizer behavior.

## Scope Boundaries
- In scope:
  - configuration vocabulary and bind convenience behavior
  - ordered per-spell method matching and ownership
  - compiled registration lanes and runtime Creations entries
  - fingerprint/cache/crystal/graft/restore propagation
  - behavioral tests and public lifecycle documentation
- Out of scope:
  - unrelated object cleanup implementations
  - broad formatting or naming changes
  - commits, pushes, releases, or publication

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: All implementation phases, documentation/assets, and final Windows CI
  runtime verification are complete; owner acceptance precedes closure and artifact disposition.

## Success Metrics
- Every current contact is classified by source-backed responsibility.
- The existence check and missing-name behavior are stated exactly.
- Spellbook-level and per-bind inputs are distinguished without invented precedence.
- Consumption order and every current order-destroying transform are identified.
- No product edit starts from an unapproved representation or lifecycle assumption.

## Requirements (Functional + Non-Functional)
- Current behavior claims require complete source evidence for the owning method.
- Missing configured names must be traced to an explicit skip, error, or later failure.
- Proposed order behavior must preserve the user's supplied order end to end.
- Cleanup remains deterministic and best-effort across separate creations.
- No new hot-path locks, protocols, module globals, compatibility shims, or
  defensive snapshots.

## Constraints / Assumptions
- List storage and book-first/book-last composition are the current owner direction.
- Disposal metadata is established once per Spell; arbitrary internal mutation is out of scope.
- Existing method-failure behavior stops the current object's chain at the first error.
- Current executed scope includes configuration, Bind/Spell, and compiler/Creations propagation.
  Later implementation still follows its task-level entry gates.

## Dependencies / External References
- `context_compass/system_docs/src_components.md`
- `context_compass/system_docs/src_graph.md`
- `context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md`
- `context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/cleanup_and_disposal.md`

## Phased Work
The owner selected the following sequence on 2026-09-04. It supersedes earlier
whole-pipeline execution proposals while retaining their findings as reference.

1. Configuration, Bind, and Spell (active).
   - Combine both lists; enforce_priority_disposal_methods defaults False (book last)
     and puts the book block first when True. Book order owns shared names in both modes.
   - Match into one list, skipping absent names and retaining each name's first occurrence.
   - Spell owns the list; SHA consumes its order at the existing bind boundary.
   - Read consumer interfaces only to establish the values the next phases require.
   - Source discovery: `tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md`.
   - Start: `tickets/tasks/2026-09-04_ordered_disposal_patch_contract_task.md`.
2. Compiler and Creations.
   - Carry the resolved sequence through existing compiled registration paths.
   - Remove redundant disposal-list copies where the agreed ownership contract allows.
   - Verify method-call order, registration flags, and existing cleanup behavior.
3. Crystallizer, replay, and publication documentation.
   - Preserve order in recorded spell metadata and active/staged replay.
   - Cover restore and graft using the agreed input-selection semantics.
   - Update relevant docs, regenerate derived assets, and verify the complete contract.

Each phase records its concrete correction before implementation. Matching scope,
cleanup-failure policy, and private-attribute mutation defenses are not expanded.

## Milestones (Track Progress)
- [x] Phase 1: Configuration/Bind/Spell contract established and implemented (in review).
- [x] Phase 2: Compiler/Creations propagation and method invocation verified (in review).
- [x] Phase 3: Persistence/replay order, documentation, and generated assets verified (in review).

## Stories (Required to Complete)
- [ ] `tickets/stories/2026-09-04_ordered_disposal_binding_story.md`
- [ ] `tickets/stories/2026-09-04_ordered_disposal_runtime_story.md`
- [ ] `tickets/stories/2026-09-04_ordered_disposal_persistence_story.md`

## Tasks (Cross-Cutting or Epic-Level)
- Discovery reference (review): `tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md`.
- The nine new tasks below are specified and ready; prerequisite gates still control execution.
  Only the selected task belongs on the active route. Creating a ticket does not mean its
  implementation is complete or that its dependencies are already satisfied.

## Implementation Task Sequence

| Step | Task | Prerequisites |
| --- | --- | --- |
| 1 | `tickets/tasks/2026-09-04_ordered_disposal_patch_contract_task.md` | Current discovery/design |
| 2 | `tickets/tasks/2026-09-04_disposal_priority_configuration_task.md` | 1 |
| 3 | `tickets/tasks/2026-09-04_ordered_disposal_bind_and_spell_task.md` | 1, 2 |
| 4 | `tickets/tasks/2026-09-04_disposal_configuration_roundtrip_task.md` | 2 |
| 5 | `tickets/tasks/2026-09-04_ordered_disposal_compiler_propagation_task.md` | 1, 3 |
| 6 | `tickets/tasks/2026-09-04_ordered_disposal_creations_task.md` | 5 |
| 7 | `tickets/tasks/2026-09-04_ordered_disposal_crystal_replay_task.md` | 4, 6 |
| 8 | `tickets/tasks/2026-09-04_ordered_disposal_docs_assets_task.md` | 7 |
| 9 | `tickets/tasks/2026-09-04_ordered_disposal_end_to_end_validation_task.md` | 4, 6, 7, 8 |

Every child names its parent, exact source/test reading anchors, scope, acceptance,
validation plan, risks, and a single NEXT action. Reopen complete source before edits;
the anchors are navigation, and past contact-function reads do not imply full-file reads.

## Holistic Change Map - Source-Traced 2026-09-04

The configuration slice is the first deliverable, not the whole feature. The component
sections and source handoffs for this complete chain have now been read. Detailed evidence
is appended to the owning child tasks and the active patch-contract task.

| Boundary | Required change or verification | Existing design to preserve |
| --- | --- | --- |
| SpellbookConfiguration | Add False default, bool schema, fluent setter, and honest reload accounting. | Setup/freeze lifecycle; supplied configurations work before validation; explicit values win. |
| Spellbook -> Bind -> Spell | Replace first-bind shared candidates with both ordered inputs; match once; hash and retain one resolved list. | Existing class-profile matching, first-occurrence deduplication, and bind-time identity. |
| Processor -> planner -> executors | Remove actual live-name copies; keep direct-reference arrays. | Solo/generalized/many-only algorithms, override lanes, store selection, and ordered schema/hash values. |
| Creations and transfer | Retain the established inner list at registration, extraction, and restoration. | Two registries, detach-before-dispose, reverse key/bucket traversal, and current failure posture. |
| Configuration transport / Nexus | Test generic bool/list transport, recorded reload, defaults, and shared configurations. | No duplicate property on Nexus/Crystallizer roots; no new carrier schema solely for the flag. |
| SpellCrystal / restore / graft | Remove capture sorting; forward names in staged, parked, and merged binds; verify recorded-ID joins. | Passive recording, public-verb replay, and explicit per-member shortfalls. |
| Tests / docs / assets | Add producer-to-actual-call tests and replay/cache cases; update verified descriptions and generated outputs. | Existing cleanup regressions, selective corpus regeneration, check-only CI, and unrelated agents' work. |

Why the boundaries matter:
- Configuration controls group priority; the resolved Spell list expresses that decision.
  Runtime cleanup therefore needs neither the flag nor another configuration/method match.
- Method order inside one object, reverse object/bucket traversal inside a store, and the
  inter-scope cleanup cascade are separate axes. This epic changes only the first.
- A tuple holding multiple Spell-list references is not a copy of each inner list. Likewise,
  ordered serialized/hash values are not live registry ownership. Do not rewrite all tuples.
- Spell cleanup deletes its disposal-name reference without clearing the collection.
  Keep that behavior when the list is also retained by live creation entries.
- Restore reloads configuration before binds. Same-policy replay must keep the resolved
  order unchanged when it is passed through the composition rule again.
- Recorded Spell SHAs are used for member/selection lookup in restore and graft. A different
  host's policy can alter the ordered result and its SHA. Test that case in the replay task;
  do not silently invent an ID translation or host-policy override during configuration work.
- Existing direct-Creations tests prove the invocation loop, not upstream preservation.
  They can stay green while Bind loses order, which is why end-to-end tests are necessary.

Read integrity: configuration, Creations, ConduitCreations, both solo compiler modules,
runtime record/processor, SpellbookCrystal, PersistenceCrystal, and GraftRunner were read
whole. Larger files were read through the relevant complete methods or metadata blocks;
this is not a claim to have read every large source file in the epic in full. Source
behavior, future design, and tests actually executed remain distinct.

## Acceptance Criteria (Epic Done)
- Current Spellbook-configured and per-bind mechanics are documented with source evidence.
- Missing configured names have an explicit documented outcome.
- The owner approves the exact representation and correction boundary.
- Cleanup executes each accepted method in supplied order and objects in reverse creation order.
- Fingerprint and persistence behavior are explicitly tested.
- Generated build assets and LLM support corpora are current.
- Owner reviews and accepts the behavior before closure.

## Risks / Mitigations
- Risk: Existing implementation details are mistaken for desired architecture.
  Mitigation: Separate current source fact from proposed correction in every note.
- Risk: Duplicate names invoke one method more than once.
  Mitigation: Retain the first occurrence in the configured group order.
- Risk: A method raises before later cleanup methods execute.
  Mitigation: Preserve current fail-stop-per-object behavior unless the owner explicitly
  selects per-method aggregation.

## Applicable Anti-Patterns
- [x] No epic-state transition without task-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [x] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- First map existing tests against current configuration, matching, consumption,
  multi-method order, persistence, and error behavior.
- Add behavior tests only after the owner approves the correction.
- Bind tests where configured order differs from class definition order, where
  reordering changes the fingerprint, and where identical ordered inputs remain
  stable across fresh processes/hash seeds.
- Spellbook component tests proving both groups contribute, priority is off by default,
  True moves book names first in their supplied order, overlaps are reordered once, and
  each new Spell uses its own explicit list. Empty spell names leave book names intact.
- Component tests through real Spellbook bind/conjure/meld/cleanup.
- Persistence and graft/restore round-trip tests.
- Active and staged restore plus selected, parked, and merged graft-member tests
  preserving distinct ordered disposal sequences.
- Compiler signature/namespace tests appropriate to the owner-approved design.
- Cross-process fingerprint stability with multiple matched disposal methods.
- Existing Creations reverse-order regressions.
- Source build-asset and repository-asset checks after implementation.

## Rollout / Adoption Plan
- Preserve existing public parameters; add the configuration setter for group order.
- Change only sequence ownership and propagation semantics.
- Update public documentation to state that every matching method executes in order.
- Regenerate derived assets in the same implementation lane.

## Open Questions
- Group composition is settled: enforce_priority_disposal_methods defaults False;
  True puts matching book methods first, including shared names, in configuration order.
- `with_enforce_priority_disposal_methods(enabled=True)` is the proposed fluent setter.

## Decision Log
- REVOKED AS IMPLEMENTATION AUTHORITY (2026-09-04): Prior mutable-list,
  ordered-tuple, snapshot, mutation, and identity recommendations were made
  before the current configuration-to-consumption mechanics were fully stated.
- DECISION: Preserve the owner's narrow goal: supplied disposal-name order must
  survive through the behavior that currently supports disposal matching.
- DECISION: Preserve the current class-profile scope; no callable/factory or
  existing-object expansion.
- DECISION: Current-state fact finding precedes all representation or lifecycle design.
- DECISION (2026-09-04): Use one resolved list per Spell. Book and per-spell names both
  contribute. enforce_priority_disposal_methods defaults False and opts into book-first
  order when True. A shared name occurs once at its first position.
  This supersedes earlier tuple and explicit-list-replaces-book-defaults proposals.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: none during discovery; patch artifacts become mandatory before implementation

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - ordered disposal ownership and execution
  - compiler/persistence propagation
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-03T01:05:17Z
  TYPE: DECISION
  CLAIM: The owner requires a mutable ordered list owned by each Spell. The list
    is derived by walking configured method names in order and retaining those
    implemented by that spell. Runtime consumers must use the live list rather
    than defensive copies; normal Python mutation after bind is permitted.
  EVIDENCE:
  - Owner direction in the active conversation, 2026-09-03T01:05:17Z
  - `context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md:29-36`
  IMPACT: The implementation target is an ownership correction across the complete
    pipeline, not a local container substitution.
  NEXT: Finish reading the 24 live source contact files and classify every contact
    as owner, derived view, runtime consumer, serializer, restorer, or generated output.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-03T01:05:17Z
  TYPE: FACT
  CLAIM: Source inventory finds 26 Python files containing
    `disposal_method_names`: 24 live source contacts plus two generated packaged
    documentation payloads. Confirmed transformations already include three
    `frozenset` boundaries, Creations list copies, fingerprint sequence
    consumption, and sorted crystal persistence.
  EVIDENCE:
  - `src/melder/aether/spellbook/spellbook.py:5136-5159`
  - `src/melder/aether/spellbook/bind/bind.py:396-412`
  - `src/melder/aether/spellbook/spell.py:302-435`
  - `src/melder/aether/conduit/creations/creations.py:197-354`
  - `src/melder/crystallizer/crystals/spell_crystal.py:281-282`
  IMPACT: The current system cannot promise configured method order or a single live
    spell-owned reference across runtime and persistence.
  NEXT: Read the unread compiler and replay contact files completely before fixing
    the proposed implementation boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:17:46Z
  TYPE: MEASURE
  CLAIM: The assembled `src_graph` document and index agree at 25,706 lines and
    SHA256 `140c847cdaeecd167911a487f614da68c4d7df67bf1b4b7b4c735d31d93e3f8c`,
    but current-file SHA256 comparison shows eight of nine disposal-path graph
    descriptors are stale. Only `graft_runner.py` still matches its recorded
    source hash; Conduit, Creations, Bind, SpellbookConfiguration, Spell,
    Spellbook, RestoreEngine, and SpellCrystal have moved.
  EVIDENCE:
  - `context_compass/system_docs/src_graph.md:4057-4062`
  - `context_compass/system_docs/src_graph.md:4696-4701`
  - `context_compass/system_docs/src_graph.md:5328-5333`
  - `context_compass/system_docs/src_graph.md:5488-5493`
  - `context_compass/system_docs/src_graph.md:5628-5633`
  - `context_compass/system_docs/src_graph.md:14636-14641`
  - `context_compass/system_docs/src_graph.md:16196-16201`
  - `context_compass/system_docs/src_graph.md:16337-16342`
  - `context_compass/system_docs/src_graph.md:16833-16838`
  IMPACT: The graph remains a valid routing map, but its authored descriptions
    cannot evidence current disposal behavior. Every set/list/order claim must be
    promoted from UNKNOWN only after reading the current source.
  NEXT: Read the current configuration-to-Spell ownership chain completely,
    then read Creations and Crystallizer replay before classifying each contact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:18:43Z
  TYPE: DECISION
  CLAIM: Ordered disposal is an end-to-end invariant for both public input
    routes: per-bind `Spellbook.bind(..., disposal_method_names=[...])` values
    and Spellbook-level configured disposal names. Bind must preserve the chosen
    route's order while filtering names for each Spell, and that per-Spell order
    must survive compiler planning, runtime registration, cleanup, crystal
    serialization, restore, and graft.
  EVIDENCE:
  - Owner clarification in the active conversation, 2026-09-04T11:18:43Z
  IMPACT: The discovery and eventual implementation cannot stop at
    `SpellbookConfiguration`; every order-transforming contact is in scope.
  NEXT: Trace both public input routes through every current source contact and
    classify which conversions are required boundaries versus accidental order loss.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:21:24Z
  TYPE: FACT
  CLAIM: Disposal metadata did not originate as a set contract. Commit
    `e890fecb7` introduced ordered `Spell.disposal_method_names` lists and
    filtered configured names in configured order. Bind-signature commit
    `bea61832f` moved resolution to bind time using a sorted intersection.
    Commit `1543624ef` then changed the shared configured value, resolved value,
    and Spell value to `frozenset` explicitly for immutability/consistency.
    Current source contains no disposal-specific union, intersection,
    difference, subset, or other set-algebra consumer. It uses membership,
    truthiness, iteration, fingerprint extension, and sequence conversion.
  EVIDENCE:
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:1107-1159`
  - `src/melder/aether/spellbook/spellbook.py:4839-4862`
  - `src/melder/aether/spellbook/spellbook.py:5136-5159`
  - `src/melder/aether/spellbook/bind/bind.py:396-412`
  - `src/melder/aether/spellbook/bind/bind.py:534-628`
  - `src/melder/aether/spellbook/spell.py:302-435`
  IMPACT: `frozenset` is an immutability choice, not a required behavioral
    operation. It discards caller order. The Spellbook also initializes one
    shared `_configured_disposal_method_names` value only once, so the first
    per-bind list currently becomes Spellbook-wide and later per-bind lists are
    ignored rather than remaining spell-bound.
  NEXT: Trace compiler, Creations, and persistence contacts to identify every
    snapshot and determine the smallest ordered replacement contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:25:37Z
  TYPE: FACT
  CLAIM: Runtime disposal is sequence-driven, not set-driven.
    `Creations._attempt_cleanup` invokes method names in stored iteration order
    and stops the current object's chain at the first method failure while the
    detached registry continues with later objects. Creations preserves method
    order but copies the sequence at registration, transfer extraction, and
    restoration. Compiler/cache contacts either create ordered tuple/list
    projections or retain each Spell sequence reference; none performs set
    algebra. `SpellCrystal` is the only live contact that explicitly sorts the
    names. Active restore and selected-member graft replay the recorded list,
    but staged restore and parked/merge graft members omit their own disposal
    names from `bind_inactive`.
  EVIDENCE:
  - `src/melder/aether/conduit/creations/creations.py:148-354`
  - `src/melder/aether/conduit/creations/creations.py:369-500`
  - `src/melder/aether/conduit/conduit.py:1386-1428`
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:79-94`
  - `src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1011-1199`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1091-1247`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:370-446`
  - `src/melder/crystallizer/crystals/spell_crystal.py:143-282`
  - `src/melder/crystallizer/crystals/spell_crystal.py:644-661`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1903-2002`
  - `src/melder/crystallizer/crystal_loader_system/graft_runner.py:371-480`
  IMPACT: An ordered sequence is compatible with every known consumer and is
    required for deterministic cleanup. Replacing the current frozenset with an
    ordered representation is not blocked by a set operation. The remaining
    design question is when runtime snapshots are intentional versus when live
    mutation must propagate.
  NEXT: Measure cross-process fingerprint stability and finish the exact
    owner/consumer/serializer/restorer edit map before recommending list versus
    tuple ownership.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:26:43Z
  TYPE: MEASURE
  CLAIM: Current bind fingerprinting is cross-process unstable when two or more
    disposal names are present. The live path resolves a `frozenset` and extends
    the ordered fingerprint parts with `tuple(disposal_method_names)`. With the
    same names (`close`, `shutdown`, `cleanup`) and fixed non-disposal prefix,
    `PYTHONHASHSEED` values 1-5 produced four iteration orders and four SHA256
    digests. Seeds 3 and 4 happened to agree; the other three differed.
  EVIDENCE:
  - `src/melder/aether/spellbook/bind/bind.py:396-412`
  - `src/melder/aether/spellbook/bind/bind.py:534-628`
  IMPACT: This is larger than cosmetic cleanup ordering. Multi-method spell IDs,
    compiler/cache signatures, persisted custody identities, and restore joins
    can vary across processes. An ordered canonical sequence is required even
    if the public collection is otherwise treated as immutable.
  NEXT: Complete the contact edit map and recommend the exact ordered ownership
    and snapshot boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:28:51Z
  TYPE: DECISION_REQUEST
  CLAIM: The historical bind-time disposal contract requires stable metadata
    after `spell_id` creation, but it does not require unordered storage. The
    completed design task moved resolution to bind because disposal names shape
    compiler/cache identity, blocked later configuration drift, and initially
    stored an immutable ordered tuple. The later frozenset refactor retained
    immutability while losing order. The active epic's mutable-live-list decision
    therefore needs owner confirmation against the existing identity law.
  EVIDENCE:
  - `context_compass/tickets/tasks/completed/2026-06-10_enforce_bind_time_disposal_signature_task.md:18-43`
  - `context_compass/tickets/tasks/completed/2026-06-10_enforce_bind_time_disposal_signature_task.md:180-226`
  - `src/melder/aether/spellbook/spellbook.py:6539-6561`
  - `src/melder/aether/spellbook/bind/bind.py:534-628`
  IMPACT: The ordered repair has two viable ownership models. An immutable tuple
    is the smallest correction and preserves bind identity. A mutable list is a
    larger behavioral change because post-bind mutation can desynchronize
    `spell_id`, plan/cache signatures, compiled namespaces, registered creations,
    and persisted crystals.
  NEXT: Finish the edit/test map, then ask the owner to choose tuple-stable or
    mutable-with-invalidation before patch artifacts or product edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:31:40Z
  TYPE: PLAN
  CLAIM: Fact-finding yields the following exact MRP edit map if the owner
    selects stable ordered tuples. `SpellbookConfiguration` remains the ordered
    Spellbook-level list source. `Spellbook.bind` and `bind_inactive` must stop
    treating the first per-bind sequence as a shared Spellbook value: `None`
    should inherit the cached ordered configuration sequence, while an explicit
    sequence should apply only to that Spell (`[]` explicitly disables inherited
    disposal). `Bind` must filter in configured order and fingerprint that same
    ordered result. `Spell` must store the ordered result. `Creations` already
    executes and retains order; its input annotations/documentation should accept
    an ordered `Sequence` and its per-creation list copy remains an intentional
    runtime snapshot under tuple-stable semantics. `SpellCrystal` must stop
    sorting. Staged restore plus parked and merged graft members must pass their
    recorded sequence into `bind_inactive`. Compiler contacts are audit/test
    surfaces: they already preserve sequence via ordered tuple/list projections
    or Spell-sequence references and require no set operation.
  EVIDENCE:
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:1107-1159`
  - `src/melder/aether/spellbook/spellbook.py:4754-4862`
  - `src/melder/aether/spellbook/spellbook.py:5030-5159`
  - `src/melder/aether/spellbook/bind/bind.py:310-412`
  - `src/melder/aether/spellbook/bind/bind.py:534-628`
  - `src/melder/aether/spellbook/spell.py:287-435`
  - `src/melder/aether/conduit/creations/creations.py:1-354`
  - `src/melder/crystallizer/crystals/spell_crystal.py:143-282`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1903-2002`
  - `src/melder/crystallizer/crystal_loader_system/graft_runner.py:371-480`
  IMPACT: The likely product-code edit is seven behavior files plus focused
    annotations/docs, tests, generated system-document payloads, and LLM support
    regeneration. The fifteen compiler contacts need regression coverage but no
    speculative rewrite. Mutable-list ownership would expand this map into
    re-identification, invalidation, recompilation, and registered-creation
    propagation work.
  NEXT: Obtain owner rulings on tuple versus mutable list, duplicate handling,
    and per-bind precedence; then author the patch contracts before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:32:22Z
  TYPE: FACT
  CLAIM: Existing coverage proves only the bottom half of the order contract.
    Creations unit regressions already require every method to run in declared
    order and pin fail-stop behavior for the current object. Configuration tests
    already require ordered first-occurrence deduplication. The Spellbook
    component test instead asserts frozenset equality, Bind fingerprint coverage
    uses only zero or one disposal name, and no current restore/graft test proves
    distinct multi-method order across active and staged members.
  EVIDENCE:
  - `tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py:1-211`
  - `tests/unit/melder/spellbook/configuration/test_configuration.py:408-414`
  - `tests/component/melder/spellbook/test_spellbook_component_spellbook.py:547-633`
  - `tests/unit/melder/spellbook/bind/test_bind.py:1646-1724`
  IMPACT: The current suite can pass while upstream order is destroyed because
    the only exact-order tests inject lists directly into Creations. End-to-end,
    fingerprint, and persistence tests are required for this repair.
  NEXT: Present the fact-found model and owner decisions before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:36:15Z
  TYPE: FACT
  CLAIM: Resolved disposal method names are part of the bind-time SHA256.
    `Bind._bind_logic` computes the matching collection before constructing the
    Spell and passes it into `Bind.sha256_profile`; the fingerprint extends its
    ordered parts with those names. The resulting digest is assigned once to
    `Spell.spell_id` and the initial `SpellIndex` selection. No disposal-metadata
    mutation hook recomputes that digest, remaps Spellbook/Aether indexes, or
    invalidates every compiled/runtime/persistence snapshot.
  EVIDENCE:
  - `src/melder/aether/spellbook/bind/bind.py:396-421`
  - `src/melder/aether/spellbook/bind/bind.py:534-628`
  - `src/melder/aether/spellbook/spell.py:287-435`
  - `src/melder/aether/conduit/creations/creations.py:264-354`
  - `src/melder/crystallizer/crystals/spell_crystal.py:143-282`
  IMPACT: Post-bind in-place mutation would leave `spell_id` describing the old
    sequence while some consumers retain old tuple/list snapshots, some compiled
    namespaces retain the old collection reference, already-registered creations
    retain copied lists, and persisted crystals retain their emission-time list.
    Mutable ownership is therefore unsafe without a full structural mutation and
    re-identification protocol, which is outside this repair.
  NEXT: Use list input normalized at bind into an immutable ordered Spell tuple,
    unless the owner explicitly chooses the much larger mutation/re-identification lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:38:33Z
  TYPE: DECISION
  CLAIM: The Spell-owned representation is an immutable ordered tuple. Public
    configuration and bind surfaces continue accepting lists/sequences, Bind
    performs ordered matching/deduplication, and post-bind mutation is not a
    supported contract. Python has no standard frozen ordered set; a tuple
    provides the required ordering and immutability without a custom type or
    dependency.
  EVIDENCE:
  - Owner clarification in the active conversation, 2026-09-04T11:38:33Z
  - `src/melder/aether/spellbook/bind/bind.py:396-421`
  - `src/melder/aether/spellbook/bind/bind.py:534-628`
  IMPACT: The identity/invalidation expansion is removed. Ordered tuple values
    make bind SHA, compiler signatures, Creations snapshots, and persisted lists
    coherent while retaining the user's declared execution order.
  NEXT: Settle duplicate-name and per-method-failure behavior, then author the
    required patch contracts for the seven-file behavior edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:51:06Z
  TYPE: DECISION
  CLAIM: One immutable ordered tuple is created at Bind and owned by the Spell.
    Compiler records/plans/executor namespaces and Creations entries retain that
    exact tuple reference rather than rebuilding lists or tuples. Transfer paths
    carry the same tuple. SHA256 necessarily consumes its ordered values, and
    Crystallizer necessarily emits a detached list for JSON/persistence; restore
    creates a new Spell tuple at the new bind boundary.
  EVIDENCE:
  - Owner clarification in the active conversation, 2026-09-04T11:51:06Z
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:79-94`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1091-1247`
  - `src/melder/aether/conduit/creations/creations.py:264-354`
  - `src/melder/crystallizer/crystals/spell_crystal.py:143-282`
  IMPACT: The earlier proposal to preserve Creations list copies is superseded.
    Removing redundant runtime snapshots prevents stale metadata, avoids
    allocations, and makes one Spell-owned value authoritative until the true
    persistence boundary.
  NEXT: Update the patch edit map so compiler propagation and Creations storage
    retain tuple identity, then settle duplicates/failure posture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:58:57Z
  TYPE: FACT
  CLAIM: Current Spellbook-configured disposal matching happens at the first
    `bind`/`bind_inactive`, not at conjure. While the Spellbook's shared
    `_configured_disposal_method_names` field is `None`, the first call chooses
    its per-bind sequence when provided, otherwise the configuration list,
    otherwise empty; it converts that choice to one shared `frozenset` reused by
    later binds. `Bind._bind_logic` builds a class binding profile and, only for
    `ClassBindingProfile`, retains profile method names found in the shared set.
    The profile method list is built from callable entries in the class's own
    `__dict__`, excluding inherited methods. A configured name absent from that
    list is silently omitted. When no names match, the Spell receives an empty
    frozenset and `has_disposal_methods=False`. Conjure does not rematch methods;
    it only checks frozenset type and boolean consistency.
  EVIDENCE:
  - `src/melder/aether/spellbook/spellbook.py:4754-4862`
  - `src/melder/aether/spellbook/spellbook.py:5030-5159`
  - `src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:70-132`
  - `src/melder/aether/spellbook/bind/bind.py:310-421`
  - `src/melder/aether/spellbook/spell.py:287-435`
  - `src/melder/aether/spellbook/spellbook.py:6539-6561`
  IMPACT: Current behavior neither applies each per-bind list independently nor
    uses Spellbook configuration order. The first bind selects one Spellbook-wide
    candidate set; matching follows own-class definition order before the
    frozenset erases order. Missing and inherited-only names disappear without
    diagnostics or runtime disposal registration.
  NEXT: Trace the exact compiler/Creations consumption chain and the separate
    `disposal` configuration flag before proposing any correction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T11:59:53Z
  TYPE: FACT
  CLAIM: Current downstream consumption is gated by
    `Spell.has_disposal_methods`. The runtime processor carries the Spell flag
    and names into `SpellRuntimeRecord`; planners and generated executor
    namespaces propagate them into registration calls. `Existence.many` results
    are registered only when the flag is true, while managed singleton/scoped
    existences register normally and attach disposal metadata when present.
    Existing-object registration uses the same Spell flag through Conduit.
    Creations stores disposal metadata only when the flag is true, disposes
    objects in reverse creation order, and invokes stored method names
    sequentially; the first failing method ends that object's chain while later
    objects still run and failures aggregate. Names discarded during Bind never
    reach this pipeline and cause no warning. A source-wide exact-access search
    found no runtime read of the separate configuration `disposal` boolean;
    `with_disposal` only writes the property, so method-name matches currently
    drive tracking by themselves.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:79-94`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2650-2670`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1500-1584`
  - `src/melder/aether/conduit/conduit.py:1386-1428`
  - `src/melder/aether/conduit/creations/creations.py:148-354`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:1090-1105`
  IMPACT: A missing configured name is not managed later; it is silently absent
    from the Spell and no disposal call is attempted. A partial match registers
    only matched names. With zero matches, `many` instances are not retained for
    cleanup at all. The `disposal` boolean currently does not enable or disable
    this behavior.
  NEXT: Replace the epic handoff with this current-state map and present only
    the real owner decisions: absent-name policy and Spellbook/per-bind
    combination/order semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T20:20:36Z
  TYPE: PLAN
  CLAIM: The owner selected a three-phase delivery: configuration/Bind/Spell,
    then compiler/Creations, then Crystallizer/replay/documentation. The Phase 1
    task now contains the current mechanics, a worked example, and a proposed
    correction. Matching is per class even though candidate selection is latched
    once today. Consumer interfaces are sufficient for Phase 1; later phase
    implementation is not part of this discovery pass.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md:14-165`
  - Owner instruction in the active conversation, 2026-09-04
  IMPACT: Source facts and the first reviewable correction are held in the active
    task. Historical whole-pipeline proposals do not widen the current phase.
  NEXT: Review the first phase's candidate-selection and ordered-storage contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T20:38:15Z
  TYPE: DECISION
  CLAIM: Phase 1 now targets the owner's list-based composition rule: configured
    names precede explicit Spell names by default, with a switch to reverse the
    group order. Matching is performed once when each Spell is created. Later
    compiler/Creations and persistence phases remain separate.
  EVIDENCE:
  - Owner instruction in the active conversation, 2026-09-04
  - `context_compass/tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md:136-187`
  IMPACT: Storage and input composition are decided. Tuple, override-only, and
    mutation/invalidation proposals in historical notes are not the implementation plan.
  NEXT: Prepare the Phase 1 implementation contract for the four producer files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T20:47:44Z
  TYPE: DECISION
  CLAIM: The owner named the configuration flag enforce_priority_disposal_methods
    and set the default to False. True promotes matching configured names to the
    front in configuration order. False keeps spell-specific order first and
    appends remaining configured names. This replaces the prior default-True plan.
  EVIDENCE:
  - Owner instruction in the active conversation, 2026-09-04
  IMPACT: Phase 1's name, default, group order, and shared-name priority are explicit.
  NEXT: Prepare the Phase 1 implementation contract using the revised setting.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:06:17Z
  TYPE: PLAN
  CLAIM: The requested configuration/fluent/Crystallizer/Nexus map is complete in
    the Phase 1 task. SpellbookConfiguration owns the schema, defaults, and fluent
    setter. Existing book configuration payloads and Nexus default construction
    carry the flag without duplicate root properties. Pre-bind default availability
    and reload default accounting are included in the implementation/test boundary.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md:195-320`
  IMPACT: Phase 1 discovery is in review; runtime and persistence implementation
    remain undone. The source-oriented map replaces speculative cross-system edits.
  NEXT: Prepare the Phase 1 configuration/Bind/Spell implementation contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:33:23Z
  TYPE: PLAN
  CLAIM: The owner-requested work breakdown now has three phase stories and nine concrete
    tasks. Contract/configuration/binding/configuration-transport form Phase 1; compiler
    and Creations form Phase 2; replay/docs-assets/final verification form Phase 3.
    Each task carries dependencies and explicit post-compaction reading locations.
  EVIDENCE:
  - `context_compass/tickets/stories/2026-09-04_ordered_disposal_binding_story.md:1-65`
  - `context_compass/tickets/stories/2026-09-04_ordered_disposal_runtime_story.md:1-61`
  - `context_compass/tickets/stories/2026-09-04_ordered_disposal_persistence_story.md:1-64`
  IMPACT: The current task stack can be resumed from repository files. Product source,
    patch artifacts, and runtime test results have not been created by this planning pass.
  NEXT: Verify ticket links/ranges, then resume at the patch-contract task after re-entry.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:37:43Z
  TYPE: MEASURE
  CLAIM: Ticket-stack verification passed for three new stories and nine new tasks.
    Required template sections and codex_1 assignments are present. The dependency
    graph is acyclic. All 126 extracted file/range references resolve, including
    61 ranged citations whose start/end locations are within the referenced files.
  EVIDENCE:
  - `context_compass/tickets/stories/2026-09-04_ordered_disposal_binding_story.md:1-65`
  - `context_compass/tickets/stories/2026-09-04_ordered_disposal_runtime_story.md:1-61`
  - `context_compass/tickets/stories/2026-09-04_ordered_disposal_persistence_story.md:1-64`
  IMPACT: Planning and compaction handoff are complete. This validates ticket structure
    and reading pointers only; no product implementation or runtime tests were performed.
  NEXT: After REONBOARD, execute the routed ordered_disposal_patch_contract task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:06:16Z
  TYPE: FACT
  CLAIM: The owner-requested holistic read now connects the configuration flag to every
    major producer, compiler/runtime, and persistence boundary in the epic. The change map
    above records what needs modification and which existing mechanisms stay intact.
    Source/test evidence is in the child tasks; no product implementation or runtime tests
    were performed by this read.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_patch_contract_task.md`
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_compiler_propagation_task.md`
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_creations_task.md`
  - `context_compass/tickets/tasks/2026-09-04_disposal_configuration_roundtrip_task.md`
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_crystal_replay_task.md`
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_docs_assets_task.md`
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_end_to_end_validation_task.md`
  IMPACT: The selected small configuration implementation can follow a system-informed
    contract without reopening settled list/priority decisions or changing later phases.
  NEXT: Prepare the scoped patch contracts, then implement the configuration task only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:39:54Z
  TYPE: MEASURE
  CLAIM: The first configuration-only implementation is in review: bool/default/fluent API,
    init/clear availability, and reload accounting are implemented with 21 new cases.
    The full focused configuration/reload/adoption boundary passes 115 tests on Windows 3.14t.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-04_disposal_priority_configuration_task.md`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:1128-1157`
  IMPACT: This stages policy only. Bind/Spell, compiler, Creations, crystal replay, canonical
    promotion, and generated assets remain pending. Nothing was committed or pushed.
  NEXT: Review the configuration slice, then prepare its Bind/Spell successor contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:40:08Z
  TYPE: MEASURE
  CLAIM: The Bind/Spell producer slice is implemented and in review. Independent ordered
    groups, both priorities, absent/duplicate names, bind SHA, and Spell list ownership pass
    focused tests. Latest producer and surrounding verification totals 753 selected cases.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_bind_and_spell_task.md`
  IMPACT: The source of ordered metadata is established. Compiler/Creations ownership,
    full configuration transport, crystal replay, canonical promotion, and assets remain pending.
  NEXT: Review this slice, then prepare the compiler propagation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:33:58Z
  TYPE: MEASURE
  CLAIM: Runtime phase is implemented and in review: seven compiler files plus Creations,
    with 51 new regression cases. Final selected Spellbook/compiler/Creations/conduit suite
    passes 2,797 tests on Windows 3.14t. Real runtime checks caught two inline emitted copies
    beyond the original metadata inventory; both were removed under the caller contract.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_compiler_propagation_task.md`
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_creations_task.md`
  IMPACT: Established disposal order/reference now reaches real cleanup, including repeated
    calls, override variants, and transfer. No new locks or disposal-loop rewrite. Persistence
    order, full configuration transport, canonical docs, and final assets remain pending.
  NEXT: Verify configuration round trips, then implement the crystal/replay task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:08:48Z
  TYPE: DECISION_REQUEST
  CLAIM: Configuration transport is verified (59 focused tests, no production correction).
    The real graft diagnostic reaches the planned policy gate: changed target-book disposal
    order changes the bind SHA, while sibling parking still looks up the recorded SHA.
    Same-policy graft succeeds; changed policy binds the selected member and skips its sibling.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-04_disposal_configuration_roundtrip_task.md`
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_crystal_replay_task.md`
  IMPACT: Replay task is blocked on explicit target-policy/new-ID approval. No persistence
    source changes or invented ID translation have been made.
  NEXT: Owner decides whether grafting should retain target policy and follow returned live IDs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:28:11Z
  TYPE: DECISION
  CLAIM: Owner clarified and approved that configured book names own overlaps in both modes.
    False means spell-only names then the complete book block; True means book block then
    spell-only names. Each block preserves its own supplied order; duplicates execute once.
    This supersedes earlier False-mode spell-first overlap retention, not the binding boundary.
  EVIDENCE:
  - Owner clarification and implementation approval, active conversation, 2026-09-05.
  IMPACT: Briefly reopen the producer task to correct grouping and prove the runtime result
    before completing replay. Receiving-book composition remains authoritative at new binds.
  NEXT: Complete the focused producer correction under its existing task and patch contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:37:10Z
  TYPE: MEASURE
  CLAIM: Clarified overlap composition is implemented and passes 2,807 selected tests.
    Book names retain one ordered block in both modes; spell-only names go before/after it.
    Runtime propagation needs no source correction. Persistence source and final assets remain pending.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_bind_and_spell_task.md`
  IMPACT: Producer is in review; receiving-book policy is settled and replay is ready to resume.
  NEXT: Complete ordered crystal capture/replay, then the existing documentation/assets task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T13:21:33Z
  TYPE: MEASURE
  CLAIM: Remaining ordered-disposal work is implemented. Book-owned overlap order survives
    binding, compiler/Creations, crystal capture, active/staged restore, and fresh/merge graft.
    Actual new bind identities drive replay joins. Docs/examples and generated assets are updated.
    Full Windows 3.14t CI runtime run: 11,359 passed, 28 skipped, 15 xfailed, 1 xpassed; exit 0.
  EVIDENCE:
  - `tickets/tasks/2026-09-04_ordered_disposal_end_to_end_validation_task.md`
  IMPACT: Epic is in review, not closed/published. Source/corpus checks and hygiene pass.
    Ubuntu CI and independent RTD qualification remain external evidence; unrelated findings are
    recorded separately in the final task. No commit or push was issued by this agent.
  NEXT: Owner accepts the delivered feature, then close tickets and dispose temporary artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

### Current source contact inventory

Configuration, bind, and Spell ownership:
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py`
- `src/melder/aether/spellbook/spellbook.py`
- `src/melder/aether/spellbook/bind/bind.py`
- `src/melder/aether/spellbook/spell.py`

Compiled planning and execution carriers:
- `src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_runtime_analysis.py`
- `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_helpers.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py`

Runtime storage and execution:
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/creations/creations.py`

Persistence and replay:
- `src/melder/crystallizer/crystals/spell_crystal.py`
- `src/melder/crystallizer/crystals/spellbook_crystal.py`
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py`
- `src/melder/crystallizer/crystal_loader_system/graft_runner.py`

Generated contacts, never hand-edited:
- `src/melder/_build_assets/_system_documents/payloads/src_components_payload.py`
- `src/melder/_build_assets/_system_documents/payloads/src_graph_payload.py`

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level contract, cross-layer propagation, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Current resume route: `tickets/tasks/2026-09-04_ordered_disposal_end_to_end_validation_task.md` (review).
ALL TECHNICAL PHASES COMPLETE: final evidence and separate findings are in that task. Await owner closure.
Latest ruling: book owns overlap order in both modes; False positions its block last, True first.
Configuration, producers, compiler/Creations, and configuration transport are verified. Runtime
verification passes 2,797 selected tests; transport adds a 59-test focused boundary.
The latest overlap correction passes 2,807 tests. Replay policy is settled; its source is unchanged.
This agent did not commit/push, but separate commits landed during the work on codex_features2.
The Implementation Task Sequence above links all nine tasks and their prerequisites under
three stories. The discovery task remains a review/reference document, not the execution route.
Ticket-stack creation and structural verification are complete: three stories, nine tasks,
126 valid file/range references, 61 in-bounds citations, and no dependency cycle.
Persistence, canonical documentation promotion, and final assets remain pending.
Resume from the routed task after REONBOARD.

Historical producer baseline, replaced by the 2026-09-05 slice: on the first bind, Spellbook selected either
that call's per-bind names, otherwise the SpellbookConfiguration names, otherwise
empty, and latches one shared frozenset for later binds. Bind checks only class
profiles and matches against callable names from the class's own `__dict__`;
missing and inherited-only configured names are silently dropped. Conjure does
not rematch. The resulting Spell flag/names flow through compiler registration
into Creations, which invokes accepted names sequentially during reverse-order
cleanup. Zero matches means no disposal tracking; for `Existence.many`, the
instance is not retained for cleanup. The separate `disposal` boolean has no
runtime reader. These downstream mechanisms remain unchanged by the producer slice.

Current direction is list storage, combining both input groups once at Spell creation.
enforce_priority_disposal_methods defaults False; True promotes book methods in their
configured order, including shared names. The Phase 1 task holds examples, the
four-file producer boundary, and a completed Configuration Change Map covering fluent
API, Crystallizer transport/reload, and Nexus defaults. Prepare the implementation contract
before each newly activated component, then follow the dependency chain. Phases 2
and 3 handle consumption and persistence; configuration, producers, and runtime propagation are implemented.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
