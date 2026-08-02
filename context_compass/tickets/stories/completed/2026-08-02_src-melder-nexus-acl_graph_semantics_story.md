

# Story: Author graph semantics for `src/melder/nexus/acl`

## Metadata
- Story ID: STORY-2026-08-02-GRAPH-SEM-src-melder-nexus-acl
- Epic: EPIC-2026-08-02-author-graph-semantics
- Status: completed
- Owner: bootstrap_0
- Agent Name: bootstrap_0
- Priority: p2
- Created: 2026-08-02T14:47:05Z
- Updated: 2026-08-02T16:30:00Z

## User Narrative
As an agent reading the source graph, I want `src/melder/nexus/acl` to carry authored
semantics, so that I can tell what its objects are FOR without re-deriving it
from the code every time.

## Value / MRP Alignment
The mechanical tier already says what exists. Without the authored tier the graph
cannot say what anything means, and every reader pays the same rediscovery cost.

## Ticket Contract
- ENTRY_GATE: active board row exists and the graph is current (`extract_graph.py --check`).
- EXECUTION_BOUNDARY: descriptors under `src/melder/nexus/acl` only. Do not author neighbouring packages.
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
- IN: authored tier for `src/melder/nexus/acl`.
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
- 39 node(s) below carry authored semantics grounded in the source.
- No node authored from its name alone.

## Validation / Test Plan
```bash
python context_compass/tools/system_documents/python/graph_walker.py \
    --descriptors <descriptors> --report --by package
```

## Nodes To Author

Unsemantic (39):
- `melder.nexus.acl.builder.frame_acl_builder`
- `melder.nexus.acl.builder.frame_acl_codegen_builder`
- `melder.nexus.acl.builder.frame_acl_command_builder`
- `melder.nexus.acl.builder.frame_acl_view_builder`
- `melder.nexus.acl.configurations.frame_acl_codegen_configuration`
- `melder.nexus.acl.configurations.frame_acl_command_configuration`
- `melder.nexus.acl.configurations.frame_acl_view_configuration`
- `melder.nexus.acl.configurations.profiles.builder.frame_acl_profile_builder`
- `melder.nexus.acl.configurations.profiles.builder.frame_acl_profile_builder._NamedCleanableProfile`
- `melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile`
- `melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile_builder`
- `melder.nexus.acl.configurations.profiles.codegen.full_access_profile.FullAccessCodegenProfileStrategy`
- `melder.nexus.acl.configurations.profiles.codegen.hybrid_profile.HybridCodegenProfileStrategy`
- `melder.nexus.acl.configurations.profiles.codegen.permissive_profile.PermissiveCodegenProfileStrategy`
- `melder.nexus.acl.configurations.profiles.codegen.precision.PrecisionCodegenProfileStrategy`
- `melder.nexus.acl.configurations.profiles.codegen.safe_profile.SafeCodegenProfileStrategy`
- `melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile`
- `melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile_builder`
- `melder.nexus.acl.configurations.profiles.command.hybrid_profile.HybridCommandProfileStrategy`
- `melder.nexus.acl.configurations.profiles.command.permissive_profile.PermissiveCommandProfileStrategy`
- `melder.nexus.acl.configurations.profiles.command.precision.PrecisionCommandProfileStrategy`
- `melder.nexus.acl.configurations.profiles.command.safe_profile.SafeCommandProfileStrategy`
- `melder.nexus.acl.configurations.profiles.frame_acl_profile`
- `melder.nexus.acl.configurations.profiles.rules.frame_acl_rule`
- `melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset`
- `melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile`
- `melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile_builder`
- `melder.nexus.acl.configurations.profiles.view.hybrid_profile.HybridViewProfileStrategy`
- `melder.nexus.acl.configurations.profiles.view.permissive_profile.PermissiveViewProfileStrategy`
- `melder.nexus.acl.configurations.profiles.view.precision.PrecisionViewProfileStrategy`
- `melder.nexus.acl.configurations.profiles.view.safe_profile.SafeViewProfileStrategy`
- `melder.nexus.acl.frame_acl_compiled_access_surface`
- `melder.nexus.acl.frame_acl_compiler`
- `melder.nexus.acl.frame_acl_configuration`
- `melder.nexus.acl.frame_acl_configuration_chain`
- `melder.nexus.acl.frame_acl_container`
- `melder.nexus.acl.validator.compatibility.frame_acl_set_compatibility_report`
- `melder.nexus.acl.validator.compatibility.frame_acl_set_compatibility_validator`
- `melder.nexus.acl.validator.frame_acl_validator`

Semantics stale (0) - source changed under existing prose, re-verify then
`graph_walker.py --accept <id> --apply`:
- none

## Open Questions
- (none recorded)

## Decision Log
- 2026-08-02T14:47:05Z: generated by `graph_semantics_tickets.py` from the graph census.
- 2026-08-02T16:30:00Z: CLOSED by bootstrap_0. All 39 nodes authored from source.
  Shape of this package: 25 of the 39 were MODULE nodes whose class was already
  authored, so the work was placement prose - where each file sits in the ACL
  layering (builder -> configuration revision -> chain -> compiler -> compiled
  access surface, with the validator pair off to the side). The 14 real class
  nodes were the profile presets. Their docstrings carry the model explicitly and
  it is worth having in the graph: `safe -> hybrid -> permissive` is a MONOTONIC
  ladder (each rung allows a superset of the previous), `precision` sits
  deliberately OUTSIDE that ordering as the enumerate-exactly posture, and
  `full_access` (codegen only) is the unconstrained top end above the ladder
  rather than a rung of it. Authored roles state which of those four positions
  each strategy holds, because the position is the fact a reader needs and the
  class name alone does not carry it. `_NamedCleanableProfile` authored as the
  structural contract (name + cleanup) that lets the three families share
  registry helpers without an inheritance relationship the domain does not have.
  `graph_walker.py --report` shows 0 unsemantic / 0 stale for this package.
- 2026-08-02T16:30:00Z: graph reassembled after this batch - 581 sections, 1199
  nodes, 1445 edges, 25,074 lines; all 581 ranges verified against their own
  headers. Repo census now 864 AUTHORED / 0 SEMANTICS_STALE / 335 UNSEMANTIC.

## Notes
- Generated. Re-running the scan UPDATES this ticket rather than creating another.
- The `GRAPH-SEM` id above is what makes that work; do not remove it.

## Context / Handoff Summary
Author the semantic tier for `src/melder/nexus/acl`. The node list is the scope. Read the
code; do not infer from names.
