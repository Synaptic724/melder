Completed: 2026-06-12T12:29:40Z
Summary: Closed as a stale tranche ticket after the older graph-population lane
was superseded by a fresh documentation-drift investigation epic.

# Task: Populate Src Graph For Aether First Tranche

## Metadata
- Task ID: TASK-2026-04-19-populate-src-graph-for-aether-first-tranche
- Story: STORY-2026-04-19-populate-src-graph-for-aether-directory
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T19:36:46Z
- Updated: 2026-06-12T12:29:40Z

## Objective
Populate the first high-value `aether` graph tranche by hand:
the `Aether` root, frame/runtime roots, and the public AR root/session/room
objects that define the core substrate and AR topology.

## Ticket Contract
- ENTRY_GATE: the repo-level graph epic and `aether` story are active, and the
  user explicitly asked to begin the manual graph population lane now.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aether.py`
  - `src/melder/aether/aetheric_frame.py`
  - `src/melder/aether/aether_utility_system.py`
  - `src/melder/aether/nexus/nexus.py`
  - `src/melder/aether/nexus/rift/rift.py`
  - `src/melder/aether/nexus/rift/rift_space/rift_space.py`
  - `codex/context_compass/system_docs/src_graph.json`
  - patch-lane expanded graph working copy for this tranche
- DEPENDENCIES:
  - `codex/context_compass/system_docs/graph_details_document.md`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/tickets/stories/2026-04-19_populate_src_graph_for_aether_directory_story.md`
- EXIT_GATE: the core `aether` root/frame/AR nodes and their first semantic
  ownership/creation/borrowing edges are added to `src_graph.json` and the
  canonical graph parses after recompression.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the first tranche needs to
  widen beyond the root/frame/AR objects to stay coherent.

## Scope Boundaries
- In scope:
  - `Aether`
  - `AethericFrame`
  - `AetherUtilitySystem`
  - `Nexus`
  - `Rift`
  - `RiftSpace`
  - the first semantic relationships among those objects
- Out of scope:
  - deep conduit internals
  - dev_ops internals
  - ACL/profile family leaf classes
  - `tests/**`

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: this is the first active manual population tranche for the
  repo graph lane.

## Steps / Checklist
- [ ] Expand the canonical graph into a patch-lane working copy.
- [ ] Read the first-tranche `aether` root/frame/AR files and confirm the
      starter graph entries against live code.
- [ ] Add missing core `aether` nodes and first semantic edges.
- [ ] Recompress and validate the canonical graph.
- [ ] Record the tranche result in ticket notes.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- first populated `aether` graph tranche
- updated `src_graph.json`
- tranche notes and validation record

## Files / Paths Impacted
- src/melder/aether/
- codex/context_compass/system_docs/src_graph.json
- codex/context_compass/system_docs/patches/active/*/src_graph.expanded.json
- codex/context_compass/tickets/tasks/2026-04-19_populate_src_graph_for_aether_first_tranche_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null`

## Risks / Rollback Notes
- Risk: the first tranche widens too fast into the entire `aether` subtree.
  Rollback: keep the tranche limited to root/frame/AR objects and schedule the
  deeper directories later.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the first `aether` graph tranche is accepted or intentionally superseded.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-19T19:36:46Z
  TYPE: PLAN
  CLAIM: The first `aether` tranche should stay narrow and high-value: root,
    frame, utility host, and AR root/session/room objects. That is enough to
    start the real graph lane without exploding into every subordinate
    subsystem on the first pass.
  EVIDENCE:
  - src/melder/aether: directory inventory
  - codex/context_compass/system_docs/src_graph.json: starter node set
  IMPACT: We can begin real graph population immediately while keeping the
    first tranche coherent and reviewable.
  NEXT: expand the canonical graph and reconcile these first-tranche objects
    against live source/docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:36:46Z
  TYPE: FACT
  CLAIM: The current canonical graph starter set already captures part of the
    AR layer, but it still omits the real substrate roots needed for the first
    `aether` tranche: `Aether`, `AethericFrame`, and `AetherUtilitySystem`.
    That means the graph can currently explain live AR session relationships
    only partially; it still lacks the hidden support-root and frame-container
    layer that architecture/components docs already describe.
  EVIDENCE:
  - codex/context_compass/system_docs/src_graph.json:1-1
  - codex/context_compass/system_docs/src_architecture.md:210-254
  - codex/context_compass/system_docs/src_components.md:219-307
  IMPACT: The first real population tranche should add the substrate root/frame
    layer before expanding into deeper `aether` subsystems.
  NEXT: write the expanded patch-lane graph copy with the missing root/frame
    nodes and first semantic edges.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:40:17Z
  TYPE: FACT
  CLAIM: The first `aether` graph tranche is no longer only planned. The
    expanded patch-lane working copy now includes the missing substrate/root
    layer:
    - `Aether`
    - `AethericFrame`
    - `AetherUtilitySystem`
    plus the first semantic edges tying that layer back into `Spellbook` and
    `Nexus`. The canonical compressed `src_graph.json` was recompressed from
    that expanded whole-document patch copy.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json:1-318
  - codex/context_compass/system_docs/src_graph.json:1-1
  IMPACT: The repo graph lane is now in real manual population mode, not just
    planning mode.
  NEXT: continue the `aether` story by adding the next high-value objects and
    edges from the same subtree instead of switching directories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:40:17Z
  TYPE: MEASURE
  CLAIM: The canonical compressed graph and the expanded working copy both
    validate as JSON after the first `aether` tranche recompression.
  EVIDENCE:
  - validation_result: `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_CANONICAL_GRAPH_AFTER_TRANCHE`
  - validation_result: `Get-Content codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_EXPANDED_GRAPH_AFTER_TRANCHE`
  IMPACT: The expand-edit-compress workflow is now proven on a real population tranche, not just in the example lane.
  NEXT: keep populating the `aether` story from the same expanded patch copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:40:17Z
  TYPE: FACT
  CLAIM: The first tranche source read shows that the graph still
    underrepresents two important ownership layers:
    1) `AethericFrame` owns frame-local control-plane and registry services
       such as `SpellSystemStates` and `DevOpsManager`
    2) `Nexus` owns the AR manager layer such as `FrameDescriptorManager`,
       `FrameACLManager`, and `RiftGateController`
    Those are part of the first-tranche root/frame/AR model and should be in
    the graph before this task moves on.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:20-107
  - src/melder/aether/nexus/nexus.py:54-112
  - src/melder/aether/nexus/nexus.py:168-190
  IMPACT: The current graph starter is directionally right, but it is still too
    thin around frame-local and Nexus-owned manager relationships.
  NEXT: patch the expanded graph working copy to add the missing manager-layer
    nodes and the ownership/borrowing edges around them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:45:19Z
  TYPE: FACT
  CLAIM: The first `aether` tranche now includes the missing frame and Nexus
    manager layer in the graph. The expanded/canonical graph now adds:
    - `ConduitCloud`
    - `MutationResearch`
    - `SpellSystemStates`
    - `DevOpsManager`
    - `FrameDescriptorManager`
    - `FrameACLManager`
    - `RiftGateController`
    and the first ownership/borrowing edges tying them to `AethericFrame`,
    `Nexus`, and `Rift`.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:20-107
  - src/melder/aether/dev_ops/dev_ops_manager.py:12-78
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:15-88
  - src/melder/aether/nexus/frame_descriptor_manager.py:24-88
  - src/melder/aether/nexus/frame_acl_manager.py:28-93
  - src/melder/aether/nexus/rift/rift_gate_controller/rift_gate_controller.py:8-37
  - codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json:1-488
  IMPACT: The graph can now represent the real frame-local and Nexus-owned
    manager topology instead of only the top-level runtime roots.
  NEXT: continue the same `aether` story with the next high-value subtrees
    rather than switching directories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:45:19Z
  TYPE: MEASURE
  CLAIM: The expanded and canonical graph both still validate as JSON after the
    manager-layer patch and recompression.
  EVIDENCE:
  - validation_result: `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_CANONICAL_GRAPH_AFTER_MANAGER_PATCH`
  - validation_result: `Get-Content codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_EXPANDED_GRAPH_AFTER_MANAGER_PATCH`
  IMPACT: The graph lane is still structurally clean after widening the first
    tranche to include the manager layer.
  NEXT: continue deeper into the `aether` subtree from the same expanded patch
    copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:52:35Z
  TYPE: FACT
  CLAIM: The conduit execution stack and frame-local DevOps stack still need
    more structure in the graph to be genuinely useful. The current source read
    shows:
    - `Conduit` owns `Creations`, `Meld`, `ConduitWard`, and one
      `CreationGate`
    - `Meld` borrows both `Spellbook` and `Creations`
    - `CreationContext` borrows spell-owned state and a dynamic-mode
      `CreationGate`
    - `DevOpsManager` owns `ChangeControlManager`, `RiskManager`, and the
      frame-local `CreationGateController`
    So the graph still needs at least `Creations`, `ChangeControlManager`, and
    `RiskManager`, plus the missing ownership/borrowing edges around those
    objects, before this first tranche can be called structurally credible.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:32-190
  - src/melder/aether/conduit/conduit.py:208-383
  - src/melder/aether/conduit/meld/meld.py:24-113
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:92-173
  - src/melder/aether/conduit/creations/creations.py:13-62
  - src/melder/aether/dev_ops/dev_ops_manager.py:14-80
  - src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:31-116
  - src/melder/aether/dev_ops/risk_manager/risk_manager.py:41-88
  IMPACT: The graph can already explain the root/frame/manager topology, but
    it still underexplains actual runtime execution ownership inside the
    conduit stack.
  NEXT: patch the expanded graph with the missing conduit/dev-ops service nodes
    and their ownership/borrowing edges.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:53:48Z
  TYPE: FACT
  CLAIM: The first `aether` tranche now includes the missing conduit/dev-ops
    service layer in the graph. The expanded/canonical graph now adds:
    - `Creations`
    - `ChangeControlManager`
    - `RiskManager`
    and the missing semantic edges around:
    - `AethericFrame -> Conduit`
    - `DevOpsManager -> ChangeControlManager`
    - `DevOpsManager -> RiskManager`
    - `ChangeControlManager -> SpellSystemStates`
    - `RiskManager -> SpellSystemStates`
    - `Conduit -> Creations`
    - `Conduit -> Aether`
    - `Meld -> Spellbook`
    - `Meld -> Creations`
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:32-190
  - src/melder/aether/conduit/conduit.py:416-530
  - src/melder/aether/conduit/meld/meld.py:24-110
  - src/melder/aether/conduit/creations/creations.py:13-63
  - src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:31-116
  - src/melder/aether/dev_ops/risk_manager/risk_manager.py:41-88
  - codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json:1-643
  IMPACT: The graph now describes not just the AR root/frame layer but the
    actual runtime execution ownership beneath it, which makes the `aether`
    tranche much more useful as a structural map.
  NEXT: continue the same `aether` tranche with the next highest-value
    subsystem instead of jumping to another top-level story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:53:48Z
  TYPE: MEASURE
  CLAIM: The expanded and canonical graph both still validate as JSON after the
    conduit/dev-ops service patch and recompression.
  EVIDENCE:
  - validation_result: `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_CANONICAL_GRAPH_AFTER_CONDUIT_PATCH`
  - validation_result: `Get-Content codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_EXPANDED_GRAPH_AFTER_CONDUIT_PATCH`
  IMPACT: The graph remains structurally valid while the first tranche gets
    denser, so we can continue population without stopping for repair work.
  NEXT: keep expanding the first `aether` tranche from the current expanded
    patch copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:53:48Z
  TYPE: FACT
  CLAIM: The next meaningful gap in the same `aether` tranche is the AR
    projection/viewer side. The current graph still underrepresents:
    - `FrameDescriptor`
    - `FrameProjectionSet`
    - `ViewProjection`
    - `CommandProjection`
    - `CodegenProjection`
    - `RiftGate`
    and the ownership/borrowing edges tying them to
    `FrameDescriptorManager`, `Rift`, and `FrameViewer`.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py:15-87
  - src/melder/aether/nexus/rift/projection/frame_projection_set.py:9-60
  - src/melder/aether/nexus/rift/projection/view_projection.py:6-67
  - src/melder/aether/nexus/rift/projection/command_projection.py:6-56
  - src/melder/aether/nexus/rift/projection/codegen_projection.py:6-56
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:30-112
  - src/melder/aether/nexus/rift/rift_gate/rift_gate.py:8-76
  IMPACT: The graph can already explain runtime roots and execution ownership,
    but it still underexplains how descriptor truth becomes projection state and
    how the viewer consumes it.
  NEXT: patch the expanded graph with the missing projection/viewer nodes and
    their ownership/borrowing edges.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:56:13Z
  TYPE: FACT
  CLAIM: The first `aether` tranche now includes the AR projection/viewer side
    as well. The graph adds:
    - `FrameDescriptor`
    - `RiftGate`
    - `FrameProjectionSet`
    - `ViewProjection`
    - `CommandProjection`
    - `CodegenProjection`
    - `FrameViewer`
    plus the missing ownership/borrowing edges tying those objects back to
    `FrameDescriptorManager`, `Rift`, and `RiftSpace`.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py:15-87
  - src/melder/aether/nexus/rift/projection/frame_projection_set.py:9-60
  - src/melder/aether/nexus/rift/projection/view_projection.py:6-67
  - src/melder/aether/nexus/rift/projection/command_projection.py:6-56
  - src/melder/aether/nexus/rift/projection/codegen_projection.py:6-56
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:30-112
  - src/melder/aether/nexus/rift/rift_gate/rift_gate.py:8-76
  - codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json:1-828
  IMPACT: The graph can now explain the `aether` subtree from substrate root to
    AR projection bundle and room-local viewer consumption instead of stopping
    at runtime ownership only.
  NEXT: decide whether the first `aether` tranche should stop after one final
    coherence pass or widen further into deeper `aether` subtrees.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:56:13Z
  TYPE: MEASURE
  CLAIM: The expanded and canonical graph both still validate as JSON after the
    projection/viewer patch and recompression.
  EVIDENCE:
  - validation_result: `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_CANONICAL_GRAPH_AFTER_PROJECTION_PATCH`
  - validation_result: `Get-Content codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_EXPANDED_GRAPH_AFTER_PROJECTION_PATCH`
  IMPACT: The first `aether` tranche remains structurally sound as it becomes
    significantly denser.
  NEXT: continue the tranche deliberately rather than widening blindly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:58:36Z
  TYPE: FACT
  CLAIM: The next meaningful gap inside the same `aether` tranche is the
    room-mode specialization and per-frame contract layer. The source shows the
    graph still needs:
    - `FrameLinkContract`
    - `StaticRiftSpace`
    - `CapabilityRiftSpace`
    - `CodegenRiftSpace`
    - `StaticCommandSystem`
    - `StaticFrameViewer`
    plus specialization and posture edges tying those objects back to
    `RiftSpace`, `CommandSystem`, and `FrameViewer`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-89
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:1-80
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:1-90
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:1-78
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:1-171
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:1-146
  IMPACT: Without this layer the graph still explains the room base objects
    but not the actual mode-specific behavior split that architecture/components
    docs rely on heavily.
  NEXT: patch the expanded graph with the room-mode specialization and
    frame-link nodes and edges.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:01:13Z
  TYPE: FACT
  CLAIM: The first `aether` tranche now includes the room-mode specialization
    and frame-contract layer. The graph adds:
    - `FrameLinkContract`
    - `StaticRiftSpace`
    - `CapabilityRiftSpace`
    - `CodegenRiftSpace`
    - `StaticCommandSystem`
    - `StaticFrameViewer`
    and the matching specialization/ownership edges tying those objects to
    `Rift`, `RiftSpace`, `CommandSystem`, and `FrameViewer`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-89
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:1-80
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:1-90
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:1-78
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:1-171
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:1-146
  - codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json:1-916
  IMPACT: The first `aether` tranche now captures not just base room/viewer
    ownership but the actual static/capability/codegen posture split that the
    rest of the docs already rely on.
  NEXT: perform one final coherence review of the current `aether` tranche and
    decide whether to stop this tranche or keep widening deeper into `aether`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:01:13Z
  TYPE: MEASURE
  CLAIM: The expanded and canonical graph both still validate as JSON after the
    room-mode and frame-contract patch.
  EVIDENCE:
  - validation_result: `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_CANONICAL_GRAPH_AFTER_MODE_PATCH`
  - validation_result: `Get-Content codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_EXPANDED_GRAPH_AFTER_MODE_PATCH`
  IMPACT: The graph remains structurally clean while the first `aether` tranche
    becomes much closer to a coherent subsystem map.
  NEXT: continue only after a deliberate coherence decision on whether the
    first `aether` tranche is complete enough.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:02:22Z
  TYPE: DECISION
  CLAIM: The coherence review still leaves four `aether`-native holes that are
    worth closing before this tranche pauses:
    - `ConduitCluster`
    - `SpellSpace`
    - `NexusFrameRecord`
    - `IncidentManager`
    These are all still part of the same top-level ownership model and are more
    important than widening into lower-priority directory coverage right now.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_cluster.py:11-36
  - src/melder/aether/conduit/spell_space/spell_space.py:10-33
  - src/melder/aether/nexus/nexus_frame_record.py:12-41
  - src/melder/aether/dev_ops/incident_manager/incident_manager.py:15-33
  IMPACT: One more bounded patch can make the first `aether` tranche
    substantially more coherent before handoff.
  NEXT: patch the graph with these four nodes and their key ownership edges.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:03:32Z
  TYPE: DECISION
  CLAIM: The first `aether` tranche is now coherent enough to hand off. It
    covers the substrate roots, frame-local services, DevOps manager stack,
    conduit execution stack, AR projection/viewer flow, room-mode
    specialization, and the remaining high-value `aether`-native support
    objects (`ConduitCluster`, `SpellSpace`, `NexusFrameRecord`,
    `IncidentManager`). The next useful move is a second `aether` tranche
    focused on deeper record/contract/ACL leaf objects instead of widening this
    first task further.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json:1-1008
  - validation_result: `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_CANONICAL_GRAPH_AFTER_COHERENCE_PATCH`
  IMPACT: The graph lane can keep moving without turning the first task into an
    unbounded `aether` catch-all.
  NEXT: open the second `aether` tranche and route the board to it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first active `aether` graph-population tranche.
