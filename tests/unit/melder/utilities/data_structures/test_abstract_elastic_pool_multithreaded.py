import threading
from typing import Any, Callable, Dict, List

import pytest

from melder.utilities.general_base.abstract_elastic_pool import (
    AbstractElasticPool,
)


class _ThreadedElasticPool(AbstractElasticPool[Dict[str, Any]]):
    """Concrete elastic pool used for multithreaded hot-path probes."""

    __slots__ = AbstractElasticPool.__slots__ + [
        "_create_counter",
        "_create_lock",
        "created_ids",
        "destroyed_ids",
    ]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._create_counter: int = 0
        self._create_lock: threading.Lock = threading.Lock()
        self.created_ids: List[int] = []
        self.destroyed_ids: List[int] = []

    def create_object(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        with self._create_lock:
            self._create_counter += 1
            object_id = self._create_counter
            self.created_ids.append(object_id)
        return {"id": object_id}

    def destroy_object(self, obj: Dict[str, Any]) -> None:
        self.destroyed_ids.append(obj["id"])


class _Clock:
    """Simple mutable monotonic clock stub for advisory pool tests."""

    __slots__ = ["value"]

    def __init__(self, value: float = 0.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value


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
            name=f"elastic-pool-worker-{index}",
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
    "seed_count",
    [4, 8],
)
def test_multithreaded_seeded_acquire_pops_each_idle_object_once(
        seed_count: int,
) -> None:
    """Seeded retained objects should not be handed out twice under concurrent pops."""
    clock = _Clock()
    pool = _ThreadedElasticPool(
        baseline_idle=seed_count,
        max_idle=seed_count,
        time_func=clock,
    )
    acquired_ids: List[int] = []
    acquired_ids_lock = threading.Lock()
    for object_id in range(1, seed_count + 1):
        pool._idle.append({"id": object_id})

    def worker(_: int) -> None:
        obj = pool.acquire()
        with acquired_ids_lock:
            acquired_ids.append(obj["id"])

    errors = _run_threaded_workers(seed_count, worker)

    assert not errors
    assert len(acquired_ids) == seed_count
    assert len(set(acquired_ids)) == seed_count
    assert pool.idle_count == 0
    assert pool.created_ids == []


@pytest.mark.parametrize(
    ("worker_count", "iterations"),
    [(4, 40), (8, 40)],
)
def test_multithreaded_acquire_release_cycles_leave_pool_bounded(
        worker_count: int,
        iterations: int,
) -> None:
    """Concurrent acquire/release cycles should leave idle retention bounded."""
    clock = _Clock()
    pool = _ThreadedElasticPool(
        baseline_idle=4,
        max_idle=4,
        time_func=clock,
    )

    def worker(_: int) -> None:
        for _ in range(iterations):
            obj = pool.acquire()
            pool.release(obj)

    errors = _run_threaded_workers(worker_count, worker)

    assert not errors
    assert pool.idle_count <= pool.target_idle
    assert pool.target_idle == 4
    assert len(pool.created_ids) >= 1


@pytest.mark.parametrize(
    ("release_count", "max_idle"),
    [(8, 1), (16, 4)],
)
def test_multithreaded_concurrent_releases_account_for_every_acquired_object(
        release_count: int,
        max_idle: int,
) -> None:
    """Concurrent releases should account for every acquired object exactly once."""
    clock = _Clock()
    pool = _ThreadedElasticPool(
        baseline_idle=max_idle,
        max_idle=max_idle,
        time_func=clock,
    )
    acquired = [pool.acquire() for _ in range(release_count)]

    def worker(index: int) -> None:
        pool.release(acquired[index])

    errors = _run_threaded_workers(release_count, worker)

    assert not errors
    assert pool.idle_count <= pool.target_idle
    assert len(pool.destroyed_ids) + pool.idle_count == release_count


@pytest.mark.parametrize("worker_count", [4, 8])
def test_multithreaded_overflow_decay_stays_within_bounds(worker_count: int) -> None:
    """Concurrent overflow trims should keep advisory target idle within bounds."""
    clock = _Clock(value=100.0)
    pool = _ThreadedElasticPool(
        baseline_idle=2,
        stretch_percent=50,
        settle_time_seconds=10.0,
        decay_percent_per_interval=25,
        decay_interval_seconds=5.0,
        max_idle=10,
        time_func=clock,
    )
    pool._target_idle = 6
    pool._decay_step = 1
    pool._last_expand_at = 0.0
    pool._last_decay_at = 0.0
    for item_id in range(100, 106):
        pool._idle.append({"id": item_id})

    def worker(index: int) -> None:
        pool.release({"id": 1000 + index})

    errors = _run_threaded_workers(worker_count, worker)

    assert not errors
    assert pool.baseline_idle <= pool.target_idle <= 6
    assert pool.idle_count == 6


@pytest.mark.parametrize(
    ("worker_count", "iterations"),
    [(4, 20), (8, 20)],
)
def test_multithreaded_cleanup_after_hammer_destroys_retained_idle_once(
        worker_count: int,
        iterations: int,
) -> None:
    """Post-hammer cleanup should destroy exactly the retained idle shells."""
    clock = _Clock()
    pool = _ThreadedElasticPool(
        baseline_idle=4,
        max_idle=4,
        time_func=clock,
    )

    def worker(_: int) -> None:
        for _ in range(iterations):
            obj = pool.acquire()
            pool.release(obj)

    errors = _run_threaded_workers(worker_count, worker)

    assert not errors
    idle_before_cleanup = pool.idle_count
    destroyed_before_cleanup = len(pool.destroyed_ids)

    pool.cleanup()

    assert pool.cleaned is True
    assert len(pool.destroyed_ids) == destroyed_before_cleanup + idle_before_cleanup
