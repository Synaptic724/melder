import threading
import time
from concurrent.futures import wait, ALL_COMPLETED
from typing import Any, Callable, Dict, List, Optional, Sequence

from melder.utilities.data_structures.concurrent_queue import ConcurrentQueue
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEvent,
    CancellationEventSignal,
)
from melder.utilities.custom_exceptions.operation_cancelled_error import (
    OperationCancelledError,
)
from melder.utilities.general_base.cleanable import Cleanable


class PhaseSchedulerError(RuntimeError):
    """
    Base exception for PhaseScheduler-related failures.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class PhaseTimeoutError(PhaseSchedulerError):
    """
    Raised when a phase exceeds its configured barrier timeout.
    """

    def __init__(self, phase_name: str, timeout_ms: int) -> None:
        msg = (
            f"Phase '{phase_name}' exceeded barrier timeout "
            f"({timeout_ms} ms). Resolution pipeline aborted."
        )
        super().__init__(msg)
        self.phase_name = phase_name
        self.timeout_ms = timeout_ms


class PhaseExecutionError(PhaseSchedulerError):
    """
    Raised when one or more units of work in a phase fail.

    Attributes:
        phase_name: Name of the failing phase.
        errors: List of exceptions raised by the phase's units.
    """

    def __init__(self, phase_name: str, errors: List[BaseException]) -> None:
        msg = (
            f"Phase '{phase_name}' encountered {len(errors)} error(s). "
            f"Resolution pipeline aborted."
        )
        super().__init__(msg)
        self.phase_name = phase_name
        self.errors = errors


# Factory signature:
#   factory(cancel_event) -> Sequence[UnitOfWork]
PhaseWorkFactory = Callable[[CancellationEvent], Sequence["UnitOfWork"]]


class PhaseScheduler(Cleanable):
    """
    Coordinated, multi-phase scheduler for Spellbook resolution.

    This is a **one-shot**, per-Spellbook pipeline runner that:

    - Uses configuration to determine:
        * Worker count (phase_scheduler_workers_per_spellbook)
        * Barrier timeout in ms (phase_scheduler_barrier_timeout_milliseconds)
    - Owns:
        * A shared CancellationEventSignal for cooperative cancellation.
        * A single ConcurrentQueue feeding all worker threads.
        * A fixed pool of worker threads reused across all phases.
    - Executes phases in **registration order**, enforcing:
        * Phase barrier: all UoWs for that phase must complete.
        * Timeout: if the barrier is not reached in time, the phase aborts.
        * Cancellation: any error or timeout cancels the entire pipeline.

    Lifespan
    --------
    - Intended for **one run** per Spellbook conjuration.
    - After `run_all_phases(...)` returns (or raises), call `cleanup()`.
      Once cleaned, the scheduler is permanently broken by design.

    Integration pattern
    -------------------
        scheduler = PhaseScheduler(
            spellbook=spellbook,
            configuration=cfg,
        )

        scheduler.register_phase("scan_spells", phase1_factory)
        scheduler.register_phase("build_graphs", phase2_factory)
        scheduler.register_phase("build_dags", phase3_factory)

        results = scheduler.run_all_phases()
        # results["scan_spells"] -> Sequence[UnitOfWork] (inspect .result())

        scheduler.cleanup()

    Notes
    -----
    - The scheduler does **not** know Spell or DAG internals.
      It only coordinates UnitOfWork instances.
    - Phase strategies/factories are responsible for:
      * Inspecting the Spellbook.
      * Creating appropriately labeled UnitOfWork instances.
      * Attaching the shared `cancel_event` (for cooperative cancellation).
    """

    __slots__ = Cleanable.__slots__ + [
        "_spellbook",
        "_configuration",
        "_workers",
        "_barrier_timeout_ms",
        "_cancel_signal",
        "_cancel_event",
        "_queue",
        "_threads",
        "_lock",
        "_workers_started",
        "_shutdown",
        "_phase_factories",
        "_phase_order",
        "_sentinel",
    ]

    def __init__(
            self,
            *,
            spellbook: Any,
            configuration: Any,
            workers: Optional[int] = None,
            barrier_timeout_ms: Optional[int] = None,
    ) -> None:
        """
        Initialize a new PhaseScheduler.

        Args:
            spellbook:
                The owning Spellbook instance. Used for context only; this
                scheduler does not mutate the Spellbook directly.
            configuration:
                The active Configuration instance. Used to pull worker counts
                and barrier timeout if explicit overrides are not provided.
            workers:
                Optional override for the number of worker threads. If None,
                the scheduler reads `phase_scheduler_workers_per_spellbook`
                from the configuration and falls back to 4 if not present.
            barrier_timeout_ms:
                Optional override for the per-phase barrier timeout in
                milliseconds. If None, the scheduler reads
                `phase_scheduler_barrier_timeout_milliseconds` from the
                configuration and falls back to 60000 ms (60 seconds).
        """
        Cleanable.__init__(self)

        self._spellbook = spellbook
        self._configuration = configuration

        # Worker count: configuration → override → default (4)
        if workers is not None:
            resolved_workers = workers
        else:
            try:
                resolved_workers = configuration.get_property(
                    "phase_scheduler_workers_per_spellbook"
                )
            except Exception:
                resolved_workers = 4

        if not isinstance(resolved_workers, int) or resolved_workers < 1:
            raise ValueError(
                "phase_scheduler_workers_per_spellbook must be a positive integer."
            )

        self._workers: int = resolved_workers

        # Barrier timeout (ms): configuration → override → default (60000)
        if barrier_timeout_ms is not None:
            resolved_timeout = barrier_timeout_ms
        else:
            try:
                resolved_timeout = configuration.get_property(
                    "phase_scheduler_barrier_timeout_milliseconds"
                )
            except Exception:
                resolved_timeout = 60000

        if not isinstance(resolved_timeout, int) or resolved_timeout <= 0:
            raise ValueError(
                "phase_scheduler_barrier_timeout_milliseconds must be a positive integer."
            )

        self._barrier_timeout_ms: int = resolved_timeout

        # Cancellation + queue + worker state
        self._cancel_signal: CancellationEventSignal = CancellationEventSignal()
        self._cancel_event: CancellationEvent = self._cancel_signal.event

        # Use ConcurrentQueue instead of queue.Queue
        self._queue: ConcurrentQueue[Any] = ConcurrentQueue()
        self._threads: List[threading.Thread] = []
        self._workers_started: bool = False
        self._shutdown: bool = False

        self._lock: threading.RLock = threading.RLock()

        # Phase registry
        self._phase_factories: Dict[str, PhaseWorkFactory] = {}
        self._phase_order: List[str] = []

        # Unique sentinel object to signal worker shutdown
        self._sentinel: object = object()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down the scheduler.

        Behavior:
            - Idempotent.
            - Signals cancellation.
            - Sends a sentinel to each worker thread and lets them exit.
            - Nulls out references (spellbook, configuration, queue, threads).
            - Marks the scheduler as cleaned; further use is illegal.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True
            self._shutdown = True

            # Signal global cancellation.
            self._cancel_signal.cancel()

            # Send a sentinel to each worker if they've been started and the queue exists.
            if self._workers_started and self._queue is not None:
                for _ in range(self._workers):
                    self._queue.enqueue(self._sentinel)

            # Join threads.
            for thread in self._threads:
                try:
                    thread.join(timeout=1.0)
                except Exception:
                    # Ignore join failures during teardown.
                    pass

            # Clean up the queue itself if present.
            if self._queue is not None:
                try:
                    self._queue.cleanup()
                except Exception:
                    pass
                self._queue = None

            # Null out references for GC friendliness.
            self._threads = []
            self._spellbook = None
            self._configuration = None

        # Drop lock last.
        self._lock = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def cancel_event(self) -> CancellationEvent:
        """
        Shared CancellationEvent used by all Units of Work.

        Phase factories should attach this event to every UnitOfWork they
        produce so that scheduler-initiated cancellation is honoured.
        """
        return self._cancel_event

    @property
    def is_cancelled(self) -> bool:
        """
        Return True if cancellation has been signalled.
        """
        return self._cancel_signal.is_set

    @property
    def workers(self) -> int:
        """
        Number of worker threads assigned to this scheduler.
        """
        return self._workers

    @property
    def barrier_timeout_ms(self) -> int:
        """
        Per-phase barrier timeout in milliseconds.
        """
        return self._barrier_timeout_ms

    # ------------------------------------------------------------------
    # Phase registration API
    # ------------------------------------------------------------------

    def register_phase(self, name: str, factory: PhaseWorkFactory) -> None:
        """
        Register a phase in the scheduler.

        Phases execute in the order they are registered.

        Args:
            name:
                Logical phase name (e.g. "scan_spells", "build_graphs").
            factory:
                Callable that receives the shared CancellationEvent and
                returns a Sequence of UnitOfWork objects to execute for
                this phase.

        Raises:
            RuntimeError: If the scheduler has been cleaned.
            ValueError: If the name is empty or already registered.
            TypeError: If `factory` is not callable.
        """
        self.check_cleaned()

        if not isinstance(name, str) or not name:
            raise ValueError("Phase name must be a non-empty string.")

        if not callable(factory):
            raise TypeError("Phase factory must be callable(cancel_event) -> Sequence[UnitOfWork].")

        with self._lock:
            if name in self._phase_factories:
                raise ValueError(f"Phase '{name}' is already registered.")
            self._phase_factories[name] = factory
            self._phase_order.append(name)

    # ------------------------------------------------------------------
    # Worker pool
    # ------------------------------------------------------------------

    def _start_workers_if_needed(self) -> None:
        """
        Ensure the worker pool is started exactly once.
        """
        if self._workers_started:
            return

        with self._lock:
            if self._workers_started:
                return

            for i in range(self._workers):
                thread = threading.Thread(
                    target=self._worker_loop,
                    name=f"MelderPhaseWorker-{i}",
                    daemon=True,
                )
                self._threads.append(thread)
                thread.start()

            self._workers_started = True

    def _worker_loop(self) -> None:
        """
        Worker thread loop.

        Continuously pulls UnitOfWork instances off the shared queue and
        executes them until:

            - A sentinel is received, or
            - The scheduler is shut down, or
            - Cancellation is signalled.

        Exceptions thrown by UoW execution:
            - OperationCancelledError:
                Treated as expected cooperative cancellation.
            - Any other BaseException:
                Triggers global cancellation via `cancel()`, but the worker
                continues its loop until shutdown.
        """
        while True:
            if self._shutdown or self._cancel_signal.is_set:
                break

            # Non-blocking dequeue using ConcurrentQueue.
            # If empty, briefly sleep to avoid a hot spin.
            uow = self._queue.dequeue(ignore_exception=True)
            if uow is None:
                time.sleep(0.01)
                continue

            if uow is self._sentinel:
                # Sentinel: worker is being shut down.
                break

            try:
                uow()
            except OperationCancelledError:
                # Cooperative cancellation already recorded into the Future.
                pass
            except BaseException:
                # Record failure via Future + propagate cancellation to the pipeline.
                self._cancel_signal.cancel()

    # ------------------------------------------------------------------
    # Phase execution / barrier
    # ------------------------------------------------------------------

    def _run_single_phase(
            self,
            phase_name: str,
            factory: PhaseWorkFactory,
    ) -> Sequence["UnitOfWork"]:
        """
        Internal

        Run a single phase:

            1. Ask the factory for UnitsOfWork.
            2. Enqueue all UoWs onto the shared worker queue.
            3. Wait for completion (or timeout) using Future.wait().
            4. Aggregate any exceptions and raise PhaseExecutionError.

        Args:
            phase_name:
                Logical name of the phase.
            factory:
                PhaseWorkFactory used to build the phase's UoWs.

        Returns:
            Sequence[UnitOfWork]:
                The sequence produced by the factory. Callers may inspect
                `result()` or `exception()` on these as needed.

        Raises:
            PhaseTimeoutError: If the barrier timeout is exceeded.
            PhaseExecutionError: If any UoW raises an exception.
        """
        if self._cancel_signal.is_set:
            # Upstream failure or explicit cancel – short-circuit this phase.
            raise PhaseSchedulerError(
                f"Phase '{phase_name}' skipped because cancellation has already been signalled."
            )

        # Build the work for this phase.
        units: Sequence["UnitOfWork"] = factory(self._cancel_event)

        # No work = trivial barrier.
        if not units:
            return units

        # Make sure workers are up.
        self._start_workers_if_needed()

        # Enqueue all units.
        for uow in units:
            self._queue.enqueue(uow)

        timeout_sec = self._barrier_timeout_ms / 1000.0

        # Barrier: wait for all futures tied to this phase to complete.
        start = time.monotonic()
        done, not_done = wait(units, timeout=timeout_sec, return_when=ALL_COMPLETED)
        elapsed_ms = int((time.monotonic() - start) * 1000.0)

        if not_done:
            # Timed out: signal cancellation and raise.
            self._cancel_signal.cancel()
            raise PhaseTimeoutError(phase_name, self._barrier_timeout_ms)

        # All Futures completed (either with result, exception, or cancellation).
        errors: List[BaseException] = []
        for uow in units:
            exc = uow.exception()
            if exc is not None:
                errors.append(exc)

        if errors:
            # Cancel downstream phases.
            self._cancel_signal.cancel()
            raise PhaseExecutionError(phase_name, errors)

        return units

    # ------------------------------------------------------------------
    # Public run API
    # ------------------------------------------------------------------

    def run_all_phases(self) -> Dict[str, Sequence["UnitOfWork"]]:
        """
        Execute all registered phases in registration order.

        Returns:
            Dict[str, Sequence[UnitOfWork]]:
                Mapping of phase_name -> Sequence[UnitOfWork]. Callers may
                inspect individual results via `uow.result()` after a
                successful run.

        Raises:
            PhaseSchedulerError (including subclasses PhaseTimeoutError
            and PhaseExecutionError) if any phase fails or times out.
        """
        self.check_cleaned()

        with self._lock:
            phase_names = list(self._phase_order)

        if not phase_names:
            return {}

        results: Dict[str, Sequence["UnitOfWork"]] = {}

        for name in phase_names:
            factory = self._phase_factories.get(name)
            if factory is None:
                raise PhaseSchedulerError(
                    f"Internal error: phase '{name}' has no registered factory."
                )

            units = self._run_single_phase(name, factory)
            results[name] = units

            if self._cancel_signal.is_set:
                # Upstream phase signalled cancellation; do not proceed further.
                break

        return results

    def cancel(self) -> None:
        """
        Explicitly signal cancellation for all phases and workers.

        This is idempotent and can be called from any thread.
        """
        self._cancel_signal.cancel()
