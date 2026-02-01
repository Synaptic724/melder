import threading
from collections import deque
from melder.utilities.general_base.cleanable import Cleanable


class MeldGate(Cleanable):
    """
    Conduit-local meld gate for controlling meld execution.

    Purpose:
        Provide two distinct control modes for a single Conduit:

        1) **Blocking mode** (enabled flag)
           - When `enabled` is False, callers block on an internal Event until
             re-enabled via open().

        2) **Terminal deny mode** (_closed flag)
           - When `_closed` is True, the gate is permanently closed to new meld
             calls. Conduit.meld checks this state and raises immediately.
           - Terminal close is intended for teardown: stop accepting new work,
             allow in-flight work to drain, then proceed.

    Contract:
        - `enabled` is a fast-path boolean flag used by Conduit.meld.
        - When disabled (`enabled=False`) and not terminally closed, callers may block
          on the internal Event until re-enabled.
        - `open()` / `close()` are idempotent and thread-safe.
        - `cleanup()` unblocks any waiters, marks the gate terminally closed, and
          marks the gate cleaned.
        - `close_and_wait_until_free()` marks the gate terminally closed to new work,
          wakes any waiters so they can observe closure, and waits for active meld
          tickets to drain.

    Threading:
        - Internal RLock guards state transitions for `enabled`, `_closed`, and the Event.
        - `enabled` is read without locking on the hot path; it is written
          under the lock in open()/close()/cleanup()/close_and_wait_until_free().
    """

    __slots__ = ("_lock", "enabled", "_event", "_tickets", "_closed")

    def __init__(self, enabled: bool = True) -> None:
        """
        Public API

        Initialize a MeldGate in enabled or disabled state.

        Args:
            enabled:
                If True, melds pass immediately (unless terminally closed is enforced
                by the caller).
                If False, melds block until open() is called (unless terminally closed).
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self.enabled: bool = enabled
        self._event: threading.Event = threading.Event()
        self._tickets: deque[None] = deque()
        self._closed: bool = False

        if enabled:
            self._event.set()
        else:
            self._event.clear()

    def cleanup(self) -> None:
        """
        Public API

        Idempotently release any waiters and mark the gate as cleaned.

        Contract:
            - Marks the gate terminally closed.
            - Forces the Event set so no thread remains blocked in wait().
            - Clears ticket tracking (teardown intent) and marks cleaned.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._closed = True
            self.enabled = True
            self._event.set()
            self._tickets.clear()
            self._cleaned = True

    def open(self) -> None:
        """
        Public API

        Enable melds and release any waiting threads.

        Contract:
            - Sets enabled=True.
            - Sets the internal Event to release waiters.
            - Does not alter terminal closed state.
            - Idempotent.
        """
        self.check_cleaned()
        with self._lock:
            self.enabled = True
            self._event.set()

    def close(self) -> None:
        """
        Public API

        Disable melds so callers block until re-enabled.

        Contract:
            - Sets enabled=False.
            - Clears the internal Event so waiters block.
            - Does not alter terminal closed state.
            - Idempotent.
        """
        self.check_cleaned()
        with self._lock:
            self.enabled = False
            self._event.clear()

    def wait(self) -> None:
        """
        Public API

        Block until melds are enabled.

        Contract:
            - Returns immediately if enabled.
            - Blocks on the internal Event when disabled.
            - Caller is responsible for checking terminal closure if they care
              (Conduit.meld does this before and after waiting).
        """
        if self.enabled:
            return
        self._event.wait()

    def register_ticket(self) -> None:
        """
        Public API

        Register an active meld ticket for this gate.

        Contract:
            - Appends a ticket marker to the internal deque.
            - Caller is responsible for paired unregister_ticket().
        """
        self._tickets.append(None)

    def unregister_ticket(self) -> None:
        """
        Public API

        Release a previously registered meld ticket.

        Contract:
            - Pops a ticket from the internal deque.
            - Raises IndexError if no tickets are present (pairing bug).
        """
        self._tickets.pop()

    def has_active_tickets(self) -> bool:
        """
        Public API

        Report whether any meld tickets are currently active.

        Returns:
            bool: True if one or more tickets are active; otherwise False.
        """
        return bool(self._tickets)

    def active_ticket_count(self) -> int:
        """
        Public API

        Return the number of active meld tickets.

        Returns:
            int: Count of currently registered tickets.
        """
        self.check_cleaned()
        return len(self._tickets)

    def is_closed(self) -> bool:
        """
        Public API

        Report whether the gate is terminally closed to new meld calls.

        Returns:
            bool: True if the gate is terminally closed; otherwise False.
        """
        return self._closed

    def close_and_wait_until_free(self, timeout: float = 30.0, interval: float = 0.1) -> None:
        """
        Public API

        Terminally close the gate to new meld calls and wait for active meld tickets to drain.

        Contract:
            - Marks the gate closed so new melds raise immediately (via Conduit.meld).
            - Forces enabled=False so Conduit.meld enters its gating branch.
            - Sets the Event to release any waiters so they wake, re-check is_closed(),
              and raise (instead of deadlocking).
            - Waits until active tickets reach zero.

        Raises:
            RuntimeError: If ticket drain does not occur within timeout.
        """
        self.check_cleaned()

        with self._lock:
            self._closed = True
            self.enabled = False
            self._event.set()

        try:
            # IMPORTANT: wait(...) expects "keep waiting while condition() is True"
            # so we wait while tickets exist.
            wait(lambda: self.has_active_tickets(), timeout=timeout, interval=interval)
        except TimeoutError as e:
            raise RuntimeError("Timeout waiting for meld tickets to drain.") from e
