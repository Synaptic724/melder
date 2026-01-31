from collections import defaultdict, deque
from dataclasses import dataclass
import inspect
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.dag.target_spec import TargetSpec, TargetSpecKind
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.interfaces.interfaces import ISpell

OccurrenceKey = Tuple[str, Tuple[str, ...]]
InstanceKey = Tuple[str, Optional[Tuple[str, ...]]]


@dataclass(frozen=True)
class OccurrencePlanSelection:
    """
    Internal

    Runtime-ready selection derived from a Phase 8 OccurrencePlan.

    Purpose:
        Bundle the occurrence plan data needed by meld runtime execution while
        keeping selection logic in the Phase 8 module.
    """
    __melder_internal__ = _mrg.sentinel
    occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]]
    execution_order: List[str]
    instance_keys_by_spell_id: Dict[str, List[InstanceKey]]
    canonical_occurrences_by_spell_id: Dict[str, OccurrenceKey]
    root_instance_key: InstanceKey
    shared_spell_ids: Set[str]
    contract_overrides_by_occurrence: Dict[OccurrenceKey, Dict[str, Any]]
    contract_overrides_by_spell_id: Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]]


def select_occurrence_plan(
        plan: Optional["OccurrencePlan"],
        *,
        root_spell_id: str,
) -> Optional[OccurrencePlanSelection]:
    """
    Determine whether a Phase 8 OccurrencePlan can drive a meld execution.

    Contract:
        - Assumes plan is not None; callers own any availability checks.
        - Does not filter on contract completeness; callers decide how to handle
          missing SpellContract providers.
        - Uses plan-provided contract override mappings when available.

    Args:
        plan: Phase 8 OccurrencePlan or None.
        root_spell_id: Current root spell id for this execution.

    Returns:
        Optional[OccurrencePlanSelection]: Selected plan data for runtime use.
    """
    return OccurrencePlanSelection(
        occurrence_graph=plan.occurrence_graph,
        execution_order=plan.execution_order,
        instance_keys_by_spell_id=plan.instance_keys_by_spell_id,
        canonical_occurrences_by_spell_id=plan.canonical_occurrences_by_spell_id,
        root_instance_key=plan.root_instance_key,
        shared_spell_ids=plan.shared_spell_ids,
        contract_overrides_by_occurrence=plan.contract_overrides_by_occurrence,
        contract_overrides_by_spell_id=plan.contract_overrides_by_spell_id,
    )


class OccurrencePlan(Cleanable):
    """
    Internal

    Phase 8 artifact that captures occurrence expansion and execution ordering
    for a single root blueprint.

    Purpose:
        Precompute the path-aware occurrence graph and instance planning that
        the meld runtime currently builds per call, including resolved
        SpellContract override payloads when available.

    Contract:
        - Instances are treated as immutable once built.
        - This object owns the provided collections and clears them on cleanup.
        - root_spell_id must be the version id used to build the plan.
        - Contract override payloads are recorded only for resolved providers.
        - Contract dependencies are required in automatic mode; dynamic mode may
          leave them incomplete until contracts are linked and phases re-run.

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
        "_contract_overrides_by_occurrence",
        "_contract_overrides_by_spell_id",
        "_contract_dependencies_complete",
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
            contract_overrides_by_occurrence: Dict[OccurrenceKey, Dict[str, Any]],
            contract_overrides_by_spell_id: Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]],
            contract_dependencies_complete: bool,
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
            contract_overrides_by_occurrence:
                Mapping of provider occurrences to normalized SpellContract override payloads.
            contract_overrides_by_spell_id:
                Mapping of provider spell ids to (occurrence, override) payloads.
            contract_dependencies_complete:
                True when all SpellContract dependencies were resolved for this
                plan. In automatic mode, missing providers raise during build.

        Raises:
            ValueError:
                If any required input is None.
        """
        super().__init__()

        self._root_spell_id = root_spell_id
        self._occurrence_graph = occurrence_graph
        self._execution_order = execution_order
        self._instance_keys_by_spell_id = instance_keys_by_spell_id
        self._canonical_occurrences_by_spell_id = canonical_occurrences_by_spell_id
        self._root_instance_key = root_instance_key
        self._shared_spell_ids = shared_spell_ids
        self._contract_overrides_by_occurrence = contract_overrides_by_occurrence
        self._contract_overrides_by_spell_id = contract_overrides_by_spell_id
        self._contract_dependencies_complete = contract_dependencies_complete

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
        self._contract_overrides_by_occurrence.clear()
        self._contract_overrides_by_spell_id.clear()

        self._root_spell_id = None
        self._occurrence_graph = None
        self._execution_order = None
        self._instance_keys_by_spell_id = None
        self._canonical_occurrences_by_spell_id = None
        self._root_instance_key = None
        self._shared_spell_ids = None
        self._contract_overrides_by_occurrence = None
        self._contract_overrides_by_spell_id = None
        self._contract_dependencies_complete = None

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

    @property
    def contract_overrides_by_occurrence(self) -> Dict[OccurrenceKey, Dict[str, Any]]:
        """
        Return SpellContract override payloads keyed by provider occurrence.

        Contract:
            - The returned mapping is owned by the plan and should be treated
              as read-only by callers.
        """
        self.check_cleaned()
        return self._contract_overrides_by_occurrence

    @property
    def contract_overrides_by_spell_id(
            self,
    ) -> Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]]:
        """
        Return SpellContract override payloads grouped by provider spell id.

        Contract:
            - The returned mapping is owned by the plan and should be treated
              as read-only by callers.
        """
        self.check_cleaned()
        return self._contract_overrides_by_spell_id

    @property
    def contract_dependencies_complete(self) -> bool:
        """
        Indicate whether SpellContract dependencies were fully resolved.

        Contract:
            - True only when every SpellContract dependency resolved to an
              occurrence in the plan graph.
            - In automatic mode, missing providers raise during build, so this is
              expected to be True for valid plans.
        """
        self.check_cleaned()
        return self._contract_dependencies_complete


class OccurrencePlanBuilder(object):
    """
    Internal

    Phase 8 compiler that mirrors the runtime occurrence planning logic from
    MeldEngine and produces an OccurrencePlan artifact.

    Purpose:
        Convert a RootResolutionBlueprint and spell metadata into a reusable
        occurrence plan for fast meld execution, including contract override
        payload maps when providers are available.

    Contract:
        - This builder does not own any referenced objects.
        - Inputs must remain valid for the duration of build().
        - SpellContract resolution is attempted when providers are available.
        - SpellContract providers are required in automatic mode.
        - Dynamic mode may allow missing providers during plan build.
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
        self._root_spell = root_spell
        self._blueprint = blueprint
        self._spell_lookup = spell_lookup
        self._system_states = system_states

    def build(self) -> OccurrencePlan:
        """
        Build and return the OccurrencePlan for the configured root blueprint.

        Contract:
            - Mirrors MeldEngine occurrence planning behavior.
            - Compiles SpellContract override payloads for resolved dependencies.
            - Raises MeldExecutionError when dependency spells cannot be resolved
              in automatic mode.

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
        (
            contract_overrides_by_occurrence,
            contract_overrides_by_spell_id,
            contract_dependencies_complete,
        ) = self._compile_contract_overrides(
            occurrence_graph=occurrence_graph,
        )

        return OccurrencePlan(
            root_spell_id=root_spell_id,
            occurrence_graph=occurrence_graph,
            execution_order=execution_order,
            instance_keys_by_spell_id=instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
            root_instance_key=root_instance_key,
            shared_spell_ids=shared_spell_ids,
            contract_overrides_by_occurrence=contract_overrides_by_occurrence,
            contract_overrides_by_spell_id=contract_overrides_by_spell_id,
            contract_dependencies_complete=contract_dependencies_complete,
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
            - Preserves queue insertion order (no tie-break sorting).
            - If cycles are detected, returns fallback_order first, then remaining
              nodes in set-iteration order.

        Args:
            occurrence_graph: Path-aware occurrence graph.
            fallback_order: Blueprint order used as a stable tie-breaker.

        Returns:
            List[str]: Spell ids in execution order.
        """
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

        queue = [node_id for node_id, degree in indegree.items() if degree == 0]
        order: List[str] = []

        queue_idx = 0
        while queue_idx < len(queue):
            node_id = queue[queue_idx]
            queue_idx += 1
            order.append(node_id)
            for child_id in edges.get(node_id, []):
                indegree[child_id] -= 1
                if indegree[child_id] == 0:
                    queue.append(child_id)

        if len(order) == len(nodes):
            return order

        resolved: List[str] = []
        seen: Set[str] = set()
        for node_id in fallback_order or []:
            if node_id in nodes and node_id not in seen:
                seen.add(node_id)
                resolved.append(node_id)
        for node_id in nodes:
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
            - Automatic mode treats missing SpellContract providers as build-time errors.
            - Dynamic mode tolerates missing SpellContract providers.

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
        topology = self._system_states._local_topologies.get(spell_id)
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
            - Skips DAG edges that have no param metadata.

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
        for parent_node in node.dependencies:
            param_name = node.incoming_params.get(parent_node)
            if param_name is None:
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

            dependencies.setdefault(param_name, []).append(child_occurrence)

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
            - Missing contracts raise during plan build in automatic mode.
            - Missing contracts are ignored during plan build in dynamic mode.

        Args:
            dependencies: Mapping to update with contract dependencies.
            occurrence: The (spell_id, path) occurrence being expanded.

        Raises:
            MeldExecutionError: If a SpellContract is ambiguous or inconsistent.
        """
        spell_id, path = occurrence
        spell = self._spell_lookup[spell_id]
        allow_missing = self._allow_missing_contract_providers()

        for param_name, contract in self._iter_spell_contract_defaults(spell):
            target_spell_id = self._resolve_spell_contract_spell_id(
                contract=contract,
                consumer_spell=spell,
                param_name=param_name,
                allow_missing=allow_missing,
            )
            if target_spell_id is None:
                continue
            child_occurrence = (target_spell_id, path + (param_name,))
            dependencies.setdefault(param_name, []).append(child_occurrence)

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
        signature = inspect.signature(call_target)

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
            allow_missing:
                When True, missing providers return None instead of raising.
                Use this for dynamic mode when providers may be linked later.

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

        if allow_missing:
            return None
        raise MeldExecutionError(
            spell_id=consumer_spell_id,
            spell_name=consumer_spell_name,
            node_id=consumer_spell_id,
            param_name=param_name,
            message=(
                "SpellContract could not be resolved. "
                "No contracted spell matched the contract."
            ),
        )

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
            Missing contract keys yield an empty list.
        """
        spellbook = self._root_spell._spellbook
        contracted_lookup = spellbook._lookup_contracted_spells
        contracted_maps = spellbook._contracted_spells

        contracted_candidates: List[ISpell] = []
        for conduit_id, lookup_map in contracted_lookup.items():
            spell_index = lookup_map.get(contract_key)
            if spell_index is None:
                continue
            contracted_map = contracted_maps.get(conduit_id)
            if contracted_map is None:
                continue
            spell_obj = contracted_map.get(spell_index)
            if spell_obj is None:
                continue
            contracted_candidates.append(spell_obj)

        return contracted_candidates

    def _allow_missing_contract_providers(self) -> bool:
        """
        Determine whether plan build may tolerate missing SpellContract providers.

        Contract:
            - True only when system_state is dynamic.
            - Automatic mode remains strict and requires providers to resolve.
        """
        spellbook = self._root_spell._spellbook
        system_state = spellbook._configuration.get_property("system_state")
        state_enum = EnumHelpers.convert_enum_and_check(system_state, SystemState)
        return state_enum is SystemState.dynamic

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
        spell_id, path = occurrence
        spell = self._spell_lookup[spell_id]
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
            spell = self._spell_lookup[spell_id]

            if self._is_shared_existence(spell.existence):
                shared_spell_ids.add(spell_id)
                canonical = self._select_canonical_occurrence(occurrences)
                canonical_occurrences_by_spell_id[spell_id] = canonical
                instance_keys_by_spell_id[spell_id] = [(spell_id, None)]
            else:
                instance_keys_by_spell_id[spell_id] = [
                    (spell_id, path) for _, path in occurrences
                ]

        root_occurrence = (root_spell_id, ())
        root_instance_key = self._instance_key_for_occurrence(root_occurrence)

        return (
            instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id,
            root_instance_key,
            shared_spell_ids,
        )

    def _compile_contract_overrides(
            self,
            *,
            occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]],
    ) -> Tuple[
        Dict[OccurrenceKey, Dict[str, Any]],
        Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]],
        bool,
    ]:
        """
        Compile SpellContract override payload maps for the plan.

        Contract:
            - Missing providers raise MeldExecutionError in automatic mode.
            - Missing providers mark the plan incomplete in dynamic mode.
            - Invalid override payloads raise MeldExecutionError.
            - Records overrides only when payloads are non-empty and occurrences exist.

        Args:
            occurrence_graph: Occurrence graph to validate against.

        Returns:
            Tuple:
                - overrides_by_occurrence: Provider occurrence -> override payload.
                - overrides_by_spell_id: Provider spell id -> list of overrides.
                - complete: True if all contract dependencies were resolved and aligned.
        """
        overrides_by_occurrence: Dict[OccurrenceKey, Dict[str, Any]] = {}
        overrides_by_spell_id: Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]] = {}
        complete = True

        for occurrence, dependencies in occurrence_graph.items():
            overrides_by_occurrence.setdefault(occurrence, {})
            is_complete = self._compile_contract_overrides_for_occurrence(
                occurrence=occurrence,
                dependencies=dependencies,
                overrides_by_occurrence=overrides_by_occurrence,
                overrides_by_spell_id=overrides_by_spell_id,
            )
            if not is_complete:
                complete = False

        return overrides_by_occurrence, overrides_by_spell_id, complete

    def _compile_contract_overrides_for_occurrence(
            self,
            *,
            occurrence: OccurrenceKey,
            dependencies: Dict[str, List[OccurrenceKey]],
            overrides_by_occurrence: Dict[OccurrenceKey, Dict[str, Any]],
            overrides_by_spell_id: Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]],
    ) -> bool:
        """
        Compile SpellContract override payloads for a single occurrence.

        Contract:
            - Raises when a contract provider is missing in automatic mode.
            - Missing providers mark this occurrence incomplete in dynamic mode.
            - Raises when an override payload is invalid.
            - Records overrides only when payloads are non-empty.

        Args:
            occurrence: Current (spell_id, path) occurrence.
            dependencies: Dependency map for the occurrence.
            overrides_by_occurrence: Map to update with occurrence overrides.
            overrides_by_spell_id: Map to update with spell-id overrides.

        Returns:
            bool: True when contract dependencies and overrides aligned for
            this occurrence. In automatic mode, missing providers raise.
        """
        spell = self._resolve_occurrence_spell(occurrence)
        _, path = occurrence
        complete = True
        allow_missing = self._allow_missing_contract_providers()

        for param_name, contract in self._iter_spell_contract_defaults(spell):
            target_spell_id = self._resolve_spell_contract_spell_id(
                contract=contract,
                consumer_spell=spell,
                param_name=param_name,
                allow_missing=allow_missing,
            )
            if target_spell_id is None:
                complete = False
                continue

            child_occurrence = (target_spell_id, path + (param_name,))

            normalized = self._normalize_contract_override_payload(
                payload=contract.spell_override,
                consumer_spell_id=spell.spell_index.current,
                consumer_spell_name=spell.spell_name,
                param_name=param_name,
            )
            if not normalized:
                continue

            self._record_contract_override(
                occurrence=child_occurrence,
                spell_id=target_spell_id,
                overrides_by_occurrence=overrides_by_occurrence,
                overrides_by_spell_id=overrides_by_spell_id,
                normalized_payload=normalized,
            )

        return complete

    def _resolve_occurrence_spell(
            self,
            occurrence: OccurrenceKey,
    ) -> Optional[ISpell]:
        """
        Resolve the spell object for a plan occurrence.

        Contract:
            - Returns the root spell when the occurrence matches the root id.
            - Returns None when no spell is available for the occurrence.

        Args:
            occurrence: (spell_id, path) tuple from the occurrence graph.

        Returns:
            Optional[ISpell]: The spell object, or None if missing.
        """
        spell_id, _ = occurrence
        return self._spell_lookup[spell_id]

    @staticmethod
    def _normalize_contract_override_payload(
            *,
            payload: Any,
            consumer_spell_id: str,
            consumer_spell_name: str,
            param_name: str,
    ) -> Dict[str, Any]:
        """
        Normalize a SpellContract override payload for plan storage.

        Contract:
            - dict payloads are stored verbatim (no copy).
            - list/tuple payloads become {"__args__": payload}.

        Args:
            payload: Raw spell_override payload from the SpellContract.
            consumer_spell_id: Spell id for diagnostics.
            consumer_spell_name: Spell name for diagnostics.
            param_name: Parameter name for diagnostics.

        Returns:
            Dict[str, Any]: Normalized override payload.

        Raises:
            MeldExecutionError: If the payload is not a dict, list, or tuple, or
                if __args__ is not a list/tuple when provided.
        """
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, (list, tuple)):
            return {"__args__": payload}
        raise MeldExecutionError(
            spell_id=consumer_spell_id,
            spell_name=consumer_spell_name,
            node_id=consumer_spell_id,
            param_name=param_name,
            message="SpellContract spell_override must be a dict, list, or tuple.",
        )

    @staticmethod
    def _record_contract_override(
            *,
            occurrence: OccurrenceKey,
            spell_id: str,
            overrides_by_occurrence: Dict[OccurrenceKey, Dict[str, Any]],
            overrides_by_spell_id: Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]],
            normalized_payload: Dict[str, Any],
    ) -> None:
        """
        Record a normalized SpellContract override payload.

        Contract:
            - Stores payloads for both occurrence and spell id lookup.
            - Payloads are copied on insert to prevent external mutation.

        Args:
            occurrence: Provider occurrence receiving the override.
            spell_id: Provider spell id.
            overrides_by_occurrence: Map to update with occurrence overrides.
            overrides_by_spell_id: Map to update with spell-id overrides.
            normalized_payload: Normalized override payload to store.

        Returns:
            None.
        """
        overrides_by_occurrence[occurrence] = normalized_payload
        overrides_by_spell_id.setdefault(spell_id, []).append(
            (occurrence, normalized_payload)
        )

    @staticmethod
    def _select_canonical_occurrence(
            occurrences: Sequence[OccurrenceKey],
    ) -> OccurrenceKey:
        """
        Pick a stable occurrence for shared instance dependency paths.

        Contract:
            - The canonical occurrence is the first entry in the provided
              sequence (no lexicographic ordering).

        Args:
            occurrences: Occurrences for the same spell id.

        Returns:
            OccurrenceKey: The canonical occurrence.
        """
        return occurrences[0]

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
        spell = self._spell_lookup[spell_id]
        if self._is_shared_existence(spell.existence):
            return spell_id, None
        return spell_id, path
