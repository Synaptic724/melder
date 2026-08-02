

# Story: Author graph semantics for `src/melder/aether/aetheric_mediator`

## Metadata
- Story ID: STORY-2026-08-02-GRAPH-SEM-src-melder-aether-aetheric-mediator
- Epic: EPIC-2026-08-02-author-graph-semantics
- Status: draft
- Owner:
- Agent Name:
- Priority: p2
- Created: 2026-08-02T14:47:05Z
- Updated: 2026-08-02T14:47:05Z

## User Narrative
As an agent reading the source graph, I want `src/melder/aether/aetheric_mediator` to carry authored
semantics, so that I can tell what its objects are FOR without re-deriving it
from the code every time.

## Value / MRP Alignment
The mechanical tier already says what exists. Without the authored tier the graph
cannot say what anything means, and every reader pays the same rediscovery cost.

## Ticket Contract
- ENTRY_GATE: active board row exists and the graph is current (`extract_graph.py --check`).
- EXECUTION_BOUNDARY: descriptors under `src/melder/aether/aetheric_mediator` only. Do not author neighbouring packages.
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
- IN: authored tier for `src/melder/aether/aetheric_mediator`.
- OUT: mechanical fields, other packages, refactoring the source.

## State Transition Event
- draft -> ready when an agent claims it on the attention board.

## Dependencies / Related Work
- Epic: EPIC-2026-08-02-author-graph-semantics

## Tasks (Implementation Checklist)
- [ ] Read the source for each node below.
- [ ] Author the semantic fields in the descriptors.
- [ ] Reassemble the graph and verify ranges.
- [ ] `graph_walker.py --report` shows this package clean.

## Acceptance Criteria
- 38 node(s) below carry authored semantics grounded in the source.
- No node authored from its name alone.

## Validation / Test Plan
```bash
python context_compass/tools/system_documents/python/graph_walker.py \
    --descriptors <descriptors> --report --by package
```

## Nodes To Author

Unsemantic (38):
- `melder.aether.aetheric_mediator.admission_orchestrator`
- `melder.aether.aetheric_mediator.admission_orchestrator.AdmissionOrchestrator`
- `melder.aether.aetheric_mediator.admission_result`
- `melder.aether.aetheric_mediator.admission_result.AdmissionReason`
- `melder.aether.aetheric_mediator.admission_result.AdmissionResult`
- `melder.aether.aetheric_mediator.claim_mode`
- `melder.aether.aetheric_mediator.claim_mode.ClaimCompatibility`
- `melder.aether.aetheric_mediator.claim_mode.ClaimMode`
- `melder.aether.aetheric_mediator.claim_table`
- `melder.aether.aetheric_mediator.claim_table.ClaimBlock`
- `melder.aether.aetheric_mediator.claim_table.ClaimTable`
- `melder.aether.aetheric_mediator.claim_table._GrantedClaim`
- `melder.aether.aetheric_mediator.identity`
- `melder.aether.aetheric_mediator.identity.Identity`
- `melder.aether.aetheric_mediator.information_registry`
- `melder.aether.aetheric_mediator.information_registry.FactRecord`
- `melder.aether.aetheric_mediator.information_registry.InformationRegistry`
- `melder.aether.aetheric_mediator.mediator`
- `melder.aether.aetheric_mediator.mediator.Mediator`
- `melder.aether.aetheric_mediator.scope_keys`
- `melder.aether.aetheric_mediator.scope_keys.ScopeKey`
- `melder.aether.aetheric_mediator.scope_keys.ScopePrefix`
- `melder.aether.aetheric_mediator.staged_transaction`
- `melder.aether.aetheric_mediator.staged_transaction.StagedTransaction`
- `melder.aether.aetheric_mediator.strategy_builder`
- `melder.aether.aetheric_mediator.strategy_builder.StrategyBuilder`
- `melder.aether.aetheric_mediator.transaction_request`
- `melder.aether.aetheric_mediator.transaction_request.MetadataPolicy`
- `melder.aether.aetheric_mediator.transaction_request.TransactionRequest`
- `melder.aether.aetheric_mediator.transaction_session`
- `melder.aether.aetheric_mediator.transaction_session.OutcomePolicy`
- `melder.aether.aetheric_mediator.transaction_session.SessionStatus`
- `melder.aether.aetheric_mediator.transaction_session.TransactionSession`
- `melder.aether.aetheric_mediator.transaction_session._RollbackAction`
- `melder.aether.aetheric_mediator.transaction_strategy`
- `melder.aether.aetheric_mediator.transaction_strategy.TransactionStrategy`
- `melder.aether.aetheric_mediator.transaction_type`
- `melder.aether.aetheric_mediator.transaction_type.TransactionType`

Semantics stale (0) - source changed under existing prose, re-verify then
`graph_walker.py --accept <id> --apply`:
- none

## Open Questions
- (none recorded)

## Decision Log
- 2026-08-02T14:47:05Z: generated by `graph_semantics_tickets.py` from the graph census.

## Notes
- Generated. Re-running the scan UPDATES this ticket rather than creating another.
- The `GRAPH-SEM` id above is what makes that work; do not remove it.

## Context / Handoff Summary
Author the semantic tier for `src/melder/aether/aetheric_mediator`. The node list is the scope. Read the
code; do not infer from names.
