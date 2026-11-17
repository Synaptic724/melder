# component_patch_crystal_analysis

## Metadata
- Patch ID: configure_in_seconds_2026_11_17
- Component: crystal analysis (`crystallizer/crystal_analysis/`: `ModuleAnswerCache`, `CrystalAnalyzer`,
  `DependencyViewStrategy`)
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Ticket: https://github.com/Synaptic724/melder/issues/331
- Created: 2026-11-17T12:05:00Z
- Updated: 2026-11-17T12:32:22Z

## Component Purpose and Boundary
- A spell crystal records its root module's world. Since 0.2.8305 a repeat root module copies its kept world; a new
  root module still walks its world, answering each import target once per pass. This patch moves the first-seen
  answer of each import target across passes and makes the walk's final ordering logarithmic per pick.

## Before/After Behavior Summary
- Before: the first edge to a target in each pass called `resolve_module_path` (a `ModuleAnswerCache` path lookup
  plus a `Path` built from text), then `_match_custody` (a `Path`-keyed pass lookup, `str(Path)` and a custody-kind
  lookup) and, for a leaf, the path's suffix. MelderOps' 298 walks made 464,900 edge answers this way.
  `DependencyViewStrategy.finalize` ran Kahn's algorithm over a sorted list: `pop(0)` and a full re-sort per ready
  node.
- After: the first edge to a target in a pass asks `ModuleAnswerCache.lookup_edge_answer` once and, on a hit,
  builds its pass edge from the kept path object, this analyzer's strategy of the kept kind and the kept leaf
  record; on a miss it computes as before and stores the answer. `finalize` keeps ready nodes in a min-heap: the
  same order, O(log V) per pick.

## Interface Deltas
- `ModuleAnswerCache.lookup_edge_answer(policy_key, module_name, module_obj, file_text)` returns the kept
  (path, custody kind, leaf record) or None; `store_edge_answer(...)` keeps one. Per policy key, keyed by module name;
  the entry carries a weak reference to the module object (or none), the `__file__` text and, with no object,
  `sys.path`. Bounded and LRU-evicted like the other maps; `_stats_for_tests` counts it.
- `CrystalAnalyzer._resolve_pass_edge` consults it on a per-pass miss when the analyzer keys answers (default
  chains) and the target is not synthetic.

## State and Lifecycle Deltas
- One more process-wide map of values and weak references; nothing holds a module or source text.

## Failure Mode Deltas
- None new: an entry that fails its guard is recomputed and replaced, as the path and custody entries are.

## Dependency and Ordering Constraints
- The answer fuses the path entry (object and `__file__`, or `sys.path` with no object) and the custody entry
  (policy and path), so its guard is theirs; it is consulted only where both would have been.

## Validation Expectations
- A second walk of a world that shares modules with an earlier one resolves no module path and runs no custody
  match for the shared targets, and its result equals a fresh analysis's.
- A re-import (a new module object), a changed `__file__`, a moved `sys.path` (no object) or another policy each
  make the edge answer miss; a synthetic target is never kept. `importlib.reload` keeps the object and its file, so
  its path, custody and leaf stay valid and the answer is reused (its facts are derived again under 0.2.8305's spec
  guard).
- `finalize` returns the same order and the same cycle walk error as before on acyclic, diamond and cyclic graphs.

## Unknowns and Open Decisions
- None open. A new root module's walk stays proportional to its world: the crystal records that world in walk
  order, and making it constant per bind would change what a crystal records (owner decision required).

## Context / Handoff Summary
One fused, guarded answer per import target across walks; one heap for the load order.
