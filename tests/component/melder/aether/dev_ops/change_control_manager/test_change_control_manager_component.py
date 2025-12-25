import pytest

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
from melder.utilities.custom_exceptions.operation_cancelled_error import (
    OperationCancelledError,
)
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEventSignal,
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


def test_component_change_control_pending_change_round_trip() -> None:
    """
    Purpose:
        Validate pending-change metadata round-trips through real components.
    Contract:
        - register_pending_change stores the reason and metadata.
        - get_pending_change returns a snapshot copy.
        - list_pending_changes includes the entry.
        - clear_pending_change removes it.
    Returns:
        None.
    Raises:
        AssertionError: If pending-change tracking is incorrect.
    """
    frame = AethericFrame("component-ccm-pending")
    states = frame.spell_system_states
    manager = frame.dev_ops_manager.change_control_manager
    index = SpellIndex("spell-pending-change")
    states.register_lineage(index, object())
    try:
        manager.register_pending_change(
            index,
            reason="rebinding",
            metadata={"ticket": "T-100"},
        )
        entry = manager.get_pending_change(index.id)
        assert entry is not None
        assert entry["reason"] == "rebinding"
        assert entry["ticket"] == "T-100"
        snapshot = manager.list_pending_changes()
        assert index.id in snapshot

        entry["ticket"] = "mutated"
        fresh = manager.get_pending_change(index.id)
        assert fresh is not None
        assert fresh["ticket"] == "T-100"

        manager.clear_pending_change(index.id)
        assert manager.get_pending_change(index.id) is None
    finally:
        frame.cleanup()


def test_component_change_control_notify_unknown_spell_tracks_dirty() -> None:
    """
    Purpose:
        Validate unknown spell ids are tracked as dirty with monitoring active.
    Contract:
        - notify_spell_changed records the spell id in dirty_spells.
        - dirty_roots remains empty when no component_of mapping exists.
        - monitor_active is True after notification.
    Returns:
        None.
    Raises:
        AssertionError: If dirty tracking is incorrect.
    """
    frame = AethericFrame("component-ccm-unknown")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        manager.notify_spell_changed("ghost-spell")
        info = manager.describe()
        assert "ghost-spell" in info["dirty_spells"]
        assert info["dirty_roots"] == set()
        assert info["monitor_active"] is True
    finally:
        frame.cleanup()


def test_component_change_control_revalidate_dirty_roots_failure_keeps_dirty() -> None:
    """
    Purpose:
        Validate dirty roots remain when revalidation fails.
    Contract:
        - revalidate_dirty_roots propagates the revalidator exception.
        - dirty roots stay marked after failure.
        - monitor_active remains True.
    Returns:
        None.
    Raises:
        AssertionError: If dirty roots are cleared after failure.
    """
    frame = AethericFrame("component-ccm-revalidate-failure")
    states = frame.spell_system_states
    root_id = "root-ccm-failure"
    dep_id = "dep-ccm-failure"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    manager = frame.dev_ops_manager.change_control_manager
    blueprints: dict[str, object] = {}

    def _revalidate(_dirty_roots, _cancel_event) -> None:
        raise RuntimeError("revalidate failed")

    try:
        blueprints = _build_root_blueprints(states)
        manager.rebuild_component_of(blueprints)
        manager.set_revalidator(_revalidate)

        manager.notify_spell_changed(dep_id)
        assert manager.is_root_dirty(root_id) is True

        with pytest.raises(RuntimeError, match="revalidate failed"):
            manager.revalidate_dirty_roots()

        info = manager.describe()
        assert root_id in info["dirty_roots"]
        assert info["monitor_active"] is True
    finally:
        _cleanup_blueprints(blueprints)
        frame.cleanup()


def test_component_change_control_revalidate_dirty_roots_no_revalidator_noop() -> None:
    """
    Purpose:
        Validate revalidation is a no-op when no revalidator is registered.
    Contract:
        - Dirty roots remain marked when revalidate_dirty_roots is called without a hook.
        - monitor_active remains True.
    Returns:
        None.
    Raises:
        AssertionError: If dirty roots are cleared without a revalidator.
    """
    frame = AethericFrame("component-ccm-revalidate-no-hook")
    states = frame.spell_system_states
    root_id = "root-ccm-no-hook"
    dep_id = "dep-ccm-no-hook"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    manager = frame.dev_ops_manager.change_control_manager
    blueprints: dict[str, object] = {}

    try:
        blueprints = _build_root_blueprints(states)
        manager.rebuild_component_of(blueprints)
        manager.notify_spell_changed(dep_id)
        assert manager.is_root_dirty(root_id) is True

        manager.revalidate_dirty_roots()
        info = manager.describe()
        assert root_id in info["dirty_roots"]
        assert info["monitor_active"] is True
    finally:
        _cleanup_blueprints(blueprints)
        frame.cleanup()


def test_component_change_control_revalidate_dirty_roots_respects_cancellation() -> None:
    """
    Purpose:
        Validate cancellation aborts revalidation before the callback runs.
    Contract:
        - cancel_event throws before revalidator is called.
        - dirty roots remain marked and monitoring stays active.
    Returns:
        None.
    Raises:
        AssertionError: If cancellation does not abort the revalidation.
    """
    frame = AethericFrame("component-ccm-cancel")
    states = frame.spell_system_states
    root_id = "root-ccm-cancel"
    dep_id = "dep-ccm-cancel"
    root_index = _register_lineage(states, root_id)
    _register_lineage(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    manager = frame.dev_ops_manager.change_control_manager
    blueprints: dict[str, object] = {}
    calls: list[set[str]] = []

    def _revalidate(dirty_roots: set[str], _cancel_event) -> None:
        calls.append(set(dirty_roots))

    signal = CancellationEventSignal()

    try:
        blueprints = _build_root_blueprints(states)
        manager.rebuild_component_of(blueprints)
        manager.set_revalidator(_revalidate)
        manager.notify_spell_changed(dep_id)
        assert manager.is_root_dirty(root_id) is True

        signal.cancel()
        with pytest.raises(OperationCancelledError):
            manager.revalidate_dirty_roots(cancel_event=signal.event)

        assert calls == []
        info = manager.describe()
        assert root_id in info["dirty_roots"]
        assert info["monitor_active"] is True
    finally:
        signal.cleanup()
        _cleanup_blueprints(blueprints)
        frame.cleanup()
