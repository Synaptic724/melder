"""
Integration: the stage -> notch -> meld loop on public calls, by spell_id
(TASK-2026-10-16-public_notch_target_for_staged_versions).

`Conduit.notch_spell(spell_index=..., spell_id=...)` takes the spell_id `bind_inactive` returned and resolves it
inside the call. Before it, the only public way to get a Spell for a parked spell_id returned the index's active
spell, so the loop needed private access. The call also checks its target - owned by the conduit's Book, a member
of the index passed - for both forms: on 0.2.8248 a version of another index corrupted both indexes, and another
index's active version or another Book's version raised half-way with the index's active version already parked.
"""
import contextlib
from typing import Iterator, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration
from tests._spell_identity_test_support import version_of

pytestmark = pytest.mark.integration


class _ServiceA:
    """The version bound active."""

    def __init__(self) -> None:
        """Tag the object with its version."""
        self.tag = "A"


class _ServiceB:
    """The version staged and notched in."""

    def __init__(self) -> None:
        """Tag the object with its version."""
        self.tag = "B"


class _ServiceY1:
    """The active version of a second index."""

    def __init__(self) -> None:
        """Tag the object with its version."""
        self.tag = "Y1"


class _ServiceY2:
    """A version parked on the second index."""

    def __init__(self) -> None:
        """Tag the object with its version."""
        self.tag = "Y2"


def _reset_world() -> None:
    """Fresh Aether and utility-system singletons for one test."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_world() -> Iterator[None]:
    """Isolate each test behind fresh singletons."""
    _reset_world()
    yield
    _reset_world()


def _make_spellbook() -> Spellbook:
    """
    A Book in a dynamic world, so `bind_inactive` works before and after conjure.

    Returns:
        Spellbook: A new Book on the default frame.
    """
    configuration = SpellbookConfiguration(aether_frame="default")
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(aetheric_frame="default", configuration=configuration)


@contextlib.contextmanager
def _staged(
        *, before_conjure: bool = False, tag: str = "",
) -> Iterator[Tuple[Spellbook, Conduit, str, str, SpellIndex]]:
    """
    A root whose index holds A (active) and B (parked), B staged before or after conjure under A's binding
    (spellframe 'service', binding name 'a<tag>'): every version of an index is bound the way its first version
    was (2026-10-25).

    Args:
        before_conjure: Stage B on the Book before `conjure` (True) or on the root after it (False).
        tag: Names a second world sharing the frame: its binding names take the suffix and it binds versions
            of the services of its own, since one class is one spell (S1 of
            EPIC-2026-10-18-spell_identity_is_the_code).

    Yields:
        Tuple: (book, root, id_a, id_b, index).
    """
    service_a = version_of(_ServiceA, world=tag) if tag else _ServiceA
    service_b = version_of(_ServiceB, world=tag) if tag else _ServiceB
    book = _make_spellbook()
    id_a = book.bind(
        spell=service_a, existence=Existence.unique, permissions="create", spellframe="service",
        binding_name=f"a{tag}",
    )
    index = book.find_spell_by_spell_id(id_a).spell_index
    if before_conjure:
        id_b = book.bind_inactive(
            spell=service_b, spell_index=index, existence=Existence.unique, permissions="create",
            spellframe="service", binding_name=f"a{tag}",
        )
        root = book.conjure(dynamic=True, name=f"root{tag}")
    else:
        root = book.conjure(dynamic=True, name=f"root{tag}")
        id_b = root.bind_inactive(
            spell=service_b, spell_index=index, existence=Existence.unique, permissions="create",
            spellframe="service", binding_name=f"a{tag}",
        )
    try:
        yield book, root, id_a, id_b, index
    finally:
        root.cleanup()


def _assert_index_intact(root: Conduit, index: SpellIndex, active_id: str, members: set, tag: str) -> None:
    """
    Assert an index still selects `active_id`, holds `members`, and its active version melds.

    Args:
        root: The conduit that melds.
        index: The index to check.
        active_id: The spell_id it must still select.
        members: Its members' spell_ids.
        tag: The `tag` the active version's objects carry.
    """
    assert index.selected_spell_id == active_id
    assert index.spells_in_index() == members
    assert root.meld(spell_id=active_id).tag == tag


def test_notch_by_id_promotes_a_version_staged_after_conjure() -> None:
    """The spell_id `bind_inactive` returned is enough to promote the version; the next meld builds it."""
    with _staged() as (book, root, id_a, id_b, index):
        root.notch_spell(spell_index=index, spell_id=id_b)

        assert index.selected_spell_id == id_b
        assert isinstance(root.meld(spell_id=id_b), _ServiceB)


def test_notch_by_id_promotes_a_version_staged_before_conjure() -> None:
    """A version staged on the Book before conjure is promoted by its spell_id the same way (0.2.8248 wires it)."""
    with _staged(before_conjure=True) as (book, root, id_a, id_b, index):
        root.notch_spell(spell_index=index, spell_id=id_b)

        assert isinstance(root.meld(spell_id=id_b), _ServiceB)


def test_notch_by_id_returns_the_now_active_version() -> None:
    """The call returns the Spell it made active."""
    with _staged() as (book, root, id_a, id_b, index):
        result = root.notch_spell(spell_index=index, spell_id=id_b)

        assert result.spell_id == id_b
        assert result.spell_index is index


def test_notch_back_by_id_restores_the_first_version() -> None:
    """The outgoing version is parked, not destroyed: notching back by its spell_id restores it."""
    with _staged() as (book, root, id_a, id_b, index):
        root.notch_spell(spell_index=index, spell_id=id_b)
        root.notch_spell(spell_index=index, spell_id=id_a)

        assert index.selected_spell_id == id_a
        assert isinstance(root.meld(spell_id=id_a), _ServiceA)
        assert index.spells_in_index() == {id_a, id_b}


def test_notch_by_id_to_the_active_version_is_a_no_op() -> None:
    """Naming the version already active changes nothing and raises nothing."""
    with _staged() as (book, root, id_a, id_b, index):
        result = root.notch_spell(spell_index=index, spell_id=id_a)

        assert result.spell_id == id_a
        _assert_index_intact(root, index, id_a, {id_a, id_b}, "A")


def test_notch_refuses_a_parked_version_of_another_index_and_leaves_both_intact() -> None:
    """
    Regression: a version parked in another index of the Book used to be accepted and corrupt both indexes.

    Contract:
        - By spell_id and by object, the call raises ValueError; both indexes keep selection, members and melds.
    """
    with _staged() as (book, root, id_a, id_b, index):
        id_y1 = book.bind(
            spell=_ServiceY1, existence=Existence.unique, permissions="create", spellframe="other", binding_name="y1",
        )
        other = book.find_spell_by_spell_id(id_y1).spell_index
        id_y2 = root.bind_inactive(
            spell=_ServiceY2, spell_index=other, existence=Existence.unique, permissions="create",
            spellframe="other", binding_name="y1",
        )

        with pytest.raises(ValueError, match="belongs to another SpellIndex"):
            root.notch_spell(spell_index=index, spell_id=id_y2)
        with pytest.raises(ValueError, match="belongs to another SpellIndex"):
            root.notch_spell(spell_index=index, spell=book._get_owned_spell(id_y2))

        _assert_index_intact(root, index, id_a, {id_a, id_b}, "A")
        _assert_index_intact(root, other, id_y1, {id_y1, id_y2}, "Y1")


def test_notch_refuses_the_active_version_of_another_index_and_keeps_the_index_active() -> None:
    """
    Regression: another index's active version used to raise RuntimeError after this index's version was parked.
    """
    with _staged() as (book, root, id_a, id_b, index):
        id_y1 = book.bind(spell=_ServiceY1, existence=Existence.unique, permissions="create", binding_name="y1")

        with pytest.raises(ValueError, match="belongs to another SpellIndex"):
            root.notch_spell(spell_index=index, spell_id=id_y1)

        _assert_index_intact(root, index, id_a, {id_a, id_b}, "A")


def test_notch_refuses_a_version_another_book_owns_and_keeps_the_index_active() -> None:
    """
    Regression: another Book's parked version used to raise RuntimeError after this index's version was parked.
    """
    with _staged() as (book, root, id_a, id_b, index):
        with _staged(tag="other") as (other_book, other_root, other_a, other_b, other_index):
            with pytest.raises(ValueError, match="is not owned by this conduit's Spellbook"):
                root.notch_spell(spell_index=index, spell_id=other_b)
            with pytest.raises(ValueError, match="is not owned by this conduit's Spellbook"):
                root.notch_spell(spell_index=index, spell=other_book._get_owned_spell(other_b))

            _assert_index_intact(root, index, id_a, {id_a, id_b}, "A")
            _assert_index_intact(other_root, other_index, other_a, {other_a, other_b}, "A")


def test_notch_refuses_an_unknown_id_and_keeps_the_index_active() -> None:
    """A spell_id nothing bound is refused; the index is untouched."""
    with _staged() as (book, root, id_a, id_b, index):
        with pytest.raises(ValueError, match="is not owned by this conduit's Spellbook"):
            root.notch_spell(spell_index=index, spell_id="0" * 64)

        _assert_index_intact(root, index, id_a, {id_a, id_b}, "A")


def test_index_link_borrower_follows_a_notch_made_by_id() -> None:
    """A borrower linked to the index melds the version the owner notched in by spell_id."""
    owner_book = _make_spellbook()
    borrower_book = _make_spellbook()
    id_a = owner_book.bind(
        spell=_ServiceA, existence=Existence.unique, permissions="create", spellframe="service", binding_name="a",
    )
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        index = owner_book.find_spell_by_spell_id(id_a).spell_index
        id_b = owner.bind_inactive(
            spell=_ServiceB, spell_index=index, existence=Existence.unique, permissions="create",
            spellframe="service", binding_name="a",
        )
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")

        owner.notch_spell(spell_index=index, spell_id=id_b)

        assert borrower.validate_contracts_and_define()
        assert isinstance(borrower.meld(spell_id=id_b), _ServiceB)
    finally:
        borrower.cleanup()
        owner.cleanup()
