# Story: Preserve non-resolution policy and graph relationships through storage and restore

## Metadata
- Story ID: STORY-2026-09-19-discoverable-registration-persistence
- Epic: EPIC-2026-09-19-discoverable-non-resolvable-registrations
- Sequence: S6
- Status: draft
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T17:25:45Z
- Updated: 2026-09-19T21:38:40Z

## User Narrative
As a user, I can store and restore a graph containing discovery-only definitions and caller-supplied
dependencies without making those definitions resolvable or losing their versioned relationships.

## Value / MRP Alignment
The persisted world must reconstruct the same policy and graph meaning as the live registered world.

## Ticket Contract
- ENTRY_GATE: S1 identity compatibility, S2 mode, S3 supplied-input schema, S4 runtime behavior and
  S5 graph/revision payload contracts are available; execution task and required patch contracts exist.
- EXECUTION_BOUNDARY: Crystal capture/value payloads, checkpoint/profile storage, cache/hydration,
  restore/graft, and registration/index lifecycle propagation.
- DEPENDENCIES: S1-S5; supply durable round-trip evidence to S7.
- EXIT_GATE: Cross-process or isolated-world replay/graft retains mode, relationships and selected revisions.
- FAILURE_ESCALATION: Record unsupported target/source recovery, identity conflicts or record-version
  decisions explicitly. Do not invent live references or silently default False to True.

## Requirements (Functional)
- Capture per-Spell resolvable policy and accepted role/reference/revision metadata as plain values.
- Keep live references and application-instance memory outside serialized graph policy.
- Carry metadata through active and staged bind capture, snapshots, checkpoint chains and asset storage.
- Replay through normal binding verbs with the recorded mode; legacy absence means prior resolvable behavior.
- Preserve mode across bind_inactive, notch, index moves, ownership transfer and graft where supported.
- Retain recorded-to-live identity translation when the receiving fingerprint/schema changes.
- Keep graph revisions and target selections consistent with S5, including retained source revisions.
- Restore discovery-only definitions without scheduling their construction or requiring their own
  constructor dependencies to resolve.
- Preserve caller-supplied requirements after replay; report unavailable live input rather than creating it.
- Update compiled-cache metadata/version handling using the existing mismatch/invalidation system.
- Preserve the owner-selected existing version rules; no automatic source-body revision identity.
- Use existing record compatibility gates so an older reader cannot ignore False and enable resolution.
- Preserve removal and history semantics; current graph removal and retained historical revisions differ.
- Re-emission of a restored world must retain the new policy and graph payload rather than dropping fields.

## Requirements (Non-Functional)
- Keep passive emission ownership: structural units emit; activation does not sweep the whole world.
- Respect loader admission, frame-before-book setup, fresh structural identities and failure teardown.
- Use current record/cache compatibility mechanisms and plain-value contracts; no new persistence framework.

## Scope Boundaries
- In scope: durable representation, runtime rebuild and relevant structural lifecycle transitions.
- Out of scope: serializing arbitrary live objects, redesigning supplied-object disposal, unrelated storage backends.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Planned after the shared registration/socket/graph schema is defined.

## Dependencies / Related Work
- Parent: `tickets/epics/2026-09-19_discoverable_non_resolvable_registrations_epic.md`
- S2: `tickets/stories/2026-09-19_discoverable_registration_modifier_story.md`
- S3: `tickets/stories/2026-09-19_caller_supplied_socket_compiler_story.md`
- S4: `tickets/stories/2026-09-19_discoverable_resolution_runtime_story.md`
- S5: `tickets/stories/2026-09-19_discoverable_nexus_graph_and_history_story.md`
- Next: `tickets/stories/2026-09-19_discoverable_registration_qualification_story.md`

## Required Reading Before Work
1. Parent epic and accepted S1-S5 identity, socket, graph and cache contracts.
   Read `tickets/tasks/2026-09-19_define_non_resolvable_admission_identity_task.md` for the owner
   version-policy decision and omitted/True versus False fingerprint/record compatibility.
2. Verify architecture/component indexes. Read Crystallizer Root, Persistence Record, And Module-World
   Surfaces; Persistence & Restore; Subsystem Decomposition; SpellIndex Mutation Surface; Ownership Transfer.
3. Verify graph-index slices for touched source owners; read complete capture/serialization consumers:
   - `src/melder/crystallizer/crystals/spell_crystal.py`
   - `src/melder/crystallizer/crystals/spell_index_crystal.py`
   - `src/melder/crystallizer/crystals/spellbook_crystal.py`
   - `src/melder/crystallizer/crystals/mutation_research_crystal.py`
   - `src/melder/crystallizer/persistence/persistence_profile.py`
   - `src/melder/crystallizer/persistence/persistence_crystal.py`
   - `src/melder/crystallizer/persistence/persistence_system.py`
   - `src/melder/crystallizer/asset_management/asset_management_system.py`
   - `src/melder/crystallizer/asset_management/crystallizer_cache.py`
   Follow their actual record-version/codec imports before deciding compatibility.
4. Trace rebuilding and structural transitions:
   - `src/melder/crystallizer/crystallizer.py` — emit, checkpoint, load and graft facades.
   - `src/melder/crystallizer/crystal_loader_system/crystal_loader_system.py`
   - `src/melder/crystallizer/crystal_loader_system/load_admission.py`
   - `src/melder/crystallizer/crystal_loader_system/restore_engine.py`
   - `src/melder/crystallizer/crystal_loader_system/graft_runner.py`
   - `src/melder/crystallizer/crystal_loader_system/user_world_rebuild.py`
   - `src/melder/aether/spellbook/spellbook.py` — bind/inactive, notch, membership and removal emissions.
   - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
   - `src/melder/utilities/caching_system/caching_system.py`
   - `src/melder/aether/spellbook/spellbook_creation_system.py` — compiled payload load/hydration.
5. Before tests, read test architecture/components via indexes and relevant persistence fixtures:
   - `tests/unit/melder/crystallizer/persistence/test_restore_engine.py`
   - `tests/unit/melder/crystallizer/crystal_loader_system/test_restore_fold_safety.py`
   - `tests/unit/melder/crystallizer/crystal_loader_system/test_restore_plan_levels.py`
   - `tests/component/melder/crystallizer/test_crystallizer_restore_policy_component.py`
   - `tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py`
   - `tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_cache_rehydration_exec.py`


## S2 Implementation Handoff
The native registration bool is implemented and tested; it is not yet carried by SpellCrystal.
S6 must record an explicit bool, default only absent legacy data to True, and preserve False through
all active/inactive replay and graft entry points. Use current record compatibility gates to prevent
older readers from silently enabling a False definition. Existing True SHA inputs are unchanged;
False uses v4-binding-non-resolvable with the remaining inputs/order intact. Source-body versioning
was not added. Read:
`tickets/tasks/2026-09-19_implement_resolvable_registration_modifier_task.md`.

## S3 Delivered Compiler Data and Compatibility Limit
S3 provides local referenced_spell_ids, parameter_kind/position and OVERRIDE_REQUIRED policy.
Injection/model/planner records retain required_override_params as immutable plain-value rows:
(name, position, parameter-kind name, reference-ID tuple). Injection IR/signature exports carry the
new metadata, and False roots are excluded from executable payload admission.

This is not crystal capture or full compiled-cache hydration. S4 must transport/enforce the rows
through live CodegenCreationSchemaHelpers and executor families; S6 must qualify the resulting
cache compatibility together with capture/restore/graft policy. Do not infer durable safety from
an updated compiler signature or the existing automatic invalidation mechanism alone.

Read `tickets/tasks/2026-09-19_implement_override_required_compiler_task.md` and its final validation
artifact, then S4/S5's accepted runtime/graph payload contracts before selecting the wire schema.
Legacy absence, recorded False, target identity translation and re-emission remain explicit tests.

## Tasks (Implementation Checklist)
- [ ] Create capture/compatibility task and record the mode/revision wire schema.
- [ ] Add active/staged and legacy-record round-trip regressions.
- [ ] Implement capture, decode, binding replay and graft forwarding.
- [ ] Verify notch/transfer/removal retain current graph policy and history correctly.
- [ ] Qualify cache invalidation/hydration and recorded-to-live identity translation.
- [ ] Verify rebuilt worlds re-emit the complete graph contract and hand evidence to S7.

## Acceptance Criteria
- Restored False registrations remain visible and unresolvable in a fresh runtime world.
- Legacy records lacking the modifier preserve prior behavior.
- Graph relationships and selected revisions survive checkpoint, load and supported graft flows.
- Required caller inputs remain pending after restore and fail usefully when absent.
- Mode and identity remain consistent through supported registration/index lifecycle changes.
- Failed replay respects current admission/teardown and reports unreplayable information explicitly.

## Validation / Test Plan
- Not run. Use isolated-world/cross-process tests for actual value round trips and identity translation.
- Cover pre/post-conjure active/staged registrations, old/new schema records and stored source recovery.
- Include a restored consumer meld with a supplied input and a refusal without it.
- Verify ordinary resolvable records remain compatible; do not claim full record coverage from one fixture.

## UX / API / Data Notes
Restore reconstructs registration/graph structure. Supplying a live runtime value remains the caller's act.

## Risks / Mitigations
The most dangerous fallback is losing False during replay and returning a constructible registration.
Schema tests must inspect both recorded values and the behavior of the rebuilt graph.

## Applicable Anti-Patterns
- [ ] No False-to-True loss or raw object-reference serialization.
- [ ] No direct registry merges that bypass bind/replay contracts.
- [ ] No new global invalidation scheme or revived existing-instance lifecycle redesign.

## Open Questions
Use S1/S5 decisions for target families, graph revision identity, legacy policy and receiving-book differences.

## Decision Log
- Existing emit/checkpoint/asset/loader ownership is preserved; the feature adds recorded policy and graph data.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: accepted story closure with declared per-artifact retention.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: mode/graph custody, version schemas, replay, cache and lifecycle propagation.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-19T17:25:45Z
  TYPE: PLAN
  CLAIM: Persist and replay the same capability and resolved graph meaning established by S2-S5.
  EVIDENCE:
  - src/melder/crystallizer/crystals/spell_crystal.py:143-342
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1739-2014
  IMPACT: Rebuilt registrations must not silently regain resolution or lose descriptive relationships.
  NEXT: Read the accepted wire/revision contract and map each capture-to-replay field before coding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:38:40Z
  TYPE: FACT
  CLAIM: S3 has implemented plain-value reference/required-input metadata and signature transport.
    It has not implemented SpellCrystal policy, replay/graft forwarding or full executor hydration.
    Its 2098 passing cases are compiler/compatibility evidence, not persistence round-trip evidence.
  EVIDENCE:
  - tickets/tasks/2026-09-19_implement_override_required_compiler_task.md
  - artifacts/override_required_compiler_20260919/validation.md:1-72
  IMPACT: S6 must preserve recorded False and the accepted S5 graph through normal replay and
    qualify cache records against S4's final executor contract without serializing live values.
  NEXT: After S4/S5, map each accepted native field through capture, codec, replay and re-emission.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Owner accepts round-trip behavior and evidence.
- [ ] Child tasks, artifacts and boards synchronized.

## Noting Behavior
Keep compatibility and cross-subsystem persistence decisions here; task notes retain exact fixture evidence.

## Context / Handoff Summary
Draft S6. Capture, storage and restore are separate from compiler cache replay; both must preserve mode.
S2/S3 provide native policy and compiler reference/input rows; their persistence is still unimplemented.
Consume the handoffs above after S4/S5 settle runtime/graph contracts. Do not revive object-instance
serialization or assume activation captures omitted prior emissions.
