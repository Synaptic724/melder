from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicLogger
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


def test_aether_share_new_spell_to_clusters_registers_shared_spell() -> None:
    """
    Purpose:
        Validate _share_new_spell_to_clusters registers new shareables.
    Contract:
        - Shareable spell is added to the cluster shared registry.
    Returns:
        None.
    Raises:
        AssertionError: If the shared spell is not recorded.
    """
    aether = Aether()
    frame_name = "frame-share-new"
    frame = aether._ensure_frame(frame_name)
    cloud = frame._conduit_cloud
    cloud.create_cluster("cluster-a")

    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="owner")
    try:
        cloud.add_conduit_to_cluster(conduit, "cluster-a")

        with spellbook.binding_transaction():
            shareable_id = spellbook.bind(
                spell=BasicConfig,
                existence=Existence.unique_per_conduit_cluster,
                permissions="create",
            )
        shareable_spell = next(
            spell for idx, spell in spellbook._spells.items() if idx.current == shareable_id
        )
        cluster = cloud._get_cluster("cluster-a")
        assert shareable_spell.spell_index not in cluster.get_shared_spells().get(conduit.id, set())

        cloud.refresh_cluster_shares_for_conduit(conduit)

        cluster = cloud._get_cluster("cluster-a")
        shared = cluster.get_shared_spells()
        assert shareable_spell.spell_index in shared.get(conduit.id, set())
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_aether_share_new_spell_to_clusters_ignores_non_shareable() -> None:
    """
    Purpose:
        Validate _share_new_spell_to_clusters ignores non-shareable spells.
    Contract:
        - Non-shareable spell does not enter the shared registry.
    Returns:
        None.
    Raises:
        AssertionError: If non-shareable spells are registered.
    """
    aether = Aether()
    frame_name = "frame-share-ignore"
    frame = aether._ensure_frame(frame_name)
    cloud = frame._conduit_cloud
    cloud.create_cluster("cluster-a")

    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="owner")
    try:
        cloud.add_conduit_to_cluster(conduit, "cluster-a")

        with spellbook.binding_transaction():
            non_shareable_id = spellbook.bind(
                spell=BasicConfig,
                existence=Existence.unique,
                permissions="create",
            )
        non_shareable_spell = next(
            spell for idx, spell in spellbook._spells.items() if idx.current == non_shareable_id
        )
        cloud.refresh_cluster_shares_for_conduit(conduit)

        cluster = cloud._get_cluster("cluster-a")
        assert cluster.get_shared_spells() == {}
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_aether_refresh_cluster_shares_for_conduit_picks_up_new_shareables() -> None:
    """
    Purpose:
        Validate refresh_cluster_shares adds newly bound shareables.
    Contract:
        - New shareable spell indexes appear in the shared registry after refresh.
    Returns:
        None.
    Raises:
        AssertionError: If refresh does not add shareable spells.
    """
    aether = Aether()
    frame_name = "frame-refresh-shares"
    frame = aether._ensure_frame(frame_name)
    cloud = frame._conduit_cloud
    cloud.create_cluster("cluster-a")

    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="owner")
    try:
        cloud.add_conduit_to_cluster(conduit, "cluster-a")

        with spellbook.binding_transaction():
            config_id = spellbook.bind(
                spell=BasicConfig,
                existence=Existence.unique_per_conduit_cluster,
                permissions="create",
            )
            logger_id = spellbook.bind(
                spell=BasicLogger,
                existence=Existence.unique_per_conduit_cluster,
                permissions="create",
            )
        config_index = next(
            idx for idx in spellbook._spells.keys() if idx.current == config_id
        )
        logger_index = next(
            idx for idx in spellbook._spells.keys() if idx.current == logger_id
        )
        cluster = cloud._get_cluster("cluster-a")
        assert cluster.get_shared_spells().get(conduit.id, set()) == set()

        cloud.refresh_cluster_shares_for_conduit(conduit)

        shared = cluster.get_shared_spells().get(conduit.id, set())
        assert config_index in shared
        assert logger_index in shared
    finally:
        conduit.cleanup()
        spellbook.cleanup()
