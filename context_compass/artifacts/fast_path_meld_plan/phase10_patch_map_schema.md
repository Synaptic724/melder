# Phase 10 Patch Map Schema (Draft, 2026-01-27)

## Scope
Define patch map artifacts that let supported overrides and mutation rewires
stay on the fast path without rebuilding the DAG per call.

## Evidence References
- `src/melder/aether/conduit/meld/overrides/spell_overrider.py:SpellOverrider.apply`
- `src/melder/aether/conduit/meld/overrides/spell_overrider.py:_specificity_for_spec`
- `src/melder/aether/conduit/meld/overrides/graph_mutator.py:GraphMutator.apply`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:MeldRuntime.execute`

## Patch Map Artifacts (Draft)

```
OverridePatchMap:
  root_spell_id: str
  targets_by_spec: Dict[str, List[SocketRef]]
  specificity_by_spec: Dict[str, "Specificity"]

MutationPatchMap:
  root_spell_id: str
  targets_by_spec: Dict[str, List[MutationEdgePatch]]

MutationEdgePatch:
  child_spell_id: str
  param_name: str
  old_parent_id: str | None
  new_parent_id: str | None
```

## Notes
- OverridePatchMap caches the DagTargetingEngine resolution for TargetSpec
  keys, preserving specificity logic.
- MutationPatchMap encodes edge replacement intent; whether this can avoid
  a full DAG rebuild is still UNKNOWN.
- Mutation patch application may need to emit replacement SocketRef entries
  for new targets if the DAG index must stay consistent.

## Inputs Required To Compile
- RootResolutionBlueprint.dag_index
- RootResolutionBlueprint.socket_refs
- Socket kind filters for mutation sockets

## Runtime Inputs Required
- Actual override values for each TargetSpec (value injection).
- Mutation override payload (TargetSpec -> new spell id).
- Mutator fallback when patch map marks unsupported rewires.

## Storage Location
- Root SpellCrafter (parallel to Phase 5/8/9 artifacts), cleaned with Phase 5
  artifact resets and invalidated when blueprints change.

## Invalidation / Signature Inputs (Draft)
- Blueprint changes (Phase 5 re-run).
- Socket ref changes.
- Contract wiring changes.
- Mutation contract socket kind changes.

## Open Questions
- Can MutationPatchMap apply without DAG rebuild, or must it fall back?
- How to handle conflicting override rules with equal specificity.
- Should patch maps encode TargetSpec specificity tiers explicitly or rely on runtime?
