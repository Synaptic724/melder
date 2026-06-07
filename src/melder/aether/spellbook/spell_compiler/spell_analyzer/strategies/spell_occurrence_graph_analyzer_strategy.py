import inspect
from collections import deque
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.spell_analyzer.data.spell_existence_occurrence_analysis import (
    SpellExistenceOccurrence,
    SpellExistenceOccurrenceAnalysis,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.data.spell_occurrence_graph_analysis import (
    SpellOccurrenceGraphAnalysis,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy import (
    SpellAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell_compiler.dag.dag_index import (
        DagIndex,
        SocketRef,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.aether.spellbook.spellbook import Spellbook


OccurrenceKey = Tuple[str, int]


class SpellOccurrenceGraphAnalyzerStrategy(SpellAnalyzerStrategy):
    """
    Build the occurrence-graph analysis artifact for one spell.

    Purpose:
        Own the graph-expansion stage of the occurrence analyzer directly.
        This strategy is the occurrence lane's structural foundation: it turns
        rooted blueprint truth plus live topology context into one explicit
        path-aware occurrence graph that later strategies can trust as already-
        expanded input.

    Contract:
        - Consumes `Spell`, the existing `SpellCompilerArtifact`, the owning
          Spellbook spell pool, Phase 5 rooted blueprint truth, and current
          spell-system topology state.
        - Publishes only:
          - `_occurrence_graph_analysis`
          - `_occurrence_analysis_fast_key`
          - `_occurrence_analysis_input_signature`
        - Owns:
          - shared-occurrence collapse decisions
          - occurrence graph expansion
          - ordered-node graph completion
          - topology and DAG fallback dependency expansion
          - SpellContract dependency edge insertion
          - mutation-override dependency rewrites
          - cheap graph-side metrics
        - Does not compute execution order, instance/sharedness, or contract
          payload analysis artifacts. Later strategies own those outputs.
        - Existing-creation spells no-op because they do not participate in
          occurrence expansion.

    Threading:
        - Runs inside compiler-thread orchestration only.
        - Assumes upstream compiler coordination serializes artifact mutation
          for one spell during this analysis pass.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable registry id for this occurrence strategy.
        """
        return "spell_occurrence_graph_analyzer"

    def analyze(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Build and publish the occurrence-graph analysis artifact.

        Purpose:
            Materialize one compiler-owned graph analysis object for the
            current spell so later occurrence strategies do not have to reopen
            blueprint traversal, dependency expansion, or collapse rules.

        Contract:
            - Validates that the artifact is live before any work begins.
            - Computes the graph-side fast key and input signature directly in
              this strategy instead of reaching back into old Phase 8 helper
              methods.
            - Replaces the prior graph artifact atomically and best-effort
              cleans the superseded analysis object.
            - Leaves order, instance, and contract artifacts untouched.

        Returns:
            None.
        """
        artifact.check_cleaned()
        if spell.is_existing_creation:
            return

        spellbook = spell._spellbook
        if spellbook is None:
            raise RuntimeError(
                "SpellOccurrenceGraphAnalyzerStrategy requires a live owning Spellbook."
            )
        root_blueprint = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellOccurrenceGraphAnalyzerStrategy requires Phase 5 root blueprint truth."
            )
        spell_rows_and_existence = self._build_spell_rows_and_existence_occurrence_analysis(
            root_spell_id=root_blueprint.root_spell_id,
            spell_lookup=spellbook._spell_id_pool,
        )
        if spell_rows_and_existence is None:
            spell_rows = None
            existence_occurrence_analysis = None
        else:
            spell_rows, existence_occurrence_analysis = spell_rows_and_existence

        fast_key = self._build_occurrence_graph_fast_key(
            root_blueprint=root_blueprint,
            spell_lookup=spellbook._spell_id_pool,
            spellbook=spellbook,
            spell_system_states=spell._spell_system_states,
            spell_rows=spell_rows,
        )
        input_signature = self._build_occurrence_graph_input_signature(
            root_blueprint=root_blueprint,
            spell_lookup=spellbook._spell_id_pool,
            spellbook=spellbook,
            spell_system_states=spell._spell_system_states,
            spell_rows=spell_rows,
        )
        if (
                fast_key is not None
                and artifact._occurrence_analysis_fast_key == fast_key
                and input_signature is not None
                and artifact._occurrence_analysis_input_signature == input_signature
                and artifact._occurrence_graph_analysis is not None
        ):
            return

        collapse_shared_occurrences = True
        occurrence_graph = self._build_occurrence_graph(
            dag=root_blueprint.dag,
            root_spell_id=root_blueprint.root_spell_id,
            collapse_shared_occurrences=collapse_shared_occurrences,
            spell_lookup=spellbook._spell_id_pool,
            spell_system_states=spell._spell_system_states,
            path_registry=root_blueprint.path_registry,
            spellbook=spellbook,
            root_blueprint=root_blueprint,
        )
        self._extend_occurrence_graph_with_ordered_nodes(
            occurrence_graph=occurrence_graph,
            ordered_node_ids=root_blueprint.ordered_node_ids,
            dag=root_blueprint.dag,
            collapse_shared_occurrences=collapse_shared_occurrences,
            spell_lookup=spellbook._spell_id_pool,
            spell_system_states=spell._spell_system_states,
            path_registry=root_blueprint.path_registry,
            spellbook=spellbook,
            root_blueprint=root_blueprint,
        )
        graph_analysis = SpellOccurrenceGraphAnalysis(
            root_spell_id=root_blueprint.root_spell_id,
            occurrence_graph=occurrence_graph,
            path_registry=root_blueprint.path_registry,
            occurrence_count=len(occurrence_graph),
            edge_count=self._count_occurrence_edges(occurrence_graph),
            topology_dependency_count=self._count_topology_dependencies(
                spell_system_states=spell._spell_system_states,
                occurrence_graph=occurrence_graph,
            ),
            dag_fallback_dependency_count=self._count_dag_fallback_dependencies(
                spell_system_states=spell._spell_system_states,
                occurrence_graph=occurrence_graph,
            ),
            shared_collapse_enabled=collapse_shared_occurrences,
            existence_occurrence_analysis=existence_occurrence_analysis,
        )

        previous_graph = artifact._occurrence_graph_analysis
        artifact._occurrence_graph_analysis = graph_analysis
        artifact._occurrence_analysis_fast_key = fast_key
        artifact._occurrence_analysis_input_signature = input_signature
        self._cleanup_previous(previous_graph, graph_analysis)

    @staticmethod
    def _freeze_schema_value(value: Any) -> Any:
        """
        Normalize arbitrary values into deterministic schema-safe forms.

        Contract:
            - Preserves primitive scalar values.
            - Recursively normalizes composite values through the shared
              compiler execution helper.
            - Returns hashable deterministic rows suitable for signature input.
        """
        return SharedCompilerExecutions.freeze_phase11_schema_value(value)

    def _build_occurrence_graph_fast_key(
            self,
            *,
            root_blueprint: "RootResolutionBlueprint",
            spell_lookup: Dict[str, "Spell"],
            spellbook: "Spellbook",
            spell_system_states: Optional["SpellSystemStates"],
            spell_rows: Optional[Tuple[Any, ...]],
    ) -> Optional[Tuple[Any, ...]]:
        """
        Build a lightweight deterministic key for graph-analysis reuse.

        Purpose:
            Avoid recomputing the deep graph input signature when the upstream
            graph-shape inputs have not changed and no mutation overrides are
            present.

        Contract:
            - Returns `None` when required inputs are unavailable.
            - Returns `None` when any spell carries a mutation override,
              forcing the deep signature path.
            - Tracks blueprint identity, visible spell rows, local topology
              rows, and contracted provider routing rows.
        """
        if root_blueprint is None or spell_lookup is None:
            return None

        try:
            ordered_node_ids = tuple(root_blueprint.ordered_node_ids)
            path_registry_identity = id(root_blueprint.path_registry)
            blueprint_socket_rows = tuple(
                (
                    socket_ref.node_id,
                    socket_ref.param_name,
                    socket_ref.param_path_id,
                    socket_ref.socket_kind.value,
                )
                for socket_ref in (root_blueprint.socket_refs or ())
            )
        except Exception:
            return None

        if spell_rows is None:
            return None

        topology_rows: Tuple[Any, ...] = ()
        local_topologies = None
        if spell_system_states is not None:
            local_topologies = spell_system_states._local_topologies
        if local_topologies is not None:
            try:
                topology_rows_list: List[Tuple[Any, ...]] = []
                for spell_id in sorted(local_topologies.keys()):
                    topology = local_topologies.get(spell_id)
                    if topology is None:
                        continue
                    socket_rows = tuple(
                        (
                            socket.param_name,
                            tuple(sorted(socket.target_spell_ids)),
                        )
                        for socket in topology.sockets
                    )
                    topology_rows_list.append((spell_id, socket_rows))
                topology_rows = tuple(topology_rows_list)
            except Exception:
                return None

        try:
            contracted_lookup = spellbook._lookup_contracted_spells
            contracted_maps = spellbook._contracted_spells
            frame_configuration = spellbook._aetheric_frame_configuration
            if frame_configuration is None:
                return None
            system_state = frame_configuration.system_state
        except Exception:
            return None

        try:
            contracted_rows_list: List[Tuple[Any, ...]] = []
            for conduit_id in sorted(contracted_lookup.keys()):
                lookup_map = contracted_lookup.get(conduit_id)
                if lookup_map is None:
                    continue
                contracted_map = contracted_maps.get(conduit_id)
                for contract_key in sorted(lookup_map.keys()):
                    spell_index = lookup_map.get(contract_key)
                    if spell_index is None:
                        continue
                    provider_spell_id = None
                    if contracted_map is not None:
                        provider_spell = contracted_map.get(spell_index)
                        if provider_spell is not None:
                            provider_spell_id = provider_spell.spell_index.current
                    contracted_rows_list.append(
                        (
                            conduit_id,
                            contract_key[0],
                            contract_key[1],
                            provider_spell_id,
                        )
                    )
            contracted_rows = tuple(contracted_rows_list)
        except Exception:
            return None

        return (
            root_blueprint.root_spell_id,
            ordered_node_ids,
            path_registry_identity,
            blueprint_socket_rows,
            spell_rows,
            topology_rows,
            system_state,
            contracted_rows,
        )

    def _build_occurrence_graph_input_signature(
            self,
            *,
            root_blueprint: "RootResolutionBlueprint",
            spell_lookup: Dict[str, "Spell"],
            spellbook: "Spellbook",
            spell_system_states: Optional["SpellSystemStates"],
            spell_rows: Optional[Tuple[Any, ...]],
    ) -> Optional[str]:
        """
        Build a deterministic graph-analysis input signature.

        Purpose:
            Detect semantic drift in graph-shape inputs so repeated warm runs
            can safely skip redundant graph rebuilding when the upstream
            blueprint, spell set, topology, and contract-routing inputs are
            unchanged.

        Contract:
            - Returns `None` when required inputs are unavailable, forcing a
              rebuild.
            - Includes blueprint shape, spell mutation/existence rows, local
              topology rows, and contracted provider routing rows.
        """
        if root_blueprint is None or spell_lookup is None:
            return None

        try:
            ordered_node_ids = tuple(root_blueprint.ordered_node_ids)
            path_registry_identity = id(root_blueprint.path_registry)
            blueprint_socket_rows = tuple(
                (
                    socket_ref.node_id,
                    socket_ref.param_name,
                    socket_ref.param_path_id,
                    socket_ref.socket_kind.value,
                )
                for socket_ref in (root_blueprint.socket_refs or ())
            )
        except Exception:
            return None

        if spell_rows is None:
            return None

        topology_rows: Tuple[Any, ...] = ()
        local_topologies = None
        if spell_system_states is not None:
            local_topologies = spell_system_states._local_topologies
        if local_topologies is not None:
            try:
                topology_rows_list: List[Tuple[Any, ...]] = []
                for spell_id in sorted(local_topologies.keys()):
                    topology = local_topologies.get(spell_id)
                    if topology is None:
                        continue
                    socket_rows = tuple(
                        (
                            socket.param_name,
                            tuple(sorted(socket.target_spell_ids)),
                        )
                        for socket in topology.sockets
                    )
                    topology_rows_list.append((spell_id, socket_rows))
                topology_rows = tuple(topology_rows_list)
            except Exception:
                return None

        try:
            contracted_lookup = spellbook._lookup_contracted_spells
            contracted_maps = spellbook._contracted_spells
            frame_configuration = spellbook._aetheric_frame_configuration
            if frame_configuration is None:
                return None
            system_state = frame_configuration.system_state
        except Exception:
            return None

        try:
            contracted_rows_list: List[Tuple[Any, ...]] = []
            for conduit_id in sorted(contracted_lookup.keys()):
                lookup_map = contracted_lookup.get(conduit_id)
                if lookup_map is None:
                    continue
                contracted_map = contracted_maps.get(conduit_id)
                for contract_key in sorted(lookup_map.keys()):
                    spell_index = lookup_map.get(contract_key)
                    if spell_index is None:
                        continue
                    provider_spell_id = None
                    if contracted_map is not None:
                        provider_spell = contracted_map.get(spell_index)
                        if provider_spell is not None:
                            provider_spell_id = provider_spell.spell_index.current
                    contracted_rows_list.append(
                        (
                            conduit_id,
                            contract_key[0],
                            contract_key[1],
                            provider_spell_id,
                        )
                    )
            contracted_rows = tuple(contracted_rows_list)
        except Exception:
            return None

        return SharedCompilerExecutions.hash_codegen_signature(
            root_blueprint.root_spell_id,
            ordered_node_ids,
            path_registry_identity,
            blueprint_socket_rows,
            spell_rows,
            topology_rows,
            system_state,
            contracted_rows,
        )

    def _build_spell_rows_and_existence_occurrence_analysis(
            self,
            *,
            root_spell_id: str,
            spell_lookup: Dict[str, "Spell"],
    ) -> Optional[Tuple[Tuple[Any, ...], SpellExistenceOccurrenceAnalysis]]:
        """
        Build fast-key/input-signature spell rows plus existence-occurrence data in one walk.
        """
        if not root_spell_id or spell_lookup is None:
            return None

        try:
            spell_rows_list: List[Tuple[Any, ...]] = []
            occurrence_rows_list: List[SpellExistenceOccurrence] = []
            existence_counts_by_name: Dict[Existence, int] = {}
            existence_disposal_counts_by_name: Dict[Tuple[Existence, bool], int] = {}
            disposal_enabled_spell_count = 0
            root_existence: Optional[Existence] = None

            for spell_id, candidate_spell in sorted(spell_lookup.items()):
                current_spell_id = candidate_spell.spell_index.current
                existence = candidate_spell.existence
                has_disposal_methods = bool(candidate_spell.has_disposal_methods)
                spell_rows_list.append(
                    (
                        spell_id,
                        current_spell_id,
                        existence.name,
                        bool(candidate_spell.is_existing_creation),
                    )
                )
                occurrence_rows_list.append(
                    SpellExistenceOccurrence(
                        spell_id=spell_id,
                        existence=existence,
                        has_disposal_methods=has_disposal_methods,
                    )
                )
                current_count = existence_counts_by_name.get(existence, 0)
                existence_counts_by_name[existence] = current_count + 1
                current_pair_count = existence_disposal_counts_by_name.get(
                    (existence, has_disposal_methods),
                    0,
                )
                existence_disposal_counts_by_name[
                    (existence, has_disposal_methods)
                ] = current_pair_count + 1
                if has_disposal_methods:
                    disposal_enabled_spell_count += 1
                if spell_id == root_spell_id:
                    root_existence = existence
        except Exception:
            return None

        existence_counts = tuple(
            sorted(
                existence_counts_by_name.items(),
                key=lambda item: item[0].name,
            )
        )
        existence_disposal_counts = tuple(
            sorted(
                existence_disposal_counts_by_name.items(),
                key=lambda item: (
                    item[0][0].name,
                    int(item[0][1]),
                ),
            )
        )
        analysis = SpellExistenceOccurrenceAnalysis(
            root_existence=root_existence,
            total_spell_count=len(occurrence_rows_list),
            spell_existence_rows=tuple(occurrence_rows_list),
            existence_counts=existence_counts,
            disposal_enabled_spell_count=disposal_enabled_spell_count,
            existence_disposal_counts=existence_disposal_counts,
        )
        return tuple(spell_rows_list), analysis

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellOccurrenceGraphAnalysis],
            current: SpellOccurrenceGraphAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded occurrence-graph analysis artifact.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass

    @staticmethod
    def _is_shared_existence(existence: Existence) -> bool:
        """
        Determine whether an existence policy yields a shared instance.
        """
        return existence is not Existence.many

    @staticmethod
    def _occurrence_sort_key(
            occurrence: OccurrenceKey,
    ) -> Tuple[str, int]:
        """
        Build a deterministic ordering key for occurrence tuples.
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
        """
        for param_name in sorted(dependencies.keys()):
            child_occurrences = sorted(
                dependencies[param_name],
                key=SpellOccurrenceGraphAnalyzerStrategy._occurrence_sort_key,
            )
            for child_occurrence in child_occurrences:
                yield child_occurrence

    def _should_collapse_shared_occurrences(
            self,
            *,
            spell_lookup: Dict[str, "Spell"],
    ) -> bool:
        """
        Determine whether shared occurrences can be collapsed during expansion.
        """
        _ = spell_lookup
        return True

    def _build_occurrence_graph(
            self,
            *,
            dag: Any,
            root_spell_id: str,
            collapse_shared_occurrences: bool,
            spell_lookup: Dict[str, "Spell"],
            spell_system_states: "SpellSystemStates",
            path_registry: Any,
            spellbook: "Spellbook",
            root_blueprint: "RootResolutionBlueprint",
    ) -> Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]]:
        """
        Build a path-aware occurrence graph rooted at the entrypoint spell.

        Contract:
            - Includes the root occurrence even when it has no dependencies.
            - Expands dependencies from topology first, then DAG fallback,
              then contract and mutation overlays.
            - Applies shared-occurrence collapse only when the spell set is
              mutation-clean for the current run.
            - Returns one analyzer-owned occurrence graph mapping that later
              strategies must treat as read-only.
        """
        root_path_id = path_registry.root_path_id
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

            spell_id = occurrence[0]
            if collapse_shared_occurrences:
                spell = spell_lookup.get(spell_id)
                if spell is not None and self._is_shared_existence(spell.existence):
                    if spell_id in shared_seen:
                        seen.add(occurrence)
                        continue
                    shared_seen.add(spell_id)
            seen.add(occurrence)

            dependencies = self._collect_occurrence_dependencies(
                occurrence=occurrence,
                dag=dag,
                spell_lookup=spell_lookup,
                spell_system_states=spell_system_states,
                path_registry=path_registry,
                spellbook=spellbook,
                root_blueprint=root_blueprint,
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
            spell_lookup: Dict[str, "Spell"],
            spell_system_states: "SpellSystemStates",
            path_registry: Any,
            spellbook: "Spellbook",
            root_blueprint: "RootResolutionBlueprint",
    ) -> None:
        """
        Ensure ordered nodes outside the root path still get occurrences.
        """
        existing_occurrences = set(occurrence_graph.keys())
        present_spell_ids = {
            spell_id
            for spell_id, _ in existing_occurrences
        }
        root_path_id = path_registry.root_path_id
        shared_seen: Set[str] = set()
        if collapse_shared_occurrences:
            for spell_id in present_spell_ids:
                spell = spell_lookup.get(spell_id)
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

                spell_id = occurrence[0]
                if collapse_shared_occurrences:
                    spell = spell_lookup.get(spell_id)
                    if spell is not None and self._is_shared_existence(spell.existence):
                        if spell_id in shared_seen:
                            existing_occurrences.add(occurrence)
                            continue
                        shared_seen.add(spell_id)
                existing_occurrences.add(occurrence)
                present_spell_ids.add(spell_id)

                dependencies = self._collect_occurrence_dependencies(
                    occurrence=occurrence,
                    dag=dag,
                    spell_lookup=spell_lookup,
                    spell_system_states=spell_system_states,
                    path_registry=path_registry,
                    spellbook=spellbook,
                    root_blueprint=root_blueprint,
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

    def _collect_occurrence_dependencies(
            self,
            *,
            occurrence: OccurrenceKey,
            dag: Any,
            spell_lookup: Dict[str, "Spell"],
            spell_system_states: "SpellSystemStates",
            path_registry: Any,
            spellbook: "Spellbook",
            root_blueprint: "RootResolutionBlueprint",
    ) -> Dict[str, List[OccurrenceKey]]:
        """
        Collect dependency occurrences for a single spell occurrence.
        """
        dependencies: Dict[str, List[OccurrenceKey]] = {}

        used_topology = self._append_topology_dependencies(
            dependencies=dependencies,
            spell_id=occurrence[0],
            path_id=occurrence[1],
            spell_system_states=spell_system_states,
            path_registry=path_registry,
        )
        if not used_topology:
            self._append_dag_dependencies(
                dependencies=dependencies,
                spell_id=occurrence[0],
                path_id=occurrence[1],
                dag=dag,
                path_registry=path_registry,
            )
        self._apply_spell_contract_dependencies(
            dependencies=dependencies,
            occurrence=occurrence,
            spell_lookup=spell_lookup,
            spellbook=spellbook,
            path_registry=path_registry,
        )
        return dependencies

    @staticmethod
    def _append_topology_dependencies(
            *,
            dependencies: Dict[str, List[OccurrenceKey]],
            spell_id: str,
            path_id: int,
            spell_system_states: "SpellSystemStates",
            path_registry: Any,
    ) -> bool:
        """
        Append dependencies discovered from SpellSystemStates local topology.
        """
        topology = spell_system_states._local_topologies.get(spell_id)
        if topology is None:
            return False

        for socket in topology.sockets:
            if not socket.target_spell_ids:
                continue
            for target_id in socket.target_spell_ids:
                child_path_id = path_registry.extend_path(path_id, socket.param_name)
                dependencies.setdefault(socket.param_name, []).append(
                    (target_id, child_path_id)
                )
        return True

    @staticmethod
    def _append_dag_dependencies(
            *,
            dependencies: Dict[str, List[OccurrenceKey]],
            spell_id: str,
            path_id: int,
            dag: Any,
            path_registry: Any,
    ) -> None:
        """
        Append dependencies discovered from the DAG metadata.
        """
        if dag is None:
            return
        node = dag.get_node(spell_id)
        if node is None:
            return
        parent_entries: List[Tuple[str, str, Any]] = []
        for parent_node in node.dependencies:
            incoming_name = node.incoming_params.get(parent_node)
            if incoming_name is None:
                continue
            parent_entries.append((incoming_name, parent_node.id, parent_node))
        for param_name, _, parent_node in sorted(parent_entries):
            child_path_id = path_registry.extend_path(path_id, param_name)
            child_occurrence = (parent_node.id, child_path_id)

            dependencies.setdefault(param_name, []).append(child_occurrence)

    def _apply_spell_contract_dependencies(
            self,
            *,
            dependencies: Dict[str, List[OccurrenceKey]],
            occurrence: OccurrenceKey,
            spell_lookup: Dict[str, "Spell"],
            spellbook: "Spellbook",
            path_registry: Any,
    ) -> None:
        """
        Add dependency occurrences for SpellContract sockets.
        """
        spell = spell_lookup[occurrence[0]]
        allow_missing = self._allow_missing_contract_providers(spellbook)

        for param_name, contract in self._iter_spell_contract_defaults(spell):
            target_spell_id = self._resolve_spell_contract_spell_id(
                contract=contract,
                consumer_spell=spell,
                param_name=param_name,
                spellbook=spellbook,
                allow_missing=allow_missing,
            )
            if target_spell_id is None:
                continue
            child_path_id = path_registry.extend_path(occurrence[1], param_name)
            dependencies.setdefault(param_name, []).append(
                (target_spell_id, child_path_id)
            )

    @staticmethod
    def _iter_spell_contract_defaults(
            spell: "Spell",
    ) -> Iterable[Tuple[str, SpellContract]]:
        """
        Yield SpellContract defaults discovered in the spell's callable surface.
        """
        contracts: List[Tuple[str, SpellContract]] = []
        requirements = spell._compiler_artifact._requirements

        if spell.is_existing_creation:
            signature = inspect.signature(spell.spell)
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
                    if isinstance(param.default_value, SpellContract):
                        contracts.append((param.name, param.default_value))
            return contracts

        signature = inspect.signature(spell.spell)
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
            consumer_spell: "Spell",
            param_name: str,
            spellbook: "Spellbook",
            allow_missing: bool = False,
    ) -> Optional[str]:
        """
        Resolve a SpellContract to a concrete provider spell id.
        """
        consumer_spell_id = consumer_spell.spell_index.current
        if consumer_spell_id is None:
            consumer_spell_id = consumer_spell.spell_id

        contracted_candidates = self._collect_contracted_contract_candidates(
            contract_key=contract.canonical_key,
            spellbook=spellbook,
        )
        if len(contracted_candidates) > 1:
            raise MeldExecutionError(
                spell_id=consumer_spell_id,
                spell_name=consumer_spell.spell_name,
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
            spell_name=consumer_spell.spell_name,
            node_id=consumer_spell_id,
            param_name=param_name,
            message=(
                "SpellContract could not be resolved. "
                "No contracted spell matched the contract."
            ),
        )

    @staticmethod
    def _collect_contracted_contract_candidates(
            *,
            contract_key: Tuple[str, str],
            spellbook: "Spellbook",
    ) -> List["Spell"]:
        """
        Collect contracted spell candidates that satisfy the contract key.
        """
        contracted_candidates: List["Spell"] = []
        for conduit_id in sorted(spellbook._lookup_contracted_spells.keys()):
            lookup_map = spellbook._lookup_contracted_spells[conduit_id]
            spell_index = lookup_map.get(contract_key)
            if spell_index is None:
                continue
            contracted_map = spellbook._contracted_spells.get(conduit_id)
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

    @staticmethod
    def _allow_missing_contract_providers(
            spellbook: "Spellbook",
    ) -> bool:
        """
        Determine whether graph build may tolerate missing SpellContract providers.
        """
        frame_configuration = spellbook._aetheric_frame_configuration
        if frame_configuration is None:
            raise RuntimeError("Root spellbook has no frame configuration.")
        state_enum = EnumHelpers.convert_enum_and_check(
            frame_configuration.system_state,
            SystemState,
        )
        return state_enum is SystemState.dynamic

    @staticmethod
    def _count_occurrence_edges(
            occurrence_graph: Dict[Tuple[str, int], Dict[str, List[Tuple[str, int]]]],
    ) -> int:
        """
        Count the total number of dependency edges in the occurrence graph.
        """
        edge_count = 0
        for dependency_map in occurrence_graph.values():
            for dependency_occurrences in dependency_map.values():
                edge_count += len(dependency_occurrences)
        return edge_count

    @staticmethod
    def _count_topology_dependencies(
            *,
            spell_system_states: "SpellSystemStates",
            occurrence_graph: Dict[Tuple[str, int], Dict[str, List[Tuple[str, int]]]],
    ) -> int:
        """
        Count edges whose spell ids have topology entries.
        """
        topology_dependency_count = 0
        for occurrence, dependency_map in occurrence_graph.items():
            if spell_system_states._local_topologies.get(occurrence[0]) is None:
                continue
            for dependency_occurrences in dependency_map.values():
                topology_dependency_count += len(dependency_occurrences)
        return topology_dependency_count

    @staticmethod
    def _count_dag_fallback_dependencies(
            *,
            spell_system_states: "SpellSystemStates",
            occurrence_graph: Dict[Tuple[str, int], Dict[str, List[Tuple[str, int]]]],
    ) -> int:
        """
        Count edges whose spell ids had to fall back to DAG metadata.
        """
        fallback_count = 0
        for occurrence, dependency_map in occurrence_graph.items():
            if spell_system_states._local_topologies.get(occurrence[0]) is not None:
                continue
            for dependency_occurrences in dependency_map.values():
                fallback_count += len(dependency_occurrences)
        return fallback_count


