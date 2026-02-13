import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from queue import SimpleQueue
import sys
from typing import Callable, Iterable, List, Dict, Tuple

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from melder.utilities.synchronization.counter_switch import CounterSwitch
from melder.utilities.synchronization.fast_switch import FastSwitch
from melder.utilities.synchronization.ticket_flag import TicketFlag


@dataclass(frozen=True)
class _RoundStats:
    """
    Hold one benchmark round for a single strategy.

    Purpose:
        Keep per-round timing and checksum values so aggregate calculations
        are explicit and reproducible.

    Contract:
        - Times are measured in nanoseconds.
        - Checksums are deterministic sanity values for loop correctness.
    """

    strategy: str
    access_ns: int
    update_ns: int
    change_ns: int
    access_checksum: int
    update_checksum: int
    change_checksum: int


@dataclass(frozen=True)
class _AggregateStats:
    """
    Hold averaged benchmark results for a strategy.

    Purpose:
        Provide a compact summary for ranking strategies across workloads.

    Contract:
        - All averages are arithmetic means over benchmark rounds.
        - Per-op values are derived from averaged totals and iteration count.
    """

    strategy: str
    avg_access_ns: float
    avg_update_ns: float
    avg_change_ns: float
    avg_access_op_ns: float
    avg_update_op_ns: float
    avg_change_op_ns: float
    avg_total_ns: float


class _RLockBoolPrimitive:
    """
    Benchmark primitive using ``threading.RLock`` + boolean state.

    Purpose:
        Model a re-entrant lock guard around a single gate-state boolean.
    """

    __slots__ = ("_lock", "_enabled")

    def __init__(self) -> None:
        """Initialize the primitive in enabled state."""
        self._lock = threading.RLock()
        self._enabled = True

    def run_access(self, iterations: int) -> int:
        """
        Execute locked read-only gate checks.

        Returns:
            int: Count of truthy reads.
        """
        count = 0
        for _ in range(iterations):
            with self._lock:
                if self._enabled:
                    count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute locked state toggles.

        Returns:
            int: Count of iterations where state ended True after toggle.
        """
        count = 0
        for _ in range(iterations):
            with self._lock:
                self._enabled = not self._enabled
                if self._enabled:
                    count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute locked close->open change cycles.

        Returns:
            int: Count of successful cycles ending in enabled state.
        """
        count = 0
        for _ in range(iterations):
            with self._lock:
                self._enabled = False
                self._enabled = True
                if self._enabled:
                    count += 1
        return count


class _LockBoolPrimitive:
    """
    Benchmark primitive using ``threading.Lock`` + boolean state.

    Purpose:
        Model a non-reentrant lock guard around a single gate-state boolean.
    """

    __slots__ = ("_lock", "_enabled")

    def __init__(self) -> None:
        """Initialize the primitive in enabled state."""
        self._lock = threading.Lock()
        self._enabled = True

    def run_access(self, iterations: int) -> int:
        """
        Execute locked read-only gate checks.

        Returns:
            int: Count of truthy reads.
        """
        count = 0
        for _ in range(iterations):
            with self._lock:
                if self._enabled:
                    count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute locked state toggles.

        Returns:
            int: Count of iterations where state ended True after toggle.
        """
        count = 0
        for _ in range(iterations):
            with self._lock:
                self._enabled = not self._enabled
                if self._enabled:
                    count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute locked close->open change cycles.

        Returns:
            int: Count of successful cycles ending in enabled state.
        """
        count = 0
        for _ in range(iterations):
            with self._lock:
                self._enabled = False
                self._enabled = True
                if self._enabled:
                    count += 1
        return count


class _DequeTicketPrimitive:
    """
    Benchmark primitive using ``deque`` ticket operations.

    Purpose:
        Model a low-overhead ticket queue where active work is represented by
        ``None`` markers and access checks use ``len(deque)``.
    """

    __slots__ = ("_tickets",)

    def __init__(self) -> None:
        """Initialize with an empty ticket deque."""
        self._tickets = deque()

    def run_access(self, iterations: int) -> int:
        """
        Execute read-only checks using ``len(deque)``.

        Returns:
            int: Count of iterations where no active ticket exists.
        """
        count = 0
        tickets = self._tickets
        for _ in range(iterations):
            if len(tickets) == 0:
                count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute enqueue/dequeue update pairs with ``None`` ticket markers.

        Returns:
            int: Count of iterations where queue was drained back to zero.
        """
        count = 0
        tickets = self._tickets
        for _ in range(iterations):
            tickets.append(None)
            tickets.pop()
            if len(tickets) == 0:
                count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute change cycles using len-check + enqueue + dequeue.

        Returns:
            int: Count of successful guarded change cycles.
        """
        count = 0
        tickets = self._tickets
        for _ in range(iterations):
            if len(tickets) == 0:
                tickets.append(None)
                tickets.pop()
                count += 1
        return count


class _BoolOnlyPrimitive:
    """
    Benchmark primitive using only a plain boolean.

    Purpose:
        Provide a lock-free baseline for simple boolean access and updates.
    """

    __slots__ = ("_enabled",)

    def __init__(self) -> None:
        """Initialize the primitive in enabled state."""
        self._enabled = True

    def run_access(self, iterations: int) -> int:
        """
        Execute plain boolean read checks.

        Returns:
            int: Count of truthy reads.
        """
        count = 0
        enabled = self._enabled
        for _ in range(iterations):
            if enabled:
                count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute plain boolean state toggles.

        Returns:
            int: Count of iterations where state ended True after toggle.
        """
        count = 0
        enabled = self._enabled
        for _ in range(iterations):
            enabled = not enabled
            if enabled:
                count += 1
        self._enabled = enabled
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute plain boolean close->open change cycles.

        Returns:
            int: Count of successful cycles ending in enabled state.
        """
        count = 0
        for _ in range(iterations):
            self._enabled = False
            self._enabled = True
            if self._enabled:
                count += 1
        return count


class _SimpleQueueTicketPrimitive:
    """
    Benchmark primitive using ``SimpleQueue`` as its own context manager.

    Purpose:
        Compare a queue-based blocking ticket acquire/release model against
        deque and lock-based primitives.
    """

    __slots__ = ("_queue", "_leased_ticket")

    def __init__(self) -> None:
        """Initialize a single-ticket queue with ``None`` payload."""
        self._queue = SimpleQueue()
        self._queue.put(None)
        self._leased_ticket = None

    def __enter__(self):
        """
        Acquire one ticket using blocking queue get.

        Returns:
            object:
                The acquired ticket payload.
        """
        self._leased_ticket = self._queue.get()
        return self._leased_ticket

    def __exit__(self, exc_type, exc, tb) -> bool:
        """
        Return leased ticket back to the queue.

        Returns:
            bool:
                Always ``False`` to avoid suppressing exceptions.
        """
        self._queue.put(self._leased_ticket)
        self._leased_ticket = None
        return False

    def run_access(self, iterations: int) -> int:
        """
        Execute ticket acquire/release checks via context manager.

        Returns:
            int:
                Count of iterations where acquired ticket is ``None``.
        """
        count = 0
        for _ in range(iterations):
            with self as ticket:
                if ticket is None:
                    count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute ticket acquire/release update cycles.

        Returns:
            int:
                Count of successful queue lease cycles.
        """
        count = 0
        for _ in range(iterations):
            with self:
                count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute change cycles using queue lease and local change marker.

        Returns:
            int:
                Count of successful lease + change cycles.
        """
        count = 0
        for _ in range(iterations):
            with self:
                changed = True
                if changed:
                    count += 1
        return count


class _FastSwitchPrimitive:
    """
    Benchmark adapter over the production ``FastSwitch`` primitive.

    Purpose:
        Compare raw deque-ticket switch semantics in the same harness used by
        bool/lock/deque/simplequeue baselines.
    """

    __slots__ = ("_switch",)

    def __init__(self) -> None:
        """Initialize with a falsey switch (zero tickets)."""
        self._switch = FastSwitch()

    def run_access(self, iterations: int) -> int:
        """
        Execute read checks against ticket-count zero state.

        Returns:
            int:
                Count of iterations where ticket count is zero.
        """
        count = 0
        switch = self._switch
        for _ in range(iterations):
            if len(switch) == 0:
                count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute method-based ticket update cycles.

        Returns:
            int:
                Count of successful update cycles.
        """
        count = 0
        switch = self._switch
        for _ in range(iterations):
            switch.set_true()
            switch.set_false()
            count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute change cycles via explicit FastSwitch methods.

        Returns:
            int:
                Count of successful change cycles.
        """
        count = 0
        switch = self._switch
        for _ in range(iterations):
            switch.set_true()
            changed = True
            if changed:
                count += 1
            switch.set_false()
        return count


class _CounterSwitchPrimitive:
    """
    Benchmark adapter over the production ``CounterSwitch`` primitive.

    Purpose:
        Compare deque-counter + condition-sleep semantics against the existing
        baseline primitives.
    """

    __slots__ = ("_switch",)

    def __init__(self) -> None:
        """Initialize with idle counter state (zero tickets)."""
        self._switch = CounterSwitch(0)

    def run_access(self, iterations: int) -> int:
        """
        Execute read checks against idle state.

        Returns:
            int:
                Count of iterations where state remains idle.
        """
        count = 0
        switch = self._switch
        for _ in range(iterations):
            if switch.state == 0:
                count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute explicit pending->complete->idle cycles.

        Returns:
            int:
                Count of successful state cycles.
        """
        count = 0
        switch = self._switch
        for _ in range(iterations):
            switch.set_pending()
            switch.set_complete()
            switch.reset(0)
            count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute selector-driven change publish cycles.

        Returns:
            int:
                Count of successful selector change cycles.
        """
        count = 0
        switch = self._switch
        selector = switch.selector
        for _ in range(iterations):
            mode = selector()
            if mode == 1:
                switch.close_selector()
            if selector() >= 2:
                count += 1
            switch.reset(0)
        return count


class _TicketFlagPrimitive:
    """
    Benchmark adapter over the production ``TicketFlag`` primitive.

    Purpose:
        Compare deque-backed flag semantics against ``FastSwitch`` and plain
        bool in a dedicated three-strategy benchmark.
    """

    __slots__ = ("_flag",)

    def __init__(self) -> None:
        """Initialize with falsey ticket-flag state."""
        self._flag = TicketFlag()

    def run_access(self, iterations: int) -> int:
        """
        Execute read checks against zero-ticket state.

        Returns:
            int:
                Count of iterations where flag remains falsey.
        """
        count = 0
        flag = self._flag
        for _ in range(iterations):
            if len(flag) == 0:
                count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute method-driven true/false update cycles.

        Returns:
            int:
                Count of successful update cycles.
        """
        count = 0
        flag = self._flag
        for _ in range(iterations):
            flag.set_true()
            flag.set_false()
            count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute change cycles using explicit flag method calls.

        Returns:
            int:
                Count of successful change cycles.
        """
        count = 0
        flag = self._flag
        for _ in range(iterations):
            flag.set_true()
            changed = True
            if changed:
                count += 1
            flag.set_false()
        return count


def _measure_ns(fn: Callable[[int], int], iterations: int) -> tuple[int, int]:
    """
    Measure function runtime in nanoseconds.

    Args:
        fn:
            Callable that runs one benchmark workload and returns checksum.
        iterations:
            Number of loop iterations passed to ``fn``.

    Returns:
        tuple[int, int]:
            ``(elapsed_ns, checksum)``.
    """
    start_ns = time.perf_counter_ns()
    checksum = fn(iterations)
    elapsed_ns = time.perf_counter_ns() - start_ns
    return elapsed_ns, checksum


def _split_iterations(total_iterations: int, thread_count: int) -> List[int]:
    """
    Split total iterations across worker threads.

    Contract:
        - Sum of returned slices equals ``total_iterations``.
        - Slice sizes differ by at most one iteration.
    """
    if thread_count <= 0:
        raise ValueError("thread_count must be greater than zero.")
    base = total_iterations // thread_count
    remainder = total_iterations % thread_count
    return [base + (1 if index < remainder else 0) for index in range(thread_count)]


def _measure_threaded_ns(
    fn: Callable[[int], int],
    total_iterations: int,
    thread_count: int,
) -> tuple[int, int]:
    """
    Measure one shared workload under concurrent thread execution.

    Purpose:
        Run the same shared primitive method concurrently across N threads and
        return elapsed time and total checksum.

    Args:
        fn:
            Shared workload function that accepts iteration count.
        total_iterations:
            Total operations to execute across all workers.
        thread_count:
            Number of worker threads.

    Returns:
        tuple[int, int]:
            ``(elapsed_ns, checksum_sum)``.
    """
    work_slices = _split_iterations(total_iterations, thread_count)
    results = [0] * thread_count
    errors: List[BaseException] = []
    start_barrier = threading.Barrier(thread_count + 1)

    def _worker(index: int, iterations: int) -> None:
        try:
            start_barrier.wait()
            results[index] = fn(iterations)
        except BaseException as exc:
            errors.append(exc)

    workers = [
        threading.Thread(target=_worker, args=(index, iters), daemon=True)
        for index, iters in enumerate(work_slices)
    ]
    for worker in workers:
        worker.start()

    start_ns = time.perf_counter_ns()
    start_barrier.wait()
    for worker in workers:
        worker.join()
    elapsed_ns = time.perf_counter_ns() - start_ns

    if errors:
        raise errors[0]
    return elapsed_ns, sum(results)


def _run_threaded_round(
    strategy: str,
    factory: Callable[[], object],
    iterations: int,
    thread_count: int,
) -> _RoundStats:
    """
    Execute one full concurrent benchmark round for a strategy.

    Contract:
        - Uses a fresh primitive instance per workload.
        - Each workload runs all workers against one shared primitive.
        - Returns checksums summed across workers.
    """
    access_primitive = factory()
    access_ns, access_checksum = _measure_threaded_ns(
        access_primitive.run_access,
        iterations,
        thread_count,
    )

    update_primitive = factory()
    update_ns, update_checksum = _measure_threaded_ns(
        update_primitive.run_update,
        iterations,
        thread_count,
    )

    change_primitive = factory()
    change_ns, change_checksum = _measure_threaded_ns(
        change_primitive.run_change,
        iterations,
        thread_count,
    )

    return _RoundStats(
        strategy=strategy,
        access_ns=access_ns,
        update_ns=update_ns,
        change_ns=change_ns,
        access_checksum=access_checksum,
        update_checksum=update_checksum,
        change_checksum=change_checksum,
    )


def _run_round(
    strategy: str,
    factory: Callable[[], object],
    iterations: int,
) -> _RoundStats:
    """
    Execute one full benchmark round for a strategy.

    Contract:
        - Uses a fresh primitive instance per round.
        - Measures access, update, and change workloads separately.
    """
    primitive = factory()
    access_ns, access_checksum = _measure_ns(primitive.run_access, iterations)
    update_ns, update_checksum = _measure_ns(primitive.run_update, iterations)
    change_ns, change_checksum = _measure_ns(primitive.run_change, iterations)
    return _RoundStats(
        strategy=strategy,
        access_ns=access_ns,
        update_ns=update_ns,
        change_ns=change_ns,
        access_checksum=access_checksum,
        update_checksum=update_checksum,
        change_checksum=change_checksum,
    )


def _aggregate(stats: Iterable[_RoundStats], iterations: int) -> _AggregateStats:
    """
    Aggregate round stats into averaged totals and per-op values.
    """
    rows: List[_RoundStats] = list(stats)
    rounds = len(rows)
    if rounds == 0:
        raise AssertionError("Expected at least one benchmark row.")
    strategy = rows[0].strategy
    avg_access_ns = sum(row.access_ns for row in rows) / rounds
    avg_update_ns = sum(row.update_ns for row in rows) / rounds
    avg_change_ns = sum(row.change_ns for row in rows) / rounds
    return _AggregateStats(
        strategy=strategy,
        avg_access_ns=avg_access_ns,
        avg_update_ns=avg_update_ns,
        avg_change_ns=avg_change_ns,
        avg_access_op_ns=avg_access_ns / iterations,
        avg_update_op_ns=avg_update_ns / iterations,
        avg_change_op_ns=avg_change_ns / iterations,
        avg_total_ns=avg_access_ns + avg_update_ns + avg_change_ns,
    )


def _print_report(aggregates: List[_AggregateStats], iterations: int, rounds: int) -> None:
    """
    Print a concise benchmark report sorted by total average time.
    """
    print("")
    print(
        f"creation_gate_primitive_perf: iterations={iterations}, rounds={rounds}, "
        f"timestamp={time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    ranked = sorted(aggregates, key=lambda row: row.avg_total_ns)
    for row in ranked:
        print(
            f"{row.strategy}: "
            f"access_avg_ns={row.avg_access_ns:.0f} ({row.avg_access_op_ns:.2f}/op), "
            f"update_avg_ns={row.avg_update_ns:.0f} ({row.avg_update_op_ns:.2f}/op), "
            f"change_avg_ns={row.avg_change_ns:.0f} ({row.avg_change_op_ns:.2f}/op), "
            f"total_avg_ns={row.avg_total_ns:.0f}"
        )


def _print_weighted_projection(
    aggregates: List[_AggregateStats],
    profiles: Dict[str, Tuple[float, float, float]],
) -> None:
    """
    Print weighted ns/op projections for workload profiles.

    Purpose:
        Project strategy ranking under realistic operation mix ratios instead
        of equal-weight phase totals.

    Args:
        aggregates:
            Per-strategy averages from measured microbench rounds.
        profiles:
            Mapping of profile name to ``(access_weight, update_weight,
            change_weight)`` tuple. Weights should sum to 1.0.
    """
    if not aggregates:
        return

    for profile_name, (w_access, w_update, w_change) in profiles.items():
        rows = []
        for aggregate in aggregates:
            projected_ns_per_op = (
                aggregate.avg_access_op_ns * w_access
                + aggregate.avg_update_op_ns * w_update
                + aggregate.avg_change_op_ns * w_change
            )
            rows.append((aggregate.strategy, projected_ns_per_op))
        rows.sort(key=lambda item: item[1])
        print(f"weighted_profile={profile_name}")
        for strategy, projected in rows:
            print(f"{strategy}: projected_ns_per_op={projected:.2f}")


def test_creation_gate_primitives_perf() -> None:
    """
    Benchmark lock+bool versus deque-ticket primitives.

    Purpose:
        Compare seven synchronization primitive styles using 1,000,000
        iterations per workload and averaged timing across rounds.

    Contract:
        - Runs access, update, and change loops for each strategy.
        - Uses exactly 1,000,000 iterations per workload.
        - Prints averaged totals and per-operation timings.
        - Verifies deterministic loop checksums for sanity.
    """
    iterations = 1_000_000
    rounds = 5
    expected_access = iterations
    expected_update = iterations // 2
    expected_change = iterations

    configs = [
        ("bool_only", _BoolOnlyPrimitive),
        ("rlock_bool", _RLockBoolPrimitive),
        ("lock_bool", _LockBoolPrimitive),
        ("deque_ticket", _DequeTicketPrimitive),
        ("simplequeue_ticket_ctx", _SimpleQueueTicketPrimitive),
        ("fast_switch", _FastSwitchPrimitive),
        ("counter_switch", _CounterSwitchPrimitive),
    ]

    aggregates: List[_AggregateStats] = []
    for strategy, factory in configs:
        rows: List[_RoundStats] = [
            _run_round(strategy, factory, iterations)
            for _ in range(rounds)
        ]
        for row in rows:
            if row.access_checksum != expected_access:
                raise AssertionError(
                    f"{strategy} access checksum mismatch: {row.access_checksum}"
                )
            if strategy in {
                "deque_ticket",
                "simplequeue_ticket_ctx",
                "fast_switch",
                "counter_switch",
            }:
                expected_update_count = iterations
            else:
                expected_update_count = expected_update
            if row.update_checksum != expected_update_count:
                raise AssertionError(
                    f"{strategy} update checksum mismatch: {row.update_checksum}"
                )
            if row.change_checksum != expected_change:
                raise AssertionError(
                    f"{strategy} change checksum mismatch: {row.change_checksum}"
                )
        aggregates.append(_aggregate(rows, iterations))

    _print_report(aggregates, iterations, rounds)

    # Keep the benchmark test assertion lightweight; values are machine-dependent.
    if len(aggregates) != 7:
        raise AssertionError("Expected seven benchmark strategy aggregates.")


def test_creation_gate_primitives_perf_threaded() -> None:
    """
    Benchmark shared-primitive performance under thread contention.

    Purpose:
        Measure strategy behavior at thread counts 2..5 with shared primitive
        contention and explicit bool-only exclusion in multithread mode.

    Contract:
        - Uses exactly 1,000,000 total iterations per workload per strategy.
        - Runs 3 rounds per strategy/thread count pair.
        - Skips ``bool_only`` as broken by design in multithread mode because
          it is unguarded and race-prone.
        - Prints per-thread-count ranking by averaged total ns.
    """
    iterations = 1_000_000
    rounds = 3
    thread_counts = [2, 3, 4, 5]
    expected_access = iterations
    expected_change = iterations

    configs = [
        ("bool_only", _BoolOnlyPrimitive),
        ("rlock_bool", _RLockBoolPrimitive),
        ("lock_bool", _LockBoolPrimitive),
        ("deque_ticket", _DequeTicketPrimitive),
        ("simplequeue_ticket_ctx", _SimpleQueueTicketPrimitive),
        ("fast_switch", _FastSwitchPrimitive),
        ("counter_switch", _CounterSwitchPrimitive),
    ]

    print("")
    print(
        "creation_gate_primitive_threaded_perf: "
        f"iterations={iterations}, rounds={rounds}, thread_counts={thread_counts}, "
        f"timestamp={time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    measured_rows = 0
    for thread_count in thread_counts:
        print(f"threads={thread_count}")
        aggregates: List[_AggregateStats] = []

        for strategy, factory in configs:
            if strategy == "bool_only":
                print(
                    "bool_only: BROKEN "
                    "(unguarded shared bool race conditions in multithread mode)"
                )
                continue

            rows: List[_RoundStats] = [
                _run_threaded_round(strategy, factory, iterations, thread_count)
                for _ in range(rounds)
            ]

            for row in rows:
                if row.access_checksum != expected_access:
                    raise AssertionError(
                        f"{strategy} threaded access checksum mismatch: {row.access_checksum}"
                    )

                if strategy in {"lock_bool", "rlock_bool"}:
                    expected_update = iterations // 2
                    if row.update_checksum != expected_update:
                        raise AssertionError(
                            f"{strategy} threaded update checksum mismatch: {row.update_checksum}"
                        )
                elif strategy in {"simplequeue_ticket_ctx", "fast_switch", "counter_switch"}:
                    if row.update_checksum != iterations:
                        raise AssertionError(
                            f"{strategy} threaded update checksum mismatch: {row.update_checksum}"
                        )
                else:
                    if row.update_checksum < 0 or row.update_checksum > iterations:
                        raise AssertionError(
                            f"{strategy} threaded update checksum out of range: {row.update_checksum}"
                        )

                if strategy in {
                    "lock_bool",
                    "rlock_bool",
                    "simplequeue_ticket_ctx",
                    "fast_switch",
                    "counter_switch",
                }:
                    if row.change_checksum != expected_change:
                        raise AssertionError(
                            f"{strategy} threaded change checksum mismatch: {row.change_checksum}"
                        )
                else:
                    if row.change_checksum < 0 or row.change_checksum > iterations:
                        raise AssertionError(
                            f"{strategy} threaded change checksum out of range: {row.change_checksum}"
                        )

            aggregate = _aggregate(rows, iterations)
            aggregates.append(aggregate)
            measured_rows += 1

        ranked = sorted(aggregates, key=lambda row: row.avg_total_ns)
        for row in ranked:
            print(
                f"{row.strategy}: "
                f"access_avg_ns={row.avg_access_ns:.0f} ({row.avg_access_op_ns:.2f}/op), "
                f"update_avg_ns={row.avg_update_ns:.0f} ({row.avg_update_op_ns:.2f}/op), "
                f"change_avg_ns={row.avg_change_ns:.0f} ({row.avg_change_op_ns:.2f}/op), "
                f"total_avg_ns={row.avg_total_ns:.0f}"
            )

    if measured_rows == 0:
        raise AssertionError("Expected at least one threaded benchmark measurement.")


def test_creation_gate_primitives_perf_weighted_profiles() -> None:
    """
    Project strategy ranking under weighted hot-path workload profiles.

    Purpose:
        Complement equal-weight microbench totals with read-heavy and mixed
        workload projections so fast-path primitives are evaluated with
        realistic operation ratios.

    Contract:
        - Measures the same strategies using the same per-phase loops.
        - Uses 1,000,000 iterations and 3 rounds.
        - Prints weighted ns/op projections for configured profiles.
    """
    iterations = 1_000_000
    rounds = 3

    configs = [
        ("bool_only", _BoolOnlyPrimitive),
        ("rlock_bool", _RLockBoolPrimitive),
        ("lock_bool", _LockBoolPrimitive),
        ("deque_ticket", _DequeTicketPrimitive),
        ("simplequeue_ticket_ctx", _SimpleQueueTicketPrimitive),
        ("fast_switch", _FastSwitchPrimitive),
        ("counter_switch", _CounterSwitchPrimitive),
    ]

    aggregates: List[_AggregateStats] = []
    for strategy, factory in configs:
        rows: List[_RoundStats] = [
            _run_round(strategy, factory, iterations)
            for _ in range(rounds)
        ]
        aggregates.append(_aggregate(rows, iterations))

    print("")
    print(
        "creation_gate_primitive_weighted_profiles: "
        f"iterations={iterations}, rounds={rounds}, "
        f"timestamp={time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    _print_weighted_projection(
        aggregates,
        profiles={
            # 99.9% reads, sparse mutation/change traffic.
            "hot_read_999_0_5_0_5": (0.999, 0.0005, 0.0005),
            # 99% reads, 1% mutations split evenly.
            "hot_read_99_0_5_0_5": (0.99, 0.005, 0.005),
            # Balanced baseline for comparison.
            "balanced_33_33_33": (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0),
        },
    )

    if len(aggregates) != 7:
        raise AssertionError("Expected seven weighted-profile strategy aggregates.")


def test_fast_switch_three_mode_perf() -> None:
    """
    Dedicated three-strategy benchmark for fast-switch style primitives.

    Purpose:
        Measure only the requested contenders:
        - plain bool baseline
        - deque flag (TicketFlag)
        - FastSwitch

    Contract:
        - Uses 1,000,000 iterations.
        - Uses 5 rounds.
        - Runs access/update/change loops for each strategy.
        - Prints ranked totals and per-op timings.
    """
    iterations = 1_000_000
    rounds = 5
    expected_access = iterations
    expected_update = iterations // 2
    expected_change = iterations

    configs = [
        ("bool_only", _BoolOnlyPrimitive),
        ("deque_flag", _TicketFlagPrimitive),
        ("fast_switch", _FastSwitchPrimitive),
    ]

    aggregates: List[_AggregateStats] = []
    for strategy, factory in configs:
        rows: List[_RoundStats] = [
            _run_round(strategy, factory, iterations)
            for _ in range(rounds)
        ]
        for row in rows:
            if row.access_checksum != expected_access:
                raise AssertionError(
                    f"{strategy} access checksum mismatch: {row.access_checksum}"
                )
            if strategy == "bool_only":
                expected_update_count = expected_update
            else:
                expected_update_count = iterations
            if row.update_checksum != expected_update_count:
                raise AssertionError(
                    f"{strategy} update checksum mismatch: {row.update_checksum}"
                )
            if row.change_checksum != expected_change:
                raise AssertionError(
                    f"{strategy} change checksum mismatch: {row.change_checksum}"
                )
        aggregates.append(_aggregate(rows, iterations))

    print("")
    print(
        "fast_switch_three_mode_perf: "
        f"iterations={iterations}, rounds={rounds}, "
        f"timestamp={time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    ranked = sorted(aggregates, key=lambda row: row.avg_total_ns)
    for row in ranked:
        print(
            f"{row.strategy}: "
            f"access_avg_ns={row.avg_access_ns:.0f} ({row.avg_access_op_ns:.2f}/op), "
            f"update_avg_ns={row.avg_update_ns:.0f} ({row.avg_update_op_ns:.2f}/op), "
            f"change_avg_ns={row.avg_change_ns:.0f} ({row.avg_change_op_ns:.2f}/op), "
            f"total_avg_ns={row.avg_total_ns:.0f}"
        )

    if len(aggregates) != 3:
        raise AssertionError("Expected three strategy aggregates for three-mode test.")
