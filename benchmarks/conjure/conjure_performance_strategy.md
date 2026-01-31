# Conjure Performance Strategy and Deep-Dive Notes

## Metadata
- Doc ID: PERF-CONJURE-2026-01-31
- Status: draft
- Owner:
- Created: 2026-01-31
- Updated: 2026-01-31
- Scope: conjure-only optimization (all artifacts built during conjure)

## Constraints (Non-Negotiable)
- All Phase 5-11 artifacts must be built during conjure (no deferral to meld).
- Outputs and semantics must match current behavior.
- No new runtime dependency on meld-time recompute.

## Evidence: Where the allocations come from
### Hotspot A: socket_path tuple allocations
- Location: `src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py` -> `_overlay_sockets_and_index`.
- Line of interest: `socket_path = path + (socket_desc.param_name,)`.
- Mechanism:
  - BFS walks keys of `(node_id, path)`.
  - Path is part of the identity. If the same node is reachable via multiple
    paths, each distinct path yields a new socket_path and new SocketRef.
  - Each SocketRef is added to `RootResolutionBlueprint._socket_refs` and
    `DagIndex`.

### Hotspot B: child_occurrence tuple allocations
- Location: `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`.
- Lines of interest:
  - `_append_topology_dependencies`: `child_occurrence = (target_id, path + (socket.param_name,))`
  - `_apply_spell_contract_dependencies`: `child_occurrence = (target_spell_id, path + (param_name,))`

### Why the count is high in depth9
Evidence from `tests/mocks/spellbook/deep_layers.py`:
- `get_depth_9_classes()` returns 17 classes (not 9).
- Each non-leaf class has **two** constructor parameters (`left`, `right`).
- Each layer A/B depends on the same two children (A and B) of the next layer.
  This is a diamond DAG, not a tree. A node can be reached by many distinct paths.

Implication:
- `_overlay_sockets_and_index` creates SocketRefs per (node_id, path), not per node.
- Distinct paths explode by layer. This is expected for a diamond DAG.

Approximate path math for depth9 (illustrative, not exact):
- Occurrences per layer double as you descend: 1, 2, 4, 8, 16, 32, 64, 128, 256.
- Each internal occurrence adds two socket paths.
- One root blueprint can easily create hundreds of socket_path allocations.
- Phase 5 builds a blueprint for **every spell id**, multiplying allocations
  across all subtrees.

This explains why 1446 socket_path allocations can occur even for 17 classes.

## Evidence: Where blueprint duplication happens
- Location: `src/melder/spellbook/spell_crafter/spell_crafter.py` -> `run_phase_root_blueprints`.
- Behavior:
  - Builds root blueprints for all structural roots.
  - For every spell_id not a root, builds a per-spell blueprint using
    `build_blueprint_for_spell_id`.
- Result: Phase 5 overlays sockets and builds DagIndex for many blueprints,
  not just the root.

## Key Questions to Answer (UNKNOWN until measured)
- What is the exact count of socket refs per blueprint for depth9?
- How many total blueprints are created per conjure (root + non-root)?
- How many distinct paths exist per node at each layer in real runs?
- How much time and memory is spent per Phase 8-11 builder relative to Phase 5?

## Strategy (Conjure-Only, Intrusive OK)
This strategy keeps all artifacts built during conjure, but removes duplication.

### Iteration 1: Measure and partition cost (no behavior change)
- Add an instrumented benchmark in `benchmarks/conjure/` that records:
  - Count of blueprints built.
  - Count of SocketRefs per blueprint.
  - Count of `(node_id, path)` occurrences per blueprint.
  - Time per sub-step inside Phase 5 (build DAG, overlay sockets, index build).
- Output should be programmatically returned and asserted in tests (no prints).

### Iteration 2: Reduce duplication in Phase 5
Goal: build all artifacts in conjure, but avoid redundant work per spell.
Candidate approaches:
1) Shared DAG + shared topology index
   - Build a single frame-wide DAG (or per-root DAGs) and store it once.
   - For non-root spells, avoid building new DAG nodes when an equivalent
     structure already exists in the same frame.
2) SocketRef sharing by prefix reuse
   - Precompute reusable path segments so `path + (name,)` reuses tuples
     rather than allocating new ones when the same path is needed.
3) Avoid rebuilding the DagIndex multiple times
   - If a blueprint is built by slicing a shared structure, build the index
     from shared data once.

### Iteration 3: Reduce Phase 8-11 overhead without deferral
- Cache SpellContract defaults once per spell (avoid repeated signature work).
- Build `spell_lookup` once per conjure and reuse in all builders.
- Remove list snapshots and repeated joins in patch map builds where safe.

## Risks and Constraints
- Must preserve override targeting semantics (SocketRef path identity).
- Must preserve validation behavior and change-control integration.
- Must not introduce lazy build behavior (per user constraint).

## Evidence Sources
- `src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- `tests/mocks/spellbook/deep_layers.py`
- `benchmarks/testing_other_di/test_melder_hotpath_profiles.py`

## Context / Handoff Summary
- Depth9 test uses 17 classes with shared dependencies per layer, creating a
  diamond DAG and many distinct paths.
- Phase 5 builds blueprints for every spell_id, not just the root, so socket
  path allocations multiply across all subtrees.
- Next step: add instrumentation benchmarks in `benchmarks/conjure/` and
  confirm exact counts before changing Phase 5 internals.
