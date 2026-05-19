from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
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


def test_aetheric_frame_cleanup_cleans_components_and_conduits() -> None:
    """
    Purpose:
        Validate AethericFrame cleanup tears down owned components.
    Contract:
        - Conduits, clusters, and managers are cleaned.
        - Frame registries are cleared after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clear owned resources.
    """
    aether = Aether()
    frame_name = "frame-cleanup"
    frame = aether._ensure_frame(frame_name)
    frame._conduit_cloud.create_cluster("cluster-a")
    cluster = frame._conduit_cloud._get_cluster("cluster-a")

    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")

    cloud = frame._conduit_cloud
    mutation = frame._aether._mutation_research
    states = frame._spell_system_states
    devops = frame._dev_ops_manager

    frame.cleanup()

    assert frame.cleaned is True
    assert conduit.cleaned is True
    assert cluster.cleaned is True
    assert cloud.cleaned is True
    assert mutation.cleaned is False
    assert states.cleaned is True
    assert devops.cleaned is True
    assert not hasattr(frame, '_conduits')
    assert not hasattr(frame, '_spell_registry')
    assert not hasattr(frame, '_version_registry')

    spellbook.cleanup()
