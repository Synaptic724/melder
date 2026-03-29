from melder.aether.aether import Aether
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
    frame = AethericFrame(Aether(), "component-states-topology-roundtrip")
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
    frame = AethericFrame(Aether(), "component-states-topology-replace")
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
    frame = AethericFrame(Aether(), "component-states-topology-cleanup")
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
    frame = AethericFrame(Aether(), "component-states-register-flags")
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
    frame = AethericFrame(Aether(), "component-states-dependency-reason")
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


def test_component_spell_system_states_rebind_updates_spell_id_index() -> None:
    """
    Purpose:
        Validate re-registering a lineage refreshes the spell-id index.
    Contract:
        - register_lineage updates the current spell id on the existing state.
        - get_by_spell_id resolves the updated current id.
        - change_reason remains register_or_rebind after rebind.
    Returns:
        None.
    Raises:
        AssertionError: If the spell-id index is not refreshed.
    """
    frame = AethericFrame(Aether(), "component-states-rebind")
    states = frame.spell_system_states
    index = _register_lineage(states, "spell-rebind-v1")
    try:
        state = states.get_by_index_id(index.id)
        assert state is not None
        assert state.current_spell_id == "spell-rebind-v1"

        index.update("spell-rebind-v2")
        states.register_lineage(index, object())

        state = states.get_by_index_id(index.id)
        assert state is not None
        assert state.current_spell_id == "spell-rebind-v2"
        assert states.get_by_spell_id("spell-rebind-v2") is state
        assert state.change_reason is SpellStateChangeReason.register_or_rebind
    finally:
        frame.cleanup()


def test_component_spell_system_states_impact_closure_preserves_root_state() -> None:
    """
    Purpose:
        Validate impact closure marks dependents transitively dirty while preserving root state.
    Contract:
        - Root remains non-transitively dirty with a structural-change reason.
        - Dependents are marked impacted_by_dependency with dependency_changed reason.
        - Dirty lineage set includes the root and dependent.
    Returns:
        None.
    Raises:
        AssertionError: If impact closure flags are incorrect.
    """
    frame = AethericFrame(Aether(), "component-states-impact-closure")
    states = frame.spell_system_states
    root_index = _register_lineage(states, "root-impact-closure")
    dep_index = _register_lineage(states, "dep-impact-closure")
    states.update_dependencies(dep_index, [root_index.current])
    states.consume_dirty_lineages()
    states.mark_structural_change(root_index)

    impacted = states.compute_impact_closure([root_index.id])
    try:
        assert impacted == {root_index.id, dep_index.id}
        root_state = states.get_by_index_id(root_index.id)
        dep_state = states.get_by_index_id(dep_index.id)
        assert root_state is not None
        assert dep_state is not None
        assert root_state.transitively_dirty is False
        assert root_state.change_reason is SpellStateChangeReason.structure_changed
        assert SpellState.structure_changed in root_state.flags
        assert dep_state.transitively_dirty is True
        assert dep_state.change_reason is SpellStateChangeReason.dependency_changed
        assert SpellState.impacted_by_dependency in dep_state.flags
        dirty = set(states.consume_dirty_lineages())
        assert dirty == {root_index.id, dep_index.id}
    finally:
        frame.cleanup()


def test_component_spell_system_states_mark_structural_change_marks_dirty() -> None:
    """
    Purpose:
        Validate mark_structural_change marks the lineage dirty with correct flags.
    Contract:
        - Dirty list includes the lineage after structural change.
        - change_reason is structure_changed and structure_changed flag is set.
    Returns:
        None.
    Raises:
        AssertionError: If dirty tracking or flags are incorrect.
    """
    frame = AethericFrame(Aether(), "component-states-structural-dirty")
    states = frame.spell_system_states
    index = _register_lineage(states, "spell-structural-dirty")
    states.consume_dirty_lineages()
    try:
        states.mark_structural_change(index)
        dirty = set(states.consume_dirty_lineages())
        assert index.id in dirty
        state = states.get_by_index_id(index.id)
        assert state is not None
        assert state.change_reason is SpellStateChangeReason.structure_changed
        assert SpellState.structure_changed in state.flags
        assert state.validity is SpellValidity.gated
    finally:
        frame.cleanup()


def test_component_spell_system_states_update_dependencies_tracks_reverse_edges() -> None:
    """
    Purpose:
        Validate dependency updates wire and unwind reverse edges.
    Contract:
        - Dependencies are attached to the root state.
        - Dependents are registered on dependency states.
        - Removing dependencies clears reverse edges.
    Returns:
        None.
    Raises:
        AssertionError: If edges are not wired correctly.
    """
    frame = AethericFrame(Aether(), "component-states-reverse-edges")
    states = frame.spell_system_states
    root_index = _register_lineage(states, "root-reverse-edges")
    dep_index = _register_lineage(states, "dep-reverse-edges")
    states.consume_dirty_lineages()
    try:
        states.update_dependencies(root_index, [dep_index.current])
        root_state = states.get_by_index_id(root_index.id)
        dep_state = states.get_by_index_id(dep_index.id)
        assert root_state is not None
        assert dep_state is not None
        assert dep_index.current in root_state.direct_dependencies
        assert root_index.id in dep_state.direct_dependents
        assert root_state.change_reason is SpellStateChangeReason.dependencies_changed
        assert SpellState.dependencies_changed in root_state.flags

        states.update_dependencies(root_index, [])
        dep_state = states.get_by_index_id(dep_index.id)
        assert dep_state is not None
        assert root_index.id not in dep_state.direct_dependents
    finally:
        frame.cleanup()


def test_component_spell_system_states_consume_dirty_lineages_clears() -> None:
    """
    Purpose:
        Validate consume_dirty_lineages clears the dirty queue.
    Contract:
        - Registered lineages appear in the dirty list.
        - consume_dirty_lineages clears the queue after read.
    Returns:
        None.
    Raises:
        AssertionError: If the dirty queue is not cleared.
    """
    frame = AethericFrame(Aether(), "component-states-consume-dirty")
    states = frame.spell_system_states
    index_a = _register_lineage(states, "spell-dirty-a")
    index_b = _register_lineage(states, "spell-dirty-b")
    try:
        dirty = set(states.consume_dirty_lineages())
        assert index_a.id in dirty
        assert index_b.id in dirty
        assert states.consume_dirty_lineages() == []
    finally:
        frame.cleanup()


def test_component_spell_system_states_cleanup_cleans_spell_system_state() -> None:
    """
    Purpose:
        Validate cleanup cascades to SpellSystemState objects.
    Contract:
        - SpellSystemState instances are cleaned when the frame is cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If state objects remain uncleaned.
    """
    frame = AethericFrame(Aether(), "component-states-cleanup-state")
    states = frame.spell_system_states
    index = _register_lineage(states, "spell-state-cleanup")
    state = states.get_by_index_id(index.id)
    assert state is not None
    frame.cleanup()
    assert state.cleaned is True


def test_component_spell_system_states_clear_dirty_resets_state_flags() -> None:
    """
    Purpose:
        Validate clearing dirty state resets topology flags on SpellSystemState.
    Contract:
        - clear_dirty sets validity to valid and resets last_validated_at.
        - topology-related flags are removed.
    Returns:
        None.
    Raises:
        AssertionError: If flags or validity remain dirty after clear.
    """
    frame = AethericFrame(Aether(), "component-states-clear-dirty")
    states = frame.spell_system_states
    root_index = _register_lineage(states, "root-clear-dirty")
    dep_index = _register_lineage(states, "dep-clear-dirty")
    states.update_dependencies(root_index, [dep_index.current])
    try:
        state = states.get_by_index_id(root_index.id)
        assert state is not None
        state.clear_dirty(last_validated_at=123.0)
        assert state.validity is SpellValidity.valid
        assert state.dirty is False
        assert state.last_validated_at == 123.0
        flags = state.flags
        assert SpellState.new_lineage not in flags
        assert SpellState.structure_changed not in flags
        assert SpellState.dependencies_changed not in flags
    finally:
        frame.cleanup()


def test_component_spell_system_states_rebind_preserves_old_spell_id_mapping() -> None:
    """
    Purpose:
        Validate old spell ids continue resolving after a rebind.
    Contract:
        - get_by_spell_id resolves both the old and new version ids.
    Returns:
        None.
    Raises:
        AssertionError: If old spell ids are not still resolvable.
    """
    frame = AethericFrame(Aether(), "component-states-rebind-old-id")
    states = frame.spell_system_states
    index = _register_lineage(states, "spell-rebind-old-id")
    try:
        state = states.get_by_index_id(index.id)
        assert state is not None
        index.update("spell-rebind-new-id")
        states.register_lineage(index, object())
        assert states.get_by_spell_id("spell-rebind-old-id") is state
        assert states.get_by_spell_id("spell-rebind-new-id") is state
    finally:
        frame.cleanup()


def test_component_spell_system_states_update_dependencies_with_unknown_dep() -> None:
    """
    Purpose:
        Validate unknown dependency ids are tracked without reverse edges.
    Contract:
        - Unknown dependency ids appear in direct_dependencies.
        - No state is created for the unknown dependency.
        - Root lineage is marked dirty.
    Returns:
        None.
    Raises:
        AssertionError: If unknown dependency tracking is incorrect.
    """
    frame = AethericFrame(Aether(), "component-states-unknown-dep")
    states = frame.spell_system_states
    root_index = _register_lineage(states, "root-unknown-dep")
    states.consume_dirty_lineages()
    try:
        states.update_dependencies(root_index, ["missing-dep-id"])
        root_state = states.get_by_index_id(root_index.id)
        assert root_state is not None
        assert "missing-dep-id" in root_state.direct_dependencies
        assert states.get_by_spell_id("missing-dep-id") is None
        dirty = set(states.consume_dirty_lineages())
        assert root_index.id in dirty
    finally:
        frame.cleanup()


def test_component_spell_system_states_impact_closure_handles_cycle() -> None:
    """
    Purpose:
        Validate impact closure terminates on cyclic dependency graphs.
    Contract:
        - Impacted set includes both nodes in the cycle.
        - Non-root nodes are marked transitively dirty.
    Returns:
        None.
    Raises:
        AssertionError: If closure does not handle cycles correctly.
    """
    frame = AethericFrame(Aether(), "component-states-cycle")
    states = frame.spell_system_states
    index_a = _register_lineage(states, "spell-cycle-a")
    index_b = _register_lineage(states, "spell-cycle-b")
    states.update_dependencies(index_a, [index_b.current])
    states.update_dependencies(index_b, [index_a.current])
    states.consume_dirty_lineages()
    states.mark_structural_change(index_a)
    impacted = states.compute_impact_closure([index_a.id])
    try:
        assert impacted == {index_a.id, index_b.id}
        state_a = states.get_by_index_id(index_a.id)
        state_b = states.get_by_index_id(index_b.id)
        assert state_a is not None
        assert state_b is not None
        assert state_a.transitively_dirty is False
        assert state_b.transitively_dirty is True
        assert state_b.change_reason is SpellStateChangeReason.dependency_changed
        assert SpellState.impacted_by_dependency in state_b.flags
    finally:
        frame.cleanup()


def test_component_spell_system_states_clear_dirty_preserves_non_topology_flags() -> None:
    """
    Purpose:
        Validate clear_dirty does not remove non-topology flags.
    Contract:
        - Ops/contract/mutation flags remain after clear_dirty.
        - Topology flags are removed.
    Returns:
        None.
    Raises:
        AssertionError: If non-topology flags are cleared.
    """
    frame = AethericFrame(Aether(), "component-states-flag-persist")
    states = frame.spell_system_states
    index = _register_lineage(states, "spell-flag-persist")
    try:
        state = states.get_by_index_id(index.id)
        assert state is not None
        state.set_validity(
            SpellValidity.gated,
            change_reason=SpellStateChangeReason.contract_violation,
            flags_to_add=[
                SpellState.has_open_incident,
                SpellState.contract_violation,
                SpellState.mutation_failed,
            ],
        )
        state.mark_dependency_change()
        state.clear_dirty(last_validated_at=456.0)
        flags = state.flags
        assert SpellState.has_open_incident in flags
        assert SpellState.contract_violation in flags
        assert SpellState.mutation_failed in flags
        assert SpellState.new_lineage not in flags
        assert SpellState.structure_changed not in flags
        assert SpellState.dependencies_changed not in flags
        assert SpellState.impacted_by_dependency not in flags
    finally:
        frame.cleanup()

