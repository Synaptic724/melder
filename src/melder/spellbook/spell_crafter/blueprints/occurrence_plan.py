from collections import defaultdict, deque
import inspect
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.dag.target_spec import TargetSpec, TargetSpecKind
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell

OccurrenceKey = Tuple[str, Tuple[str, ...]]
InstanceKey = Tuple[str, Optional[Tuple[str, ...]]]


class OccurrencePlan(Cleanable):
    """
    Internal

    Phase 8 artifact that captures occurrence expansion and execution ordering
    for a single root blueprint.

    Purpose:
        Precompute the path-aware occurrence graph and instance planning that
        the meld runtime currently builds per call.

    Contract:
        - Instances are treated as immutable once built.
        - This object owns the provided collections and clears them on cleanup.
        - root_spell_id must be the version id used to build the plan.

    Threading:
        - Not thread-safe. Treat as single-threaded, read-only data.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_root_spell_id",
        "_occurrence_graph",
        "_execution_order",
        "_instance_keys_by_spell_id",
        "_canonical_occurrences_by_spell_id",
        "_root_instance_key",
        "_shared_spell_ids",
    ]

    def __init__(
            self,
            *,
            root_spell_id: str,
            occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]],
            execution_order: List[str],
            instance_keys_by_spell_id: Dict[str, List[InstanceKey]],
            canonical_occurrences_by_spell_id: Dict[str, OccurrenceKey],
            root_instance_key: InstanceKey,
            shared_spell_ids: Set[str],
    ) -> None:
        """
        Initialize a Phase 8 occurrence plan.

        Contract:
            - All inputs must be non-None.
            - Inputs are stored by reference and treated as owned.
            - Callers must not mutate inputs after construction.

        Args:
            root_spell_id:
                Version id of the root spell used to build the plan.
            occurrence_graph:
                Path-aware occurrence graph keyed by (spell_id, path).
            execution_order:
                Ordered list of spell ids for execution.
            instance_keys_by_spell_id:
                Mapping from spell id to instance keys.
            canonical_occurrences_by_spell_id:
                Canonical occurrence for each shared spell id.
            root_instance_key:
                Instance key representing the root instance.
            shared_spell_ids:
                Spell ids that resolve to shared instances.

        Raises:
            ValueError:
                If any required input is None.
        """
        super().__init__()
        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")
        if occurrence_graph is None:
            raise ValueError("occurrence_graph must not be None.")
        if execution_order is None:
            raise ValueError("execution_order must not be None.")
        if instance_keys_by_spell_id is None:
            raise ValueError("instance_keys_by_spell_id must not be None.")
        if canonical_occurrences_by_spell_id is None:
            raise ValueError("canonical_occurrences_by_spell_id must not be None.")
        if root_instance_key is None:
            raise ValueError("root_instance_key must not be None.")
        if shared_spell_ids is None:
            raise ValueError("shared_spell_ids must not be None.")

        self._root_spell_id = root_spell_id
        self._occurrence_graph = occurrence_graph
        self._execution_order = execution_order
        self._instance_keys_by_spell_id = instance_keys_by_spell_id
        self._canonical_occurrences_by_spell_id = canonical_occurrences_by_spell_id
        self._root_instance_key = root_instance_key
        self._shared_spell_ids = shared_spell_ids

    def cleanup(self) -> None:
        """
        Deterministically tear down the plan and owned collections.

        Contract:
            - Idempotent: safe to call multiple times.
            - Clears all owned containers and nulls references.
        """
        if self._cleaned:
            return
        self._cleaned = True

        self._occurrence_graph.clear()
        self._execution_order.clear()
        self._instance_keys_by_spell_id.clear()
        self._canonical_occurrences_by_spell_id.clear()
        self._shared_spell_ids.clear()

        self._root_spell_id = None
        self._occurrence_graph = None
        self._execution_order = None
        self._instance_keys_by_spell_id = None
        self._canonical_occurrences_by_spell_id = None
        self._root_instance_key = None
        self._shared_spell_ids = None

    @property
    def root_spell_id(self) -> str:
        """
        Return the root spell id for this plan.

        Contract:
            - Raises if the plan has been cleaned.
        """
        self.check_cleaned()
        return self._root_spell_id

    @property
    def occurrence_graph(self) -> Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]]:
        """
        Return the path-aware occurrence graph.

        Contract:
            - The returned mapping is owned by the plan and should be
              treated as read-only by callers.
        """
        self.check_cleaned()
        return self._occurrence_graph

    @property
    def execution_order(self) -> List[str]:
        """
        Return the spell id execution order.

        Contract:
            - The returned list is owned by the plan and should be treated
              as read-only by callers.
        """
        self.check_cleaned()
        return self._execution_order

    @property
    def instance_keys_by_spell_id(self) -> Dict[str, List[InstanceKey]]:
        """
        Return instance keys grouped by spell id.

        Contract:
            - The returned mapping is owned by the plan and should be
              treated as read-only by callers.
        """
        self.check_cleaned()
        return self._instance_keys_by_spell_id

    @property
    def canonical_occurrences_by_spell_id(self) -> Dict[str, OccurrenceKey]:
        """
        Return canonical occurrences for shared spell ids.

        Contract:
            - The returned mapping is owned by the plan and should be
              treated as read-only by callers.
        """
        self.check_cleaned()
        return self._canonical_occurrences_by_spell_id

    @property
    def root_instance_key(self) -> InstanceKey:
        """
        Return the instance key for the root occurrence.

        Contract:
            - The key is stable for the lifetime of the plan.
        """
        self.check_cleaned()
        return self._root_instance_key

    @property
    def shared_spell_ids(self) -> Set[str]:
        """
        Return the spell ids that resolve to shared instances.

        Contract:
            - The returned set is owned by the plan and should be treated
              as read-only by callers.
        """
        self.check_cleaned()
        return self._shared_spell_ids


class OccurrencePlanBuilder(object):
    """
    Internal

    Phase 8 compiler that mirrors the runtime occurrence planning logic from
    MeldEngine and produces an OccurrencePlan artifact.

    Purpose:
        Convert a RootResolutionBlueprint and spell metadata into a reusable
        occurrence plan for fast meld execution.

    Contract:
        - This builder does not own any referenced objects.
        - Inputs must remain valid for the duration of build().
        - SpellContract resolution is attempted when providers are available.
        - Missing SpellContract providers are deferred to the meld runtime.
        - Not thread-safe.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = [
        "_root_spell",
        "_blueprint",
        "_spell_lookup",
        "_system_states",
    ]

    def __init__(
            self,
            *,
            root_spell: ISpell,
            blueprint: Any,
            spell_lookup: Dict[str, ISpell],
            system_states: Any,
    ) -> None:
        """
        Initialize the occurrence plan builder.

        Args:
            root_spell:
                Root spell used for identity and default lookups.
            blueprint:
                RootResolutionBlueprint providing DAG, ordered nodes, and dag index.
            spell_lookup:
                Mapping of spell_id to ISpell for all reachable nodes.
            system_states:
                SpellSystemStates used to query local topologies.

        Raises:
            ValueError:
                If root_spell or blueprint is None.
        """
        if root_spell is None:
            raise ValueError("root_spell must not be None.")
        if blueprint is None:
            raise ValueError("blueprint must not be None.")
        if spell_lookup is None:
            spell_lookup = {}
        self._root_spell = root_spell
        self._blueprint = blueprint
        self._spell_lookup = spell_lookup
        self._system_states = system_states

    def build(self) -> OccurrencePlan:
        """
        Build and return the OccurrencePlan for the configured root blueprint.

        Contract:
            - Mirrors MeldEngine occurrence planning behavior.
            - Raises MeldExecutionError when dependency spells cannot be resolved.

        Returns:
            OccurrencePlan: The compiled phase 8 artifact.
        """
        root_spell_id = self._blueprint.root_spell_id
        dag = self._blueprint.dag
        ordered_node_ids = self._blueprint.ordered_node_ids

        occurrence_graph = self._build_occurrence_graph(
            dag=dag,
            root_spell_id=root_spell_id,
        )
        self._extend_occurrence_graph_with_ordered_nodes(
            occurrence_graph=occurrence_graph,
            ordered_node_ids=ordered_node_ids,
            dag=dag,
        )
        execution_order = self._build_execution_order(
            occurrence_graph=occurrence_graph,
            fallback_order=ordered_node_ids,
        )
        (
            instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id,
            root_instance_key,
            shared_spell_ids,
        ) = self._build_instance_plan(
            occurrence_graph=occurrence_graph,
            root_spell_id=root_spell_id,
        )

        return OccurrencePlan(
            root_spell_id=root_spell_id,
            occurrence_graph=occurrence_graph,
            execution_order=execution_order,
            instance_keys_by_spell_id=instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
            root_instance_key=root_instance_key,
            shared_spell_ids=shared_spell_ids,
        )

    @staticmethod
    def _is_shared_existence(existence: Existence) -> bool:
        """
        Determine whether an existence policy yields a shared instance.

        Contract:
            - Existence.many is treated as non-shared.
            - All other existences are treated as shared.

        Args:
            existence: Existence policy to evaluate.

        Returns:
            bool: True if the existence is shared.
        """
        return existence is not Existence.many

    def _build_occurrence_graph(
            self,
            *,
            dag: Any,
            root_spell_id: str,
    ) -> Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]]:
        """
        Build a path-aware occurrence graph rooted at the entrypoint spell.

        Contract:
            - Returns a mapping of occurrence -> param_name -> child occurrences.
            - Uses local topology when available; falls back to DAG metadata.
            - Includes the root occurrence even if it has no dependencies.

        Args:
            dag: DirectedAcyclicWorkGraph from the blueprint.
            root_spell_id: Version id for the root spell.

        Returns:
            Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]]: Occurrence graph.
        """
        root_occurrence = (root_spell_id, ())
        occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]] = {}
        queue = deque([root_occurrence])
        seen: Set[OccurrenceKey] = set()

        while queue:
            occurrence = queue.popleft()
            if occurrence in seen:
                continue
            seen.add(occurrence)

            dependencies = self._collect_occurrence_dependencies(
                occurrence=occurrence,
                dag=dag,
            )
            occurrence_graph[occurrence] = dependencies

            for child_list in dependencies.values():
                for child_occurrence in child_list:
                    if child_occurrence not in seen:
                        queue.append(child_occurrence)

        return occurrence_graph

    def _extend_occurrence_graph_with_ordered_nodes(
            self,
            *,
            occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]],
            ordered_node_ids: Sequence[str],
            dag: Any,
    ) -> None:
        """
        Ensure ordered nodes outside the root path still get occurrences.

        Contract:
            - Nodes already present in the occurrence graph are left unchanged.
            - Missing ordered nodes are treated as additional entrypoints with
              empty paths and expanded via dependency discovery.
            - Newly discovered occurrences are appended without overwriting
              existing entries.

        Args:
            occurrence_graph:
                Existing occurrence graph to extend in-place.
            ordered_node_ids:
                Ordered node ids from the blueprint.
            dag:
                DirectedAcyclicWorkGraph used for dependency discovery.

        Returns:
            None.
        """
        if not ordered_node_ids or dag is None:
            return

        existing_occurrences = set(occurrence_graph.keys())
        present_spell_ids = {spell_id for spell_id, _ in existing_occurrences}

        for node_id in ordered_node_ids:
            if node_id in present_spell_ids:
                continue

            queue = deque([(node_id, ())])
            while queue:
                occurrence = queue.popleft()
                if occurrence in existing_occurrences:
                    continue
                existing_occurrences.add(occurrence)
                present_spell_ids.add(occurrence[0])

                dependencies = self._collect_occurrence_dependencies(
                    occurrence=occurrence,
                    dag=dag,
                )
                occurrence_graph[occurrence] = dependencies

                for child_list in dependencies.values():
                    for child_occurrence in child_list:
                        if child_occurrence not in existing_occurrences:
                            queue.append(child_occurrence)

    @staticmethod
    def _build_execution_order(
            *,
            occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]],
            fallback_order: Sequence[str],
    ) -> List[str]:
        """
        Build a dependency-safe execution order for spell ids.

        Contract:
            - Uses the occurrence graph to build a topological order.
            - Uses fallback_order as a stable tie-breaker.
            - If cycles are detected, returns a stable fallback ordering.

        Args:
            occurrence_graph: Path-aware occurrence graph.
            fallback_order: Blueprint order used as a stable tie-breaker.

        Returns:
            List[str]: Spell ids in execution order.
        """
        if not occurrence_graph:
            return list(fallback_order) if fallback_order else []

        edges: Dict[str, Set[str]] = defaultdict(set)
        indegree: Dict[str, int] = defaultdict(int)
        nodes: Set[str] = set()

        for occurrence, dependencies in occurrence_graph.items():
            node_id = occurrence[0]
            nodes.add(node_id)
            for dependency_list in dependencies.values():
                for dependency_occurrence in dependency_list:
                    dep_id = dependency_occurrence[0]
                    nodes.add(dep_id)
                    if node_id not in edges[dep_id]:
                        edges[dep_id].add(node_id)
                        indegree[node_id] += 1

        for node_id in nodes:
            indegree.setdefault(node_id, 0)

        fallback_rank = {node_id: idx for idx, node_id in enumerate(fallback_order or [])}
        last_rank = len(fallback_rank)

        def _sort_key(node_id: str) -> Tuple[int, str]:
            return (fallback_rank.get(node_id, last_rank), node_id)

        queue = [node_id for node_id, degree in indegree.items() if degree == 0]
        queue.sort(key=_sort_key)
        order: List[str] = []

        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            for child_id in sorted(edges.get(node_id, []), key=_sort_key):
                indegree[child_id] -= 1
                if indegree[child_id] == 0:
                    queue.append(child_id)
            queue.sort(key=_sort_key)

        if len(order) == len(nodes):
            return order

        resolved: List[str] = []
        seen: Set[str] = set()
        for node_id in fallback_order or []:
            if node_id in nodes and node_id not in seen:
                seen.add(node_id)
                resolved.append(node_id)
        for node_id in sorted(nodes):
            if node_id not in seen:
                seen.add(node_id)
                resolved.append(node_id)
        return resolved

    def _collect_occurrence_dependencies(
            self,
            *,
            occurrence: OccurrenceKey,
            dag: Any,
    ) -> Dict[str, List[OccurrenceKey]]:
        """
        Collect dependency occurrences for a single spell occurrence.

        Contract:
            - Uses system state topology when available.
            - Falls back to DAG dependency metadata.
            - Adds SpellContract dependencies when providers are available.
            - Adds mutation override dependencies.
            - Defers missing SpellContract providers to runtime.

        Args:
            occurrence: The (spell_id, path) occurrence being expanded.
            dag: DirectedAcyclicWorkGraph for fallback dependency discovery.

        Returns:
            Dict[str, List[OccurrenceKey]]: Parameter-to-occurrence mapping.

        """
        spell_id, path = occurrence
        dependencies: Dict[str, List[OccurrenceKey]] = {}

        self._append_topology_dependencies(
            dependencies=dependencies,
            spell_id=spell_id,
            path=path,
        )
        self._append_dag_dependencies(
            dependencies=dependencies,
            spell_id=spell_id,
            path=path,
            dag=dag,
        )
        self._apply_spell_contract_dependencies(
            dependencies=dependencies,
            occurrence=occurrence,
        )
        self._apply_mutation_overrides_to_dependencies(
            dependencies=dependencies,
            occurrence=occurrence,
        )

        return dependencies

    def _append_topology_dependencies(
            self,
            *,
            dependencies: Dict[str, List[OccurrenceKey]],
            spell_id: str,
            path: Tuple[str, ...],
    ) -> None:
        """
        Append dependencies discovered from SpellSystemStates local topology.

        Contract:
            - No-op if system states or topology are unavailable.
            - Appends child occurrences for each socket target.

        Args:
            dependencies: Mapping to update in place.
            spell_id: Spell id for the occurrence.
            path: Occurrence path segments.
        """
        if self._system_states is None:
            return

        try:
            topology = self._system_states.get_local_topology_by_id(spell_id)
        except Exception:
            topology = None

        if topology is None:
            return

        for socket in topology.sockets:
            if not socket.target_spell_ids:
                continue
            for target_id in socket.target_spell_ids:
                child_occurrence = (target_id, path + (socket.param_name,))
                dependencies.setdefault(socket.param_name, []).append(child_occurrence)

    def _append_dag_dependencies(
            self,
            *,
            dependencies: Dict[str, List[OccurrenceKey]],
            spell_id: str,
            path: Tuple[str, ...],
            dag: Any,
    ) -> None:
        """
        Append dependencies discovered from the DAG metadata.

        Contract:
            - No-op if the DAG or node metadata are unavailable.
            - Mutation contract sockets override other dependencies for a param.

        Args:
            dependencies: Mapping to update in place.
            spell_id: Spell id for the occurrence.
            path: Occurrence path segments.
            dag: DirectedAcyclicWorkGraph used for dependency discovery.
        """
        if dag is None:
            return

        node = dag.get_node(spell_id)
        if node is None:
            return

        mutated_params: Set[str] = set()
        sorted_parents = sorted(node.dependencies, key=lambda parent: parent.id)
        for parent_node in sorted_parents:
            param_name = node.incoming_params.get(parent_node)
            if not param_name:
                continue
            socket_kind = dag._socket_kinds.get((parent_node, node))
            child_occurrence = (parent_node.id, path + (param_name,))

            if socket_kind is SocketKind.MUTATION_CONTRACT:
                if param_name not in mutated_params:
                    dependencies[param_name] = []
                    mutated_params.add(param_name)
                if child_occurrence not in dependencies[param_name]:
                    dependencies[param_name].append(child_occurrence)
                continue

            if param_name in mutated_params:
                continue

            existing = dependencies.get(param_name)
            if existing is None:
                dependencies[param_name] = [child_occurrence]
            elif child_occurrence not in existing:
                existing.append(child_occurrence)

    def _apply_spell_contract_dependencies(
            self,
            *,
            dependencies: Dict[str, List[OccurrenceKey]],
            occurrence: OccurrenceKey,
    ) -> None:
        """
        Add dependency occurrences for SpellContract sockets.

        Contract:
            - Only parameters with SpellContract defaults are treated as
              contract sockets.
            - Contract sockets are resolved without touching Phase 1 artifacts.
            - Missing contracts are deferred to runtime.

        Args:
            dependencies: Mapping to update with contract dependencies.
            occurrence: The (spell_id, path) occurrence being expanded.

        Raises:
            MeldExecutionError: If a SpellContract is ambiguous or inconsistent.
        """
        spell_id, path = occurrence
        spell = self._spell_lookup.get(spell_id)
        if spell is None and spell_id == self._root_spell.spell_index.current:
            spell = self._root_spell
        if spell is None:
            return

        for param_name, contract in self._iter_spell_contract_defaults(spell):
            if contract is None:
                continue

            target_spell_id = self._resolve_spell_contract_spell_id(
                contract=contract,
                consumer_spell=spell,
                param_name=param_name,
                allow_missing=True,
            )
            if target_spell_id is None:
                continue
            child_occurrence = (target_spell_id, path + (param_name,))
            existing = dependencies.get(param_name)
            if existing is None:
                dependencies[param_name] = [child_occurrence]
            elif child_occurrence not in existing:
                existing.append(child_occurrence)

    def _iter_spell_contract_defaults(
            self,
            spell: ISpell,
    ) -> Iterable[Tuple[str, SpellContract]]:
        """
        Yield SpellContract defaults discovered in the spell's call signature.

        Contract:
            - Only parameters with SpellContract defaults are returned.
            - Ignores "self"/"cls" and var-arg parameters.
            - Returns an empty iterable when the signature cannot be resolved.

        Args:
            spell: Spell whose constructor or callable signature is inspected.

        Returns:
            Iterable[Tuple[str, SpellContract]]: Parameter names paired with
                SpellContract defaults.
        """
        call_target = spell.spell
        try:
            signature = inspect.signature(call_target)
        except (TypeError, ValueError):
            return []

        contracts: List[Tuple[str, SpellContract]] = []
        for param_name, parameter in signature.parameters.items():
            if param_name in ("self", "cls"):
                continue
            if parameter.kind in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            if parameter.default is inspect.Parameter.empty:
                continue
            default_value = parameter.default
            if isinstance(default_value, SpellContract):
                contracts.append((param_name, default_value))

        return contracts

    def _resolve_spell_contract_spell_id(
            self,
            *,
            contract: SpellContract,
            consumer_spell: ISpell,
            param_name: str,
            allow_missing: bool = False,
    ) -> Optional[str]:
        """
        Resolve a SpellContract to a concrete provider spell id.

        Args:
            contract: SpellContract describing the provider requirement.
            consumer_spell: The spell that declared the contract.
            param_name: Parameter name for diagnostics.
            allow_missing: When True, missing providers return None instead of raising.

        Returns:
            Optional[str]: Provider spell id for the contract.

        Raises:
            MeldExecutionError: If the contract is ambiguous or inconsistent.
        """
        consumer_spell_id = consumer_spell.spell_index.current
        consumer_spell_name = consumer_spell.spell_name
        contract_key = contract.canonical_key

        contracted_candidates = self._collect_contracted_contract_candidates(
            contract_key=contract_key,
            consumer_spell=consumer_spell,
            param_name=param_name,
        )
        if len(contracted_candidates) > 1:
            raise MeldExecutionError(
                spell_id=consumer_spell_id,
                spell_name=consumer_spell_name,
                node_id=consumer_spell_id,
                param_name=param_name,
                message=(
                    "SpellContract resolved to multiple contracted spells. "
                    "Use distinct bindings or remove the ambiguous contracts."
                ),
            )
        if len(contracted_candidates) == 1:
            return contracted_candidates[0].spell_index.current

        local_candidate = self._resolve_local_contract_candidate(
            contract_key=contract_key,
            consumer_spell=consumer_spell,
            param_name=param_name,
        )
        if local_candidate is None:
            local_candidate = self._resolve_fallback_contract_candidate(
                contract_key=contract_key,
                consumer_spell=consumer_spell,
                param_name=param_name,
            )

        if local_candidate is None:
            if allow_missing:
                return None
            raise MeldExecutionError(
                spell_id=consumer_spell_id,
                spell_name=consumer_spell_name,
                node_id=consumer_spell_id,
                param_name=param_name,
                message=(
                    "SpellContract could not be resolved. "
                    "No contracted or local spell matched the contract."
                ),
            )

        return local_candidate.spell_index.current

    def _collect_contracted_contract_candidates(
            self,
            *,
            contract_key: Tuple[str, str],
            consumer_spell: ISpell,
            param_name: str,
    ) -> List[ISpell]:
        """
        Collect contracted spell candidates that satisfy the contract key.

        Args:
            contract_key: Canonical (frame_key, binding_key) for the contract.
            consumer_spell: Spell declaring the contract.
            param_name: Parameter name for diagnostics.

        Returns:
            List[ISpell]: Contracted spell candidates.

        Raises:
            MeldExecutionError:
                If contracted lookup maps are inconsistent or missing.
        """
        spellbook = consumer_spell._spellbook
        if spellbook is None:
            return []

        contracted_lookup = spellbook._lookup_contracted_spells
        if not contracted_lookup:
            return []

        contracted_maps = spellbook._contracted_spells
        if contracted_maps is None:
            raise MeldExecutionError(
                spell_id=consumer_spell.spell_index.current,
                spell_name=consumer_spell.spell_name,
                node_id=consumer_spell.spell_index.current,
                param_name=param_name,
                message="Contracted spell map missing while resolving SpellContract.",
            )

        contracted_candidates: List[ISpell] = []
        for conduit_id, lookup_map in contracted_lookup.items():
            spell_index = lookup_map.get(contract_key)
            if spell_index is None:
                continue

            contracted_map = contracted_maps.get(conduit_id)
            if contracted_map is None:
                raise MeldExecutionError(
                    spell_id=consumer_spell.spell_index.current,
                    spell_name=consumer_spell.spell_name,
                    node_id=consumer_spell.spell_index.current,
                    param_name=param_name,
                    message=(
                        "Contracted spell map missing for conduit '{0}' while "
                        "resolving SpellContract."
                    ).format(conduit_id),
                )
            spell_obj = contracted_map.get(spell_index)
            if spell_obj is None:
                raise MeldExecutionError(
                    spell_id=consumer_spell.spell_index.current,
                    spell_name=consumer_spell.spell_name,
                    node_id=consumer_spell.spell_index.current,
                    param_name=param_name,
                    message="Contracted spell index missing while resolving SpellContract.",
                )
            contracted_candidates.append(spell_obj)

        return contracted_candidates

    def _resolve_local_contract_candidate(
            self,
            *,
            contract_key: Tuple[str, str],
            consumer_spell: ISpell,
            param_name: str,
    ) -> Optional[ISpell]:
        """
        Resolve a local spell candidate from the owning spellbook.

        Args:
            contract_key: Canonical (frame_key, binding_key) for the contract.
            consumer_spell: Spell declaring the contract.
            param_name: Parameter name for diagnostics.

        Returns:
            Optional[ISpell]: Local spell candidate or None.

        Raises:
            MeldExecutionError: If local spell maps are missing.
        """
        spellbook = consumer_spell._spellbook
        if spellbook is None:
            return None

        local_lookup = spellbook._lookup_spells
        if local_lookup is None:
            return None

        spell_index = local_lookup.get(contract_key)
        if spell_index is None:
            return None

        local_map = spellbook._spells
        if local_map is None:
            raise MeldExecutionError(
                spell_id=consumer_spell.spell_index.current,
                spell_name=consumer_spell.spell_name,
                node_id=consumer_spell.spell_index.current,
                param_name=param_name,
                message="Local spell map missing while resolving SpellContract.",
            )

        return local_map.get(spell_index)

    def _resolve_fallback_contract_candidate(
            self,
            *,
            contract_key: Tuple[str, str],
            consumer_spell: ISpell,
            param_name: str,
    ) -> Optional[ISpell]:
        """
        Resolve a fallback candidate from the builder spell lookup mapping.

        Args:
            contract_key: Canonical (frame_key, binding_key) for the contract.
            consumer_spell: Spell declaring the contract.
            param_name: Parameter name for diagnostics.

        Returns:
            Optional[ISpell]: Fallback spell candidate or None.

        Raises:
            MeldExecutionError: If multiple local candidates match the key.
        """
        fallback_candidates: List[ISpell] = []
        for spell_obj in self._spell_lookup.values():
            if spell_obj.key == contract_key:
                fallback_candidates.append(spell_obj)

        if len(fallback_candidates) > 1:
            raise MeldExecutionError(
                spell_id=consumer_spell.spell_index.current,
                spell_name=consumer_spell.spell_name,
                node_id=consumer_spell.spell_index.current,
                param_name=param_name,
                message=(
                    "SpellContract resolved to multiple local spells. "
                    "Use a binding_name to disambiguate."
                ),
            )
        if fallback_candidates:
            return fallback_candidates[0]

        return None

    def _resolve_mutation_override_targets(
            self,
            *,
            mutation_override: Dict[str, Any],
            dag_index: DagIndex,
    ) -> List[Tuple[SocketRef, str]]:
        """
        Resolve mutation override entries into socket references and targets.

        Contract:
            - Only mutation contract sockets are eligible.
            - Raises on invalid keys or targets.

        Args:
            mutation_override: Override key to spell id mapping.
            dag_index: DagIndex used for socket targeting.

        Returns:
            List[Tuple[SocketRef, str]]: SocketRef to target spell id pairs.

        Raises:
            MeldExecutionError: If the override payload or keys are invalid.
        """
        if not mutation_override:
            return []

        if not isinstance(mutation_override, dict):
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message="mutation_override must be a dict of override_key -> spell_id.",
            )

        if dag_index is None:
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message="mutation_override requires an active DagIndex.",
            )

        resolved: List[Tuple[SocketRef, str]] = []

        for raw_key, target_id in mutation_override.items():
            self._validate_mutation_override_entry(
                raw_key=raw_key,
                target_id=target_id,
            )

            spec = self._parse_mutation_override_spec(raw_key)
            matches = self._resolve_mutation_override_spec(
                spec=spec,
                dag_index=dag_index,
                raw_key=raw_key,
            )
            for socket_ref in matches:
                resolved.append((socket_ref, target_id))

        return resolved

    def _validate_mutation_override_entry(
            self,
            *,
            raw_key: Any,
            target_id: Any,
    ) -> None:
        """
        Validate a single mutation override entry.

        Args:
            raw_key: Raw override key from the mutation map.
            target_id: Target spell id for the override.

        Raises:
            MeldExecutionError: If the key or target is invalid.
        """
        if not isinstance(raw_key, str) or not raw_key.strip():
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message="Invalid mutation_override key: {0!r}.".format(raw_key),
            )
        if not isinstance(target_id, str) or not target_id.strip():
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message=(
                    "Invalid mutation_override target for key {0!r}: "
                    "expected non-empty spell_id string."
                ).format(raw_key),
            )

    def _parse_mutation_override_spec(self, raw_key: str) -> TargetSpec:
        """
        Parse a mutation override key into a TargetSpec.

        Args:
            raw_key: Raw override key string.

        Returns:
            TargetSpec: Parsed targeting specification.

        Raises:
            MeldExecutionError: If parsing fails.
        """
        try:
            return TargetSpec.parse(raw_key)
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message="Invalid mutation_override key: {0!r}.".format(raw_key),
                inner=exc,
            ) from exc

    def _resolve_mutation_override_spec(
            self,
            *,
            spec: TargetSpec,
            dag_index: DagIndex,
            raw_key: str,
    ) -> List[SocketRef]:
        """
        Resolve a TargetSpec into matching mutation sockets.

        Args:
            spec: Parsed targeting specification.
            dag_index: DagIndex used for socket targeting.
            raw_key: Raw override key for diagnostics.

        Returns:
            List[SocketRef]: Matching mutation sockets.

        Raises:
            MeldExecutionError: If the spec is invalid or yields no sockets.
        """
        if spec.kind is TargetSpecKind.PATH:
            return self._resolve_mutation_override_by_path(
                spec=spec,
                dag_index=dag_index,
                raw_key=raw_key,
            )
        if spec.kind is TargetSpecKind.UNIQUE:
            return self._resolve_mutation_override_by_unique(
                spec=spec,
                dag_index=dag_index,
                raw_key=raw_key,
            )
        if spec.kind is TargetSpecKind.BROADCAST:
            return self._resolve_mutation_override_by_broadcast(
                spec=spec,
                dag_index=dag_index,
                raw_key=raw_key,
            )

        raise MeldExecutionError(
            spell_id=self._root_spell.spell_index.current,
            spell_name=self._root_spell.spell_name,
            message="Unsupported TargetSpecKind for override {0!r}.".format(raw_key),
        )

    def _resolve_mutation_override_by_path(
            self,
            *,
            spec: TargetSpec,
            dag_index: DagIndex,
            raw_key: str,
    ) -> List[SocketRef]:
        """
        Resolve a PATH TargetSpec to mutation sockets.

        Args:
            spec: PATH TargetSpec.
            dag_index: DagIndex used for socket targeting.
            raw_key: Raw override key for diagnostics.

        Returns:
            List[SocketRef]: Matching mutation sockets.

        Raises:
            MeldExecutionError: If no sockets are found for the path.
        """
        if not spec.path:
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message=(
                    "Path override key {0!r} did not contain any segments."
                ).format(raw_key),
            )
        candidates = dag_index.get_by_exact_path(spec.path)
        matches = self._filter_mutation_contract_sockets(candidates)
        if not matches:
            path_str = ">".join(spec.path)
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message=(
                    "No mutation sockets found for override path "
                    "'{0}'."
                ).format(path_str),
            )
        return matches

    def _resolve_mutation_override_by_unique(
            self,
            *,
            spec: TargetSpec,
            dag_index: DagIndex,
            raw_key: str,
    ) -> List[SocketRef]:
        """
        Resolve a UNIQUE TargetSpec to a single mutation socket.

        Args:
            spec: UNIQUE TargetSpec.
            dag_index: DagIndex used for socket targeting.
            raw_key: Raw override key for diagnostics.

        Returns:
            List[SocketRef]: Single matching mutation socket.

        Raises:
            MeldExecutionError: If zero or multiple sockets match.
        """
        if not spec.param_name:
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message=(
                    "Unique override key {0!r} is missing a parameter name."
                ).format(raw_key),
            )
        candidates = dag_index.get_by_name(spec.param_name)
        matches = self._filter_mutation_contract_sockets(candidates)
        count = len(matches)
        if count == 0:
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message=(
                    "No mutation sockets found for unique override "
                    "'*{0}'."
                ).format(spec.param_name),
            )
        if count > 1:
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message=(
                    "Unique override matched multiple mutation sockets "
                    "for '*{0}'."
                ).format(spec.param_name),
            )
        return matches

    def _resolve_mutation_override_by_broadcast(
            self,
            *,
            spec: TargetSpec,
            dag_index: DagIndex,
            raw_key: str,
    ) -> List[SocketRef]:
        """
        Resolve a BROADCAST TargetSpec to mutation sockets.

        Args:
            spec: BROADCAST TargetSpec.
            dag_index: DagIndex used for socket targeting.
            raw_key: Raw override key for diagnostics.

        Returns:
            List[SocketRef]: Matching mutation sockets.

        Raises:
            MeldExecutionError: If no sockets match.
        """
        if not spec.param_name:
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message=(
                    "Broadcast override key {0!r} is missing a parameter name."
                ).format(raw_key),
            )
        candidates = dag_index.get_by_name(spec.param_name)
        matches = self._filter_mutation_contract_sockets(candidates)
        if not matches:
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message=(
                    "No mutation sockets found for broadcast override "
                    "'**{0}'."
                ).format(spec.param_name),
            )
        return matches

    @staticmethod
    def _filter_mutation_contract_sockets(
            sockets: Sequence[SocketRef],
    ) -> List[SocketRef]:
        """
        Filter sockets to only mutation contract sockets.

        Args:
            sockets: Socket candidates.

        Returns:
            List[SocketRef]: Mutation contract sockets.
        """
        return [
            socket
            for socket in sockets
            if socket.socket_kind is SocketKind.MUTATION_CONTRACT
        ]

    def _apply_mutation_overrides_to_dependencies(
            self,
            *,
            dependencies: Dict[str, List[OccurrenceKey]],
            occurrence: OccurrenceKey,
    ) -> None:
        """
        Overlay mutation overrides onto dependency occurrences.

        Contract:
            - Overrides are matched against the occurrence path for disambiguation.
            - Overrides replace the dependency list for the targeted parameter.

        Args:
            dependencies: Parameter-to-occurrence mapping to update in-place.
            occurrence: The (spell_id, path) occurrence being expanded.
        """
        if self._blueprint is None:
            return

        spell_id, path = occurrence
        spell = self._spell_lookup.get(spell_id)
        if spell is None and spell_id == self._root_spell.spell_index.current:
            spell = self._root_spell
        if spell is None:
            return

        mutation_override = spell.mutation_override
        if not mutation_override:
            return

        override_targets = self._resolve_mutation_override_targets(
            mutation_override=mutation_override,
            dag_index=self._blueprint.dag_index,
        )

        for socket_ref, target_id in override_targets:
            if socket_ref.node_id != spell_id:
                continue
            if socket_ref.param_path[:-1] != path:
                continue
            param_name = socket_ref.param_name
            child_occurrence = (target_id, path + (param_name,))
            dependencies[param_name] = [child_occurrence]

    def _build_instance_plan(
            self,
            *,
            occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]],
            root_spell_id: str,
    ) -> Tuple[
        Dict[str, List[InstanceKey]],
        Dict[str, OccurrenceKey],
        InstanceKey,
        Set[str],
    ]:
        """
        Build per-spell instance keys and canonical occurrences.

        Contract:
            - Existence.many yields one instance per occurrence path.
            - Shared existences yield a single instance with a canonical path.

        Args:
            occurrence_graph: Path-aware occurrence graph.
            root_spell_id: Root spell id for the plan.

        Returns:
            Tuple:
                - Dict[str, List[InstanceKey]]: Instance keys per spell id.
                - Dict[str, OccurrenceKey]: Canonical occurrence per shared spell.
                - InstanceKey: Root instance key.
                - Set[str]: Shared spell ids.
        """
        occurrences_by_spell_id: Dict[str, List[OccurrenceKey]] = defaultdict(list)
        for occurrence in occurrence_graph:
            spell_id, _ = occurrence
            occurrences_by_spell_id[spell_id].append(occurrence)

        instance_keys_by_spell_id: Dict[str, List[InstanceKey]] = {}
        canonical_occurrences_by_spell_id: Dict[str, OccurrenceKey] = {}
        shared_spell_ids: Set[str] = set()

        for spell_id, occurrences in occurrences_by_spell_id.items():
            spell = self._spell_lookup.get(spell_id)
            if spell is None:
                if spell_id == root_spell_id:
                    spell = self._root_spell
                else:
                    raise MeldExecutionError(
                        spell_id=spell_id,
                        spell_name=spell_id,
                        message=(
                            "Dependency spell with id '{0}' not found in spellbook for plan."
                        ).format(spell_id),
                    )

            if self._is_shared_existence(spell.existence):
                shared_spell_ids.add(spell_id)
                canonical = self._select_canonical_occurrence(occurrences)
                canonical_occurrences_by_spell_id[spell_id] = canonical
                instance_keys_by_spell_id[spell_id] = [(spell_id, None)]
            else:
                sorted_occurrences = sorted(occurrences, key=lambda entry: entry[1])
                instance_keys_by_spell_id[spell_id] = [
                    (spell_id, path) for _, path in sorted_occurrences
                ]

        root_occurrence = (root_spell_id, ())
        root_instance_key = self._instance_key_for_occurrence(root_occurrence)

        return (
            instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id,
            root_instance_key,
            shared_spell_ids,
        )

    @staticmethod
    def _select_canonical_occurrence(
            occurrences: Sequence[OccurrenceKey],
    ) -> OccurrenceKey:
        """
        Pick a stable occurrence for shared instance dependency paths.

        Contract:
            - The canonical occurrence is the one with the lexicographically
              smallest path.

        Args:
            occurrences: Occurrences for the same spell id.

        Returns:
            OccurrenceKey: The canonical occurrence.
        """
        return min(occurrences, key=lambda entry: entry[1])

    def _instance_key_for_occurrence(
            self,
            occurrence: OccurrenceKey,
    ) -> InstanceKey:
        """
        Map an occurrence to its instance key based on existence policy.

        Contract:
            - Shared existences use a None path.
            - Existence.many preserves the occurrence path.

        Args:
            occurrence: The (spell_id, path) occurrence to map.

        Returns:
            InstanceKey: Instance key for the occurrence.

        Raises:
            MeldExecutionError: If the spell id cannot be resolved.
        """
        spell_id, path = occurrence
        spell = self._spell_lookup.get(spell_id)
        if spell is None:
            root_id = self._root_spell.spell_index.current
            if spell_id == root_id:
                spell = self._root_spell
            else:
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_id,
                    message=(
                        "Dependency spell with id '{0}' not found in spellbook for plan."
                    ).format(spell_id),
                )
        if self._is_shared_existence(spell.existence):
            return spell_id, None
        return spell_id, path
