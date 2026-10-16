"""
Integration: managed objects dispensed through real worlds (STORY-2026-10-15-managed_dispense_codegen).

Roots in two frames and two binding names in one root dispense from their own pools; a post-conjure bind in a
dynamic world, a notch to another version, a borrower through a conduit link and a lesser's `managed_spell_meld`
all lease from the pool of the version they resolve, in its owner root's store; a world restored by the
Crystallizer dispenses from fresh, empty pools.
"""
from collections.abc import Iterator
from typing import Any, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
)

pytestmark = pytest.mark.integration


class Session:
    """The managed target; module-scoped so a restore can import it by qualname."""

    built: List["Session"] = []

    def __init__(self) -> None:
        """Record the build."""
        Session.built.append(self)


class Handler:
    """A `many` holder of one Session."""

    def __init__(self, session: Session) -> None:
        """
        Keep the session.

        Args:
            session: The leased session.
        """
        self.session = session


class Anchor:
    """A plain unique spell so every root has an ordinary member too."""


def _reset_world() -> None:
    """Fresh Aether, utility system, Nexus and Crystallizer singletons."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_world() -> Iterator[None]:
    """Isolate each test behind fresh singletons and an empty build log."""
    _reset_world()
    Session.built = []
    yield
    _reset_world()


@pytest.fixture()
def cache_root(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    """Route the crystallizer cache into a per-test directory."""
    from melder.crystallizer.asset_management import crystallizer_cache

    root = tmp_path / "__melder_cache__" / "__crystallizer_cache__"
    monkeypatch.setattr(
        crystallizer_cache.CrystallizerCache, "resolve_cache_root_path", staticmethod(lambda: root),
    )
    return root


def _automatic_book(frame: str = "default") -> Spellbook:
    """An automatic Book with one phase worker."""
    configuration = SpellbookConfiguration(aether_frame=frame)
    configuration.load_default_dictionary()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame=frame, configuration=configuration)


def _dynamic_book(frame: str = "default") -> Spellbook:
    """A dynamic Book with one phase worker, its configuration finalized first."""
    configuration = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(aetheric_frame=frame, configuration=configuration)


def _bind_session(book_or_root: Any, **options: Any) -> str:
    """Bind Session as a managed spell; return its id."""
    return book_or_root.bind(
        spell=Session, existence=Existence.managed_spell_quantity, permissions="create", **options,
    )


def _pool(root: Conduit, spell_id: str) -> ManagedSpellQuantity:
    """Return the pool the root's store holds for one managed version."""
    pool = root._creations.get_managed_quantity(spell_id)
    assert pool is not None
    return pool


def _two_roots() -> Tuple[Tuple[Spellbook, Conduit, str], Tuple[Spellbook, Conduit, str]]:
    """Two automatic roots in two frames, each with its own Session binding."""
    roots = []
    for frame, name in (("frame-one", "one"), ("frame-two", "two")):
        book = _automatic_book(frame)
        book.bind(spell=Anchor, binding_name=f"anchor-{name}", existence=Existence.unique, permissions="create")
        spell_id = _bind_session(book, binding_name=name)
        roots.append((book, book.conjure(name=f"root-{name}"), spell_id))
    return roots[0], roots[1]


def test_roots_in_two_frames_dispense_from_their_own_pools() -> None:
    """Each root leases from its own pool; a release names the root to pick the pool."""
    (first_book, first, first_id), (second_book, second, second_id) = _two_roots()
    try:
        leased = first.meld(spell_id=first_id)
        assert (_pool(first, first_id).count, _pool(second, second_id).count) == (1, 0)
        with pytest.raises(ValueError, match="Session is managed by 2 pools"):
            ReleaseManagedSpell().release(leased)
        ReleaseManagedSpell().release(leased, conduit=first)
        assert first.meld(spell_id=first_id) is leased
        assert second.meld(spell_id=second_id) is not leased
    finally:
        second.cleanup()
        first.cleanup()
        second_book.cleanup()
        first_book.cleanup()


def test_two_binding_names_in_one_root_dispense_from_two_pools() -> None:
    """One class bound twice: two versions, two pools, a release picks one by spell id."""
    book = _automatic_book()
    left_id = _bind_session(book, binding_name="left")
    right_id = _bind_session(book, binding_name="right")
    root = book.conjure(name="two-names")
    try:
        left = root.meld(spell=Session, binding_name="left")
        right = root.meld(spell=Session, binding_name="right")
        assert (_pool(root, left_id).count, _pool(root, right_id).count) == (1, 1)
        ReleaseManagedSpell().release(right, spell_id=right_id)
        assert root.meld(spell_id=right_id) is right
        assert root.meld(spell_id=left_id) is not left
    finally:
        root.cleanup()
        book.cleanup()


def test_post_conjure_bind_in_a_dynamic_world_dispenses() -> None:
    """A managed spell bound on a live dynamic root gets its pool at the bind and leases through holders."""
    book = _dynamic_book()
    book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    root = book.conjure(dynamic=True, name="late")
    try:
        spell_id = _bind_session(root)
        root.bind(spell=Handler, existence=Existence.many, permissions="create")
        handler = root.meld(spell=Handler)
        assert isinstance(handler.session, Session) and _pool(root, spell_id).count == 1
        ReleaseManagedSpell().release(handler.session)
        assert root.meld(spell=Handler).session is handler.session
    finally:
        root.cleanup()
        book.cleanup()


def test_a_notch_dispenses_from_the_new_versions_pool() -> None:
    """Versions coexist: after a notch melds lease from the active version's pool; the old pool keeps its objects."""
    book = _dynamic_book()
    book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    root = book.conjure(dynamic=True, name="versions")
    try:
        active_id = _bind_session(root, managed_spell_limit=16)
        parked_id = root.bind_inactive(
            spell=Session, spell_index=book.find_spell_by_id(active_id).spell_index,
            existence=Existence.managed_spell_quantity, permissions="create", managed_spell_limit=8,
        )
        old = root.meld(spell_id=active_id)
        ReleaseManagedSpell().release(old)
        parked = book._get_owned_spell(parked_id)
        root.notch_spell(spell_index=parked.spell_index, spell=parked)
        new = root.meld(spell=Session)
        assert new is not old
        assert (_pool(root, active_id).idle_count, _pool(root, parked_id).count) == (1, 1)
    finally:
        root.cleanup()
        book.cleanup()


def test_a_borrower_leases_from_the_owners_pool() -> None:
    """Through a link and a contract the borrower's melds lease from the owner root's pool."""
    owner_book, borrower_book = _dynamic_book(), _dynamic_book()
    spell_id = _bind_session(owner_book)
    owner_book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    borrower_book.bind(spell=Handler, existence=Existence.many, permissions="create")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(spell_id=spell_id, conduit=owner, permissions="create")
        assert borrower.validate_contracts_and_define()
        handler = borrower.meld(spell=Handler)
        assert isinstance(handler.session, Session) and _pool(owner, spell_id).count == 1
        ReleaseManagedSpell().release(handler.session)
        assert owner.meld(spell_id=spell_id) is handler.session
    finally:
        borrower.cleanup()
        owner.cleanup()
        borrower_book.cleanup()
        owner_book.cleanup()


def test_a_lessers_managed_spell_meld_returns_the_object_to_the_roots_pool() -> None:
    """`managed_spell_meld` on a lesser leases from, and gives back to, its root's pool."""
    book = _automatic_book()
    spell_id = _bind_session(book)
    root = book.conjure(name="with-lesser")
    lesser = root.create_lesser_conduit()
    try:
        with lesser.managed_spell_meld(Session) as session:
            assert _pool(root, spell_id).describe()["out_count"] == 1
        assert _pool(root, spell_id).idle_count == 1
        assert root.meld(spell=Session) is session
    finally:
        lesser.cleanup()
        root.cleanup()
        book.cleanup()


def test_a_restored_world_dispenses_from_an_empty_pool(cache_root: Any) -> None:
    """After a restart the rebuilt root's pool starts empty and leases, reuses and injects as before."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    book = _dynamic_book()
    book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    spell_id = _bind_session(book)
    book.bind(spell=Handler, existence=Existence.many, permissions="create")
    root = book.conjure(dynamic=True, name="recorded")
    root.meld(spell=Handler)
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    _reset_world()
    Session.built = []
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    rebooted = Crystallizer()
    rebooted.activate(configuration)
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    restored = Aether().get_root_conduit_by_name("recorded")
    pool = _pool(restored, spell_id)
    assert (pool.count, pool.idle_count) == (0, 0)
    handler = restored.meld(spell=Handler)
    ReleaseManagedSpell().release(handler.session)
    assert restored.meld(spell_id=spell_id) is handler.session
    assert len(Session.built) == 1
