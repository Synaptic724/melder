import threading
import time
from collections import deque
from typing import Deque, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable


class RiftGate(Cleanable):
    """
    Generic gate primitive for coordinating Rift-scoped operations.

    Purpose:
        Provide a minimal, reusable synchronization boundary that can guard
        Rift-owned operational paths without introducing a larger state machine
        before the later projection and command/view integration work lands.

    Control model:
        1. Blocking mode (`enabled` flag):
           - When enabled is False, callers may block in wait().
           - open() re-enables access and releases waiters.
        2. Terminal close mode (`_closed` flag):
           - close_and_wait_until_free() marks the gate terminally closed
             to new work and waits for active tickets to drain.
           - cleanup() also marks terminal close and releases waiters.

    Ticket model:
        - Callers register a ticket when entering guarded work and unregister
          on exit.
        - Drain operations wait for ticket count to reach zero.
        - Ticket bookkeeping uses deque[None] for low overhead and
          allocation-friendly append/pop behavior.

    Threading:
        - State transitions for enabled / _closed and the event are
          protected by an internal RLock``.
        - ``enabled`` is intentionally readable without lock on hot paths.
    """

    __melder_internal__ = _mrg.sentinel
    ENTRY_MODE_WAIT = "wait"
    ENTRY_MODE_RAISE = "raise"
    __slots__ = ("_lock", "enabled", "_entry_mode", "_event", "_tickets", "_closed")

    def __init__(self, enabled: bool = True, entry_mode: str = "wait") -> None:
        """
        Initialize the gate in an enabled or disabled state.

        Purpose:
            Construct a low-overhead gate instance that tracks both admission
            state and in-flight ticket count for one protected Rift path.

        Contract:
            - ``_closed`` starts ``False``.
            - ``enabled`` reflects constructor input.
            - ``_event`` state mirrors ``enabled``:
              set when enabled, cleared when disabled.
            - Ticket queue starts empty.

        Args:
            enabled:
                True starts with immediate pass-through behavior.
                False starts in blocking mode until ``open()`` is called.
            entry_mode:
                Admission mode used by ``admit()`` while the gate is disabled.
                Supported values are ``wait`` and ``raise``.

        Returns:
            None.
        """
        super().__init__()
        self._lock: Optional[threading.RLock] = threading.RLock()
        self.enabled: Optional[bool] = enabled
        self._entry_mode: str = self._normalize_entry_mode(entry_mode)
        self._event: Optional[threading.Event] = threading.Event()
        self._tickets: Optional[Deque[None]] = deque()
        self._closed: bool = False

        if enabled:
            self._event.set()
        else:
            self._event.clear()

    def cleanup(self) -> None:
        """
        Idempotently close and release the gate for teardown.

        Purpose:
            Deterministically terminate gate usage and drop owned
            synchronization and ticket resources.

        Contract:
            - Marks gate terminally closed.
            - Forces ``enabled=True`` and signals the event to unblock waiters.
            - Clears outstanding tickets as teardown intent.
            - Marks this instance cleaned and nulls owned references.
            - Leaves the object unusable for all guarded operations.

        Returns:
            None.
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
            self.enabled = None
            self._entry_mode = None
            self._event = None
            self._tickets = None

        self._lock = None

    @property
    def entry_mode(self) -> str:
        """
        Return the configured admission mode.

        Returns:
            str: Configured admission mode.
        """
        self.check_cleaned()
        return self._entry_mode

    def open(self) -> None:
        """
        Enable entry and release waiting callers.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self.enabled = True
            self._event.set()

    def close(self) -> None:
        """
        Disable entry so callers block in ``wait()``.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self.enabled = False
            self._event.clear()

    def wait(self) -> None:
        """
        Block until the gate event is signalled.

        Returns:
            None.
        """
        self.check_cleaned()
        if self.enabled:
            return
        self._event.wait()

    def admit(self) -> None:
        """
        Attempt to cross the gate using the configured admission mode.

        Contract:
            - Raises immediately when the gate is terminally closed.
            - Returns immediately when admission is enabled.
            - When admission is disabled and ``entry_mode == "raise"``,
              raises immediately.
            - When admission is disabled and ``entry_mode == "wait"``, blocks
              until the gate is reopened or terminally closed.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the gate is terminally closed or configured to raise on
                disabled entry.
        """
        self.check_cleaned()
        if self._closed:
            raise RuntimeError("RiftGate is closed.")
        if self.enabled:
            return
        if self._entry_mode == self.ENTRY_MODE_RAISE:
            raise RuntimeError("RiftGate entry is disabled.")
        self._event.wait()
        self.check_cleaned()
        if self._closed:
            raise RuntimeError("RiftGate is closed.")

    def set_entry_mode(self, entry_mode: str) -> None:
        """
        Set the gate admission mode.

        Args:
            entry_mode:
                Admission mode. Supported values are ``wait`` and ``raise``.

        Returns:
            None.
        """
        self.check_cleaned()
        normalized_entry_mode = self._normalize_entry_mode(entry_mode)
        with self._lock:
            self._entry_mode = normalized_entry_mode

    def register_ticket(self) -> None:
        """
        Register an active in-flight operation.

        Returns:
            None.
        """
        self.check_cleaned()
        self._tickets.append(None)

    def unregister_ticket(self) -> None:
        """
        Unregister a previously registered in-flight operation.

        Returns:
            None.
        """
        self.check_cleaned()
        self._tickets.pop()

    def has_active_tickets(self) -> bool:
        """
        Return True when at least one active ticket is present.

        Returns:
            bool: True when at least one ticket is registered.
        """
        self.check_cleaned()
        return bool(self._tickets)

    def active_ticket_count(self) -> int:
        """
        Return active ticket count.

        Returns:
            int: Number of currently registered tickets.
        """
        self.check_cleaned()
        return len(self._tickets)

    def is_closed(self) -> bool:
        """
        Return True when gate is terminally closed.

        Returns:
            bool: True when terminal closure has been requested.
        """
        self.check_cleaned()
        return self._closed

    def close_and_wait_until_free(
        self,
        timeout: float = 30.0,
        interval: float = 0.1,
    ) -> None:
        """
        Terminally close the gate and wait for all tickets to drain.

        Args:
            timeout:
                Maximum seconds to wait for ticket drain.
            interval:
                Poll interval in seconds for checking drain progress.

        Returns:
            None.

        Raises:
            RuntimeError:
                If ticket drain does not complete before ``timeout``.
        """
        self.check_cleaned()

        with self._lock:
            self._closed = True
            self.enabled = False
            self._event.set()

        deadline = time.monotonic() + timeout
        while self.has_active_tickets():
            if time.monotonic() >= deadline:
                raise RuntimeError("Timeout waiting for rift tickets to drain.")
            time.sleep(interval)

    @classmethod
    def _normalize_entry_mode(cls, entry_mode: str) -> str:
        """
        Normalize and validate one admission mode.

        Args:
            entry_mode:
                Candidate admission mode.

        Returns:
            str: Normalized admission mode.

        Raises:
            ValueError:
                If the requested mode is unsupported.
        """
        if not entry_mode:
            raise ValueError("entry_mode cannot be empty.")
        normalized_entry_mode = entry_mode.strip().lower()
        if normalized_entry_mode not in {
                cls.ENTRY_MODE_WAIT,
                cls.ENTRY_MODE_RAISE,
        }:
            raise ValueError(
                "entry_mode must be 'wait' or 'raise', got '{0}'.".format(
                    entry_mode
                )
            )
        return normalized_entry_mode
