"""
Unit tests of the managed pools in a Creations store (STORY-2026-10-15-managed_quantity_pool, S3).

Scope:
    `Creations.ensure_managed_quantity` / `get_managed_quantity` and the pool map they keep beside `_creations`;
    the store verbs that meet a pool: cleanup (pools before the disposable registry, failures in the store's
    group), extract/restore (the `managed` row an ownership transfer moves), purge (zero, nothing touched) and the
    reusable clears that root stores never run (pools untouched). Since S4 (STORY-2026-10-15-release_managed_spell)
    the store registers every pool it takes with `ReleaseManagedSpell` and unregisters every pool it gives up.
"""
import threading
from collections.abc import Iterator
from threading import RLock
from typing import Any, List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.conduit_creations import ConduitCreations
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spellbook import Spellbook


class _SpellStub:
    """The Spell fields the store and the pool read: identity, Existence, options, disposal names, build lock."""

    def __init__(
            self,
            spell_id: str = "managed-sid",
            *,
            existence: Existence = Existence.managed_spell_quantity,
            mode: Optional[ManagedSpellMode] = ManagedSpellMode.elastic,
            limit: Optional[int] = 256,
            disposal: Tuple[str, ...] = ("close",),
            target: Optional[type] = None,
    ) -> None:
        """
        Keep the fields.

        Args:
            spell_id: The spell's spell_id.
            existence: The binding's Existence.
            mode: The managed mode.
            limit: The managed limit.
            disposal: The disposal method names.
            target: The managed class; `_Probe` when omitted.
        """
        self.spell_id = spell_id
        # The managed class: the key ReleaseManagedSpell routes releases by (S4).
        self.spell: type = target if target is not None else _Probe
        self.spell_index = SpellIndex(spell_id)
        self.spell_name = f"Spell<{spell_id}>"
        self.binding_name = None
        self.aetheric_frame = "default"
        self.existence = existence
        self.disposal_method_names = list(disposal)
        self.managed_spell_mode = mode
        self.managed_spell_limit = limit
        self.managed_spell_timeout_seconds = None
        self.managed_spell_reset_methods = ()
        self._lock = RLock()

    def _spell_index_unless_cleaned(self) -> Optional[SpellIndex]:
        """Return the version's index (the registry's selected-version read)."""
        return self.spell_index


class _Probe:
    """Disposal probe writing its label to a shared log; raises on request."""

    def __init__(self, label: str, log: List[str], *, fail: bool = False) -> None:
        """
        Keep the label, the log and the failure switch.

        Args:
            label: Name written on close.
            log: Shared ordered log.
            fail: Whether close raises after logging.
        """
        self.label = label
        self.log = log
        self.fail = fail

    def close(self) -> None:
        """Log one disposal; raise when asked to."""
        self.log.append(self.label)
        if self.fail:
            raise OSError(self.label)


def _idle_object(pool: ManagedSpellQuantity, obj: object) -> object:
    """
    Put one built object into the pool the way a lease and a release do.

    Args:
        pool: The pool.
        obj: The object the plan built into the reserved place.

    Returns:
        object: The same object, now idle.
    """
    assert pool.reserve() is None
    pool.put_back(obj)
    return obj


def _reset_world() -> None:
    """Install a fresh Aether, and with it a fresh ReleaseManagedSpell, for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_registry() -> Iterator[None]:
    """A fresh registry per test, so the pools one test registers never meet another's releases."""
    _reset_world()
    yield
    _reset_world()


@pytest.fixture
def store() -> ConduitCreations:
    """A root store per test."""
    return ConduitCreations(conduit_id="root-1")


def test_ensure_builds_one_pool_owned_by_the_store(store: ConduitCreations) -> None:
    """The pool is composed from the Spell and owned by the store's conduit."""
    spell = _SpellStub(mode=ManagedSpellMode.limited_quantity, limit=4)
    pool = store.ensure_managed_quantity(spell)
    assert isinstance(pool, ManagedSpellQuantity)
    assert store.get_managed_quantity("managed-sid") is pool
    assert (pool.spell, pool.owner_conduit_id, pool.mode, pool.limit) == (
        spell, "root-1", ManagedSpellMode.limited_quantity, 4,
    )


def test_ensure_is_idempotent(store: ConduitCreations) -> None:
    """A second stamp of the same version keeps its pool."""
    spell = _SpellStub()
    assert store.ensure_managed_quantity(spell) is store.ensure_managed_quantity(spell)


def test_ensure_points_a_kept_pool_at_the_newest_spell_object(store: ConduitCreations) -> None:
    """A rebind under the same content-stable id meets the old pool, which then describes the new Spell."""
    old, new = _SpellStub(), _SpellStub()
    pool = store.ensure_managed_quantity(old)
    assert store.ensure_managed_quantity(new) is pool
    assert pool.spell is new


def test_ensure_refuses_a_non_managed_spell(store: ConduitCreations) -> None:
    """No pool for another Existence; the map stays empty."""
    with pytest.raises(ValueError, match="needs an Existence.managed_spell_quantity spell"):
        store.ensure_managed_quantity(_SpellStub(existence=Existence.unique, mode=None, limit=None))
    assert store.get_managed_quantity("managed-sid") is None


def test_ensure_refuses_a_cleaned_store(store: ConduitCreations) -> None:
    """A torn-down store takes no pool."""
    store.cleanup()
    with pytest.raises(RuntimeError, match="has already been cleaned"):
        store.ensure_managed_quantity(_SpellStub())


def test_a_pool_is_never_a_creation(store: ConduitCreations) -> None:
    """Resolution reads `_creations` only, and a pool never lands there."""
    store.ensure_managed_quantity(_SpellStub())
    assert store.get_creation("managed-sid") is None
    assert store._creations == {} and store._disposable_creations == {}


def test_get_managed_quantity_answers_none_for_an_unknown_id(store: ConduitCreations) -> None:
    """No pool, no answer."""
    assert store.get_managed_quantity("nothing-here") is None


def test_purge_of_a_managed_spell_returns_zero_and_touches_nothing(store: ConduitCreations) -> None:
    """Purge is not part of the managed design: the pool and its idle objects stay."""
    log: List[str] = []
    spell = _SpellStub()
    pool = store.ensure_managed_quantity(spell)
    idle = _idle_object(pool, _Probe("idle", log))
    assert store.purge(spell) == 0
    assert store.purge(spell, purge_all=False, creation=idle) == 0
    assert store.get_managed_quantity("managed-sid") is pool
    assert (pool.idle_count, pool.count) == (1, 1)
    assert log == []


def test_cleanup_cleans_pools_before_the_disposable_registry(store: ConduitCreations) -> None:
    """Pooled objects may hold the store's uniques, so the pools go first."""
    log: List[str] = []
    store.add_creation("unique-sid", _Probe("unique", log), has_disposal_methods=True, disposal_methods=["close"])
    pool = store.ensure_managed_quantity(_SpellStub())
    _idle_object(pool, _Probe("pooled", log))
    store.cleanup()
    assert log == ["pooled", "unique"]
    assert pool.cleaned is True


def test_cleanup_cleans_the_newest_pool_first(store: ConduitCreations) -> None:
    """Pools follow the store's newest-first teardown."""
    log: List[str] = []
    first = store.ensure_managed_quantity(_SpellStub("first"))
    second = store.ensure_managed_quantity(_SpellStub("second"))
    _idle_object(first, _Probe("first", log))
    _idle_object(second, _Probe("second", log))
    store.cleanup()
    assert log == ["second", "first"]


def test_cleanup_raises_pool_failures_in_the_stores_group(store: ConduitCreations) -> None:
    """A failing pooled object is one chained RuntimeError in the store's group, beside the registry's."""
    log: List[str] = []
    store.add_creation(
        "unique-sid", _Probe("unique", log, fail=True), has_disposal_methods=True, disposal_methods=["close"],
    )
    pool = store.ensure_managed_quantity(_SpellStub())
    _idle_object(pool, _Probe("pooled", log, fail=True))
    with pytest.raises(ExceptionGroup) as excinfo:
        store.cleanup()
    assert log == ["pooled", "unique"]
    errors = excinfo.value.exceptions
    assert len(errors) == 2
    assert all(isinstance(error, RuntimeError) and isinstance(error.__cause__, OSError) for error in errors)


def test_extract_hands_the_pool_over_as_a_managed_row(store: ConduitCreations) -> None:
    """The row carries the same pool object; the store gives it up."""
    pool = store.ensure_managed_quantity(_SpellStub())
    rows = store.extract_spell_creations("managed-sid")
    assert rows == [{"scope": "managed", "disposable": False, "stored": pool}]
    assert store.get_managed_quantity("managed-sid") is None
    assert store.extract_spell_creations("managed-sid") == []


def test_restore_installs_the_moved_pool_with_its_idle_objects(store: ConduitCreations) -> None:
    """The target store takes the same pool object; its idle objects and count travel with it."""
    log: List[str] = []
    source = ConduitCreations(conduit_id="source")
    pool = source.ensure_managed_quantity(_SpellStub())
    idle = _idle_object(pool, _Probe("idle", log))
    store.restore_spell_creations("managed-sid", source.extract_spell_creations("managed-sid"))
    assert store.get_managed_quantity("managed-sid") is pool
    assert pool._idle[-1] is idle and pool.count == 1
    assert log == []


def test_restore_cleans_the_pool_it_replaces(store: ConduitCreations) -> None:
    """The empty pool a transfer flip composed is retired when the moved pool arrives."""
    log: List[str] = []
    composed = store.ensure_managed_quantity(_SpellStub())
    _idle_object(composed, _Probe("composed", log))
    source = ConduitCreations(conduit_id="source")
    moved = source.ensure_managed_quantity(_SpellStub())
    store.restore_spell_creations("managed-sid", source.extract_spell_creations("managed-sid"))
    assert store.get_managed_quantity("managed-sid") is moved
    assert composed.cleaned is True
    assert log == ["composed"]


def test_restore_of_the_pool_already_held_cleans_nothing(store: ConduitCreations) -> None:
    """A row carrying the store's own pool is a no-op for that pool."""
    pool = store.ensure_managed_quantity(_SpellStub())
    store.restore_spell_creations("managed-sid", [{"scope": "managed", "disposable": False, "stored": pool}])
    assert store.get_managed_quantity("managed-sid") is pool
    assert pool.cleaned is False


def test_restore_raises_the_replaced_pools_failures_after_installing(store: ConduitCreations) -> None:
    """The moved pool is in place even when retiring the replaced one failed."""
    log: List[str] = []
    composed = store.ensure_managed_quantity(_SpellStub())
    _idle_object(composed, _Probe("composed", log, fail=True))
    source = ConduitCreations(conduit_id="source")
    moved = source.ensure_managed_quantity(_SpellStub())
    with pytest.raises(ExceptionGroup, match="replaced while restoring spell 'managed-sid'"):
        store.restore_spell_creations("managed-sid", source.extract_spell_creations("managed-sid"))
    assert store.get_managed_quantity("managed-sid") is moved


def test_reusable_clears_never_touch_a_pool() -> None:
    """Only root stores hold pools and roots never clear their store this way; a clear leaves pools alone."""
    log: List[str] = []
    plain = Creations(owner_conduit_id="root-1", id="root-1")
    pool = plain.ensure_managed_quantity(_SpellStub())
    _idle_object(pool, _Probe("idle", log))
    plain.add_creation("unique-sid", _Probe("unique", log), has_disposal_methods=True, disposal_methods=["close"])
    plain.clear_all()
    plain.reset_for_pool()
    assert plain.get_managed_quantity("managed-sid") is pool
    assert log == ["unique"]
    assert pool.idle_count == 1


def _registered(cls: type) -> List[Tuple[str, str]]:
    """
    Return the registry's view of one class: (spell id, holding root) per pool, in registration order.

    Args:
        cls: The managed class.

    Returns:
        List[Tuple[str, str]]: One pair per registered pool.
    """
    return [(entry["spell_id"], entry["holding_conduit_id"]) for entry in ReleaseManagedSpell().describe(cls)]


def test_ensure_registers_the_pool_under_its_class_and_the_stores_root(store: ConduitCreations) -> None:
    """A store that takes a pool registers it, so a release of its class reaches it."""
    pool = store.ensure_managed_quantity(_SpellStub())
    assert _registered(_Probe) == [("managed-sid", "root-1")]
    assert pool.reserve() is None
    ReleaseManagedSpell().release(_Probe("released", []))
    assert pool.idle_count == 1


def test_a_second_stamp_registers_nothing_new(store: ConduitCreations) -> None:
    """Ensure is idempotent, and so is its registration."""
    store.ensure_managed_quantity(_SpellStub())
    store.ensure_managed_quantity(_SpellStub())
    assert _registered(_Probe) == [("managed-sid", "root-1")]


def test_a_rebind_bringing_another_class_moves_the_registration(store: ConduitCreations) -> None:
    """The kept pool is re-keyed under the new class object."""

    class _Redefined:
        """A redefinition of the managed class."""

    store.ensure_managed_quantity(_SpellStub())
    store.ensure_managed_quantity(_SpellStub(target=_Redefined))
    assert _registered(_Probe) == []
    assert _registered(_Redefined) == [("managed-sid", "root-1")]


def test_extract_unregisters_the_pool_it_gives_up(store: ConduitCreations) -> None:
    """A pool in flight between stores is not routable."""
    store.ensure_managed_quantity(_SpellStub())
    store.extract_spell_creations("managed-sid")
    assert _registered(_Probe) == []


def test_restore_registers_the_moved_pool_under_the_restoring_root(store: ConduitCreations) -> None:
    """The pool is routable again, held by the store that took it."""
    source = ConduitCreations(conduit_id="source")
    source.ensure_managed_quantity(_SpellStub())
    assert _registered(_Probe) == [("managed-sid", "source")]
    store.restore_spell_creations("managed-sid", source.extract_spell_creations("managed-sid"))
    assert _registered(_Probe) == [("managed-sid", "root-1")]


def test_restore_unregisters_the_pool_it_replaces(store: ConduitCreations) -> None:
    """The composed pool leaves the registry; releases reach the moved one."""
    composed = store.ensure_managed_quantity(_SpellStub())
    source = ConduitCreations(conduit_id="source")
    moved = source.ensure_managed_quantity(_SpellStub())
    store.restore_spell_creations("managed-sid", source.extract_spell_creations("managed-sid"))
    assert _registered(_Probe) == [("managed-sid", "root-1")]
    assert moved.reserve() is None
    ReleaseManagedSpell().release(_Probe("moved", []))
    assert (moved.idle_count, composed.cleaned) == (1, True)


def test_restore_of_a_pool_the_store_already_holds_keeps_it_registered(store: ConduitCreations) -> None:
    """A row carrying the store's own pool changes nothing in the registry."""
    pool = store.ensure_managed_quantity(_SpellStub())
    store.restore_spell_creations("managed-sid", [{"scope": "managed", "disposable": False, "stored": pool}])
    assert _registered(_Probe) == [("managed-sid", "root-1")]


def test_cleanup_unregisters_every_pool(store: ConduitCreations) -> None:
    """A torn-down root leaves no routable pool behind."""
    store.ensure_managed_quantity(_SpellStub("first"))
    store.ensure_managed_quantity(_SpellStub("second"))
    store.cleanup()
    assert _registered(_Probe) == []


def test_a_store_cleaned_after_the_registry_is_gone_still_cleans(store: ConduitCreations) -> None:
    """Teardown does not need the registry: with it gone, there is nothing to unregister from."""
    pool = store.ensure_managed_quantity(_SpellStub())
    ReleaseManagedSpell._reset_singleton_for_tests()
    store.cleanup()
    assert pool.cleaned is True


def test_ensure_with_new_settings_keeps_the_pool_and_takes_the_settings(store: ConduitCreations) -> None:
    """A rebind under the same spell_id with other settings meets the pool, which takes them (0.2.8254)."""
    first = store.ensure_managed_quantity(_SpellStub(mode=ManagedSpellMode.limited_quantity, limit=1))
    rebound = _SpellStub(mode=ManagedSpellMode.limited_quantity, limit=2)
    second = store.ensure_managed_quantity(rebound)
    assert second is first
    assert (second.limit, second.spell) == (2, rebound)
    assert [entry["spell_id"] for entry in ReleaseManagedSpell().describe(_Probe)] == ["managed-sid"]


def test_ensure_rebinds_an_existing_pool_after_releasing_the_store_lock(
        store: ConduitCreations,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The rebind takes the pool's lock, so it runs with the store lock free: the store lock stays a leaf."""
    store.ensure_managed_quantity(_SpellStub())
    store_lock_free: List[bool] = []
    original = ManagedSpellQuantity._rebind_spell

    def _spy(pool: ManagedSpellQuantity, spell: Any) -> None:
        probe: List[bool] = []

        def _try_store_lock() -> None:
            acquired = store._lock.acquire(timeout=1.0)
            probe.append(acquired)
            if acquired:
                store._lock.release()

        prober = threading.Thread(target=_try_store_lock)
        prober.start()
        prober.join()
        store_lock_free.append(probe[0])
        original(pool, spell)

    monkeypatch.setattr(ManagedSpellQuantity, "_rebind_spell", _spy, raising=True)
    store.ensure_managed_quantity(_SpellStub())
    assert store_lock_free == [True]
