import threading
from concurrent.futures import Future
from typing import Any, Callable, Dict, Literal, Optional, Tuple, ClassVar
from types import TracebackType
# Melder imports
from melder.utilities.custom_exceptions.operation_cancelled_error import OperationCancelledError
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from mypy_extensions import mypyc_attr

@mypyc_attr(native_class=True)
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
    """
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
    __deletable__ = [
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
