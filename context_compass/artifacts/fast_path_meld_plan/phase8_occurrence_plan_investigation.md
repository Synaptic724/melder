# Phase 8 Occurrence Plan Investigation (2026-01-27)

## Scope
Phase 8 planning focuses on the occurrence graph and execution order that the
MeldEngine currently computes per call. This note records the current inputs,
outputs, and decision points with file-level evidence.

## Evidence Targets (Current Runtime)
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:MeldEngine.run`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_occurrence_graph`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_extend_occurrence_graph_with_ordered_nodes`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_execution_order`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_collect_occurrence_dependencies`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_apply_spell_contract_dependencies`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_record_contract_override`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_apply_mutation_overrides_to_dependencies`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_instance_plan`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_instance_key_for_occurrence`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_occurrence_for_instance_key`

## Core Data Structures
- Occurrence key: `_OccurrenceKey = tuple[str, tuple[str, ...]]` where the path is
  the param-name chain from the root. Evidence: `meld_engine.py` top-level aliases.
- Instance key: `_InstanceKey = tuple[str, Optional[tuple[str, ...]]]`. Shared
  existences collapse to `None` path; per-path existences keep the path. Evidence:
  `_instance_key_for_occurrence`.

## What the runtime currently builds per call
### Occurrence graph
Built by `_build_occurrence_graph` as a BFS from `(root_spell_id, ())` and yields:
`Dict[_OccurrenceKey, Dict[str, List[_OccurrenceKey]]]`. Evidence: `_build_occurrence_graph`.

Dependency expansion is collected by `_collect_occurrence_dependencies`, which:
- Uses local topology when available (`SpellSystemStates.get_local_topology_by_id`).
- Falls back to DAG node dependencies (`dag.get_node`, `node.dependencies`,
  `node.incoming_params`, `dag._socket_kinds`).
- Appends the param name into the occurrence path for each dependency.
Evidence: `_collect_occurrence_dependencies`.

SpellContract and mutation overrides are applied during dependency collection:
- `_apply_spell_contract_dependencies` adds contract targets and records override
  payloads via `_record_contract_override`.
- `_apply_mutation_overrides_to_dependencies` rewires dependencies based on
  `spell.mutation_override` and `DagIndex` targeting.
Evidence: `_apply_spell_contract_dependencies`, `_record_contract_override`,
`_apply_mutation_overrides_to_dependencies`.

### Ordered nodes expansion
`_extend_occurrence_graph_with_ordered_nodes` injects occurrences for any
blueprint `ordered_node_ids` not already present in the root expansion, treating
them as additional entrypoints with empty paths. Evidence: method contract in
`_extend_occurrence_graph_with_ordered_nodes`.

### Execution order
`_build_execution_order` derives a dependency-safe list of spell ids by
topologically sorting edges built from the occurrence graph, with a fallback
tie-breaker using `ordered_node_ids`. Evidence: `_build_execution_order`.

### Instance plan (per spell)
`_build_instance_plan` groups occurrences by spell id and produces:
- `instance_keys_by_spell_id`
- `canonical_occurrences_by_spell_id` (for shared existences)
- `root_instance_key`
- `shared_spell_ids`
Evidence: `_build_instance_plan`.

## Phase 8 Outputs To Precompute
Based on the above, Phase 8 likely needs to emit:
- Occurrence graph (path-aware dependencies).
- Execution order (per spell id).
- Instance plan metadata (instance keys + canonical occurrences + shared set).

These are currently computed inside `MeldEngine.run` and consumed immediately.
Evidence: `MeldEngine.run` order of operations.

## Inputs Needed For Phase 8 Compilation
Observed inputs used by the current runtime:
- `RootResolutionBlueprint.dag` and `RootResolutionBlueprint.ordered_node_ids`.
  Evidence: `MeldEngine.run` uses `blueprint.dag` and `blueprint.ordered_node_ids`.
- `SpellSystemStates.get_local_topology_by_id` when available. Evidence:
  `_collect_occurrence_dependencies`.
- `DirectedAcyclicWorkGraph` node dependencies and socket kinds. Evidence:
  `_collect_occurrence_dependencies` uses `dag.get_node` and `dag._socket_kinds`.
- Spell lookup table (`spell_lookup`) for contracts and existence checks.
  Evidence: `_apply_spell_contract_dependencies`, `_build_instance_plan`.
- `DagIndex` from the blueprint for mutation override targeting. Evidence:
  `_apply_mutation_overrides_to_dependencies` uses `self._blueprint.dag_index`.

## Notes On Contract and Mutation Overrides (Phase 8 adjacency)
- Contract overrides are recorded into `_contract_overrides_by_occurrence` and
  `_contract_overrides_by_spell_id` during occurrence expansion. Evidence:
  `_record_contract_override`.
- Mutation overrides can rewrite dependencies for a specific occurrence path.
  Evidence: `_apply_mutation_overrides_to_dependencies`.

These may be Phase 10 concerns, but the occurrence graph already incorporates
their effects in the current runtime.

## UNKNOWN / Needs Investigation
- Where `ordered_node_ids` are computed and whether they already account for
  contract or mutation wiring. Evidence target: `RootResolutionBlueprint` build
  path in `spell_crafter.py` (UNKNOWN).
- How `dag._socket_kinds` is populated and whether it is stable for Phase 8 use.
  Evidence target: DAG construction in `spell_crafter/dag` (UNKNOWN).
- Whether Phase 8 should include contract override maps as part of the plan or
  leave that for Phase 10. Evidence target: override and contract handling in
  `meld_runtime` / `spell_overrider` (UNKNOWN).

## Candidate Phase 8 Artifact Shape (Draft)
This section is a draft based on the current runtime work and must be confirmed.
- occurrence_graph: Dict[_OccurrenceKey, Dict[str, List[_OccurrenceKey]]]
- execution_order: List[str]
- instance_keys_by_spell_id: Dict[str, List[_InstanceKey]]
- canonical_occurrences_by_spell_id: Dict[str, _OccurrenceKey]
- root_instance_key: _InstanceKey
- shared_spell_ids: set[str]

All fields above have evidence in `MeldEngine` today. The storage location and
invalidation policy remain TBD and must be defined in the Phase 8 schema task.
