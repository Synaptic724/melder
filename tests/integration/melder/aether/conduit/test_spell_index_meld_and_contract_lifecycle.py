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
from typing import Callable, Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.contract_classes import ContractServicePrimary
from tests.mocks.spellbook.contract_classes import ContractServiceSecondary
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
    index = owner_book.find_spell_by_spell_id(service_id).spell_index
    try:
        yield (owner_book, borrower_book, owner, borrower, service_id, index)
    finally:
        borrower.cleanup()
        owner.cleanup()


# --- baseline: bind + meld -------------------------------------------------

def test_bind_then_meld_returns_instance():
    with _owner_only() as (book, owner, service_id):
        instance = owner.meld(spell_id=service_id)
        assert isinstance(instance, ContractServicePrimary)


def test_meld_by_positional_spell_id():
    with _owner_only() as (book, owner, service_id):
        assert isinstance(owner.meld(spell_id=service_id), ContractServicePrimary)


# --- spell contract lifecycle ----------------------------------------------

def test_add_spell_contract_lets_borrower_meld_borrowed_spell():
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id, conduit=owner, permissions="create",
            )
        assert borrower.validate_contracts_and_define()
        instance = borrower.meld(spell_id=service_id)
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
        instance = borrower.meld(spell_id=service_id)
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


# --- one version, one copy (contracted_copy_removal_by_version_2026_10_16) -------------------------------------

def _stage_secondary(owner: Conduit, index: SpellIndex) -> str:
    """
    Purpose:
        Stage ContractServiceSecondary as a parked version of the service index, under the same frame and binding
        name, and return its spell_id.
    """
    return owner.bind_inactive(
        spell=ContractServiceSecondary,
        spell_index=index,
        spellframe=IService,
        binding_name="primary",
        existence=Existence.unique,
        permissions="create",
    )


def _members_in_order(order: list[str]) -> Callable[[SpellIndex], list[str]]:
    """
    Purpose:
        Build a stand-in for `SpellIndex.spells_in_index` that returns the members in `order` (members not named
        come last), so a test fixes the order an index unlink visits them in. The real method runs first, so a
        cleaned index raises as it does.
    """
    real = SpellIndex.spells_in_index

    def ordered(index: SpellIndex) -> list[str]:
        members = real(index)
        return sorted(members, key=lambda member_id: order.index(member_id) if member_id in order else len(order))

    return ordered


@pytest.mark.parametrize("first", ["parked", "active"])
def test_remove_index_contract_after_a_notch_removes_each_members_copy_in_either_order(
        monkeypatch: pytest.MonkeyPatch, first: str,
) -> None:
    """
    Purpose:
        After the owner notches a linked index to a version staged on it, unlinking the index removes every member's
        own copy - the old version's parked copy and the new version's active one - whichever member the unlink
        visits first. The member set's order follows the hash seed, so the test fixes each order. Until 0.2.8251
        the parked-first order removed the active copy under the parked member's id, then raised RuntimeError
        "Spell version <id> not found for conduit ID <owner>." and left the parked copy behind.
    """
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")
        staged_id = _stage_secondary(owner, index)
        owner.notch_spell(spell_index=index, spell_id=staged_id)
        assert set(borrower_book._contracted_spells_by_id.get(owner._id, {})) == {staged_id}
        assert set(borrower_book._inactive_contracted_spells.get(owner._id, {})) == {service_id}

        order = [service_id, staged_id] if first == "parked" else [staged_id, service_id]
        with monkeypatch.context() as patch:
            patch.setattr(SpellIndex, "spells_in_index", _members_in_order(order), raising=True)
            with borrower.transaction("link", conduits=[borrower, owner]):
                borrower.remove_index_from_contract(index_id=index.id, conduit=owner)

        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        assert contract._check_index_exists(owner._conduit_ward, index.id) is False
        assert contract._check_if_exists(owner._conduit_ward, service_id) is False
        assert contract._check_if_exists(owner._conduit_ward, staged_id) is False
        assert index.id not in borrower_book._contracted_indexes
        assert borrower_book._contracted_spells_by_id.get(owner._id, {}) == {}
        assert borrower_book._inactive_contracted_spells.get(owner._id, {}) == {}


def test_removing_a_parked_version_grant_keeps_the_active_versions_copy() -> None:
    """
    Purpose:
        A borrower granted a version that its owner then notched away from, and granted the new version too, removes
        only the old version's parked copy when that grant goes, and still melds the new version. Until 0.2.8251 the
        removal took the new version's active copy instead and left the old one parked.
    """
    with _linked_pair() as (owner_book, borrower_book, owner, borrower, service_id, index):
        primary_spell = owner.get_spell_by_spell_id(service_id)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(spell_id=service_id, conduit=owner, permissions="create")
        staged_id = _stage_secondary(owner, index)
        owner.notch_spell(spell_index=index, spell_id=staged_id)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(spell_id=staged_id, conduit=owner, permissions="create")
        assert set(borrower_book._contracted_spells_by_id.get(owner._id, {})) == {staged_id}
        assert set(borrower_book._inactive_contracted_spells.get(owner._id, {})) == {service_id}

        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.remove_spell_from_contract(spell=primary_spell, conduit=owner)

        assert set(borrower_book._contracted_spells_by_id.get(owner._id, {})) == {staged_id}
        assert service_id not in borrower_book._inactive_contracted_spells.get(owner._id, {})
        assert borrower.validate_contracts_and_define()
        assert isinstance(borrower.meld(spell_id=staged_id), ContractServiceSecondary)
