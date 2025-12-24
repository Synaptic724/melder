from melder.aether.aetheric_frame import AethericFrame
from melder.aether.dev_ops.change_control_manager.change_control_manager import (
    ChangeControlManager,
)
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


def test_component_change_control_rebuild_component_of_maps_root_and_dependency() -> None:
    """
    Purpose:
        Validate component-of mapping from real root blueprints.
    Contract:
        - Root spell ids map to themselves.
        - Dependency spell ids map back to the root.
    Returns:
        None.
    Raises:
        AssertionError: If component-of mappings are missing.
    """
    frame = AethericFrame("component-ccm-mapping")
    states = frame.spell_system_states
    root_id = "root-ccm"
    dep_id = "dep-ccm"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    manager = ChangeControlManager(states)
    blueprints: dict[str, object] = {}
    try:
        blueprints = _build_root_blueprints(states)
        manager.rebuild_component_of(blueprints)
        info = manager.describe()
        component_of = info["component_of"]
        assert component_of[root_id] == {root_id}
        assert component_of[dep_id] == {root_id}
    finally:
        _cleanup_blueprints(blueprints)
        manager.cleanup()
        frame.cleanup()


def test_component_change_control_includes_deep_dependencies() -> None:
    """
    Purpose:
        Validate deep dependencies are attributed to the root.
    Contract:
        - Leaf nodes map to the root spell id in component_of.
    Returns:
        None.
    Raises:
        AssertionError: If deep dependencies are not mapped.
    """
    frame = AethericFrame("component-ccm-deep")
    states = frame.spell_system_states
    root_id = "root-deep"
    mid_id = "mid-deep"
    leaf_id = "leaf-deep"
    root_index = _register_lineage(states, root_id)
    mid_index = _register_lineage(states, mid_id)
    _register_lineage(states, leaf_id)
    states.update_dependencies(root_index, [mid_id])
    states.update_dependencies(mid_index, [leaf_id])

    manager = ChangeControlManager(states)
    blueprints: dict[str, object] = {}
    try:
        blueprints = _build_root_blueprints(states)
        manager.rebuild_component_of(blueprints)
        component_of = manager.describe()["component_of"]
        assert component_of[root_id] == {root_id}
        assert component_of[mid_id] == {root_id}
        assert component_of[leaf_id] == {root_id}
    finally:
        _cleanup_blueprints(blueprints)
        manager.cleanup()
        frame.cleanup()


def test_component_change_control_revalidate_dirty_roots_uses_blueprint_roots() -> None:
    """
    Purpose:
        Validate revalidation clears dirty roots derived from blueprints.
    Contract:
        - notify_spell_changed marks the root dirty.
        - revalidate_dirty_roots invokes the registered revalidator.
        - Dirty roots are cleared after revalidation.
    Returns:
        None.
    Raises:
        AssertionError: If dirty roots are not cleared.
    """
    frame = AethericFrame("component-ccm-revalidate")
    states = frame.spell_system_states
    root_id = "root-revalidate"
    dep_id = "dep-revalidate"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    manager = ChangeControlManager(states)
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
        manager.rebuild_component_of(blueprints)
        manager.set_revalidator(_revalidate)

        manager.notify_spell_changed(dep_id)
        assert manager.is_root_dirty(root_id) is True

        manager.revalidate_dirty_roots()
        assert calls == [{root_id}]
        info = manager.describe()
        assert info["dirty_roots"] == set()
        assert info["monitor_active"] is False
    finally:
        _cleanup_blueprints(blueprints)
        manager.cleanup()
        frame.cleanup()
