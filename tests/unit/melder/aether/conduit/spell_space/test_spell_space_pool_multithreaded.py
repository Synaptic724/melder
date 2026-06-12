import threading
from types import SimpleNamespace
from typing import Any, Callable, List, Optional, Union

import pytest

from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.conduit.spell_space.spell_space_pool import SpellSpacePool
from melder.aether.conduit.spell_space.spell_space_thread_state import (
    SpellSpaceThreadState,
)


class _ConduitCreationsStub:
    """Minimal conduit-owned creations stub for spellspace pool probes."""

    def __init__(self, *, owner_conduit_id: str) -> None:
        self._owner_conduit_id = owner_conduit_id
        self._creations: dict[str, Any] = {}

    @property
    def owner_conduit_id(self) -> str:
        return self._owner_conduit_id


class _ConduitMeldStub:
    """Minimal conduit-facing meld stub for spellspace pool probes."""

    def __init__(self, *, meld_result: Any = None) -> None:
        self._meld_result = meld_result
        self._spellbook = SimpleNamespace(
            _spells={},
            _contracted_spells={},
            _spells_by_id={},
            _contracted_spells_by_id={},
            _spell_id_pool={},
            _lookup_spells={},
            _lookup_contracted_spells={},
        )
        self._conduit_id = "conduit-test"
        self._resolution_conduit_id = "conduit-test"
        self._dynamic_environment = False
        self._meld_hooks: dict[str, list[Any]] = {}

    def meld(
            self,
            spell_name: Optional[str] = None,
            *,
            spell: Optional[Union[str, object]] = None,
            spellframe: Optional[Union[str, object]] = None,
            binding_name: Optional[str] = None,
            spell_override: Optional[Union[dict, list, tuple]] = None,
    ) -> Any:
        return self._meld_result


def _build_pool(*, baseline_idle: int, max_idle: int) -> tuple[SpellSpacePool, set[SpellSpace]]:
    """Create one concrete spellspace pool plus its backing registry."""
    owner_conduit_id = "conduit-test"
    creations = _ConduitCreationsStub(owner_conduit_id=owner_conduit_id)
    conduit_meld = _ConduitMeldStub()
    registry: set[SpellSpace] = set()
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld,
        owner_conduit_creations=creations,
        spellspace_registry=registry,
        spellspace_stack_state=SpellSpaceThreadState(),
        baseline_idle=baseline_idle,
        max_idle=max_idle,
    )
    return pool, registry


def _run_threaded_workers(
        worker_count: int,
        worker: Callable[[int], None],
        *,
        timeout_seconds: float = 5.0,
) -> List[BaseException]:
    """Run one worker body across many threads and collect failures."""
    barrier = threading.Barrier(worker_count)
    errors: List[BaseException] = []
    error_lock = threading.Lock()
    threads: List[threading.Thread] = []

    def wrapped(index: int) -> None:
        try:
            barrier.wait()
            worker(index)
        except BaseException as exc:
            with error_lock:
                errors.append(exc)

    for index in range(worker_count):
        thread = threading.Thread(
            target=wrapped,
            args=(index,),
            daemon=True,
            name=f"spellspace-pool-worker-{index}",
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join(timeout=timeout_seconds)

    alive_threads = [thread.name for thread in threads if thread.is_alive()]
    if alive_threads:
        errors.append(
            AssertionError(
                f"Threads did not finish: {alive_threads}",
            )
        )
    return errors


@pytest.mark.parametrize(
    ("worker_count", "iterations"),
    [(4, 20), (8, 20)],
)
def test_multithreaded_managed_spellspace_cycles_leave_registry_empty(
        worker_count: int,
        iterations: int,
) -> None:
    """Managed spellspace cycles should not leak registry membership."""
    pool, registry = _build_pool(baseline_idle=4, max_idle=4)

    def worker(_: int) -> None:
        for _ in range(iterations):
            space = pool.acquire_untracked()
            space.recycle_from_managed_context()

    errors = _run_threaded_workers(worker_count, worker)

    assert not errors
    assert registry == set()
    assert pool.idle_count <= pool.target_idle


@pytest.mark.parametrize(
    ("worker_count", "iterations"),
    [(4, 20), (8, 20)],
)
def test_multithreaded_manual_spellspace_cycles_leave_registry_empty(
        worker_count: int,
        iterations: int,
) -> None:
    """Manual spellspace cycles should register on acquire and clear on cleanup."""
    pool, registry = _build_pool(baseline_idle=4, max_idle=4)

    def worker(_: int) -> None:
        for _ in range(iterations):
            space = pool.acquire(track_registry=True)
            space.cleanup()

    errors = _run_threaded_workers(worker_count, worker)

    assert not errors
    assert registry == set()
    assert pool.idle_count <= pool.target_idle


@pytest.mark.parametrize(
    ("worker_count", "iterations"),
    [(4, 20), (8, 20)],
)
def test_multithreaded_mixed_spellspace_cycles_leave_registry_empty(
        worker_count: int,
        iterations: int,
) -> None:
    """Mixed managed/manual spellspace cycles should still leave no registry drift."""
    pool, registry = _build_pool(baseline_idle=4, max_idle=4)

    def worker(index: int) -> None:
        for iteration in range(iterations):
            if (index + iteration) % 2 == 0:
                space = pool.acquire_untracked()
                space.recycle_from_managed_context()
            else:
                space = pool.acquire(track_registry=True)
                space.cleanup()

    errors = _run_threaded_workers(worker_count, worker)

    assert not errors
    assert registry == set()
    assert pool.idle_count <= pool.target_idle


@pytest.mark.parametrize(
    ("release_count", "max_idle"),
    [(8, 1), (16, 2)],
)
def test_multithreaded_spellspace_overflow_accounts_for_every_shell(
        release_count: int,
        max_idle: int,
) -> None:
    """Overflow pressure should leave each spellspace either retained or cleaned."""
    pool, registry = _build_pool(baseline_idle=max_idle, max_idle=max_idle)
    acquired = [pool.acquire_untracked() for _ in range(release_count)]

    def worker(index: int) -> None:
        acquired[index].recycle_from_managed_context()

    errors = _run_threaded_workers(release_count, worker)

    assert not errors
    assert registry == set()
    cleaned_count = sum(space.cleaned for space in acquired)
    assert cleaned_count + pool.idle_count == release_count
    assert pool.idle_count <= pool.target_idle


@pytest.mark.parametrize("seed_count", [4, 8])
def test_multithreaded_spellspace_seeded_acquire_untracked_pops_unique_shells(
        seed_count: int,
) -> None:
    """Seeded managed spellspaces should not be handed out twice under concurrent pops."""
    pool, registry = _build_pool(baseline_idle=seed_count, max_idle=seed_count)
    seeded = [pool.acquire_untracked() for _ in range(seed_count)]
    for space in seeded:
        space.recycle_from_managed_context()

    acquired_ids: List[str] = []
    acquired_ids_lock = threading.Lock()

    def worker(_: int) -> None:
        space = pool.acquire_untracked()
        with acquired_ids_lock:
            acquired_ids.append(space.id)

    errors = _run_threaded_workers(seed_count, worker)

    assert not errors
    assert registry == set()
    assert len(acquired_ids) == seed_count
    assert len(set(acquired_ids)) == seed_count
    assert pool.idle_count == 0


@pytest.mark.parametrize(
    ("worker_count", "iterations"),
    [(4, 20), (8, 20)],
)
def test_multithreaded_spellspace_pool_cleanup_after_hammer_cleans_retained_idle(
        worker_count: int,
        iterations: int,
) -> None:
    """Pool cleanup after concurrent managed cycles should clean retained idle shells."""
    pool, registry = _build_pool(baseline_idle=4, max_idle=4)

    def worker(_: int) -> None:
        for _ in range(iterations):
            space = pool.acquire_untracked()
            space.recycle_from_managed_context()

    errors = _run_threaded_workers(worker_count, worker)

    assert not errors
    retained = list(pool._idle)
    assert registry == set()

    pool.cleanup()

    assert pool.cleaned is True
    assert registry == set()
    assert all(space.cleaned for space in retained)
