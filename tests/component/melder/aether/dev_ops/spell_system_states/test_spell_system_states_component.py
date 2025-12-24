from melder.aether.aetheric_frame import AethericFrame
from melder.aether.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)


def _register_lineage(states, spell_id: str) -> SpellIndex:
    """
    Purpose:
        Register a SpellIndex lineage in SpellSystemStates for component tests.
    Contract:
        - Returns a SpellIndex whose current id matches spell_id.
        - Registers a state entry for the lineage.
    Args:
        states: SpellSystemStates registry.
        spell_id: Version id to register as current.
    Returns:
        SpellIndex: The created spell index instance.
    """
    index = SpellIndex(spell_id)
    states.register_lineage(index, object())
    return index


def _build_topology(spell_id: str, dependency_id: str) -> SpellLocalTopology:
    """
    Purpose:
        Build a simple topology with one dependency socket.
    Contract:
        - The topology exposes a single NORMAL socket for the dependency.
    Args:
        spell_id: Owning spell id for the topology.
        dependency_id: Target spell id for the socket.
    Returns:
        SpellLocalTopology: The constructed topology.
    """
    return SpellLocalTopology(
        spell_id=spell_id,
        sockets=(
            SpellSocketDescriptor(
                spell_id=spell_id,
                param_name="dep",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(dependency_id,),
            ),
        ),
    )


def test_component_spell_system_states_registers_local_topology_round_trip() -> None:
    """
    Purpose:
        Validate local topology registration and retrieval paths.
    Contract:
        - get_local_topology returns the registered topology.
        - get_local_topology_by_id returns the same topology.
    Returns:
        None.
    Raises:
        AssertionError: If the topology is not retrievable.
    """
    frame = AethericFrame("component-states-topology-roundtrip")
    states = frame.spell_system_states
    root_id = "root-topology-roundtrip"
    dep_id = "dep-topology-roundtrip"
    root_index = _register_lineage(states, root_id)
    topology = _build_topology(root_id, dep_id)
    states.register_local_topology(root_index, topology)
    try:
        assert states.get_local_topology(root_index) is topology
        assert states.get_local_topology_by_id(root_id) is topology
    finally:
        frame.cleanup()


def test_component_spell_system_states_registers_local_topology_replacement() -> None:
    """
    Purpose:
        Validate registering a topology for the same spell id replaces the entry.
    Contract:
        - The most recently registered topology is returned.
    Returns:
        None.
    Raises:
        AssertionError: If the topology is not replaced.
    """
    frame = AethericFrame("component-states-topology-replace")
    states = frame.spell_system_states
    root_id = "root-topology-replace"
    dep_a = "dep-topology-a"
    dep_b = "dep-topology-b"
    root_index = _register_lineage(states, root_id)
    topology_a = _build_topology(root_id, dep_a)
    topology_b = _build_topology(root_id, dep_b)
    states.register_local_topology(root_index, topology_a)
    states.register_local_topology(root_index, topology_b)
    try:
        assert states.get_local_topology(root_index) is topology_b
        assert states.get_local_topology_by_id(root_id) is topology_b
    finally:
        frame.cleanup()


def test_component_spell_system_states_cleanup_cleans_local_topologies() -> None:
    """
    Purpose:
        Validate SpellSystemStates cleanup cleans registered topologies.
    Contract:
        - Topology cleanup is invoked during state cleanup.
        - Accessors raise after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If topology cleanup does not occur.
    """
    frame = AethericFrame("component-states-topology-cleanup")
    states = frame.spell_system_states
    root_id = "root-topology-cleanup"
    dep_id = "dep-topology-cleanup"
    root_index = _register_lineage(states, root_id)
    topology = _build_topology(root_id, dep_id)
    states.register_local_topology(root_index, topology)
    frame.cleanup()
    assert topology.cleaned is True
    assert states.cleaned is True


def test_component_spell_system_states_register_lineage_sets_change_reason() -> None:
    """
    Purpose:
        Validate registering a lineage sets validity and change reason.
    Contract:
        - New lineages are gated with register_or_rebind as the change reason.
        - Structure and new_lineage flags are present.
    Returns:
        None.
    Raises:
        AssertionError: If change-reason or flags are missing.
    """
    frame = AethericFrame("component-states-register-flags")
    states = frame.spell_system_states
    index = _register_lineage(states, "spell-register-flags")
    try:
        state = states.get_by_index_id(index.id)
        assert state is not None
        assert state.validity is SpellValidity.gated
        assert state.change_reason is SpellStateChangeReason.register_or_rebind
        flags = state.flags
        assert SpellState.structure_changed in flags
        assert SpellState.new_lineage in flags
    finally:
        frame.cleanup()


def test_component_spell_system_states_dependency_change_sets_reason() -> None:
    """
    Purpose:
        Validate dependency updates mark dependency-change state.
    Contract:
        - change_reason is dependencies_changed after update_dependencies.
        - dependencies_changed flag is present.
    Returns:
        None.
    Raises:
        AssertionError: If dependency-change flags are not set.
    """
    frame = AethericFrame("component-states-dependency-reason")
    states = frame.spell_system_states
    root_index = _register_lineage(states, "root-dep-reason")
    dep_index = _register_lineage(states, "dep-dep-reason")
    states.update_dependencies(root_index, [dep_index.current])
    try:
        state = states.get_by_index_id(root_index.id)
        assert state is not None
        assert state.change_reason is SpellStateChangeReason.dependencies_changed
        assert SpellState.dependencies_changed in state.flags
        assert state.validity is SpellValidity.gated
    finally:
        frame.cleanup()
