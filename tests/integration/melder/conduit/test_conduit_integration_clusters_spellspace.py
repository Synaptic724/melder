from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_dynamic_configuration() -> SpellbookConfiguration:
    """
    Purpose:
        Create a dynamic configuration for cluster/cloud tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Returns:
        SpellbookConfiguration: Dynamic configuration instance.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def test_conduit_cluster_join_leave_list_and_delete() -> None:
    """
    Purpose:
        Validate cluster create/join/leave/delete lifecycle.
    Contract:
        - Conduits join clusters and appear in list_clusters.
        - leave_cluster removes the conduit from the cluster.
        - delete_cluster removes the cluster definition.
    Returns:
        None.
    Raises:
        AssertionError: If cluster membership is incorrect.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    peer_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    peer = peer_book.conjure(automatic=False, name="peer")
    try:
        cloud = owner._spellbook._aether.get_conduit_cloud(owner._aetheric_frame_name)
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.add_conduit_to_cluster(peer, "cluster-a")

        assert set(cloud.get_clusters_for_conduit(owner._id)) == {"cluster-a"}
        assert set(cloud.get_clusters_for_conduit(peer._id)) == {"cluster-a"}

        cloud.refresh_cluster_shares_for_conduit(owner)

        cloud.remove_conduit_from_cluster(peer, "cluster-a")
        assert cloud.get_clusters_for_conduit(peer._id) == []

        cloud.remove_conduit_from_cluster(owner, "cluster-a")
        cloud.delete_cluster("cluster-a")
        assert cloud.get_clusters_for_conduit(owner._id) == []
    finally:
        peer.permanent_cleanup()
        owner.permanent_cleanup()


def test_conduit_conduit_cloud_register_unregister() -> None:
    """
    Purpose:
        Validate conduit cloud registration and unregistration.
    Contract:
        - Named dynamic conduits are visible in the conduit cloud.
        - unregister_conduit_cloud removes the conduit from the cloud.
        - register_conduit_cloud re-adds the conduit.
        - lesser conduits cannot register in the cloud.
    Returns:
        None.
    Raises:
        AssertionError: If cloud registration is incorrect.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(automatic=False, name="owner")
    lesser = conduit.create_lesser_conduit()
    try:
        cloud = conduit._spellbook._aether.get_conduit_cloud(conduit._aetheric_frame_name)
        assert cloud.get_conduit("owner") is conduit
        assert cloud.list_cloud_names() == ("owner",)
        assert cloud.get_conduit("owner") is conduit

        with pytest.raises(ValueError, match="Only normal conduits can be registered as root conduits"):
            conduit._spellbook._aether._ensure_frame(
                conduit._aetheric_frame_name
            ).register_root_conduit(lesser)
    finally:
        conduit.permanent_cleanup()


def test_aether_get_conduit_cloud_returns_frame_service_in_automatic() -> None:
    """
    Purpose:
        Validate Aether still exposes the frame-local cloud in automatic mode.
    Contract:
        - Automatic frames still own a ConduitCloud service.
    Returns:
        None.
    Raises:
        AssertionError: If the frame-local cloud is unavailable.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        cloud = spellbook._aether.get_conduit_cloud(conduit._aetheric_frame_name)
        assert cloud.get_conduit("root") is conduit
    finally:
        conduit.permanent_cleanup()
