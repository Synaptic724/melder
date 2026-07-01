"""
Integration tests -- meld + contract + index-contract LIFECYCLE (deep, behavioral).

Answers the "what actually happens" questions end to end on real dynamic conduits:
- bind a spell and meld it (baseline resolution),
- add a SPELL contract -> the borrower can meld the borrowed spell; remove it ->
  the borrower can no longer resolve it,
- add an INDEX contract (the new SpellIndex-contract) -> the borrower resolves the
  index's active member; remove it -> resolution is gone.

Transactions are intentionally OUT OF SCOPE here (a separate agent owns the
transaction-strategy tests): these drive the public conduit facades, which manage
their own change-control windows, and assert only the behavioral outcomes.

Runtime: Python 3.14t. Authored on a 3.10 sandbox that cannot execute them (no
pytest + modules need 3.14 deferred annotations) -> user runs on 3.14t. Validate
this file first; it is the harness for the deeper notch/add/remove-index tranche.
"""

import contextlib
from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.contract_classes import ContractServicePrimary
from tests.mocks.spellbook.protocols import IService

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_lifecycle() -> None:
    """Clean Aether singleton around each test; rebind the class refs."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    config = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=config)


def _bind_service(book: Spellbook, binding_name: str = "primary") -> str:
    return book.bind(
        spell=ContractServicePrimary,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name=binding_name,
    )


@contextlib.contextmanager
def _owner_only() -> Iterator[tuple]:
    """One dynamic owner conduit with a single bound service."""
    book = _make_spellbook()
    service_id = _bind_service(book)
    owner = book.conjure(dynamic=True, name="owner")
    try:
        yield (book, owner, service_id)
    finally:
        owner.cleanup()


@contextlib.contextmanager
def _linked_pair() -> Iterator[tuple]:
    """Owner (with a bound service) linked to a borrower; yields both + the index."""
    owner_book = _make_spellbook()
    borrower_book = _make_spellbook()
    service_id = _bind_service(owner_book)
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    owner.link(borrower)
    index = owner_book.find_spell_by_id(service_id).spell_index
    try:
        yield (owner_book, borrower_book, owner, borrower, service_id, index)
    finally:
        borrower.cleanup()
        owner.cleanup()


# --- baseline: bind + meld -------------------------------------------------

def test_bind_then_meld_returns_instance():
    with _owner_only() as (book, owner, service_id):
        instance = owner.meld(spell=service_id)
        assert isinstance(instance, ContractServicePrimary)


def test_meld_by_positional_spell_id():
    with _owner_only() as (book, owner, service_id):
        assert isinstance(owner.meld(service_id), ContractServicePrimary)


# --- spell contract lifecycle ----------------------------------------------

def test_add_spell_contract_lets_borrower_meld_borrowed_spell():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id, conduit=owner, permissions="create",
            )
        assert borrower.validate_contracts_and_define()
        instance = borrower.meld(spell=service_id)
        assert isinstance(instance, ContractServicePrimary)


def test_borrower_tracks_contracted_spell_after_add():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create")
        active_by_id = borrower_book._contracted_spells_by_id.get(owner._id, {})
        assert service_id in active_by_id


def test_remove_spell_contract_drops_borrower_visibility():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create")
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.remove_spell_from_contract(spell_id=service_id, conduit=owner)
        active_by_id = borrower_book._contracted_spells_by_id.get(owner._id, {})
        assert service_id not in active_by_id


# --- index contract lifecycle (the new SpellIndex-contract) ----------------

def test_add_index_contract_lets_borrower_meld_active_member():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")
        assert borrower.validate_contracts_and_define()
        instance = borrower.meld(spell=service_id)
        assert isinstance(instance, ContractServicePrimary)


def test_index_contract_records_index_and_member():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        assert contract._check_index_exists(owner._conduit_ward, index.id) is True
        assert contract._check_if_exists(owner._conduit_ward, service_id) is True
        assert index.id in borrower_book._contracted_indexes


def test_remove_index_contract_drops_borrower_index_and_member():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.remove_index_from_contract(index_id=index.id, conduit=owner)
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        assert contract._check_index_exists(owner._conduit_ward, index.id) is False
        assert index.id not in borrower_book._contracted_indexes
        active_by_id = borrower_book._contracted_spells_by_id.get(owner._id, {})
        assert service_id not in active_by_id
