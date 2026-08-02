

# Story: Author graph semantics for `src/melder/crystallizer/crystal_analysis`

## Metadata
- Story ID: STORY-2026-08-02-GRAPH-SEM-src-melder-crystallizer-crystal-analysis
- Epic: EPIC-2026-08-02-author-graph-semantics
- Status: completed
- Owner: bootstrap_0
- Agent Name: bootstrap_0
- Priority: p2
- Created: 2026-08-02T14:47:05Z
- Updated: 2026-08-02T16:05:00Z

## User Narrative
As an agent reading the source graph, I want `src/melder/crystallizer/crystal_analysis` to carry authored
semantics, so that I can tell what its objects are FOR without re-deriving it
from the code every time.

## Value / MRP Alignment
The mechanical tier already says what exists. Without the authored tier the graph
cannot say what anything means, and every reader pays the same rediscovery cost.

## Ticket Contract
- ENTRY_GATE: active board row exists and the graph is current (`extract_graph.py --check`).
- EXECUTION_BOUNDARY: descriptors under `src/melder/crystallizer/crystal_analysis` only. Do not author neighbouring packages.
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
- IN: authored tier for `src/melder/crystallizer/crystal_analysis`.
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
- 45 node(s) below carry authored semantics grounded in the source.
- No node authored from its name alone.

## Validation / Test Plan
```bash
python context_compass/tools/system_documents/python/graph_walker.py \
    --descriptors <descriptors> --report --by package
```

## Nodes To Author

Unsemantic (45):
- `melder.crystallizer.crystal_analysis.crystal_analysis_result.CrystalAnalysisResult`
- `melder.crystallizer.crystal_analysis.crystal_analyzer.CrystalAnalyzer`
- `melder.crystallizer.crystal_analysis.custody.binary_unknown_custody_strategy`
- `melder.crystallizer.crystal_analysis.custody.binary_unknown_custody_strategy.BinaryUnknownCustodyStrategy`
- `melder.crystallizer.crystal_analysis.custody.site_package_custody_strategy`
- `melder.crystallizer.crystal_analysis.custody.site_package_custody_strategy.SitePackageCustodyStrategy`
- `melder.crystallizer.crystal_analysis.custody.source_custody_strategy`
- `melder.crystallizer.crystal_analysis.custody.source_custody_strategy.SourceCustodyStrategy`
- `melder.crystallizer.crystal_analysis.custody.synthetic_custody_strategy`
- `melder.crystallizer.crystal_analysis.custody.synthetic_custody_strategy.SyntheticCustodyStrategy`
- `melder.crystallizer.crystal_analysis.custody.user_source_custody_strategy`
- `melder.crystallizer.crystal_analysis.custody.user_source_custody_strategy.UserSourceCustodyStrategy`
- `melder.crystallizer.crystal_analysis.impact_engine`
- `melder.crystallizer.crystal_analysis.physical_source_cache`
- `melder.crystallizer.crystal_analysis.physical_source_cache.PhysicalSourceCache`
- `melder.crystallizer.crystal_analysis.preflight.cluster_membership_strategy`
- `melder.crystallizer.crystal_analysis.preflight.cluster_membership_strategy.ClusterMembershipStrategy`
- `melder.crystallizer.crystal_analysis.preflight.configuration_loss_strategy`
- `melder.crystallizer.crystal_analysis.preflight.configuration_loss_strategy.ConfigurationLossStrategy`
- `melder.crystallizer.crystal_analysis.preflight.contract_peer_strategy`
- `melder.crystallizer.crystal_analysis.preflight.contract_peer_strategy.ContractPeerStrategy`
- `melder.crystallizer.crystal_analysis.preflight.frame_posture_strategy`
- `melder.crystallizer.crystal_analysis.preflight.frame_posture_strategy.FramePostureStrategy`
- `melder.crystallizer.crystal_analysis.preflight.hydration_strategy`
- `melder.crystallizer.crystal_analysis.preflight.hydration_strategy.HydrationStrategy`
- `melder.crystallizer.crystal_analysis.preflight.link_integrity_strategy`
- `melder.crystallizer.crystal_analysis.preflight.link_integrity_strategy.LinkIntegrityStrategy`
- `melder.crystallizer.crystal_analysis.preflight.mutation_research_composition_strategy`
- `melder.crystallizer.crystal_analysis.preflight.mutation_research_composition_strategy.MutationResearchCompositionStrategy`
- `melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy`
- `melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy.PersistenceAnalysisStrategy`
- `melder.crystallizer.crystal_analysis.preflight.persistence_analyzer`
- `melder.crystallizer.crystal_analysis.preflight.persistence_analyzer.PersistenceAnalyzer`
- `melder.crystallizer.crystal_analysis.preflight.source_drift_strategy`
- `melder.crystallizer.crystal_analysis.preflight.source_drift_strategy.SourceDriftStrategy`
- `melder.crystallizer.crystal_analysis.preflight.synthetic_source_integrity_strategy`
- `melder.crystallizer.crystal_analysis.preflight.synthetic_source_integrity_strategy.SyntheticSourceIntegrityStrategy`
- `melder.crystallizer.crystal_analysis.preflight.user_source_integrity_strategy`
- `melder.crystallizer.crystal_analysis.preflight.user_source_integrity_strategy.UserSourceIntegrityStrategy`
- `melder.crystallizer.crystal_analysis.strategies.base_strategy.CrystalFactStrategy`
- `melder.crystallizer.crystal_analysis.strategies.base_strategy.FactContext`
- `melder.crystallizer.crystal_analysis.strategies.dependency_view_strategy.DependencyViewStrategy`
- `melder.crystallizer.crystal_analysis.strategies.export_surface_strategy.ExportSurfaceStrategy`
- `melder.crystallizer.crystal_analysis.strategies.from_import_statement_strategy.FromImportStatementStrategy`
- `melder.crystallizer.crystal_analysis.strategies.import_statement_strategy.ImportStatementStrategy`

Semantics stale (0) - source changed under existing prose, re-verify then
`graph_walker.py --accept <id> --apply`:
- none

## Open Questions
- (none recorded)

## Decision Log
- 2026-08-02T14:47:05Z: generated by `graph_semantics_tickets.py` from the graph census.
- 2026-08-02T16:05:00Z: CLOSED by bootstrap_0. All 45 nodes authored from source.
  `graph_walker.py --report --by package` shows 0 unsemantic / 0 stale for
  `src/melder/crystallizer/crystal_analysis`. Graph reassembled: 581 sections,
  1199 nodes, 1445 edges, 25046 lines; all 581 ranges verified against their own
  headers; index proof recomputed and matched (line_count 25046, LF,
  content_sha256 `b50974b0...`).
- 2026-08-02T16:05:00Z: DEFECT FOUND AND FIXED while closing this story - the
  staleness detector was inert repo-wide. `semantics_authored_against` must hold
  the node's own `span_sha256`; every stamp written this session held the FILE's
  `source_sha256` instead - precisely the failure `span_sha()` documents ("a
  file-level hash marks every node in a 40-class module stale because one class
  changed"). Compounding it, the descriptors carried no `span_sha256` at all
  (the migration dropped the field), so `state_of()` short-circuited and
  reported 0 stale because it could not compare, not because nothing was stale.
  Fix: re-ran `extract_graph.py` (mechanical refresh restored `span_sha256`;
  425 unstamped nodes grandfathered by the tool), then `graph_walker.py --accept`
  on the 66 wrongly-stamped nodes. 65 of those were provably safe - their stamp
  equalled their file's CURRENT `source_sha256`, so the source had not moved
  since authoring. The 1 that was not provable
  (`_build_assets._system_documents._builder.SystemDocumentsBuildPolicy`) was
  re-read before accepting, and its thin `responsibilities` corrected in the
  process. Census now: 770 AUTHORED / 0 STALE / 429 UNSEMANTIC over 1199 nodes,
  and all 491 authored class nodes carry a live per-node stamp.
- 2026-08-02T16:05:00Z: OPEN GAP, not fixed here - `extract_graph.py` computes
  `span_sha256` for `ast.ClassDef` only, so the 279 authored MODULE nodes have
  no span and their staleness can never fire. The file's `source_sha256` is
  already in the descriptor and is the natural span for a module node. Recorded
  for the tooling handoff rather than patched mid-story; out of this ticket's
  EXECUTION_BOUNDARY.

## Notes
- Generated. Re-running the scan UPDATES this ticket rather than creating another.
- The `GRAPH-SEM` id above is what makes that work; do not remove it.

## Context / Handoff Summary
Author the semantic tier for `src/melder/crystallizer/crystal_analysis`. The node list is the scope. Read the
code; do not infer from names.
