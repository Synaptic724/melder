import threading
from collections import deque

from melder.utilities.general_base.cleanable import Cleanable


class MeldGate(Cleanable):
    """
    Conduit-local meld gate for controlling meld execution.

    Purpose:
        Provide a deterministic, low-overhead mechanism to block or allow
        meld calls for a single Conduit.

    Contract:
        - `enabled` is a fast-path boolean flag used by Conduit.meld.
        - When disabled, callers block on an internal Event until re-enabled.
        - enable()/disable() are idempotent and thread-safe.
        - cleanup() unblocks any waiters and marks the gate as cleaned.
        - close_and_wait_until_free() marks the gate closed and waits for
          active meld tickets to drain.

    Threading:
        - Internal RLock guards state transitions for `enabled` and the Event.
        - `enabled` is read without locking on the hot path; it is written
          under the lock in enable()/disable()/cleanup().
    """

    __slots__ = ("_lock", "enabled", "_event", "_tickets", "_tickets_empty", "_closed")

    def __init__(self, enabled: bool = True) -> None:
        """
        Public API

        Initialize a MeldGate in enabled or disabled state.

        Args:
            enabled: If True, melds pass immediately. If False, melds block
                until enable() is called.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self.enabled: bool = enabled
        self._event: threading.Event = threading.Event()
        self._tickets: deque[None] = deque()
        self._tickets_empty: threading.Event = threading.Event()
        self._closed: bool = False
        self._tickets_empty.set()
        if enabled:
            self._event.set()
        else:
            self._event.clear()

    def cleanup(self) -> None:
        """
        Public API

        Idempotently release any waiters and mark the gate as cleaned.

        Contract:
            - Ensures the internal Event is set to avoid deadlocks.
            - Marks the gate as cleaned.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self.enabled = True
            self._event.set()
            self._tickets.clear()
            self._tickets_empty.set()
            self._closed = True
            self._cleaned = True

    def enable(self) -> None:
        """
        Public API

        Enable melds and release any waiting threads.

        Contract:
            - Sets enabled=True.
            - Sets the internal Event to release waiters.
            - Idempotent.
        """
        self.check_cleaned()
        with self._lock:
            self.enabled = True
            self._event.set()

    def disable(self) -> None:
        """
        Public API

        Disable melds so callers block until re-enabled.

        Contract:
            - Sets enabled=False.
            - Clears the internal Event so waiters block.
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
        """
        self.check_cleaned()
        if self.enabled:
            return
        self._event.wait()

    def register_ticket(self) -> None:
        """
        Public API

        Register an active meld ticket for this gate.

        Contract:
            - Appends a None ticket to the internal deque.
            - Caller is responsible for paired unregister_ticket().
        """
        self.check_cleaned()
        if self._closed:
            raise RuntimeError("MeldGate is closed.")
        self._tickets.append(None)
        self._tickets_empty.clear()

    def unregister_ticket(self) -> None:
        """
        Public API

        Release a previously registered meld ticket.

        Contract:
            - Pops a ticket from the internal deque when present.
            - Safe to call even if no tickets are present.
        """
        self.check_cleaned()
        if self._tickets:
            self._tickets.pop()
        if not self._tickets:
            self._tickets_empty.set()

    def has_active_tickets(self) -> bool:
        """
        Public API

        Report whether any meld tickets are currently active.

        Returns:
            bool: True if one or more tickets are active; otherwise False.
        """
        self.check_cleaned()
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

        Report whether the gate is closed to new meld calls.

        Returns:
            bool: True if the gate is closed; otherwise False.
        """
        self.check_cleaned()
        return self._closed

    def close_and_wait_until_free(self) -> None:
        """
        Public API

        Close the gate and wait for active meld tickets to drain.

        Contract:
            - Marks the gate closed so new melds raise immediately.
            - Enables the gate to release any waiters, then waits until
              active tickets reach zero.
        """
        self.check_cleaned()
        self._closed = True
        self.enabled = True
        self._event.set()
        self._tickets_empty.wait()
