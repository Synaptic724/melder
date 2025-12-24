from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicLogger
from tests.mocks.spellbook.core_classes import BasicService


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
) -> Configuration:
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
        Configuration: Configured instance.
    """
    configuration = Configuration(aether_frame=aether_frame)
    if dynamic:
        configuration.dynamic_defaults()
    else:
        configuration.automatic_defaults()
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
    aether._ensure_frame(frame_name)
    aether._create_cluster("cluster-a", frame_name)

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
        aether._add_conduit_to_cluster(conduit, "cluster-a", frame_name)

        shareable_id = spellbook.bind(
            spell=BasicConfig,
            existence=Existence.unique_per_conduit_cluster,
            permissions="create",
        )
        shareable_spell = next(
            spell for idx, spell in spellbook._spells.items() if idx.current == shareable_id
        )
        cluster = aether._get_cluster("cluster-a", frame_name)
        assert shareable_spell.spell_index not in cluster.get_shared_spells().get(conduit.id, set())

        aether._share_new_spell_to_clusters(conduit, shareable_spell, frame_name)

        cluster = aether._get_cluster("cluster-a", frame_name)
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
    aether._ensure_frame(frame_name)
    aether._create_cluster("cluster-a", frame_name)

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
        aether._add_conduit_to_cluster(conduit, "cluster-a", frame_name)

        non_shareable_id = spellbook.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )
        non_shareable_spell = next(
            spell for idx, spell in spellbook._spells.items() if idx.current == non_shareable_id
        )
        aether._share_new_spell_to_clusters(conduit, non_shareable_spell, frame_name)

        cluster = aether._get_cluster("cluster-a", frame_name)
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
    aether._ensure_frame(frame_name)
    aether._create_cluster("cluster-a", frame_name)

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
        aether._add_conduit_to_cluster(conduit, "cluster-a", frame_name)

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
        cluster = aether._get_cluster("cluster-a", frame_name)
        assert cluster.get_shared_spells().get(conduit.id, set()) == set()

        aether._refresh_cluster_shares_for_conduit(conduit, frame_name)

        shared = cluster.get_shared_spells().get(conduit.id, set())
        assert config_index in shared
        assert logger_index in shared
    finally:
        conduit.cleanup()
        spellbook.cleanup()
