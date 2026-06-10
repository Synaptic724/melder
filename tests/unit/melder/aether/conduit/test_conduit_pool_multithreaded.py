import threading
from typing import Callable, List, Optional

import pytest

from melder.aether.conduit.conduit_pool import ConduitPool


class _RootConduitStub:
    """Minimal root-conduit stub for conduit pool multithreaded tests."""

    def __init__(self, conduit_id: str) -> None:
        self._id = conduit_id


class _PooledConduitStub:
    """Simple lesser-conduit shell with thread-safe cleanup counting."""

    __slots__ = ["cleanup_calls", "conduit_id", "_lock"]

    def __init__(self, conduit_id: str) -> None:
        self.cleanup_calls = 0
        self.conduit_id = conduit_id
        self._lock = threading.Lock()

    def permanent_cleanup(self) -> None:
        with self._lock:
            self.cleanup_calls += 1


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
            name=f"conduit-pool-worker-{index}",
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
    ("return_count", "max_idle"),
    [(8, 1), (16, 4)],
)
def test_multithreaded_return_lesser_conduit_keeps_pool_bounded(
        return_count: int,
        max_idle: int,
) -> None:
    """Concurrent lesser returns should leave each shell retained or destroyed once."""
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=max_idle,
        max_idle=max_idle,
    )
    returned = [
        _PooledConduitStub(f"lesser-{index}")
        for index in range(return_count)
    ]

    def worker(index: int) -> None:
        pool.return_lesser_conduit(returned[index])

    errors = _run_threaded_workers(return_count, worker)

    assert not errors
    destroyed_count = sum(conduit.cleanup_calls for conduit in returned)
    assert destroyed_count + pool.idle_count == return_count
    assert pool.idle_count <= pool.target_idle


@pytest.mark.parametrize("seed_count", [4, 8])
def test_multithreaded_create_object_pops_each_seeded_shell_once(seed_count: int) -> None:
    """Concurrent create_object calls should not hand out the same retained shell twice."""
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=seed_count,
        max_idle=seed_count,
    )
    seeded = [
        _PooledConduitStub(f"seed-{index}")
        for index in range(seed_count)
    ]
    for conduit in seeded:
        pool.return_lesser_conduit(conduit)

    acquired_ids: List[str] = []
    acquired_ids_lock = threading.Lock()

    def worker(_: int) -> None:
        conduit = pool.create_object()
        assert conduit is not None
        with acquired_ids_lock:
            acquired_ids.append(conduit.conduit_id)

    errors = _run_threaded_workers(seed_count, worker)

    assert not errors
    assert len(acquired_ids) == seed_count
    assert len(set(acquired_ids)) == seed_count
    assert pool.idle_count == 0


@pytest.mark.parametrize(
    ("worker_count", "iterations"),
    [(4, 20), (8, 20)],
)
def test_multithreaded_conduit_pop_return_cycles_do_not_raise(
        worker_count: int,
        iterations: int,
) -> None:
    """Concurrent pop/return cycles should stay bounded and exception-free."""
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=4,
        max_idle=4,
    )

    def worker(index: int) -> None:
        for iteration in range(iterations):
            conduit = pool.create_object()
            if conduit is None:
                conduit = _PooledConduitStub(f"new-{index}-{iteration}")
            pool.return_lesser_conduit(conduit)

    errors = _run_threaded_workers(worker_count, worker)

    assert not errors
    assert pool.idle_count <= pool.target_idle


@pytest.mark.parametrize("overflow_count", [4, 8])
def test_multithreaded_fixed_capacity_overflow_never_touches_clock(
        overflow_count: int,
) -> None:
    """Fixed-capacity concurrent overflow should never consult the decay clock."""
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=1,
        max_idle=1,
    )
    retained = _PooledConduitStub("retained")
    overflow = [
        _PooledConduitStub(f"overflow-{index}")
        for index in range(overflow_count)
    ]
    pool.return_lesser_conduit(retained)

    def exploding_clock() -> float:
        raise AssertionError("Fixed-capacity full path should not touch the decay clock.")

    pool._time_func = exploding_clock

    def worker(index: int) -> None:
        pool.return_lesser_conduit(overflow[index])

    errors = _run_threaded_workers(overflow_count, worker)

    assert not errors
    total_cleanup_calls = retained.cleanup_calls + sum(
        conduit.cleanup_calls for conduit in overflow
    )
    assert pool.idle_count == 1
    assert total_cleanup_calls == overflow_count


@pytest.mark.parametrize(
    ("worker_count", "iterations"),
    [(4, 20), (8, 20)],
)
def test_multithreaded_conduit_pool_cleanup_after_hammer_cleans_retained_idle(
        worker_count: int,
        iterations: int,
) -> None:
    """Pool cleanup after concurrent lesser churn should clean retained idle shells."""
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=4,
        max_idle=4,
    )

    def worker(index: int) -> None:
        for iteration in range(iterations):
            conduit = pool.create_object()
            if conduit is None:
                conduit = _PooledConduitStub(f"new-{index}-{iteration}")
            pool.return_lesser_conduit(conduit)

    errors = _run_threaded_workers(worker_count, worker)

    assert not errors
    retained = list(pool._idle)
    cleanup_before = sum(conduit.cleanup_calls for conduit in retained)

    pool.cleanup()

    cleanup_after = sum(conduit.cleanup_calls for conduit in retained)
    assert pool.cleaned is True
    assert cleanup_after == cleanup_before + len(retained)


@pytest.mark.parametrize("seed_count", [4, 8])
def test_multithreaded_conduit_seeded_pop_return_roundtrip_keeps_unique_shells(
        seed_count: int,
) -> None:
    """Seeded lesser shells should stay unique across one concurrent pop wave."""
    root = _RootConduitStub("root-1")
    pool = ConduitPool(
        root_conduit=root,
        baseline_idle=seed_count,
        max_idle=seed_count,
    )
    seeded = [
        _PooledConduitStub(f"seed-roundtrip-{index}")
        for index in range(seed_count)
    ]
    for conduit in seeded:
        pool.return_lesser_conduit(conduit)

    acquired_ids: List[str] = []
    acquired_ids_lock = threading.Lock()
    release_barrier = threading.Barrier(seed_count)

    def worker(_: int) -> None:
        conduit = pool.create_object()
        assert conduit is not None
        with acquired_ids_lock:
            acquired_ids.append(conduit.conduit_id)
        release_barrier.wait()
        pool.return_lesser_conduit(conduit)

    errors = _run_threaded_workers(seed_count, worker)

    assert not errors
    assert len(acquired_ids) == seed_count
    assert len(set(acquired_ids)) == seed_count
    assert pool.idle_count == seed_count
