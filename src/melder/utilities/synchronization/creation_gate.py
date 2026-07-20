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

    Responsibilities:
        - Admit or park callers entering guarded creation work.
        - Count in-flight work so a drain can wait it out.
        - Support a TEMPORARY freeze and a TERMINAL close, distinctly.

    THE VISIBILITY-FIRST PROTOCOL (`admit_ticket`, the important part):
        The ticket is appended BEFORE the admission checks, and popped again if
        the caller turns out not to be admitted:

            append ticket        <- become VISIBLE to drains immediately
            if closed:  pop, raise
            if enabled: return   <- admitted, ticket stays held
            pop; wait; retry     <- not admitted, become invisible, park

        That ordering is the whole race closure. From the append until the pop,
        any concurrent drain poll COUNTS this caller and must wait for it. The
        obvious alternative - check first, then append - has a window where a
        drain observes zero tickets and declares itself free while a caller is
        already committed to entering. Appending first can only ever make a
        drain wait slightly longer; checking first can let it finish early,
        which is unsound.

    TWO CLOSE MODES, OPPOSITE EVENT POLARITY:
        - `close_and_wait_until_free()` is TERMINAL. Sets `_closed`, disables
          entry, and SETS the event - waking every parked caller so they observe
          the closed flag and raise. New callers are refused permanently.
        - `close_and_drain()` is a TEMPORARY FREEZE. Disables entry and CLEARS
          the event so callers PARK rather than fail. `_closed` is untouched, so
          a later `open()` resumes normal service.

        Set-to-fail versus clear-to-park is the distinction. Reading only the
        method names, the two look interchangeable; they are opposites.

    DRAIN IS A POLL LOOP:
        Both drains spin on `has_active_tickets()` with `time.sleep(interval)`
        and a deadline, rather than waiting on a second condition. That keeps
        the hot admission path free of extra signalling machinery at the cost of
        drain latency bounded by `interval` - a deliberate trade, since drains
        are rare and admissions are not.

    Owned State:
        - `enabled`: plain attribute, deliberately NOT a property, so the hot
          path reads it with one attribute load and no lock.
        - `_closed`: terminal flag; once set, admission never succeeds again.
        - `_event`: parking surface for blocked callers.
        - `_tickets`: deque whose LENGTH is the in-flight count. Elements are
          `None`; only cardinality carries meaning.
        - `_lock`: RLock guarding state transitions, not the hot read.

    Threading:
        - State transitions for "enabled" / "_closed" and the event are
          protected by an internal "RLock".
        - "enabled" is intentionally readable without a lock on hot paths.
        - `wait()` is fully lock-free: one `enabled` read, then park on the
          event. It is the cheapest path through the gate when open.
        - `admit_ticket` mutates the ticket deque without the lock, relying on
          `append`/`pop` atomicity. Cardinality is therefore always sound even
          though the admission decision around it is not serialized.

    Lifecycle / Cleanup:
        - Idempotent, double-checked under the lock.
        - Terminally closes, re-enables, and SETS the event before releasing, so
          nothing stays parked across teardown; then releases every owned slot
          under normal del posture.
        - PRECONDITION, same as the rest of this family: clean up a gate once
          its callers are done. A thread parked inside `admit_ticket` that wakes
          after teardown finds its retry loop reaching a released deque. That is
          out-of-contract use, in the same category as any other use-after-clean.

    Registration:
        MELDER KERNEL - guarded. Melder owns admission policy for creation work;
        a user has no reason to register a gate as a spell.

    Subsystem Context:
        The per-conduit member of the gate family in
        `utilities/synchronization/`. `LoadGate` is process-wide and exclusive;
        this one is conduit-scoped and counting. `CreationGateController` owns
        the collection of these for a lineage and drives bulk enable/disable and
        close-and-drain across them.

    System Context:
        Each `Conduit` owns one `CreationGate`, registered into the frame-owned
        `CreationGateController`. In dynamic mode `Conduit.meld(...)` passes
        through it, so this is the primitive that can hold resolution still
        while structural change lands. The temporary-freeze mode exists for
        exactly that: drain in-flight melds, mutate topology, reopen - without
        the terminal refusal a real close would impose.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Per-conduit admission gate for creation work. "
        "admit_ticket() enters guarded work (appending its ticket BEFORE "
        "checking, so drains always count it); close_and_drain() freezes "
        "temporarily and parks callers; close_and_wait_until_free() closes "
        "terminally and fails them. Drains poll until the ticket count is zero."
    )
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

    def admit_ticket(self) -> None:
        """
        Public API

        Atomically-by-ordering admit one guarded operation: acquire a
        VISIBLE ticket first, then validate gate state, retrying through
        parks until admitted or terminally refused.

        Purpose:
            Close the check-then-register drain race (owner finding,
            2026-07-12): with separate checks, a drainer could disable
            admission, observe zero tickets, and return while a meld that
            had already passed its checks registered late and executed
            inside the "drained" exclusive window. Ticket-first admission
            makes that impossible without any lock: the ticket is
            appended BEFORE the state reads, so either the drainer's
            zero-poll sees this ticket and waits, or this caller's state
            read happens after the freeze and it backs out.

        Contract:
            - LOOP: append ticket -> if terminally closed: pop + raise ->
              if enabled: return (ADMITTED, ticket held) -> else pop +
              park in the gate event -> retry on wake.
            - On return the caller HOLDS one ticket and must pair it with
              `unregister_ticket()` (try/finally at the call site).
            - On raise no ticket is held (the transient ticket is popped
              before the refusal), so callers never unregister after a
              failed admission.
            - Parked callers hold NO ticket (a frozen window's drain is
              never extended by waiters) - at most a transient one for
              the instant between append and the state read, which only
              delays a drain poll by one interval.
            - Wakes from terminal closure re-check and refuse
              (`close_and_wait_until_free` sets the event with
              `_closed=True` exactly so waiters can observe it).

        Threading:
            - Lock-free by design (owner ruling): deque append/pop are
              thread-safe primitives, and the append-before-read ordering
              carries the drain guarantee on free-threaded builds. The
              only cleaned-state guard is at entry; a cleanup racing the
              loop surfaces as the standard deleted-slot AttributeError
              (lifecycle misuse, loud by contract).

        Returns:
            None. (The caller holds one admitted ticket.)

        Raises:
            RuntimeError:
                If the gate is terminally closed, or if called after
                "cleanup()".
        """
        self.check_cleaned()
        tickets = self._tickets
        while True:
            # Visibility FIRST: from this append until the pop below, any
            # drain poll counts this caller and must wait.
            tickets.append(None)
            if self._closed:
                tickets.pop()
                raise RuntimeError("CreationGate is closed.")
            if self.enabled:
                return
            # Not admitted: become invisible again, then park until the
            # gate reopens (or terminally closes and wakes everyone).
            tickets.pop()
            self._event.wait()

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

    def close_and_drain(
        self,
        timeout: float = 30.0,
        interval: float = 0.1,
    ) -> None:
        """
        Public API

        Temporarily freeze the gate and wait for all tickets to drain.

        Purpose:
            Give one coordinating thread (a transaction window such as a
            SpellIndex notch) exclusive runtime rights for a short span:
            new entrants park in "wait()" while every in-flight guarded
            call finishes, and a later "open()" fully restores admission.

        Contract:
            - PARK mode, not terminal: "enabled=False" and the event is
              cleared (new callers block in "wait()"), but "_closed" is
              NOT touched - "is_closed()" stays False throughout, and
              "open()" resumes every parked waiter.
            - Polls until "active_ticket_count == 0" so in-flight guarded
              work (a meld holds its ticket across its whole executor,
              validators included) completes BEFORE the caller proceeds.
            - On drain timeout the gate is left frozen (parked, never
              terminal) and RuntimeError raises; the caller's reopen path
              owns restoring admission.

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
            - Freeze-state transition is lock-guarded.
            - Drain wait loop is cooperative polling based on ticket queue
              length; no runtime locks are held while waiting.

        Returns:
            None.

        Notes:
            This is the non-terminal sibling of
            :meth:`close_and_wait_until_free`; shutdown paths keep the
            terminal verb, coordination windows use this one.
        """
        with self._lock:
            self.enabled = False
            self._event.clear()

        deadline = time.monotonic() + timeout
        while self.has_active_tickets():
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "Timeout waiting for creation tickets to drain during "
                    "a temporary gate freeze (close_and_drain)."
                )
            time.sleep(interval)
