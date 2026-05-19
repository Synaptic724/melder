from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
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


def _make_configuration(
    *,
    aether_frame: str = "default",
    dynamic: bool = False,
    workers: int = 1,
) -> SpellbookConfiguration:
    """
    Purpose:
        Create a configuration for Aether integration tests.
    Contract:
        - system_state is set to automatic or dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Args:
        dynamic: Whether to use dynamic defaults.
        workers: Scheduler workers per spellbook.
    Returns:
        SpellbookConfiguration: Configured instance.
    """
    configuration = SpellbookConfiguration(aether_frame=aether_frame)
    if dynamic:
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
    else:
        apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return configuration


def test_aether_cluster_membership_tracks_conduits() -> None:
    """
    Purpose:
        Validate cluster membership list tracking via Aether APIs.
    Contract:
        - Added conduits appear in the cluster membership list.
        - Cluster lists are discoverable per conduit id.
        - Removing a conduit updates membership and cluster lists.
    Returns:
        None.
    Raises:
        AssertionError: If membership tracking is incorrect.
    """
    aether = Aether()
    frame_name = "frame-membership"
    frame = aether._ensure_frame(frame_name)
    cloud = frame._conduit_cloud
    cloud.create_cluster("cluster-a")

    book_a = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    book_b = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    book_a.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    book_b.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_a = book_a.conjure(name="root-a")
    conduit_b = book_b.conjure(name="root-b")
    try:
        cloud.add_conduit_to_cluster(conduit_a, "cluster-a")
        cloud.add_conduit_to_cluster(conduit_b, "cluster-a")

        members = set(cloud._get_cluster("cluster-a").get_members())
        assert members == {conduit_a.id, conduit_b.id}

        clusters_a = set(cloud.get_clusters_for_conduit(conduit_a.id))
        clusters_b = set(cloud.get_clusters_for_conduit(conduit_b.id))
        assert clusters_a == {"cluster-a"}
        assert clusters_b == {"cluster-a"}

        cloud.remove_conduit_from_cluster(conduit_b, "cluster-a")
        members = set(cloud._get_cluster("cluster-a").get_members())
        assert members == {conduit_a.id}

        clusters_b = set(cloud.get_clusters_for_conduit(conduit_b.id))
        assert clusters_b == set()
    finally:
        conduit_b.cleanup()
        conduit_a.cleanup()
        book_b.cleanup()
        book_a.cleanup()


def test_aether_cluster_lookup_missing_cluster_raises() -> None:
    """
    Purpose:
        Validate cluster lookups raise when the cluster is missing.
    Contract:
        - Missing cluster queries raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If missing-cluster lookups do not raise.
    """
    aether = Aether()
    frame_name = "frame-missing-cluster"
    frame = aether._ensure_frame(frame_name)
    cloud = frame._conduit_cloud
    with pytest.raises(ValueError, match="does not exist"):
        cloud._get_cluster("missing")
    with pytest.raises(ValueError, match="does not exist"):
        cloud.remove_conduit_from_cluster(
            conduit=object(),
            cluster_name="missing",
        )


def test_aether_get_clusters_for_conduit_empty_when_none() -> None:
    """
    Purpose:
        Validate get_clusters_for_conduit returns empty when no clusters exist.
    Contract:
        - Empty list is returned for unknown conduit ids.
    Returns:
        None.
    Raises:
        AssertionError: If a non-empty list is returned.
    """
    aether = Aether()
    frame_name = "frame-empty-clusters"
    frame = aether._ensure_frame(frame_name)
    clusters = frame._conduit_cloud.get_clusters_for_conduit("missing-id")
    assert clusters == []
