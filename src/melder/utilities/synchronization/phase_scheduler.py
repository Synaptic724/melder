import threading
import time
from concurrent.futures import wait, FIRST_EXCEPTION
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple
from collections import deque
from melder.utilities.interfaces.interfaces import IConfiguration, ISpellbook
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEvent,
    CancellationEventSignal,
)
from melder.utilities.custom_exceptions.operation_cancelled_error import OperationCancelledError
from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.phase_timeout_error import PhaseTimeoutError
from melder.utilities.general_base.cleanable import Cleanable

# Adjust this import path to wherever UnitOfWork is actually defined.
from melder.utilities.synchronization.unit_of_work import UnitOfWork
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

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
      * Creating appropriately labeled UnitOfWork instances via
        :meth:`create_unit_of_work` so that all work items share the
        scheduler's CancellationEvent.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
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
        """
        Cleanable.__init__(self)
        self._configuration: IConfiguration = configuration
        self._workers: int = self._get_worker_count(configuration)
        self._barrier_timeout_ms: int = self._get_timeout_ms(configuration)

        # Cancellation + queue + worker state
        self._cancel_signal: CancellationEventSignal = CancellationEventSignal()
        self._cancel_event: CancellationEvent = self._cancel_signal.event

        # Use concurrent containers for shared state.
        self._queue: deque[Any] = deque()
        self._threads: List[threading.Thread] = []
        self._workers_started: bool = False
        self._shutdown: bool = False

        self._lock: threading.RLock = threading.RLock()

        # Phase registry (concurrent containers).
        self._phase_factories: Dict[str, Callable[[], Sequence[UnitOfWork]]] = {}
        self._phase_order: List[str] = []

        # Unique sentinel object to signal worker shutdown
        self._sentinel: object = object()

    def _get_worker_count(self, configuration: IConfiguration) -> int:
        """
        Internal helper to get the worker count.
        """
        # Worker count
        try:
            return configuration.get_property(
                "phase_scheduler_workers_per_spellbook"
            )
        except Exception:
            raise ValueError(
                "Failed to read phase_scheduler_workers_per_spellbook from configuration."
            )

    def _get_timeout_ms(self, configuration: IConfiguration) -> int:
        """
        Internal helper to get the barrier timeout in milliseconds.
        """
        try:
            return configuration.get_property(
                "phase_scheduler_barrier_timeout_milliseconds"
            )
        except Exception:
            raise ValueError(
                "Failed to read phase_scheduler_barrier_timeout_milliseconds from configuration."
            )
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
                    self._queue.append(self._sentinel)

            # Join threads.
            for thread in self._threads:
                try:
                    thread.join(timeout=5.0)
                except Exception:
                    # Ignore join failures during teardown.
                    pass

            # Clean up the queue itself if present.
            if self._queue is not None:
                self._queue.clear()
                self._queue = None

            if self._threads is not None:
                self._threads.clear()
                self._threads = None
            if self._phase_factories is not None:
                self._phase_factories.clear()
                self._phase_factories = None
            if self._phase_order is not None:
                self._phase_order.clear()
                self._phase_order = None

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

        Phase factories should NOT construct their own events; instead they
        should call :meth:`create_unit_of_work` so this event is wired in
        automatically.
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
    # UnitOfWork factory
    # ------------------------------------------------------------------

    def create_unit_of_work(
            self,
            func: Callable[..., Any],
            *,
            args: Optional[Tuple[Any, ...]] = None,
            kwargs: Optional[Dict[str, Any]] = None,
            label: Optional[str] = None,
            metadata: Any = None,
    ) -> UnitOfWork:
        """
        Convenience factory for creating a UnitOfWork that is already wired to
        this scheduler's shared CancellationEvent.

        Phase factories should prefer this instead of constructing UnitOfWork
        directly so that:

            - All work items participate in scheduler-driven cooperative
              cancellation.
            - The wiring of CancellationEvent is centralized inside the
              scheduler.

        Args:
            func:
                The callable to execute inside the UnitOfWork.
            args:
                Optional positional arguments for the callable.
            kwargs:
                Optional keyword arguments for the callable.
            label:
                Optional human-readable label (for logging/telemetry).
            metadata:
                Optional metadata describing this unit (spell id, phase, etc.).

        Returns:
            UnitOfWork: A newly constructed UnitOfWork bound to this scheduler's
            CancellationEvent.
        """
        self.check_cleaned()

        return UnitOfWork(
            func=func,
            args=args,
            kwargs=kwargs,
            cancel_event=self._cancel_event,
            label=label,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Phase registration API
    # ------------------------------------------------------------------

    def register_phase(self, name: str, factory: Callable[[], Sequence[UnitOfWork]]) -> None:
        """
        Register a phase in the scheduler.

        Phases execute in the order they are registered.

        Args:
            name:
                Logical phase name (e.g. "scan_spells", "build_graphs").
            factory:
                Callable[[] -> Sequence[UnitOfWork]] that, when invoked, builds
                all UnitsOfWork for this phase. Factories should use
                :meth:`create_unit_of_work` to ensure each unit is bound to
                this scheduler's CancellationEvent.

        Raises:
            RuntimeError: If the scheduler has been cleaned.
            ValueError: If the name is empty or already registered.
            TypeError: If `factory` is not callable.
        """
        self.check_cleaned()

        if not isinstance(name, str) or not name:
            raise ValueError("Phase name must be a non-empty string.")

        if not callable(factory):
            raise TypeError("Phase factory must be callable() -> Sequence[UnitOfWork].")

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
            try:
                uow = self._queue.popleft()
            except IndexError:
                time.sleep(0.0001)
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
            factory: Callable[[], Sequence[UnitOfWork]],
    ) -> Sequence[UnitOfWork]:
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
                Callable[[] -> Sequence[UnitOfWork]] used to build the phase's
                UnitsOfWork.

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
        units: Sequence[UnitOfWork] = factory()

        # No work = trivial barrier.
        if not units:
            return units

        # Make sure workers are up.
        self._start_workers_if_needed()

        # Enqueue all units.
        for uow in units:
            self._queue.append(uow)

        timeout_sec = self._barrier_timeout_ms / 1000.0

        # Barrier: wait for futures tied to this phase to complete or fail.
        start = time.monotonic()
        deadline = start + timeout_sec
        pending = set(units)
        done: set[UnitOfWork] = set()

        while pending:
            if self._cancel_signal.is_set:
                errors = [uow.exception() for uow in done if uow.exception() is not None]
                if errors:
                    raise PhaseExecutionError(phase_name, errors)
                raise PhaseSchedulerError(
                    f"Phase '{phase_name}' cancelled during execution."
                )

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                # Timed out: signal cancellation and raise.
                self._cancel_signal.cancel()
                raise PhaseTimeoutError(phase_name, self._barrier_timeout_ms)

            # Poll in tight intervals so we can fail fast on exceptions/cancel.
            wait_timeout = min(0.0001, remaining)
            done_now, pending = wait(
                pending,
                timeout=wait_timeout,
                return_when=FIRST_EXCEPTION,
            )

            if done_now:
                done.update(done_now)
                errors = [uow.exception() for uow in done_now if uow.exception() is not None]
                if errors:
                    # Cancel downstream phases.
                    self._cancel_signal.cancel()
                    all_errors = [uow.exception() for uow in done if uow.exception() is not None]
                    raise PhaseExecutionError(phase_name, all_errors)

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

    def run_all_phases(self, conduit_id: Optional[str] = None) -> Dict[str, Sequence[UnitOfWork]]:
        """
        Execute all registered phases in registration order.

        Args:
            conduit_id:
                Optional conduit identifier carried by callers that need to
                align phase execution with a specific conduit context. The
                scheduler does not use this value directly; phase factories
                may capture it via closure as needed.
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

        # Snapshot the phase order to avoid surprises if someone tweaks it
        # concurrently (ConcurrentList is safe, but we still want a stable run view).
        phase_names = list(self._phase_order)

        if not phase_names:
            return {}

        results: Dict[str, Sequence[UnitOfWork]] = {}

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
