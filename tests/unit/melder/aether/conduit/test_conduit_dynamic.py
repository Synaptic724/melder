from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.creations.creations import Creations


def test_create_lesser_conduit_fires_hooks_and_links(
    conduit_normal: Conduit,
) -> None:
    """
    Verify create_lesser_conduit fires hooks and links the child conduit.

    Contract:
        - Pre, activated, and post hooks fire in order.
        - The conduit ward links the new lesser conduit.
        - The child shares the parent's spellbook and configuration.

    Args:
        conduit_normal (Conduit): Normal conduit used as the parent.

    Raises:
        AssertionError: If hook order or linking behavior is incorrect.
    """
    conduit_normal._conduit_ward = MagicMock()
    events: list[tuple[str, object]] = []

    def on_pre(parent: Conduit) -> None:
        """
        Record a pre-create hook event.

        Args:
            parent (Conduit): Parent conduit.

        Returns:
            None: Hook does not return a value.
        """
        events.append(("pre", parent))

    def on_activated(child: Conduit) -> None:
        """
        Record an activation hook event.

        Args:
            child (Conduit): Newly created child conduit.

        Returns:
            None: Hook does not return a value.
        """
        events.append(("activated", child))

    def on_post(parent: Conduit, child: Conduit) -> None:
        """
        Record a post-create hook event.

        Args:
            parent (Conduit): Parent conduit.
            child (Conduit): Newly created child conduit.

        Returns:
            None: Hook does not return a value.
        """
        events.append(("post", (parent, child)))

    conduit_normal._conduit_hooks = {
        "on_conduit_pre_created": [on_pre],
        "on_conduit_activated": [on_activated],
        "on_conduit_post_created": [on_post],
    }

    child = conduit_normal.create_lesser_conduit()
    try:
        conduit_normal._conduit_ward._link_lesser_conduit.assert_called_once_with(child)
        assert events[0] == ("pre", conduit_normal)
        assert events[1][0] == "activated"
        assert events[2][0] == "post"
        assert child._spellbook is conduit_normal._spellbook
        assert child._configuration is conduit_normal._configuration
        assert child._conduit_state == ConduitState.lesser
    finally:
        child.cleanup()


def test_nested_lesser_conduits_share_root_creations(
    conduit_normal: Conduit,
) -> None:
    """
    Verify nested lesser conduits inherit the root scope lineage.

    Contract:
        - Lesser conduits retain Creations managers and root lineage metadata.
        - Both lesser wards point back to the root conduit.
    """
    first = conduit_normal.create_lesser_conduit()
    second = first.create_lesser_conduit()
    try:
        assert isinstance(first._creations, Creations)
        assert isinstance(second._creations, Creations)
        assert first._root_conduit_id == conduit_normal._id
        assert second._root_conduit_id == conduit_normal._id
        assert first._meld._resolution_conduit_id == conduit_normal._id
        assert second._meld._resolution_conduit_id == conduit_normal._id
        assert first._conduit_ward.root_conduit is conduit_normal
        assert second._conduit_ward.root_conduit is conduit_normal
    finally:
        second.cleanup()
        first.cleanup()


def test_set_new_policy_raises_when_not_dynamic(conduit_normal: Conduit) -> None:
    """
    Verify set_new_policy is blocked in non-dynamic environments.

    Contract:
        - Non-dynamic conduits cannot change policies.

    Args:
        conduit_normal (Conduit): Normal conduit with dynamic disabled.

    Raises:
        AssertionError: If set_new_policy does not raise.
    """
    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal.set_new_policy("default")


def test_set_new_policy_delegates_for_dynamic(conduit_dynamic_normal: Conduit) -> None:
    """
    Verify set_new_policy delegates to the conduit ward in dynamic mode.

    Contract:
        - _set_new_policy is called with the provided value.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If delegation does not occur.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._nexus_publish_enabled = True
    conduit_dynamic_normal._nexus = MagicMock()

    conduit_dynamic_normal.set_new_policy("default")

    conduit_dynamic_normal._conduit_ward._set_new_policy.assert_called_once_with("default")
    conduit_dynamic_normal._nexus._publish_conduit_record.assert_called_once_with(
        conduit_dynamic_normal
    )


def test_conduit_exposes_get_conduit_cloud_surface(
    conduit_lesser: Conduit,
    conduit_normal: Conduit,
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify the public conduit cloud accessor remains available on the conduit surface.
    """
    for conduit in (conduit_lesser, conduit_normal, conduit_dynamic_normal):
        assert hasattr(conduit, "get_conduit_cloud")


def test_transfer_spell_ownership_raises_when_not_dynamic(
    conduit_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify transfer_spell_ownership is blocked in non-dynamic environments.

    Contract:
        - Dynamic mode is required for ownership transfer.

    Args:
        conduit_normal (Conduit): Normal conduit with dynamic disabled.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If transfer does not raise.
    """
    with pytest.raises(RuntimeError, match="Ownership transfer is disabled for the current frame posture|Ownership transfer requires dynamic mode"):
        conduit_normal.transfer_spell_ownership(
            spell="sha-1",
            target_conduit=conduit_lesser,
        )


def test_transfer_spell_ownership_raises_when_source_conduit_is_lesser(
    conduit_dynamic_lesser: Conduit,
    conduit_normal: Conduit,
) -> None:
    """
    Verify transfer_spell_ownership fails immediately for lesser conduits.

    Contract:
        - Lesser conduits are rejected before transaction or ward logic.
    """
    with pytest.raises(RuntimeError, match="Only normal conduits can transfer spell ownership"):
        conduit_dynamic_lesser.transfer_spell_ownership(
            spell="sha-1",
            target_conduit=conduit_normal,
        )


def test_get_mutation_research_raises_when_source_conduit_is_lesser(
    conduit_dynamic_lesser: Conduit,
) -> None:
    """
    Verify get_mutation_research fails immediately for lesser conduits.

    Contract:
        - Lesser conduits are rejected before mutation-runtime access.
    """
    with pytest.raises(RuntimeError, match="Only normal conduits can access MutationResearch"):
        conduit_dynamic_lesser.get_mutation_research()


def test_transfer_spell_ownership_delegates_when_dynamic(
    conduit_dynamic_normal: Conduit,
    conduit_lesser: Conduit,
) -> None:
    """
    Verify transfer_spell_ownership delegates to the conduit ward.

    Contract:
        - _transfer_spell_ownership is called with provided arguments.
        - The ward return value is returned to the caller.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        conduit_lesser (Conduit): Target conduit instance.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._transfer_spell_ownership.return_value = {
        "ok": True
    }
    with patch.object(
        Conduit,
        "_transaction_blocked_for_current_posture",
        return_value=False,
    ):
        result = conduit_dynamic_normal.transfer_spell_ownership(
            spell="sha-1",
            target_conduit=conduit_lesser,
            move_creations=True,
            include_dependencies=True,
            force_unshare=False,
            invalidate_after_transfer=False,
            mark_dependencies_dirty=True,
        )

    conduit_dynamic_normal._conduit_ward._transfer_spell_ownership.assert_called_once_with(
        spell="sha-1",
        target_conduit=conduit_lesser,
        move_creations=True,
        include_dependencies=True,
        force_unshare=False,
        invalidate_after_transfer=False,
        mark_dependencies_dirty=True,
    )
    assert result == {"ok": True}


def test_upgrade_to_normal_raises_when_not_dynamic(conduit_normal: Conduit) -> None:
    """
    Verify upgrade_to_normal is blocked in non-dynamic environments.

    Contract:
        - Dynamic mode is required for upgrades.

    Args:
        conduit_normal (Conduit): Normal conduit with dynamic disabled.

    Raises:
        AssertionError: If upgrade_to_normal does not raise.
    """
    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal.upgrade_to_normal("test")


def test_upgrade_to_normal_raises_when_not_lesser(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify upgrade_to_normal rejects non-lesser conduits.

    Contract:
        - Only lesser conduits can be upgraded.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If upgrade_to_normal does not raise.
    """
    with pytest.raises(RuntimeError, match="Only lesser conduits can be upgraded"):
        conduit_dynamic_normal.upgrade_to_normal("test")


def test_upgrade_to_normal_transitions_and_registers(
    conduit_dynamic_lesser: Conduit,
    aetheric_frame_stub: MagicMock,
) -> None:
    """
    Verify upgrade_to_normal transitions state and registers the conduit.

    Contract:
        - Conduit becomes normal and receives the provided name.
        - Existing Creations manager is preserved and re-wired into Meld.
        - Ward conversion and spellbook reset are invoked.
        - Root registration and cloud registration occur for named conduits.

    Args:
        conduit_dynamic_lesser (Conduit): Dynamic lesser conduit instance.
        conduit_cloud_stub (MagicMock): ConduitCloud stub used for registration checks.

    Raises:
        AssertionError: If the upgrade workflow is incomplete.
    """
    old_creations = conduit_dynamic_lesser._creations
    old_root_pool = conduit_dynamic_lesser._conduit_pool
    conduit_dynamic_lesser._conduit_ward = MagicMock()
    conduit_dynamic_lesser._spellbook.create_new_preset_spellbook = MagicMock()
    conduit_dynamic_lesser._nexus_publish_enabled = True
    conduit_dynamic_lesser._nexus = MagicMock()

    conduit_dynamic_lesser.upgrade_to_normal(name="alpha")

    assert conduit_dynamic_lesser._conduit_state == ConduitState.normal
    assert conduit_dynamic_lesser._name == "alpha"
    assert conduit_dynamic_lesser._creations is old_creations
    assert conduit_dynamic_lesser._meld._creations is old_creations
    assert conduit_dynamic_lesser._meld._resolution_conduit_id == conduit_dynamic_lesser._id
    assert conduit_dynamic_lesser._conduit_pool is not old_root_pool
    assert conduit_dynamic_lesser._conduit_pool.root_conduit is conduit_dynamic_lesser
    assert conduit_dynamic_lesser._conduit_pool.root_conduit_id == conduit_dynamic_lesser._id
    conduit_dynamic_lesser._conduit_ward._convert_to_normal_conduit.assert_called_once_with()
    conduit_dynamic_lesser._spellbook.create_new_preset_spellbook.assert_called_once_with()
    aetheric_frame_stub.register_root_conduit.assert_called_once_with(
        conduit_dynamic_lesser
    )
    conduit_dynamic_lesser._nexus._publish_conduit_record.assert_called_once_with(
        conduit_dynamic_lesser
    )


def test_upgrade_to_normal_refreshes_transaction_identity_without_changing_owner_id(
    conduit_dynamic_lesser: Conduit,
) -> None:
    """
    Verify upgrade_to_normal preserves conduit identity and refreshes metadata.

    Contract:
        - The conduit id stays stable across lesser -> normal upgrade.
        - TransactionIdentity keeps the same owner id.
        - Available transactions expand once the conduit becomes normal.
        - Root conduit metadata is refreshed to the upgraded conduit id.
    """
    conduit_dynamic_lesser._conduit_ward = MagicMock()
    conduit_dynamic_lesser._spellbook.create_new_preset_spellbook = MagicMock()
    conduit_dynamic_lesser._nexus_publish_enabled = False

    original_id = conduit_dynamic_lesser._id
    assert conduit_dynamic_lesser._transaction_identity is None

    conduit_dynamic_lesser.upgrade_to_normal(name="alpha")

    identity = conduit_dynamic_lesser._transaction_identity

    assert conduit_dynamic_lesser._id == original_id
    assert conduit_dynamic_lesser._root_conduit_id == original_id
    assert identity is not None
    assert identity.owner_id == original_id
    assert identity.supports_transaction("bind") is True
    assert identity.supports_transaction("scan") is True
    assert identity.supports_transaction("link") is True
    assert identity.supports_transaction("transfer_ownership") is True
    assert identity.supports_transaction("mutation") is True
    assert identity.supports_transaction("cluster_link") is True
    assert identity.metadata["conduit_state"] == ConduitState.normal.value
    assert identity.metadata["root_conduit_id"] == original_id


def test_upgrade_to_normal_defaults_name_when_omitted(
    conduit_dynamic_lesser: Conduit,
    aetheric_frame_stub: MagicMock,
) -> None:
    """
    Verify upgrade_to_normal assigns the default root name when omitted.

    Contract:
        - Conduit becomes normal with the default name.
        - Root registration still occurs for the upgraded conduit.
    """
    conduit_dynamic_lesser._conduit_ward = MagicMock()
    conduit_dynamic_lesser._spellbook.create_new_preset_spellbook = MagicMock()
    conduit_dynamic_lesser._nexus_publish_enabled = True
    conduit_dynamic_lesser._nexus = MagicMock()

    conduit_dynamic_lesser.upgrade_to_normal(name="default")

    assert conduit_dynamic_lesser._conduit_state == ConduitState.normal
    assert conduit_dynamic_lesser._name == "default"
    aetheric_frame_stub.register_root_conduit.assert_called_once_with(
        conduit_dynamic_lesser
    )


def test_upgrade_to_normal_registers_hooks(
    conduit_dynamic_lesser: Conduit,
    conduit_cloud_stub: MagicMock,
) -> None:
    """
    Verify upgrade_to_normal registers per-conduit local hooks when provided.

    Contract:
        - The supplied hook is attached to the conduit local hook map.

    Args:
        conduit_dynamic_lesser (Conduit): Dynamic lesser conduit instance.
        conduit_cloud_stub (MagicMock): ConduitCloud stub for registration calls.

    Raises:
        AssertionError: If hooks are not registered.
    """
    old_creations = conduit_dynamic_lesser._creations
    conduit_dynamic_lesser._conduit_ward = MagicMock()
    conduit_dynamic_lesser._spellbook.create_new_preset_spellbook = MagicMock()

    def hook(conduit: Conduit) -> None:
        """
        No-op hook used for registration checks.

        Args:
            conduit (Conduit): The conduit invoking the hook.

        Returns:
            None: Hook does not return a value.
        """
        _ = conduit

    conduit_dynamic_lesser.upgrade_to_normal(
        name="alpha",
        hooks={"on_conduit_post_link": hook},
    )

    assert conduit_dynamic_lesser._creations is old_creations
    assert conduit_dynamic_lesser._local_conduit_hooks is not None
    assert conduit_dynamic_lesser._local_conduit_hooks["on_conduit_post_link"][0] is hook


def test_create_lesser_conduit_publishes_descriptor_record_when_enabled(
    conduit_dynamic_normal: Conduit,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify lesser creation publishes a conduit record when Nexus publication is enabled.

    Contract:
        - Lesser conduits inherit the parent's Nexus publish flag.
        - The newly created lesser conduit publishes itself after lineage wiring.
    """
    published_calls = []

    def _capture_publish(conduit: Conduit) -> None:
        published_calls.append(conduit)

    monkeypatch.setattr(
        Conduit,
        "_publish_conduit_record_to_nexus",
        _capture_publish,
    )
    conduit_dynamic_normal._nexus_publish_enabled = True

    new_conduit = conduit_dynamic_normal.create_lesser_conduit()

    assert new_conduit._nexus_publish_enabled is True
    assert published_calls == [new_conduit]
    new_conduit.permanent_cleanup()


def test_create_lesser_conduit_inherits_root_conduit_pool(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify newly created lessers share the root-owned conduit pool reference.
    """
    lesser = conduit_dynamic_normal.create_lesser_conduit()
    try:
        assert lesser._conduit_pool is conduit_dynamic_normal._conduit_pool
        assert lesser._transaction_identity is None
        lesser.cleanup()
        assert lesser._transaction_identity is None
    finally:
        lesser.permanent_cleanup()


def test_create_lesser_conduit_preserves_temporarily_closed_pooled_gate(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify pooled lesser reacquire preserves non-terminal gate disable state.

    Contract:
        - Returning a lesser conduit shell to the pool does not reopen its gate.
        - Reusing the shell preserves the current temporary disabled state.
        - Gate governance belongs to the dev-ops/controller layer, not conduit
          reacquire lifecycle.
    """
    lesser = conduit_dynamic_normal.create_lesser_conduit()
    lesser._creation_gate.close()

    assert lesser._creation_gate.enabled is False
    assert lesser._creation_gate.is_closed() is False

    lesser.cleanup()
    reused = conduit_dynamic_normal.create_lesser_conduit()

    try:
        assert reused is lesser
        assert reused._creation_gate.enabled is False
        assert reused._creation_gate.is_closed() is False
    finally:
        reused.permanent_cleanup()


def test_set_creation_gate_controller_for_lineage_uses_existing_gate_and_updates_lesser_conduits(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify lineage rebinding reuses an existing gate and propagates controller/root metadata to lesser conduits.

    Contract:
        - Existing gate is adopted when the conduit has no local gate.
        - Lesser conduits receive the shared controller, root id, and meld resolution id.
        - Lesser conduits are asked to continue rebinding recursively.
    """
    controller = MagicMock()
    existing_gate = MagicMock()
    lesser = MagicMock()
    lesser._meld = MagicMock()
    conduit_dynamic_normal._creation_gate = None
    conduit_dynamic_normal._creation_gate_controller = controller
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._lock = MagicMock()
    conduit_dynamic_normal._conduit_ward._lock.__enter__.return_value = conduit_dynamic_normal._conduit_ward._lock
    conduit_dynamic_normal._conduit_ward._lock.__exit__.return_value = False
    conduit_dynamic_normal._conduit_ward._lesser_conduits = {"child": lesser}
    controller.get_conduit_gate.return_value = existing_gate

    conduit_dynamic_normal._set_creation_gate_controller_for_lineage()

    assert conduit_dynamic_normal._creation_gate is existing_gate
    assert lesser._creation_gate_controller is controller
    assert lesser._root_conduit_id == conduit_dynamic_normal._root_conduit_id
    assert lesser._meld._resolution_conduit_id == conduit_dynamic_normal._root_conduit_id
    lesser._set_creation_gate_controller_for_lineage.assert_called_once()


def test_set_creation_gate_controller_for_lineage_creates_gate_when_missing(
    conduit_dynamic_normal: Conduit,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_set_creation_gate_controller_for_lineage should create a gate when none exists anywhere."""
    controller = MagicMock()
    created_gate = MagicMock()
    conduit_dynamic_normal._creation_gate = None
    conduit_dynamic_normal._creation_gate_controller = controller
    conduit_dynamic_normal._conduit_ward = MagicMock()
    conduit_dynamic_normal._conduit_ward._lock = MagicMock()
    conduit_dynamic_normal._conduit_ward._lock.__enter__.return_value = conduit_dynamic_normal._conduit_ward._lock
    conduit_dynamic_normal._conduit_ward._lock.__exit__.return_value = False
    conduit_dynamic_normal._conduit_ward._lesser_conduits = {}
    controller.get_conduit_gate.return_value = None
    create_gate_for_current_root = MagicMock(return_value=created_gate)
    monkeypatch.setattr(
        Conduit,
        "_create_gate_for_current_root",
        lambda self, conduit_id: create_gate_for_current_root(conduit_id),
    )

    conduit_dynamic_normal._set_creation_gate_controller_for_lineage()

    create_gate_for_current_root.assert_called_once_with(conduit_dynamic_normal._id)
    assert conduit_dynamic_normal._creation_gate is created_gate


def test_upgrade_to_normal_logs_seed_failure_and_continues(
    conduit_dynamic_lesser: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify resolution-state seed failures are logged without aborting upgrade_to_normal.

    Contract:
        - Exceptions while seeding target resolution state are logged and suppressed.
        - The overall upgrade still completes.
    """
    conduit_dynamic_lesser._logger = MagicMock()
    conduit_dynamic_lesser._conduit_ward = MagicMock()
    root_conduit = MagicMock()
    root_conduit._id = "root-1"
    conduit_dynamic_lesser._conduit_ward.root_conduit = root_conduit
    conduit_dynamic_lesser._spellbook.create_new_preset_spellbook = MagicMock()
    conduit_dynamic_lesser._nexus_publish_enabled = True
    conduit_dynamic_lesser._nexus = MagicMock()
    spell_system_states = MagicMock()
    source_state = MagicMock()
    spell_system_states.get_conduit_resolution_state.return_value = source_state
    spell_system_states.get_or_create_conduit_resolution_state.side_effect = RuntimeError("seed boom")
    conduit_dynamic_lesser._spellbook._spell_system_states = spell_system_states

    conduit_dynamic_lesser.upgrade_to_normal(name="alpha")

    conduit_dynamic_lesser._logger.error.assert_called()
    assert conduit_dynamic_lesser._conduit_state == ConduitState.normal
    assert conduit_dynamic_lesser._name == "alpha"


def test_upgrade_to_normal_tolerates_root_conduit_lookup_failure(
    conduit_dynamic_lesser: Conduit,
    aether_stub: MagicMock,
) -> None:
    """upgrade_to_normal should continue when root_conduit lookup raises during seed setup."""
    conduit_dynamic_lesser._logger = MagicMock()
    conduit_dynamic_lesser._conduit_ward = MagicMock()
    type(conduit_dynamic_lesser._conduit_ward).root_conduit = PropertyMock(
        side_effect=RuntimeError("root lookup boom")
    )
    conduit_dynamic_lesser._spellbook.create_new_preset_spellbook = MagicMock()
    conduit_dynamic_lesser._spellbook._spell_system_states = MagicMock()
    conduit_dynamic_lesser._nexus_publish_enabled = True
    conduit_dynamic_lesser._nexus = MagicMock()

    conduit_dynamic_lesser.upgrade_to_normal(name="alpha")

    conduit_dynamic_lesser._logger.error.assert_not_called()
    assert conduit_dynamic_lesser._conduit_state == ConduitState.normal
    assert conduit_dynamic_lesser._name == "alpha"


def test_upgrade_to_normal_clears_dirty_with_last_validated_at(
    conduit_dynamic_lesser: Conduit,
    aether_stub: MagicMock,
) -> None:
    """upgrade_to_normal should clear dirty state with the source last_validated_at timestamp when the source is clean."""
    conduit_dynamic_lesser._logger = MagicMock()
    conduit_dynamic_lesser._conduit_ward = MagicMock()
    root_conduit = MagicMock()
    root_conduit._id = "root-1"
    conduit_dynamic_lesser._conduit_ward.root_conduit = root_conduit
    conduit_dynamic_lesser._spellbook.create_new_preset_spellbook = MagicMock()
    conduit_dynamic_lesser._nexus_publish_enabled = True
    conduit_dynamic_lesser._nexus = MagicMock()
    spell_system_states = MagicMock()
    source_state = MagicMock()
    target_state = MagicMock()
    source_state.is_dirty.return_value = False
    source_state.last_validated_at.return_value = 123.0
    spell_system_states.get_conduit_resolution_state.return_value = source_state
    spell_system_states.get_or_create_conduit_resolution_state.return_value = target_state
    conduit_dynamic_lesser._spellbook._spell_system_states = spell_system_states

    conduit_dynamic_lesser.upgrade_to_normal(name="alpha")

    target_state.clear_dirty.assert_called_once_with(123.0)


def test_upgrade_to_normal_logs_and_reraises_outer_failure(
    conduit_dynamic_lesser: Conduit,
) -> None:
    """upgrade_to_normal should log and re-raise failures from the main upgrade workflow."""
    conduit_dynamic_lesser._logger = MagicMock()
    conduit_dynamic_lesser._conduit_ward = MagicMock()
    conduit_dynamic_lesser._conduit_ward._convert_to_normal_conduit.side_effect = RuntimeError("convert boom")

    with pytest.raises(RuntimeError, match="convert boom"):
        conduit_dynamic_lesser.upgrade_to_normal(name="alpha")

    conduit_dynamic_lesser._logger.error.assert_called_once()


def test_create_lesser_conduit_raises_when_root_conduit_missing(
    conduit_dynamic_lesser: Conduit,
) -> None:
    """create_lesser_conduit should fail when the lineage root is unavailable."""
    conduit_dynamic_lesser._conduit_ward = MagicMock()
    conduit_dynamic_lesser._conduit_ward.root_conduit = None

    with pytest.raises(RuntimeError, match="Root conduit is not set"):
        conduit_dynamic_lesser.create_lesser_conduit()


def test_create_lesser_conduit_raises_when_lesser_has_no_ward(
    conduit_dynamic_lesser: Conduit,
) -> None:
    """create_lesser_conduit should fail when a lesser conduit has no ward lineage."""
    conduit_dynamic_lesser._conduit_ward = None

    with pytest.raises(RuntimeError, match="Root conduit is not set"):
        conduit_dynamic_lesser.create_lesser_conduit()


def test_create_lesser_conduit_raises_when_root_conduit_not_normal(
    conduit_dynamic_lesser: Conduit,
) -> None:
    """create_lesser_conduit should fail when the lineage root is not a normal conduit."""
    root_conduit = MagicMock()
    root_conduit._conduit_state = ConduitState.lesser
    conduit_dynamic_lesser._conduit_ward = MagicMock()
    conduit_dynamic_lesser._conduit_ward.root_conduit = root_conduit

    with pytest.raises(RuntimeError, match="Root conduit must be a normal conduit"):
        conduit_dynamic_lesser.create_lesser_conduit()


def test_conduit_no_longer_exposes_cloud_or_cluster_surface(
    conduit_normal: Conduit,
    conduit_lesser: Conduit,
    conduit_dynamic_normal: Conduit,
    conduit_dynamic_lesser: Conduit,
) -> None:
    """Conduit should keep the cloud accessor but not expose cluster mutator helpers."""
    removed_methods = (
        "register_conduit_cloud",
        "unregister_conduit_cloud",
        "create_cluster",
        "delete_cluster",
        "join_cluster",
        "leave_cluster",
        "list_clusters",
        "refresh_cluster_shares",
    )
    for conduit in (
        conduit_normal,
        conduit_lesser,
        conduit_dynamic_normal,
        conduit_dynamic_lesser,
    ):
        assert hasattr(conduit, "get_conduit_cloud")
        for method_name in removed_methods:
            assert not hasattr(conduit, method_name)
