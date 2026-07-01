import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig, BasicService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration():
    """Reset the Aether singleton around each test for isolation."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _dynamic_configuration() -> SpellbookConfiguration:
    """Dynamic configuration suitable for link/contract transactions."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _inbound(snapshot) -> list:
    """Inbound spell ids from a get_spells_in_contract_by_conduit snapshot."""
    if not snapshot:
        return []
    return [spell_id for spell_id, _spell in snapshot.get("inbound", [])]


@pytest.fixture
def linked_pair():
    """
    An owner conduit (with two bound services) linked to a borrower conduit.

    Yields:
        (owner, borrower, service_id, config_id) with no transaction active.
    """
    configuration = _dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(spell=BasicService, existence=Existence.unique, permissions="create")
    config_id = owner_book.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")
    borrower_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    owner.link(borrower)
    yield owner, borrower, service_id, config_id
    borrower.cleanup()
    owner.cleanup()


# ---------------------------------------------------------------------------
# add_spell_to_contract -- self-admit and variations
# ---------------------------------------------------------------------------
def test_add_spell_to_contract_standalone_contracts_inbound(linked_pair) -> None:
    """A standalone single add self-admits and contracts the spell inbound."""
    owner, borrower, service_id, _config_id = linked_pair
    assert borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create") is True
    assert service_id in _inbound(borrower.get_spells_in_contract_by_conduit(owner.id))


def test_add_spell_to_contract_by_conduit_id_string(linked_pair) -> None:
    """The standalone add resolves the peer from a conduit_id string."""
    owner, borrower, service_id, _config_id = linked_pair
    assert borrower.add_spell_to_contract(spell_id=service_id, conduit_id=owner.id, permissions="create") is True
    assert service_id in _inbound(borrower.get_spells_in_contract_by_conduit(owner.id))


def test_add_two_spells_one_by_one_standalone(linked_pair) -> None:
    """Two independent standalone adds each self-admit and both land inbound."""
    owner, borrower, service_id, config_id = linked_pair
    assert borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create") is True
    assert borrower.add_spell_to_contract(spell_id=config_id, conduit=owner, permissions="create") is True
    assert set(_inbound(borrower.get_spells_in_contract_by_conduit(owner.id))) == {service_id, config_id}


def test_add_spell_to_contract_read_permission(linked_pair) -> None:
    """A read-permission standalone add still contracts the spell inbound."""
    owner, borrower, service_id, _config_id = linked_pair
    assert borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="read") is True
    assert service_id in _inbound(borrower.get_spells_in_contract_by_conduit(owner.id))


def test_add_spell_to_contract_reuses_open_link_window(linked_pair) -> None:
    """Inside an explicit link window the add runs in that window (reuse path)."""
    owner, borrower, service_id, _config_id = linked_pair
    with borrower.transaction("link", conduits=[borrower, owner]):
        assert borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create") is True
    assert service_id in _inbound(borrower.get_spells_in_contract_by_conduit(owner.id))


def test_add_same_spell_twice_is_stable(linked_pair) -> None:
    """Adding the same spell twice leaves exactly one inbound entry."""
    owner, borrower, service_id, _config_id = linked_pair
    borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create")
    borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create")
    inbound = _inbound(borrower.get_spells_in_contract_by_conduit(owner.id))
    assert inbound.count(service_id) == 1


# ---------------------------------------------------------------------------
# bulk add + lookups
# ---------------------------------------------------------------------------
def test_bulk_add_spells_in_link_window(linked_pair) -> None:
    """Bulk add inside a link window contracts every spell."""
    owner, borrower, service_id, config_id = linked_pair
    with borrower.transaction("link", conduits=[borrower, owner]):
        results = borrower.add_spells_to_contract(spell_ids=[service_id, config_id], conduit=owner, permissions="create")
    assert results == {service_id: True, config_id: True}
    assert set(_inbound(borrower.get_spells_in_contract_by_conduit(owner.id))) == {service_id, config_id}


def test_get_spell_in_contracts_points_to_owner(linked_pair) -> None:
    """After a contract, the reverse lookup resolves the providing conduit."""
    owner, borrower, service_id, _config_id = linked_pair
    borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create")
    spell_in_contract = borrower.get_spell_in_contracts(service_id)
    assert spell_in_contract is not None
    assert spell_in_contract[0] == owner.id


def test_get_contracted_conduits_includes_owner(linked_pair) -> None:
    """The provider appears in the borrower's contracted-conduit set."""
    owner, borrower, service_id, _config_id = linked_pair
    borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create")
    contracted = borrower.get_contracted_conduits()
    assert contracted is not None
    assert any(conduit_id == owner.id for conduit_id, _conduit in contracted)


def test_lookup_by_conduit_name(linked_pair) -> None:
    """Inbound spells are reachable by the provider conduit name."""
    owner, borrower, service_id, _config_id = linked_pair
    borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create")
    by_name = borrower.get_spells_in_contract_by_conduit_name("owner")
    assert service_id in _inbound(by_name)


def test_all_spells_in_contracts_counts_two(linked_pair) -> None:
    """Contracting both services shows two entries for the provider."""
    owner, borrower, service_id, config_id = linked_pair
    borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create")
    borrower.add_spell_to_contract(spell_id=config_id, conduit=owner, permissions="create")
    all_contracts = borrower.get_all_spells_in_contracts(validate=True)
    assert all_contracts is not None
    assert owner.id in all_contracts
    assert len(all_contracts[owner.id]) == 2


# ---------------------------------------------------------------------------
# remove + link/sever
# ---------------------------------------------------------------------------
def test_add_then_remove_spell_in_link_window(linked_pair) -> None:
    """A standalone add followed by an in-window remove clears the spell."""
    owner, borrower, service_id, _config_id = linked_pair
    borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create")
    with borrower.transaction("link", conduits=[borrower, owner]):
        assert borrower.remove_spell_from_contract(spell_id=service_id, conduit=owner) is True
    assert borrower.get_spell_in_contracts(service_id) is None


def test_bulk_remove_spells_in_link_window(linked_pair) -> None:
    """Bulk add then bulk remove leaves nothing inbound."""
    owner, borrower, service_id, config_id = linked_pair
    with borrower.transaction("link", conduits=[borrower, owner]):
        borrower.add_spells_to_contract(spell_ids=[service_id, config_id], conduit=owner, permissions="create")
        results = borrower.remove_spells_from_contract(spell_ids=[service_id, config_id], conduit=owner)
    assert results == {service_id: True, config_id: True}
    assert _inbound(borrower.get_spells_in_contract_by_conduit(owner.id)) == []


def test_link_then_sever_updates_link_lists(linked_pair) -> None:
    """Severing the link removes each conduit from the other's link list."""
    owner, borrower, _service_id, _config_id = linked_pair
    assert borrower in owner.get_links()
    assert owner.sever_link(borrower) is True
    assert borrower not in owner.get_links()
    assert owner not in borrower.get_links()


def test_two_borrowers_borrow_same_spell() -> None:
    """One provider can contract the same spell to two independent borrowers."""
    configuration = _dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(spell=BasicService, existence=Existence.unique, permissions="create")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower_a = Spellbook(configuration=configuration).conjure(dynamic=True, name="a")
    borrower_b = Spellbook(configuration=configuration).conjure(dynamic=True, name="b")
    try:
        owner.link(borrower_a)
        owner.link(borrower_b)
        assert borrower_a.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="read") is True
        assert borrower_b.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="read") is True
        assert service_id in _inbound(borrower_a.get_spells_in_contract_by_conduit(owner.id))
        assert service_id in _inbound(borrower_b.get_spells_in_contract_by_conduit(owner.id))
    finally:
        borrower_a.cleanup()
        borrower_b.cleanup()
        owner.cleanup()
