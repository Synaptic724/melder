from __future__ import annotations

from melder.aether.aether import Aether
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


def test_component_snapshot_tracks_unregistered_dependency_ids() -> None:
    """
    Purpose:
        Validate unregistered dependency ids appear in reverse edges.
    Contract:
        - Reverse dependencies include the ghost id.
        - Ghost ids are not added to all_spell_ids.
    Returns:
        None.
    Raises:
        AssertionError: If ghost dependencies are mishandled.
    """
    frame = AethericFrame(Aether(), "component-snapshot-ghost")
    states = frame._spell_system_states
    root_id = "root-ghost-snap"
    root_index = _register_lineage(states, root_id)
    states.update_dependencies(root_index, ["ghost-id"])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        assert snapshot.dependencies[root_id] == {"ghost-id"}
        assert snapshot.reverse_dependencies["ghost-id"] == {root_id}
        assert "ghost-id" not in snapshot.all_spell_ids
        assert snapshot.root_spell_ids == {root_id}
    finally:
        frame.cleanup()


def test_component_snapshot_cleanup_does_not_clean_topologies() -> None:
    """
    Purpose:
        Validate snapshot cleanup does not clean topology objects.
    Contract:
        - Snapshot cleanup leaves SpellLocalTopology intact.
        - SpellSystemStates still returns the topology after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If topology is cleaned by snapshot cleanup.
    """
    frame = AethericFrame(Aether(), "component-snapshot-cleanup")
    states = frame._spell_system_states
    root_id = "root-topology"
    root_index = _register_lineage(states, root_id)
    states.update_dependencies(root_index, [])

    topology = SpellLocalTopology(
        spell_id=root_id,
        sockets=(
            SpellSocketDescriptor(
                spell_id=root_id,
                param_name="socket",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(),
            ),
        ),
    )
    states.register_local_topology(root_index, topology)

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        snapshot.cleanup()
        assert topology.cleaned is False
        assert states.get_local_topology_by_id(root_id) is topology
    finally:
        frame.cleanup()


def test_component_snapshot_roots_change_after_dependency_removed() -> None:
    """
    Purpose:
        Validate root ids adjust after dependency removal.
    Contract:
        - After removing the dependency, both spells are roots.
    Returns:
        None.
    Raises:
        AssertionError: If root ids do not update.
    """
    frame = AethericFrame(Aether(), "component-snapshot-root-shift")
    states = frame._spell_system_states
    root_id = "root-shift"
    dep_id = "dep-shift"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])
    states.update_dependencies(root_index, [])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        assert snapshot.root_spell_ids == {root_id, dep_id}
    finally:
        frame.cleanup()


def test_component_snapshot_collects_multiple_topologies() -> None:
    """
    Purpose:
        Validate snapshot captures multiple registered topologies.
    Contract:
        - Topologies for both spells are present in the snapshot.
    Returns:
        None.
    Raises:
        AssertionError: If topologies are missing.
    """
    frame = AethericFrame(Aether(), "component-snapshot-multi-topology")
    states = frame._spell_system_states
    root_id = "root-topo"
    dep_id = "dep-topo"
    root_index = _register_lineage(states, root_id)
    dep_index = _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    root_topology = SpellLocalTopology(spell_id=root_id, sockets=())
    dep_topology = SpellLocalTopology(spell_id=dep_id, sockets=())
    states.register_local_topology(root_index, root_topology)
    states.register_local_topology(dep_index, dep_topology)

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        assert snapshot.topologies[root_id] is root_topology
        assert snapshot.topologies[dep_id] is dep_topology
    finally:
        frame.cleanup()


def test_component_snapshot_helpers_resolve_shared_dependency() -> None:
    """
    Purpose:
        Validate snapshot helpers report shared dependencies for multiple roots.
    Contract:
        - Shared dependency shows both parents in reverse dependencies.
        - Root dependencies expose the shared dependency.
    Returns:
        None.
    Raises:
        AssertionError: If helper outputs are incorrect.
    """
    frame = AethericFrame(Aether(), "component-snapshot-shared")
    states = frame._spell_system_states
    root_a = "root-share-a"
    root_b = "root-share-b"
    shared = "dep-share"
    root_a_index = _register_lineage(states, root_a)
    root_b_index = _register_lineage(states, root_b)
    _register_lineage(states, shared)
    states.update_dependencies(root_a_index, [shared])
    states.update_dependencies(root_b_index, [shared])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        assert snapshot.get_reverse_dependencies_for(shared) == {root_a, root_b}
        assert snapshot.get_dependencies_for(root_a) == {shared}
        assert snapshot.get_dependencies_for(root_b) == {shared}
    finally:
        frame.cleanup()


def test_component_snapshot_mutation_drives_blueprint_builder() -> None:
    """
    Purpose:
        Validate blueprint building consumes the snapshot dependencies as-is.
    Contract:
        - Mutating snapshot dependencies affects the resulting blueprint DAG.
    Returns:
        None.
    Raises:
        AssertionError: If blueprint ignores snapshot dependency changes.
    """
    frame = AethericFrame(Aether(), "component-snapshot-mutation")
    states = frame._spell_system_states
    root_id = "root-mutation"
    dep_id = "dep-mutation"
    extra_id = "dep-extra"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        snapshot.dependencies[root_id].add(extra_id)
        snapshot.reverse_dependencies.setdefault(extra_id, set()).add(root_id)
        snapshot.all_spell_ids.add(extra_id)

        blueprints = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
        blueprint = blueprints[root_id]
        assert extra_id in blueprint.dag.nodes
        root_node = blueprint.dag.get_node(root_id)
        extra_node = blueprint.dag.get_node(extra_id)
        assert root_node is not None
        assert extra_node is not None
        assert extra_node in root_node.dependencies
    finally:
        frame.cleanup()


def test_component_snapshot_topologies_feed_blueprint_builder() -> None:
    """
    Purpose:
        Validate snapshot topologies are used to seed blueprint socket refs.
    Contract:
        - Socket refs match registered topology sockets.
        - DagIndex resolves the socket path.
    Returns:
        None.
    Raises:
        AssertionError: If socket refs are not recorded.
    """
    frame = AethericFrame(Aether(), "component-snapshot-topology-blueprint")
    states = frame._spell_system_states
    root_id = "root-topology-blueprint"
    dep_id = "dep-topology-blueprint"
    root_index = _register_lineage(states, root_id)
    dep_index = _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    topology = SpellLocalTopology(
        spell_id=root_id,
        sockets=(
            SpellSocketDescriptor(
                spell_id=root_id,
                param_name="dep",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(dep_id,),
            ),
        ),
    )
    states.register_local_topology(root_index, topology)

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        blueprint = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)[
            root_id
        ]
        blueprint.ensure_dag_index_built()
        path_registry = blueprint.path_registry
        assert {path_registry.materialize_path(ref.param_path_id) for ref in blueprint.socket_refs} == {("dep",)}
        assert blueprint.dag_index.get_by_exact_path(("dep",)) != []
    finally:
        frame.cleanup()

