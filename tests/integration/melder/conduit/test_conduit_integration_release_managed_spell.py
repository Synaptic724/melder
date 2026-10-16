"""
Integration: ReleaseManagedSpell routes objects back to the pools of live roots (STORY-2026-10-15-release_managed_spell).

Through real Spellbooks and root conduits: conjure and a post-conjure bind register their pools, a release by class
reaches the right pool, the active version takes a same-class release and a notch moves it, two binding names are
told apart by spell id and two roots by conduit (a lesser naming its root), root and Aether teardown leave nothing
registered, and a lease's `with` gives its object back. Dispensing through a meld arrives with S5, so objects are
leased the way an emitted plan will: an idle pop, else `reserve` and build.
"""
from collections.abc import Iterator
from typing import Any, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
)

pytestmark = pytest.mark.integration


class Anchor:
    """A plain unique binding so each root has an ordinary spell beside the managed one."""


class Leased:
    """A managed target with a reset and a disposal method that log through the class."""

    log: List[str] = []

    def __init__(self, label: str = "built") -> None:
        """
        Keep a label for the log.

        Args:
            label: Name written to the log.
        """
        self.label = label

    def reset(self) -> None:
        """Record one reset."""
        Leased.log.append(f"reset:{self.label}")

    def close(self) -> None:
        """Record one disposal."""
        Leased.log.append(f"close:{self.label}")


def _reset_aether() -> None:
    """Install a fresh Aether (and with it a fresh registry) for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """A fresh Aether and an empty log per test."""
    _reset_aether()
    Leased.log = []
    yield
    _reset_aether()


def _automatic_book(frame: str = "default") -> Spellbook:
    """
    An automatic Book with one phase worker.

    Args:
        frame: The aetheric frame the Book lives in.

    Returns:
        Spellbook: The Book.
    """
    configuration = SpellbookConfiguration(aether_frame=frame)
    configuration.load_default_dictionary()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame=frame, configuration=configuration)


def _dynamic_book() -> Spellbook:
    """A dynamic Book with one phase worker."""
    configuration = SpellbookConfiguration(aether_frame="default")
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(aetheric_frame="default", configuration=configuration)


def _bind_managed(book_or_root: Any, *, binding_name: Any = None, **options: Any) -> str:
    """
    Bind `Leased` as a managed spell with `reset` on release and `close` on disposal.

    Args:
        book_or_root: A Spellbook or a root conduit.
        binding_name: The binding name, or None for the default binding.
        **options: Managed bind options.

    Returns:
        str: The spell id.
    """
    return book_or_root.bind(
        spell=Leased, binding_name=binding_name, existence=Existence.managed_spell_quantity, permissions="create",
        disposal_method_names=["close"], managed_spell_reset_methods=["reset"], **options,
    )


def _conjured(name: str = "managed-root", frame: str = "default", **binding: Any) -> Tuple[Spellbook, Conduit, str]:
    """
    An automatic root with Anchor and one managed `Leased` binding.

    Args:
        name: The root's name.
        frame: The frame.
        **binding: `_bind_managed` keywords.

    Returns:
        Tuple[Spellbook, Conduit, str]: The Book, its root and the managed spell id.
    """
    book = _automatic_book(frame)
    # One anchor per root: under process-wide spell ids an identical binding in a second frame would collide.
    book.bind(spell=Anchor, binding_name=f"anchor-{name}", existence=Existence.unique, permissions="create")
    spell_id = _bind_managed(book, **binding)
    root = book.conjure(name=name)
    return book, root, spell_id


def _out(pool: ManagedSpellQuantity, label: str) -> Leased:
    """
    Lease the way an emitted plan will: an idle pop, else reserve a place and build.

    Args:
        pool: The pool.
        label: Label of a newly built object.

    Returns:
        Leased: The leased object.
    """
    try:
        return pool._idle.pop()
    except IndexError:
        served = pool.reserve()
        return Leased(label) if served is None else served


def _pool_of(root: Conduit, spell_id: str) -> ManagedSpellQuantity:
    """
    Return the pool the root's store holds for one managed version.

    Args:
        root: The owning root.
        spell_id: The managed spell's spell_id.

    Returns:
        ManagedSpellQuantity: The pool.
    """
    pool = root._creations.get_managed_quantity(spell_id)
    assert pool is not None
    return pool


def test_conjure_registers_the_pool_and_a_release_by_class_reaches_it() -> None:
    """The class is all a release needs: reset, then idle for the next lease."""
    book, root, spell_id = _conjured()
    try:
        entries = ReleaseManagedSpell().describe(Leased)
        assert [(entry["spell_id"], entry["holding_conduit_id"], entry["active_version"]) for entry in entries] == [
            (spell_id, root.id, True),
        ]
        pool = _pool_of(root, spell_id)
        obj = _out(pool, "a")
        ReleaseManagedSpell().release(obj)
        assert (pool.idle_count, Leased.log) == (1, ["reset:a"])
        assert _out(pool, "b") is obj
    finally:
        root.cleanup()
        book.cleanup()


def test_root_teardown_unregisters_its_pools() -> None:
    """After the root ends, the class is managed nowhere."""
    book, root, spell_id = _conjured()
    root.cleanup()
    try:
        assert ReleaseManagedSpell().describe(Leased) == ()
        with pytest.raises(ValueError, match="Leased is not a managed spell class in any live root"):
            ReleaseManagedSpell().release(Leased())
    finally:
        book.cleanup()


def test_a_post_conjure_bind_registers_and_a_notch_moves_the_releases() -> None:
    """Two versions of one index: the active one takes a same-class release; a notch moves it."""
    book = _dynamic_book()
    book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    root = book.conjure(dynamic=True, name="managed-late")
    try:
        active_id = _bind_managed(root, managed_spell_limit=16)
        parked_id = root.bind_inactive(
            spell=Leased, spell_index=book.find_spell_by_id(active_id).spell_index,
            existence=Existence.managed_spell_quantity, permissions="create", disposal_method_names=["close"],
            managed_spell_limit=8,
        )
        active_pool, parked_pool = _pool_of(root, active_id), _pool_of(root, parked_id)
        assert sorted(entry["spell_id"] for entry in ReleaseManagedSpell().describe(Leased)) == sorted(
            [active_id, parked_id],
        )
        ReleaseManagedSpell().release(_out(active_pool, "first"))
        assert (active_pool.idle_count, parked_pool.idle_count) == (1, 0)
        # find_spell_by_id answers a parked id with the index's live spell; the notch needs the parked one.
        parked = book._get_owned_spell(parked_id)
        root.notch_spell(spell_index=parked.spell_index, spell=parked)
        ReleaseManagedSpell().release(_out(parked_pool, "second"))
        assert (active_pool.idle_count, parked_pool.idle_count) == (1, 1)
    finally:
        root.cleanup()
        book.cleanup()


def test_two_binding_names_in_one_root_need_a_spell_id() -> None:
    """Both versions are selected in their own index; the conduit alone cannot pick, the spell id can."""
    book = _automatic_book()
    book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    left_id = _bind_managed(book, binding_name="left")
    right_id = _bind_managed(book, binding_name="right")
    root = book.conjure(name="two-names")
    try:
        right = _pool_of(root, right_id)
        with pytest.raises(ValueError, match="Leased is managed by 2 pools: .*Pass spell_id=... or conduit=..."):
            ReleaseManagedSpell().release(Leased())
        with pytest.raises(ValueError, match="Leased is managed by 2 pools"):
            ReleaseManagedSpell().release(Leased(), conduit=root)
        ReleaseManagedSpell().release(_out(right, "r"), spell_id=right_id)
        assert (right.idle_count, _pool_of(root, left_id).idle_count) == (1, 0)
    finally:
        root.cleanup()
        book.cleanup()


def test_two_roots_are_told_apart_by_conduit_including_a_lesser() -> None:
    """The conduit names the root that holds the pool; a lesser names its root."""
    first_book, first_root, first_id = _conjured(name="first-root", frame="frame-one", binding_name="one")
    second_book, second_root, second_id = _conjured(name="second-root", frame="frame-two", binding_name="two")
    lesser = second_root.create_lesser_conduit()
    try:
        first_pool, second_pool = _pool_of(first_root, first_id), _pool_of(second_root, second_id)
        with pytest.raises(ValueError, match="Leased is managed by 2 pools"):
            ReleaseManagedSpell().release(Leased())
        ReleaseManagedSpell().release(_out(first_pool, "one"), conduit=first_root)
        ReleaseManagedSpell().release(_out(second_pool, "two"), conduit=lesser)
        assert (first_pool.idle_count, second_pool.idle_count) == (1, 1)
    finally:
        lesser.cleanup()
        second_root.cleanup()
        first_root.cleanup()
        second_book.cleanup()
        first_book.cleanup()


def test_a_cleaned_conduit_filter_is_refused() -> None:
    """A torn-down conduit names no root."""
    book, root, spell_id = _conjured()
    lesser = root.create_lesser_conduit()
    lesser.permanent_cleanup()
    try:
        with pytest.raises(RuntimeError, match="has already been cleaned"):
            ReleaseManagedSpell().release(Leased(), conduit=lesser)
    finally:
        root.cleanup()
        book.cleanup()


def test_a_lease_with_block_gives_the_object_back() -> None:
    """`managed(obj)` returns a lease whose block releases on exit."""
    book, root, spell_id = _conjured()
    try:
        pool = _pool_of(root, spell_id)
        obj = _out(pool, "leased")
        with ReleaseManagedSpell().managed(obj) as held:
            assert held is obj
            assert pool.idle_count == 0
        assert (pool.idle_count, Leased.log) == (1, ["reset:leased"])
    finally:
        root.cleanup()
        book.cleanup()


def test_aether_teardown_with_a_live_root_leaves_a_fresh_empty_registry() -> None:
    """The frames unregister their pools before Aether cleans the registry; the next boot starts empty."""
    book, root, spell_id = _conjured()
    pool = _pool_of(root, spell_id)
    ReleaseManagedSpell().release(_out(pool, "idle"))
    old_registry = ReleaseManagedSpell()
    _reset_aether()
    assert old_registry.cleaned is True
    assert pool.cleaned is True
    assert Leased.log == ["reset:idle", "close:idle"]
    assert ReleaseManagedSpell() is not old_registry
    assert ReleaseManagedSpell().describe(Leased) == ()
