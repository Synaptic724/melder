"""
Integration: managed pools and owner stamps through ownership transfers (STORY-2026-10-15-managed_ownership_transfer).

Real dynamic worlds: one frame, the owner root ("owner") and the receiving root ("target") in two Books. A moving
transfer carries every member's pool to the target and stamps every member that carries a stamp onto the target's
store; a transfer without a move gives the target fresh pools and leaves the old objects undisposed; a transfer that
fails after its rows moved leaves every pool, stamp and registry entry where it was. The same stamps decide where a
`unique` version's object lives after a failed transfer or a notch on the new owner.
"""
from collections.abc import Iterator
from typing import Any, List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership import TransferOfOwnership
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration
from tests._spell_identity_test_support import version_of

pytestmark = pytest.mark.integration


class Session:
    """The managed class: records its builds and whether it was disposed."""

    built: List["Session"] = []

    def __init__(self) -> None:
        """Record the build; not closed."""
        self.closed = False
        Session.built.append(self)

    def close(self) -> None:
        """The disposal method: mark closed."""
        self.closed = True

    def flush(self) -> None:
        """A second disposal step the parked version's binding names (its binding, not its version)."""


class Keeper:
    """A `unique` class; its staged second version is `version_of(Keeper, version=2)`."""

    def close(self) -> None:
        """Nothing to release."""


class Anchor:
    """A plain spell so the target Book conjures a root."""


def _reset_world() -> None:
    """Install a fresh Aether (and with it a fresh ReleaseManagedSpell) for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
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


def _configuration() -> SpellbookConfiguration:
    """A dynamic Book configuration with one phase worker."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _world(target_class: type = Session) -> Tuple[Spellbook, Spellbook, Conduit, Conduit, str]:
    """
    Two Books in one dynamic frame: the owner binds the class under test, the target binds Anchor.

    Args:
        target_class: Session (managed, limit 16, disposal "close") or Keeper (unique).

    Returns:
        Tuple: (owner Book, target Book, owner root, target root, the spell id of the owner's version).
    """
    configuration = _configuration()
    owner_book = Spellbook(configuration=configuration)
    if target_class is Session:
        spell_id = owner_book.bind(spell=Session, existence=Existence.managed_spell_quantity, permissions="create",
                                   disposal_method_names=["close"], managed_spell_limit=16)
    else:
        spell_id = owner_book.bind(spell=Keeper, existence=Existence.unique, permissions="create")
    target_book = Spellbook(configuration=configuration)
    target_book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    return owner_book, target_book, owner, target, spell_id


def _lease_two(conduit: Conduit, spell_id: str) -> Tuple[Session, Session]:
    """Lease two objects and release both, so the pool holds two idle objects."""
    one = conduit.meld(spell_id=spell_id)
    two = conduit.meld(spell_id=spell_id)
    ReleaseManagedSpell().release(one)
    ReleaseManagedSpell().release(two)
    return one, two


def _park_second_version(owner_book: Spellbook, owner: Conduit, spell_id: str, target_class: type = Session) -> Any:
    """
    Stage a second version of the owner's spell after conjure (a stamped parked member) and return its Spell.

    Args:
        owner_book: The owner Book.
        owner: The owner root.
        spell_id: The active version's id.
        target_class: Session (limit 8, disposal "close" and "flush") or Keeper (disposal "close"). The staged
            class is `version_of(target_class, version=2)`: one object is one spell (S1 of
            EPIC-2026-10-18-spell_identity_is_the_code), so a version is new code under the same name, and its
            settings and disposal names are its binding.

    Returns:
        Spell: The parked version.
    """
    spell_index = owner_book.find_spell_by_spell_id(spell_id).spell_index
    if target_class is Session:
        parked_id = owner.bind_inactive(spell=version_of(Session, version=2), spell_index=spell_index,
                                        existence=Existence.managed_spell_quantity, permissions="create",
                                        disposal_method_names=["close", "flush"], managed_spell_limit=8)
    else:
        parked_id = owner.bind_inactive(spell=version_of(Keeper, version=2), spell_index=spell_index,
                                        existence=Existence.unique, permissions="create",
                                        disposal_method_names=["close"])
    return owner_book._get_owned_spell(parked_id)


def _registry(owner: Conduit, target: Conduit) -> List[Tuple[str, str, int, int]]:
    """
    The registry's rows for Session and its versions: (spell id, holding root label, count, idle count), sorted.

    A staged version is a class of its own (one object is one spell), registered under that class, so the rows
    of every Session subclass count; a subclass with no live pool adds none.
    """
    labels = {owner.id: "owner", target.id: "target"}
    return sorted(
        (row["spell_id"], labels.get(row["holding_conduit_id"], row["holding_conduit_id"]), row["count"],
         row["idle_count"])
        for cls in (Session, *Session.__subclasses__())
        for row in ReleaseManagedSpell().describe(cls)
    )


def _failing_transfer(owner: Conduit, target: Conduit, spell_id: str, move: bool,
                      monkeypatch: pytest.MonkeyPatch) -> None:
    """Run a transfer that fails after its rows moved (the impact gating raises) and expect its error."""

    def boom(self: TransferOfOwnership, **kwargs: Any) -> None:
        raise RuntimeError("forced failure after the rows moved")

    monkeypatch.setattr(TransferOfOwnership, "_gate_transfer_impacts", boom)
    with pytest.raises(RuntimeError, match="forced failure after the rows moved"):
        owner.transfer_spell_ownership(spell=spell_id, target_conduit=target, move_creations=move)
    monkeypatch.undo()


def test_a_move_carries_the_pool_its_idle_objects_and_the_stamp_to_the_target() -> None:
    """The same pool object moves; the target's meld reuses an idle object; the registry names the target."""
    owner_book, target_book, owner, target, spell_id = _world()
    one, two = _lease_two(owner, spell_id)
    pool = owner._creations.get_managed_quantity(spell_id)

    owner.transfer_spell_ownership(spell=spell_id, target_conduit=target)

    assert owner._creations.get_managed_quantity(spell_id) is None
    assert target._creations.get_managed_quantity(spell_id) is pool
    assert _registry(owner, target) == [(spell_id, "target", 2, 2)]
    leased = target.meld(spell_id=spell_id)
    assert leased in (one, two)
    assert len(Session.built) == 2


def test_releases_after_a_move_reach_the_moved_pool() -> None:
    """A release by class after the move puts the object back into the pool the target now holds."""
    owner_book, target_book, owner, target, spell_id = _world()
    _lease_two(owner, spell_id)
    owner.transfer_spell_ownership(spell=spell_id, target_conduit=target)

    leased = target.meld(spell_id=spell_id)
    assert _registry(owner, target) == [(spell_id, "target", 2, 1)]
    ReleaseManagedSpell().release(leased)
    assert _registry(owner, target) == [(spell_id, "target", 2, 2)]
    assert not leased.closed


def test_a_parked_version_moved_and_notched_in_leases_from_its_moved_pool() -> None:
    """The parked version's pool and its stamp both move, so after a notch on the target it leases from that pool."""
    owner_book, target_book, owner, target, spell_id = _world()
    parked = _park_second_version(owner_book, owner, spell_id)
    parked_pool = owner._creations.get_managed_quantity(parked.spell_id)

    owner.transfer_spell_ownership(spell=spell_id, target_conduit=target)

    assert owner._creations.get_managed_quantity(parked.spell_id) is None
    assert target._creations.get_managed_quantity(parked.spell_id) is parked_pool
    target.notch_spell(spell_index=parked.spell_index, spell=parked)
    leased = target.meld(spell=Session)
    assert parked_pool.count == 1
    ReleaseManagedSpell().release(leased)
    assert parked_pool.idle_count == 1


def test_a_move_leaves_no_pool_registered_under_the_owner() -> None:
    """Every version's pool is registered under the target after a move; none under the owner."""
    owner_book, target_book, owner, target, spell_id = _world()
    parked = _park_second_version(owner_book, owner, spell_id)
    _lease_two(owner, spell_id)

    owner.transfer_spell_ownership(spell=spell_id, target_conduit=target)

    assert _registry(owner, target) == sorted([(spell_id, "target", 2, 2), (parked.spell_id, "target", 0, 0)])


def test_no_move_gives_the_target_a_fresh_pool_and_disposes_nothing() -> None:
    """The target builds from its own empty pool; the objects the owner pooled stay undisposed."""
    owner_book, target_book, owner, target, spell_id = _world()
    one, two = _lease_two(owner, spell_id)
    old_pool = owner._creations.get_managed_quantity(spell_id)

    owner.transfer_spell_ownership(spell=spell_id, target_conduit=target, move_creations=False)

    new_pool = target._creations.get_managed_quantity(spell_id)
    assert new_pool is not None and new_pool is not old_pool
    assert _registry(owner, target) == [(spell_id, "target", 0, 0)]
    leased = target.meld(spell_id=spell_id)
    assert leased not in (one, two)
    assert not one.closed and not two.closed


def test_no_move_with_a_parked_version_leases_from_the_target_after_a_notch() -> None:
    """
    The parked version is stamped onto the target, which composes its pool; the owner keeps its old one.

    Once that version is notched in, a release by class meets the second version's two pools - its class is its
    own, since one object is one spell - one in each root, both the selected version's, and raises the
    documented ambiguity; a release naming the conduit reaches the target's pool.
    """
    owner_book, target_book, owner, target, spell_id = _world()
    parked = _park_second_version(owner_book, owner, spell_id)
    old_parked_pool = owner._creations.get_managed_quantity(parked.spell_id)

    owner.transfer_spell_ownership(spell=spell_id, target_conduit=target, move_creations=False)

    assert owner._creations.get_managed_quantity(parked.spell_id) is old_parked_pool
    new_parked_pool = target._creations.get_managed_quantity(parked.spell_id)
    assert new_parked_pool is not None and new_parked_pool is not old_parked_pool
    target.notch_spell(spell_index=parked.spell_index, spell=parked)
    leased = target.meld(spell=Session)
    assert (new_parked_pool.count, old_parked_pool.count) == (1, 0)
    with pytest.raises(ValueError, match="is managed by 2 pools"):
        ReleaseManagedSpell().release(leased)
    ReleaseManagedSpell().release(leased, conduit=target)
    assert new_parked_pool.idle_count == 1


def test_a_failed_move_leaves_the_pool_and_the_stamp_with_the_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    """After the rollback the owner leases its own idle objects and a release by class reaches its pool."""
    owner_book, target_book, owner, target, spell_id = _world()
    one, two = _lease_two(owner, spell_id)
    pool = owner._creations.get_managed_quantity(spell_id)

    _failing_transfer(owner, target, spell_id, True, monkeypatch)

    assert owner._creations.get_managed_quantity(spell_id) is pool
    assert target._creations.get_managed_quantity(spell_id) is None
    assert _registry(owner, target) == [(spell_id, "owner", 2, 2)]
    leased = owner.meld(spell_id=spell_id)
    assert leased in (one, two)
    ReleaseManagedSpell().release(leased)
    assert _registry(owner, target) == [(spell_id, "owner", 2, 2)]


def test_a_failed_transfer_without_a_move_leaves_no_pool_in_the_target(monkeypatch: pytest.MonkeyPatch) -> None:
    """The pool the target's stamp composed is discarded; the owner keeps leasing and releasing its own pool."""
    owner_book, target_book, owner, target, spell_id = _world()
    one, two = _lease_two(owner, spell_id)
    pool = owner._creations.get_managed_quantity(spell_id)

    _failing_transfer(owner, target, spell_id, False, monkeypatch)

    assert owner._creations.get_managed_quantity(spell_id) is pool
    assert target._creations.get_managed_quantity(spell_id) is None
    assert _registry(owner, target) == [(spell_id, "owner", 2, 2)]
    leased = owner.meld(spell_id=spell_id)
    assert leased in (one, two)
    ReleaseManagedSpell().release(leased)
    assert not one.closed and not two.closed


def test_a_failed_move_leaves_a_parked_version_with_the_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    """The parked version's pool and stamp go back too: notched in on the owner, it leases from its own pool."""
    owner_book, target_book, owner, target, spell_id = _world()
    parked = _park_second_version(owner_book, owner, spell_id)
    parked_pool = owner._creations.get_managed_quantity(parked.spell_id)

    _failing_transfer(owner, target, spell_id, True, monkeypatch)

    assert target._creations.get_managed_quantity(parked.spell_id) is None
    assert owner._creations.get_managed_quantity(parked.spell_id) is parked_pool
    owner.notch_spell(spell_index=parked.spell_index, spell=parked)
    leased = owner.meld(spell=Session)
    assert parked_pool.count == 1
    ReleaseManagedSpell().release(leased)
    assert parked_pool.idle_count == 1


def test_a_failed_transfer_without_a_move_leaves_a_parked_version_with_the_owner(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The parked version's composed target pool is discarded and its stamp goes back to the owner."""
    owner_book, target_book, owner, target, spell_id = _world()
    parked = _park_second_version(owner_book, owner, spell_id)
    parked_pool = owner._creations.get_managed_quantity(parked.spell_id)

    _failing_transfer(owner, target, spell_id, False, monkeypatch)

    assert target._creations.get_managed_quantity(parked.spell_id) is None
    assert owner._creations.get_managed_quantity(parked.spell_id) is parked_pool
    owner.notch_spell(spell_index=parked.spell_index, spell=parked)
    owner.meld(spell=Session)
    assert parked_pool.count == 1


def test_a_failed_transfer_leaves_a_unique_object_with_the_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    """After the rollback the owner's meld returns the object it built before; the target stores none."""
    owner_book, target_book, owner, target, spell_id = _world(Keeper)
    first = owner.meld(spell_id=spell_id)

    _failing_transfer(owner, target, spell_id, True, monkeypatch)

    assert owner.meld(spell_id=spell_id) is first
    # Nothing of the spell is filed in the target, under any binding (STORY-2026-10-25-creations_store_slots_by_binding).
    assert target._creations.count_spell_creations(spell_id) == 0


def test_a_parked_unique_version_moved_and_notched_in_stores_its_object_in_the_target() -> None:
    """The moved parked version names the target's store, so its first meld there stores the object there."""
    owner_book, target_book, owner, target, spell_id = _world(Keeper)
    parked = _park_second_version(owner_book, owner, spell_id, Keeper)

    owner.transfer_spell_ownership(spell=spell_id, target_conduit=target)
    target.notch_spell(spell_index=parked.spell_index, spell=parked)
    built = target.meld(spell=Keeper)

    assert target._creations.get_creation(parked.store_key) is built
    assert owner._creations.count_spell_creations(parked.spell_id) == 0
