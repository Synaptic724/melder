# Patch lane: graph_dangling_edge_repair_2026_07_18

STATUS: CONSUMED 2026-07-18T23:45:00Z by melder_0. Do NOT reuse the expanded copy in this lane.

## What this lane did
Expand-edit-compress pass over the canonical graph (per
`agent_onboarding/default/design_engineer/skills/graph_details_instructions.md:79-96`):

- added node `...embargo_manager.embargo_manager.ClaimMode` (StrEnum, `embargo_manager.py:19`)
- added node `...profiles.resolution_profile.SpellResolutionProfile` (`resolution_profile.py:322`)
- repaired 2 edge endpoints that had dropped the `.SharedCompilerExecutions` class suffix

Result: 535 -> 537 nodes, 1002 edges unchanged, dangling edges 5 -> 0. Recompressed into
`system_docs/src_graph.json` and regenerated `system_docs/readable_src_graph.json` at 220-width.

## Why src_graph.expanded.json is still here
Deletion was attempted at lane closure and failed with `Operation not permitted` (the same
mount permission condition that blocked git from unlinking its temp objects this session).

**That file is STALE the moment canonical storage moves on.** It is a point-in-time working
copy, not a source of truth. This lane exists as a cautionary marker precisely because a
comparable orphan already sits in `populate_src_graph_aether_first_tranche/` holding only
300 nodes / 380 edges against canonical 537 / 1002 - reusing it would silently regress the
graph.

## Correct action for the next maintainer
Delete `src_graph.expanded.json` from this lane, then remove the lane. To edit the graph,
start a NEW lane and expand from current canonical storage - never from a leftover copy.
