from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
    build_aetheric_frame_configuration_for_spellbook_configuration,
    set_frame_ai_native_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration,
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


def test_aether_frame_isolation_for_conduit_and_spell_lookup() -> None:
    """
    Purpose:
        Validate frame isolation for conduit and spell lookups.
    Contract:
        - Default-frame lookups do not see other frames.
        - Explicit frame lookup resolves the target frame.
    Returns:
        None.
    Raises:
        AssertionError: If frame isolation or lookup routing fails.
    """
    book_a = Spellbook(
        aetheric_frame="frame-a",
        configuration=_make_configuration(aether_frame="frame-a"),
    )
    book_b = Spellbook(
        aetheric_frame="frame-b",
        configuration=_make_configuration(aether_frame="frame-b"),
    )
    spell_id_a = book_a.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    spell_id_b = book_b.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit_a = book_a.conjure(name="root-a")
    conduit_b = book_b.conjure(name="root-b")
    try:
        with pytest.raises(ValueError, match="Spell version"):
            conduit_a.get_conduit_by_spell_id(spell_id_b)

        assert conduit_a.get_conduit_by_spell_id(
            spell_id_a,
            aetheric_frame_name="frame-a",
        ) is conduit_a
        assert conduit_b.get_conduit_by_spell_id(
            spell_id_b,
            aetheric_frame_name="frame-b",
        ) is conduit_b

        assert conduit_a.get_conduit_by_spell_id(
            spell_id_b,
            aetheric_frame_name="frame-b",
        ) is conduit_b

        with pytest.raises(ValueError, match="not found"):
            conduit_a.get_conduit_by_name("root-b")

        assert conduit_a.get_conduit_by_name(
            "root-b",
            aetheric_frame="frame-b",
        ) is conduit_b
    finally:
        conduit_b.cleanup()
        conduit_a.cleanup()


def test_aether_conduit_cloud_isolated_by_frame() -> None:
    """
    Purpose:
        Validate ConduitCloud registries are isolated per frame.
    Contract:
        - Each frame's cloud resolves only its own conduits.
        - Cross-frame lookup raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If conduit clouds are not frame-isolated.
    """
    book_a = Spellbook(
        aetheric_frame="frame-a",
        configuration=_make_configuration(aether_frame="frame-a", dynamic=True),
    )
    book_b = Spellbook(
        aetheric_frame="frame-b",
        configuration=_make_configuration(aether_frame="frame-b", dynamic=True),
    )
    book_a.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    book_b.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit_a = book_a.conjure(automatic=False, name="root-a")
    conduit_b = book_b.conjure(automatic=False, name="root-b")
    try:
        cloud_a = conduit_a.get_conduit_cloud()
        cloud_b = conduit_b.get_conduit_cloud()

        assert cloud_a.get_conduit("root-a") is conduit_a
        assert cloud_b.get_conduit("root-b") is conduit_b
        with pytest.raises(ValueError, match="not found"):
            cloud_a.get_conduit("root-b")
        with pytest.raises(ValueError, match="not found"):
            cloud_b.get_conduit("root-a")
    finally:
        conduit_b.cleanup()
        conduit_a.cleanup()


def test_aetheric_frame_version_registry_tracks_bound_spells() -> None:
    """
    Purpose:
        Validate AethericFrame version registry tracks bound spell versions.
    Contract:
        - has_version returns True for bound spell ids.
        - get_all_versions includes bound spell ids.
        - find_and_return_spell_index resolves the SpellIndex lineage.
    Returns:
        None.
    Raises:
        AssertionError: If version registry does not reflect bound spells.
    """
    aether = Aether()
    frame_name = "frame-versions"
    frame = aether._ensure_frame(frame_name)

    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    service_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    config_id = spellbook.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        frame.refresh_version_registry()
        assert frame.has_version(service_id) is True
        assert frame.has_version(config_id) is True
        all_versions = frame.get_all_versions()
        assert service_id in all_versions
        assert config_id in all_versions
        spell_index = frame.find_and_return_spell_index(service_id)
        assert spell_index is not None
        assert spell_index.current == service_id
    finally:
        conduit.cleanup()


def test_bottom_up_frame_cleanup_cleans_conduits_and_removes_frame() -> None:
    """
    Purpose:
        Validate bottom-up frame cleanup cleans conduits and removes the frame.
    Contract:
        - `frame.cleanup()` cleans the frame and its conduits.
        - Aether no longer resolves the cleaned frame.
    Returns:
        None.
    Raises:
        AssertionError: If frame cleanup does not clear frame state.
    """
    aether = Aether()
    frame_name = "frame-clean"
    frame = aether._ensure_frame(frame_name)
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

    frame.cleanup()

    assert frame.cleaned is True
    assert conduit.cleaned is True
    with pytest.raises(ValueError, match="does not exist"):
        aether._get_conduit_by_id(conduit.id, frame_name)
    with pytest.raises(RuntimeError, match="already been cleaned"):
        conduit.meld(spell=spell_id)


def test_aether_configuration_bound_on_conjure_and_shared_by_frame() -> None:
    """
    Purpose:
        Validate configuration binding into Aether and per-frame reuse.
    Contract:
        - Aether has no configuration before the first conjure.
        - Conjure binds the configuration for the frame.
        - Subsequent spellbooks in the same frame reuse the bound configuration.
    Returns:
        None.
    Raises:
        AssertionError: If configuration binding or reuse is incorrect.
    """
    aether = Aether()
    frame_name = "frame-config"
    configuration = _make_configuration(aether_frame=frame_name)
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration(configuration, True)
    book_a = Spellbook(
        aetheric_frame=frame_name,
        configuration=configuration,
    )
    assert aether._get_configuration(frame_name) is None

    book_a.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book_a.conjure(name="root")
    try:
        assert aether._get_configuration(frame_name) is book_a.get_configuration()

        book_b = Spellbook(aetheric_frame=frame_name)
        try:
            assert book_b.get_configuration() is book_a.get_configuration()
            assert book_b.is_configuration_locked() is True
        finally:
            book_b.cleanup()
    finally:
        conduit.cleanup()
        book_a.cleanup()


def test_aether_managers_are_scoped_by_frame() -> None:
    """
    Purpose:
        Validate DevOps, mutation, and state managers are frame-scoped.
    Contract:
        - Manager accessors return the owning frame's instances.
        - Different frames receive distinct manager instances.
    Returns:
        None.
    Raises:
        AssertionError: If manager scoping or accessors are incorrect.
    """
    aether = Aether()
    frame_a = aether._ensure_frame("frame-managers-a")
    frame_b = aether._ensure_frame("frame-managers-b")

    devops_a = aether._get_devops_manager("frame-managers-a")
    devops_b = aether._get_devops_manager("frame-managers-b")
    assert devops_a is frame_a.dev_ops_manager
    assert devops_b is frame_b.dev_ops_manager
    assert devops_a is not devops_b

    states_a = aether._get_spell_system_states("frame-managers-a")
    assert states_a is frame_a.spell_system_states

    incident_a = aether._get_incident_manager("frame-managers-a")
    assert incident_a is devops_a.incident_manager

    change_control_a = aether._get_change_control_manager("frame-managers-a")
    assert change_control_a is devops_a.change_control_manager

    mutation_a = aether._get_mutation_research()
    assert mutation_a is aether.mutation_research


def test_aether_spell_versions_drop_after_conduit_cleanup() -> None:
    """
    Purpose:
        Validate Aether version registry reflects conduit cleanup.
    Contract:
        - Bound spell ids appear in Aether version queries.
        - Cleanup removes those spell ids from the frame registry.
    Returns:
        None.
    Raises:
        AssertionError: If Aether version registry is stale after cleanup.
    """
    aether = Aether()
    frame_name = "frame-spell-versions"
    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    service_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    config_id = spellbook.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")

    versions = aether._get_all_spell_versions(frame_name)
    assert service_id in versions
    assert config_id in versions

    conduit.cleanup()

    assert frame_name not in aether._aetheric_frames
    with pytest.raises(ValueError, match="does not exist"):
        aether._get_all_spell_versions(frame_name)
