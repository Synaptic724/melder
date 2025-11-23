import threading
# Melder Imports
from melder.utilities.custom_exceptions.operation_cancelled_error import OperationCancelledError


class CancellationEvent:
    """
    Lightweight, read-only view over a shared cancellation signal.

    This object is **read-optimized**:

    * Checking cancellation (`is_set`) does **not** acquire any Python-level
      locks and simply delegates to the underlying :class:`threading.Event`.
    * Multiple threads are free to poll the event as often as they like
      without contending on a shared lock.

    Instances are produced by :class:`CancellationEventSignal` and should be
    passed into worker components (e.g. resolution planners, DAG builders,
    validation routines) that need to cooperatively honour cancellation.

    Typical usage
    -------------

        signal = CancellationEventSignal()
        cancel_event = signal.event

        def worker():
            if cancel_event.is_set:
                return  # or raise OperationCancelledError(...)
            ...do work...

        # Somewhere else (coordinator / supervisor):
        signal.cancel()  # all observers see the cancellation almost instantly
    """

    __slots__ = ("_flag",)

    def __init__(self, flag: threading.Event) -> None:
        """
        Internal constructor.

        Users should obtain instances from
        :meth:`CancellationEventSignal.event` instead of creating events
        directly.

        Args:
            flag:
                The shared :class:`threading.Event` that represents the
                underlying cancellation signal.
        """
        self._flag = flag

    @property
    def is_set(self) -> bool:
        """
        Return True if cancellation has been signalled.

        This is a **lock-free read** with respect to user code: it simply
        calls :meth:`threading.Event.is_set` on the underlying event.

        Returns:
            bool: True if a call to :meth:`CancellationEventSignal.cancel`
            has occurred; False otherwise.
        """
        return self._flag.is_set()

    def throw_if_set(self) -> None:
        """
        Convenience helper for cooperative cancellation.

        Raises:
            OperationCancelledError: If cancellation has been signalled.
        """
        if self._flag.is_set():
            raise OperationCancelledError(
                "Operation cancelled via CancellationEvent signal."
            )


class CancellationEventSignal:
    """
    Mutable source of cancellation events.

    This object owns the underlying :class:`threading.Event` and can be used
    to:

        * Produce a :class:`CancellationEvent` view for consumers.
        * Trigger cancellation exactly once via :meth:`cancel`.

    Design notes
    ------------

    * Write path (cancel) is a single `event.set()` call – thread-safe and
      cheap.
    * Read path (via :class:`CancellationEvent`) does **not** use any
      additional locks beyond what :class:`threading.Event` already does
      internally.
    * Intended usage is one signal shared across many worker threads in a
      burst-style pipeline (e.g. staged resolution compilation).
    """

    __slots__ = ("_flag", "_event")

    def __init__(self) -> None:
        self._flag = threading.Event()
        # Pre-create a single event view; all consumers share it.
        self._event = CancellationEvent(self._flag)

    @property
    def event(self) -> CancellationEvent:
        """
        Return the read-only :class:`CancellationEvent` associated with this
        signal.

        All callers receive the **same** event instance; this is intentional
        so that everyone observes the same cancellation signal.
        """
        return self._event

    def cancel(self) -> None:
        """
        Signal cancellation for all observers of this source.

        This method is idempotent: calling it multiple times has no additional
        effect beyond the first call.

        Typical usage in a parallel resolution pipeline:

            signal = CancellationEventSignal()
            cancel_event = signal.event

            # Worker threads poll cancel_event.is_set periodically.
            # Coordinator decides to abort after N failures:
            signal.cancel()
        """
        self._flag.set()

    @property
    def is_set(self) -> bool:
        """
        Convenience passthrough to the underlying event's cancellation state.

        Returns:
            bool: True if cancellation has been signalled.
        """
        return self._flag.is_set()
