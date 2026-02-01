from __future__ import annotations

from melder.aether.aetheric_frame import AethericFrame
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.system.spell_system_adjacency_builder import (
    SpellSystemAdjacencyBuilder,
)
from melder.spellbook.spell_crafter.system.spell_system_root_blueprint_builder import (
    SpellSystemRootBlueprintBuilder,
)
from melder.spellbook.spell_crafter.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)


def _register_lineage(states, spell_id: str) -> SpellIndex:
    """
    Purpose:
        Register a spell lineage into SpellSystemStates.
    Contract:
        - Returns a SpellIndex with current id set to spell_id.
        - Registers the lineage in the states registry.
    Args:
        states: SpellSystemStates registry.
        spell_id: Version id to register.
    Returns:
        SpellIndex: The created spell index.
    """
    index = SpellIndex(spell_id)
    states.register_lineage(index, object())
    return index


def test_component_root_blueprint_builder_traverses_state_topologies() -> None:
    """
    Purpose:
        Validate root blueprint builder consumes state topologies.
    Contract:
        - Socket refs include nested param paths across dependencies.
        - DagIndex resolves sockets by exact path.
    Returns:
        None.
    Raises:
        AssertionError: If socket traversal or indexing is incorrect.
    """
    frame = AethericFrame("component-root-blueprints")
    states = frame._spell_system_states
    root_id = "root-blueprint"
    mid_id = "mid-blueprint"
    leaf_id = "leaf-blueprint"
    root_index = _register_lineage(states, root_id)
    mid_index = _register_lineage(states, mid_id)
    _register_lineage(states, leaf_id)

    states.update_dependencies(root_index, [mid_id])
    states.update_dependencies(mid_index, [leaf_id])

    root_topology = SpellLocalTopology(
        spell_id=root_id,
        sockets=(
            SpellSocketDescriptor(
                spell_id=root_id,
                param_name="mid",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(mid_id,),
            ),
        ),
    )
    mid_topology = SpellLocalTopology(
        spell_id=mid_id,
        sockets=(
            SpellSocketDescriptor(
                spell_id=mid_id,
                param_name="leaf",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(leaf_id,),
            ),
        ),
    )
    states.register_local_topology(root_index, root_topology)
    states.register_local_topology(mid_index, mid_topology)

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        blueprints = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
        blueprint = blueprints[root_id]
        path_registry = blueprint.path_registry
        assert {path_registry.materialize_path(ref.param_path_id) for ref in blueprint.socket_refs} == {
            ("mid",),
            ("mid", "leaf"),
        }

        root_socket = blueprint.dag_index.get_by_exact_path(("mid",))[0]
        leaf_socket = blueprint.dag_index.get_by_exact_path(("mid", "leaf"))[0]
        assert root_socket.node_id == root_id
        assert leaf_socket.node_id == mid_id
        assert blueprint.ordered_node_ids[-1] == root_id
    finally:
        frame.cleanup()


def test_component_root_blueprint_builder_skips_missing_topology() -> None:
    """
    Purpose:
        Validate missing topologies prune socket traversal.
    Contract:
        - Socket refs are only collected for spells with registered topologies.
        - DAG still contains the full dependency chain.
    Returns:
        None.
    Raises:
        AssertionError: If socket collection ignores missing topologies.
    """
    frame = AethericFrame("component-root-blueprints-missing")
    states = frame._spell_system_states
    root_id = "root-missing-topo"
    mid_id = "mid-missing-topo"
    leaf_id = "leaf-missing-topo"
    root_index = _register_lineage(states, root_id)
    mid_index = _register_lineage(states, mid_id)
    _register_lineage(states, leaf_id)

    states.update_dependencies(root_index, [mid_id])
    states.update_dependencies(mid_index, [leaf_id])

    root_topology = SpellLocalTopology(
        spell_id=root_id,
        sockets=(
            SpellSocketDescriptor(
                spell_id=root_id,
                param_name="mid",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(mid_id,),
            ),
        ),
    )
    states.register_local_topology(root_index, root_topology)

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        blueprint = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)[
            root_id
        ]
        path_registry = blueprint.path_registry
        assert {path_registry.materialize_path(ref.param_path_id) for ref in blueprint.socket_refs} == {("mid",)}
        assert blueprint.dag_index.get_by_exact_path(("mid", "leaf")) == []
        assert set(blueprint.dag.nodes) == {root_id, mid_id, leaf_id}
    finally:
        frame.cleanup()


def test_component_root_blueprint_builder_builds_multiple_roots() -> None:
    """
    Purpose:
        Validate root blueprints are produced for multiple root spells.
    Contract:
        - Each root spell receives its own blueprint.
        - DAGs contain only the root node when no dependencies exist.
    Returns:
        None.
    Raises:
        AssertionError: If blueprints or DAGs are incorrect.
    """
    frame = AethericFrame("component-root-blueprints-multi")
    states = frame._spell_system_states
    root_a = "root-a"
    root_b = "root-b"
    root_a_index = _register_lineage(states, root_a)
    root_b_index = _register_lineage(states, root_b)

    topo_a = SpellLocalTopology(spell_id=root_a, sockets=())
    topo_b = SpellLocalTopology(spell_id=root_b, sockets=())
    states.register_local_topology(root_a_index, topo_a)
    states.register_local_topology(root_b_index, topo_b)

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        blueprints = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
        assert set(blueprints) == {root_a, root_b}
        assert set(blueprints[root_a].dag.nodes) == {root_a}
        assert set(blueprints[root_b].dag.nodes) == {root_b}
        assert blueprints[root_a].ordered_node_ids == [root_a]
        assert blueprints[root_b].ordered_node_ids == [root_b]
    finally:
        frame.cleanup()


def test_component_root_blueprint_builder_handles_shared_dependency() -> None:
    """
    Purpose:
        Validate shared dependencies appear in each root blueprint DAG.
    Contract:
        - Both root blueprints include the shared dependency node.
        - Each root depends on the shared node in its DAG.
    Returns:
        None.
    Raises:
        AssertionError: If shared dependencies are missing.
    """
    frame = AethericFrame("component-root-blueprints-shared")
    states = frame._spell_system_states
    root_a = "root-shared-a"
    root_b = "root-shared-b"
    shared = "dep-shared"
    root_a_index = _register_lineage(states, root_a)
    root_b_index = _register_lineage(states, root_b)
    _register_lineage(states, shared)

    states.update_dependencies(root_a_index, [shared])
    states.update_dependencies(root_b_index, [shared])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        blueprints = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
        assert set(blueprints) == {root_a, root_b}
        for root_id in (root_a, root_b):
            blueprint = blueprints[root_id]
            assert shared in blueprint.dag.nodes
            root_node = blueprint.dag.get_node(root_id)
            shared_node = blueprint.dag.get_node(shared)
            assert root_node is not None
            assert shared_node is not None
            assert shared_node in root_node.dependencies
    finally:
        frame.cleanup()


def test_component_root_blueprint_builder_records_empty_target_sockets() -> None:
    """
    Purpose:
        Validate sockets with empty target spell ids are still indexed.
    Contract:
        - Socket refs are emitted even when target_spell_ids is empty.
        - DagIndex resolves the socket path for the root spell.
    Returns:
        None.
    Raises:
        AssertionError: If socket refs are missing.
    """
    frame = AethericFrame("component-root-blueprints-empty-target")
    states = frame._spell_system_states
    root_id = "root-empty-target"
    root_index = _register_lineage(states, root_id)
    states.update_dependencies(root_index, [])

    topology = SpellLocalTopology(
        spell_id=root_id,
        sockets=(
            SpellSocketDescriptor(
                spell_id=root_id,
                param_name="config",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=True,
                target_spell_ids=(),
            ),
        ),
    )
    states.register_local_topology(root_index, topology)

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        blueprint = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)[
            root_id
        ]
        path_registry = blueprint.path_registry
        assert {path_registry.materialize_path(ref.param_path_id) for ref in blueprint.socket_refs} == {("config",)}
        assert blueprint.dag_index.get_by_exact_path(("config",)) != []
    finally:
        frame.cleanup()
