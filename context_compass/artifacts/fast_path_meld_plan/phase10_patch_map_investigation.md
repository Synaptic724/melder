# Phase 10 Patch Map Investigation (2026-01-27)

## Scope
Map current override and mutation handling so Phase 10 can precompile patch
maps that keep supported override cases on the fast path.

## Evidence Anchors
- `src/melder/aether/conduit/meld/overrides/spell_overrider.py:SpellOverrider.apply`
- `src/melder/aether/conduit/meld/overrides/spell_overrider.py:_specificity_for_spec`
- `src/melder/aether/conduit/meld/overrides/graph_mutator.py:GraphMutator.apply`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:MeldRuntime.execute`

## Current Runtime Override Flow
From `MeldRuntime.execute`:
- If blueprint exists, apply mutation overrides with `GraphMutator.apply`.
- Then apply value overrides with `SpellOverrider.apply` to build `override_map`.
- Build `ResolutionFrame` overrides and run `MeldEngine`.

## SpellOverrider (value overrides)
Behavior (evidence: `SpellOverrider.apply`):
- Parse TargetSpec keys (PATH / UNIQUE / BROADCAST).
- Resolve matching sockets via DagTargetingEngine (blueprint.dag_index).
- Apply specificity precedence (PATH > UNIQUE > BROADCAST).
- Detect conflicting overrides at the same specificity and raise.
- Produce `override_map: Dict[SocketRef, Any]`.

Patch map implications:
- A patch map can precompute which sockets a TargetSpec would affect.
- Runtime still needs to supply values, but the socket targets can be cached.

## GraphMutator (mutation overrides)
Behavior (evidence: `GraphMutator.apply`):
- Validate override payloads (string key + non-empty target spell id).
- Resolve mutation sockets via DagTargetingEngine (filtered to MUTATION_CONTRACT).
- Clone DAG, rewire targeted edges, and recompute topo order.
- Build new socket refs and DagIndex entries for introduced nodes.
- Rebuild socket refs for mutation targets by creating new SocketRef entries.

Patch map implications:
- Some mutation rewires could be represented as "edge replacement" patches.
- However, GraphMutator currently rebuilds DAG and DagIndex, which is a heavy
  operation. Phase 10 must define which rewires can be applied without full
  DAG rebuild, or else keep mutation overrides in slow path.

## Inputs Required For Patch Map Compilation
Based on current runtime:
- RootResolutionBlueprint (dag + dag_index + socket_refs).
- TargetSpec resolution (DagTargetingEngine).
- Socket kinds (to filter mutation sockets).
- TargetSpec specificity resolution (PATH/UNIQUE/BROADCAST precedence).

## Outputs Required
Draft patch map outputs:
- OverridePatchMap: TargetSpec -> list[SocketRef] with specificity metadata.
- MutationPatchMap: TargetSpec -> list[MutationEdgePatch] where a patch encodes
  (child_id, param_name, old_parent_id, new_parent_id).

## UNKNOWNs
- Which mutation overrides can be safely patched without DAG rebuild.
- Whether patch maps should store pre-resolved sockets or retain TargetSpec.
- How to handle conflicting overrides when precomputed sockets overlap.
- Whether mutation patch maps must also emit new SocketRef/DagIndex entries.
