"""
Integration: managed pools live in the owning root's store (STORY-2026-10-15-managed_quantity_pool, S3).

Through a real Spellbook and root conduit: conjure gives every active managed version a pool in the root's store, a
post-conjure bind and bind_inactive give theirs at the stamp, the root's teardown disposes what its pools hold (idle
objects and every recorded child) and leaves objects that are out to their holders, the conduit's purge answers zero
for a managed spell, the live-creation probes answer from the pool from the root and from a lesser, and disposing
the spell leaves its pool in place. Dispensing through a meld arrives with S5, so the tests lease the way an emitted
plan will: an idle pop, else `reserve` and build.
"""
from collections.abc import Iterator
from typing import List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
)

pytestmark = pytest.mark.integration


class Anchor:
    """A plain unique binding so the root has an ordinary spell beside the managed one."""


class Pooled:
    """A managed target whose disposal the tests count through a class-level log."""

    log: List[str] = []

    def __init__(self, label: str = "built") -> None:
        """
        Keep a label for the log.

        Args:
            label: Name written to the log on close.
        """
        self.label = label

    def close(self) -> None:
        """Record one disposal."""
        Pooled.log.append(self.label)


class OtherPooled(Pooled):
    """A second managed class, bound after conjure."""


def _reset_aether() -> None:
    """Install a fresh Aether singleton for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """A fresh Aether and an empty disposal log per test."""
    _reset_aether()
    Pooled.log = []
    yield
    _reset_aether()


def _automatic_book() -> Spellbook:
    """An automatic Book with one phase worker."""
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


def _dynamic_book() -> Spellbook:
    """A dynamic Book with one phase worker."""
    configuration = SpellbookConfiguration(aether_frame="default")
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(aetheric_frame="default", configuration=configuration)


def _bind_managed(book_or_root: object, spell: type = Pooled, **options: object) -> str:
    """
    Bind one managed class with `close` as its disposal method.

    Args:
        book_or_root: A Spellbook or a root conduit.
        spell: The class.
        **options: Managed bind options.

    Returns:
        str: The spell id.
    """
    return book_or_root.bind(
        spell=spell, existence=Existence.managed_spell_quantity, permissions="create",
        disposal_method_names=["close"], **options,
    )


def _conjured(managed_options: dict) -> Tuple[Spellbook, Conduit, str]:
    """
    An automatic root with Anchor and one managed Pooled binding.

    Args:
        managed_options: The managed bind options.

    Returns:
        Tuple[Spellbook, Conduit, str]: The Book, its root and the managed spell id.
    """
    book = _automatic_book()
    book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    spell_id = _bind_managed(book, **managed_options)
    root = book.conjure(name="managed-root")
    return book, root, spell_id


def _lease(pool: ManagedSpellQuantity, label: str) -> object:
    """
    Lease the way an emitted plan will: an idle pop, else reserve a place and build.

    Args:
        pool: The pool.
        label: Label of a newly built object.

    Returns:
        object: The leased object.
    """
    try:
        return pool._idle.pop()
    except IndexError:
        served = pool.reserve()
        return Pooled(label) if served is None else served


def test_conjure_gives_the_active_managed_version_a_pool_in_the_root_store() -> None:
    """The pool is composed from the Spell's options, owned by the root, beside no stored object."""
    book, root, spell_id = _conjured({"managed_spell_mode": "limited_quantity", "managed_spell_limit": 3})
    try:
        pool = root._creations.get_managed_quantity(spell_id)
        assert isinstance(pool, ManagedSpellQuantity)
        assert (pool.mode, pool.limit, pool.owner_conduit_id) == (ManagedSpellMode.limited_quantity, 3, root._id)
        assert pool.spell is book.find_spell_by_id(spell_id)
        assert root._creations.get_creation(spell_id) is None
    finally:
        root.cleanup()
        book.cleanup()


def test_a_dynamic_conjure_gives_the_pool_too() -> None:
    """The dynamic posture stamps owners the same way."""
    book = _dynamic_book()
    spell_id = _bind_managed(book, managed_spell_mode="queue", managed_spell_limit=2, managed_spell_timeout_seconds=1.0)
    root = book.conjure(dynamic=True, name="managed-dynamic")
    try:
        pool = root._creations.get_managed_quantity(spell_id)
        assert (pool.mode, pool.limit, pool.timeout_seconds) == (ManagedSpellMode.queue, 2, 1.0)
    finally:
        root.cleanup()
        book.cleanup()


def test_a_post_conjure_bind_and_bind_inactive_each_get_their_pool() -> None:
    """Stamping a version after conjure composes its pool in the root's store, active or parked."""
    book = _dynamic_book()
    book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    root = book.conjure(dynamic=True, name="managed-late")
    try:
        active_id = _bind_managed(root, OtherPooled, managed_spell_limit=16)
        parked_id = root.bind_inactive(
            spell=OtherPooled, spell_index=book.find_spell_by_id(active_id).spell_index,
            existence=Existence.managed_spell_quantity, permissions="create", disposal_method_names=["close"],
            managed_spell_limit=8,
        )
        active_pool = root._creations.get_managed_quantity(active_id)
        parked_pool = root._creations.get_managed_quantity(parked_id)
        assert (active_pool.limit, parked_pool.limit) == (16, 8)
        assert active_pool is not parked_pool
    finally:
        root.cleanup()
        book.cleanup()


def test_root_teardown_disposes_idle_objects_and_recorded_children_but_not_objects_out() -> None:
    """Teardown disposes what the pool holds; an object out is its holder's, though its recorded child dies."""
    book, root, spell_id = _conjured({"managed_spell_limit": 8})
    pool = root._creations.get_managed_quantity(spell_id)
    idle = _lease(pool, "idle")
    out = _lease(pool, "out")
    pool.adopt(out, [(Pooled("child-of-out"), ["close"])])
    pool.put_back(idle)
    try:
        root.cleanup()
        assert Pooled.log == ["idle", "child-of-out"]
        assert pool.cleaned is True
        assert out.label == "out"
    finally:
        book.cleanup()


def test_conduit_purge_of_a_managed_spell_returns_zero_and_keeps_the_pool() -> None:
    """Purge is not part of the managed design: nothing is retired."""
    book, root, spell_id = _conjured({})
    pool = root._creations.get_managed_quantity(spell_id)
    pool.put_back(_lease(pool, "idle"))
    try:
        assert root.purge(Pooled) == 0
        assert root.purge(spell_id=spell_id) == 0
        assert root._creations.get_managed_quantity(spell_id) is pool
        assert (pool.idle_count, Pooled.log) == (1, [])
    finally:
        root.cleanup()
        book.cleanup()


def test_live_creation_probes_answer_from_the_pool_from_the_root_and_a_lesser() -> None:
    """Live once the pool built an object; a lesser reads its root's pool."""
    book, root, spell_id = _conjured({})
    pool = root._creations.get_managed_quantity(spell_id)
    lesser = root.create_lesser_conduit()
    try:
        assert root.has_live_creation(spell=spell_id) is False
        _lease(pool, "out")
        status = root.describe_live_creation_status(spell=spell_id)
        assert (status["is_live"], status["creation_count"], status["storage_scope_kind"]) == (
            True, 1, "managed_pool",
        )
        assert status["storage_owner_conduit_id"] == root._id
        assert lesser.has_live_creation(spell=spell_id) is True
    finally:
        lesser.cleanup()
        root.cleanup()
        book.cleanup()


def test_disposing_the_managed_spell_leaves_its_pool_in_place() -> None:
    """cleanup_spell destroys nothing a pool holds: the old version's pool stays until the root ends."""
    book = _dynamic_book()
    book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    spell_id = _bind_managed(book)
    root = book.conjure(dynamic=True, name="managed-dispose")
    pool = root._creations.get_managed_quantity(spell_id)
    pool.put_back(_lease(pool, "idle"))
    try:
        root.cleanup_spell(spell=book.find_spell_by_id(spell_id))
        assert root._creations.get_managed_quantity(spell_id) is pool
        assert (pool.idle_count, Pooled.log) == (1, [])
    finally:
        root.cleanup()
        book.cleanup()
    assert Pooled.log == ["idle"]
