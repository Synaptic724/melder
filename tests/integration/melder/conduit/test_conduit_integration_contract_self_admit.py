from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration():
    """
    Purpose:
        Ensure each test starts and ends with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton and rebinds Spellbook/Conduit before and
          after the test for isolation.
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
    """Create a dynamic configuration suitable for link/contract tests."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _inbound_spell_ids(snapshot) -> list:
    """Extract inbound spell ids from a get_spells_in_contract_by_conduit snapshot."""
    if not snapshot:
        return []
    return [spell_id for spell_id, _spell in snapshot.get("inbound", [])]


def _linked_owner_and_borrower():
    """
    Build an owner conduit (with one bound service) linked to a borrower conduit.

    Returns:
        Tuple of (owner_conduit, borrower_conduit, service_spell_id).
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    owner.link(borrower)
    return owner, borrower, service_id


def test_add_spell_to_contract_self_admits_without_an_explicit_link_window() -> None:
    """
    Purpose:
        Verify a single add_spell_to_contract now self-admits its own
        add_spell_or_index_to_contract transaction when called standalone --
        without the caller opening a link transaction window first.
    Contract:
        - The standalone add returns True and the spell appears inbound in the
          borrower's contract with the owner.
    Returns:
        None.
    Raises:
        AssertionError: If the standalone add does not admit or contract.
    """
    owner, borrower, service_id = _linked_owner_and_borrower()
    try:
        # No `with borrower.transaction("link", ...)` wrapper: the single add
        # self-admits its own contract transaction.
        assert borrower.add_spell_to_contract(
            spell_id=service_id,
            conduit=owner,
            permissions="create",
        ) is True

        inbound = _inbound_spell_ids(
            borrower.get_spells_in_contract_by_conduit(owner.id)
        )
        assert service_id in inbound
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_add_spell_to_contract_still_reuses_an_active_link_window() -> None:
    """
    Purpose:
        Verify the reuse path is unchanged: when a link transaction window is
        already open, add_spell_to_contract runs inside it rather than opening a
        second transaction.
    Contract:
        - The add inside an explicit link window returns True and contracts the
          spell, exactly as before the self-admit change.
    Returns:
        None.
    Raises:
        AssertionError: If the in-window add does not admit or contract.
    """
    owner, borrower, service_id = _linked_owner_and_borrower()
    try:
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            ) is True

        inbound = _inbound_spell_ids(
            borrower.get_spells_in_contract_by_conduit(owner.id)
        )
        assert service_id in inbound
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_add_spell_to_contract_requires_a_peer_conduit() -> None:
    """
    Purpose:
        Verify the standalone add still needs a resolvable peer conduit; a
        contract mutation with no target cannot seal the far side.
    Contract:
        - Calling add_spell_to_contract with neither conduit nor conduit_id
          raises rather than silently self-admitting against nothing.
    Returns:
        None.
    Raises:
        AssertionError: If the missing-peer call does not raise.
    """
    owner, borrower, service_id = _linked_owner_and_borrower()
    try:
        with pytest.raises(Exception):
            borrower.add_spell_to_contract(
                spell_id=service_id,
                permissions="create",
            )
    finally:
        borrower.cleanup()
        owner.cleanup()
