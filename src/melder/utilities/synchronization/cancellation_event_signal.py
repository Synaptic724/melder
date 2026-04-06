import threading
# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.custom_exceptions.operation_cancelled_error import OperationCancelledError
from melder.utilities.general_base.cleanable import Cleanable


class CancellationEvent(Cleanable):
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

    __slots__ = Cleanable.__slots__ + ["_flag",]
    __melder_internal__ = _mrg.sentinel

    def __init__(self, flag: threading.Event) -> None:
        """
        Build a read-only cancellation view over one shared event object.

        Users should obtain instances from
        :meth:`CancellationEventSignal.event` instead of creating events
        directly.

        Args:
            flag:
                The shared :class:`threading.Event` that represents the
                underlying cancellation signal.

        Raises:
            ValueError: If `flag` is `None`.
        """
        Cleanable.__init__(self)
        if flag is None:
            raise ValueError("CancellationEvent requires a valid threading.Event")
        self._flag = flag

    # ------------------------------------------------------------
    # Cleanup — deterministic, idempotent, zero contamination
    # ------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this CancellationEvent.

        Behavior:
            * Idempotent via Cleanable._cleaned flag.
            * Drops the shared event reference owned by the parent signal.
            * After cleanup, any access raises RuntimeError.
        """
        if self._cleaned:
            return

        # No lock needed — this class is read-only and the flag is just a reference.
        self._flag = None
        self._cleaned = True

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
        self.check_cleaned()
        return self._flag.is_set()

    def throw_if_set(self) -> None:
        """
        Convenience helper for cooperative cancellation.

        Raises:
            OperationCancelledError: If cancellation has been signalled.
            RuntimeError: If this event view has already been cleaned.
        """
        self.check_cleaned()
        if self._flag.is_set():
            raise OperationCancelledError(
                "Operation cancelled via CancellationEvent signal."
            )


class CancellationEventSignal(Cleanable):
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

    __slots__ = Cleanable.__slots__ + ["_flag", "_event"]
    __melder_internal__ = _mrg.sentinel

    def __init__(self) -> None:
        """
        Create a cancellation signal and pre-build its shared event view.

        Contract:
            - Owns one mutable :class:`threading.Event`.
            - Owns one reusable :class:`CancellationEvent` wrapper that all
              consumers share.
        """
        Cleanable.__init__(self)
        self._flag = threading.Event()
        # Pre-create a single event view; all consumers share it.
        self._event = CancellationEvent(self._flag)

    # ------------------------------------------------------------
    # Cleanup — deterministic, complete teardown
    # ------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this CancellationEventSignal.

        Behavior:
            * Idempotent.
            * Cancels the signal.
            * Cleans the child CancellationEvent.
            * Nulls out the underlying threading event and event view.
            * Marks cleaned via Cleanable.
        """
        if self._cleaned:
            return

        # Cancel any active workers
        if self._flag is not None:
            self._flag.set()

        # Clean child event
        if self._event is not None:
            try:
                self._event.cleanup()
            except Exception:
                pass

        # Null everything
        self._flag = None
        self._event = None
        self._cleaned = True


    @property
    def event(self) -> CancellationEvent:
        """
        Return the read-only :class:`CancellationEvent` associated with this
        signal.

        All callers receive the same event instance so every observer sees the
        same cancellation state.

        Raises:
            RuntimeError: If this signal has already been cleaned.
        """
        self.check_cleaned()
        return self._event

    def cancel(self) -> None:
        """
        Signal cancellation for all observers of this source.

        This method is idempotent: calling it multiple times has no additional
        effect beyond the first call.

        Raises:
            RuntimeError: If this signal has already been cleaned.
        """
        self.check_cleaned()
        self._flag.set()

    @property
    def is_set(self) -> bool:
        """
        Convenience passthrough to the underlying event's cancellation state.

        Returns:
            bool: True if cancellation has been signalled.

        Raises:
            RuntimeError: If this signal has already been cleaned.
        """
        self.check_cleaned()
        return self._flag.is_set()
