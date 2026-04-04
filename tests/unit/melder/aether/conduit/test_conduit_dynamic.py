from unittest.mock import MagicMock

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


def test_get_conduit_cloud_raises_for_lesser(conduit_lesser: Conduit) -> None:
    """
    Verify get_conduit_cloud rejects lesser conduits.

    Contract:
        - Lesser conduits cannot access the conduit cloud.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If the call does not raise.
    """
    with pytest.raises(RuntimeError, match="Lesser conduits cannot access"):
        conduit_lesser.get_conduit_cloud()


def test_get_conduit_cloud_raises_when_not_dynamic(conduit_normal: Conduit) -> None:
    """
    Verify get_conduit_cloud rejects non-dynamic environments.

    Contract:
        - Dynamic environment is required for conduit cloud access.

    Args:
        conduit_normal (Conduit): Normal conduit with dynamic disabled.

    Raises:
        AssertionError: If the call does not raise.
    """
    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal.get_conduit_cloud()


def test_get_conduit_cloud_delegates_for_dynamic(
    conduit_dynamic_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify get_conduit_cloud delegates to Aether in dynamic mode.

    Contract:
        - Aether return value is passed through unchanged.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If delegation fails.
    """
    sentinel = MagicMock()
    aether_stub._get_conduit_cloud.return_value = sentinel

    result = conduit_dynamic_normal.get_conduit_cloud()

    aether_stub._get_conduit_cloud.assert_called_once_with("default")
    assert result is sentinel


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
    with pytest.raises(RuntimeError, match="Ownership transfer requires dynamic mode"):
        conduit_normal.transfer_spell_ownership(
            spell="sha-1",
            target_conduit=conduit_lesser,
        )


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
        conduit_normal.upgrade_to_normal()


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
        conduit_dynamic_normal.upgrade_to_normal()


def test_upgrade_to_normal_transitions_and_registers(
    conduit_dynamic_lesser: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify upgrade_to_normal transitions state and registers the conduit.

    Contract:
        - Conduit becomes normal and receives the provided name.
        - Existing Creations manager is preserved and re-wired into Meld.
        - Ward conversion and spellbook reset are invoked.
        - Aether registration and cloud registration occur for named conduits.

    Args:
        conduit_dynamic_lesser (Conduit): Dynamic lesser conduit instance.
        aether_stub (MagicMock): Aether stub used for registration checks.

    Raises:
        AssertionError: If the upgrade workflow is incomplete.
    """
    old_creations = conduit_dynamic_lesser._creations
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
    conduit_dynamic_lesser._conduit_ward._convert_to_normal_conduit.assert_called_once_with()
    conduit_dynamic_lesser._spellbook.create_new_preset_spellbook.assert_called_once_with()
    aether_stub._add_conduit.assert_called_once_with(conduit_dynamic_lesser, "default")
    aether_stub._register_conduit_cloud.assert_called_once_with(conduit_dynamic_lesser, "default")
    conduit_dynamic_lesser._nexus._publish_conduit_record.assert_called_once_with(
        conduit_dynamic_lesser
    )


def test_upgrade_to_normal_defaults_name_when_omitted(
    conduit_dynamic_lesser: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify upgrade_to_normal assigns the default root name when omitted.

    Contract:
        - Conduit becomes normal with the default name.
        - Aether registration still occurs for the upgraded conduit.
    """
    conduit_dynamic_lesser._conduit_ward = MagicMock()
    conduit_dynamic_lesser._spellbook.create_new_preset_spellbook = MagicMock()
    conduit_dynamic_lesser._nexus_publish_enabled = True
    conduit_dynamic_lesser._nexus = MagicMock()

    conduit_dynamic_lesser.upgrade_to_normal(name=None)

    assert conduit_dynamic_lesser._conduit_state == ConduitState.normal
    assert conduit_dynamic_lesser._name == "default"
    aether_stub._add_conduit.assert_called_once_with(conduit_dynamic_lesser, "default")


def test_upgrade_to_normal_registers_hooks(
    conduit_dynamic_lesser: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify upgrade_to_normal registers per-conduit local hooks when provided.

    Contract:
        - The supplied hook is attached to the conduit local hook map.

    Args:
        conduit_dynamic_lesser (Conduit): Dynamic lesser conduit instance.
        aether_stub (MagicMock): Aether stub for registration calls.

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


def test_get_mutation_research_raises_for_lesser(conduit_lesser: Conduit) -> None:
    """
    Verify get_mutation_research rejects lesser conduits.

    Contract:
        - Only normal conduits can access MutationResearch.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If the call does not raise.
    """
    with pytest.raises(RuntimeError, match="Only normal conduits"):
        conduit_lesser.get_mutation_research()


def test_get_mutation_research_raises_when_not_dynamic(
    conduit_normal: Conduit,
) -> None:
    """
    Verify get_mutation_research rejects non-dynamic environments.

    Contract:
        - Dynamic mode is required for MutationResearch access.

    Args:
        conduit_normal (Conduit): Normal conduit with dynamic disabled.

    Raises:
        AssertionError: If the call does not raise.
    """
    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal.get_mutation_research()


def test_get_mutation_research_delegates_when_dynamic(
    conduit_dynamic_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify get_mutation_research delegates to Aether in dynamic mode.

    Contract:
        - Aether return value is passed through unchanged.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If delegation fails.
    """
    sentinel = MagicMock()
    aether_stub._get_mutation_research.return_value = sentinel

    result = conduit_dynamic_normal.get_mutation_research()

    aether_stub._get_mutation_research.assert_called_once_with("default")
    assert result is sentinel


def test_register_conduit_cloud_raises_when_not_dynamic(conduit_normal: Conduit) -> None:
    """
    Verify register_conduit_cloud is blocked in non-dynamic environments.

    Contract:
        - Dynamic mode is required for cloud registration.

    Args:
        conduit_normal (Conduit): Normal conduit with dynamic disabled.

    Raises:
        AssertionError: If registration does not raise.
    """
    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal.register_conduit_cloud(conduit_normal)


def test_register_conduit_cloud_raises_for_lesser(conduit_dynamic_lesser: Conduit) -> None:
    """
    Verify register_conduit_cloud rejects lesser conduits.

    Contract:
        - Lesser conduits cannot register in the conduit cloud.

    Args:
        conduit_dynamic_lesser (Conduit): Dynamic lesser conduit instance.

    Raises:
        AssertionError: If registration does not raise.
    """
    with pytest.raises(RuntimeError, match="Lesser conduits cannot register"):
        conduit_dynamic_lesser.register_conduit_cloud(conduit_dynamic_lesser)


def test_register_conduit_cloud_raises_when_name_missing(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify register_conduit_cloud rejects unnamed conduits.

    Contract:
        - A conduit must have a name before registration.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If registration does not raise for missing name.
    """
    with pytest.raises(RuntimeError, match="name is not set"):
        conduit_dynamic_normal.register_conduit_cloud(conduit_dynamic_normal)


def test_register_conduit_cloud_delegates_to_aether(
    conduit_dynamic_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify register_conduit_cloud delegates to Aether.

    Contract:
        - Aether receives the registration call with the conduit and frame.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_dynamic_normal.name = "alpha"
    conduit_dynamic_normal._nexus_publish_enabled = True
    conduit_dynamic_normal._nexus = MagicMock()

    conduit_dynamic_normal.register_conduit_cloud(conduit_dynamic_normal)

    aether_stub._register_conduit_cloud.assert_called_once_with(conduit_dynamic_normal, "default")
    conduit_dynamic_normal._nexus._publish_frame_record.assert_called_once_with(
        conduit_dynamic_normal._spellbook
    )


def test_unregister_conduit_cloud_raises_when_not_dynamic(conduit_normal: Conduit) -> None:
    """
    Verify unregister_conduit_cloud is blocked in non-dynamic environments.

    Contract:
        - Dynamic mode is required for cloud unregistration.

    Args:
        conduit_normal (Conduit): Normal conduit with dynamic disabled.

    Raises:
        AssertionError: If unregistration does not raise.
    """
    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        conduit_normal.unregister_conduit_cloud(conduit_normal)


def test_unregister_conduit_cloud_raises_for_lesser(conduit_dynamic_lesser: Conduit) -> None:
    """
    Verify unregister_conduit_cloud rejects lesser conduits.

    Contract:
        - Lesser conduits cannot unregister from the conduit cloud.

    Args:
        conduit_dynamic_lesser (Conduit): Dynamic lesser conduit instance.

    Raises:
        AssertionError: If unregistration does not raise.
    """
    with pytest.raises(RuntimeError, match="Lesser conduits cannot unregister"):
        conduit_dynamic_lesser.unregister_conduit_cloud(conduit_dynamic_lesser)


def test_unregister_conduit_cloud_raises_when_name_missing(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify unregister_conduit_cloud rejects unnamed conduits.

    Contract:
        - A conduit must have a name before unregistration.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If unregistration does not raise for missing name.
    """
    with pytest.raises(RuntimeError, match="name is not set"):
        conduit_dynamic_normal.unregister_conduit_cloud(conduit_dynamic_normal)


def test_unregister_conduit_cloud_delegates_to_aether(
    conduit_dynamic_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify unregister_conduit_cloud delegates to Aether.

    Contract:
        - Aether receives the unregistration call with the conduit and frame.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_dynamic_normal.name = "alpha"
    conduit_dynamic_normal._nexus_publish_enabled = True
    conduit_dynamic_normal._nexus = MagicMock()

    conduit_dynamic_normal.unregister_conduit_cloud(conduit_dynamic_normal)

    aether_stub._unregister_conduit_cloud.assert_called_once_with(conduit_dynamic_normal, "default")
    conduit_dynamic_normal._nexus._publish_frame_record.assert_called_once_with(
        conduit_dynamic_normal._spellbook
    )


def test_create_cluster_delegates_to_aether(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify create_cluster delegates to Aether.

    Contract:
        - Aether receives the create call with the conduit's frame.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_normal._nexus_publish_enabled = True
    conduit_normal._nexus = MagicMock()

    conduit_normal.create_cluster("cluster-1")

    aether_stub._create_cluster.assert_called_once_with("cluster-1", "default")
    conduit_normal._nexus._publish_frame_record.assert_called_once_with(
        conduit_normal._spellbook
    )


def test_delete_cluster_delegates_to_aether(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify delete_cluster delegates to Aether.

    Contract:
        - Aether receives the remove call with the conduit's frame.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_normal._nexus_publish_enabled = True
    conduit_normal._nexus = MagicMock()

    conduit_normal.delete_cluster("cluster-1")

    aether_stub._remove_cluster.assert_called_once_with("cluster-1", "default")
    conduit_normal._nexus._publish_frame_record.assert_called_once_with(
        conduit_normal._spellbook
    )


def test_join_cluster_delegates_to_aether(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify join_cluster delegates to Aether.

    Contract:
        - Aether receives the add call with the conduit instance and frame.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_normal.join_cluster("cluster-1")

    aether_stub._add_conduit_to_cluster.assert_called_once_with(conduit_normal, "cluster-1", "default")


def test_leave_cluster_delegates_to_aether(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify leave_cluster delegates to Aether.

    Contract:
        - Aether receives the remove call with the conduit instance and frame.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_normal.leave_cluster("cluster-1")

    aether_stub._remove_conduit_from_cluster.assert_called_once_with(conduit_normal, "cluster-1", "default")


def test_list_clusters_returns_aether_list(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify list_clusters returns the Aether cluster list.

    Contract:
        - Aether results are passed through unchanged.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If the list is not returned.
    """
    aether_stub._get_clusters_for_conduit.return_value = ["alpha", "beta"]

    result = conduit_normal.list_clusters()

    aether_stub._get_clusters_for_conduit.assert_called_once_with(conduit_normal._id, "default")
    assert result == ["alpha", "beta"]


def test_refresh_cluster_shares_delegates_to_aether(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify refresh_cluster_shares delegates to Aether.

    Contract:
        - Aether receives the refresh call with the conduit instance and frame.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If delegation fails.
    """
    conduit_normal.refresh_cluster_shares()

    aether_stub._refresh_cluster_shares_for_conduit.assert_called_once_with(conduit_normal, "default")
