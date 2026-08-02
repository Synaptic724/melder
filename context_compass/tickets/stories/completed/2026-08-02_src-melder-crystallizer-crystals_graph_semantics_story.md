
- Completed: 2026-08-02T15:30:00Z
- Summary: Authored 12 module + 11 class/enum nodes for `src/melder/crystallizer/crystals` by reading each source file.
  `graph_walker.py --report` shows 0 unsemantic and 0 stale for this package;
  graph reassembled and index verified (line_count + content_sha256).
  Each node stamped `semantics_authored_against` with its file's current
  source_sha256, so the prose now participates in staleness detection instead
  of silently going wrong when the code moves.


# Story: Author graph semantics for `src/melder/crystallizer/crystals`

## Metadata
- Story ID: STORY-2026-08-02-GRAPH-SEM-src-melder-crystallizer-crystals
- Epic: EPIC-2026-08-02-author-graph-semantics
- Status: done
- Owner: cowork
- Agent Name: bootstrap_0
- Priority: p2
- Created: 2026-08-02T14:47:05Z
- Updated: 2026-08-02T14:47:05Z

## User Narrative
As an agent reading the source graph, I want `src/melder/crystallizer/crystals` to carry authored
semantics, so that I can tell what its objects are FOR without re-deriving it
from the code every time.

## Value / MRP Alignment
The mechanical tier already says what exists. Without the authored tier the graph
cannot say what anything means, and every reader pays the same rediscovery cost.

## Ticket Contract
- ENTRY_GATE: active board row exists and the graph is current (`extract_graph.py --check`).
- EXECUTION_BOUNDARY: descriptors under `src/melder/crystallizer/crystals` only. Do not author neighbouring packages.
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
- IN: authored tier for `src/melder/crystallizer/crystals`.
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
- 23 node(s) below carry authored semantics grounded in the source.
- No node authored from its name alone.

## Validation / Test Plan
```bash
python context_compass/tools/system_documents/python/graph_walker.py \
    --descriptors <descriptors> --report --by package
```

## Nodes To Author

Unsemantic (23):
- `melder.crystallizer.crystals.aether_crystal`
- `melder.crystallizer.crystals.aether_crystal.AetherCrystal`
- `melder.crystallizer.crystals.aetheric_frame_crystal`
- `melder.crystallizer.crystals.aetheric_frame_crystal.AethericFrameCrystal`
- `melder.crystallizer.crystals.cluster_crystal`
- `melder.crystallizer.crystals.cluster_crystal.ClusterCrystal`
- `melder.crystallizer.crystals.conduit_crystal`
- `melder.crystallizer.crystals.conduit_crystal.ConduitCrystal`
- `melder.crystallizer.crystals.contract_crystal`
- `melder.crystallizer.crystals.contract_crystal.ContractCrystal`
- `melder.crystallizer.crystals.crystallizer_crystal`
- `melder.crystallizer.crystals.crystallizer_crystal.CrystallizerCrystal`
- `melder.crystallizer.crystals.mutation_research_crystal`
- `melder.crystallizer.crystals.mutation_research_crystal.MutationResearchCrystal`
- `melder.crystallizer.crystals.nexus_crystal`
- `melder.crystallizer.crystals.nexus_crystal.NexusCrystal`
- `melder.crystallizer.crystals.recorded_unit_state`
- `melder.crystallizer.crystals.recorded_unit_state.RecordedUnitState`
- `melder.crystallizer.crystals.spell_crystal`
- `melder.crystallizer.crystals.spell_index_crystal`
- `melder.crystallizer.crystals.spell_index_crystal.SpellIndexCrystal`
- `melder.crystallizer.crystals.spellbook_crystal`
- `melder.crystallizer.crystals.spellbook_crystal.SpellbookCrystal`

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
Author the semantic tier for `src/melder/crystallizer/crystals`. The node list is the scope. Read the
code; do not infer from names.
