"""
Integration tests -- full lifecycle (E1), cleanup variants (A6), and index-link depth.

Chains the whole surface end to end and fills out the behavioral corners:
- E1  bind -> bind_inactive -> add_to_spell_index -> notch -> meld -> notch-back.
- A6  cleanup an INACTIVE member (index + active member survive) vs cleanup the ACTIVE
      SOLE member (index destroyed).
- depth: permission variants, relink idempotency, two-index isolation, borrower cleanup
      leaving the owner intact, and add/remove-member roundtrips.

Transactions are OUT OF SCOPE. Runtime: Python 3.14t; the 3.10 sandbox cannot run
these -> user runs on 3.14t (validate the notch multi-member harness first).
"""

import contextlib
from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
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
def reset_aether_singleton_for_lifecycle_depth() -> None:
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


def _two_member_conduit():
    """Single dynamic conduit whose index has A active + B inactive."""
    book = _make_spellbook()
    id_a = book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    conduit = book.conjure(dynamic=True, name="root")
    index = book.find_spell_by_id(id_a).spell_index
    # bind_inactive stages B off the resolution surface AND attaches it to A's
    # index as an inactive member in one call (it requires an existing target
    # index; it cannot stand alone).
    id_b = conduit.bind_inactive(
        spell=_ServiceB, spell_index=index, existence=Existence.unique,
        permissions="create", binding_name="b",
    )
    spell_b = book._get_owned_spell(id_b)
    return book, conduit, id_a, id_b, index, spell_b


@contextlib.contextmanager
def _linked_pair(permission: str = "create") -> Iterator[tuple]:
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


# --- E1 full lifecycle ------------------------------------------------------

def test_full_lifecycle_stage_add_notch_meld():
    book, conduit, id_a, id_b, index, spell_b = _two_member_conduit()
    try:
        assert index.spells_in_index() == {id_a, id_b}     # staged + moved
        conduit.notch_spell(spell_index=index, spell=spell_b)
        assert index.selected_spell_id == id_b             # notched
        assert isinstance(conduit.meld(spell_id=id_b), _ServiceB)  # melds the new active
    finally:
        conduit.cleanup()


def test_lifecycle_notch_back_restores_and_melds_original():
    book, conduit, id_a, id_b, index, spell_b = _two_member_conduit()
    try:
        conduit.notch_spell(spell_index=index, spell=spell_b)
        spell_a = book._get_owned_spell(id_a)
        conduit.notch_spell(spell_index=index, spell=spell_a)
        assert index.selected_spell_id == id_a
        assert isinstance(conduit.meld(spell_id=id_a), _ServiceA)
    finally:
        conduit.cleanup()


# --- A6 cleanup variants ----------------------------------------------------

def test_cleanup_inactive_member_leaves_index_and_active():
    book, conduit, id_a, id_b, index, spell_b = _two_member_conduit()
    try:
        conduit.cleanup_spell(spell=spell_b)   # dispose the inactive member
        assert index.spells_in_index() == {id_a}
        assert index.selected_spell_id == id_a
        assert isinstance(conduit.meld(spell_id=id_a), _ServiceA)
    finally:
        conduit.cleanup()


def test_cleanup_active_sole_member_destroys_index():
    book = _make_spellbook()
    id_a = book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    conduit = book.conjure(dynamic=True, name="root")
    try:
        conduit.cleanup_spell(spell=book.find_spell_by_id(id_a))
        assert book.find_spell_by_id(id_a) is None   # index + spell gone
    finally:
        conduit.cleanup()


# --- depth: permission variants + idempotency ------------------------------

def test_index_link_at_create_grants_member_create():
    with _linked_pair("create") as (ob, bb, owner, borrower, id_a, index):
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        detail = contract._get_detail_map(owner._conduit_ward)[id_a]
        assert detail.permissions is Permissions.create


def test_index_link_at_read_grants_member_read():
    with _linked_pair("read") as (ob, bb, owner, borrower, id_a, index):
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        detail = contract._get_detail_map(owner._conduit_ward)[id_a]
        assert detail.permissions is Permissions.read


def test_relink_same_index_is_idempotent():
    with _linked_pair("create") as (ob, bb, owner, borrower, id_a, index):
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        # Still exactly one index-detail for the index (merge, not duplicate).
        assert contract._check_index_exists(owner._conduit_ward, index.id) is True
        assert index.id in bb._contracted_indexes


def test_unlink_then_relink_reestablishes_index():
    with _linked_pair("create") as (ob, bb, owner, borrower, id_a, index):
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.remove_index_from_contract(index_id=index.id, conduit=owner)
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        assert contract._check_index_exists(owner._conduit_ward, index.id) is True


def test_two_indexes_linked_are_isolated():
    with _linked_pair("create") as (ob, bb, owner, borrower, id_a, index):
        # Link a second, distinct index to the same borrower.
        id_c = ob.bind(spell=_ServiceC, existence=Existence.unique, permissions="create", binding_name="c")
        index_c = ob.find_spell_by_id(id_c).spell_index
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_index_to_contract(index=index_c, conduit=owner, permissions="create")
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.remove_index_from_contract(index_id=index_c.id, conduit=owner)
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        # Removing index_c leaves the first index intact.
        assert contract._check_index_exists(owner._conduit_ward, index_c.id) is False
        assert contract._check_index_exists(owner._conduit_ward, index.id) is True


def test_borrower_cleanup_leaves_owner_index_resolvable():
    owner_book = _make_spellbook()
    borrower_book = _make_spellbook()
    id_a = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    owner.link(borrower)
    index = owner_book.find_spell_by_id(id_a).spell_index
    with borrower.transaction("link", conduits=[borrower, owner]):
        borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")
    try:
        borrower.cleanup()
        # The owner still owns and can resolve its index after the borrower leaves.
        assert isinstance(owner.meld(spell_id=id_a), _ServiceA)
    finally:
        owner.cleanup()


# --- depth: add/remove member roundtrip ------------------------------------

def test_add_then_remove_member_roundtrip():
    book, conduit, id_a, id_b, index, spell_b = _two_member_conduit()
    try:
        assert index.spells_in_index() == {id_a, id_b}
        conduit.remove_from_spell_index(spell=spell_b, source_index=index)
        assert index.spells_in_index() == {id_a}
        # B is back in its own fresh single-member index.
        assert spell_b.spell_index.spells_in_index() == {id_b}
    finally:
        conduit.cleanup()


def test_add_to_index_keeps_source_creations_untouched_for_active():
    book, conduit, id_a, id_b, index, spell_b = _two_member_conduit()
    try:
        # Moving the inactive B onto A's index does not disturb A's resolution.
        assert isinstance(conduit.meld(spell_id=id_a), _ServiceA)
    finally:
        conduit.cleanup()
