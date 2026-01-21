from melder.aether.aetheric_frame import AethericFrame
from melder.aether.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.spell_crafter.system.spell_system_adjacency_builder import (
    SpellSystemAdjacencyBuilder,
)
from melder.spellbook.spell_crafter.system.spell_system_root_blueprint_builder import (
    SpellSystemRootBlueprintBuilder,
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
    frame = AethericFrame("component-devops-revalidate")
    states = frame.spell_system_states
    devops = frame.dev_ops_manager
    root_id = "root-devops"
    dep_id = "dep-devops"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_id)
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
        devops.change_control_manager.rebuild_component_of(blueprints)
        devops.change_control_manager.set_revalidator(_revalidate)

        devops.change_control_manager.notify_spell_changed(dep_id)
        assert devops.change_control_manager.is_root_dirty(root_id) is True

        devops.revalidate_dirty_roots()
        info = devops.change_control_manager.describe()
        assert calls == [{root_id}]
        assert info["dirty_roots"] == set()
        assert info["monitor_active"] is False
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
    frame = AethericFrame("component-devops-cleanup")
    devops = frame.dev_ops_manager
    states = devops.spell_system_states
    incident_manager = devops.incident_manager
    change_control = devops.change_control_manager

    index = _register_lineage(states, "spell-cleanup")
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
