"""
Integration tests -- cross-conduit meld through the index-link + behavior probes.

Final fill for area F + the open-question probes (O): the borrower actually RESOLVES
through the index-link (and follows a notch), the guards don't over-fire on non-member
spells, existence spreads lineage-wide, and the reachable open-questions are pinned.

Transactions are OUT OF SCOPE. Runtime: Python 3.14t; the 3.10 sandbox cannot run
these -> user runs on 3.14t.
"""

import contextlib
from typing import Any, Iterator

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


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_meld_probes() -> None:
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


def _resolves(conduit: Conduit, spell_id: str) -> bool:
    try:
        return conduit.meld(spell=spell_id) is not None
    except Exception:
        return False


@contextlib.contextmanager
def _single_linked(permission: str = "create") -> Iterator[tuple]:
    owner_book = _make_spellbook()
    borrower_book = _make_spellbook()
    id_a = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    owner.link(borrower)
    index = owner_book.find_spell_by_id(id_a).spell_index
    with borrower.transaction("link", conduits=[borrower, owner]):
        borrower.add_index_to_contract(index=index, conduit=owner, permissions=permission)
    try:
        yield (owner_book, borrower_book, owner, borrower, id_a, index)
    finally:
        borrower.cleanup()
        owner.cleanup()


@contextlib.contextmanager
def _two_member_linked() -> Iterator[tuple]:
    owner_book = _make_spellbook()
    borrower_book = _make_spellbook()
    id_a = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    owner.link(borrower)
    index = owner_book.find_spell_by_id(id_a).spell_index
    id_b = owner.bind_inactive(
        spell=_ServiceB, spell_index=index, existence=Existence.unique,
        permissions="create", binding_name="b",
    )
    spell_b = owner_book._get_owned_spell(id_b)
    with borrower.transaction("link", conduits=[borrower, owner]):
        borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")
    try:
        yield (owner_book, borrower_book, owner, borrower, id_a, id_b, index, spell_b)
    finally:
        borrower.cleanup()
        owner.cleanup()


# --- cross-conduit meld through the index-link -----------------------------

def test_borrower_melds_active_member_through_index_link():
    with _single_linked("create") as (ob, bb, owner, borrower, id_a, index):
        assert borrower.validate_contracts_and_define()
        assert isinstance(borrower.meld(spell=id_a), _ServiceA)


def test_borrower_loses_meld_after_index_unlink():
    with _single_linked("create") as (ob, bb, owner, borrower, id_a, index):
        borrower.validate_contracts_and_define()
        assert _resolves(borrower, id_a) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.remove_index_from_contract(index_id=index.id, conduit=owner)
        assert _resolves(borrower, id_a) is False


def test_borrower_melds_new_active_after_owner_notch():
    with _two_member_linked() as (ob, bb, owner, borrower, id_a, id_b, index, spell_b):
        owner.notch_spell(spell_index=index, spell=spell_b)
        assert borrower.validate_contracts_and_define()
        assert isinstance(borrower.meld(spell=id_b), _ServiceB)


# --- existence spreads lineage-wide ----------------------------------------

def test_index_link_spreads_member_existence_to_borrower():
    with _two_member_linked() as (ob, bb, owner, borrower, id_a, id_b, index, spell_b):
        existing = bb._contracted_spell_ids.get(owner._id, set())
        assert id_a in existing
        assert id_b in existing


# --- guards do not over-fire on non-member spells --------------------------

def test_removal_guard_allows_non_index_member_spell():
    # A spell contracted directly (NOT via an index-link) is removable normally.
    owner_book = _make_spellbook()
    borrower_book = _make_spellbook()
    sid = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    owner.link(borrower)
    try:
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_spell_to_contract(spell_id=sid, conduit=owner, permissions="create")
        with borrower.transaction("link", conduits=[borrower, owner]):
            # No index-link governs this spell -> the guard does not fire.
            borrower.remove_spell_from_contract(spell_id=sid, conduit=owner)
        active = borrower_book._contracted_spells_by_id.get(owner._id, {})
        assert sid not in active
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_removal_guard_raises_for_index_member():
    with _single_linked("create") as (ob, bb, owner, borrower, id_a, index):
        with pytest.raises(RuntimeError):
            with borrower.transaction("link", conduits=[borrower, owner]):
                borrower.remove_spell_from_contract(spell_id=id_a, conduit=owner)


# --- ownership / staging probes --------------------------------------------

def test_add_index_to_contract_rejects_index_not_owned_by_target():
    # Build a foreign index owned by a THIRD spellbook; linking it via `owner`
    # (which does not own it) must be refused.
    owner_book = _make_spellbook()
    borrower_book = _make_spellbook()
    foreign_book = _make_spellbook()
    foreign_id = foreign_book.bind(spell=_ServiceB, existence=Existence.unique, permissions="create", binding_name="f")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    foreign_book.conjure(dynamic=True, name="foreign")
    owner.link(borrower)
    foreign_index = foreign_book.find_spell_by_id(foreign_id).spell_index
    try:
        with pytest.raises(RuntimeError):
            with borrower.transaction("link", conduits=[borrower, owner]):
                borrower.add_index_to_contract(index=foreign_index, conduit=owner, permissions="create")
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_bind_inactive_spell_is_not_meldable_until_notched():
    book = _make_spellbook()
    id_a = book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    conduit = book.conjure(dynamic=True, name="root")
    index = book.find_spell_by_id(id_a).spell_index
    id_b = conduit.bind_inactive(
        spell=_ServiceB, spell_index=index, existence=Existence.unique,
        permissions="create", binding_name="b",
    )
    try:
        # Parked off the resolution surface (inactive member of A's index) ->
        # not meldable by id until notched.
        assert _resolves(conduit, id_b) is False
    finally:
        conduit.cleanup()


def test_notch_to_already_active_is_noop():
    book = _make_spellbook()
    id_a = book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    conduit = book.conjure(dynamic=True, name="root")
    try:
        spell_a = book.find_spell_by_id(id_a)
        conduit.notch_spell(spell_index=spell_a.spell_index, spell=spell_a)  # already active
        assert spell_a.spell_index.selected_spell_id == id_a
        assert isinstance(conduit.meld(spell=id_a), _ServiceA)
    finally:
        conduit.cleanup()


# --- transfer + index probes -----------------------------------------------

def test_transfer_multi_member_target_melds_active():
    config = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    owner_book = Spellbook(configuration=config)
    id_a = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    target_book = Spellbook(configuration=config)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    index = owner_book.find_spell_by_id(id_a).spell_index
    id_b = owner.bind_inactive(
        spell=_ServiceB, spell_index=index, existence=Existence.unique,
        permissions="create", binding_name="b",
    )
    spell_b = owner_book._get_owned_spell(id_b)
    try:
        owner.transfer_spell_ownership(spell=id_a, target_conduit=target)
        assert isinstance(target.meld(spell=id_a), _ServiceA)
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


def test_two_borrowers_unlink_one_leaves_other_linked():
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
    for b in (b1, b2):
        with b.transaction("link", conduits=[b, owner]):
            b.add_index_to_contract(index=index, conduit=owner, permissions="create")
    try:
        with b1.transaction("link", conduits=[b1, owner]):
            b1.remove_index_from_contract(index_id=index.id, conduit=owner)
        assert index.id not in b1_book._contracted_indexes
        assert index.id in b2_book._contracted_indexes
    finally:
        b1.cleanup()
        b2.cleanup()
        owner.cleanup()


def test_index_link_active_member_is_live_borrowed_copy():
    with _single_linked("create") as (ob, bb, owner, borrower, id_a, index):
        active = bb._contracted_spells_by_id.get(owner._id, {})
        assert id_a in active


def test_notched_away_id_is_evicted_from_resolution():
    book = _make_spellbook()
    id_a = book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    id_b = book.bind(
        spell=_ServiceB, existence=Existence.unique, permissions="create",
        binding_name="b", bind_inactive=True,
    )
    conduit = book.conjure(dynamic=True, name="root")
    spell_b = book._get_owned_spell(id_b)
    index = book.find_spell_by_id(id_a).spell_index
    conduit.add_to_spell_index(spell=spell_b, target_index=index)
    try:
        conduit.notch_spell(spell_index=index, spell=spell_b)
        # The outgoing id A is off the resolution surface; the new active B melds.
        assert _resolves(conduit, id_a) is False
        assert isinstance(conduit.meld(spell=id_b), _ServiceB)
    finally:
        conduit.cleanup()
