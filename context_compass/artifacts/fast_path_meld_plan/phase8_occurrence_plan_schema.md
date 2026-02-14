# Phase 8 OccurrencePlan Schema (Draft, 2026-01-27)

## Scope
Define the OccurrencePlan artifact that replaces per-call occurrence planning
in `MeldEngine.run` with a precompiled plan produced during Phase 8.

## Evidence References
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:MeldEngine.run`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_occurrence_graph`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_extend_occurrence_graph_with_ordered_nodes`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_execution_order`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_instance_plan`
- `context_compass/artifacts/fast_path_meld_plan/ticket_fast_path_github.md`

## OccurrencePlan (Draft Schema)
The fields below map directly to data currently computed per call in
`MeldEngine.run`. Types are expressed using existing aliases from the runtime.

```
OccurrencePlan:
  root_spell_id: str
  occurrence_graph: Dict[_OccurrenceKey, Dict[str, List[_OccurrenceKey]]]
  execution_order: List[str]
  instance_keys_by_spell_id: Dict[str, List[_InstanceKey]]
  canonical_occurrences_by_spell_id: Dict[str, _OccurrenceKey]
  root_instance_key: _InstanceKey
  shared_spell_ids: set[str]
```

### Field Evidence Mapping
- `root_spell_id`: input to `_build_occurrence_graph` and `_build_instance_plan`.
- `occurrence_graph`: built by `_build_occurrence_graph` and mutated by
  `_extend_occurrence_graph_with_ordered_nodes`.
- `execution_order`: built by `_build_execution_order`.
- `instance_keys_by_spell_id`, `canonical_occurrences_by_spell_id`,
  `root_instance_key`, `shared_spell_ids`: built by `_build_instance_plan`.

## Inputs Required To Compile OccurrencePlan
Observed inputs used in current runtime planning:
- Root blueprint DAG and ordered node ids:
  - `RootResolutionBlueprint.dag`
  - `RootResolutionBlueprint.ordered_node_ids`
  Evidence: `MeldEngine.run`.
- System state local topology (when available):
  - `SpellSystemStates.get_local_topology_by_id`
  Evidence: `_collect_occurrence_dependencies`.
- DAG node dependency metadata:
  - `dag.get_node`, `node.dependencies`, `node.incoming_params`,
    `dag._socket_kinds`
  Evidence: `_collect_occurrence_dependencies`.
- Spell lookup (to resolve contract sockets and existence policy):
  Evidence: `_apply_spell_contract_dependencies`, `_build_instance_plan`.
- DAG index for mutation override targeting:
  Evidence: `_apply_mutation_overrides_to_dependencies`.

## Storage Location (UNKNOWN)
We need to decide where the OccurrencePlan lives.
Candidates (not yet validated):
- RootResolutionBlueprint (per root, per conduit)
- SpellCrafter (per spell, per conduit)
- Spell (attached to spell or spell index)
- Conduit (plan cache keyed by root spell id)

Decision requires evidence from the phase scheduler and cleanup semantics.

## Invalidation / Signature Inputs (Draft)
Phase 8 output must be invalidated when upstream inputs change. Based on
Phase 1-7 artifacts and current runtime dependencies, candidate inputs include:
- RootResolutionBlueprint DAG or ordered ids (Phase 5).
- Local topology for any spell (Phase 3).
- Contract socket wiring and mutation override targets (Phase 3 + mutation data).
- Spell existence or contract bindings (Phase 3 + spell metadata).

The exact signature fields are UNKNOWN and must be confirmed in the plan
signature/invalidation task.

## Open Questions
- Should the OccurrencePlan include contract override maps, or should those be
  emitted by Phase 10 patch maps?
- How to encode SpellSpace requirements for occurrence expansion?
- Do we need multiple OccurrencePlan variants per root (hooks enabled, etc.)?

## Notes
The schema above mirrors the runtime outputs exactly so the Phase 8 compiler can
replace per-call planning with plan execution. Additional metadata (signature,
epoch, or validity flags) will be added once plan lifecycle is defined.
