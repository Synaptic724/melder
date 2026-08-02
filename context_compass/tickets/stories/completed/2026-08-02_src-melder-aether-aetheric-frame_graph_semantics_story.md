

# Story: Author graph semantics for `src/melder/aether/aetheric_frame`

## Metadata
- Story ID: STORY-2026-08-02-GRAPH-SEM-src-melder-aether-aetheric-frame
- Epic: EPIC-2026-08-02-author-graph-semantics
- Status: completed
- Owner: bootstrap_0
- Agent Name: bootstrap_0
- Priority: p2
- Created: 2026-08-02T14:47:05Z
- Updated: 2026-08-02T16:50:00Z

## User Narrative
As an agent reading the source graph, I want `src/melder/aether/aetheric_frame` to carry authored
semantics, so that I can tell what its objects are FOR without re-deriving it
from the code every time.

## Value / MRP Alignment
The mechanical tier already says what exists. Without the authored tier the graph
cannot say what anything means, and every reader pays the same rediscovery cost.

## Ticket Contract
- ENTRY_GATE: active board row exists and the graph is current (`extract_graph.py --check`).
- EXECUTION_BOUNDARY: descriptors under `src/melder/aether/aetheric_frame` only. Do not author neighbouring packages.
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
- IN: authored tier for `src/melder/aether/aetheric_frame`.
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
- 69 node(s) below carry authored semantics grounded in the source.
- No node authored from its name alone.

## Validation / Test Plan
```bash
python context_compass/tools/system_documents/python/graph_walker.py \
    --descriptors <descriptors> --report --by package
```

## Nodes To Author

Unsemantic (69):
- `melder.aether.aetheric_frame.aetheric_frame`
- `melder.aether.aetheric_frame.aetheric_frame_configuration`
- `melder.aether.aetheric_frame.conduit_cloud`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.change_control_manager`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.conflict_manager.conflict_manager`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager.AcquisitionDecision`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager.ChangeControlEmbargoRecord`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.orchestrator`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.add_spell_or_index_to_contract_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.add_spell_or_index_to_contract_transaction_strategy.AddSpellOrIndexToContractTransactionStrategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.add_to_index_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.add_to_index_transaction_strategy.AddToIndexTransactionStrategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.bind_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.cluster_join_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.cluster_join_transaction_strategy.ClusterJoinTransactionStrategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.cluster_leave_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.cluster_leave_transaction_strategy.ClusterLeaveTransactionStrategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.cluster_link_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.conjure_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.conjure_transaction_strategy.ConjureTransactionStrategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.elect_conduit_cluster_leader_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.elect_conduit_cluster_leader_transaction_strategy.ElectConduitClusterLeaderTransactionStrategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.link_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.notch_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.notch_transaction_strategy.NotchTransactionStrategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.remove_from_index_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.remove_from_index_transaction_strategy.RemoveFromIndexTransactionStrategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.remove_spell_or_index_from_contract_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.remove_spell_or_index_from_contract_transaction_strategy.RemoveSpellOrIndexFromContractTransactionStrategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy_builder`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transfer_ownership_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.unelect_conduit_cluster_leader_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.unelect_conduit_cluster_leader_transaction_strategy.UnelectConduitClusterLeaderTransactionStrategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.unlink_transaction_strategy`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_mediator`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_session`
- `melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request`
- `melder.aether.aetheric_frame.dev_ops.conduit_lineage_gate_ops`
- `melder.aether.aetheric_frame.dev_ops.conduit_lineage_gate_ops.ConduitLineageGateOps`
- `melder.aether.aetheric_frame.dev_ops.dev_ops_manager`
- `melder.aether.aetheric_frame.dev_ops.devops_identity`
- `melder.aether.aetheric_frame.dev_ops.devops_information_registry`
- `melder.aether.aetheric_frame.dev_ops.devops_information_registry.DevopsFactRecord`
- `melder.aether.aetheric_frame.dev_ops.devops_information_strategy`
- `melder.aether.aetheric_frame.dev_ops.devops_information_strategy_builder`
- `melder.aether.aetheric_frame.dev_ops.incident_manager.incident`
- `melder.aether.aetheric_frame.dev_ops.incident_manager.incident_manager`
- `melder.aether.aetheric_frame.dev_ops.incident_manager.incident_severity`
- `melder.aether.aetheric_frame.dev_ops.incident_manager.incident_status`
- `melder.aether.aetheric_frame.dev_ops.information_strategies.cluster_fanout_strategy`
- `melder.aether.aetheric_frame.dev_ops.information_strategies.frame_operational_view_strategy`
- `melder.aether.aetheric_frame.dev_ops.information_strategies.information_strategy_support`
- `melder.aether.aetheric_frame.dev_ops.information_strategies.registry_consistency_audit_strategy`
- `melder.aether.aetheric_frame.dev_ops.information_strategies.transaction_activity_view_strategy`
- `melder.aether.aetheric_frame.dev_ops.information_strategies.transfer_blast_radius_strategy`
- `melder.aether.aetheric_frame.dev_ops.risk_manager.risk_manager`
- `melder.aether.aetheric_frame.dev_ops.risk_manager.risk_manager._ConduitRiskState`
- `melder.aether.aetheric_frame.dev_ops.spell_system_states.conduit_resolution_state`
- `melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state`
- `melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason`
- `melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state`
- `melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states`
- `melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity`
- `melder.aether.aetheric_frame.lookup_container`
- `melder.aether.aetheric_frame.lookup_container.LookupContainer`

Semantics stale (0) - source changed under existing prose, re-verify then
`graph_walker.py --accept <id> --apply`:
- none

## Open Questions
- (none recorded)

## Decision Log
- 2026-08-02T14:47:05Z: generated by `graph_semantics_tickets.py` from the graph census.
- 2026-08-02T16:50:00Z: CLOSED by bootstrap_0. All 69 nodes authored from source.
  53 were MODULE nodes over already-authored classes, so those got placement prose.
  The 16 real class nodes are where the value is, and they cluster into three
  groups. (1) The change-control transaction family - eleven strategies that were
  unsemantic. Their docstrings carry a genuine model and it is now in the graph:
  every strategy is a SCOPE PLAN, not a mutation, and what distinguishes them is
  which surfaces they seal and how hard. `conjure` claims the spellbook EXCLUSIVE
  and NO conduit scope, because the root conduit id is minted mid-pipeline and does
  not exist to claim - which is also why bind's plan has a pre- and post-conjure
  shape. The three SpellIndex flows share an invariant (a spell is in exactly one
  index, so remove is a move-out to a fresh index and add GCs an emptied source),
  but only `notch` needs a runtime freeze; the two moves are structural. The
  cluster pair and the contract pair are exact inverses with matching claim modes,
  and cluster join/leave exist to supply isolation `ConduitCluster` documents
  itself as lacking. Election is light (inert clusters hard-error at the door, so
  nothing is in flight) while unelection is heavy (PARK-mode quiesce of every
  member root lineage before the domain effect). (2) The value types - embargo
  record, acquisition decision, fact record, risk bucket - authored on their
  immutability and what they let callers skip. (3) `LookupContainer` and
  `ConduitLineageGateOps`, both authored with owns_state from __slots__ and with
  the borrow/own distinction stated explicitly: the gate facade wraps the frame's
  single CreationGateController BY REFERENCE and its cleanup drops the reference
  without ever cleaning the controller, because DevOpsManager owns that lifecycle.
  `graph_walker.py --report` shows 0 unsemantic / 0 stale for this package.
- 2026-08-02T16:50:00Z: graph reassembled - 581 sections, 1199 nodes, 1445 edges,
  25,109 lines; all 581 ranges verified against their own headers. Repo census now
  933 AUTHORED / 0 SEMANTICS_STALE / 266 UNSEMANTIC (77.8%).

## Notes
- Generated. Re-running the scan UPDATES this ticket rather than creating another.
- The `GRAPH-SEM` id above is what makes that work; do not remove it.

## Context / Handoff Summary
Author the semantic tier for `src/melder/aether/aetheric_frame`. The node list is the scope. Read the
code; do not infer from names.
