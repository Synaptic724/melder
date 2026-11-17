# architecture_patch

## Metadata
- Patch ID: configure_in_seconds_2026_11_17
- Status: implemented at 0.2.8306; deltas merged into src_components, src_architecture, tests_components and
  the source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer) authors and implements
- Ticket: https://github.com/Synaptic724/melder/issues/331 (third iteration, widened on 2026-11-17)
- Created: 2026-11-17T12:05:00Z
- Updated: 2026-11-17T12:32:22Z

## Patch Scope and Non-Goals
- Objective: a bind's per-bind bookkeeping stops growing with the world it joins. A MutationResearch world entry
  costs the same however large the research set is - the undo ring is minted lazily and the persistence twin is
  emitted from parts kept incrementally - and a crystal walk for a new root module takes each import edge's answers
  from memory across walks, ordering the result with a heap.
- Non-goals: validation reuse across `Conduit.validate_resolution` calls (dropped by the owner on 2026-11-17: about
  0.18 s of MelderOps' configure without the profiler); the spell code digest and the spell profile's source reads;
  changing what a crystal or the MutationResearch record holds; a larger undo ring; any public API.

## Changed-Components Matrix
| Component | Change |
| --- | --- |
| `ResearchSet` | appends mark the undo ring stale; organizing verbs, `snapshot_network` and ring reads mint first |
| lane, journal, residence, versioner | keep append-only payload parts and expose a view of them |
| `MutationResearch` (root) | emits its twin from views of the parts instead of a full description |
| `MutationResearchCrystal` | accepts a composition view and materializes it on first read |
| `ModuleAnswerCache` | keeps each module's import-edge answer (path object, custody kind, leaf record) across walks |
| `CrystalAnalyzer` | takes a first-seen edge from that answer; `DependencyViewStrategy` picks ready nodes from a heap |

## Interface and Boundary Deltas
- No public signature changes. Kernel-internal additions: each MutationResearch structure's payload view, the
  set's and root's composition views, `MutationResearchCrystal(composition_view=...)`, and
  `ModuleAnswerCache.lookup_edge_answer` / `store_edge_answer`.
- Contract change, owner decision 2026-11-17: `record_world_entry`, `register_spell` and `register_group` no longer
  mint an undo-ring snapshot; they mark the ring stale, and `recompose_group` with them (it records through
  `register_group`). `create_lane`, `attach`,
  `detach`, `join`, `archive` and `restore_network` mint a pending snapshot before they change the organization and
  mint again after it, as before; `snapshot_network`, `network_snapshot_shas` and `latest_network_snapshot` mint a
  pending snapshot first. `describe_composition` stays read-only and reports the ring as of its last mint, and so
  does the recorded twin. A ring read after N appends therefore holds one snapshot for them, not N.
- `network_snapshot_shas` and `latest_network_snapshot` take the set lock (they read the versioner alone today).

## Cross-Component Invariants
- The recorded twin, materialized, equals what `describe_composition()` returned at the same organization, journal
  and ring state: same organization (lanes in `lane_id` order, each with its nodes in lane order and its tip),
  same residence mapping, same journal window (the newest 200 entries, `entry_count`, `next_sequence`), same ring.
- A payload part is never mutated in place once a view can hold it: appends extend its list; a detach, a residence
  transfer or a restore replaces the list; cleanup drops the reference (`del`), never `clear()`. A twin emitted
  before a restore or a cleanup therefore still describes the composition it was emitted for.
- The undo ring keeps its 64 slots, its content addressing and restore semantics. The snapshot minted before an
  organizing verb holds the organization that verb starts from, so the state just before a mistake stays
  restorable after any number of appends.
- An edge answer is reused only under the guards of the two caches it fuses: the same module object (or none) with
  the same `__file__` text (with no object, the same `sys.path`), and the same custody policy; synthetic modules and
  custom strategy chains are never kept. A crystal built with reused edge answers records exactly what a fresh walk
  records; the heap-based order equals the sorted-list order.

## Migration and Rollout Order
1. Failing-first pins (GIL off): constant per-append cost and twin equality, the lazy ring, twin integrity after a
   restore and after cleanup, edge reuse across walks, heap order equality.
2. MutationResearch parts and views, the lazy ring, the twin's view path.
3. The edge answer in `ModuleAnswerCache` and `CrystalAnalyzer`; the heap in `DependencyViewStrategy`.
4. Suites, docs, graph, release note, notch 0.2.8306, rebuild last; full suite; probe without the profiler.

## Rollback Strategy
- Revert the 0.2.8306 commit. Records are unchanged in shape, so nothing written by 0.2.8306 needs migrating back.

## Validation Expectations and Evidence Plan
- New pins beside the MutationResearch research-set tests and `test_module_answer_cache.py`; the MutationResearch,
  crystallizer, spellbook and conduit suites and the full suite with the GIL off; the probe extended to
  MutationResearch, timed without the profiler on 0.2.8305 and 0.2.8306; MelderOps' re-measure on the wheel.

## Ticket Coverage Map
| Requirement (#331) | Patch section |
| --- | --- |
| world entry at constant cost; incremental twin | component_patch_mutation_research; ..._twin |
| lazy undo ring for every append | component_patch_mutation_research |
| import edges memoized across walks; heap order | component_patch_crystal_analysis; ..._edge_answers |

## Unknowns and Decision Requests
- None open. Decided by the owner on 2026-11-17: scope, lazy ring for every append, incremental twin, 64 slots kept,
  validation reuse dropped.

## Context / Handoff Summary
Design written before implementation. A world entry pays one node payload, one journal payload and one residence
claim; the twin holds views and materializes on read; the ring mints when someone looks or before an organizing
verb. The walk takes first-seen edges from one fused answer instead of a path and a custody lookup.
