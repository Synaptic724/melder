from __future__ import annotations

import threading
import time
from collections import deque

from melder.utilities.general_base.cleanable import Cleanable


class CreationGate(Cleanable):
    """
    Generic gate primitive for coordinating creation and cleanup operations.

    Purpose:
        Provide a minimal, reusable synchronization boundary that can guard
        creation-oriented paths (for example conduit meld entry or spell
        creation-context rebuild paths) without introducing a heavy state
        machine.

    Control model:
        1. Blocking mode (`enabled` flag):
           - When enabled is ``False``, callers may block in ``wait()``.
           - ``open()`` re-enables access and releases waiters.
        2. Terminal close mode (`_closed` flag):
           - ``close_and_wait_until_free()`` marks the gate terminally closed
             to new work and waits for active tickets to drain.
           - ``cleanup()`` also marks terminal close and releases waiters.

    Ticket model:
        - Callers register a ticket when entering guarded work and unregister
          on exit.
        - Drain operations wait for ticket count to reach zero.
        - Ticket bookkeeping uses ``deque[None]`` for low overhead and
          allocation-friendly append/pop behavior.

    Threading:
        - State transitions for ``enabled`` / ``_closed`` and the event are
          protected by an internal ``RLock``.
        - ``enabled`` is intentionally readable without lock on hot paths.
    """

    __slots__ = ("_lock", "enabled", "_event", "_tickets", "_closed")

    def __init__(self, enabled: bool = True) -> None:
        """
        Public API

        Initialize the gate in an enabled or disabled state.

        Args:
            enabled:
                True starts with immediate pass-through behavior.
                False starts in blocking mode until ``open()`` is called.
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

        Idempotently close and release the gate for teardown.

        Contract:
            - Marks gate terminally closed.
            - Forces ``enabled=True`` and signals event to unblock waiters.
            - Clears outstanding tickets as teardown intent.
            - Marks this instance cleaned.
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

        Enable entry and release waiting callers.
        """
        self.check_cleaned()
        with self._lock:
            self.enabled = True
            self._event.set()

    def close(self) -> None:
        """
        Public API

        Disable entry so callers block in ``wait()``.
        """
        self.check_cleaned()
        with self._lock:
            self.enabled = False
            self._event.clear()

    def wait(self) -> None:
        """
        Public API

        Block until the gate event is signalled.

        Notes:
            - Returns immediately when already enabled.
            - Callers that care about terminal closure should check
              ``is_closed()`` before and after waiting.
        """
        if self.enabled:
            return
        self._event.wait()

    def register_ticket(self) -> None:
        """
        Public API

        Register an active in-flight operation.
        """
        self._tickets.append(None)

    def unregister_ticket(self) -> None:
        """
        Public API

        Unregister a previously registered in-flight operation.

        Raises:
            IndexError:
                If no tickets exist (caller pairing bug).
        """
        self._tickets.pop()

    def has_active_tickets(self) -> bool:
        """
        Public API

        Return True when at least one active ticket is present.
        """
        return bool(self._tickets)

    def active_ticket_count(self) -> int:
        """
        Public API

        Return active ticket count.
        """
        self.check_cleaned()
        return len(self._tickets)

    def is_closed(self) -> bool:
        """
        Public API

        Return True when gate is terminally closed.
        """
        return self._closed

    def close_and_wait_until_free(
        self,
        timeout: float = 30.0,
        interval: float = 0.1,
    ) -> None:
        """
        Public API

        Terminally close the gate and wait for all tickets to drain.

        Contract:
            - Sets ``_closed=True`` to indicate no new work should be accepted.
            - Sets ``enabled=False`` to keep normal gate checks in blocked mode.
            - Signals the event so existing waiters wake and can observe close.
            - Polls until ``active_ticket_count == 0``.

        Args:
            timeout:
                Maximum seconds to wait for ticket drain.
            interval:
                Poll interval in seconds for checking drain progress.

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
                raise RuntimeError("Timeout waiting for creation tickets to drain.")
            time.sleep(interval)
