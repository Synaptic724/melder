import itertools
import sys
import threading


_THREADS: int = 12
_INCREMENTS_PER_THREAD: int = 4000
_EXPECTED_TOTAL: int = _THREADS * _INCREMENTS_PER_THREAD
_RACE_ROUNDS: int = 200


def _print_metric(name: str, value: int, expected: int, details: str) -> None:
    """
    Print compact experiment telemetry for visibility under pytest -s.

    Args:
        name: Label for the measured quantity.
        value: Observed value.
        expected: Expected baseline value.
        details: Additional context about the measurement.
    """
    delta = expected - value
    status = "OK" if delta == 0 else "DEGRADED"
    print(
        "  {0}: value={1} expected={2} delta={3} status={4} :: {5}".format(
            name,
            value,
            expected,
            delta,
            status,
            details,
        )
    )


def _gil_runtime_mode() -> str:
    """
    Report interpreter GIL mode when metadata is available.

    Returns:
        "gil", "no-gil", or "unknown".
    """
    is_enabled = getattr(sys, "_is_gil_enabled", None)
    if callable(is_enabled):
        return "no-gil" if not is_enabled() else "gil"
    return "unknown"


def _run_threaded(task) -> None:
    """
    Run `task` from `_THREADS` worker threads and wait for completion.

    Args:
        task: Callable executed by each worker thread.
    """
    threads = []
    for _ in range(_THREADS):
        thread = threading.Thread(target=task)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def test_itertools_count_next_is_atomic_enough_for_hot_id_allocation() -> None:
    """
    Verify `next(itertools.count())` behaves as a unique hot-ID source.

    This is the hot-path behavior we care about in no-GIL/free-threaded runs:
    cheap monotonic token allocation without a shared Python-level lock.

    Contract:
        - Each call to `next(counter)` returns a distinct integer.
        - Parallel workers never observe duplicate values.
        - Exactly `_THREADS * _INCREMENTS_PER_THREAD` unique IDs are produced.
    """
    gil_mode = _gil_runtime_mode()
    assert gil_mode in {"gil", "no-gil", "unknown"}
    print(
        "[atomic-counter-experiment] test=itertools_count_unique "
        "runtime={0} threads={1} per_thread={2} expected={3}".format(
            gil_mode,
            _THREADS,
            _INCREMENTS_PER_THREAD,
            _EXPECTED_TOTAL,
        )
    )

    counter = itertools.count()
    values = []
    lock = threading.Lock()

    def worker() -> None:
        local = []
        for _ in range(_INCREMENTS_PER_THREAD):
            local.append(next(counter))
        with lock:
            values.extend(local)

    _run_threaded(worker)

    unique_count = len(set(values))
    observed_min = min(values)
    observed_max = max(values)
    observed_first_ten = values[:10]
    _print_metric(
        "unique_ids",
        unique_count,
        _EXPECTED_TOTAL,
        "range=({0}, {1}) first10={2}".format(
            observed_min,
            observed_max,
            observed_first_ten,
        ),
    )
    print("  rationale: next(counter) should hand out strictly unique IDs with no duplicates")

    assert len(values) == _EXPECTED_TOTAL
    assert unique_count == _EXPECTED_TOTAL
    assert observed_min == 0
    assert observed_max == _EXPECTED_TOTAL - 1


def test_split_python_counter_update_can_lose_updates_without_lock() -> None:
    """
    Demonstrate a split read/modify/write can drop updates under concurrency.

    The barrier forces all threads to read the same value for each round, then all
    write the same incremented value. The final total must be far below the
    expected atomic total.
    """
    state = {"count": 0}
    start_phase = threading.Barrier(_THREADS)
    write_phase = threading.Barrier(_THREADS)

    def worker() -> None:
        for _ in range(_RACE_ROUNDS):
            start_phase.wait()
            value = state["count"]
            write_phase.wait()
            state["count"] = value + 1

    print(
        "[atomic-counter-experiment] test=split_update_race "
        "scenario=barrier_forced_conflict threads={0} rounds={1}".format(
            _THREADS,
            _RACE_ROUNDS,
        )
    )

    _run_threaded(worker)
    observed = state["count"]
    expected_atomic = _RACE_ROUNDS * _THREADS
    _print_metric(
        "race_count_after_rounds",
        observed,
        expected_atomic,
        "barrier forces same-read same-write in each round",
    )
    print(
        "  rationale: if this were an atomic increment, result must be "
        "{0}, but split read/write collapses concurrent writes".format(
            expected_atomic
        )
    )

    assert 0 < observed <= _RACE_ROUNDS
    assert observed != expected_atomic


def test_locking_or_counter_primitive_restores_correct_totals() -> None:
    """
    Confirm two safe hot-path alternatives:
        - protect the split operation with a lock, or
        - use `itertools.count().__next__` directly.

    Contract:
        - lock-protected split increments reach the expected exact total
        - count-based increments also reach the expected exact total
    """
    locked_state = {"count": 0}
    lock = threading.Lock()

    def lock_worker() -> None:
        for _ in range(_INCREMENTS_PER_THREAD):
            with lock:
                locked_state["count"] += 1

    _run_threaded(lock_worker)
    print(
        "[atomic-counter-experiment] test=lock_vs_counter_safe path "
        "threads={0} per_thread={1}".format(_THREADS, _INCREMENTS_PER_THREAD)
    )
    _print_metric(
        "locked_counter_total",
        locked_state["count"],
        _EXPECTED_TOTAL,
        "control: lock-protected read-modify-write",
    )
    assert locked_state["count"] == _EXPECTED_TOTAL

    counter = itertools.count()
    values = []
    values_lock = threading.Lock()

    def count_worker() -> None:
        local = []
        for _ in range(_INCREMENTS_PER_THREAD):
            local.append(next(counter))
        with values_lock:
            values.extend(local)

    _run_threaded(count_worker)
    count_unique = len(set(values))
    _print_metric(
        "next_counter_unique",
        count_unique,
        _EXPECTED_TOTAL,
        "control: native C-level next(counter) path",
    )
    print(
        "  sample_ids_last=..."
        "{0}".format(values[-10:] if values else [])
    )
    assert len(values) == _EXPECTED_TOTAL
    assert count_unique == _EXPECTED_TOTAL
