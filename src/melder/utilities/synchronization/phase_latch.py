import threading
from typing import List


class PhaseLatch:
    """
    Countdown completion latch for one phase barrier.

    Purpose:
        Provide the O(1)-synchronization barrier primitive consumed by
        `PhaseScheduler`: the control thread waits on ONE event while worker
        threads report per-unit completion, instead of the control thread
        installing waiters on every unit's Future.

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

    Threading:
        - `complete()` / `record_error()` are called from worker threads;
          both synchronize on one internal lock.
        - `wait()` and `errors` are control-thread operations.

    Lifecycle:
        - Transient per-phase object, like a Future: owns only a lock and an
          event, holds no external resources, and requires no cleanup call.
    """

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
