"""
Concurrency tests of ReleaseManagedSpell (STORY-2026-10-15-release_managed_spell, S4).

Scope:
    Lock-free releases against the copy-on-write publication: many threads releasing into one pool lose nothing,
    releases keep routing while other pools of other classes register and unregister, and concurrent registrations
    and unregistrations of one class neither lose nor duplicate a pool. Runs under `-X gil=0` and `-X gil=1`.
"""
import threading
from collections.abc import Iterator
from typing import Callable, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spellbook import Spellbook


class Hot:
    """The class released under load."""


class Churn:
    """The class whose pools come and go meanwhile."""


class _SpellStub:
    """The Spell fields a pool reads, elastic with a large idle cap."""

    def __init__(self, spell_id: str, target: type) -> None:
        """
        Keep the identity and the class.

        Args:
            spell_id: The version id.
            target: The managed class.
        """
        self.spell_id = spell_id
        self.spell = target
        self.spell_name = target.__name__
        self.binding_name = spell_id
        self.aetheric_frame = "default"
        self.existence = Existence.managed_spell_quantity
        self.disposal_method_names: List[str] = []
        self.managed_spell_mode = ManagedSpellMode.elastic
        self.managed_spell_limit = 100_000
        self.managed_spell_timeout_seconds = None
        self.managed_spell_reset_methods = ()
        self.spell_index = SpellIndex(spell_id)

    def _spell_index_unless_cleaned(self) -> Optional[SpellIndex]:
        """Return the index."""
        return self.spell_index


def _reset_world() -> None:
    """Install a fresh Aether and registry."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_registry() -> Iterator[None]:
    """A fresh registry per test."""
    _reset_world()
    yield
    _reset_world()


def _pool(spell_id: str, target: type) -> ManagedSpellQuantity:
    """
    Build and register one pool.

    Args:
        spell_id: The version id.
        target: The managed class.

    Returns:
        ManagedSpellQuantity: The registered pool.
    """
    pool = ManagedSpellQuantity(spell=_SpellStub(spell_id, target), owner_conduit_id="root-1")
    ReleaseManagedSpell().register(pool, root_conduit_id="root-1")
    return pool


def _run_together(workers: List[Callable[[], None]]) -> List[BaseException]:
    """
    Start the workers behind one barrier and collect what they raised.

    Args:
        workers: One callable per thread.

    Returns:
        List[BaseException]: Every error a worker raised.
    """
    barrier = threading.Barrier(len(workers))
    errors: List[BaseException] = []
    errors_lock = threading.Lock()

    def _run(worker: Callable[[], None]) -> None:
        barrier.wait()
        try:
            worker()
        except BaseException as error:
            with errors_lock:
                errors.append(error)

    threads = [threading.Thread(target=_run, args=(worker,)) for worker in workers]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert not any(thread.is_alive() for thread in threads)
    return errors


def test_eight_threads_releasing_into_one_pool_lose_nothing() -> None:
    """Every released object is idle afterwards."""
    pool = _pool("hot", Hot)
    per_thread = 500
    objects = []
    for _ in range(8 * per_thread):
        assert pool.reserve() is None
        objects.append(Hot())
    chunks = [objects[start:start + per_thread] for start in range(0, len(objects), per_thread)]

    def _releaser(chunk: List[Hot]) -> Callable[[], None]:
        def _release_all() -> None:
            registry = ReleaseManagedSpell()
            for obj in chunk:
                registry.release(obj)
        return _release_all

    assert _run_together([_releaser(chunk) for chunk in chunks]) == []
    assert (pool.idle_count, pool.count) == (len(objects), len(objects))


def test_releases_keep_routing_while_another_class_churns_registrations() -> None:
    """Republishing the maps for one class never hides another class's pool from a release."""
    hot = _pool("hot", Hot)
    churn_pools = [
        ManagedSpellQuantity(spell=_SpellStub(f"churn-{number}", Churn), owner_conduit_id="root-1")
        for number in range(8)
    ]
    releases = 2_000
    objects = []
    for _ in range(4 * releases):
        assert hot.reserve() is None
        objects.append(Hot())
    chunks = [objects[start:start + releases] for start in range(0, len(objects), releases)]

    def _releaser(chunk: List[Hot]) -> Callable[[], None]:
        def _release_all() -> None:
            registry = ReleaseManagedSpell()
            for obj in chunk:
                registry.release(obj)
        return _release_all

    def _churner(pool: ManagedSpellQuantity) -> Callable[[], None]:
        def _churn() -> None:
            registry = ReleaseManagedSpell()
            for _ in range(300):
                registry.register(pool, root_conduit_id="root-1")
                registry.unregister(pool)
        return _churn

    workers = [_releaser(chunk) for chunk in chunks] + [_churner(pool) for pool in churn_pools[:4]]
    assert _run_together(workers) == []
    assert hot.idle_count == len(objects)
    assert ReleaseManagedSpell().describe(Churn) == ()


def test_concurrent_registrations_of_one_class_are_all_kept() -> None:
    """No registration is lost when eight threads publish at once."""
    pools = [
        ManagedSpellQuantity(spell=_SpellStub(f"churn-{number}", Churn), owner_conduit_id="root-1")
        for number in range(32)
    ]

    def _registrar(group: List[ManagedSpellQuantity]) -> Callable[[], None]:
        def _register() -> None:
            for pool in group:
                ReleaseManagedSpell().register(pool, root_conduit_id="root-1")
        return _register

    groups = [pools[start:start + 4] for start in range(0, len(pools), 4)]
    assert _run_together([_registrar(group) for group in groups]) == []
    assert sorted(entry["spell_id"] for entry in ReleaseManagedSpell().describe(Churn)) == sorted(
        f"churn-{number}" for number in range(32)
    )


def test_concurrent_unregistrations_leave_nothing_behind() -> None:
    """Every pool removed by eight threads at once is gone, and nothing else."""
    hot = _pool("hot", Hot)
    pools = [_pool(f"churn-{number}", Churn) for number in range(32)]

    def _unregistrar(group: List[ManagedSpellQuantity]) -> Callable[[], None]:
        def _unregister() -> None:
            for pool in group:
                ReleaseManagedSpell().unregister(pool)
                ReleaseManagedSpell().unregister(pool)
        return _unregister

    groups = [pools[start:start + 4] for start in range(0, len(pools), 4)]
    assert _run_together([_unregistrar(group) for group in groups]) == []
    assert ReleaseManagedSpell().describe(Churn) == ()
    assert [entry["spell_id"] for entry in ReleaseManagedSpell().describe(Hot)] == ["hot"]


def test_register_racing_the_registrys_cleanup_either_lands_or_raises_the_cleaned_error() -> None:
    """A registration that loses the race to teardown raises plainly; nothing hangs."""
    pools = [
        ManagedSpellQuantity(spell=_SpellStub(f"churn-{number}", Churn), owner_conduit_id="root-1")
        for number in range(64)
    ]
    registry = ReleaseManagedSpell()

    def _registrar() -> None:
        for pool in pools:
            try:
                registry.register(pool, root_conduit_id="root-1")
            except RuntimeError as error:
                assert "has already been cleaned" in str(error)

    def _cleaner() -> None:
        registry.cleanup()

    assert _run_together([_registrar, _registrar, _cleaner]) == []
    assert registry.cleaned is True
