# Story: Expose connected discovery-only definitions and graph revisions through Nexus

## Completion
- Completed: 2026-09-20T00:25:59Z
- Summary: Delivered ACL-filtered definition/reference/base navigation with existing source, history and version-selection workflows.
- Acceptance: Owner requested turn-in, then required two repairs first; both are verified.

## Metadata
- Story ID: STORY-2026-09-19-discoverable-nexus-graph-and-history
- Epic: EPIC-2026-09-19-discoverable-non-resolvable-registrations
- Sequence: S5
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T17:25:45Z
- Updated: 2026-09-20T00:25:59Z

## User Narrative
As an agent, I can discover a registered abstract base/helper, navigate its relationships, inspect
and compare revisions, and stage a revision through Nexus without resolving the definition.

## Value / MRP Alignment
The owner requires a manifested architectural graph. A source file list or disconnected metadata row
is insufficient; discovery, relationships and history must form a coherent agent-facing surface.

## Ticket Contract
- ENTRY_GATE: S1 defines graph/revision ownership, S2 provides policy, S3 provides target relationships,
  and S4 prevents accidental execution. Scoped task and relevant patch contracts precede code edits.
- EXECUTION_BOUNDARY: Nexus descriptor/publication/projection/commands and MR source/history/graph access.
- DEPENDENCIES: S1-S4; produce the graph/revision payload contract consumed by S6.
- EXIT_GATE: Agent-facing tests prove connected navigation and version queries without meld/creation.
- FAILURE_ESCALATION: Escalate identity or graph-role ambiguity; do not replace runtime registration with
  a new architecture framework or infer design ownership solely from source syntax.

## Requirements (Functional)
- Publish discovery-only registrations as addressable nodes with capability, target/source and version.
- Support selected and parked definition views according to the accepted visibility lifecycle.
- Preserve caller-supplied dependency targets and applicable inheritance/implementation/internal-use edges.
- Distinguish declared design relationships from mechanically verified structure.
- Distinguish declared type, selected executable provider and candidate membership. Excluding a False
  candidate from construction does not make it a dependency; avoid fabricated graph edges.
- Expose graph navigation, source/part reads, revision comparison, impact and permitted candidate work.
- Keep viewing/editing permissions distinct from runtime invocation; normal ACL/frame policy still applies.
- Preserve the declared version relationships; a graph snapshot must not silently follow latest targets.
- Use existing version identity rules, as selected by the owner. Definition revisions use explicit
  module/binding/version workflows; same-identity body edits do not automatically mint versions.
- Express graph relationship changes through the existing revision/organization workflow; no new
  automatic source-version identity is part of this feature.
- Keep candidate preparation separate from live adoption; identify affected resolvable consumers.
- Reuse existing MR/custody/source analysis facilities where source supports the required contract.
- Produce the durable schema boundary for S6; S5 proves in-memory graph/history, S6 proves replay.

## Requirements (Non-Functional)
- No requirement to execute arbitrary code just to list or inspect a registered definition.
- No compulsory Melder base classes/decorators in user code and no duplicate architecture truth store.
- Stable tool payloads and explicit missing-source/missing-revision results.

## Scope Boundaries
- In scope: graph publication, permitted navigation/revision operations, MR history and payload design.
- Out of scope: filesystem IDE replacement, automatic migration of live Python objects, storage implementation.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner-authorized turn-in after delivered scope and reported failure repairs passed.

## Dependencies / Related Work
- Parent: `tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md`
- S3: `tickets/stories/completed/2026-09-19_caller_supplied_socket_compiler_story.md`
- S4: `tickets/stories/completed/2026-09-19_discoverable_resolution_runtime_story.md`
- Next: `tickets/stories/completed/2026-09-19_discoverable_registration_persistence_story.md`
- Evidence: `tickets/tasks/2026-09-19_understand_nexus_crystallizer_spellbook_task.md`

## Required Reading Before Work
1. Parent epic, accepted S1 graph/revision decisions, S2 mode and S3 resolved target contract.
   Read `tickets/tasks/completed/2026-09-19_define_discoverable_registration_selection_task.md` for selector
   scope and descriptive-edge meaning. The required-input category is OVERRIDE_REQUIRED.
2. Verify `system_docs/src_components_index.md`; read AR Runtime Surface, Nexus Descriptor And ACL
   Managers, RiftSpace Workstation And Command Surface, and MutationResearch Root/ResearchSet slices.
3. Verify graph-index ranges for the changed owners, then read complete source methods/call paths:
   - `src/melder/aether/spellbook/spellbook.py` — conjure/incremental publication and parked identity lookup.
   - `src/melder/nexus/frame_descriptor_manager.py` — publication and removal.
   - `src/melder/nexus/frame_descriptor/frame_descriptor.py`
   - `src/melder/nexus/frame_descriptor/spell_record.py`
   - `src/melder/nexus/frame_descriptor/spell_descriptor_payload.py`
   - `src/melder/nexus/nexus.py` — projections, ACL refresh and frame policy.
   - `src/melder/nexus/rift/rift.py` — target links and current projection ownership.
   - `src/melder/nexus/rift/frame_viewer/view_spell.py`
   - `src/melder/nexus/rift/projection/view_projection.py`
   - `src/melder/nexus/acl/frame_acl_compiler.py`
   - `src/melder/nexus/rift/command_system/capability_command_system.py`
   - `src/melder/nexus/rift/command_system/codegen_command_system.py` — research and materialize operations.
4. Read source/history owners and the exact identity material they use:
   - `src/melder/mutation_research/mutation_research.py` — source/part/diff/impact, world entry and synthesis.
   - `src/melder/mutation_research/research_set/research_set.py`
   - `src/melder/mutation_research/research_set/research_node.py`
   - `src/melder/mutation_research/research_set/grouped_research_node.py`
   - `src/melder/mutation_research/research_set/network_versioner.py`
   - `src/melder/mutation_research/synthesis/structural_synthesizer.py`
   - `src/melder/crystallizer/crystals/spell_crystal.py`
   - `src/melder/aether/spellbook/bind/bind.py` — structural fingerprint versus source-version identity.
5. Before tests, read test architecture/components via indexes and the actual room/history fixtures:
   - `tests/integration/melder/mutation_research/test_research_room_commands_integration.py`
   - `tests/unit/melder/aether/test_view_spell_research_reads.py`
   - `tests/unit/melder/mutation_research/test_mutation_research_foresight.py`
   - `tests/unit/melder/mutation_research/test_mutation_research_compositions.py`
   - `tests/unit/melder/mutation_research/research_set/test_research_set.py`

## S3 Delivered Graph Input
S3 retains descriptive referenced_spell_ids on OVERRIDE_REQUIRED local socket descriptors while
leaving executable target_spell_ids empty. Position, parameter_kind, selector key and declaration
facts remain available. SpellSystemStates owns this topology; the Phase5 executable snapshot excludes
False definitions and cannot serve as the whole descriptive graph.

Read the S3 implementation task and these source owners before choosing projection payloads:
- `tickets/tasks/completed/2026-09-19_implement_override_required_compiler_task.md`
- `src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py`
- `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py`

The compiler references establish selected input relationships, not every inheritance/internal-use
edge requested for Nexus. S5 still defines and tests the public connected graph, provenance, current/
parked version views and history. Reuse existing version rules; do not infer new edges from absence
in an executable plan or treat supplied live references as lifecycle-owned objects.

## Tasks (Implementation Checklist)
- [x] Joint implementation and qualification:
  `tickets/tasks/completed/2026-09-19_publish_and_replay_non_resolvable_definitions_task.md`.
- [x] Define payloads in the scoped Nexus/crystal patch.
- [x] Add real publication/navigation tests for False definitions, bases and supplied references.
- [x] Expose capability/relationships through ACL-filtered views and preserve research commands.
- [x] Verify existing distinct-version history and graph updates after explicit notch.
- [x] Preserve candidate/adoption rules and hand native capability to S6 replay.

## Acceptance Criteria
- Agents can find a definition, traverse to/from consumers, inspect its source and compare versions.
- Non-resolvable nodes cannot be invoked through tools that should obey the runtime capability.
- Descriptive relationships survive current/parked views and graph revision selection.
- Source and graph history do not silently collapse distinct revisions into one apparent state.
- ACL/frame posture remains enforced; unavailable source/history is reported explicitly.

## Validation / Test Plan
- Real room tests pass for definition/reference/base navigation, hidden sections/endpoints, source/history,
  parked version recording and updated graph links after explicit notch. Direct False meld refuses.
- Compare two definition revisions with distinct existing identities and an explicit organization change.
  Check affected-consumer reporting; do not require same-identity body edits to create a new version.
- Prove inspection does not rely on a successful meld or an existing instance.

## UX / API / Data Notes
Agent tools address registered graph identities/revisions. Resolution is an explicit capability, not discovery.

## Risks / Mitigations
Current research reads need SpellCrystal custody, and structural bind SHA does not hash arbitrary method
bodies. The owner retained that version model; materialize/register a distinct version identity when
creating a revision rather than claiming an automatic source-body version event.

## Applicable Anti-Patterns
- [x] No source catalogue substituted for graph relationships.
- [x] No tool invocation capability inferred from visibility.
- [x] No latest-version drift or fabricated architectural ownership edges.

## Open Questions
Consume S1 answers on role vocabulary, edge provenance, revision identity and visibility before coding.

## Decision Log
- Versioned graph manifestation is required; persistence is a separate S6 implementation obligation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: accepted story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Nexus graph, permissions, registered definitions, source and relationship revisions.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-19T17:25:45Z
  TYPE: PLAN
  CLAIM: Stage first-class graph/history work rather than reducing the feature to source browsing.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:2295-2784
  - src/melder/nexus/frame_descriptor_manager.py:259-414
  - src/melder/aether/spellbook/bind/bind.py:586-698
  IMPACT: Mode and supplied-input relationships remain useful to agents and meaningful across revisions.
  NEXT: Read S1/S3 contracts and trace publication-to-projection-to-research identity before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:38:40Z
  TYPE: FACT
  CLAIM: S3 now preserves selected non-executable reference IDs and parameter/address metadata in
    local topology. False definitions are intentionally absent from executable Phase5 snapshots.
    Nexus publication and graph/history behavior have not been implemented by the compiler task.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_implement_override_required_compiler_task.md
  - artifacts/override_required_compiler_20260919/validation.md:1-18
  IMPACT: S5 has a concrete input owner and must publish the descriptive graph independently from
    constructor traversal. Existing version identity and ownership boundaries remain unchanged.
  NEXT: After S4, trace local topology and registrations into Nexus's descriptor/projection owners.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T23:28:23Z
  TYPE: FACT
  CLAIM: Existing Nexus payloads now carry capability and typed selected/reference/base links; public
    ViewSpell/FrameViewer queries preserve endpoint and section visibility. Real room/source/history
    and explicit version-selection tests pass. Existing version rules and projection refresh remain.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/validation.md
  - artifacts/non_resolvable_graph_replay_20260919/version_graph.xml:1-1
  IMPACT: The definition graph is usable without construction; no new graph registry or ownership model.
  NEXT: Owner reviews integrated S4-S7 implementation and retained limits.
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
- [x] Owner accepts graph/history behavior and evidence.
- [x] Child tasks, artifacts and boards synchronized.

## Noting Behavior
Keep graph schema and cross-subsystem revision decisions here; task notes own implementation traces.

## Context / Handoff Summary
CLOSED at 2026-09-20T00:25:59Z. Delivered ACL-filtered definition/reference/base navigation with existing source, history and version-selection workflows.
Final evidence and limits are in the graph/replay and follow-up validation artifacts.
No next implementation step remains in this accepted record.

### Historical pre-closure handoff
S5 implemented and in review. FrameDescriptorManager publishes capability and value-only typed links;
ViewSpell/FrameViewer navigate visible incoming/outgoing relationships. Late Phase3 republishes updated
references; Rift projection refresh remains explicit. Real source/history and version-selection tests
pass. Full evidence and existing limits are in the joint graph/replay task's validation artifact.
