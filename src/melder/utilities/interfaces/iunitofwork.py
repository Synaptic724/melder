from typing import Any, Callable, Optional, Protocol, Self, runtime_checkable
from types import TracebackType
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class IUnitOfWork(ICleanable, Protocol):
    """
    Future-based encapsulation of a single unit of work, with integrated
    cancellation support via :class:`CancellationEvent` and explicit cleanup.

    This class extends both:

        * :class:`Cleanable` - deterministic, idempotent cleanup semantics.
        * :class:`concurrent.futures.Future` - result(), exception(), callbacks, etc.

    It **does not** own threads or an executor:

        * You construct a UnitOfWork with a callable + args + optional cancel event.
        * You then either:
            - Call :meth:`run_synchronously` on whatever thread should do the work, or
            - Treat the instance itself as a callable (``threading.Thread(target=uow)``),
              or
            - Use it inside your own worker loop / pipeline.

        * The UnitOfWork:
            - Performs an up-front check of its associated :class:`CancellationEvent`
              (if provided).
            - Executes the callable.
            - Records `set_result` or `set_exception` on the underlying Future.

    Thread-safety & coordination
    ----------------------------

    * A per-instance :class:`threading.RLock` (_lock) protects access to internal
      state that can be cleaned or mutated.
    * Most public operations call :meth:`check_cleaned` to enforce lifecycle rules.
    * ``with UnitOfWork(...) as uow:`` acquires the internal lock for the caller,
      allowing you to safely read/update metadata or coordinate multi-step actions.

    Cleanup semantics
    -----------------

    * :meth:`cleanup` is idempotent.
    * Once cleaned:
        - All internal references (func, args, kwargs, cancel_event, metadata) are
          nulled out.
        - The internal lock is set to None.
        - Subsequent guarded operations will fail via :meth:`check_cleaned` or by
          detecting that the lock is None.
    """

    _label: Optional[str]
    _metadata: Any
    _cancel_event: Optional[CancellationEvent]

    def cleanup(self) -> None:
        """
        Deterministically tear down this UnitOfWork, clearing references and
        disabling further use.

        Behavior:
            * Idempotent - safe to call multiple times.
            * Clears:
                - The wrapped callable and its bound args/kwargs.
                - The associated CancellationEvent.
                - Any label/metadata.
            * Marks the object as cleaned and drops the internal lock.

        After cleanup:
            * :meth:`check_cleaned` will cause most operations to raise
              ``RuntimeError("UnitOfWork has been cleaned.")``.
            * The underlying Future's internal state (result/exception) is left
              as-is so any awaiting code can still observe the final outcome.
        """
        ...

    def __enter__(self) -> Self:
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
            lock used by :class:`Future`.

        Returns:
            Self: This unit after the coordination lock has been acquired.
        """
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """
        Exit the critical section entered via :meth:`__enter__`.

        The internal lock is always released and exceptions from the with-body
        are not suppressed.
        """
        ...

    @property
    def cancel_event(self) -> Optional[CancellationEvent]:
        """
        The :class:`CancellationEvent` associated with this unit of work, if
        any.

        Worker code or the underlying callable may use this to perform
        additional cooperative cancellation checks beyond the up-front check
        done in :meth:`run_synchronously`.

        Returns:
            Optional[CancellationEvent]:
                Shared cancellation view for this unit, or None when no
                cooperative cancellation source is attached.
        """
        ...

    @property
    def label(self) -> Optional[str]:
        """
        Optional human-readable label for this UnitOfWork.

        This is useful for logging, debugging, or exposing information to AI
        agents (e.g. tagging a unit with spell IDs and stage names).

        Returns:
            Optional[str]: Human-readable label associated with this unit.
        """
        ...

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
        ...

    def run_synchronously(self) -> Any:
        """
        Execute the unit of work on the **current** thread.

        This is the core execution path that:

            * Ensures the UnitOfWork has not been cleaned.
            * Performs an up-front cancellation check using the associated
              :class:`CancellationEvent`, if any.
            * Invokes the underlying callable with its bound args/kwargs.
            * Records the result or exception on the underlying Future.

        It can be used directly:

            result = uow.run_synchronously()

        Or indirectly by passing the UnitOfWork instance itself as a callable:

            thread = threading.Thread(target=uow)
            thread.start()

        Returns:
            Any: The result of the underlying callable.

        Raises:
            OperationCancelledError:
                If cancellation was requested via the associated
                :class:`CancellationEvent` prior to execution.
            Exception:
                Any exception raised by the underlying callable. It will also
                be recorded on the underlying Future and re-raised here.
        """
        ...

    def __call__(self) -> Any:
        """
        Convenience alias that executes this unit of work synchronously on
        the caller's thread.

        This is equivalent to :meth:`run_synchronously`. It is mainly
        provided so that UnitOfWork instances can be passed to APIs that
        expect a plain callable (e.g. ad-hoc thread targets or custom
        worker loops).

        Returns:
            Any: Result of the wrapped callable, exactly as returned by
            :meth:`run_synchronously`.
        """
        ...

    def result(self, timeout: Optional[float] = None) -> Any:
        """
        Return the completed result value, waiting up to `timeout` seconds if needed.
        """
        ...

    def exception(self, timeout: Optional[float] = None) -> BaseException | None:
        """
        Return the captured exception, waiting up to `timeout` seconds if needed.
        """
        ...

    def add_done_callback(self, fn: Callable[[Any], Any]) -> None:
        """
        Register one callback to run when this unit of work reaches a done state.

        Returns:
            None.
        """
        ...

    def done(self) -> bool:
        """
        Return whether this unit of work has reached a terminal Future state.
        """
        ...

    def cancelled(self) -> bool:
        """
        Return whether this unit of work completed in a cancelled state.
        """
        ...

