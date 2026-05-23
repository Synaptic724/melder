from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_compiler.system.spell_system_adjacency_builder import (
    SpellSystemAdjacencyBuilder,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_root_blueprint_builder import (
    SpellSystemRootBlueprintBuilder,
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


def _build_root_blueprints(states) -> dict[str, object]:
    """
    Purpose:
        Build root blueprints from the current SpellSystemStates snapshot.
    Contract:
        - Returns a mapping keyed by root spell id.
    Args:
        states: SpellSystemStates registry to snapshot.
    Returns:
        dict[str, RootResolutionBlueprint]: Root blueprint mapping.
    """
    snapshot = SpellSystemAdjacencyBuilder.build(states)
    return SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)


def _cleanup_blueprints(blueprints: dict[str, object]) -> None:
    """
    Purpose:
        Deterministically clean RootResolutionBlueprint objects.
    Contract:
        - Invokes cleanup on each blueprint in the mapping.
    Args:
        blueprints: Mapping of root ids to RootResolutionBlueprint objects.
    Returns:
        None.
    """
    for blueprint in blueprints.values():
        blueprint.cleanup()


def test_component_dev_ops_revalidate_dirty_roots_clears_change_control_state() -> None:
    """
    Purpose:
        Validate DevOpsManager revalidation clears dirty roots via ChangeControlManager.
    Contract:
        - notify_spell_changed marks the root dirty.
        - revalidate_dirty_roots delegates to the registered revalidator.
        - Dirty roots are cleared after successful revalidation.
    Returns:
        None.
    Raises:
        AssertionError: If dirty roots are not cleared.
    """
    frame = AethericFrame(Aether(), "component-devops-revalidate")
    states = frame.spell_system_states
    devops = frame.dev_ops_manager
    root_id = "root-devops"
    dep_id = "dep-devops"
    conduit_id = "conduit-1"
    root_index = _register_index(states, root_id)
    _register_index(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    calls: list[set[str]] = []
    blueprints: dict[str, object] = {}

    def _revalidate(dirty_roots: set[str], _cancel_event) -> None:
        """
        Purpose:
            Capture dirty root ids passed by ChangeControlManager.
        Contract:
            - Appends the dirty_roots set for assertions.
        Args:
            dirty_roots: Root ids marked dirty by change control.
            _cancel_event: Optional cancellation event (unused).
        Returns:
            None.
        """
        calls.append(set(dirty_roots))

    try:
        blueprints = _build_root_blueprints(states)
        devops.change_control_manager.rebuild_component_of(conduit_id, blueprints)
        devops.change_control_manager.set_revalidator(conduit_id, _revalidate)

        devops.change_control_manager.notify_spell_changed(dep_id)
        assert devops.change_control_manager.is_root_dirty(conduit_id, root_id) is True

        devops.revalidate_dirty_roots(conduit_id)
        info = devops.change_control_manager.describe()
        assert calls == [{root_id}]
        assert info["dirty_roots_by_conduit"][conduit_id] == set()
        assert info["monitor_active_by_conduit"][conduit_id] is False
    finally:
        _cleanup_blueprints(blueprints)
        frame.cleanup()


def test_component_dev_ops_cleanup_cleans_children_and_states() -> None:
    """
    Purpose:
        Validate DevOpsManager cleanup cascades to child managers and states.
    Contract:
        - IncidentManager and ChangeControlManager are cleaned.
        - SpellSystemStates are cleaned and gated entries are cleared.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not cascade properly.
    """
    frame = AethericFrame(Aether(), "component-devops-cleanup")
    devops = frame.dev_ops_manager
    states = devops.spell_system_states
    incident_manager = devops.incident_manager
    change_control = devops.change_control_manager

    index = _register_index(states, "spell-cleanup")
    state = states.get_by_index_id(index.id)
    assert state is not None
    assert state.validity is SpellValidity.gated

    incident = incident_manager.create_incident(
        kind="cleanup",
        summary="cleanup incident",
        severity=IncidentSeverity.info,
    )
    try:
        devops.cleanup()
        assert incident_manager.cleaned is True
        assert change_control.cleaned is True
        assert states.cleaned is True
        assert incident.cleaned is True
    finally:
        frame.cleanup()


def test_component_dev_ops_properties_expose_frame_owned_surfaces() -> None:
    """
    Purpose:
        Validate DevOpsManager property accessors expose stable frame-owned surfaces.
    Contract:
        - incident_manager, change_control_manager, risk_manager, creation_gate_controller,
          devops_information_registry, and spell_system_states are stable references.
    Returns:
        None.
    Raises:
        AssertionError: If property accessors drift from frame-owned objects.
    """
    frame = AethericFrame(Aether(), "component-devops-properties")
    devops = frame.dev_ops_manager
    try:
        assert devops.incident_manager is devops.incident_manager
        assert devops.change_control_manager is devops.change_control_manager
        assert devops.risk_manager is devops.risk_manager
        assert devops.creation_gate_controller is devops.creation_gate_controller
        assert devops.devops_information_registry is frame.devops_information_registry
        assert devops.spell_system_states is frame.spell_system_states
    finally:
        frame.cleanup()


def test_component_dev_ops_enable_conduit_gate_noops_for_unknown_gate() -> None:
    """
    Purpose:
        Validate enabling a missing conduit gate is a no-op.
    Contract:
        - Missing gate lookups do not raise.
    Returns:
        None.
    Raises:
        AssertionError: If missing gates raise.
    """
    frame = AethericFrame(Aether(), "component-devops-enable-missing")
    devops = frame.dev_ops_manager
    try:
        devops.enable_conduit_gate("missing-conduit")
    finally:
        frame.cleanup()


def test_component_dev_ops_disable_conduit_gate_noops_for_unknown_gate() -> None:
    """
    Purpose:
        Validate disabling a missing conduit gate is a no-op.
    Contract:
        - Missing gate lookups do not raise.
    Returns:
        None.
    Raises:
        AssertionError: If missing gates raise.
    """
    frame = AethericFrame(Aether(), "component-devops-disable-missing")
    devops = frame.dev_ops_manager
    try:
        devops.disable_conduit_gate("missing-conduit")
    finally:
        frame.cleanup()


def test_component_dev_ops_enable_conduit_gate_opens_registered_gate() -> None:
    """
    Purpose:
        Validate enable_conduit_gate opens a real registered gate.
    Contract:
        - Registered conduit gates are reopened through the facade.
    Returns:
        None.
    Raises:
        AssertionError: If enable_conduit_gate does not open the gate.
    """
    frame = AethericFrame(Aether(), "component-devops-enable-gate")
    devops = frame.dev_ops_manager
    controller = devops.creation_gate_controller
    gate = controller.create_conduit_gate("conduit-1", root_conduit_id="root-1")
    try:
        gate.close()
        assert gate.enabled is False
        devops.enable_conduit_gate("conduit-1")
        assert gate.enabled is True
    finally:
        frame.cleanup()


def test_component_dev_ops_disable_conduit_gate_closes_registered_gate() -> None:
    """
    Purpose:
        Validate disable_conduit_gate closes a real registered gate.
    Contract:
        - Registered conduit gates are closed through the facade.
    Returns:
        None.
    Raises:
        AssertionError: If disable_conduit_gate does not close the gate.
    """
    frame = AethericFrame(Aether(), "component-devops-disable-gate")
    devops = frame.dev_ops_manager
    controller = devops.creation_gate_controller
    gate = controller.create_conduit_gate("conduit-1", root_conduit_id="root-1")
    try:
        assert gate.enabled is True
        devops.disable_conduit_gate("conduit-1")
        assert gate.enabled is False
    finally:
        frame.cleanup()


def test_component_dev_ops_enable_conduit_lineage_opens_all_registered_gates() -> None:
    """
    Purpose:
        Validate enable_conduit_lineage reopens every gate in a lineage snapshot.
    Contract:
        - All lineage gates transition to enabled through the facade.
    Returns:
        None.
    Raises:
        AssertionError: If lineage gates remain closed.
    """
    frame = AethericFrame(Aether(), "component-devops-enable-lineage")
    devops = frame.dev_ops_manager
    controller = devops.creation_gate_controller
    gate_a = controller.create_conduit_gate("conduit-a", root_conduit_id="root-1")
    gate_b = controller.create_conduit_gate("conduit-b", root_conduit_id="root-1")
    try:
        gate_a.close()
        gate_b.close()
        devops.enable_conduit_lineage("root-1")
        assert gate_a.enabled is True
        assert gate_b.enabled is True
    finally:
        frame.cleanup()


def test_component_dev_ops_disable_conduit_lineage_closes_all_registered_gates() -> None:
    """
    Purpose:
        Validate disable_conduit_lineage closes every gate in a lineage snapshot.
    Contract:
        - All lineage gates transition to disabled through the facade.
    Returns:
        None.
    Raises:
        AssertionError: If lineage gates remain open.
    """
    frame = AethericFrame(Aether(), "component-devops-disable-lineage")
    devops = frame.dev_ops_manager
    controller = devops.creation_gate_controller
    gate_a = controller.create_conduit_gate("conduit-a", root_conduit_id="root-1")
    gate_b = controller.create_conduit_gate("conduit-b", root_conduit_id="root-1")
    try:
        devops.disable_conduit_lineage("root-1")
        assert gate_a.enabled is False
        assert gate_b.enabled is False
    finally:
        frame.cleanup()


def test_component_dev_ops_close_and_wait_conduit_terminally_closes_gate() -> None:
    """
    Purpose:
        Validate close_and_wait_conduit terminally closes a registered gate.
    Contract:
        - The gate is terminally closed after drain completes.
    Returns:
        None.
    Raises:
        AssertionError: If the gate is not terminally closed.
    """
    frame = AethericFrame(Aether(), "component-devops-close-conduit")
    devops = frame.dev_ops_manager
    controller = devops.creation_gate_controller
    gate = controller.create_conduit_gate("conduit-1", root_conduit_id="root-1")
    try:
        devops.close_and_wait_conduit("conduit-1", timeout=0.01, interval=0.001)
        assert gate.is_closed() is True
    finally:
        frame.cleanup()


def test_component_dev_ops_close_and_wait_conduit_lineage_terminally_closes_all_gates() -> None:
    """
    Purpose:
        Validate close_and_wait_conduit_lineage terminally closes every gate in the lineage.
    Contract:
        - All lineage gates are terminally closed after drain completes.
    Returns:
        None.
    Raises:
        AssertionError: If any lineage gate stays open.
    """
    frame = AethericFrame(Aether(), "component-devops-close-lineage")
    devops = frame.dev_ops_manager
    controller = devops.creation_gate_controller
    gate_a = controller.create_conduit_gate("conduit-a", root_conduit_id="root-1")
    gate_b = controller.create_conduit_gate("conduit-b", root_conduit_id="root-1")
    try:
        devops.close_and_wait_conduit_lineage("root-1", timeout=0.01, interval=0.001)
        assert gate_a.is_closed() is True
        assert gate_b.is_closed() is True
    finally:
        frame.cleanup()



