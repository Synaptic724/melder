import threading
import time
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable, Iterable, List, Tuple

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
    Hold one single-thread benchmark round for a strategy.

    Purpose:
        Keep timing and checksum values grouped so aggregate calculations stay
        explicit and deterministic.

    Contract:
        - Time fields are measured in nanoseconds.
        - Checksum fields are loop-integrity sanity values.
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
    Hold averaged single-thread benchmark stats.

    Purpose:
        Provide one comparable row per strategy across access/update/change
        workloads.
    """

    strategy: str
    avg_access_ns: float
    avg_update_ns: float
    avg_change_ns: float
    avg_access_op_ns: float
    avg_update_op_ns: float
    avg_change_op_ns: float
    avg_total_ns: float


@dataclass(frozen=True)
class _ThreadedRoundStats:
    """
    Hold one orchestrated threaded benchmark round for a strategy.

    Purpose:
        Capture elapsed runtime for one shared primitive under orchestrated
        worker execution and main-thread flick control.
    """

    strategy: str
    thread_count: int
    elapsed_ns: int
    checksum: int


@dataclass(frozen=True)
class _ThreadedAggregateStats:
    """
    Hold averaged threaded benchmark stats.

    Purpose:
        Provide one comparable row per strategy/thread-count pair.
    """

    strategy: str
    thread_count: int
    avg_elapsed_ns: float
    avg_op_ns: float


class _BoolOnlyPrimitive:
    """
    Plain bool strategy baseline.

    Purpose:
        Provide the lowest-overhead non-thread-safe boolean path for direct
        comparison against deque-backed strategies.
    """

    __slots__ = ("_enabled",)

    def __init__(self) -> None:
        """Initialize in falsey state."""
        self._enabled = False

    def is_open(self) -> bool:
        """
        Return current boolean state.

        Returns:
            bool:
                Current open/closed state.
        """
        return self._enabled

    def set_open(self) -> None:
        """
        Set the switch open.

        Returns:
            None.
        """
        self._enabled = True

    def set_closed(self) -> None:
        """
        Set the switch closed.

        Returns:
            None.
        """
        self._enabled = False

    def run_access(self, iterations: int) -> int:
        """
        Execute access-loop reads while falsey.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of reads that observed closed state.
        """
        count = 0
        is_open = self.is_open
        for _ in range(iterations):
            if not is_open():
                count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute open->closed update cycles.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of successful update cycles.
        """
        count = 0
        set_open = self.set_open
        set_closed = self.set_closed
        for _ in range(iterations):
            set_open()
            set_closed()
            count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute change cycles with an open-state check.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of successful change cycles.
        """
        count = 0
        set_open = self.set_open
        set_closed = self.set_closed
        is_open = self.is_open
        for _ in range(iterations):
            set_open()
            if is_open():
                count += 1
            set_closed()
        return count


class _LockBoolPrimitive:
    """
    Bool strategy guarded by ``threading.Lock``.

    Purpose:
        Provide a thread-safe bool baseline with explicit non-reentrant lock
        protection for reads and writes.
    """

    __slots__ = ("_enabled", "_lock")

    def __init__(self) -> None:
        """Initialize in falsey state with lock guard."""
        self._enabled = False
        self._lock = threading.Lock()

    def is_open(self) -> bool:
        """
        Return current boolean state under lock.

        Returns:
            bool:
                Current open/closed state.
        """
        with self._lock:
            return self._enabled

    def set_open(self) -> None:
        """
        Set the switch open under lock.

        Returns:
            None.
        """
        with self._lock:
            self._enabled = True

    def set_closed(self) -> None:
        """
        Set the switch closed under lock.

        Returns:
            None.
        """
        with self._lock:
            self._enabled = False

    def run_access(self, iterations: int) -> int:
        """
        Execute locked access-loop reads while falsey.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of reads that observed closed state.
        """
        count = 0
        is_open = self.is_open
        for _ in range(iterations):
            if not is_open():
                count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute locked open->closed update cycles.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of successful update cycles.
        """
        count = 0
        set_open = self.set_open
        set_closed = self.set_closed
        for _ in range(iterations):
            set_open()
            set_closed()
            count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute locked change cycles with open-state check.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of successful change cycles.
        """
        count = 0
        set_open = self.set_open
        set_closed = self.set_closed
        is_open = self.is_open
        for _ in range(iterations):
            set_open()
            if is_open():
                count += 1
            set_closed()
        return count


class _RLockBoolPrimitive:
    """
    Bool strategy guarded by ``threading.RLock``.

    Purpose:
        Provide a thread-safe bool baseline with explicit reentrant lock
        protection for reads and writes.
    """

    __slots__ = ("_enabled", "_lock")

    def __init__(self) -> None:
        """Initialize in falsey state with reentrant lock guard."""
        self._enabled = False
        self._lock = threading.RLock()

    def is_open(self) -> bool:
        """
        Return current boolean state under lock.

        Returns:
            bool:
                Current open/closed state.
        """
        with self._lock:
            return self._enabled

    def set_open(self) -> None:
        """
        Set the switch open under lock.

        Returns:
            None.
        """
        with self._lock:
            self._enabled = True

    def set_closed(self) -> None:
        """
        Set the switch closed under lock.

        Returns:
            None.
        """
        with self._lock:
            self._enabled = False

    def run_access(self, iterations: int) -> int:
        """
        Execute locked access-loop reads while falsey.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of reads that observed closed state.
        """
        count = 0
        is_open = self.is_open
        for _ in range(iterations):
            if not is_open():
                count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute locked open->closed update cycles.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of successful update cycles.
        """
        count = 0
        set_open = self.set_open
        set_closed = self.set_closed
        for _ in range(iterations):
            set_open()
            set_closed()
            count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute locked change cycles with open-state check.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of successful change cycles.
        """
        count = 0
        set_open = self.set_open
        set_closed = self.set_closed
        is_open = self.is_open
        for _ in range(iterations):
            set_open()
            if is_open():
                count += 1
            set_closed()
        return count


class _FastSwitchPrimitive:
    """
    Adapter over ``FastSwitch``.

    Purpose:
        Measure raw deque-ticket switch mechanics against bool baseline and
        TicketFlag behavior.
    """

    __slots__ = ("_switch",)

    def __init__(self) -> None:
        """Initialize with no active tickets."""
        self._switch = FastSwitch()

    def is_open(self) -> bool:
        """
        Return switch open state.

        Returns:
            bool:
                ``True`` when at least one ticket exists.
        """
        return len(self._switch) > 0

    def set_open(self) -> None:
        """
        Set switch open using one ticket.

        Contract:
            - Adds a ticket only when currently closed.

        Returns:
            None.
        """
        if len(self._switch) == 0:
            self._switch.set_true()

    def set_closed(self) -> None:
        """
        Set switch closed by clearing tickets.

        Returns:
            None.
        """
        self._switch.clear_tickets()

    def run_access(self, iterations: int) -> int:
        """
        Execute access-loop reads while falsey.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of reads that observed closed state.
        """
        count = 0
        is_open = self.is_open
        for _ in range(iterations):
            if not is_open():
                count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute open->closed update cycles.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of successful update cycles.
        """
        count = 0
        set_open = self.set_open
        set_closed = self.set_closed
        for _ in range(iterations):
            set_open()
            set_closed()
            count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute change cycles with an open-state check.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of successful change cycles.
        """
        count = 0
        set_open = self.set_open
        set_closed = self.set_closed
        is_open = self.is_open
        for _ in range(iterations):
            set_open()
            if is_open():
                count += 1
            set_closed()
        return count


class _TicketFlagPrimitive:
    """
    Adapter over ``TicketFlag``.

    Purpose:
        Measure deque-backed flag semantics with cleanup guards disabled from
        the benchmark hot path.
    """

    __slots__ = ("_flag",)

    def __init__(self) -> None:
        """Initialize with no active tickets."""
        self._flag = TicketFlag()

    def is_open(self) -> bool:
        """
        Return flag open state.

        Returns:
            bool:
                ``True`` when at least one ticket exists.
        """
        return len(self._flag) > 0

    def set_open(self) -> None:
        """
        Set flag open using one ticket.

        Contract:
            - Adds a ticket only when currently closed.

        Returns:
            None.
        """
        if len(self._flag) == 0:
            self._flag.set_true()

    def set_closed(self) -> None:
        """
        Set flag closed by clearing tickets.

        Returns:
            None.
        """
        self._flag.clear_tickets()

    def run_access(self, iterations: int) -> int:
        """
        Execute access-loop reads while falsey.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of reads that observed closed state.
        """
        count = 0
        is_open = self.is_open
        for _ in range(iterations):
            if not is_open():
                count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute open->closed update cycles.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of successful update cycles.
        """
        count = 0
        set_open = self.set_open
        set_closed = self.set_closed
        for _ in range(iterations):
            set_open()
            set_closed()
            count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute change cycles with an open-state check.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of successful change cycles.
        """
        count = 0
        set_open = self.set_open
        set_closed = self.set_closed
        is_open = self.is_open
        for _ in range(iterations):
            set_open()
            if is_open():
                count += 1
            set_closed()
        return count


class _CounterSwitchSelectorPrimitive:
    """
    Adapter over ``CounterSwitch`` selector semantics.

    Purpose:
        Benchmark the selector fast-latch path specifically when complete state
        is represented by ticket cardinality ``>=2``.
    """

    __slots__ = ("_switch",)

    def __init__(self) -> None:
        """
        Initialize with default open latch state.

        Contract:
            - ``CounterSwitch`` defaults to state ``2``.
        """
        self._switch = CounterSwitch()

    def is_open(self) -> bool:
        """
        Check latch state through selector API.

        Returns:
            bool:
                ``True`` when selector returns open state ``>=2``.
        """
        return self._switch.selector() >= 2

    def set_open(self) -> None:
        """
        Force complete/open state.

        Returns:
            None.
        """
        self._switch.set_complete()

    def set_closed(self) -> None:
        """
        Force pending/closed state.

        Returns:
            None.
        """
        self._switch.set_pending()

    def run_access(self, iterations: int) -> int:
        """
        Execute selector reads against open latch state.

        Contract:
            - State remains open for the full loop.
            - Count increments on selector open state ``>=2``.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of complete selector results.
        """
        count = 0
        selector = self._switch.selector
        for _ in range(iterations):
            if selector() >= 2:
                count += 1
        return count

    def run_update(self, iterations: int) -> int:
        """
        Execute pending->complete latch cycles.

        Contract:
            - Each iteration starts from open latch state.
            - Transition goes ``2 -> 1 -> 2``.
            - Uses direct methods only (no context manager).

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of successful publish cycles.
        """
        count = 0
        switch = self._switch
        set_pending = switch.set_pending
        close_selector = switch.close_selector
        for _ in range(iterations):
            set_pending()
            close_selector()
            count += 1
        return count

    def run_change(self, iterations: int) -> int:
        """
        Execute selector-verified completion cycles.

        Contract:
            - Each iteration starts from open latch state.
            - Transition goes ``2 -> 1 -> 2``.
            - Selector validates complete mode after publication.
            - Second selector call validates complete mode ``2``.

        Args:
            iterations:
                Number of loop iterations.

        Returns:
            int:
                Count of successful complete validations.
        """
        count = 0
        switch = self._switch
        selector = switch.selector
        set_pending = switch.set_pending
        close_selector = switch.close_selector
        for _ in range(iterations):
            set_pending()
            close_selector()
            if selector() >= 2:
                count += 1
        return count


class _ThreadStepOrchestrator:
    """
    Main-thread step orchestrator for worker lanes.

    Purpose:
        Let worker threads run only when the main thread releases a specific
        step, then block the main thread until every worker reports completion
        for that same step.

    Contract:
        - Worker entry for a step is blocked until main thread release.
        - Main thread release is one-step-at-a-time.
        - Main thread can fail-fast all workers via ``abort``.
        - No defensive fallback paths are included; this helper is benchmark
          infrastructure and assumes well-formed caller flow.
    """

    __slots__ = (
        "_worker_count",
        "_condition",
        "_released_step",
        "_completed_workers",
        "_aborted",
    )

    def __init__(self, worker_count: int) -> None:
        """
        Initialize orchestrator state.

        Args:
            worker_count:
                Number of workers expected to complete each released step.

        Returns:
            None.
        """
        self._worker_count = worker_count
        self._condition = threading.Condition()
        self._released_step = -1
        self._completed_workers = 0
        self._aborted = False

    def wait_for_step(self, step: int, timeout_seconds: float) -> None:
        """
        Block a worker until the requested step is released.

        Args:
            step:
                Step index expected by the worker.
            timeout_seconds:
                Maximum wait duration for this step.

        Returns:
            None.

        Raises:
            TimeoutError:
                If step was not released within timeout.
            RuntimeError:
                If orchestration has been aborted.
        """
        deadline = time.perf_counter() + timeout_seconds
        with self._condition:
            while self._released_step < step and not self._aborted:
                remaining = deadline - time.perf_counter()
                if remaining <= 0:
                    raise TimeoutError(
                        f"Worker timed out waiting for step '{step}'."
                    )
                self._condition.wait(timeout=remaining)
            if self._aborted:
                raise RuntimeError("Worker released due to orchestrator abort.")

    def release_step(self, step: int) -> None:
        """
        Release one step to all workers.

        Args:
            step:
                Step index to release.

        Returns:
            None.
        """
        with self._condition:
            self._completed_workers = 0
            self._released_step = step
            self._condition.notify_all()

    def mark_done(self) -> None:
        """
        Mark one worker complete for the current released step.

        Returns:
            None.
        """
        with self._condition:
            self._completed_workers += 1
            if self._completed_workers >= self._worker_count:
                self._condition.notify_all()

    def wait_for_step_completion(self, timeout_seconds: float) -> None:
        """
        Block main thread until all workers complete current step.

        Args:
            timeout_seconds:
                Maximum wait duration for completion.

        Returns:
            None.

        Raises:
            TimeoutError:
                If completion did not reach worker count in time.
            RuntimeError:
                If orchestration has been aborted.
        """
        deadline = time.perf_counter() + timeout_seconds
        with self._condition:
            while self._completed_workers < self._worker_count and not self._aborted:
                remaining = deadline - time.perf_counter()
                if remaining <= 0:
                    raise TimeoutError("Main thread timed out waiting for workers.")
                self._condition.wait(timeout=remaining)
            if self._aborted:
                raise RuntimeError("Main thread released due to orchestrator abort.")

    def abort(self) -> None:
        """
        Abort orchestration and wake all waiters.

        Returns:
            None.
        """
        with self._condition:
            self._aborted = True
            self._condition.notify_all()


def _measure_ns(fn: Callable[[int], int], iterations: int) -> tuple[int, int]:
    """
    Measure one workload function in nanoseconds.

    Args:
        fn:
            Callable workload that accepts iteration count.
        iterations:
            Loop count forwarded to ``fn``.

    Returns:
        tuple[int, int]:
            ``(elapsed_ns, checksum)``.
    """
    start_ns = time.perf_counter_ns()
    checksum = fn(iterations)
    elapsed_ns = time.perf_counter_ns() - start_ns
    return elapsed_ns, checksum


def _run_round(
    strategy: str,
    factory: Callable[[], object],
    iterations: int,
) -> _RoundStats:
    """
    Execute one single-thread benchmark round.

    Args:
        strategy:
            Strategy name used for reporting.
        factory:
            Primitive factory for this strategy.
        iterations:
            Loop count per workload.

    Returns:
        _RoundStats:
            Round timing/checksum snapshot.
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
    Aggregate single-thread round stats for one strategy.

    Args:
        stats:
            Round snapshots for one strategy.
        iterations:
            Loop count used for each round workload.

    Returns:
        _AggregateStats:
            Averaged strategy metrics.
    """
    rows = list(stats)
    rounds = len(rows)
    avg_access_ns = sum(row.access_ns for row in rows) / rounds
    avg_update_ns = sum(row.update_ns for row in rows) / rounds
    avg_change_ns = sum(row.change_ns for row in rows) / rounds
    return _AggregateStats(
        strategy=rows[0].strategy,
        avg_access_ns=avg_access_ns,
        avg_update_ns=avg_update_ns,
        avg_change_ns=avg_change_ns,
        avg_access_op_ns=avg_access_ns / iterations,
        avg_update_op_ns=avg_update_ns / iterations,
        avg_change_op_ns=avg_change_ns / iterations,
        avg_total_ns=avg_access_ns + avg_update_ns + avg_change_ns,
    )


def _aggregate_threaded(
    stats: Iterable[_ThreadedRoundStats],
    total_ops: int,
) -> _ThreadedAggregateStats:
    """
    Aggregate threaded round stats for one strategy/thread count pair.

    Args:
        stats:
            Threaded round snapshots.
        total_ops:
            Total read operations executed per round.

    Returns:
        _ThreadedAggregateStats:
            Averaged elapsed and per-op timing.
    """
    rows = list(stats)
    rounds = len(rows)
    avg_elapsed_ns = sum(row.elapsed_ns for row in rows) / rounds
    return _ThreadedAggregateStats(
        strategy=rows[0].strategy,
        thread_count=rows[0].thread_count,
        avg_elapsed_ns=avg_elapsed_ns,
        avg_op_ns=avg_elapsed_ns / total_ops,
    )


def _run_orchestrated_flick_round(
    strategy: str,
    factory: Callable[[], object],
    *,
    thread_count: int,
    steps: int,
    reads_per_step: int,
) -> _ThreadedRoundStats:
    """
    Execute one orchestrated threaded round.

    Purpose:
        Run N worker threads where workers only read shared state after each
        main-thread release, and the main thread flicks open/closed between
        releases.

    Args:
        strategy:
            Strategy name used for reporting.
        factory:
            Primitive factory for this strategy.
        thread_count:
            Number of worker threads.
        steps:
            Number of orchestrated phases.
        reads_per_step:
            Read-loop iterations executed by each worker per step.

    Returns:
        _ThreadedRoundStats:
            Elapsed time and checksum for this threaded round.
    """
    primitive = factory()
    orchestrator = _ThreadStepOrchestrator(thread_count)
    start_barrier = threading.Barrier(thread_count + 1)
    errors: List[BaseException] = []
    worker_checksums = [0] * thread_count

    def _worker(worker_index: int) -> None:
        try:
            start_barrier.wait()
            is_open = primitive.is_open
            for step in range(steps):
                orchestrator.wait_for_step(step, timeout_seconds=20.0)
                local_count = 0
                for _ in range(reads_per_step):
                    if is_open():
                        local_count += 1
                worker_checksums[worker_index] += local_count
                orchestrator.mark_done()
        except BaseException as exc:
            errors.append(exc)
            orchestrator.abort()

    workers = [
        threading.Thread(target=_worker, args=(index,), daemon=True)
        for index in range(thread_count)
    ]
    for worker in workers:
        worker.start()

    start_barrier.wait()
    start_ns = time.perf_counter_ns()
    set_open = primitive.set_open
    set_closed = primitive.set_closed
    for step in range(steps):
        if step % 2 == 0:
            set_open()
        else:
            set_closed()
        orchestrator.release_step(step)
        orchestrator.wait_for_step_completion(timeout_seconds=20.0)
    elapsed_ns = time.perf_counter_ns() - start_ns

    for worker in workers:
        worker.join(timeout=20.0)
    if any(worker.is_alive() for worker in workers):
        raise AssertionError(
            f"Threaded benchmark worker did not terminate for '{strategy}'."
        )
    if errors:
        raise errors[0]

    return _ThreadedRoundStats(
        strategy=strategy,
        thread_count=thread_count,
        elapsed_ns=elapsed_ns,
        checksum=sum(worker_checksums),
    )


def test_fast_switch_three_mode_perf_single_thread() -> None:
    """
    Benchmark the requested three strategies in single-thread mode.

    Contract:
        - Compares ``bool_only``, ``lock_bool``, ``rlock_bool``,
          ``deque_flag``, ``fast_switch``, and ``counter_switch_selector``.
        - Runs access/update/change workloads for each strategy.
        - Uses 1,000,000 iterations and 5 rounds.
        - Prints ranked totals and per-op timings.
    """
    iterations = 1_000_000
    rounds = 5
    expected_checksum = iterations

    configs: List[Tuple[str, Callable[[], object]]] = [
        ("bool_only", _BoolOnlyPrimitive),
        ("lock_bool", _LockBoolPrimitive),
        ("rlock_bool", _RLockBoolPrimitive),
        ("deque_flag", _TicketFlagPrimitive),
        ("fast_switch", _FastSwitchPrimitive),
        ("counter_switch_selector", _CounterSwitchSelectorPrimitive),
    ]

    aggregates: List[_AggregateStats] = []
    for strategy, factory in configs:
        rows: List[_RoundStats] = [
            _run_round(strategy, factory, iterations)
            for _ in range(rounds)
        ]
        for row in rows:
            if row.access_checksum != expected_checksum:
                raise AssertionError(
                    f"{strategy} access checksum mismatch: {row.access_checksum}"
                )
            if row.update_checksum != expected_checksum:
                raise AssertionError(
                    f"{strategy} update checksum mismatch: {row.update_checksum}"
                )
            if row.change_checksum != expected_checksum:
                raise AssertionError(
                    f"{strategy} change checksum mismatch: {row.change_checksum}"
                )
        aggregates.append(_aggregate(rows, iterations))

    print("")
    print(
        "fast_switch_three_mode_single_thread_perf: "
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


def test_fast_switch_three_mode_perf_threaded_orchestrated() -> None:
    """
    Benchmark three strategies under orchestrated multithread reads.

    Purpose:
        Use a thread orchestrator where workers run only when the main thread
        releases each step, and the main thread flicks open/closed state
        before every release.

    Contract:
        - Compares ``bool_only``, ``lock_bool``, ``rlock_bool``,
          ``deque_flag``, ``fast_switch``, and ``counter_switch_selector``.
        - Uses thread counts ``2, 3, 4, 5``.
        - Uses 3 rounds per strategy/thread pair.
        - Uses deterministic checksum validation for every round.
        - Prints per-thread rankings by averaged elapsed time.
    """
    steps = 24
    reads_per_step = 5_000
    rounds = 3
    thread_counts = [2, 3, 4, 5]
    true_steps = (steps + 1) // 2

    configs: List[Tuple[str, Callable[[], object]]] = [
        ("bool_only", _BoolOnlyPrimitive),
        ("lock_bool", _LockBoolPrimitive),
        ("rlock_bool", _RLockBoolPrimitive),
        ("deque_flag", _TicketFlagPrimitive),
        ("fast_switch", _FastSwitchPrimitive),
        ("counter_switch_selector", _CounterSwitchSelectorPrimitive),
    ]

    print("")
    print(
        "fast_switch_three_mode_threaded_orchestrated_perf: "
        f"steps={steps}, reads_per_step={reads_per_step}, rounds={rounds}, "
        f"thread_counts={thread_counts}, "
        f"timestamp={time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    measurements: List[_ThreadedAggregateStats] = []
    for thread_count in thread_counts:
        print(f"threads={thread_count}")
        total_ops = thread_count * steps * reads_per_step
        expected_checksum = thread_count * true_steps * reads_per_step
        thread_rows: List[_ThreadedAggregateStats] = []
        for strategy, factory in configs:
            rows: List[_ThreadedRoundStats] = [
                _run_orchestrated_flick_round(
                    strategy,
                    factory,
                    thread_count=thread_count,
                    steps=steps,
                    reads_per_step=reads_per_step,
                )
                for _ in range(rounds)
            ]
            for row in rows:
                if row.checksum != expected_checksum:
                    raise AssertionError(
                        f"{strategy} threaded checksum mismatch: {row.checksum}"
                    )
            aggregate = _aggregate_threaded(rows, total_ops)
            thread_rows.append(aggregate)
            measurements.append(aggregate)
        for row in sorted(thread_rows, key=lambda item: item.avg_elapsed_ns):
            print(
                f"{row.strategy}: "
                f"avg_elapsed_ns={row.avg_elapsed_ns:.0f}, "
                f"avg_op_ns={row.avg_op_ns:.2f}/op"
            )

    if not measurements:
        raise AssertionError("Expected threaded orchestrated benchmark measurements.")
