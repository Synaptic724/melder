"""
Bare-CPython mechanism probe for the gauntlet order effect (melder_0, 2026-09-30).

Purpose:
    Check, with no DI library imported, whether short-lived thread churn alone leaves
    a free-threaded process slower at starting and joining threads, and which kind
    of work inside those threads does it.

Usage:
    python -X gil=0 mech_probe.py <scenario> [waves]

Scenarios (one per process; each wave starts 3 threads together and joins them,
the gauntlet's shape):
    none    - no churn; measure twice.
    idle    - the threads do nothing.
    local   - each thread builds and drops 2,000 small slotted objects.
    handoff - like local, but each thread leaves 200 objects in a shared pool that
              the next wave's threads take and drop (objects outlive their thread).
    keep    - like local, but each thread leaves 20 objects alive to the end; the
              thread cost is measured again after they are dropped.
    intern  - each thread interns 50 new unique strings (immortal on 3.14t).

Contract:
    Prints one line: scenario, waves, then the median start+join (us) of 200 no-op
    threads before the churn, after it, and (keep only) after dropping the kept
    objects.
"""
import collections
import statistics
import sys
import threading
import time
from typing import Any, Callable, Deque, List


class Small:
    """A slotted two-field object, the shape the gauntlet builds."""

    __slots__ = ("a", "b")

    def __init__(self, a: Any, b: Any) -> None:
        """Store two references."""
        self.a = a
        self.b = b


def _noop() -> None:
    """Thread body for the start+join probe."""
    return None


def _thread_cycle_us(samples: int) -> float:
    """
    Median start+join of `samples` no-op threads, one at a time.

    Args:
        samples: Threads to start and join.

    Returns:
        float: Median microseconds per start+join.
    """
    durations: List[int] = []
    for _ in range(samples):
        t0 = time.perf_counter_ns()
        thread = threading.Thread(target=_noop)
        thread.start()
        thread.join()
        durations.append(time.perf_counter_ns() - t0)
    return statistics.median(durations) / 1000.0


def _churn(waves: int, body: Callable[[int], None]) -> None:
    """
    Run `waves` waves of 3 concurrent short-lived threads executing `body`.

    Args:
        waves: Number of waves.
        body: Thread body; receives a unique integer per thread.
    """
    serial = 0
    for _ in range(waves):
        threads = []
        for _ in range(3):
            serial += 1
            thread = threading.Thread(target=body, args=(serial,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()


def main() -> int:
    """
    Run one scenario and print its thread-cost line.

    Returns:
        int: 0.
    """
    scenario = sys.argv[1]
    waves = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    pool: Deque[List[Small]] = collections.deque()
    kept: List[List[Small]] = []
    lock = threading.Lock()

    def idle(serial: int) -> None:
        return None

    def local(serial: int) -> None:
        items = [Small(i, serial) for i in range(2000)]
        del items

    def handoff(serial: int) -> None:
        items = [Small(i, serial) for i in range(2000)]
        with lock:
            taken = pool.popleft() if pool else None
            pool.append(items[:200])
        del taken
        del items

    def keep(serial: int) -> None:
        items = [Small(i, serial) for i in range(2000)]
        with lock:
            kept.append(items[:20])
        del items

    def intern(serial: int) -> None:
        for i in range(50):
            sys.intern(f"probe_name_{serial}_{i}")

    bodies = {"none": None, "idle": idle, "local": local, "handoff": handoff, "keep": keep, "intern": intern}
    before = _thread_cycle_us(200)
    body = bodies[scenario]
    if body is not None:
        _churn(waves, body)
    after = _thread_cycle_us(200)
    line = f"{scenario:8s} waves={waves} before={before:.0f}us after={after:.0f}us"
    if scenario == "keep":
        kept.clear()
        line += f" after_drop={_thread_cycle_us(200):.0f}us"
    if scenario == "handoff":
        pool.clear()
        line += f" after_drop={_thread_cycle_us(200):.0f}us"
    print(line, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
