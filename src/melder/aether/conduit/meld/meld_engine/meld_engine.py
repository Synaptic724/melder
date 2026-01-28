from collections import defaultdict, deque
import inspect
from threading import RLock
from typing import Any, Callable, Dict, Iterable, List, MutableMapping, Optional, Sequence, Set, Tuple

# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.utilities.interfaces.interfaces import ISpell, ICreations
from melder.spellbook.spell_crafter.dag.resolution_frame.resolution_frame import (
    ResolutionFrame,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.blueprints.injection_plan import (
    InjectionPlan,
    InjectionSpec,
)
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import OccurrencePlan
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.dag.target_spec import TargetSpec, TargetSpecKind
from melder.spellbook.existence.existence import Existence
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.lesser_creations import LesserCreations
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract

_OccurrenceKey = tuple[str, tuple[str, ...]]
_InstanceKey = tuple[str, Optional[tuple[str, ...]]]


class MeldEngine(Cleanable):
    """
    Per-meld-call execution engine.

    This class turns a validated spell + context into a concrete instance by
    walking the deep `RootResolutionBlueprint` DAG when available. It:

        * Walks the DirectedAcyclicWorkGraph from Phase 5 in topological order.
        * Builds constructor arguments from dependency results and socket-level overrides.
        * Applies reuse/registration according to Existence and Creations/LesserCreations.
        * Stores per-node results into a ResolutionFrame.

    If no blueprint is present, it falls back to single-node construction using
    the root spell and per-call overrides.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_context",
        "_root_spell",
        "_dag",
        "_resolution_frame",
        "_requirements",
        "_frame",
        "_logger",
        "_blueprint",
        "_override_map",
        "_spell_lookup",
        "_system_states",
        "_instance_results",
        "_override_targets_by_spell_id",
        "_any_overrides_present",
        "_contract_overrides_by_occurrence",
        "_contract_overrides_by_spell_id",
        "_occurrence_plan",
        "_injection_plan",
    ]

    def __init__(
            self,
            *,
            context: "MeldContext",
            root_spell: ISpell,
            dag: Any,
            resolution_frame: Any,
            requirements: Any,
            frame: ResolutionFrame,
            blueprint: Optional[RootResolutionBlueprint],
            override_map: Dict[SocketRef, Any],
            spell_lookup: Dict[str, ISpell],
            system_states: Any,
            occurrence_plan: Optional[OccurrencePlan] = None,
            injection_plan: Optional[InjectionPlan] = None,
    ) -> None:
        """
        Initialize a new `MeldEngine` for a single meld call.

        Args:
            context: The per-call `MeldContext` carrying creations,
                overrides, cancellation, etc.
            root_spell: The root `ISpell` being activated.
            dag: The `DirectedAcyclicWorkGraph` describing the local
                dependency graph for this spell (currently unused in the
                MVP, but kept for future DAG-based execution).
            resolution_frame: The `SpellResolutionFrame` describing the
                root spell's DAG metadata (root node id, ordering, etc.).
            requirements: The `SpellRequirements` object describing the
                root spell's parameter requirements (currently not used
                directly in the MVP constructor path).
            frame: The per-execution `ResolutionFrame` that holds
                overrides, node results, and errors.
            blueprint: RootResolutionBlueprint for deep DAG execution (may be None).
            override_map: SocketRef -> value overrides computed by SpellOverrider.
            spell_lookup: mapping of spell_id -> ISpell for all nodes in the DAG.
            system_states: SpellSystemStates handle (used to resolve topologies).
            occurrence_plan:
                Optional Phase 8 OccurrencePlan to reuse occurrence expansion and
                execution ordering for this root spell.
            injection_plan:
                Optional Phase 9 InjectionPlan to reuse dependency wiring for
                per-instance keyword arguments.
            logger: Optional logger; will be normalized to `SafeLogger`
                if provided.

        Raises:
            ValueError: If any of the required arguments (`context`,
                `root_spell`, `frame`) is `None`.
        """
        super().__init__()

        if context is None:
            raise ValueError("context cannot be None.")
        if root_spell is None:
            raise ValueError("root_spell cannot be None.")
        if frame is None:
            raise ValueError("frame cannot be None.")

        self._lock: RLock = RLock()
        self._context: "MeldContext" = context
        self._root_spell: ISpell = root_spell

        self._dag: Any = dag
        self._resolution_frame: Any = resolution_frame
        self._requirements: Any = requirements
        self._frame: ResolutionFrame = frame
        self._blueprint: Optional[RootResolutionBlueprint] = blueprint
        self._override_map: Dict[SocketRef, Any] = override_map or {}
        self._spell_lookup: Dict[str, ISpell] = spell_lookup or {}
        self._system_states = system_states
        self._instance_results: Dict[_InstanceKey, Any] = {}
        self._override_targets_by_spell_id: Dict[str, List[SocketRef]] = {}
        self._any_overrides_present: bool = False
        self._contract_overrides_by_occurrence: Dict[_OccurrenceKey, Any] = {}
        self._contract_overrides_by_spell_id: Dict[str, List[tuple[_OccurrenceKey, Any]]] = {}
        self._occurrence_plan: Optional[OccurrencePlan] = occurrence_plan
        self._injection_plan: Optional[InjectionPlan] = injection_plan

    # ------------------------------------------------------------------ #
    # Cleanup
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically clear references held by this engine.

        The runtime owns the lifetime of the engine; after `run()` has
        completed (success or error), it is responsible for calling
        `cleanup()` to drop references to the context, spell, DAG, and
        frame so they are eligible for GC.

        This method is:

            * Idempotent – calling it multiple times is safe.
            * Thread-safe – guarded by an internal `RLock`.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._context = None
            self._root_spell = None
            self._dag = None
            self._resolution_frame = None
            self._requirements = None
            self._frame = None
            self._blueprint = None
            self._override_map = None
            self._spell_lookup = None
            self._system_states = None
            self._instance_results = None
            self._override_targets_by_spell_id = None
            self._any_overrides_present = None
            self._contract_overrides_by_occurrence = None
            self._contract_overrides_by_spell_id = None
            self._occurrence_plan = None
            self._injection_plan = None
            self._cleaned = True

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def context(self) -> "MeldContext":
        """
        Return the per-call `MeldContext` associated with this engine.

        The context is owned by the caller (typically `MeldRuntime`) and
        is expected to be cleaned up by the caller after `run()` has
        finished.
        """
        return self._context

    @property
    def root_spell(self) -> ISpell:
        """
        Return the root spell being activated for this meld call.
        """
        return self._root_spell

    @property
    def frame(self) -> ResolutionFrame:
        """
        Return the `ResolutionFrame` that holds overrides, per-node
        results, and errors for this meld call.
        """
        return self._frame

    # ------------------------------------------------------------------ #
    # Core execution
    # ------------------------------------------------------------------ #

    def run(self) -> Any:
        """
        Purpose:
            Execute a meld call and return the constructed root instance.
        Side Effects:
            - Stores constructed instances in the ResolutionFrame.
            - Mutates internal instance results and override tracking.
            - Invokes spell callables to construct instances.
        Args:
            None.
        Returns:
            Any: The constructed root instance.
        Raises:
            MeldExecutionError: If resolution fails, dependencies are missing,
                or override conflicts are detected.
            OperationCancelledError: If cancellation is signalled mid-run.

        Notes:
            Executes the deep DAG in dependency-safe order when a blueprint
            is available. SpellContract sockets are resolved during occurrence
            expansion using contracted spells. When a Phase 8 OccurrencePlan
            is present, the engine reuses its occurrence graph and execution
            order.
        """
        self.check_cleaned()

        cancel_event: Optional[CancellationEvent] = self._context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        self._override_targets_by_spell_id = self._collect_override_targets(
            self._override_map
        )

        # If we have a deep blueprint, walk it; otherwise fall back to root-only.
        if self._blueprint is None or not self._blueprint.ordered_node_ids:
            instance_key = self._instance_key_for_root()
            instance, _ = self._resolve_spell_instance(
                self._root_spell,
                construct_fn=self._construct_root_only,
            )
            self._store_instance_result(instance_key, instance)
            return instance

        blueprint = self._blueprint
        ordered_ids = blueprint.ordered_node_ids
        dag = blueprint.dag
        root_id = self._root_spell.spell_index.current

        plan_data = self._select_occurrence_plan(
            root_spell_id=root_id,
        )
        if plan_data is None:
            occurrence_graph = self._build_occurrence_graph(
                dag=dag,
                root_spell_id=root_id,
            )
            self._extend_occurrence_graph_with_ordered_nodes(
                occurrence_graph=occurrence_graph,
                ordered_node_ids=ordered_ids,
                dag=dag,
            )
            execution_order = self._build_execution_order(
                occurrence_graph=occurrence_graph,
                fallback_order=ordered_ids,
            )
            (
                instance_keys_by_spell_id,
                canonical_occurrences_by_spell_id,
                root_instance_key,
                shared_spell_ids,
            ) = self._build_instance_plan(
                occurrence_graph=occurrence_graph,
                root_spell_id=root_id,
            )
        else:
            (
                occurrence_graph,
                execution_order,
                instance_keys_by_spell_id,
                canonical_occurrences_by_spell_id,
                root_instance_key,
                shared_spell_ids,
            ) = plan_data

        injection_plan = None
        if plan_data is not None:
            injection_plan = self._select_injection_plan(root_spell_id=root_id)

        self._any_overrides_present = self._detect_any_overrides()
        self._validate_shared_override_targets(shared_spell_ids)

        for node_id in execution_order:
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            spell = self._spell_lookup.get(node_id)
            if spell is None and node_id == root_id:
                spell = self._root_spell
            if spell is None:
                raise MeldExecutionError(
                    spell_id=node_id,
                    spell_name=node_id,
                    message=f"Spell with id '{node_id}' not found in spellbook for meld.",
                )

            instance_keys = instance_keys_by_spell_id.get(node_id, [])
            for instance_key in instance_keys:
                def _construct_node(
                        *,
                        instance_key: _InstanceKey = instance_key,
                        spell: ISpell = spell,
                ) -> Any:
                    contract_override = self._get_contract_override_payload_for_instance(
                        instance_key=instance_key,
                        canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
                    )
                    injection_spec = None
                    if injection_plan is not None:
                        injection_spec = injection_plan.get(instance_key)
                    if injection_spec is not None:
                        kwargs = self._build_kwargs_for_instance_from_plan(
                            instance_key=instance_key,
                            injection_spec=injection_spec,
                            canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
                            contract_override=contract_override,
                        )
                    else:
                        kwargs = self._build_kwargs_for_instance(
                            instance_key=instance_key,
                            occurrence_graph=occurrence_graph,
                            canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
                            contract_override=contract_override,
                        )
                    return self._construct_spell(spell, kwargs)

                instance, _ = self._resolve_spell_instance(
                    spell,
                    construct_fn=_construct_node,
                )
                self._store_instance_result(instance_key, instance)
                if cancel_event is not None and cancel_event.is_set:
                    cancel_event.throw_if_set()

        try:
            return self._get_instance_result(root_instance_key)
        except MeldExecutionError:
            # If the blueprint didn't include the root (unlikely), build root directly.
            fallback_key = self._instance_key_for_root()
            instance, _ = self._resolve_spell_instance(
                self._root_spell,
                construct_fn=self._construct_root_only,
            )
            self._store_instance_result(fallback_key, instance)
            return instance

    # ------------------------------------------------------------------ #
    # Instance planning
    # ------------------------------------------------------------------ #

    def _detect_any_overrides(self) -> bool:
        """
        Purpose:
            Determine whether this meld call carries any overrides.
        Contract:
            - Returns True when either socket-level overrides or root-level
              overrides are present.
            - Contract-level overrides are treated as overrides when non-empty.
            - Empty override maps and empty frame overrides are treated as
              no overrides.
        Returns:
            bool: True if any overrides are present, otherwise False.
        """
        if self._override_map:
            return True
        if self._contract_overrides_by_spell_id:
            return True
        overrides = self._frame.overrides
        return bool(overrides)

    def _collect_override_targets(
            self,
            override_map: Dict[SocketRef, Any],
    ) -> Dict[str, List[SocketRef]]:
        """
        Purpose:
            Group override targets by spell id for validation.
        Contract:
            - Keys are spell version ids.
            - Values are the SocketRef entries targeted by overrides.
        Args:
            override_map: SocketRef -> override value mapping.
        Returns:
            Dict[str, List[SocketRef]]: Override sockets grouped by spell id.
        """
        targets: Dict[str, List[SocketRef]] = defaultdict(list)
        for socket_ref in (override_map or {}):
            targets[socket_ref.node_id].append(socket_ref)
        return dict(targets)

    def _has_overrides_for_spell(self, spell_id: str) -> bool:
        """
        Purpose:
            Determine whether any overrides target the given spell.
        Contract:
            - Socket overrides are resolved by spell id.
            - Contract overrides are resolved by spell id.
            - Root-level overrides apply to the root spell id only.
        Args:
            spell_id: Spell version id to check.
        Returns:
            bool: True if overrides target the spell id.
        """
        if self._override_targets_by_spell_id.get(spell_id):
            return True
        if self._contract_overrides_by_spell_id.get(spell_id):
            return True
        root_id = self._root_spell.spell_index.current
        if spell_id != root_id:
            return False
        overrides = self._frame.overrides
        return bool(overrides)

    def _validate_shared_override_targets(
            self,
            shared_spell_ids: Iterable[str],
    ) -> None:
        """
        Purpose:
            Reject ambiguous overrides for shared spell instances.
        Contract:
            - Shared spell instances may receive at most one override per parameter.
            - Shared spell instances may receive at most one contract override payload.
            - Multiple overrides for the same parameter raise MeldExecutionError
              even if the values are identical.
        Args:
            shared_spell_ids: Spell ids that resolve to shared instances.
        Returns:
            None.
        Raises:
            MeldExecutionError: If multiple overrides target the same parameter
                on a shared spell.
        """
        for spell_id in shared_spell_ids:
            socket_refs = self._override_targets_by_spell_id.get(spell_id, [])
            if not socket_refs:
                socket_refs = []

            by_param: Dict[str, List[SocketRef]] = defaultdict(list)
            for socket_ref in socket_refs:
                by_param[socket_ref.param_name].append(socket_ref)

            for param_name, refs in by_param.items():
                if len(refs) <= 1:
                    continue
                spell = self._spell_lookup.get(spell_id)
                spell_name = spell.spell_name if spell is not None else spell_id
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_name,
                    node_id=spell_id,
                    param_name=param_name,
                    message=(
                        f"Multiple overrides target parameter {param_name!r} on shared "
                        f"spell {spell_name!r}. Shared instances accept at most one "
                        "override per parameter."
                    ),
                )

            contract_overrides = self._contract_overrides_by_spell_id.get(spell_id, [])
            if len(contract_overrides) > 1:
                spell = self._spell_lookup.get(spell_id)
                spell_name = spell.spell_name if spell is not None else spell_id
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_name,
                    node_id=spell_id,
                    message=(
                        f"Multiple SpellContract overrides target shared spell "
                        f"{spell_name!r}. Shared instances accept at most one "
                        "SpellContract override payload."
                    ),
                )

    @staticmethod
    def _is_shared_existence(existence: Existence) -> bool:
        """
        Purpose:
            Determine whether an existence policy yields a shared instance.
        Contract:
            - Existence.many is treated as non-shared (per-path instances).
            - All other existences are treated as shared for override validation.
        Args:
            existence: Existence policy for the spell.
        Returns:
            bool: True when the existence is shared; False otherwise.
        """
        return existence is not Existence.many

    def _instance_key_for_root(self) -> _InstanceKey:
        """
        Purpose:
            Build the instance key for the root spell in root-only execution.
        Contract:
            - Shared existences use a None path.
            - Existence.many uses the empty path as the instance key.
        Returns:
            _InstanceKey: Instance key for the root spell.
        """
        root_id = self._root_spell.spell_index.current
        if self._is_shared_existence(self._root_spell.existence):
            return root_id, None
        return root_id, ()

    def _select_occurrence_plan(
            self,
            *,
            root_spell_id: str,
    ) -> Optional[Tuple[
            Dict[_OccurrenceKey, Dict[str, List[_OccurrenceKey]]],
            List[str],
            Dict[str, List[_InstanceKey]],
            Dict[str, _OccurrenceKey],
            _InstanceKey,
            Set[str],
    ]]:
        """
        Purpose:
            Determine whether a Phase 8 OccurrencePlan can drive this run.
        Contract:
            - Returns None if no usable plan is available.
            - Raises MeldExecutionError when a required SpellContract cannot
              be resolved (mirrors runtime planning behavior).
            - Returns plan data only when the plan matches the current root
              spell id and contract overrides align with plan dependencies.
            - Uses plan-provided contract override mappings when complete.
        Args:
            root_spell_id: Current root spell id for this execution.
        Returns:
            Optional[Tuple[...]]: Tuple containing occurrence graph, execution
                order, instance keys, canonical occurrences, root key, and
                shared spell ids when the plan is usable; otherwise None.
        """
        plan = self._occurrence_plan
        if plan is None:
            return None

        try:
            if plan.root_spell_id != root_spell_id:
                return None
            occurrence_graph = plan.occurrence_graph
            execution_order = plan.execution_order
            instance_keys_by_spell_id = plan.instance_keys_by_spell_id
            canonical_occurrences_by_spell_id = plan.canonical_occurrences_by_spell_id
            root_instance_key = plan.root_instance_key
            shared_spell_ids = plan.shared_spell_ids
            contract_overrides_by_occurrence = plan.contract_overrides_by_occurrence
            contract_overrides_by_spell_id = plan.contract_overrides_by_spell_id
            contract_dependencies_complete = plan.contract_dependencies_complete
        except Exception:
            return None

        if not contract_dependencies_complete:
            return None

        self._contract_overrides_by_occurrence = contract_overrides_by_occurrence
        self._contract_overrides_by_spell_id = contract_overrides_by_spell_id

        return (
            occurrence_graph,
            execution_order,
            instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id,
            root_instance_key,
            shared_spell_ids,
        )

    def _select_injection_plan(
            self,
            *,
            root_spell_id: str,
    ) -> Optional[Dict[_InstanceKey, InjectionSpec]]:
        """
        Purpose:
            Determine whether a Phase 9 InjectionPlan can drive this run.
        Contract:
            - Returns None if no usable plan is available.
            - Returns the instance injection mapping when the plan matches
              the current root spell id.
        Args:
            root_spell_id: Current root spell id for this execution.
        Returns:
            Optional[Dict[_InstanceKey, InjectionSpec]]: Mapping of instance keys
                to injection specs when the plan is usable; otherwise None.
        """
        plan = self._injection_plan
        if plan is None:
            return None
        try:
            if plan.root_spell_id != root_spell_id:
                return None
            instance_injections = plan.instance_injections
        except Exception:
            return None
        return instance_injections

    def _build_occurrence_graph(
            self,
            *,
            dag: Any,
            root_spell_id: str,
    ) -> Dict[_OccurrenceKey, Dict[str, List[_OccurrenceKey]]]:
        """
        Purpose:
            Build a path-aware occurrence graph rooted at the entrypoint spell.
        Contract:
            - Returns a mapping of occurrence -> param_name -> child occurrences.
            - Uses local topology when available; falls back to DAG metadata.
            - Includes the root occurrence even if it has no dependencies.
        Args:
            dag: DirectedAcyclicWorkGraph from the blueprint.
            root_spell_id: Version id for the root spell.
        Returns:
            Dict[_OccurrenceKey, Dict[str, List[_OccurrenceKey]]]: Occurrence graph.
        """
        root_occurrence: _OccurrenceKey = (root_spell_id, ())
        occurrence_graph: Dict[_OccurrenceKey, Dict[str, List[_OccurrenceKey]]] = {}
        queue: deque[_OccurrenceKey] = deque([root_occurrence])
        seen: set[_OccurrenceKey] = set()

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
            occurrence_graph: Dict[_OccurrenceKey, Dict[str, List[_OccurrenceKey]]],
            ordered_node_ids: Sequence[str],
            dag: Any,
    ) -> None:
        """
        Purpose:
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

            queue: deque[_OccurrenceKey] = deque([(node_id, ())])
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

    def _build_execution_order(
            self,
            *,
            occurrence_graph: Dict[_OccurrenceKey, Dict[str, List[_OccurrenceKey]]],
            fallback_order: Sequence[str],
    ) -> List[str]:
        """
        Purpose:
            Build a dependency-safe execution order for spell ids.
        Side Effects:
            None. This method is a pure ordering helper.
        Args:
            occurrence_graph: Path-aware occurrence graph.
            fallback_order: Blueprint order used as a stable tie-breaker.
        Returns:
            List[str]: Spell ids in execution order.
        Raises:
            None.
        """
        if not occurrence_graph:
            return list(fallback_order) if fallback_order else []

        edges: Dict[str, set[str]] = defaultdict(set)
        indegree: Dict[str, int] = defaultdict(int)
        nodes: set[str] = set()

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

        def _sort_key(node_id: str) -> tuple[int, str]:
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
        seen: set[str] = set()
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
            occurrence: _OccurrenceKey,
            dag: Any,
    ) -> Dict[str, List[_OccurrenceKey]]:
        """
        Purpose:
            Collect dependency occurrences for a single spell occurrence.
        Side Effects:
            - May record SpellContract override payloads for dependency occurrences.
        Args:
            occurrence: The (spell_id, path) occurrence being expanded.
            dag: DirectedAcyclicWorkGraph for fallback dependency discovery.
        Returns:
            Dict[str, List[_OccurrenceKey]]: Parameter-to-occurrence mapping.
        Raises:
            MeldExecutionError: If SpellContract resolution is ambiguous or missing.
        """
        spell_id, path = occurrence
        dependencies: Dict[str, List[_OccurrenceKey]] = {}

        topology = None
        if self._system_states is not None:
            try:
                topology = self._system_states.get_local_topology_by_id(spell_id)
            except Exception:
                topology = None

        if topology is not None:
            for socket in topology.sockets:
                if not socket.target_spell_ids:
                    continue
                for target_id in socket.target_spell_ids:
                    child_occurrence = (target_id, path + (socket.param_name,))
                    dependencies.setdefault(socket.param_name, []).append(child_occurrence)

        node = dag.get_node(spell_id) if dag is not None else None
        if node is not None:
            mutated_params: set[str] = set()
            sorted_parents = sorted(node.dependencies, key=lambda parent: parent.id)
            for parent_node in sorted_parents:
                param_name = node.incoming_params.get(parent_node)
                if not param_name:
                    continue
                socket_kind = None
                if dag is not None:
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

        self._apply_spell_contract_dependencies(
            dependencies=dependencies,
            occurrence=occurrence,
        )

        self._apply_mutation_overrides_to_dependencies(
            dependencies=dependencies,
            occurrence=occurrence,
        )

        return dependencies

    def _apply_spell_contract_dependencies(
            self,
            *,
            dependencies: Dict[str, List[_OccurrenceKey]],
            occurrence: _OccurrenceKey,
    ) -> None:
        """
        Purpose:
            Add dependency occurrences for SpellContract sockets.
        Contract:
            - Only parameters with SpellContract defaults are treated as contract
              sockets.
            - Contract sockets are resolved without touching cleaned Phase 1
              requirements artifacts.
        Side Effects:
            - Mutates the dependencies mapping in-place.
            - Records SpellContract override payloads when provided.
        Args:
            dependencies: Mapping to update with contract dependencies.
            occurrence: The (spell_id, path) occurrence being expanded.
        Returns:
            None.
        Raises:
            MeldExecutionError: If a SpellContract is missing or ambiguous.
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
            )
            child_occurrence = (target_spell_id, path + (param_name,))
            existing = dependencies.get(param_name)
            if existing is None:
                dependencies[param_name] = [child_occurrence]
            elif child_occurrence not in existing:
                existing.append(child_occurrence)

            self._record_contract_override(
                occurrence=child_occurrence,
                contract=contract,
                consumer_spell=spell,
                param_name=param_name,
            )

    def _iter_spell_contract_defaults(
            self,
            spell: ISpell,
    ) -> Iterable[Tuple[str, SpellContract]]:
        """
        Purpose:
            Yield SpellContract defaults discovered in the spell's call signature.
        Contract:
            - Only parameters with SpellContract defaults are returned.
            - Ignores "self"/"cls" and var-arg parameters.
            - Returns an empty iterable when the signature cannot be resolved.
        Side Effects:
            None. This method performs introspection only.
        Args:
            spell: Spell whose constructor or callable signature is inspected.
        Returns:
            Iterable[Tuple[str, SpellContract]]: Parameter names paired with
                SpellContract defaults.
        Raises:
            None. Failures to introspect return an empty iterable.
        """
        try:
            call_target = spell.spell
        except AttributeError:
            return []

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
    ) -> str:
        """
        Purpose:
            Resolve a SpellContract to a concrete provider spell id.
        Side Effects:
            None. This method performs lookup only.
        Args:
            contract: SpellContract describing the provider requirement.
            consumer_spell: The spell that declared the contract.
            param_name: Parameter name for diagnostics.
        Returns:
            str: Provider spell id for the contract.
        Raises:
            MeldExecutionError: If the contract is missing, ambiguous, or inconsistent.
        """
        try:
            consumer_spell_id = consumer_spell.spell_index.current
        except AttributeError:
            consumer_spell_id = "<unknown>"
        try:
            consumer_spell_name = consumer_spell.spell_name
        except AttributeError:
            consumer_spell_name = str(consumer_spell_id)

        contract_key = contract.canonical_key
        contracted_candidates: List[ISpell] = []

        try:
            spellbook = consumer_spell._spellbook
        except AttributeError:
            spellbook = None

        contracted_lookup = None
        if spellbook is not None:
            try:
                contracted_lookup = spellbook._lookup_contracted_spells
            except AttributeError:
                contracted_lookup = None

        if contracted_lookup:
            for conduit_id, lookup_map in contracted_lookup.items():
                spell_index = lookup_map.get(contract_key)
                if spell_index is None:
                    continue
                try:
                    contracted_maps = spellbook._contracted_spells
                except AttributeError:
                    contracted_maps = None
                if contracted_maps is None:
                    raise MeldExecutionError(
                        spell_id=consumer_spell_id,
                        spell_name=consumer_spell_name,
                        node_id=consumer_spell_id,
                        param_name=param_name,
                        message="Contracted spell map missing while resolving SpellContract.",
                    )
                contracted_map = contracted_maps.get(conduit_id)
                if contracted_map is None:
                    raise MeldExecutionError(
                        spell_id=consumer_spell_id,
                        spell_name=consumer_spell_name,
                        node_id=consumer_spell_id,
                        param_name=param_name,
                        message=(
                            f"Contracted spell map missing for conduit '{conduit_id}' while "
                            "resolving SpellContract."
                        ),
                    )
                spell_obj = contracted_map.get(spell_index)
                if spell_obj is None:
                    raise MeldExecutionError(
                        spell_id=consumer_spell_id,
                        spell_name=consumer_spell_name,
                        node_id=consumer_spell_id,
                        param_name=param_name,
                        message="Contracted spell index missing while resolving SpellContract.",
                    )
                contracted_candidates.append(spell_obj)

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

    def _normalize_contract_override_payload(
            self,
            *,
            payload: Any,
            consumer_spell_id: str,
            consumer_spell_name: str,
            param_name: str,
    ) -> Dict[str, Any]:
        """
        Purpose:
            Normalize a SpellContract override payload for runtime use.
        Side Effects:
            None. Returns a normalized payload copy.
        Args:
            payload: Raw spell_override payload from the SpellContract.
            consumer_spell_id: Spell id for diagnostics.
            consumer_spell_name: Spell name for diagnostics.
            param_name: Parameter name for diagnostics.
        Returns:
            Dict[str, Any]: Normalized override payload.
        Raises:
            MeldExecutionError: If the payload type is unsupported.
        """
        if payload is None:
            return {}
        if isinstance(payload, dict):
            normalized = dict(payload)
            if "__args__" in normalized:
                raw_args = normalized["__args__"]
                if not isinstance(raw_args, (list, tuple)):
                    raise MeldExecutionError(
                        spell_id=consumer_spell_id,
                        spell_name=consumer_spell_name,
                        node_id=consumer_spell_id,
                        param_name=param_name,
                        message="SpellContract __args__ override must be a list or tuple.",
                    )
            return normalized
        if isinstance(payload, (list, tuple)):
            return {"__args__": list(payload)}
        raise MeldExecutionError(
            spell_id=consumer_spell_id,
            spell_name=consumer_spell_name,
            node_id=consumer_spell_id,
            param_name=param_name,
            message=(
                "SpellContract spell_override must be a dict, list, or tuple."
            ),
        )

    def _record_contract_override(
            self,
            *,
            occurrence: _OccurrenceKey,
            contract: SpellContract,
            consumer_spell: ISpell,
            param_name: str,
    ) -> None:
        """
        Purpose:
            Record SpellContract override payloads for later application.
        Side Effects:
            - Updates contract override maps for occurrences and spell ids.
        Args:
            occurrence: Provider occurrence receiving the override.
            contract: SpellContract providing the override payload.
            consumer_spell: Spell that declared the contract.
            param_name: Parameter name for diagnostics.
        Returns:
            None.
        Raises:
            MeldExecutionError: If the override payload type is invalid.
        """
        try:
            consumer_spell_id = consumer_spell.spell_index.current
        except AttributeError:
            consumer_spell_id = "<unknown>"
        try:
            consumer_spell_name = consumer_spell.spell_name
        except AttributeError:
            consumer_spell_name = str(consumer_spell_id)

        normalized = self._normalize_contract_override_payload(
            payload=contract.spell_override,
            consumer_spell_id=consumer_spell_id,
            consumer_spell_name=consumer_spell_name,
            param_name=param_name,
        )
        if not normalized:
            return

        self._contract_overrides_by_occurrence[occurrence] = dict(normalized)
        spell_id = occurrence[0]
        self._contract_overrides_by_spell_id.setdefault(spell_id, []).append(
            (occurrence, dict(normalized))
        )

    def _get_contract_override_payload_for_instance(
            self,
            *,
            instance_key: _InstanceKey,
            canonical_occurrences_by_spell_id: Dict[str, _OccurrenceKey],
    ) -> Optional[Dict[str, Any]]:
        """
        Purpose:
            Retrieve the SpellContract override payload for an instance.
        Side Effects:
            None. This method is a read-only lookup.
        Args:
            instance_key: Instance key being constructed.
            canonical_occurrences_by_spell_id: Canonical occurrences for shared spells.
        Returns:
            Optional[Dict[str, Any]]: Override payload or None.
        Raises:
            MeldExecutionError: If a shared spell lacks a canonical occurrence.
        """
        spell_id, path = instance_key
        if path is not None:
            occurrence = (spell_id, path)
            payload = self._contract_overrides_by_occurrence.get(occurrence)
            return dict(payload) if payload is not None else None

        canonical = self._occurrence_for_instance_key(
            instance_key=instance_key,
            canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
        )
        payload = self._contract_overrides_by_occurrence.get(canonical)
        if payload is not None:
            return dict(payload)

        contract_overrides = self._contract_overrides_by_spell_id.get(spell_id, [])
        if not contract_overrides:
            return None
        return dict(contract_overrides[0][1])

    def _resolve_mutation_override_targets(
            self,
            *,
            mutation_override: Dict[str, Any],
            dag_index: DagIndex,
    ) -> List[tuple[SocketRef, str]]:
        """
        Purpose:
            Resolve mutation override keys into targeted mutation sockets.
        Contract:
            - Only MutationContract sockets are eligible targets.
            - PATH / UNIQUE / BROADCAST cardinality rules are enforced.
            - Invalid keys or targets raise MeldExecutionError.
        Args:
            mutation_override:
                Mapping of override_key -> target spell id.
            dag_index:
                DagIndex from the active root blueprint.
        Returns:
            List[tuple[SocketRef, str]]:
                List of (socket_ref, target_spell_id) pairs to apply.
        Raises:
            MeldExecutionError:
                If override keys are invalid, ambiguous, or have no matches.
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

        resolved: List[tuple[SocketRef, str]] = []

        for raw_key, target_id in mutation_override.items():
            if not isinstance(raw_key, str) or not raw_key.strip():
                raise MeldExecutionError(
                    spell_id=self._root_spell.spell_index.current,
                    spell_name=self._root_spell.spell_name,
                    message=f"Invalid mutation_override key: {raw_key!r}.",
                )
            if not isinstance(target_id, str) or not target_id.strip():
                raise MeldExecutionError(
                    spell_id=self._root_spell.spell_index.current,
                    spell_name=self._root_spell.spell_name,
                    message=(
                        f"Invalid mutation_override target for key {raw_key!r}: "
                        "expected non-empty spell_id string."
                    ),
                )

            try:
                spec = TargetSpec.parse(raw_key)
            except Exception as exc:
                raise MeldExecutionError(
                    spell_id=self._root_spell.spell_index.current,
                    spell_name=self._root_spell.spell_name,
                    message=f"Invalid mutation_override key: {raw_key!r}.",
                    inner=exc,
                ) from exc

            matches: List[SocketRef] = []
            if spec.kind is TargetSpecKind.PATH:
                if not spec.path:
                    raise MeldExecutionError(
                        spell_id=self._root_spell.spell_index.current,
                        spell_name=self._root_spell.spell_name,
                        message=f"Path override key {raw_key!r} did not contain any segments.",
                    )
                candidates = dag_index.get_by_exact_path(spec.path)
                matches = [
                    socket
                    for socket in candidates
                    if socket.socket_kind is SocketKind.MUTATION_CONTRACT
                ]
                if not matches:
                    path_str = ">".join(spec.path)
                    raise MeldExecutionError(
                        spell_id=self._root_spell.spell_index.current,
                        spell_name=self._root_spell.spell_name,
                        message=(
                            "No mutation sockets found for override path "
                            f"'{path_str}'."
                        ),
                    )

            elif spec.kind is TargetSpecKind.UNIQUE:
                if not spec.param_name:
                    raise MeldExecutionError(
                        spell_id=self._root_spell.spell_index.current,
                        spell_name=self._root_spell.spell_name,
                        message=f"Unique override key {raw_key!r} is missing a parameter name.",
                    )
                candidates = dag_index.get_by_name(spec.param_name)
                matches = [
                    socket
                    for socket in candidates
                    if socket.socket_kind is SocketKind.MUTATION_CONTRACT
                ]
                count = len(matches)
                if count == 0:
                    raise MeldExecutionError(
                        spell_id=self._root_spell.spell_index.current,
                        spell_name=self._root_spell.spell_name,
                        message=(
                            "No mutation sockets found for unique override "
                            f"'*{spec.param_name}'."
                        ),
                    )
                if count > 1:
                    raise MeldExecutionError(
                        spell_id=self._root_spell.spell_index.current,
                        spell_name=self._root_spell.spell_name,
                        message=(
                            "Unique override matched multiple mutation sockets "
                            f"for '*{spec.param_name}'."
                        ),
                    )

            elif spec.kind is TargetSpecKind.BROADCAST:
                if not spec.param_name:
                    raise MeldExecutionError(
                        spell_id=self._root_spell.spell_index.current,
                        spell_name=self._root_spell.spell_name,
                        message=f"Broadcast override key {raw_key!r} is missing a parameter name.",
                    )
                candidates = dag_index.get_by_name(spec.param_name)
                matches = [
                    socket
                    for socket in candidates
                    if socket.socket_kind is SocketKind.MUTATION_CONTRACT
                ]
                if not matches:
                    raise MeldExecutionError(
                        spell_id=self._root_spell.spell_index.current,
                        spell_name=self._root_spell.spell_name,
                        message=(
                            "No mutation sockets found for broadcast override "
                            f"'**{spec.param_name}'."
                        ),
                    )
            else:
                raise MeldExecutionError(
                    spell_id=self._root_spell.spell_index.current,
                    spell_name=self._root_spell.spell_name,
                    message=f"Unsupported TargetSpecKind for override {raw_key!r}.",
                )

            for socket_ref in matches:
                resolved.append((socket_ref, target_id))

        return resolved

    def _apply_mutation_overrides_to_dependencies(
            self,
            *,
            dependencies: Dict[str, List[_OccurrenceKey]],
            occurrence: _OccurrenceKey,
    ) -> None:
        """
        Purpose:
            Overlay mutation overrides onto dependency occurrences.
        Contract:
            - Only applies when the active spell has a mutation_override payload.
            - Matching mutation sockets are rewired to the override spell id.
            - Overrides are matched against the occurrence path for disambiguation.
            - Missing mutation_override attributes are treated as "no overrides".
        Args:
            dependencies:
                Parameter-to-occurrence mapping to update in-place.
            occurrence:
                The (spell_id, path) occurrence being expanded.
        Returns:
            None.
        Raises:
            MeldExecutionError:
                If mutation overrides are invalid or ambiguous.
        """
        if self._blueprint is None:
            return

        spell_id, path = occurrence
        spell = self._spell_lookup.get(spell_id)
        if spell is None and spell_id == self._root_spell.spell_index.current:
            spell = self._root_spell
        if spell is None:
            return

        try:
            mutation_override = spell.mutation_override
        except AttributeError:
            mutation_override = {}
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
            occurrence_graph: Dict[_OccurrenceKey, Dict[str, List[_OccurrenceKey]]],
            root_spell_id: str,
    ) -> tuple[
        Dict[str, List[_InstanceKey]],
        Dict[str, _OccurrenceKey],
        _InstanceKey,
        set[str],
    ]:
        """
        Purpose:
            Build per-spell instance keys and canonical occurrences.
        Contract:
            - Existence.many -> one instance per occurrence path.
            - Shared existences -> one instance per spell id.
            - Canonical occurrences anchor dependency paths for shared spells.
        Args:
            occurrence_graph: Path-aware occurrence graph.
            root_spell_id: Version id for the root spell.
        Returns:
            tuple:
                - Dict[str, List[_InstanceKey]]: instance keys by spell id.
                - Dict[str, _OccurrenceKey]: canonical occurrence per shared spell.
                - _InstanceKey: instance key for the root spell.
                - set[str]: spell ids treated as shared.
        Raises:
            MeldExecutionError: If a spell id is missing from the lookup table.
        """
        occurrences_by_spell_id: Dict[str, List[_OccurrenceKey]] = defaultdict(list)
        for occurrence in occurrence_graph:
            spell_id, _ = occurrence
            occurrences_by_spell_id[spell_id].append(occurrence)

        instance_keys_by_spell_id: Dict[str, List[_InstanceKey]] = {}
        canonical_occurrences_by_spell_id: Dict[str, _OccurrenceKey] = {}
        shared_spell_ids: set[str] = set()

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
                            f"Dependency spell with id '{spell_id}' not found in spellbook for meld."
                        ),
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

        root_occurrence: _OccurrenceKey = (root_spell_id, ())
        root_instance_key = self._instance_key_for_occurrence(root_occurrence)

        return (
            instance_keys_by_spell_id,
            canonical_occurrences_by_spell_id,
            root_instance_key,
            shared_spell_ids,
        )

    @staticmethod
    def _select_canonical_occurrence(
            occurrences: Sequence[_OccurrenceKey],
    ) -> _OccurrenceKey:
        """
        Purpose:
            Pick a stable occurrence for shared instance dependency paths.
        Contract:
            - The canonical occurrence is the one with the lexicographically
              smallest path.
        Args:
            occurrences: Occurrences for the same spell id.
        Returns:
            _OccurrenceKey: The canonical occurrence.
        """
        return min(occurrences, key=lambda entry: entry[1])

    def _instance_key_for_occurrence(
            self,
            occurrence: _OccurrenceKey,
    ) -> _InstanceKey:
        """
        Purpose:
            Map an occurrence to its instance key based on existence policy.
        Contract:
            - Existence.many preserves the occurrence path.
            - Shared existences collapse to a None path.
        Args:
            occurrence: The (spell_id, path) occurrence to map.
        Returns:
            _InstanceKey: Instance key for the occurrence.
        Raises:
            MeldExecutionError: If the spell id is not registered in the lookup.
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
                        f"Dependency spell with id '{spell_id}' not found in spellbook for meld."
                    ),
                )
        if self._is_shared_existence(spell.existence):
            return spell_id, None
        return spell_id, path

    def _occurrence_for_instance_key(
            self,
            *,
            instance_key: _InstanceKey,
            canonical_occurrences_by_spell_id: Dict[str, _OccurrenceKey],
    ) -> _OccurrenceKey:
        """
        Purpose:
            Resolve the occurrence used to build kwargs for an instance.
        Contract:
            - Shared instances use their canonical occurrence path.
            - Per-path instances use their own occurrence path.
        Args:
            instance_key: The instance key being resolved.
            canonical_occurrences_by_spell_id: Canonical occurrence mapping.
        Returns:
            _OccurrenceKey: The occurrence used for dependency lookup.
        Raises:
            MeldExecutionError: If a shared spell lacks a canonical occurrence.
        """
        spell_id, path = instance_key
        if path is not None:
            return spell_id, path
        canonical = canonical_occurrences_by_spell_id.get(spell_id)
        if canonical is None:
            raise MeldExecutionError(
                spell_id=spell_id,
                spell_name=spell_id,
                message=f"Canonical occurrence missing for shared spell '{spell_id}'.",
            )
        return canonical

    def _build_instance_override_map(
            self,
            *,
            spell_id: str,
            occurrence_path: tuple[str, ...],
            shared: bool,
    ) -> Dict[str, Any]:
        """
        Purpose:
            Select overrides applicable to a specific spell instance.
        Contract:
            - Shared instances accept path-agnostic overrides for their params.
            - Per-path instances accept overrides whose param_path matches the
              occurrence path.
        Args:
            spell_id: Spell id being constructed.
            occurrence_path: Path to the occurrence from the root.
            shared: Whether the instance is shared.
        Returns:
            Dict[str, Any]: Parameter name to override value mapping.
        """
        overrides: Dict[str, Any] = {}
        for socket_ref, value in (self._override_map or {}).items():
            if socket_ref.node_id != spell_id:
                continue
            if shared:
                overrides[socket_ref.param_name] = value
                continue
            if not socket_ref.param_path:
                continue
            if tuple(socket_ref.param_path[:-1]) == occurrence_path:
                overrides[socket_ref.param_name] = value
        return overrides

    def _build_kwargs_for_instance(
            self,
            *,
            instance_key: _InstanceKey,
            occurrence_graph: Dict[_OccurrenceKey, Dict[str, List[_OccurrenceKey]]],
            canonical_occurrences_by_spell_id: Dict[str, _OccurrenceKey],
            contract_override: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Purpose:
            Build keyword args for a specific spell instance.
        Side Effects:
            None. Returns a new kwargs mapping.
        Args:
            instance_key: Instance key being constructed.
            occurrence_graph: Dependency graph keyed by occurrence.
            canonical_occurrences_by_spell_id: Canonical occurrences for shared spells.
            contract_override: Optional SpellContract override payload for this instance.
        Returns:
            Dict[str, Any]: Keyword arguments for construction.
        Raises:
            MeldExecutionError: If a dependency instance is missing.
        """
        occurrence = self._occurrence_for_instance_key(
            instance_key=instance_key,
            canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
        )
        spell_id, path = occurrence
        shared = instance_key[1] is None

        override_values = self._build_instance_override_map(
            spell_id=spell_id,
            occurrence_path=path,
            shared=shared,
        )

        contract_payload = dict(contract_override) if contract_override else {}
        positional_override = None
        if "__args__" in contract_payload:
            positional_override = contract_payload.pop("__args__")

        kwargs: Dict[str, Any] = {}
        dependencies = occurrence_graph.get(occurrence, {})
        for param_name, dependency_occurrences in dependencies.items():
            if param_name in override_values:
                kwargs[param_name] = override_values[param_name]
                continue
            values: List[Any] = []
            for dependency_occurrence in dependency_occurrences:
                dependency_key = self._instance_key_for_occurrence(dependency_occurrence)
                if dependency_key not in self._instance_results:
                    raise MeldExecutionError(
                        spell_id=spell_id,
                        spell_name=spell_id,
                        node_id=spell_id,
                        param_name=param_name,
                        message=(
                            f"Dependency '{dependency_occurrence[0]}' missing while "
                            f"building args for '{spell_id}'."
                        ),
                    )
                values.append(self._instance_results[dependency_key])
            if not values:
                continue
            if len(values) == 1:
                kwargs[param_name] = values[0]
            else:
                kwargs[param_name] = values

        if positional_override is not None:
            kwargs["__args__"] = positional_override

        for param_name, value in contract_payload.items():
            if param_name in override_values:
                continue
            kwargs[param_name] = value

        for param_name, value in override_values.items():
            if param_name not in kwargs:
                kwargs[param_name] = value

        return kwargs

    def _build_kwargs_for_instance_from_plan(
            self,
            *,
            instance_key: _InstanceKey,
            injection_spec: InjectionSpec,
            canonical_occurrences_by_spell_id: Dict[str, _OccurrenceKey],
            contract_override: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Purpose:
            Build keyword args for a specific spell instance using a Phase 9
            InjectionPlan.
        Side Effects:
            None. Returns a new kwargs mapping.
        Args:
            instance_key: Instance key being constructed.
            injection_spec: InjectionSpec describing dependency wiring.
            canonical_occurrences_by_spell_id: Canonical occurrences for shared spells.
            contract_override: Optional SpellContract override payload for this instance.
        Returns:
            Dict[str, Any]: Keyword arguments for construction.
        Raises:
            MeldExecutionError: If a dependency instance is missing.
        """
        occurrence = self._occurrence_for_instance_key(
            instance_key=instance_key,
            canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
        )
        spell_id, path = occurrence
        shared = instance_key[1] is None

        override_values = self._build_instance_override_map(
            spell_id=spell_id,
            occurrence_path=path,
            shared=shared,
        )

        contract_payload = dict(contract_override) if contract_override else {}
        positional_override = None
        if "__args__" in contract_payload:
            positional_override = contract_payload.pop("__args__")

        kwargs: Dict[str, Any] = {}
        for param_name, param_source in injection_spec.param_sources.items():
            if param_source.kind != "dependency":
                continue
            dependency_keys = param_source.dependency_keys or []
            if param_name in override_values:
                kwargs[param_name] = override_values[param_name]
                continue
            values: List[Any] = []
            for dependency_key in dependency_keys:
                if dependency_key not in self._instance_results:
                    raise MeldExecutionError(
                        spell_id=spell_id,
                        spell_name=spell_id,
                        node_id=spell_id,
                        param_name=param_name,
                        message=(
                            f"Dependency '{dependency_key[0]}' missing while "
                            f"building args for '{spell_id}'."
                        ),
                    )
                values.append(self._instance_results[dependency_key])
            if not values:
                continue
            if len(values) == 1:
                kwargs[param_name] = values[0]
            else:
                kwargs[param_name] = values

        if positional_override is not None:
            kwargs["__args__"] = positional_override

        for param_name, value in contract_payload.items():
            if param_name in override_values:
                continue
            kwargs[param_name] = value

        for param_name, value in override_values.items():
            if param_name not in kwargs:
                kwargs[param_name] = value

        return kwargs

    def _store_instance_result(
            self,
            instance_key: _InstanceKey,
            instance: Any,
    ) -> None:
        """
        Purpose:
            Store a resolved instance for the given instance key.
        Contract:
            - Instance results are stored in a path-aware map.
            - The first instance for a spell id is also stored in ResolutionFrame.
        Args:
            instance_key: Instance key for the constructed spell.
            instance: Constructed instance.
        Returns:
            None.
        """
        self._instance_results[instance_key] = instance
        spell_id = instance_key[0]
        if not self._frame.has_result(spell_id):
            self._frame.set_result(spell_id, instance)

    def _get_instance_result(self, instance_key: _InstanceKey) -> Any:
        """
        Purpose:
            Retrieve a resolved instance by instance key.
        Contract:
            - Returns the instance when present.
        Args:
            instance_key: Instance key to retrieve.
        Returns:
            Any: The resolved instance.
        Raises:
            MeldExecutionError: If the instance is missing from the results map.
        """
        if instance_key not in self._instance_results:
            spell_id, _ = instance_key
            raise MeldExecutionError(
                spell_id=spell_id,
                spell_name=spell_id,
                message=f"Instance result missing for spell '{spell_id}'.",
            )
        return self._instance_results[instance_key]

    def _raise_override_on_existing(self, spell: ISpell) -> None:
        """
        Purpose:
            Raise when overrides target an already-instantiated shared spell.
        Contract:
            - Shared spell instances cannot accept overrides after creation.
            - Root-level overrides are rejected when the root already exists.
        Args:
            spell: The spell whose instance is being reused.
        Returns:
            None.
        Raises:
            MeldExecutionError: If overrides target an existing shared instance.
        """
        if not self._is_shared_existence(spell.existence):
            return

        spell_id = spell.spell_index.current
        root_id = self._root_spell.spell_index.current
        if spell_id == root_id and self._any_overrides_present:
            raise MeldExecutionError(
                spell_id=spell_id,
                spell_name=spell.spell_name,
                node_id=spell_id,
                message=(
                    "Overrides were supplied for a root spell that already exists. "
                    "Shared instances cannot be overridden after creation."
                ),
            )

        if self._has_overrides_for_spell(spell_id):
            raise MeldExecutionError(
                spell_id=spell_id,
                spell_name=spell.spell_name,
                node_id=spell_id,
                message=(
                    "Overrides were supplied for a shared spell that already exists. "
                    "Shared instances cannot be overridden after creation."
                ),
            )

    # ------------------------------------------------------------------ #
    # Construction helpers
    # ------------------------------------------------------------------ #

    def _construct_root_only(self) -> Any:
        """
        Construct the root spell instance using only override metadata.

        This path is used when we either have no DAG yet or the DAG is
        effectively a single node with no dependencies.

        Resolution logic (MVP)
        ----------------------

        * For existing-creation spells:
            - Return `spell.user_created_object` if available.
        * For class/method/lambda spells:
            - Use overrides from `ResolutionFrame.overrides`:
                - `__args__` (list/tuple) → positional args
                - other keys → keyword args
            - Invoke `spell.spell(*args, **kwargs)`.
        * For anything else:
            - Return `spell.spell` as-is (value spell).

        Any exception raised by the underlying callable is wrapped in a
        `MeldExecutionError` with the root spell's identity attached.

        Returns:
            The constructed instance for the root spell.

        Raises:
            MeldExecutionError:
                * If an existing-creation spell has no attached
                  `user_created_object`.
                * If invocation of the underlying callable fails.
        """
        spell = self._root_spell
        target = spell.spell

        # Only factory-like spells are expected here.
        if not (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell):
            # Treat everything else as a value spell.
            return target

        overrides = self._frame.overrides
        if overrides is None:
            overrides = {}

        # Positional overrides (if provided).
        raw_args = overrides.get("__args__")
        if isinstance(raw_args, Sequence) and not isinstance(raw_args, (str, bytes)):
            args = list(raw_args)
        else:
            args = []

        # Keyword overrides (all keys except "__args__").
        kwargs = {
            key: value
            for key, value in overrides.items()
            if key != "__args__"
        }

        try:
            instance = target(*args, **kwargs)
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=f"Error invoking spell target {spell.spell_name!r}.",
                inner=exc,
            ) from exc

        return instance

    # ------------------------------------------------------------------ #
    # DAG helpers                                                        #
    # ------------------------------------------------------------------ #
    def _build_kwargs_for_node(
            self,
            *,
            node_id: str,
            dag,
            override_map: Dict[SocketRef, Any],
    ) -> Dict[str, Any]:
        """
        Build keyword args for a node by combining overrides and dependency instances.
        """
        kwargs: Dict[str, Any] = {}
        node = dag.get_node(node_id)
        if node is None:
            return kwargs

        # Map overrides targeting this node_id
        for socket_ref, value in (override_map or {}).items():
            if socket_ref.node_id == node_id:
                kwargs[socket_ref.param_name] = value

        # Resolve dependencies from DAG edges + topology
        if not node.dependencies:
            return kwargs

        topo = None
        if self._system_states is not None:
            try:
                topo = self._system_states.get_local_topology_by_id(node_id)
            except Exception:
                topo = None

        incoming_map: Dict[str, list[str]] = {}
        if topo is not None:
            for socket in topo.sockets:
                for target_id in socket.target_spell_ids:
                    incoming_map.setdefault(socket.param_name, []).append(target_id)

        # Merge incoming_params if topology is missing.
        for parent_node in node.dependencies:
            parent_id = parent_node.id
            param_name = node.incoming_params.get(parent_node)
            if param_name:
                incoming_map.setdefault(param_name, []).append(parent_id)

        for param_name, parent_ids in incoming_map.items():
            if param_name in kwargs:
                # Already overridden; skip DI value.
                continue
            values = []
            for parent_id in sorted(set(parent_ids)):
                if not self._frame.has_result(parent_id):
                    raise MeldExecutionError(
                        spell_id=node_id,
                        spell_name=node_id,
                        message=(
                            f"Dependency '{parent_id}' missing while building args for '{node_id}'."
                        ),
                    )
                values.append(self._frame.get_result(parent_id))
            if not values:
                continue
            if len(values) == 1:
                kwargs[param_name] = values[0]
            else:
                # Multiple providers -> inject list. Downstream type checks can enforce collections.
                kwargs[param_name] = values

        return kwargs

    def _construct_spell(self, spell: ISpell, kwargs: Dict[str, Any]) -> Any:
        """
        Purpose:
            Construct a spell instance using the provided arguments.
        Side Effects:
            - Invokes the spell callable to create an instance.
        Args:
            spell: Spell to construct.
            kwargs: Keyword argument payload (may include "__args__" for positional args).
        Returns:
            Any: Constructed spell instance.
        Raises:
            MeldExecutionError: If construction fails or required data is missing.
        """
        if spell.is_existing_creation:
            if spell.user_created_object is None:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message="EXISTING_CREATION spell has no backing object.",
                )
            return spell.user_created_object

        if not (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell):
            return spell.spell

        try:
            call_kwargs = dict(kwargs)
            raw_args = call_kwargs.pop("__args__", [])
            if isinstance(raw_args, Sequence) and not isinstance(raw_args, (str, bytes)):
                args = list(raw_args)
            else:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message="__args__ override must be a list or tuple.",
                )
            return spell.spell(*args, **call_kwargs)
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=f"Error invoking spell '{spell.spell_name}'.",
                inner=exc,
            ) from exc

    def _store_result(self, node_id: str, value: Any) -> None:
        self._frame.set_result(node_id, value)

    def _should_use_spell_lock(self, spell: ISpell, creations: Any) -> bool:
        """
        Internal

        Decide whether a shared existence should acquire the spell lock.

        Contract:
            - Shared existences normally take the spell lock.
            - If the caller creations lock is already held and the shared
              existence resolves against the same creations container, the
              spell lock is skipped to avoid lock inversion.
        """
        if spell.existence not in (
                Existence.unique,
                Existence.unique_per_conduit_cluster,
                Existence.unique_per_conduit_lineage,
        ):
            return False

        if (
                self._context.caller_creations_lock_held
                and creations is self._context.caller_creations
        ):
            return False

        return True

    def _resolve_spell_instance(
            self,
            spell: ISpell,
            *,
            construct_fn: Callable[[], Any],
    ) -> tuple[Any, bool]:
        """
        Internal

        Resolve a spell instance while enforcing per-existence locking rules.

        Contract:
            - Per-conduit existences hold the caller creations lock across
              check -> construct -> register.
            - Shared existences hold the spell lock across the same flow and
              use the creations lock only for map access.
            - When the caller creations lock is already held for the same
              container, shared existences skip the spell lock to avoid
              lock inversion.
            - Existence.many always constructs and registers without reuse.
            - Shared existences raise if overrides target an already-instantiated
              instance.

        Args:
            spell: The spell being resolved.
            construct_fn: Callable that performs construction when needed.

        Returns:
            tuple[Any, bool]:
                (instance, created) where created is True only when this call
                constructs and registers a new instance.
        """
        creations = self._select_creations_for_spell(spell)
        existence: Existence = spell.existence
        instance: Any = None
        created = False

        if existence is Existence.many:
            instance = construct_fn()
            if creations is not None:
                with creations._lock:
                    self._register_spell(spell, instance, creations)
            return instance, True

        if existence in (
                Existence.unique_per_conduit,
                Existence.unique_per_spell_space,
        ):
            if creations is None:
                instance = construct_fn()
                return instance, True
            with creations._lock:
                instance = self._get_existing_creation(spell, creations)
                if instance is None:
                    instance = construct_fn()
                    self._register_spell(spell, instance, creations)
                    created = True
                else:
                    self._raise_override_on_existing(spell)
            return instance, created

        use_spell_lock = self._should_use_spell_lock(spell, creations)
        if use_spell_lock:
            with spell._lock:
                if creations is not None:
                    with creations._lock:
                        instance = self._get_existing_creation(spell, creations)
                else:
                    instance = self._get_existing_creation(spell, None)

                if instance is None:
                    instance = construct_fn()
                    if creations is not None:
                        with creations._lock:
                            self._register_spell(spell, instance, creations)
                    created = True
                else:
                    self._raise_override_on_existing(spell)
            return instance, created

        if creations is None:
            instance = construct_fn()
            return instance, True

        with creations._lock:
            instance = self._get_existing_creation(spell, creations)
            if instance is None:
                instance = construct_fn()
                self._register_spell(spell, instance, creations)
                created = True
            else:
                self._raise_override_on_existing(spell)

        return instance, created

    def _select_creations_for_spell(self, spell: ISpell) -> Any:
        """
        Internal

        Select the appropriate creations container for reuse/registration.

        Contract:
            - Per-conduit lifetimes use the caller creations container.
            - Shared lifetimes use the spell's owner creations when available,
              otherwise fall back to the context owner creations container.
            - If the preferred container is None, fall back to the other.

        Args:
            spell: The spell whose Existence determines selection.

        Returns:
            The selected creations container, or None if neither is available.
        """
        existence: Existence = spell.existence
        caller_creations = self._context.caller_creations
        owner_creations = spell._owner_creations
        if owner_creations is None:
            owner_creations = self._context.owner_creations

        if existence in (
                Existence.unique_per_conduit,
                Existence.many,
                Existence.unique_per_spell_space,
        ):
            if caller_creations is not None:
                return caller_creations
            return owner_creations

        if owner_creations is not None:
            return owner_creations
        return caller_creations

    def _get_existing_creation(
            self,
            spell: ISpell,
            creations: Any | None = None,
    ) -> Optional[Any]:
        """
        Attempt reuse from creations manager based on Existence.

        Selection:
            - Uses caller creations for per-conduit lifetimes.
            - Uses owner creations for shared lifetimes.
        """
        if creations is None:
            creations = self._select_creations_for_spell(spell)
        existence: Existence = spell.existence
        spell_id: str = spell.spell_id

        # many never reuses
        if existence is Existence.many:
            return None
        if creations is None:
            return None

        if isinstance(creations, Creations):
            if existence is Existence.unique:
                found = creations._unique.get(spell_id)
                return found.value if found is not None else None
            if existence is Existence.unique_per_conduit:
                found = creations._unique_per_scope.get(spell_id)
                return found.value if found is not None else None
            if existence is Existence.unique_per_conduit_cluster:
                found = creations._unique_per_cluster.get(spell_id)
                return found.value if found is not None else None
            if existence is Existence.unique_per_conduit_lineage:
                found = creations._unique_per_lineage.get(spell_id)
                return found.value if found is not None else None
            if existence is Existence.unique_per_spell_space:
                spellspace = creations._conduit.get_active_spellspace()
                if spellspace is None:
                    raise SpellSpaceScopeError(
                        "Existence.unique_per_spell_space requires an active SpellSpace. "
                        "Use 'with conduit.enter_spellspace()' when melding."
                    )
                if spellspace.owner_conduit is not creations._conduit:
                    raise SpellSpaceScopeError(
                        "Active SpellSpace belongs to a different conduit."
                    )
                found = creations.get_spellspace_creation(spellspace.id, spell_id)
                return found.value if found is not None else None
            return None

        if isinstance(creations, LesserCreations):
            if existence is Existence.unique_per_conduit:
                found = creations._unique_per_scope.get(spell_id)
                return found.value if found is not None else None
            parent_creations = creations._parent_creations
            if isinstance(parent_creations, Creations):
                if existence is Existence.unique:
                    found = parent_creations._unique.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_conduit_cluster:
                    found = parent_creations._unique_per_cluster.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_conduit_lineage:
                    found = parent_creations._unique_per_lineage.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_spell_space:
                    spellspace = creations._conduit.get_active_spellspace()
                    if spellspace is None:
                        raise SpellSpaceScopeError(
                            "Existence.unique_per_spell_space requires an active SpellSpace. "
                            "Use 'with conduit.enter_spellspace()' when melding."
                        )
                    if spellspace.owner_conduit is not creations._conduit:
                        raise SpellSpaceScopeError(
                            "Active SpellSpace belongs to a different conduit."
                        )
                    found = creations.get_spellspace_creation(spellspace.id, spell_id)
                    return found.value if found is not None else None
            return None

        return None

    def _register_spell(
            self,
            spell: ISpell,
            instance: Any,
            creations: Any | None = None,
    ) -> None:
        """
        Register a constructed instance into the appropriate creations container.

        Contract:
            - Per-conduit lifetimes register against the caller creations container.
            - Shared lifetimes register against the owner creations container.
            - Unknown creations containers are treated as no-ops.
            - Existence.many registration is skipped when the spell declares
              no disposal methods.

        Args:
            spell: The spell that produced the instance.
            instance: The newly constructed instance to register.
            creations: Optional creations container override. If None, selection
                follows `_select_creations_for_spell`.

        Returns:
            None.
        """
        if creations is None:
            creations = self._select_creations_for_spell(spell)
        existence: Existence = spell.existence
        spell_id: str = spell.spell_id
        has_disposal_methods: bool = spell.has_disposal_methods
        disposal_methods: list[str] = spell.disposal_method_names

        if creations is None:
            return None

        if isinstance(creations, Creations):
            if existence is Existence.unique:
                creations.add_unique(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.unique_per_conduit:
                creations.add_unique_per_scope(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.many:
                if not has_disposal_methods:
                    return
                creations.add_many(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.unique_per_conduit_cluster:
                creations.add_unique_per_cluster(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.unique_per_conduit_lineage:
                creations.add_unique_per_lineage(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.unique_per_spell_space:
                spellspace = creations._conduit.get_active_spellspace()
                if spellspace is None:
                    raise SpellSpaceScopeError(
                        "Existence.unique_per_spell_space requires an active SpellSpace. "
                        "Use 'with conduit.enter_spellspace()' when melding."
                    )
                if spellspace.owner_conduit is not creations._conduit:
                    raise SpellSpaceScopeError(
                        "Active SpellSpace belongs to a different conduit."
                    )
                creations.register_spellspace_creation(
                    spellspace.id,
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            return

        if isinstance(creations, LesserCreations):
            if existence is Existence.unique_per_conduit:
                creations.add_unique_per_scope(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            if existence is Existence.many:
                if not has_disposal_methods:
                    return
                creations.add_many(
                    spell_id,
                    instance,
                    has_disposal_methods=has_disposal_methods,
                    disposal_methods=disposal_methods,
                )
                return
            parent_creations = creations._parent_creations
            if isinstance(parent_creations, Creations):
                if existence is Existence.unique:
                    parent_creations.add_unique(
                        spell_id,
                        instance,
                        has_disposal_methods=has_disposal_methods,
                        disposal_methods=disposal_methods,
                    )
                    return
                if existence is Existence.unique_per_conduit_cluster:
                    parent_creations.add_unique_per_cluster(
                        spell_id,
                        instance,
                        has_disposal_methods=has_disposal_methods,
                        disposal_methods=disposal_methods,
                    )
                    return
                if existence is Existence.unique_per_conduit_lineage:
                    parent_creations.add_unique_per_lineage(
                        spell_id,
                        instance,
                        has_disposal_methods=has_disposal_methods,
                        disposal_methods=disposal_methods,
                    )
                    return
                if existence is Existence.unique_per_spell_space:
                    spellspace = creations._conduit.get_active_spellspace()
                    if spellspace is None:
                        raise SpellSpaceScopeError(
                            "Existence.unique_per_spell_space requires an active SpellSpace. "
                            "Use 'with conduit.enter_spellspace()' when melding."
                        )
                    if spellspace.owner_conduit is not creations._conduit:
                        raise SpellSpaceScopeError(
                            "Active SpellSpace belongs to a different conduit."
                        )
                    creations.register_spellspace_creation(
                        spellspace.id,
                        spell_id,
                        instance,
                        has_disposal_methods=has_disposal_methods,
                        disposal_methods=disposal_methods,
                    )
                    return
            return
