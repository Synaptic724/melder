from __future__ import annotations

from melder.aether.aether import Aether
from melder.aether.aetheric_frame import AethericFrame
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.system.spell_system_adjacency_builder import (
    SpellSystemAdjacencyBuilder,
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


def test_component_adjacency_builder_tracks_reverse_edges_and_topologies() -> None:
    """
    Purpose:
        Validate adjacency builder consumes SpellSystemStates end-to-end.
    Contract:
        - Dependencies and reverse edges reflect state wiring.
        - Roots are computed from incoming edges.
        - Registered local topologies are surfaced.
    Returns:
        None.
    Raises:
        AssertionError: If snapshot contents are incorrect.
    """
    frame = AethericFrame(Aether(), "component-adjacency-builder")
    states = frame._spell_system_states
    root_id = "root-adj"
    dep_a = "dep-a"
    dep_b = "dep-b"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_a)
    _register_lineage(states, dep_b)
    states.update_dependencies(root_index, [dep_a, dep_b])

    topology = SpellLocalTopology(
        spell_id=root_id,
        sockets=(
            SpellSocketDescriptor(
                spell_id=root_id,
                param_name="dep_a",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(dep_a,),
            ),
            SpellSocketDescriptor(
                spell_id=root_id,
                param_name="dep_b",
                position=1,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(dep_b,),
            ),
        ),
    )
    states.register_local_topology(root_index, topology)

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        assert snapshot.dependencies[root_id] == {dep_a, dep_b}
        assert snapshot.dependencies[dep_a] == set()
        assert snapshot.dependencies[dep_b] == set()
        assert snapshot.reverse_dependencies[dep_a] == {root_id}
        assert snapshot.reverse_dependencies[dep_b] == {root_id}
        assert snapshot.root_spell_ids == {root_id}
        assert snapshot.topologies[root_id] is topology
    finally:
        frame.cleanup()


def test_component_adjacency_builder_reflects_dependency_updates() -> None:
    """
    Purpose:
        Validate adjacency snapshots reflect updated dependencies.
    Contract:
        - Removed dependencies are excluded from the snapshot.
        - Reverse dependencies update accordingly.
    Returns:
        None.
    Raises:
        AssertionError: If snapshot does not reflect updated state.
    """
    frame = AethericFrame(Aether(), "component-adjacency-updates")
    states = frame._spell_system_states
    root_id = "root-update"
    dep_a = "dep-a-update"
    dep_b = "dep-b-update"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_a)
    _register_lineage(states, dep_b)

    states.update_dependencies(root_index, [dep_a, dep_b])
    states.update_dependencies(root_index, [dep_b])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        assert snapshot.dependencies[root_id] == {dep_b}
        assert snapshot.reverse_dependencies.get(dep_a, set()) == set()
        assert snapshot.reverse_dependencies[dep_b] == {root_id}
        assert snapshot.root_spell_ids == {root_id, dep_a}
    finally:
        frame.cleanup()


def test_component_adjacency_builder_empty_states_snapshot() -> None:
    """
    Purpose:
        Validate adjacency builder handles empty SpellSystemStates.
    Contract:
        - Snapshot collections are empty when no lineages are registered.
    Returns:
        None.
    Raises:
        AssertionError: If snapshot contains unexpected entries.
    """
    frame = AethericFrame(Aether(), "component-adjacency-empty")
    states = frame._spell_system_states
    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        assert snapshot.dependencies == {}
        assert snapshot.reverse_dependencies == {}
        assert snapshot.all_spell_ids == set()
        assert snapshot.root_spell_ids == set()
        assert snapshot.topologies == {}
    finally:
        frame.cleanup()


def test_component_adjacency_builder_ignores_unregistered_dependency_ids() -> None:
    """
    Purpose:
        Validate dependency ids without registered lineages do not change roots.
    Contract:
        - Unregistered dependency ids remain in dependencies.
        - Root spell ids still include the registered spell.
    Returns:
        None.
    Raises:
        AssertionError: If unregistered dependencies affect roots unexpectedly.
    """
    frame = AethericFrame(Aether(), "component-adjacency-ghost")
    states = frame._spell_system_states
    root_id = "root-ghost"
    root_index = _register_lineage(states, root_id)
    states.update_dependencies(root_index, ["ghost-id"])
    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        assert snapshot.dependencies[root_id] == {"ghost-id"}
        assert snapshot.root_spell_ids == {root_id}
        assert "ghost-id" not in snapshot.all_spell_ids
    finally:
        frame.cleanup()


def test_component_adjacency_builder_tracks_multiple_dependents() -> None:
    """
    Purpose:
        Validate reverse edges capture multiple dependents for a shared dependency.
    Contract:
        - Reverse dependencies include all parent spell ids.
        - Roots include each independent parent spell.
    Returns:
        None.
    Raises:
        AssertionError: If reverse dependencies are incomplete.
    """
    frame = AethericFrame(Aether(), "component-adjacency-multi-parent")
    states = frame._spell_system_states
    root_a = "root-parent-a"
    root_b = "root-parent-b"
    shared = "dep-shared"
    root_a_index = _register_lineage(states, root_a)
    root_b_index = _register_lineage(states, root_b)
    _register_lineage(states, shared)

    states.update_dependencies(root_a_index, [shared])
    states.update_dependencies(root_b_index, [shared])

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        assert snapshot.reverse_dependencies[shared] == {root_a, root_b}
        assert snapshot.dependencies[root_a] == {shared}
        assert snapshot.dependencies[root_b] == {shared}
        assert snapshot.root_spell_ids == {root_a, root_b}
    finally:
        frame.cleanup()


def test_component_adjacency_builder_collects_dependency_topologies() -> None:
    """
    Purpose:
        Validate dependency topologies are collected even when the root has none.
    Contract:
        - Snapshot includes topologies registered for dependency spells.
    Returns:
        None.
    Raises:
        AssertionError: If dependency topologies are missing.
    """
    frame = AethericFrame(Aether(), "component-adjacency-dep-topology")
    states = frame._spell_system_states
    root_id = "root-no-topology"
    dep_id = "dep-with-topology"
    root_index = _register_lineage(states, root_id)
    dep_index = _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    dep_topology = SpellLocalTopology(spell_id=dep_id, sockets=())
    states.register_local_topology(dep_index, dep_topology)

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        assert dep_id in snapshot.topologies
        assert snapshot.topologies[dep_id] is dep_topology
        assert snapshot.topologies[root_id] is None
    finally:
        frame.cleanup()


def test_component_adjacency_builder_ignores_unregistered_topology_entry() -> None:
    """
    Purpose:
        Validate topologies registered for unknown spell ids are ignored.
    Contract:
        - Snapshot excludes topologies that do not match registered spell ids.
    Returns:
        None.
    Raises:
        AssertionError: If ghost topologies are included.
    """
    frame = AethericFrame(Aether(), "component-adjacency-ghost-topology")
    states = frame._spell_system_states
    root_id = "root-ghost-topo"
    root_index = _register_lineage(states, root_id)
    states.update_dependencies(root_index, [])

    ghost_index = SpellIndex("ghost-topo")
    ghost_topology = SpellLocalTopology(spell_id="ghost-topo", sockets=())
    states.register_local_topology(ghost_index, ghost_topology)

    try:
        snapshot = SpellSystemAdjacencyBuilder.build(states)
        assert snapshot.topologies == {root_id: None}
    finally:
        frame.cleanup()

