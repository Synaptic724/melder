from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame import AethericFrame
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
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


def test_aether_ensure_frame_rejects_non_string() -> None:
    """
    Purpose:
        Validate _ensure_frame rejects non-string frame names.
    Contract:
        - TypeError is raised for non-string frame names.
    Returns:
        None.
    Raises:
        AssertionError: If non-string inputs do not raise.
    """
    aether = Aether()
    with pytest.raises(TypeError, match="aetheric_frame_name"):
        aether._ensure_frame(123)


def test_unregistered_frame_cleanup_is_noop_for_aether_registry() -> None:
    """
    Purpose:
        Validate direct cleanup of an unregistered frame is a no-op for Aether.
    Contract:
        - Missing frame cleanup does not raise.
        - Default frame remains available.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup mutates default frame state.
    """
    aether = Aether()
    frame = AethericFrame(Aether(), "missing-frame")
    frame.cleanup()
    aether._ensure_default_frame()
    assert aether._default_frame is not None


def test_aether_conduit_lookup_missing_frame_raises() -> None:
    """
    Purpose:
        Validate conduit lookups reject missing frames.
    Contract:
        - _get_conduit_by_id raises ValueError for missing frames.
        - _get_conduit_by_name raises ValueError for missing frames.
    Returns:
        None.
    Raises:
        AssertionError: If missing-frame lookups do not raise.
    """
    aether = Aether()
    with pytest.raises(ValueError, match="does not exist"):
        aether._get_conduit_by_id("id", "missing-frame")
    with pytest.raises(ValueError, match="does not exist"):
        aether._get_conduit_by_name("name", "missing-frame")


def test_aether_conduit_cloud_register_unregister_missing_frame_raises() -> None:
    """
    Purpose:
        Validate conduit cloud operations reject missing frames.
    Contract:
        - Register/unregister calls raise ValueError for missing frames.
    Returns:
        None.
    Raises:
        AssertionError: If missing-frame operations do not raise.
    """
    aether = Aether()
    with pytest.raises(ValueError, match="does not exist"):
        aether._register_conduit_cloud(conduit=object(), aetheric_frame_name="missing-frame")
    with pytest.raises(ValueError, match="does not exist"):
        aether._unregister_conduit_cloud(conduit=object(), aetheric_frame_name="missing-frame")


def test_aether_get_all_spell_versions_missing_frame_raises() -> None:
    """
    Purpose:
        Validate _get_all_spell_versions rejects missing frames.
    Contract:
        - ValueError is raised when the frame is missing.
    Returns:
        None.
    Raises:
        AssertionError: If missing-frame lookups do not raise.
    """
    aether = Aether()
    with pytest.raises(ValueError, match="does not exist"):
        aether._get_all_spell_versions("missing-frame")


def test_aether_add_spells_to_aether_rejects_invalid_type() -> None:
    """
    Purpose:
        Validate _add_spells_to_aether enforces SpellIndex types.
    Contract:
        - TypeError is raised when the set contains non-SpellIndex values.
    Returns:
        None.
    Raises:
        AssertionError: If type validation does not raise.
    """
    aether = Aether()
    frame_name = "frame-type-check"
    aether._ensure_frame(frame_name)
    with pytest.raises(TypeError, match="SpellIndex"):
        aether._add_spells_to_aether("conduit-id", {"bad"}, frame_name)


def test_aether_remove_spells_from_aether_missing_conduit_noop() -> None:
    """
    Purpose:
        Validate _remove_spells_from_aether ignores unknown conduit ids.
    Contract:
        - Removing spells for a missing conduit does not raise.
    Returns:
        None.
    Raises:
        AssertionError: If missing-conduit removal raises.
    """
    aether = Aether()
    frame_name = "frame-remove-noop"
    aether._ensure_frame(frame_name)
    aether._remove_spells_from_aether("missing-id", set(), frame_name)


def test_aether_default_frame_spell_lookup_works() -> None:
    """
    Purpose:
        Validate default-frame spell lookup by id.
    Contract:
        - _get_conduit_by_spell_id resolves the owning conduit in default frame.
    Returns:
        None.
    Raises:
        AssertionError: If default-frame lookup fails.
    """
    spellbook = Spellbook(
        configuration=_make_configuration(),
    )
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    aether = Aether()
    try:
        assert aether._get_conduit_by_spell_id(spell_id, "default") is conduit
    finally:
        conduit.cleanup()
        spellbook.cleanup()

def test_aether_change_control_clear_pending_change_missing_noop() -> None:
    """
    Purpose:
        Validate clearing a missing pending change is a no-op.
    Contract:
        - clear_pending_change does not raise for unknown ids.
    Returns:
        None.
    Raises:
        AssertionError: If clearing a missing change raises.
    """
    frame_name = "frame-clear-noop"
    book = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    aether = Aether()
    ccm = aether._get_change_control_manager(frame_name)
    ccm.clear_pending_change("missing-index-id")
    assert ccm.list_pending_changes() == {}
    book.cleanup()


def test_aether_spell_system_states_getters_missing_return_none() -> None:
    """
    Purpose:
        Validate SpellSystemStates returns None for unknown ids.
    Contract:
        - get_by_index_id and get_by_spell_id return None for missing keys.
    Returns:
        None.
    Raises:
        AssertionError: If missing keys do not return None.
    """
    frame_name = "frame-states-missing"
    aether = Aether()
    aether._ensure_frame(frame_name)
    states = aether._get_spell_system_states(frame_name)
    assert states.get_by_index_id("missing") is None
    assert states.get_by_spell_id("missing") is None


def test_aether_register_single_spell_index_missing_frame_raises() -> None:
    """
    Purpose:
        Validate _register_single_spell_index rejects missing frames.
    Contract:
        - ValueError is raised when the frame does not exist.
    Returns:
        None.
    Raises:
        AssertionError: If missing-frame registration does not raise.
    """
    book = Spellbook(configuration=_make_configuration())
    book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    spell_index = next(iter(book._spells.keys()))
    aether = Aether()
    with pytest.raises(ValueError, match="does not exist"):
        aether._register_single_spell_index("cid", spell_index, "missing-frame")
    book.cleanup()


def test_aether_remove_single_spell_index_missing_frame_raises() -> None:
    """
    Purpose:
        Validate _remove_single_spell_index rejects missing frames.
    Contract:
        - ValueError is raised when the frame does not exist.
    Returns:
        None.
    Raises:
        AssertionError: If missing-frame removal does not raise.
    """
    book = Spellbook(configuration=_make_configuration())
    book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    spell_index = next(iter(book._spells.keys()))
    aether = Aether()
    with pytest.raises(ValueError, match="does not exist"):
        aether._remove_single_spell_index("cid", spell_index, "missing-frame")
    book.cleanup()


def test_aether_get_conduit_by_spell_id_missing_frame_raises() -> None:
    """
    Purpose:
        Validate _get_conduit_by_spell_id rejects missing frames.
    Contract:
        - ValueError is raised when the frame does not exist.
    Returns:
        None.
    Raises:
        AssertionError: If missing-frame lookup does not raise.
    """
    aether = Aether()
    with pytest.raises(ValueError, match="does not exist"):
        aether._get_conduit_by_spell_id("spell-id", "missing-frame")


def test_aether_conduit_cloud_missing_name_raises() -> None:
    """
    Purpose:
        Validate conduit cloud registration rejects conduits without names.
    Contract:
        - Register/unregister raise ValueError when conduit.name is None.
    Returns:
        None.
    Raises:
        AssertionError: If unnamed conduits are accepted.
    """
    frame_name = "frame-cloud-missing-name"
    book = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure()
    aether = Aether()
    try:
        with pytest.raises(ValueError, match="cannot be None"):
            aether._register_conduit_cloud(conduit, frame_name)
        with pytest.raises(ValueError, match="cannot be None"):
            aether._unregister_conduit_cloud(conduit, frame_name)
    finally:
        conduit.cleanup()
        book.cleanup()


def test_aether_conduit_cloud_duplicate_name_raises() -> None:
    """
    Purpose:
        Validate duplicate conduit names are rejected in ConduitCloud.
    Contract:
        - Second conduit with same name raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate names are allowed.
    """
    frame_name = "frame-cloud-dup"
    configuration = _make_configuration(aether_frame=frame_name, dynamic=True)
    book_a = Spellbook(
        aetheric_frame=frame_name,
        configuration=configuration,
    )
    book_a.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_a = book_a.conjure(automatic=False, name="root")
    try:
        book_b = Spellbook(aetheric_frame=frame_name)
        book_b.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )
        with pytest.raises(ValueError, match="already exists"):
            book_b.conjure(automatic=False, name="root")
        book_b.cleanup()
    finally:
        conduit_a.cleanup()
        book_a.cleanup()
