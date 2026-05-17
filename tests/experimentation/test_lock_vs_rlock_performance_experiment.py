import threading
import time
from dataclasses import dataclass
from typing import Callable, List, Type


ITERATIONS: int = 1_000_000
THREAD_COUNTS: tuple[int, ...] = (5, 10, 15, 20)
WINDOW_SECONDS: float = 5.0


@dataclass(frozen=True)
class _SpeedMeasurement:
    """
    Immutable plain lock/unlock speed result.

    Purpose:
        Hold the output of one single-thread lock benchmark in a compact,
        print-friendly form.

    Contract:
        - `iterations` is the exact number of acquire/release pairs executed.
        - `elapsed_seconds` is wall-clock duration for the measured loop only.
        - `ns_per_acquisition` is derived directly from those two fields.
    """

    label: str
    iterations: int
    elapsed_seconds: float

    @property
    def ns_per_acquisition(self) -> float:
        """
        Return the nanoseconds spent per acquire/release pair.
        """
        return (self.elapsed_seconds * 1_000_000_000.0) / float(self.iterations)


@dataclass(frozen=True)
class _ThroughputMeasurement:
    """
    Immutable shared-lock throughput result for one thread count.

    Purpose:
        Hold the total completed acquire/release count across all worker
        threads for one fixed time window.

    Contract:
        - `acquisitions` counts only completed acquire/release pairs.
        - `window_seconds` is the requested benchmark window, not total process
          lifetime.
        - `acq_per_second` is derived directly from those two fields.
    """

    label: str
    threads: int
    acquisitions: int
    window_seconds: float

    @property
    def acq_per_second(self) -> float:
        """
        Return the completed acquire/release throughput for this run.
        """
        return float(self.acquisitions) / self.window_seconds


def _measure_plain_lock_speed(lock_factory: Callable[[], threading.Lock], label: str) -> _SpeedMeasurement:
    """
    Measure plain single-thread lock/unlock speed.

    Args:
        lock_factory:
            Callable returning a fresh lock instance.
        label:
            Human-readable label for the lock type under test.

    Returns:
        _SpeedMeasurement:
            Completed measurement payload for one million acquire/release pairs.
    """
    lock = lock_factory()
    start = time.perf_counter_ns()
    for _ in range(ITERATIONS):
        lock.acquire()
        lock.release()
    elapsed_ns = time.perf_counter_ns() - start
    return _SpeedMeasurement(
        label=label,
        iterations=ITERATIONS,
        elapsed_seconds=elapsed_ns / 1_000_000_000.0,
    )


def _measure_contended_throughput(
    lock_factory: Callable[[], threading.Lock],
    label: str,
    threads: int,
) -> _ThroughputMeasurement:
    """
    Measure shared-lock throughput under fixed-window contention.

    Args:
        lock_factory:
            Callable returning a fresh shared lock instance.
        label:
            Human-readable label for the lock type under test.
        threads:
            Number of worker threads that contend on the shared lock.

    Returns:
        _ThroughputMeasurement:
            Total completed acquire/release throughput for the fixed window.
    """
    lock = lock_factory()
    barrier = threading.Barrier(threads + 1)
    stop = threading.Event()
    counts: List[int] = [0] * threads
    workers: List[threading.Thread] = []

    def worker(index: int) -> None:
        local_count = 0
        barrier.wait()
        while not stop.is_set():
            lock.acquire()
            lock.release()
            local_count += 1
        counts[index] = local_count

    for index in range(threads):
        thread = threading.Thread(target=worker, args=(index,))
        thread.start()
        workers.append(thread)

    barrier.wait()
    time.sleep(WINDOW_SECONDS)
    stop.set()

    for worker_thread in workers:
        worker_thread.join()

    return _ThroughputMeasurement(
        label=label,
        threads=threads,
        acquisitions=sum(counts),
        window_seconds=WINDOW_SECONDS,
    )


def _print_speed_results(results: List[_SpeedMeasurement]) -> None:
    """
    Print the plain single-thread speed section.
    """
    print("section 1: plain single-thread lock/unlock speed")
    print(f"{'lock':<24} {'iterations':>14} {'elapsed(ms)':>14} {'ns/acq':>14}")
    print("-" * 72)
    for result in results:
        print(
            f"{result.label:<24} "
            f"{result.iterations:>14} "
            f"{result.elapsed_seconds * 1000.0:>14.3f} "
            f"{result.ns_per_acquisition:>14.2f}"
        )


def _print_throughput_results(results: List[_ThroughputMeasurement]) -> None:
    """
    Print the shared-lock throughput section.
    """
    print("section 2: shared-lock throughput and contention at depth 1")
    print(
        f"{'lock':<24} {'threads':>8} {'window(s)':>12} "
        f"{'acquisitions':>16} {'acq/sec':>18}"
    )
    print("-" * 88)
    for result in results:
        print(
            f"{result.label:<24} "
            f"{result.threads:>8} "
            f"{result.window_seconds:>12.1f} "
            f"{result.acquisitions:>16} "
            f"{result.acq_per_second:>18.2f}"
        )


def test_lock_vs_rlock_performance_experiment() -> None:
    """
    Print one fair Python lock benchmark pass for Lock versus RLock.

    Contract:
        - Uses the same fair shape as the final Rust benchmark slice:
          one million plain acquire/release pairs plus fixed-window shared-lock
          throughput at `5`, `10`, `15`, and `20` threads.
        - Does not assert on timing values because this is an experiment, not a
          correctness contract test.
        - Exists to make the no-GIL Python lock cost visible inside the Melder
          repo under pytest.
    """
    print("melder python lock experiment")
    print("plain lock/unlock only; no nested same-thread reentry in this run")
    print(f"single-thread speed iterations: {ITERATIONS}")
    print(f"shared-lock throughput window per thread-count run: {WINDOW_SECONDS:.1f}s")
    print()

    speed_results = [
        _measure_plain_lock_speed(threading.Lock, "threading.Lock"),
        _measure_plain_lock_speed(threading.RLock, "threading.RLock"),
    ]

    throughput_results: List[_ThroughputMeasurement] = []
    for threads in THREAD_COUNTS:
        throughput_results.append(
            _measure_contended_throughput(threading.Lock, "threading.Lock", threads)
        )
        throughput_results.append(
            _measure_contended_throughput(threading.RLock, "threading.RLock", threads)
        )

    _print_speed_results(speed_results)
    print()
    _print_throughput_results(throughput_results)
