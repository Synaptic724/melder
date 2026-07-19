# Patch lane: graph_schema_drift_normalization_2026_07_18

STATUS: CONSUMED 2026-07-19T00:05:00Z by melder_0. Do NOT reuse the expanded copy in this lane.

Encoding-only normalization: 69 field corrections (strength/cardinality/phase vocabulary and
required-field backfill, plus 5 nodes given `owns_state` from source `__slots__`). Topology
untouched at 537 nodes / 1002 edges. Recompressed to `system_docs/src_graph.json` and
reflowed to `system_docs/readable_src_graph.json`.

`src_graph.expanded.json` here is a point-in-time working copy and is STALE as soon as
canonical storage moves on. Deletion at closure was blocked by the mount (`Operation not
permitted`). Next maintainer: delete it and remove this lane. To edit the graph, expand fresh
from current canonical storage - never from a leftover copy.
