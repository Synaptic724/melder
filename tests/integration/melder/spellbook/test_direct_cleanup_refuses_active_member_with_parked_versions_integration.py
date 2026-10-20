"""
Integration: a direct removal of an index's active member that has parked siblings is refused with nothing changed
(STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions; patch direct_cleanup_refusal_2026_10_18).

`Conduit.cleanup_spell` refuses the active member of a multi-member index. Until the fix the two other public doors -
a direct `Spell.cleanup()` and `Spellbook.cleanup_and_remove_spell` - cleaned the index under its parked versions,
leaving a version no later call could notch, move, dispose or clean (probe D2 and D3,
artifacts/correctness_defects_20261017/probes/probe_direct_cleanup_active_member.py). All three now refuse it, each
message naming the remedies - notch the index to a parked version, dispose the parked versions, or move them out -
and the sole member of an index is removed as before (the owner's choice, 2026-10-18).
"""
import contextlib
import re
from typing import Iterator, Optional, Protocol, Set, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus

pytestmark = pytest.mark.integration


def _refusal() -> str:
    """
    The part of the refusal message both doors share with `cleanup_spell`'s, as a `pytest.raises` pattern.

    Returns:
        str: The pattern.
    """
    return re.escape(
        "is the active member of a multi-member index, and disposing it would leave the index's parked versions "
        "without an active one. Notch the index to one of them, dispose them with cleanup_spell, or move them out "
        "with remove_from_spell_index first."
    )


class Greeter(Protocol):
    """The contract every version implements."""

    def greet(self) -> str:
        """Return a greeting."""
        ...


class English:
    """The version bound active."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """A version parked on English's index."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Note:
    """A plain spell so the borrower Book has something to conjure."""


def _reset_world() -> None:
    """Fresh utility, Nexus and Aether singletons, rebound on Spellbook and Conduit."""
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_world() -> Iterator[None]:
    """Isolate each test behind fresh singletons."""
    _reset_world()
    yield
    _reset_world()


class _World:
    """Handles of the lender (English active, French parked when staged) and its index-linked borrower."""

    def __init__(self, book: Spellbook, lender: Conduit, borrower_book: Spellbook, borrower: Conduit,
                 english: Spell) -> None:
        """
        Keep the handles; `_world` stages French when asked.

        Args:
            book: The lender's Book.
            lender: The lender's root conduit.
            borrower_book: The borrower's Book.
            borrower: The borrower's root conduit, linked to the lender and contracting English's index.
            english: The active English Spell.
        """
        self.book = book
        self.lender = lender
        self.borrower_book = borrower_book
        self.borrower = borrower
        self.english = english
        self.index: SpellIndex = english.spell_index
        self.french: Optional[Spell] = None

    def find_index(self, spell_id: str) -> Optional[SpellIndex]:
        """
        The index the frame's spell registry names for `spell_id`, or None.

        Args:
            spell_id: A version's spell_id.

        Returns:
            Optional[SpellIndex]: The registered index.
        """
        return self.book._aetheric_frame.find_index_for_spell(spell_id)

    def borrower_copies(self) -> Tuple[Set[str], Set[str]]:
        """
        The borrower's active and parked copies of the lender's versions, by spell_id.

        Returns:
            Tuple[Set[str], Set[str]]: (active spell_ids, parked spell_ids).
        """
        active = set(self.borrower_book._contracted_spells_by_id.get(self.lender._id, {}))
        parked = set(self.borrower_book._inactive_contracted_spells.get(self.lender._id, {}))
        return active, parked


@contextlib.contextmanager
def _world(frame: str, *, stage_french: bool = True) -> Iterator[_World]:
    """
    English active on the lender's index, a borrower contracting the whole index, French parked on it when asked.

    Args:
        frame: The frame for both Books.
        stage_french: Stage French on English's index after the borrower contracted it.

    Yields:
        _World: The handles; both roots are torn down on exit.
    """
    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    book.configure_aether_frame(
        system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
    )
    borrower_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    english_id = book.bind(
        spell=English, spellframe=Greeter, binding_name="greeter", existence=Existence.many, permissions="create",
    )
    borrower_book.bind(spell=Note, existence=Existence.many, permissions="create")
    lender = book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    world = _World(book, lender, borrower_book, borrower, book.find_spell_by_spell_id(english_id))
    try:
        lender.link(borrower)
        with borrower.transaction("link", conduits=[borrower, lender]):
            assert borrower.add_index_to_contract(index=world.index, conduit=lender, permissions="create")
        if stage_french:
            french_id = lender.bind_inactive(
                spell=French, spell_index=world.index, spellframe=Greeter, binding_name="greeter",
                existence=Existence.many, permissions="create",
            )
            world.french = book.find_spell_by_spell_id(french_id)
        yield world
    finally:
        borrower.cleanup()
        lender.cleanup()


def _assert_nothing_changed(world: _World) -> None:
    """
    Assert the refused removal changed nothing: the index live and selecting English, English active, French parked,
    both registered with the frame, the lineage tracked, the borrower's copies as staged, English meldable.

    Args:
        world: The handles (French staged).
    """
    assert world.french is not None
    english_id, french_id = world.english.spell_id, world.french.spell_id
    assert not world.index.cleaned
    assert world.index.selected_spell_id == english_id
    assert world.index.spells_in_index() == {english_id, french_id}
    assert not world.english.cleaned and not world.french.cleaned
    assert world.book._spells_by_id[english_id] is world.english
    assert world.book._inactive_spells[french_id] is world.french
    assert world.find_index(english_id) is world.index
    assert world.find_index(french_id) is world.index
    assert world.book._spell_system_states.get_by_index_id(world.index.id) is not None
    assert world.borrower_copies() == ({english_id}, {french_id})
    assert isinstance(world.lender.meld(spell_id=english_id), English)


def test_direct_cleanup_of_an_active_member_with_parked_siblings_refuses() -> None:
    """
    Regression (probe D2): `English.cleanup()` cleaned the index under the parked French.

    Contract:
        - It raises the multi-member RuntimeError and changes nothing.
    """
    with _world("direct_cleanup_refused") as world:
        with pytest.raises(RuntimeError, match=_refusal()):
            world.english.cleanup()

        _assert_nothing_changed(world)


@pytest.mark.parametrize("by_spell_id", [False, True], ids=["by_spell", "by_spell_id"])
def test_cleanup_and_remove_spell_refuses_a_member_with_parked_siblings(by_spell_id: bool) -> None:
    """
    Regression (probe D3): `cleanup_and_remove_spell(English)` cleaned the index under the parked French.

    Contract:
        - Named by Spell or by spell_id, it raises the multi-member RuntimeError and changes nothing.
    """
    with _world("remove_refused_" + ("id" if by_spell_id else "spell")) as world:
        target = world.english.spell_id if by_spell_id else world.english
        with pytest.raises(RuntimeError, match=_refusal()):
            world.book.cleanup_and_remove_spell(target)

        _assert_nothing_changed(world)


def test_cleanup_spell_refusal_names_the_remedies() -> None:
    """
    `cleanup_spell(English)` keeps its refusal of the active member and now names the same three remedies.

    Contract:
        - It raises the multi-member RuntimeError, prefixed "cleanup_spell: spell <spell_id>", and changes nothing.
    """
    with _world("cleanup_spell_refused") as world:
        prefix = "^cleanup_spell: spell " + re.escape(world.english.spell_id) + " "
        with pytest.raises(RuntimeError, match=prefix + _refusal()):
            world.lender.cleanup_spell(spell=world.english)

        _assert_nothing_changed(world)


def test_after_the_refusal_a_notch_away_lets_the_old_version_go() -> None:
    """The refusal's remedy: notch to French, then dispose the now-parked English; French serves on its live index."""
    with _world("refused_then_notch_away") as world:
        assert world.french is not None
        with pytest.raises(RuntimeError, match=_refusal()):
            world.english.cleanup()

        world.lender.notch_spell(spell_index=world.index, spell_id=world.french.spell_id)
        world.lender.cleanup_spell(spell=world.english)

        assert world.english.cleaned and not world.index.cleaned
        assert world.index.spells_in_index() == {world.french.spell_id}
        assert isinstance(world.lender.meld(spell_id=world.french.spell_id), French)


def test_after_the_refusal_disposing_the_parked_version_lets_the_member_go() -> None:
    """The other remedy: dispose French first; English is then the index's sole member and is removed with it."""
    with _world("refused_then_dispose_parked") as world:
        assert world.french is not None
        english_id = world.english.spell_id
        with pytest.raises(RuntimeError, match=_refusal()):
            world.english.cleanup()

        world.lender.cleanup_spell(spell=world.french)
        world.english.cleanup()

        assert world.english.cleaned and world.french.cleaned and world.index.cleaned
        assert world.find_index(english_id) is None
        assert english_id not in world.book._spells_by_id


def test_after_the_refusal_moving_the_parked_version_out_lets_the_member_go() -> None:
    """
    The third remedy: move French out with `remove_from_spell_index`; English is then its index's sole member and is
    removed with it, while French stays parked, alone in a fresh index.
    """
    with _world("refused_then_move_parked_out") as world:
        assert world.french is not None
        english_id, french_id = world.english.spell_id, world.french.spell_id
        with pytest.raises(RuntimeError, match=_refusal()):
            world.english.cleanup()

        world.lender.remove_from_spell_index(spell_id=french_id, source_index=world.index)
        world.english.cleanup()

        assert world.english.cleaned and world.index.cleaned
        assert english_id not in world.book._spells_by_id
        assert not world.french.cleaned
        assert world.book._inactive_spells[french_id] is world.french
        assert world.french.spell_index is not world.index
        assert world.french.spell_index.spells_in_index() == {french_id}


@pytest.mark.parametrize("door", ["spell_cleanup", "cleanup_and_remove_spell"])
def test_a_sole_active_member_is_still_removed_directly(door: str) -> None:
    """Control: English alone on its index is removed by either door, its index cleaned and gone from the frame."""
    with _world("sole_member_" + door, stage_french=False) as world:
        english_id = world.english.spell_id

        if door == "spell_cleanup":
            world.english.cleanup()
        else:
            world.book.cleanup_and_remove_spell(english_id)

        assert world.english.cleaned and world.index.cleaned
        assert world.find_index(english_id) is None
        assert english_id not in world.book._spells_by_id
