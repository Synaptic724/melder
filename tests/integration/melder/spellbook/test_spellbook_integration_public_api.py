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


def test_spellbook_public_api_get_configuration_returns_same_instance() -> None:
    """
    Purpose:
        Validate get_configuration returns a stable configuration instance.
    Contract:
        - Multiple calls return the same configuration object.
    Returns:
        None.
    Raises:
        AssertionError: If configuration object changes.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    assert config is spellbook.get_configuration()


def test_spellbook_public_api_id_and_spells_mapping_read_only() -> None:
    """
    Purpose:
        Validate id and spells mapping behavior for local bindings.
    Contract:
        - id returns a non-empty string.
        - spells mapping contains the bound spell.
        - spells mapping is read-only.
    Returns:
        None.
    Raises:
        AssertionError: If id is empty, spell is missing, or map is writable.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    assert isinstance(spellbook.id, str)
    assert spellbook.id != ""

    spells = spellbook.spells
    assert any(spell_index.has_version(spell_id) for spell_index in spells.keys())

    spell_index = next(iter(spells.keys()))
    with pytest.raises(TypeError):
        spells[spell_index] = None


def test_spellbook_public_api_contracted_spells_mapping_read_only() -> None:
    """
    Purpose:
        Validate contracted_spells mapping is read-only and populated.
    Contract:
        - Contracted spells appear under the owner conduit id.
        - Contracted spell maps are immutable.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spells are missing or mutable.
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
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_spell_to_contract(
                spell_id=spell_id,
                conduit=owner,
                permissions="create",
            )

        contracted = borrower_book.contracted_spells
        assert owner.id in contracted
        spell_map = contracted[owner.id]
        assert any(spell_index.has_version(spell_id) for spell_index in spell_map.keys())

        with pytest.raises(TypeError):
            contracted[owner.id] = {}

        spell_index = next(iter(spell_map.keys()))
        with pytest.raises(TypeError):
            spell_map[spell_index] = None
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spellbook_public_api_find_spell_index_and_key_raise_when_missing() -> None:
    """
    Purpose:
        Validate lookup APIs raise when a spell is missing.
    Contract:
        - find_spell_index raises RuntimeError for unknown spells.
        - find_spell_key raises RuntimeError for unknown spells.
    Returns:
        None.
    Raises:
        AssertionError: If missing lookups do not raise.
    """
    spellbook = Spellbook()
    with pytest.raises(RuntimeError, match="Spell not found"):
        spellbook.find_spell_index("missing", "MissingSpell", "__default__")
    with pytest.raises(RuntimeError, match="Spell key not found"):
        spellbook.find_spell_key("missing", "MissingSpell", "__default__")


def test_spellbook_public_api_get_spell_permissions_raises_for_unknown_index() -> None:
    """
    Purpose:
        Validate get_spell_permissions rejects foreign spell indexes.
    Contract:
        - Passing an unknown SpellIndex raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If permissions resolve for an unknown spell.
    """
    owner_book = Spellbook(aetheric_frame="frame-a")
    config = owner_book.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    foreign_index = next(iter(owner_book.spells.keys()))

    other_book = Spellbook(aetheric_frame="frame-b")
    with pytest.raises(RuntimeError, match="not found in the spellbook"):
        other_book.get_spell_permissions(foreign_index)


def test_spellbook_public_api_inspect_spell_returns_none_when_unregistered() -> None:
    """
    Purpose:
        Validate inspect_spell returns None for unregistered spells.
    Contract:
        - Unregistered classes or objects return None.
    Returns:
        None.
    Raises:
        AssertionError: If an unregistered spell resolves to an id.
    """
    spellbook = Spellbook()
    assert spellbook.inspect_spell(BasicConfig) is None
