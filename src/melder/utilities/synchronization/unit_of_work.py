import threading
from concurrent.futures import Future, InvalidStateError
from typing import Any, Callable, Dict, Literal, Optional, Tuple, ClassVar
from types import TracebackType
# Melder imports
from melder.utilities.custom_exceptions.operation_cancelled_error import OperationCancelledError
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg




class UnitOfWork(Cleanable, Future):
    """
    Future-based encapsulation of a single unit of work, with integrated
    cancellation support via: class:`CancellationEvent` and explicit cleanup.

    This class extends both:

        *: class: 'Cleanable` – deterministic, idempotent cleanup semantics.
        *: class:`concurrent.futures.Future` – result(), exception(), callbacks, etc.

    It **does not** own threads or an executor:

        * You construct a UnitOfWork with a callable + args + optional cancel event.
        * You then either:
            - Call: meth:`run_synchronously` on whatever thread should do the work, or
            - Treat the instance itself as a callable (``threading.Thread(target=uow)``),
              or
            - Use it inside your own worker loop / pipeline.

        * The UnitOfWork:
            - Performs an up-front check of its associated: class:`CancellationEvent`
              (if provided).
            - Executes the callable.
            - Records `set_result` or `set_exception` on the underlying Future.

    Thread-safety and coordination
    ----------------------------

    * A per-instance: class:`threading.RLock` (_lock) protects access to internal
      state that can be cleaned or mutated.
    * Most public operations call: meth:`check_cleaned` to enforce lifecycle rules.
    * "with UnitOfWork(...) as uow:" acquires the internal lock for the caller,
      allowing you to safely read/update metadata or coordinate multistep actions.

    Cleanup semantics
    -----------------

    *: meth: 'cleanup` is idempotent.
    * Once cleaned:
        - All internal references (func, args, kwargs, cancel_event, metadata) are
          nulled out.
        - The internal lock is set to None.
        - Subsequent guarded operations will fail via: meth:`check_cleaned` or by
          detecting that the lock is None.

    Responsibilities:
        - Bind one callable with its args, kwargs, and optional cancellation view.
        - Execute it exactly once, recording the outcome on the Future surface.
        - Check cooperative cancellation BEFORE invoking the callable.
        - Carry a label and metadata for supervision and telemetry.

    TWO EXECUTION LANES - pick by caller, they differ on exceptions:

        `run_synchronously()` - the GENERAL lane.
            Takes `_lock`, guards on cleaned state, and RE-RAISES whatever the
            callable raised after recording it. Use it when a human-shaped
            caller wants normal exception flow. Also reachable as `uow()`, so
            the instance can be a plain thread target.

        `run_for_scheduler()` - the HOT lane, for `PhaseScheduler` workers.
            LOCK-FREE and NEVER RAISES. It RETURNS the failure instead, so the
            worker can hand it straight to `PhaseLatch.record_error(...)`
            without a try/except around every dispatch. Returns None on success
            OR when the control thread already decided the outcome.

        The lock-free reads in the hot lane are justified by THREAD CONFINEMENT,
        not by luck: a scheduler unit is built on the control thread, handed to
        exactly one worker through the queue (that hand-off is the
        synchronization point), executed once, and inspected only after the
        phase barrier. No second thread touches `_func`/`_args`/`_kwargs`/
        `_cancel_event` while it runs, and scheduler units are never cleaned
        mid-run.

    OUTCOME RACES ARE EXPECTED AND HAVE A DEFINED WINNER:
        The control thread can abort a phase (timeout or fail-fast) by writing
        `set_exception(...)` on units that are still running. When a worker then
        tries to record its own outcome it gets `InvalidStateError`. Every such
        site swallows it deliberately: THE CONTROL THREAD'S OUTCOME WINS. A unit
        that lost the race still returns cleanly so the latch keeps progressing.

    Owned State:
        - `_func` / `_args` / `_kwargs`: the bound call.
        - `_cancel_event`: borrowed `CancellationEvent` view, or None.
        - `_label` / `_metadata`: supervision payload, never interpreted here.
        - `_lock`: guards THIS object's fields. Distinct from the lock `Future`
          keeps internally for result state - they are not the same lock and do
          not protect each other.

    Threading:
        - The context-manager form (`with uow:`) acquires the INSTANCE lock so a
          caller can read or adjust metadata atomically. It has nothing to do
          with execution and does not serialize the callable.
        - `run_synchronously()` holds the instance lock for the whole call,
          including the user callable. Do not use that lane for long work you
          also want to inspect concurrently.
        - `run_for_scheduler()` takes no lock at all.

    Lifecycle / Cleanup:
        - Idempotent, double-checked, releases every owned slot under normal del
          posture with `_lock` dropped last.
        - IMPORTANT: cleanup deliberately does NOT touch the underlying Future's
          result or exception state. Anything awaiting this unit can still
          observe the outcome after the unit itself has been torn down. The
          bound call is released; the answer is not.

    Registration:
        MELDER KERNEL - guarded. The scheduler constructs units; a user has no
        reason to register one as a spell.

    Subsystem Context:
        The work half of the phase machinery in `utilities/synchronization/`.
        `PhaseScheduler` owns the pool and phase ordering, `PhaseLatch` owns the
        barrier, and this owns one runnable item. The chain per unit is:
        scheduler dequeues -> `run_for_scheduler()` -> returns failure or None ->
        worker calls `latch.record_error(...)` or `latch.complete()`.
        `CancellationEvent` is the fourth participant, checked before the call.

    System Context:
        Every conjure runs phases 1-4, 5-7, and 8-11 through the scheduler, and
        each spell's per-phase work is one of these. That is why the hot lane
        never raises: a raising unit would unwind a pool worker instead of
        reporting into its latch, and the phase barrier would then wait out a
        unit that is already dead.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. One runnable unit bound to a callable, exposed as a "
        "Future. Two lanes: run_synchronously() locks and re-raises for normal "
        "callers; run_for_scheduler() is lock-free, never raises, and RETURNS "
        "the failure so a PhaseScheduler worker can report it into its "
        "PhaseLatch. Cleanup releases the bound call but preserves the outcome."
    )
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_func",
        "_args",
        "_kwargs",
        "_cancel_event",
        "_label",
        "_metadata",
        "_lock",
    ]

    def __init__(
            self: "UnitOfWork",
            func: Callable[..., Any],
            *,
            args: Optional[Tuple[Any, ...]] = None,
            kwargs: Optional[Dict[str, Any]] = None,
            cancel_event: Optional[CancellationEvent] = None,
            label: Optional[str] = None,
            metadata: Any = None,
    ) -> None:
        """
        Create a new UnitOfWork.

        Args:
            func:
                The callable to execute. This may be a free function or a
                bound method (e.g. a ResolutionCompiler method).
            args:
                Optional positional arguments to pass to "func" when
                executing. Defaults to an empty tuple.
            kwargs:
                Optional keyword arguments to pass to "func" when executing.
                Defaults to an empty dict.
            cancel_event:
                Optional :class:`CancellationEvent`. If provided, the event is
                checked for cancellation *before* invoking "func".
            label:
                Optional human-readable label used for debugging / logging /
                telemetry (e.g. "scan:spell-01H...", "dag:spell-01K...").
            metadata:
                Optional arbitrary metadata describing this unit of work
                (spell ID, stage name, ResolutionContext, etc.).

        Returns:
            None.
        """
        # Explicitly init both bases – we don't rely on cooperative supper().
        Future.__init__(self)
        Cleanable.__init__(self)

        if not callable(func):
            raise TypeError("func must be callable.")

        self._func: Callable[..., Any] = func
        self._args: Tuple[Any, ...] = args if args is not None else ()
        self._kwargs: Dict[str, Any] = kwargs if kwargs is not None else {}
        self._cancel_event: Optional[CancellationEvent] = cancel_event
        self._label: Optional[str] = label
        self._metadata: Any = metadata

        # Internal synchronization for our own state (separate from Future's lock).
        self._lock: threading.RLock = threading.RLock()



    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this UnitOfWork, clearing references and
        disabling further use.

        Behaviour:
            * Idempotent – safe to call multiple times.
            * Clears:
                - The wrapped callable and its bound args/kwargs.
                - The associated CancellationEvent.
                - Any label/metadata.
            * Marks the object as cleaned and drops the internal lock.

        After cleanup:
            *: meth:`check_cleaned` will cause most operations to raise
              "RuntimeError("UnitOfWork has been cleaned.")".
            * The underlying Future's internal state (result/exception) is left
              as-is so any awaiting code can still observe the outcome.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True

            # Null out references for GC friendliness.
            del self._func
            del self._args
            del self._kwargs
            del self._cancel_event
            del self._label
            del self._metadata
        # Drop the lock reference last.
        del self._lock

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "UnitOfWork":
        """
        Enter a critical section protected by this UnitOfWork's internal lock.

        This lets callers coordinate multiple operations under a single
        lock acquisition, for example:

            with uow:
                # inspect / tweak metadata atomically
                info = uow.metadata
                ...

        Note:
            This lock is **only** for UnitOfWork's own fields
            (func/args/kwargs/metadata/cancel_event), not the internal
            lock used by: class: 'Future`.

        Returns:
            UnitOfWork: This unit after the internal coordination lock has been
            acquired.
        """
        self._lock.acquire()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Literal[False]:
        """
        Exit the critical section entered via: meth:`__enter__`.

        The internal lock is always released, and exceptions from the with-body
        are not suppressed.
        """
        self._lock.release()
        return False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def cancel_event(self) -> Optional[CancellationEvent]:
        """
        The: class:`CancellationEvent` associated with this unit of work, if
        any.

        Worker code or the underlying callable may use this to perform
        additional cooperative cancellation checks beyond the up-front check
        done in: meth:`run_synchronously`.

        Returns:
            Optional[CancellationEvent]: Shared cancellation view for this unit,
            or None when no cooperative cancellation source was attached.
        """
        self.check_cleaned()
        with self._lock:
            return self._cancel_event

    @property
    def label(self) -> Optional[str]:
        """
        Optional human-readable label for this UnitOfWork.

        This is useful for logging, debugging, or exposing information to AI
        agents (e.g. tagging a unit with spell IDs and stage names).

        Returns:
            Optional[str]: Human-readable label associated with this unit.
        """
        self.check_cleaned()
        with self._lock:
            return self._label

    @property
    def metadata(self) -> Any:
        """
        Arbitrary metadata attached to this unit of work.

        This can be used to attach spell identifiers, ResolutionContext
        instances, stage markers, or any other information a supervising
        pipeline wants to keep track of.

        Returns:
            Any: Arbitrary caller-supplied metadata stored on this unit.
        """
        self.check_cleaned()
        with self._lock:
            return self._metadata

    # ------------------------------------------------------------------
    # Execution (caller-controlled scheduling)
    # ------------------------------------------------------------------

    def run_synchronously(self) -> Any:
        """
        Execute the unit of work on the **current** thread.

        This is the core execution path that:

            * Ensures the UnitOfWork has not been cleaned.
            * Performs an up-front cancellation check using the associated: class:`CancellationEvent`, if any.
            * Invokes the underlying callable with its bound args/kwargs.
            * Records the result or exception on the underlying Future.

        It can be used directly:

            result = uow.run_synchronously()

        Or indirectly bypassing the UnitOfWork instance itself as a callable:

            thread = threading.Thread(target=uow)
            thread.start()

        Returns:
            Any: The result of the underlying callable.

        Raises:
            OperationCancelledError:
                If cancellation was requested via the associated: class:`CancellationEvent` prior to execution.
            Exception:
                Any exception raised by the underlying callable. It will also
                be recorded in the underlying Future and re-raised here.
        """
        self.check_cleaned()
        with self._lock:
            # If someone else already executed us, surface the stored outcome.
            if self.done():
                return self.result()

            # Cancellation check BEFORE running the work.
            if self._cancel_event is not None and self._cancel_event.is_set:
                exc = OperationCancelledError(
                    f"UnitOfWork{f'[{self._label}]' if self._label else ''} "
                    f"aborted before start due to cancellation."
                )
                self.set_exception(exc)
                raise exc

            try:
                result = self._func(*self._args, **self._kwargs)
            except BaseException as exc:
                self.set_exception(exc)
                raise
            else:
                self.set_result(result)
                return result


    def __call__(self) -> Any:
        """
        Convenience alias that executes this unit of work synchronously on
        the caller's thread.

        This is equivalent to: meth:`run_synchronously`. It is mainly
        provided so that UnitOfWork instances can be passed to APIs that
        expect a plain callable (e.g. ad-hoc thread targets or custom
        worker loops).

        Returns:
            Any: Result of the wrapped callable, exactly as returned by: meth:`run_synchronously`.
        """
        return self.run_synchronously()

    def run_for_scheduler(self) -> Optional[BaseException]:
        """
        Execute this unit on a scheduler worker thread, lock-free.

        Purpose:
            Provide the PhaseScheduler hot-path execution lane without the
            per-instance `_lock` acquisition and without exception
            re-raising: outcomes are recorded on the Future surface and the
            failure (if any) is RETURNED so the worker can report it into
            the phase latch.

        Contract:
            - Thread confinement by construction justifies the lock-free
              read of `_func`/`_args`/`_kwargs`/`_cancel_event`: a scheduler
              unit is built by the control thread, handed to exactly one
              worker through the queue (the synchronization point), executed
              once, and inspected only after the phase barrier. No second
              thread touches these fields during execution, and scheduler
              units are never cleaned mid-run.
            - Outcome writes (`set_result` / `set_exception`) are
              race-guarded against the control thread's barrier-abort
              writes (timeout/fail-fast `set_exception`): losing that race
              is expected and the control thread's outcome wins.
            - Cooperative cancellation: when the captured run event is set
              before execution, the unit records and returns an
              `OperationCancelledError` without invoking the callable.
            - Never raises; always returns the failure or None.

        Returns:
            Optional[BaseException]:
                None on success (or when the outcome was already decided by
                the control thread); the recorded exception otherwise.
        """
        if self._cleaned or self.done():
            # Cleaned units cannot run; already-done units were decided by
            # the control thread's barrier abort. Either way: no-op success
            # so the latch still progresses.
            return None

        if self._cancel_event is not None and self._cancel_event.is_set:
            exc: BaseException = OperationCancelledError(
                f"UnitOfWork{f'[{self._label}]' if self._label else ''} "
                f"aborted before start due to cancellation."
            )
            try:
                self.set_exception(exc)
            except InvalidStateError:
                # Control thread already aborted this unit; its outcome wins.
                pass
            return exc

        try:
            result = self._func(*self._args, **self._kwargs)
        except BaseException as run_exc:
            try:
                self.set_exception(run_exc)
            except InvalidStateError:
                pass
            return run_exc
        try:
            self.set_result(result)
        except InvalidStateError:
            # Lost the race against a barrier abort; the abort outcome wins.
            pass
        return None
