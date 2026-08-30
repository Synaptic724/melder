import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure each transfer-ownership integration test starts on a clean Aether.
    Contract:
        - Resets the Aether singleton + rebinds Spellbook/Conduit._aether before and
          after the test for isolation.
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
    """Build a dynamic spellbook configuration with one scheduler worker."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def test_transfer_moves_spell_ownership_to_target() -> None:
    """
    Purpose:
        Verify ownership transfer moves a spell from source to target end-to-end after
        the footprint-discovery migration (conduit metadata -> envelope strategy -> ward).
    Contract:
        - The summary reports source/target/spell.
        - The spell's owning conduit becomes the target.
    Returns:
        None.
    Raises:
        AssertionError: If ownership does not move.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    target_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        summary = owner.transfer_spell_ownership(
            spell=spell_id,
            target_conduit=target,
        )

        assert summary["spell_id"] == spell_id
        assert summary["source"] == owner.id
        assert summary["target"] == target.id
        assert owner.get_conduit_by_spell_id(spell_id) is target
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


def test_transfer_flips_meld_resolution_to_target() -> None:
    """
    Purpose:
        Verify meld resolution follows ownership after a transfer: the target can meld
        the spell and the source can no longer resolve it.
    Contract:
        - target.meld returns a built instance.
        - source.meld raises (the spell is no longer owned there).
    Returns:
        None.
    Raises:
        AssertionError: If resolution does not flip to the target.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    target_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        owner.transfer_spell_ownership(spell=spell_id, target_conduit=target)

        assert isinstance(target.meld(spell_id=spell_id), BasicService)
        with pytest.raises(KeyError, match="No spell found"):
            owner.meld(spell_id=spell_id)
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


def test_transfer_moves_only_the_targeted_spell() -> None:
    """
    Purpose:
        Verify a transfer is selective: only the targeted spell moves; the source keeps
        its other owned spells (the footprint targets one lineage, not the whole conduit).
    Contract:
        - The transferred spell's owner becomes the target.
        - A second, untransferred spell remains owned by the source.
    Returns:
        None.
    Raises:
        AssertionError: If an untargeted spell is disturbed.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    config_id = owner_book.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    target_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        owner.transfer_spell_ownership(spell=service_id, target_conduit=target)

        assert owner.get_conduit_by_spell_id(service_id) is target
        assert owner.get_conduit_by_spell_id(config_id) is owner
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()
