import threading
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    ClassVar,
)
from queue import SimpleQueue



if TYPE_CHECKING:
    from melder.aether.spellbook.configuration.spellbook_configuration import (
        SpellbookConfiguration,
    )
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEvent,
    CancellationEventSignal,
)
from melder.utilities.synchronization.phase_latch import PhaseLatch
from melder.utilities.custom_exceptions.operation_cancelled_error import OperationCancelledError
from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.phase_timeout_error import PhaseTimeoutError
from melder.utilities.general_base.cleanable import Cleanable

# Adjust this import path to wherever UnitOfWork is actually defined.
from melder.utilities.synchronization.unit_of_work import UnitOfWork



class PhaseScheduler(Cleanable):
    """
    Coordinated, multiphase scheduler for Spellbook resolution.

    This is a **persistent**, per-owner pipeline runner. The Spellbook is
    the original owner; world-scope owners (the crystallizer restore lane)
    construct it through the explicit-value lane instead of a
    SpellbookConfiguration (S2, parallel_restore_ulid_identity). It:

    - Determines its policy from EITHER lane:
        * Configuration lane: worker count
          (phase_scheduler_workers_per_spellbook) and barrier timeout in ms
          (phase_scheduler_barrier_timeout_milliseconds)
        * Explicit lane: keyword-only worker_count / barrier_timeout_ms
          construction overrides (both required together when no
          configuration is supplied)
    - Owns:
        * A fixed pool of worker threads, spawned lazily once and reused
          across ALL runs for the scheduler's lifetime (v2: the pool is no
          longer torn down per conjure group; thread spawn/join cost moves
          to Spellbook teardown).
        * A single queue feeding all worker threads. Workers block on the
          queue (no idle polling) and exit only on an explicit sentinel.
        * A per-run CancellationEventSignal: every `run_all_phases(...)`
          call begins a fresh cooperative-cancellation scope, so one run's
          failure can never poison a later run on the same pool.
    - Executes phases in **registration order**, enforcing:
        * Phase barrier: all units for that phase must be complete, tracked
          by one `PhaseLatch` per phase (one event wait) instead of
          per-unit Future waits.
        * Timeout: if the barrier is not reached in time, the phase aborts.
        * Fail-fast: a unit failure wakes the barrier immediately and
          cancels the rest of the run; before the failure surfaces to the
          caller, the phase QUIESCES - it waits (bounded by the barrier
          budget) until every in-flight sibling unit has reported, so
          caller-side unwind/teardown never runs concurrently with a
          straggler unit body still building state.

    Lifespan
    --------
    - Intended to live as long as its owning Spellbook and be reused for
      every phase run (conjure groups and lazy revalidations).
    - Phase registrations are per-run state: they are consumed by
      `run_all_phases(...)` and cleared afterward (or via `clear_phases()`).
    - `cleanup()` permanently breaks the scheduler: workers are sentinelled
      and joined exactly once, at owner teardown.

    Integration pattern
    -------------------
        scheduler = spellbook-owned PhaseScheduler(...)

        scheduler.register_phase("scan_spells", phase1_factory)
        scheduler.register_phase("build_graphs", phase2_factory)
        results = scheduler.run_all_phases()
        # registrations are cleared; the scheduler is immediately reusable:
        scheduler.register_phase("root_blueprints", phase5_factory)
        results = scheduler.run_all_phases()

        ... at Spellbook teardown ...
        scheduler.cleanup()

    Control contract (why workers never run inline)
    -----------------------------------------------
    Units always execute on worker threads, even with one worker. An inline
    workers==1 fast path was tried and reverted: synchronous execution in
    the caller thread cannot honor the scheduler's async control contract.
    A unit blocked on an external signal deadlocks the caller (external
    cancel can never be observed), and preemptive barrier timeouts
    (PhaseTimeoutError while a unit is still running) are impossible
    without a separate execution thread. The persistent pool in this
    version is the sanctioned answer to single-run thread-spawn overhead.

    Notes
    -----
    - The scheduler does **not** know Spell or DAG internals.
      It only coordinates UnitOfWork instances.
    - Phase strategies/factories are responsible for:
      * Inspecting the Spellbook.
      * Creating appropriately labelled UnitOfWork instances via
        :meth:`create_unit_of_work` so that all work items share the
        CURRENT RUN's CancellationEvent.

    THE WORKER-LOOP CONTRACT (everything depends on it):
        Every dequeued unit reports into its latch EXACTLY ONCE - no more, no
        fewer. The loop wraps execution in a defensive catch even though
        `run_for_scheduler()` is documented never to raise, because a unit that
        somehow escaped without reporting would leave the control thread
        blocked until the full barrier timeout to discover it. Reporting is the
        invariant; correctness of the unit is secondary to it.

        Cancellation reports as `complete()`, NOT `record_error()`. A cancelled
        unit is an expected outcome of an already-aborted run, so counting it as
        a failure would bury the ORIGINAL error under a pile of derived ones.

    QUIESCE BEFORE UNWINDING (fail-fast is not enough):
        The fail-fast wake returns while sibling unit BODIES may still be
        executing on pool workers. Raising immediately lets the caller's failure
        handler - for the restore lane, an all-or-nothing teardown - run
        concurrently with those stragglers, and a straggler can then register
        runtime state into a world that is being destroyed. So a failing phase
        calls `latch.wait_all_reported(...)` before raising.

        Bounded by the same barrier budget: a hung straggler times the quiesce
        out and the raise proceeds anyway.

    DOCUMENTED RESIDUAL - the scheduler never kills threads:
        There is no forced termination anywhere. Abort paths mark units via
        `set_exception` and rely on cooperative cancellation; a unit that
        ignores its cancel event and never returns will occupy a pool worker
        for the scheduler's lifetime. Bounded waits mean the CONTROL thread
        always makes progress, but a genuinely hung unit is a leaked worker,
        not a recovered one.

        Aborts deliberately use `set_exception` rather than `uow.cancel()`:
        workers still dequeue and invoke units, and the unit-side outcome
        writes are race-guarded, so cancelling the Future would fight the
        worker instead of informing it.

    THE POST-SCAN (why a phase checks twice):
        After a clean barrier, every unit is re-read for a stored exception.
        This catches units handed to the scheduler ALREADY DONE with a
        pre-recorded failure - the worker skips done units, so the latch never
        sees them. All units are finished at that point, so the reads never
        block.

    Owned State:
        - Persistent worker pool, spawned lazily on first run and reused for
          the scheduler's whole lifetime. Spawn/join cost moves to owner
          teardown rather than being paid per conjure.
        - One queue feeding every worker; workers block on it and exit only on
          an explicit sentinel.
        - A per-run `CancellationEventSignal`, replaced at each
          `run_all_phases(...)`, so one run's failure can never poison a later
          run on the same pool.
        - Phase registrations, cleared after each run.

    Registration:
        MELDER KERNEL - guarded. The scheduler is runtime machinery constructed
        by its owner (a Spellbook, or the restore lane through the
        explicit-value constructor).

    Subsystem Context:
        The orchestrator of the phase family in `utilities/synchronization/`.
        The full chain per unit: this enqueues `(UnitOfWork, PhaseLatch)` -> a
        worker dequeues and calls `run_for_scheduler()` -> that returns a
        failure or None -> the worker calls `latch.record_error(...)` or
        `latch.complete()` -> the latch fires -> this wakes, and on failure
        quiesces before raising. `CancellationEventSignal` is the fifth
        participant, checked by each unit before it runs.

    System Context:
        Every conjure runs phases 1-4 (structural), 5-7 (foundational
        resolution), and 8-11 (plan resolution) through one of these, and the
        crystallizer restore lane drives its own via the explicit-value
        constructor. A `PhaseExecutionError` or `PhaseTimeoutError` here is what
        the Spellbook surfaces to a user as a failed conjure - which is why the
        quiesce matters: without it, a failed conjure could tear down a world
        while units are still writing into it.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Persistent multi-phase runner. register_phase() in order, then
        run_all_phases(): each phase is a barrier, units run on a reused worker pool, a unit
        failure wakes the barrier immediately, and the phase QUIESCES before raising so caller
        teardown never races in-flight stragglers. Never kills threads - cancellation is
        cooperative, so a unit that ignores its cancel event leaks a worker.
    """
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
            worker_count: Optional[int] = None,
            barrier_timeout_ms: Optional[int] = None,
    ) -> None:
        """
        Initialize a new PhaseScheduler.

        Contract:
            Two construction lanes, both keyword-only:
            - Configuration lane (spellbook owners, unchanged behavior):
              omit the explicit values; worker count and barrier timeout
              are read from the SpellbookConfiguration keys exactly as
              before.
            - Explicit lane (world-scope owners, e.g. the crystallizer
              restore lane - parallel_restore_ulid_identity S2): supply
              BOTH `worker_count` and `barrier_timeout_ms`; the
              configuration readers are skipped and `configuration` may be
              None. Execution semantics (pool, queue, latch barriers,
              cancellation) are identical across lanes.

        Args:
            spellbook:
                The owning instance. Used for context only; this scheduler
                never mutates its owner. May be None for world-scope
                owners constructing through the explicit lane.
            configuration:
                The active SpellbookConfiguration. Required (non-None)
                when either explicit value is omitted; ignored for a value
                that was supplied explicitly.
            worker_count:
                Optional explicit worker-thread count. Must be a positive
                int (bools rejected) when supplied.
            barrier_timeout_ms:
                Optional explicit per-phase barrier timeout in
                milliseconds. Must be a positive int (bools rejected)
                when supplied.

        Raises:
            ValueError:
                If an explicit value is invalid, or a value is omitted and
                `configuration` is None or unreadable.

        Returns:
            None.
        """
        Cleanable.__init__(self)
        self._configuration: Optional[SpellbookConfiguration] = configuration
        if worker_count is None or barrier_timeout_ms is None:
            if configuration is None:
                raise ValueError(
                    "PhaseScheduler requires a configuration when "
                    "worker_count/barrier_timeout_ms are not both supplied "
                    "explicitly. Fix: pass the owning "
                    "SpellbookConfiguration, or supply both explicit "
                    "values (e.g. PhaseScheduler(spellbook=None, "
                    "configuration=None, worker_count=4, "
                    "barrier_timeout_ms=60000))."
                )
        self._workers: int = (
            self._require_positive_override("worker_count", worker_count)
            if worker_count is not None
            else self._get_worker_count(configuration)
        )
        self._barrier_timeout_ms: int = (
            self._require_positive_override(
                "barrier_timeout_ms", barrier_timeout_ms
            )
            if barrier_timeout_ms is not None
            else self._get_timeout_ms(configuration)
        )

        # Per-run cancellation scope. A fresh signal is installed at the top
        # of every run_all_phases() call; between runs these hold the most
        # recent run's (tripped or untripped) scope so `cancel()` and
        # `is_cancelled` stay meaningful to external observers.
        self._cancel_signal: CancellationEventSignal = CancellationEventSignal()
        self._cancel_event: CancellationEvent = self._cancel_signal.event

        # Shared work queue: workers block on get() and exit on sentinel.
        self._queue: SimpleQueue[Any] = SimpleQueue()
        self._threads: List[threading.Thread] = []
        self._workers_started: bool = False
        self._shutdown: bool = False

        self._lock: threading.RLock = threading.RLock()

        # Per-run phase registry (consumed and cleared by run_all_phases).
        self._phase_factories: Dict[str, Callable[[], Sequence[UnitOfWork]]] = {}
        self._phase_order: List[str] = []

        # Unique sentinel object to signal worker shutdown
        self._sentinel: object = object()

    @staticmethod
    def _require_positive_override(name: str, value: int) -> int:
        """
        Validate one explicit construction override.

        Contract:
            Mirrors the configuration readers' strictness: ints only
            (bools rejected), strictly positive.

        Args:
            name:
                Override parameter name (for the error message).
            value:
                Candidate override value.

        Returns:
            int: The validated value, unchanged.

        Raises:
            ValueError:
                If the value is a bool, not an int, or not positive.
        """
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(
                "PhaseScheduler explicit override '{0}' must be a positive "
                "int (got {1!r}).".format(name, value)
            )
        return value

    def _get_worker_count(self, configuration: SpellbookConfiguration) -> int:
        """
        Read scheduler worker count from configuration.

        Returns:
            int: Configured workers-per-spellbook value.

        Raises:
            ValueError: If the configuration property cannot be read.
        """
        # Worker count
        try:
            worker_count = configuration.get_property(
                "phase_scheduler_workers_per_spellbook"
            )
            if not isinstance(worker_count, int) or isinstance(worker_count, bool):
                raise TypeError(
                    "phase_scheduler_workers_per_spellbook must be an int."
                )
            return worker_count
        except Exception:
            raise ValueError(
                "Failed to read phase_scheduler_workers_per_spellbook from configuration."
            )

    def _get_timeout_ms(self, configuration: SpellbookConfiguration) -> int:
        """
        Read the per-phase barrier timeout from the configuration.

        Returns:
            int: Barrier timeout in milliseconds.

        Raises:
            ValueError: If the configuration property cannot be read.
        """
        try:
            timeout_ms = configuration.get_property(
                "phase_scheduler_barrier_timeout_milliseconds"
            )
            if not isinstance(timeout_ms, int) or isinstance(timeout_ms, bool):
                raise TypeError(
                    "phase_scheduler_barrier_timeout_milliseconds must be an int."
                )
            return timeout_ms
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

        Behaviour:
            - Idempotent.
            - Signals cancellation for the current run scope.
            - Sends a sentinel to each worker thread and lets them exit.
            - Joins worker threads (bounded), then nulls owned references.
            - Marks the scheduler as cleaned; further use is illegal.

        Ordering:
            This is the ONLY place pool threads are joined. Owners (the
            Spellbook) call this once at their own teardown, which is where
            per-conjure thread churn moved in the persistent-pool design.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True
            self._shutdown = True

            # Trip the current run scope so in-flight units fast-return.
            self._cancel_signal.cancel()

            # Send a sentinel to each worker if they've been started and the queue exists.
            if self._workers_started and self._queue is not None:
                for _ in range(self._workers):
                    self._queue.put(self._sentinel)

            # Join threads.
            for thread in self._threads:
                try:
                    thread.join(timeout=5.0)
                except Exception:
                    # Ignore join failures during teardown.
                    pass

            # Clean up the queue itself if present.
            if self._queue is not None:
                for _ in range(self._queue.qsize()):
                    try:
                        self._queue.get_nowait()
                    except Exception:
                        break

            if self._threads is not None:
                self._threads.clear()
            if self._phase_factories is not None:
                self._phase_factories.clear()
            if self._phase_order is not None:
                self._phase_order.clear()

            del self._threads
            del self._phase_factories
            del self._phase_order
            del self._configuration
            del self._queue
        # Drop lock last.
        del self._lock

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def cancel_event(self) -> CancellationEvent:
        """
        CancellationEvent for the CURRENT run scope.

        Phase factories should NOT construct their own events; instead they
        should call :meth:`create_unit_of_work` so this event is wired in
        automatically. Factories execute inside `run_all_phases(...)`, so
        they always observe the active run's event.

        Returns:
            CancellationEvent: Cooperative-cancellation view for the current
            (or most recent) run scope.
        """
        return self._cancel_event

    @property
    def is_cancelled(self) -> bool:
        """
        Return whether the current run scope has been cancelled.

        Contract:
            - Reflects the CURRENT (or most recent) run's signal; a fresh scope
              is installed per `run_all_phases(...)`, so this resets each run.

        Returns:
            bool: True when this run's cancellation signal has been tripped.
        """
        return self._cancel_signal.is_set

    @property
    def workers(self) -> int:
        """
        Return the configured worker-thread count for this scheduler instance.

        Returns:
            int: Fixed pool size resolved at construction (config or explicit
            override); the pool is spawned once and reused for the lifetime.
        """
        return self._workers

    @property
    def barrier_timeout_ms(self) -> int:
        """
        Return a configured per-phase barrier timeout in milliseconds.

        Returns:
            int: Fixed per-phase barrier budget in ms (config or explicit
            override); bounds both the phase wait and the fail-fast quiesce.
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
        the CURRENT run's CancellationEvent.

        Phase factories should prefer this instead of constructing UnitOfWork
        directly so that:

            - All work items participate in run-scoped cooperative
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
            UnitOfWork: A newly constructed UnitOfWork bound to the current
            run's CancellationEvent.

        Raises:
            RuntimeError:
                If the scheduler has been cleaned.
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

    def worker_thread_idents(self) -> List[int]:
        """
        Return the pool's worker thread identities, starting the pool if
        needed.

        Purpose:
            Cohort enrollment surface (parallel_restore_ulid_identity S4):
            a load-span holder needs the worker idents to enroll them into
            the LoadGate cohort BEFORE registering restore phases, and
            idents only exist once the persistent pool has started.

        Contract:
            - Starts the worker pool on first call (idempotent; the pool
              is persistent and started at most once per scheduler life).
            - Returns a DETACHED sorted list; mutating it never touches
              scheduler state.
            - Stable across calls for the scheduler's lifetime (workers
              exit only at cleanup).

        Returns:
            List[int]: Sorted worker thread identities.

        Raises:
            RuntimeError:
                If the scheduler has been cleaned.
        """
        self.check_cleaned()
        self._start_workers_if_needed()
        with self._lock:
            return sorted(
                thread.ident
                for thread in self._threads
                if thread.ident is not None
            )

    def register_phase(self, name: str, factory: Callable[[], Sequence[UnitOfWork]]) -> None:
        """
        Register a phase for the NEXT run.

        Phases execute in the order they are registered. Registrations are
        per-run state: `run_all_phases(...)` consumes and clears them, and
        callers that abort between registration and run must call
        :meth:`clear_phases` so stale registrations cannot leak into a
        later run on this persistent scheduler.

        Args:
            name:
                Logical phase name (e.g. "scan_spells", "build_graphs").
            factory:
                Callable[[] -> Sequence[UnitOfWork]] that, when invoked, builds
                all UnitsOfWork for this phase. Factories should use
                :meth:`create_unit_of_work` to ensure each unit is bound to
                the current run's CancellationEvent.

        Raises:
            RuntimeError: If the scheduler has been cleaned.
            ValueError: If the name is empty or already registered.
            TypeError: If `factory` is not callable.

        Returns:
            None.
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

    def clear_phases(self) -> None:
        """
        Clear all per-run phase registrations.

        Contract:
            - Idempotent; safe when no phases are registered.
            - Called automatically at the end of `run_all_phases(...)`;
              exposed for callers whose registration step fails before the
              run starts, so a persistent scheduler never carries stale
              registrations into the next run.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            self._phase_factories.clear()
            self._phase_order.clear()

    # ------------------------------------------------------------------
    # Worker pool
    # ------------------------------------------------------------------

    def _start_workers_if_needed(self) -> None:
        """
        Start the worker pool once and only once for the scheduler lifetime.

        Contract:
            - Returns immediately when workers are already running.
            - Creates exactly "self._workers" daemon threads on the first
              start; the pool is then reused by every later run.
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

        Blocks on the shared queue for `(unit, latch)` work items and
        executes them until the shutdown sentinel arrives.

        Contract:
            - Fully blocking dequeue: idle workers consume zero CPU (no
              polling); shutdown is sentinel-only.
            - Workers are run-agnostic: they never read scheduler-level
              cancellation state. Cancellation is observed per unit through
              the unit's own captured run event, and abandoned-run items
              report into their own (abandoned) latch, which by construction
              cannot touch a newer run's barrier.
            - Every dequeued unit reports into its latch exactly once:
              success and cooperative cancellation report `complete()`;
              failures report `record_error(...)` (fail-fast wake).
            - Workers never die from unit exceptions; the latch carries the
              failure to the control thread.
        """
        queue_get = self._queue.get
        sentinel = self._sentinel
        while True:
            item = queue_get()
            if item is sentinel:
                break

            uow, latch = item
            try:
                failure = uow.run_for_scheduler()
            except BaseException as exc:
                # Defensive boundary: run_for_scheduler() itself should not
                # raise (it records outcomes), but the latch must always make
                # progress or the control thread would have to wait for the
                # full barrier timeout to discover the problem.
                failure = exc
            if failure is None or isinstance(failure, OperationCancelledError):
                # Cooperative cancellation is an expected non-error outcome:
                # it only happens after the run was already aborted (the
                # control thread has the original failure) or pre-cancelled.
                latch.complete()
            else:
                latch.record_error(failure)

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
            2. Enqueue all units (each paired with this phase's latch).
            3. Wait on the latch: all-done, first-error, or timeout.
            4. On first-error: cancel the run, quiesce in-flight stragglers
               (bounded by the barrier budget), then aggregate exceptions
               and raise PhaseExecutionError.

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
            PhaseSchedulerError: If the run was cancelled before/with no unit
                error of its own.
        """
        if self._cancel_signal.is_set:
            # Upstream failure or explicit cancel - short-circuit this phase.
            raise PhaseSchedulerError(
                f"Phase '{phase_name}' skipped because cancellation has already been signalled."
            )

        # Build the work for this phase.
        units: Sequence[UnitOfWork] = factory()

        # No work = trivial barrier.
        if not units:
            return units

        # NOTE: units always execute on worker threads, even with one worker.
        # An inline workers==1 fast path was tried and reverted: synchronous
        # execution in the caller thread cannot honor the scheduler's async
        # control contract. A unit blocked on an external signal deadlocks
        # the caller (external cancel can never be observed), and preemptive
        # barrier timeouts (PhaseTimeoutError while a unit is still running)
        # are impossible without a separate execution thread. The persistent
        # pool IS the sanctioned single-worker-overhead answer.

        # Make sure workers are up (first run only).
        self._start_workers_if_needed()

        # One latch per phase: the only barrier synchronization object.
        latch = PhaseLatch(len(units))
        queue_put = self._queue.put
        for uow in units:
            queue_put((uow, latch))

        timeout_sec = self._barrier_timeout_ms / 1000.0

        # One event wait:
        # - wakes early on first unit error (fail-fast)
        # - otherwise wakes when all units complete
        # - or returns False at timeout
        finished = latch.wait(timeout_sec)
        errors = latch.errors

        if errors:
            # Cancel the rest of this run; stragglers of this phase observe
            # the cancel event at their pre-run check and report cancelled.
            self._cancel_signal.cancel()

            # Best-effort: mark unfinished units as cancelled so nothing is left "pending forever".
            # IMPORTANT: do NOT call uow.cancel() here because workers still dequeue and call the unit;
            # the unit-side outcome writes are race-guarded.
            for uow in units:
                if not uow.done():
                    try:
                        uow.set_exception(
                            OperationCancelledError(
                                f"Phase '{phase_name}' aborted due to an earlier failure."
                            )
                        )
                    except Exception:
                        # Ignore races with workers completing the unit.
                        pass

            # QUIESCE before unwinding (parallel_restore lane, 2026-07-19):
            # the fail-fast wake fires while sibling unit BODIES may still
            # be executing on pool workers, and raising immediately lets a
            # caller's failure handler (the restore engine's all-or-nothing
            # teardown) run concurrently with those stragglers - a straggler
            # can then register runtime state mid-teardown (the cleaned-husk
            # frame leak on the owner's red run). Every dequeued unit
            # reports into its latch exactly once (worker-loop contract) and
            # already-done units no-op to complete(), so the all-reported
            # barrier terminates. Bounded by the same barrier budget: a hung
            # straggler times the quiesce out and the raise proceeds (the
            # scheduler never kills threads; documented residual).
            latch.wait_all_reported(timeout_sec)

            raise PhaseExecutionError(phase_name, errors)

        # If cancelled externally (no unit error yet), treat as cancellation.
        if self._cancel_signal.is_set:
            raise PhaseSchedulerError(
                f"Phase '{phase_name}' cancelled during execution."
            )

        # Timeout: no exception, but not all units finished.
        if not finished:
            self._cancel_signal.cancel()

            for uow in units:
                if not uow.done():
                    try:
                        uow.set_exception(
                            OperationCancelledError(
                                f"Phase '{phase_name}' timed out after {self._barrier_timeout_ms}ms."
                            )
                        )
                    except Exception:
                        pass

            raise PhaseTimeoutError(phase_name, self._barrier_timeout_ms)

        # Contract-preserving post-scan: the historical barrier collected
        # stored exceptions from DONE futures, which covers units handed to
        # the scheduler with a pre-recorded failure (the worker skips
        # already-done units, so the latch never sees such errors). All
        # units are done here, so these are non-blocking reads.
        stored_errors: List[BaseException] = []
        for uow in units:
            exc = uow.exception()
            if exc is not None:
                stored_errors.append(exc)
        if stored_errors:
            self._cancel_signal.cancel()
            raise PhaseExecutionError(phase_name, stored_errors)

        return units


    # ------------------------------------------------------------------
    # Public run API
    # ------------------------------------------------------------------

    def run_all_phases(self, conduit_id: Optional[str] = None) -> Dict[str, Sequence[UnitOfWork]]:
        """
        Execute all registered phases in the registration order as one run.

        Run semantics (persistent scheduler):
            - A fresh CancellationEventSignal is installed at the start, so
              this run's cancellation scope is isolated from every previous
              run on the same pool.
            - Phase registrations are consumed by this call and cleared in
              all outcomes (success, failure, timeout), leaving the
              scheduler immediately reusable.

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

        # Fresh per-run cancellation scope: one run's abort can never poison
        # the next run on this persistent pool.
        self._cancel_signal = CancellationEventSignal()
        self._cancel_event = self._cancel_signal.event

        # Snapshot the phase order for a stable run view.
        phase_names = list(self._phase_order)

        if not phase_names:
            return {}

        results: Dict[str, Sequence[UnitOfWork]] = {}

        try:
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
        finally:
            # Registrations are per-run state on a persistent scheduler.
            self.clear_phases()

        return results

    def cancel(self) -> None:
        """
        Explicitly signal cancellation for the current run scope.

        This is idempotent and can be called from any thread. It does not
        join workers or clean the scheduler; it only trips the current run's
        cancellation signal. Workers themselves are unaffected (they exit on
        sentinel only); in-flight units observe the event cooperatively.

        Returns:
            None.
        """
        self._cancel_signal.cancel()
