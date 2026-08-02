

# Story: Author graph semantics for `src/melder/nexus/rift`

## Metadata
- Story ID: STORY-2026-08-02-GRAPH-SEM-src-melder-nexus-rift
- Epic: EPIC-2026-08-02-author-graph-semantics
- Status: completed
- Owner: bootstrap_0
- Agent Name: bootstrap_0
- Priority: p2
- Created: 2026-08-02T14:47:05Z
- Updated: 2026-08-02T16:30:00Z

## User Narrative
As an agent reading the source graph, I want `src/melder/nexus/rift` to carry authored
semantics, so that I can tell what its objects are FOR without re-deriving it
from the code every time.

## Value / MRP Alignment
The mechanical tier already says what exists. Without the authored tier the graph
cannot say what anything means, and every reader pays the same rediscovery cost.

## Ticket Contract
- ENTRY_GATE: active board row exists and the graph is current (`extract_graph.py --check`).
- EXECUTION_BOUNDARY: descriptors under `src/melder/nexus/rift` only. Do not author neighbouring packages.
- DEPENDENCIES: EPIC-2026-08-02-author-graph-semantics
- EXIT_GATE: every node below carries `role` and `responsibilities`; `graph_walker.py --report` shows 0 unsemantic and 0 stale for this package; graph reassembled.
- FAILURE_ESCALATION: raise DECISION_REQUEST if a node's purpose cannot be established from source.

## Requirements (Functional)
- Author `role` and `responsibilities` for each node listed below.
- Author `owns_state` and `phases` where the source supports them.
- Author `edges_authored` for relationships this package owns or borrows.

## Requirements (Non-Functional)
- **Semantics must be authored by READING THE CODE.** Never inferred from names.
- `owns_lifecycle_of`, `uses` and `borrows` are syntactically identical - `self._x = x`
  in all three cases. The difference is design intent that appears nowhere in the
  source text. Measured on a labelled corpus, a cleanup-contract heuristic
  discriminated at 21% vs 21% - no signal at all. Invented semantics are worse
  than none, because they read as verified.

## Scope Boundaries
- IN: authored tier for `src/melder/nexus/rift`.
- OUT: mechanical fields, other packages, refactoring the source.

## State Transition Event
- draft -> ready when an agent claims it on the attention board.

## Dependencies / Related Work
- Epic: EPIC-2026-08-02-author-graph-semantics

## Tasks (Implementation Checklist)
- [x] Read the source for each node below.
- [x] Author the semantic fields in the descriptors.
- [x] Reassemble the graph and verify ranges.
- [x] `graph_walker.py --report` shows this package clean.

## Acceptance Criteria
- 55 node(s) below carry authored semantics grounded in the source.
- No node authored from its name alone.

## Validation / Test Plan
```bash
python context_compass/tools/system_documents/python/graph_walker.py \
    --descriptors <descriptors> --report --by package
```

## Nodes To Author

Unsemantic (55):
- `melder.nexus.rift.codegen_system.codegen_system`
- `melder.nexus.rift.codegen_system.codegen_transaction_context`
- `melder.nexus.rift.codegen_system.execution.codegen_compiler`
- `melder.nexus.rift.codegen_system.execution.codegen_execution_result`
- `melder.nexus.rift.codegen_system.execution.codegen_executor`
- `melder.nexus.rift.codegen_system.namespace.codegen_control_surface`
- `melder.nexus.rift.codegen_system.namespace.codegen_namespace`
- `melder.nexus.rift.codegen_system.namespace.codegen_namespace_builder`
- `melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration`
- `melder.nexus.rift.codegen_system.namespace.strategies.codegen_builtins_strategy`
- `melder.nexus.rift.codegen_system.namespace.strategies.codegen_command_strategy`
- `melder.nexus.rift.codegen_system.namespace.strategies.codegen_control_strategy`
- `melder.nexus.rift.codegen_system.namespace.strategies.codegen_room_objects_strategy`
- `melder.nexus.rift.codegen_system.namespace.strategies.codegen_target_strategy`
- `melder.nexus.rift.codegen_system.namespace.strategies.codegen_workstation_strategy`
- `melder.nexus.rift.codegen_system.observability.codegen_event_publisher`
- `melder.nexus.rift.codegen_system.observability.codegen_monitor`
- `melder.nexus.rift.codegen_system.validation.codegen_validation_reporter`
- `melder.nexus.rift.codegen_system.validation.codegen_validation_result`
- `melder.nexus.rift.codegen_system.validation.codegen_validator`
- `melder.nexus.rift.codegen_system.validation.strategies.codegen_ast_structure_strategy`
- `melder.nexus.rift.codegen_system.validation.strategies.codegen_attribute_access_strategy`
- `melder.nexus.rift.codegen_system.validation.strategies.codegen_builtin_policy_strategy`
- `melder.nexus.rift.codegen_system.validation.strategies.codegen_import_policy_strategy`
- `melder.nexus.rift.codegen_system.validation.strategies.codegen_name_resolution_strategy`
- `melder.nexus.rift.codegen_system.validation.strategies.codegen_recursive_control_strategy`
- `melder.nexus.rift.codegen_system.validation.strategies.codegen_reflection_policy_strategy`
- `melder.nexus.rift.command_system.capability_command_system`
- `melder.nexus.rift.command_system.codegen_command_system`
- `melder.nexus.rift.command_system.command_system`
- `melder.nexus.rift.command_system.static_command_system`
- `melder.nexus.rift.frame_link.frame_link`
- `melder.nexus.rift.frame_link.frame_link_contract`
- `melder.nexus.rift.frame_viewer.frame_viewer`
- `melder.nexus.rift.frame_viewer.static_frame_viewer`
- `melder.nexus.rift.frame_viewer.view_conduit`
- `melder.nexus.rift.frame_viewer.view_frame`
- `melder.nexus.rift.frame_viewer.view_multiframe`
- `melder.nexus.rift.frame_viewer.view_spell`
- `melder.nexus.rift.projection.codegen_projection`
- `melder.nexus.rift.projection.command_projection`
- `melder.nexus.rift.projection.frame_projection_set`
- `melder.nexus.rift.projection.view_projection`
- `melder.nexus.rift.rift`
- `melder.nexus.rift.rift_gate.rift_gate`
- `melder.nexus.rift.rift_gate_controller.rift_gate_controller`
- `melder.nexus.rift.rift_space.capability_rift_space`
- `melder.nexus.rift.rift_space.codegen_rift_space`
- `melder.nexus.rift.rift_space.event_system.rift_event`
- `melder.nexus.rift.rift_space.event_system.rift_event_system`
- `melder.nexus.rift.rift_space.memory_system.rift_memory`
- `melder.nexus.rift.rift_space.memory_system.rift_memory_system`
- `melder.nexus.rift.rift_space.rift_space`
- `melder.nexus.rift.rift_space.static_rift_space`
- `melder.nexus.rift.rift_space.workstation`

Semantics stale (0) - source changed under existing prose, re-verify then
`graph_walker.py --accept <id> --apply`:
- none

## Open Questions
- (none recorded)

## Decision Log
- 2026-08-02T14:47:05Z: generated by `graph_semantics_tickets.py` from the graph census.
- 2026-08-02T16:30:00Z: CLOSED by bootstrap_0. All 55 nodes authored from source.
  Every one of the 55 was a MODULE node - the classes in this package were already
  authored - so the deliverable was placement, not restatement. Roles were written
  from the `Subsystem Context` / `System Context` sections of each file's class
  docstring, which carry the layering facts a file listing cannot: the room triad
  (FrameViewer reads / CommandSystem mediates / Workstation binds, and commands
  deliberately store nothing so results must land on the workstation); the room
  CAPABILITY LADDER static -> capability -> codegen trading reach for safety; the
  codegen engine's ordering invariant (VALIDATE BEFORE EXECUTE, namespace built
  only after validation is accepted, so a rejected request never materializes its
  execution environment); FrameProjectionSet's generation marker as what allows
  the three projections to swap as one coherent unit; and the gate pair, where
  RiftGate is the admission primitive (reversible blocking for refresh, one-way
  close for shutdown) and RiftGateController is the Nexus-owned control plane that
  makes an ACL fan-out a coordinated block/drain/refresh/reopen across many Rifts.
  `graph_walker.py --report` shows 0 unsemantic / 0 stale for this package.
- 2026-08-02T16:30:00Z: graph reassembled after this batch - 581 sections, 1199
  nodes, 1445 edges, 25,074 lines; all 581 ranges verified against their own
  headers. Repo census now 864 AUTHORED / 0 SEMANTICS_STALE / 335 UNSEMANTIC.

## Notes
- Generated. Re-running the scan UPDATES this ticket rather than creating another.
- The `GRAPH-SEM` id above is what makes that work; do not remove it.

## Context / Handoff Summary
Author the semantic tier for `src/melder/nexus/rift`. The node list is the scope. Read the
code; do not infer from names.
