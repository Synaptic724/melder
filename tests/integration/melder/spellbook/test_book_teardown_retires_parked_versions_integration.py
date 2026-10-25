"""
Integration: a Book's teardown retires its parked versions and the indexes only they hold
(STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned; patch book_teardown_parked_2026_10_19).

`Spellbook._cleanup_spells` cleaned each index through its active member and nothing else, so a parked version - on a
shared index, or alone in one `remove_from_spell_index` minted - stayed uncleaned when its Book was torn down, the
minted index with it, and the version's own `cleanup()` then raised "Spellbook has already been cleaned." (probe
T2-T3, artifacts/correctness_defects_20261017/probes/probe_book_teardown_parked.py). The teardown now retires every
parked version locally, as `cleanup_spell` retires one, and cleans the indexes only parked versions hold.

French is staged under English's binding (Greeter, 'english'): every version of an index is bound the way its first
version was (2026-10-25).
"""
import contextlib
from typing import Iterator, Optional, Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus

pytestmark = pytest.mark.integration


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
    """The version staged on English's index under English's binding."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Keeper:
    """The keeper Book's one spell: its root keeps the frame alive after the probed root is torn down."""


class Pooled:
    """A managed class, bound active."""


class PooledV2:
    """The managed class's next version: its own code, so its own spell_id (one object is one spell)."""

    def reset(self) -> None:
        """Return to the idle state before the next lease."""


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


def _book(frame: str, *, settle: bool) -> Spellbook:
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


class _World:
    """Handles of the probed Book: English active on its index, French parked on it, the root and the keeper."""

    def __init__(self, root: Conduit, english: Spell, french: Spell, keeper: Optional[Conduit]) -> None:
        """
        Keep the handles.

        Args:
            root: The probed Book's root conduit, 'lender'.
            english: The active English Spell.
            french: The parked French Spell.
            keeper: The keeper's root when the frame is kept alive, else None.
        """
        self.root = root
        self.english = english
        self.french = french
        self.index: SpellIndex = english.spell_index
        self.keeper = keeper


@contextlib.contextmanager
def _world(frame: str, *, keep_frame: bool) -> Iterator[_World]:
    """
    English active and French parked on English's index in a dynamic frame with caching off.

    Args:
        frame: The frame.
        keep_frame: Conjure a keeper root first, so the frame outlives the probed root; otherwise the probed root is
            the frame's only conduit.

    Yields:
        _World: The handles; the roots are torn down on exit (a teardown already done is a no-op).
    """
    keeper: Optional[Conduit] = None
    if keep_frame:
        keeper_book = _book(frame, settle=True)
        keeper_book.bind(spell=Keeper, existence=Existence.many, permissions="create")
        keeper = keeper_book.conjure(dynamic=True, name="keeper")
    book = _book(frame, settle=not keep_frame)
    english_id = book.bind(
        spell=English, spellframe=Greeter, binding_name="english", existence=Existence.many, permissions="create",
    )
    root = book.conjure(dynamic=True, name="lender")
    english = _owned(book, english_id)
    french_id = root.bind_inactive(
        spell=French, spell_index=english.spell_index, spellframe=Greeter, binding_name="english",
        existence=Existence.many, permissions="create",
    )
    world = _World(root, english, _owned(book, french_id), keeper)
    try:
        yield world
    finally:
        root.cleanup()
        if keeper is not None:
            keeper.cleanup()


@pytest.mark.parametrize("keep_frame", [True, False])
def test_book_teardown_cleans_a_parked_version_on_a_shared_index(keep_frame: bool) -> None:
    """
    Regression (probe T2): after its root's teardown a Book's parked version stayed uncleaned, and its `cleanup()`
    raised "Spellbook has already been cleaned.".

    Contract:
        - The root's teardown cleans English, the index and French, parked on it.
        - French's own `cleanup()` afterwards returns: the version is already retired.
    """
    with _world("shared_%s" % keep_frame, keep_frame=keep_frame) as world:
        assert not world.french.cleaned

        world.root.cleanup()

        assert world.english.cleaned
        assert world.index.cleaned
        assert world.french.cleaned
        world.french.cleanup()
        assert world.french.cleaned


@pytest.mark.parametrize("keep_frame", [True, False])
def test_book_teardown_cleans_a_parked_version_alone_in_its_own_index(keep_frame: bool) -> None:
    """
    Regression (probe T3): a version moved into an index of its own with `remove_from_spell_index` stayed uncleaned
    at its Book's teardown, and so did that index.

    Contract:
        - After the move French is the only member of a new index.
        - The root's teardown cleans French, its index and English's index.
    """
    with _world("minted_%s" % keep_frame, keep_frame=keep_frame) as world:
        world.root.remove_from_spell_index(spell_id=world.french.spell_id, source_index=world.index)
        minted = world.french.spell_index
        assert minted is not world.index
        assert minted.spells_in_index() == {world.french.spell_id}

        world.root.cleanup()

        assert world.french.cleaned
        assert minted.cleaned
        assert world.index.cleaned
        world.french.cleanup()


def test_book_teardown_with_only_active_versions_cleans_them_as_before() -> None:
    """
    Control (probe T1): a Book whose versions are all active tears down as it did.

    Contract:
        - The root's teardown cleans the active version and its index.
    """
    keeper_book = _book("active_only", settle=True)
    keeper_book.bind(spell=Keeper, existence=Existence.many, permissions="create")
    keeper = keeper_book.conjure(dynamic=True, name="keeper")
    book = _book("active_only", settle=False)
    english_id = book.bind(
        spell=English, spellframe=Greeter, binding_name="english", existence=Existence.many, permissions="create",
    )
    root = book.conjure(dynamic=True, name="lender")
    english = _owned(book, english_id)
    index = english.spell_index

    root.cleanup()

    assert english.cleaned
    assert index.cleaned
    keeper.cleanup()


def test_spellbook_cleanup_before_conjure_cleans_a_version_parked_before_conjure() -> None:
    """
    Regression (the Book's own cleanup, no root): a version staged with `bind_inactive` before conjure stayed
    uncleaned when its unconjured Book was cleaned.

    Contract:
        - `Spellbook.cleanup()` cleans English, its index and French, parked on it.
    """
    book = _book("unconjured", settle=True)
    english_id = book.bind(
        spell=English, spellframe=Greeter, binding_name="english", existence=Existence.many, permissions="create",
    )
    english = _owned(book, english_id)
    index = english.spell_index
    french_id = book.bind_inactive(
        spell=French, spell_index=index, spellframe=Greeter, binding_name="english", existence=Existence.many,
        permissions="create",
    )
    french = _owned(book, french_id)

    book.cleanup()

    assert english.cleaned
    assert index.cleaned
    assert french.cleaned


def test_a_parked_version_disposed_before_the_teardown_is_not_retired_twice() -> None:
    """
    Control: a parked version disposed with `cleanup_spell` leaves the Book's maps, so the teardown does not meet it.

    Contract:
        - `cleanup_spell` of French cleans it and keeps English's index; the root's teardown then cleans English and
          the index and raises nothing.
    """
    with _world("disposed_first", keep_frame=True) as world:
        world.root.cleanup_spell(spell=world.french)
        assert world.french.cleaned
        assert not world.index.cleaned

        world.root.cleanup()

        assert world.english.cleaned
        assert world.index.cleaned


def test_book_teardown_unregisters_the_pools_of_an_active_and_a_parked_managed_version() -> None:
    """
    Control (probe T5): the root store's teardown unregisters the pool of every managed version it holds, the parked
    version's included; the parked version itself is now cleaned too.

    Contract:
        - Before the teardown each version's pool is registered once; after it neither is, and both Spells read
          cleaned.
    """
    keeper_book = _book("managed", settle=True)
    keeper_book.bind(spell=Keeper, existence=Existence.many, permissions="create")
    keeper = keeper_book.conjure(dynamic=True, name="keeper")
    book = _book("managed", settle=False)
    active_id = book.bind(
        spell=Pooled, spellframe="pools", binding_name="pooled", existence=Existence.managed_spell_quantity,
        permissions="create", managed_spell_mode="limited_quantity", managed_spell_limit=1,
    )
    root = book.conjure(dynamic=True, name="lender")
    active = _owned(book, active_id)
    parked_id = root.bind_inactive(
        spell=PooledV2, spell_index=active.spell_index, spellframe="pools", binding_name="pooled",
        existence=Existence.managed_spell_quantity, permissions="create", managed_spell_mode="limited_quantity",
        managed_spell_limit=2,
    )
    parked = _owned(book, parked_id)
    assert len(ReleaseManagedSpell().describe(Pooled)) == 1
    assert len(ReleaseManagedSpell().describe(PooledV2)) == 1

    root.cleanup()

    assert len(ReleaseManagedSpell().describe(Pooled)) == 0
    assert len(ReleaseManagedSpell().describe(PooledV2)) == 0
    assert active.cleaned
    assert parked.cleaned
    keeper.cleanup()
