import threading
import time
from collections import deque
from typing import Deque

from melder.utilities.general_base.cleanable import Cleanable


class RiftGateDrainTimeoutError(RuntimeError):
    """
    A RiftGate drain ran out of time with threads still inside.

    Purpose:
        Let a caller that drains a gate - `Nexus.remove_rift`, `Nexus.cleanup` - tell a drain timeout apart from every
        other RuntimeError the gate raises (a cleaned gate, a refused admission) and decide what to do about the
        threads still inside: refuse the removal, or clean up anyway and log it.

    Contract:
        - Subclasses RuntimeError, so code that caught the timeout as a RuntimeError keeps working.
        - Its message is the one the drain has always raised: "Timeout waiting for rift tickets to drain."
        - `threads_inside` is how many threads other than the draining caller were still inside when the drain gave
          up; the caller's own ticket is never waited for, so it is never counted.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. The drain-timeout error of the Rift gate. Melder kernel machinery: read it to understand
        the runtime, do not drive it directly.
    """

    def __init__(self, threads_inside: int) -> None:
        """
        Build the timeout error for one drain.

        Args:
            threads_inside:
                Threads other than the draining caller still inside when the drain gave up.

        Returns:
            None.
        """
        super().__init__("Timeout waiting for rift tickets to drain.")
        self.threads_inside: int = threads_inside


class _RiftGateHolder(threading.local):
    """
    The calling thread's ticket depth on one RiftGate.

    Contract:
        - `depth` starts at 0 on every thread. It counts the thread's unreleased `admit_ticket` and
          `register_ticket` calls on the gate that owns this holder; while it is above 0 the gate's ticket deque
          holds exactly one ticket for the thread.
        - Only the owning thread reads or writes its own `depth`, so it needs no lock.
    """

    def __init__(self) -> None:
        """
        Start the calling thread at depth 0 (`threading.local` runs this once per thread, on first access).

        Returns:
            None.
        """
        super().__init__()
        self.depth: int = 0


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
           - close_terminally() marks the gate terminally closed to new work;
             wait_until_free() then waits for the threads inside to leave;
             close_and_wait_until_free() does both.
           - cleanup() also marks terminal close and releases waiters.

    Ticket model (GitHub #274, step 3):
        - One ticket per THREAD inside, not per call. A thread takes its
          ticket with its first `admit_ticket` (or `register_ticket`); every
          nested admission on the same thread only deepens a thread-local
          depth, and the thread's one ticket goes when its last paired
          `unregister_ticket` brings the depth back to 0. Counts and drains
          therefore count threads inside.
        - Re-entry passes whatever the gate's state: a thread that already
          holds a ticket is admitted again at once even while the gate is
          disabled (an ACL refresh's reversible close) or terminally closed
          (a removal). The close is waiting for that thread to leave, so
          refusing or parking it would wait on itself.
        - Drains never wait for the caller's own ticket: a thread that drains
          a gate it is inside - an agent removing its own Rift - waits only
          for the other threads.
        - Releasing a ticket after the gate was cleaned is a no-op: cleanup
          dropped every ticket, and a thread that was inside when its Rift was
          torn down still releases on its way out.
        - Ticket bookkeeping uses deque[None] for low overhead and
          allocation-friendly append/pop behavior.

    Threading:
        - State transitions for enabled / _closed and the event are
          protected by an internal RLock.
        - enabled is intentionally readable without lock on hot paths.
        - Re-entry is one thread-local read and one write, with no lock; a
          first admission is the lock-free ticket-first loop of
          `admit_ticket`.

    Registration:
        MELDER KERNEL - guarded. One gate per Rift, owned by that Rift and
        coordinated through `RiftGateController`.

    Subsystem Context:
        The admission primitive of the AR layer, the same role `CreationGate`
        plays for conduits and `LoadGate` plays for crystallizer loads. All
        three exist because some operations must wait for READERS rather than
        for other writers.

    System Context:
        The two control modes answer different questions and must not be
        conflated. Blocking mode is REVERSIBLE - `enabled=False` parks new
        callers and `open()` releases them, which is what an ACL-driven
        projection refresh needs: block entrants, drain, refresh once, reopen.
        Terminal close is ONE-WAY and exists for shutdown, where reopening
        would be wrong.
        Ticket bookkeeping is what makes draining truthful. Counting active
        work rather than holding a boolean lets `close_and_wait_until_free()`
        wait for real in-flight operations to finish instead of guessing, which
        is the same reason the conduit `CreationGate` tracks tickets: a meld
        holds its ticket across the whole executor, so ticket-zero genuinely
        means no reader is inside.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Generic gate primitive for coordinating Rift-scoped operations. Melder
        kernel machinery: read it to understand the runtime, do not drive it directly.
    """

    ENTRY_MODE_WAIT = "wait"
    ENTRY_MODE_RAISE = "raise"
    __slots__ = ("_lock", "enabled", "_entry_mode", "_event", "_tickets", "_closed", "_holder")

    def __init__(self, enabled: bool = True, entry_mode: str = "wait") -> None:
        """
        Initialize the gate in an enabled or disabled state.

        Purpose:
            Construct a low-overhead gate instance that tracks both admission
            state and in-flight ticket count for one protected Rift path.

        Contract:
            - _closed starts False.
            - enabled reflects constructor input.
            - _event state mirrors enabled:
              set when enabled, cleared when disabled.
            - Ticket queue starts empty, and every thread starts at ticket
              depth 0 in the per-thread holder.

        Args:
            enabled:
                True starts with immediate pass-through behavior.
                False starts in blocking mode until open() is called.
            entry_mode:
                Admission mode used by admit() while the gate is disabled.
                Supported values are wait and raise.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self.enabled: bool = enabled
        self._entry_mode: str = self._normalize_entry_mode(entry_mode)
        self._event: threading.Event = threading.Event()
        self._tickets: Deque[None] = deque()
        self._closed: bool = False
        self._holder: _RiftGateHolder = _RiftGateHolder()

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
            - Forces enabled=True and signals the event to unblock waiters.
            - Clears outstanding tickets as teardown intent, so a drain still
              waiting on this gate returns, and a thread that was inside
              releases its ticket quietly afterwards (`unregister_ticket`).
            - Marks this instance cleaned and deletes owned references,
              including the per-thread holder.
            - Leaves the object unusable for all guarded operations.

        Returns:
            None.

        Threading:
            Runs under the gate lock. A release racing this cleanup itself -
            possible only when a teardown proceeds with threads still inside,
            after a drain gave up on them - can find the bookkeeping already
            deleted and raise AttributeError.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._closed = True
            self.enabled = True
            self._event.set()
            self._tickets.clear()

            del self.enabled
            del self._entry_mode
            del self._event
            del self._tickets
            del self._holder
        del self._lock

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
        Disable entry so callers block in wait().

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
            - When admission is disabled and entry_mode == "raise",
              raises immediately.
            - When admission is disabled and entry_mode == "wait", blocks
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

    def admit_ticket(self) -> None:
        """
        Atomically-by-ordering admit one command: acquire a VISIBLE ticket
        first, then validate gate state, honoring the configured entry mode.

        Purpose:
            Close the check-then-register drain race (same class as the
            conduit CreationGate fix, 2026-07-12): with `admit()` and
            `register_ticket()` as two separate steps, a projection
            refresh could disable admission, observe zero tickets, and
            run its refresh while an already-admitted command registered
            late and executed inside the drained window. Ticket-first
            admission closes that lock-free: the ticket is appended
            BEFORE the state reads, so either the drain poll counts this
            caller and waits, or this caller's post-append read sees the
            freeze and backs out.

        Contract:
            - RE-ENTRY: a thread that already holds a ticket on this gate is
              admitted at once - its depth deepens, the deque is untouched -
              whatever `_closed` and `enabled` say. A disabled or closed gate
              is waiting for that thread to leave (GitHub #274, step 3).
            - FIRST ADMISSION LOOP: append ticket -> terminally closed: pop +
              raise -> enabled: return (ADMITTED, ticket held, depth 1) ->
              disabled + entry_mode "raise": pop + raise -> disabled +
              "wait": pop + park + retry on wake.
            - On return the caller holds an admission and must pair it with
              one `unregister_ticket()`; on raise it holds none. The deque
              holds exactly one ticket per thread inside.
            - Parked callers hold NO steady ticket (drains never wait on
              waiters).

        Threading:
            Re-entry is one thread-local read and one write, with no lock. A
            first admission is lock-free by append-before-read ordering (deque
            ops are thread-safe primitives); cleaned-state guard at entry only.

        Returns:
            None. (The caller holds one admission.)

        Raises:
            RuntimeError:
                If the gate is terminally closed, entry is disabled in
                "raise" mode, or the gate was cleaned - never for a thread
                that already holds a ticket on a live gate.
        """
        self.check_cleaned()
        holder = self._holder
        depth = holder.depth
        if depth:
            holder.depth = depth + 1
            return
        tickets = self._tickets
        while True:
            # Visibility FIRST: from this append until the pop below, any
            # drain poll counts this caller and must wait.
            tickets.append(None)
            if self._closed:
                tickets.pop()
                raise RuntimeError("RiftGate is closed.")
            if self.enabled:
                holder.depth = 1
                return
            tickets.pop()
            if self._entry_mode == self.ENTRY_MODE_RAISE:
                raise RuntimeError("RiftGate entry is disabled.")
            self._event.wait()

    def set_entry_mode(self, entry_mode: str) -> None:
        """
        Set the gate admission mode.

        Args:
            entry_mode:
                Admission mode. Supported values are wait and raise.

        Returns:
            None.
        """
        self.check_cleaned()
        normalized_entry_mode = self._normalize_entry_mode(entry_mode)
        with self._lock:
            self._entry_mode = normalized_entry_mode

    def register_ticket(self) -> None:
        """
        Register the calling thread as inside, without checking the gate state.

        Contract:
            - Same per-thread bookkeeping as `admit_ticket`: the thread's first
              registration appends its one ticket, a nested one only deepens
              its depth.
            - Checks neither `_closed` nor `enabled`; it is the unconditional
              half of the old two-step admission. Pair it with one
              `unregister_ticket()`.

        Returns:
            None.

        Raises:
            RuntimeError: If the gate was cleaned.

        Threading:
            Lock-free: one thread-local read and write, plus one deque append
            on the thread's first registration.
        """
        self.check_cleaned()
        holder = self._holder
        depth = holder.depth
        if depth:
            holder.depth = depth + 1
            return
        self._tickets.append(None)
        holder.depth = 1

    def unregister_ticket(self) -> None:
        """
        Release one admission of the calling thread.

        Contract:
            - A no-op once the gate was cleaned: cleanup dropped every ticket,
              and a thread that was inside when its Rift was torn down - its own
              removal, or a cleanup that gave up waiting for it - releases
              quietly on its way out (GitHub #274, step 3).
            - Otherwise the thread's depth drops by one; the thread's one
              ticket leaves the deque when the depth reaches 0.

        Returns:
            None.

        Raises:
            RuntimeError: If the calling thread holds no ticket on this live
                gate - an unpaired release, or a release from a thread other
                than the one that was admitted.

        Threading:
            Lock-free: one thread-local read and write, plus one deque pop on
            the thread's last release.
        """
        if self._cleaned:
            return
        holder = self._holder
        depth = holder.depth
        if not depth:
            raise RuntimeError(
                "RiftGate ticket released by a thread that holds none: every "
                "unregister_ticket must pair with an admit_ticket or "
                "register_ticket on the same thread."
            )
        depth -= 1
        holder.depth = depth
        if not depth:
            self._tickets.pop()

    def has_active_tickets(self) -> bool:
        """
        Return True when at least one thread is inside the gate.

        Returns:
            bool: True when at least one ticket is registered.
        """
        self.check_cleaned()
        return bool(self._tickets)

    def active_ticket_count(self) -> int:
        """
        Return how many threads are inside the gate.

        Contract:
            - Counts threads, not calls: a thread admitted several times holds
              one ticket.
            - A point-in-time read; a first admission that is refused shows for
              an instant (ticket-first) before it backs out.

        Returns:
            int: Number of currently registered tickets, one per thread inside.
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

    def close_terminally(self) -> None:
        """
        Close the gate to new work for good, without waiting for anyone.

        Purpose:
            The first half of a removal's or a shutdown's drain: from here on
            every thread without a ticket is refused at once ("RiftGate is
            closed."), while the threads already inside keep passing by
            re-entry so they can finish and leave. `Nexus.cleanup` closes every
            Rift's gate first and waits for them afterwards, under one deadline.

        Contract:
            - Sets the terminal flag and disables the gate under the gate lock,
              and wakes parked first-time callers so they see the close and
              raise.
            - Idempotent; there is no way back short of a new gate.

        Returns:
            None.

        Raises:
            RuntimeError: If the gate was cleaned.

        Threading:
            Takes the gate lock briefly.
        """
        self.check_cleaned()
        with self._lock:
            self._closed = True
            self.enabled = False
            self._event.set()

    def wait_until_free(
        self,
        timeout: float = 30.0,
        interval: float = 0.1,
    ) -> None:
        """
        Wait until no thread other than the caller is inside the gate.

        Purpose:
            The second half of a drain. It does not close the gate itself; call
            it after `close_terminally()` (or use `close_and_wait_until_free`),
            or new threads can keep arriving while it waits.

        Contract:
            - Never waits for the caller's own ticket: it waits while the gate
              holds more tickets than the caller's own (1 when the calling
              thread is inside, else 0), so an agent removing its own Rift is
              not waited for (GitHub #274, 5c).
            - A gate cleaned while this waits has no tickets left, so the wait
              returns.

        Args:
            timeout:
                Maximum seconds to wait for the other threads to leave.
            interval:
                Poll interval in seconds for checking drain progress.

        Returns:
            None.

        Raises:
            RiftGateDrainTimeoutError:
                If other threads are still inside when the timeout runs out;
                its `threads_inside` says how many.
            RuntimeError:
                If the gate was cleaned before the wait started.

        Threading:
            Polls without the gate lock. The ticket deque and the per-thread
            holder are held in locals on purpose: a cleanup during the wait
            deletes the fields, and the cleared deque is what tells the wait
            that nobody is left (GitHub #274).
        """
        self.check_cleaned()
        tickets = self._tickets
        holder = self._holder
        deadline = time.monotonic() + timeout
        while True:
            threads_inside = len(tickets) - (1 if holder.depth else 0)
            if threads_inside <= 0:
                return
            if time.monotonic() >= deadline:
                raise RiftGateDrainTimeoutError(threads_inside)
            time.sleep(interval)

    def close_and_wait_until_free(
        self,
        timeout: float = 30.0,
        interval: float = 0.1,
    ) -> None:
        """
        Terminally close the gate and wait for the other threads inside to leave.

        Contract:
            - `close_terminally()` then `wait_until_free(timeout, interval)`:
              newcomers are refused from the start of the call, the threads
              already inside pass by re-entry until they leave, and the
              caller's own ticket is not waited for.

        Args:
            timeout:
                Maximum seconds to wait for ticket drain.
            interval:
                Poll interval in seconds for checking drain progress.

        Returns:
            None.

        Raises:
            RiftGateDrainTimeoutError:
                If other threads are still inside when the timeout runs out
                (a RuntimeError, message "Timeout waiting for rift tickets to
                drain."). The gate stays closed.
            RuntimeError:
                If the gate was cleaned.

        Threading:
            Takes the gate lock only to close; the wait polls without it.
        """
        self.close_terminally()
        self.wait_until_free(timeout=timeout, interval=interval)

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

