"""
Integration tests -- index-link FOLLOW-ON dynamics on a SHARED linked index (area F, deep).

The point of the index-link (vs a version-anchored spell contract) is that the
borrower FOLLOWS the lineage. These drive the owner's index operations while the
index is contracted to one or more borrowers and assert the borrower state:

- F3  notch on a shared linked index -> borrower's active borrowed copy switches
      (old parked, new active) and the IndexDetail head moves.
- F4  add a member to a linked index (add_to_spell_index) -> the new member is
      propagated to the borrower as a parked per-member contract.
- F5  remove a member (remove_from_spell_index) -> its per-member contract is dropped
      on the borrower.
- F9  cleanup the sole member -> the index is destroyed -> the borrower drops the
      whole index-link.
- F11 two borrowers -> both follow a notch.

Transactions are OUT OF SCOPE (another agent). Runtime: Python 3.14t; the 3.10
sandbox cannot execute these -> user runs on 3.14t (validate the notch multi-member
harness in `test_spell_index_notch_lifecycle.py` first).
"""

import contextlib
from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _ServiceA:
    def __init__(self) -> None:
        self.tag = "A"


class _ServiceB:
    def __init__(self) -> None:
        self.tag = "B"


class _ServiceC:
    def __init__(self) -> None:
        self.tag = "C"


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_follow() -> None:
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


def _link_index(borrower: Conduit, owner: Conduit, index, permissions: str = "create") -> None:
    with borrower.transaction("link", conduits=[borrower, owner]):
        assert borrower.add_index_to_contract(index=index, conduit=owner, permissions=permissions)


@contextlib.contextmanager
def _two_member_linked() -> Iterator[tuple]:
    """
    Owner with a 2-member index (A active, B inactive), linked to one borrower.
    Yields (owner_book, borrower_book, owner, borrower, id_a, id_b, index, spell_b).
    """
    owner_book = _make_spellbook()
    borrower_book = _make_spellbook()
    id_a = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    owner.link(borrower)
    index = owner_book.find_spell_by_id(id_a).spell_index
    id_b = owner.bind_inactive(  # index = {A, B}, A active
        spell=_ServiceB, spell_index=index, existence=Existence.unique,
        permissions="create", binding_name="b",
    )
    spell_b = owner_book._get_owned_spell(id_b)
    _link_index(borrower, owner, index)
    try:
        yield (owner_book, borrower_book, owner, borrower, id_a, id_b, index, spell_b)
    finally:
        borrower.cleanup()
        owner.cleanup()


@contextlib.contextmanager
def _single_member_linked() -> Iterator[tuple]:
    """Owner with a 1-member index A, linked to one borrower."""
    owner_book = _make_spellbook()
    borrower_book = _make_spellbook()
    id_a = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    owner.link(borrower)
    index = owner_book.find_spell_by_id(id_a).spell_index
    _link_index(borrower, owner, index)
    try:
        yield (owner_book, borrower_book, owner, borrower, id_a, index)
    finally:
        borrower.cleanup()
        owner.cleanup()


# --- F3 notch follows on a shared linked index -----------------------------

def test_link_gives_borrower_active_and_parked_members():
    with _two_member_linked() as (ob, bb, owner, borrower, id_a, id_b, index, spell_b):
        active = bb._contracted_spells_by_id.get(owner._id, {})
        parked = bb._inactive_contracted_spells.get(owner._id, {})
        assert id_a in active     # active member -> live borrowed copy
        assert id_b in parked     # inactive member -> parked borrowed copy


def test_notch_switches_borrower_active_copy():
    with _two_member_linked() as (ob, bb, owner, borrower, id_a, id_b, index, spell_b):
        owner.notch_spell(spell_index=index, spell=spell_b)
        active = bb._contracted_spells_by_id.get(owner._id, {})
        assert id_b in active
        assert id_a not in active


def test_notch_parks_borrower_old_copy():
    with _two_member_linked() as (ob, bb, owner, borrower, id_a, id_b, index, spell_b):
        owner.notch_spell(spell_index=index, spell=spell_b)
        parked = bb._inactive_contracted_spells.get(owner._id, {})
        assert id_a in parked


def test_notch_moves_index_detail_head_on_borrower_contract():
    with _two_member_linked() as (ob, bb, owner, borrower, id_a, id_b, index, spell_b):
        owner.notch_spell(spell_index=index, spell=spell_b)
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        index_detail = contract._get_index_detail_map(owner._conduit_ward)[index.id]
        assert index_detail.selected_spell_id == id_b


# --- F4 add member propagates to the borrower ------------------------------

def test_add_member_to_linked_index_propagates_parked_copy():
    with _single_member_linked() as (ob, bb, owner, borrower, id_a, index):
        # Stage a new inactive member C directly onto the linked index
        # (bind_inactive attaches C to an existing index; it cannot stand alone).
        id_c = owner.bind_inactive(
            spell=_ServiceC, spell_index=index, existence=Existence.unique,
            permissions="create", binding_name="c",
        )
        spell_c = ob._get_owned_spell(id_c)
        # The borrower now carries C as a per-member contract (parked copy) + a Detail.
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        assert contract._check_if_exists(owner._conduit_ward, id_c) is True
        parked = bb._inactive_contracted_spells.get(owner._id, {})
        assert id_c in parked


# --- F5 remove member drops it on the borrower -----------------------------

def test_remove_member_from_linked_index_drops_borrower_copy():
    with _two_member_linked() as (ob, bb, owner, borrower, id_a, id_b, index, spell_b):
        # B is an inactive member of the linked index; split it out.
        owner.remove_from_spell_index(spell=spell_b, source_index=index)
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        assert contract._check_if_exists(owner._conduit_ward, id_b) is False
        parked = bb._inactive_contracted_spells.get(owner._id, {})
        assert id_b not in parked


# --- F9 destroy cascade via cleanup ----------------------------------------

def test_cleanup_sole_member_destroys_borrower_index_link():
    with _single_member_linked() as (ob, bb, owner, borrower, id_a, index):
        index_id = index.id
        owner.cleanup_spell(spell=ob.find_spell_by_id(id_a))
        # The lineage is dead -> the borrower drops the whole index-link + member.
        assert index_id not in bb._contracted_indexes
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        assert contract._check_index_exists(owner._conduit_ward, index_id) is False
        assert contract._check_if_exists(owner._conduit_ward, id_a) is False


# --- F11 multi-borrower both follow ----------------------------------------

def test_two_borrowers_both_follow_a_notch():
    owner_book = _make_spellbook()
    b1_book = _make_spellbook()
    b2_book = _make_spellbook()
    id_a = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    owner = owner_book.conjure(dynamic=True, name="owner")
    b1 = b1_book.conjure(dynamic=True, name="b1")
    b2 = b2_book.conjure(dynamic=True, name="b2")
    owner.link(b1)
    owner.link(b2)
    index = owner_book.find_spell_by_id(id_a).spell_index
    id_b = owner.bind_inactive(
        spell=_ServiceB, spell_index=index, existence=Existence.unique,
        permissions="create", binding_name="b",
    )
    spell_b = owner_book._get_owned_spell(id_b)
    _link_index(b1, owner, index)
    _link_index(b2, owner, index)
    try:
        owner.notch_spell(spell_index=index, spell=spell_b)
        for book in (b1_book, b2_book):
            active = book._contracted_spells_by_id.get(owner._id, {})
            assert id_b in active
            assert id_a not in active
    finally:
        b1.cleanup()
        b2.cleanup()
        owner.cleanup()
