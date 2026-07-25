import threading
from collections import deque
from typing import Deque, Optional, ClassVar

from melder.utilities.general_base.cleanable import Cleanable



class CounterSwitch(Cleanable):
    """
    Deque-backed selector latch with minimal leader election.

    Purpose:
        Provide one fast coordination primitive where deque cardinality is the
        state and leader election is performed only by "selector()".

    State model:
        - "0": idle
        - "1": pending (leader claimed)
        - ">=2": open/ready

    Selector model:
        - "selector()" returns immediately for ">=2".
        - For "0", one caller claims leader by appending one ticket.
          This is the only place a lock is used.
        - For "1", followers wait on the event until signalled.

    Advance model:
        - "advance(delta)" mutates raw counter-tickets.
        - Positive deltas append; negative deltas pop.
        - Event is cleared only for state "1" and set for all other states.

    Fast-state mirror:
        - "fast_state" is a plain int slot mirroring the deque cardinality for
          lock-free hot-path readers (one attribute load, no descriptor call,
          no "len()" call).
        - The deque remains the authoritative state; the mirror is written at
          every mutation point ("__init__", "advance", "selector" leader
          claim) immediately after the deque mutation.
        - Readers tolerate the same transient staleness window as a raw
          "len(self._tickets)" read; publication ordering guarantees are
          unchanged because the mirror is only ever written after the deque
          reflects the new state.

    Responsibilities:
        - Hold a three-state coordination value backed by deque cardinality.
        - Elect exactly one leader out of the idle state, under the one lock.
        - Park followers on the event while a leader is pending.
        - Publish a lock-free `fast_state` mirror for hot readers.
        - Terminate cleanly once its threads are done, releasing owned slots.

    Design intent:
        - Minimal API surface for hot paths.
        - Non-defensive by design.

    Threading:
        - `advance()` and the `>=2` fast path in `selector()` are LOCKLESS.
        - The lock is taken in exactly two places: the idle-state leader claim
          and `cleanup()`. They share the lock deliberately, so a leader claim
          cannot interleave with the terminal transition.
        - Mirror ordering is the publication guarantee: `fast_state` is written
          only AFTER the deque mutation, so a hot reader can never observe a
          state the deque has not already reached. It can be stale; it cannot be
          ahead.

    Owned State:
        - `_tickets`: the authoritative state. Cardinality IS the value.
        - `fast_state`: lock-free int mirror of that cardinality.
        - `_event`: cleared ONLY at state 1 (pending); set in every other state.
          So "event is set" means "not pending".
        - `_lock`: guards leader claims and teardown, nothing else.

    Registration:
        GUARDED, and exported. Owner ruling 2026-07-19 made the switches fair to
        EXPOSE, and they are on the public root surface. Exposure is not
        bindability: this type is present in `INTERNAL_MANIFEST`, so
        `Spellbook.bind(...)` refuses it. Hold one as your own coordination
        latch directly; do not bind it.

    Subsystem Context:
        Part of `utilities/synchronization/`, in the switch family with
        `FastSwitch` and `TicketFlag`. The contrast with `FastSwitch` is worth
        knowing: that one is the cheapest possible flag and its `cleanup()` is
        deliberately NOT idempotent, deleting its field outright. This one is
        the coordination-capable member - it elects a leader, parks followers,
        and its `cleanup()` IS idempotent and double-checked under the lock,
        because releasing parked waiters correctly is the whole point.

    System Context:
        A substrate primitive outside the DGR boot order. Worth contrasting with
        `LoadGate`, which parks threads on the same kind of shared condition but
        keeps `None` tombstones through teardown so a late waiter can re-check
        and exit. This switch does NOT - it deletes its slots, because its owner
        quiesces it before cleanup rather than cleaning up underneath live
        selectors. Two different answers to the same question, chosen by who is
        expected to be parked at teardown time.

    Lifecycle / Cleanup:
        - "cleanup()" idles the switch inside the guarded section - tickets
          clear, mirror zeroes, event sets - then releases all four owned slots
          under normal del posture.
        - Idempotent and double-checked under the lock, so concurrent TEARDOWN
          is safe even though concurrent USE during teardown is not.
        - PRECONDITION: the owner cleans up a switch once its threads are DONE,
          never while selectors are in flight. The primitive cannot enforce this
          - ticket cardinality is the state VALUE, not a count of callers, so it
          has no way to observe or drain in-flight selectors. Using a cleaned
          switch raises AttributeError, which is the intended loud failure for
          out-of-contract use.
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Three-state coordination latch: 0=idle, 1=pending "
        "(a leader claimed it), >=2=open. Call selector() to either pass "
        "through, become the leader, or park until the leader finishes. Read "
        "fast_state for a lock-free hot-path view. Cleanup is terminal - clean "
        "up only once your threads are done, never underneath live selectors."
    )

    __slots__ = ("_lock", "_event", "_tickets", "fast_state")
    def __init__(self, state: int = 2) -> None:
        """
        Public API

        Initialize counter state from ticket cardinality.

        Contract:
            - Ticket cardinality IS the state: `state` tickets are enqueued,
              so 0 starts idle, 1 starts pending, and >=2 starts open.
            - The event mirrors that state at construction: cleared at state
              1 (pending), set otherwise, so "event set" means "not pending".
            - `fast_state` is seeded from the deque length as the lock-free
              hot-read mirror.

        Args:
            state:
                Initial ticket count. Default "2" starts open.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.Lock = threading.Lock()
        self._event: threading.Event = threading.Event()
        self._tickets: deque[None] = deque()
        if state > 0:
            self._tickets.extend([None] * state)
        # Hot-path read mirror; see class docstring for the staleness contract.
        self.fast_state: int = len(self._tickets)
        if state == 1:
            self._event.clear()
        else:
            self._event.set()

    def cleanup(self) -> None:
        """
        Public API

        Terminally tear down this primitive.

        PRECONDITION - the caller must have quiesced this switch:
            Cleanup is only valid once no thread is inside "selector()". The
            owner of a CounterSwitch cleans it up when its threads are DONE, not
            while they are still coordinating on it.

            This is a call-site invariant that the primitive cannot enforce:
            ticket cardinality is the STATE value, not a count of callers, so
            the switch has no way to observe in-flight selectors. It therefore
            cannot drain and does not try. Ignoring the precondition means a
            parked selector wakes into released slots and raises
            AttributeError - out-of-contract use, failing loudly on purpose.

        Contract:
            - Idempotent; safe under concurrent double-cleanup.
            - Inside the guarded section: clears all tickets, zeroes the
              fast-state mirror, and sets the event, so the switch reaches a
              coherent idle-and-open terminal state before anything is released.
            - Then releases all four owned slots under NORMAL DEL POSTURE. The
              switch is terminal; nothing is expected to read it again.

        Threading:
            - Teardown serializes with "selector()" leader claims on the
              existing claim lock, so a leader claim cannot interleave with the
              terminal transition. Hot paths ("advance", the ">=2" selector
              fast path) remain lockless and untouched.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._tickets.clear()
            self.fast_state = 0
            self._event.set()
            self._cleaned = True
        del self._event
        del self._tickets
        del self._lock
        del self.fast_state

    def __len__(self) -> int:
        """
        Public API

        Return the current raw ticket count (the state value).

        Contract:
            - LOCKLESS and UNGUARDED: reads deque length directly as a
              hot-path read that never takes the lock. On a cleaned switch it
              raises `AttributeError` (the deque is deleted) rather than
              returning 0 - use-after-clean fails loudly by design.

        Returns:
            int:
                Raw ticket cardinality: 0 idle, 1 pending, >=2 open.
        """
        return len(self._tickets)

    def __bool__(self) -> bool:
        """
        Public API

        Return whether the switch is currently open (`state >= 2`).

        Contract:
            - LOCKLESS and UNGUARDED hot read (no `check_cleaned()`),
              mirroring `__len__`. Raises `AttributeError` on a cleaned
              switch rather than returning False.

        Returns:
            bool:
                True when the deque holds >= 2 tickets (open).
        """
        return len(self._tickets) >= 2

    @property
    def state(self) -> int:
        """
        Public API

        Return the raw deque-backed state value.

        Contract:
            - LOCKLESS and UNGUARDED read of deque cardinality (the
              authoritative state); raises `AttributeError` after cleanup.
            - Distinct from `fast_state`, the plain-int mirror for readers
              that want to avoid even the `len()` call.

        Returns:
            int: 0 when idle, 1 when a leader has claimed it and is pending, and >=2
                once open.
        """
        return len(self._tickets)

    def advance(self, delta: int) -> int:
        """
        Public API

        Apply signed state delta.

        Contract:
            - LOCKLESS by design: positive deltas append tickets, negative
              deltas pop that many, and a zero delta is a no-op returning the
              current count.
            - PUBLICATION ORDERING: `fast_state` is written AFTER the deque
              mutation, so a hot reader can only observe a state the deque has
              already reached (stale, never ahead).
            - Re-derives the event from the new count: cleared at exactly
              state 1 (pending), set for every other state.
            - UNGUARDED (no `check_cleaned()`); a negative delta larger than
              the ticket count raises `IndexError` on the empty pop.

        Args:
            delta:
                Positive appends tickets, negative pops tickets.

        Returns:
            int:
                Resulting state after the signed ticket mutation.
        """
        if delta == 0:
            return len(self._tickets)
        if delta > 0:
            self._tickets.extend([None] * delta)
        else:
            for _ in range(-delta):
                self._tickets.pop()
        count = len(self._tickets)
        # Mirror write happens after the deque mutation so hot readers can
        # only observe a state the deque has already reached.
        self.fast_state = count
        if count == 1:
            self._event.clear()
        else:
            self._event.set()
        return count

    def selector(self, timeout_seconds: Optional[float] = None) -> int:
        """
        Public API

        Enter a selector and return the current state.

        Args:
            timeout_seconds:
                Optional follower wait timeout.

        Returns:
            int:
                Current state after leader election or follower wake-up.
                Terminal "0" when cleanup released this selector or the
                switch is already cleaned at the claim point.

        Raises:
            TimeoutError:
                If a follower waits at pending state, and the event is not
                signalled before `timeout_seconds` expires.
        """
        count = len(self._tickets)
        if count >= 2:
            return count

        if count == 0:
            with self._lock:
                count = len(self._tickets)
                if count >= 2:
                    return count
                if count == 0:
                    self._tickets.append(None)
                    # Leader claim is a deque mutation, so the fast-state
                    # mirror must be updated here as well.
                    self.fast_state = 1
                    self._event.clear()
                    return 1

        completed = self._event.wait(timeout=timeout_seconds)
        if not completed:
            raise TimeoutError(
                "CounterSwitch selector timed out while pending."
            )
        return len(self._tickets)

