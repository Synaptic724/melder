from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)


def _register_index(states, spell_id: str) -> SpellIndex:
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
    states.register_index(index)
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


def _build_collection_topology(spell_id: str, frame_key: str) -> SpellLocalTopology:
    """
    Purpose:
        Build a topology with one collection DI socket.
    Contract:
        - The socket is NORMAL and collection-shaped.
        - dependency_key carries the supplied frame key.
    Args:
        spell_id: Owning spell id for the topology.
        frame_key: Collection frame key to record.
    Returns:
        SpellLocalTopology: The constructed topology.
    """
    return SpellLocalTopology(
        spell_id=spell_id,
        sockets=(
            SpellSocketDescriptor(
                spell_id=spell_id,
                param_name="services",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=True,
                is_optional=False,
                target_spell_ids=(),
                dependency_key=(frame_key, "__default__"),
            ),
        ),
    )


def _build_contract_topology(spell_id: str, frame_key: str, binding_key: str) -> SpellLocalTopology:
    """
    Purpose:
        Build a topology with one spell-contract socket.
    Contract:
        - The socket is SPELL_CONTRACT-shaped.
        - contract_key carries the supplied frame and binding keys.
    Args:
        spell_id: Owning spell id for the topology.
        frame_key: Contract frame key to record.
        binding_key: Contract binding key to record.
    Returns:
        SpellLocalTopology: The constructed topology.
    """
    return SpellLocalTopology(
        spell_id=spell_id,
        sockets=(
            SpellSocketDescriptor(
                spell_id=spell_id,
                param_name="service",
                position=0,
                socket_kind=SocketKind.SPELL_CONTRACT,
                is_collection=False,
                is_optional=False,
                target_spell_ids=(),
                contract_key=(frame_key, binding_key),
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
    root_index = _register_index(states, root_id)
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
    root_index = _register_index(states, root_id)
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
    root_index = _register_index(states, root_id)
    topology = _build_topology(root_id, dep_id)
    states.register_local_topology(root_index, topology)
    frame.cleanup()
    assert topology.cleaned is True
    assert states.cleaned is True


def test_component_spell_system_states_register_index_sets_change_reason() -> None:
    """
    Purpose:
        Validate registering a lineage sets validity and change reason.
    Contract:
        - New lineages are gated with register_or_rebind as the change reason.
        - Structure and new_index flags are present.
    Returns:
        None.
    Raises:
        AssertionError: If change-reason or flags are missing.
    """
    frame = AethericFrame(Aether(), "component-states-register-flags")
    states = frame.spell_system_states
    index = _register_index(states, "spell-register-flags")
    try:
        state = states.get_by_index_id(index.id)
        assert state is not None
        assert state.validity is SpellValidity.gated
        assert state.change_reason is SpellStateChangeReason.register_or_rebind
        flags = state.flags
        assert SpellState.structure_changed in flags
        assert SpellState.new_index in flags
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
    root_index = _register_index(states, "root-dep-reason")
    dep_index = _register_index(states, "dep-dep-reason")
    states.update_dependencies(root_index, [dep_index.selected_spell_id])
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
        - register_index updates the current spell id on the existing state.
        - get_by_spell_id resolves the updated current id.
        - change_reason remains register_or_rebind after rebind.
    Returns:
        None.
    Raises:
        AssertionError: If the spell-id index is not refreshed.
    """
    frame = AethericFrame(Aether(), "component-states-rebind")
    states = frame.spell_system_states
    index = _register_index(states, "spell-rebind-v1")
    try:
        state = states.get_by_index_id(index.id)
        assert state is not None
        assert state.current_spell_id == "spell-rebind-v1"

        index.update("spell-rebind-v2")
        states.register_index(index)

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
    root_index = _register_index(states, "root-impact-closure")
    dep_index = _register_index(states, "dep-impact-closure")
    states.update_dependencies(dep_index, [root_index.selected_spell_id])
    states.consume_dirty_indexes()
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
        dirty = set(states.consume_dirty_indexes())
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
    index = _register_index(states, "spell-structural-dirty")
    states.consume_dirty_indexes()
    try:
        states.mark_structural_change(index)
        dirty = set(states.consume_dirty_indexes())
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
    root_index = _register_index(states, "root-reverse-edges")
    dep_index = _register_index(states, "dep-reverse-edges")
    states.consume_dirty_indexes()
    try:
        states.update_dependencies(root_index, [dep_index.selected_spell_id])
        root_state = states.get_by_index_id(root_index.id)
        dep_state = states.get_by_index_id(dep_index.id)
        assert root_state is not None
        assert dep_state is not None
        assert dep_index.selected_spell_id in root_state.direct_dependencies
        assert root_index.id in dep_state.direct_dependents
        assert root_state.change_reason is SpellStateChangeReason.dependencies_changed
        assert SpellState.dependencies_changed in root_state.flags

        states.update_dependencies(root_index, [])
        dep_state = states.get_by_index_id(dep_index.id)
        assert dep_state is not None
        assert root_index.id not in dep_state.direct_dependents
    finally:
        frame.cleanup()


def test_component_spell_system_states_consume_dirty_indexes_clears() -> None:
    """
    Purpose:
        Validate consume_dirty_indexes clears the dirty queue.
    Contract:
        - Registered lineages appear in the dirty list.
        - consume_dirty_indexes clears the queue after read.
    Returns:
        None.
    Raises:
        AssertionError: If the dirty queue is not cleared.
    """
    frame = AethericFrame(Aether(), "component-states-consume-dirty")
    states = frame.spell_system_states
    index_a = _register_index(states, "spell-dirty-a")
    index_b = _register_index(states, "spell-dirty-b")
    try:
        dirty = set(states.consume_dirty_indexes())
        assert index_a.id in dirty
        assert index_b.id in dirty
        assert states.consume_dirty_indexes() == []
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
    index = _register_index(states, "spell-state-cleanup")
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
    root_index = _register_index(states, "root-clear-dirty")
    dep_index = _register_index(states, "dep-clear-dirty")
    states.update_dependencies(root_index, [dep_index.selected_spell_id])
    try:
        state = states.get_by_index_id(root_index.id)
        assert state is not None
        state.clear_dirty(last_validated_at=123.0)
        assert state.validity is SpellValidity.valid
        assert state.dirty is False
        assert state.last_validated_at == 123.0
        flags = state.flags
        assert SpellState.new_index not in flags
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
    index = _register_index(states, "spell-rebind-old-id")
    try:
        state = states.get_by_index_id(index.id)
        assert state is not None
        index.update("spell-rebind-new-id")
        states.register_index(index)
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
    root_index = _register_index(states, "root-unknown-dep")
    states.consume_dirty_indexes()
    try:
        states.update_dependencies(root_index, ["missing-dep-id"])
        root_state = states.get_by_index_id(root_index.id)
        assert root_state is not None
        assert "missing-dep-id" in root_state.direct_dependencies
        assert states.get_by_spell_id("missing-dep-id") is None
        dirty = set(states.consume_dirty_indexes())
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
    index_a = _register_index(states, "spell-cycle-a")
    index_b = _register_index(states, "spell-cycle-b")
    states.update_dependencies(index_a, [index_b.selected_spell_id])
    states.update_dependencies(index_b, [index_a.selected_spell_id])
    states.consume_dirty_indexes()
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
    index = _register_index(states, "spell-flag-persist")
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
        assert SpellState.new_index not in flags
        assert SpellState.structure_changed not in flags
        assert SpellState.dependencies_changed not in flags
        assert SpellState.impacted_by_dependency not in flags
    finally:
        frame.cleanup()


def test_component_spell_system_states_register_local_topology_builds_collection_dependents_index() -> None:
    """
    Purpose:
        Validate collection topologies feed the spellbook-scoped collection index.
    Contract:
        - mark_collection_dependents_dirty marks the owner lineage for the matching frame key.
    Returns:
        None.
    Raises:
        AssertionError: If collection-dependent indexing is missing.
    """
    frame = AethericFrame(Aether(), "component-states-collection-index")
    states = frame.spell_system_states
    index = SpellIndex("spell-collection-index")
    index._owner_spellbook = type("SpellbookStub", (), {"_id": "spellbook-1"})()
    states.register_index(index)
    topology = _build_collection_topology("spell-collection-index", "svc")
    states.register_local_topology(index, topology)
    states.consume_dirty_indexes()
    try:
        impacted = states.mark_collection_dependents_dirty(
            spellbook_id="spellbook-1",
            frame_keys={"svc"},
        )
        assert impacted == {index.id}
        state = states.get_by_index_id(index.id)
        assert state is not None
        assert SpellState.dependencies_changed in state.flags
    finally:
        frame.cleanup()


def test_component_spell_system_states_register_local_topology_builds_contract_dependents_index() -> None:
    """
    Purpose:
        Validate contract topologies feed the spellbook-scoped contract index.
    Contract:
        - mark_contract_dependents_dirty marks the owner lineage for the matching contract key.
    Returns:
        None.
    Raises:
        AssertionError: If contract-dependent indexing is missing.
    """
    frame = AethericFrame(Aether(), "component-states-contract-index")
    states = frame.spell_system_states
    index = SpellIndex("spell-contract-index")
    index._owner_spellbook = type("SpellbookStub", (), {"_id": "spellbook-1"})()
    states.register_index(index)
    topology = _build_contract_topology("spell-contract-index", "svc", "primary")
    states.register_local_topology(index, topology)
    states.consume_dirty_indexes()
    try:
        impacted = states.mark_contract_dependents_dirty(
            spellbook_id="spellbook-1",
            contract_keys={("svc", "primary")},
        )
        assert impacted == {index.id}
        state = states.get_by_index_id(index.id)
        assert state is not None
        assert SpellState.contract_unvalidated in state.flags
        assert state.change_reason is SpellStateChangeReason.contract_unvalidated
    finally:
        frame.cleanup()


def test_component_spell_system_states_mark_contract_dependents_dirty_without_keys_marks_all_for_spellbook() -> None:
    """
    Purpose:
        Validate missing contract-key filters mark every contract consumer in the spellbook scope.
    Contract:
        - All registered contract consumers in the spellbook bucket are impacted.
    Returns:
        None.
    Raises:
        AssertionError: If some contract consumers are skipped.
    """
    frame = AethericFrame(Aether(), "component-states-contract-all")
    states = frame.spell_system_states
    index_a = SpellIndex("spell-contract-all-a")
    index_b = SpellIndex("spell-contract-all-b")
    spellbook_stub = type("SpellbookStub", (), {"_id": "spellbook-1"})()
    index_a._owner_spellbook = spellbook_stub
    index_b._owner_spellbook = spellbook_stub
    states.register_index(index_a)
    states.register_index(index_b)
    states.register_local_topology(
        index_a,
        _build_contract_topology("spell-contract-all-a", "svc", "primary"),
    )
    states.register_local_topology(
        index_b,
        _build_contract_topology("spell-contract-all-b", "svc", "secondary"),
    )
    states.consume_dirty_indexes()
    try:
        impacted = states.mark_contract_dependents_dirty(
            spellbook_id="spellbook-1",
            contract_keys=None,
        )
        assert impacted == {index_a.id, index_b.id}
    finally:
        frame.cleanup()


def test_component_spell_system_states_drop_conduit_resolution_state_cleans_removed_state() -> None:
    """
    Purpose:
        Validate dropping conduit resolution state removes and cleans the bucket.
    Contract:
        - Removed conduit state is cleaned and no longer retrievable.
    Returns:
        None.
    Raises:
        AssertionError: If conduit resolution state survives drop.
    """
    frame = AethericFrame(Aether(), "component-states-drop-conduit")
    states = frame.spell_system_states
    state = states.get_or_create_conduit_resolution_state("conduit-1")
    try:
        states.drop_conduit_resolution_state("conduit-1")
        assert state.cleaned is True
        assert states.get_conduit_resolution_state("conduit-1") is None
    finally:
        frame.cleanup()


def test_component_spell_system_states_set_risk_manager_propagates_to_existing_states() -> None:
    """
    Purpose:
        Validate setting the risk manager propagates to already-created child states.
    Contract:
        - Existing spell-index and conduit-resolution states receive the same risk manager reference.
    Returns:
        None.
    Raises:
        AssertionError: If risk manager propagation is incomplete.
    """
    frame = AethericFrame(Aether(), "component-states-risk-manager")
    states = frame.spell_system_states
    index = _register_index(states, "spell-risk-manager")
    spell_state = states.get_by_index_id(index.id)
    conduit_state = states.get_or_create_conduit_resolution_state("conduit-1")
    risk_manager = frame.dev_ops_manager.risk_manager
    try:
        states.set_risk_manager(risk_manager)
        assert spell_state is not None
        assert spell_state._risk_manager is risk_manager
        assert conduit_state._risk_manager is risk_manager
    finally:
        frame.cleanup()


def test_component_spell_system_states_bulk_set_conduit_validity_round_trip() -> None:
    """
    Purpose:
        Validate bulk conduit spell/root validity publishing through the live registry.
    Contract:
        - Bulk spell and root validity writes are readable through the conduit bucket.
        - clear_conduit_dirty resets the dirty marker after validation.
    Returns:
        None.
    Raises:
        AssertionError: If conduit validity round-trip fails.
    """
    frame = AethericFrame(Aether(), "component-states-conduit-validity")
    states = frame.spell_system_states
    try:
        states.bulk_set_conduit_spell_validity(
            "conduit-1",
            {"spell-a": SpellValidity.valid, "spell-b": SpellValidity.gated},
        )
        states.bulk_set_conduit_root_validity(
            "conduit-1",
            {"root-a": SpellValidity.valid},
        )
        state = states.get_conduit_resolution_state("conduit-1")
        assert state is not None
        assert state.get_spell_validity("spell-a") is SpellValidity.valid
        assert state.get_spell_validity("spell-b") is SpellValidity.gated
        assert state.get_root_validity("root-a") is SpellValidity.valid
        assert state.is_dirty() is True
        states.clear_conduit_dirty("conduit-1", 10.0)
        assert state.is_dirty() is False
    finally:
        frame.cleanup()



