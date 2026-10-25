"""
Integration: a version separated into an index of its own is known to its frame
(STORY-2026-10-17-minted_index_missing_from_frame_registry; patch minted_index_registry_2026_10_18).

`Conduit.remove_from_spell_index` moves a parked version out of its index into a fresh index of its own, created as
Bind creates an index. Until the fix the frame's spell registry - the catalog every lookup by spell_id walks - never
listed that index, so the version was unknown to its frame, parked there or notched active: the Conduit's spell_id
lookups raised "Spell version <id> not found in any conduit.", a grant and an ownership transfer by spell_id were
refused, another Book could bind the same spell_id, and MutationResearch residency lost the version (probes M2-M7 and
V2-V3, artifacts/minted_index_registry_20261018/probes/). The index is now registered as a post-conjure `bind`
registers the index it creates, it leaves the registry with the rest at its root's teardown, and residency reads its
version parked until a notch makes it active (the owner's word, 2026-10-18).

Every version of an index is bound the way its first version was (2026-10-25): French is staged under English's
binding, keeps it in the index it is moved into, and goes active there only once English no longer holds the address,
so the cases that notch French active dispose English first.
"""
import contextlib
from typing import TYPE_CHECKING, Iterator, List, Optional, Protocol, Tuple

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

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.aetheric_frame import AethericFrame

pytestmark = pytest.mark.integration


class Greeter(Protocol):
    """The contract both versions implement."""

    def greet(self) -> str:
        """Return a greeting."""
        ...


class English:
    """The version bound active."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """The version staged on English's index under English's binding, then moved into an index of its own."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Note:
    """A plain spell so another Book has something to conjure."""


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


def _book(frame: str, *, settle: bool = False) -> Spellbook:
    """
    A Book in `frame`.

    Args:
        frame: The frame the Book binds in.
        settle: Make the frame dynamic with caching off - for the frame's first Book only.

    Returns:
        Spellbook: The Book, not conjured.
    """
    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    if settle:
        book.configure_aether_frame(
            system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
        )
    return book


def _owned(book: Spellbook, spell_id: str) -> Spell:
    """
    The Spell `book` holds under `spell_id`, active or parked.

    Args:
        book: The owning Book.
        spell_id: The spell_id `bind` or `bind_inactive` returned.

    Returns:
        Spell: The Spell.
    """
    spell = book.find_spell_by_spell_id(spell_id)
    assert spell is not None
    return spell


def _bind_french(book: Spellbook) -> str:
    """
    Bind French in `book` under (Greeter, 'french'), an address no spell holds, so the only refusal it can meet is the
    spell_id collision: a spell_id is French's code whatever the binding (0.2.8257).

    Args:
        book: The Book that binds.

    Returns:
        str: The spell_id bind returned.
    """
    return book.bind(
        spell=French, spellframe=Greeter, binding_name="french", existence=Existence.many, permissions="create",
    )


class _Lender:
    """Handles of the lender: English active on its index, French parked on it, and the roots made beside it."""

    def __init__(self, frame_name: str, book: Spellbook, lender: Conduit, english: Spell, french: Spell) -> None:
        """
        Keep the handles.

        Args:
            frame_name: The lender's frame.
            book: The lender's Book.
            lender: The lender's root conduit, 'lender'.
            english: The active English Spell.
            french: The parked French Spell, on English's index until `separate` moves it.
        """
        self.frame_name = frame_name
        self.book = book
        self.lender = lender
        self.english = english
        self.french = french
        self.index: SpellIndex = english.spell_index
        self.roots: List[Conduit] = []

    @property
    def frame(self) -> AethericFrame:
        """The lender's frame."""
        return self.book._aetheric_frame

    def separate(self) -> SpellIndex:
        """
        Move French out of English's index with `remove_from_spell_index`.

        Returns:
            SpellIndex: The index French was moved into, French its only member.
        """
        self.lender.remove_from_spell_index(spell_id=self.french.spell_id, source_index=self.index)
        return self.french.spell_index

    def free_the_address(self) -> None:
        """
        Dispose English, the sole member of its index once French is moved out, so the address the two share is free:
        a split version keeps its binding, and its index goes active only once no other spell holds the address
        (2026-10-25).
        """
        self.lender.cleanup_spell(spell=self.english)

    def peer(self, name: str, *, frame: Optional[str] = None) -> Tuple[Spellbook, Conduit]:
        """
        Conjure a root holding one plain spell, torn down with the world.

        Args:
            name: The root's name.
            frame: Another frame, settled dynamic by this Book; the lender's frame when None.

        Returns:
            Tuple[Spellbook, Conduit]: The root's Book and the root.
        """
        book = _book(frame or self.frame_name, settle=frame is not None)
        book.bind(spell=Note, existence=Existence.many, permissions="create")
        root = book.conjure(dynamic=True, name=name)
        self.roots.append(root)
        return book, root


@contextlib.contextmanager
def _lender(frame: str) -> Iterator[_Lender]:
    """
    English active on the lender's index and French parked on it under English's binding, in a dynamic frame with
    caching off.

    Args:
        frame: The lender's frame.

    Yields:
        _Lender: The handles; every root is torn down on exit, the peers first.
    """
    book = _book(frame, settle=True)
    english_id = book.bind(
        spell=English, spellframe=Greeter, binding_name="english", existence=Existence.many, permissions="create",
    )
    lender = book.conjure(dynamic=True, name="lender")
    english = _owned(book, english_id)
    french_id = lender.bind_inactive(
        spell=French, spell_index=english.spell_index, spellframe=Greeter, binding_name="english",
        existence=Existence.many, permissions="create",
    )
    world = _Lender(frame, book, lender, english, _owned(book, french_id))
    try:
        yield world
    finally:
        for root in reversed(world.roots):
            root.cleanup()
        lender.cleanup()


def test_a_version_separated_into_its_own_index_is_found_by_spell_id() -> None:
    """
    Regression (probe M2): after `remove_from_spell_index(French)` the frame did not find French's index, and the
    Conduit's spell_id lookups raised "Spell version <id> not found in any conduit." for a version its Book owns.

    Contract:
        - Before the move the frame finds French in English's index (control, probe M1).
        - After it the frame finds French in the index it was moved into, under the lender; `get_spell_by_spell_id`
          answers French and `get_conduit_by_spell_id` the lender; English stays in its own index.
    """
    with _lender("found_parked") as world:
        french_id = world.french.spell_id
        assert world.frame.find_index_for_spell(french_id) is world.index

        minted = world.separate()

        assert minted is not world.index
        assert minted.spells_in_index() == {french_id}
        assert world.frame.find_index_for_spell(french_id) is minted
        assert world.frame.find_conduit_id_for_spell(french_id) == world.lender._id
        assert world.lender.get_spell_by_spell_id(french_id) is world.french
        assert world.lender.get_conduit_by_spell_id(french_id) is world.lender
        assert world.frame.find_index_for_spell(world.english.spell_id) is world.index


def test_a_version_notched_active_in_its_own_index_is_found_by_spell_id() -> None:
    """
    Regression (probe M3): French notched active in the index it was moved into melded, but the frame did not find
    it and the Conduit's spell_id lookups raised "not found in any conduit".

    Contract:
        - While English holds the address the two share, the notch is refused and English still melds (a split version
          keeps its binding, 2026-10-25).
        - Once English is disposed, French notched active in its index is found there, the lookups answer French and
          the lender, and French melds.
    """
    with _lender("found_active") as world:
        french_id = world.french.spell_id
        minted = world.separate()

        with pytest.raises(RuntimeError, match="is held by spell_id"):
            world.lender.notch_spell(spell_index=minted, spell_id=french_id)
        assert isinstance(world.lender.meld(spell_id=world.english.spell_id), English)
        world.free_the_address()
        world.lender.notch_spell(spell_index=minted, spell_id=french_id)

        assert minted.selected_spell_id == french_id
        assert world.frame.find_index_for_spell(french_id) is minted
        assert world.lender.get_spell_by_spell_id(french_id) is world.french
        assert world.lender.get_conduit_by_spell_id(french_id) is world.lender
        assert isinstance(world.lender.meld(spell_id=french_id), French)


@pytest.mark.parametrize("notched", [False, True], ids=["parked", "notched_active"])
def test_a_version_in_its_own_index_can_be_granted_by_spell_id(notched: bool) -> None:
    """
    Regression (probes M3, G2 and G3): a linked borrower's `add_spell_to_contract(spell_id=French)` raised "Spell
    version <id> not found in any conduit." for French in the index it was moved into, parked there or notched
    active.

    Contract:
        - The grant proceeds, and the borrower's copy of French is parked or active as French is on the lender (French
          is notched active once English, disposed, no longer holds the address).
    """
    with _lender("granted_" + ("active" if notched else "parked")) as world:
        borrower_book, borrower = world.peer("borrower")
        world.lender.link(borrower)
        french_id = world.french.spell_id
        minted = world.separate()
        if notched:
            world.free_the_address()
            world.lender.notch_spell(spell_index=minted, spell_id=french_id)

        with borrower.transaction("link", conduits=[borrower, world.lender]):
            granted = borrower.add_spell_to_contract(spell_id=french_id, conduit=world.lender, permissions="create")

        assert granted
        active = set(borrower_book._contracted_spells_by_id.get(world.lender._id, {}))
        parked = set(borrower_book._inactive_contracted_spells.get(world.lender._id, {}))
        assert (french_id in active, french_id in parked) == (notched, not notched)


def test_a_version_notched_active_in_its_own_index_can_be_transferred_by_spell_id() -> None:
    """
    Regression (probe M7): `transfer_spell_ownership(spell=<French's spell_id>)` raised "Spell version <id> not found
    in any conduit." for French notched active in the index it was moved into.

    Contract:
        - The transfer proceeds: the target's Book owns French and the frame names the target as French's conduit
          (French is notched active once English, disposed, no longer holds the address).
    """
    with _lender("transferred") as world:
        target_book, target = world.peer("target")
        french_id = world.french.spell_id
        minted = world.separate()
        world.free_the_address()
        world.lender.notch_spell(spell_index=minted, spell_id=french_id)

        world.lender.transfer_spell_ownership(spell=french_id, target_conduit=target)

        assert target_book.find_spell_by_spell_id(french_id) is not None
        assert world.frame.find_conduit_id_for_spell(french_id) == target._id
        assert world.lender.get_conduit_by_spell_id(french_id) is target


@pytest.mark.parametrize("conjured", [False, True], ids=["unconjured_book", "conjured_book"])
@pytest.mark.parametrize("same_frame", [True, False], ids=["same_frame", "other_frame"])
def test_a_version_in_its_own_index_cannot_be_bound_again_by_another_book(same_frame: bool, conjured: bool) -> None:
    """
    Regression (probes M4b and M5b): while French sat in the index `remove_from_spell_index` minted, bind's collision
    guard did not see it, so another Book bound French's spell_id - of the same frame, or of another frame under
    process-wide spell ids (the default); a Book not yet conjured then had its conjure refused.

    Contract:
        - The bind is refused with the collision error, as it is for a version in any other index.
    """
    frame = "rebind_" + ("same" if same_frame else "other") + ("_conjured" if conjured else "_unconjured")
    with _lender(frame) as world:
        world.separate()
        other_frame = frame if same_frame else frame + "_other"
        if conjured:
            book, _root = world.peer("other", frame=None if same_frame else other_frame)
        else:
            book = _book(other_frame, settle=not same_frame)

        with pytest.raises(RuntimeError, match="Spell ID collision detected"):
            _bind_french(book)


def test_a_separated_version_is_registered_under_its_root_until_the_root_is_torn_down() -> None:
    """
    Regression (probes M2 and M6): the index French was moved into was never registered under its root; once it is,
    the root's teardown must take it out of the frame with the root's other indexes.

    Contract:
        - While the lender lives the frame finds French's index under the lender.
        - After the lender's teardown (another root keeps the frame alive) the frame finds neither French's index nor
          a conduit for it, holds no entry for French's spell_id, and a new Book of the frame may bind French.
    """
    with _lender("root_teardown") as world:
        world.peer("keeper")
        french_id = world.french.spell_id
        minted = world.separate()
        frame = world.frame
        assert frame.find_index_for_spell(french_id) is minted
        assert frame.find_conduit_id_for_spell(french_id) == world.lender._id

        world.lender.cleanup()

        assert not frame.cleaned
        assert frame.find_index_for_spell(french_id) is None
        assert frame.find_conduit_id_for_spell(french_id) is None
        assert not frame.has_spell(french_id)
        assert _bind_french(_book("root_teardown")) == french_id


def test_a_separated_version_moved_back_leaves_no_registered_index_behind() -> None:
    """
    Control: French moved back onto English's index with `add_to_spell_index` empties the index it was moved into,
    which is destroyed - and, now that it is registered, taken out of the frame's registry with it.

    Contract:
        - The emptied index is cleaned and gone from the lender's registry entry; the frame finds French in English's
          index under the lender. No public read lists a conduit's registered indexes, so the entry is read directly:
          the registry is the structure this story repairs.
    """
    with _lender("moved_back") as world:
        french_id = world.french.spell_id
        minted = world.separate()

        world.lender.add_to_spell_index(spell_id=french_id, target_index=world.index)

        assert minted.cleaned
        assert minted not in world.frame._spell_registry.get(world.lender._id, set())
        assert world.frame.find_index_for_spell(french_id) is world.index
        assert world.frame.find_conduit_id_for_spell(french_id) == world.lender._id


def test_residency_reads_a_separated_version_parked_then_active_after_a_notch() -> None:
    """
    Regression (probes V2 and V3): `residency_view` lost French in the index it was moved into - parked there and
    notched active there - because the frame did not list that index; with the index listed, the index's selection of
    its parked member (activation takes a notch) must not read as active.

    Contract:
        - French parked on English's index reads parked there (control, probe V1).
        - Moved into an index of its own it reads parked in that index, while English reads active in its own index;
          notched active there once English is disposed (a split version goes active only once its address is free,
          2026-10-25) it reads active in it.
    """
    with _lender("residency") as world:
        research = world.lender.mutation_research
        french_id = world.french.spell_id
        before = research.residency_view(french_id)
        assert (before["runtime"], before["index_id"]) == ("parked", world.index.id)

        minted = world.separate()
        parked = research.residency_view(french_id)
        english = research.residency_view(world.english.spell_id)
        world.free_the_address()
        world.lender.notch_spell(spell_index=minted, spell_id=french_id)
        active = research.residency_view(french_id)

        assert (parked["runtime"], parked["frame_name"], parked["index_id"]) == ("parked", "residency", minted.id)
        assert (active["runtime"], active["frame_name"], active["index_id"]) == ("active", "residency", minted.id)
        assert (english["runtime"], english["index_id"]) == ("active", world.index.id)
