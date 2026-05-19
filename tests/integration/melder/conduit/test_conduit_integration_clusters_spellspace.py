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
        owner.create_cluster("cluster-a")
        owner.join_cluster("cluster-a")
        peer.join_cluster("cluster-a")

        assert set(owner.list_clusters()) == {"cluster-a"}
        assert set(peer.list_clusters()) == {"cluster-a"}

        owner.refresh_cluster_shares()

        peer.leave_cluster("cluster-a")
        assert peer.list_clusters() == []

        owner.leave_cluster("cluster-a")
        owner.delete_cluster("cluster-a")
        assert owner.list_clusters() == []
    finally:
        peer.cleanup()
        owner.cleanup()


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
        cloud = conduit.get_conduit_cloud()
        assert cloud.get_conduit("owner") is conduit
        assert cloud._registry["owner"] is conduit

        conduit.unregister_conduit_cloud(conduit)
        assert "owner" not in cloud._registry
        assert cloud.get_conduit("owner") is conduit

        conduit.register_conduit_cloud(conduit)
        assert cloud.get_conduit("owner") is conduit

        with pytest.raises(RuntimeError, match="Lesser conduits cannot register"):
            lesser.register_conduit_cloud(lesser)
    finally:
        conduit.cleanup()


def test_conduit_get_conduit_cloud_rejects_automatic() -> None:
    """
    Purpose:
        Validate get_conduit_cloud rejects automatic environments.
    Contract:
        - Automatic conduits raise when accessing the conduit cloud.
    Returns:
        None.
    Raises:
        AssertionError: If conduit cloud is accessible in automatic mode.
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
        with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
            conduit.get_conduit_cloud()
    finally:
        conduit.cleanup()
