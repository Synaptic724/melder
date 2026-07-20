import threading
from typing import ClassVar, List

# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class PhaseLatch:
    """
    Countdown completion latch for one phase barrier.

    Purpose:
        Provide the O(1)-synchronization barrier primitive consumed by
        `PhaseScheduler`: the control thread waits on ONE event while worker
        threads report per-unit completion, instead of the control thread
        installing waiters on every unit's Future.

    Responsibilities:
        - Count down expected unit reports and fire when the phase is done.
        - Fire EARLY and unconditionally on the first error (fail-fast).
        - Separately track when every unit has reported, so a fail-fast caller
          can wait out stragglers before tearing down.
        - Collect the error set for the control thread to inspect.

    The Two Events (the whole design):
        This latch owns TWO independent events, and the distinction is the
        reason it exists rather than a plain `threading.Event`:

        - `_event` - "stop waiting". Set when the count reaches zero OR on the
          first `record_error(...)`. Answers "should the control thread move on".
        - `_all_reported_event` - "nothing is still running". Set ONLY when the
          remaining count reaches zero, regardless of errors. Answers "is it
          safe to tear down".

        A fail-fast wake returns from `wait()` while straggler unit bodies are
        still executing on pool workers. Unwinding into teardown at that moment
        races those bodies. `wait_all_reported()` is the barrier that closes
        that race.

    Contract:
        - Constructed with the exact number of expected unit completions.
        - `complete()` records one successful (or cooperatively cancelled)
          unit; the event fires when the count reaches zero.
        - `record_error(exc)` records one failed unit AND fires the event
          immediately (fail-fast wake) so the control thread can abort the
          phase without waiting for stragglers; the failed unit also counts
          toward completion.
        - `wait(timeout)` returns True when the event fired within the
          timeout (all-done OR first-error), False on timeout. Callers must
          inspect `errors` to distinguish success from fail-fast.
        - Late completions after a fail-fast or timeout are harmless: the
          counter may pass zero and the event is already set. A latch is
          owned by exactly one phase run and is never reused, so stale
          completions from an abandoned phase can never touch a newer
          barrier (each queued unit carries its own latch reference).
        - `wait_all_reported(timeout)` is the QUIESCE barrier: it fires only
          when every expected unit has reported (success, cooperative
          cancel, or failure), so a fail-fast control thread can wait out
          in-flight stragglers before unwinding into caller teardown. Late
          reports drive this second event exactly like the first.

    Owned State:
        - `_lock`: guards the counter and error list. Not held during waits.
        - `_event`: the fail-fast / all-done wake.
        - `_all_reported_event`: the quiesce barrier.
        - `_remaining`: countdown of unreported units. MAY GO NEGATIVE - late
          stragglers from an aborted phase keep decrementing, and the zero
          checks are `<= 0` precisely so that is harmless.
        - `_errors`: accumulated unit failures.

    Threading:
        - `complete()` / `record_error()` are called from worker threads;
          both synchronize on one internal lock.
        - `wait()` and `errors` are control-thread operations.
        - `errors` returns a COPY taken under the lock, so the control thread
          can iterate it safely while stragglers are still appending.
        - Neither wait verb holds the lock, so reporting never blocks on a
          waiter.

    Lifecycle / Cleanup:
        - Transient per-phase object, like a Future: owns only a lock and two
          events, holds no external resources, and requires no cleanup call.
        - Deliberately NOT `Cleanable`. There is nothing to release, and a
          teardown contract would imply a lifetime this object does not have.
        - ONE LATCH PER PHASE RUN, never reused. Each queued unit carries its
          own latch reference, which is what makes late reports from an
          abandoned phase safe: they land on the dead latch, not a live one.

    Input Validation:
        `expected` must be a positive int and `bool` is explicitly rejected.
        That check is not pedantry - `True` is an `int` in Python, so
        `PhaseLatch(True)` would otherwise silently build a latch expecting one
        unit and a phase would appear to complete after its first report.

    Registration:
        MELDER KERNEL - guarded. The scheduler owns phase barriers; a user has
        no reason to register one as a spell. Leaf class with no subclasses, so
        the sentinel cannot propagate through the MRO.

    Subsystem Context:
        Part of `utilities/synchronization/`, and specifically the barrier half
        of the phase machinery. `PhaseScheduler` owns the worker pool and phase
        ordering; this owns the single question "is this phase finished, and is
        anything still running". `UnitOfWork` is what reports into it. Compare
        `SafeGuard`, which coordinates locks rather than completions.

    System Context:
        Every conjure runs phases 1-4 (structural), 5-7 (foundational
        resolution), and 8-11 (plan resolution) through the scheduler, and each
        phase is bounded by one of these latches. The quiesce verb exists
        because a phase that fails fast must still not unwind into caller
        teardown while unit bodies touch objects the caller is about to destroy
        - that ordering is what keeps a failed conjure from leaving a half-torn
        world behind.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Phase completion barrier for PhaseScheduler. Two "
        "events: wait() wakes on all-done OR first error (fail-fast), "
        "wait_all_reported() wakes only when nothing is still running (quiesce "
        "before teardown). One latch per phase run; never reused."
    )

    __slots__ = ["_lock", "_event", "_all_reported_event", "_remaining", "_errors"]

    def __init__(self, expected: int) -> None:
        """
        Initialize a latch expecting `expected` unit completions.

        Args:
            expected:
                Exact number of units that will report into this latch.
                Must be positive; empty phases never construct a latch.

        Raises:
            ValueError: If `expected` is not a positive integer.

        Returns:
            None.
        """
        if not isinstance(expected, int) or isinstance(expected, bool) or expected < 1:
            raise ValueError("PhaseLatch expected count must be a positive int.")
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._all_reported_event = threading.Event()
        self._remaining: int = expected
        self._errors: List[BaseException] = []

    def complete(self) -> None:
        """
        Record one non-failing unit completion.

        Contract:
            - Decrements the remaining count; fires the event at zero.
            - Safe to call after a fail-fast already fired the event
              (stragglers of an aborted phase still report here).

        Returns:
            None.
        """
        with self._lock:
            self._remaining -= 1
            if self._remaining <= 0:
                self._event.set()
                self._all_reported_event.set()

    def record_error(self, exc: BaseException) -> None:
        """
        Record one failed unit and wake the control thread immediately.

        Contract:
            - Appends the exception to the error list.
            - Counts the failed unit toward completion.
            - Fires the event unconditionally (fail-fast), so the control
              thread aborts without waiting for the remaining units.

        Args:
            exc: Exception raised by the failed unit.

        Returns:
            None.
        """
        with self._lock:
            self._errors.append(exc)
            self._remaining -= 1
            self._event.set()
            if self._remaining <= 0:
                self._all_reported_event.set()

    def wait_all_reported(self, timeout_seconds: float) -> bool:
        """
        Wait until EVERY expected unit has reported, bounded (quiesce).

        Purpose:
            The fail-fast wake (`wait`) returns while straggler unit bodies
            may still be executing on pool workers. Callers that unwind
            into teardown must not race those bodies: this verb parks until
            the remaining count reaches zero - success, cooperative
            cancellation, and failure reports all count - so a True return
            means no unit body is still in flight.

        Contract:
            - Returns True when all expected reports landed within the
              timeout; False when at least one unit is still unreported
              (hung or still running) at the bound.
            - Idempotent after the fact: once all units have reported,
              every later call returns True immediately.
            - Termination rides the worker-loop law: every dequeued unit
              reports into its latch exactly once.

        Args:
            timeout_seconds: Maximum seconds to wait.

        Returns:
            bool: True when the phase is fully quiesced, else False.
        """
        return self._all_reported_event.wait(timeout_seconds)

    def wait(self, timeout_seconds: float) -> bool:
        """
        Wait for all-done or first-error, bounded by the barrier timeout.

        Args:
            timeout_seconds: Maximum seconds to wait.

        Returns:
            bool: True when the event fired within the timeout (callers must
            check `errors` to distinguish success from fail-fast); False on
            timeout.
        """
        return self._event.wait(timeout_seconds)

    @property
    def errors(self) -> List[BaseException]:
        """
        Return a snapshot of the errors recorded so far.

        Returns:
            List[BaseException]: Copied error list; safe to iterate while
            stragglers keep reporting.
        """
        with self._lock:
            return list(self._errors)
