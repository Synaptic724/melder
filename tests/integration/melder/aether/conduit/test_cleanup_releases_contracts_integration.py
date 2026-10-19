"""
Integration tests: cleaning up a spell takes the version out of every contract that holds it, then disposes it
(STORY-2026-10-17-parked_cleanup_leaves_borrower_copies, cleanup_releases_contracts_2026_10_19, 0.2.8261).

Through 0.2.8260 `Conduit.cleanup_spell` told a lender's borrowers only when the version's index died with it: a
parked version whose index survived kept its entry, borrowed id and lender-side Detail on every index-link borrower,
past the borrower's own unlink, and a later notch to the class staged again raised in the borrower fan-out; a version
grant was never touched; and the direct `Spellbook.cleanup_spell` and a lesser conduit's `cleanup_spell` reached no
contract at all. Every `cleanup_spell` door now releases the version from every contract of the Book's root conduit
before the Book disposes it, and drops the index links when the index goes with it.

Each test runs in a fresh Aether: the owner binds A active (B parked on A's index where the test needs a parked
version), the borrower links to it.
"""

from typing import Iterator, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)

pytestmark = pytest.mark.integration


class _ServiceA:
    """The owner's active version."""

    def __init__(self) -> None:
        self.tag = "A"


class _ServiceB:
    """The owner's parked version on A's index."""

    def __init__(self) -> None:
        self.tag = "B"


class _Solo:
    """The sole member of its own index."""

    def __init__(self) -> None:
        self.tag = "solo"


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_cleanup_contracts() -> Iterator[None]:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.
    Returns:
        Iterator[None]: Control returns to the test between the two resets.
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


def _make_book() -> Spellbook:
    """
    Purpose:
        A Spellbook in the dynamic posture, with one phase worker.
    Returns:
        Spellbook: The new Book.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


def _world() -> Tuple[Spellbook, Spellbook, Conduit, Conduit, str, str, str]:
    """
    Purpose:
        The owner with A active and B parked on A's index and Solo alone in its own index; the borrower linked to
        the owner, nothing contracted yet.
    Returns:
        Tuple: (owner_book, borrower_book, owner, borrower, id_a, id_b, id_solo).
    """
    owner_book = _make_book()
    borrower_book = _make_book()
    id_a = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    id_solo = owner_book.bind(spell=_Solo, existence=Existence.unique, permissions="create", binding_name="solo")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    index = owner_book.find_spell_by_spell_id(id_a).spell_index
    id_b = owner.bind_inactive(spell=_ServiceB, spell_index=index, existence=Existence.unique,
                               permissions="create", binding_name="b")
    owner.link(borrower)
    return owner_book, borrower_book, owner, borrower, id_a, id_b, id_solo


def _link_index_of(owner_book: Spellbook, owner: Conduit, borrower: Conduit, spell_id: str) -> str:
    """
    Purpose:
        The borrower contracts the whole index of `spell_id`.
    Returns:
        str: The index's id.
    """
    index = owner_book.find_spell_by_spell_id(spell_id).spell_index
    with borrower.transaction("link", conduits=[borrower, owner]):
        assert borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")
    return index.id


def _grant(owner_book: Spellbook, owner: Conduit, borrower: Conduit, spell_id: str) -> None:
    """
    Purpose:
        The borrower contracts one version by its Spell (a version grant).
    Returns:
        None.
    """
    spell = owner_book.find_spell_by_spell_id(spell_id)
    with borrower.transaction("link", conduits=[borrower, owner]):
        assert borrower.add_spell_to_contract(spell=spell, conduit=owner, permissions="create")


def _borrowed(borrower_book: Spellbook, owner: Conduit) -> Tuple[List[str], List[str], List[str]]:
    """
    Purpose:
        What the borrower Book holds for the owner: active entries, parked entries and borrowed ids, by spell_id.
    Returns:
        Tuple[List[str], List[str], List[str]]: The three sorted id lists.
    """
    active = sorted(borrower_book._contracted_spells_by_id.get(owner._id, {}))
    parked = sorted(borrower_book._inactive_contracted_spells.get(owner._id, {}))
    ids = sorted(borrower_book._contracted_spell_ids.get(owner._id, set()))
    return active, parked, ids


def _owner_details(borrower: Conduit, owner: Conduit, *spell_ids: str) -> List[bool]:
    """
    Purpose:
        Whether the contract holds an owner-side Detail for each spell_id.
    Returns:
        List[bool]: One flag per spell_id, in order.
    """
    contract = borrower._conduit_ward._find_contract_by_id(owner._id)
    return [contract._check_if_exists(owner._conduit_ward, spell_id) for spell_id in spell_ids]


def test_cleanup_of_a_parked_member_drops_it_from_index_link_borrowers() -> None:
    owner_book, borrower_book, owner, borrower, id_a, id_b, _id_solo = _world()
    index_id = _link_index_of(owner_book, owner, borrower, id_a)
    try:
        owner.cleanup_spell(spell=owner_book._get_owned_spell(id_b))
        assert _borrowed(borrower_book, owner) == ([id_a], [], [id_a])
        assert _owner_details(borrower, owner, id_a, id_b) == [True, False]
        assert index_id in borrower_book._contracted_indexes
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_unlink_after_a_parked_cleanup_leaves_no_borrowed_ids() -> None:
    owner_book, borrower_book, owner, borrower, id_a, id_b, _id_solo = _world()
    index_id = _link_index_of(owner_book, owner, borrower, id_a)
    try:
        owner.cleanup_spell(spell=owner_book._get_owned_spell(id_b))
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.remove_index_from_contract(index_id=index_id, conduit=owner)
        assert _borrowed(borrower_book, owner) == ([], [], [])
        assert index_id not in borrower_book._contracted_indexes
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_notch_to_a_restaged_version_after_its_cleanup_reaches_index_link_borrowers() -> None:
    owner_book, borrower_book, owner, borrower, id_a, id_b, _id_solo = _world()
    _link_index_of(owner_book, owner, borrower, id_a)
    index = owner_book.find_spell_by_spell_id(id_a).spell_index
    try:
        owner.cleanup_spell(spell=owner_book._get_owned_spell(id_b))
        again = owner.bind_inactive(spell=_ServiceB, spell_index=index, existence=Existence.unique,
                                    permissions="create", binding_name="b")
        assert again == id_b
        owner.notch_spell(spell_index=index, spell_id=id_b)
        assert _borrowed(borrower_book, owner)[0] == [id_b]
        assert borrower.meld(spell_id=id_b).tag == "B"
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_cleanup_of_a_parked_granted_version_drops_the_grant() -> None:
    owner_book, borrower_book, owner, borrower, _id_a, id_b, _id_solo = _world()
    _grant(owner_book, owner, borrower, id_b)
    try:
        assert id_b in _borrowed(borrower_book, owner)[1]
        owner.cleanup_spell(spell=owner_book._get_owned_spell(id_b))
        active, parked, ids = _borrowed(borrower_book, owner)
        assert id_b not in active + parked + ids
        assert _owner_details(borrower, owner, id_b) == [False]
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_cleanup_of_a_granted_sole_member_leaves_the_borrower_no_cleaned_copy() -> None:
    owner_book, borrower_book, owner, borrower, _id_a, _id_b, id_solo = _world()
    _grant(owner_book, owner, borrower, id_solo)
    try:
        assert _borrowed(borrower_book, owner)[0] == [id_solo]
        owner.cleanup_spell(spell=owner_book.find_spell_by_spell_id(id_solo))
        assert _borrowed(borrower_book, owner) == ([], [], [])
        assert _owner_details(borrower, owner, id_solo) == [False]
        # As for a version the borrower never held; through 0.2.8260 it raised AttributeError on the cleaned Spell.
        with pytest.raises(KeyError, match="No spell found with spell_id"):
            borrower.meld(spell_id=id_solo)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_direct_spellbook_cleanup_of_a_parked_member_updates_index_link_borrowers() -> None:
    owner_book, borrower_book, owner, borrower, id_a, id_b, _id_solo = _world()
    _link_index_of(owner_book, owner, borrower, id_a)
    try:
        owner_book.cleanup_spell(spell=owner_book._get_owned_spell(id_b))
        assert _borrowed(borrower_book, owner) == ([id_a], [], [id_a])
        assert _owner_details(borrower, owner, id_b) == [False]
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_direct_spellbook_cleanup_of_a_sole_member_drops_the_index_link() -> None:
    owner_book, borrower_book, owner, borrower, _id_a, _id_b, id_solo = _world()
    index_id = _link_index_of(owner_book, owner, borrower, id_solo)
    try:
        owner_book.cleanup_spell(spell=owner_book.find_spell_by_spell_id(id_solo))
        assert _borrowed(borrower_book, owner) == ([], [], [])
        assert index_id not in borrower_book._contracted_indexes
        contract = borrower._conduit_ward._find_contract_by_id(owner._id)
        assert contract._check_index_exists(owner._conduit_ward, index_id) is False
        assert _owner_details(borrower, owner, id_solo) == [False]
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_lesser_conduit_cleanup_spell_releases_the_root_contracts() -> None:
    owner_book, borrower_book, owner, borrower, id_a, id_b, _id_solo = _world()
    _link_index_of(owner_book, owner, borrower, id_a)
    lesser = owner.create_lesser_conduit()
    try:
        lesser.cleanup_spell(spell=owner_book._get_owned_spell(id_b))
        assert _borrowed(borrower_book, owner) == ([id_a], [], [id_a])
        assert _owner_details(borrower, owner, id_b) == [False]
    finally:
        lesser.cleanup()
        borrower.cleanup()
        owner.cleanup()


def test_borrowers_drop_the_version_while_it_is_still_live(monkeypatch: pytest.MonkeyPatch) -> None:
    owner_book, borrower_book, owner, borrower, id_a, id_b, _id_solo = _world()
    _link_index_of(owner_book, owner, borrower, id_a)
    spell_b: Spell = owner_book._get_owned_spell(id_b)
    seen: List[Tuple[str, bool]] = []
    original = Spellbook._remove_contracted_spell

    def recording(self: Spellbook, spell_id: str, conduit_id: str) -> None:
        """Record whether the owner's version is already cleaned when the borrower drops it."""
        if self is borrower_book:
            seen.append((spell_id, spell_b._cleaned))
        original(self, spell_id, conduit_id)

    monkeypatch.setattr(Spellbook, "_remove_contracted_spell", recording)
    try:
        owner.cleanup_spell(spell=spell_b)
        assert seen == [(id_b, False)]
        assert spell_b._cleaned
    finally:
        monkeypatch.undo()
        borrower.cleanup()
        owner.cleanup()


def test_refused_cleanup_of_an_active_member_leaves_borrower_contracts_intact() -> None:
    owner_book, borrower_book, owner, borrower, id_a, id_b, _id_solo = _world()
    _link_index_of(owner_book, owner, borrower, id_a)
    try:
        before = _borrowed(borrower_book, owner)
        with pytest.raises(RuntimeError, match="active member of a multi-member index"):
            owner.cleanup_spell(spell=owner_book.find_spell_by_spell_id(id_a))
        assert _borrowed(borrower_book, owner) == before
        assert _owner_details(borrower, owner, id_a, id_b) == [True, True]
    finally:
        borrower.cleanup()
        owner.cleanup()
