import threading
from typing import ClassVar



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

    Responsibilities:
        - Expose one lock-free `is_set` read over the shared cancellation flag.
        - Offer `throw_if_set()` for call sites that prefer raising to branching.
        - Own nothing: the flag belongs to the parent signal.

    Contract:
        - Read-only. There is no way to CAUSE cancellation through this view;
          only `CancellationEventSignal.cancel()` can do that. That asymmetry is
          the point - workers observe, the coordinator decides.
        - `is_set` and `throw_if_set()` both reject use after cleanup.

    SHARED INSTANCE - important:
        `CancellationEventSignal.event` hands every caller THE SAME view object,
        not a per-consumer copy. Consumers must therefore treat it as borrowed:
        never call `cleanup()` on a view you were handed, because that tears it
        down for every other worker observing the same signal. The parent signal
        owns this object's lifetime.

    Owned State:
        - `_flag`: borrowed reference to the parent signal's `threading.Event`.
          Borrowed, not owned - cleanup drops the reference and never touches
          the event itself.

    Threading:
        Read path is lock-free by design. `is_set` delegates straight to
        `threading.Event.is_set()`, so any number of workers can poll it as hot
        as they like without contending. That is the whole reason this view
        exists rather than handing workers the signal itself.

    Lifecycle / Cleanup:
        Idempotent. Drops the borrowed flag reference under normal del posture
        and marks cleaned; subsequent access raises through `check_cleaned()`.
        Cleaning a view does NOT cancel anything and does not affect the parent.

    Registration:
        MELDER KERNEL - guarded. Cancellation plumbing is Melder's; a user
        observes cancellation through the object they were handed rather than
        registering one.

    Subsystem Context:
        The read half of the cancellation pair in `utilities/synchronization/`.
        `CancellationEventSignal` is the write half and owns this object. The
        split exists so a worker physically cannot cancel the pipeline it is
        running inside - it holds a type with no `cancel()` on it.

    System Context:
        Consumed by `PhaseScheduler`'s worker pool, which threads one shared
        cancellation signal through a phase run. A unit that observes
        cancellation aborts cooperatively and reports into its `PhaseLatch`,
        which is why `OperationCancelledError` counts as a completion rather
        than a failure.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Read-only view of a shared cancellation flag. Poll "
        "is_set (lock-free) or call throw_if_set() to abort cooperatively. You "
        "cannot cancel through this type - only the owning "
        "CancellationEventSignal can. Borrowed: never clean up a view you were "
        "handed, it is shared by every observer."
    )

    __slots__ = Cleanable.__slots__ + ["_flag",]
    __melder_internal__: ClassVar[object] = _mrg.sentinel

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

        Returns:
            None.
        """
        Cleanable.__init__(self)
        if flag is None:
            raise ValueError("CancellationEvent requires a valid threading.Event")
        self._flag = flag

    # ------------------------------------------------------------
    # Cleanup - deterministic, idempotent, zero contamination
    # ------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this CancellationEvent.

        Behavior:
            * Idempotent via `Cleanable._cleaned`.
            * Drops the shared event reference owned by the parent signal.
            * After cleanup, any access raises `RuntimeError`.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        # No lock needed - this class is read-only and the flag is just a reference.
        del self._flag

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

        Returns:
            None.
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

    * Write path (cancel) is a single `event.set()` call - thread-safe and
      cheap.
    * Read path (via :class:`CancellationEvent`) does **not** use any
      additional locks beyond what :class:`threading.Event` already does
      internally.
    * Intended usage is one signal shared across many worker threads in a
      burst-style pipeline (e.g. staged resolution compilation).

    Responsibilities:
        - Own the `threading.Event` that IS the cancellation state.
        - Own the single `CancellationEvent` view every consumer shares.
        - Trigger cancellation via `cancel()`.
        - Cancel and tear down together at end of life.

    CLEANUP IMPLIES CANCEL - read this before tearing one down:
        `cleanup()` calls `self._flag.set()` before releasing anything. Tearing
        down a signal therefore CANCELS every worker still observing it. That is
        deliberate: a pipeline whose signal is being destroyed has no coordinator
        left, so the safe terminal state is "everyone stop" rather than
        "everyone keep running with no way to be told otherwise".

        Practical consequence: do not clean up a signal as a tidy-up step while
        work you still want is in flight. Cleanup is an abort, not a release.

    Contract:
        - `cancel()` is idempotent; `threading.Event.set()` is already so.
        - `event` returns the SAME view instance on every call, never a copy.
        - `cleanup()` is idempotent and double-checked under the lock.
        - Post-cleanup access raises through `check_cleaned()`.

    Owned State:
        - `_flag`: the `threading.Event` carrying cancellation state. OWNED.
        - `_event`: the one shared `CancellationEvent` view. OWNED, and cleaned
          by this object - consumers must not clean it themselves.
        - `_lock`: serializes the write path and teardown.

    Threading:
        - Write path is one `Event.set()` under the lock - cheap and safe.
        - Read path through `CancellationEvent` takes NO additional lock, so
          hot polling never contends with the coordinator.
        - `cleanup()` sets `_cleaned` FIRST, inside the lock, before doing the
          teardown work. A concurrent `cancel()` therefore raises through
          `check_cleaned()` rather than racing a half-torn signal - failing the
          late caller is preferred to letting it touch releasing state.

    Lifecycle / Cleanup:
        - Idempotent, double-checked under the lock.
        - Order: mark cleaned, set the flag (cancel), clean the child view, then
          release all three slots under normal del posture.
        - Child cleanup is wrapped best-effort: a failure tearing down the view
          must not prevent the signal from releasing its own state, since a
          half-released signal is worse than a lost child error.

    Registration:
        MELDER KERNEL - guarded. The coordinator side of cancellation is
        Melder's to construct and own.

    Subsystem Context:
        The write half of the cancellation pair in `utilities/synchronization/`,
        owning `CancellationEvent` as its read half. Compare `PhaseLatch`, which
        answers "is this phase done"; this answers "should anyone still be
        working". A phase run typically holds both.

    System Context:
        One signal is shared across a `PhaseScheduler` worker pool for a phase
        run. When a unit fails, the scheduler's fail-fast path can cancel the
        rest rather than waiting them out - which is why cancelled units report
        as completions into the latch instead of errors, and why a cancelled
        conjure ends without a Conduit but is not a defect.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Coordinator side of cooperative cancellation. Call "
        "cancel() to stop every observer; hand workers the .event view so they "
        "can poll without contending. WARNING: cleanup() cancels as part of "
        "teardown - it is an abort, not a release."
    )

    __slots__ = Cleanable.__slots__ + ["_lock", "_flag", "_event"]
    __melder_internal__: ClassVar[object] = _mrg.sentinel

    def __init__(self) -> None:
        """
        Create a cancellation signal and pre-build its shared event view.

        Contract:
            - Owns one mutable :class:`threading.Lock`.
            - Owns one mutable :class:`threading.Event`.
            - Owns one reusable :class:`CancellationEvent` wrapper that all
              consumers share.

        Returns:
            None.
        """
        Cleanable.__init__(self)
        self._lock: threading.Lock = threading.Lock()
        self._flag: threading.Event = threading.Event()
        # Pre-create a single event view; all consumers share it.
        self._event: CancellationEvent = CancellationEvent(self._flag)

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

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
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
            del self._flag
            del self._event
            del self._lock



    @property
    def event(self) -> CancellationEvent:
        """
        Return the read-only :class:`CancellationEvent` associated with this
        signal.

        All callers receive the same event instance so every observer sees the
        same cancellation state.

        Returns:
            CancellationEvent:
                The one shared read-only view - the SAME instance on every
                call, never a per-consumer copy.

        Raises:
            RuntimeError: If this signal has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._event

    def cancel(self) -> None:
        """
        Signal cancellation for all observers of this source.

        This method is idempotent: calling it multiple times has no additional
        effect beyond the first call.

        Raises:
            RuntimeError: If this signal has already been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
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
        with self._lock:
            return self._flag.is_set()
