import threading
import time
from collections import deque
from typing import ClassVar


from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class CreationGate(Cleanable):
    """
    Generic gate primitive for coordinating creation and cleanup operations.

    Purpose:
        Provide a minimal, reusable synchronization boundary that can guard
        creation-oriented paths (for example, conduit meld entry or spell
        creation-context rebuild paths) without introducing a heavy state
        machine.

    Control model:
        1. Blocking mode (`enabled` flag):
           - When enabled is "False", callers may block in "wait()".
           - "open()" re-enables access and releases waiters.
        2. Terminal close mode (`_closed` flag):
           - "close_and_wait_until_free()" marks the gate terminally closed
             to new work and waits for active tickets to drain.
           - "cleanup()" also marks terminal close and releases waiters.

    Ticket model:
        - Callers register a ticket when entering guarded work and unregister
          on exit.
        - Drain operations wait for the ticket count to reach zero.
        - Ticket bookkeeping uses "deque[None]" for low overhead and
          allocation-friendly append/pop behaviour.

    Threading:
        - State transitions for "enabled" / "_closed" and the event are
          protected by an internal "RLock".
        - "enabled" is intentionally readable without a lock on hot paths.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["_lock", "enabled", "_event", "_tickets", "_closed"]

    def __init__(self, enabled: bool = True) -> None:
        """
        Public API

        Initialize the gate in an enabled or disabled state.

        Purpose:
            Construct a low-overhead gate instance that tracks both admission
            state and in-flight ticket count for one protected creation path.

        Contract:
            - "_closed" starts "False".
            - "enabled" reflects constructor input.
            - "_event" state mirrors "enabled":
              set when enabled, cleared when disabled.
            - Ticket queue starts empty.

        Args:
            enabled:
                True starts with immediate pass-through behaviour.
                False starts in blocking mode until "open()" is called.

        Returns:
            None.
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

        Purpose:
            Deterministically terminate gate usage and drop owned
            synchronization/ticket resources.

        Contract:
            - Marks gate terminally closed.
            - Forces "enabled=True" and signals event to unblock waiters.
            - Clears outstanding tickets as teardown intent.
            - Marks this instance cleaned and nulls owned references.
            - Leaves the object unusable for all guarded operations.

        Threading:
            - Cleanup is lock-guarded to avoid interleaving teardown with gate
              state transitions.
            - The event is signalled before references are nulled so blocked
              waiters are released deterministically.

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

            del self.enabled
            del self._event
            del self._tickets
        del self._lock

    def open(self) -> None:
        """
        Public API

        Enable entry and release waiting callers.

        Purpose:
            Transition the gate into pass-through mode.

        Contract:
            - Sets "enabled=True".
            - Sets the gate event so callers blocked in "wait()" resume.

        Raises:
            RuntimeError:
                If called after "cleanup()".

        Threading:
            - The gate lock protects State transition.

        Returns:
            None.
        """
        with self._lock:
            self.enabled = True
            self._event.set()

    def close(self) -> None:
        """
        Public API

        Disable entry so callers block in "wait()".

        Purpose:
            Transition the gate into blocking mode without terminal closure.

        Contract:
            - Sets "enabled=False".
            - Clears the gate event so future "wait()" calls block.
            - Does not modify "_closed".

        Raises:
            RuntimeError:
                If called after "cleanup()".

        Threading:
            - The gate lock protects State transition.

        Returns:
            None.
        """
        with self._lock:
            self.enabled = False
            self._event.clear()

    def wait(self) -> None:
        """
        Public API

        Block until the gate event is signalled.

        Purpose:
            Provide an admission barrier for callers that must pause while
            gate entry is disabled.

        Contract:
            - Returns immediately when "enabled" is truthy.
            - Blocks on the event when "enabled" is falsy until another
              thread signals via "open()" or terminal close paths.

        Notes:
            - Returns immediately when already enabled.
            - Callers that care about terminal closure should check
              "is_closed()" before and after waiting.

        Raises:
            RuntimeError:
                If called after "cleanup()".

        Returns:
            None.
        """
        if self.enabled:
            return
        self._event.wait()

    def register_ticket(self) -> None:
        """
        Public API

        Register an active in-flight operation.

        Purpose:
            Mark one unit of work as inside the guarded region.

        Contract:
            - Appends one ticket marker to the internal ticket queue.
            - Must be paired with "unregister_ticket()" by caller code.

        Raises:
            RuntimeError:
                If called after "cleanup()".

        Threading:
            - Ticket operations are intentionally minimal and rely on caller
              discipline for correct pairing semantics.

        Returns:
            None.
        """
        self._tickets.append(None)

    def unregister_ticket(self) -> None:
        """
        Public API

        Unregister a previously registered in-flight operation.

        Purpose:
            Remove one in-flight marker when guarding work exits.

        Contract:
            - Removes exactly one ticket marker.
            - Caller must only unregister tickets it previously registered.

        Raises:
            IndexError:
                If no tickets exist (caller pairing bug).
            RuntimeError:
                If called after "cleanup()".

        Returns:
            None.
        """
        self._tickets.pop()

    def has_active_tickets(self) -> bool:
        """
        Public API

        Return True when at least one active ticket is present.

        Purpose:
            Provide a low-cost boolean check used by drain loops and tests.

        Returns:
            bool:
                True when at least one ticket is registered.

        Raises:
            RuntimeError:
                If called after "cleanup()".

        Notes:
            This is the boolean view used by drain loops; callers that need an
            exact count should use: meth:`active_ticket_count`.
        """
        return bool(self._tickets)

    def active_ticket_count(self) -> int:
        """
        Public API

        Return active ticket count.

        Purpose:
            Return exact in-flight ticket cardinality.

        Returns:
            int:
                Number of currently registered tickets.

        Raises:
            RuntimeError:
                If called after "cleanup()".

        Notes:
            This is the exact-count counterpart to: meth:`has_active_tickets`.
        """
        return len(self._tickets)

    def is_closed(self) -> bool:
        """
        Public API

        Return True when the gate is terminally closed.

        Purpose:
            Expose terminal-close state to callers that distinguish
            temporary blocking from final shutdown.

        Returns:
            bool:
                True when "close_and_wait_until_free()" or "cleanup()"
                has marked terminal closure.

        Raises:
            RuntimeError:
                If called after "cleanup()".

        Notes:
            This reports terminal closure only. Temporary blocked state from: meth: 'close` is tracked separately through "enabled".
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

        Purpose:
            Seal gate entry for shutdown/reconfiguration and wait until all
            in-flight guarded work has exited.

        Contract:
            - Sets "_closed=True" to indicate no new work should be accepted.
            - Sets "enabled=False" to keep normal gate checks in blocked mode.
            - Signals the event so existing waiters wake and can observe close.
            - Polls until "active_ticket_count == 0".

        Args:
            timeout:
                Maximum seconds to wait for ticket drain.
            interval:
                Poll interval in seconds for checking drain progress.

        Raises:
            RuntimeError:
                If ticket drain does not complete before "timeout".
                Also raised when called after "cleanup()".

        Threading:
            - Close-state transition is lock-guarded.
            - Drain wait loop is cooperative polling based on ticket queue
              length.

        Returns:
            None.

        Notes:
            Existing waiters are released so they can observe terminal closure;
            the method then waits only on the ticket drain, not on the waiter exit.
        """
        with self._lock:
            self._closed = True
            self.enabled = False
            self._event.set()

        deadline = time.monotonic() + timeout
        while self.has_active_tickets():
            if time.monotonic() >= deadline:
                raise RuntimeError("Timeout waiting for creation tickets to drain.")
            time.sleep(interval)
