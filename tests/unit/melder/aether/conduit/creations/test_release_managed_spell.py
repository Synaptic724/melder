"""
Unit tests of ReleaseManagedSpell, the class-keyed registry of managed pools (STORY-2026-10-15-release_managed_spell, S4).

Scope:
    The Aether-owned singleton (construction, ownership, cleanup, the reset hook), the registry the stores keep
    (`register` / `unregister`), the release fast path and the cold resolver (not managed, filters, the selected
    version, ambiguity), `managed`, `release_all` and `describe`. Pools are real `ManagedSpellQuantity` objects over
    stub Spells carrying a real `SpellIndex`; a root conduit is only needed for the `conduit` filter, which the
    integration tests drive.
"""
from collections.abc import Iterator
from typing import Any, List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.managed_spell_lease import ManagedSpellLease
from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spellbook import Spellbook


class Pooled:
    """A managed class whose resets and disposals write to a class-level log."""

    log: List[str] = []

    def __init__(self, label: str = "built", *, fail_reset: bool = False) -> None:
        """
        Keep a label and the reset failure switch.

        Args:
            label: Name written to the log.
            fail_reset: Whether `reset` raises after logging.
        """
        self.label = label
        self.fail_reset = fail_reset

    def reset(self) -> None:
        """Log one reset, then fail when asked to."""
        Pooled.log.append(f"reset:{self.label}")
        if self.fail_reset:
            raise ValueError(f"reset failed: {self.label}")

    def close(self) -> None:
        """Log one disposal."""
        Pooled.log.append(f"close:{self.label}")


class OtherPooled:
    """A second managed class."""

    def close(self) -> None:
        """Dispose nothing."""


class PooledChild(Pooled):
    """A subclass: a class of its own for the registry, never routed to its base's pool."""


class _SpellStub:
    """The Spell fields a pool and the resolver read, with a real SpellIndex."""

    def __init__(
            self,
            spell_id: str = "sid-1",
            *,
            target: type = Pooled,
            binding_name: Optional[str] = "pooled",
            frame: str = "default",
            index: Optional[SpellIndex] = None,
            resets: Tuple[str, ...] = (),
    ) -> None:
        """
        Keep the identity, the class, an elastic managed policy and the index.

        Args:
            spell_id: The spell's spell_id.
            target: The managed class.
            binding_name: The binding name.
            frame: The frame name.
            index: The version's index; a fresh one selecting `spell_id` when omitted.
            resets: The reset method names.
        """
        self.spell_id = spell_id
        self.spell = target
        self.spell_name = target.__name__
        self.binding_name = binding_name
        self.aetheric_frame = frame
        self.existence = Existence.managed_spell_quantity
        self.disposal_method_names = ["close"]
        self.managed_spell_mode = ManagedSpellMode.elastic
        self.managed_spell_limit = 256
        self.managed_spell_timeout_seconds = None
        self.managed_spell_reset_methods = tuple(resets)
        self.spell_index = index if index is not None else SpellIndex(spell_id)
        self.cleaned = False

    def _spell_index_unless_cleaned(self) -> Optional[SpellIndex]:
        """Return the index, or None once the stub is marked cleaned."""
        return None if self.cleaned else self.spell_index


def _reset_world() -> None:
    """Install a fresh Aether (and with it a fresh registry) for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_registry() -> Iterator[None]:
    """A fresh Aether-owned registry and an empty log per test."""
    _reset_world()
    Pooled.log = []
    yield
    _reset_world()


def _pool(spell: Optional[_SpellStub] = None, *, root: str = "root-1", register: bool = True) -> ManagedSpellQuantity:
    """
    Build one pool over a stub Spell and register it the way a store does.

    Args:
        spell: The stub Spell; a default `Pooled` binding when omitted.
        root: The holding root's id.
        register: Whether to register it.

    Returns:
        ManagedSpellQuantity: The pool.
    """
    pool = ManagedSpellQuantity(spell=spell if spell is not None else _SpellStub(), owner_conduit_id=root)
    if register:
        ReleaseManagedSpell().register(pool, root_conduit_id=root)
    return pool


def _out(pool: ManagedSpellQuantity, obj: Any) -> Any:
    """
    Count one object out of the pool the way a miss does.

    Args:
        pool: The pool.
        obj: The object built into the reserved place.

    Returns:
        Any: The object, now out.
    """
    assert pool.reserve() is None
    return obj


# ---------------------------------------------------------------- the singleton


def test_the_registry_is_one_process_singleton_owned_by_aether() -> None:
    """Every construction returns the instance Aether built and holds."""
    registry = ReleaseManagedSpell()
    assert ReleaseManagedSpell() is registry
    assert Aether()._release_managed_spell is registry
    assert registry.cleaned is False


def test_a_bare_first_construction_without_aether_is_refused() -> None:
    """Only Aether creates the registry; a refused construction leaves a later proper one possible."""
    ReleaseManagedSpell._reset_singleton_for_tests()
    with pytest.raises(ValueError, match="ReleaseManagedSpell is created by Aether at boot"):
        ReleaseManagedSpell()
    fresh = ReleaseManagedSpell(aether=Aether())
    assert fresh.cleaned is False
    assert ReleaseManagedSpell() is fresh


def test_aether_teardown_cleans_the_registry_and_the_next_aether_builds_a_fresh_one() -> None:
    """Aether cleans what it hosts; the next boot hosts a new registry."""
    registry = ReleaseManagedSpell()
    _reset_world()
    assert registry.cleaned is True
    assert ReleaseManagedSpell() is not registry
    assert ReleaseManagedSpell() is Aether()._release_managed_spell


def test_the_reset_hook_cleans_the_instance_and_clears_the_singleton() -> None:
    """The test reset cleans the live registry; the next bare construction no longer finds it."""
    registry = ReleaseManagedSpell()
    ReleaseManagedSpell._reset_singleton_for_tests()
    assert registry.cleaned is True
    with pytest.raises(ValueError, match="created by Aether"):
        ReleaseManagedSpell()


def test_the_reset_hook_without_an_instance_does_nothing() -> None:
    """Resetting twice is harmless."""
    ReleaseManagedSpell._reset_singleton_for_tests()
    ReleaseManagedSpell._reset_singleton_for_tests()
    with pytest.raises(ValueError, match="created by Aether"):
        ReleaseManagedSpell()


def test_cleanup_is_idempotent_and_clears_the_singleton() -> None:
    """A second cleanup does nothing; the cleaned instance is never handed out again."""
    registry = ReleaseManagedSpell()
    registry.cleanup()
    registry.cleanup()
    assert registry.cleaned is True
    assert ReleaseManagedSpell._live_instance() is None


def test_live_instance_answers_the_aether_owned_registry_and_none_once_cleaned() -> None:
    """The stores' lookup finds the live registry, and nothing once it is gone."""
    registry = ReleaseManagedSpell()
    assert ReleaseManagedSpell._live_instance() is registry
    registry.cleanup()
    assert ReleaseManagedSpell._live_instance() is None


def test_a_cleaned_registry_refuses_every_verb_but_unregister() -> None:
    """Use after cleanup raises the cleaned error; unregister, part of teardown, does nothing."""
    pool = _pool()
    registry = ReleaseManagedSpell()
    registry.cleanup()
    with pytest.raises(RuntimeError, match="ReleaseManagedSpell has already been cleaned"):
        registry.release(Pooled())
    with pytest.raises(RuntimeError, match="ReleaseManagedSpell has already been cleaned"):
        registry.managed(Pooled())
    with pytest.raises(RuntimeError, match="ReleaseManagedSpell has already been cleaned"):
        registry.describe(Pooled)
    with pytest.raises(RuntimeError, match="ReleaseManagedSpell has already been cleaned"):
        registry.register(pool, root_conduit_id="root-1")
    registry.unregister(pool)


def test_cleanup_never_cleans_a_registered_pool() -> None:
    """Pools belong to their stores; the registry only forgets them."""
    pool = _pool()
    ReleaseManagedSpell().cleanup()
    assert pool.cleaned is False


# ---------------------------------------------------------------- register / unregister


def test_a_registered_pool_takes_releases_of_its_class() -> None:
    """One dict get by class reaches the pool."""
    pool = _pool()
    obj = _out(pool, Pooled("a"))
    ReleaseManagedSpell().release(obj)
    assert pool.idle_count == 1
    assert pool.count == 1


def test_register_is_idempotent() -> None:
    """Registering a pool twice lists it once."""
    pool = _pool()
    ReleaseManagedSpell().register(pool, root_conduit_id="root-1")
    assert len(ReleaseManagedSpell().describe(Pooled)) == 1


def test_register_records_the_root_that_holds_the_pool_now() -> None:
    """A restore into another root re-registers the same pool under that root."""
    pool = _pool(root="root-1")
    assert ReleaseManagedSpell().describe(Pooled)[0]["holding_conduit_id"] == "root-1"
    ReleaseManagedSpell().register(pool, root_conduit_id="root-2")
    entries = ReleaseManagedSpell().describe(Pooled)
    assert [entry["holding_conduit_id"] for entry in entries] == ["root-2"]


def test_register_rekeys_a_pool_whose_class_changed() -> None:
    """A rebind under the same id that brings another class object moves the pool to that class."""
    pool = _pool(_SpellStub(target=Pooled))
    pool._rebind_spell(_SpellStub(target=OtherPooled))
    ReleaseManagedSpell().register(pool, root_conduit_id="root-1")
    assert ReleaseManagedSpell().describe(Pooled) == ()
    assert [entry["spell_id"] for entry in ReleaseManagedSpell().describe(OtherPooled)] == ["sid-1"]


def test_register_refuses_a_pool_torn_down_with_its_root() -> None:
    """A store never hands the registry a retired pool."""
    pool = _pool(register=False)
    pool.cleanup()
    with pytest.raises(RuntimeError, match="ManagedSpellQuantity has already been cleaned"):
        ReleaseManagedSpell().register(pool, root_conduit_id="root-1")


def test_unregister_forgets_the_pool() -> None:
    """After a store gives the pool up, its class is no longer managed anywhere."""
    pool = _pool()
    ReleaseManagedSpell().unregister(pool)
    assert ReleaseManagedSpell().describe(Pooled) == ()
    with pytest.raises(ValueError, match="is not a managed spell class in any live root"):
        ReleaseManagedSpell().release(Pooled())


def test_unregister_is_idempotent_and_ignores_an_unknown_pool() -> None:
    """Unregistering twice, or a pool never registered, does nothing."""
    pool = _pool()
    stranger = _pool(_SpellStub("sid-2"), register=False)
    ReleaseManagedSpell().unregister(pool)
    ReleaseManagedSpell().unregister(pool)
    ReleaseManagedSpell().unregister(stranger)
    assert ReleaseManagedSpell().describe(Pooled) == ()


def test_unregister_keeps_the_other_pools_of_the_class() -> None:
    """Two versions of one class: giving one up leaves the other routable."""
    first = _pool(_SpellStub("sid-1"))
    second = _pool(_SpellStub("sid-2"))
    ReleaseManagedSpell().unregister(first)
    assert [entry["spell_id"] for entry in ReleaseManagedSpell().describe(Pooled)] == ["sid-2"]
    ReleaseManagedSpell().release(_out(second, Pooled()))
    assert second.idle_count == 1


# ---------------------------------------------------------------- release and the resolver


def test_release_runs_the_pools_resets_and_pools_the_object() -> None:
    """The fast path is the pool's own put_back: resets in order, then idle."""
    pool = _pool(_SpellStub(resets=("reset",)))
    obj = _out(pool, Pooled("a"))
    ReleaseManagedSpell().release(obj)
    assert Pooled.log == ["reset:a"]
    assert pool.idle_count == 1


def test_release_of_an_unmanaged_class_names_the_remedy() -> None:
    """No pool for the class: bind it as managed, or its root is gone."""
    message = (
        "OtherPooled is not a managed spell class in any live root: bind it with "
        "existence=Existence.managed_spell_quantity, or its root was torn down."
    )
    with pytest.raises(ValueError) as caught:
        ReleaseManagedSpell().release(OtherPooled())
    assert str(caught.value) == message


def test_release_never_routes_a_subclass_to_its_bases_pool() -> None:
    """The key is the exact class object."""
    _pool(_SpellStub(target=Pooled))
    with pytest.raises(ValueError, match="PooledChild is not a managed spell class"):
        ReleaseManagedSpell().release(PooledChild())


def test_release_propagates_a_raising_reset() -> None:
    """The pool destroys the object and the reset's error reaches the caller."""
    pool = _pool(_SpellStub(resets=("reset",)))
    obj = _out(pool, Pooled("bad", fail_reset=True))
    with pytest.raises(ValueError, match="reset failed: bad"):
        ReleaseManagedSpell().release(obj)
    assert (pool.idle_count, pool.count) == (0, 0)
    assert Pooled.log == ["reset:bad", "close:bad"]


def test_release_into_a_pool_torn_down_while_registered_raises_the_pools_error() -> None:
    """A release racing teardown reaches the retired pool, which says the object is the caller's."""
    pool = _pool()
    obj = _out(pool, Pooled())
    pool.cleanup()
    with pytest.raises(RuntimeError, match="was torn down with its root conduit; the object is yours to dispose"):
        ReleaseManagedSpell().release(obj)


def test_release_with_a_matching_spell_id_takes_the_one_pool() -> None:
    """A filter on a one-pool class still releases."""
    pool = _pool()
    ReleaseManagedSpell().release(_out(pool, Pooled()), spell_id="sid-1")
    assert pool.idle_count == 1


def test_release_picks_a_pool_by_spell_id() -> None:
    """Two versions: the spell id says which pool."""
    index = SpellIndex("sid-1")
    first = _pool(_SpellStub("sid-1", index=index))
    second = _pool(_SpellStub("sid-2", index=index, binding_name="other"))
    ReleaseManagedSpell().release(_out(second, Pooled()), spell_id="sid-2")
    assert (first.idle_count, second.idle_count) == (0, 1)


def test_release_with_a_spell_id_no_pool_carries_names_the_pools() -> None:
    """A filter that matches nothing lists what is there."""
    _pool(_SpellStub("sid-1"))
    with pytest.raises(ValueError) as caught:
        ReleaseManagedSpell().release(Pooled(), spell_id="sid-9")
    text = str(caught.value)
    assert text.startswith("No pool of managed class Pooled matches spell_id=sid-9.")
    assert "spell_id=sid-1" in text


def test_release_refuses_a_spell_id_that_is_not_a_string() -> None:
    """The filter must be a spell_id (a str)."""
    _pool()
    with pytest.raises(TypeError, match="spell_id must be a str or None; got int"):
        ReleaseManagedSpell().release(Pooled(), spell_id=7)


def test_release_refuses_a_conduit_that_is_not_a_conduit() -> None:
    """The filter must be a root conduit or one of its lessers."""
    _pool()
    with pytest.raises(TypeError, match="conduit must be a Conduit .* got str"):
        ReleaseManagedSpell().release(Pooled(), conduit="root-1")


def test_release_prefers_the_selected_version_of_an_index() -> None:
    """Two versions of one index, no filter: the release goes to the version its index selects."""
    index = SpellIndex("sid-1")
    first = _pool(_SpellStub("sid-1", index=index))
    second = _pool(_SpellStub("sid-2", index=index))
    index.update("sid-2")
    ReleaseManagedSpell().release(_out(second, Pooled()))
    assert (first.idle_count, second.idle_count) == (0, 1)


def test_a_notch_moves_the_preference() -> None:
    """The preference follows the index's selection."""
    index = SpellIndex("sid-1")
    first = _pool(_SpellStub("sid-1", index=index))
    _pool(_SpellStub("sid-2", index=index))
    index.update("sid-2")
    index.update("sid-1")
    ReleaseManagedSpell().release(_out(first, Pooled()))
    assert first.idle_count == 1


def test_two_selected_versions_are_ambiguous_and_the_error_names_each_pool() -> None:
    """Two binding names, each selected in its own index: the caller must pick."""
    _pool(_SpellStub("sid-1", binding_name="left"), root="root-1")
    _pool(_SpellStub("sid-2", binding_name="right"), root="root-2")
    with pytest.raises(ValueError) as caught:
        ReleaseManagedSpell().release(Pooled())
    text = str(caught.value)
    assert text.startswith("Pooled is managed by 2 pools: ")
    assert "spell_id=sid-1, binding=left, frame=default, root=root-1, active=True" in text
    assert "spell_id=sid-2, binding=right, frame=default, root=root-2, active=True" in text
    assert text.endswith("Pass spell_id=... or conduit=... to pick one.")


def test_no_selected_version_among_several_is_ambiguous() -> None:
    """Versions whose spells were cleaned select nothing; the caller must pick."""
    first, second = _SpellStub("sid-1"), _SpellStub("sid-2")
    _pool(first)
    _pool(second)
    first.cleaned = True
    second.cleaned = True
    with pytest.raises(ValueError, match="Pooled is managed by 2 pools: .*active=False"):
        ReleaseManagedSpell().release(Pooled())


def test_a_default_binding_is_named_default_in_the_error() -> None:
    """A pool of the default binding reads binding=default."""
    _pool(_SpellStub("sid-1", binding_name=None))
    _pool(_SpellStub("sid-2", binding_name="named"))
    with pytest.raises(ValueError, match="spell_id=sid-1, binding=default,"):
        ReleaseManagedSpell().release(Pooled())


# ---------------------------------------------------------------- managed, release_all, describe


def test_managed_returns_a_lease_on_the_resolved_pool() -> None:
    """The lease releases into the pool the registry resolved."""
    pool = _pool()
    obj = _out(pool, Pooled())
    lease = ReleaseManagedSpell().managed(obj)
    assert isinstance(lease, ManagedSpellLease)
    assert lease.object is obj
    lease.release()
    assert pool.idle_count == 1


def test_managed_resolves_with_the_filters() -> None:
    """The same resolver: a spell id picks the pool."""
    index = SpellIndex("sid-1")
    _pool(_SpellStub("sid-1", index=index))
    second = _pool(_SpellStub("sid-2", index=index, binding_name="other"))
    with ReleaseManagedSpell().managed(_out(second, Pooled()), spell_id="sid-2"):
        pass
    assert second.idle_count == 1


def test_managed_refuses_an_unmanaged_class_before_any_lease_exists() -> None:
    """Resolution happens when the lease is made."""
    with pytest.raises(ValueError, match="OtherPooled is not a managed spell class"):
        ReleaseManagedSpell().managed(OtherPooled())


def test_release_all_releases_every_object() -> None:
    """Each object goes back."""
    pool = _pool()
    objects = [_out(pool, Pooled(str(number))) for number in range(3)]
    ReleaseManagedSpell().release_all(objects)
    assert (pool.idle_count, pool.count) == (3, 3)


def test_release_all_releases_the_rest_and_raises_the_failures_together() -> None:
    """A failing object does not stop the others; one group carries every failure."""
    pool = _pool()
    good = _out(pool, Pooled("good"))
    with pytest.raises(ExceptionGroup) as caught:
        ReleaseManagedSpell().release_all([OtherPooled(), good, OtherPooled()])
    assert str(caught.value).startswith("Errors occurred releasing 2 of 3 managed objects")
    assert [type(error) for error in caught.value.exceptions] == [ValueError, ValueError]
    assert pool.idle_count == 1


def test_release_all_of_nothing_does_nothing() -> None:
    """An empty iterable releases nothing and raises nothing."""
    ReleaseManagedSpell().release_all([])


def test_release_all_passes_the_filters_through() -> None:
    """Every object is resolved with the same keywords."""
    index = SpellIndex("sid-1")
    _pool(_SpellStub("sid-1", index=index))
    second = _pool(_SpellStub("sid-2", index=index, binding_name="other"))
    ReleaseManagedSpell().release_all([_out(second, Pooled()), _out(second, Pooled())], spell_id="sid-2")
    assert second.idle_count == 2


def test_describe_answers_one_snapshot_per_pool_with_where_it_lives_and_whether_it_is_selected() -> None:
    """The pool's own snapshot, plus the holding root and the selected-version flag."""
    index = SpellIndex("sid-1")
    _pool(_SpellStub("sid-1", index=index), root="root-1")
    _pool(_SpellStub("sid-2", index=index), root="root-1")
    entries = ReleaseManagedSpell().describe(Pooled)
    assert [(entry["spell_id"], entry["active_version"]) for entry in entries] == [("sid-1", True), ("sid-2", False)]
    assert {entry["holding_conduit_id"] for entry in entries} == {"root-1"}
    assert entries[0]["mode"] == "elastic"
    assert (entries[0]["count"], entries[0]["idle_count"]) == (0, 0)


def test_describe_of_a_class_with_no_pool_is_empty() -> None:
    """No pool is not an error for a read."""
    assert ReleaseManagedSpell().describe(OtherPooled) == ()


def test_describe_refuses_what_is_not_a_class() -> None:
    """The key is a class object."""
    with pytest.raises(TypeError, match="describe takes a class; got Pooled"):
        ReleaseManagedSpell().describe(Pooled())
