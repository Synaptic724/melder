
- Completed: 2026-08-02T16:30:00Z
- Summary: Authored the semantic tier for `src/melder/aether/conduit` by reading each source file.
  0 unsemantic and 0 stale for this package; graph reassembled, index verified.
  Nodes stamped `semantics_authored_against` so the prose participates in
  staleness detection instead of silently going wrong when the code moves.


# Story: Author graph semantics for `src/melder/aether/conduit`

## Metadata
- Story ID: STORY-2026-08-02-GRAPH-SEM-src-melder-aether-conduit
- Epic: EPIC-2026-08-02-author-graph-semantics
- Status: done
- Owner: cowork
- Agent Name: bootstrap_0
- Priority: p2
- Created: 2026-08-02T14:47:05Z
- Updated: 2026-08-02T14:47:05Z

## User Narrative
As an agent reading the source graph, I want `src/melder/aether/conduit` to carry authored
semantics, so that I can tell what its objects are FOR without re-deriving it
from the code every time.

## Value / MRP Alignment
The mechanical tier already says what exists. Without the authored tier the graph
cannot say what anything means, and every reader pays the same rediscovery cost.

## Ticket Contract
- ENTRY_GATE: active board row exists and the graph is current (`extract_graph.py --check`).
- EXECUTION_BOUNDARY: descriptors under `src/melder/aether/conduit` only. Do not author neighbouring packages.
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
- IN: authored tier for `src/melder/aether/conduit`.
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
- 31 node(s) below carry authored semantics grounded in the source.
- No node authored from its name alone.

## Validation / Test Plan
```bash
python context_compass/tools/system_documents/python/graph_walker.py \
    --descriptors <descriptors> --report --by package
```

## Nodes To Author

Unsemantic (31):
- `melder.aether.conduit.conduit`
- `melder.aether.conduit.conduit_cluster`
- `melder.aether.conduit.conduit_pool`
- `melder.aether.conduit.conduit_state.conduit_state`
- `melder.aether.conduit.conduit_ward.conduit_ward`
- `melder.aether.conduit.conduit_ward.contract.contract`
- `melder.aether.conduit.conduit_ward.contract.contract_types.contract_types`
- `melder.aether.conduit.conduit_ward.contract.detail_reason`
- `melder.aether.conduit.conduit_ward.contract.details`
- `melder.aether.conduit.conduit_ward.contract.details.IndexDetail`
- `melder.aether.conduit.conduit_ward.permissions.permissions`
- `melder.aether.conduit.conduit_ward.policies.policies`
- `melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership`
- `melder.aether.conduit.creations.cluster_creations`
- `melder.aether.conduit.creations.cluster_creations.ClusterCreations`
- `melder.aether.conduit.creations.conduit_creations`
- `melder.aether.conduit.creations.creations`
- `melder.aether.conduit.meld.conduit_meld`
- `melder.aether.conduit.meld.contracts.spell_contract`
- `melder.aether.conduit.meld.contracts.spell_map`
- `melder.aether.conduit.meld.creation_context.creation_context`
- `melder.aether.conduit.meld.creation_context.creation_context_builder`
- `melder.aether.conduit.meld.creation_context.creation_context_factory`
- `melder.aether.conduit.meld.meld`
- `melder.aether.conduit.meld.overrides.spell_overrider`
- `melder.aether.conduit.meld.overrides.spell_overrider._Specificity`
- `melder.aether.conduit.meld.spellspace_meld`
- `melder.aether.conduit.spell_space.spell_space`
- `melder.aether.conduit.spell_space.spell_space_pool`
- `melder.aether.conduit.spell_space.spell_space_thread_state`
- `melder.aether.conduit.spell_space.spell_space_thread_state._SpellSpaceLocal`

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
Author the semantic tier for `src/melder/aether/conduit`. The node list is the scope. Read the
code; do not infer from names.
