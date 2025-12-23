from __future__ import annotations

import pytest

from melder.aether.aether import Aether
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


def test_spellbook_integration_config_shared_and_locked() -> None:
    """
    Purpose:
        Validate configuration sharing and locking across Spellbooks in a frame.
    Contract:
        - Conjuring a Spellbook freezes and binds the configuration.
        - A second Spellbook in the same frame adopts the same configuration.
        - Frozen configuration rejects mutation attempts.
    Returns:
        None.
    Raises:
        AssertionError: If configuration sharing or locking fails.
    """
    spellbook = Spellbook(aetheric_frame="shared-frame")
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        assert spellbook.is_configuration_locked() is True

        sibling = Spellbook(aetheric_frame="shared-frame")
        sibling_config = sibling.get_configuration()
        assert sibling_config is config
        assert sibling.is_configuration_locked() is True

        with pytest.raises(RuntimeError, match="frozen"):
            sibling_config.set_property("phase_scheduler_workers_per_spellbook", 2)

        instance = conduit.meld(spell=spell_id)
        assert isinstance(instance, BasicService)
    finally:
        conduit.cleanup()


def test_spellbook_integration_create_new_preset_spellbook_shares_config() -> None:
    """
    Purpose:
        Validate preset Spellbook creation preserves frame and configuration.
    Contract:
        - Preset Spellbook reuses the existing configuration object.
        - Preset Spellbook can bind and conjure distinct spells.
    Returns:
        None.
    Raises:
        AssertionError: If preset Spellbook integration fails.
    """
    spellbook = Spellbook(aetheric_frame="preset-frame")
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    preset = spellbook.create_new_preset_spellbook()
    assert preset.get_configuration() is config

    preset_spell_id = preset.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = preset.conjure(name="preset-root")
    try:
        instance = conduit.meld(spell=preset_spell_id)
        assert isinstance(instance, BasicConfig)
    finally:
        conduit.cleanup()


def test_spellbook_integration_create_binder_fluent_bind_and_meld() -> None:
    """
    Purpose:
        Validate SpellBinder fluent binding through Spellbook integration.
    Contract:
        - Fluent binding returns a usable spell_id.
        - Conduit.meld resolves the bound spell.
    Returns:
        None.
    Raises:
        AssertionError: If fluent binding fails to resolve.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    binder = spellbook.create_binder()
    spell_id = binder.bind(BasicService).as_unique().finalize()

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(spell=spell_id)
        assert isinstance(instance, BasicService)
        assert instance.marker == "service"
    finally:
        conduit.cleanup()


def test_spellbook_integration_inspect_spell_returns_registered_id() -> None:
    """
    Purpose:
        Validate Spellbook.inspect_spell returns a registered spell id.
    Contract:
        - Inspecting a bound existing instance returns its spell_id.
        - Meld returns the same instance for existing-object spells.
    Returns:
        None.
    Raises:
        AssertionError: If inspect_spell fails to resolve the id.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    existing = BasicConfig()
    spell_id = spellbook.bind(
        spell=existing,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        inspected = spellbook.inspect_spell(existing)
        assert inspected == spell_id

        resolved = conduit.meld(spell=spell_id)
        assert resolved is existing
    finally:
        conduit.cleanup()


def test_spellbook_integration_contracted_spells_visible() -> None:
    """
    Purpose:
        Validate Spellbook contracted spell visibility after linking conduits.
    Contract:
        - Borrower Spellbook records contracted spell entries by conduit id.
        - Contracted spells can be melded via the borrower conduit.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spells are not visible or resolvable.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        borrower.add_spell_to_contract(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
        )

        contracted = borrower_book.contracted_spells.get(owner.id)
        assert contracted is not None
        assert any(
            spell_index.has_version(spell_id) for spell_index in contracted.keys()
        )

        instance = borrower.meld(spell=spell_id)
        assert isinstance(instance, BasicService)
    finally:
        borrower.cleanup()
        owner.cleanup()
