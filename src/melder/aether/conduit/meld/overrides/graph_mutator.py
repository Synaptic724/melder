from __future__ import annotations

from typing import Any, Dict

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagTargetingEngine
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.dag.target_spec import TargetSpec
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.utilities.general_base.cleanable import Cleanable


class GraphMutator(Cleanable):
    """
    Runtime helper for applying mutation_override to a root blueprint.

    This implementation validates targets against MutationContract sockets and
    currently returns the underlying blueprint unchanged. It is a scaffold for
    future graph rewiring logic.
    """

    __slots__ = Cleanable.__slots__ + ["_blueprint", "_engine"]

    def __init__(self, blueprint: RootResolutionBlueprint) -> None:
        super().__init__()
        if blueprint is None:
            raise ValueError("blueprint must not be None.")
        self._blueprint: RootResolutionBlueprint = blueprint
        self._engine: DagTargetingEngine = DagTargetingEngine(blueprint.dag_index)

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True
        if self._engine is not None:
            try:
                self._engine.cleanup()
            except Exception:
                pass
        self._engine = None
        self._blueprint = None

    def apply(self, mutation_override: Dict[str, Any]) -> RootResolutionBlueprint:
        """
        Apply mutation overrides to a cloned blueprint, rewiring mutation sockets.

        Mutation config (MVP):
            { override_key: new_provider_spell_id }
        """
        self.check_cleaned()
        if not mutation_override:
            return self._blueprint

        def _filter_mutation(socket_ref):
            return socket_ref.socket_kind is SocketKind.MUTATION_CONTRACT

        # Validate override payload types up front.
        for raw_key, target_id in mutation_override.items():
            if not isinstance(raw_key, str) or not raw_key.strip():
                raise RuntimeError(f"Invalid mutation_override key: {raw_key!r}")
            if not isinstance(target_id, str) or not target_id.strip():
                raise RuntimeError(
                    f"Invalid mutation_override target for key '{raw_key}': expected non-empty spell_id string."
                )

        # Clone DAG shallowly (nodes/edges by key) and reuse socket_refs/index.
        source = self._blueprint
        new_dag = DirectedAcyclicWorkGraph()
        for node_id in source.dag.nodes.keys():
            new_dag.add_node(node_id)
        # We may add new target_ids; track them to sync sockets/index later.
        added_nodes = set()
        for parent_key, parent_node in source.dag.nodes.items():
            for child_node in parent_node.dependents:
                child_key = child_node.id
                param_name = child_node.incoming_params.get(parent_node)
                socket_kind = source.dag._socket_kinds.get((parent_node, child_node))
                new_dag.add_dependency(
                    parent_key=parent_key,
                    child_key=child_key,
                    param_name=param_name,
                    socket_kind=socket_kind,
                )

        # Rewire mutation sockets per override.
        for raw_key, target_id in mutation_override.items():
            spec = TargetSpec.parse(raw_key)
            sockets = self._engine.resolve(spec, _filter_mutation)
            for socket_ref in sockets:
                # Find parent->child edge and replace parent with new target id.
                # child is socket_ref.node_id
                child_id = socket_ref.node_id
                # Remove existing incoming edges matching this param_name
                child_node = new_dag.get_node(child_id)
                if child_node is None:
                    continue
                to_remove = []
                for parent in list(child_node.dependencies):
                    param_name = child_node.incoming_params.get(parent)
                    if param_name == socket_ref.param_name:
                        to_remove.append((parent.id, child_id, param_name))
                for parent_id, c_id, pname in to_remove:
                    # Rebuild edges without the old one
                    try:
                        parent_node = new_dag.get_node(parent_id)
                        if parent_node is not None:
                            child_node.dependencies.discard(parent_node)
                            parent_node.dependents.discard(child_node)
                            new_dag._socket_kinds.pop((parent_node, child_node), None)
                    except Exception:
                        pass
                # Add new edge to target_id
                new_dag.add_node(target_id)
                added_nodes.add(target_id)
                new_dag.add_dependency(
                    parent_key=target_id,
                    child_key=child_id,
                    param_name=socket_ref.param_name,
                    socket_kind=socket_ref.socket_kind,
                )

        # Recompute topo order
        ordered_ids = new_dag.collect_dependency_ids()

        # Build socket_refs/index; reuse existing ones for unchanged nodes.
        new_socket_refs = list(source.socket_refs)
        new_index = DagIndex()
        for ref in new_socket_refs:
            new_index.add_socket(ref)
        # For newly introduced nodes, we do not have topology; only index the mutation socket itself.
        for raw_key, target_id in mutation_override.items():
            spec = TargetSpec.parse(raw_key)
            sockets = self._engine.resolve(spec, _filter_mutation)
            for socket_ref in sockets:
                param_path = socket_ref.param_path
                new_ref = SocketRef(
                    node_id=target_id,
                    param_name=socket_ref.param_name,
                    param_path=param_path,
                    socket_kind=socket_ref.socket_kind,
                )
                new_socket_refs.append(new_ref)
                new_index.add_socket(new_ref)

        mutated_blueprint = RootResolutionBlueprint(
            root_spell_id=source.root_spell_id,
            root_lineage_id=source.root_lineage_id,
            dag=new_dag,
            ordered_node_ids=ordered_ids,
            socket_refs=new_socket_refs,
            dag_index=new_index,
        )
        return mutated_blueprint
