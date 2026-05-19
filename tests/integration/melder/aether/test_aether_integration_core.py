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


def test_aether_ensure_frame_reuses_existing() -> None:
    """
    Purpose:
        Validate _ensure_frame reuses existing frames and wires defaults.
    Contract:
        - Repeated calls return the same frame instance.
        - The default frame is stored on the Aether instance.
    Returns:
        None.
    Raises:
        AssertionError: If frame reuse or default wiring fails.
    """
    aether = Aether()
    frame = aether._ensure_frame("frame-alpha")
    same = aether._ensure_frame("frame-alpha")
    assert frame is same
    assert aether._aetheric_frames["frame-alpha"] is frame

    default_frame = aether._ensure_frame("default")
    assert default_frame is aether._default_frame


def test_aether_get_configuration_missing_frame_raises() -> None:
    """
    Purpose:
        Validate _get_configuration fails for unknown frames.
    Contract:
        - ValueError is raised for missing frames.
    Returns:
        None.
    Raises:
        AssertionError: If missing-frame lookups do not raise.
    """
    aether = Aether()
    with pytest.raises(ValueError, match="does not exist"):
        aether._get_configuration("missing-frame")


def test_aether_bind_configuration_missing_frame_raises() -> None:
    """
    Purpose:
        Validate _bind_configuration fails for unknown frames.
    Contract:
        - ValueError is raised when binding to a missing frame.
    Returns:
        None.
    Raises:
        AssertionError: If missing-frame binds do not raise.
    """
    aether = Aether()
    config = SpellbookConfiguration(aether_frame="missing-frame").with_defaults()
    with pytest.raises(ValueError, match="does not exist"):
        aether._bind_configuration(config, "missing-frame")


def test_aether_get_conduit_cloud_missing_frame_raises() -> None:
    """
    Purpose:
        Validate _get_conduit_cloud fails for unknown frames.
    Contract:
        - ValueError is raised for missing frames.
    Returns:
        None.
    Raises:
        AssertionError: If missing-frame lookups do not raise.
    """
    aether = Aether()
def test_aether_resolves_conduit_by_name_id_and_spell_id() -> None:
    """
    Purpose:
        Validate Aether resolves conduits by name, id, and spell id.
    Contract:
        - get_conduit_by_id returns the owning conduit.
        - get_conduit_by_name returns the owning conduit.
        - get_conduit_by_spell_id returns the owning conduit.
        - Missing lookups raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If registry lookups are incorrect.
    """
    aether = Aether()
    frame_name = "frame-registry"
    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        assert aether._get_conduit_by_id(conduit.id, frame_name) is conduit
        assert aether._get_conduit_by_name("root", frame_name) is conduit
        assert aether._get_conduit_by_spell_id(spell_id, frame_name) is conduit

        with pytest.raises(ValueError, match="not found"):
            aether._get_conduit_by_name("missing", frame_name)
        with pytest.raises(ValueError, match="not found"):
            aether._get_conduit_by_id("missing-id", frame_name)
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_aether_cluster_lifecycle_create_get_remove() -> None:
    """
    Purpose:
        Validate cluster creation and removal flows in Aether.
    Contract:
        - _create_cluster registers the cluster.
        - _get_cluster returns the cluster by name.
        - _remove_cluster deletes the cluster.
        - Duplicate creation and missing removal raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If cluster lifecycle behavior is incorrect.
    """
    aether = Aether()
    frame_name = "frame-cluster"
    frame = aether._ensure_frame(frame_name)
    cloud = frame._conduit_cloud

    cloud.create_cluster("cluster-a")
    cluster = cloud._get_cluster("cluster-a")
    assert cluster._name == "cluster-a"
    with pytest.raises(ValueError, match="already exists"):
        cloud.create_cluster("cluster-a")

    cloud.delete_cluster("cluster-a")
    with pytest.raises(ValueError, match="does not exist"):
        cloud._get_cluster("cluster-a")
    with pytest.raises(ValueError, match="does not exist"):
        cloud.delete_cluster("cluster-a")


def test_aether_cleanup_aetheric_frames_cleans_conduits() -> None:
    """
    Purpose:
        Validate cleanup_aetheric_frames cleans all frames and conduits.
    Contract:
        - Frame cleanup marks frames as cleaned.
        - Conduits in those frames are cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not mark frames or conduits cleaned.
    """
    aether = Aether()
    book_a = Spellbook(
        aetheric_frame="frame-clean-a",
        configuration=_make_configuration(aether_frame="frame-clean-a"),
    )
    book_b = Spellbook(
        aetheric_frame="frame-clean-b",
        configuration=_make_configuration(aether_frame="frame-clean-b"),
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
    frame_a = aether._aetheric_frames["frame-clean-a"]
    frame_b = aether._aetheric_frames["frame-clean-b"]

    aether.cleanup_aetheric_frames()

    assert frame_a.cleaned is True
    assert frame_b.cleaned is True
    assert conduit_a.cleaned is True
    assert conduit_b.cleaned is True
    assert "frame-clean-a" not in aether._aetheric_frames
    assert "frame-clean-b" not in aether._aetheric_frames

    book_b.cleanup()
    book_a.cleanup()


def test_aether_cleanup_resets_singleton() -> None:
    """
    Purpose:
        Validate cleanup resets the singleton and allows reinitialization.
    Contract:
        - cleanup marks the instance cleaned and clears the singleton.
        - A new instance can be created afterward.
    Returns:
        None.
    Raises:
        AssertionError: If the singleton does not reset correctly.
    """
    aether = Aether()
    old_id = aether._id

    aether.cleanup()

    new_aether = Aether()
    assert new_aether is not aether
    assert new_aether._id != old_id
    assert new_aether.cleaned is False
