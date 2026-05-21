from collections import defaultdict, deque
from dataclasses import dataclass
import heapq
import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    ClassVar,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.dag.dag_index import (
        DagIndex,
        PathRegistry,
        SocketRef,
    )

from mypy_extensions import mypyc_attr

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.dag.target_spec import TargetSpec, TargetSpecKind
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import EnumHelpers
OccurrenceKey = Tuple[str, int]
InstanceKey = Tuple[str, Optional[int]]

@mypyc_attr(native_class=True)
@dataclass(frozen=True, slots=True)
class OccurrencePlanSelection:
    """
    Runtime-ready Phase 8 handoff bundle.

    Purpose:
        Package the subset of occurrence-plan data that runtime execution needs
        after Phase 8 is finished. This keeps CreationContext and later
        execution layers from reaching back into the full builder object for
        selection logic they do not own.

    Contract:
        - Carries only already-selected runtime data; it does not perform plan
          expansion, validation, or filtering on its own.
        - Preserves the path-aware occurrence graph, execution ordering,
          instance-key planning, and any resolved SpellContract override
          payloads needed by later phases.
        - Is intended to be an immutable handoff object once constructed.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
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
    Lift a Phase 8 plan into its runtime-ready handoff form.

    Contract:
        - Expected to be called only after the caller has confirmed that a
          concrete Phase 8 plan is available.
        - Does not recompute or filter occurrence data; it forwards the
          plan-owned runtime payload as-is.
        - Does not enforce contract-completeness policy; callers decide whether
          incomplete SpellContract state is acceptable for the current runtime
          path.
        - Returns a lightweight `OccurrencePlanSelection` wrapper instead of
          exposing the full plan object as the runtime contract.

    Args:
        plan:
            Phase 8 occurrence plan to expose to runtime execution.
        root_spell_id:
            Current root spell id for this execution context. The current
            implementation does not re-filter by this value, but the parameter
            remains part of the handoff contract because callers select plans in
            root-spell context.

    Returns:
        Optional[OccurrencePlanSelection]:
            Runtime-ready selection payload for the supplied plan.
    """
    if plan is None:
        return None
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

@mypyc_attr(native_class=True)
class OccurrencePlan(Cleanable):
    """
    Phase 8 occurrence-expansion artifact for one root blueprint.

    Purpose:
        Capture the path-aware runtime expansion of a rooted blueprint before
        Phase 9 injection planning and Phase 11 execution assembly run. This is
        the point where the blueprint stops being just a structural DAG and
        starts carrying occurrence-specific runtime semantics such as shared
        instance collapse, canonical occurrences, and resolved SpellContract
        payload routing.

    Contract:
        - `root_spell_id` must match the root blueprint used to build the plan.
        - The plan owns its occurrence graph, execution order, instance-key
          maps, and contract-override payload maps.
        - Contract override payloads are recorded only for resolved providers.
        - Automatic mode expects contract dependencies to be complete; dynamic
          mode may carry an intentionally incomplete plan until linking and
          later phase reruns resolve the missing providers.
        - After build, the plan is treated as immutable runtime input.

    Threading:
        - Not thread-safe. Treat as read-only data after construction.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
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
        "_path_registry",
    ]

    __deletable__: ClassVar[List[str]] = [
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
        "_path_registry",
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
            path_registry: PathRegistry,
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
                Path-aware occurrence graph keyed by (spell_id, path_id).
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
            path_registry:
                PathRegistry that interns the occurrence path ids used by this plan.

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
        if contract_overrides_by_occurrence is None:
            raise ValueError("contract_overrides_by_occurrence must not be None.")
        if contract_overrides_by_spell_id is None:
            raise ValueError("contract_overrides_by_spell_id must not be None.")
        if contract_dependencies_complete is None:
            raise ValueError("contract_dependencies_complete must not be None.")
        if path_registry is None:
            raise ValueError("path_registry must not be None.")

        self._root_spell_id: str = root_spell_id
        self._occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]] = occurrence_graph
        self._execution_order: List[str] = execution_order
        self._instance_keys_by_spell_id: Dict[str, List[InstanceKey]] = instance_keys_by_spell_id
        self._canonical_occurrences_by_spell_id: Dict[str, OccurrenceKey] = canonical_occurrences_by_spell_id
        self._root_instance_key: InstanceKey = root_instance_key
        self._shared_spell_ids: Set[str] = shared_spell_ids
        self._contract_overrides_by_occurrence: Dict[OccurrenceKey, Dict[str, Any]] = contract_overrides_by_occurrence
        self._contract_overrides_by_spell_id: Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]] = contract_overrides_by_spell_id
        self._contract_dependencies_complete: bool = contract_dependencies_complete
        self._path_registry: PathRegistry = path_registry

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

        del self._root_spell_id
        del self._occurrence_graph
        del self._execution_order
        del self._instance_keys_by_spell_id
        del self._canonical_occurrences_by_spell_id
        del self._root_instance_key
        del self._shared_spell_ids
        del self._contract_overrides_by_occurrence
        del self._contract_overrides_by_spell_id
        del self._contract_dependencies_complete
        del self._path_registry

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
            - Missing occurrences imply no override payload for that provider.
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

    @property
    def path_registry(self) -> PathRegistry:
        """
        Return the PathRegistry for occurrence path ids.

        Contract:
            - The registry is owned by the originating blueprint.
            - The plan does not clean the registry; it only holds a reference.
        """
        self.check_cleaned()
        return self._path_registry

@mypyc_attr(native_class=True)
class OccurrencePlanBuilder(object):
    """
    Internal

    Phase 8 compiler that mirrors runtime occurrence planning logic and
    produces an OccurrencePlan artifact.

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
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = [
        "_cleaned",
        "_root_spell",
        "_blueprint",
        "_spell_lookup",
        "_system_states",
        "_path_registry",
    ]
    __deletable__: ClassVar[List[str]] = [
        "_cleaned"
        "_root_spell",
        "_blueprint",
        "_spell_lookup",
        "_system_states",
        "_path_registry",
    ]

    def __init__(
            self,
            *,
            root_spell: Spell,
            blueprint: Any,
            spell_lookup: Dict[str, Spell],
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
                Mapping of spell_id to Spell for all reachable nodes.
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
        self._cleaned: bool = False
        self._root_spell: Spell = root_spell
        self._blueprint: Any = blueprint
        self._spell_lookup: Dict[str, Spell] = spell_lookup
        self._system_states: Any = system_states
        self._path_registry: Any = blueprint.path_registry

    def cleanup(self) -> None:
        """
        Release the builder's borrowed references and local transient state.

        Purpose:
            Mark the builder dead after one planning pass so later accidental
            reuse fails fast instead of retaining borrowed runtime references.

        Contract:
            - Idempotent.
            - Does not mutate the borrowed spell, blueprint, spell lookup, or
              system-state objects.
            - Releases only the builder's own references to those objects.

        Returns:
            None.
        """
        if self._cleaned:
            return

        self._cleaned = True
        del self._root_spell
        del self._blueprint
        del self._spell_lookup
        del self._system_states
        del self._path_registry

    def _require_active(self) -> None:
        """
        Raise when the builder is used after deterministic cleanup.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the builder has already been cleaned.
        """
        if self._cleaned:
            raise RuntimeError("OccurrencePlanBuilder has already been cleaned.")

    def build(self) -> OccurrencePlan:
        """
        Build and return the OccurrencePlan for the configured root blueprint.

        Contract:
            - Mirrors runtime occurrence planning behavior.
            - Compiles SpellContract override payloads for resolved dependencies.
            - Raises MeldExecutionError when dependency spells cannot be resolved
              in automatic mode.

        Returns:
            OccurrencePlan: The compiled phase 8 artifact.
        """
        self._require_active()
        root_spell_id = self._blueprint.root_spell_id
        dag = self._blueprint.dag
        ordered_node_ids = self._blueprint.ordered_node_ids
        collapse_shared_occurrences = self._should_collapse_shared_occurrences()

        occurrence_graph = self._build_occurrence_graph(
            dag=dag,
            root_spell_id=root_spell_id,
            collapse_shared_occurrences=collapse_shared_occurrences,
        )
        self._extend_occurrence_graph_with_ordered_nodes(
            occurrence_graph=occurrence_graph,
            ordered_node_ids=ordered_node_ids,
            dag=dag,
            collapse_shared_occurrences=collapse_shared_occurrences,
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
            path_registry=self._path_registry,
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

    @staticmethod
    def _occurrence_sort_key(occurrence: OccurrenceKey) -> Tuple[str, int]:
        """
        Build a deterministic ordering key for occurrence tuples.

        Contract:
            - Spell id is the primary sort key.
            - Path ids sort ascending.
            - None path ids sort before concrete ids.

        Args:
            occurrence: Occurrence tuple ``(spell_id, path_id)``.

        Returns:
            Tuple[str, int]: Comparable key used for deterministic ordering.
        """
        path_id = occurrence[1]
        if path_id is None:
            return occurrence[0], -1
        return occurrence[0], path_id

    @staticmethod
    def _iter_dependency_occurrences_for_enqueue(
            dependencies: Dict[str, List[OccurrenceKey]],
    ) -> Iterable[OccurrenceKey]:
        """
        Iterate dependency occurrences in deterministic queue order.

        Contract:
            - Parameters are traversed in lexical key order.
            - Occurrences for each parameter are traversed with occurrence sort.

        Args:
            dependencies: Parameter-to-occurrence mapping.

        Yields:
            OccurrenceKey: Dependency occurrence entries in canonical order.
        """
        for param_name in sorted(dependencies.keys()):
            child_occurrences = sorted(
                dependencies[param_name],
                key=OccurrencePlanBuilder._occurrence_sort_key,
            )
            for child_occurrence in child_occurrences:
                yield child_occurrence

    def _should_collapse_shared_occurrences(self) -> bool:
        """
        Determine whether shared occurrences can be collapsed during expansion.

        Purpose:
            Avoid expanding repeated shared-spell occurrences when mutation
            overrides are not present, which reduces path tuple churn in the
            occurrence graph.

        Contract:
            - Returns True only when no spell reports a non-empty mutation override.
            - Uses the spell.mutation_override payload as the signal.
            - Does not mutate any spell state.

        Returns:
            bool: True when shared occurrence collapse is allowed.
        """
        self._require_active()
        for spell in self._spell_lookup.values():
            if spell.mutation_override:
                return False
        return True

    def _build_occurrence_graph(
            self,
            *,
            dag: Any,
            root_spell_id: str,
            collapse_shared_occurrences: bool,
    ) -> Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]]:
        """
        Build a path-aware occurrence graph rooted at the entrypoint spell.

        Contract:
            - Returns a mapping of occurrence -> param_name -> child occurrences.
            - Uses local topology when available; falls back to DAG metadata.
            - Includes the root occurrence even if it has no dependencies.
            - When collapse_shared_occurrences is True, only the first occurrence
              for shared spell ids is expanded.

        Args:
            dag: DirectedAcyclicWorkGraph from the blueprint.
            root_spell_id: Version id for the root spell.
            collapse_shared_occurrences:
                When True, skip expanding repeated shared-spell occurrences.

        Returns:
            Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]]: Occurrence graph.
        """
        root_path_id = self._path_registry.root_path_id
        root_occurrence = (root_spell_id, root_path_id)
        occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]] = {}
        queue = deque([root_occurrence])
        seen: Set[OccurrenceKey] = set()
        queued: Set[OccurrenceKey] = {root_occurrence}
        shared_seen: Set[str] = set()

        while queue:
            occurrence = queue.popleft()
            queued.discard(occurrence)
            if occurrence in seen:
                continue

            spell_id, _ = occurrence
            if collapse_shared_occurrences:
                spell = self._spell_lookup.get(spell_id)
                if spell is not None and self._is_shared_existence(spell.existence):
                    if spell_id in shared_seen:
                        seen.add(occurrence)
                        continue
                    shared_seen.add(spell_id)
            seen.add(occurrence)

            dependencies = self._collect_occurrence_dependencies(
                occurrence=occurrence,
                dag=dag,
            )
            occurrence_graph[occurrence] = dependencies

            for child_occurrence in self._iter_dependency_occurrences_for_enqueue(
                    dependencies,
            ):
                if child_occurrence not in seen and child_occurrence not in queued:
                    queued.add(child_occurrence)
                    queue.append(child_occurrence)

        return occurrence_graph

    def _extend_occurrence_graph_with_ordered_nodes(
            self,
            *,
            occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]],
            ordered_node_ids: Sequence[str],
            dag: Any,
            collapse_shared_occurrences: bool,
    ) -> None:
        """
        Ensure ordered nodes outside the root path still get occurrences.

        Contract:
            - Nodes already present in the occurrence graph are left unchanged.
            - Missing ordered nodes are treated as additional entrypoints with
              empty paths and expanded via dependency discovery.
            - Newly discovered occurrences are appended without overwriting
              existing entries.
            - When collapse_shared_occurrences is True, only the first occurrence
              for shared spell ids is expanded.

        Args:
            occurrence_graph:
                Existing occurrence graph to extend in-place.
            ordered_node_ids:
                Ordered node ids from the blueprint.
            dag:
                DirectedAcyclicWorkGraph used for dependency discovery.
            collapse_shared_occurrences:
                When True, skip expanding repeated shared-spell occurrences.

        Returns:
            None.
        """
        existing_occurrences = set(occurrence_graph.keys())
        present_spell_ids = {spell_id for spell_id, _ in existing_occurrences}
        root_path_id = self._path_registry.root_path_id
        shared_seen: Set[str] = set()
        if collapse_shared_occurrences:
            for spell_id in present_spell_ids:
                spell = self._spell_lookup.get(spell_id)
                if spell is not None and self._is_shared_existence(spell.existence):
                    shared_seen.add(spell_id)

        for node_id in ordered_node_ids:
            if node_id in present_spell_ids:
                continue

            queue = deque([(node_id, root_path_id)])
            queued: Set[OccurrenceKey] = {(node_id, root_path_id)}
            while queue:
                occurrence = queue.popleft()
                queued.discard(occurrence)
                if occurrence in existing_occurrences:
                    continue
                spell_id, _ = occurrence
                if collapse_shared_occurrences:
                    spell = self._spell_lookup.get(spell_id)
                    if spell is not None and self._is_shared_existence(spell.existence):
                        if spell_id in shared_seen:
                            existing_occurrences.add(occurrence)
                            continue
                        shared_seen.add(spell_id)
                existing_occurrences.add(occurrence)
                present_spell_ids.add(occurrence[0])

                dependencies = self._collect_occurrence_dependencies(
                    occurrence=occurrence,
                    dag=dag,
                )
                occurrence_graph[occurrence] = dependencies

                for child_occurrence in self._iter_dependency_occurrences_for_enqueue(
                        dependencies,
                ):
                    if (
                            child_occurrence not in existing_occurrences
                            and child_occurrence not in queued
                    ):
                        queued.add(child_occurrence)
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
            - Uses spell-id lexical ordering as the deterministic tie-breaker.
            - If cycles are detected, returns fallback_order first, then remaining
              nodes in lexical order.

        Args:
            occurrence_graph: Path-aware occurrence graph.
            fallback_order: Blueprint order used as a stable tie-breaker.

        Returns:
            List[str]: Spell ids in execution order.
        """
        edges: Dict[str, Set[str]] = defaultdict(set)
        indegree: Dict[str, int] = defaultdict(int)
        nodes: Set[str] = set()

        for occurrence in sorted(
                occurrence_graph.keys(),
                key=OccurrencePlanBuilder._occurrence_sort_key,
        ):
            dependencies = occurrence_graph[occurrence]
            node_id = occurrence[0]
            nodes.add(node_id)
            for dependency_name in sorted(dependencies.keys()):
                dependency_list = dependencies[dependency_name]
                for dependency_occurrence in dependency_list:
                    dep_id = dependency_occurrence[0]
                    nodes.add(dep_id)
                    if node_id not in edges[dep_id]:
                        edges[dep_id].add(node_id)
                        indegree[node_id] += 1

        for node_id in sorted(nodes):
            indegree.setdefault(node_id, 0)

        queue = [node_id for node_id, degree in indegree.items() if degree == 0]
        heapq.heapify(queue)
        order: List[str] = []

        while queue:
            node_id = heapq.heappop(queue)
            order.append(node_id)
            for child_id in sorted(edges.get(node_id, [])):
                indegree[child_id] -= 1
                if indegree[child_id] == 0:
                    heapq.heappush(queue, child_id)

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
            - Falls back to DAG dependency metadata only when topology is unavailable.
            - Adds SpellContract dependencies when providers are available.
            - Adds mutation override dependencies.
            - Automatic mode treats missing SpellContract providers as build-time errors.
            - Dynamic mode tolerates missing SpellContract providers.

        Args:
            occurrence: The (spell_id, path_id) occurrence being expanded.
            dag: DirectedAcyclicWorkGraph for fallback dependency discovery.

        Returns:
            Dict[str, List[OccurrenceKey]]: Parameter-to-occurrence mapping.

        """
        spell_id, path_id = occurrence
        dependencies: Dict[str, List[OccurrenceKey]] = {}

        used_topology = self._append_topology_dependencies(
            dependencies=dependencies,
            spell_id=spell_id,
            path_id=path_id,
        )
        if not used_topology:
            self._append_dag_dependencies(
                dependencies=dependencies,
                spell_id=spell_id,
                path_id=path_id,
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
            path_id: int,
    ) -> bool:
        """
        Append dependencies discovered from SpellSystemStates local topology.

        Contract:
            - No-op if system states or topology are unavailable.
            - Appends child occurrences for each socket target.
            - Returns True when topology data was available (even if empty).

        Args:
            dependencies: Mapping to update in place.
            spell_id: Spell id for the occurrence.
            path_id: Occurrence path id.

        Returns:
            bool: True when local topology data was available; False otherwise.
        """
        topology = self._system_states._local_topologies.get(spell_id)
        if topology is None:
            return False

        path_registry = self._path_registry
        for socket in topology.sockets:
            if not socket.target_spell_ids:
                continue
            for target_id in socket.target_spell_ids:
                child_path_id = path_registry.extend_path(path_id, socket.param_name)
                child_occurrence = (target_id, child_path_id)
                dependencies.setdefault(socket.param_name, []).append(child_occurrence)
        return True

    def _append_dag_dependencies(
            self,
            *,
            dependencies: Dict[str, List[OccurrenceKey]],
            spell_id: str,
            path_id: int,
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
            path_id: Occurrence path id.
            dag: DirectedAcyclicWorkGraph used for dependency discovery.
        """
        if dag is None:
            return
        node = dag.get_node(spell_id)
        if node is None:
            return
        mutated_params: Set[str] = set()
        path_registry = self._path_registry
        parent_entries: List[Tuple[str, str, Any]] = []
        for parent_node in node.dependencies:
            incoming_name = node.incoming_params.get(parent_node)
            if incoming_name is None:
                continue
            parent_entries.append((incoming_name, parent_node.id, parent_node))
        for param_name, _, parent_node in sorted(parent_entries):
            socket_kind = dag._socket_kinds.get((parent_node, node))
            child_path_id = path_registry.extend_path(path_id, param_name)
            child_occurrence = (parent_node.id, child_path_id)

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
            - Prefers Phase 1 requirements when available; falls back to signature inspection.
            - Missing contracts raise during plan build in automatic mode.
            - Missing contracts are ignored during plan build in dynamic mode.

        Args:
            dependencies: Mapping to update with contract dependencies.
            occurrence: The (spell_id, path_id) occurrence being expanded.

        Raises:
            MeldExecutionError: If a SpellContract is ambiguous or inconsistent.
        """
        spell_id, path_id = occurrence
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
            child_path_id = self._path_registry.extend_path(path_id, param_name)
            child_occurrence = (target_spell_id, child_path_id)
            dependencies.setdefault(param_name, []).append(child_occurrence)

    def _iter_spell_contract_defaults(
            self,
            spell: Spell,
    ) -> Iterable[Tuple[str, SpellContract]]:
        """
        Yield SpellContract defaults discovered in the spell's call signature.

        Contract:
            - Only parameters with SpellContract defaults are returned.
            - Ignores "self"/"cls" and var-arg parameters.
            - Returns an empty iterable when the signature cannot be resolved.
            - Prefers Phase 1 requirements when available; falls back to signature inspection.

        Args:
            spell: Spell whose constructor or callable signature is inspected.

        Returns:
            Iterable[Tuple[str, SpellContract]]: Parameter names paired with
                SpellContract defaults.
        """
        contracts: List[Tuple[str, SpellContract]] = []
        requirements = None
        try:
            requirements = spell.requirements
        except AttributeError:
            requirements = None

        is_existing_creation = False
        try:
            is_existing_creation = spell.is_existing_creation
        except AttributeError:
            is_existing_creation = False

        if is_existing_creation:
            call_target = spell.spell
            signature = inspect.signature(call_target)
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

        if requirements is not None:
            for param in requirements.parameters:
                if param.di_shape is ParameterDIShape.SPELL_CONTRACT:
                    default_value = param.default_value
                    if isinstance(default_value, SpellContract):
                        contracts.append((param.name, default_value))
            return contracts

        call_target = spell.spell
        signature = inspect.signature(call_target)
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
            consumer_spell: Spell,
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
        if consumer_spell_id is None:
            consumer_spell_id = consumer_spell.spell_id
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
            consumer_spell: Spell,
            param_name: str,
    ) -> List[Spell]:
        """
        Collect contracted spell candidates that satisfy the contract key.

        Args:
            contract_key: Canonical (frame_key, binding_key) for the contract.
            consumer_spell: Spell declaring the contract.
            param_name: Parameter name for diagnostics.

        Returns:
            List[Spell]: Contracted spell candidates.
            Missing contract keys yield an empty list.
        """
        spellbook = self._root_spell._spellbook
        if spellbook is None:
            raise RuntimeError("Root spell has no owning spellbook.")
        contracted_lookup = spellbook._lookup_contracted_spells
        contracted_maps = spellbook._contracted_spells

        contracted_candidates: List[Spell] = []
        for conduit_id in sorted(contracted_lookup.keys()):
            lookup_map = contracted_lookup[conduit_id]
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

        contracted_candidates.sort(
            key=lambda spell: spell.spell_index.current or spell.spell_id
        )
        return contracted_candidates

    def _allow_missing_contract_providers(self) -> bool:
        """
        Determine whether plan build may tolerate missing SpellContract providers.

        Contract:
            - True only when system_state is dynamic.
            - Automatic mode remains strict and requires providers to resolve.
        """
        spellbook = self._root_spell._spellbook
        if spellbook is None:
            raise RuntimeError("Root spell has no owning spellbook.")
        frame_configuration = spellbook._aetheric_frame_configuration
        if frame_configuration is None:
            raise RuntimeError("Root spellbook has no frame configuration.")
        system_state = frame_configuration.system_state
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

        self._blueprint.ensure_dag_index_built()

        if not isinstance(mutation_override, dict):
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current,
                spell_name=self._root_spell.spell_name,
                message="mutation_override must be a dict of override_key -> spell_id.",
            )

        resolved: List[Tuple[SocketRef, str]] = []
        mutation_items: List[Tuple[Any, Any]]
        if all(isinstance(key, str) for key in mutation_override.keys()):
            mutation_items = [
                (raw_key, mutation_override[raw_key])
                for raw_key in sorted(mutation_override.keys())
            ]
        else:
            mutation_items = list(mutation_override.items())

        for raw_key, target_id in mutation_items:
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
                spell_id=self._root_spell.spell_index.current or self._root_spell.spell_id,
                spell_name=self._root_spell.spell_name,
                message="Invalid mutation_override key: {0!r}.".format(raw_key),
            )
        if not isinstance(target_id, str) or not target_id.strip():
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current or self._root_spell.spell_id,
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
                spell_id=self._root_spell.spell_index.current or self._root_spell.spell_id,
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
                spell_id=self._root_spell.spell_index.current or self._root_spell.spell_id,
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
                spell_id=self._root_spell.spell_index.current or self._root_spell.spell_id,
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
                spell_id=self._root_spell.spell_index.current or self._root_spell.spell_id,
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
                spell_id=self._root_spell.spell_index.current or self._root_spell.spell_id,
                spell_name=self._root_spell.spell_name,
                message=(
                    "No mutation sockets found for unique override "
                    "'*{0}'."
                ).format(spec.param_name),
            )
        if count > 1:
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current or self._root_spell.spell_id,
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
                spell_id=self._root_spell.spell_index.current or self._root_spell.spell_id,
                spell_name=self._root_spell.spell_name,
                message=(
                    "Broadcast override key {0!r} is missing a parameter name."
                ).format(raw_key),
            )
        candidates = dag_index.get_by_name(spec.param_name)
        matches = self._filter_mutation_contract_sockets(candidates)
        if not matches:
            raise MeldExecutionError(
                spell_id=self._root_spell.spell_index.current or self._root_spell.spell_id,
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
            occurrence: The (spell_id, path_id) occurrence being expanded.
        """
        spell_id, path_id = occurrence
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
            parent_id = self._path_registry.parent_id(socket_ref.param_path_id)
            if parent_id is None or parent_id != path_id:
                continue
            param_name = socket_ref.param_name
            child_path_id = self._path_registry.extend_path(path_id, param_name)
            child_occurrence = (target_id, child_path_id)
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
        for occurrence in sorted(
                occurrence_graph.keys(),
                key=self._occurrence_sort_key,
        ):
            spell_id, _ = occurrence
            occurrences_by_spell_id[spell_id].append(occurrence)

        instance_keys_by_spell_id: Dict[str, List[InstanceKey]] = {}
        canonical_occurrences_by_spell_id: Dict[str, OccurrenceKey] = {}
        shared_spell_ids: Set[str] = set()

        for spell_id in sorted(occurrences_by_spell_id.keys()):
            occurrences = sorted(
                occurrences_by_spell_id[spell_id],
                key=self._occurrence_sort_key,
            )
            spell = self._spell_lookup[spell_id]

            if self._is_shared_existence(spell.existence):
                shared_spell_ids.add(spell_id)
                canonical = self._select_canonical_occurrence(occurrences)
                canonical_occurrences_by_spell_id[spell_id] = canonical
                instance_keys_by_spell_id[spell_id] = [(spell_id, None)]
            else:
                instance_keys_by_spell_id[spell_id] = [
                    (spell_id, path_id) for _, path_id in occurrences
                ]

        root_occurrence = (root_spell_id, self._path_registry.root_path_id)
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
            - Only occurrences with override payloads are added to the map.

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

        for occurrence in sorted(
                occurrence_graph.keys(),
                key=self._occurrence_sort_key,
        ):
            dependencies = occurrence_graph[occurrence]
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
            occurrence: Current (spell_id, path_id) occurrence.
            dependencies: Dependency map for the occurrence.
            overrides_by_occurrence: Map to update with occurrence overrides.
            overrides_by_spell_id: Map to update with spell-id overrides.

        Returns:
            bool: True when contract dependencies and overrides aligned for
            this occurrence. In automatic mode, missing providers raise.
        """
        spell = self._resolve_occurrence_spell(occurrence)
        if spell is None:
            raise RuntimeError(
                "Occurrence spell could not be resolved from the spell lookup."
            )
        _, path_id = occurrence
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

            child_path_id = self._path_registry.extend_path(path_id, param_name)
            child_occurrence = (target_spell_id, child_path_id)
            consumer_spell_id = spell.spell_index.current or spell.spell_id

            normalized = self._normalize_contract_override_payload(
                payload=contract.spell_override,
                consumer_spell_id=consumer_spell_id,
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
    ) -> Optional[Spell]:
        """
        Resolve the spell object for a plan occurrence.

        Contract:
            - Returns the root spell when the occurrence matches the root id.
            - Returns None when no spell is available for the occurrence.

        Args:
            occurrence: (spell_id, path_id) tuple from the occurrence graph.

        Returns:
            Optional[Spell]: The spell object, or None if missing.
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
            - dict payloads are copied into a normalized map.
            - list/tuple payloads become {"__args__": tuple(payload)}.
            - None payloads produce an empty override map.

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
        if payload is None:
            return {}
        if isinstance(payload, dict):
            normalized_payload: Dict[str, Any] = {}
            for key, value in payload.items():
                if key == "__args__":
                    if not isinstance(value, (list, tuple)):
                        raise MeldExecutionError(
                            spell_id=consumer_spell_id,
                            spell_name=consumer_spell_name,
                            node_id=consumer_spell_id,
                            param_name=param_name,
                            message="SpellContract __args__ override must be a list or tuple.",
                        )
                    normalized_payload[key] = tuple(value)
                    continue
                normalized_payload[key] = value
            return normalized_payload
        if isinstance(payload, (list, tuple)):
            return {"__args__": tuple(payload)}
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
        stored_payload = dict(normalized_payload)
        if "__args__" in stored_payload and isinstance(stored_payload["__args__"], list):
            stored_payload["__args__"] = tuple(stored_payload["__args__"])
        overrides_by_occurrence[occurrence] = stored_payload
        overrides_by_spell_id.setdefault(spell_id, []).append(
            (occurrence, stored_payload)
        )

    @staticmethod
    def _select_canonical_occurrence(
            occurrences: Sequence[OccurrenceKey],
    ) -> OccurrenceKey:
        """
        Pick a stable occurrence for shared instance dependency paths.

        Contract:
            - The canonical occurrence is the lexicographically smallest
              occurrence key.

        Args:
            occurrences: Occurrences for the same spell id.

        Returns:
            OccurrenceKey: The canonical occurrence.
        """
        return min(
            occurrences,
            key=OccurrencePlanBuilder._occurrence_sort_key,
        )

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
            occurrence: The (spell_id, path_id) occurrence to map.

        Returns:
            InstanceKey: Instance key for the occurrence.

        Raises:
            MeldExecutionError: If the spell id cannot be resolved.
        """
        spell_id, path_id = occurrence
        spell = self._spell_lookup[spell_id]
        if self._is_shared_existence(spell.existence):
            return spell_id, None
        return spell_id, path_id
